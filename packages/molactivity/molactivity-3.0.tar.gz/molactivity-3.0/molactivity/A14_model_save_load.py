
PROTOCOL_VERSION = 4
MAGIC_NUMBER = b'PURE_PICKLE_V4'

OPCODE_NONE = b'\x00'
OPCODE_BOOL_TRUE = b'\x01'
OPCODE_BOOL_FALSE = b'\x02'
OPCODE_INT = b'\x03'
OPCODE_FLOAT = b'\x04'
OPCODE_STRING = b'\x05'
OPCODE_BYTES = b'\x06'
OPCODE_LIST = b'\x07'
OPCODE_TUPLE = b'\x08'
OPCODE_DICT = b'\x09'
OPCODE_SET = b'\x10'
OPCODE_COMPLEX = b'\x11'
OPCODE_OBJECT = b'\x12'
OPCODE_END = b'\xFF'

def _write_bytes(f, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif isinstance(data, int):
        data = data.to_bytes(4, 'big', signed=True)
    f.write(data)

def _write_length(f, length):
    f.write(length.to_bytes(4, 'big'))

def _read_bytes(f, length):
    return f.read(length)

def _read_length(f):
    data = f.read(4)
    if len(data) != 4:
        raise EOFError
    return int.from_bytes(data, 'big')

def _serialize_object(obj, f):
    if obj is None:
        _write_bytes(f, OPCODE_NONE)
    
    elif isinstance(obj, bool):
        if obj:
            _write_bytes(f, OPCODE_BOOL_TRUE)
        else:
            _write_bytes(f, OPCODE_BOOL_FALSE)
    
    elif isinstance(obj, int):
        _write_bytes(f, OPCODE_INT)
        int_str = str(obj)
        int_bytes = int_str.encode('utf-8')
        _write_length(f, len(int_bytes))
        _write_bytes(f, int_bytes)
    
    elif isinstance(obj, float):
        _write_bytes(f, OPCODE_FLOAT)
        float_str = repr(obj)
        float_bytes = float_str.encode('utf-8')
        _write_length(f, len(float_bytes))
        _write_bytes(f, float_bytes)
    
    elif isinstance(obj, complex):
        _write_bytes(f, OPCODE_COMPLEX)
        real_str = repr(obj.real)
        imag_str = repr(obj.imag)
        real_bytes = real_str.encode('utf-8')
        imag_bytes = imag_str.encode('utf-8')
        _write_length(f, len(real_bytes))
        _write_bytes(f, real_bytes)
        _write_length(f, len(imag_bytes))
        _write_bytes(f, imag_bytes)
    
    elif isinstance(obj, str):
        _write_bytes(f, OPCODE_STRING)
        str_bytes = obj.encode('utf-8')
        _write_length(f, len(str_bytes))
        _write_bytes(f, str_bytes)
    
    elif isinstance(obj, bytes):
        _write_bytes(f, OPCODE_BYTES)
        _write_length(f, len(obj))
        _write_bytes(f, obj)
    
    elif isinstance(obj, list):
        _write_bytes(f, OPCODE_LIST)
        _write_length(f, len(obj))
        for item in obj:
            _serialize_object(item, f)
    
    elif isinstance(obj, tuple):
        _write_bytes(f, OPCODE_TUPLE)
        _write_length(f, len(obj))
        for item in obj:
            _serialize_object(item, f)
    
    elif isinstance(obj, set):
        _write_bytes(f, OPCODE_SET)
        _write_length(f, len(obj))
        for item in obj:
            _serialize_object(item, f)
    
    elif isinstance(obj, dict):
        _write_bytes(f, OPCODE_DICT)
        _write_length(f, len(obj))
        for key, value in obj.items():
            _serialize_object(key, f)
            _serialize_object(value, f)
    
    else:
        _write_bytes(f, OPCODE_OBJECT)
        
        
        class_name = obj.__class__.__name__
        class_bytes = class_name.encode('utf-8')
        _write_length(f, len(class_bytes))
        _write_bytes(f, class_bytes)
        
        module_name = getattr(obj.__class__, '__module__', '')
        module_bytes = module_name.encode('utf-8')
        _write_length(f, len(module_bytes))
        _write_bytes(f, module_bytes)
        
        if hasattr(obj, '__dict__'):
            obj_dict = obj.__dict__
        elif hasattr(obj, '__getstate__'):
            obj_dict = obj.__getstate__()
        else:
            obj_dict = {}
            for attr in dir(obj):
                if not attr.startswith('_'): 
                    try:
                        value = getattr(obj, attr)
                        if not callable(value):
                            obj_dict[attr] = value
                    except:
                        pass
        
        _serialize_object(obj_dict, f)

def _deserialize_object(f):
    opcode = f.read(1)
    if not opcode:
        raise EOFError
    
    if opcode == OPCODE_NONE:
        return None
    
    elif opcode == OPCODE_BOOL_TRUE:
        return True
    
    elif opcode == OPCODE_BOOL_FALSE:
        return False
    
    elif opcode == OPCODE_INT:
        length = _read_length(f)
        int_bytes = _read_bytes(f, length)
        int_str = int_bytes.decode('utf-8')
        return int(int_str)
    
    elif opcode == OPCODE_FLOAT:
        length = _read_length(f)
        float_bytes = _read_bytes(f, length)
        float_str = float_bytes.decode('utf-8')
        return float(float_str)
    
    elif opcode == OPCODE_COMPLEX:
        real_length = _read_length(f)
        real_bytes = _read_bytes(f, real_length)
        real_str = real_bytes.decode('utf-8')
        
        imag_length = _read_length(f)
        imag_bytes = _read_bytes(f, imag_length)
        imag_str = imag_bytes.decode('utf-8')
        
        return complex(float(real_str), float(imag_str))
    
    elif opcode == OPCODE_STRING:
        length = _read_length(f)
        str_bytes = _read_bytes(f, length)
        return str_bytes.decode('utf-8')
    
    elif opcode == OPCODE_BYTES:
        length = _read_length(f)
        return _read_bytes(f, length)
    
    elif opcode == OPCODE_LIST:
        length = _read_length(f)
        result = []
        for _ in range(length):
            item = _deserialize_object(f)
            result.append(item)
        return result
    
    elif opcode == OPCODE_TUPLE:
        length = _read_length(f)
        items = []
        for _ in range(length):
            item = _deserialize_object(f)
            items.append(item)
        return tuple(items)
    
    elif opcode == OPCODE_SET:
        length = _read_length(f)
        items = []
        for _ in range(length):
            item = _deserialize_object(f)
            items.append(item)
        return set(items)
    
    elif opcode == OPCODE_DICT:
        length = _read_length(f)
        result = {}
        for _ in range(length):
            key = _deserialize_object(f)
            value = _deserialize_object(f)
            result[key] = value
        return result
    
    elif opcode == OPCODE_OBJECT:
        class_name_length = _read_length(f)
        class_name_bytes = _read_bytes(f, class_name_length)
        class_name = class_name_bytes.decode('utf-8')
        
        module_name_length = _read_length(f)
        module_name_bytes = _read_bytes(f, module_name_length)
        module_name = module_name_bytes.decode('utf-8')
        
        obj_dict = _deserialize_object(f)
        
        class GenericObject:
            def __init__(self, class_name, module_name, attributes):
                self.__class__.__name__ = class_name
                self.__class__.__module__ = module_name
                if attributes is not None:
                    if hasattr(attributes, 'items'):
                        for key, value in attributes.items():
                            setattr(self, key, value)
           
                    elif isinstance(attributes, dict):
                        for key, value in attributes.items():
                            setattr(self, key, value)
                    else:
                        pass
        
        return GenericObject(class_name, module_name, obj_dict)
    
    else:
        raise ValueError

def dump(obj, file):

    if isinstance(file, str):
        with open(file, 'wb') as f:
            return dump(obj, f)
    
    _write_bytes(file, MAGIC_NUMBER)
    _write_bytes(file, PROTOCOL_VERSION.to_bytes(1, 'big'))
    
    _serialize_object(obj, file)
    
    _write_bytes(file, OPCODE_END)

def load(file):

    if isinstance(file, str):
        with open(file, 'rb') as f:
            return load(f)
    
    magic = file.read(len(MAGIC_NUMBER))
    if magic != MAGIC_NUMBER:
        raise ValueError
    
    version_bytes = file.read(1)
    if not version_bytes or version_bytes[0] != PROTOCOL_VERSION:
        raise ValueError
    
    obj = _deserialize_object(file)
    
    end_marker = file.read(1)
    if end_marker != OPCODE_END:
        raise ValueError
    
    return obj

def dumps(obj):
    class BytesBuffer:
        def __init__(self):
            self.data = b''
        
        def write(self, data):
            if isinstance(data, str):
                data = data.encode('utf-8')
            elif isinstance(data, int):
                data = data.to_bytes(4, 'big', signed=True)
            self.data += data
        
        def getvalue(self):
            return self.data
    
    buffer = BytesBuffer()
    
    _write_bytes(buffer, MAGIC_NUMBER)
    _write_bytes(buffer, PROTOCOL_VERSION.to_bytes(1, 'big'))
    
    _serialize_object(obj, buffer)
    
    _write_bytes(buffer, OPCODE_END)
    
    return buffer.getvalue()

def loads(data):

    class BytesReader:
        def __init__(self, data):
            self.data = data
            self.pos = 0
        
        def read(self, length):
            if self.pos + length > len(self.data):
                return self.data[self.pos:]
            result = self.data[self.pos:self.pos + length]
            self.pos += length
            return result
    
    reader = BytesReader(data)
    
    magic = reader.read(len(MAGIC_NUMBER))
    if magic != MAGIC_NUMBER:
        raise ValueError
    
    version_bytes = reader.read(1)
    if not version_bytes or version_bytes[0] != PROTOCOL_VERSION:
        raise ValueError
    
    obj = _deserialize_object(reader)
    
    end_marker = reader.read(1)
    if end_marker != OPCODE_END:
        raise ValueError
    
    return obj

