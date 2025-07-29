from .tensors import Tensor
from .nn import Module

class Loss(Module):
    '''
    Base class for all loss functions
    '''
    def forward(self, y_pred: Tensor, y_true: Tensor) -> Tensor:
        '''
        Computes the loss
        '''
        raise NotImplementedError

class MSELoss(Loss):
    '''
    Calculates the Mean Squared Error loss
    '''
    def forward(self, y_pred: Tensor, y_true: Tensor) -> Tensor:
        if y_pred.data.shape != y_true.data.shape:
             raise ValueError(f"Shape mismatch for MSELoss: y_pred has {y_pred.data.shape}, y_true has {y_true.data.shape}")
        
        return ((y_pred - y_true) ** 2).mean()

class CrossEntropyLoss(Loss):
    '''
    Calculates the Cross-Entropy loss
    '''
    def __init__(self, epsilon: float = 1e-12):
        super().__init__()
        self.epsilon = epsilon
    
    def forward(self, y_pred: Tensor, y_true: Tensor) -> Tensor:
        if y_pred.data.shape != y_true.data.shape:
             raise ValueError(f"Shape mismatch for CrossEntropyLoss: y_pred has {y_pred.data.shape}, y_true has {y_true.data.shape}")

        loss = -(y_true * (y_pred + self.epsilon).log()).sum()
        batch_size = y_pred.data.shape[0] if y_pred.data.ndim > 1 else 1
        
        return loss / batch_size