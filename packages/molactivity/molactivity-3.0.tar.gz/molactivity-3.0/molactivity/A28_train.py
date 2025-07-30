
from .A19_prepare_data import prepare_pure_training_dataset
from .A31_transformer import MolecularTransformer
from .A16_operations import sigmoid
from .A18_optimizer import Adam
from .A13_loss import FocalLoss
from .A26_tensor import Tensor
from .A29_train_further import continue_train
from .A14_model_save_load import dump
from .A6_argument_parser import ArgumentProcessor  
from .A30_train_parallel import parallel_training

def initialize_network_and_optimizer(optimal_parameters, activation='gelu', input_features=2048, embedding_size=128):
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

def conduct_individual_training(network, data_handler, optimizer, network_index, model_version, unique_id, epochs=1):
    
    criterion = FocalLoss(alpha=0.25, gamma=2.0, high_pred_penalty=5.0, reduction='mean')  
    
    for epoch in range(epochs):  # epochs to train
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
        
            print(f"    batch {batch_count}, loss: {loss_value:.4f}")
        
        avg_loss = sum(epoch_losses) / len(epoch_losses) if epoch_losses else 0
        print(f"  Epoch {epoch+1}, avg loss: {avg_loss:.4f}, "
)
        
        if all_predictions:
            min_pred = min(all_predictions)
            max_pred = max(all_predictions)
            print(f"Epoch {epoch+1} range: [{min_pred:.4f}, {max_pred:.4f}]")
    
    model_filename = f'model_{unique_id+1}.dict'
    
    save_data = {
        'model_parameters': network.state_dict(),
        'optimizer_state': optimizer.state_dict(),
        'epoch': epochs
    }
    with open(model_filename, 'wb') as f:
        dump(save_data, f)

    
    return network

def training():
    
    FORCE_PARALLEL_TRAINING = False
    DEFAULT_CONTINUE_TRAIN = False
    DEFAULT_MODEL_FILE = "model_1.dict"  
    DEFAULT_ADDITIONAL_EPOCHS = 1
    
    try:
        
        config_parser = ArgumentProcessor(description='Molecular property prediction')
        config_parser.add_argument('--num_networks', type=int, default=2, 
                                 help='Quantity of networks to train')
        config_parser.add_argument('--activation', type=str, default='gelu', choices=['relu', 'gelu'],
                                 help='activation: relu or gelu (default: gelu)')
        config_parser.add_argument('--device', type=str, default='gpu', choices=['cpu', 'gpu'],
                                 help='training device: cpu or gpu (default: cpu)')
        config_parser.add_argument('--parallel', action='store_true',
                                 help='using parallel training (default: one by one)')
        config_parser.add_argument('--max_workers', type=int, default=None,
                                 help='max_workers for parallel training (default: auto)')
        config_parser.add_argument('--continue_training', action='store_true',
                                 help=f'continue training (default: {DEFAULT_CONTINUE_TRAIN})')
        config_parser.add_argument('--model_file', type=str, default=DEFAULT_MODEL_FILE,
                                 help=f'model to be trained furter(default: {DEFAULT_MODEL_FILE})')
        config_parser.add_argument('--additional_epochs', type=int, default=DEFAULT_ADDITIONAL_EPOCHS,
                                 help=f'further train epochs(default: {DEFAULT_ADDITIONAL_EPOCHS})')
        config_parser.add_argument('--dataset', type=str, default='training_dataset.csv',
                                 help='file name for training_dataset (default: training_dataset.csv(）)')
        parameters = config_parser.parse_args()

        use_continue = parameters.continue_training or DEFAULT_CONTINUE_TRAIN
        model_file = parameters.model_file if parameters.model_file != DEFAULT_MODEL_FILE else DEFAULT_MODEL_FILE
        add_epochs = parameters.additional_epochs if parameters.additional_epochs != DEFAULT_ADDITIONAL_EPOCHS else DEFAULT_ADDITIONAL_EPOCHS

        if parameters.device == 'gpu':
            try:
                from .gpu_t import check_gpu_available, get_gpu_info
                if check_gpu_available():
                    print(f"using GPU: {get_gpu_info()}")
                    use_gpu = True
                else:
                    print("GPU not available, using CPU")
                    use_gpu = False
            except ImportError:
                print("GPU not available, using CPU")
                use_gpu = False
        else:
            print("using device: CPU")
            use_gpu = False

        if use_continue:
            print(f"loading model: {model_file}")
        else:
            print(f"number of models to train: {parameters.num_networks}")
            if parameters.parallel and parameters.max_workers:
                print(f"max workers: {parameters.max_workers}")
        print(f"dataset: {parameters.dataset}")

        data_handler = prepare_pure_training_dataset(parameters.dataset, fingerprint_type='Morgan', 
                                                   batch_size=32, shuffle=False, balance_data=True)
        
        optimal_parameters = {
            'learning_rate': 0.001,
            'transformer_depth': 2,   #6
            'attention_heads': 2, 
            'hidden_dimension': 64   #2048
        }

        if use_continue:
            result = continue_train(
                model_file=model_file,
                data_handler=data_handler,
                additional_epochs=add_epochs,
                activation=parameters.activation,
                optimal_parameters=optimal_parameters,
                new_model_suffix='_continued'
            )
            
            if result is not None:
                trained_network, new_model_file = result
            else:
                print(f"further train failed")
        else:
            
            if (FORCE_PARALLEL_TRAINING or parameters.parallel) and parameters.num_networks > 1:
                print("using parallel training")
                try:
                    
                    trained_model_files = parallel_training(
                        num_networks=parameters.num_networks,
                        optimal_parameters=optimal_parameters,
                        activation=parameters.activation,
                        use_gpu=use_gpu,
                        dataset_file=parameters.dataset,
                        max_workers=parameters.max_workers
                    )
                    
                    print(f"successfully trained {len(trained_model_files)} models")
                    print(f"model file: {trained_model_files}")
                    
                except ImportError as e:
                    print(f"parallel training failed: {e}")
                    print("train one by one...")
                    parameters.parallel = False
                except Exception as e:
                    print(f"parallel training failed: {e}")
                    print("train one by one......")
                    parameters.parallel = False
            
            if not (FORCE_PARALLEL_TRAINING or parameters.parallel) or parameters.num_networks == 1:
                print("train one by one...")
                
                if use_gpu:
                    try:
                        from .gpu_t import conduct_gpu_training
                        trained_networks = []
                        
                        for network_idx in range(parameters.num_networks):
                            print(f'\n--- training model {network_idx+1} ---')
                            network, optimizer = initialize_network_and_optimizer(optimal_parameters, parameters.activation)
                            
                            trained_network = conduct_gpu_training(
                                network, data_handler, optimizer, 0, 2, network_idx
                            )
                            trained_networks.append(trained_network)
                            
                    except Exception as e:
                        print(f"GPU train failed: {e}")
                        print("using cpu...")
                        use_gpu = False
                
                if not use_gpu:
                    trained_networks = []
                    
                    for network_idx in range(parameters.num_networks):
                        print(f'\n--- training model {network_idx+1} ---')
                        network, optimizer = initialize_network_and_optimizer(optimal_parameters, parameters.activation)
                        
                        trained_network = conduct_individual_training(
                            network, data_handler, optimizer, 0, 2, network_idx
                        )
                        trained_networks.append(trained_network)

                print(f"successfully trained {len(trained_networks)} models")
                print(f"model file: {[f'model_{i+1}.dict' for i in range(len(trained_networks))]}")
        
    except Exception as e:

        raise
