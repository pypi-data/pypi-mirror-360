from typing import Optional
import math
from scipy.special import erf
from .B16_tensor import Tensor
from .B3_autograd import Function
import numpy as np
from .B7_module import Module

class ReLUFunction(Function):
    @staticmethod
    def forward(ctx, x):
        if hasattr(x, 'data'):
            x_data = x.data
        else:
            x_data = np.array(x)
        
        zeros = np.zeros_like(x_data)
        result = np.maximum(x_data, zeros)
        ctx.save_for_backward(x)
        return result
    
    @staticmethod
    def backward(ctx, grad_output):
        x, = ctx.saved_tensors
        if hasattr(x, 'data'):
            x_data = x.data
        else:
            x_data = np.array(x)
            
        if hasattr(grad_output, 'data'):
            grad_data = grad_output.data
        else:
            grad_data = np.array(grad_output)
            
        grad_x = grad_data * (x_data > 0)
        return Tensor(grad_x)

class ReLU(Module):
    def __init__(self, inplace: bool = False):
        super().__init__()
        self.inplace = inplace
        self._input = None

    def forward(self, x: Tensor) -> Tensor:
        if self.inplace:
            if not isinstance(x, Tensor):
                raise TypeError
            if not x.requires_grad:
                x.requires_grad = True
            self._input = x
            x.data = np.maximum(x.data, 0)
            return x
        else:
            return ReLUFunction.apply(x)

    def __str__(self) -> str:
        return f"ReLU(inplace={self.inplace})"

    def backward(self, grad_output: Tensor) -> Tensor:
        if self.inplace:
            grad_input = grad_output.data * (self._input.data > 0)
            return Tensor(grad_input, requires_grad=grad_output.requires_grad)
        else:
            return grad_output

    def __call__(self, input: Tensor) -> Tensor:
        return self.forward(input)

class Sigmoid(Module):
    def __init__(self) -> None:
        super().__init__()

        self._output_cache: Optional[Tensor] = None

    def forward(self, input: Tensor) -> Tensor:
        self._output_cache = Tensor(1) / (Tensor(1) + (-input).exp())
        return self._output_cache

    def __call__(self, input: Tensor) -> Tensor:
        return self.forward(input)

class GELUFunction(Function):
    @staticmethod
    def forward(ctx, x, approximate: str = 'tanh'):
        ctx.save_for_backward(x)
        ctx.metadata['approximate'] = approximate
        
        if hasattr(x, 'data'):
            x_data = x.data
        else:
            x_data = np.array(x)
        
        if approximate == 'tanh':
            sqrt_2_over_pi = math.sqrt(2 / math.pi)
            x_cubed = x_data * x_data * x_data
            inner = sqrt_2_over_pi * (x_data + 0.044715 * x_cubed)
            return 0.5 * x_data * (1 + np.tanh(inner))
        else:
            x_over_sqrt2 = x_data / math.sqrt(2)
            return 0.5 * x_data * (1 + erf(x_over_sqrt2))
    
    @staticmethod
    def backward(ctx, grad_output):
        x, = ctx.saved_tensors
        approximate = ctx.metadata['approximate']
        
        if hasattr(x, 'data'):
            x_data = x.data
        else:
            x_data = np.array(x)
            
        if hasattr(grad_output, 'data'):
            grad_data = grad_output.data
        else:
            grad_data = np.array(grad_output)
        
        if approximate == 'tanh':
            sqrt_2_over_pi = math.sqrt(2 / math.pi)
            x_sq = x_data * x_data
            x_cubed = x_data * x_sq
            inner = sqrt_2_over_pi * (x_data + 0.044715 * x_cubed)
            tanh_inner = np.tanh(inner)
            
            deriv = 0.5 * (1 + tanh_inner) + \
                   0.5 * x_data * (1 - tanh_inner * tanh_inner) * \
                   sqrt_2_over_pi * (1 + 3 * 0.044715 * x_sq)
        else:
            sqrt_2 = math.sqrt(2)
            x_over_sqrt2 = x_data / sqrt_2
            erf_term = erf(x_over_sqrt2)
            exp_term = np.exp(-0.5 * x_data * x_data)
            deriv = 0.5 * (1 + erf_term) + x_data * exp_term / math.sqrt(2 * math.pi)
        
        return Tensor(grad_data * deriv)

class GELU(Module):
    def __init__(self, approximate: str = 'tanh') -> None:
        super().__init__()

        assert approximate in ['tanh', None], "approximate must be 'tanh' or None"
        self.approximate = approximate

    def forward(self, input: Tensor) -> Tensor:
        return GELUFunction.apply(input, self.approximate)

    def __call__(self, input: Tensor) -> Tensor:
        return self.forward(input)

class LeakyReLU(Module):
    def __init__(self, negative_slope: float = 0.01, inplace: bool = False) -> None:
        super().__init__()

        self.negative_slope = negative_slope
        self.inplace = inplace
        self._input_cache: Optional[Tensor] = None

    def forward(self, input: Tensor) -> Tensor:
        self._input_cache = input if not self.inplace else input.clone()
        
        if self.inplace:
            input.relu_()
            input.add_((self._input_cache < 0).type_as(input) * self.negative_slope * self._input_cache)
            return input
        else:
            pos = input.relu()
            neg = (input < 0).type_as(input) * self.negative_slope * input
            return pos + neg

    def __call__(self, input: Tensor) -> Tensor:
        return self.forward(input)

class Swish(Module):
    def __init__(self) -> None:
        super().__init__()

        self._input_cache: Optional[Tensor] = None
        self._sigmoid_cache: Optional[Tensor] = None

    def forward(self, input: Tensor) -> Tensor:
        self._input_cache = input.clone()
        self._sigmoid_cache = Tensor(1) / (Tensor(1) + (-input).exp())
        return input * self._sigmoid_cache

    def __call__(self, input: Tensor) -> Tensor:
        return self.forward(input)

def relu(input: Tensor, inplace: bool = False) -> Tensor:
    return ReLU(inplace=inplace).forward(input)

def gelu(input: Tensor, approximate: str = 'tanh') -> Tensor:
    return GELU(approximate=approximate).forward(input)

def leaky_relu(input: Tensor, negative_slope: float = 0.01, inplace: bool = False) -> Tensor:
    return LeakyReLU(negative_slope=negative_slope, inplace=inplace).forward(input)
