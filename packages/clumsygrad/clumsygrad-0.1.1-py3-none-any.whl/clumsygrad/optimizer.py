"""
This module contains common optimizers for optimizing parameters in a computational graph.
"""

from typing import List

from .tensor import Tensor, TensorType


class SGD:
    """
    Stochastic Gradient Descent (SGD) optimizer.
    
    This optimizer updates parameters using the formula: `param -= lr * grad`,
    where `param` is a parameter tensor, `lr` is the learning rate, and `grad` is the gradient of the parameter.
    """
    
    def __init__(self, parameters: List[Tensor], lr: float = 0.01):
        """
        Initialize the SGD optimizer.
        
        Args:
            parameters (List[Tensor]): List of parameter tensors to optimize.
            lr (float): Learning rate for the optimizer. Default is 0.01.
        """
    
        self.parameters = [p for p in parameters if p._tensor_type == TensorType.PARAMETER]
        self.lr = lr
    
    def step(self):
        """Update parameters."""
        for param in self.parameters:
            if param.grad is not None:
                param._data -= self.lr * param.grad
    
    def zero_grad(self):
        """Zero gradients for all parameters."""
        for param in self.parameters:
            param.grad = None