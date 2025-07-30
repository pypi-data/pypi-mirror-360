

class Lock:

    def __init__(self):
        self._locked = False
        self._owner = None
    
    def acquire(self, blocking=True, timeout=-1):

        if not self._locked:
            self._locked = True
            self._owner = id(object()) 
            return True
        else:
            if not blocking:
                return False
  
            return False
    
    def release(self):
        "good"
  
        self._locked = False
        self._owner = None

    def __enter__(self):
        "good"
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        "good"
        self.release()

class threading:

    @staticmethod
    def Lock():
        return Lock()


def wraps(wrapped, assigned=None, updated=None):

    if assigned is None:
        assigned = ('__module__', '__name__', '__qualname__', '__doc__', '__annotations__')
    if updated is None:
        updated = ('__dict__',)
    
    def decorator(wrapper):

        for attr in assigned:
            try:
                original_value = getattr(wrapped, attr)
                setattr(wrapper, attr, original_value)
            except AttributeError:
                pass

        for attr in updated:
            try:
                wrapper_attr = getattr(wrapper, attr)
                wrapped_attr = getattr(wrapped, attr)
                if hasattr(wrapper_attr, 'update'):
                    wrapper_attr.update(wrapped_attr)
            except AttributeError:
                pass

        wrapper.__wrapped__ = wrapped
        
        return wrapper
    
    return decorator

class functools:
    
    @staticmethod
    def wraps(wrapped, assigned=None, updated=None):
        return wraps(wrapped, assigned, updated)

class _AutoValue:
    
    def __init__(self):
        self._value = 0
    
    def __call__(self):
        self._value += 1
        return self._value

_auto_instance = _AutoValue()

def auto():

    return _auto_instance()

class EnumMeta(type):
    
    def __new__(cls, name, bases, namespace):
        auto_value = 0
        enum_members = {}
        
        for key, value in list(namespace.items()):
            if not key.startswith('_') and not callable(value):
                if hasattr(value, '__call__') and value.__name__ == 'auto':
                    auto_value += 1
                    enum_members[key] = auto_value
                    namespace[key] = auto_value
                elif isinstance(value, int):
                    enum_members[key] = value
                    auto_value = max(auto_value, value)
        
        enum_class = super().__new__(cls, name, bases, namespace)
        
        enum_class._member_map_ = enum_members
        enum_class._member_names_ = list(enum_members.keys())
        enum_class._member_values_ = list(enum_members.values())
        
        return enum_class
    
    def __iter__(cls):
        for name in cls._member_names_:
            yield getattr(cls, name)
    
    def __len__(cls):
        return len(cls._member_names_)

class Enum(metaclass=EnumMeta):
    
    def __init__(self, value):
        self._value_ = value
        self._name_ = None
    
    @property
    def name(self):
        if self._name_ is None:
            for name, val in self.__class__._member_map_.items():
                if val == self._value_:
                    self._name_ = name
                    break
        return self._name_
    
    @property
    def value(self):
        return self._value_
    
    def __str__(self):
        return f"{self.__class__.__name__}.{self.name}"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}: {self.value}>"
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._value_ == other._value_
        return False
    
    def __hash__(self):
        return hash(self._value_)

class enum:
    
    Enum = Enum
    auto = auto

class _CopyRegistry:
    
    def __init__(self):
        self._registry = {}
    
    def register(self, type_cls, copy_func):
        self._registry[type_cls] = copy_func
    
    def get(self, type_cls):
        return self._registry.get(type_cls)

class copy:
    
    @staticmethod
    def copy(obj):

        if obj is None or isinstance(obj, (int, float, str, bool, complex, bytes, frozenset)):
            return obj
        
        if hasattr(obj, '__copy__'):
            return obj.__copy__()
        
        if isinstance(obj, list):
            return obj[:]  
        elif isinstance(obj, tuple):
            return tuple(obj) 
        elif isinstance(obj, dict):
            return obj.copy() 
        elif isinstance(obj, set):
            return obj.copy() 
        
        elif hasattr(obj, '__dict__'):
            try:
                new_obj = obj.__class__.__new__(obj.__class__)
                if hasattr(obj, '__dict__'):
                    new_obj.__dict__.update(obj.__dict__)
                if hasattr(obj, '__slots__'):
                    for slot in obj.__slots__:
                        if hasattr(obj, slot):
                            setattr(new_obj, slot, getattr(obj, slot))
                return new_obj
            except:
                pass
        
        return obj
    
    @staticmethod  
    def deepcopy(obj, memo=None):

        return _perform_deepcopy(obj, memo)
    
