
import numpy as np
import weakref
import threading
from functools import wraps
from enum import Enum, auto

class GradMode(Enum):

    TRAINING = auto()
    INFERENCE = auto()

class Context:
    __slots__ = ['saved_tensors', 'non_differentiable', 'metadata', 'module_ref', 'module_ref_a', 'module_ref_b', 'module_refs']
    
    def __init__(self):
        self.saved_tensors = None  
        self.non_differentiable = set()
        self.metadata = {}
        self.module_ref = None
        self.module_ref_a = None
        self.module_ref_b = None
        self.module_refs = {}  
    
    def save_for_backward(self, *tensors):  

        self.saved_tensors = tensors
    
    def mark_non_differentiable(self, *tensors):  

        self.non_differentiable.update(id(t) for t in tensors)

class FunctionMeta(type):

    _registry = {}
    
    def __new__(mcls, name, bases, attrs):

        for method in ['forward', 'backward']:
            if method in attrs:
                attrs[method] = FunctionMeta._wrap_method(attrs[method])
        cls = super().__new__(mcls, name, bases, attrs)
        if name != 'Function':
            mcls._registry[name] = cls
        return cls
    
    @staticmethod
    def _wrap_method(method):

        @wraps(method)
        def wrapper(ctx, *args, **kwargs):
            return method(ctx, *args, **kwargs)
        return staticmethod(wrapper)

class Function(metaclass=FunctionMeta):

    __slots__ = ['requires_grad', 'ctx']
    
    @staticmethod
    def forward(ctx, *args):

        raise NotImplementedError
    
    @staticmethod
    def backward(ctx, *grad_outputs):

        raise NotImplementedError
    
    @classmethod
    def apply(cls, *args, **kwargs):

        
        def is_tensor(obj):
            return hasattr(obj, '_data') and hasattr(obj, 'requires_grad')
        
        ctx = Context()
        tensor_args = []
        processed_args = []
        
        source_module = None
        module_refs = {}
        
        for i, arg in enumerate(args):
            if is_tensor(arg):
                if hasattr(arg, '_module') and arg._module is not None:
                    module_refs[i] = arg._module
                    if source_module is None:
                        source_module = arg._module
        
        for i, arg in enumerate(args):
            if is_tensor(arg):
                tensor_args.append(arg)
                processed_args.append(arg) 
            else:
                processed_args.append(arg)
        
        ctx.module_ref = source_module
        ctx.module_refs = module_refs
        
        raw_output = cls.forward(ctx, *processed_args, **kwargs)
        if hasattr(raw_output, '_data') and hasattr(raw_output, 'data'):
            raw_output = raw_output.data
        elif not isinstance(raw_output, (np.ndarray, np.generic)):
            raw_output = np.array(raw_output, dtype=np.float32)
        
        if _engine._grad_mode == GradMode.INFERENCE:
            requires_grad = False
        else:
            requires_grad = any(getattr(t, 'requires_grad', False) for t in tensor_args)
            if 'requires_grad' in kwargs:
                requires_grad = kwargs['requires_grad']
        
        from .B16_tensor import Tensor
        output = Tensor(
            raw_output,
            requires_grad=requires_grad,
            _grad_fn=cls if requires_grad else None,
            _children=tensor_args if requires_grad else []
        )
        
        if source_module is not None and hasattr(output, 'attach_module_reference'):
            output.attach_module_reference(source_module)
        
        if requires_grad:
            output._ctx = ctx
                
            for t in tensor_args:
                if getattr(t, 'requires_grad', False):
                    if not hasattr(t, '_output_refs'):
                        t._output_refs = []
                    t._output_refs.append(weakref.ref(output))
        
        return output

class DistAutogradContext:

    def __init__(self):
        self._worker_id = 0
        self._contexts = {}

