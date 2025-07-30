from .A26_tensor import Tensor
from .A16_operations import sigmoid
from .A19_prepare_data import prepare_pure_predicting_dataset
from .A31_transformer import MolecularTransformer
from .A14_model_save_load import load
from . import A2_arrays as arrays
from . import A7_data_process as dp
from .A27_tools import path_available
import glob

def discover_model_files(pattern='model_*.dict'):
  
    model_files = glob.glob(pattern)
    
    if not model_files:
        print(f"did not find models")
        return []
    
    def extract_number(filename):
        import re
        match = re.search(r'model_(\d+)\.dict', filename)
        return int(match.group(1)) if match else 0
    
    model_files.sort(key=extract_number)
    
    print(f"find {len(model_files)} models: {model_files}")
    return model_files

def parse_model_selection(model_selection):
   
    if not model_selection or model_selection.lower() in ['all', 'auto']:
        return discover_model_files()
    
    if ',' in model_selection:
        parts = [part.strip() for part in model_selection.split(',')]
        model_files = []
        
        for part in parts:
            if part.endswith('.dict'):
                if path_available(part):
                    model_files.append(part)
                else:
                    print(f"did not find models")
            elif part.isdigit():
                filename = f"model_{part}.dict"
                if path_available(filename):
                    model_files.append(filename)
                else:
                    print(f"did not find models")
            elif '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    for i in range(start, end + 1):
                        filename = f"model_{i}.dict"
                        if path_available(filename):
                            model_files.append(filename)
                        else:
                            print(f"did not find models")
                except ValueError:
                    print(f"no valid models")
        
        return model_files
    
    elif model_selection.endswith('.dict'):
        if path_available(model_selection):
            return [model_selection]
        else:
            print(f"did not find models")
            return []
    elif model_selection.isdigit():
        filename = f"model_{model_selection}.dict"
        if path_available(filename):
            return [filename]
        else:
            print(f"did not find models")
            return []
    else:
        print(f"no valid models")
        return []

def flatten_nested_dict(d, prefix="", separator="."):

    flattened = {}
    try:
        for key, value in d.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key
            if isinstance(value, dict):
                nested_result = flatten_nested_dict(value, new_key, separator)
                if nested_result is not None:
                    flattened.update(nested_result)
            else:
                flattened[new_key] = value
    except Exception as e:
        return {}
        
    return flattened

def load_trained_network_pure(network, model_file):

    try:
        with open(model_file, 'rb') as f:
            saved_state = load(f)
                            
        saved_parameters = saved_state['model_parameters']

        flattened_params = flatten_nested_dict(saved_parameters)

        param_dict = dict(network.named_parameters())
            
        loaded_count = 0
        missing_params = []
        for name, param in param_dict.items():
            if name in flattened_params:
                saved_param = flattened_params[name]
                    
                if isinstance(saved_param, dict) and saved_param.get('__type__') == 'FinalArrayCompatible':
                    from .A10_final_array import FinalArrayCompatible
                    restored_data = FinalArrayCompatible(
                        saved_param['data'], 
                        saved_param['shape'], 
                        saved_param['dtype']
                    )
                    param.data = restored_data
                elif isinstance(saved_param, Tensor):
                    param.data = saved_param.data
                elif hasattr(saved_param, 'shape'):  
                    param.data = saved_param
                else:
                    if hasattr(saved_param, 'data'):
                        array_data = saved_param.data
                        param.data = arrays.asarray_numpy_compatible(array_data).data
                    else:
                        param.data = arrays.asarray_numpy_compatible(saved_param).data
                loaded_count += 1
            else:
                missing_params.append(name)

        return loaded_count > 0 
            
    except Exception as e:
        print(f"loading model failed: {str(e)}")
        return False


def create_network():
    
    network = MolecularTransformer(
        input_features=2048, 
        output_features=1, 
        embedding_size=128, #512
        layer_count=2,
        head_count=2,  #4
        hidden_size=64, #512
        dropout_rate=0.1
    )
    
    return network

