"""
This module provides various activation functions for tensors.
"""

import numpy as np

from .grad import (relu_backward, sigmoid_backward, softmax_backward,
                   tanh_backward)
from .tensor import Tensor


def tanh(tensor: Tensor) -> Tensor:
    r"""
    Element-wise hyperbolic tangent activation function.
    
    .. math::
        \tanh(x) = \frac{e^x - e^{-x}}{e^x + e^{-x}}
    
    Args:
        tensor: Input tensor.
        
    Returns:
        Tensor: A new tensor containing the hyperbolic tangent of the input tensor.
    """
    
    new_tensor = Tensor._create_node(
        data=np.tanh(tensor._data),
        grad_fn=tanh_backward,
        parents=(tensor,)
    )
    return new_tensor

def relu(tensor: Tensor) -> Tensor:
    r"""
    Element-wise Rectified Linear Unit (ReLU) activation function.
    
    .. math::
        \text{ReLU}(x) = \max(0, x)
    
    Args:
        tensor: Input tensor.
        
    Returns:
        Tensor: A new tensor containing the ReLU activation of the input tensor.
    """

    new_tensor = Tensor._create_node(
        data=np.maximum(0, tensor._data),
        grad_fn=relu_backward,
        parents=(tensor,)
    )
    return new_tensor

def sigmoid(tensor: Tensor) -> Tensor:
    r"""
    Element-wise sigmoid activation function.
    
    .. math::
        \sigma(x) = \frac{1}{1 + e^{-x}}
    
    Args:
        tensor: Input tensor.
        
    Returns:
        Tensor: A new tensor containing the sigmoid activation of the input tensor. 
    """
    
    new_tensor = Tensor._create_node(
        data=1 / (1 + np.exp(-tensor._data)),
        grad_fn=sigmoid_backward,
        parents=(tensor,)
    )
    return new_tensor

def softmax(tensor: Tensor, axis=-1) -> Tensor:
    r"""
    Element-wise softmax activation function.
    
    .. math::
        \text{softmax}(x_i) = \frac{e^{x_i}}{\sum_j e^{x_j}}
        
    Args:
        tensor: Input tensor.
        axis: Axis along which to compute the softmax. Default is -1 (last axis).
        
    Returns:
        Tensor: A new tensor containing the softmax activation of the input tensor.
        
    Note:
        The data in the input tensor is shifted by subtracting the maximum value along the specified axis
        to prevent overflow in the exponential computation.
    """
    
    x_shifted = tensor._data - np.max(tensor._data, axis=axis, keepdims=True)
    exp_x = np.exp(x_shifted)
    softmax_output = exp_x / np.sum(exp_x, axis=axis, keepdims=True)
    
    new_tensor = Tensor._create_node(
        data=softmax_output,
        grad_fn=softmax_backward,
        parents=(tensor,),
        extra={'axis': axis}
    )
    return new_tensor