import multiprocessing as mp
import torch
import numpy as np
import glob
import os

def discover_rocket_model_files(pattern='model_*.pt'):
    model_files = glob.glob(pattern)
    
    if not model_files:
        print(f"did not find rocket models")
        return []
    
    def extract_number(filename):
        import re
        match = re.search(r'model_(\d+)\.pt', filename)
        return int(match.group(1)) if match else 0
    
    model_files.sort(key=extract_number)
    
    print(f"find {len(model_files)} rocket models: {model_files}")
    return model_files

def parse_rocket_model_selection(model_selection):
    if not model_selection or model_selection.lower() in ['all', 'auto']:
        return discover_rocket_model_files()
    
    if ',' in model_selection:
        parts = [part.strip() for part in model_selection.split(',')]
        model_files = []
        
        for part in parts:
            if part.endswith('.pt'):
                if os.path.exists(part):
                    model_files.append(part)
                else:
                    print(f"did not find model: {part}")
            elif part.isdigit():
                filename = f"model_{part}.pt"
                if os.path.exists(filename):
                    model_files.append(filename)
                else:
                    print(f"did not find model: {filename}")
            elif '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    for i in range(start, end + 1):
                        filename = f"model_{i}.pt"
                        if os.path.exists(filename):
                            model_files.append(filename)
                        else:
                            print(f"did not find model: {filename}")
                except ValueError:
                    print(f"no valid models in range: {part}")
        
        return model_files
    
    elif model_selection.endswith('.pt'):
        if os.path.exists(model_selection):
            return [model_selection]
        else:
            print(f"did not find model: {model_selection}")
            return []
    elif model_selection.isdigit():
        filename = f"model_{model_selection}.pt"
        if os.path.exists(filename):
            return [filename]
        else:
            print(f"did not find model: {filename}")
            return []
    else:
        print(f"no valid models: {model_selection}")
        return []

def rocket_parallel_evaluation(model_files, dataset_file='evaluating_dataset.csv', 
                             max_workers=None, optimization_config=None, device='cuda', multi_gpu=False):
    if optimization_config is None:
        optimization_config = {
            'use_torch_optimization': True,
            'cache_fingerprints': True,
            'batch_processing': True,
            'memory_efficient': True,
            'mixed_precision': True,
            'compile_mode': True,
        }
    
    if max_workers is None:
        if multi_gpu and torch.cuda.is_available():
            max_workers = min(len(model_files), torch.cuda.device_count())
        else:
            cpu_count = mp.cpu_count()
            num_models = len(model_files)
            if num_models <= 2:
                max_workers = 1
            elif num_models <= cpu_count:
                max_workers = num_models
            else:
                max_workers = min(num_models, cpu_count, 4)
    
    data_provider_info = {
        'file': dataset_file,
        'fingerprint_type': 'Morgan',
        'batch_size': optimization_config.get('batch_size', 256),
        'shuffle': False
    }
    
    task_args = []
    for i, model_file in enumerate(model_files):
        gpu_id = None
        if multi_gpu and torch.cuda.is_available():
            gpu_id = i % torch.cuda.device_count()
        task_args.append((model_file, data_provider_info, optimization_config, device, gpu_id))
    
    successful_results = []
    failed_results = []
    
    if max_workers == 1 or len(model_files) == 1:
        for args in task_args:
            result = _worker_rocket_evaluate_single_model(args)
            success, model_file, predictions, error_msg = result
            if success:
                successful_results.append((model_file, predictions))
            else:
                failed_results.append((model_file, error_msg))
    else:
        try:
            with mp.Pool(processes=max_workers) as pool:
                results = pool.map(_worker_rocket_evaluate_single_model, task_args)
                
                for result in results:
                    success, model_file, predictions, error_msg = result
                    if success:
                        successful_results.append((model_file, predictions))
                    else:
                        failed_results.append((model_file, error_msg))
        except Exception as e:
            print(f"rocket parallel processing failed: {e}")
            for args in task_args:
                result = _worker_rocket_evaluate_single_model(args)
                success, model_file, predictions, error_msg = result
                if success:
                    successful_results.append((model_file, predictions))
                else:
                    failed_results.append((model_file, error_msg))
    
    return successful_results, failed_results



