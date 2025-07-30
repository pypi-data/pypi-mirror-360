from .A32_typing import Optional
from . import A20_math as math
from .A27_tools import Error_Function
from .A26_tensor import Tensor
from .A3_autograd import Function
from . import A2_arrays as arrays
from .A15_module import Module

class ReLUFunction(Function):
    @staticmethod
    def forward(ctx, x):
        if hasattr(x, 'data'):
            x_data = x.data
        else:
            x_asarray = arrays.asarray(x)
            x_data = x_asarray.data
        
        x_array = arrays.Array(x_data)
        zeros_array = arrays.zeros_like(x_array)
        max_result = arrays.maximum(x_array, zeros_array)
        result_asarray = arrays.asarray(max_result.data)
        result = result_asarray.data
        ctx.save_for_backward(x)
        return result
    
    @staticmethod
    def backward(ctx, grad_output):
        x, = ctx.saved_tensors
        if hasattr(x, 'data'):
            x_data = x.data
        else:
            x_asarray = arrays.asarray(x)
            x_data = x_asarray.data
            
        if hasattr(grad_output, 'data'):
            grad_data = grad_output.data
        else:
            grad_asarray = arrays.asarray(grad_output)
            grad_data = grad_asarray.data
            
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
                raise TypeError("In-place operations require Tensor input")
            if not x.requires_grad:
                x.requires_grad = True
            self._input = x
            max_result = arrays.maximum(x.data, 0)
            max_asarray = arrays.asarray(max_result.data)
            x.data = max_asarray.data
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
            x_asarray = arrays.asarray(x)
            x_data = x_asarray.data
        
        if approximate == 'tanh':
            sqrt_2_over_pi = math.sqrt(2 / math.pi)
            x_cubed = x_data * x_data * x_data
            inner = sqrt_2_over_pi * (x_data + 0.044715 * x_cubed)
            inner_array = arrays.Array(inner)
            tanh_result = arrays.tanh(inner_array)
            tanh_data = tanh_result.data
            
            if isinstance(tanh_data, list):
                if isinstance(tanh_data[0], list):
                    result = [[0.5 * x_data[i][j] * (1 + tanh_data[i][j]) 
                              for j in range(len(tanh_data[i]))] 
                             for i in range(len(tanh_data))]
                else:
                    result = [0.5 * x_data[i] * (1 + tanh_data[i]) 
                             for i in range(len(tanh_data))]
            else:
                result = 0.5 * x_data * (1 + tanh_data)
            
            return result
        else:
            x_over_sqrt2 = x_data / math.sqrt(2)
            return 0.5 * x_data * (1 + Error_Function(x_over_sqrt2))
    
    @staticmethod
    def backward(ctx, grad_output):
        x, = ctx.saved_tensors
        approximate = ctx.metadata['approximate']
        
        if hasattr(x, 'data'):
            x_data = x.data
        else:
            x_asarray = arrays.asarray(x)
            x_data = x_asarray.data
            
        if hasattr(grad_output, 'data'):
            grad_data = grad_output.data
        else:
            grad_asarray = arrays.asarray(grad_output)
            grad_data = grad_asarray.data
        
        if approximate == 'tanh':
            sqrt_2_over_pi = math.sqrt(2 / math.pi)
            x_sq = x_data * x_data
            x_cubed = x_data * x_sq
            inner = sqrt_2_over_pi * (x_data + 0.044715 * x_cubed)
            inner_array = arrays.Array(inner)
            tanh_result = arrays.tanh(inner_array)
            tanh_inner = tanh_result.data
            
            deriv = 0.5 * (1 + tanh_inner) + \
                   0.5 * x_data * (1 - tanh_inner * tanh_inner) * \
                   sqrt_2_over_pi * (1 + 3 * 0.044715 * x_sq)
        else:
            sqrt_2 = math.sqrt(2)
            x_over_sqrt2 = x_data / sqrt_2
            erf_term = Error_Function(x_over_sqrt2)
            x_squared = x_data * x_data
            half_neg_x_squared = -0.5 * x_squared
            exp_input = arrays.Array(half_neg_x_squared)
            exp_result = arrays.exp(exp_input)
            exp_term = exp_result.data
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



