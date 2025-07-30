
from . import A20_math as math
from .A32_typing import List, Union, Tuple, Optional, Any
from . import A22_random as pure_random

class Array:
    def __init__(self, data: Union[List, Tuple, float, int, 'Array'], dtype=None):

        if isinstance(data, Array):
            self.data = data.data.copy()
        elif isinstance(data, (list, tuple)):
        
            def convert_nested_to_float(nested_data):
                if isinstance(nested_data, (list, tuple)):
                    return [convert_nested_to_float(item) for item in nested_data]
                elif hasattr(nested_data, 'data'):
                    return convert_nested_to_float(nested_data.data)
                else:
                    return float(nested_data)
            
            self.data = convert_nested_to_float(data)
        elif hasattr(data, 'shape') and hasattr(data, 'flatten'):
            if len(data.shape) == 0:
                self.data = [float(data)]
            elif len(data.shape) == 1:
                self.data = [float(x) for x in data]
            else:
                self.data = data.tolist()
        else:
            if isinstance(data, Array):
                self.data = data.data
            elif hasattr(data, 'data') and hasattr(data, 'shape'):
                self.data = data.data
            else:
                try:
                    self.data = [float(data)]
                except (TypeError, ValueError):
                    self.data = [data]
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
            
        def get_nested_shape(data):
            if not isinstance(data, list):
                return ()
            if not data:
                return (0,)
            
            first_shape = (len(data),)
            if isinstance(data[0], list):
                sub_shape = get_nested_shape(data[0])
                return first_shape + sub_shape
            else:
                return first_shape
        
        shape = get_nested_shape(self.data)
        
        def validate_shape(data, expected_shape):
            if len(expected_shape) == 1:
                return len(data) == expected_shape[0]
            if len(data) != expected_shape[0]:
                return False
            if len(expected_shape) > 1:
                for item in data:
                    if not validate_shape(item, expected_shape[1:]):
                        return False
            return True
            
        return shape
    
    def reshape(self, *shape: int) -> 'Array':

        total_size = len(self.data)
        
        if len(shape) == 1:
            if isinstance(shape[0], (list, tuple)):
                shape = shape[0]
            elif hasattr(shape[0], '__iter__'): 
                shape = tuple(shape[0])
        
        shape = list(shape)
        
        shape = [int(dim) for dim in shape]
        
  
        flat_data = []
        if hasattr(self, '_flat_data') and self._flat_data:
           
            flat_data = self._flat_data[:]
        else:
          
            flat_data = []  
            def flatten_recursive(data):
                if isinstance(data, list):
                    for item in data:
                        flatten_recursive(item)
                else:
                    flat_data.append(float(data))
            
            flatten_recursive(self.data)
        
        total_size = len(flat_data)
        
       
        if -1 in shape:
            "good"

            idx = shape.index(-1)
            other_dims = 1
            for i, dim in enumerate(shape):
                if i != idx and dim != -1:
                    other_dims *= dim
            if other_dims == 0:
                shape[idx] = 0
            else:
                shape[idx] = total_size // other_dims

        else:
            total_shape = 1
            for dim in shape:
                total_shape *= dim

        new_array = Array.__new__(Array)
        new_array.dtype = self.dtype
        new_array.shape = tuple(shape)
        
        if len(shape) == 1:
            new_array.data = flat_data[:]
        elif len(shape) == 2:
            rows, cols = shape
            nested_data = []
            for i in range(rows):
                row = []
                for j in range(cols):
                    idx = i * cols + j
                    if idx < len(flat_data):
                        row.append(flat_data[idx])
                    else:
                        row.append(0.0) 
                nested_data.append(row)
            new_array.data = nested_data
        elif len(shape) == 3:
            d0, d1, d2 = shape
            nested_data = []
            for i in range(d0):
                layer = []
                for j in range(d1):
                    row = []
                    for k in range(d2):
                        idx = i * d1 * d2 + j * d2 + k
                        if idx < len(flat_data):
                            row.append(flat_data[idx])
                        else:
                            row.append(0.0)  
                    layer.append(row)
                nested_data.append(layer)
            new_array.data = nested_data
        elif len(shape) == 4:
            d0, d1, d2, d3 = shape
            nested_data = []
            for i in range(d0):
                batch = []
                for j in range(d1):
                    layer = []
                    for k in range(d2):
                        row = []
                        for l in range(d3):
                            idx = i * d1 * d2 * d3 + j * d2 * d3 + k * d3 + l
                            if idx < len(flat_data):
                                row.append(flat_data[idx])
                            else:
                                row.append(0.0)  
                        layer.append(row)
                    batch.append(layer)
                nested_data.append(batch)
            new_array.data = nested_data
        else:
            new_array.data = self._reshape_recursive(flat_data, shape, 0)
            
        return new_array
    
    def transpose(self):

        rows, cols = self.shape
        result = []
        for j in range(cols):
            row = []
            for i in range(rows):
                if isinstance(self.data[0], list):
                    row.append(self.data[i][j])
                else:
                    row.append(self.data[i * cols + j])
            result.append(row)
        return Array(result)
    
    @property
    def T(self):
        return self.transpose()
    
    def __add__(self, other: Union['Array', float, int]) -> 'Array':
        "good"
        if isinstance(other, (int, float)):
            if isinstance(self.data, list):
                if len(self.data) > 0 and isinstance(self.data[0], list):  
                    return Array([[float(x + other) for x in row] for row in self.data], dtype=self.dtype)
                else:  
                    return Array([float(x + other) for x in self.data], dtype=self.dtype)
            else: 
                return Array([float(self.data + other)], dtype=self.dtype)
        if isinstance(other, Array):

            
            if isinstance(self.data[0], list) and isinstance(other.data[0], list):
                return Array([[float(a + b) for a, b in zip(row_a, row_b)] 
                            for row_a, row_b in zip(self.data, other.data)], dtype=self.dtype)
            elif not isinstance(self.data[0], list) and not isinstance(other.data[0], list):
                return Array([float(a + b) for a, b in zip(self.data, other.data)], dtype=self.dtype)
            else:
                return Array([a + b for a, b in zip(self.data, other.data)], dtype=self.dtype)

    def __mul__(self, other):
        if hasattr(other, 'shape') and hasattr(other, 'tolist'):
            try:
                other = Array(other.tolist())
            except Exception:
                pass
        
        if isinstance(other, (int, float)):
            def mul_recursive(data):
                if isinstance(data, list):
                    if len(data) > 0 and isinstance(data[0], list):
                        return [mul_recursive(item) for item in data]
                    else:
                        return [float(x * other) for x in data]
                else:
                    return float(data * other)
            
            if isinstance(self.data, list):
                result_data = mul_recursive(self.data)
                return Array(result_data, dtype=self.dtype)
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
    
    def __rmul__(self, other):
        "good"
        return self.__mul__(other)

    
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
            

    def __truediv__(self, other: Union['Array', float, int]) -> 'Array':
        
        "good"
        if hasattr(other, 'shape') and hasattr(other, 'tolist'):
            try:
                other = Array(other.tolist())
            except Exception:
                pass
        
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("division by zero")
            def div_recursive(data):
                if isinstance(data, list):
                    if len(data) > 0 and isinstance(data[0], list):
                        return [div_recursive(item) for item in data]
                    else:
                        return [float(x / other) for x in data]
                else:
                    return float(data / other)
            
            if isinstance(self.data, list):
                result_data = div_recursive(self.data)
                return Array(result_data, dtype=self.dtype)
            else:  
                return Array([float(self.data / other)], dtype=self.dtype)
        elif isinstance(other, Array):
      
            if self.shape == other.shape:
                def div_elementwise(data_a, data_b):
                    if isinstance(data_a, list) and isinstance(data_b, list):
                        if len(data_a) > 0 and isinstance(data_a[0], list):
                            return [div_elementwise(row_a, row_b) for row_a, row_b in zip(data_a, data_b)]
                        else:
                          
                            return [float(a / b) if b != 0 else float('inf') for a, b in zip(data_a, data_b)]
                    else:
                        return float(data_a / data_b) if data_b != 0 else float('inf')
                
                result_data = div_elementwise(self.data, other.data)
                return Array(result_data, dtype=self.dtype)
        
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
            raise TypeError
    
    def __pow__(self, other: Union['Array', float, int]) -> 'Array':
        if isinstance(other, (int, float)):
            return Array([x ** other for x in self.data], dtype=self.dtype)
        if isinstance(other, Array):
            if self.shape != other.shape:
                raise ValueError("shapes do not match")
            return Array([a ** b for a, b in zip(self.data, other.data)], dtype=self.dtype)
        raise TypeError
    
    def sum(self, axis: Optional[int] = None, keepdims: bool = False) -> Union['Array', float]:

        if not self.data:
            return 0.0
            
        if axis is None:
            if len(self.data) > 0 and isinstance(self.data[0], list):
                flat_data = self._flatten_recursive(self.data)
                return __builtins__['sum'](flat_data)
            else:
                return __builtins__['sum'](self.data)
        
        if axis >= len(self.shape):
            raise ValueError
        
        if len(self.shape) == 1:
            result = __builtins__['sum'](self.data)
            if keepdims:
                return Array([result])
            return result
        
        if len(self.shape) == 2:
            rows, cols = self.shape
            if axis == 0:
                result = []
                for j in range(cols):
                    col_sum = __builtins__['sum'](self.data[i][j] for i in range(rows))
                    result.append(col_sum)
                result_array = Array(result)
                if keepdims:
                    result_array = result_array.reshape(1, cols)
                return result_array
            else:
                result = []
                for i in range(rows):
                    row_sum = __builtins__['sum'](self.data[i])
                    result.append(row_sum)
                result_array = Array(result)
                if keepdims:
                    result_array = result_array.reshape(rows, 1)
                return result_array
        
        if len(self.shape) == 3:
            d0, d1, d2 = self.shape
            if axis == 0:
                result = []
                for i in range(d1):
                    row = []
                    for j in range(d2):
                        sum_val = __builtins__['sum'](self.data[k][i][j] for k in range(d0))
                        row.append(sum_val)
                    result.append(row)
                result_array = Array(result)
                if keepdims:
                    result_array = result_array.reshape(1, d1, d2)
                return result_array
            elif axis == 1:
                result = []
                for i in range(d0):
                    row = []
                    for j in range(d2):
                        sum_val = __builtins__['sum'](self.data[i][k][j] for k in range(d1))
                        row.append(sum_val)
                    result.append(row)
                result_array = Array(result)
                if keepdims:
                
                    new_data = []
                    for i in range(d0):
                        new_data.append([result_array.data[i]])
                    result_array = Array(new_data)
                return result_array
            else:  
                result = []
                for i in range(d0):
                    row = []
                    for j in range(d1):
                        sum_val = __builtins__['sum'](self.data[i][j][k] for k in range(d2))
                        row.append(sum_val)
                    result.append(row)
                result_array = Array(result)
                if keepdims:
               
                    new_data = []
                    for i in range(d0):
                        layer = []
                        for j in range(d1):
                            layer.append([result_array.data[i][j]])
                        new_data.append(layer)
                    result_array = Array(new_data)
                return result_array
        
        return self._sum_general(axis, keepdims)
    
    def _sum_general(self, axis: int, keepdims: bool = False):
      
        if len(self.shape) == 4:
            return self._sum_4d(axis, keepdims)
        
        return self._sum_recursive(axis, keepdims)
    
    def _sum_4d(self, axis: int, keepdims: bool = False):
        d0, d1, d2, d3 = self.shape
        
        if axis == 0:
            result = []
            for i in range(d1):
                layer = []
                for j in range(d2):
                    row = []
                    for k in range(d3):
                        sum_val = __builtins__['sum'](self.data[l][i][j][k] for l in range(d0))
                        row.append(sum_val)
                    layer.append(row)
                result.append(layer)
            result_array = Array(result)
            if keepdims:
          
                new_data = [result_array.data]
                result_array = Array(new_data)
            return result_array
        elif axis == 1:
            result = []
            for i in range(d0):
                layer = []
                for j in range(d2):
                    row = []
                    for k in range(d3):
                        sum_val = __builtins__['sum'](self.data[i][l][j][k] for l in range(d1))
                        row.append(sum_val)
                    layer.append(row)
                result.append(layer)
            result_array = Array(result)
            if keepdims:
          
                new_data = []
                for i in range(d0):
                    new_data.append([result_array.data[i]])
                result_array = Array(new_data)
            return result_array
        elif axis == 2:
            result = []
            for i in range(d0):
                layer = []
                for j in range(d1):
                    row = []
                    for k in range(d3):
                        sum_val = __builtins__['sum'](self.data[i][j][l][k] for l in range(d2))
                        row.append(sum_val)
                    layer.append(row)
                result.append(layer)
            result_array = Array(result)
            if keepdims:
          
                new_data = []
                for i in range(d0):
                    batch = []
                    for j in range(d1):
                        batch.append([result_array.data[i][j]])
                    new_data.append(batch)
                result_array = Array(new_data)
            return result_array
        else:  
            result = []
            for i in range(d0):
                layer = []
                for j in range(d1):
                    row = []
                    for k in range(d2):
                        sum_val = __builtins__['sum'](self.data[i][j][k][l] for l in range(d3))
                        row.append(sum_val)
                    layer.append(row)
                result.append(layer)
            result_array = Array(result)
            if keepdims:
            
                new_data = []
                for i in range(d0):
                    batch = []
                    for j in range(d1):
                        layer = []
                        for k in range(d2):
                            layer.append([result_array.data[i][j][k]])
                        batch.append(layer)
                    new_data.append(batch)
                result_array = Array(new_data)
            return result_array
    
    def _sum_recursive(self, axis: int, keepdims: bool = False):
   
        flat_data = self._flatten_recursive(self.data)
        
    
        if axis == len(self.shape) - 1:
            return __builtins__['sum'](flat_data)
        else:
            return __builtins__['sum'](flat_data)
    
    def mean(self, axis: Optional[int] = None) -> Union['Array', float]:
  
        if not self.data:
            raise ValueError
            
        if axis is not None and axis >= len(self.shape):
            raise ValueError
            
        try:
            if axis is None:
                if len(self.shape) == 1:
                    return __builtins__['sum'](self.data) / len(self.data)
                else:
                    flat_data = self._flatten_recursive(self.data)
                    return __builtins__['sum'](flat_data) / len(flat_data)
            result = self.sum(axis)
            if isinstance(result, Array):
                return result / self.shape[axis]
            return result
        except Exception as e:
            raise RuntimeError
    
    def max(self, axis: Optional[int] = None, keepdims: bool = False) -> Union['Array', float]:
 
        if axis is None:
            if isinstance(self.data[0], list):
                flat_data = self._flatten_recursive(self.data)
                return __builtins__['max'](flat_data)
            else:
                return __builtins__['max'](self.data)
        
        if axis >= len(self.shape):
            raise ValueError
        
        if len(self.shape) == 1:
            return __builtins__['max'](self.data)
        
        if len(self.shape) == 2:
            rows, cols = self.shape
            if axis == 0:
                result = []
                for j in range(cols):
                    col_max = self.data[0][j]
                    for i in range(1, rows):
                        if self.data[i][j] > col_max:
                            col_max = self.data[i][j]
                    result.append(col_max)
                return Array(result)
            else: 
                result = []
                for i in range(rows):
                    row_max = self.data[i][0]
                    for j in range(1, cols):
                        if self.data[i][j] > row_max:
                            row_max = self.data[i][j]
                    result.append(row_max)
                return Array(result)
        
        if len(self.shape) == 3:
            d0, d1, d2 = self.shape
            if axis == 0:
                result = []
                for i in range(d1):
                    row = []
                    for j in range(d2):
                        max_val = self.data[0][i][j]
                        for k in range(1, d0):
                            if self.data[k][i][j] > max_val:
                                max_val = self.data[k][i][j]
                        row.append(max_val)
                    result.append(row)
                return Array(result)
            elif axis == 1:
                result = []
                for i in range(d0):
                    row = []
                    for j in range(d2):
                        max_val = self.data[i][0][j]
                        for k in range(1, d1):
                            if self.data[i][k][j] > max_val:
                                max_val = self.data[i][k][j]
                        row.append(max_val)
                    result.append(row)
                return Array(result)
            else:  
                result = []
                for i in range(d0):
                    row = []
                    for j in range(d1):
                        max_val = self.data[i][j][0]
                        for k in range(1, d2):
                            if self.data[i][j][k] > max_val:
                                max_val = self.data[i][j][k]
                        row.append(max_val)
                    result.append(row)
                return Array(result)
        
        return self._max_general(axis, keepdims)
    
    def _flatten_recursive(self, data):
        result = []
        for item in data:
            if isinstance(item, list):
                result.extend(self._flatten_recursive(item))
            else:
                result.append(item)
        return result
    
    def _max_general(self, axis: int, keepdims: bool = False):
  
        if len(self.shape) == 4:
            return self._max_4d(axis, keepdims)
        
        return self._max_recursive(axis, keepdims)
    
    def _max_4d(self, axis: int, keepdims: bool = False):
        d0, d1, d2, d3 = self.shape
        
        if axis == 0:
            result = []
            for i in range(d1):
                layer = []
                for j in range(d2):
                    row = []
                    for k in range(d3):
                        max_val = self.data[0][i][j][k]
                        for l in range(1, d0):
                            if self.data[l][i][j][k] > max_val:
                                max_val = self.data[l][i][j][k]
                        row.append(max_val)
                    layer.append(row)
                result.append(layer)
            return Array(result)
        elif axis == 1:
            result = []
            for i in range(d0):
                layer = []
                for j in range(d2):
                    row = []
                    for k in range(d3):
                        max_val = self.data[i][0][j][k]
                        for l in range(1, d1):
                            if self.data[i][l][j][k] > max_val:
                                max_val = self.data[i][l][j][k]
                        row.append(max_val)
                    layer.append(row)
                result.append(layer)
            return Array(result)
        elif axis == 2:
            result = []
            for i in range(d0):
                layer = []
                for j in range(d1):
                    row = []
                    for k in range(d3):
                        max_val = self.data[i][j][0][k]
                        for l in range(1, d2):
                            if self.data[i][j][l][k] > max_val:
                                max_val = self.data[i][j][l][k]
                        row.append(max_val)
                    layer.append(row)
                result.append(layer)
            return Array(result)
        else: 
            result = []
            for i in range(d0):
                layer = []
                for j in range(d1):
                    row = []
                    for k in range(d2):
                        max_val = self.data[i][j][k][0]
                        for l in range(1, d3):
                            if self.data[i][j][k][l] > max_val:
                                max_val = self.data[i][j][k][l]
                        row.append(max_val)
                    layer.append(row)
                result.append(layer)
            result_array = Array(result)
            if keepdims:
              
                new_data = []
                for i in range(d0):
                    layer = []
                    for j in range(d1):
                        row = []
                        for k in range(d2):
                            row.append([result_array.data[i][j][k]])
                        layer.append(row)
                    new_data.append(layer)
                result_array = Array(new_data)
            return result_array
    
    def _max_recursive(self, axis: int, keepdims: bool = False):
       
        flat_data = self._flatten_recursive(self.data)
        
    
        if axis == len(self.shape) - 1:
            return __builtins__['max'](flat_data)
        else:
            return __builtins__['max'](flat_data)
    
    def min(self, axis: Optional[int] = None) -> Union['Array', float]:
        if axis is None:
            return __builtins__['min'](self.data)
        if axis >= len(self.shape):
            raise ValueError("axis out of bounds")
        if len(self.shape) == 1:
            return __builtins__['min'](self.data)
        if len(self.shape) == 2:
            rows, cols = self.shape
            if axis == 0:
                return Array([__builtins__['min'](self.data[i::cols]) for i in range(cols)])
            else:
                return Array([__builtins__['min'](self.data[i*cols:(i+1)*cols]) for i in range(rows)])
        raise NotImplementedError
    
    def dot(self, other: 'Array') -> 'Array':

        if len(self.shape) == 2 and len(other.shape) == 2:
      
            return self._dot_2d_2d(other)
        
        elif len(self.shape) == 3 and len(other.shape) == 2:
       
            return self._dot_3d_2d(other)
        
        elif len(self.shape) == 3 and len(other.shape) == 3:
          
            return self._dot_3d_3d(other)
        
        elif len(self.shape) == 4 and len(other.shape) == 4:
           
            if (self.shape[0] != other.shape[0] or self.shape[1] != other.shape[1] or 
                self.shape[3] != other.shape[2]):
                raise ValueError
            return self._dot_4d_4d(other)
        
        else:
            raise ValueError
    
    def _dot_2d_2d(self, other: 'Array') -> 'Array':
        rows_a, cols_a = self.shape
        rows_b, cols_b = other.shape
        
        result = []
        for i in range(rows_a):
            row = []
            for j in range(cols_b):
                sum_val = 0
                for k in range(cols_a):
                    if isinstance(self.data[0], list):
                        val_a = self.data[i][k]
                    else:
                        val_a = self.data[i * cols_a + k]
                    
                    if isinstance(other.data[0], list):
                        val_b = other.data[k][j]
                    else:
                        val_b = other.data[k * cols_b + j]
                    
                    sum_val += val_a * val_b
                row.append(sum_val)
            result.append(row)
        return Array(result)
    
    def _dot_3d_2d(self, other: 'Array') -> 'Array':
        batch_size, seq_len, features = self.shape
        out_features = other.shape[1]
        
        result = []
        for b in range(batch_size):
            batch_result = []
            for s in range(seq_len):
                row = []
                for o in range(out_features):
                    sum_val = 0
                    for f in range(features):
                        val_a = self.data[b][s][f]
                        if isinstance(other.data[0], list):
                            val_b = other.data[f][o]
                        else:
                            val_b = other.data[f * out_features + o]
                        sum_val += val_a * val_b
                    row.append(sum_val)
                batch_result.append(row)
            result.append(batch_result)
        return Array(result)
    
    def _dot_3d_3d(self, other: 'Array') -> 'Array':
        batch_size = self.shape[0]
        result = []
        for b in range(batch_size):
            a_2d = Array(self.data[b])
            b_2d = Array(other.data[b])
            batch_result = a_2d._dot_2d_2d(b_2d)
            result.append(batch_result.data)
        return Array(result)
    
    def _dot_4d_4d(self, other: 'Array') -> 'Array':
        batch_size, num_heads, seq_len, features = self.shape
        _, _, features_other, seq_len_other = other.shape
        
        result = []
        for b in range(batch_size):
            batch_result = []
            for h in range(num_heads):
                a_2d = Array(self.data[b][h]) 
                b_2d = Array(other.data[b][h])  
                head_result = a_2d._dot_2d_2d(b_2d) 
                batch_result.append(head_result.data)
            result.append(batch_result)
        return Array(result)
    
    def __matmul__(self, other: 'Array') -> 'Array':
        return self.dot(other)
    
    def __getitem__(self, key: Union[int, slice, Tuple]) -> 'Array':
        if isinstance(key, int):
            if key >= len(self.data):
                raise IndexError
            return Array([self.data[key]], dtype=self.dtype)
        if isinstance(key, slice):
            return Array(self.data[key], dtype=self.dtype)
        if isinstance(key, tuple):
            if len(key) != len(self.shape):
                raise ValueError
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
        raise TypeError
    
    def __setitem__(self, key: Union[int, slice, Tuple], value: Union['Array', float, int]) -> None:
        if isinstance(key, int):
  
            self.data[key] = float(value)
        elif isinstance(key, slice):
            if isinstance(value, (int, float)):
                for i in range(*key.indices(len(self.data))):
                    self.data[i] = float(value)
            elif isinstance(value, Array):
                for i, v in zip(range(*key.indices(len(self.data))), value.data):
                    self.data[i] = float(v)
        elif isinstance(key, tuple):
    
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
            raise TypeError
    
    def __repr__(self) -> str:
        return f"Array({self.data}, shape={self.shape}, dtype={self.dtype})"
    
    @property
    def ndim(self) -> int:
        return len(self.shape)
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def copy(self) -> 'Array':
        return Array(self.data.copy(), dtype=self.dtype)
    
    def astype(self, dtype) -> 'Array':
        return Array(self.data, dtype=dtype)
    
    def fill(self, value: float) -> None:
        self.data = [float(value)] * len(self.data)
    
    def clip(self, min_val: float, max_val: float) -> 'Array':
        def clip_recursive(data):
            if isinstance(data, list):
                return [clip_recursive(item) for item in data]
            else:
                return __builtins__['max'](min_val, __builtins__['min'](data, max_val))
        
        return Array(clip_recursive(self.data), dtype=self.dtype)
    
    def exp(self) -> 'Array':
        def exp_recursive(data):
            if isinstance(data, list):
                return [exp_recursive(item) for item in data]
            else:
                try:
                    return math.exp(float(data))
                except (ValueError, TypeError):
                    return 0.0
        
        result_data = exp_recursive(self.data)
        result = Array(result_data, dtype=self.dtype)
        if hasattr(self, 'shape'):
            result.shape = self.shape
        return result
    
    def log(self) -> 'Array':
        def log_recursive(data):
            if isinstance(data, list):
                return [log_recursive(item) for item in data]
            else:
                try:
                    val = float(data)
                    if val <= 0:
                        return float('-inf') 
                    return math.log(val)
                except (ValueError, TypeError):
                    return 0.0
        
        result_data = log_recursive(self.data)
        result = Array(result_data, dtype=self.dtype)
        if hasattr(self, 'shape'):
            result.shape = self.shape
        return result
    
    def sqrt(self) -> 'Array':
        def sqrt_recursive(data):
            if isinstance(data, list):
                return [sqrt_recursive(item) for item in data]
            else:
                try:
                    val = float(data)
                    if val < 0:
                        return 0.0  
                    return math.sqrt(val)
                except (ValueError, TypeError):
                    return 0.0
        
        result_data = sqrt_recursive(self.data)
        result = Array(result_data, dtype=self.dtype)
        if hasattr(self, 'shape'):
            result.shape = self.shape
        return result
    
    def abs(self) -> 'Array':
        def abs_recursive(data):
            if isinstance(data, list):
                return [abs_recursive(item) for item in data]
            else:
                return __builtins__['abs'](data)
        
        result_data = abs_recursive(self.data)
        return Array(result_data, dtype=self.dtype)
    
    def flatten(self) -> 'Array':
  
        def flatten_recursive(data):
            result = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, list):
                        result.extend(flatten_recursive(item))
                    else:
                        result.append(item)
            else:
                result.append(data)
            return result
        
        flat_data = flatten_recursive(self.data)
        return Array(flat_data, dtype=self.dtype)
    
    def var(self, axis: Optional[int] = None) -> Union['Array', float]:
        mean_val = self.mean(axis)
        if axis is None:
            return __builtins__['sum']((x - mean_val) ** 2 for x in self.data) / len(self.data)
        if len(self.shape) == 1:
            return __builtins__['sum']((x - mean_val) ** 2 for x in self.data) / len(self.data)
        if len(self.shape) == 2:
            rows, cols = self.shape
            if axis == 0:
                return Array([__builtins__['sum']((self.data[i::cols] - mean_val.data[i]) ** 2 for i in range(cols)) / rows])
            else:
                return Array([__builtins__['sum']((self.data[i*cols:(i+1)*cols] - mean_val.data[i]) ** 2 for i in range(rows)) / cols])
        raise NotImplementedError

    def _ensure_2d(self) -> None:
        if len(self.shape) == 1:
            self.data = [self.data]
            self.shape = (1, len(self.data[0]))

    def argmax(self, axis: Optional[int] = None) -> Union['Array', int]:

        if axis is None:
            if isinstance(self.data[0], list):
                max_val = self.data[0][0]
                max_idx = 0
                idx = 0
                for i, row in enumerate(self.data):
                    for j, val in enumerate(row):
                        if val > max_val:
                            max_val = val
                            max_idx = idx
                        idx += 1
                return max_idx
            else:
                max_val = self.data[0]
                max_idx = 0
                for i, val in enumerate(self.data):
                    if val > max_val:
                        max_val = val
                        max_idx = i
                return max_idx
        
        if axis >= len(self.shape):
            raise ValueError
        
        if len(self.shape) == 1:
            return self.argmax()
        
        if len(self.shape) == 2:
            rows, cols = self.shape
            if axis == 0:
                result = []
                for j in range(cols):
                    max_val = self.data[0][j]
                    max_idx = 0
                    for i in range(rows):
                        if self.data[i][j] > max_val:
                            max_val = self.data[i][j]
                            max_idx = i
                    result.append(max_idx)
                return Array(result)
            else:  
                result = []
                for i in range(rows):
                    max_val = self.data[i][0]
                    max_idx = 0
                    for j in range(cols):
                        if self.data[i][j] > max_val:
                            max_val = self.data[i][j]
                            max_idx = j
                    result.append(max_idx)
                return Array(result)
        
        raise NotImplementedError
    def any(self) -> bool:

        if isinstance(self.data[0], list):
            for row in self.data:
                for val in row:
                    if val:
                        return True
            return False
        else:
            for val in self.data:
                if val:
                    return True
            return False
    
    def __getstate__(self):
        return {
            'data': self.data,
            'shape': self.shape,
            'dtype': self.dtype
        }
    
    def __setstate__(self, state):
        self.data = state['data']
        self.shape = state['shape']
        self.dtype = state['dtype']
    

