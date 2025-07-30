import multiprocessing as mp
import sys
import time
import threading
from .B15_prepare_data import prepare_pure_training_dataset
from .B9_transformer import MolecularTransformer
from .B13_operations import sigmoid
from .B3_autograd import no_grad
from .B14_optimizer import Adam
from .B11_focal_loss import FocalLoss
from .B16_tensor import Tensor
import pickle

def _message_listener(message_queue, num_processes):
    """监听消息队列并实时显示训练进度"""
    active_processes = num_processes
    
    while active_processes > 0:
        try:
            # 等待消息，超时0.1秒
            message = message_queue.get(timeout=0.1)
            
            if message == "PROCESS_FINISHED":
                active_processes -= 1
            else:
                print(message)
                sys.stdout.flush()
                
        except:
            # 队列为空，继续等待
            continue

def _worker_fast_train_single_model(args):
    try:
        model_idx, optimal_parameters, activation, dataset_info, epochs, input_features, embedding_size, message_queue = args
        
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
                    if message_queue:
                        message_queue.put(f"vey high loss {loss_value:.4f}, no update")
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
                
                if message_queue:
                    message_queue.put(f"model {model_idx+1} batch {batch_count}, loss: {loss_value:.4f}")
                    # 强制刷新输出
                    sys.stdout.flush()
            
            avg_loss = sum(epoch_losses) / len(epoch_losses) if epoch_losses else 0
            if message_queue:
                message_queue.put(f"[model {model_idx+1}] Epoch [{epoch+1}/{epochs}], avg_loss: {avg_loss:.4f}, "
                      f"High Pred False: {high_pred_false_count}, "
                      f"Very High Pred False: {very_high_pred_false_count}, "
                      f"Extreme High Pred False: {extreme_high_pred_false_count}")
            
            if all_predictions:
                min_pred = min(all_predictions)
                max_pred = max(all_predictions)
                if message_queue:
                    message_queue.put(f"model {model_idx+1}] Epoch {epoch+1} pred range: [{min_pred:.4f}, {max_pred:.4f}]")
        
        model_filename = f'model_{model_idx+1}.dict'
        save_data = {
            'model_parameters': network.state_dict(),
            'optimizer_state': optimizer.state_dict(),
            'epoch': epochs
        }
        
        with open(model_filename, 'wb') as f:
            pickle.dump(save_data, f)
        
        # 通知监听器该进程完成
        if message_queue:
            message_queue.put("PROCESS_FINISHED")
        
        return (True, model_idx, model_filename, None)
        
    except Exception as e:
        import traceback
        error_msg = f"model {model_idx+1} training failed: {str(e)}\n{traceback.format_exc()}"
        
        # 通知监听器该进程完成
        if message_queue:
            message_queue.put("PROCESS_FINISHED")
        
        return (False, model_idx, None, error_msg)

def fast_parallel_training(num_networks, optimal_parameters, activation='gelu', 
                          dataset_file='training_dataset.csv', max_workers=None, 
                          epochs=2, batch_size=32, input_features=2048, embedding_size=512):

    
    if max_workers is None:
        cpu_count = mp.cpu_count()
        if num_networks <= cpu_count // 2:
            max_workers = num_networks
        else:
            max_workers = min(num_networks, cpu_count // 2, 4) 
    
    
    dataset_info = {
        'file': dataset_file,
        'fingerprint_type': 'Morgan',
        'batch_size': batch_size,
        'shuffle': False,
        'balance_data': True
    }
    
    # 创建消息队列用于实时输出（使用Manager来确保跨进程兼容性）
    manager = mp.Manager()
    message_queue = manager.Queue()
    
    task_args = []
    for i in range(num_networks):
        task_args.append((i, optimal_parameters, activation, dataset_info, epochs, input_features, embedding_size, message_queue))
    
    successful_models = []
    failed_models = []
    
    if max_workers == 1 or num_networks == 1:
        # 串行训练时不需要消息监听器，直接执行
        for args in task_args:
            result = _worker_fast_train_single_model(args)
         
            success, model_idx, model_file, error_msg = result
            if success:
                successful_models.append(model_file)
            else:
                failed_models.append((model_idx, error_msg))
    else:
        # 并行训练时启动消息监听器
        listener_thread = threading.Thread(target=_message_listener, args=(message_queue, num_networks))
        listener_thread.daemon = True
        listener_thread.start()
        
        try:
            if sys.platform.startswith('win'):
                ctx = mp.get_context('spawn')
                with ctx.Pool(processes=max_workers) as pool:
                    results = pool.map(_worker_fast_train_single_model, task_args)
            else:
                with mp.Pool(processes=max_workers) as pool:
                    results = pool.map(_worker_fast_train_single_model, task_args)
        except Exception as e:
            print(f"parallel training failed: {e}")
            print("train one by one")
    
            results = []
            for args in task_args:
                result = _worker_fast_train_single_model(args)
                if result is not None:
                    results.append(result)
        
        # 等待监听器线程完成
        listener_thread.join()
        
        for result in results:
            success, model_idx, model_file, error_msg = result
            if success:
                successful_models.append(model_file)
            else:
                failed_models.append((model_idx, error_msg))
    
    return successful_models 