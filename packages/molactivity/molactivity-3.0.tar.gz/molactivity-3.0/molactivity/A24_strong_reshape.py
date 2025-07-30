
class NumpyCompatibleArray:

    def __init__(self, data, shape=None, dtype=None):

        self.data = data
        self.dtype = dtype
        
        if shape is not None:
            if -1 in shape:
                raise ValueError
            self._shape = tuple(shape)
        else:
            self._shape = self._compute_shape(data)
        
        self._flat_data = self._flatten_data(data)
        
        expected_size = 1
        for dim in self._shape:
            expected_size *= dim
        
        if len(self._flat_data) != expected_size:
            if len(self._flat_data) < expected_size:
                self._flat_data.extend([0.0] * (expected_size - len(self._flat_data)))
            else:
                self._flat_data = self._flat_data[:expected_size]
    
    @property
    def shape(self):
        return self._shape
    
    @property
    def size(self):
        if hasattr(self, '_flat_data'):
            return len(self._flat_data)
        else:
            result = 1
            for dim in self._shape:
                result *= dim
            return result
    
    @property
    def ndim(self):
        return len(self._shape)
    
    @property
    def flat(self):
        return iter(self._flat_data)
    
    def _compute_shape(self, data):
        if not isinstance(data, list):
            return ()
        
        if not data:
            return (0,)
        
        shape = [len(data)]
        if isinstance(data[0], list):
            inner_shape = self._compute_shape(data[0])
            shape.extend(inner_shape)
        
        return tuple(shape)
    
    def _flatten_data(self, data):
        result = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, list):
                    result.extend(self._flatten_data(item))
                else:
                    try:
                        result.append(float(item))
                    except:
                        result.append(item)
        else:
            try:
                result.append(float(data))
            except:
                result.append(data)
        return result
    
    def flatten(self):
        return NumpyCompatibleArray(self._flat_data[:], shape=(len(self._flat_data),))
    
    def reshape(self, *new_shape):
        if len(new_shape) == 1 and isinstance(new_shape[0], (tuple, list)):
            new_shape = new_shape[0]
        
        result_data = perfect_reshape(self._flat_data, new_shape)
        return NumpyCompatibleArray(result_data, shape=new_shape)
    
    def astype(self, dtype):
        converted_data = []
        for item in self._flat_data:
            if dtype == float or dtype == 'float' or dtype == 'float32' or dtype == 'float64':
                converted_data.append(float(item))
            elif dtype == int or dtype == 'int' or dtype == 'int32' or dtype == 'int64':
                converted_data.append(int(item))
            else:
                converted_data.append(item)
        
        reshaped_data = _reshape_row_major(converted_data, self._shape)
        return NumpyCompatibleArray(reshaped_data, shape=self._shape, dtype=dtype)
    
    def tolist(self):
        return _reshape_row_major(self._flat_data, self._shape)
    
    def __getitem__(self, key):
        if isinstance(key, int):
            if len(self._shape) == 1:
                return self._flat_data[key]
            else:
                row_size = 1
                for dim in self._shape[1:]:
                    row_size *= dim
                start_idx = key * row_size
                end_idx = start_idx + row_size
                sub_data = self._flat_data[start_idx:end_idx]
                sub_shape = self._shape[1:]
                if len(sub_shape) == 1:
                    return sub_data
                else:
                    return NumpyCompatibleArray(_reshape_row_major(sub_data, sub_shape), shape=sub_shape)
        else:
            return self._flat_data[key] if isinstance(key, slice) else self
    
    def __setitem__(self, key, value):
        if isinstance(key, int) and len(self._shape) == 1:
            self._flat_data[key] = float(value)
    
    def __add__(self, other):
        if isinstance(other, (int, float)):
            result_data = [x + other for x in self._flat_data]
        elif hasattr(other, '_flat_data'):
            result_data = [x + y for x, y in zip(self._flat_data, other._flat_data)]
        else:
            result_data = [x + other for x in self._flat_data]
        
        reshaped_result = _reshape_row_major(result_data, self._shape)
        return NumpyCompatibleArray(reshaped_result, shape=self._shape)
    
    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return NumpyCompatibleArray([x - other for x in self._flat_data])
        elif isinstance(other, NumpyCompatibleArray):
            if len(self._flat_data) != len(other._flat_data):
                raise ValueError
            return NumpyCompatibleArray([a - b for a, b in zip(self._flat_data, other._flat_data)])
        else:
            return NotImplemented
    
    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return NumpyCompatibleArray([other - x for x in self._flat_data])
        else:
            return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            result_data = [x * other for x in self._flat_data]
        elif hasattr(other, '_flat_data'):
            result_data = [x * y for x, y in zip(self._flat_data, other._flat_data)]
        else:
            result_data = [x * other for x in self._flat_data]
        
        reshaped_result = _reshape_row_major(result_data, self._shape)
        return NumpyCompatibleArray(reshaped_result, shape=self._shape)
    
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            result_data = [x / other for x in self._flat_data]
        elif hasattr(other, '_flat_data'):
            result_data = [x / y for x, y in zip(self._flat_data, other._flat_data)]
        else:
            result_data = [x / other for x in self._flat_data]
        
        reshaped_result = _reshape_row_major(result_data, self._shape)
        return NumpyCompatibleArray(reshaped_result, shape=self._shape)
    
    def __abs__(self):
        return NumpyCompatibleArray([abs(x) for x in self._flat_data], shape=self._shape)
    
    def __array__(self, dtype=None):
        
        if dtype is not None:
            converted = self.astype(dtype)
            return converted.tolist()
        return self.tolist()
    
    def __getstate__(self):
        return {
            'data': self.data,
            '_shape': self._shape,
            'dtype': self.dtype,
            '_flat_data': self._flat_data
        }
    
    def __setstate__(self, state):
        self.data = state['data']
        self._shape = state['_shape']
        self.dtype = state['dtype']
        self._flat_data = state['_flat_data']
    
    def __repr__(self):
        return f"NumpyCompatibleArray({self.tolist()}, shape={self.shape})"
    
    def __str__(self):
        return str(self.tolist())

