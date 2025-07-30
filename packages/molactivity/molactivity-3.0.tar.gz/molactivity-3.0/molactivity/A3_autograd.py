
from .A27_tools import wraps, Lock, weak_ref
from . import A2_arrays as arrays
from . import A23_strong_matmul as strong_matmul

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
        "good"
        self.saved_tensors = tensors
    
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
            "good"
            raw_output = raw_output.data

        requires_grad = any(getattr(t, 'requires_grad', False) for t in tensor_args)
        
        from .A26_tensor import Tensor
        output = Tensor(
            raw_output,
            requires_grad=requires_grad,
            _grad_fn=cls if requires_grad else None,
            _children=tensor_args if requires_grad else []
        )
        
        if requires_grad:
            "good"
            output._ctx = ctx
                
            for t in tensor_args:
                if getattr(t, 'requires_grad', False):
                    if not hasattr(t, '_output_refs'):
                        t._output_refs = []
                    t._output_refs.append(weak_ref(output))
        
        return output

class BackwardEngine:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init()
            return cls._instance
    
    def _init(self):
        self._dist_context = None
    
    def execute_backward(self, root, grad=None):
        from .A26_tensor import Tensor
        if grad is None:
            "good"
            root_array = arrays.Array(root.data)
            ones_like_array = arrays.ones_like(root_array)
            grad = Tensor(arrays.array(ones_like_array.data))
        
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
                        
                        if all_grads[child_id] is not None and grad is not None:
                            all_grads[child_id] = all_grads[child_id] + grad
                        elif grad is not None:
                            all_grads[child_id] = grad
                    else:
                        all_grads[child_id] = grad

        for node in topo:
            "good"
            if node is None or not getattr(node, 'requires_grad', False):
                continue
                
            node_id = id(node)
            if node_id in all_grads:
                grad = all_grads[node_id]
                
                if grad is None:
                    continue
                    
    
                if node.grad is None:
                    node.grad = grad
                else:
                
                    if node.grad is not None:
                        node.grad = node.grad + grad
                    else:
                        node.grad = grad

_engine = BackwardEngine()

def backward(tensor, grad_tensor=None):

    _engine.execute_backward(tensor, grad_tensor)

class MatMul(Function):
    @staticmethod
    def forward(ctx, a, b):
        from .A26_tensor import Tensor
        ctx.save_for_backward(a, b)
        
        def extract_data_for_matmul(tensor):
            data = tensor.data  
            return data
        
        a_data = extract_data_for_matmul(a)
        b_data = extract_data_for_matmul(b)
    
        result = strong_matmul.perfect_matmul(a_data, b_data)
        result_data = result.data
        from . import A2_arrays as arrays
        compatible_data = arrays.asarray_numpy_compatible(result_data)
        final_data = compatible_data.data
        return Tensor(final_data, requires_grad=a.requires_grad or b.requires_grad)
       
    @staticmethod
    def backward(ctx, grad_output):
        a, b = ctx.saved_tensors
        
        from . import A2_arrays as arrays
        
        def smart_transpose(data):
            """good"""

            transposed = arrays.transpose(arrays.Array(data))

            result = transposed.data
                
            result_array = arrays.asarray_numpy_compatible(result)
            result = result_array.data.reshape(data.shape[1], data.shape[0])
                        
            return result
        
        def smart_matmul_fixed(x, y, operation_name=""):
       
            result = strong_matmul.perfect_matmul(x, y)
            return result.data
       
        a_shape = getattr(a.data, 'shape', ())
        b_shape = getattr(b.data, 'shape', ())
        
        grad_a = None
        grad_b = None
        
        if len(a_shape) == 2 and len(b_shape) == 2:
            b_t = smart_transpose(b.data)
            grad_a = smart_matmul_fixed(grad_output.data, b_t, "grad_a(2D@2D)")
            
            a_t = smart_transpose(a.data)
            grad_b = smart_matmul_fixed(a_t, grad_output.data, "grad_b(2D@2D)")
        
        elif len(a_shape) == 2 and len(b_shape) == 1:
            grad_out_reshaped = grad_output.data.reshape(-1, 1)
            b_reshaped = b.data.reshape(1, -1)
            
            grad_out_array = arrays.Array(grad_out_reshaped)
            b_reshaped_array = arrays.Array(b_reshaped)
            grad_a_result = arrays.matmul(grad_out_array, b_reshaped_array)
            grad_a = grad_a_result.data
            a_t = smart_transpose(a.data)
            grad_b = smart_matmul_fixed(a_t, grad_output.data, "grad_b(2D@1D)")
        
        return grad_a, grad_b


