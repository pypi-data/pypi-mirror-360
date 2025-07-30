import numpy as np

def add(a, b):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Add(Function):
        @staticmethod
        def forward(ctx, a, b):
            ctx.module_ref_a = getattr(a, '_module', None)
            ctx.module_ref_b = getattr(b, '_module', None)
            
            a_shape = a.shape if hasattr(a, 'shape') else None
            b_shape = b.shape if hasattr(b, 'shape') else None
            
            ctx.metadata = {
                'a_shape': a_shape,
                'b_shape': b_shape
            }
            
            if hasattr(a, 'detach') and not hasattr(a, 'data'):
                a = a.detach().numpy()
            if hasattr(b, 'detach') and not hasattr(b, 'data'):
                b = b.detach().numpy()
            
            a_data = np.asarray(a.data if hasattr(a, 'data') else a, dtype=np.float32)
            b_data = np.asarray(b.data if hasattr(b, 'data') else b, dtype=np.float32)
            
            ctx.save_for_backward(a, b)
            return Tensor(a_data + b_data)
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)

            a, b = ctx.saved_tensors
            from .B16_tensor import Tensor
            def reduce_grad(grad, shape):
                grad_data = grad.data if hasattr(grad, 'data') else grad
                while len(grad_data.shape) > len(shape):
                    grad_data = np.sum(grad_data, axis=0)
                for i, s in enumerate(shape):
                    if s == 1:
                        grad_data = np.sum(grad_data, axis=i, keepdims=True)
                return grad_data.reshape(shape)
            grad_a = grad_output
            grad_b = grad_output
            if hasattr(a, 'shape') and grad_a.shape != a.shape:
                grad_a = reduce_grad(grad_a, a.shape)
            if hasattr(b, 'shape') and grad_b.shape != b.shape:
                grad_b = reduce_grad(grad_b, b.shape)
            if not isinstance(grad_a, Tensor):
                grad_a = Tensor(grad_a, requires_grad=False)
            if not isinstance(grad_b, Tensor):
                grad_b = Tensor(grad_b, requires_grad=False)
            return grad_a, grad_b
    
    if not isinstance(a, Tensor):
        a = Tensor(a)
    if not isinstance(b, Tensor):
        b = Tensor(b)
    
    result = Add.apply(a, b)
    
    if hasattr(a, '_module') and a._module is not None:
        if hasattr(result, 'attach_module_reference'):
            result.attach_module_reference(a._module)
    elif hasattr(b, '_module') and b._module is not None:
        if hasattr(result, 'attach_module_reference'):
            result.attach_module_reference(b._module)
    
    return result

