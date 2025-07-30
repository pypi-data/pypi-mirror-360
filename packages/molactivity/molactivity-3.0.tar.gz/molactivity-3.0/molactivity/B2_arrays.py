
import math
from typing import List, Union, Tuple, Optional
from . import A22_random as pure_random  
import numpy as np

def uniform(low: float = 0.0, high: float = 1.0, size: Optional[Tuple[int, ...]] = None, dtype: Optional[type] = None) -> 'Array':
    
    if size is None:
        size = (1,)
    if dtype is None:
        dtype = float
        
    if isinstance(size, int):
        total_size = size
    else:
        total_size = 1
        for dim in size:
            total_size *= dim
    
    data = [pure_random.uniform(low, high) for _ in range(total_size)]
    
    result = Array(data, dtype=dtype)
    if isinstance(size, tuple) and len(size) > 1:
        result = result.reshape(*size)
    
    return result

class Array:
    def __init__(self, data: Union[List, Tuple, float, int, 'Array', np.ndarray], dtype=None):

        if 'torch' in str(type(data)):
            try:
                if hasattr(data, 'detach'):
                    numpy_data = data.detach().cpu().numpy()
                else:
                    numpy_data = data.cpu().numpy()
                
                if numpy_data.ndim > 1:
                    self.data = numpy_data.tolist()
                else:
                    self.data = numpy_data.flatten().tolist()
                    
            except Exception as e:
                try:
                    self.data = data.tolist()
                except:
                    raise ValueError(f"cannot change PyTorch to Array: {str(e)}")
        elif isinstance(data, Array):
            self.data = data.data.copy()
        elif isinstance(data, np.ndarray):
            self.data = data.flatten().tolist()
        elif isinstance(data, (list, tuple)):
            self.data = self._flatten_and_convert(data)
        else:
            self.data = [float(data)]
        self.shape = self._compute_shape()
        self.dtype = dtype or float
        
    def _flatten_and_convert(self, data: Union[List, Tuple]) -> List:
        if not isinstance(data, (list, tuple)):
            return [float(data)]
        result = []
        for x in data:
            if isinstance(x, (list, tuple)):
                result.extend(self._flatten_and_convert(x))
            else:
                result.append(float(x))
        return result
    
    def _compute_shape(self) -> Tuple[int, ...]:
        if not isinstance(self.data, list):
            return (1,)
        if not self.data:
            return (0,)
            
        if isinstance(self.data[0], (list, tuple)):
            first_dim = len(self.data)
            second_dim = len(self.data[0])
            if not all(len(x) == second_dim for x in self.data):
                raise ValueError
            return (first_dim, second_dim)
            
        return (len(self.data),)
    
    def reshape(self, *shape: int) -> 'Array':

        total_size = len(self.data)
        
        if len(shape) == 1:
            if isinstance(shape[0], (list, tuple)):
                shape = shape[0]
            elif hasattr(shape[0], '__iter__'):  
                shape = tuple(shape[0])
        
        shape = list(shape)
        
        shape = [int(dim) for dim in shape]
        
        if -1 in shape:
            if shape.count(-1) > 1:
                raise ValueError
            idx = shape.index(-1)
            other_dims = 1
            for i, dim in enumerate(shape):
                if i != idx and dim != -1:
                    other_dims *= dim
            shape[idx] = total_size // other_dims
            if total_size % other_dims != 0:
                raise ValueError
        else:
            total_shape = 1
            for dim in shape:
                total_shape *= dim
            if total_shape != total_size:
                raise ValueError(f"cannot reshape array of size {total_size} into shape {shape}")
            
        new_array = Array(self.data.copy(), dtype=self.dtype)
        new_array.shape = tuple(shape)
        
        if len(shape) == 2:
            rows, cols = shape
            nested_data = []
            for i in range(rows):
                row = []
                for j in range(cols):
                    row.append(self.data[i * cols + j])
                nested_data.append(row)
            new_array.data = nested_data
            
        return new_array
    
    def transpose(self):
        if len(self.shape) != 2:
            raise ValueError("transpose requires 2D array")
        rows, cols = self.shape
        result = []
        for j in range(cols):
            row = []
            for i in range(rows):
                row.append(self.data[i * cols + j])
            result.append(row)
        return Array(result)
    
    @property
    def T(self):
        return self.transpose()
    
    def __add__(self, other: Union['Array', float, int]) -> 'Array':
        if isinstance(other, (int, float)):
            return Array([x + other for x in self.data], dtype=self.dtype)
        if isinstance(other, Array):
            if self.shape != other.shape:
                raise ValueError("shapes do not match")
            return Array([a + b for a, b in zip(self.data, other.data)], dtype=self.dtype)
        raise TypeError(f"unsupported operand type(s) for +: 'Array' and '{type(other)}'")
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            if isinstance(self.data, list):
                if isinstance(self.data[0], list):  
                    return Array([[float(x * other) for x in row] for row in self.data], dtype=self.dtype)
                else:
                    return Array([float(x * other) for x in self.data], dtype=self.dtype)
            else: 
                return Array([float(self.data * other)], dtype=self.dtype)
        elif isinstance(other, Array):

            if self.shape == other.shape:
                if isinstance(self.data[0], list) and isinstance(other.data[0], list):
                    return Array([[float(a * b) for a, b in zip(row_a, row_b)] 
                                for row_a, row_b in zip(self.data, other.data)], dtype=self.dtype)
                elif not isinstance(self.data[0], list) and not isinstance(other.data[0], list):
                    return Array([float(a * b) for a, b in zip(self.data, other.data)], dtype=self.dtype)
            
            if len(self.data) == 1 and len(other.data) > 1:
                scalar_value = self.data[0]
                return other * scalar_value
            
            if len(other.data) == 1 and len(self.data) > 1:
                scalar_value = other.data[0]
                return self * scalar_value  
            
            if isinstance(self.data[0], list) and not isinstance(other.data[0], list):
                if len(other.data) == len(self.data): 
                    result = []
                    for i, row in enumerate(self.data):
                        result.append([float(cell * other.data[i]) for cell in row])
                    return Array(result, dtype=self.dtype)
            
            if not isinstance(self.data[0], list) and isinstance(other.data[0], list):
                if len(self.data) == len(other.data):  
                    result = []
                    for i, row in enumerate(other.data):
                        result.append([float(self.data[i] * cell) for cell in row])
                    return Array(result, dtype=self.dtype)
            
            raise ValueError(f"shapes do not match for multiplication: {self.shape} vs {other.shape}")
        else:
            raise TypeError(f"unsupported operand type(s) for *: 'Array' and '{type(other)}'")
    
    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return self.__mul__(other)
        raise TypeError(f"unsupported operand type(s) for *: '{type(other)}' and 'Array'")
    
    def __sub__(self, other: Union['Array', float, int]) -> 'Array':
        if isinstance(other, (int, float)):
            if isinstance(self.data, list):
                if isinstance(self.data[0], list):  
                    return Array([[float(x - other) for x in row] for row in self.data], dtype=self.dtype)
                else: 
                    return Array([float(x - other) for x in self.data], dtype=self.dtype)
            else: 
                return Array([float(self.data - other)], dtype=self.dtype)
        elif isinstance(other, Array):
            if self.shape == other.shape:
                if isinstance(self.data[0], list) and isinstance(other.data[0], list):
                    return Array([[float(a - b) for a, b in zip(row_a, row_b)] 
                                for row_a, row_b in zip(self.data, other.data)], dtype=self.dtype)
                elif not isinstance(self.data[0], list) and not isinstance(other.data[0], list):
                    return Array([float(a - b) for a, b in zip(self.data, other.data)], dtype=self.dtype)
            
            if len(self.data) == 1 and len(other.data) > 1:
                scalar_value = self.data[0]
                if isinstance(other.data[0], list): 
                    return Array([[float(scalar_value - cell) for cell in row] for row in other.data], dtype=self.dtype)
                else: 
                    return Array([float(scalar_value - x) for x in other.data], dtype=self.dtype)
            
            if len(other.data) == 1 and len(self.data) > 1:
                scalar_value = other.data[0]
                return self - scalar_value 
            
            if isinstance(self.data[0], list) and not isinstance(other.data[0], list):
                if len(other.data) == len(self.data): 
                    result = []
                    for i, row in enumerate(self.data):
                        result.append([float(cell - other.data[i]) for cell in row])
                    return Array(result, dtype=self.dtype)
            
            if not isinstance(self.data[0], list) and isinstance(other.data[0], list):
                if len(self.data) == len(other.data): 
                    result = []
                    for i, row in enumerate(other.data):
                        result.append([float(self.data[i] - cell) for cell in row])
                    return Array(result, dtype=self.dtype)
            
            raise ValueError(f"shapes do not match for subtraction: {self.shape} vs {other.shape}")
        else:
            raise TypeError(f"unsupported operand type(s) for -: 'Array' and '{type(other)}'")
    
    def __rsub__(self, other: Union[float, int]) -> 'Array':
        if isinstance(other, (int, float)):
            if isinstance(self.data, list):
                if isinstance(self.data[0], list): 
                    return Array([[float(other - x) for x in row] for row in self.data], dtype=self.dtype)
                else:  
                    return Array([float(other - x) for x in self.data], dtype=self.dtype)
            else: 
                return Array([float(other - self.data)], dtype=self.dtype)
        else:
            raise TypeError(f"unsupported operand type(s) for -: '{type(other)}' and 'Array'")
    
    def __truediv__(self, other: Union['Array', float, int]) -> 'Array':
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("division by zero")
            if isinstance(self.data, list):
                if isinstance(self.data[0], list): 
                    return Array([[float(x / other) for x in row] for row in self.data], dtype=self.dtype)
                else:  
                    return Array([float(x / other) for x in self.data], dtype=self.dtype)
            else: 
                return Array([float(self.data / other)], dtype=self.dtype)
        elif isinstance(other, Array):

            if self.shape == other.shape:
                if isinstance(self.data[0], list) and isinstance(other.data[0], list):
                    return Array([[float(a / b) if b != 0 else float('inf') for a, b in zip(row_a, row_b)] 
                                for row_a, row_b in zip(self.data, other.data)], dtype=self.dtype)
                elif not isinstance(self.data[0], list) and not isinstance(other.data[0], list):
                    return Array([float(a / b) if b != 0 else float('inf') for a, b in zip(self.data, other.data)], dtype=self.dtype)
            
            if len(self.data) == 1 and len(other.data) > 1:
                scalar_value = self.data[0]
                if isinstance(other.data[0], list):  
                    return Array([[float(scalar_value / cell) if cell != 0 else float('inf') for cell in row] 
                                 for row in other.data], dtype=self.dtype)
                else: 
                    return Array([float(scalar_value / x) if x != 0 else float('inf') for x in other.data], dtype=self.dtype)
            
            if len(other.data) == 1 and len(self.data) > 1:
                scalar_value = other.data[0]
                if scalar_value == 0:
                    raise ZeroDivisionError("division by zero")
                return self * (1.0 / scalar_value)
            
            if isinstance(self.data[0], list) and not isinstance(other.data[0], list):
                if len(other.data) == len(self.data): 
                    result = []
                    for i, row in enumerate(self.data):
                        if other.data[i] == 0:
                            result.append([float('inf')] * len(row))
                        else:
                            result.append([float(cell / other.data[i]) for cell in row])
                    return Array(result, dtype=self.dtype)
            
            if not isinstance(self.data[0], list) and isinstance(other.data[0], list):
                if len(self.data) == len(other.data):  
                    result = []
                    for i, row in enumerate(other.data):
                        result.append([float(self.data[i] / cell) if cell != 0 else float('inf') for cell in row])
                    return Array(result, dtype=self.dtype)
            
            raise ValueError(f"shapes do not match for division: {self.shape} vs {other.shape}")
        else:
            raise TypeError(f"unsupported operand type(s) for /: 'Array' and '{type(other)}'")
    
    def __rtruediv__(self, other: Union[float, int]) -> 'Array':
        if isinstance(other, (int, float)):
            if isinstance(self.data, list):
                if isinstance(self.data[0], list): 
                    return Array([[float(other / x) if x != 0 else float('inf') for x in row] for row in self.data], dtype=self.dtype)
                else: 
                    return Array([float(other / x) if x != 0 else float('inf') for x in self.data], dtype=self.dtype)
            else: 
                return Array([float(other / self.data) if self.data != 0 else float('inf')], dtype=self.dtype)
        else:
            raise TypeError(f"unsupported operand type(s) for /: '{type(other)}' and 'Array'")
    
    def __pow__(self, other: Union['Array', float, int]) -> 'Array':
        if isinstance(other, (int, float)):
            return Array([x ** other for x in self.data], dtype=self.dtype)
        if isinstance(other, Array):
            if self.shape != other.shape:
                raise ValueError("shapes do not match")
            return Array([a ** b for a, b in zip(self.data, other.data)], dtype=self.dtype)
        raise TypeError(f"unsupported operand type(s) for **: 'Array' and '{type(other)}'")
    
    def sum(self, axis: Optional[int] = None) -> Union['Array', float]:
        if axis is None:
            return sum(self.data)
        if axis >= len(self.shape):
            raise ValueError("axis out of bounds")
        if len(self.shape) == 1:
            return sum(self.data)
        if len(self.shape) == 2:
            rows, cols = self.shape
            if axis == 0:
                return Array([sum(self.data[i::cols]) for i in range(cols)])
            else:
                return Array([sum(self.data[i*cols:(i+1)*cols]) for i in range(rows)])
        raise NotImplementedError("sum for arrays with more than 2 dimensions not implemented")
    
    def mean(self, axis: Optional[int] = None) -> Union['Array', float]:

        if not self.data:
            raise ValueError
            
        if axis is not None and axis >= len(self.shape):
            raise ValueError
            
        try:
            if axis is None:
                return sum(self.data) / len(self.data)
            result = self.sum(axis)
            if isinstance(result, Array):
                return result / self.shape[axis]
            return result
        except Exception as e:
            raise RuntimeError
    
    def max(self, axis: Optional[int] = None) -> Union['Array', float]:
        if axis is None:
            return max(self.data)
        if axis >= len(self.shape):
            raise ValueError("axis out of bounds")
        if len(self.shape) == 1:
            return max(self.data)
        if len(self.shape) == 2:
            rows, cols = self.shape
            if axis == 0:
                return Array([max(self.data[i::cols]) for i in range(cols)])
            else:
                return Array([max(self.data[i*cols:(i+1)*cols]) for i in range(rows)])
        raise NotImplementedError("max for arrays with more than 2 dimensions not implemented")
    
    def min(self, axis: Optional[int] = None) -> Union['Array', float]:
        if axis is None:
            return min(self.data)
        if axis >= len(self.shape):
            raise ValueError("axis out of bounds")
        if len(self.shape) == 1:
            return min(self.data)
        if len(self.shape) == 2:
            rows, cols = self.shape
            if axis == 0:
                return Array([min(self.data[i::cols]) for i in range(cols)])
            else:
                return Array([min(self.data[i*cols:(i+1)*cols]) for i in range(rows)])
        raise NotImplementedError("min for arrays with more than 2 dimensions not implemented")
    
    def dot(self, other: 'Array') -> 'Array':
        if not isinstance(other, Array):
            raise TypeError("dot product requires Array operand")
        if len(self.shape) != 2 or len(other.shape) != 2:
            raise ValueError("dot product requires 2D arrays")
        if self.shape[1] != other.shape[0]:
            raise ValueError("shapes not aligned for dot product")
        
        result = []
        for i in range(self.shape[0]):
            row = []
            for j in range(other.shape[1]):
                sum_val = 0
                for k in range(self.shape[1]):
                    sum_val += self.data[i * self.shape[1] + k] * other.data[k * other.shape[1] + j]
                row.append(sum_val)
            result.extend(row)
        return Array(result).reshape(self.shape[0], other.shape[1])
    
    def __matmul__(self, other: 'Array') -> 'Array':
        return self.dot(other)
    
    def __getitem__(self, key: Union[int, slice, Tuple]) -> 'Array':
        if isinstance(key, int):
            if key >= len(self.data):
                raise IndexError("index out of bounds")
            return Array([self.data[key]], dtype=self.dtype)
        if isinstance(key, slice):
            return Array(self.data[key], dtype=self.dtype)
        if isinstance(key, tuple):
            if len(key) != len(self.shape):
                raise ValueError("number of indices must match array dimensions")
            if len(self.shape) == 2:
                rows, cols = self.shape
                if isinstance(key[0], int) and isinstance(key[1], int):
                    return Array([self.data[key[0] * cols + key[1]]], dtype=self.dtype)
                row_slice = key[0] if isinstance(key[0], slice) else slice(key[0], key[0] + 1)
                col_slice = key[1] if isinstance(key[1], slice) else slice(key[1], key[1] + 1)
                result = []
                for i in range(*row_slice.indices(rows)):
                    for j in range(*col_slice.indices(cols)):
                        result.append(self.data[i * cols + j])
                return Array(result, dtype=self.dtype)
        raise TypeError("invalid index type")
    
    def __setitem__(self, key: Union[int, slice, Tuple], value: Union['Array', float, int]) -> None:
        if isinstance(key, int):
            if key >= len(self.data):
                raise IndexError("index out of bounds")
            self.data[key] = float(value)
        elif isinstance(key, slice):
            if isinstance(value, (int, float)):
                for i in range(*key.indices(len(self.data))):
                    self.data[i] = float(value)
            elif isinstance(value, Array):
                for i, v in zip(range(*key.indices(len(self.data))), value.data):
                    self.data[i] = float(v)
        elif isinstance(key, tuple):
            if len(key) != len(self.shape):
                raise ValueError("number of indices must match array dimensions")
            if len(self.shape) == 2:
                rows, cols = self.shape
                if isinstance(key[0], int) and isinstance(key[1], int):
                    self.data[key[0] * cols + key[1]] = float(value)
                else:
                    row_slice = key[0] if isinstance(key[0], slice) else slice(key[0], key[0] + 1)
                    col_slice = key[1] if isinstance(key[1], slice) else slice(key[1], key[1] + 1)
                    if isinstance(value, (int, float)):
                        for i in range(*row_slice.indices(rows)):
                            for j in range(*col_slice.indices(cols)):
                                self.data[i * cols + j] = float(value)
                    elif isinstance(value, Array):
                        idx = 0
                        for i in range(*row_slice.indices(rows)):
                            for j in range(*col_slice.indices(cols)):
                                self.data[i * cols + j] = float(value.data[idx])
                                idx += 1
        else:
            raise TypeError("invalid index type")
    
    def __repr__(self) -> str:
        return f"Array({self.data}, shape={self.shape}, dtype={self.dtype})"
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def copy(self) -> 'Array':
        return Array(self.data.copy(), dtype=self.dtype)
    
    def astype(self, dtype) -> 'Array':
        return Array(self.data, dtype=dtype)
    
    def fill(self, value: float) -> None:
        self.data = [float(value)] * len(self.data)
    
    def clip(self, min_val: float, max_val: float) -> 'Array':
        return Array([max(min_val, min(x, max_val)) for x in self.data], dtype=self.dtype)
    
    def exp(self) -> 'Array':
        return Array([math.exp(x) for x in self.data], dtype=self.dtype)
    
    def log(self) -> 'Array':
        return Array([math.log(x) for x in self.data], dtype=self.dtype)
    
    def sqrt(self) -> 'Array':
        return Array([math.sqrt(x) for x in self.data], dtype=self.dtype)
    
    def abs(self) -> 'Array':
        return Array([abs(x) for x in self.data], dtype=self.dtype)
    
    def var(self, axis: Optional[int] = None) -> Union['Array', float]:
        mean_val = self.mean(axis)
        if axis is None:
            return sum((x - mean_val) ** 2 for x in self.data) / len(self.data)
        if len(self.shape) == 1:
            return sum((x - mean_val) ** 2 for x in self.data) / len(self.data)
        if len(self.shape) == 2:
            rows, cols = self.shape
            if axis == 0:
                return Array([sum((self.data[i::cols] - mean_val.data[i]) ** 2 for i in range(cols)) / rows])
            else:
                return Array([sum((self.data[i*cols:(i+1)*cols] - mean_val.data[i]) ** 2 for i in range(rows)) / cols])
        raise NotImplementedError("var for arrays with more than 2 dimensions not implemented")

    def _ensure_2d(self) -> None:
        if len(self.shape) == 1:
            self.data = [self.data]
            self.shape = (1, len(self.data[0]))

