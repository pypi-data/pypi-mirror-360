import torch
import torch.nn as nn
from rdkit import Chem
from rdkit.Chem import AllChem
import pandas as pd
import random
import numpy as np
import argparse
import os

def configure_settings():
    config_parser = argparse.ArgumentParser(description='Molecular property prediction')
    config_parser.add_argument('--num_networks', type=int, default=3, 
                             help='Quantity of networks to train')
    config_parser.add_argument('--parallel', action='store_true', 
                             help='Enable parallel network training')
    return config_parser.parse_args()

def softmax(x, dim=-1):
    shifted_x = x - torch.max(x, dim=dim, keepdim=True)[0]
    exp_x = torch.exp(shifted_x)
    return exp_x / torch.sum(exp_x, dim=dim, keepdim=True)


class AttentionMechanism(nn.Module):
    def __init__(self, embedding_size, head_count):
        super(AttentionMechanism, self).__init__()
        self.embedding_size = embedding_size
        self.head_count = head_count
        self.per_head_dim = embedding_size // head_count
        assert self.per_head_dim * head_count == embedding_size, "Embedding size must divide evenly by head count"
        self.query_key_value = nn.Linear(embedding_size, 3 * embedding_size)
        self.output_projection = nn.Linear(embedding_size, embedding_size)

    def forward(self, x):
        batch_size = x.size(0)
        qkv = self.query_key_value(x).reshape(batch_size, -1, self.head_count, 3 * self.per_head_dim).transpose(1, 2)
        queries, keys, values = qkv.chunk(3, dim=-1)
        queries = queries / (self.per_head_dim ** 0.5)
        attention_scores = (queries @ keys.transpose(-2, -1))
        attention_weights = softmax(attention_scores, dim=-1)
        attention_output = (attention_weights @ values).transpose(1, 2).reshape(batch_size, -1, self.embedding_size)
        attention_output = self.output_projection(attention_output)
        return attention_output

class TransformerBlock(nn.Module):
    def __init__(self, embedding_size, head_count, hidden_size, dropout_rate):
        super(TransformerBlock, self).__init__()
        self.attention = AttentionMechanism(embedding_size, head_count)
        self.feedforward = nn.Sequential(
            nn.Linear(embedding_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, embedding_size),
            nn.Dropout(dropout_rate),
        )
        self.normalization1 = nn.LayerNorm(embedding_size)
        self.normalization2 = nn.LayerNorm(embedding_size)
        self.dropout = nn.Dropout(dropout_rate)

    def forward(self, x):
        residual = x
        x = self.normalization1(x)
        x = self.attention(x) + residual
        x = self.dropout(x)
        residual = x
        x = self.normalization2(x)
        x = self.feedforward(x) + residual
        x = self.dropout(x)
        return x

class TransformerStack(nn.Module):
    def __init__(self, embedding_size, layer_count, head_count, hidden_size, dropout_rate):
        super(TransformerStack, self).__init__()
        self.layers = nn.ModuleList([
            TransformerBlock(embedding_size, head_count, hidden_size, dropout_rate)
            for _ in range(layer_count)
        ])
        self.final_normalization = nn.LayerNorm(embedding_size)

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        x = self.final_normalization(x)
        return x

class MolecularTransformer(nn.Module):
    def __init__(self, input_features, output_features, embedding_size, layer_count, head_count, hidden_size, dropout_rate):
        super(MolecularTransformer, self).__init__()
        self.embedding_size = embedding_size
        self.feature_embedding = nn.Linear(input_features, embedding_size)
        self.transformer = TransformerStack(embedding_size, layer_count, head_count, hidden_size, dropout_rate)
        self.output_layer = nn.Linear(embedding_size, output_features)

    def forward(self, x):
        x = self.feature_embedding(x)
        x = self.transformer(x)
        x = x.mean(dim=1)
        x = self.output_layer(x)
        return x

class BaseMolecularDataset:
    def __init__(self, data_file, fingerprint_type='Morgan'):
        self.molecular_data = pd.read_csv(data_file)
        self.smiles_strings = self.molecular_data['SMILES']
        self.fingerprint_method = fingerprint_type

    def __len__(self):
        return len(self.smiles_strings)

    def _get_molecular_features(self, smiles):
        molecule = Chem.MolFromSmiles(smiles)
        if molecule is None:
            print(f"Warning: Invalid SMILES: {smiles}")
            return None

        if self.fingerprint_method == 'Morgan':
            return torch.tensor(AllChem.GetMorganFingerprintAsBitVect(molecule, 2, 2048))
        else:
            raise ValueError("Specified fingerprint method not supported")