def array(data: Union[List, Tuple, float, int, Array], dtype=None) -> Array:
    return Array(data, dtype=dtype)

def zeros(shape: Union[int, Tuple[int, ...]], dtype: str = 'float32') -> Array:

    if isinstance(shape, int):
        if shape <= 0:
            shape = (1,)
        else:
            shape = (shape,)
    elif isinstance(shape, tuple):
        fixed_shape = []
        for dim in shape:
            if not isinstance(dim, int) or dim <= 0:
                fixed_shape.append(1) 
            else:
                fixed_shape.append(dim)
        shape = tuple(fixed_shape)
    else:
        raise ValueError
        
    try:
        if isinstance(shape, int):
            total_size = shape
        else:
            total_size = 1
            for dim in shape:
                total_size *= dim
                
        data = [0.0] * total_size
        result = Array(data, dtype=dtype)
        
        if isinstance(shape, tuple) and len(shape) > 1:
            result = result.reshape(*shape)
            
        return result
    except Exception as e:
        raise RuntimeError

def ones(shape: Union[int, Tuple[int, ...]], dtype: str = 'float32') -> Array:

    if isinstance(shape, int):
        if shape <= 0:
            shape = (1,)
        else:
            shape = (shape,)
    elif isinstance(shape, tuple):
        fixed_shape = []
        for dim in shape:
            if not isinstance(dim, int) or dim <= 0:
                fixed_shape.append(1) 
            else:
                fixed_shape.append(dim)
        shape = tuple(fixed_shape)
    else:
        raise ValueError
        
    try:
        if isinstance(shape, int):
            total_size = shape
        else:
            total_size = 1
            for dim in shape:
                total_size *= dim
                
        data = [1.0] * total_size
        result = Array(data, dtype=dtype)
        
        if isinstance(shape, tuple) and len(shape) > 1:
            result = result.reshape(*shape)
            
        return result
    except Exception as e:
        raise RuntimeError