def array(data: Union[List, Tuple, float, int, Array], dtype=None) -> Array:
    return Array(data, dtype=dtype)

def zeros(shape: Union[int, Tuple[int, ...]], dtype: str = 'float32') -> Array:

    if isinstance(shape, int):
        if shape <= 0:
            raise ValueError
        shape = (shape,)
    elif isinstance(shape, tuple):
        if not all(isinstance(dim, int) and dim > 0 for dim in shape):
            raise ValueError
    else:
        raise ValueError
        
    try:
        np_array = np.zeros(shape, dtype=dtype)
        return Array(np_array)
    except Exception as e:
        raise RuntimeError

def ones(shape: Union[int, Tuple[int, ...]], dtype: str = 'float32') -> Array:

    if isinstance(shape, int):
        if shape <= 0:
            raise ValueError
        shape = (shape,)
    elif isinstance(shape, tuple):
        if not all(isinstance(dim, int) and dim > 0 for dim in shape):
            raise ValueError
    else:
        raise ValueError
        
    try:
        np_array = np.ones(shape, dtype=dtype)
        return Array(np_array)
    except Exception as e:
        raise RuntimeError

def empty(shape: Union[int, Tuple[int, ...]], dtype=None) -> Array:
    return zeros(shape, dtype=dtype)

