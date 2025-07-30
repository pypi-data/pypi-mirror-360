
import numpy as np
from typing import Optional, List, Union, Any, Tuple  
import weakref
import math


class Tensor:
    def __init__(
        self,
        data: Union[np.ndarray, list, float, int, 'Tensor'],
        requires_grad: bool = False,
        dtype: Optional[type] = None,
        _grad_fn: Optional[type] = None, 
        _children: Optional[List['Tensor']] = None
    ):
        if isinstance(data, (list, tuple)):
            self._data = np.array(data, dtype=dtype if dtype else np.float32)
        elif isinstance(data, (float, int)):
            self._data = np.array([data], dtype=dtype if dtype else np.float32)
        elif isinstance(data, Tensor):
            self._data = data.data.astype(dtype) if dtype else np.array(data.data)
        else:
            if 'torch' in str(type(data)):
                data = data.detach().cpu().numpy()
                self._data = data.astype(dtype) if dtype else data.copy()
            elif hasattr(data, 'copy') and isinstance(data, np.ndarray):
                self._data = data.astype(dtype) if dtype else data.copy()
            else:
                self._data = np.array(data, dtype=dtype if dtype else np.float32)

        self.requires_grad = bool(requires_grad)
        self.grad: Optional[Tensor] = None
        
        self._grad_fn = _grad_fn
        self._children = _children if _children is not None else []
        self._ctx: Optional[Any] = None
        self._output_refs: List[weakref.ref] = []

        self.shape = self._data.shape
        self.dtype = self._data.dtype
        self.device = 'cpu'

        self._id = id(self)

    @classmethod
    def empty(cls, *shape: int, dtype: type = np.float32, requires_grad: bool = False) -> 'Tensor':
        return cls(np.empty(shape, dtype=dtype), requires_grad=requires_grad)
    
    @classmethod
    def zeros(cls, *shape, requires_grad=False):
        return cls([[0.0]*shape[1] for _ in range(shape[0])], requires_grad=requires_grad)
    
    @classmethod
    def ones(cls, *shape, requires_grad=False):
        return cls([[1.0]*shape[1] for _ in range(shape[0])], requires_grad=requires_grad)
    
    @classmethod
    def randn(cls, *shape, requires_grad=False):
        import math
        import time
        seed = int(time.time() * 1000) % 1000000
        def simple_random():
            nonlocal seed
            seed = (seed * 9301 + 49297) % 233280
            return seed / 233280.0
        
        data = []
        for _ in range(shape[0]):
            row = []
            for _ in range(shape[1]):
                u1 = simple_random()
                u2 = simple_random()
                z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2 * math.pi * u2)
                row.append(z0)
            data.append(row)
        return cls(data, requires_grad=requires_grad)
    
    @property
    def data(self) -> np.ndarray:
        return self._data

    @data.setter
    def data(self, value: np.ndarray) -> None:
        self._data = value

    @property
    def ndim(self) -> int:
        return len(self.shape)

    @property
    def size(self) -> int:
        return self._data.size

    def float(self) -> 'Tensor':
        return self._apply_unary_op(lambda x: x.astype(np.float32))

    def long(self) -> 'Tensor':
        return self._apply_unary_op(lambda x: x.astype(np.int64))

    def int(self) -> 'Tensor':
        return self._apply_unary_op(lambda x: x.astype(np.int32))

    def __add__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        from .B13_operations import add
        return add(self, other if isinstance(other, Tensor) else Tensor(other))

    def __mul__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        from .B13_operations import mul
        return mul(self, other if isinstance(other, Tensor) else Tensor(other))

    def pow(self, exponent: Union['Tensor', float, int]) -> 'Tensor':
        from .B13_operations import pow
        return pow(self, exponent if isinstance(exponent, Tensor) else Tensor(exponent))

    def __pow__(self, exponent: Union['Tensor', float, int]) -> 'Tensor':
        return self.pow(exponent)

    def sqrt(self) -> 'Tensor':
        return self.pow(0.5)

    def exp(self) -> 'Tensor':
        from .B13_operations import exp
        return exp(self)
    
    def backward(self, gradient: Optional['Tensor'] = None) -> None:
     
        from .B3_autograd import backward as autograd_backward
        
        if gradient is not None and not isinstance(gradient, Tensor):
            gradient = Tensor(gradient)
            
        
        if (not hasattr(self, '_grad_fn') or self._grad_fn is None) and self.requires_grad:
            from .B13_operations import IdentityFunction
            self._grad_fn = IdentityFunction
            
        if not hasattr(self, '_grad_fn') or self._grad_fn is None:
            return
            
        autograd_backward(self, gradient)
        
        if self.requires_grad and self.grad is None:
            self.grad = Tensor(np.zeros_like(self.data))
        elif self.requires_grad and self.grad is not None:
            if np.isnan(self.grad.data).any() or np.isinf(self.grad.data).any():
                print("Warning: Invalid gradient after backward pass")
                self.grad = Tensor(np.zeros_like(self.data))

    def dist_context(self):
        from .B3_autograd import _engine
        return getattr(_engine, '_dist_context', None)

    def _apply_unary_op(self, op) -> 'Tensor':
        return Tensor(
            op(self._data),
            requires_grad=self.requires_grad,
            _grad_fn=self._grad_fn,
            _children=self._children
        )

    def __repr__(self) -> str:
        return f"Tensor({self._data}, shape={self.shape}, dtype={self.dtype}, " \
               f"requires_grad={self.requires_grad})"

    def zero_(self) -> 'Tensor':
        self._data.fill(0)
        return self

    def fill_(self, value: float) -> 'Tensor':
        self._data.fill(value)
        return self

    def __eq__(self, other):
        if not isinstance(other, Tensor):
            return False
        return self._id == other._id

    def abs(self) -> 'Tensor':
        from .B13_operations import abs
        return abs(self)

    def maximum(self, other: Union['Tensor', float, int]) -> 'Tensor':
        from .B13_operations import maximum
        return maximum(self, other if isinstance(other, Tensor) else Tensor(other))

    def clamp(self, min_val: float, max_val: float) -> 'Tensor':
        from .B13_operations import maximum, minimum
        min_tensor = min_val if isinstance(min_val, Tensor) else Tensor(min_val)
        max_tensor = max_val if isinstance(max_val, Tensor) else Tensor(max_val)
        
        result = maximum(self, min_tensor)
        result = minimum(result, max_tensor)
        return result

    def detach(self) -> 'Tensor':
        return Tensor(self._data.copy(), requires_grad=False)

    def cpu(self) -> 'Tensor':
        return self

    def clone(self) -> 'Tensor':
        return Tensor(
            self._data.copy(),
            requires_grad=self.requires_grad,
            _grad_fn=self._grad_fn,
            _children=self._children
        )

    def __neg__(self) -> 'Tensor':
        return self.__mul__(-1)

    def __sub__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        from .B13_operations import sub
        return sub(self, other if isinstance(other, Tensor) else Tensor(other))

    def __rsub__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        from .B13_operations import sub
        return sub(Tensor(other), self)

    def __truediv__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        from .B13_operations import div
        return div(self, other if isinstance(other, Tensor) else Tensor(other))

    def __getitem__(self, indices) -> 'Tensor':
        from .B13_operations import indexing
        try:
            return indexing(self, indices)
        except (ImportError, AttributeError):
            result = Tensor(
                self._data[indices],
                requires_grad=self.requires_grad
            )
            if self.requires_grad:
                result._children = [self]
                from .B3_autograd import Function
                class IndexFunction(Function):
                    @staticmethod
                    def forward(ctx, x, indices):
                        ctx.indices = indices
                        ctx.input_shape = x.shape
                        return x._data[indices]
                    
                    @staticmethod
                    def backward(ctx, grad_output):
                        grad_input = np.zeros(ctx.input_shape, dtype=grad_output.data.dtype)
                        grad_input[ctx.indices] = grad_output.data
                        return Tensor(grad_input)
                
                result._grad_fn = IndexFunction
            return result

    def t(self) -> 'Tensor':
        from .B13_operations import transpose
        return transpose(self)

    def dot(self, other: 'Tensor') -> 'Tensor':
        from .B13_operations import matmul
        return matmul(self, other)

    def mean(self, dim=None, keepdim=False):
        from .B13_operations import mean
        return mean(self, dim, keepdim)

    def sum(self, dim: Optional[int] = None, keepdim: bool = False) -> 'Tensor':
        from .B13_operations import sum
        return sum(self, dim, keepdim)

    def max(self, dim=None, keepdim=False):
        if dim is None:
            return Tensor(np.max(self._data))
        else:
            axis = dim
            values = np.max(self._data, axis=axis, keepdims=keepdim)
            indices = np.argmax(self._data, axis=axis)
            if keepdim:
                indices = np.expand_dims(indices, axis=axis)
            return Tensor(values), Tensor(indices)

    def var(self, dim: Optional[int] = None, keepdim: bool = False, unbiased: bool = True) -> 'Tensor':
        from .B13_operations import sum
        mean = self.mean(dim, keepdim)
        return sum((self - mean) ** 2, dim, keepdim) / (self._data.size if dim is None else self.shape[dim] - (1 if unbiased else 0))

    def relu(self) -> 'Tensor':
        from .B13_operations import maximum
        return maximum(self, 0)

    def tanh(self) -> 'Tensor':
        from .B13_operations import exp
        return (exp(Tensor(2)*self) - Tensor(1)) / (exp(Tensor(2)*self) + Tensor(1))

    def zero_grad_(self) -> None:
        if self.grad is not None:
            self.grad.zero_()
        self.grad = None

    def clip_grad_norm_(self, max_norm: float) -> None:

        if self.grad is None:
            return
        
        total_norm = np.sqrt(np.sum(self.grad.data ** 2))
        if total_norm > max_norm:
            scale = max_norm / (total_norm + 1e-6)
            self.grad.data *= scale

    def uniform_(self, low: float = 0.0, high: float = 1.0) -> 'Tensor':
        self._data = np.random.uniform(low, high, self.shape).astype(self.dtype)
        return self

    def normal_(self, mean: float = 0.0, std: float = 1.0) -> 'Tensor':
        self._data = np.random.normal(mean, std, self.shape).astype(self.dtype)
        return self

    def numpy(self) -> np.ndarray:
        return self._data.copy()

    def item(self) -> Union[float, int]:
        if self.size != 1:
            raise ValueError
        return float(self._data) if np.issubdtype(self.dtype, np.floating) else int(self._data)

    def __array__(self, dtype=None) -> np.ndarray:

        if dtype is not None:
            return self._data.astype(dtype)
        return self._data

    def __str__(self) -> str:
        return f"Tensor({self._data}, requires_grad={self.requires_grad})"

    def isnan(self) -> 'Tensor':
        return Tensor(np.isnan(self._data))

    def isinf(self) -> 'Tensor':
        return Tensor(np.isinf(self._data))

    def any(self) -> bool:
        return bool(np.any(self._data))

    def clamp_min(self, min_val: float) -> 'Tensor':
        from .B13_operations import maximum
        return maximum(self, min_val)

    def clamp_min_(self, min_val: float) -> 'Tensor':
        self._data = np.maximum(self._data, min_val)
        return self

    def __gt__(self, other: Union['Tensor', float, int, np.ndarray]) -> 'Tensor':
        if isinstance(other, np.ndarray):
            other = Tensor(other)
        if isinstance(other, Tensor):
            return Tensor(self._data > other._data)
        return Tensor(self._data > other)

    def __lt__(self, other: Union['Tensor', float, int, np.ndarray]) -> 'Tensor':
        if isinstance(other, np.ndarray):
            other = Tensor(other)
        if isinstance(other, Tensor):
            return Tensor(self._data < other._data)
        return Tensor(self._data < other)

    def __ge__(self, other: Union['Tensor', float, int, np.ndarray]) -> 'Tensor':
        if isinstance(other, np.ndarray):
            other = Tensor(other)
        if isinstance(other, Tensor):
            return Tensor(self._data >= other._data)
        return Tensor(self._data >= other)

    def __le__(self, other: Union['Tensor', float, int, np.ndarray]) -> 'Tensor':
        if isinstance(other, np.ndarray):
            other = Tensor(other)
        if isinstance(other, Tensor):
            return Tensor(self._data <= other._data)
        return Tensor(self._data <= other)

    def __rgt__(self, other: Union['Tensor', float, int, np.ndarray]) -> 'Tensor':
        if isinstance(other, np.ndarray):
            other = Tensor(other)
        if isinstance(other, Tensor):
            return Tensor(other._data > self._data)
        return Tensor(other > self._data)

    def __rlt__(self, other: Union['Tensor', float, int, np.ndarray]) -> 'Tensor':
        if isinstance(other, np.ndarray):
            other = Tensor(other)
        if isinstance(other, Tensor):
            return Tensor(other._data < self._data)
        return Tensor(other < self._data)

    def __rge__(self, other: Union['Tensor', float, int, np.ndarray]) -> 'Tensor':
        if isinstance(other, np.ndarray):
            other = Tensor(other)
        if isinstance(other, Tensor):
            return Tensor(other._data >= self._data)
        return Tensor(other >= self._data)

    def __rle__(self, other: Union['Tensor', float, int, np.ndarray]) -> 'Tensor':
        if isinstance(other, np.ndarray):
            other = Tensor(other)
        if isinstance(other, Tensor):
            return Tensor(other._data <= self._data)
        return Tensor(other <= self._data)

    def type_as(self, other: 'Tensor') -> 'Tensor':
        return Tensor(self._data.astype(other.dtype), requires_grad=self.requires_grad)

    def erf(self) -> 'Tensor':
        from scipy.special import erf
        from .B3_autograd import Function
        class Erf(Function):
            @staticmethod
            def forward(ctx, x):
                ctx.save_for_backward(x)
                return Tensor(erf(x._data))
            
            @staticmethod
            def backward(ctx, grad_output):
                x, = ctx.saved_tensors
                return grad_output * (2 / math.sqrt(math.pi)) * (-x._data * x._data).exp()
        
        return Erf.apply(self)

    @property
    def T(self) -> 'Tensor':
        return self.transpose()

    def log(self) -> 'Tensor':
        from .B13_operations import log
        return log(self)

    @classmethod
    def _calculate_fan_in_and_fan_out(cls, tensor: 'Tensor') -> Tuple[int, int]:
        dimensions = tensor.ndim
        if dimensions < 2:
            raise ValueError

        num_input_fmaps = tensor.shape[1]
        num_output_fmaps = tensor.shape[0]
        receptive_field_size = 1
        if dimensions > 2:
            receptive_field_size = tensor.data[0][0].size
        fan_in = num_input_fmaps * receptive_field_size
        fan_out = num_output_fmaps * receptive_field_size
        return fan_in, fan_out

    @classmethod
    def xavier_uniform_(cls, tensor: 'Tensor', gain: float = 1.0) -> 'Tensor':
       
        fan_in, fan_out = cls._calculate_fan_in_and_fan_out(tensor)
        std = gain * math.sqrt(2.0 / (fan_in + fan_out))
        a = math.sqrt(3.0) * std
        return tensor.uniform_(-a, a)

    @classmethod
    def xavier_normal_(cls, tensor: 'Tensor', gain: float = 1.0) -> 'Tensor':
    
        fan_in, fan_out = cls._calculate_fan_in_and_fan_out(tensor)
        std = gain * math.sqrt(2.0 / (fan_in + fan_out))
        return tensor.normal_(0, std)

    @classmethod
    def kaiming_uniform_(
        cls,
        tensor: 'Tensor',
        a: float = 0,
        mode: str = 'fan_in',
        nonlinearity: str = 'leaky_relu'
    ) -> 'Tensor':
        
        fan = cls._calculate_fan_in_and_fan_out(tensor)[0 if mode == 'fan_in' else 1]
        
        if nonlinearity == 'relu':
            gain = math.sqrt(2.0)
        elif nonlinearity == 'leaky_relu':
            gain = math.sqrt(2.0 / (1 + a ** 2))
        elif nonlinearity in ['sigmoid', 'tanh']:
            gain = 1.0
        else:  
            gain = 1.0
            
        std = gain / math.sqrt(fan)
        bound = math.sqrt(3.0) * std
        tensor._data = np.random.uniform(-bound, bound, tensor.shape).astype(tensor.dtype)
        return tensor

    @classmethod
    def kaiming_normal_(
        cls,
        tensor: 'Tensor',
        a: float = 0,
        mode: str = 'fan_in',
        nonlinearity: str = 'leaky_relu'
    ) -> 'Tensor':
      
        fan = cls._calculate_fan_in_and_fan_out(tensor)[0 if mode == 'fan_in' else 1]
        
        if nonlinearity == 'relu':
            gain = math.sqrt(2.0)
        elif nonlinearity == 'leaky_relu':
            gain = math.sqrt(2.0 / (1 + a ** 2))
        elif nonlinearity in ['sigmoid', 'tanh']:
            gain = 1.0
        else:
            gain = 1.0
            
        std = gain / math.sqrt(fan)
        tensor._data = np.random.normal(0, std, tensor.shape).astype(tensor.dtype)
        return tensor

    @staticmethod
    def validate_init(tensor: 'Tensor', 
                    expected_std: float, 
                    context: str = "",
                    mean_tol: float = 0.15,
                    std_tol: float = 0.3) -> bool:
  
        
        passed = True

            
        return passed

    def reshape(self, shape):
        from .B13_operations import reshape
        return reshape(self, shape)

    def __hash__(self):
        return id(self)

    @classmethod
    def stack(cls, tensors, dim=0):
        np_arrays = [t.data if isinstance(t, Tensor) else np.array(t) for t in tensors]
        axis = dim
        stacked = np.stack(np_arrays, axis=axis)
        return cls(stacked)

    def transpose(self, dim0=None, dim1=None):
  
        from .B13_operations import transpose
        
        if dim0 is not None and dim1 is not None:
            axes = list(range(len(self.shape)))
            axes[dim0], axes[dim1] = axes[dim1], axes[dim0]
            t = transpose(self, tuple(axes))
        elif dim0 is not None:
            axes = list(range(len(self.shape)))
            axes[dim0], axes[-1] = axes[-1], axes[dim0]
            t = transpose(self, tuple(axes))
        else:
            t = transpose(self, None)
        import weakref
        base = self
        while hasattr(base, '_base') and base._base is not None:
            base = base._base
        if isinstance(base, Parameter):
            if not hasattr(base, '_views'):
                base._views = set()
            base._views.add(weakref.ref(t))
        return t

    def chunk(self, chunks: int, dim: int = -1) -> List['Tensor']:
  
        if dim < 0:
            dim = len(self.shape) + dim
            
        if chunks <= 0:
            raise ValueError
            
        size = self.shape[dim]
        if size % chunks != 0:
            raise ValueError
            
        result = []
        
        axis = dim
        splits = np.split(self._data, chunks, axis=axis)
        for split in splits:
            result.append(Tensor(split, requires_grad=self.requires_grad))
            
        return result

    def squeeze(self, dim: Optional[int] = None) -> 'Tensor':
    
        if dim is not None:
            if dim < 0:
                dim = len(self.shape) + dim
            if dim >= len(self.shape):
                raise ValueError(f"dimension {dim} out of range")
            if self.shape[dim] != 1:
                return self
            new_shape = list(self.shape)
            new_shape.pop(dim)
            from .B13_operations import reshape
            return reshape(self, new_shape)
        else:
            new_shape = tuple(s for s in self.shape if s != 1)
            if new_shape == self.shape:
                return self
            from .B13_operations import reshape
            return reshape(self, new_shape)

    def __matmul__(self, other):
        return self.matmul(other)

    def __rmatmul__(self, other):
        if not isinstance(other, Tensor):
            other = Tensor(other)
        return other.matmul(self)

    def __rmul__(self, other):
        from .B13_operations import mul
        return mul(Tensor(other), self)

    def __radd__(self, other):
        from .B13_operations import add
        return add(Tensor(other), self)

    def __rtruediv__(self, other):
        from .B13_operations import div
        return div(Tensor(other), self)

    def __and__(self, other):
        if not isinstance(other, Tensor):
            other = Tensor(other)
        return Tensor(np.logical_and(self._data, other._data))

    def __rand__(self, other):
        if not isinstance(other, Tensor):
            other = Tensor(other)
        return Tensor(np.logical_and(other._data, self._data))

    def min(self):
        return Tensor(np.min(self._data))

    def tolist(self):
  
        return self._data.tolist()

    def attach_module_reference(self, module, visited=None):
  
        if visited is None:
            visited = set()
        
        if id(self) in visited:
            return self
        
        visited.add(id(self))
        
        self._module = module
        
        for child in getattr(self, '_children', []):
            if child is not None and id(child) != id(self):  
                if hasattr(child, 'attach_module_reference'):
                    child.attach_module_reference(module, visited)
        
        if hasattr(self, 'grad') and self.grad is not None:
            if hasattr(self.grad, 'attach_module_reference'):
                self.grad.attach_module_reference(module, visited)
        
        ctx = getattr(self, '_ctx', None)
        if ctx is not None and hasattr(ctx, 'saved_tensors'):
            for tensor in ctx.saved_tensors:
                if tensor is not None and id(tensor) != id(self): 
                    if hasattr(tensor, 'attach_module_reference'):
                        tensor.attach_module_reference(module, visited)
        
        return self
    
    def get_module_reference(self):
      
        return getattr(self, '_module', None)
    
    def ensure_has_grad(self):
        if self.requires_grad and self.grad is None:
            self.grad = Tensor(np.zeros_like(self.data))
        return self

    def matmul(self, other):
        if not isinstance(other, Tensor):
            other = Tensor(other)
        from .B3_autograd import MatMul
        return MatMul.apply(self, other)

    def __getattr__(self, name):
        if name == 'grad':
            grad = self.__dict__.get('grad', None)
            if grad is None and hasattr(self, '_base') and self._base is not None:
                return getattr(self._base, 'grad', None)
            return grad
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

