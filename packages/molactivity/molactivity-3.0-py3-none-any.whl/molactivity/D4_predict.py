import torch
from .D2_data_loader import get_transforms, CustomImageFolder
from torch.utils.data import DataLoader
from .D3_model import VisionTrans_model
from . import D1_config as config
import os
import pandas as pd

def get_test_loader(test_data_dir, batch_size, folder_label_mapping=None):
    transform = get_transforms()
    test_dataset = CustomImageFolder(root=test_data_dir, transform=transform, folder_label_mapping=folder_label_mapping)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    return test_loader

def predict_all_class1_prob(model, device, test_loader):
    model.eval()
    results = []
    
    print("Starting prediction...")
    with torch.no_grad():
        for batch_idx, (images, labels) in enumerate(test_loader):
            images = images.to(device)
            outputs = model(images).logits
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            
            class_1_probabilities = probabilities[:, 1]
            predicted_classes = torch.argmax(probabilities, dim=1)
            
            for sample_idx, (true_label, pred_class, class_1_prob) in enumerate(
                zip(labels, predicted_classes, class_1_probabilities)
            ):
                global_idx = batch_idx * test_loader.batch_size + sample_idx
                results.append({
                    'Image_Index': global_idx + 1,
                    'True_Label': true_label.item(),
                    'Class_1_Probability': class_1_prob.item()
                })
            
            if (batch_idx + 1) % 20 == 0:
                print(f"batch {batch_idx + 1} completed")
    
    return results

def load_trained_model(model_path, num_classes, device):
    model = VisionTrans_model(num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model

def save_results_sorted_by_prob(results, output_path):
    df = pd.DataFrame(results)
    
    df_sorted = df.sort_values('Class_1_Probability', ascending=False).reset_index(drop=True)
    
    df_sorted.to_csv(output_path, index=False)
    
    return df_sorted

def analyze_ranking_performance(df_sorted):
    print("\nresults analysis")
    
    total_samples = len(df_sorted)
    total_class_1 = (df_sorted['True_Label'] == 1).sum()
    total_class_0 = total_samples - total_class_1
    
    print(f"total_samples: {total_samples}")
    print(f"total_class_1: {total_class_1} ({total_class_1/total_samples*100:.1f}%)")
    print(f"total_class_0: {total_class_0} ({total_class_0/total_samples*100:.1f}%)")
    
    intervals = [0.1, 0.2, 0.3, 0.5, 1.0]
    
    for interval in intervals:
        top_n = int(total_samples * interval)
        top_samples = df_sorted.head(top_n)
        class_1_in_top = (top_samples['True_Label'] == 1).sum()
        precision = class_1_in_top / top_n if top_n > 0 else 0
        recall = class_1_in_top / total_class_1 if total_class_1 > 0 else 0
        
        print(f"Top {interval*100:2.0f}% ({top_n:4d} samples): "
              f"contain {class_1_in_top:3d} class_1, "
              f"precision={precision:.3f}, "
              f"recall={recall:.3f}")

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"device: {device}")
    
    import glob
    model_files = glob.glob("*.pth")
    
    if not model_files:
        print("no models foound")
        return
    
    model_path = model_files[0]
    print(f"find {len(model_files)} models:")
    for i, model_file in enumerate(model_files):
        file_size = os.path.getsize(model_file) / (1024*1024)  
        marker = "(will use this model)" if model_file == model_path else ""
        print(f"  {i+1}. {model_file} ({file_size:.1f} MB) {marker}")
    
    print(f"using model: {model_path}")
    
    try:
        model = load_trained_model(model_path, config.num_classes, device)
        print("successfully loaded trained model")
        
        test_data_dir = getattr(config, 'test_data_dir', config.data_dir)
        folder_label_mapping = getattr(config, 'folder_label_mapping', None)
        test_loader = get_test_loader(test_data_dir, config.batch_size, folder_label_mapping)
        print(f"successfully loaded {len(test_loader.dataset)} images")
        
        print("start predicting")
        results = predict_all_class1_prob(model, device, test_loader)
        
        output_path = 'image_predictions.csv'
        df_sorted = save_results_sorted_by_prob(results, output_path)
        
        print(f"\npredictions completed, saved to {output_path}")
        
        analyze_ranking_performance(df_sorted)
        
        print("\ntop 10 predicted probability")
        top_10 = df_sorted.head(10)
        for _, row in top_10.iterrows():
            print(f"sample {int(row['Image_Index']):4d}: "
                  f"true label={int(row['True_Label'])}, "
                  f"predicted class_1_probability={row['Class_1_Probability']:.6f}")
        
    except Exception as e:
        print(f"error: {str(e)}")

if __name__ == "__main__":
    main() 