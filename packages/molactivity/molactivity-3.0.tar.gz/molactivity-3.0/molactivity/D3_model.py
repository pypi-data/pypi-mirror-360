import torch
import os
from transformers import ViTForImageClassification, ViTConfig
from safetensors.torch import load_file

def load_pretrained_parameters(model_path):
    try:
        state_dict = load_file(model_path)
        dequantized_dict = {}
        
        base_keys = set()
        for key in state_dict.keys():
            if not key.endswith('_scale') and not key.endswith('_zero_point'):
                base_keys.add(key)
        
        
        for key in base_keys:
            weight = state_dict[key]
            scale_key = key + '_scale'
            zero_point_key = key + '_zero_point'
            
            if scale_key in state_dict and zero_point_key in state_dict:
                scale = state_dict[scale_key].item()
                zero_point = state_dict[zero_point_key].item()
                
                dequantized = (weight.float() - zero_point) * scale
                dequantized_dict[key] = dequantized.float()  
                
            else:
                if weight.dtype in (torch.int8, torch.uint8, torch.int32, torch.int64):
                    dequantized_dict[key] = weight.float()
                else:
                    dequantized_dict[key] = weight.float()
        
        return dequantized_dict
        
    except Exception as e:
        print(f"loading parameters failed: {str(e)}")
        return None

def VisionTrans_model(num_classes):
    local_model_path = "./molactivity/D8_pretrained_parameters"
    classifier_modified = False 
    model = None  
    
    if os.path.exists(local_model_path) and os.listdir(local_model_path):
        
        model_file = os.path.join(local_model_path, "pretrained_weights.safetensors")
        if os.path.exists(model_file):
            pretrained_weights = load_pretrained_parameters(model_file)
            
            if pretrained_weights is not None:
                try:
                    
                    config = ViTConfig.from_pretrained(local_model_path, local_files_only=True)
                    
                    model = ViTForImageClassification(config)
                    
                    filtered_weights = {k: v for k, v in pretrained_weights.items() 
                                      if not k.startswith('classifier.')}
                    
                    
                    model.classifier = torch.nn.Linear(in_features=model.classifier.in_features, out_features=num_classes)
                    classifier_modified = True 
                    
                    missing_keys, unexpected_keys = model.load_state_dict(filtered_weights, strict=False)
                    print("successfully loaded pre-trained parameters")

                    return model  
                    
                except Exception as e:
                    print(f"loading pretrained parameters failed: {str(e)}")
                    try:
                        config = ViTConfig.from_pretrained(local_model_path, local_files_only=True)
                        model = ViTForImageClassification(config)
                        print("Created model from config without pretrained weights")
                    except Exception as e2:
                        print(f"Failed to create model from config: {str(e2)}")
                        model = None
            else:
                try:
                    model = ViTForImageClassification.from_pretrained(local_model_path, local_files_only=True, ignore_mismatched_sizes=True)
                    print("Loaded model using from_pretrained fallback")
                except Exception as e:
                    print(f"Failed to load model with from_pretrained: {str(e)}")
                    model = None
        else:
            print("no pretrained_weights.safetensors file found")
            try:
                model = ViTForImageClassification.from_pretrained(local_model_path, local_files_only=True, ignore_mismatched_sizes=True)
                print("Loaded model using from_pretrained fallback")
            except Exception as e:
                print(f"Failed to load model with from_pretrained: {str(e)}")
                model = None
    else:
        print("no pre-trained parameters directory found")
       
    if model is None:
        print("Creating default ViT model...")
        try:
            config = ViTConfig(
                image_size=224,
                patch_size=16,
                num_channels=3,
                num_labels=num_classes,
                hidden_size=768,
                num_hidden_layers=12,
                num_attention_heads=12,
                intermediate_size=3072,
            )
            model = ViTForImageClassification(config)
            print("Created default ViT model successfully")
        except Exception as e:
            print(f"Failed to create default model: {str(e)}")
            raise RuntimeError("Could not create any model")
    
    if model is not None and not classifier_modified:
        if hasattr(model, 'classifier') and model.classifier is not None:
            model.classifier = torch.nn.Linear(in_features=model.classifier.in_features, out_features=num_classes)
        else:
            model.classifier = torch.nn.Linear(in_features=768, out_features=num_classes) 
    
    return model

