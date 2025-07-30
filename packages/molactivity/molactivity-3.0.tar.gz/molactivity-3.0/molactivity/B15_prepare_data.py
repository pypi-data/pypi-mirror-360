
import numpy as np
from .B16_tensor import Tensor
from . import A7_data_process as dm
from . import A22_random as pure_random
from .A4_chem_features import ChemicalFeatureGenerator

class PureMolecularDataset:
    def __init__(self, data_file, fingerprint_type='Morgan'):
        self.molecular_data = dm.read_csv(data_file)
        
        self.smiles_strings = self.molecular_data['SMILES']
        self.fingerprint_method = fingerprint_type
        
        self.has_labels = 'ACTIVITY' in self.molecular_data.columns
        if self.has_labels:
            self.activity_labels = self.molecular_data['ACTIVITY']

    def __len__(self):
        return len(self.smiles_strings)

    def _generate_fingerprint(self, smiles: str) -> Tensor:
        try:
            feature_generator = ChemicalFeatureGenerator(fp_size=2048, radius=2)
            fingerprint = feature_generator.generate_morgan_fingerprint(smiles)
            return Tensor(fingerprint, requires_grad=False)
        except Exception as e:
            error_msg = str(e)
            if error_msg == "1":
                print(f"failed SMILES: {smiles}")
                return Tensor(np.zeros(2048, dtype=np.float32), requires_grad=False)
            elif "invalid literal for int()" in error_msg:
                print(f"repaired SMILES: {smiles}")
                return Tensor(np.zeros(2048, dtype=np.float32), requires_grad=False)
            else:
                print(f"failed SMILES: {smiles}")
                return Tensor(np.zeros(2048, dtype=np.float32), requires_grad=False)

    def __getitem__(self, index):
        smiles = self.smiles_strings[index]
        features = self._generate_fingerprint(smiles)
        if features is None:
            print(f"failed SMILES: {smiles}")
            return None, None if self.has_labels else None
        
        if self.has_labels:
            activity_label = Tensor([float(self.activity_labels[index])], requires_grad=False)
            return features, activity_label
        else:
            return features

class PureBatchProvider:
    def __init__(self, dataset, batch_size=32, shuffle=False, sampler=None):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle_flag = shuffle
        self.sampler = sampler
        self.current_position = 0
        self.indices = list(range(len(dataset)))
        if shuffle and sampler is None:
            pure_random.shuffle(self.indices)  
        elif sampler is not None:
            self.indices = list(sampler)
        self.is_prediction = not dataset.has_labels

    def __iter__(self):
        self.current_position = 0
        return self

    def __next__(self):
        if self.current_position >= len(self.dataset):
            raise StopIteration

        feature_batch = []
        label_batch = []
        
        for _ in range(self.batch_size):
            if self.current_position >= len(self.dataset):
                break
                
            idx = self.indices[self.current_position]
            if self.is_prediction:
                features = self.dataset[idx]
                if features is not None:
                    feature_batch.append(features.data)  
            else:
                features, label = self.dataset[idx]
                if features is not None and label is not None:
                    feature_batch.append(features.data) 
                    label_batch.append(label.data) 
            
            self.current_position += 1

        if not feature_batch:
            raise StopIteration

        if self.is_prediction:
            stacked_features = np.stack(feature_batch)
            return Tensor(stacked_features, requires_grad=False), None
        else:
            stacked_features = np.stack(feature_batch)
            stacked_labels = np.stack(label_batch)
            return Tensor(stacked_features, requires_grad=False), Tensor(stacked_labels, requires_grad=False)

    def __len__(self):
        return (len(self.dataset) + self.batch_size - 1) // self.batch_size

class PureBalancedSampler:
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
        class_counts = {}
        for label_tensor in self.dataset.activity_labels:
            label = int(label_tensor) if hasattr(label_tensor, '__int__') else int(label_tensor)
            class_counts[label] = class_counts.get(label, 0) + 1
        
        total_samples = sum(class_counts.values())
        class_weights = {label: total_samples/count for label, count in class_counts.items()}
        
        weights = []
        for label_tensor in self.dataset.activity_labels:
            label = int(label_tensor) if hasattr(label_tensor, '__int__') else int(label_tensor)
            weights.append(class_weights[label])
        
        return weights

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

def prepare_pure_training_dataset(csv_path, fingerprint_type='Morgan', batch_size=32, shuffle=False, balance_data=False):
    dataset = PureMolecularDataset(csv_path, fingerprint_type)
    if balance_data:
        sampler = PureBalancedSampler(dataset)
        data_loader = PureBatchProvider(dataset, batch_size=batch_size, sampler=sampler)
    else:
        data_loader = PureBatchProvider(dataset, batch_size=batch_size, shuffle=shuffle)
    return data_loader

def prepare_pure_predicting_dataset(csv_path, fingerprint_type='Morgan', batch_size=32, shuffle=False):
    dataset = PureMolecularDataset(csv_path, fingerprint_type)
    data_loader = PureBatchProvider(dataset, batch_size=batch_size, shuffle=shuffle)
    return data_loader 