class BackwardEngine:
    _instance = None
    _lock = threading.Lock()
    _grad_mode = GradMode.TRAINING
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init()
            return cls._instance
    
    def _init(self):
        self._dist_context = None
    
    def _compute_backward(self, func, *args, grad_outputs):
        from .B16_tensor import Tensor
        try:
            for grad in (grad_outputs if isinstance(grad_outputs, (tuple, list)) else [grad_outputs]):
                if grad is not None and (np.isnan(grad.data).any() or np.isinf(grad.data).any()):
                    print("Warning: Invalid gradient in backward computation")
                    return tuple(Tensor(np.zeros_like(arg.data)) for arg in args)
            
            if isinstance(grad_outputs, (tuple, list)):
                grads = func.backward(*args, *grad_outputs)
            else:
                grads = func.backward(*args, grad_outputs)
            
            if grads is None:
                return tuple(None for _ in args)
            
            if not isinstance(grads, tuple):
                grads = (grads,)
            
            valid_grads = []
            for grad, arg in zip(grads, args):
                if grad is None:
                    valid_grads.append(None)
                elif np.isnan(grad.data).any() or np.isinf(grad.data).any():
                    print("Warning: Invalid gradient after backward computation")
                    valid_grads.append(Tensor(np.zeros_like(arg.data)))
                else:
                    valid_grads.append(grad)
            
            return tuple(valid_grads)
            
        except Exception as e:
            print(f"Error in backward computation: {str(e)}")
            return tuple(Tensor(np.zeros_like(arg.data)) for arg in args)
    
    def execute_backward(self, root, grad=None):
        from .B16_tensor import Tensor
        if grad is None:
            grad = Tensor(np.ones_like(root.data))
        
        all_grads = {}
        all_grads[id(root)] = grad
        
        visited = set()
        topo = []
        
        def build_topo(node):
            if id(node) in visited or node is None:
                return
            visited.add(id(node))
            if hasattr(node, '_children'):
                for child in node._children:
                    if child is not None:
                        build_topo(child)
            topo.append(node)
        
        build_topo(root)
        
        for node in reversed(topo):
            if node is None or not hasattr(node, '_grad_fn') or node._grad_fn is None:
                continue
                
            node_grad = all_grads.get(id(node))
            if node_grad is None:
                continue
            
            ctx = getattr(node, '_ctx', None)
            if ctx is None:
                continue
                
            try:
                grads = node._grad_fn.backward(ctx, node_grad)
                
                if grads is not None:
                    if not isinstance(grads, tuple):
                        grads = (grads,)
                    
                    children = getattr(node, '_children', [])
                    for i, (child, grad) in enumerate(zip(children, grads)):
                        if child is None or grad is None:
                            continue
                            
                        if not isinstance(grad, Tensor):
                            grad = Tensor(grad)
                        
                        child_id = id(child)
                        if child_id in all_grads:
                            all_grads[child_id] = all_grads[child_id] + grad
                        else:
                            all_grads[child_id] = grad
                            
            except Exception as e:
                import traceback
                traceback.print_exc()
        
        for node in topo:
            if node is None or not getattr(node, 'requires_grad', False):
                continue
                
            node_id = id(node)
            if node_id in all_grads:
                grad = all_grads[node_id]
                if node.grad is None:
                    node.grad = grad
                else:
                    node.grad = node.grad + grad

_engine = BackwardEngine()

def backward(tensor, grad_tensor=None):

    _engine.execute_backward(tensor, grad_tensor)

def enable_grad():
 
    return GradModeGuard(GradMode.TRAINING)

def no_grad():

    return GradModeGuard(GradMode.INFERENCE)

class GradModeGuard:
  
    __slots__ = ['prev_mode']
    
    def __init__(self, mode):
  
        self.prev_mode = _engine._grad_mode
        _engine._grad_mode = mode
    
    def __enter__(self):
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        _engine._grad_mode = self.prev_mode

class FunctionRegistry:

    _custom_funcs = {}
    
    @classmethod
    def register(cls, name, forward, backward):

        class CustomFunction(Function):
            @staticmethod
            def forward(ctx, *args, **kwargs):
                return forward(ctx, *args, **kwargs)
            
            @staticmethod
            def backward(ctx, *grad_outputs):
                return backward(ctx, *grad_outputs)
        
        CustomFunction.__name__ = name
        cls._custom_funcs[name] = CustomFunction
    
    @classmethod
    def get(cls, name):
 
        return cls._custom_funcs[name]

def checkpoint(func, *args):

    class CheckpointFunction(Function):
        @staticmethod
        def forward(ctx, func, *args):
            ctx.save_for_backward(func, *args)
            with no_grad():
                return func(*args)
        
        @staticmethod
        def backward(ctx, *grad_outputs):
            func, *args = ctx.saved_tensors
            return (None,) + _engine._compute_backward(func, *args, *grad_outputs)
    
    return CheckpointFunction.apply(func, *args)

class MatMul(Function):
    @staticmethod
    def forward(ctx, a, b):
        from .B16_tensor import Tensor
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
        return grad_a, grad_b 

def matmul(self, other):
    from .B16_tensor import Tensor
    if not isinstance(other, Tensor):
        other = Tensor(other)
    return MatMul.apply(self, other)

__all__ = [
    'Function', 'backward', 'no_grad', 'enable_grad',
    'checkpoint', 'FunctionRegistry'
]