def sub(a, b):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Sub(Function):
        @staticmethod
        def forward(ctx, a, b):
            ctx.module_ref_a = getattr(a, '_module', None)
            ctx.module_ref_b = getattr(b, '_module', None)
            
            a_shape = a.shape if hasattr(a, 'shape') else None
            b_shape = b.shape if hasattr(b, 'shape') else None
            
            ctx.metadata = {
                'a_shape': a_shape,
                'b_shape': b_shape
            }
            
            if hasattr(a, 'detach'):
                a = a.detach().cpu().numpy()
            if hasattr(b, 'detach'):
                b = b.detach().cpu().numpy()
            
            a_data = np.asarray(a.data if hasattr(a, 'data') else a, dtype=np.float32)
            b_data = np.asarray(b.data if hasattr(b, 'data') else b, dtype=np.float32)
            
            ctx.save_for_backward(a, b)
            return Tensor(a_data - b_data)
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            
            if not hasattr(ctx, 'saved_tensors') or ctx.saved_tensors is None or len(ctx.saved_tensors) != 2:
                print('[Warning] Sub.backward: ctx.saved_tensors is missing or invalid, returning zeros.')
                from .B16_tensor import Tensor
                zero = Tensor(np.zeros_like(grad_output), requires_grad=False)
                return zero, zero
            a, b = ctx.saved_tensors
            
            module_ref_a = getattr(ctx, 'module_ref_a', None)
            module_ref_b = getattr(ctx, 'module_ref_b', None)
            
            metadata = getattr(ctx, 'metadata', {})
            a_shape = metadata.get('a_shape')
            b_shape = metadata.get('b_shape')
            
            debug = False  
            
            from .B16_tensor import Tensor
            
            grad_a = grad_output
            grad_b = -grad_output
            
            if a_shape is not None and grad_a.shape != a_shape:
                try:
                    if hasattr(grad_a, 'data') and isinstance(grad_a.data, np.ndarray):
                        if len(grad_a.data.shape) >= 1 and (a_shape == (1,) or 
                                                           (len(a_shape) == 2 and a_shape[0] == 1 and a_shape[1] == 1)):
                            scalar_value = float(np.sum(grad_a.data)) / np.prod(grad_a.data.shape)
                            grad_a = Tensor(np.full(a_shape, scalar_value), requires_grad=False)
                 
                    if grad_a.shape != a_shape:
                        
                        if hasattr(grad_a, 'sum'):
                            if len(a_shape) < len(grad_a.shape):
                                axis_to_sum = tuple(range(len(grad_a.shape) - len(a_shape)))
                                grad_a = grad_a.sum(axis=axis_to_sum, keepdims=True)
                        if hasattr(grad_a, 'reshape'):
                            grad_a = grad_a.reshape(a_shape)
                        elif hasattr(grad_a, 'data') and hasattr(grad_a.data, 'reshape'):
                            grad_a.data = grad_a.data.reshape(a_shape)
                except Exception as e:
        
                    try:
                        if hasattr(grad_a, 'data'):
                            scalar_value = float(np.sum(grad_a.data)) / np.prod(grad_a.data.shape)
                            grad_a = Tensor(np.full(a_shape, scalar_value), requires_grad=False)
                        else:
                            grad_a = Tensor(np.zeros(a_shape), requires_grad=False)
                    except Exception:
                        grad_a = Tensor(np.zeros(a_shape), requires_grad=False)
            
            if b_shape is not None and grad_b.shape != b_shape:
                try:
                    if hasattr(grad_b, 'data') and isinstance(grad_b.data, np.ndarray):
                        if len(grad_b.data.shape) >= 1 and (b_shape == (1,) or 
                                                           (len(b_shape) == 2 and b_shape[0] == 1 and b_shape[1] == 1)):
                            scalar_value = float(np.sum(grad_b.data)) / np.prod(grad_b.data.shape)
                            grad_b = Tensor(np.full(b_shape, scalar_value), requires_grad=False)
                           
                    if grad_b.shape != b_shape:
                       
                        if hasattr(grad_b, 'sum'):
                            if len(b_shape) < len(grad_b.shape):
                                axis_to_sum = tuple(range(len(grad_b.shape) - len(b_shape)))
                                grad_b = grad_b.sum(axis=axis_to_sum, keepdims=True)
                        if hasattr(grad_b, 'reshape'):
                            grad_b = grad_b.reshape(b_shape)
                        elif hasattr(grad_b, 'data') and hasattr(grad_b.data, 'reshape'):
                            grad_b.data = grad_b.data.reshape(b_shape)
                except Exception as e:
                    
                    try:
                        if hasattr(grad_b, 'data'):
                            scalar_value = float(np.sum(grad_b.data)) / np.prod(grad_b.data.shape)
                            grad_b = Tensor(np.full(b_shape, scalar_value), requires_grad=False)
                        else:
                            grad_b = Tensor(np.zeros(b_shape), requires_grad=False)
                    except Exception:
                        grad_b = Tensor(np.zeros(b_shape), requires_grad=False)
            
            if not isinstance(grad_a, Tensor):
                grad_a = Tensor(grad_a, requires_grad=False)
            if not isinstance(grad_b, Tensor):
                grad_b = Tensor(grad_b, requires_grad=False)
            
            if module_ref_a is not None and hasattr(grad_a, 'attach_module_reference'):
                grad_a.attach_module_reference(module_ref_a)
            if module_ref_b is not None and hasattr(grad_b, 'attach_module_reference'):
                grad_b.attach_module_reference(module_ref_b)
            
            return grad_a, grad_b
    
    return Sub.apply(a, b)

