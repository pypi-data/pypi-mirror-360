import multiprocessing as mp
import numpy as np

def _worker_fast_evaluate_single_model(args):
    try:
        model_file, data_provider_info, optimization_config = args
        
        from .B15_prepare_data import prepare_pure_predicting_dataset
        from .B5_evaluate import load_multiple_models
        from .B16_tensor import Tensor
        from .B13_operations import sigmoid
        
        data_provider = prepare_pure_predicting_dataset(
            data_provider_info['file'], 
            fingerprint_type=data_provider_info.get('fingerprint_type', 'Morgan'), 
            batch_size=data_provider_info.get('batch_size', 64), 
            shuffle=False
        )
        
        models = load_multiple_models([model_file])
        model = models[0]
        model.eval() 
        model_predictions = []
        
        if optimization_config.get('use_vectorized_ops', True):
            batch_cache = []
            
            for batch_idx, (features, _) in enumerate(data_provider):
                try:
                    if not isinstance(features, Tensor):
                        features = Tensor(features, requires_grad=False)
                    
                    outputs = model(features)
                    probs_tensor = sigmoid(outputs.squeeze())
                    
                    if hasattr(probs_tensor.data, 'flatten'):
                        batch_predictions = probs_tensor.data.flatten()
                    else:
                        batch_predictions = np.array(probs_tensor.data).flatten()
                    
                    batch_cache.append(batch_predictions)
                    
                except Exception as e:
                    continue
            
            if batch_cache:
                if optimization_config.get('memory_efficient', True):
                    model_predictions = np.concatenate(batch_cache).tolist()
                else:
                    model_predictions = [item for batch in batch_cache for item in batch]
        else:
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
                    else:
                        batch_predictions = [float(probs_tensor.data)]
                    
                    model_predictions.extend(batch_predictions)
                    
                except Exception as e:
                    continue
        
        return (True, model_file, model_predictions, None)
        
    except Exception as e:
        return (False, model_file, [], str(e))

def fast_parallel_evaluation(model_files, dataset_file='evaluating_dataset.csv', 
                           max_workers=None, optimization_config=None):
    if optimization_config is None:
        optimization_config = {
            'use_vectorized_ops': True,
            'cache_fingerprints': True,
            'batch_processing': True,
            'memory_efficient': True,
        }
    
    if max_workers is None:
        cpu_count = mp.cpu_count()
        num_models = len(model_files)
        if num_models <= cpu_count:
            max_workers = num_models
        else:
            max_workers = min(num_models, cpu_count, 6)
    
    data_provider_info = {
        'file': dataset_file,
        'fingerprint_type': 'Morgan',
        'batch_size': optimization_config.get('batch_size', 64),
        'shuffle': False
    }
    
    task_args = []
    for model_file in model_files:
        task_args.append((model_file, data_provider_info, optimization_config))
    
    successful_results = []
    failed_results = []
    
    if max_workers == 1 or len(model_files) == 1:
        for args in task_args:
            result = _worker_fast_evaluate_single_model(args)
            success, model_file, predictions, error_msg = result
            if success:
                successful_results.append((model_file, predictions))
            else:
                failed_results.append((model_file, error_msg))
    else:
        try:
            with mp.Pool(processes=max_workers) as pool:
                results = pool.map(_worker_fast_evaluate_single_model, task_args)
                
                for result in results:
                    success, model_file, predictions, error_msg = result
                    if success:
                        successful_results.append((model_file, predictions))
                    else:
                        failed_results.append((model_file, error_msg))
        except Exception as e:
            print(f"parallel processing failed: {e}")
            for args in task_args:
                result = _worker_fast_evaluate_single_model(args)
                success, model_file, predictions, error_msg = result
                if success:
                    successful_results.append((model_file, predictions))
                else:
                    failed_results.append((model_file, error_msg))
    
    return successful_results, failed_results

def generate_fast_parallel_ensemble_predictions(model_files, dataset_file='evaluating_dataset.csv', 
                                               max_workers=None, optimization_config=None, 
                                               batch_size=64):
    if optimization_config is None:
        optimization_config = {
            'use_vectorized_ops': True,
            'cache_fingerprints': True,
            'batch_processing': True,
            'memory_efficient': True,
        }
    
    optimization_config['batch_size'] = batch_size
    
    successful_results, failed_results = fast_parallel_evaluation(
        model_files, dataset_file, max_workers, optimization_config
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
    
    if optimization_config.get('use_vectorized_ops', True):
        try:
            predictions_array = np.array(all_predictions)
            ensemble_predictions = np.mean(predictions_array, axis=0).tolist()
            if len(all_predictions) > 1:
                ensemble_std_devs = np.std(predictions_array, axis=0).tolist()
            else:
                ensemble_std_devs = [0.0] * min_length
        except Exception as e:
            print(f"numpy optimization failed: {e}")
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
    else:
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
        
    for model_idx, (model_file, preds) in enumerate(successful_results):
        if preds:
            avg_pred = sum(preds) / len(preds)
            min_pred = min(preds)
            max_pred = max(preds)
            print(f"{model_file}: avg={avg_pred:.4f}, range=[{min_pred:.4f}, {max_pred:.4f}]")
    
    return ensemble_predictions, ensemble_std_devs, individual_predictions 