
import glob
import os
import torch
import tempfile
import shutil
import numpy as np
import pandas as pd


def find_model_files(model_pattern='auto'):
    if model_pattern == 'auto':
        model_files = []
        
        pth_files = glob.glob("*.pth")
        for model_path in sorted(pth_files):
            if os.path.exists(model_path):
                model_files.append(model_path)
        
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

def get_prediction_data_loader(data_dir, batch_size):
    try:
        from .D2_data_loader import get_test_loader
        
        if not os.path.exists(data_dir):
            print(f"Error: Dataset folder '{data_dir}' not found!")
            return None
        
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(glob.glob(os.path.join(data_dir, ext)))
        
        if not image_files:
            print(f"No image files found in {data_dir}")
            return None
        
        print(f"Found {len(image_files)} image files")
        
        temp_dir = tempfile.mkdtemp()
        temp_class_dir = os.path.join(temp_dir, "unknown")  
        os.makedirs(temp_class_dir, exist_ok=True)
        
        temp_image_paths = []
        for i, image_file in enumerate(sorted(image_files)):
            filename = f"image_{i:04d}" + os.path.splitext(image_file)[1]
            temp_path = os.path.join(temp_class_dir, filename)
            shutil.copy2(image_file, temp_path)
            temp_image_paths.append(temp_path)
        
        try:
            test_loader = get_test_loader(temp_dir, batch_size)
            print(f"Successfully loaded {len(test_loader.dataset)} images for prediction")
            
            test_loader.temp_dir = temp_dir
            test_loader.original_image_files = sorted(image_files)
            
            return test_loader
            
        except Exception as e:
            print(f"Failed to use standard data loader: {str(e)}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None
        
    except Exception as e:
        print(f"Failed to load prediction data: {str(e)}")
        return None

def predict_with_single_model(model, prediction_loader, device):
    model.eval()
    all_probabilities = []
    
    print("Starting prediction...")
    with torch.no_grad():
        for batch_idx, batch_data in enumerate(prediction_loader):
            if isinstance(batch_data, (list, tuple)) and len(batch_data) == 2:
                images, _ = batch_data  
            else:
                images = batch_data
            
            images = images.to(device)
            outputs = model(images).logits
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            
            class_1_probs = probabilities[:, 1].cpu().numpy()
            all_probabilities.extend(class_1_probs)
            
            if (batch_idx + 1) % 20 == 0:
                print(f"Processed batch {batch_idx + 1}/{len(prediction_loader)}")
    
    return np.array(all_probabilities)

def generate_ensemble_predictions(models, model_files, prediction_loader, device):
    all_model_probabilities = []
    individual_predictions = {}
    
    for i, (model, model_file) in enumerate(zip(models, model_files)):
        print(f'\nPredicting with model {i+1}/{len(models)}: {model_file}')
        
        probabilities = predict_with_single_model(model, prediction_loader, device)
        
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
    
    return ensemble_probabilities, ensemble_std, individual_predictions

def save_prediction_results(probabilities, std_devs, individual_predictions, output_file, image_files=None):
    try:
        if image_files is not None:
            image_names = [os.path.basename(img_file) for img_file in image_files]
            results_data = {
                'Image_Name': image_names,
                'Ensemble_Probability': probabilities,
            }
        else:
            results_data = {
                'Image_Index': range(1, len(probabilities) + 1),
                'Ensemble_Probability': probabilities,
            }
        
        if std_devs is not None and np.any(std_devs > 0):
            results_data['Ensemble_Std_Dev'] = std_devs
        
        for model_name, model_data in individual_predictions.items():
            results_data[f'{model_name}_Probability'] = model_data['probabilities']
        
        df = pd.DataFrame(results_data)
        df_sorted = df.sort_values('Ensemble_Probability', ascending=False).reset_index(drop=True)
        
        df_sorted.to_csv(output_file, index=False)
        print(f"\nPrediction results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error saving results: {str(e)}")
        return False