def mul(a, b):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Mul(Function):
        @staticmethod
        def forward(ctx, a, b):
            ctx.module_ref_a = getattr(a, '_module', None)
            ctx.module_ref_b = getattr(b, '_module', None)
            
            a_shape = a.shape if hasattr(a, 'shape') else None
            b_shape = b.shape if hasattr(b, 'shape') else None
            
            ctx.metadata = {
                'a_shape': a_shape,
                'b_shape': b_shape
            }
            
            a = a.detach().numpy()
            b = b.detach().numpy()
            result = a * b
            ctx.save_for_backward(a, b)
            return Tensor(result)
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
      
            a, b = ctx.saved_tensors
            
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            
            module_ref_a = getattr(ctx, 'module_ref_a', None)
            module_ref_b = getattr(ctx, 'module_ref_b', None)
            
            metadata = getattr(ctx, 'metadata', {})
            a_shape = metadata.get('a_shape')
            b_shape = metadata.get('b_shape')
            
            
            from .B16_tensor import Tensor
            
            grad_a = grad_output * b
            grad_b = grad_output * a
            
            if a_shape is not None and grad_a.shape != a_shape:
                try:
                    if hasattr(grad_a, 'data') and isinstance(grad_a.data, np.ndarray):
                        if len(grad_a.data.shape) >= 1 and (a_shape == (1,) or 
                                                           (len(a_shape) == 2 and a_shape[0] == 1 and a_shape[1] == 1)):
                            scalar_value = float(np.sum(grad_a.data)) / np.prod(grad_a.data.shape)
                            grad_a = Tensor(np.full(a_shape, scalar_value), requires_grad=False)
                           
                    if grad_a.shape != a_shape:
                        if len(a_shape) < len(grad_a.shape):
                            axis_to_sum = tuple(range(len(grad_a.shape) - len(a_shape)))
                            if hasattr(grad_a, 'sum'):
                                grad_a = grad_a.sum(axis=axis_to_sum, keepdims=True)
                            else:
                                grad_a = Tensor(np.sum(grad_a.data, axis=axis_to_sum, keepdims=True), requires_grad=False)
                        
                        if hasattr(grad_a, 'reshape'):
                            grad_a = grad_a.reshape(a_shape)
                        elif hasattr(grad_a, 'data') and hasattr(grad_a.data, 'reshape'):
                            if np.prod(grad_a.data.shape) != np.prod(a_shape):
                                grad_a.data = np.resize(grad_a.data, a_shape)
                            else:
                                grad_a.data = grad_a.data.reshape(a_shape)
                except Exception as e:

                    try:
                        if hasattr(grad_a, 'data'):
                            scalar_value = float(np.sum(grad_a.data)) / np.prod(grad_a.data.shape)
                            grad_a = Tensor(np.full(a_shape, scalar_value), requires_grad=False)
                        else:
                            grad_a = Tensor(np.zeros(a_shape), requires_grad=False)
                    except Exception:
                        grad_a = Tensor(np.zeros(a_shape), requires_grad=False)
            
            if b_shape is not None and grad_b.shape != b_shape:
                try:
                    if hasattr(grad_b, 'data') and isinstance(grad_b.data, np.ndarray):
                        if len(grad_b.data.shape) >= 1 and (b_shape == (1,) or 
                                                           (len(b_shape) == 2 and b_shape[0] == 1 and b_shape[1] == 1)):
                            scalar_value = float(np.sum(grad_b.data)) / np.prod(grad_b.data.shape)
                            grad_b = Tensor(np.full(b_shape, scalar_value), requires_grad=False)
               
                    if grad_b.shape != b_shape:
                        if len(b_shape) < len(grad_b.shape):
                            axis_to_sum = tuple(range(len(grad_b.shape) - len(b_shape)))
                            if hasattr(grad_b, 'sum'):
                                grad_b = grad_b.sum(axis=axis_to_sum, keepdims=True)
                            else:
                                grad_b = Tensor(np.sum(grad_b.data, axis=axis_to_sum, keepdims=True), requires_grad=False)
                        
                        if hasattr(grad_b, 'reshape'):
                            grad_b = grad_b.reshape(b_shape)
                        elif hasattr(grad_b, 'data') and hasattr(grad_b.data, 'reshape'):
                            if np.prod(grad_b.data.shape) != np.prod(b_shape):
                                grad_b.data = np.resize(grad_b.data, b_shape)
                            else:
                                grad_b.data = grad_b.data.reshape(b_shape)
                except Exception as e:
        
                    try:
                        if hasattr(grad_b, 'data'):
                            scalar_value = float(np.sum(grad_b.data)) / np.prod(grad_b.data.shape)
                            grad_b = Tensor(np.full(b_shape, scalar_value), requires_grad=False)
                        else:
                            grad_b = Tensor(np.zeros(b_shape), requires_grad=False)
                    except Exception:
                        grad_b = Tensor(np.zeros(b_shape), requires_grad=False)
            
            if not isinstance(grad_a, Tensor):
                grad_a = Tensor(grad_a, requires_grad=False)
            if not isinstance(grad_b, Tensor):
                grad_b = Tensor(grad_b, requires_grad=False)
            
            if module_ref_a is not None and hasattr(grad_a, 'attach_module_reference'):
                grad_a.attach_module_reference(module_ref_a)
            if module_ref_b is not None and hasattr(grad_b, 'attach_module_reference'):
                grad_b.attach_module_reference(module_ref_b)
            
            return grad_a, grad_b
    
    if not isinstance(a, Tensor):
        a = Tensor(a)
    if not isinstance(b, Tensor):
        b = Tensor(b)
    
    result = Mul.apply(a, b)
    
    if hasattr(a, '_module') and a._module is not None:
        if hasattr(result, 'attach_module_reference'):
            result.attach_module_reference(a._module)
    elif hasattr(b, '_module') and b._module is not None:
        if hasattr(result, 'attach_module_reference'):
            result.attach_module_reference(b._module)
    
    return result

def div(a, b):
    from .B3_autograd import Function
    
    class Div(Function):
        @staticmethod
        def forward(ctx, a, b):
            ctx.save_for_backward(a, b)
            a_data = a.data if hasattr(a, 'data') else a
            b_data = b.data if hasattr(b, 'data') else b
            
            eps = 1e-12
            b_data_safe = np.where(np.abs(b_data) < eps, 
                                   np.sign(b_data) * eps, 
                                   b_data)
            
            result = a_data / b_data_safe
            
            return result
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            
            a, b = ctx.saved_tensors
            a_data = a.data if hasattr(a, 'data') else a
            b_data = b.data if hasattr(b, 'data') else b
            
            eps = 1e-12
            b_data_safe = np.where(np.abs(b_data) < eps, 
                                   np.sign(b_data) * eps, 
                                   b_data)
            
            grad_a = grad_output * (1.0 / b_data_safe)
            grad_b = grad_output * (-a_data / (b_data_safe * b_data_safe))
            
            if np.any(np.isnan(grad_a)) or np.any(np.isinf(grad_a)):
                grad_a = np.nan_to_num(grad_a, nan=0.0, posinf=1e6, neginf=-1e6)
            if np.any(np.isnan(grad_b)) or np.any(np.isinf(grad_b)):
                grad_b = np.nan_to_num(grad_b, nan=0.0, posinf=1e6, neginf=-1e6)
            
            return grad_a, grad_b
    
    return Div.apply(a, b)