class MolecularDataset(BaseMolecularDataset):
    def __init__(self, data_file, fingerprint_type='Morgan'):
        super().__init__(data_file, fingerprint_type)
        self.activity_labels = self.molecular_data['ACTIVITY']

    def __getitem__(self, index):
        features = self._get_molecular_features(self.smiles_strings[index])
        if features is None:
            return None, None
        activity_label = torch.tensor(self.activity_labels[index], dtype=torch.float)
        return features, activity_label

class MolecularPredictionDataset(BaseMolecularDataset):
    def __getitem__(self, index):
        features = self._get_molecular_features(self.smiles_strings[index])
        return features

class BalancedSampler:
    def __init__(self, dataset, with_replacement=True):
        self.dataset = dataset
        self.with_replacement = with_replacement
        self.sampling_weights = self._compute_weights()
        self.sample_count = len(dataset)
        self.hard_samples = set() 
        self.high_pred_false_samples = set() 
        self.very_high_pred_false_samples = set() 
        self.extreme_high_pred_false_samples = set()  
        self.positive_samples = set() 
        self.sample_history = {} 

    def _compute_weights(self):
        class_distribution = self.dataset.activity_labels.value_counts().to_list()
        total_samples = sum(class_distribution)
        weights = [total_samples/class_distribution[i] for i in range(len(class_distribution))]
        return [weights[int(label)] for label in self.dataset.activity_labels]

    def update_hard_samples(self, predictions, labels, threshold=0.95):
        for idx, (pred, label) in enumerate(zip(predictions, labels)):
            if label == 1:
                self.positive_samples.add(idx)
            elif label == 0:
                if pred > 0.98:
                    self.extreme_high_pred_false_samples.add(idx)
                    self.very_high_pred_false_samples.add(idx)
                    self.hard_samples.add(idx)
                elif pred > 0.95:
                    self.very_high_pred_false_samples.add(idx)
                    self.hard_samples.add(idx)
                elif pred > 0.9:
                    self.high_pred_false_samples.add(idx)
                    self.hard_samples.add(idx)

    def _get_sample_weight(self, idx):
        base_weight = self.sampling_weights[idx]
        
        if idx in self.extreme_high_pred_false_samples:
            weight = base_weight * 100.0  
        elif idx in self.very_high_pred_false_samples:
            weight = base_weight * 50.0
        elif idx in self.high_pred_false_samples:
            weight = base_weight * 20.0
        elif idx in self.hard_samples:
            weight = base_weight * 10.0
        elif idx in self.positive_samples:
            weight = base_weight * 5.0 
        else:
            weight = base_weight
        
        if idx in self.sample_history:
            sample_count = self.sample_history[idx]
            if sample_count > 0:
                weight = weight / (1 + sample_count * 0.1)  
        
        return weight

    def __iter__(self):
        if self.with_replacement:
            weights = np.array([self._get_sample_weight(i) for i in range(len(self.dataset))])
            weights = weights / weights.sum()  
            
            samples = np.random.choice(range(len(self.dataset)), 
                                    size=self.sample_count, 
                                    replace=True, 
                                    p=weights)
            
            for idx in samples:
                self.sample_history[idx] = self.sample_history.get(idx, 0) + 1
            
            return iter(samples)
        else:
            indices = list(range(len(self.dataset)))
            weights = np.array([self._get_sample_weight(i) for i in indices])
            weights = weights / weights.sum()
            
            samples = np.random.choice(indices, 
                                    size=self.sample_count, 
                                    replace=False, 
                                    p=weights)
            
            for idx in samples:
                self.sample_history[idx] = self.sample_history.get(idx, 0) + 1
            
            return iter(samples)

    def __len__(self):
        return self.sample_count