def _perform_deepcopy(obj, memo=None):
    if memo is None:
        memo = {}
    
    obj_id = id(obj)
    if obj_id in memo:
        return memo[obj_id]
    
    if obj is None or isinstance(obj, (int, float, str, bool, complex, bytes, frozenset)):
        return obj
    
    if hasattr(obj, '__deepcopy__'):
        result = obj.__deepcopy__(memo)
        memo[obj_id] = result
        return result
    
    if isinstance(obj, list):
        result = []
        memo[obj_id] = result
        for item in obj:
            result.append(_perform_deepcopy(item, memo))
        return result
    
    elif isinstance(obj, tuple):
        needs_copy = any(not isinstance(item, (int, float, str, bool, complex, bytes, frozenset, type(None))) for item in obj)
        if not needs_copy:
            return obj
        
        temp_list = []
        memo[obj_id] = temp_list
        for item in obj:
            temp_list.append(_perform_deepcopy(item, memo))
        result = tuple(temp_list)
        memo[obj_id] = result
        return result
    
    elif isinstance(obj, dict):
        result = {}
        memo[obj_id] = result
        for key, value in obj.items():
            new_key = _perform_deepcopy(key, memo)
            new_value = _perform_deepcopy(value, memo)
            result[new_key] = new_value
        return result
    
    elif isinstance(obj, set):
        result = set()
        memo[obj_id] = result
        for item in obj:
            result.add(_perform_deepcopy(item, memo))
        return result
    
    elif hasattr(obj, '__dict__') or hasattr(obj, '__slots__'):
        try:
            new_obj = obj.__class__.__new__(obj.__class__)
            memo[obj_id] = new_obj
            
            if hasattr(obj, '__dict__'):
                for key, value in obj.__dict__.items():
                    setattr(new_obj, key, _perform_deepcopy(value, memo))
            
            if hasattr(obj, '__slots__'):
                for slot in obj.__slots__:
                    if hasattr(obj, slot):
                        value = getattr(obj, slot)
                        setattr(new_obj, slot, _perform_deepcopy(value, memo))
            
            return new_obj
        except:
            pass
    
    if callable(obj):
        return obj
    
    return obj



def _abs(x):
    return x if x >= 0 else -x

def _floor(x):
    if x >= 0:
        return int(x)
    else:
        if x == int(x):
            return int(x)
        else:
            return int(x) - 1

def _ceil(x):
    if x >= 0:
        if x == int(x):
            return int(x)
        else:
            return int(x) + 1
    else:
        return int(x)

def _pow10(n):
    if n == 0:
        return 1
    elif n > 0:
        result = 1
        for _ in range(n):
            result *= 10
        return result
    else:  # n < 0
        result = 1.0
        for _ in range(-n):
            result /= 10
        return result

def round(number, ndigits=None):

    
    if number != number:  
        return number
    
    if number == float('inf') or number == float('-inf'):
        return number
    
    if ndigits is None:
        return _round_to_int(number)
    
    if not isinstance(ndigits, int):
        raise TypeError("ndigits must be an integer")
    
    if ndigits == 0:
        return _round_to_int(number)
    
    scale = _pow10(ndigits)
    
    scaled = number * scale
    rounded_scaled = _round_to_int(scaled)
    result = rounded_scaled / scale
    
    return result

def _round_to_int(x):

    if x == 0.0:
        return 0
    
    sign = 1 if x >= 0 else -1
    abs_x = _abs(x)
    
    int_part = int(abs_x)
    frac_part = abs_x - int_part
    
    if frac_part < 0.5:
        result = int_part
    elif frac_part > 0.5:
        result = int_part + 1
    else:
        if int_part % 2 == 0:
            result = int_part
        else:
            result = int_part + 1
    
    return result * sign

def _is_close_to_half(frac_part):

    epsilon = 1e-15
    return _abs(frac_part - 0.5) < epsilon

