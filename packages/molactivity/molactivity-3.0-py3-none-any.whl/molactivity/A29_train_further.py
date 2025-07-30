from .A26_tensor import Tensor
from .A31_transformer import MolecularTransformer
from .A18_optimizer import Adam
from .A14_model_save_load import load, dump
from .A13_loss import FocalLoss
from .A16_operations import sigmoid

def flatten_nested_dict(d, prefix="", separator="."):
    if d is None:
        print("ERROR. dict is None")
        return {}
        
    if not isinstance(d, dict):
        print(f"ERROR. not dict type, the type is: {type(d)}")
        return {}
    
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
        print(f"ERROR. {e} {d}")
        return {}
        
    return flattened

def load_model_for_continue_training(network, optimizer, model_file):

    try:
        with open(model_file, 'rb') as f:
            saved_state = load(f)
        
        print("model loaded successfully")
        
        saved_model_params = saved_state['model_parameters']
        flattened_params = flatten_nested_dict(saved_model_params)
        
        param_dict = dict(network.named_parameters())
        loaded_count = 0
        
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
                    from . import A2_arrays as arrays
                    param.data = arrays.array(saved_param)
                loaded_count += 1
        
        
        if 'optimizer_state' in saved_state and saved_state['optimizer_state']:
            optimizer.load_state_dict(saved_state['optimizer_state'])

        
        previous_epochs = saved_state.get('epoch', 0)
        
        return True, previous_epochs
        
    except Exception as e:
        print(f"model loading failed: {str(e)}")
        return False, 0

def continue_train(model_file, data_handler, additional_epochs=2, activation='gelu', 
                  optimal_parameters=None, network_index=0, new_model_suffix='_continued'):
 
    print(f"starting further training: {model_file}")
    
    if optimal_parameters is None:
        optimal_parameters = {
            'learning_rate': 0.001,
            'transformer_depth': 2,
            'attention_heads': 2,
            'hidden_dimension': 64
        }
    
    network = MolecularTransformer(
        input_features=2048,
        output_features=1, 
        embedding_size=128,
        layer_count=optimal_parameters['transformer_depth'],
        head_count=optimal_parameters['attention_heads'], 
        hidden_size=optimal_parameters['hidden_dimension'], 
        dropout_rate=0.1,
        activation=activation
    )
    
    optimizer = Adam(network.parameters(), lr=optimal_parameters['learning_rate'])
    
    success, previous_epochs = load_model_for_continue_training(network, optimizer, model_file)
    
    if not success:
        print("failed to load model")
        return None
        
    criterion = FocalLoss(alpha=0.25, gamma=2.0, high_pred_penalty=5.0, reduction='mean')
    
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
            if batch_count % 10 == 0:
                print(f"    batch {batch_count}, loss: {loss_value:.4f}")
        
        avg_loss = sum(epoch_losses) / len(epoch_losses) if epoch_losses else 0
        
        if all_predictions:
            min_pred = min(all_predictions)
            max_pred = max(all_predictions)
            print(f"  Epoch {current_epoch},avg loss: {avg_loss:.4f}, range: [{min_pred:.4f}, {max_pred:.4f}]")
    
    base_name = model_file.rsplit('.', 1)[0] 
    extension = model_file.rsplit('.', 1)[1] if '.' in model_file else 'dict'
    new_model_file = f"{base_name}{new_model_suffix}.{extension}"
    
    print(f"model saved: {new_model_file}")
    
    model_params = network.state_dict()
    
    if model_params is None:
        print("model_params is None")
        return None
    
    if not isinstance(model_params, dict):
        print(f"model not dict type, the type is: {type(model_params)}")
        return None
        
    if len(model_params) == 0:
        print("model_params is None")
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
            dump(save_data, f)
                
    except Exception as e:
        print(f"failed to save model: {e}")

        return None
    
    print("further training completed")
    
    return network, new_model_file 