def random_normal(shape: Union[int, Tuple[int, ...]], mean=0.0, std=1.0, dtype=None) -> Array:

    if isinstance(shape, int):
        if shape <= 0:
            raise ValueError
        shape = (shape,)
    elif isinstance(shape, tuple):
        if not shape or any(dim <= 0 for dim in shape):
            raise ValueError
    else:
        raise ValueError
            
    try:
        np_array = np.random.normal(mean, std, shape)
        return Array(np_array)
    except Exception as e:
        raise RuntimeError

def random_uniform(shape: Union[int, Tuple[int, ...]], low=0.0, high=1.0, dtype=None) -> Array:
    if isinstance(shape, int):
        size = shape
    else:
        size = 1
        for dim in shape:
            size *= dim
    data = [pure_random.uniform(low, high) for _ in range(size)]  
    return Array(data, dtype=dtype).reshape(*shape) if isinstance(shape, tuple) else Array(data, dtype=dtype)

def eye(n: int, dtype=None) -> Array:
    data = [0.0] * (n * n)
    for i in range(n):
        data[i * n + i] = 1.0
    return Array(data, dtype=dtype).reshape(n, n)

def linspace(start: float, stop: float, num: int, dtype=None) -> Array:
    step = (stop - start) / (num - 1) if num > 1 else 0
    data = [start + i * step for i in range(num)]
    return Array(data, dtype=dtype)

