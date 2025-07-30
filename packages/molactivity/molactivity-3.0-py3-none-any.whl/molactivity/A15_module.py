
class Module:
    def __init__(self):
        self._parameters = {}
        self._modules = {}
        self._buffers = {}
        self._is_training = True

    def __call__(self, *args, **kwargs):
        result = self.forward(*args, **kwargs)
        
        if hasattr(result, 'attach_module_reference'):
            result.attach_module_reference(self)
        
        return result

    def forward(self, *args, **kwargs):
        
        raise NotImplementedError

    def register_parameter(self, name, param):
        
        if param is None:
            self._parameters[name] = None
        else:
            
            param._module = self
            param.requires_grad = True
            self._parameters[name] = param

    def register_buffer(self, name, tensor):
        self._buffers[name] = tensor

    def add_module(self, name, module):
        self._modules[name] = module

    def train(self, mode=True):
        self._is_training = mode
        for module in self.children():
            module.train(mode)
        return self

    def eval(self):
        return self.train(False)

    def requires_grad_(self, requires_grad=True):
        for param in self.parameters():
            param.requires_grad = requires_grad
        return self

    def zero_grad(self):
        for param in self.parameters():
            if param.grad is not None:
                param.grad.zero_()

    def parameters(self):
        for name, param in self.named_parameters():
            yield param

    def named_parameters(self, prefix=''):
        for name, param in self._parameters.items():
            if param is not None:
                yield prefix + ('.' if prefix else '') + name, param

        for mname, module in self._modules.items():
            for name, param in module.named_parameters(prefix=prefix + ('.' if prefix else '') + mname):
                yield name, param

    def children(self):
        for _, module in self._modules.items():
            yield module

    def named_children(self):
        for name, module in self._modules.items():
            yield name, module

    def state_dict(self):
        def make_pickle_safe(data):
            if hasattr(data, '__class__') and data.__class__.__name__ == 'FinalArrayCompatible':
                return {
                    '__type__': 'FinalArrayCompatible',
                    'data': data._data,
                    'shape': data._shape,
                    'dtype': data._dtype
                }
            elif hasattr(data, 'tolist'):
                return data.tolist()
            elif hasattr(data, 'copy'):
                return data.copy()
            elif isinstance(data, (list, tuple)):
                return data.copy() if hasattr(data, 'copy') else list(data)
            else:
                return data
        
        state = {}
        for name, param in self._parameters.items():
            if param is not None and hasattr(param, 'data'):
                state[name] = make_pickle_safe(param.data)
        for name, buf in self._buffers.items():
            if buf is not None and hasattr(buf, 'data'):
                state[name] = make_pickle_safe(buf.data)
        for name, module in self._modules.items():
            if hasattr(module, 'state_dict'):
                state[name] = module.state_dict()
        return state

    def load_state_dict(self, state_dict):
        for name, param in self._parameters.items():
            if param is not None and name in state_dict:
                param.data = state_dict[name]
        
        for name, buf in self._buffers.items():
            if buf is not None and name in state_dict:
                buf.data = state_dict[name]
        
        for name, module in self._modules.items():
            if name in state_dict and hasattr(module, 'load_state_dict'):
                module.load_state_dict(state_dict[name])

    def named_buffers(self, prefix=''):
        for name, buf in self._buffers.items():
            if buf is not None:
                yield prefix + ('.' if prefix else '') + name, buf

        for mname, module in self._modules.items():
            for name, buf in module.named_buffers(prefix=prefix + ('.' if prefix else '') + mname):
                yield name, buf

    def buffers(self):
        for name, buf in self.named_buffers():
            yield buf

    def __setattr__(self, name, value):
        from .A26_tensor import Tensor

        if isinstance(value, Tensor) and name != '_parameters' and name != '_buffers' and name != '_modules':
            value._module = self
            value.requires_grad = True
            self.register_parameter(name, value)
        
        elif isinstance(value, Module) and name != '_parameters' and name != '_buffers' and name != '_modules':
            self.add_module(name, value)
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        if '_parameters' in self.__dict__:
            _parameters = self.__dict__['_parameters']
            if name in _parameters:
                return _parameters[name]
        if '_buffers' in self.__dict__:
            _buffers = self.__dict__['_buffers']
            if name in _buffers:
                return _buffers[name]
        if '_modules' in self.__dict__:
            _modules = self.__dict__['_modules']
            if name in _modules:
                return _modules[name]
        raise AttributeError

    def create_parameter_index(self):
 
        self._param_index = {}
        
        shape_index = {}
        for name, param in self.named_parameters():
            shape_key = str(param.shape)
            if shape_key not in shape_index:
                shape_index[shape_key] = []
            shape_index[shape_key].append((name, param))
            
            self._param_index[id(param)] = (name, param)
        
        self._param_index['by_shape'] = shape_index
        
        return self._param_index
    
    def find_parameters_by_shape(self, shape):

        if not hasattr(self, '_param_index'):
            self.create_parameter_index()
            
        shape_key = str(shape)
        shape_index = self._param_index.get('by_shape', {})
        
        exact_matches = shape_index.get(shape_key, [])
        if exact_matches:
            return exact_matches
            
        candidate_params = []
        for param_name, param in self.named_parameters():
            if len(param.shape) == len(shape):
                compatible = True
                for dim_param, dim_shape in zip(param.shape, shape):
                    if dim_param != dim_shape and dim_param != 1 and dim_shape != 1:
                        compatible = False
                        break
                if compatible:
                    candidate_params.append((param_name, param))
                    
        return candidate_params

class ModuleList(Module):
    def __init__(self, modules=None):
        super(ModuleList, self).__init__()
        if modules is not None:
            for i, module in enumerate(modules):
                self.add_module(str(i), module)

    def __iter__(self):
        return iter(self._modules.values())

    def __len__(self):
        return len(self._modules)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return ModuleList([self._modules[str(i)] for i in range(len(self))[idx]])
        else:
            return self._modules[str(idx)]

    def append(self, module):
        self.add_module(str(len(self)), module)
        return self

    def extend(self, modules):
        for module in modules:
            self.append(module)
        return self

    def forward(self, x):
        for module in self:
            x = module(x)
        return x

class Sequential(Module):
    
    def __init__(self, *modules):

        super().__init__()
        self.modules_list = []
        for idx, module in enumerate(modules):
            self.add_module(str(idx), module)
            self.modules_list.append(module)
    
    def add_module(self, name, module):

        if not (isinstance(module, Module) or callable(module)):
            raise TypeError
            
        setattr(self, name, module)
        
        if isinstance(module, Module):
            self._modules[name] = module
    
    def forward(self, x):

        for module in self.modules_list:
            if isinstance(module, Module):
                if hasattr(module, 'forward'):
                    x = module.forward(x)
                else:
                    raise AttributeError
            elif callable(module):
                x = module(x)
            else:
                raise TypeError
        return x
    
    def __call__(self, x):
        return self.forward(x)
    
    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return Sequential(*self.modules_list[idx])
        else:
            return self.modules_list[idx]
    
    def __len__(self):
        return len(self.modules_list)
    
    def __iter__(self):
        return iter(self.modules_list)
    
    def __repr__(self):
        module_str = ', '.join(repr(m) for m in self.modules_list)
        return f"Sequential({module_str})"
        
    def train(self, mode=True):
        self.training = mode
        for module in self.modules_list:
            if isinstance(module, Module) and hasattr(module, 'train'):
                module.train(mode)
        return self
        
    def eval(self):
        return self.train(False)