class BatchProvider:
    def __init__(self, dataset, batch_size=32, shuffle=False, sampler=None):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle_flag = shuffle
        self.sampler = sampler
        self.current_position = 0
        self.indices = list(range(len(dataset)))
        if shuffle and sampler is None:
            random.shuffle(self.indices)
        elif sampler is not None:
            pass
        self.is_prediction = not hasattr(dataset, 'activity_labels')

    def __iter__(self):
        self.current_position = 0
        if self.sampler is not None:
            self.indices = list(self.sampler)
        return self

    def __next__(self):
        max_position = len(self.indices)
        if self.current_position >= max_position:
            raise StopIteration

        feature_batch = []
        label_batch = []
        
        for _ in range(self.batch_size):
            if self.current_position >= max_position:
                break
                
            idx = self.indices[self.current_position]
            if self.is_prediction:
                features = self.dataset[idx]
                if features is not None:
                    feature_batch.append(features)
            else:
                features, label = self.dataset[idx]
                if features is not None and label is not None:
                    feature_batch.append(features)
                    label_batch.append(label)
            
            self.current_position += 1

        if not feature_batch:
            raise StopIteration

        if self.is_prediction:
            return torch.stack(feature_batch), None
        else:
            return torch.stack(feature_batch), torch.stack(label_batch)

    def __len__(self):
        return (len(self.dataset) + self.batch_size - 1) // self.batch_size


def store_model(model, optimizer, epoch, filename='training_checkpoint.pt'):
    model_state = {
        'model_parameters': model.state_dict(),
        'optimizer_state': optimizer.state_dict(),
        'training_epoch': epoch,
    }
    torch.save(model_state, filename)

def prepare_training_dataset(csv_path, fingerprint_type='Morgan', batch_size=32, shuffle=False, balance_data=False):
    df = pd.read_csv(csv_path)
    df['SMILES'] = df['SMILES'].astype(str)
    df = df.dropna(subset=['SMILES', 'ACTIVITY'])
    valid_indices = []
    invalid_smiles = []
    
    for idx, row in df.iterrows():
        try:
            mol = Chem.MolFromSmiles(row['SMILES'])
            if mol is not None:
                valid_indices.append(idx)
            else:
                invalid_smiles.append(row['SMILES'])
        except:
            invalid_smiles.append(row['SMILES'])
    
    print(f"Total SMILES: {len(df)} | Valid SMILES: {len(valid_indices)} | Invalid SMILES: {len(invalid_smiles)}")
    if invalid_smiles:
        print("The first 10 Invalid SMILES:", invalid_smiles[:10])
    
    if invalid_smiles:
        clean_df = df.iloc[valid_indices].copy()
        clean_path = 'cleaned_training_dataset.csv'
        clean_df.to_csv(clean_path, index=False)
        print(f"Generated cleaned file due to invalid SMILES: {clean_path}")
        dataset = MolecularDataset(clean_path, fingerprint_type)
    else:
        print("No invalid SMILES found, using original file")
        dataset = MolecularDataset(csv_path, fingerprint_type)
     
    if balance_data:
        sampler = BalancedSampler(dataset)
        data_provider = BatchProvider(dataset, batch_size=batch_size, sampler=sampler)
    else:
        data_provider = BatchProvider(dataset, batch_size=batch_size, shuffle=shuffle)
 
    return data_provider

def prepare_predicting_dataset(csv_path, fingerprint_type='Morgan', batch_size=32, shuffle=False, balance_data=False):
    df = pd.read_csv(csv_path)   
    df['SMILES'] = df['SMILES'].astype(str)
    df = df.dropna(subset=['SMILES'])
    valid_indices = []
    invalid_smiles = []
    
    for idx, row in df.iterrows():
        try:
            mol = Chem.MolFromSmiles(row['SMILES'])
            if mol is not None:
                valid_indices.append(idx)
            else:
                invalid_smiles.append(row['SMILES'])
        except:
            invalid_smiles.append(row['SMILES'])
    
    if invalid_smiles:
        print("The first 10 Invalid SMILES:", invalid_smiles[:10])
    
    if invalid_smiles:
        clean_df = df.iloc[valid_indices].copy()
        clean_path = 'cleaned_predicting_dataset.csv'
        clean_df.to_csv(clean_path, index=False)
        print(f"Generated cleaned file due to invalid SMILES: {clean_path}")
        dataset = MolecularPredictionDataset(clean_path, fingerprint_type)
    else:
        dataset = MolecularPredictionDataset(csv_path, fingerprint_type)
    
    data_provider = BatchProvider(dataset, batch_size=batch_size, shuffle=shuffle)
    return data_provider

