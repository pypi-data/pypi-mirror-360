import glob
import os
import torch
import numpy as np
import pandas as pd

def find_model_files(model_pattern='auto'):
    if model_pattern == 'auto':
        model_files = []
        
        pth_files = glob.glob("*.pth")
        for model_path in sorted(pth_files):
            if os.path.exists(model_path):
                model_files.append(model_path)
                print(f"Found model file: {model_path}")
        
        if not model_files:
            print('No trained model files (.pth) found!')
            print('Looking for any model files...')
            potential_files = glob.glob("*model*") + glob.glob("*trained*")
            for file in potential_files:
                if os.path.isfile(file) and file.endswith(('.pth', '.pt', '.pkl')):
                    model_files.append(file)
                    print(f"Found potential model file: {file}")
        
        return model_files
    elif isinstance(model_pattern, list):
        return model_pattern
    else:
        return [model_pattern]

def load_single_model(model_path, num_classes, device):
    try:
        from .D3_model import VisionTrans_model
        
        model = VisionTrans_model(num_classes)
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)
        model.eval()
        
        file_size = os.path.getsize(model_path) / (1024*1024)
        print(f"Successfully loaded model: {model_path} ({file_size:.1f} MB)")
        return model
        
    except Exception as e:
        print(f"Failed to load model {model_path}: {str(e)}")
        return None

def load_multiple_models(model_files, num_classes, device):
    models = []
    successful_files = []
    
    for model_file in model_files:
        model = load_single_model(model_file, num_classes, device)
        if model is not None:
            models.append(model)
            successful_files.append(model_file)
    
    print(f"Successfully loaded {len(models)}/{len(model_files)} models")
    return models, successful_files

def get_evaluation_data_loader(data_dir, batch_size, folder_label_mapping=None):
    try:
        from .D2_data_loader import get_test_loader
        
        if not os.path.exists(data_dir):
            print(f"Error: Dataset folder '{data_dir}' not found!")
            return None
        
        test_loader = get_test_loader(data_dir, batch_size, folder_label_mapping)
        print(f"Successfully loaded {len(test_loader.dataset)} images for evaluation")
        
        subfolders = [f for f in os.listdir(data_dir) 
                     if os.path.isdir(os.path.join(data_dir, f))]

        
        all_image_files = []
        for subfolder in subfolders:
            subfolder_path = os.path.join(data_dir, subfolder)
            for ext in ['*.png', '*.jpg', '*.jpeg']:
                image_files = glob.glob(os.path.join(subfolder_path, ext))
                all_image_files.extend(sorted(image_files))
        
        test_loader.image_files = all_image_files
        
        return test_loader
        
    except Exception as e:
        print(f"Failed to load evaluation data: {str(e)}")
        return None

def predict_with_single_model(model, test_loader, device):
    model.eval()
    all_true_labels = []
    all_probabilities = []
    
    print("Starting prediction...")
    with torch.no_grad():
        for batch_idx, (images, labels) in enumerate(test_loader):
            images = images.to(device)
            outputs = model(images).logits
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            
            class_1_probs = probabilities[:, 1].cpu().numpy()
            true_labels = labels.numpy()
            
            all_true_labels.extend(true_labels)
            all_probabilities.extend(class_1_probs)
            
            if (batch_idx + 1) % 20 == 0:
                print(f"Processed batch {batch_idx + 1}/{len(test_loader)}")
    
    return np.array(all_true_labels), np.array(all_probabilities)

