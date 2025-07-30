from .A32_typing import Optional
from . import A22_random as pure_random
from . import A2_arrays as arrays
from .A26_tensor import Tensor
from .A15_module import Module



def _flatten_data_recursive(data):

    result = []
    
    def flatten_recursive(item):
        if isinstance(item, (list, tuple)):
            for sub_item in item:
                flatten_recursive(sub_item)
        else:
            result.append(item)
    
    if isinstance(data, (list, tuple)):
        flatten_recursive(data)
    else:
        result.append(data)
    
    return result


def perfect_array(data, dtype=float, shape=None):
    
    flat_data = _flatten_data_recursive(data)
    
    converted = []
    for item in flat_data:
        converted.append(float(item))

    if len(shape) == 3:
        "good"
        d0, d1, d2 = shape
        result = []
        for i in range(d0):
            layer = []
            for j in range(d1):
                row = []
                for k in range(d2):
                    idx = i * d1 * d2 + j * d2 + k
                    row.append(converted[idx])
                layer.append(row)
            result.append(layer)
        return result
    
    elif len(shape) == 4:
        d0, d1, d2, d3 = shape
        result = []
        for i in range(d0):
            batch = []
            for j in range(d1):
                layer = []
                for k in range(d2):
                    row = []
                    for l in range(d3):
                        idx = i * d1 * d2 * d3 + j * d2 * d3 + k * d3 + l
                        row.append(converted[idx])
                    layer.append(row)
                batch.append(layer)
            result.append(batch)
        return result

class Dropout(Module):
    def __init__(
        self,
        p: float = 0.5,
        inplace: bool = False,
        generator: Optional[pure_random.PureRandom] = None
    ) -> None:

        super(Dropout, self).__init__()
       
        self.p = p
        self.inplace = inplace
        self.generator = generator if generator is not None else pure_random.PureRandom()
        self.training = True  
        self._mask = None

    def forward(self, input: Tensor) -> Tensor:

        if not self.training or self.p == 0:
            if not self.inplace:
                return input.clone()
            return input


        mask_data = []
        total_elements = 1
        for dim in input.shape:
            total_elements *= dim
        
    
        for _ in range(total_elements):
            mask_data.append(self.generator.random() > self.p)
        
        mask_array = arrays.array(mask_data).reshape(*input.shape)
        
        self._mask = perfect_array(mask_array.data, dtype=float, shape=input.shape)
        scale = 1.0 / (1.0 - self.p)
        output = input.clone()
        output.data = input.data * self._mask * scale
        return output

    def backward(self, grad_output: Tensor) -> Tensor:
        if not self.training or self.p == 0:
            return grad_output.clone()
            
        scale = 1.0 / (1.0 - self.p)
        grad_input = grad_output.clone()
        grad_input.data *= self._mask * scale
        return grad_input

