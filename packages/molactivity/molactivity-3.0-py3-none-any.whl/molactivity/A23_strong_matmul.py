
from . import A2_arrays as arrays

def perfect_matmul(a, b):
    
    if a is None or b is None:
        raise ValueError
    
    a_data = _extract_data(a)
    b_data = _extract_data(b)
    
    a_processed, a_shape = _process_input(a_data)
    b_processed, b_shape = _process_input(b_data)
    
    _validate_matmul_compatibility(a_shape, b_shape)
    
    result = _dispatch_matmul(a_processed, b_processed, a_shape, b_shape)

    try:

        if isinstance(result, (int, float, complex)):
            result_array = arrays.Array([result])

            return result_array
        elif isinstance(result, list):
            result_array = arrays.Array(result)
            return result_array
        else:

            return result
    except Exception as e:

        raise e

def _extract_data(obj):

    if hasattr(obj, '__class__') and 'FinalArrayCompatible' in str(obj.__class__):
        if hasattr(obj, '_data'):
            return obj._data
        elif hasattr(obj, 'data'):
            return obj.data
    
    if hasattr(obj, 'data'):
        data = obj.data
        if isinstance(data, memoryview):
            return _memoryview_to_list(data, obj.shape if hasattr(obj, 'shape') else None)
        return data
    elif isinstance(obj, memoryview):
        return _memoryview_to_list(obj)
    return obj

def _memoryview_to_list(mv, shape=None):
    try:
        flat_list = list(mv)
        
        if shape is not None and len(shape) > 1:
            return _reconstruct_from_flat(flat_list, shape)
        else:
            return flat_list
    except Exception as e:
        try:
            flat_list = [float(x) for x in mv]
            if shape is not None and len(shape) > 1:
                return _reconstruct_from_flat(flat_list, shape)
            return flat_list
        except:
            return list(mv.tolist()) if hasattr(mv, 'tolist') else [mv]

def _reconstruct_from_flat(flat_data, shape):
    if len(shape) == 1:
        return flat_data[:shape[0]]
    
    def _build_recursive(data, dims, start_idx=0):
        if len(dims) == 1:
            return data[start_idx:start_idx + dims[0]], start_idx + dims[0]
        
        result = []
        current_idx = start_idx
        for _ in range(dims[0]):
            sub_array, current_idx = _build_recursive(data, dims[1:], current_idx)
            result.append(sub_array)
        return result, current_idx
    
    result, _ = _build_recursive(flat_data, shape)
    return result

def _process_input(array):

    if hasattr(array, '__class__') and 'FinalArrayCompatible' in str(array.__class__):
        data = array._data if hasattr(array, '_data') else array.data
        shape = array._shape if hasattr(array, '_shape') else array.shape
        
        return data, shape
    
    if isinstance(array, (int, float, complex)):
        return [[array]], (1, 1)
    
    if isinstance(array, memoryview):
        array = list(array)
    
    shape = _get_array_shape_matmul(array)
    
    if not shape:
        return [[array]], (1, 1)
    elif len(shape) == 1:
        return array, shape
    else:
        return array, shape

def _flatten_array_matmul(array):
    if isinstance(array, (int, float, complex)):
        return [array]
    
    result = []
    
    def _flatten_recursive(data):
        if isinstance(data, (list, tuple)):
            for item in data:
                _flatten_recursive(item)
        elif hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
            try:
                for item in data:
                    _flatten_recursive(item)
            except TypeError:
                result.append(float(data))
        else:
            result.append(float(data))
    
    _flatten_recursive(array)
    return result

def _get_array_shape_matmul(array):
    if isinstance(array, (int, float, complex)):
        return ()
    
    if not isinstance(array, (list, tuple)):
        if hasattr(array, '__len__'):
            try:
                return (len(array),)
            except:
                return ()
        return ()
    
    def _shape_recursive(data):
        if not isinstance(data, (list, tuple)):
            return []
        if not data:
            return [0]
        
        first_element = data[0]
        first_shape = _shape_recursive(first_element)
        
        all_same_shape = True
        for item in data[1:]:
            if _shape_recursive(item) != first_shape:
                all_same_shape = False
                break
        
        if all_same_shape:
            return [len(data)] + first_shape
        else:
            return [len(data)]
    
    shape = _shape_recursive(array)
    return tuple(shape)