def empty(shape: Union[int, Tuple[int, ...]], dtype=None) -> Array:
    return zeros(shape, dtype=dtype)

def random_normal(shape: Union[int, Tuple[int, ...]], mean=0.0, std=1.0, dtype=None) -> Array:

    if isinstance(shape, int):
      
        shape = (shape,)
    elif isinstance(shape, tuple):
    
        for dim in shape:
            if dim <= 0:
                raise ValueError
    else:
        raise ValueError
            
    try:
        if isinstance(shape, int):
            total_size = shape
        else:
            total_size = 1
            for dim in shape:
                total_size *= dim
                
        data = pure_random.normal_batch(total_size, mean, std)
        
        result = Array.__new__(Array)
        result.data = data
        result.shape = shape
        result.dtype = dtype or float
        
        return result
    except Exception as e:
        raise RuntimeError

def random_uniform(shape: Union[int, Tuple[int, ...]], low=0.0, high=1.0, dtype=None) -> Array:
    if isinstance(shape, int):
        size = shape
    else:
        size = 1
        for dim in shape:
            size *= dim
    data = pure_random.uniform_batch(size, low, high)  
    
    result = Array.__new__(Array)
    result.data = data
    result.shape = shape if isinstance(shape, tuple) else (shape,)
    result.dtype = dtype or float
    
    return result