def generate_rocket_parallel_ensemble_predictions(model_files, dataset_file='evaluating_dataset.csv', 
                                                 max_workers=None, optimization_config=None, 
                                                 batch_size=256, device='cuda', multi_gpu=False):
    if optimization_config is None:
        optimization_config = {
            'use_torch_optimization': True,
            'cache_fingerprints': True,
            'batch_processing': True,
            'memory_efficient': True,
            'mixed_precision': True,
            'compile_mode': True,
        }
    
    optimization_config['batch_size'] = batch_size
    
    successful_results, failed_results = rocket_parallel_evaluation(
        model_files, dataset_file, max_workers, optimization_config, device, multi_gpu
    )
    
    if not successful_results:
        print("no successful rocket predictions")
        return [], [], {}
    
    all_predictions = [predictions for _, predictions in successful_results]
    model_names = [model_file for model_file, _ in successful_results]
    
    min_length = min(len(preds) for preds in all_predictions)
    if min_length == 0:
        print("no valid rocket predictions")
        return [], [], {}
    
    for i in range(len(all_predictions)):
        all_predictions[i] = all_predictions[i][:min_length]
    
    if optimization_config.get('use_torch_optimization', True):
        try:
            if torch.cuda.is_available() and device == 'cuda':
                predictions_tensor = torch.tensor(all_predictions, dtype=torch.float32).cuda()
                ensemble_predictions = torch.mean(predictions_tensor, dim=0).cpu().numpy().tolist()
                if len(all_predictions) > 1:
                    ensemble_std_devs = torch.std(predictions_tensor, dim=0).cpu().numpy().tolist()
                else:
                    ensemble_std_devs = [0.0] * min_length
            else:
                predictions_array = np.array(all_predictions)
                ensemble_predictions = np.mean(predictions_array, axis=0).tolist()
                if len(all_predictions) > 1:
                    ensemble_std_devs = np.std(predictions_array, axis=0).tolist()
                else:
                    ensemble_std_devs = [0.0] * min_length
        except Exception as e:
            print(f"torch optimization failed: {e}")
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


def _worker_rocket_evaluate_single_model(args):
    try:
        model_file, data_provider_info, optimization_config, device, gpu_id = args
        
        if torch.cuda.is_available() and device == 'cuda':
            if gpu_id is not None:
                torch.cuda.set_device(gpu_id)
            device = torch.device(device)
        else:
            device = torch.device('cpu')
        
        from .C3_utils import prepare_predicting_dataset
        
        data_provider = prepare_predicting_dataset(
            data_provider_info['file'], 
            fingerprint_type=data_provider_info.get('fingerprint_type', 'Morgan'), 
            batch_size=data_provider_info.get('batch_size', 256), 
            shuffle=False
        )
        
        if model_file.endswith('.pt'):
            from .C3_utils import MolecularTransformer
            model = MolecularTransformer(
                input_features=2048, 
                output_features=1, 
                embedding_size=512, 
                layer_count=6,
                head_count=8, 
                hidden_size=2048, 
                dropout_rate=0.1
            )
            saved_state = torch.load(model_file, map_location=device)
            
            if 'model_parameters' in saved_state:
                model.load_state_dict(saved_state['model_parameters'])
            else:
                model.load_state_dict(saved_state)
            
            model.to(device)
        else:
            from .evaluate import load_multiple_models
            models = load_multiple_models([model_file])
            model = models[0]
            if hasattr(model, 'to'):
                model = model.to(device)
        
        if hasattr(model, 'eval'):
            model.eval()
        
        model_predictions = []
        
        with torch.no_grad():
            for features, _ in data_provider:
                if features is None:
                    continue
                
                features = features.to(device)
                outputs = model(features.float())
                probs = torch.sigmoid(outputs.squeeze()).float()
                batch_predictions = probs.cpu().numpy().tolist()
                model_predictions.extend(batch_predictions)
        
        return (True, model_file, model_predictions, None)
        
    except Exception as e:
        return (False, model_file, [], str(e))