def path_available(path):

    if not isinstance(path, str):
        return False
    
    if not path or not path.strip():
        return False
    
    try:
        with open(path, 'r', encoding='utf-8'):
            pass
        return True
    except FileNotFoundError:
        return False
    except PermissionError:
        return True
    except IsADirectoryError:
        return True
    except UnicodeDecodeError:
        try:
            with open(path, 'rb'):
                pass
            return True
        except FileNotFoundError:
            return False
        except (PermissionError, IsADirectoryError):
            return True
        except (OSError, IOError):
            return True
        except:
            return False
    except (OSError, IOError):
        return True
    except:
        return False

def path_available_safe(path):

    try:
        return path_available(path)
    except:
        return False

def validate_file_path(path):

    if not isinstance(path, str):
        return False
    
    if not path or not path.strip():
        return False
    
    try:
        with open(path, 'r', encoding='utf-8'):
            pass
        return True
    except UnicodeDecodeError:
        try:
            with open(path, 'rb'):
                pass
            return True
        except:
            return False
    except:
        return False

def is_readable_file(path):

    if not isinstance(path, str):
        return False
    
    if not path or not path.strip():
        return False
    
    try:
        with open(path, 'rb') as f:
            f.read(1) 
        return True
    except FileNotFoundError:
        return False
    except IsADirectoryError:
        return False
    except:
        return False

def get_path_status(path):

    result = {
        'exists': False,
        'is_file': False,
        'is_directory': False,
        'is_readable': False,
        'error': None
    }
    
    if not isinstance(path, str) or not path or not path.strip():
        result['error'] = 'Invalid path'
        return result
    
    try:
        with open(path, 'r', encoding='utf-8'):
            pass
        result['exists'] = True
        result['is_file'] = True
        result['is_readable'] = True
        return result
    except FileNotFoundError:
        result['error'] = 'Path not found'
        return result
    except IsADirectoryError:
        result['exists'] = True
        result['is_directory'] = True
        result['error'] = 'Is directory'
        return result
    except PermissionError:
        result['exists'] = True
        result['error'] = 'Permission denied'
        return result
    except UnicodeDecodeError:
        try:
            with open(path, 'rb'):
                pass
            result['exists'] = True
            result['is_file'] = True
            result['is_readable'] = True
            result['error'] = 'Binary file'
            return result
        except FileNotFoundError:
            result['error'] = 'Path not found'
            return result
        except IsADirectoryError:
            result['exists'] = True
            result['is_directory'] = True
            result['error'] = 'Is directory'
            return result
        except PermissionError:
            result['exists'] = True
            result['error'] = 'Permission denied'
            return result
        except (OSError, IOError) as e:
            result['exists'] = True
            result['error'] = f'I/O error: {str(e)}'
            return result
        except Exception as e:
            result['error'] = f'Unknown error: {str(e)}'
            return result
    except (OSError, IOError) as e:
        result['exists'] = True
        result['error'] = f'I/O error: {str(e)}'
        return result
    except Exception as e:
        result['error'] = f'Unknown error: {str(e)}'
        return result

def _factorial(n):
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def _exp(x):
    if x > 700:  
        return float('inf')
    if x < -700: 
        return 0.0
    
    result = 1.0
    term = 1.0
    
    for n in range(1, 100):  
        term *= x / n
        result += term
        if abs(term) < 1e-15:
            break
    
    return result

def _sqrt(x):
    if x < 0:
        raise ValueError
    if x == 0:
        return 0.0
    
    guess = x / 2.0
    for _ in range(50):  
        new_guess = (guess + x / guess) / 2.0
        if abs(new_guess - guess) < 1e-15:
            break
        guess = new_guess
    
    return guess

def _pi():

    def arctan(x):
        if _abs(x) > 1:
            if x > 0:
                return _pi() / 2 - arctan(1/x)
            else:
                return -_pi() / 2 - arctan(1/x)
        
        result = 0.0
        term = x
        x_squared = x * x
        
        for n in range(200): 
            sign = 1 if n % 2 == 0 else -1
            result += sign * term / (2 * n + 1)
            term *= x_squared
            if _abs(term / (2 * n + 3)) < 1e-15:
                break
        
        return result
    
    return 3.141592653589793