def randn(*shape: int, dtype=None) -> Array:

    if len(shape) == 0:
        raise ValueError
    
    for dim in shape:
        if not isinstance(dim, int) or dim <= 0:
            raise ValueError
    
    if len(shape) == 1:
        return random_normal(shape[0], mean=0.0, std=1.0, dtype=dtype)
    else:
        return random_normal(shape, mean=0.0, std=1.0, dtype=dtype)

class random:
    
    @staticmethod
    def uniform(low=0.0, high=1.0, size=None):

        if size is None:
            return pure_random.uniform(low, high)
        
        if isinstance(size, int):
            size = (size,)
        elif isinstance(size, (list, tuple)):
            size = tuple(size)
        else:
            raise ValueError
        
        return random_uniform(size, low, high)
    
    @staticmethod
    def randn(*args):
        return randn(*args)
    
    @staticmethod
    def normal(loc=0.0, scale=1.0, size=None):

        if size is None:
            return pure_random.normal(loc, scale)
        
        if isinstance(size, int):
            size = (size,)
        elif isinstance(size, (list, tuple)):
            size = tuple(size)
        else:
            raise ValueError
        
        return random_normal(size, loc, scale)

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
        raise ValueError
    if axis >= len(arrays[0].shape):
        raise ValueError
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
    raise NotImplementedError

def stack(arrays: List[Array], axis: int = 0) -> Array:
    if not arrays:
        raise ValueError
    if axis > len(arrays[0].shape):
        raise ValueError
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
    raise NotImplementedError

def maximum(a: Union[Array, float], b: Union[Array, float]) -> Array:
    if not isinstance(a, Array) and not isinstance(a, (int, float)):
        a = Array(a)
    if not isinstance(b, Array) and not isinstance(b, (int, float)):
        b = Array(b)
        
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return Array([max(a, b)], dtype=float)
    if isinstance(a, (int, float)):
        if len(b.data) > 0 and isinstance(b.data[0], list): 
            result = []
            for row in b.data:
                result.append([__builtins__['max'](a, x) for x in row])
            return Array(result, dtype=b.dtype)
        else:  
            return Array([__builtins__['max'](a, x) for x in b.data], dtype=b.dtype)
    if isinstance(b, (int, float)):
        if len(a.data) > 0 and isinstance(a.data[0], list): 
            result = []
            for row in a.data:
                result.append([__builtins__['max'](x, b) for x in row])
            return Array(result, dtype=a.dtype)
        else:  
            return Array([__builtins__['max'](x, b) for x in a.data], dtype=a.dtype)
    
    if a.shape != b.shape:
        raise ValueError
    
    if len(a.data) > 0 and len(b.data) > 0:
        if isinstance(a.data[0], list) and isinstance(b.data[0], list):
            result = []
            for row_a, row_b in zip(a.data, b.data):
                result.append([__builtins__['max'](x, y) for x, y in zip(row_a, row_b)])
            return Array(result, dtype=a.dtype)
        elif not isinstance(a.data[0], list) and not isinstance(b.data[0], list):
            return Array([__builtins__['max'](x, y) for x, y in zip(a.data, b.data)], dtype=a.dtype)
        else:
            raise ValueError
    else:
        return Array([], dtype=a.dtype if hasattr(a, 'dtype') else float)

def minimum(a: Union[Array, float], b: Union[Array, float]) -> Array:
    if not isinstance(a, Array) and not isinstance(a, (int, float)):
        a = Array(a)
    if not isinstance(b, Array) and not isinstance(b, (int, float)):
        b = Array(b)
        
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return Array([__builtins__['min'](a, b)], dtype=float)
    if isinstance(a, (int, float)):
        if len(b.data) > 0 and isinstance(b.data[0], list): 
            result = []
            for row in b.data:
                result.append([__builtins__['min'](a, x) for x in row])
            return Array(result, dtype=b.dtype)
        else: 
            return Array([__builtins__['min'](a, x) for x in b.data], dtype=b.dtype)
    if isinstance(b, (int, float)):
        if len(a.data) > 0 and isinstance(a.data[0], list): 
            result = []
            for row in a.data:
                result.append([__builtins__['min'](x, b) for x in row])
            return Array(result, dtype=a.dtype)
        else:  
            return Array([__builtins__['min'](x, b) for x in a.data], dtype=a.dtype)
    
    if a.shape != b.shape:
        raise ValueError
    
    if len(a.data) > 0 and len(b.data) > 0:
        if isinstance(a.data[0], list) and isinstance(b.data[0], list):
            result = []
            for row_a, row_b in zip(a.data, b.data):
                result.append([__builtins__['min'](x, y) for x, y in zip(row_a, row_b)])
            return Array(result, dtype=a.dtype)
        elif not isinstance(a.data[0], list) and not isinstance(b.data[0], list):
            return Array([__builtins__['min'](x, y) for x, y in zip(a.data, b.data)], dtype=a.dtype)
        else:
            raise ValueError
    else:
        # 处理空数组的情况
        return Array([], dtype=a.dtype if hasattr(a, 'dtype') else float)

def where(condition: Array, x: Union[Array, float], y: Union[Array, float]) -> Array:

    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return Array([x if c else y for c in condition.data], dtype=float)
    if isinstance(x, (int, float)):
       
        return Array([x if c else y_val for c, y_val in zip(condition.data, y.data)], dtype=y.dtype)
    if isinstance(y, (int, float)):
     
        return Array([x_val if c else y for c, x_val in zip(condition.data, x.data)], dtype=x.dtype)
 
    return Array([x_val if c else y_val for c, x_val, y_val in zip(condition.data, x.data, y.data)], dtype=x.dtype)

def einsum(equation: str, *arrays: Array) -> Array:
    if equation == 'ij,jk->ik':
      
        return arrays[0].dot(arrays[1])
    raise NotImplementedError

def bmm(x: Array, y: Array) -> Array:

 
    result = []
    for i in range(x.shape[0]):
        x_i = Array(x.data[i * x.shape[1] * x.shape[2]:(i + 1) * x.shape[1] * x.shape[2]], dtype=x.dtype).reshape(x.shape[1], x.shape[2])
        y_i = Array(y.data[i * y.shape[1] * y.shape[2]:(i + 1) * y.shape[1] * y.shape[2]], dtype=y.dtype).reshape(y.shape[1], y.shape[2])
        result.extend(x_i.dot(y_i).data)
    return Array(result, dtype=x.dtype).reshape(x.shape[0], x.shape[1], y.shape[2])

def conv2d(input: Array, weight: Array, bias: Optional[Array] = None, stride: Tuple[int, int] = (1, 1), padding: Tuple[int, int] = (0, 0)) -> Array:
    
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
    return __builtins__['sum'](x) / len(x)

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
        
    min_val = __builtins__['min'](data)
    max_val = __builtins__['max'](data)
    
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
    
    if hasattr(x, 'shape') and hasattr(x, 'flatten'):
        try:
            from . import A25_strong_sqrt as strong_sqrt
            strong_result = strong_sqrt.replace_np_sqrt(x)
            if len(x.shape) == 0:
                return array([float(strong_result)])
            elif len(x.shape) == 1:
                return array(strong_result.tolist() if hasattr(strong_result, 'tolist') else strong_result)
            else:
                return array(strong_result.tolist() if hasattr(strong_result, 'tolist') else strong_result)
        except Exception as e:
            pass
    
    if isinstance(x, Array):
        def sqrt_recursive(data):
            if isinstance(data, list):
                if len(data) > 0 and isinstance(data[0], list):
                    return [sqrt_recursive(item) for item in data]
                else:
                    return [math.sqrt(float(val)) for val in data]
            else:
                val = float(data)
                if val < 0:
                    raise ValueError
                return math.sqrt(val)
        
        try:
            result_data = sqrt_recursive(x.data)
            return array(result_data)
        except Exception as e:
            if isinstance(x.data, list):
                if len(x.data) > 0 and isinstance(x.data[0], list): 
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
    
    raise TypeError

def exp(x: Union[Array, float, List[float]]) -> Array:

    if isinstance(x, (int, float)):
        return array([math.exp(x)])
    
    if isinstance(x, list):
        x = array(x)
    
    if isinstance(x, Array):
        def exp_recursive(data):
            if isinstance(data, list):
                return [exp_recursive(item) for item in data]
            elif hasattr(data, 'data'):
                return exp_recursive(data.data)
            else:
                try:
                    return math.exp(float(data))
                except (ValueError, TypeError):
                    return 0.0
        
        result_data = exp_recursive(x.data)
        return array(result_data)
    
    raise TypeError

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

