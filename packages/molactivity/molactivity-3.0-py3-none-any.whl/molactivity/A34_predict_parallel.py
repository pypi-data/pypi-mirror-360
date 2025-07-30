import multiprocessing as mp

def _worker_predict_single_model(args):
    try:
        model_file, data_provider_info, use_gpu = args
        
        from .A19_prepare_data import prepare_pure_predicting_dataset
        from .A21_predict import load_multiple_models
        from .A26_tensor import Tensor
        from .A16_operations import sigmoid
        
        data_provider = prepare_pure_predicting_dataset(
            data_provider_info['file'], 
            fingerprint_type=data_provider_info.get('fingerprint_type', 'Morgan'), 
            batch_size=data_provider_info.get('batch_size', 32), 
            shuffle=data_provider_info.get('shuffle', False)
        )
        
        models = load_multiple_models([model_file], use_gpu=use_gpu)

        
        model = models[0]
        model.eval()  
        model_predictions = []
        
        for batch_idx, (features, _) in enumerate(data_provider):
            try:
                if not isinstance(features, Tensor):
                    features = Tensor(features, requires_grad=False)
                
                outputs = model(features)
                probs_tensor = sigmoid(outputs.squeeze())
                
                if hasattr(probs_tensor.data, 'flatten'):
                    batch_predictions = probs_tensor.data.flatten().tolist()
                elif hasattr(probs_tensor.data, 'tolist'):
                    batch_predictions = probs_tensor.data.tolist()
                    if not isinstance(batch_predictions, list):
                        batch_predictions = [batch_predictions]
                elif isinstance(probs_tensor.data, (list, tuple)):
                    batch_predictions = list(probs_tensor.data)
                else:
                    batch_predictions = [float(probs_tensor.data)]
                
                model_predictions.extend(batch_predictions)
                
            except Exception as e:
                continue
                
        return (True, model_file, model_predictions, None)
        
    except Exception as e:
        pass


def parallel_prediction(model_files, dataset_file='predicting_dataset.csv', max_workers=None, use_gpu=False):
    
    if max_workers is None:
        cpu_count = mp.cpu_count()
        num_models = len(model_files)
        if num_models <= cpu_count // 2:
            max_workers = num_models
        else:
            max_workers = min(num_models, cpu_count // 2, 4)  
    
    data_provider_info = {
        'file': dataset_file,
        'fingerprint_type': 'Morgan',
        'batch_size': 32,
        'shuffle': False
    }
    
    task_args = []
    for model_file in model_files:
        task_args.append((model_file, data_provider_info, use_gpu))
    
    successful_results = []
    failed_results = []
    
    if max_workers == 1 or len(model_files) == 1:
        for args in task_args:
            result = _worker_predict_single_model(args)
         
            success, model_file, predictions, error_msg = result
            if success:
                successful_results.append((model_file, predictions))
            else:
                failed_results.append((model_file, error_msg))
    else:
        with mp.Pool(processes=max_workers) as pool:
            results = pool.map(_worker_predict_single_model, task_args)
            
            for result in results:
       
                success, model_file, predictions, error_msg = result
                if success:
                    successful_results.append((model_file, predictions))
                else:
                    failed_results.append((model_file, error_msg))
    
    
    return successful_results, failed_results


def generate_parallel_ensemble_predictions(model_files, dataset_file='predicting_dataset.csv', 
                                         max_workers=None, use_gpu=False):
    
    successful_results, failed_results = parallel_prediction(
        model_files, dataset_file, max_workers, use_gpu
    )
    
    if not successful_results:
        print("no successful predictions")
        return [], [], {}
    
    all_predictions = [predictions for _, predictions in successful_results]
    model_names = [model_file for model_file, _ in successful_results]
    
    min_length = min(len(preds) for preds in all_predictions)
    if min_length == 0:
        print("no valid predictions")
        return [], [], {}
    
    for i in range(len(all_predictions)):
        all_predictions[i] = all_predictions[i][:min_length]
    
    ensemble_predictions = []
    ensemble_std_devs = []
    
    for i in range(min_length):
        values = [preds[i] for preds in all_predictions]
        mean_value = sum(values) / len(values)
        
        if len(values) > 1:
            variance = sum((x - mean_value) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
        else:
            std_dev = 0.0
        
        ensemble_predictions.append(mean_value)
        ensemble_std_devs.append(std_dev)
    
    individual_predictions = {}
    for model_file, predictions in zip(model_names, all_predictions):
        individual_predictions[model_file] = predictions
    
    print(f"ensemble predictions completed, {len(ensemble_predictions)} predictions")
    
    for model_idx, (model_file, preds) in enumerate(successful_results):
        if preds:
            avg_pred = sum(preds) / len(preds)
            min_pred = min(preds)
            max_pred = max(preds)
            print(f"{model_file}: avg={avg_pred:.4f}, range=[{min_pred:.4f}, {max_pred:.4f}]")
    
    return ensemble_predictions, ensemble_std_devs, individual_predictions 