def matmul(a, b):
    from .B16_tensor import Tensor
    if not isinstance(a, Tensor):
        a = Tensor(a)
    if not isinstance(b, Tensor):
        b = Tensor(b)
    from .B3_autograd import Function
    
    class MatMul(Function):
        @staticmethod
        def forward(ctx, a, b):
            ctx.save_for_backward(a, b)
            a_data = a.data if hasattr(a, 'data') else a
            b_data = b.data if hasattr(b, 'data') else b
            result = np.matmul(a_data, b_data)
            return Tensor(result, requires_grad=a.requires_grad or b.requires_grad)
        
        @staticmethod
        def backward(ctx, grad_output):
            a, b = ctx.saved_tensors
            grad_a = np.matmul(grad_output.data, b.data.T)
            grad_b = np.matmul(a.data.T, grad_output.data)
            def assign_grad(tensor, grad):
                visited = set()
                while hasattr(tensor, '_base') and tensor._base is not None and id(tensor) not in visited:
                    visited.add(id(tensor))
                    tensor = tensor._base
                if getattr(tensor, 'grad', None) is None:
                    setattr(tensor, 'grad', Tensor(grad))
                else:
                    setattr(tensor, 'grad', getattr(tensor, 'grad') + Tensor(grad))
            if hasattr(a, '_base') and a._base is not None:
                assign_grad(a, grad_a)
            if hasattr(b, '_base') and b._base is not None:
                assign_grad(b, grad_b)
            return grad_a, grad_b
    
    result = MatMul.apply(a, b)
    
    if hasattr(a, '_module') and a._module is not None:
        if hasattr(result, 'attach_module_reference'):
            result.attach_module_reference(a._module)
    elif hasattr(b, '_module') and b._module is not None:
        if hasattr(result, 'attach_module_reference'):
            result.attach_module_reference(b._module)
    
    return result

def pow(x, exponent):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Pow(Function):
        @staticmethod
        def forward(ctx, base, exp):
            ctx.save_for_backward(base, exp)
            
            base_data = base.data if hasattr(base, 'data') else base
            exp_data = exp.data if hasattr(exp, 'data') else exp
            
            base_data = np.asarray(base_data, dtype=np.float32)
            exp_data = np.asarray(exp_data, dtype=np.float32)
            
            result = np.power(base_data, exp_data)

            return result
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            
            base, exp = ctx.saved_tensors
            
            base_data = base.data if hasattr(base, 'data') else base
            exp_data = exp.data if hasattr(exp, 'data') else exp
            grad_output_data = grad_output.data if hasattr(grad_output, 'data') else grad_output
            
            base_data = np.asarray(base_data, dtype=np.float32)
            exp_data = np.asarray(exp_data, dtype=np.float32)
            grad_output_data = np.asarray(grad_output_data, dtype=np.float32)
            
            eps = 1e-6
            
            safe_base = np.maximum(np.abs(base_data), eps)
            
            try:
                grad_base = grad_output_data * exp_data * np.power(safe_base, exp_data - 1)
                if np.any(base_data < 0):
                    sign = np.sign(base_data)
                    grad_base = grad_base * sign
                
                safe_log = np.log(safe_base)
                grad_exp = grad_output_data * np.power(safe_base, exp_data) * safe_log
                
                grad_base = np.nan_to_num(grad_base, nan=0.0, posinf=0.0, neginf=0.0)
                grad_exp = np.nan_to_num(grad_exp, nan=0.0, posinf=0.0, neginf=0.0)
            except:
                print("error: pow failed")
                grad_base = np.zeros_like(base_data)
                grad_exp = np.zeros_like(exp_data)
            
            return grad_base, grad_exp
    
    if hasattr(exponent, '_data'): 
        return Pow.apply(x, exponent)
    else:
        return Pow.apply(x, Tensor(exponent))

def exp(x):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Exp(Function):
        @staticmethod
        def forward(ctx, x):
            x_data = np.asarray(x.data, dtype=np.float32)
            
            max_val = 88.0  
            x_clipped = np.clip(x_data, -max_val, max_val)
            
            result = np.exp(x_clipped)
            
            ctx.save_for_backward(Tensor(result))
            return result
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            
            exp_x, = ctx.saved_tensors
            return grad_output * exp_x
    
    return Exp.apply(x)

def log(x):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Log(Function):
        @staticmethod
        def forward(ctx, x):
            x_data = x.data if hasattr(x, 'data') else x
            
            eps = 1e-12
            x_safe = np.maximum(x_data, eps)
            
            ctx.save_for_backward(Tensor(x_safe))
            return np.log(x_safe)
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            
            x_safe, = ctx.saved_tensors
            return grad_output / x_safe
    
    return Log.apply(x)

def softmax(x, dim=-1):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Softmax(Function):
        @staticmethod
        def forward(ctx, x, dim):
            x_data = x.data if hasattr(x, 'data') else x
            
            if dim < 0:
                dim = len(x_data.shape) + dim
                
            max_val = np.max(x_data, axis=dim, keepdims=True)
            
            shifted_x = x_data - max_val
            
            shifted_x = np.clip(shifted_x, -88.0, 88.0)  
            
            exp_x = np.exp(shifted_x)
            
            sum_exp = np.sum(exp_x, axis=dim, keepdims=True)
            sum_exp = np.maximum(sum_exp, 1e-12)  
            
            output = exp_x / sum_exp

            ctx.save_for_backward(Tensor(output))
            ctx.metadata['dim'] = dim 
            
            return output
        
        @staticmethod
        def backward(ctx, grad_output):
            output, = ctx.saved_tensors
            dim = ctx.metadata['dim']  
            
            grad = output * (grad_output - (grad_output * output).sum(dim=dim, keepdim=True))
 
            return grad
    
    return Softmax.apply(x, dim)