def argmax(x: Array, axis: Optional[int] = None) -> Union[Array, int]:
 
    if not isinstance(x, Array):
        raise TypeError
    
    return x.argmax(axis)

def zeros_like(x: Array, dtype: Optional[type] = None) -> Array:
 
    if not isinstance(x, Array):
        x = Array(x)
    return zeros(x.shape, dtype=dtype or x.dtype)

def ones_like(x: Array, dtype: Optional[type] = None) -> Array:

    if not isinstance(x, Array):
        x = Array(x)
    return ones(x.shape, dtype=dtype or x.dtype)

def max(x: Array, axis: Optional[int] = None, keepdims: bool = False) -> Union[Array, float]:
 
    if not isinstance(x, Array):
        x = Array(x)
    return x.max(axis, keepdims)

def min(x: Array, axis: Optional[int] = None, keepdims: bool = False) -> Union[Array, float]:
 
    if not isinstance(x, Array):
        x = Array(x)
    result = x.min(axis)
    if axis is not None and keepdims and isinstance(result, Array):
        new_shape = list(x.shape)
        new_shape[axis] = 1
        result = result.reshape(*new_shape)
    return result

def sum(x: Array, axis: Optional[int] = None, keepdims: bool = False) -> Union[Array, float]:

    if not isinstance(x, Array):
        x = Array(x)
    return x.sum(axis, keepdims)

def asarray(data, dtype=None) -> Array:
  
    if hasattr(data, '__array__'):
        from .A11_final_asarray import ult_asarray
        converted_data = ult_asarray(data)
        return Array(converted_data, dtype=dtype)
    
    if isinstance(data, memoryview):
        from .A11_final_asarray import ult_asarray
        converted_data = ult_asarray(data)
        return Array(converted_data, dtype=dtype)

    if hasattr(data, 'tolist'):
        try:
            return Array(data.tolist(), dtype=dtype)
        except:
            pass
    
    if hasattr(data, 'item'):
        try:
            return Array([data.item()], dtype=dtype)
        except:
            pass
    
    return Array(data, dtype=dtype)


def isnan(x: Array) -> Array:

    if not isinstance(x, Array):
        x = Array(x)
    
    result = []
    for val in x.data:
        result.append(math.isnan(val) if isinstance(val, (int, float)) else False)
    return Array(result)

def isinf(x: Array) -> Array:
  
    if not isinstance(x, Array):
        x = Array(x)
    
    result = []
    for val in x.data:
        result.append(math.isinf(val) if isinstance(val, (int, float)) else False)
    return Array(result)

def any(x: Array) -> bool:
  
    if not isinstance(x, Array):
        x = Array(x)
    
    for val in x.data:
        if val:
            return True
    return False

def tanh(x: Union[Array, float, List[float]]) -> Array:
   
    if isinstance(x, (int, float)):
        exp_x = math.exp(x)
        exp_neg_x = math.exp(-x)
        return array([(exp_x - exp_neg_x) / (exp_x + exp_neg_x)])
    
    if isinstance(x, list):
        x = array(x)
    
    if isinstance(x, Array):
        if isinstance(x.data, list):
            if isinstance(x.data[0], list):  
                result = []
                for row in x.data:
                    row_result = []
                    for val in row:
                        exp_val = math.exp(val)
                        exp_neg_val = math.exp(-val)
                        row_result.append((exp_val - exp_neg_val) / (exp_val + exp_neg_val))
                    result.append(row_result)
                return array(result)
            else:  
                result = []
                for val in x.data:
                    exp_val = math.exp(val)
                    exp_neg_val = math.exp(-val)
                    result.append((exp_val - exp_neg_val) / (exp_val + exp_neg_val))
                return array(result)
        else: 
            exp_val = math.exp(x.data)
            exp_neg_val = math.exp(-x.data)
            return array([(exp_val - exp_neg_val) / (exp_val + exp_neg_val)])
    
    raise TypeError

def erf(x: Union[Array, float, List[float]]) -> Array:

    def _erf_single(x_val):
 
        a1 =  0.254829592
        a2 = -0.284496736
        a3 =  1.421413741
        a4 = -1.453152027
        a5 =  1.061405429
        p  =  0.3275911
        
        sign = 1 if x_val >= 0 else -1
        x_abs = abs(x_val)
        
        t = 1.0 / (1.0 + p * x_abs)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x_abs * x_abs)
        
        return sign * y
    
    if isinstance(x, (int, float)):
        return array([_erf_single(x)])
    
    if isinstance(x, list):
        x = array(x)
    
    if isinstance(x, Array):
        if isinstance(x.data, list):
            if isinstance(x.data[0], list):  
                result = []
                for row in x.data:
                    row_result = []
                    for val in row:
                        row_result.append(_erf_single(val))
                    result.append(row_result)
                return array(result)
            else:  
                result = []
                for val in x.data:
                    result.append(_erf_single(val))
                return array(result)
        else:  
            return array([_erf_single(x.data)])
    
    raise TypeError

def matmul(a: Union[Array, List, Tuple], b: Union[Array, List, Tuple]) -> Array:

    if not isinstance(a, Array):
        a = Array(a)
    if not isinstance(b, Array):
        b = Array(b)
    
    return a.dot(b)

def broadcast_to(array: Union[Array, List, Tuple], shape: Tuple[int, ...]) -> Array:
 
    if not isinstance(array, Array):
        array = Array(array)
    
    if array.shape == shape:
        return array.copy()
    
    result_data = []
    
    if len(shape) == 1:
        if len(array.shape) == 1:
            if array.shape[0] == 1:
                result_data = [array.data[0]] * shape[0]
            else:
                result_data = array.data.copy()
        else:
            raise ValueError
    
    elif len(shape) == 2:
        rows, cols = shape
        if len(array.shape) == 1:
            if array.shape[0] == 1:
                result_data = [[array.data[0]] * cols for _ in range(rows)]
            elif array.shape[0] == cols:
                result_data = [array.data.copy() for _ in range(rows)]
            else:
                raise ValueError
        elif len(array.shape) == 2:
            if array.shape == (1, 1):
                result_data = [[array.data[0][0]] * cols for _ in range(rows)]
            elif array.shape[0] == 1 and array.shape[1] == cols:
                result_data = [array.data[0].copy() for _ in range(rows)]
            elif array.shape[0] == rows and array.shape[1] == 1:
                result_data = [[array.data[i][0]] * cols for i in range(rows)]
            else:
                result_data = array.data.copy()
        else:
            raise ValueError
    
    elif len(shape) == 3:
        d0, d1, d2 = shape
        if len(array.shape) == 1:
            if array.shape[0] == 1:
                result_data = [[[array.data[0]] * d2 for _ in range(d1)] for _ in range(d0)]
            elif array.shape[0] == d2:
                result_data = [[[array.data[k] for k in range(d2)] for _ in range(d1)] for _ in range(d0)]
            else:
                raise ValueError
        elif len(array.shape) == 2:
            if array.shape == (1, 1):
                result_data = [[[array.data[0][0]] * d2 for _ in range(d1)] for _ in range(d0)]
            elif array.shape[0] == d0 and array.shape[1] == 1:
                result_data = [[[array.data[i][0]] * d2 for _ in range(d1)] for i in range(d0)]
            elif array.shape[0] == 1 and array.shape[1] == d2:
                result_data = [[[array.data[0][k] for k in range(d2)] for _ in range(d1)] for _ in range(d0)]
            elif array.shape[0] == d1 and array.shape[1] == d2:
                result_data = [[array.data[j] for j in range(d1)] for _ in range(d0)]
            else:
                raise ValueError
        elif len(array.shape) == 3:
            if array.shape[0] == d0 and array.shape[1] == 1 and array.shape[2] == 1:
                result_data = [[[array.data[i][0][0]] * d2 for _ in range(d1)] for i in range(d0)]
            elif array.shape[0] == 1 and array.shape[1] == d1 and array.shape[2] == 1:
                result_data = [[[array.data[0][j][0]] * d2 for j in range(d1)] for _ in range(d0)]
            elif array.shape[0] == 1 and array.shape[1] == 1 and array.shape[2] == d2:
                result_data = [[[array.data[0][0][k] for k in range(d2)] for _ in range(d1)] for _ in range(d0)]
            elif array.shape[0] == d0 and array.shape[1] == d1 and array.shape[2] == 1:
                result_data = [[[array.data[i][j][0]] * d2 for j in range(d1)] for i in range(d0)]
            elif array.shape[0] == d0 and array.shape[1] == 1 and array.shape[2] == d2:
                result_data = [[[array.data[i][0][k] for k in range(d2)] for _ in range(d1)] for i in range(d0)]
            elif array.shape[0] == 1 and array.shape[1] == d1 and array.shape[2] == d2:
                result_data = [[array.data[0][j] for j in range(d1)] for _ in range(d0)]
            elif array.shape == shape:
                result_data = array.data
            else:
                raise ValueError
        else:
            raise ValueError
    
    else:

        def broadcast_recursive(arr_shape, target_shape, data):
            if len(arr_shape) == 0:
                if len(target_shape) == 0:
                    return data
                else:
                    result = data
                    for dim_size in reversed(target_shape):
                        result = [result] * dim_size
                    return result
            elif len(arr_shape) == 1:
                if arr_shape[0] == 1:
                    result = data[0]
                    for dim_size in reversed(target_shape):
                        result = [result] * dim_size
                    return result
                elif arr_shape[0] == target_shape[-1]:
                    result = data
                    for dim_size in reversed(target_shape[:-1]):
                        result = [result] * dim_size
                    return result
                else:
                    raise ValueError
            else:
                if arr_shape[0] == 1:
                    inner_result = broadcast_recursive(arr_shape[1:], target_shape[1:], data[0])
                    return [inner_result] * target_shape[0]
                elif arr_shape[0] == target_shape[0]:
                    result = []
                    for i in range(arr_shape[0]):
                        inner_result = broadcast_recursive(arr_shape[1:], target_shape[1:], data[i])
                        result.append(inner_result)
                    return result
                else:
                    raise ValueError
        try:
            result_data = broadcast_recursive(array.shape, shape, array.data)
        except Exception as e:
            raise ValueError
    return Array(result_data)