def _validate_matmul_compatibility(shape_a, shape_b):
    if not shape_a or not shape_b:
        return
    
    if (len(shape_a) == 2 and shape_a == (1, 1)) or (len(shape_b) == 2 and shape_b == (1, 1)):
        return
    
    if len(shape_a) >= 2 and len(shape_b) >= 2:
        if shape_a[-1] != shape_b[-2]:
            if not _can_broadcast_matmul(shape_a, shape_b):
                raise ValueError
    elif len(shape_a) == 1 and len(shape_b) >= 2:
        if shape_a[0] != shape_b[-2]:
            raise ValueError
    elif len(shape_a) >= 2 and len(shape_b) == 1:
        if shape_a[-1] != shape_b[0]:
            raise ValueError
    elif len(shape_a) == 1 and len(shape_b) == 1:
        if shape_a[0] != shape_b[0]:
            raise ValueError

def _can_broadcast_matmul(shape_a, shape_b):

    if len(shape_a) == len(shape_b):
        for i in range(len(shape_a) - 2):
            if shape_a[i] != shape_b[i] and shape_a[i] != 1 and shape_b[i] != 1:
                return False
        return shape_a[-1] == shape_b[-2]
    return False

def _dispatch_matmul(a, b, shape_a, shape_b):

    is_large_matrix_a = (shape_a and len(shape_a) >= 2 and 
                        (shape_a[0] > 1 or shape_a[1] > 1) and
                        (shape_a[0] * shape_a[1] > 1))
    
    is_large_matrix_b = (shape_b and len(shape_b) >= 2 and 
                        (shape_b[0] > 1 or shape_b[1] > 1) and
                        (shape_b[0] * shape_b[1] > 1))
    
    if is_large_matrix_a or is_large_matrix_b:
        pass
    else:

        is_scalar_a = (not shape_a or 
                       (len(shape_a) == 2 and shape_a == (1, 1) and isinstance(a, list) and len(a) == 1 and len(a[0]) == 1) or
                       (len(shape_a) == 1 and shape_a[0] == 1 and isinstance(a, list) and len(a) == 1) or
                       (isinstance(a, (int, float, complex))))
        
        is_scalar_b = (not shape_b or 
                       (len(shape_b) == 2 and shape_b == (1, 1) and isinstance(b, list) and len(b) == 1 and len(b[0]) == 1) or
                       (len(shape_b) == 1 and shape_b[0] == 1 and isinstance(b, list) and len(b) == 1) or
                       (isinstance(b, (int, float, complex))))
        
        if is_scalar_a or is_scalar_b:
            return _scalar_multiply(a, b, shape_a, shape_b)
    
    if len(shape_a) == 1 and len(shape_b) == 1:
        return _dot_product(a, b)
    
    elif len(shape_a) == 1 and len(shape_b) == 2:
        return _vector_matrix_multiply(a, b)
    
    elif len(shape_a) == 2 and len(shape_b) == 1:
        return _matrix_vector_multiply(a, b)
    
    elif len(shape_a) == 2 and len(shape_b) == 2:
        return _matrix_matrix_multiply(a, b)
    
    else:
        return _high_dimensional_matmul(a, b, shape_a, shape_b)

def _scalar_multiply(a, b, shape_a, shape_b):

    scalar_a = _extract_scalar_value(a, shape_a)
    scalar_b = _extract_scalar_value(b, shape_b)
    
    if scalar_a is not None and scalar_b is not None:
        return scalar_a * scalar_b
    elif scalar_a is not None:
        return _scalar_array_multiply(scalar_a, b)
    else:
        return _scalar_array_multiply(scalar_b, a)

