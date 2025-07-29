from typing import List
from .tensors import Tensor

class Optimizer:
    '''
    Base class for all optimizers
    '''
    def __init__(self, params: List[Tensor], lr: float):
        if lr < 0.0:
            raise ValueError(f"Invalid learning rate: {lr}")
        self.params = params
        self.lr = lr

    def step(self):
        '''
        Updates the parameters
        '''
        raise NotImplementedError

    def zero_grad(self):
        for p in self.params:
            p.zero_grad()


class SGD(Optimizer):
    '''
    Implements Stochastic Gradient Descent optimizer
    '''
    def __init__(self, params: List[Tensor], lr: float):
        super().__init__(params, lr)

    def step(self):
        for p in self.params:
            if p.grad is not None and p.requires_grad:
                p.data -= self.lr * p.grad