def Error_Function(x):

    if isinstance(x, list):
        return [Error_Function(item) for item in x]
    
    if x == 0:
        return 0.0
    
    if x < 0:
        return -Error_Function(-x)
    
    if x > 6:
        return 1.0
    
    if x <= 2.5:
        return _erf_series(x)
    else:
        return 1.0 - _erfc_continued_fraction(x)

def _erf_series(x):

    sqrt_pi = _sqrt(_pi())
    two_over_sqrt_pi = 2.0 / sqrt_pi
    
    result = 0.0
    term = x
    x_squared = x * x
    
    for n in range(100):  
        factorial_n = _factorial(n)
        denominator = (2 * n + 1) * factorial_n
        
        sign = 1 if n % 2 == 0 else -1
        result += sign * term / denominator
        
        term *= x_squared
        
        if _abs(term / ((2 * n + 3) * _factorial(n + 1))) < 1e-15:
            break
    
    return two_over_sqrt_pi * result

def _erfc_continued_fraction(x):

    sqrt_pi = _sqrt(_pi())
    exp_neg_x_squared = _exp(-x * x)

    b0 = x
    a1 = 0.5
    b1 = x + a1
    
    f = b0 / b1
    
    for n in range(1, 100):
        an = n * 0.5
        bn = x + an
        
        if _abs(bn) < 1e-30:
            bn = 1e-30
        
        f_old = f
        f = b0 / (bn + an / f)
        
        if _abs(f - f_old) / _abs(f) < 1e-15:
            break
    
    return (exp_neg_x_squared / (sqrt_pi * x)) * f

def erfc(x):

    if isinstance(x, list):
        return [erfc(item) for item in x]
    
    return 1.0 - Error_Function(x)

class weak_ref:

    _global_refs = {}
    _next_id = 0
    
    def __init__(self, obj, callback=None):

        self._obj_id = id(obj)
        self._callback = callback
        self._is_alive = True

        if self._obj_id not in weak_ref._global_refs:
            weak_ref._global_refs[self._obj_id] = {
                'obj': obj,
                'ref_count': 0,
                'refs': []
            }
        
        weak_ref._global_refs[self._obj_id]['ref_count'] += 1
        weak_ref._global_refs[self._obj_id]['refs'].append(self)

        weak_ref._next_id += 1
        self._ref_id = weak_ref._next_id
    
    def __call__(self):

        if not self._is_alive:
            return None
            
        if self._obj_id in weak_ref._global_refs:
            return weak_ref._global_refs[self._obj_id]['obj']
        else:
            self._is_alive = False
            return None
    
    def __eq__(self, other):

        if not isinstance(other, weak_ref):
            return False
        
        if self._is_alive and other._is_alive:
            return self._obj_id == other._obj_id
        
        return False
    
    def __hash__(self):

        return hash((self._obj_id, self._ref_id))
    
    def __repr__(self):

        if self._is_alive and self._obj_id in weak_ref._global_refs:
            obj = weak_ref._global_refs[self._obj_id]['obj']
            obj_type = type(obj).__name__
            return f"<ref at {hex(id(self))} to '{obj_type}' at {hex(self._obj_id)}>"
        else:
            return f"<ref at {hex(id(self))} (dead)>"
    
    @property
    def is_alive(self):

        return self._is_alive and self._obj_id in weak_ref._global_refs
    
    def invalidate(self):

        self._is_alive = False
        if self._callback:
            try:
                self._callback(self)
            except:
                pass  
    
    @classmethod
    def cleanup_refs(cls, obj_id):

        if obj_id in cls._global_refs:
            refs_info = cls._global_refs[obj_id]
            for ref_obj in refs_info['refs']:
                ref_obj.invalidate()
            del cls._global_refs[obj_id]
    
    @classmethod
    def get_ref_count(cls, obj):

        obj_id = id(obj)
        if obj_id in cls._global_refs:
            return cls._global_refs[obj_id]['ref_count']
        return 0
    
    @classmethod
    def clear_all_refs(cls):

        for obj_id in list(cls._global_refs.keys()):
            cls.cleanup_refs(obj_id)