def arange(start: float, stop: float, step: float = 1.0, dtype=None) -> Array:
    data = []
    current = start
    while current < stop:
        data.append(current)
        current += step
    return Array(data, dtype=dtype)

def concatenate(arrays: List[Array], axis: int = 0) -> Array:
    if not arrays:
        raise ValueError("empty sequence")
    if axis >= len(arrays[0].shape):
        raise ValueError("axis out of bounds")
    if len(arrays[0].shape) == 1:
        result = []
        for arr in arrays:
            result.extend(arr.data)
        return Array(result, dtype=arrays[0].dtype)
    if len(arrays[0].shape) == 2:
        if axis == 0:
            result = []
            for arr in arrays:
                result.extend(arr.data)
            return Array(result, dtype=arrays[0].dtype).reshape(sum(arr.shape[0] for arr in arrays), arrays[0].shape[1])
        else:
            result = []
            rows = arrays[0].shape[0]
            for i in range(rows):
                for arr in arrays:
                    result.extend(arr.data[i * arr.shape[1]:(i + 1) * arr.shape[1]])
            return Array(result, dtype=arrays[0].dtype).reshape(rows, sum(arr.shape[1] for arr in arrays))
    raise NotImplementedError("concatenate for arrays with more than 2 dimensions not implemented")

