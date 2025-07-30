import os
import warnings
warnings.filterwarnings("ignore", message=".*Torch was not compiled with flash attention.*")
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['PYTHONWARNINGS'] = 'ignore'    

import torch
from . import D1_config as config
from .D2_data_loader import load_datasets, get_data_loaders
from .D3_model import VisionTrans_model
import torch.nn as nn
from collections import Counter

class AdvancedTrainingManager:
    def __init__(self, model, initial_optimizer, train_dataset, val_dataset, device, is_continue_training=False):
        self.model = model
        self.device = device
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        
        self.best_accuracy = 0.0
        self.best_weights = None
        self.accuracy_history = []
        self.loss_history = []
        
        self.is_continue_training = is_continue_training
        self.first_epoch_saved = False
        
        self.current_optimizer = initial_optimizer
        self.current_batch_size = config.batch_size
        self.current_weight_decay = config.weight_decay
        self.current_grad_clip = 1.0
        self.current_dropout = 0.1
        self.initial_lr = initial_optimizer.param_groups[0]['lr']
        
        self.strategy_attempts = {
            'lr_reduce': 0,
            'lr_increase': 0,
            'batch_size_change': 0,
            'optimizer_switch': 0,
            'weight_decay_adjust': 0,
            'grad_clip_adjust': 0,
            'layer_freeze': 0,
            'layer_unfreeze': 0,
            'dropout_adjust': 0,
            'aggressive_lr_reduce': 0,
            'reset_optimizer': 0,
            'restore_weights': 0,
            'lr_restart': 0,
            'momentum_boost': 0
        }
        
        self.strategy_cooldown = {
            'lr_reduce': 0,
            'lr_increase': 0,
            'batch_size_change': 0,
            'optimizer_switch': 0,
            'weight_decay_adjust': 0,
            'grad_clip_adjust': 0,
            'layer_freeze': 0,
            'layer_unfreeze': 0,
            'dropout_adjust': 0,
            'aggressive_lr_reduce': 0,
            'reset_optimizer': 0,
            'restore_weights': 0,
            'lr_restart': 0,
            'momentum_boost': 0
        }
        
        self.optimizer_type = 'adamw'
        self.frozen_layers = []
        self.overfitting_detected = False
        self.severe_overfitting = False
        self.stagnation_count = 0
        self.last_applied_strategies = []
        
        self.no_improvement_count = 0
        self.best_epoch = 0
        self.consecutive_overfitting = 0
        
    
    def should_save_model(self, val_accuracy):
        if self.is_continue_training and not self.first_epoch_saved:
            self.best_accuracy = val_accuracy
            self.best_weights = self.model.state_dict().copy()
            self.first_epoch_saved = True
            self.best_epoch = len(self.accuracy_history)
            torch.save(self.model.state_dict(), config.model_save_path)
            print(f"model saved to: {config.model_save_path}")
            return True
        
        if val_accuracy > self.best_accuracy + 0.001:
            improvement = val_accuracy - self.best_accuracy
            print(f"GOOD NEWS!!! accuracy improved: {self.best_accuracy:.4f} -> {val_accuracy:.4f} (+{improvement:.4f})\n")
            self.best_accuracy = val_accuracy
            self.best_weights = self.model.state_dict().copy()
            self.no_improvement_count = 0
            self.best_epoch = len(self.accuracy_history)
            self.consecutive_overfitting = 0  
            torch.save(self.model.state_dict(), config.model_save_path)
            print(f"model saved to: {config.model_save_path}")
            return True
        else:
            self.no_improvement_count += 1
        return False
    
    def detect_training_issues(self, train_loss, val_loss, val_accuracy, epoch):
        self.accuracy_history.append(val_accuracy)
        self.loss_history.append((train_loss, val_loss))
        
        for strategy in self.strategy_cooldown:
            if self.strategy_cooldown[strategy] > 0:
                self.strategy_cooldown[strategy] -= 1
        
        issues = []
        strategies = []
        
        if len(self.loss_history) >= 2:
            recent_train_loss = self.loss_history[-1][0]
            recent_val_loss = self.loss_history[-1][1]
            
            overfitting_ratio = recent_val_loss / max(recent_train_loss, 1e-8)
            
            if overfitting_ratio > 8 and recent_train_loss < 0.03:
                issues.append("serious overfitting")
                self.severe_overfitting = True
                self.consecutive_overfitting += 1
                if self.consecutive_overfitting >= 3:
                    strategies.extend(['lr_restart', 'reset_optimizer', 'batch_size_change'])
                else:
                    strategies.extend(['weight_decay_adjust', 'lr_reduce'])
            
            elif overfitting_ratio > 4:
                issues.append("overfitting")
                self.overfitting_detected = True
                self.consecutive_overfitting += 1
                strategies.extend(['weight_decay_adjust', 'lr_reduce'])
            else:
                self.consecutive_overfitting = 0
                self.overfitting_detected = False
                self.severe_overfitting = False
        
        if len(self.accuracy_history) >= 6:
            recent_acc = self.accuracy_history[-6:]
            if max(recent_acc) - min(recent_acc) < 0.003:
                issues.append("acc not improved for long")
                self.stagnation_count += 1
                if self.stagnation_count >= 4:
                    strategies.extend(['lr_restart', 'optimizer_switch', 'batch_size_change'])
                elif self.stagnation_count >= 2:
                    strategies.extend(['lr_increase', 'momentum_boost'])
                else:
                    strategies.extend(['grad_clip_adjust'])
        else:
            self.stagnation_count = 0
        
        if len(self.accuracy_history) >= 2:
            if self.accuracy_history[-1] < self.accuracy_history[-2] - 0.005:
                issues.append("acc decreased")
                strategies.extend(['restore_weights', 'lr_reduce'])
        
        if self.no_improvement_count >= 6:
            issues.append("no improve for long")
            strategies.extend(['lr_restart', 'restore_weights', 'optimizer_switch'])
        elif self.no_improvement_count >= 3:
            issues.append("needs adjustment")
            strategies.extend(['lr_increase', 'momentum_boost'])
        
        filtered_strategies = self._filter_strategies(strategies)
        
        return issues, filtered_strategies
    
    def _filter_strategies(self, strategies):
        filtered = []
        
        for strategy in strategies:
            if self.strategy_cooldown[strategy] > 0:
                continue
                
            max_attempts = {
                'lr_reduce': 3,
                'lr_increase': 3,
                'batch_size_change': 2,
                'optimizer_switch': 2,
                'weight_decay_adjust': 3,
                'grad_clip_adjust': 2,
                'layer_freeze': 1,
                'layer_unfreeze': 1,
                'dropout_adjust': 2,
                'aggressive_lr_reduce': 1,  
                'reset_optimizer': 2,
                'restore_weights': 15,
                'lr_restart': 2,
                'momentum_boost': 3
            }
            
            if self.strategy_attempts[strategy] >= max_attempts.get(strategy, 3):
                continue
            
            if len(self.last_applied_strategies) >= 2 and strategy in self.last_applied_strategies[-2:]:
                continue
                
            current_lr = self.current_optimizer.param_groups[0]['lr']
            
            if strategy in ['lr_reduce', 'aggressive_lr_reduce'] and current_lr < self.initial_lr * 0.01:
                continue
            
            if strategy == 'lr_increase' and current_lr > self.initial_lr * 2:
                continue
            
            if strategy == 'batch_size_change' and self.current_batch_size <= 8:
                continue
                
            if strategy == 'batch_size_change' and self.current_batch_size >= 64:
                continue
            
            filtered.append(strategy)
        
        priority_order = {
            'restore_weights': 10,
            'lr_restart': 9,
            'reset_optimizer': 8,
            'lr_reduce': 7,
            'weight_decay_adjust': 6,
            'optimizer_switch': 5,
            'batch_size_change': 4,
            'momentum_boost': 4,
            'grad_clip_adjust': 3,
            'lr_increase': 3,
            'layer_freeze': 1,
            'layer_unfreeze': 1,
            'dropout_adjust': 2,
            'aggressive_lr_reduce': 2
        }
        
        filtered.sort(key=lambda x: priority_order.get(x, 0), reverse=True)
        
        return filtered[:2]  
    
    def apply_strategy(self, strategy, epoch):
        
        self.last_applied_strategies.append(strategy)
        if len(self.last_applied_strategies) > 5:
            self.last_applied_strategies.pop(0)
        
        if strategy == 'lr_reduce':
            self._reduce_learning_rate()
            self.strategy_attempts['lr_reduce'] += 1
            self.strategy_cooldown['lr_reduce'] = 2
            
        elif strategy == 'lr_restart':
            self._restart_learning_rate()
            self.strategy_attempts['lr_restart'] += 1
            self.strategy_cooldown['lr_restart'] = 4
            
        elif strategy == 'aggressive_lr_reduce':
            self._aggressive_reduce_learning_rate()
            self.strategy_attempts['aggressive_lr_reduce'] += 1
            self.strategy_cooldown['aggressive_lr_reduce'] = 5
            
        elif strategy == 'lr_increase':
            self._increase_learning_rate()
            self.strategy_attempts['lr_increase'] += 1
            self.strategy_cooldown['lr_increase'] = 2
            
        elif strategy == 'batch_size_change':
            self._smart_adjust_batch_size(epoch)
            self.strategy_attempts['batch_size_change'] += 1
            self.strategy_cooldown['batch_size_change'] = 3
            
        elif strategy == 'optimizer_switch':
            self._switch_optimizer()
            self.strategy_attempts['optimizer_switch'] += 1
            self.strategy_cooldown['optimizer_switch'] = 4
            
        elif strategy == 'reset_optimizer':
            self._reset_optimizer()
            self.strategy_attempts['reset_optimizer'] += 1
            self.strategy_cooldown['reset_optimizer'] = 3
            
        elif strategy == 'weight_decay_adjust':
            self._adjust_weight_decay(increase=True)
            self.strategy_attempts['weight_decay_adjust'] += 1
            self.strategy_cooldown['weight_decay_adjust'] = 2
            
        elif strategy == 'grad_clip_adjust':
            self._adjust_gradient_clipping()
            self.strategy_attempts['grad_clip_adjust'] += 1
            self.strategy_cooldown['grad_clip_adjust'] = 2
            
        elif strategy == 'momentum_boost':
            self._boost_momentum()
            self.strategy_attempts['momentum_boost'] += 1
            self.strategy_cooldown['momentum_boost'] = 3
            
        elif strategy == 'layer_freeze':
            self._freeze_backbone_layers()
            self.strategy_attempts['layer_freeze'] += 1
            self.strategy_cooldown['layer_freeze'] = 4
            
        elif strategy == 'layer_unfreeze':
            self._unfreeze_layers()
            self.strategy_attempts['layer_unfreeze'] += 1
            self.strategy_cooldown['layer_unfreeze'] = 4
            
        elif strategy == 'dropout_adjust':
            self._adjust_dropout(increase=True)
            self.strategy_attempts['dropout_adjust'] += 1
            self.strategy_cooldown['dropout_adjust'] = 2
            
        elif strategy == 'restore_weights':
            self._restore_best_weights()
            self.strategy_attempts['restore_weights'] += 1
    
    def _restart_learning_rate(self):
        new_lr = self.initial_lr * 0.5
        for param_group in self.current_optimizer.param_groups:
            param_group['lr'] = new_lr
    
    def _boost_momentum(self):
        if hasattr(self.current_optimizer, 'param_groups'):
            for param_group in self.current_optimizer.param_groups:
                if 'momentum' in param_group:
                    old_momentum = param_group['momentum']
                    param_group['momentum'] = min(0.95, old_momentum + 0.05)
                elif 'betas' in param_group:
                    old_beta1 = param_group['betas'][0]
                    new_beta1 = min(0.95, old_beta1 + 0.02)
                    param_group['betas'] = (new_beta1, param_group['betas'][1])
    
    def _aggressive_reduce_learning_rate(self):
        old_lr = self.current_optimizer.param_groups[0]['lr']
        new_lr = old_lr * 0.1  
        for param_group in self.current_optimizer.param_groups:
            param_group['lr'] = new_lr
    
    def _smart_adjust_batch_size(self, epoch):
        old_batch_size = self.current_batch_size
        
        if self.severe_overfitting:
            self.current_batch_size = max(8, self.current_batch_size // 2)
        elif self.stagnation_count >= 2:
            if self.current_batch_size <= 16:
                self.current_batch_size = 32
            else:
                self.current_batch_size = 16
        else:
            if self.current_batch_size < 32:
                self.current_batch_size *= 2
            else:
                self.current_batch_size = max(16, self.current_batch_size // 2)
        
        if old_batch_size != self.current_batch_size:
            return True
        return False
    
    def _reset_optimizer(self):
        current_lr = self.current_optimizer.param_groups[0]['lr']
        
        if self.optimizer_type == 'adamw':
            self.current_optimizer = torch.optim.AdamW(
                self.model.parameters(), 
                lr=current_lr * 2,  
                weight_decay=self.current_weight_decay,
                betas=(0.9, 0.999),
                eps=1e-8
            )
        else:
            self.current_optimizer = torch.optim.SGD(
                self.model.parameters(), 
                lr=current_lr * 2,
                momentum=0.9, 
                weight_decay=self.current_weight_decay,
                nesterov=True
            )
            
    def _reduce_learning_rate(self):
        old_lr = self.current_optimizer.param_groups[0]['lr']
        new_lr = old_lr * 0.5
        for param_group in self.current_optimizer.param_groups:
            param_group['lr'] = new_lr
        print(f"  lr decrease: {old_lr:.8f} -> {new_lr:.8f}")
    
    def _increase_learning_rate(self):
        old_lr = self.current_optimizer.param_groups[0]['lr']
        new_lr = min(old_lr * 1.5, self.initial_lr)  
        for param_group in self.current_optimizer.param_groups:
            param_group['lr'] = new_lr
        print(f"  lr increase: {old_lr:.8f} -> {new_lr:.8f}")
    
    def _adjust_weight_decay(self, increase=True):
        old_wd = self.current_weight_decay
        if increase:
            self.current_weight_decay = min(0.05, self.current_weight_decay * 1.5) 
        else:
            self.current_weight_decay = max(0.001, self.current_weight_decay * 0.7)
        
        for param_group in self.current_optimizer.param_groups:
            param_group['weight_decay'] = self.current_weight_decay
        
        action = "increase" if increase else "decrease"
        print(f"  weight_decay {action}: {old_wd:.6f} -> {self.current_weight_decay:.6f}")
    
    def _adjust_gradient_clipping(self):
        if self.severe_overfitting:
            self.current_grad_clip = min(2.0, self.current_grad_clip * 1.3)
        else:
            if self.current_grad_clip > 1.0:
                self.current_grad_clip = max(0.3, self.current_grad_clip * 0.8)
            else:
                self.current_grad_clip = min(2.0, self.current_grad_clip * 1.3)
    
    def _freeze_backbone_layers(self):
        frozen_count = 0
        layers_to_freeze = 6 if self.severe_overfitting else 4  
        
        for name, param in self.model.named_parameters():
            if 'vit.encoder.layer' in name:
                layer_num = int(name.split('.')[3])
                if layer_num < layers_to_freeze:
                    param.requires_grad = False
                    frozen_count += 1
        
        self.frozen_layers = [f"layer_{i}" for i in range(layers_to_freeze)]
    
    def _unfreeze_layers(self):
        unfrozen_count = 0
        for param in self.model.parameters():
            if not param.requires_grad:
                param.requires_grad = True
                unfrozen_count += 1
        
        self.frozen_layers = []

    
    def _adjust_dropout(self, increase=True):
        if increase:
            self.current_dropout = min(0.3, self.current_dropout * 1.3)
        else:
            self.current_dropout = max(0.05, self.current_dropout * 0.8)
        
    def _restore_best_weights(self):
        if self.best_weights is not None:
            self.model.load_state_dict(self.best_weights)
            self.severe_overfitting = False
            self.overfitting_detected = False
            self.no_improvement_count = 0
            self.consecutive_overfitting = 0
        else:
            print(" no best weight saved")
    
    def get_current_data_loaders(self):
        from .D2_data_loader import get_data_loaders
        return get_data_loaders(self.train_dataset, self.val_dataset, self.current_batch_size)

    def _adjust_batch_size(self, epoch, reduce=False):
        old_batch_size = self.current_batch_size
        if reduce or self.overfitting_detected:
            self.current_batch_size = max(8, self.current_batch_size // 2)
        else:
            self.current_batch_size = min(64, self.current_batch_size * 2)
        
        if old_batch_size != self.current_batch_size:
            return True
        return False
    
    def _switch_optimizer(self):
        current_lr = self.current_optimizer.param_groups[0]['lr']
        
        if self.optimizer_type == 'adamw':
            self.current_optimizer = torch.optim.SGD(
                self.model.parameters(), 
                lr=max(current_lr * 20, self.initial_lr * 0.1),  
                momentum=0.9, 
                weight_decay=self.current_weight_decay,
                nesterov=True
            )
            self.optimizer_type = 'sgd'
        else:
            new_lr = max(current_lr / 20, self.initial_lr * 0.1)
            self.current_optimizer = torch.optim.AdamW(
                self.model.parameters(), 
                lr=new_lr,
                weight_decay=self.current_weight_decay,
                betas=(0.9, 0.999),
                eps=1e-8
            )
            self.optimizer_type = 'adamw'

def evaluate_model(model, data_loader, device, criterion):
    model.eval()
    correct = 0
    total = 0
    running_loss = 0.0
    
    with torch.no_grad():
        for images, labels in data_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images).logits
            loss = criterion(outputs, labels)
            
            _, predicted = torch.max(outputs, 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
            running_loss += loss.item()
    
    accuracy = correct / total
    avg_loss = running_loss / len(data_loader)
    return accuracy, avg_loss

def train_model_improved(model, train_loader, val_loader, num_epochs, learning_rate):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"device: {device}")
    
    model.to(device)
    
    all_labels = []
    for _, labels in train_loader:
        all_labels.extend(labels.tolist())
    
    class_counts = Counter(all_labels)
    
    total_samples = len(all_labels)
    num_classes = len(class_counts)
    class_weights = []
    for i in range(num_classes):
        if i in class_counts:
            weight = total_samples / (num_classes * class_counts[i])
            class_weights.append(weight)
        else:
            class_weights.append(1.0)
    
    class_weights = torch.FloatTensor(class_weights).to(device)
    
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    
    classifier_params = []
    backbone_params = []
    
    for name, param in model.named_parameters():
        if 'classifier' in name:
            classifier_params.append(param)
        else:
            backbone_params.append(param)
    
    optimizer = torch.optim.AdamW([
        {'params': backbone_params, 'lr': learning_rate * 0.1},  
        {'params': classifier_params, 'lr': learning_rate}   
    ], weight_decay=config.weight_decay)
    
    train_dataset, val_dataset = load_datasets(config.data_dir, getattr(config, 'folder_label_mapping', None))
    
    manager = AdvancedTrainingManager(model, optimizer, train_dataset, val_dataset, device, is_continue_training=False)
    
    train_losses = []
    val_losses = []
    val_accuracies = []
        
    current_train_loader = train_loader
    current_val_loader = val_loader
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        
        for batch_idx, (images, labels) in enumerate(current_train_loader):
            images, labels = images.to(device), labels.to(device)
            
            manager.current_optimizer.zero_grad()
            outputs = model(images).logits
            loss = criterion(outputs, labels)
            loss.backward()
            
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=manager.current_grad_clip)
            
            manager.current_optimizer.step()
            running_loss += loss.item()
            
            if (batch_idx + 1) % 5 == 0:
                print(f"\nbatch {batch_idx + 1} completed - loss: {loss.item():.4f}")
        
        train_loss = running_loss / len(current_train_loader)
        val_accuracy, val_loss = evaluate_model(model, current_val_loader, device, criterion)
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        val_accuracies.append(val_accuracy)
        
        print(f'\nEpoch {epoch + 1}/{num_epochs} summary:')
        print(f'   train loss: {train_loss:.4f} | val loss: {val_loss:.4f}')
        print(f'   val_accuracy: {val_accuracy:.4f} | lr: {manager.current_optimizer.param_groups[0]["lr"]:.8f}')
        print(f'   batch_size: {manager.current_batch_size} | weight_decay: {manager.current_weight_decay:.6f}')
        print(f'   optimizer: {manager.optimizer_type.upper()} | rad_clip: {manager.current_grad_clip:.2f}')
        
        manager.should_save_model(val_accuracy)
        
        issues, strategies = manager.detect_training_issues(train_loss, val_loss, val_accuracy, epoch)
        
        if issues:
            print(f"found issue: {', '.join(issues)}")
            
            max_strategies = 1 if len(issues) == 1 else min(2, len(strategies))
            applied_strategies = []
            batch_size_changed = False
            
            for i, strategy in enumerate(strategies[:max_strategies]):
                if i > 0 and strategy in ['restore_weights']:
                    continue
                
                manager.apply_strategy(strategy, epoch + 1)
                applied_strategies.append(strategy)
                
                if strategy in ['batch_size_change']:
                    batch_size_changed = True
            
            if batch_size_changed:
                print(f"batch size adjusted: {manager.current_batch_size}")
                current_train_loader, current_val_loader = manager.get_current_data_loaders()
            
            if applied_strategies:
                print(f"strategy applied: {', '.join(applied_strategies)}")
        else:
            print("continue")
        
    
    print("training completed")
    print(f"best_accuracy: {manager.best_accuracy:.4f} (in epoch {manager.best_epoch+1})")

    
    return train_losses, val_losses, val_accuracies

def train_model_improved_continue(model, train_loader, val_loader, num_epochs, learning_rate, is_continue_training=False):

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    model.to(device)
    
    all_labels = []
    for _, labels in train_loader:
        all_labels.extend(labels.tolist())
    
    class_counts = Counter(all_labels)
    
    total_samples = len(all_labels)
    num_classes = len(class_counts)
    class_weights = []
    for i in range(num_classes):
        if i in class_counts:
            weight = total_samples / (num_classes * class_counts[i])
            class_weights.append(weight)
        else:
            class_weights.append(1.0)
    
    class_weights = torch.FloatTensor(class_weights).to(device)
    
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    
    classifier_params = []
    backbone_params = []
    
    for name, param in model.named_parameters():
        if 'classifier' in name:
            classifier_params.append(param)
        else:
            backbone_params.append(param)
    
    optimizer = torch.optim.AdamW([
        {'params': backbone_params, 'lr': learning_rate * 0.1},  
        {'params': classifier_params, 'lr': learning_rate}   
    ], weight_decay=config.weight_decay)
    
    train_dataset, val_dataset = load_datasets(config.data_dir, getattr(config, 'folder_label_mapping', None))
    
    manager = AdvancedTrainingManager(model, optimizer, train_dataset, val_dataset, device, is_continue_training=is_continue_training)
    
    train_losses = []
    val_losses = []
    val_accuracies = []
        
    current_train_loader = train_loader
    current_val_loader = val_loader
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        
        for batch_idx, (images, labels) in enumerate(current_train_loader):
            images, labels = images.to(device), labels.to(device)
            
            manager.current_optimizer.zero_grad()
            outputs = model(images).logits
            loss = criterion(outputs, labels)
            loss.backward()
            
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=manager.current_grad_clip)
            
            manager.current_optimizer.step()
            running_loss += loss.item()
            
            if (batch_idx + 1) % 5 == 0:
                print(f"\nbatch {batch_idx + 1} completed - loss: {loss.item():.4f}")
        
        train_loss = running_loss / len(current_train_loader)
        val_accuracy, val_loss = evaluate_model(model, current_val_loader, device, criterion)
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        val_accuracies.append(val_accuracy)
        
        print(f'\nEpoch {epoch + 1}/{num_epochs} summary:')
        print(f'   train loss: {train_loss:.4f} | val loss: {val_loss:.4f}')
        print(f'   val_accuracy: {val_accuracy:.4f} | lr: {manager.current_optimizer.param_groups[0]["lr"]:.8f}')
        print(f'   batch_size: {manager.current_batch_size} | weight_decay: {manager.current_weight_decay:.6f}')
        print(f'   optimizer: {manager.optimizer_type.upper()} | rad_clip: {manager.current_grad_clip:.2f}')
        
        manager.should_save_model(val_accuracy)
        
        issues, strategies = manager.detect_training_issues(train_loss, val_loss, val_accuracy, epoch)
        
        if issues:
            print(f"found issue: {', '.join(issues)}")
            
            max_strategies = 1 if len(issues) == 1 else min(2, len(strategies))
            applied_strategies = []
            batch_size_changed = False
            
            for i, strategy in enumerate(strategies[:max_strategies]):
                if i > 0 and strategy in ['restore_weights']:
                    continue
                
                manager.apply_strategy(strategy, epoch + 1)
                applied_strategies.append(strategy)
                
                if strategy in ['batch_size_change']:
                    batch_size_changed = True
            
            if batch_size_changed:
                print(f"batch size adjusted: {manager.current_batch_size}")
                current_train_loader, current_val_loader = manager.get_current_data_loaders()
            
            if applied_strategies:
                print(f"strategy applied: {', '.join(applied_strategies)}")
        else:
            print("continue")
        
    
    print("\n\ncontinue training completed")
    print(f"best_accuracy: {manager.best_accuracy:.4f} (in epoch {manager.best_epoch+1})")

    
    return train_losses, val_losses, val_accuracies

def main():
    
    train_dataset, val_dataset = load_datasets(config.data_dir, getattr(config, 'folder_label_mapping', None))
    train_loader, val_loader = get_data_loaders(train_dataset, val_dataset, config.batch_size)
    
    print(f"train_dataset: {len(train_dataset)}")
    print(f"val_dataset: {len(val_dataset)}")
    print(f"initial_batch_size: {config.batch_size}")
    print(f"initial_learning_rate: {config.learning_rate}")
    print(f"num_epochs: {config.num_epochs}")
    
    model = VisionTrans_model(config.num_classes)
    
    train_losses, val_losses, val_accuracies = train_model_improved(
        model, train_loader, val_loader, config.num_epochs, config.learning_rate
    )

if __name__ == '__main__':
    main() 