def expand_dims(array: Union[Array, List, Tuple], axis: int) -> Array:
  
    if not isinstance(array, Array):
        array = Array(array)
    
    if axis < 0:
        axis = len(array.shape) + axis + 1
    

    new_shape = list(array.shape)
    new_shape.insert(axis, 1)
    
    result = array.copy()
    result.shape = tuple(new_shape)
    
    if axis == 0 and len(array.shape) == 1:
        result.data = [array.data]
    elif axis == 1 and len(array.shape) == 1:
        result.data = [[x] for x in array.data]
    elif len(array.shape) == 2 and axis == 0:
        result.data = [array.data]
    elif len(array.shape) == 2 and axis == 1:
        result.data = [[row] for row in array.data]
    elif len(array.shape) == 2 and axis == 2:
        result.data = [[[x] for x in row] for row in array.data]
    
    return result

def power(base: Union[Array, float, List[float]], exponent: Union[Array, float, List[float]]) -> Array:

    if not isinstance(base, Array):
        base = Array(base)
    
    if isinstance(exponent, (int, float)):
        try:
            if isinstance(base.data[0], list):
                def power_recursive(data):
                    if isinstance(data[0], list):
                        return [power_recursive(row) for row in data]
                    else:
                        result = []
                        for x in data:
                            try:
                                if x == 0 and exponent < 0:
                                    result.append(float('inf'))
                                elif x < 0 and not isinstance(exponent, int) and exponent != int(exponent):
                                    result.append(abs(x) ** exponent)
                                else:
                                    result.append(x ** exponent)
                            except (OverflowError, ZeroDivisionError, ValueError):
                                if x == 0:
                                    result.append(0.0 if exponent > 0 else float('inf'))
                                elif abs(x) > 1 and exponent > 100:
                                    result.append(float('inf') if x > 0 else float('-inf'))
                                elif abs(x) < 1 and exponent < -100:
                                    result.append(float('inf'))
                                else:
                                    result.append(1.0)  
                        return result
                result_data = power_recursive(base.data)
            else:
                result_data = []
                for x in base.data:
                    try:
                        if x == 0 and exponent < 0:
                            result_data.append(float('inf'))
                        elif x < 0 and not isinstance(exponent, int) and exponent != int(exponent):
                            result_data.append(abs(x) ** exponent)
                        else:
                            result_data.append(x ** exponent)
                    except (OverflowError, ZeroDivisionError, ValueError):
                        if x == 0:
                            result_data.append(0.0 if exponent > 0 else float('inf'))
                        elif abs(x) > 1 and exponent > 100:
                            result_data.append(float('inf') if x > 0 else float('-inf'))
                        elif abs(x) < 1 and exponent < -100:
                            result_data.append(float('inf'))
                        else:
                            result_data.append(1.0) 
            
            result = Array(result_data, dtype=base.dtype)
            return result
        except Exception as e:
            pass
           
    
    elif isinstance(exponent, Array):
        
        try:
            if isinstance(base.data[0], list) and isinstance(exponent.data[0], list):
                result_data = []
                for base_row, exp_row in zip(base.data, exponent.data):
                    result_row = []
                    for b, e in zip(base_row, exp_row):
                        try:
                            if b == 0 and e < 0:
                                result_row.append(float('inf'))
                            elif b < 0 and not isinstance(e, int) and e != int(e):
                                result_row.append(abs(b) ** e)
                            else:
                                result_row.append(b ** e)
                        except (OverflowError, ZeroDivisionError, ValueError):
                            if b == 0:
                                result_row.append(0.0 if e > 0 else float('inf'))
                            elif abs(b) > 1 and e > 100:
                                result_row.append(float('inf') if b > 0 else float('-inf'))
                            elif abs(b) < 1 and e < -100:
                                result_row.append(float('inf'))
                            else:
                                result_row.append(1.0)
                    result_data.append(result_row)
            else:
                result_data = []
                for b, e in zip(base.data, exponent.data):
                    try:
                        if b == 0 and e < 0:
                            result_data.append(float('inf'))
                        elif b < 0 and not isinstance(e, int) and e != int(e):
                            result_data.append(abs(b) ** e)
                        else:
                            result_data.append(b ** e)
                    except (OverflowError, ZeroDivisionError, ValueError):
                        if b == 0:
                            result_data.append(0.0 if e > 0 else float('inf'))
                        elif abs(b) > 1 and e > 100:
                            result_data.append(float('inf') if b > 0 else float('-inf'))
                        elif abs(b) < 1 and e < -100:
                            result_data.append(float('inf'))
                        else:
                            result_data.append(1.0)
            
            result = Array(result_data, dtype=base.dtype)
            return result
        except Exception as e:
            pass
    
    else:
        exponent = Array(exponent)
        return power(base, exponent)

def perfect_nan_to_num(x: Union[Any, float, List[float]], nan: float = 0.0, posinf: float = None, neginf: float = None):
  
    if posinf is None:
        posinf = 1e38
    if neginf is None:
        neginf = -1e38
    

    
    def process_single_value(value):
      
        if not isinstance(value, (int, float)):
            return value
            
        return value
    
    def process_recursive(data):
 
        if isinstance(data, list):
            return [process_recursive(item) for item in data]
        elif isinstance(data, tuple):
            return tuple(process_recursive(item) for item in data)
        else:
            return process_single_value(data)
    
    if isinstance(x, (int, float)):
        return process_single_value(x)
    
    if hasattr(x, 'data'):
        processed_data = process_recursive(x.data)
        if hasattr(x, '__class__'):
            try:
                return x.__class__(processed_data)
            except:
                return processed_data
        else:
            return processed_data
    
    if isinstance(x, (list, tuple)):
        return process_recursive(x)
    
    if hasattr(x, 'shape') and hasattr(x, 'dtype'):
        if hasattr(x, 'tolist'):
            return process_recursive(x.tolist())
        else:
            return process_recursive(x)
    
    return process_single_value(x)

def nan_to_num(x: Union[Array, float, List[float]], nan: float = 0.0, posinf: float = None, neginf: float = None) -> Array:

    if posinf is None:
        posinf = 1e38
    if neginf is None:
        neginf = -1e38
        
    if isinstance(x, (int, float)):
        if math.isnan(x):
            return array([nan])
        elif math.isinf(x):
            if x > 0:
                return array([posinf])
            else:
                return array([neginf])
        else:
            return array([x])
    
    if hasattr(x, 'shape') and hasattr(x, 'dtype'):
        try:
            if hasattr(x, 'tolist'):
                x_data = x.tolist()
                result_data = perfect_nan_to_num(x_data, nan=nan, posinf=posinf, neginf=neginf)
                return array(result_data)
            else:
                x_data = x.data if hasattr(x, 'data') else x
                result_data = perfect_nan_to_num(x_data, nan=nan, posinf=posinf, neginf=neginf)
                return array(result_data)
        except Exception as e:
            pass
    
    if isinstance(x, list):
        x = array(x)
    
    if isinstance(x, Array):
        def nan_to_num_recursive(data):
            if isinstance(data, list):
                return [nan_to_num_recursive(item) for item in data]
            else:
                if math.isnan(data):
                    return nan
                elif math.isinf(data):
                    if data > 0:
                        return posinf
                    else:
                        return neginf
                else:
                    return data
        
        result_data = nan_to_num_recursive(x.data)
        return array(result_data)
    
    raise TypeError

def prod(x: Union[Array, List[float]], axis=None) -> Union[Array, float]:

    if not isinstance(x, Array):
        x = Array(x)
    
    if axis is None:
        def prod_recursive(data):
            if isinstance(data[0], list):
                result = 1
                for row in data:
                    result *= prod_recursive(row)
                return result
            else:
                result = 1
                for val in data:
                    result *= val
                return result
        
        return prod_recursive(x.data)
    else:
      
        if isinstance(x.data[0], list):
            if axis == 0:
                result = []
                for col in range(len(x.data[0])):
                    prod_val = 1
                    for row in range(len(x.data)):
                        prod_val *= x.data[row][col]
                    result.append(prod_val)
                return Array(result)
            elif axis == 1:
                result = []
                for row in x.data:
                    prod_val = 1
                    for val in row:
                        prod_val *= val
                    result.append(prod_val)
                return Array(result)
        else:
            result = 1
            for val in x.data:
                result *= val
            return result

def all(x: Union[Array, List[bool]]) -> bool:

    if not isinstance(x, Array):
        x = Array(x)
    
    def all_recursive(data):
        if isinstance(data[0], list):
            for row in data:
                if not all_recursive(row):
                    return False
            return True
        else:
            for val in data:
                if not val:
                    return False
            return True
    
    return all_recursive(x.data)


def round_array(x: Union[Array, float, List[float]], decimals: int = 0) -> Array:
   
    from .A27_tools import round
    
    if isinstance(x, (int, float)):
        return Array([round(x, decimals)])
    
    if not isinstance(x, Array):
        x = Array(x)
    
    def round_recursive(data):
        if isinstance(data[0], list):
            return [round_recursive(row) for row in data]
        else:
            return [round(val, decimals) for val in data]
    
    result_data = round_recursive(x.data)
    return Array(result_data, dtype=x.dtype)

def isclose(a: Union[Array, float, List[float]], b: Union[Array, float, List[float]], 
           rtol: float = 1e-05, atol: float = 1e-08) -> Array:
  
    if not isinstance(a, Array):
        a = Array(a)
    if not isinstance(b, Array):
        b = Array(b)
    
    def isclose_recursive(data_a, data_b):
        if isinstance(data_a[0], list):
            return [isclose_recursive(row_a, row_b) for row_a, row_b in zip(data_a, data_b)]
        else:
            result = []
            for val_a, val_b in zip(data_a, data_b):
                diff = __builtins__['abs'](val_a - val_b)
                tolerance = atol + rtol * __builtins__['abs'](val_b)
                result.append(diff <= tolerance)
            return result
    
    result_data = isclose_recursive(a.data, b.data)
    return Array(result_data)

def allclose(a: Union[Array, float, List[float]], b: Union[Array, float, List[float]], 
            rtol: float = 1e-05, atol: float = 1e-08) -> bool:

    if not isinstance(a, Array):
        a = Array(a)
    if not isinstance(b, Array):
        b = Array(b)
    
    if a.shape != b.shape:
        return False
    
    def allclose_recursive(data_a, data_b):
        if isinstance(data_a, list):
            if len(data_a) != len(data_b):
                return False
            for item_a, item_b in zip(data_a, data_b):
                if not allclose_recursive(item_a, item_b):
                    return False
            return True
        else:
            diff = __builtins__['abs'](data_a - data_b)
            tolerance = atol + rtol * __builtins__['abs'](data_b)
            return diff <= tolerance
    
    return allclose_recursive(a.data, b.data)

