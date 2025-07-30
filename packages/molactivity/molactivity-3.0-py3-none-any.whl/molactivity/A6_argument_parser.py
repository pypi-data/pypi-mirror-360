
class ArgvHandler:

    def __init__(self):
        self._argv = ['script.py']
        self._initialized = False
    
    def set_argv(self, argv_list):

        if isinstance(argv_list, list):
            self._argv = argv_list[:]
        else:
            self._argv = [str(argv_list)]
        self._initialized = True
    
    def get_argv(self):

        return self._argv[:]
    
    def get_args(self):

        return self._argv[1:] if len(self._argv) > 1 else []
    
    def parse_command_line(self, command_string):
 
        if not command_string:
            return
        
        parts = command_string.split()
        if not parts:
            return
        
        script_index = -1
        for i, part in enumerate(parts):
            if part.endswith('.py'):
                script_index = i
                break
        
        if script_index != -1:
            self._argv = parts[script_index:]
        else:
            self._argv = parts[:]
        
        self._initialized = True
    
    def add_arg(self, arg):

        self._argv.append(str(arg))
    
    def clear(self):
        self._argv = ['script.py']
        self._initialized = False
    
    def __len__(self):
        return len(self._argv)
    
    def __getitem__(self, index):
        return self._argv[index]
    
    def __setitem__(self, index, value):
        self._argv[index] = str(value)
    
    def __iter__(self):
        return iter(self._argv)
    
    def __str__(self):
        return str(self._argv)
    
    def __repr__(self):
        return f"ArgvHandler({self._argv})"


class ParameterDefinition:
    
    def __init__(self, name, param_type=str, default=None, choices=None, help_text="", required=False):
        self.name = name
        self.param_type = param_type
        self.default = default
        self.choices = choices
        self.help_text = help_text
        self.required = required

class ParsedArguments:  
    
    def __init__(self):
        self._values = {}
    
    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        return self._values.get(name)
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            self._values[name] = value

class ArgumentProcessor:
    
    def __init__(self, description="argument processor"):
        self.description = description
        self.parameters = {}
        self.positional_params = []
        
    def add_argument(self, name, **kwargs):
        if name.startswith('--'):
            param_name = name[2:]
        elif name.startswith('-'):
            param_name = name[1:]
        else:
            param_name = name
            
        param_type = kwargs.get('type', str)
        default = kwargs.get('default', None)
        choices = kwargs.get('choices', None)
        help_text = kwargs.get('help', "")
        required = kwargs.get('required', False)
        action = kwargs.get('action', None)
        
        if action == 'store_true':
            param_type = bool
            default = False if default is None else default
            
        param_def = ParameterDefinition(
            name=param_name,
            param_type=param_type,
            default=default,
            choices=choices,
            help_text=help_text,
            required=required
        ) 
        
        self.parameters[name] = param_def
        
        if not name.startswith('-'):
            self.positional_params.append(param_def)
    
    def parse_args(self, args=None):
        
        if args is None:
            args = ArgvHandler()[1:]
        result = ParsedArguments()
        
        for param_name, param_def in self.parameters.items():
            clean_name = param_def.name
            if param_def.default is not None:
                setattr(result, clean_name, param_def.default)
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg.startswith('--'):
                if '=' in arg:
                    param_name, value = arg.split('=', 1)
                else:
                    param_name = arg
                    if i + 1 < len(args) and not args[i + 1].startswith('-'):
                        value = args[i + 1]
                        i += 1
                    else:
                        value = None
                
                self._process_parameter(result, param_name, value)
                
            elif arg.startswith('-') and len(arg) > 1:
                param_name = arg
                if i + 1 < len(args) and not args[i + 1].startswith('-'):
                    value = args[i + 1]
                    i += 1
                else:
                    value = None
                
                self._process_parameter(result, param_name, value)
            
            i += 1
        
        self._validate_required_parameters(result)
        
        return result
    
    def _process_parameter(self, result, param_name, value):
        
        param_def = None
        for name, definition in self.parameters.items():
            if name == param_name:
                param_def = definition
                break
        
        if param_def is None:
            return
        
        if param_def.param_type == bool:
            if value is None:
                setattr(result, param_def.name, True)
            else:
                setattr(result, param_def.name, self._convert_to_bool(value))
            return
        
        if value is None:
            return
        
        try:
            converted_value = self._convert_value(value, param_def.param_type)
        except:
            return
        
        if param_def.choices and converted_value not in param_def.choices:
            return
        
        setattr(result, param_def.name, converted_value)
    
    def _convert_value(self, value, target_type):
        
        if target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == str:
            return str(value)
        elif target_type == bool:
            return self._convert_to_bool(value)
        else:
            return value
    
    def _convert_to_bool(self, value):

        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ['true', '1', 'yes', 'on']:
                return True
            elif lower_value in ['false', '0', 'no', 'off']:
                return False
        return False
    
    def _validate_required_parameters(self, result):

        for param_name, param_def in self.parameters.items():
            if param_def.required:
                value = getattr(result, param_def.name)

