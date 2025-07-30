
from . import A2_arrays as arrays
from .A26_tensor import Tensor
from .A3_autograd import Function
from . import A16_operations as operations
from . import A20_math as math

class FocalLoss:
    def __init__(self, alpha=0.25, gamma=2.0, high_pred_penalty=20.0, high_pred_threshold=0.9, reduction='mean'):
        self.alpha = alpha
        self.gamma = gamma
        self.high_pred_penalty = high_pred_penalty
        self.high_pred_threshold = high_pred_threshold
        self.reduction = reduction

    def __call__(self, inputs, targets):
        return self.forward(inputs, targets)

    def forward(self, inputs, targets):
    
        if not isinstance(inputs, Tensor):
            inputs = Tensor(inputs, requires_grad=True)
        if not isinstance(targets, Tensor):
            targets = Tensor(targets, requires_grad=False)
        
        alpha = self.alpha
        gamma = self.gamma
        high_pred_penalty = self.high_pred_penalty
        high_pred_threshold = self.high_pred_threshold
        
        class FocalLossFunction(Function):
            @staticmethod
            def forward(ctx, logits, targets):
                ctx.metadata = {
                    'alpha': alpha,
                    'gamma': gamma,
                    'high_pred_penalty': high_pred_penalty,
                    'high_pred_threshold': high_pred_threshold
                }
                
                logits_data = logits.data if hasattr(logits, 'data') else logits
                targets_data = targets.data if hasattr(targets, 'data') else targets
                
                logits_array = arrays.asarray(logits_data, dtype='float')
                targets_array = arrays.asarray(targets_data, dtype='float')
                logits_np = logits_array.data
                targets_np = targets_array.data
                
                if isinstance(logits_np, list):
                    if isinstance(logits_np[0], list):
                        flat_logits = [float(item) for sublist in logits_np for item in sublist]
                    else:
                        flat_logits = [float(item) for item in logits_np]
                    logits_np = flat_logits
                else:
                    logits_np = [float(logits_np)]
                    
                if isinstance(targets_np, list):
                    if isinstance(targets_np[0], list):
                        flat_targets = [float(item) for sublist in targets_np for item in sublist]
                    else:
                        flat_targets = [float(item) for item in targets_np]
                    targets_np = flat_targets
                else:
                    targets_np = [float(targets_np)]
                
                min_len = min(len(logits_np), len(targets_np))
                logits_np = logits_np[:min_len]
                targets_np = targets_np[:min_len]
                
              
                max_vals = [max(logit, 0.0) for logit in logits_np]
                abs_logits = [abs(logit) for logit in logits_np]
                
                exp_neg_abs = []
                for abs_logit in abs_logits:
                    try:
                        exp_val = math.exp(-abs_logit)
                        log_exp_val = math.log(1 + exp_val)
                        exp_neg_abs.append(log_exp_val)
                    except (OverflowError, ValueError):
                        exp_neg_abs.append(0.0)
                
                bce_loss = []
                for i in range(len(logits_np)):
                    bce_val = max_vals[i] - logits_np[i] * targets_np[i] + exp_neg_abs[i]
                    bce_loss.append(bce_val)
                
                sigmoid_probs = []
                for logit in logits_np:
                    clipped_logit = max(-15.0, min(15.0, logit))
                    try:
                        sigmoid_val = 1.0 / (1.0 + math.exp(-clipped_logit))
                        sigmoid_probs.append(sigmoid_val)
                    except (OverflowError, ValueError):
                        sigmoid_probs.append(0.5)
                
                pt = []
                for i in range(len(targets_np)):
                    pt_val = targets_np[i] * sigmoid_probs[i] + (1 - targets_np[i]) * (1 - sigmoid_probs[i])
                    pt_val = max(1e-8, min(1-1e-8, pt_val))
                    pt.append(pt_val)
                
                focal_weight = []
                for pt_val in pt:
                    try:
                        weight_val = alpha * pow(1 - pt_val, gamma)
                        focal_weight.append(weight_val)
                    except (OverflowError, ValueError):
                        focal_weight.append(alpha)
                
                focal_loss = []
                for i in range(len(bce_loss)):
                    loss_val = focal_weight[i] * bce_loss[i]
                    focal_loss.append(loss_val)
                
                for i in range(len(focal_loss)):
                    if sigmoid_probs[i] > high_pred_threshold and targets_np[i] == 0:
                        penalty_factor = 1.5
                        focal_loss[i] *= penalty_factor
                
                high_pred_mask_float = []
                for i in range(len(sigmoid_probs)):
                    mask_val = 1.0 if (sigmoid_probs[i] > high_pred_threshold and targets_np[i] == 0) else 0.0
                    high_pred_mask_float.append(mask_val)
                
                ctx.save_for_backward(
                    Tensor(logits_np), 
                    Tensor(targets_np), 
                    Tensor(sigmoid_probs), 
                    Tensor(pt),
                    Tensor(focal_weight),
                    Tensor(high_pred_mask_float)
                )
                
                return Tensor(focal_loss, requires_grad=logits.requires_grad)
            
            @staticmethod
            def backward(ctx, grad_output):
                logits, targets, sigmoid_probs, pt, focal_weight, high_pred_mask = ctx.saved_tensors
                
                alpha = ctx.metadata['alpha']
                gamma = ctx.metadata['gamma'] 
                high_pred_penalty = ctx.metadata['high_pred_penalty']
                
                def safe_extract_data(tensor_data):
                    if hasattr(tensor_data, 'data'):
                        data = tensor_data.data
                    else:
                        data = tensor_data
                    
                    if hasattr(data, 'tolist'):
                        return data.tolist()
                    elif hasattr(data, '__iter__') and not isinstance(data, str):
                        if isinstance(data, list):
                            return [safe_extract_data(item) if hasattr(item, 'data') or hasattr(item, 'tolist') else float(item) for item in data]
                        else:
                            return list(data)
                    else:
                        return float(data)
                
                try:
                    logits_data = safe_extract_data(logits)
                    targets_data = safe_extract_data(targets)
                    sigmoid_data = safe_extract_data(sigmoid_probs)
                    pt_data = safe_extract_data(pt)
                    focal_weight_data = safe_extract_data(focal_weight)
                    mask_data = safe_extract_data(high_pred_mask)
                    
                    if not isinstance(logits_data, list):
                        logits_data = [logits_data]
                    if not isinstance(targets_data, list):
                        targets_data = [targets_data]
                    if not isinstance(sigmoid_data, list):
                        sigmoid_data = [sigmoid_data]
                    if not isinstance(pt_data, list):
                        pt_data = [pt_data]
                    if not isinstance(focal_weight_data, list):
                        focal_weight_data = [focal_weight_data]
                    if not isinstance(mask_data, list):
                        mask_data = [mask_data]
                    
                    grad = []
                    for i in range(len(sigmoid_data)):
                        bce_grad = float(sigmoid_data[i]) - float(targets_data[i])
                        
                        sigmoid_val = float(sigmoid_data[i])
                        sigmoid_grad = sigmoid_val * (1.0 - sigmoid_val)
                        
                        target_val = float(targets_data[i])
                        if target_val == 1.0:
                            dpt_dlogits = sigmoid_grad
                        else:
                            dpt_dlogits = -sigmoid_grad
                        
                        pt_val = float(pt_data[i])
                        focal_weight_val = float(focal_weight_data[i])
                        
                        if gamma > 0:
                            try:
                                power_term = pow(1.0 - pt_val, gamma - 1)
                                dfocal_weight_dlogits = -alpha * gamma * power_term * dpt_dlogits
                            except (OverflowError, ValueError, ZeroDivisionError):
                                dfocal_weight_dlogits = 0.0
                        else:
                            dfocal_weight_dlogits = 0.0
                        
                        logit_val = float(logits_data[i])
                        max_val = max(logit_val, 0.0)
                        abs_logit = abs(logit_val)
                        try:
                            log_exp_term = math.log(1.0 + math.exp(-abs_logit))
                        except (OverflowError, ValueError):
                            log_exp_term = 0.0
                        bce_loss_val = max_val - logit_val * target_val + log_exp_term
                        
                        
                        focal_grad = focal_weight_val * bce_grad + dfocal_weight_dlogits * bce_loss_val
                        
                        mask_val = float(mask_data[i])
                        if mask_val > 0.5: 
                            if sigmoid_val > 0.9 and target_val == 0.0:
                                try:
                                    exp_term = math.exp(3.0 * sigmoid_val)
                                    penalty_grad = high_pred_penalty * 3.0 * exp_term * sigmoid_grad
                                    focal_grad += penalty_grad
                                except (OverflowError, ValueError):
                                    focal_grad += high_pred_penalty * 0.1 * sigmoid_grad
                        
                        grad.append(focal_grad)
                    
                    grad_out_data = safe_extract_data(grad_output)
                    if not isinstance(grad_out_data, list):
                        grad_out_data = [grad_out_data]
                    
                    final_grad = []
                    if len(grad_out_data) == 1:
                        scalar_grad = float(grad_out_data[0])
                        for g in grad:
                            final_grad.append(g * scalar_grad)
                    else:
                        for i in range(min(len(grad), len(grad_out_data))):
                            out_grad_val = float(grad_out_data[i])
                            final_grad.append(grad[i] * out_grad_val)
                        for i in range(len(grad_out_data), len(grad)):
                            final_grad.append(0.0)
                    
                    clipped_grad = []
                    for g in final_grad:
                        if isinstance(g, (int, float)) and not (math.isnan(g) or math.isinf(g)):
                            abs_g = abs(g)
                            if abs_g > 10.0:
                                clipped_val = math.copysign(10.0 + math.log(1.0 + abs_g - 10.0), g)
                            elif abs_g < 1e-8:
                                clipped_val = 0.0
                            else:
                                clipped_val = g
                            clipped_grad.append(clipped_val)
                        else:
                            clipped_grad.append(0.0)
                    
                    return Tensor(clipped_grad), None
                    
                except Exception as e:
                    pass
                   
        focal_losses = FocalLossFunction.apply(inputs, targets)
        
        if self.reduction == 'mean':
            result = operations.mean(focal_losses)
        elif self.reduction == 'sum':
            result = operations.sum(focal_losses)
        else:
            result = focal_losses
            
        return result
