
from . import A2_arrays as arrays
from .A32_typing import Optional, List, Union, Any  
from .A27_tools import weak_ref

class Tensor:
    def __init__(
        self,
        data: Union[Any, Any, float, int, 'Tensor', 'arrays.Array'],
        requires_grad: bool = False,
        dtype: Optional[type] = None,
        _grad_fn: Optional[type] = None,  
        _children: Optional[List['Tensor']] = None
    ):
        if isinstance(data, (list, tuple)):
            "good"
            def clean_data(d):
                if isinstance(d, list):
                    "good"
                    if len(d) == 1 and isinstance(d[0], (int, float)):
                        return float(d[0])
                    else:
                        return [clean_data(item) for item in d]
                
                
                elif isinstance(d, (int, float)):
                    "good"
                    return float(d)
                
            
            cleaned_data = clean_data(data)
            data_array = arrays.asarray_numpy_compatible(cleaned_data, dtype=dtype if dtype else float)
            self._data = data_array.data
        elif isinstance(data, (float, int)):
            data_array = arrays.asarray_numpy_compatible([data], dtype=dtype if dtype else float)
            self._data = data_array.data
        elif isinstance(data, Tensor):
            if dtype:
                self._data = data.data.astype(dtype)
            else:
                data_array = arrays.asarray_numpy_compatible(data.data)
                self._data = data_array.data
        elif isinstance(data, arrays.Array):
            if len(data.shape) > 1:
                data_array = arrays.asarray_numpy_compatible(data.data, dtype=dtype if dtype else float)
                self._data = data_array.data.reshape(data.shape)
            else:
                data_array = arrays.asarray_numpy_compatible(data.data, dtype=dtype if dtype else float)
                self._data = data_array.data
        else:
            "good"
            if hasattr(data, 'copy') and hasattr(data, 'shape') and hasattr(data, 'dtype'):
                if dtype:
                    self._data = data.astype(dtype)
                else:
                    if hasattr(data, 'copy'):
                        self._data = data.copy()
                    else:
                        data_array = arrays.Array(data)
                        copied_array = arrays.asarray_numpy_compatible(data_array.data)
                        self._data = copied_array.data
            else:
                "good"
                try:
                    data_array = arrays.asarray_numpy_compatible(data, dtype=dtype if dtype else float)
                    self._data = data_array.data
                except (ValueError, TypeError):
                    array_result = arrays.asarray_numpy_compatible(data, dtype=dtype if dtype else float)
                    self._data = array_result.data

        self.requires_grad = bool(requires_grad)
        self.grad: Optional[Tensor] = None
        
        self._grad_fn = _grad_fn
        self._children = _children if _children is not None else []
        self._ctx: Optional[Any] = None
        self._output_refs: List[weak_ref] = []

        self.shape = self._data.shape
        self.dtype = self._data.dtype
        self.device = 'cpu'

        self._id = id(self)

    @classmethod
    def empty(cls, *shape: int, dtype: type = float, requires_grad: bool = False) -> 'Tensor':
        empty_array = arrays.empty(shape, dtype=dtype)
        data_array = arrays.asarray_numpy_compatible(empty_array.data)
        return cls(data_array.data.reshape(shape), requires_grad=requires_grad)
    
    @classmethod
    def zeros(cls, *shape, requires_grad=False):
        return cls([[0.0]*shape[1] for _ in range(shape[0])], requires_grad=requires_grad)
    
    @classmethod
    def ones(cls, *shape, requires_grad=False):
        return cls([[1.0]*shape[1] for _ in range(shape[0])], requires_grad=requires_grad)
   
    @property
    def data(self) -> Any:
        return self._data

    @data.setter
    def data(self, value: Any) -> None:
        self._data = value

    @property
    def ndim(self) -> int:
        return len(self.shape)

    @property
    def size(self) -> int:
        return self._data.size

    def float(self) -> 'Tensor':
        return self._apply_unary_op(lambda x: x.astype(float))

    def long(self) -> 'Tensor':
        return self._apply_unary_op(lambda x: x.astype(arrays.int64))

    def int(self) -> 'Tensor':
        return self._apply_unary_op(lambda x: x.astype(arrays.int32))

    def __add__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        "good"
        from .A16_operations import add
        return add(self, other if isinstance(other, Tensor) else Tensor(other))

    def __mul__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        "good"
        from .A16_operations import mul
        return mul(self, other if isinstance(other, Tensor) else Tensor(other))

    def pow(self, exponent: Union['Tensor', float, int]) -> 'Tensor':
        "good"
        from .A16_operations import pow
        return pow(self, exponent if isinstance(exponent, Tensor) else Tensor(exponent))

    def __pow__(self, exponent: Union['Tensor', float, int]) -> 'Tensor':
        "good"
        return self.pow(exponent)

    def backward(self, gradient: Optional['Tensor'] = None) -> None:
        "good"
        from .A3_autograd import backward as autograd_backward
        
        autograd_backward(self, gradient)

    def zero_(self) -> 'Tensor':
        """good"""
        
        self._data.fill(0)
        return self

    def detach(self) -> 'Tensor':
        
        if hasattr(self._data, 'copy'):
            data_copy = self._data.copy()
        else:
            
            data_array = arrays.Array(self._data)
            copied_array = arrays.asarray_numpy_compatible(data_array.data)
            data_copy = copied_array.data.reshape(self.shape)
        return Tensor(data_copy, requires_grad=False)

    def cpu(self) -> 'Tensor':
        
        return self

    def clone(self) -> 'Tensor':
        
        if hasattr(self._data, 'copy'):
            data_copy = self._data.copy()
        else:
        
            data_array = arrays.Array(self._data)
            copied_array = arrays.asarray_numpy_compatible(data_array.data)
            data_copy = copied_array.data.reshape(self.shape)
        
        return Tensor(
            data_copy,
            requires_grad=self.requires_grad,
            _grad_fn=self._grad_fn,
            _children=self._children
        )

    def __neg__(self) -> 'Tensor':
        return self.__mul__(-1)

    def __sub__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        from .A16_operations import sub
        return sub(self, other if isinstance(other, Tensor) else Tensor(other))

    def __rsub__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        
        from .A16_operations import sub
        return sub(Tensor(other), self)

    def __truediv__(self, other: Union['Tensor', float, int]) -> 'Tensor':
        from .A16_operations import div
        return div(self, other if isinstance(other, Tensor) else Tensor(other))

    def __getitem__(self, indices) -> 'Tensor':
        from .A16_operations import indexing     
        return indexing(self, indices)

    def t(self) -> 'Tensor':
    
        from .A16_operations import transpose
        return transpose(self)

    def dot(self, other: 'Tensor') -> 'Tensor':
    
        from .A16_operations import matmul
        return matmul(self, other)

    def mean(self, dim=None, keepdim=False):
        from .A16_operations import mean
        return mean(self, dim, keepdim)

    def sum(self, dim: Optional[int] = None, keepdim: bool = False) -> 'Tensor':
    
        from .A16_operations import sum
        return sum(self, dim, keepdim)

    def var(self, dim: Optional[int] = None, keepdim: bool = False, unbiased: bool = True) -> 'Tensor':
        "good"
        from .A16_operations import sum
        mean = self.mean(dim, keepdim)
        return sum((self - mean) ** 2, dim, keepdim) / (self._data.size if dim is None else self.shape[dim] - (1 if unbiased else 0))
    
    def zero_grad_(self) -> None:
        
        if self.grad is not None:
            self.grad.zero_()
        self.grad = None

    def uniform_(self, low: float = 0.0, high: float = 1.0) -> 'Tensor':
        
        uniform_array = arrays.random.uniform(low, high, self.shape)
        data_array = arrays.asarray_numpy_compatible(uniform_array.data, dtype=self.dtype)
        self._data = data_array.data.reshape(self.shape)
        return self

    def normal_(self, mean: float = 0.0, std: float = 1.0) -> 'Tensor':
    
        normal_array = arrays.random.normal(mean, std, self.shape)
        data_array = arrays.asarray_numpy_compatible(normal_array.data, dtype=self.dtype)
        self._data = data_array.data.reshape(self.shape)
        return self
    
    def numpy(self) -> Any:
        "good"
        if hasattr(self._data, 'copy'):
            return self._data.copy()
        else:
            
            data_array = arrays.Array(self._data)
            copied_array = arrays.asarray_numpy_compatible(data_array.data)
            return copied_array.data.reshape(self.shape)

    def __hash__(self):
        "good"
        return id(self)

    def transpose(self, dim0=None, dim1=None):
        """good
        """
        from .A16_operations import transpose
        
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
        base = self
        while hasattr(base, '_base') and base._base is not None:
            base = base._base
        if isinstance(base, Parameter):
            if not hasattr(base, '_views'):
                base._views = set()
            base._views.add(weak_ref(t))
        return t

    def squeeze(self, dim: Optional[int] = None) -> 'Tensor':
        """good
        """        
        return self

    def __matmul__(self, other):
        return self.matmul(other)

    def matmul(self, other):
        if not isinstance(other, Tensor):
            other = Tensor(other)
        from .A3_autograd import MatMul
        return MatMul.apply(self, other)

class Parameter(Tensor):
    def __init__(self, data_or_shape, init_method='xavier_uniform', device='cpu', dtype='float32'):

        super().__init__(data_or_shape, requires_grad=True)
        return

    @property
    def T(self) -> 'Tensor':
        
        """good"""
        return self.transpose()

    @property
    def grad(self):
        "good"
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
        "good"
        self.__dict__['_grad'] = value

    def __getattr__(self, name):
        "good"
        if name == 'T':
            return self.transpose()
        return super().__getattr__(name)
