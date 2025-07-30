import torch
from .C3_utils import FocalLoss, store_model, configure_settings, prepare_training_dataset, MolecularTransformer
import concurrent.futures
import threading

print_lock = threading.Lock()

def initialize_network_and_optimizer(compute_device, optimal_parameters):
    network = MolecularTransformer(
        input_features=2048, 
        output_features=1, 
        embedding_size=512, 
        layer_count=optimal_parameters['transformer_depth'],
        head_count=optimal_parameters['attention_heads'], 
        hidden_size=optimal_parameters['hidden_dimension'], 
        dropout_rate=0.1
    )
    network.to(compute_device)
    optimizer = torch.optim.Adam(network.parameters(), lr=optimal_parameters['learning_rate'])
    return network, optimizer

def conduct_individual_training(network, data_handler, compute_device, optimization_engine, initial_epoch, total_epochs, network_id):
    with print_lock:
        print(f'--- training model {network_id+1} ---')
    execute_training(network, data_handler, epochs=total_epochs, device=compute_device, 
                   optimizer=optimization_engine, start_epoch=initial_epoch, model_id=network_id+1)
    
    model_storage_path = f'model_{network_id+1}.pt'
    store_model(network, optimization_engine, initial_epoch + total_epochs - 1, model_storage_path)
    with print_lock:
        print(f'Model {network_id+1} saved successfully')
    return network

def training():
    parameters = configure_settings()
    compute_device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    data_handler = prepare_training_dataset('training_dataset.csv', fingerprint_type='Morgan', 
                                 batch_size=32, shuffle=False, balance_data=True)
    
    optimal_parameters = {
        'learning_rate': 0.001,
        'transformer_depth': 6,
        'attention_heads': 8,
        'hidden_dimension': 2048
    }

    networks = []
    optimizers = []
    starting_epochs = []

    for _ in range(parameters.num_networks):
        network, optimizer = initialize_network_and_optimizer(compute_device, optimal_parameters)
        networks.append(network)
        optimizers.append(optimizer)
        starting_epochs.append(0)
    
    if parameters.parallel:
        print(f'Initiating parallel training for {parameters.num_networks} networks...')
        with concurrent.futures.ThreadPoolExecutor(max_workers=parameters.num_networks) as executor:
            training_tasks = [
                executor.submit(conduct_individual_training, network, data_handler, 
                              compute_device, optimizer, start_epoch, 1, idx)
                for idx, (network, optimizer, start_epoch) in enumerate(zip(networks, 
                                                                          optimizers, 
                                                                          starting_epochs))
            ]
            networks = [task.result() for task in concurrent.futures.as_completed(training_tasks)]
    else:
        print(f'Executing training for {parameters.num_networks} models...')
        for idx, (network, optimizer, start_epoch) in enumerate(zip(networks, 
                                                                  optimizers, 
                                                                  starting_epochs)):
            conduct_individual_training(network, data_handler, compute_device, 
                                      optimizer, start_epoch, 3, idx)

    print("Training process completed successfully!")

def execute_training(model, data_provider, epochs=10, device='cpu', optimizer=None, start_epoch=0, model_id=None):
    model.train()
    criterion = FocalLoss(alpha=0.25, gamma=2.0, high_pred_penalty=20.0, high_pred_threshold=0.9)
    
    sampler = data_provider.sampler if hasattr(data_provider, 'sampler') else None
    
    for epoch in range(start_epoch, start_epoch + epochs):
        total_loss = 0
        batch_losses = []
        all_predictions = []
        all_labels = []
        high_pred_false_count = 0
        very_high_pred_false_count = 0
        extreme_high_pred_false_count = 0
        
        for batch_idx, (features, labels) in enumerate(data_provider):
            if features is None or labels is None:
                continue
                
            features = features.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(features.float())
            loss = criterion(outputs.squeeze(), labels)
            loss.backward()
            
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.1)
            
            optimizer.step()
            
            batch_loss = loss.item()
            total_loss += batch_loss
            batch_losses.append(batch_loss)
            
            if (batch_idx + 1) % 20 == 0:
                model_prefix = f"[Model {model_id}] " if model_id is not None else ""
                with print_lock:
                    print(f"    {model_prefix}batch {batch_idx + 1}, loss: {batch_loss:.4f}")
            
            with torch.no_grad():
                predictions = torch.sigmoid(outputs.squeeze())
                all_predictions.extend(predictions.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                
                high_pred_false = ((predictions > 0.9) & (labels == 0)).sum().item()
                very_high_pred_false = ((predictions > 0.95) & (labels == 0)).sum().item()
                extreme_high_pred_false = ((predictions > 0.99) & (labels == 0)).sum().item()
                
                high_pred_false_count += high_pred_false
                very_high_pred_false_count += very_high_pred_false
                extreme_high_pred_false_count += extreme_high_pred_false
        
        if sampler is not None and hasattr(sampler, 'update_hard_samples'):
            sampler.update_hard_samples(all_predictions, all_labels)
        
        avg_loss = total_loss / len(data_provider)
        
        model_prefix = f"[Model {model_id}] " if model_id is not None else ""
        with print_lock:
            print(f'  {model_prefix}Epoch {epoch+1}, avg loss: {avg_loss:.4f}, ')
            print(f'{model_prefix}High Pred False: {high_pred_false_count}, '
                  f'Very High Pred False: {very_high_pred_false_count}, '
                  f'Extreme High Pred False: {extreme_high_pred_false_count}')

if __name__ == '__main__':
    training()
