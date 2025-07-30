"""
This module provides basic mathematical operations.
"""

import numpy as np

from .grad import (abs_backward, cos_backward, exp_backward, log_backward,
                   mean_backward, sin_backward, sqrt_backward, sum_backward,
                   tan_backward)
from .tensor import Tensor


def sum(tensor: Tensor, axis=None, keepdims=False) -> Tensor:
    """
    Compute the sum of the tensor along specified axis.
    
    Args:
        tensor: The input Tensor to compute the sum of.
        axis: Axis or axes along which the sum is computed. Default is None, which computes the sum of the flattened array.
        keepdims: If True, the reduced axes are left in the result as dimensions with size one.
        
    Returns:
        A new Tensor containing the sum of the input tensor.
    """
    
    new_tensor = Tensor._create_node(
        data=np.sum(tensor._data, axis=axis, keepdims=keepdims),
        grad_fn=sum_backward,
        parents=(tensor,),
        extra={'axis': axis, 'keepdims': keepdims, 'input_shape': tensor._shape}
    )
    return new_tensor

def mean(tensor: Tensor, axis=None, keepdims=False) -> Tensor:
    """
    Compute the mean of the tensor along specified axis.
    
    Args:
        tensor: The input Tensor to compute the mean of.
        axis: Axis or axes along which the means are computed. Default is None, which computes the mean of the flattened array.
        keepdims: If True, the reduced axes are left in the result as dimensions with size one.
        
    Returns:
        A new Tensor containing the mean of the input tensor.
    """
    
    new_tensor = Tensor._create_node(
        data=np.mean(tensor._data, axis=axis, keepdims=keepdims),
        grad_fn=mean_backward,
        parents=(tensor,),
        extra={'axis': axis, 'keepdims': keepdims, 'input_shape': tensor._shape}
    )
    return new_tensor

def abs(tensor: Tensor) -> Tensor:
    """
    Compute the absolute value of the tensor.
    """
    
    new_tensor = Tensor._create_node(
        data=np.abs(tensor._data),
        grad_fn=abs_backward,
        parents=(tensor,),
    )
    return new_tensor

def sqrt(tensor: Tensor) -> Tensor:
    """
    Compute the square root of the tensor.
    """
    
    new_tensor = Tensor._create_node(
        data=np.sqrt(tensor._data),
        grad_fn=sqrt_backward,
        parents=(tensor,),
    )
    return new_tensor

def exp(tensor: Tensor) -> Tensor:
    """
    Compute the exponential of the tensor.
    """
    
    new_tensor = Tensor._create_node(
        data=np.exp(tensor._data),
        grad_fn=exp_backward,
        parents=(tensor,),
    )
    return new_tensor

def log(tensor: Tensor) -> Tensor:
    """
    Compute the natural logarithm of the tensor.
    """
    
    new_tensor = Tensor._create_node(
        data=np.log(tensor._data),
        grad_fn=log_backward,
        parents=(tensor,),
    )
    return new_tensor

def sin(tensor: Tensor) -> Tensor:
    """
    Compute the sine of the tensor.
    """
    
    new_tensor = Tensor._create_node(
        data=np.sin(tensor._data),
        grad_fn=sin_backward,
        parents=(tensor,),
    )
    return new_tensor

def cos(tensor: Tensor) -> Tensor:
    """
    Compute cosine of tensor.
    """
    
    new_tensor = Tensor._create_node(
        data=np.cos(tensor._data),
        grad_fn=cos_backward,
        parents=(tensor,),
    )
    return new_tensor

def tan(tensor: Tensor) -> Tensor:
    """
    Compute tangent of tensor.
    """
    
    new_tensor = Tensor._create_node(
        data=np.tan(tensor._data),
        grad_fn=tan_backward,
        parents=(tensor,),
    )
    return new_tensor