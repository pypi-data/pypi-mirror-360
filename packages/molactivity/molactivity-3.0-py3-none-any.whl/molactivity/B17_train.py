from .B15_prepare_data import prepare_pure_training_dataset
from .B9_transformer import MolecularTransformer
from .B13_operations import sigmoid
from .B3_autograd import no_grad
from .B14_optimizer import Adam
from .B11_focal_loss import FocalLoss
from .B16_tensor import Tensor  

def initialize_network_and_optimizer(optimal_parameters, activation='gelu', input_features=2048, embedding_size=512):
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
    return network, optimizer

def conduct_individual_training(network, data_handler, optimizer, network_index, model_version, unique_id, epochs=2):
    
    criterion = FocalLoss(alpha=0.25, gamma=2.0, high_pred_penalty=2.0, reduction='mean')  
    
    for epoch in range(epochs): 
        epoch_losses = []
        batch_count = 0
        high_pred_false_count = 0
        very_high_pred_false_count = 0 
        extreme_high_pred_false_count = 0
        all_predictions = []
        
        for batch_idx, (features, labels) in enumerate(data_handler):
            batch_count += 1
  
            
            outputs = network(features) 
            
            if labels.data.ndim > 1:
                labels = Tensor(labels.data.squeeze(), requires_grad=False)
            
            loss = criterion(outputs.squeeze(), labels)
            
            loss_value = loss.data.item() if hasattr(loss.data, 'item') else float(loss.data)
            if loss_value > 5.0:
                    print(f"note: very high loss {loss_value:.4f}, pass update")
                    continue
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_losses.append(loss_value)
            
            with no_grad():
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
            
            print(f"    batch {batch_count}, loss: {loss_value:.4f}")
        
        avg_loss = sum(epoch_losses) / len(epoch_losses) if epoch_losses else 0
        print(f"  Epoch [{epoch+1}/{epochs}], avg_loss: {avg_loss:.4f}, "
              f"High Pred False: {high_pred_false_count}, "
              f"Very High Pred False: {very_high_pred_false_count}, "
              f"Extreme High Pred False: {extreme_high_pred_false_count}")
        
        if all_predictions:
            min_pred = min(all_predictions)
            max_pred = max(all_predictions)
            print(f"  Epoch {epoch+1} pred range: [{min_pred:.4f}, {max_pred:.4f}]")
    
    model_filename = f'model_{unique_id+1}.dict'
   
    import pickle
    save_data = {
        'model_parameters': network.state_dict(),
        'optimizer_state': optimizer.state_dict(),
        'epoch': epochs
    }
    with open(model_filename, 'wb') as f:
        pickle.dump(save_data, f)
 
    
    print(f"model {unique_id+1} training complete")
    return network

def prepare_pure_training_dataset(dataset_file, fingerprint_type='Morgan', batch_size=32, shuffle=False, balance_data=True):
    from .B15_prepare_data import prepare_pure_training_dataset as _prepare_pure_training_dataset
    return _prepare_pure_training_dataset(dataset_file, fingerprint_type, batch_size, shuffle, balance_data)

def training():
    from .A6_argument_parser import CommandLineProcessor  
    
    config_parser = CommandLineProcessor(description='Molecular property prediction')
    config_parser.add_argument('--num_networks', type=int, default=1, 
                             help='Quantity of networks to train')
    config_parser.add_argument('--activation', type=str, default='gelu', choices=['relu', 'gelu'],
                             help='activation: relu or gelu (default: gelu)')
    parameters = config_parser.parse_args()

 
    data_handler = prepare_pure_training_dataset('training_dataset.csv', fingerprint_type='Morgan', 
                                               batch_size=32, shuffle=False, balance_data=True)

    optimal_parameters = {
        'learning_rate': 0.001,
        'transformer_depth': 6,  
        'attention_heads': 8,   
        'hidden_dimension': 512  
    }

    trained_networks = []
    
    for network_idx in range(parameters.num_networks):
        network, optimizer = initialize_network_and_optimizer(optimal_parameters, parameters.activation, 2048, 512)
        
        trained_network = conduct_individual_training(
            network, data_handler, optimizer, 0, 2, network_idx, 2
        )
        trained_networks.append(trained_network)