def stack(arrays: List[Array], axis: int = 0) -> Array:
    if not arrays:
        raise ValueError("empty sequence")
    if axis > len(arrays[0].shape):
        raise ValueError("axis out of bounds")
    if len(arrays[0].shape) == 1:
        if axis == 0:
            return Array([x for arr in arrays for x in arr.data], dtype=arrays[0].dtype).reshape(len(arrays), -1)
        else:
            return Array([x for arr in arrays for x in arr.data], dtype=arrays[0].dtype).reshape(-1, len(arrays))
    if len(arrays[0].shape) == 2:
        if axis == 0:
            return Array([x for arr in arrays for x in arr.data], dtype=arrays[0].dtype).reshape(len(arrays), *arrays[0].shape)
        elif axis == 1:
            return Array([x for arr in arrays for x in arr.data], dtype=arrays[0].dtype).reshape(arrays[0].shape[0], len(arrays), arrays[0].shape[1])
        else:
            return Array([x for arr in arrays for x in arr.data], dtype=arrays[0].dtype).reshape(arrays[0].shape[0], arrays[0].shape[1], len(arrays))
    raise NotImplementedError("stack for arrays with more than 2 dimensions not implemented")

def maximum(a: Union[Array, float], b: Union[Array, float]) -> Array:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return Array([max(a, b)], dtype=float)
    if isinstance(a, (int, float)):
        return Array([max(a, x) for x in b.data], dtype=b.dtype)
    if isinstance(b, (int, float)):
        return Array([max(x, b) for x in a.data], dtype=a.dtype)
    if a.shape != b.shape:
        raise ValueError("shapes do not match")
    return Array([max(x, y) for x, y in zip(a.data, b.data)], dtype=a.dtype)