def _extract_scalar_value(data, shape):

    if shape and len(shape) >= 2:
        total_elements = 1
        for dim in shape:
            total_elements *= dim
        if total_elements > 1:
            return None
    
    if hasattr(data, '_shape') and hasattr(data, '_data'):
        if hasattr(data, '_shape') and len(data._shape) >= 2:
            total_elements = 1
            for dim in data._shape:
                total_elements *= dim
            if total_elements > 1:
                return None
    
    if not shape or (len(shape) == 1 and shape[0] == 1) or (len(shape) == 2 and shape == (1, 1)):
        try:
            if isinstance(data, list):
                if len(data) == 1 and isinstance(data[0], list) and len(data[0]) == 1:
                    inner_val = data[0][0]
                    if isinstance(inner_val, (int, float, complex)):
                        return float(inner_val)
                    elif hasattr(inner_val, '__float__') and not hasattr(inner_val, '_shape') and not hasattr(inner_val, '_data'):
                        return float(inner_val)
                elif len(data) == 1:
                    inner_val = data[0]
                    if isinstance(inner_val, (int, float, complex)):
                        return float(inner_val)
                    elif hasattr(inner_val, '__float__') and not hasattr(inner_val, '_shape') and not hasattr(inner_val, '_data'):
                        return float(inner_val)
            elif isinstance(data, (int, float, complex)):
                return float(data)
            elif hasattr(data, '_shape') and hasattr(data, '_data'):
                if data._shape == () or data._shape == (1,) or data._shape == (1, 1):
                    if data._shape == ():
                        return float(data._data) if isinstance(data._data, (int, float, complex)) else None
                    elif data._shape == (1,) and isinstance(data._data, list) and len(data._data) == 1:
                        return float(data._data[0]) if isinstance(data._data[0], (int, float, complex)) else None
                    elif data._shape == (1, 1) and isinstance(data._data, list) and len(data._data) == 1 and isinstance(data._data[0], list) and len(data._data[0]) == 1:
                        return float(data._data[0][0]) if isinstance(data._data[0][0], (int, float, complex)) else None
                return None
        except (ValueError, TypeError, IndexError, AttributeError):
            pass
    return None

def _scalar_array_multiply(scalar, array):
    def _multiply_recursive(data):
        if isinstance(data, list):
            return [_multiply_recursive(item) for item in data]
        elif isinstance(data, (int, float, complex)):
            return scalar * data
        elif isinstance(data, memoryview):
            return scalar * float(data)
        elif hasattr(data, '_shape') and hasattr(data, '_data'):

            raise ValueError
        else:
            try:
                if hasattr(data, '__float__') and not hasattr(data, '_shape'):
                    return scalar * float(data)
                else:
                    return 0.0
            except (ValueError, TypeError):
                return 0.0
    
    return _multiply_recursive(array)

def _dot_product(vec_a, vec_b):
    if len(vec_a) != len(vec_b):
        raise ValueError
    
    result = 0.0
    for i in range(len(vec_a)):
        result += vec_a[i] * vec_b[i]
    
    return result

def _vector_matrix_multiply(vector, matrix):
    if len(vector) != len(matrix):
        raise ValueError
    
    if not matrix or not matrix[0]:
        raise ValueError
    
    cols = len(matrix[0])
    result = []
    
    for j in range(cols):
        sum_val = 0.0
        for i in range(len(vector)):
            sum_val += vector[i] * matrix[i][j]
        result.append(sum_val)
    
    return result

def _matrix_vector_multiply(matrix, vector):
    if not matrix or len(matrix[0]) != len(vector):
        raise ValueError
    
    result = []
    for row in matrix:
        sum_val = 0.0
        for i in range(len(vector)):
            sum_val += row[i] * vector[i]
        result.append(sum_val)
    
    return result

