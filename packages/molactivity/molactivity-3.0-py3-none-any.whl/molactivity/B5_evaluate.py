
from .B16_tensor import Tensor
from .B13_operations import sigmoid
from .B15_prepare_data import prepare_pure_predicting_dataset
from .B9_transformer import MolecularTransformer
import pickle
import numpy as np
from .A9_evaluate import (parse_model_selection, flatten_nested_dict,save_predictions_to_csv,
                          analyze_prediction_quality)

def load_trained_network_pure(network, model_file):

    try:
        with open(model_file, 'rb') as f:
            saved_state = pickle.load(f)
                            
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
                        param.data = np.array(array_data)
                    else:
                        param.data = np.array(saved_param)
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
        embedding_size=512, 
        layer_count=6,
        head_count=8, 
        hidden_size=2048, 
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
        return []
    
    min_length = min(len(preds) for preds in all_predictions)
    if min_length == 0:
        print("no valid predictions")
        return []
    
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
            print(f"{model_name}: average={avg_pred:.4f}, range=[{min_pred:.4f}, {max_pred:.4f}]")
    
    return ensemble_predictions, ensemble_std_devs, individual_predictions


def main(device='cpu', model_file='model_1.dict', models='auto', ensemble=True):

    print("Start evaluating")
    
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
        
        import sys
        if len(sys.argv) > 1: 
            parameters = config_parser.parse_args()
            device = parameters.device
            model_file = parameters.model_file
            models = parameters.models
            ensemble = parameters.ensemble and not parameters.single
            print(f"device: {device}")

        else:
            print(f"device: {device}")
            
    except:
        pass

    input_dataset_file = 'evaluating_dataset_c.csv'
    data_provider = prepare_pure_predicting_dataset(input_dataset_file, fingerprint_type='Morgan', 
                                                  batch_size=32, shuffle=False)
    
        
    model_files = parse_model_selection(models)
        
    print(f"using {len(model_files)} for evaluating")
        
    loaded_models = load_multiple_models(model_files)

    predictions, std_devs, individual_predictions = generate_ensemble_predictions(loaded_models, data_provider, model_files=model_files)
            
    output_file = 'evaluating_dataset_with_predictions.csv'
    if predictions:
        if ensemble and 'std_devs' in locals():
            save_success = save_predictions_to_csv(predictions, output_file, std_devs, individual_predictions, input_file=input_dataset_file)
        else:
            save_success = save_predictions_to_csv(predictions, output_file, individual_predictions=individual_predictions, input_file=input_dataset_file)
        
        if save_success:
            analyze_prediction_quality(output_file)
        else:
            pass
    else:
        print("no predictions to save")
    