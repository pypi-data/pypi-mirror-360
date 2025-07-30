"""
This module provides functions to compute various loss functions.
"""

from __future__ import annotations

import numpy as np

from .grad import mae_backward, mse_backward
from .tensor import Tensor


def mse_loss(pred: Tensor, target: Tensor) -> Tensor:
    """
    Computes the Mean Squared Error (MSE) loss between the predicted and target tensors.
    
    Args:
        pred: The predicted tensor.
        target: The target tensor.
        
    Returns:
        Tensor: The MSE loss tensor.
    """
    
    if pred._shape != target._shape:
        raise ValueError("Predicted and target tensors must have the same shape for MSE loss.")
    
    diff = pred._data - target._data
    mse = np.mean(np.square(diff))
    
    new_tensor = Tensor._create_node(
        data=mse,
        grad_fn=mse_backward,
        parents=(pred, target)
    )
    
    return new_tensor
    
def mae_loss(pred: Tensor, target: Tensor) -> Tensor:
    """
    Computes the Mean Absolute Error (MAE) loss between the predicted and target tensors.
    
    Args:
        pred: The predicted tensor.
        target: The target tensor.
        
    Returns:
        Tensor: The MAE loss tensor.
    """
    
    if pred._shape != target._shape:
        raise ValueError("Predicted and target tensors must have the same shape for MAE loss.")
    
    diff = np.abs(pred._data - target._data)
    mae = np.mean(diff)
    
    new_tensor = Tensor._create_node(
        data=mae,
        grad_fn=mae_backward,
        parents=(pred, target)  
    )
    
    return new_tensor