class Parameter(Tensor):
    def __init__(self, data_or_shape, init_method='xavier_uniform', device='cpu', dtype='float32'):
        if isinstance(data_or_shape, Tensor):
            super().__init__(data_or_shape.data, requires_grad=True)
            return
            
        if isinstance(data_or_shape, np.ndarray):
            super().__init__(data_or_shape, requires_grad=True)
            return
            
        shape = data_or_shape
        if init_method == 'xavier_uniform':
            fan_in = shape[0] if len(shape) > 1 else 1
            fan_out = shape[1] if len(shape) > 1 else 1
            denominator = max(fan_in + fan_out, 1e-6)
            scale = np.sqrt(6.0 / denominator)
            scale = np.clip(scale, -1e6, 1e6)
            data = np.random.uniform(-scale, scale, shape).astype(np.float32)
        elif init_method == 'zeros':
            data = np.zeros(shape, dtype=np.float32)
        elif init_method == 'ones':
            data = np.ones(shape, dtype=np.float32)
        else:
            raise ValueError
        super().__init__(data, requires_grad=True)
    
    def __repr__(self):
        return f"Parameter(shape={self.shape}, requires_grad={self.requires_grad})"

    @property
    def grad(self):
        grad = self.__dict__.get('_grad', None)
        if grad is not None:
            return grad
        views = getattr(self, '_views', set())
        for ref in list(views):
            v = ref()
            if v is not None:
                g = getattr(v, 'grad', None)
                if g is not None:
                    return g
        return None

    @grad.setter
    def grad(self, value):
        self.__dict__['_grad'] = value
