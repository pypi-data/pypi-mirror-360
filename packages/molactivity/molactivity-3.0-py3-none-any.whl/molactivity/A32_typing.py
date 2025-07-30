
class _GenericAlias:
    def __init__(self, origin, args):
        self._origin = origin
        self._args = args if isinstance(args, tuple) else (args,)
    
    def __repr__(self):
        if self._origin is Union:
            if len(self._args) == 2 and type(None) in self._args:
                non_none_arg = next(arg for arg in self._args if arg is not type(None))
                return f"Optional[{non_none_arg.__name__ if hasattr(non_none_arg, '__name__') else repr(non_none_arg)}]"
            else:
                args_str = ', '.join(arg.__name__ if hasattr(arg, '__name__') else repr(arg) for arg in self._args)
                return f"Union[{args_str}]"
        elif self._origin is tuple:
            if not self._args:
                return "Tuple[()]"
            args_str = ', '.join(arg.__name__ if hasattr(arg, '__name__') else repr(arg) for arg in self._args)
            return f"Tuple[{args_str}]"
        else:
            origin_name = self._origin.__name__ if hasattr(self._origin, '__name__') else repr(self._origin)
            args_str = ', '.join(arg.__name__ if hasattr(arg, '__name__') else repr(arg) for arg in self._args)
            return f"{origin_name}[{args_str}]"
    
    def __str__(self):
        return self.__repr__()
    
    def __eq__(self, other):
        if not isinstance(other, _GenericAlias):
            return False
        return self._origin == other._origin and self._args == other._args
    
    def __hash__(self):
        return hash((self._origin, self._args))
    
    def __getitem__(self, item):
        if isinstance(item, tuple):
            return _GenericAlias(self._origin, self._args + item)
        else:
            return _GenericAlias(self._origin, self._args + (item,))

class _UnionType:
    def __getitem__(self, args):
        if not isinstance(args, tuple):
            args = (args,)
        return _GenericAlias(Union, args)
    
    def __repr__(self):
        return "Union"
    
    def __str__(self):
        return "Union"

class _TupleType:
    def __getitem__(self, args):
        if not isinstance(args, tuple):
            args = (args,)
        return _GenericAlias(tuple, args)
    
    def __repr__(self):
        return "Tuple"
    
    def __str__(self):
        return "Tuple"

class _ListType:
    def __getitem__(self, arg):
        return _GenericAlias(list, (arg,))
    
    def __repr__(self):
        return "List"
    
    def __str__(self):
        return "List"

class _DictType:
    def __getitem__(self, args):
        if not isinstance(args, tuple) or len(args) != 2:
            raise TypeError
        return _GenericAlias(dict, args)
    
    def __repr__(self):
        return "Dict"
    
    def __str__(self):
        return "Dict"

class _SetType:
    def __getitem__(self, arg):
        return _GenericAlias(set, (arg,))
    
    def __repr__(self):
        return "Set"
    
    def __str__(self):
        return "Set"

class _CallableType:
    def __getitem__(self, args):
        if not isinstance(args, tuple):
            args = (args,)
        return _GenericAlias(Callable, args)
    
    def __repr__(self):
        return "Callable"
    
    def __str__(self):
        return "Callable"

class _IterableType:
    def __getitem__(self, arg):
        return _GenericAlias(Iterable, (arg,))
    
    def __repr__(self):
        return "Iterable"
    
    def __str__(self):
        return "Iterable"

class _IteratorType:
    def __getitem__(self, arg):
        return _GenericAlias(Iterator, (arg,))
    
    def __repr__(self):
        return "Iterator"
    
    def __str__(self):
        return "Iterator"

class _GeneratorType:
    def __getitem__(self, args):
        if not isinstance(args, tuple):
            args = (args,)
        return _GenericAlias(Generator, args)
    
    def __repr__(self):
        return "Generator"
    
    def __str__(self):
        return "Generator"

class _AnyType:
    def __repr__(self):
        return "Any"
    
    def __str__(self):
        return "Any"
    
    def __eq__(self, other):
        return True  
    
    def __hash__(self):
        return hash("Any")

class _NoReturnType:
    def __repr__(self):
        return "NoReturn"
    
    def __str__(self):
        return "NoReturn"