def reshape(x, shape):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Reshape(Function):
        @staticmethod
        def forward(ctx, x, new_shape):
            ctx.save_for_backward(x.shape)
            x_data = x.data if hasattr(x, 'data') else x
            result = np.reshape(x_data, new_shape)
            return Tensor(result, requires_grad=x.requires_grad)
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            
            original_shape, = ctx.saved_tensors
            grad_data = grad_output.data if hasattr(grad_output, 'data') else grad_output
            return np.reshape(grad_data, original_shape)
    
    if not isinstance(x, Tensor):
        x = Tensor(x)
    
    return Reshape.apply(x, shape)

def transpose(x, axes=None):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Transpose(Function):
        @staticmethod
        def forward(ctx, x, axes):
            ctx.save_for_backward(x.shape, axes)
            if axes is None:
                result = x.data.T
            elif isinstance(axes, tuple):
                result = np.transpose(x.data, axes)
            else:
                result = np.transpose(x.data, axes)
            t = Tensor(result, requires_grad=x.requires_grad)
            t._base = x 
            return t
        @staticmethod
        def backward(ctx, grad_output):
            original_shape, axes = ctx.saved_tensors
            if axes is None:
                grad = grad_output.data.T
            else:
                if isinstance(axes, tuple):
                    inv_axes = tuple(np.argsort(axes))
                else:
                    inv_axes = np.argsort([axes])
                grad = np.transpose(grad_output.data, inv_axes)
            grad_tensor = Tensor(grad)
            out = grad_tensor
            if hasattr(ctx, 'input_tensors'):
                base = getattr(ctx.input_tensors[0], '_base', None)
            else:
                base = None
            return grad_tensor, None
    return Transpose.apply(x, axes)

def my_max(x_np, dim=None, keepdim=False):

    import numpy as np
    
    if not isinstance(x_np, np.ndarray):
        x_np = np.array(x_np)
    
    if dim is None:
        max_val = float('-inf')
        max_idx = 0
        for i, val in enumerate(x_np.flat):
            if val > max_val:
                max_val = val
                max_idx = i
        return np.array(max_val), np.array(max_idx)
    else:
        shape = x_np.shape
        if keepdim:
            result = np.zeros(shape)
            indices = np.zeros(shape, dtype=np.int64)
        else:
            new_shape = list(shape)
            new_shape.pop(dim)
            result = np.zeros(new_shape)
            indices = np.zeros(new_shape, dtype=np.int64)
        
        for idx in np.ndindex(*shape):
            if idx[dim] == 0:
                max_val = x_np[idx]
                max_idx = 0
            elif x_np[idx] > max_val:
                max_val = x_np[idx]
                max_idx = idx[dim]
            if idx[dim] == shape[dim] - 1:
                if keepdim:
                    result[idx] = max_val
                    indices[idx] = max_idx
                else:
                    new_idx = list(idx)
                    new_idx.pop(dim)
                    result[tuple(new_idx)] = max_val
                    indices[tuple(new_idx)] = max_idx
        return result, indices

def max(x, dim=None, keepdim=False):

    import numpy as np
    from .B16_tensor import Tensor

    if 'torch' in str(type(x)):
        x = Tensor(x.detach().cpu().numpy())
    elif not isinstance(x, Tensor):
        x = Tensor(x)

    x_data = x.data if hasattr(x, 'data') else x
    if not isinstance(x_data, np.ndarray):
        x_data = np.array(x_data)

    if dim is None:
        max_val = np.max(x_data)
        max_idx = np.argmax(x_data)
        max_val_arr = np.array([max_val], dtype=x_data.dtype)
        max_idx_arr = np.array([max_idx], dtype=np.int64)
        return max_val_arr, max_idx_arr
    else:
        max_val = np.max(x_data, axis=dim)
        max_idx = np.argmax(x_data, axis=dim)
        if keepdim:
            max_idx = np.expand_dims(max_idx, axis=dim)
        return max_val, max_idx

def sum(x, dim=None, keepdim=False):
    from .B3_autograd import Function
    
    class Sum(Function):
        @staticmethod
        def forward(ctx, x, dim, keepdim):
            ctx.save_for_backward(x.shape, dim, keepdim)
            axis = tuple(dim) if isinstance(dim, list) else dim
            x_data = x.data if hasattr(x, 'data') else x
            result = np.sum(x_data, axis=axis, keepdims=keepdim)
            return result
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            
            original_shape, dim, keepdim = ctx.saved_tensors
            if dim is None and not keepdim:
                grad_output = grad_output.reshape(-1)  
            return np.broadcast_to(grad_output, original_shape)
    
    return Sum.apply(x, dim, keepdim)

def cat(tensors, dim=0):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Cat(Function):
        @staticmethod
        def forward(ctx, tensors, dim):
            ctx.save_for_backward(tensors, dim)
            tensors_data = [t.data for t in tensors]
            axis = dim
            return np.concatenate(tensors_data, axis=axis)
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            
            tensors, dim = ctx.saved_tensors
            axis = dim
            grads = []
            idx = 0
            for t in tensors:
                size = t.shape[axis]
                grads.append(grad_output.take(indices=range(idx, idx + size), axis=axis))
                idx += size
            return grads, None
    
    return Cat.apply(tensors, dim)