def load_multiple_models(model_files, use_gpu=False):

    models = []
    
    for model_file in model_files:
        
        network = create_network()
        load_trained_network_pure(network, model_file)
        models.append(network)
    
    return models

def generate_ensemble_predictions(models, data_provider, use_gpu=False, model_files=None):
    
    all_predictions = []  
    for model_idx, model in enumerate(models):
        
        model.eval()
        model_predictions = []
        
        try:
            for batch_idx, (features, _) in enumerate(data_provider):
                if features is None:
                    continue
                
                if not isinstance(features, Tensor):
                    features = Tensor(features, requires_grad=False)
                
                try:
                    outputs = model(features)
                    outputs_squeezed = outputs.squeeze()
                    probs_tensor = sigmoid(outputs_squeezed)
                    
                    if hasattr(probs_tensor.data, 'flatten'):
                        batch_predictions = probs_tensor.data.flatten().tolist()
                    elif hasattr(probs_tensor.data, 'tolist'):
                        batch_predictions = probs_tensor.data.tolist()
                    elif isinstance(probs_tensor.data, (list, tuple)):
                        batch_predictions = list(probs_tensor.data)
                    else:
                        batch_predictions = [float(probs_tensor.data)]
                    
                    model_predictions.extend(batch_predictions)
                    
                except Exception as e:
                    continue
        except:
            pass
        all_predictions.append(model_predictions)
    
    if not all_predictions:
        print("predictions failed")
        return [], [], {}
    
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
    if model_files:
        for model_idx, model_file in enumerate(model_files):
            if model_idx < len(all_predictions):
                individual_predictions[model_file] = all_predictions[model_idx]
    else:
        for model_idx, preds in enumerate(all_predictions):
            model_name = f"model_{model_idx + 1}.dict"
            individual_predictions[model_name] = preds
    
    print(f"Predictions completed, return {len(ensemble_predictions)} predictions")
    
    for model_idx, preds in enumerate(all_predictions):
        if preds:
            avg_pred = sum(preds) / len(preds)
            min_pred = min(preds)
            max_pred = max(preds)
            model_name = model_files[model_idx] if model_files and model_idx < len(model_files) else f"model_{model_idx + 1}"
    
    return ensemble_predictions, ensemble_std_devs, individual_predictions


def save_predictions_to_csv(predictions, output_file='predicting_dataset_with_predictions.csv', std_devs=None, individual_predictions=None, input_file=None):

    try:
        if input_file is None:
            input_file = 'predicting_dataset.csv'
            
        original_data = dp.read_csv(input_file)
        
        try:
            eval_data = dp.read_csv(input_file)
            has_activity_labels = 'ACTIVITY' in eval_data.columns
            if has_activity_labels:
                if len(original_data) == len(eval_data):
                    original_data_dict = original_data.to_dict()
                    original_data_dict['ACTIVITY'] = eval_data['ACTIVITY']
                    original_data = dp.DataTable(original_data_dict)
                else:
                    pass
        except Exception as e:
            pass
        
        if len(predictions) != len(original_data):
            while len(predictions) < len(original_data):
                predictions.append(0.0)
                if std_devs is not None:
                    std_devs.append(0.0)
            if len(predictions) > len(original_data):
                predictions = predictions[:len(original_data)]
                if std_devs is not None:
                    std_devs = std_devs[:len(original_data)]
        
        original_data_dict = original_data.to_dict()
        original_data_dict['ENSEMBLE_PREDICTION'] = predictions
        
        if std_devs is not None:
            original_data_dict['ENSEMBLE_STD_DEV'] = std_devs
        
        if individual_predictions is not None:
            for model_name, model_preds in individual_predictions.items():
                if len(model_preds) != len(original_data):
                    while len(model_preds) < len(original_data):
                        model_preds.append(0.0)
                    if len(model_preds) > len(original_data):
                        model_preds = model_preds[:len(original_data)]
                
                column_name = model_name.replace('.dict', '').upper()
                original_data_dict[f'PRED_{column_name}'] = model_preds
        
        result_data = dp.DataTable(original_data_dict)
        
        result_data.to_csv(output_file)
        
        print(f"predictions saved to: {output_file}")
        if individual_predictions:
            print(f"saved {len(individual_predictions)} individual model predictions")
              
        return True
        
    except Exception as e:
        print(f"failed to save predictions: {e}")
        return False

