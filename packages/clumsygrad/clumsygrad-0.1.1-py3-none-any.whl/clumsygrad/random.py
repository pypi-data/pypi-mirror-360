from typing import Tuple

import numpy as np

from .tensor import Tensor, TensorType


def rand(shape: Tuple[int, ...], tensor_type: TensorType = TensorType.INPUT) ->Tensor:
    """
    Create a new tensor with random values.
    
    Args:
        shape: The shape of the tensor to create.
        tensor_type: The type of the tensor (default is INPUT).
        
    Returns:
        A new Tensor instance with random values.
        
    Example:
        >>> import clumsygrad as cg
        >>> tensor = cg.random.rand((2, 3), tensor_type=cg.TensorType.PARAMETER)
        >>> print(tensor)
        
    """
    
    data = np.random.rand(*shape).astype(np.float32)
    return Tensor(data=data, tensor_type=tensor_type)

def randn(shape: Tuple[int, ...], tensor_type: TensorType = TensorType.INPUT) -> Tensor:
    """
    Create a new tensor with random values from a normal distribution.
    
    Args:
        shape: The shape of the tensor to create.
        tensor_type: The type of the tensor (default is INPUT).
        
    Returns:
        A new Tensor instance with random values from a normal distribution.
        
    Example:
        >>> import clumsygrad as cg
        >>> tensor = cg.random.randn((2, 3), tensor_type=cg.TensorType.PARAMETER)
        >>> print(tensor)
        
    """
    
    data = np.random.randn(*shape).astype(np.float32)
    return Tensor(data=data, tensor_type=tensor_type)