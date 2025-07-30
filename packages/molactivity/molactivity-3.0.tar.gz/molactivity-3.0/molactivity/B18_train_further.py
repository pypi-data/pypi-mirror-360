from .B9_transformer import MolecularTransformer
from .B13_operations import sigmoid
from .B14_optimizer import Adam
from .B11_focal_loss import FocalLoss
from .B16_tensor import Tensor
from .B5_evaluate import flatten_nested_dict
import pickle
import numpy as np

def load_model_for_fast_continue_training(network, optimizer, model_file):
    try:
        with open(model_file, 'rb') as f:
            saved_state = pickle.load(f)
        
        
        saved_model_params = saved_state['model_parameters']
        flattened_params = flatten_nested_dict(saved_model_params)
        
        param_dict = dict(network.named_parameters())
        loaded_count = 0
        
        for name, param in param_dict.items():
            if name in flattened_params:
                saved_param = flattened_params[name]
                
                try:
                    if isinstance(saved_param, Tensor):
                        if hasattr(saved_param.data, 'copy'):
                            param._data = saved_param.data.copy()
                        else:
                            param._data = np.array(saved_param.data, dtype=np.float32)
                    elif hasattr(saved_param, 'data'):
                        data = saved_param.data
                        if hasattr(data, 'copy'):
                            param._data = data.copy()
                        else:
                            param._data = np.array(data, dtype=np.float32)
                    elif isinstance(saved_param, np.ndarray):
                        param._data = saved_param.copy()
                    elif hasattr(saved_param, 'copy'):
                        param._data = saved_param.copy()
                    else:
                        param._data = np.array(saved_param, dtype=np.float32)
                    
                    param.requires_grad = True
                    if hasattr(param, 'shape'):
                        param.shape = param._data.shape
                        
                    loaded_count += 1
                except Exception as e:
              
                    continue
        
        
        if 'optimizer_state' in saved_state and saved_state['optimizer_state']:
            try:
                optimizer.load_state_dict(saved_state['optimizer_state'])
            except Exception as e:
                print(f"optimizer failed: {e}")
        
        previous_epochs = saved_state.get('epoch', 0)
        
        return True, previous_epochs
        
    except Exception as e:
        print(f"model loaded failed: {str(e)}")
        return False, 0

def fast_continue_train(model_file, data_handler, additional_epochs=2, activation='gelu', 
                       optimal_parameters=None, network_index=0, new_model_suffix='_continued',
                       input_features=2048, embedding_size=512):
    
    if optimal_parameters is None:
        optimal_parameters = {
            'learning_rate': 0.001,
            'transformer_depth': 6,
            'attention_heads': 8,
            'hidden_dimension': 512
        }
    
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
    
    success, previous_epochs = load_model_for_fast_continue_training(network, optimizer, model_file)
    
    if not success:
        print("model loading failed")
        return None
        
    criterion = FocalLoss(alpha=0.25, gamma=2.0, high_pred_penalty=2.0, reduction='mean')
        
    for epoch in range(additional_epochs):
        current_epoch = epoch + 1
        
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
            
            if loss_value > 5.0:
                print(f"very high loss {loss_value:.4f}, no update")
                continue
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_losses.append(loss_value)
            
            try:
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
            except:
                pass
                
            print(f"    batch {batch_count}, loss: {loss_value:.4f}")
        
        avg_loss = sum(epoch_losses) / len(epoch_losses) if epoch_losses else 0
        print(f"  Epoch [{current_epoch}/{additional_epochs}], avg_loss: {avg_loss:.4f}, "
              f"High Pred False: {high_pred_false_count}, "
              f"Very High Pred False: {very_high_pred_false_count}, "
              f"Extreme High Pred False: {extreme_high_pred_false_count}")
        
        if all_predictions:
            min_pred = min(all_predictions)
            max_pred = max(all_predictions)
            print(f"  Epoch {current_epoch} pred range: [{min_pred:.4f}, {max_pred:.4f}]")
    
    base_name = model_file.rsplit('.', 1)[0] 
    extension = model_file.rsplit('.', 1)[1] if '.' in model_file else 'dict'
    new_model_file = f"{base_name}{new_model_suffix}.{extension}"
    
    
    model_params = network.state_dict()
    
    if model_params is None or len(model_params) == 0:
        return None
    
    try:
        optimizer_state = optimizer.state_dict()
    except Exception as e:
        optimizer_state = {}
    
    save_data = {
        'model_parameters': model_params,
        'optimizer_state': optimizer_state,
        'epoch': previous_epochs + additional_epochs
    }
    
    try:
        with open(new_model_file, 'wb') as f:
            pickle.dump(save_data, f)
                
    except Exception as e:
        return None
    
    
    return network, new_model_file 