def masked_fill(x, mask, value):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class MaskedFill(Function):
        @staticmethod
        def forward(ctx, x, mask, value):
            ctx.save_for_backward(mask)
            return np.where(mask, value, x)
        
        @staticmethod
        def backward(ctx, grad_output):
            mask, = ctx.saved_tensors
            return np.where(mask, 0, grad_output), None, None
    
    return MaskedFill.apply(x, mask, value)

def abs(x):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Abs(Function):
        @staticmethod
        def forward(ctx, x):
            ctx.save_for_backward(x)
            x_data = x.data if hasattr(x, 'data') else x
            return np.abs(x_data)
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            x, = ctx.saved_tensors
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            x_data = x.data if hasattr(x, 'data') else x
            return grad_output * np.sign(x_data)
    
    return Abs.apply(x)

def maximum(a, b):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Maximum(Function):
        @staticmethod
        def forward(ctx, a, b):
            ctx.module_ref_a = getattr(a, '_module', None)
            ctx.module_ref_b = getattr(b, '_module', None)
            
            ctx.save_for_backward(a, b)
            a_data = a.data if hasattr(a, 'data') else a
            b_data = b.data if hasattr(b, 'data') else b
            return np.maximum(a_data, b_data)
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            
            a, b = ctx.saved_tensors
            a_data = a.data if hasattr(a, 'data') else a
            b_data = b.data if hasattr(b, 'data') else b
            grad_a = grad_output * (a_data > b_data)
            grad_b = grad_output * (b_data >= a_data)
            
            module_ref_a = getattr(ctx, 'module_ref_a', None)
            module_ref_b = getattr(ctx, 'module_ref_b', None)
            
            from .B16_tensor import Tensor
            grad_a_tensor = Tensor(grad_a, requires_grad=False)
            grad_b_tensor = Tensor(grad_b, requires_grad=False)
            
            if module_ref_a is not None and hasattr(grad_a_tensor, 'attach_module_reference'):
                grad_a_tensor.attach_module_reference(module_ref_a)
            if module_ref_b is not None and hasattr(grad_b_tensor, 'attach_module_reference'):
                grad_b_tensor.attach_module_reference(module_ref_b)
                
            return grad_a, grad_b
    
    if not isinstance(a, Tensor):
        a = Tensor(a)
    if not isinstance(b, Tensor):
        b = Tensor(b)
    
    result = Maximum.apply(a, b)
    
    if hasattr(a, '_module') and a._module is not None:
        if hasattr(result, 'attach_module_reference'):
            result.attach_module_reference(a._module)
    elif hasattr(b, '_module') and b._module is not None:
        if hasattr(result, 'attach_module_reference'):
            result.attach_module_reference(b._module)
        
    return result

def minimum(a, b):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Minimum(Function):
        @staticmethod
        def forward(ctx, a, b):
            ctx.module_ref_a = getattr(a, '_module', None)
            ctx.module_ref_b = getattr(b, '_module', None)
            
            ctx.save_for_backward(a, b)
            a_data = a.data if hasattr(a, 'data') else a
            b_data = b.data if hasattr(b, 'data') else b
            return np.minimum(a_data, b_data)
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            
            a, b = ctx.saved_tensors
            a_data = a.data if hasattr(a, 'data') else a
            b_data = b.data if hasattr(b, 'data') else b
            grad_a = grad_output * (a_data < b_data)
            grad_b = grad_output * (b_data <= a_data)
            
            module_ref_a = getattr(ctx, 'module_ref_a', None)
            module_ref_b = getattr(ctx, 'module_ref_b', None)
            
            from .B16_tensor import Tensor
            grad_a_tensor = Tensor(grad_a, requires_grad=False)
            grad_b_tensor = Tensor(grad_b, requires_grad=False)
            
            if module_ref_a is not None and hasattr(grad_a_tensor, 'attach_module_reference'):
                grad_a_tensor.attach_module_reference(module_ref_a)
            if module_ref_b is not None and hasattr(grad_b_tensor, 'attach_module_reference'):
                grad_b_tensor.attach_module_reference(module_ref_b)
                
            return grad_a, grad_b
    
    if not isinstance(a, Tensor):
        a = Tensor(a)
    if not isinstance(b, Tensor):
        b = Tensor(b)
        
    result = Minimum.apply(a, b)
    
    if hasattr(a, '_module') and a._module is not None:
        if hasattr(result, 'attach_module_reference'):
            result.attach_module_reference(a._module)
    elif hasattr(b, '_module') and b._module is not None:
        if hasattr(result, 'attach_module_reference'):
            result.attach_module_reference(b._module)
        
    return result

def where(condition, x, y):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Where(Function):
        @staticmethod
        def forward(ctx, condition, x, y):
            ctx.save_for_backward(condition)
            condition_data = condition.data if hasattr(condition, 'data') else condition
            x_data = x.data if hasattr(x, 'data') else x
            y_data = y.data if hasattr(y, 'data') else y
            return np.where(condition_data, x_data, y_data)
        
        @staticmethod
        def backward(ctx, grad_output):
            condition, = ctx.saved_tensors
            condition_data = condition.data if hasattr(condition, 'data') else condition
            bool_condition = condition_data.astype(bool)
            return None, grad_output * bool_condition, grad_output * (~bool_condition)
    
    return Where.apply(condition, x, y)