def minimum(a: Union[Array, float], b: Union[Array, float]) -> Array:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return Array([min(a, b)], dtype=float)
    if isinstance(a, (int, float)):
        return Array([min(a, x) for x in b.data], dtype=b.dtype)
    if isinstance(b, (int, float)):
        return Array([min(x, b) for x in a.data], dtype=a.dtype)
    if a.shape != b.shape:
        raise ValueError("shapes do not match")
    return Array([min(x, y) for x, y in zip(a.data, b.data)], dtype=a.dtype)

def where(condition: Array, x: Union[Array, float], y: Union[Array, float]) -> Array:
    if not isinstance(condition, Array):
        raise TypeError("condition must be an Array")
    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return Array([x if c else y for c in condition.data], dtype=float)
    if isinstance(x, (int, float)):
        if condition.shape != y.shape:
            raise ValueError("shapes do not match")
        return Array([x if c else y_val for c, y_val in zip(condition.data, y.data)], dtype=y.dtype)
    if isinstance(y, (int, float)):
        if condition.shape != x.shape:
            raise ValueError("shapes do not match")
        return Array([x_val if c else y for c, x_val in zip(condition.data, x.data)], dtype=x.dtype)
    if condition.shape != x.shape or condition.shape != y.shape:
        raise ValueError("shapes do not match")
    return Array([x_val if c else y_val for c, x_val, y_val in zip(condition.data, x.data, y.data)], dtype=x.dtype)