class _OptionalType:
    def __getitem__(self, arg):
        return _GenericAlias(Union, (arg, type(None)))
    
    def __repr__(self):
        return "Optional"
    
    def __str__(self):
        return "Optional"

class _TypeVarType:
    def __init__(self, name, *constraints, bound=None, covariant=False, contravariant=False):
        self.name = name
        self.constraints = constraints
        self.bound = bound
        self.covariant = covariant
        self.contravariant = contravariant
    
    def __repr__(self):
        return f"TypeVar('{self.name}')"
    
    def __str__(self):
        return self.name

Union = _UnionType()
Tuple = _TupleType()
List = _ListType()
Dict = _DictType()
Set = _SetType()
Callable = _CallableType()
Iterable = _IterableType()
Iterator = _IteratorType()
Generator = _GeneratorType()
Any = _AnyType()
NoReturn = _NoReturnType()
Optional = _OptionalType()  

def TypeVar(name, *constraints, bound=None, covariant=False, contravariant=False):
    return _TypeVarType(name, *constraints, bound=bound, covariant=covariant, contravariant=contravariant)

def get_origin(tp):
    if isinstance(tp, _GenericAlias):
        return tp._origin
    return None

def get_args(tp):
    if isinstance(tp, _GenericAlias):
        return tp._args
    return ()

def get_type_hints(obj, globalns=None, localns=None):
    if hasattr(obj, '__annotations__'):
        return obj.__annotations__.copy()
    return {}

def isinstance_check(obj, tp):
    if tp is Any:
        return True
    
    if isinstance(tp, _GenericAlias):
        origin = tp._origin
        args = tp._args
        
        if origin is Union:
            return any(isinstance_check(obj, arg) for arg in args)
        elif origin is tuple:
            if not isinstance(obj, tuple):
                return False
            if len(args) == 0:
                return len(obj) == 0
            if len(args) != len(obj):
                return False
            return all(isinstance_check(obj[i], args[i]) for i in range(len(obj)))
        elif origin is list:
            if not isinstance(obj, list):
                return False
            if len(args) == 1:
                return all(isinstance_check(item, args[0]) for item in obj)
        elif origin is dict:
            if not isinstance(obj, dict):
                return False
            if len(args) == 2:
                key_type, value_type = args
                return all(isinstance_check(k, key_type) and isinstance_check(v, value_type) 
                          for k, v in obj.items())
        elif origin is set:
            if not isinstance(obj, set):
                return False
            if len(args) == 1:
                return all(isinstance_check(item, args[0]) for item in obj)
        else:
            return isinstance(obj, origin)
    else:
        return isinstance(obj, tp)

def overload(func):
    if not hasattr(func, '_overloads'):
        func._overloads = []
    func._overloads.append(func)
    return func

def final(func_or_class):
    func_or_class._final = True
    return func_or_class

class _LiteralType:
    def __getitem__(self, values):
        if not isinstance(values, tuple):
            values = (values,)
        return _GenericAlias(Literal, values)
    
    def __repr__(self):
        return "Literal"

Literal = _LiteralType()

class _NewType:
    def __init__(self, name, tp):
        self.name = name
        self.supertype = tp
    
    def __repr__(self):
        return f"NewType('{self.name}', {self.supertype})"
    
    def __call__(self, arg):
        return arg 

def NewType(name, tp):
    return _NewType(name, tp)

class Protocol:
    pass

def cast(tp, obj):
    return obj

class ForwardRef:
    def __init__(self, arg):
        self.arg = arg
    
    def __repr__(self):
        return f"ForwardRef('{self.arg}')"

Text = str
AnyStr = TypeVar('AnyStr', str, bytes)

class _IOType:
    def __getitem__(self, arg):
        return _GenericAlias(IO, (arg,))
    
    def __repr__(self):
        return "IO"

IO = _IOType()
TextIO = IO[str]
BinaryIO = IO[bytes]

class _ContextManagerType:
    def __getitem__(self, arg):
        return _GenericAlias(ContextManager, (arg,))
    
    def __repr__(self):
        return "ContextManager"

ContextManager = _ContextManagerType()