def einsum(equation, *tensors):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Einsum(Function):
        @staticmethod
        def forward(ctx, equation, *arrays):
            ctx.save_for_backward(equation, [a.shape for a in arrays])
            arrays_data = [a.data if hasattr(a, 'data') else a for a in arrays]
            return np.einsum(equation, *arrays_data)
        
        @staticmethod
        def backward(ctx, grad_output):
            equation, shapes = ctx.saved_tensors
            grads = []
            for i, shape in enumerate(shapes):
                input_chars = equation.split('->')[0].split(',')[i]
                output_chars = equation.split('->')[1]
                grad_equation = f"{output_chars},...->{input_chars}" if output_chars != '' else f"...->{input_chars}"
                grad = np.einsum(grad_equation, grad_output, *[np.ones(s) for s in shapes[:i] + shapes[i+1:]])
                grads.append(grad)
            return (None,) + tuple(grads)
    
    return Einsum.apply(equation, *tensors)

def bmm(x, y):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Bmm(Function):
        @staticmethod
        def forward(ctx, a, b):
            ctx.save_for_backward(a, b)
            a_data = a.data if hasattr(a, 'data') else a
            b_data = b.data if hasattr(b, 'data') else b
            return np.einsum('bij,bjk->bik', a_data, b_data)
        
        @staticmethod
        def backward(ctx, grad_output):
            a, b = ctx.saved_tensors
            a_data = a.data if hasattr(a, 'data') else a
            b_data = b.data if hasattr(b, 'data') else b
            grad_a = np.einsum('bik,bjk->bij', grad_output, b_data)
            grad_b = np.einsum('bij,bik->bjk', a_data, grad_output)
            return grad_a, grad_b
    
    return Bmm.apply(x, y)

def conv2d(input, weight, bias=None, stride=(1,1), padding=(0,0)):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Conv2d(Function):
        @staticmethod
        def forward(ctx, input, weight, bias, stride, padding):
            input_data = input.data if hasattr(input, 'data') else input
            weight_data = weight.data if hasattr(weight, 'data') else weight
            bias_data = bias.data if hasattr(bias, 'data') and bias is not None else bias
            
            if input_data.ndim != 4 or weight_data.ndim != 4:
                raise ValueError
                
            N, C, H, W = input_data.shape
            F, C_, HH, WW = weight_data.shape
            
            if C != C_:
                raise ValueError
            
            SH, SW = stride
            PH, PW = padding
            
            H_out = (H + 2 * PH - HH) // SH + 1
            W_out = (W + 2 * PW - WW) // SW + 1
            
            input_pad = np.pad(input_data, ((0,0),(0,0),(PH,PH),(PW,PW)), mode='constant')
            
            cols = np.zeros((N, C, HH, WW, H_out, W_out))
            for h in range(HH):
                for w in range(WW):
                    cols[:, :, h, w, :, :] = input_pad[:, :, h:h+SH*H_out:SH, w:w+SW*W_out:SW]
            
            cols = cols.transpose(0,4,5,1,2,3).reshape(N*H_out*W_out, -1)
            weight_flat = weight_data.reshape(F, -1)
            
            output = cols @ weight_flat.T
            if bias_data is not None:
                output += bias_data
                
            output = output.reshape(N, H_out, W_out, F).transpose(0,3,1,2)
            
            ctx.save_for_backward(input, weight, bias, stride, padding, cols)
            return output
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
            
            input, weight, bias, stride, padding, cols = ctx.saved_tensors
            SH, SW = stride
            PH, PW = padding
            N, C, H, W = input.shape
            F, _, HH, WW = weight.shape
            _, _, H_out, W_out = grad_output.shape
            
            grad_output_flat = grad_output.transpose(0,2,3,1).reshape(-1, F)
            
            grad_weight = grad_output_flat.T @ cols
            grad_weight = grad_weight.reshape(weight.shape)
            
            grad_bias = grad_output_flat.sum(axis=0) if bias is not None else None
            
            weight_data = weight.data if hasattr(weight, 'data') else weight
            grad_cols = grad_output_flat @ weight_data.reshape(F, -1)
            grad_cols = grad_cols.reshape(N, H_out, W_out, C, HH, WW).transpose(0,3,4,5,1,2)
            
            input_data = input.data if hasattr(input, 'data') else input
            grad_input = np.zeros((N, C, H + 2*PH, W + 2*PW), dtype=input_data.dtype)
            for h in range(HH):
                for w in range(WW):
                    grad_input[:, :, h:h+SH*H_out:SH, w:w+SW*W_out:SW] += grad_cols[:, :, h, w, :, :]
            
            if PH > 0 or PW > 0:
                grad_input = grad_input[:, :, PH:-PH, PW:-PW] if PH > 0 and PW > 0 else \
                             grad_input[:, :, PH:-PH, :] if PH > 0 else \
                             grad_input[:, :, :, PW:-PW]
            
            return grad_input, grad_weight, grad_bias, None, None
    
    return Conv2d.apply(
        input, 
        weight, 
        bias.data if hasattr(bias, 'data') else bias, 
        stride, 
        padding
    )