def einsum(equation: str, *arrays: Array) -> Array:
    if equation == 'ij,jk->ik':
        if len(arrays) != 2:
            raise ValueError("einsum requires 2 arrays for matrix multiplication")
        return arrays[0].dot(arrays[1])
    raise NotImplementedError("only basic matrix multiplication is supported for einsum")

def bmm(x: Array, y: Array) -> Array:
    if len(x.shape) != 3 or len(y.shape) != 3:
        raise ValueError("bmm requires 3D arrays")
    if x.shape[0] != y.shape[0] or x.shape[2] != y.shape[1]:
        raise ValueError("shapes not aligned for batch matrix multiplication")
    result = []
    for i in range(x.shape[0]):
        x_i = Array(x.data[i * x.shape[1] * x.shape[2]:(i + 1) * x.shape[1] * x.shape[2]], dtype=x.dtype).reshape(x.shape[1], x.shape[2])
        y_i = Array(y.data[i * y.shape[1] * y.shape[2]:(i + 1) * y.shape[1] * y.shape[2]], dtype=y.dtype).reshape(y.shape[1], y.shape[2])
        result.extend(x_i.dot(y_i).data)
    return Array(result, dtype=x.dtype).reshape(x.shape[0], x.shape[1], y.shape[2])

def conv2d(input: Array, weight: Array, bias: Optional[Array] = None, stride: Tuple[int, int] = (1, 1), padding: Tuple[int, int] = (0, 0)) -> Array:
    if len(input.shape) != 4 or len(weight.shape) != 4:
        raise ValueError("conv2d requires 4D arrays")
    if input.shape[1] != weight.shape[1]:
        raise ValueError("input channels must match weight channels")
    if bias is not None and bias.shape[0] != weight.shape[0]:
        raise ValueError("bias size must match output channels")
    
    batch_size, in_channels, in_height, in_width = input.shape
    out_channels, _, kernel_height, kernel_width = weight.shape
    stride_h, stride_w = stride
    pad_h, pad_w = padding
    
    out_height = (in_height + 2 * pad_h - kernel_height) // stride_h + 1
    out_width = (in_width + 2 * pad_w - kernel_width) // stride_w + 1
    
    result = []
    for b in range(batch_size):
        for oc in range(out_channels):
            for oh in range(out_height):
                for ow in range(out_width):
                    sum_val = 0.0
                    for ic in range(in_channels):
                        for kh in range(kernel_height):
                            for kw in range(kernel_width):
                                ih = oh * stride_h + kh - pad_h
                                iw = ow * stride_w + kw - pad_w
                                if 0 <= ih < in_height and 0 <= iw < in_width:
                                    input_idx = b * in_channels * in_height * in_width + ic * in_height * in_width + ih * in_width + iw
                                    weight_idx = oc * in_channels * kernel_height * kernel_width + ic * kernel_height * kernel_width + kh * kernel_width + kw
                                    sum_val += input.data[input_idx] * weight.data[weight_idx]
                    if bias is not None:
                        sum_val += bias.data[oc]
                    result.append(sum_val)
    
    return Array(result, dtype=input.dtype).reshape(batch_size, out_channels, out_height, out_width)