def _matrix_matrix_multiply(matrix_a, matrix_b):
    if not matrix_a or not matrix_b or not matrix_a[0] or not matrix_b[0]:
        raise ValueError
    
    rows_a, cols_a = len(matrix_a), len(matrix_a[0])
    rows_b, cols_b = len(matrix_b), len(matrix_b[0])
    
    if cols_a != rows_b:
        raise ValueError

    try:
        result = [[0.0 for _ in range(cols_b)] for _ in range(rows_a)]
        
    except Exception as e:
        raise e
    
    try:
        for i in range(rows_a):
            for j in range(cols_b):
                sum_val = 0.0
                for k in range(cols_a):
                    sum_val += matrix_a[i][k] * matrix_b[k][j]
                result[i][j] = sum_val
            
    except Exception as e:
        pass

    return result

def _high_dimensional_matmul(a, b, shape_a, shape_b):

    if len(shape_a) > 2 and len(shape_b) > 2:
        return _batch_matmul_recursive(a, b, shape_a, shape_b)
    elif len(shape_a) > 2:
        return _high_dim_2d_matmul(a, b, shape_a, shape_b)
    elif len(shape_b) > 2:
        return _2d_high_dim_matmul(a, b, shape_a, shape_b)
    else:
        return _matrix_matrix_multiply(a, b)

def _batch_matmul_recursive(a, b, shape_a, shape_b):

    if len(shape_a) == 2 and len(shape_b) == 2:
        return _matrix_matrix_multiply(a, b)
    
    if len(shape_a) == len(shape_b) and len(shape_a) > 2:
        result = []
        batch_size = min(len(a), len(b))
        
        for i in range(batch_size):
            sub_result = _batch_matmul_recursive(
                a[i], b[i], 
                shape_a[1:], shape_b[1:]
            )
            result.append(sub_result)
        
        return result
    
    elif len(shape_a) > len(shape_b):
        result = []
        for i in range(len(a)):
            sub_result = _batch_matmul_recursive(
                a[i], b, 
                shape_a[1:], shape_b
            )
            result.append(sub_result)
        return result
    
    elif len(shape_b) > len(shape_a):
        result = []
        for i in range(len(b)):
            sub_result = _batch_matmul_recursive(
                a, b[i], 
                shape_a, shape_b[1:]
            )
            result.append(sub_result)
        return result
    
    else:
        return _matrix_matrix_multiply(a, b)

def _high_dim_2d_matmul(a, b, shape_a, shape_b):
    if len(shape_a) == 3:
        result = []
        for i in range(len(a)):
            sub_result = _matrix_matrix_multiply(a[i], b)
            result.append(sub_result)
        return result
    
    elif len(shape_a) == 4:
        result = []
        for i in range(len(a)): 
            batch_result = []
            for j in range(len(a[i])):
                sub_result = _matrix_matrix_multiply(a[i][j], b)
                batch_result.append(sub_result)
            result.append(batch_result)
        return result
    
    else:
        result = []
        for i in range(len(a)):
            sub_result = _high_dim_2d_matmul(a[i], b, shape_a[1:], shape_b)
            result.append(sub_result)
        return result

def _2d_high_dim_matmul(a, b, shape_a, shape_b):
    if len(shape_b) == 3:
        result = []
        for i in range(len(b)):
            sub_result = _matrix_matrix_multiply(a, b[i])
            result.append(sub_result)
        return result
    
    elif len(shape_b) == 4:
        result = []
        for i in range(len(b)): 
            batch_result = []
            for j in range(len(b[i])):  
                sub_result = _matrix_matrix_multiply(a, b[i][j])
                batch_result.append(sub_result)
            result.append(batch_result)
        return result
    
    else:
        result = []
        for i in range(len(b)):
            sub_result = _2d_high_dim_matmul(a, b[i], shape_a, shape_b[1:])
            result.append(sub_result)
        return result

def matrix_multiply(a, b):
    return perfect_matmul(a, b)

def dot_product(a, b):
    return perfect_matmul(a, b)

def safe_matmul(a, b, default_value=0.0):
    return perfect_matmul(a, b)

def batch_matmul(matrices_a, matrices_b):
    if len(matrices_a) != len(matrices_b):
        raise ValueError
    
    results = []
    for i in range(len(matrices_a)):
        result = perfect_matmul(matrices_a[i], matrices_b[i])
        results.append(result)
    
    return results
