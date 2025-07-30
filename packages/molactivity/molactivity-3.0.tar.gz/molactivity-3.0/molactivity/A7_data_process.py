
from .A22_random import shuffle, seed as set_random_seed


class DataTable:
 
    def __init__(self, data=None):

        if data is None:
            data = {}
        self._data = data
        self._columns = list(data.keys())
        self._row_count = len(next(iter(data.values()))) if data else 0
        
        if data:
            for col_name, col_data in data.items():
                if len(col_data) != self._row_count:
                    raise ValueError
    
    def __len__(self):
        return self._row_count
    
    def __getitem__(self, key):

        if key not in self._data:
            raise KeyError
        return DataColumn(self._data[key], key)
    
    def __setitem__(self, key, value):
    
        if len(value) != self._row_count and self._row_count > 0:
            raise ValueError
        
        self._data[key] = value
        if key not in self._columns:
            self._columns.append(key)
        if self._row_count == 0:
            self._row_count = len(value)
    
    @property
    def columns(self):
        return self._columns[:]  
    
    def add_column(self, name, data):

        self[name] = data
    
    def get_row(self, index):

        if index < 0 or index >= self._row_count:
            raise IndexError
        
        return {col: self._data[col][index] for col in self._columns}
    
    def to_dict(self):
        return {k: v[:] for k, v in self._data.items()}  
    
    def copy(self):
   
        copied_data = {}
        for col_name, col_data in self._data.items():
            copied_data[col_name] = col_data[:]  
        
        return DataTable(copied_data)
    
    def to_csv(self, filepath, index=False):

        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as file:
                headers = self._columns
                file.write(','.join(headers) + '\n')
                
                for row_idx in range(self._row_count):
                    row_values = []
                    for col_name in headers:
                        value = self._data[col_name][row_idx]
                        if isinstance(value, str) and (',' in value or '\n' in value or '"' in value):
                            escaped_value = value.replace('"', '""')
                            row_values.append(f'"{escaped_value}"')
                        else:
                            row_values.append(str(value))
                    
                    file.write(','.join(row_values) + '\n')
                    
        except Exception as e:
            raise Exception
    
    def shuffle_rows(self, seed=None):
 
        if seed is not None:
            set_random_seed(seed)
        
        indices = list(range(self._row_count))
        shuffle(indices)
        
        for col_name in self._columns:
            original_data = self._data[col_name][:]  
            self._data[col_name] = [original_data[i] for i in indices]


class DataColumn:
    
    def __init__(self, data, name=None):

        self._data = data
        self._name = name
    
    def __len__(self):
        return len(self._data)
    
    def __getitem__(self, index):
        return self._data[index]
    
    def __iter__(self):
        return iter(self._data)
    
    @property
    def name(self):
        return self._name
    
    def value_counts(self):
    
        count_dict = {}
        for value in self._data:
            if value in count_dict:
                count_dict[value] += 1
            else:
                count_dict[value] = 1
        
        return ValueCounts(count_dict)
    
    def to_list(self):
        
        return self._data[:]


class ValueCounts:

    
    def __init__(self, count_dict):

        self._count_dict = count_dict
        sorted_items = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
        self._values = [item[0] for item in sorted_items]
        self._counts = [item[1] for item in sorted_items]
    
    def to_list(self):
        return self._counts[:]
    
    def to_dict(self):
        return self._count_dict.copy()  
    
    def __getitem__(self, key):
        return self._count_dict.get(key, 0)
    
    def __len__(self):
        return len(self._count_dict)
    
    def keys(self):
        return self._values[:]  
    
    def values(self):
        return self._counts[:]  


class PureCSVReader:

    @staticmethod
    def read_csv(filepath, encoding='utf-8', delimiter=',', shuffle=False, random_seed=42):
      
        try:
            with open(filepath, 'r', encoding=encoding) as test_file:
                pass
        except FileNotFoundError:
            raise FileNotFoundError
        except UnicodeDecodeError:
            try:
                return PureCSVReader.read_csv(filepath, encoding='gbk', delimiter=delimiter, shuffle=shuffle, random_seed=random_seed)
            except:
                try:
                    return PureCSVReader.read_csv(filepath, encoding='latin-1', delimiter=delimiter, shuffle=shuffle, random_seed=random_seed)
                except Exception as e:
                    pass
        
        data = {}
        
        try:
            with open(filepath, 'r', encoding=encoding) as file:
                lines = file.readlines()
    
                header_line = lines[0].strip()
                headers = PureCSVReader._parse_csv_line(header_line, delimiter)
                
                # 去除BOM字符和空格
                headers = [header.strip().lstrip('\ufeff') for header in headers]
                
                for header in headers:
                    data[header] = []
                
                for row_num, line in enumerate(lines[1:], start=2):
                    line = line.strip()
                    if not line:  
                        continue
                    
                    row = PureCSVReader._parse_csv_line(line, delimiter)
                    
                    for header, value in zip(headers, row):
                        processed_value = PureCSVReader._convert_value(value.strip())
                        data[header].append(processed_value)
                
        except Exception as e:
            raise Exception
        
        table = DataTable(data)
        
        if shuffle:
            table.shuffle_rows(random_seed)
        
        return table
    
    @staticmethod
    def _parse_csv_line(line, delimiter=','):
    
        fields = []
        current_field = ""
        in_quotes = False
        i = 0
        
        while i < len(line):
            char = line[i]
            
            if char == '"':
                if in_quotes:
                    if i + 1 < len(line) and line[i + 1] == '"':
                        current_field += '"'
                        i += 1  
                    else:
                        in_quotes = False
                else:
                    in_quotes = True
            elif char == delimiter and not in_quotes:
                fields.append(current_field)
                current_field = ""
            else:
                current_field += char
            
            i += 1
        
        fields.append(current_field)
        
        return fields
    
    @staticmethod
    def _convert_value(value_str):
  
        if not value_str or value_str.lower() in ['', 'na', 'nan', 'null', 'none']:
            return None
        
        
        try:
            if '.' not in value_str and value_str.lstrip('-').isdigit():
                return int(value_str)
        except:
            pass
        
        try:
            return float(value_str)
        except:
            pass
        
        if value_str.lower() in ['true', 'yes']:
            return True
        elif value_str.lower() in ['false', 'no']:
            return False
        
        return value_str


def read_csv(filepath, encoding='utf-8', delimiter=',', shuffle=False, random_seed=42):
 
    return PureCSVReader.read_csv(filepath, encoding, delimiter, shuffle, random_seed)