def mean(x: Union[Array, List, Tuple], axis: Optional[int] = None) -> Union[Array, float]:

    if isinstance(x, Array):
        return x.mean(axis)
    return sum(x) / len(x)

def std(x: Union[Array, List, Tuple], axis: Optional[int] = None) -> Union[Array, float]:
    if isinstance(x, Array):
        return x.var(axis=axis) ** 0.5
    x_array = array(x)
    return x_array.var(axis=axis) ** 0.5

def histogram(x: Union[Array, List, Tuple], bins: int = 10) -> Tuple[Array, Array]:

    if isinstance(x, Array):
        data = x.data
    else:
        data = x
        
    min_val = min(data)
    max_val = max(data)
    
    bin_edges = linspace(min_val, max_val, bins + 1)
    
    hist = zeros(bins)
    for val in data:
        for i in range(bins):
            if bin_edges[i] <= val < bin_edges[i + 1]:
                hist.data[i] += 1
                break
    
    return Array(hist.data), Array(bin_edges.data)

def sqrt(x: Union[Array, float, List[float]]) -> Array:

    if isinstance(x, (int, float)):
        if x < 0:
            raise ValueError
        return array([math.sqrt(x)])
    
    if isinstance(x, list):
        x = array(x)
    
    if isinstance(x, Array):
        if isinstance(x.data, list):
            if isinstance(x.data[0], list):  
                result = []
                for row in x.data:
                    row_result = []
                    for val in row:
                        if val < 0:
                            raise ValueError
                        row_result.append(math.sqrt(val))
                    result.append(row_result)
                return array(result)
            else:  
                result = []
                for val in x.data:
                    if val < 0:
                        raise ValueError
                    result.append(math.sqrt(val))
                return array(result)
        else: 
            if x.data < 0:
                raise ValueError
            return array([math.sqrt(x.data)])
    
    raise TypeError(f"unsupported operand type(s) for sqrt: '{type(x)}'")

def exp(x: Union[Array, float, List[float]]) -> Array:

    if isinstance(x, (int, float)):
        return array([math.exp(x)])
    
    if isinstance(x, list):
        x = array(x)
    
    result = []
    for val in x.data:
        result.append(math.exp(val))
    return array(result)

def log(x: Union[Array, float, List[float]]) -> Array:
 
    if isinstance(x, (int, float)):
        if x <= 0:
            raise ValueError
        return array([math.log(x)])
    
    if isinstance(x, list):
        x = array(x)
    
    result = []
    for val in x.data:
        if val <= 0:
            raise ValueError
        result.append(math.log(val))
    return array(result)