def mean(x, dim=None, keepdim=False):

    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Mean(Function):
        @staticmethod
        def forward(ctx, x, dim, keepdim):
            if dim is not None:
                if isinstance(dim, int):
                    dim = [dim]
                dim = sorted([d if d >= 0 else x.ndim + d for d in dim])  
                
                for d in dim:
                    if d < 0 or d >= x.ndim:
                        raise ValueError
            
            ctx.save_for_backward(x.shape, dim, keepdim)
            
            axis = tuple(dim) if isinstance(dim, list) else dim
            result = np.mean(x.data, axis=axis, keepdims=keepdim)
            
            if not keepdim and result.ndim == 0:
                result = np.array([result])
                
            return result
        
        @staticmethod
        def backward(ctx, *args, **kwargs):
            original_shape, dim, keepdim = ctx.saved_tensors
            
            grad_output = kwargs.get('grad_outputs', args[0] if args else None)
                        
            grad_data = np.asarray(grad_output, dtype=np.float32) if not isinstance(grad_output, np.ndarray) else grad_output
            if hasattr(grad_output, 'data'):
                grad_data = np.asarray(grad_output.data, dtype=np.float32)

            if grad_data.ndim == 0:
                grad_data = np.array([grad_data])
            
            try:
                if dim is None:  
                    total_elements = np.prod(original_shape)
                    scalar_value = float(np.sum(grad_data)) / total_elements 
                    grad_input = np.full(original_shape, scalar_value)
                else:
                    if keepdim:
                        n_elements = np.prod([original_shape[d] for d in dim]) if isinstance(dim, (list, tuple)) else original_shape[dim]
                        grad_input = np.broadcast_to(grad_data / n_elements, original_shape)
                    else:

                        if len(grad_data.shape) == 1 and len(original_shape) == 2 and original_shape[0] == 1 and original_shape[1] == 1:
                            scalar_value = float(np.sum(grad_data)) / grad_data.size
                            grad_input = np.full(original_shape, scalar_value)
                           
                        else:
                            expand_shape = list(original_shape)
                            if isinstance(dim, (list, tuple)):
                                for d in dim:
                                    expand_shape[d] = 1
                            else:
                                expand_shape[dim] = 1
                            
                            try:
                               
                                if np.prod(grad_data.shape) > np.prod(expand_shape):
                                    grad_data = np.sum(grad_data.reshape(-1))
                                    grad_expanded = np.full(expand_shape, float(grad_data) / np.prod(original_shape))
                                elif np.prod(grad_data.shape) < np.prod(expand_shape):
                                    grad_expanded = np.broadcast_to(grad_data.reshape(-1), expand_shape)
                                else:
                                    grad_expanded = np.reshape(grad_data, expand_shape)
                                
                                grad_input = np.broadcast_to(grad_expanded, original_shape)
                                
                            except Exception as e:
                          
                                scalar_value = float(np.sum(grad_data)) / np.prod(original_shape)
                                grad_input = np.full(original_shape, scalar_value)
                                
            except Exception as e:

                grad_input = np.zeros(original_shape)
            
            if np.any(np.isnan(grad_input)):
         
                grad_input = np.nan_to_num(grad_input)
            
            if np.any(np.isinf(grad_input)):
    
                grad_input = np.clip(grad_input, -1e10, 1e10)
            
            return grad_input, None, None
    

    if not isinstance(x, Tensor):
        x = Tensor(x)
    
    
    return Mean.apply(x, dim, keepdim)

def sigmoid(x):
    from .B16_tensor import Tensor
    from .B3_autograd import Function
    
    class Sigmoid(Function):
        @staticmethod
        def forward(ctx, x):
            x_data = x.data if hasattr(x, 'data') else x
            x_clipped = np.clip(x_data, -15, 15) 
            output = 1 / (1 + np.exp(-x_clipped))
            
            ctx.save_for_backward(Tensor(output))
            return output
        
        @staticmethod
        def backward(ctx, grad_output):
            output, = ctx.saved_tensors
            grad = output * (1 - output) * grad_output
            return grad
    
    return Sigmoid.apply(x)

from .B3_autograd import Function

class IdentityFunction(Function):
    @staticmethod
    def forward(ctx, x):
        ctx.module_ref = getattr(x, '_module', None)
        return x
    
    @staticmethod
    def backward(ctx, grad_output):
        module_ref = getattr(ctx, 'module_ref', None)
        
        from .B16_tensor import Tensor
        if not isinstance(grad_output, Tensor):
            grad_output = Tensor(grad_output, requires_grad=False)
            
        if module_ref is not None and hasattr(grad_output, 'attach_module_reference'):
            grad_output.attach_module_reference(module_ref)
            
        return grad_output

def indexing(input_tensor, indices):
    
    class Index(Function):
        @staticmethod
        def forward(ctx, x, indices):
            ctx.save_for_backward(x)
            ctx.metadata = {
                'indices': indices,
                'input_shape': x.shape
            }
            result = x.data[indices]
            return result
        
        @staticmethod 
        def backward(ctx, grad_output):
            x, = ctx.saved_tensors
            indices = ctx.metadata['indices']
            input_shape = ctx.metadata['input_shape']
            
            grad_input_data = np.zeros(input_shape, dtype=grad_output.data.dtype)
            grad_input_data[indices] = grad_output.data
            from .B16_tensor import Tensor
            return Tensor(grad_input_data)
    
    return Index.apply(input_tensor, indices)