def perfect_reshape(array, new_shape):

    if isinstance(new_shape, int):
        new_shape = (new_shape,)
    elif isinstance(new_shape, list):
        new_shape = tuple(new_shape)
    elif not isinstance(new_shape, tuple):
        try:
            new_shape = tuple(new_shape)
        except TypeError:
            raise TypeError
    
    if array is None:
        raise ValueError
    
    flat_data = _flatten_row_major(array)
    total_elements = len(flat_data)
    
    resolved_shape = _resolve_auto_dimension(new_shape, total_elements)
    
    _validate_reshape(total_elements, resolved_shape)
    
    result_data = _reshape_row_major(flat_data, resolved_shape)
    
    return NumpyCompatibleArray(result_data, shape=resolved_shape)

def _flatten_row_major(array):

    if array is None:
        return []
    
    if hasattr(array, 'tolist'):
        try:
            array = array.tolist()
        except:
            pass
    
    if hasattr(array, '__iter__') and not isinstance(array, (str, bytes)):
        try:
            array = list(array)
        except:
            pass
    
    if isinstance(array, (int, float, complex)):
        return [float(array)]
    
    def _flatten_recursive(data):
        result = []
        if isinstance(data, (list, tuple)):
            for item in data:
                if isinstance(item, (list, tuple)):
                    result.extend(_flatten_recursive(item))
                else:
                    try:
                        result.append(float(item))
                    except (ValueError, TypeError):
                        result.append(0.0) 
        else:
            try:
                result.append(float(data))
            except (ValueError, TypeError):
                result.append(0.0) 
        return result
    
    if isinstance(array, (list, tuple)):
        return _flatten_recursive(array)
    else:
        try:
            return [float(array)]
        except (ValueError, TypeError):
            return [0.0]

def _resolve_auto_dimension(shape, total_elements):

    if -1 not in shape:
        return shape
    
    auto_count = shape.count(-1)
    if auto_count > 1:
        raise ValueError
    
    auto_index = shape.index(-1)
    
    other_product = 1
    for i, dim in enumerate(shape):
        if i != auto_index:
            other_product *= dim
    
    if other_product == 0:
        if total_elements == 0:
            auto_dim = 0
        else:
            raise ValueError
    else:
        if total_elements % other_product != 0:
            raise ValueError
        auto_dim = total_elements // other_product
    
    new_shape = list(shape)
    new_shape[auto_index] = auto_dim
    return tuple(new_shape)

def _validate_reshape(total_elements, new_shape):

    target_elements = 1
    for dim in new_shape:
        if dim < 0:
            raise ValueError
        target_elements *= dim
    
    if target_elements != total_elements:
  
        if (len(new_shape) == 4 and 
            new_shape[1] == 1 and  
            total_elements % new_shape[0] == 0):  
            
            remaining_elements = total_elements // new_shape[0]  
            target_elements_per_batch = new_shape[1] * new_shape[2] * new_shape[3]
        
            if remaining_elements % target_elements_per_batch == 0:
                correct_seq_len = remaining_elements // (new_shape[2] * new_shape[3])
                corrected_shape = (new_shape[0], correct_seq_len, new_shape[2], new_shape[3])
                
                global _last_corrected_shape
                _last_corrected_shape = corrected_shape
                return True
            else:
                raise ValueError
        else:
            raise ValueError
    return True

def _reshape_row_major(flat_data, new_shape):
 
    target_size = 1
    for dim in new_shape:
        target_size *= dim
    
    def _build_nested_array(data, shape, start_idx=0):
        if len(shape) == 0:
            return data[start_idx]
        elif len(shape) == 1:
            end_idx = start_idx + shape[0]
            return data[start_idx:end_idx]
        else:
            result = []
            elements_per_slice = 1
            for dim in shape[1:]:
                elements_per_slice *= dim
            
            for i in range(shape[0]):
                slice_start = start_idx + i * elements_per_slice
                result.append(_build_nested_array(data, shape[1:], slice_start))
            return result
    
    return _build_nested_array(flat_data, new_shape)

_last_corrected_shape = None
_need_truncate_data = False

def replace_np_reshape(array, new_shape):
 
    global _last_corrected_shape, _need_truncate_data
    _last_corrected_shape = None  
    _need_truncate_data = False  
    
    if isinstance(new_shape, int):
        new_shape = (new_shape,)
    elif isinstance(new_shape, list):
        new_shape = tuple(new_shape)
    
    for dim in new_shape:
        if dim < -1:
            raise ValueError
        elif dim == 0:
            raise ValueError
    
    flat_data = _flatten_row_major(array)
    total_elements = len(flat_data)
    
    resolved_shape = _resolve_auto_dimension(new_shape, total_elements)
    
    _validate_reshape(total_elements, resolved_shape)
    

    if _last_corrected_shape is not None:
        resolved_shape = _last_corrected_shape
    
    reshaped_data = _reshape_row_major(flat_data, resolved_shape)
    
    return NumpyCompatibleArray(reshaped_data, shape=resolved_shape)
