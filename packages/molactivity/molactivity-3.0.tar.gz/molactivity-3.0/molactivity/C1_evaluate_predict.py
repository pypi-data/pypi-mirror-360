import torch
from .C3_utils import configure_settings, prepare_predicting_dataset, MolecularTransformer
import os
import numpy as np

def load_trained_network(network, model_file, compute_device):
    if os.path.exists(model_file):
        try:
            saved_state = torch.load(model_file, map_location=compute_device)
            
            if 'model_parameters' in saved_state:
                network.load_state_dict(saved_state['model_parameters'])
            else:
                network.load_state_dict(saved_state)
            
            network = network.to(compute_device)
            
            total_params = sum(p.numel() for p in network.parameters())
            print(f"Successfully loaded model from {model_file} with {total_params} parameters")
            
            return network
        except Exception as e:
            print(f"Error loading model {model_file}: {e}")
            return None
    else:
        print(f"Model file {model_file} not found")
        return None

def generate_predictions(model, data_provider, device='cpu'):
    model.eval()
    model = model.to(device) 
    predictions = []
    with torch.no_grad():
        for features, _ in data_provider:
            if features is None:
                continue
            features = features.to(device)
            outputs = model(features.float())
            probs = torch.sigmoid(outputs.squeeze()).float()
            predictions.extend(probs.cpu().numpy().tolist())
    return predictions

def append_predictions_to_data(data, predictions):
    data['prediction_score'] = predictions
    return data

def calculate_dynamic_threshold(predictions, labels, target_fpr=0.01):
    min_threshold = 0.98
    thresholds = np.linspace(min_threshold, 1.0, 100)
    best_threshold = min_threshold
    
    for threshold in thresholds:
        pred_labels = (predictions >= threshold).astype(int)
        fpr = np.sum((pred_labels == 1) & (labels == 0)) / np.sum(labels == 0)
        if fpr <= target_fpr:
            best_threshold = threshold
            break
    
    return best_threshold

def predict_and_save(model, data_provider, output_file, device='cpu', predictions=None):
    if predictions is None:
        predictions = generate_predictions(model, data_provider, device)
    
    data = data_provider.dataset.molecular_data.copy()
    
    data['prediction_score'] = predictions
    
    data.to_csv(output_file, index=False)

def prediction():
    parameters = configure_settings()
    compute_device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f'Computation device: {compute_device}')

    prediction_provider = prepare_predicting_dataset('training_dataset2.csv', fingerprint_type='Morgan', 
                                        batch_size=32, shuffle=False, balance_data=False)

    trained_networks = []
    for idx in range(parameters.num_networks):
        model_path = f'model_{idx+1}.pt'
        if not os.path.exists(model_path):
            print(f'Warning: Model file {model_path} not located')
            continue
            
        network = MolecularTransformer(input_features=2048, output_features=1, 
                                     embedding_size=512, layer_count=6, 
                                     head_count=8, hidden_size=2048, 
                                     dropout_rate=0.1)
        network = network.to(compute_device)  
        
        network = load_trained_network(network, model_path, compute_device)
        if network is None:
            print(f'Failed to load model {idx+1}')
            continue
            
        network.eval()
        trained_networks.append(network)
        print(f'Model {idx+1} loaded successfully')

    if not trained_networks:
        print('No trained network models available! Execute training first.')
        return

    ensemble_predictions = []
    for network_idx, network in enumerate(trained_networks):
        print(f'Starting predictions with model {network_idx+1}...')
        current_predictions = generate_predictions(network, prediction_provider, device=compute_device)
        ensemble_predictions.append(current_predictions)
        print('Predictions completed')

    ensemble_predictions = np.array(ensemble_predictions)
    
    averaged_predictions = np.mean(ensemble_predictions, axis=0)
    
    result_file = 'evaluating_dataset_with_predictions.csv'
    predict_and_save(trained_networks[0], prediction_provider, result_file, device=compute_device, predictions=averaged_predictions)
    print(f'Prediction results saved to {result_file}')

if __name__ == '__main__':
    prediction()