def resize(array: Union[Array, List[float]], new_shape: Union[int, Tuple[int, ...]]) -> Array:

    if not isinstance(array, Array):
        array = Array(array)
    
    if isinstance(new_shape, int):
        new_shape = (new_shape,)
    
    new_size = 1
    for dim in new_shape:
        new_size *= dim
    
    flat_data = []
    def flatten_recursive(data):
        if isinstance(data, list):
            for item in data:
                flatten_recursive(item)
        else:
            flat_data.append(data)
    
    flatten_recursive(array.data)
    
    if new_size > len(flat_data):
        result_data = []
        for i in range(new_size):
            result_data.append(flat_data[i % len(flat_data)])
    else:
        result_data = flat_data[:new_size]
    
    result = Array(result_data)
    if len(new_shape) > 1:
        result = result.reshape(*new_shape)
    
    return result

def full_like(array: Union[Array, List[float]], fill_value: float, dtype: Optional[type] = None) -> Array:

    if not isinstance(array, Array):
        array = Array(array)
    
    total_size = 1
    for dim in array.shape:
        total_size *= dim
    
    data = [fill_value] * total_size
    result = Array(data, dtype=dtype or array.dtype)
    
    if len(array.shape) > 1:
        result = result.reshape(*array.shape)
    
    return result

def empty_like(array: Union[Array, List[float]], dtype: Optional[type] = None) -> Array:
 
    return zeros_like(array, dtype=dtype)

def argsort(array: Union[Array, List[float]], axis: int = -1) -> Array:
 
    if not isinstance(array, Array):
        array = Array(array)
    
    if axis == -1:
        axis = len(array.shape) - 1
    
    if len(array.shape) == 1:
        indexed_data = [(i, val) for i, val in enumerate(array.data)]
        indexed_data.sort(key=lambda x: x[1])
        indices = [x[0] for x in indexed_data]
        return Array(indices)
    else:
     
        if isinstance(array.data[0], list):
            if axis == 0:
                result = []
                for col in range(len(array.data[0])):
                    column_data = [(i, array.data[i][col]) for i in range(len(array.data))]
                    column_data.sort(key=lambda x: x[1])
                    indices = [x[0] for x in column_data]
                    result.append(indices)
                transposed = [[result[j][i] for j in range(len(result))] for i in range(len(result[0]))]
                return Array(transposed)
            else:
                result = []
                for row in array.data:
                    indexed_row = [(i, val) for i, val in enumerate(row)]
                    indexed_row.sort(key=lambda x: x[1])
                    indices = [x[0] for x in indexed_row]
                    result.append(indices)
                return Array(result)
        else:
            indexed_data = [(i, val) for i, val in enumerate(array.data)]
            indexed_data.sort(key=lambda x: x[1])
            indices = [x[0] for x in indexed_data]
            return Array(indices)

def clip(x: Union[Array, float, List[float]], min_val: float, max_val: float) -> Array:
  
    if isinstance(x, (int, float)):
        clipped_val = __builtins__['max'](min_val, __builtins__['min'](x, max_val))
        return Array([clipped_val])
    
    if not isinstance(x, Array):
        x = Array(x)
    
    return x.clip(min_val, max_val)

def logical_and(a: Union[Array, float, List[float]], b: Union[Array, float, List[float]]) -> Array:
    
    if not isinstance(a, Array):
        a = Array(a)
    if not isinstance(b, Array):
        b = Array(b)
    
    if isinstance(a.data[0], list) and isinstance(b.data[0], list):
        result_data = []
        for row_a, row_b in zip(a.data, b.data):
            result_row = [bool(val_a) and bool(val_b) for val_a, val_b in zip(row_a, row_b)]
            result_data.append(result_row)
    elif not isinstance(a.data[0], list) and not isinstance(b.data[0], list):
        result_data = [bool(val_a) and bool(val_b) for val_a, val_b in zip(a.data, b.data)]
    else:
        raise ValueError
    
    return Array(result_data)

def split(array: Union[Array, List, Tuple], indices_or_sections: Union[int, List[int]], axis: int = 0) -> List[Array]:
  
    if not isinstance(array, Array):
        array = Array(array)
    
    if axis < 0:
        axis = len(array.shape) + axis
    
    if axis >= len(array.shape):
        raise ValueError
    
    axis_size = array.shape[axis]
    
    if isinstance(indices_or_sections, int):
        sections = indices_or_sections
        if axis_size % sections != 0:
            raise ValueError
        
        section_size = axis_size // sections
        split_indices = [i * section_size for i in range(1, sections)]
    else:
        split_indices = list(indices_or_sections)
    
    all_indices = [0] + split_indices + [axis_size]
    
    result = []
    
    if len(array.shape) == 1:
        for i in range(len(all_indices) - 1):
            start = all_indices[i]
            end = all_indices[i + 1]
            result.append(Array(array.data[start:end]))
    
    elif len(array.shape) == 2:
        if axis == 0:
            for i in range(len(all_indices) - 1):
                start = all_indices[i]
                end = all_indices[i + 1]
                result.append(Array(array.data[start:end]))
        else:
            for i in range(len(all_indices) - 1):
                start = all_indices[i]
                end = all_indices[i + 1]
                split_data = []
                for row in array.data:
                    split_data.append(row[start:end])
                result.append(Array(split_data))
    
    elif len(array.shape) == 3:
        if axis == 0:
            for i in range(len(all_indices) - 1):
                start = all_indices[i]
                end = all_indices[i + 1]
                result.append(Array(array.data[start:end]))
        elif axis == 1:
            for i in range(len(all_indices) - 1):
                start = all_indices[i]
                end = all_indices[i + 1]
                split_data = []
                for layer in array.data:
                    split_data.append(layer[start:end])
                result.append(Array(split_data))
        else:
            for i in range(len(all_indices) - 1):
                start = all_indices[i]
                end = all_indices[i + 1]
                split_data = []
                for layer in array.data:
                    layer_data = []
                    for row in layer:
                        layer_data.append(row[start:end])
                    split_data.append(layer_data)
                result.append(Array(split_data))
    
    else:
        raise NotImplementedError
    
    return result

def abs(x: Union[Array, float, List[float]]) -> Array:

    if isinstance(x, (int, float)):
        return Array([__builtins__['abs'](x)])
    
    if isinstance(x, Array):
        return x.abs()
    
    x = Array(x)
    return x.abs()

def sign(x: Union[Array, float, List[float]]) -> Array:
  
    if isinstance(x, (int, float)):
        if x > 0:
            return Array([1.0])
        elif x < 0:
            return Array([-1.0])
        else:
            return Array([0.0])
    
    if not isinstance(x, Array):
        x = Array(x)
    
    def sign_recursive(data):
        if isinstance(data, list):
            return [sign_recursive(item) for item in data]
        else:
            if data > 0:
                return 1.0
            elif data < 0:
                return -1.0
            else:
                return 0.0
    
    result_data = sign_recursive(x.data)
    return Array(result_data, dtype=x.dtype)


def reshape(array: Union[Array, List, Tuple], shape: Union[int, Tuple[int, ...]]) -> Array:
   
    if not isinstance(array, Array):
        array = Array(array)
    
    try:
        return array.reshape(*shape if isinstance(shape, tuple) else (shape,))
    except (ValueError, TypeError) as e:
        try:
            if hasattr(array, 'data'):
                flat_data = array.flatten().data if hasattr(array, 'flatten') else array.data
            else:
                flat_data = array
            
            if not isinstance(flat_data, list):
                flat_data = list(flat_data)
            
            if isinstance(shape, tuple):
                total_elements = 1
                for dim in shape:
                    total_elements *= dim
                new_shape = shape
            else:
                total_elements = shape
                new_shape = (shape,)
            
            result = Array(flat_data)
            result.shape = new_shape
            return result
        except Exception as fallback_error:
            raise e

def transpose(array: Union[Array, List, Tuple], axes: Optional[Tuple[int, ...]] = None) -> Array:

    if not isinstance(array, Array):
        array = Array(array)
    
    if axes is None:
        if len(array.shape) == 1:
            return array  
        elif len(array.shape) == 2:
            return array.transpose()  
        else:
            axes = tuple(range(len(array.shape) - 1, -1, -1))

    return _transpose_with_axes(array, axes)

def _transpose_with_axes(array: Array, axes: Tuple[int, ...]) -> Array:
    
    new_shape = tuple(array.shape[axis] for axis in axes)
    
    result_data = _create_nested_list(new_shape)
    
    _fill_transposed_data(array.data, result_data, array.shape, new_shape, axes)
    
    return Array(result_data)

def _create_nested_list(shape: Tuple[int, ...]):
    if len(shape) == 1:
        return [0.0] * shape[0]
    elif len(shape) == 2:
        return [[0.0 for _ in range(shape[1])] for _ in range(shape[0])]
    elif len(shape) == 3:
        return [[[0.0 for _ in range(shape[2])] for _ in range(shape[1])] for _ in range(shape[0])]
    elif len(shape) == 4:
        return [[[[0.0 for _ in range(shape[3])] for _ in range(shape[2])] 
                 for _ in range(shape[1])] for _ in range(shape[0])]
    else:
        return [_create_nested_list(shape[1:]) for _ in range(shape[0])]

