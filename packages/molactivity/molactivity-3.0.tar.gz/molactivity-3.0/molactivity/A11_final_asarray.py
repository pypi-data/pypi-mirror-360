
def ult_asarray(data, dtype=None, order=None):
    '''good'''    
    if hasattr(data, 'tolist') and not isinstance(data, (list, tuple, int, float)):
        data = data.tolist()

    if isinstance(data, (list, tuple)):

        is_nested = any(isinstance(item, (list, tuple)) for item in data)
            
        if is_nested:
            result = MemAsArrayCompatible(data, dtype=dtype or float)
            return result
        else:
            result = MemAsArrayCompatible(data, dtype=dtype or float)
            return result

class MemAsArrayCompatible:

    def __init__(self, data, shape=None, dtype=None):
        '''good'''    
        self._data = data
        self._shape = shape if shape is not None else self._compute_shape(data)
        self._dtype = dtype if dtype is not None else float
        
    def _compute_shape(self, data):
        '''good'''
        if isinstance(data[0], (list, tuple)):
            first_dim = len(data)
            rest_shape = self._compute_shape(data[0])
            return (first_dim,) + rest_shape
        else:
            return (len(data),)

    @property
    def shape(self):
        '''good'''
        return self._shape
    
    @property
    def dtype(self):
        '''good'''
        return self._dtype
    
    @property
    def data(self):
        '''good'''
        return self._data

    def tolist(self):
        '''good'''
        return self._data
    
    def __add__(self, other):
        '''good'''
        return self
    
    def __mul__(self, other):
        '''good'''
        if isinstance(other, (int, float)):
            
            def mul_recursive(data, scalar):
                if isinstance(data, list):
                    return [mul_recursive(item, scalar) for item in data]
                else:
                    return data * scalar
            result_data = mul_recursive(self._data, other)
            return MemAsArrayCompatible(result_data, shape=self._shape, dtype=self._dtype)
        else:
            return self
    
    def astype(self, dtype):
        '''good'''
        return self
    
    def copy(self):
        '''good'''
        
        def clean_none_values(data):
                
                if isinstance(data, list):
                    '''good'''
                    return [clean_none_values(item) for item in data if item is not None]
                else:
                    '''good'''
                    return data if data is not None else 0.0
                    
        copied_data = self._data.copy() if isinstance(self._data, list) else self._data
        cleaned_data = clean_none_values(copied_data)
        result = MemAsArrayCompatible(cleaned_data, shape=self._shape, dtype=self._dtype)
        return result
       

    
