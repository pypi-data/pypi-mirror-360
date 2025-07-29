from .tensors import Tensor

import numpy as np
from numpy.typing import NDArray
import os
from safetensors import numpy as st_numpy
from typing import List, Dict, Any

# neural networks
class Module:
    '''
    Base class for all neural network modules
    '''
    def __init__(self):
        self._parameters: Dict[str, Tensor] = {}
        self._modules: Dict[str, 'Module'] = {}

    def __setattr__(self, name: str, value: Any):
        '''
        Registers parameters and submodules automatically
        '''
        if isinstance(value, Tensor):
            self._parameters[name] = value
        elif isinstance(value, Module):
            self._modules[name] = value
        super().__setattr__(name, value)

    def forward(self, *args, **kwargs):
        '''
        Defines the computation performed at every call
        '''
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        '''
        Makes the module callable and calls the forward method
        '''
        return self.forward(*args, **kwargs)

    def parameters(self) -> List[Tensor]:
        '''
        Returns a list of all model parameters with requires_grad is True
        '''
        params = []
        for param in self._parameters.values():
            if param.requires_grad:
                params.append(param)
        for module in self._modules.values():
            params.extend(module.parameters())
        return params

    def zero_grad(self):
        '''
        Sets gradients of all model parameters to zero
        '''
        for p in self.parameters():
            p.zero_grad()

    def state_dict(self) -> Dict[str, NDArray]:
        '''
        Returns a dictionary containing a whole state of the module
        '''
        sd = {name: p.data for name, p in self._parameters.items()}
        for name, module in self._modules.items():
            for key, val in module.state_dict().items():
                sd[f"{name}.{key}"] = val
        return sd

    def load_state_dict(self, state_dict: Dict[str, NDArray]):
        '''
        Copies parameters from state_dict into this module
        '''
        for key, value in state_dict.items():
            parts = key.split('.')
            module = self
            try:
                for part in parts[:-1]:
                    module = getattr(module, part)
                
                param_name = parts[-1]
                param = getattr(module, param_name)

                if not isinstance(param, Tensor):
                     raise TypeError(f"Loaded attribute '{key}' is not a Tensor in the model.")

                if param.data.shape != value.shape:
                    raise ValueError(f"Shape mismatch for '{key}': model has {param.data.shape}, loaded has {value.shape}")
                
                param.data[:] = value
            except AttributeError:
                print(f"Warning: key '{key}' not found in model, skipping.")


class Linear(Module):
    '''
    Linear is a layer for dense layer connection
    '''
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        he_std = np.sqrt(2.0 / in_features)
        self.weight = Tensor(np.random.randn(out_features, in_features) * he_std)
        
        if bias:
            self.bias = Tensor(np.zeros(out_features))
        else:
            self.bias = None

    def forward(self, x: Tensor) -> Tensor:
        out = x @ self.weight.transpose((1, 0))
        if self.bias is not None:
            out = out + self.bias
        return out

    def __repr__(self) -> str:
        return f"Linear(in_features={self.in_features}, out_features={self.out_features}"


class Sequential(Module):
    '''
    Sequential class is used to store all the layers and activation functions
    '''
    def __init__(self, *args: Module):
        super().__init__()
        for i, module in enumerate(args):
            setattr(self, str(i), module)

    def forward(self, x: Tensor) -> Tensor:
        for module in self._modules.values():
            x = module(x)
        return x

# activation layers
class ReLU(Module):
    def forward(self, x: Tensor) -> Tensor:
        return x.relu()

class Sigmoid(Module):
    def forward(self, x: Tensor) -> Tensor:
        return x.sigmoid()

class Tanh(Module):
    def forward(self, x: Tensor) -> Tensor:
        return x.tanh()

# saving and loading the model
def save(model: Module, path: str):
    '''
    Saves the state_dict of a Module to a file using safetensors.
    '''
    state_dict = model.state_dict()
    st_numpy.save_file(state_dict, path)
    print(f"Model state saved to {path} using safetensors.")

def load(model: Module, path: str):
    '''
    Loads a state_dict from a safetensors file into a Module.
    '''
    if not os.path.exists(path):
        raise FileNotFoundError(f"State dict file not found at: {path}")

    state_dict = st_numpy.load_file(path)    
    model.load_state_dict(state_dict)
    print("State dict successfully loaded into the model.")