def main(device='cpu', model_file='model_1.dict', models='auto', ensemble=True):

    print("Start predicting")
    
    try:
        from .A6_argument_parser import ArgumentProcessor
        
        config_parser = ArgumentProcessor(description='Molecular property prediction')
        config_parser.add_argument('--device', type=str, default=device, choices=['cpu', 'gpu'],
                                 help='select device: cpu or gpu (default: cpu)')
        config_parser.add_argument('--model_file', type=str, default=model_file,
                                 help=f'model name (default: {model_file})')
        config_parser.add_argument('--models', type=str, default=models,
                                 help='model choice: "auto"/"all", "1,3,5"(specific), "1-3"(range), or model name')
        config_parser.add_argument('--ensemble', action='store_true', default=ensemble,
                                 help='using ensemble (default: True)')
        config_parser.add_argument('--parallel', action='store_true',
                                 help='using parallel prediction (default: one by one)')
        config_parser.add_argument('--max_workers', type=int, default=None,
                                 help='max_workers for parallel prediction (default: auto)')
        
        import sys
        if len(sys.argv) > 1: 
            parameters = config_parser.parse_args()
            device = parameters.device
            model_file = parameters.model_file
            models = parameters.models
            ensemble = parameters.ensemble and not parameters.single
            parallel = parameters.parallel
            max_workers = parameters.max_workers
            print(f"device: {device}")
            if parallel:
                print(f"parallel prediction: enabled")
                if max_workers:
                    print(f"max workers: {max_workers}")

        else:
            print(f"device: {device}")
            parallel = False
            max_workers = None
            
    except:
        parallel = False
        max_workers = None

    input_dataset_file = 'predicting_dataset.csv' 
    data_provider = prepare_pure_predicting_dataset(input_dataset_file, fingerprint_type='Morgan', 
                                                  batch_size=32, shuffle=False)
    
        
    model_files = parse_model_selection(models)
        
    print(f"using {len(model_files)} for predicting")
    
    use_gpu = False
    if device == 'gpu':
        try:
            from .gpu_t import check_gpu_available, get_gpu_info
            if check_gpu_available():
                print(f"using GPU: {get_gpu_info()}")
                use_gpu = True
            else:
                print("GPU not available, using CPU")
        except ImportError:
            print("GPU not available, using CPU")
    
    if parallel and len(model_files) > 1:
        print("using parallel prediction")
        try:
            from .A30_eval_parallel import generate_parallel_ensemble_predictions
            
            predictions, std_devs = generate_parallel_ensemble_predictions(
                model_files=model_files,
                dataset_file=input_dataset_file,
                max_workers=max_workers,
                use_gpu=use_gpu
            )
            
            print(f"parallel prediction completed: {len(predictions)} predictions")
            
        except ImportError as e:
            print(f"parallel prediction failed: {e}")
            print("using sequential prediction...")
            parallel = False
        except Exception as e:
            print(f"parallel prediction failed: {e}")
            print("using sequential prediction...")
            parallel = False
    
    if not parallel or len(model_files) == 1:
        print("using sequential prediction...")
        loaded_models = load_multiple_models(model_files, use_gpu=use_gpu)
        predictions, std_devs, individual_predictions = generate_ensemble_predictions(loaded_models, data_provider, use_gpu=use_gpu, model_files=model_files)
            
    output_file = 'predicting_dataset_with_predictions.csv'
    if predictions:
        if ensemble and 'std_devs' in locals():
            save_success = save_predictions_to_csv(predictions, output_file, std_devs, individual_predictions, input_file=input_dataset_file)
        else:
            save_success = save_predictions_to_csv(predictions, output_file, individual_predictions=individual_predictions, input_file=input_dataset_file)
        
    else:
        print("no predictions to save")
    
