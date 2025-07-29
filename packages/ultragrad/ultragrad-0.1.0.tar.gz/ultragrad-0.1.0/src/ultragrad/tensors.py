import numpy as np
from numpy.typing import NDArray

class Tensor_Error(Exception):
    '''
    Custom exception for Tensor class errors
    '''
    pass

class Tensor:
    '''
    Tensor class is the core autograd engine for 
    multiple dimensional Tensors
    '''

    def __init__(self,data,_children=(),_op:str='',_label:str='',requires_grad=True):
        if not isinstance(data, np.ndarray):
            try:
                data = np.array(data, dtype=np.float64)
            except (TypeError, ValueError):
                raise Tensor_Error(f"Tensor data must be convertible to a numpy array and you have provided {data}")
            
        if data.dtype != np.float64:
            data = data.astype(np.float64)

        self.data = data
        
        # computational graph parameters
        self._children = set(_children)
        self._op = _op
        self._label = _label

        # backward parameters
        self.grad = np.zeros_like(data,dtype=data.dtype)
        
        self._backward = lambda : None
        self.requires_grad = requires_grad

    def __repr__(self):
        return f"Tensor(data={self.data},shape={self.data.shape})"
    
    def _unbroadcast_grad(self, grad: NDArray) -> NDArray:
        '''
        For doing the backpropagation on same shape
        '''
        ndim_diff = grad.ndim - self.data.ndim
        if ndim_diff > 0:
            grad = grad.sum(axis=tuple(range(ndim_diff)))

        axes_to_sum = tuple(i for i, (s_self, s_grad) in enumerate(zip(self.data.shape, grad.shape)) if s_self == 1 and s_grad > 1)
        if axes_to_sum:
            grad = grad.sum(axis=tuple(axes_to_sum), keepdims=True)
        
        return grad
    
    # mathematical operations
    def __add__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other, requires_grad=False)
        out = Tensor(self.data + other.data, _children=(self, other), _op='+')

        def _backward():
            if self.requires_grad:
                self.grad += self._unbroadcast_grad(out.grad)
            if other.requires_grad:
                other.grad += other._unbroadcast_grad(out.grad)

        out._backward = _backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other, requires_grad=False)
        out = Tensor(self.data * other.data, _children=(self, other), _op='*')
        
        def _backward():
            if self.requires_grad:
                grad_self = out.grad * other.data
                self.grad += self._unbroadcast_grad(grad_self)
            if other.requires_grad:
                grad_other = out.grad * self.data
                other.grad += other._unbroadcast_grad(grad_other)

        out._backward = _backward
        return out

    def __sub__(self,other):
        return self + (-other)

    def __truediv__(self,other):
        return self * (other**-1)

    def __pow__(self, other: float):
        if not isinstance(other, (int, float)):
            raise Tensor_Error(f"Power can only be applied with a scalar value, here the value used is {other}")
        out = Tensor(self.data ** other, _children=(self,), _op='**')

        def _backward():
            if self.requires_grad:
                self.grad += out.grad * (other * (self.data ** (other - 1)))

        out._backward = _backward
        return out

    def __neg__(self):
        return self * -1
    
    # reverse mathematical operations
    def __radd__(self,other):
        return self + other
    
    def __rmul__(self,other):
        return self * other
    
    def __rsub__(self, other):
        return Tensor(other, requires_grad=False) - self
    
    def __rtruediv__(self, other):
        return other * (self ** -1)
    
    # reduction operations
    def sum(self, axis=None, keepdims=False):
        '''
        sum method is used for regularization functions like L1 and L2
        '''
        out = Tensor(np.sum(self.data, axis=axis, keepdims=keepdims), _children=(self,), _op='sum')

        def _backward():
            if self.requires_grad:
                self.grad += out.grad * np.ones_like(self.data)

        out._backward = _backward
        return out

    def mean(self, axis=None, keepdims=False):
        '''
        mean method is used for loss functions
        '''
        total_sum = self.sum(axis=axis, keepdims=keepdims)
        if axis is None:
            count = self.data.size
        else:
            axis = (axis,) if isinstance(axis, int) else tuple(axis)
            count = np.prod([self.data.shape[i] for i in axis])
        
        return total_sum / count
    
    # matrix operations
    def matmul(self, other):
        '''
        matrix multiplication of two Tensors
        '''
        other = other if isinstance(other, Tensor) else Tensor(other, requires_grad=False)
        if self.data.ndim < 2 or other.data.ndim < 2:
            raise Tensor_Error("Matrix multiplication requires at least 2D Tensor")

        out = Tensor(np.matmul(self.data, other.data), _children=(self, other), _op='matmul')
        
        def _backward():
            if self.requires_grad:
                grad_self = np.matmul(out.grad, other.data.swapaxes(-1, -2))
                self.grad += self._unbroadcast_grad(grad_self)
            if other.requires_grad:
                grad_other = np.matmul(self.data.swapaxes(-1, -2), out.grad)
                other.grad += other._unbroadcast_grad(grad_other)

        out._backward = _backward
        return out
    
    def __matmul__(self, other):
        return self.matmul(other)
    
    def reshape(self, *new_shape):
        '''
        reshape method is used to change the shape of the Tensor
        '''
        if len(new_shape) == 1 and isinstance(new_shape[0], (tuple, list)):
            new_shape = new_shape[0]
        out = Tensor(self.data.reshape(new_shape), _children=(self,), _op='reshape')

        def _backward():
            if self.requires_grad:
                self.grad += out.grad.reshape(self.data.shape)

        out._backward = _backward
        return out

    def transpose(self, axes=None):
        '''
        transposing the columns to rows and rows to columns
        '''
        out = Tensor(self.data.transpose(axes), _children=(self,), _op='transpose')

        def _backward():
            if self.requires_grad:
                if axes is None:
                    inv_axes = None
                else:
                    inv_axes = np.argsort(axes)
                self.grad += out.grad.transpose(inv_axes)

        out._backward = _backward
        return out
    
    # activation functions
    def relu(self):
        '''
        Rectified Linear Unit activation function
        '''
        out = Tensor(np.maximum(0, self.data), _children=(self,), _op='relu')

        def _backward():
            if self.requires_grad:
                self.grad += out.grad * (self.data > 0)
        
        out._backward = _backward
        return out

    def tanh(self):
        '''
        Tanh is a hyberbolic activation function
        '''
        out = Tensor(np.tanh(self.data), _children=(self,), _op='tanh')

        def _backward():
            if self.requires_grad:
                self.grad += out.grad * (1 - out.data**2)

        out._backward = _backward
        return out
    
    def sigmoid(self):
        '''
        Sigmoid is a common activation function
        '''
        out = Tensor(1 / (1 + np.exp(-self.data)), _children=(self,), _op='sigmoid')

        def _backward():
            if self.requires_grad:
                self.grad += out.grad * (out.data * (1 - out.data))

        out._backward = _backward
        return out
    
    def leaky_relu(self, alpha=0.01):
        '''
        Next version of RELU function
        '''
        out = Tensor(np.where(self.data > 0, self.data, alpha * self.data), _children=(self,), _op='leaky_relu', requires_grad=self.requires_grad)
        
        def _backward():
            if self.requires_grad:
                self.grad += out.grad * np.where(self.data > 0, 1.0, alpha)
        
        out._backward = _backward
        return out

    def exp(self):
        '''
        Exponential function is an activation function
        '''
        out = Tensor(np.exp(self.data), _children=(self,), _op='exp')

        def _backward():
            if self.requires_grad:
                self.grad += out.grad * out.data

        out._backward = _backward
        return out

    def log(self):
        '''
        Log method is used in finding the loss value
        '''
        out = Tensor(np.log(self.data), _children=(self,), _op='log')

        def _backward():
            if self.requires_grad:
                self.grad += out.grad / self.data

        out._backward = _backward
        return out
    
    def softmax(self, axis=-1):
        '''
        Softmax activation function is mostly used for categorization at final layer
        '''
        e_x = np.exp(self.data - np.max(self.data, axis=axis, keepdims=True))
        out_data = e_x / e_x.sum(axis=axis, keepdims=True)
        out = Tensor(out_data, _children=(self,), _op='softmax')
        
        def _backward():
            if self.requires_grad:
                s = out.data
                grad_s = out.grad
                self.grad += s * (grad_s - (grad_s * s).sum(axis=axis, keepdims=True))

        out._backward = _backward
        return out
    
    # backward propagation
    def backward(self, gradient = None):
        '''
        Backpropagation of Tensor values to calculate the gradients for the Tensors
        '''
        if not self.requires_grad:
            return

        if gradient is None:
            if self.data.size != 1:
                raise Tensor_Error("backward() can only be called implicitly on a scalar Tensor.")
            self.grad = np.ones_like(self.data)
        else:
            if not isinstance(gradient, np.ndarray):
                gradient = np.array(gradient, dtype=np.float64)
            if gradient.shape != self.data.shape:
                raise Tensor_Error(f"Gradient shape mismatch. Expected {self.data.shape}, got {gradient.shape}")
            self.grad = np.array(gradient)

        topo = []
        visited = set()
        def build_topo(v):
            if v not in visited:
                visited.add(v)
                for child in v._children:
                    build_topo(child)
                topo.append(v)
        build_topo(self)
        
        for node in reversed(topo):
            node._backward()
    
    def zero_grad(self):
        self.grad.fill(0.0)