def generate_ensemble_predictions(models, model_files, test_loader, device):
    all_model_probabilities = []
    true_labels = None
    individual_predictions = {}
    
    for i, (model, model_file) in enumerate(zip(models, model_files)):
        print(f'\nEvaluating with model {i+1}/{len(models)}: {model_file}')
        
        labels, probabilities = predict_with_single_model(model, test_loader, device)
        
        if true_labels is None:
            true_labels = labels
        
        all_model_probabilities.append(probabilities)
        
        model_name = os.path.splitext(os.path.basename(model_file))[0]
        individual_predictions[model_name] = {
            'probabilities': probabilities
        }
    
    all_model_probabilities = np.array(all_model_probabilities)
    ensemble_probabilities = np.mean(all_model_probabilities, axis=0)
    
    if len(models) > 1:
        ensemble_std = np.std(all_model_probabilities, axis=0)
    else:
        ensemble_std = np.zeros_like(ensemble_probabilities)
    
    return true_labels, ensemble_probabilities, ensemble_std, individual_predictions

def calculate_metrics(true_labels, probabilities):
    from sklearn.metrics import roc_auc_score
    
    metrics = {}
    
    try:
        metrics['auc_roc'] = roc_auc_score(true_labels, probabilities)
        
        return metrics
    except Exception as e:
        print(f"Error calculating metrics: {str(e)}")
        return None

def analyze_prediction_quality(true_labels, probabilities, std_devs=None, config=None, image_files=None):
    print("\n")
    print("RESULTS ANALYSIS")
    
    total_samples = len(probabilities)
    total_class_1 = np.sum(true_labels == 1)
    total_class_0 = total_samples - total_class_1
    
    print("\nDataset Statistics:")
    print(f"Total samples: {total_samples}")
    print(f"Class 1 (Active): {total_class_1} ({total_class_1/total_samples*100:.1f}%)")
    print(f"Class 0 (Inactive): {total_class_0} ({total_class_0/total_samples*100:.1f}%)")
    
    metrics = calculate_metrics(true_labels, probabilities)
    if metrics:
        print("\nPerformance Metrics:")
        print(f"AUC-ROC: {metrics['auc_roc']:.4f}")
        
     
    if config and config['analysis_parameters']['show_top_predictions'] > 0:
        print(f"\nTop {config['analysis_parameters']['show_top_predictions']} Probabilities:")
        
        sorted_indices = np.argsort(probabilities)[::-1]
        
        if image_files:
            print(f"{'Rank':<5} {'Image_Name':<30} {'Probability':<12} {'True':<5} ")
            print("-" * 60)
            
            for i in range(min(config['analysis_parameters']['show_top_predictions'], len(sorted_indices))):
                idx = sorted_indices[i]
                prob = probabilities[idx]
                true = true_labels[idx]
                image_name = os.path.basename(image_files[idx])
                
                print(f"{i+1:<5} {image_name:<30} {prob:<12.6f} {true:<5} ")
        else:
            print(f"{'Rank':<5} {'Probability':<12} {'True':<5} ")
            print("-" * 50)
            
            for i in range(min(config['analysis_parameters']['show_top_predictions'], len(sorted_indices))):
                idx = sorted_indices[i]
                prob = probabilities[idx]
                true = true_labels[idx]
                
                print(f"{i+1:<5} {prob:<12.6f} {true:<5} ")
    
def save_evaluation_results(true_labels, probabilities, std_devs, individual_predictions, output_file, test_loader):
    try:
        image_files = getattr(test_loader, 'image_files', None)
        
        if image_files is not None:
            image_names = [os.path.basename(img_file) for img_file in image_files]
            results_data = {
                'Image_Name': image_names,
                'True_Label': true_labels,
                'Ensemble_Probability': probabilities,
            }
        else:
            results_data = {
                'Image_Index': range(1, len(probabilities) + 1),
                'True_Label': true_labels,
                'Ensemble_Probability': probabilities,
            }
        
        if std_devs is not None and np.any(std_devs > 0):
            results_data['Ensemble_Std_Dev'] = std_devs
        
        for model_name, model_data in individual_predictions.items():
            results_data[f'{model_name}_Probability'] = model_data['probabilities']
        
        df = pd.DataFrame(results_data)
        df_sorted = df.sort_values('Ensemble_Probability', ascending=False).reset_index(drop=True)
        
        df_sorted.to_csv(output_file, index=False)
        print(f"\nEvaluation results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error saving results: {str(e)}")
        return False