from typing import Optional
import numpy as np
from .B16_tensor import Tensor
from .B7_module import Module

class Dropout(Module):
    def __init__(
        self,
        p: float = 0.5,
        inplace: bool = False,
        generator: Optional[np.random.Generator] = None
    ) -> None:
   
        super(Dropout, self).__init__()
        if p < 0 or p >= 1:
            raise ValueError
            
        self.p = p
        self.inplace = inplace
        self.generator = generator if generator is not None else np.random.default_rng()
        self.training = True  
        self._mask: Optional[np.ndarray] = None

    def forward(self, input: Tensor) -> Tensor:
       
        if not self.training or self.p == 0:
            if not self.inplace:
                return input.clone()
            return input

        
        self._mask = self.generator.random(input.shape) > self.p
        scale = 1.0 / (1.0 - self.p)
        
        if self.inplace:
            input.data *= self._mask * scale
            return input
        else:
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

    def train(self, mode: bool = True) -> None:
        self.training = mode

    def eval(self) -> None:
        self.train(False)

    def reset_seed(self, seed: Optional[int] = None) -> None:
        self.generator = np.random.default_rng(seed)

    def extra_repr(self) -> str:
        return f'p={self.p}, inplace={self.inplace}, training={self.training}'

    def __repr__(self) -> str:
        return f'Dropout({self.extra_repr()})'

    def __call__(self, input: Tensor) -> Tensor:
        return self.forward(input)