def _fill_transposed_data(source_data, target_data, source_shape: Tuple[int, ...], 
                         target_shape: Tuple[int, ...], axes: Tuple[int, ...]):
    
    if len(source_shape) == 2 and len(target_shape) == 2:
        rows, cols = source_shape
        for i in range(rows):
            for j in range(cols):
                if axes == (1, 0):  
                    target_data[j][i] = source_data[i][j]
                else: 
                    target_data[i][j] = source_data[i][j]
        return
    
    if len(source_shape) == 3 and len(target_shape) == 3:
        d0, d1, d2 = source_shape
        for i in range(d0):
            for j in range(d1):
                for k in range(d2):
                    new_indices = [0, 0, 0]
                    old_indices = [i, j, k]
                    for new_pos, old_pos in enumerate(axes):
                        new_indices[new_pos] = old_indices[old_pos]
                    
                    target_data[new_indices[0]][new_indices[1]][new_indices[2]] = source_data[i][j][k]
        return
    
    if len(source_shape) == 4 and len(target_shape) == 4:
        d0, d1, d2, d3 = source_shape
        for i in range(d0):
            for j in range(d1):
                for k in range(d2):
                    for l in range(d3):
                        new_indices = [0, 0, 0, 0]
                        old_indices = [i, j, k, l]
                        for new_pos, old_pos in enumerate(axes):
                            new_indices[new_pos] = old_indices[old_pos]
                        
                        target_data[new_indices[0]][new_indices[1]][new_indices[2]][new_indices[3]] = source_data[i][j][k][l]
        return
    
    if len(source_shape) > 4:
        _fill_transposed_data_recursive(source_data, target_data, source_shape, axes, [])
        return
    
    raise NotImplementedError

def _fill_transposed_data_recursive(source_data, target_data, source_shape: Tuple[int, ...], 
                                   axes: Tuple[int, ...], current_indices: List[int]):
    
    if len(current_indices) == len(source_shape):
  
        new_indices = [0] * len(source_shape)
        for new_pos, old_pos in enumerate(axes):
            new_indices[new_pos] = current_indices[old_pos]
        
        src_value = source_data
        for idx in current_indices:
            src_value = src_value[idx]
        
        target_ref = target_data
        for i, idx in enumerate(new_indices[:-1]):
            target_ref = target_ref[idx]
        target_ref[new_indices[-1]] = src_value
        return
    
    current_dim = len(current_indices)
    for i in range(source_shape[current_dim]):
        _fill_transposed_data_recursive(source_data, target_data, source_shape, axes, 
                                       current_indices + [i])

def pad(array: Union[Array, List, Tuple], pad_width, mode: str = 'constant', constant_values: float = 0.0) -> Array:

    if not isinstance(array, Array):
        array = Array(array)
 
    new_shape = []
    for i, (before, after) in enumerate(pad_width):
        new_shape.append(array.shape[i] + before + after)
    new_shape = tuple(new_shape)
    
    if len(array.shape) == 1:
        return _pad_1d(array, pad_width, constant_values)
    elif len(array.shape) == 2:
        return _pad_2d(array, pad_width, constant_values)
    elif len(array.shape) == 3:
        return _pad_3d(array, pad_width, constant_values)
    elif len(array.shape) == 4:
        return _pad_4d(array, pad_width, constant_values)
    else:
        raise NotImplementedError

def _pad_1d(array: Array, pad_width, constant_values: float) -> Array:
    before, after = pad_width[0]
    
    new_data = [constant_values] * before + array.data + [constant_values] * after
    return Array(new_data)

def _pad_2d(array: Array, pad_width, constant_values: float) -> Array:
    (before_0, after_0), (before_1, after_1) = pad_width
    rows, cols = array.shape
    
    new_cols = cols + before_1 + after_1
    
    new_data = []
    
    for _ in range(before_0):
        new_data.append([constant_values] * new_cols)
    
    for i in range(rows):
        row = ([constant_values] * before_1 + 
               array.data[i] + 
               [constant_values] * after_1)
        new_data.append(row)
    
    for _ in range(after_0):
        new_data.append([constant_values] * new_cols)
    
    return Array(new_data)

def _pad_3d(array: Array, pad_width, constant_values: float) -> Array:
    (before_0, after_0), (before_1, after_1), (before_2, after_2) = pad_width
    d0, d1, d2 = array.shape
    
    new_d1 = d1 + before_1 + after_1
    new_d2 = d2 + before_2 + after_2
    
    new_data = []
    
    for _ in range(before_0):
        layer = []
        for _ in range(new_d1):
            layer.append([constant_values] * new_d2)
        new_data.append(layer)
    
    for i in range(d0):
        layer = []
        
        for _ in range(before_1):
            layer.append([constant_values] * new_d2)
        
        for j in range(d1):
            row = ([constant_values] * before_2 + 
                   array.data[i][j] + 
                   [constant_values] * after_2)
            layer.append(row)
        
        for _ in range(after_1):
            layer.append([constant_values] * new_d2)
        
        new_data.append(layer)
    
    for _ in range(after_0):
        layer = []
        for _ in range(new_d1):
            layer.append([constant_values] * new_d2)
        new_data.append(layer)
    
    return Array(new_data)

def _pad_4d(array: Array, pad_width, constant_values: float) -> Array:
    (before_0, after_0), (before_1, after_1), (before_2, after_2), (before_3, after_3) = pad_width
    d0, d1, d2, d3 = array.shape
    
    new_d1 = d1 + before_1 + after_1
    new_d2 = d2 + before_2 + after_2
    new_d3 = d3 + before_3 + after_3
    
    new_data = []
    
    for _ in range(before_0):
        batch = []
        for _ in range(new_d1):
            layer = []
            for _ in range(new_d2):
                layer.append([constant_values] * new_d3)
            batch.append(layer)
        new_data.append(batch)
    
    for i in range(d0):
        batch = []
        
        for _ in range(before_1):
            layer = []
            for _ in range(new_d2):
                layer.append([constant_values] * new_d3)
            batch.append(layer)
        
        for j in range(d1):
            layer = []
            
            for _ in range(before_2):
                layer.append([constant_values] * new_d3)
            
            for k in range(d2):
                row = ([constant_values] * before_3 + 
                       array.data[i][j][k] + 
                       [constant_values] * after_3)
                layer.append(row)
            
            for _ in range(after_2):
                layer.append([constant_values] * new_d3)
            
            batch.append(layer)
        
        for _ in range(after_1):
            layer = []
            for _ in range(new_d2):
                layer.append([constant_values] * new_d3)
            batch.append(layer)
        
        new_data.append(batch)
    
    for _ in range(after_0):
        batch = []
        for _ in range(new_d1):
            layer = []
            for _ in range(new_d2):
                layer.append([constant_values] * new_d3)
            batch.append(layer)
        new_data.append(batch)
    
    return Array(new_data)

def log1p(array: Union[Array, List, Tuple]) -> Array:
   
    if not isinstance(array, Array):
        array = Array(array)
    
    result_data = _log1p_recursive(array.data)
    return Array(result_data)

def _log1p_recursive(data):
    if isinstance(data, list):
        return [_log1p_recursive(item) for item in data]
    elif isinstance(data, Array):
        return _log1p_recursive(data.data)
    else:
        try:
            return _log1p_scalar(float(data))
        except (TypeError, ValueError):
            if hasattr(data, 'data'):
                return _log1p_recursive(data.data)
            else:
                return _log1p_scalar(0.0) 

def _log1p_scalar(x) -> float:

    from . import A20_math as math
    
    if isinstance(x, Array):
        return _log1p_recursive(x.data)
    
    try:
        x = float(x)
    except (TypeError, ValueError):
        if hasattr(x, 'data'):
            return _log1p_recursive(x.data)
        else:
            return 0.0
    
    if x < -1.0:
        return float('-inf')
    elif x == -1.0:
        return float('-inf')
    elif __builtins__['abs'](x) < 1e-8: 
     
        return x - x*x/2.0 + x*x*x/3.0
    elif x < 0.5:
        return math.log(1.0 + x)
    else:
        return math.log(1.0 + x)

def int32(x: Union[Array, float, int, List]) -> Array:
 
    if not isinstance(x, Array):
        x = Array(x)
    
    result_data = _int_convert_recursive(x.data, 'int32')
    result = Array(result_data)
    result.dtype = int
    return result

def int64(x: Union[Array, float, int, List]) -> Array:
 
    if not isinstance(x, Array):
        x = Array(x)
    
    result_data = _int_convert_recursive(x.data, 'int64')
    result = Array(result_data)
    result.dtype = int
    return result

def _int_convert_recursive(data, dtype_name):
    if isinstance(data, list):
        return [_int_convert_recursive(item, dtype_name) for item in data]
    elif isinstance(data, Array):
        return _int_convert_recursive(data.data, dtype_name)
    else:
        try:
            return int(float(data))
        except (TypeError, ValueError):
            if hasattr(data, 'data'):
                return _int_convert_recursive(data.data, dtype_name)
            else:
                return 0  

def vstack(arrays_list: List[Array]) -> Array:
  
    if not arrays_list:
        raise ValueError
    
    arrays_list = [Array(arr) if not isinstance(arr, Array) else arr for arr in arrays_list]
    
    first_shape = arrays_list[0].shape

    if len(first_shape) == 1:
        result_data = []
        for arr in arrays_list:
            result_data.extend(arr.data)
        return Array(result_data)
    else:
        result_data = []
        for arr in arrays_list:
            result_data.extend(arr.data)
        return Array(result_data)

def ndindex(*shape: int):

    if len(shape) == 0:
        yield ()
        return
    
    if len(shape) == 1:
        for i in range(shape[0]):
            yield (i,)
        return
    
    def _generate_indices(dims):
        if len(dims) == 1:
            for i in range(dims[0]):
                yield [i]
        else:
            for i in range(dims[0]):
                for rest in _generate_indices(dims[1:]):
                    yield [i] + rest
    
    for indices in _generate_indices(shape):
        yield tuple(indices)


def asarray_numpy_compatible(data, dtype=None):
    if hasattr(data, '__array__'):
        try:
            from .A11_final_asarray import ult_asarray
            great_data = ult_asarray(data, dtype=dtype)
            result = Array([0])  
            result.data = great_data
            result.shape = great_data.shape
            result.dtype = dtype or great_data.dtype
            return result
        except Exception as e:
            pass
    
    if isinstance(data, memoryview):
        try:
            from .A11_final_asarray import ult_asarray
            great_data = ult_asarray(data, dtype=dtype)
            result = Array([0])
            result.data = great_data
            result.shape = great_data.shape
            result.dtype = dtype or great_data.dtype
            return result
        except Exception as e:
            return asarray(data, dtype=dtype)
    
    standard_result = asarray(data, dtype=dtype)
    
    if isinstance(standard_result.data, list):
         
        from . import A10_final_array as final_array
        final_array_data = final_array.perfect_array(standard_result.data, dtype=dtype or float)
        result = Array([0])  
        result.data = final_array_data
        result.shape = final_array_data.shape  
        result.dtype = dtype or final_array_data.dtype
        
        return result
    
    return standard_result

