import torch
import os

def load_model_for_continue_training(network, optimizer, model_file, compute_device):
    try:
        if os.path.exists(model_file):
            saved_state = torch.load(model_file, map_location=compute_device)
            network.load_state_dict(saved_state['model_parameters'])
            optimizer.load_state_dict(saved_state['optimizer_state'])
            previous_epochs = saved_state.get('training_epoch', 0)
            return True, previous_epochs
        else:
            print(f"Model file {model_file} not found")
            return False, 0
    except Exception as e:
        print(f"Failed to load model: {str(e)}")
        return False, 0

def rocket_continue_train(model_file, data_handler, additional_epochs, optimal_parameters, 
                         compute_device, new_model_suffix='_continued'):
    print(f"Starting rocket continue training: {model_file}")
    
    from molactivity.C2_train import initialize_network_and_optimizer, execute_training
    from molactivity.C3_utils import store_model
    
    network, optimizer = initialize_network_and_optimizer(compute_device, optimal_parameters)
    
    success, previous_epochs = load_model_for_continue_training(network, optimizer, model_file, compute_device)
    
    if not success:
        print("Failed to load model for continue training")
        return None
    
    print(f'--- continuing training for {model_file} ---')
    execute_training(network, data_handler, epochs=additional_epochs, device=compute_device, 
                   optimizer=optimizer, start_epoch=previous_epochs, model_id=1)
    
    base_name = model_file.rsplit('.', 1)[0]
    extension = model_file.rsplit('.', 1)[1] if '.' in model_file else 'pt'
    new_model_file = f"{base_name}{new_model_suffix}.{extension}"
    
    store_model(network, optimizer, previous_epochs + additional_epochs, new_model_file)
    print(f"Continue training completed. New model saved: {new_model_file}")
    
    return network, new_model_file

def rocket_parallel_training(num_networks, optimal_parameters, compute_device, dataset_file, 
                           max_workers, epochs, batch_size):
    
    from molactivity.C2_train import initialize_network_and_optimizer, execute_training
    from molactivity.C3_utils import prepare_training_dataset, store_model
    import concurrent.futures
    
    def train_single_network(network_idx):
        try:
            print(f"Starting training for network {network_idx+1}")
            
            network, optimizer = initialize_network_and_optimizer(compute_device, optimal_parameters)
            
            data_handler = prepare_training_dataset(
                dataset_file, 
                fingerprint_type='Morgan', 
                batch_size=batch_size, 
                shuffle=False, 
                balance_data=True
            )
            
            execute_training(
                network, 
                data_handler, 
                epochs=epochs, 
                device=compute_device, 
                optimizer=optimizer, 
                start_epoch=0, 
                model_id=network_idx+1
            )
            
            model_file = f'model_{network_idx+1}.pt'
            store_model(network, optimizer, epochs, model_file)
            print(f"Network {network_idx+1} training completed and saved to {model_file}")
            
            return network_idx, True, model_file
            
        except Exception as e:
            print(f"Network {network_idx+1} training failed: {str(e)}")
            return network_idx, False, str(e)
    
    successful_models = []
    failed_models = []
    
    if max_workers is None:
        max_workers = min(num_networks, 4)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(train_single_network, i) for i in range(num_networks)]
        
        for future in concurrent.futures.as_completed(futures):
            network_idx, success, result = future.result()
            if success:
                successful_models.append(result)
            else:
                failed_models.append((network_idx, result))
    
    print(f"Parallel training completed. Success: {len(successful_models)}, Failed: {len(failed_models)}")
    
    if failed_models:
        print("Failed models:")
        for network_idx, error in failed_models:
            print(f"  Network {network_idx+1}: {error}")
    
    return successful_models