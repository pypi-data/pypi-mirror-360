from .B16_tensor import Tensor, Parameter
import math
import numpy as np
from .B7_module import Module

class Linear(Module):
    def __init__(self, in_features: int, out_features: int, bias: bool = True, 
                 device: str = 'cpu', dtype: str = 'float32'):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.use_bias = bias
        self.device = device
        self.dtype = dtype

        weight = np.random.randn(out_features, in_features).astype(np.float32)
        fan_in = in_features
        gain = math.sqrt(2.0)  
        std = gain / math.sqrt(fan_in)
        bound = math.sqrt(3.0) * std
        weight = np.random.uniform(-bound, bound, (out_features, in_features))
        self.weight = Parameter(weight)
        
        if bias:
            self.bias = Parameter(np.zeros(out_features, dtype=np.float32))
        else:
            self.bias = None

    def forward(self, input: Tensor) -> Tensor:
        if not input.requires_grad:
            input.requires_grad = True
        if input.ndim == 1:
            input = input.reshape(1, -1)
        
        output = input @ self.weight.T
        if self.use_bias and self.bias is not None:
            output = output + self.bias
        return output

    def extra_repr(self) -> str:
        return f'in_features={self.in_features}, out_features={self.out_features}, bias={self.bias is not None}'
