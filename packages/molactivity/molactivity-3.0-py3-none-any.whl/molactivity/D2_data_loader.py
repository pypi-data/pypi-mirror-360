import os
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

def get_transforms():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])

class CustomImageFolder(datasets.ImageFolder):
    def __init__(self, root, transform=None, folder_label_mapping=None):
        self.folder_label_mapping = folder_label_mapping
        super().__init__(root, transform)
    
    def find_classes(self, directory):
        classes = [d.name for d in os.scandir(directory) if d.is_dir() and d.name != '.ipynb_checkpoints']
        
        if self.folder_label_mapping:
            
            for cls in classes:
                if cls not in self.folder_label_mapping:
                    raise ValueError(f"Folder '{cls}' not found in folder_label_mapping. "
                                   f"Please add it to the mapping configuration.")
            
            classes_with_labels = [(cls, self.folder_label_mapping[cls]) for cls in classes]
            classes_with_labels.sort(key=lambda x: x[1])  
            classes = [cls for cls, _ in classes_with_labels]
            class_to_idx = {cls: self.folder_label_mapping[cls] for cls in classes}
        else:
            classes.sort()
            class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
        
        return classes, class_to_idx

def load_datasets(data_dir, folder_label_mapping=None):
    transform = get_transforms()
    dataset = CustomImageFolder(root=data_dir, transform=transform, folder_label_mapping=folder_label_mapping)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    return train_dataset, val_dataset

def get_data_loaders(train_dataset, val_dataset, batch_size):
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader

def get_test_loader(test_data_dir, batch_size, folder_label_mapping=None):
    transform = get_transforms()
    test_dataset = CustomImageFolder(root=test_data_dir, transform=transform, folder_label_mapping=folder_label_mapping)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    return test_loader
