
import multiprocessing as mp

def _worker_train_single_model(args):

    try:
        model_idx, optimal_parameters, activation, use_gpu, dataset_info, input_features, embedding_size, epochs = args
        
        from .A19_prepare_data import prepare_pure_training_dataset
        from .A31_transformer import MolecularTransformer
        from .A16_operations import sigmoid
        from .A18_optimizer import Adam
        from .A13_loss import FocalLoss
        from .A26_tensor import Tensor
        from .A14_model_save_load import dump
        
        data_handler = prepare_pure_training_dataset(
            dataset_info['file'], 
            fingerprint_type=dataset_info.get('fingerprint_type', 'Morgan'), 
            batch_size=dataset_info.get('batch_size', 32), 
            shuffle=dataset_info.get('shuffle', False), 
            balance_data=dataset_info.get('balance_data', True)
        )
        
        network = MolecularTransformer(
            input_features=input_features,
            output_features=1, 
            embedding_size=embedding_size,
            layer_count=optimal_parameters['transformer_depth'],
            head_count=optimal_parameters['attention_heads'], 
            hidden_size=optimal_parameters['hidden_dimension'], 
            dropout_rate=0.1,
            activation=activation
        )
        optimizer = Adam(network.parameters(), lr=optimal_parameters['learning_rate'])
                
        criterion = FocalLoss(alpha=0.25, gamma=2.0, high_pred_penalty=5.0, reduction='mean')
        
        for epoch in range(epochs):  #train epoch
            epoch_losses = []
            batch_count = 0
            high_pred_false_count = 0
            very_high_pred_false_count = 0 
            extreme_high_pred_false_count = 0
            all_predictions = []
            
            for batch_idx, (features, labels) in enumerate(data_handler):
                batch_count += 1
                
                if not isinstance(features, Tensor):
                    features = Tensor(features, requires_grad=False)
                if not isinstance(labels, Tensor):
                    labels = Tensor(labels, requires_grad=False)
                
                outputs = network(features)  
                
                if labels.data.ndim > 1:
                    labels = Tensor(labels.data.squeeze(), requires_grad=False)
                
                loss = criterion(outputs.squeeze(), labels)
                
                loss_value = loss.data.item() if hasattr(loss.data, 'item') else float(loss.data)
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                epoch_losses.append(loss_value)
                
                predictions = sigmoid(outputs.squeeze())
                all_predictions.extend(predictions.data.flatten().tolist())
                    
                pred_data = predictions.data.flatten()
                label_data = labels.data.flatten()
                    
                for pred, label in zip(pred_data, label_data):
                    if pred > 0.9 and label < 0.5:
                        high_pred_false_count += 1
                    if pred > 0.95 and label < 0.5:
                        very_high_pred_false_count += 1
                    if pred > 0.98 and label < 0.5:
                        extreme_high_pred_false_count += 1


                if batch_count % 5 == 0:
                    print(f"[ {model_idx+1}] batch {batch_count}, loss: {loss_value:.4f}")
            
            avg_loss = sum(epoch_losses) / len(epoch_losses) if epoch_losses else 0
            print(f"[ {model_idx+1}] Epoch {epoch+1}, loss: {avg_loss:.4f}, "
                  f"High Pred False: {high_pred_false_count}, "
                  f"Very High Pred False: {very_high_pred_false_count}, "
                  f"Extreme High Pred False: {extreme_high_pred_false_count}")
            
            if all_predictions:
                min_pred = min(all_predictions)
                max_pred = max(all_predictions)
                print(f"[ {model_idx+1}] Epoch {epoch+1} prediction range: [{min_pred:.4f}, {max_pred:.4f}]")
        
        model_filename = f'model_{model_idx+1}.dict'
        save_data = {
            'model_parameters': network.state_dict(),
            'optimizer_state': optimizer.state_dict(),
            'epoch': epochs
        }
        with open(model_filename, 'wb') as f:
            dump(save_data, f)
        
        print(f"[ {model_idx+1}] train complete，model saved to {model_filename}")
        return (True, model_idx, model_filename, None)
        
    except Exception as e:
        import traceback
        error_msg = f"[ {model_idx+1}] training failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return (False, model_idx, None, error_msg)


def parallel_training(num_networks, optimal_parameters, activation='gelu', use_gpu=False, 
                     dataset_file='training_dataset.csv', max_workers=None, 
                     input_features=2048, embedding_size=128, epochs=1, batch_size=32):
   
    if max_workers is None:
        cpu_count = mp.cpu_count()
        if num_networks <= cpu_count // 2:
            max_workers = num_networks
        else:
            max_workers = min(num_networks, cpu_count // 2, 4)  # max 4 workers
    
    
    dataset_info = {
        'file': dataset_file,
        'fingerprint_type': 'Morgan',
        'batch_size': batch_size,
        'shuffle': False,
        'balance_data': True
    }
    
    task_args = []
    for i in range(num_networks):
        task_args.append((i, optimal_parameters, activation, use_gpu, dataset_info, input_features, embedding_size, epochs))
    
    successful_models = []
    failed_models = []
        
    if max_workers == 1 or num_networks == 1:
        for args in task_args:
            result = _worker_train_single_model(args)
            if result is None:
                print(f"Warning: Worker returned None, skipping...")
                continue
            success, model_idx, model_file, error_msg = result
            if success:
                successful_models.append(model_file)
            else:
                failed_models.append((model_idx, error_msg))
    else:
        
        with mp.Pool(processes=max_workers) as pool:
         
            results = pool.map(_worker_train_single_model, task_args)
                
            for result in results:
                if result is None:
                    print(f"Warning: Worker returned None, skipping...")
                    continue
                success, model_idx, model_file, error_msg = result
                if success:
                    successful_models.append(model_file)
                else:
                    failed_models.append((model_idx, error_msg))
    
    return successful_models
