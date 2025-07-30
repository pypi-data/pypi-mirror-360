import numpy as np
from .B16_tensor import Tensor
from .B3_autograd import Function
from . import B13_operations as operations_T

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
                
                logits_np = np.asarray(logits_data, dtype=np.float32)
                targets_np = np.asarray(targets_data, dtype=np.float32)
                
               
                max_val = np.maximum(logits_np, 0)
                log_exp = np.log1p(np.exp(-np.abs(logits_np))) 
                bce_loss = max_val - logits_np * targets_np + log_exp
                
                sigmoid_probs = 1.0 / (1.0 + np.exp(-np.clip(logits_np, -15, 15)))
                
                pt = targets_np * sigmoid_probs + (1 - targets_np) * (1 - sigmoid_probs)
                pt = np.clip(pt, 1e-8, 1-1e-8)  
                
                focal_weight = alpha * np.power(1 - pt, gamma)
                
                focal_loss = focal_weight * bce_loss
                
                high_pred_mask = (sigmoid_probs > high_pred_threshold) & (targets_np == 0)
                if np.any(high_pred_mask):
                    penalty = high_pred_penalty * (np.exp(sigmoid_probs[high_pred_mask] * 3) - 1)
                    focal_loss[high_pred_mask] += penalty
                
                ctx.save_for_backward(
                    Tensor(logits_np), 
                    Tensor(targets_np), 
                    Tensor(sigmoid_probs), 
                    Tensor(pt),
                    Tensor(focal_weight),
                    Tensor(high_pred_mask.astype(np.float32))
                )
                
                return Tensor(focal_loss, requires_grad=logits.requires_grad)
            
            @staticmethod
            def backward(ctx, grad_output):
                logits, targets, sigmoid_probs, pt, focal_weight, high_pred_mask = ctx.saved_tensors
                
                alpha = ctx.metadata['alpha']
                gamma = ctx.metadata['gamma'] 
                high_pred_penalty = ctx.metadata['high_pred_penalty']
                
                logits_np = logits.data
                targets_np = targets.data  
                sigmoid_np = sigmoid_probs.data
                pt_np = pt.data
                focal_weight_np = focal_weight.data
                mask_np = high_pred_mask.data.astype(bool)
                grad_out_np = grad_output.data if hasattr(grad_output, 'data') else grad_output
                
                if grad_out_np.ndim == 0:
                    grad_out_np = np.array([grad_out_np])
                
                bce_grad = sigmoid_np - targets_np
                
              
                sigmoid_grad = sigmoid_np * (1 - sigmoid_np)
                dpt_dlogits = targets_np * sigmoid_grad - (1 - targets_np) * sigmoid_grad
                
                if gamma > 0:
                    dfocal_weight_dlogits = -alpha * gamma * np.power(1 - pt_np, gamma - 1) * dpt_dlogits
                else:
                    dfocal_weight_dlogits = np.zeros_like(logits_np)
                
                grad = focal_weight_np * bce_grad + dfocal_weight_dlogits * 0.1  
                
                if np.any(mask_np):
                    penalty_grad = high_pred_penalty * 3 * np.exp(3 * sigmoid_np[mask_np]) * sigmoid_grad[mask_np]
                    grad[mask_np] += penalty_grad
                
                if np.isscalar(grad_out_np) or grad_out_np.size == 1:
                    final_grad = grad * float(grad_out_np)
                else:
                    final_grad = grad * grad_out_np
                
                final_grad = np.clip(final_grad, -10.0, 10.0)
                
                return Tensor(final_grad), None
        
        focal_losses = FocalLossFunction.apply(inputs, targets)
        
        if self.reduction == 'mean':
            result = operations_T.mean(focal_losses)
        elif self.reduction == 'sum':
            result = operations_T.sum(focal_losses)
        else:
            result = focal_losses
            
        return result