class FocalLoss(nn.Module):
    def __init__(self, alpha=0.25, gamma=2.0, high_pred_penalty=20.0, high_pred_threshold=0.9):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.high_pred_penalty = high_pred_penalty  
        self.high_pred_threshold = high_pred_threshold

    def forward(self, inputs, targets):
        BCE_loss = nn.BCEWithLogitsLoss(reduction='none')(inputs, targets)
        pt = torch.exp(-BCE_loss)
        F_loss = self.alpha * (1-pt)**self.gamma * BCE_loss
        
        with torch.no_grad():
            predictions = torch.sigmoid(inputs)
            high_pred_mask = (predictions > self.high_pred_threshold) & (targets == 0)
            very_high_pred_mask = (predictions > 0.95) & (targets == 0)
            extreme_high_pred_mask = (predictions > 0.98) & (targets == 0)
        
        with torch.no_grad():
            penalty_factor = torch.ones_like(inputs)
            penalty_factor[high_pred_mask] = 1 + (predictions[high_pred_mask] - self.high_pred_threshold) * self.high_pred_penalty
            penalty_factor[very_high_pred_mask] = 1 + (predictions[very_high_pred_mask] - 0.95) * (self.high_pred_penalty * 1.5)
            penalty_factor[extreme_high_pred_mask] = 1 + (predictions[extreme_high_pred_mask] - 0.98) * (self.high_pred_penalty * 2)
        
        with torch.no_grad():
            grad_scale = torch.ones_like(inputs)
            grad_scale[high_pred_mask] = 0.5
            grad_scale[very_high_pred_mask] = 0.3
            grad_scale[extreme_high_pred_mask] = 0.2
        
        final_loss = F_loss * penalty_factor * grad_scale
        
        with torch.no_grad():
            extra_penalty = torch.zeros_like(inputs)
            extra_penalty[high_pred_mask] = torch.exp(predictions[high_pred_mask] * 3) - 1
            extra_penalty[very_high_pred_mask] = torch.exp(predictions[very_high_pred_mask] * 4) - 1
            extra_penalty[extreme_high_pred_mask] = torch.exp(predictions[extreme_high_pred_mask] * 5) - 1
        
        return (final_loss + extra_penalty).mean()

def load_trained_network(network, model_file, compute_device):
    if os.path.exists(model_file):
        saved_state = torch.load(model_file, map_location=compute_device)
        network.load_state_dict(saved_state['model_parameters'])
        for param in network.parameters():
            param.data = param.data.to(compute_device)
        return network
    return None

def analyze_prediction_quality(output_file):
    print("\nResults analysis:")
    
    try:
        import pandas as pd
        data = pd.read_csv(output_file)
        
        prediction_column = 'ENSEMBLE_PREDICTION' if 'ENSEMBLE_PREDICTION' in data.columns else 'prediction_score'
        
        if prediction_column not in data.columns or 'ACTIVITY' not in data.columns:
            print(f"Missing {prediction_column} or ACTIVITY columns")
            return
            
        predictions = data[prediction_column].tolist()
        activities = data['ACTIVITY'].tolist()
        
        indexed_predictions = [(i, pred, act) for i, (pred, act) in enumerate(zip(predictions, activities))]
        indexed_predictions.sort(key=lambda x: x[1], reverse=True) 
        
        print("The top 10 predictions:")
        print(f"{'Prediction':<10} {'True_label':<8} ")
        print(f"{'-'*35}")
        
        for i in range(min(10, len(indexed_predictions))):
            idx, pred, actual = indexed_predictions[i]
            print(f"{pred:<10.6f} {actual:<8} ")
        
        active_predictions = [pred for pred, act in zip(predictions, activities) if act == 1]
        if active_predictions:
            print("Active compounds:")
            print(f"Range: [{min(active_predictions):.4f}, {max(active_predictions):.4f}]")
            print(f"Average: {sum(active_predictions)/len(active_predictions):.4f}")
        
        inactive_predictions = [pred for pred, act in zip(predictions, activities) if act == 0]
        if inactive_predictions:
            print("Inactive compounds:")
            print(f"Range: [{min(inactive_predictions):.4f}, {max(inactive_predictions):.4f}]")
            print(f"Average: {sum(inactive_predictions)/len(inactive_predictions):.4f}")
        
    except Exception as e:
        print(f"Failed to analyze predictions: {e}")