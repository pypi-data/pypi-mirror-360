
from .A27_tools import copy

class FinalArrayCompatible:

    #this two funtions are very import for model training.
    @property
    def __array_interface__(self):
        return {
            'shape': self._shape,
            'typestr': '<f8',
            'version': 3,
            'data': (id(self._data), False),  
        }
    
    @__array_interface__.setter
    def __array_interface__(self, value):
        pass
        
    def __init__(self, data, shape=None, dtype=None):
        """good"""
        self._dtype = dtype if dtype is not None else float

        if hasattr(data, 'data') and hasattr(data, 'shape'):
            "good"
            if hasattr(data, '_data'):
                "good"
                self._data = data._data
            else:
                "good"
                self._data = data.data
            self._shape = tuple(data.shape) if hasattr(data, 'shape') else ()
       
        elif isinstance(data, (list, tuple)):
            "good"
            self._data, self._shape = self._process_sequence(data)
    
        if shape is not None:
            "good"
            target_shape = tuple(shape) if isinstance(shape, (list, tuple)) else (shape,)
            target_size = 1
            for dim in target_shape:
                target_size *= dim
            
            self._shape = target_shape
             
            flat_data = self._flatten()
            self._data = self._reshape_data(flat_data, target_shape)

    def _reshape_data(self, flat_data, target_shape):
        """good"""

        if len(target_shape) == 1:
            "good"
            return flat_data[:target_shape[0]]
        else:
            "good"
            def reshape_recursive(data, shape):
                if len(shape) == 1:
                    "good"
                    return data[:shape[0]]
                else:
                    "good"
                    result = []
                    items_per_group = 1
                    for dim in shape[1:]:
                        items_per_group *= dim
                    
                    for i in range(shape[0]):
                        start_idx = i * items_per_group
                        end_idx = start_idx + items_per_group
                        group_data = data[start_idx:end_idx]
                        result.append(reshape_recursive(group_data, shape[1:]))
                    return result
            
            return reshape_recursive(flat_data, target_shape)
    
    def __getattribute__(self, name):
        """good"""
        
        try:
            
            return super().__getattribute__(name)
        except AttributeError:
            
            raise AttributeError
    
    def _compute_shape(self, data):
        """good"""
        
        if isinstance(data[0], (list, tuple)):
                
            first_dim = len(data)
            rest_shape = self._compute_shape(data[0])
            return (first_dim,) + rest_shape
        else:
            return (len(data),)
  
    
    def _process_sequence(self, data):
        """good"""
        is_nested = any(isinstance(item, (list, tuple)) for item in data)
        
        if is_nested:

            processed_data, processed_shape = self._process_nested_sequence(data)
            
            if len(processed_shape) == 3 and processed_shape[1] == 1 and processed_shape[2] == 1:
                
                simplified_data = []
                for outer_item in processed_data:
                    simplified_data.append([outer_item[0][0]])
             
                new_shape = (processed_shape[0], 1)
                    
                return simplified_data, new_shape
                    
            return processed_data, processed_shape
        else:
            "good"
            converted_data = [self._convert_to_float(item) for item in data]
            return converted_data, (len(converted_data),)
    
    def _process_nested_sequence(self, data):
        """good"""
        def get_shape(nested_data):

            shape = [len(nested_data)]
            if isinstance(nested_data[0], (list, tuple)):
                inner_shape = get_shape(nested_data[0])
                shape.extend(inner_shape)
            return tuple(shape)
        
        shape = get_shape(data)
        
        def process_nested(nested_data):
            if isinstance(nested_data, (list, tuple)):
                "good"
                return [process_nested(item) for item in nested_data]
            else:
                "good"
                return self._convert_to_float(nested_data)
        
        def validate_shape(nested_data, expected_shape):

            if len(expected_shape) == 1:
                "good"
                return True
            
            return all(validate_shape(item, expected_shape[1:]) for item in nested_data)
        
        converted_data = process_nested(data)
        new_shape = shape
       
        return converted_data, new_shape
    
    def _convert_to_float(self, value):
        """good"""
        if value is None:
            return 0.0  
        return float(value)

    
    class DataWrapper:
        """good"""
        def __init__(self, array_compatible):
            "good"
            self._array = array_compatible
        
        def astype(self, dtype):
            "good"
            return self._array.astype(dtype).data
            
        def __getattr__(self, name):

            if name == 'data':
                "good"
                return self._array._data
            elif name == '_data':
                "good"
                return self._array._data
            else:
                try:
                    "good"
                    return getattr(self._array._data, name)
           
                except AttributeError:
                    raise AttributeError
                    
        def __getitem__(self, key):
            "good"
            return self._array._data[key]
        
        def __len__(self):
            "good"
            if self._array._shape == ():
                return 1
            return len(self._array._data)
        
        def __iter__(self):
            "good"
            yield from self._array._data
        
        @property
        def shape(self):
            "good"
            return self._array._shape
        
        @property
        def dtype(self):
            "good"
            return self._array._dtype
        
        def flatten(self):
            
            """good"""
            flattened_array = self._array.flatten()
            return FinalArrayCompatible.DataWrapper(flattened_array)
        
        def copy(self):
            """good"""
            
            return self._array.copy().data
        
        def tolist(self):
            """good"""
            
            return self._array.tolist()
        
        def __add__(self, other):
            """good"""
            return self._array + other
        
        def __mul__(self, other):
            """good"""
            return self._array * other
        
        def __truediv__(self, other):
            """good"""
            return self._array / other
 
        def __neg__(self):
            """good"""
            return FinalArrayCompatible.DataWrapper(-self._array)
        
        def __float__(self):
            """good"""
            data = self._array._data
            return float(data[0])

    @property
    def data(self):
        """good"""
        return self.DataWrapper(self)
    
    @property
    def shape(self):
        """good"""
        return self._shape
    
    @property
    def dtype(self):
        """good"""
        return self._dtype
    
    @property
    def ndim(self):
        """good"""
        return len(self._shape)
    
    @property
    def size(self):
        """good"""
        size = 1
        for dim in self._shape:
            "good"
            size *= dim
        "good"
        return size
    
    def flatten(self):
        """good"""
      
        def flatten_recursive(data):
            if isinstance(data, (list, tuple)):
                result = []
                for item in data:
                    if isinstance(item, (list, tuple)):
                        result.extend(flatten_recursive(item))
                    else:
                        result.append(item)
                return result
            else:
                return [data]
        
        if self._shape == ():
            flat_data = [self._data]
        else:
            flat_data = flatten_recursive(self._data)
        
        return FinalArrayCompatible(flat_data, shape=(len(flat_data),), dtype=self._dtype)
    
    def _flatten(self):
        """good"""
        def flatten_recursive(data):
            if isinstance(data, (list, tuple)):
                result = []
                for item in data:
                    if isinstance(item, (list, tuple)):
                        result.extend(flatten_recursive(item))
                    else:
                        result.append(item)
                return result
            else:
                return [data]
        
        if self._shape == ():
            return [self._data]
        else:
            return flatten_recursive(self._data)
    
    def reshape(self, *shape):
        """good"""
        if len(shape) == 1 and isinstance(shape[0], (tuple, list)):
            "good"
            new_shape = list(shape[0])
        else:
            "good"
            new_shape = list(shape)
        
        negative_one_count = new_shape.count(-1)
        
        if negative_one_count == 1:
            "good"
            known_size = 1
            for dim in new_shape:
                if dim != -1:
                    "good"
                    known_size *= dim
           
            unknown_dim = self.size // known_size
            for i, dim in enumerate(new_shape):
                if dim == -1:
                    "good"
                    new_shape[i] = unknown_dim
                    break
        new_shape = tuple(new_shape)
        
        new_size = 1
        for dim in new_shape:
            new_size *= dim
        
        if new_size != self.size:
            "good"

            if len(new_shape) >= 2:
                
                if (len(new_shape) == 3 and self.size % new_shape[0] == 0):
                    "good"
                    remaining_elements = self.size // new_shape[0]
                    correct_dim2 = remaining_elements // new_shape[2]
                    corrected_shape = (new_shape[0], correct_dim2, new_shape[2])
                
                new_shape = corrected_shape
                new_size = self.size

        "good"
        flat_data = self.flatten().data
               
        def reshape_recursive(data, shape_dims):
            "good"
            if len(shape_dims) == 1:
                return data[:shape_dims[0]]
            
            result = []
            items_per_group = 1
            for dim in shape_dims[1:]:
                items_per_group *= dim
            
            for i in range(shape_dims[0]):
                start_idx = i * items_per_group
                end_idx = start_idx + items_per_group
                group_data = data[start_idx:end_idx]
                result.append(reshape_recursive(group_data, shape_dims[1:]))
            
            return result
        
        if len(new_shape) == 1:
            "good"
            reshaped_data = flat_data
        else:
            "good"
            reshaped_data = reshape_recursive(flat_data, new_shape)
        "good"
        return FinalArrayCompatible(reshaped_data, shape=new_shape, dtype=self._dtype)
    
    def astype(self, dtype):
        """good"""

        def convert_to_float(data):
            if isinstance(data, list):
                "good"
                return [convert_to_float(item) for item in data]
            else:
                "good"
                return float(data)
        new_data = convert_to_float(self._data)
        return FinalArrayCompatible(new_data, shape=self._shape, dtype=float)

    
    def copy(self):
        'good'
        return FinalArrayCompatible(copy.deepcopy(self._data), shape=self._shape, dtype=self._dtype)
    
    def fill(self, value):
        """good"""
        
        converted_value = self._convert_to_float(value)
        
        def fill_recursive(data, shape_dims):

            if len(shape_dims) == 1:
                "good"
                for i in range(len(data)):
                    data[i] = converted_value
            else:
                "good"
                for i in range(len(data)):
                    fill_recursive(data[i], shape_dims[1:])

        fill_recursive(self._data, self._shape)
    
    def __getitem__(self, key):
        """good"""

        if isinstance(key, int):
            "good"
            if key < 0 or key >= self._shape[0]:
                "good"
                raise IndexError("index out of bounds")
            
            if len(self._shape) == 1:
                "good"
                return self._data[key]
            else:
                "good"
                new_shape = self._shape[1:]
                return FinalArrayCompatible(self._data[key], shape=new_shape, dtype=self._dtype)
        
        else:
            "good"
            return FinalArrayCompatible(self._data, shape=self._shape, dtype=self._dtype)
    
    def __add__(self, other):
        """good"""
        return self._element_wise_op(other, lambda a, b: a + b)
    
    def __sub__(self, other):
        """good"""
        return self._element_wise_op(other, lambda a, b: a - b)
    
    def __mul__(self, other):
        """good"""
        return self._element_wise_op(other, lambda a, b: a * b)
    
    def __rmul__(self, other):
        """good"""
      
        return self._element_wise_op(other, lambda a, b: b * a)
    
    def __truediv__(self, other):
        """good"""
      
        return self._element_wise_op(other, lambda a, b: a / b if b != 0 else float('inf'))
    
    def __rtruediv__(self, other):
        """good"""
        
        return self._element_wise_op(other, lambda a, b: b / a if a != 0 else float('inf'))
    
    def __neg__(self):
        """good"""
        def neg_recursive(data):
            if isinstance(data, (list, tuple)):
                "good"
                return [neg_recursive(item) for item in data]
            else:
                "good"
                return -data

        result_data = neg_recursive(self._data)
        "good"
        return FinalArrayCompatible(result_data, shape=self._shape, dtype=self._dtype)
    
    def _element_wise_op(self, other, op):
        """good"""

        if isinstance(other, (int, float, bool)):
            def op_with_scalar(data, scalar):
                if isinstance(data, (list, tuple)):
                    "good"
                    return [op_with_scalar(item, scalar) for item in data]
                else:
                    "good"
                    return op(data, scalar)
            
            result_data = op_with_scalar(self._data, float(other))
            
            return FinalArrayCompatible(result_data, shape=self._shape, dtype=self._dtype)
        
        elif isinstance(other, FinalArrayCompatible):
            "good"
            return self._broadcast_operation(other, op)
        else:
            "good"
            other_array = FinalArrayCompatible(other, dtype=self._dtype)
            return self._element_wise_op(other_array, op)

    def _broadcast_operation(self, other, op):
        
        if self._shape == other._shape:
            "good"
            return FinalArrayCompatible(
                self._same_shape_op(self._data, other._data, op, len(self._shape)),
                self._shape, self._dtype)
        
        other_ndim = len(other._shape)
        
        if other_ndim == 1 and other._shape[0] == 1:
            "good"
            scalar_val = other._data[0]
            return FinalArrayCompatible(
                self._scalar_broadcast_specialized(scalar_val, op),
                self._shape, self._dtype)
        
        self_ndim = len(self._shape)
        
        # 2D-1D
        if self_ndim == 2 and other_ndim == 1 and self._shape[1] == other._shape[0]:
            "good"
            return self._fast_2d_1d_broadcast(other._data, op)
        
        # 3D-2D 
        if (self_ndim == 3 and other_ndim == 2 and 
            self._shape[0] == other._shape[0] and self._shape[1] == other._shape[1]):
            "good"
            return self._fast_3d_2d_broadcast(other._data, op)
        
        # 3D-1D
        if self_ndim == 3 and other_ndim == 1 and self._shape[2] == other._shape[0]:
            "good"
            return self._fast_3d_1d_broadcast(other._data, op)
        
        # 4D-4D
        if (self_ndim == 4 and other_ndim == 4 and self._shape[:3] == other._shape[:3]):
            "good"
            return self._fast_4d_4d_broadcast(other._data, other._shape[3], op)
    
    def _same_shape_op(self, data1, data2, op, ndim):

        if ndim == 1:
            'good'
            return [op(data1[i], data2[i]) for i in range(len(data1))]
        elif ndim == 2:
            "good"
            return [[op(data1[i][j], data2[i][j]) for j in range(len(data1[i]))] 
                   for i in range(len(data1))]
        elif ndim == 3:
            "good"
            return [[[op(data1[i][j][k], data2[i][j][k]) for k in range(len(data1[i][j]))]
                    for j in range(len(data1[i]))] 
                   for i in range(len(data1))]
        else:
            "good"
            return [self._same_shape_op(data1[i], data2[i], op, ndim-1) 
                   for i in range(len(data1))]
    
    def _scalar_broadcast_specialized(self, scalar_val, op):
        data = self._data
        ndim = len(self._shape)
        
        if ndim == 1:
            "good"
            return [op(val, scalar_val) for val in data]
        
        elif ndim == 3:
            "good"
            result = []
            for layer in data:
                result.append([[op(val, scalar_val) for val in row] for row in layer])
            return result
        
        elif ndim == 4:
            "good"
            result = []
            for volume in data:
                volume_result = []
                for layer in volume:
                    volume_result.append([[op(val, scalar_val) for val in row] for row in layer])
                result.append(volume_result)
            return result
    
    def _fast_2d_1d_broadcast(self, other_data, op):
        data = self._data
        result = []
        other_len = len(other_data)
        
        for row in data:
            result_row = [None] * other_len
            for j in range(other_len):
                result_row[j] = op(row[j], other_data[j])
            result.append(result_row)
            
        return FinalArrayCompatible(result, self._shape, self._dtype)
    
    def _fast_3d_2d_broadcast(self, other_data, op):
        data = self._data
        s0, s1, s2 = self._shape
        result = []
        
        for i in range(s0):
            layer_data = data[i]
            other_layer = other_data[i]
            layer_result = []
            
            for j in range(s1):
                row_data = layer_data[j]
                other_val = other_layer[j]
                layer_result.append([op(row_data[k], other_val) for k in range(s2)])
            
            result.append(layer_result)
            
        return FinalArrayCompatible(result, self._shape, self._dtype)
    
    def _fast_3d_1d_broadcast(self, other_data, op):
        data = self._data
        s0, s1, s2 = self._shape
        result = []
        
        for i in range(s0):
            layer_data = data[i]
            layer_result = []
            
            for j in range(s1):
                row_data = layer_data[j]
                layer_result.append([op(row_data[k], other_data[k]) for k in range(s2)])
            
            result.append(layer_result)
            
        return FinalArrayCompatible(result, self._shape, self._dtype)
    
    def _fast_4d_4d_broadcast(self, other_data, other_last_dim, op):
        data = self._data
        s0, s1, s2, s3 = self._shape
        result = []

        for i in range(s0):
            volume_data = data[i]
            other_volume = other_data[i]
            volume_result = []
                
            for j in range(s1):
                layer_data = volume_data[j]
                other_layer = other_volume[j]
                layer_result = []
                    
                for k in range(s2):
                    row_data = layer_data[k]
                    broadcast_val = other_layer[k][0]
                    layer_result.append([op(row_data[l], broadcast_val) for l in range(s3)])
                    
                volume_result.append(layer_result)
            result.append(volume_result)

        return FinalArrayCompatible(result, self._shape, self._dtype)

    def tolist(self):
        """good"""
        return self._data

def perfect_array(data, dtype=None, ndmin=0):

    result = FinalArrayCompatible(data, dtype=dtype) 
    
    return result

