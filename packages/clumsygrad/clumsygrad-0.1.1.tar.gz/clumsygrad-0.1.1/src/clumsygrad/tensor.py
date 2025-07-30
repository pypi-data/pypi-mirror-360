"""
This module contains the Tensor class implementation for automatic differentiation.
It supports basic tensor operations, tracks gradients, and can be used to build computational graphs for backpropagation.
It also contains some utility functions for managing tensors and their gradients.
"""

from __future__ import annotations

import gc
from enum import IntEnum
from typing import Callable, Dict, List, Optional, Set, Tuple, Union

import numpy as np

from .grad import *


class TensorType(IntEnum):
    """
    Defines tensor types in the computational graph. Each type controls gradient computation and tensor behavior.
    
    Examples:
        >>> input_tensor = Tensor([1, 2, 3], tensor_type=TensorType.INPUT)
        >>> param_tensor = Tensor([0.5, 0.3], tensor_type=TensorType.PARAMETER)
        >>> # INTERMEDIATE tensors are created automatically during operations
        >>> result = input_tensor + param_tensor  # Creates INTERMEDIATE tensor
    """
    
    INPUT = 0
    """
    Input tensor that feeds data into the computation graph.
    
    - Does not require gradients by default
    - Used for model inputs, data, and constants
    - Cannot be optimized during training
    """
    
    PARAMETER = 1
    """
    Trainable parameter tensor (weights, biases).
    
    - Requires gradients for backpropagation
    - Updated during optimization
    - Tracked in parameter collections
    """
    
    INTERMEDIATE = 2
    """
    Intermediate computation result.
    
    - Created automatically during tensor operations
    - Requires gradients if parents require gradients
    - Memory can be freed after backward pass
    """

class Tensor:
    """
    The main Tensor class, comprising the core functionality for creation and manipulation of tensors in the computational graph.
    """
    
    _id_counter = 0
    
    __slots__ = ('_data', '_shape', '_id', '_grad_fn', '_grad', '_children', '_parents',
                 '_extra', '_tensor_type', '_requires_grad')
    
    @staticmethod
    def _create_node(data: Union[np.ndarray, list, float],
                     grad_fn: Optional[Callable], 
                     parents: Tuple[Tensor, ...],
                     extra: Optional[dict] = None) -> Tensor:
        
        """
        Creates a new tensor node in the computational graph.
        By default, this node is created as an INTERMEDIATE tensor.
        
        Args:
            data: The data for the new tensor.
            grad_fn: The gradient function to use for backpropagation.
            parents: The parent tensors that this tensor depends on.
            extra: Additional metadata for the tensor (optional).
            
        Returns:
            A new Tensor instance representing the node in the computational graph. 
        """
        
        node = Tensor(data=data, tensor_type=TensorType.INTERMEDIATE)
        node._grad_fn = grad_fn
        node._parents = parents
        node._requires_grad = any(parent._requires_grad for parent in parents)
        
        if extra: node._extra.update(extra)
        for parent in parents: parent._children.append(node)
        
        return node
                
    def _cleanup_references(self):
        for parent in self._parents:
            while self in parent._children:
                parent._children.remove(self)
        
        for child in self._children:
            child._parents = tuple(p for p in child._parents if p._id != self._id)
            
        self._parents = ()
        self._children.clear()
    
    def __init__(self, 
                 data: Union[np.ndarray, list, float],
                 tensor_type: TensorType = TensorType.INPUT,
                ):
        """
        Initialize a new tensor.
        
        Args:
            data: The initial data for the tensor.
            tensor_type (TensorType): The type of the tensor, as TensorType.INPUT/PARAMETER/INTERMEDIATE (default is INPUT).
            
        Note: 
            The tensor will not track/propagate gradients if it is of type INPUT.
            If it is of type PARAMETER, it will be treated as a trainable parameter.
            Using INTERMEDIATE tensor type is nuanced and not recommended 
            unless you are explicitly creating a node in the graph.
            By default, data type is set to float32.
        """
        
        self._data = np.array(data, dtype=np.float32)
        self._shape = self._data.shape
        self._grad_fn = None
        self._grad = None
        self._tensor_type = tensor_type
        
        if self._tensor_type == TensorType.PARAMETER:
            self._requires_grad = True
        else:
            self._requires_grad = False
        
        self._parents: Tuple[Tensor, ...] = ()
        self._children: List[Tensor] = []
        
        self._id = Tensor._id_counter
        Tensor._id_counter += 1
        
        self._extra = {}
    
    def __repr__(self):
        grad_fn_name = self._grad_fn.__name__ if self._grad_fn else None
        return (f"Tensor(id={self._id}, shape={self._shape}, "
                f"tensor_type={self._tensor_type.name}, "
                f"grad_fn={grad_fn_name}, "
                f"requires_grad={self._requires_grad})")
    
    @property
    def data(self) -> np.ndarray:
        """Return the data of the tensor."""
        return self._data
    
    @property
    def shape(self) -> tuple:
        """Return the shape of the tensor."""
        return self._shape
    
    @property
    def grad(self) -> Optional[np.ndarray]:
        """Return the gradient of the tensor."""
        return self._grad
    
    @grad.setter
    def grad(self, value: np.ndarray):
        """Set the gradient of the tensor."""
        self._grad = value
    
    @property
    def requires_grad(self) -> bool:
        """Return whether this tensor requires gradients."""
        return self._requires_grad
    
    def T(self) -> Tensor:
        """
        Returns the transpose of the tensor.
        
        Note:
            Double transposing a tensor returns the original tensor node,
            and creates a new stale tensor, which needs to be cleared if required.
        """
        new_tensor = None
        
        if self._grad_fn == transpose_backward and len(self._parents) == 1:
            new_tensor = self._parents[0]
            self._cleanup_references()
        else:
            new_tensor = Tensor._create_node(
                data=self._data.T,
                grad_fn=transpose_backward,
                parents=(self,),
            )
        
        return new_tensor
    
    def __add__(self, other: Union[Tensor, float]) -> Tensor:
        if isinstance(other, Tensor):
            if self._shape != other._shape:
                raise ValueError(f"Shape mismatch for addition: {self._shape} vs {other._shape}")
            
            new_tensor = Tensor._create_node(
                data=self._data + other._data,
                grad_fn=add_backward,
                parents=(self, other),
            )
        else:
            new_tensor = Tensor._create_node(
                data=self._data + other,
                grad_fn=add_scalar_backward,
                parents=(self,),
                extra={'scalar_value': float(other)}
            )
        
        return new_tensor
    
    def __radd__(self, other: Union[Tensor, float]) -> Tensor:
        return self.__add__(other)
    
    def __sub__(self, other: Union[Tensor, float]) -> Tensor:
        if isinstance(other, Tensor):
            if self._shape != other._shape:
                raise ValueError(f"Shape mismatch for subtraction: {self._shape} vs {other._shape}")
            
            new_tensor = Tensor._create_node(
                data=self._data - other._data,
                grad_fn=sub_backward,
                parents=(self, other),
            )
        else:
            new_tensor = Tensor._create_node(
                data=self._data - other,
                grad_fn=sub_scalar_backward,
                parents=(self,),
                extra={'scalar_value': float(other)}
            )
        
        return new_tensor
    
    def __mul__(self, other: Union[Tensor, float]) -> Tensor:
        if isinstance(other, Tensor):
            if self._shape != other._shape:
                raise ValueError(f"Shape mismatch for multiplication: {self._shape} vs {other._shape}")
            
            new_tensor = Tensor._create_node(
                data=self._data * other._data,
                grad_fn=mul_backward,
                parents=(self, other),
            )
        else:
            new_tensor = Tensor._create_node(
                data=self._data * other,
                grad_fn=mul_scalar_backward,
                parents=(self,),
                extra={'scalar_value': float(other)}
            )
        
        return new_tensor
    
    def __rmul__(self, other: Union[Tensor, float]) -> Tensor:
        return self.__mul__(other)
    
    def __matmul__(self, other: Tensor) -> Tensor:
        if not isinstance(other, Tensor):
            raise TypeError("Right operand must be a Tensor for matrix multiplication.")
        
        if len(self._shape) < 2 or len(other._shape) < 2:
            raise ValueError("Matrix multiplication requires at least 2D tensors.")
        
        if self._shape[-1] != other._shape[-2]:
            raise ValueError(f"Matrix shapes not aligned: {self._shape} @ {other._shape}")
        
        new_tensor = Tensor._create_node(
            data=self._data @ other._data,
            grad_fn=matmul_backward,
            parents=(self, other),
        )
        return new_tensor
    
    def __pow__(self, power: float) -> Tensor:
        new_tensor = Tensor._create_node(
            data=self._data ** power,
            grad_fn=power_backward,
            parents=(self,),
            extra={'power': float(power)}
        )
        return new_tensor
    
    def __neg__(self) -> Tensor:
        new_tensor = Tensor._create_node(
            data=-self._data,
            grad_fn=negate_backward,
            parents=(self,),
        )
        return new_tensor
    
    def reshape(self, new_shape: Tuple[int, ...]) -> Tensor:
        """
        Reshape the tensor to a new shape.
        
        Args:
            new_shape: The desired shape for the tensor.
            
        Returns:
            A new Tensor with the reshaped data.
            
        Raises:
            ValueError: If the new shape does not have the same number of elements as the original shape.
        """
    
        if np.prod(new_shape) != np.prod(self._shape):
            raise ValueError("New shape must have the same number of elements as the original shape.")
        
        new_tensor = Tensor._create_node(
            data=self._data.reshape(new_shape),
            grad_fn=reshape_backward,
            parents=(self,),
            extra={'original_shape': self._shape}
        )
        return new_tensor
    
    def backward(self, gradient: Optional[np.ndarray | float] = None, keep_graph: bool = False):
        """
        backward pass to compute gradients. Once the backward pass is completed, the graph is freed from memory unless `keep_graph` is set to True.
        Only the current tensor and all INPUT/PARAMETER tensors will be retained in memory.
        
        Args:
            gradient: Optional gradient to start the backward pass. If None, it assumes a scalar output and uses ones.
            keep_graph: If True, keeps the computational graph for further backward passes.
            
        Raises:
            RuntimeError: If the tensor does not require gradients or if the gradient is not compatible.
            
        Note:
            - Setting `keep_graph=True` inside a training loop can lead to memory leaks.
            
        Example:
            >>> t = Tensor(np.array([1.0, 2.0, 3.0]), tensor_type=TensorType.PARAMETER)
            >>> y = t ** 2 + 3 * t + 2
            >>> y.backward()
        """
        
        if not self._requires_grad:
            raise RuntimeError("Tensor does not require gradients")
        
        if gradient is None:
            if self._data.size != 1:
                raise RuntimeError("Gradient can only be implicitly created for scalar outputs")
            gradient = np.ones_like(self._data)
            
        self._grad = gradient
        
        topo_order: List[Tensor] = []
        visited: Set[Tensor] = set()
        
        def build_topo(node: Tensor):
            if node._id in visited or not node._requires_grad:
                return
            visited.add(node._id)
            
            for parent in node._parents:
                build_topo(parent)
            topo_order.append(node)
        
        build_topo(self)
        
        for node in reversed(topo_order):
            if node._grad_fn and node._grad is not None:
                gradients = node._grad_fn(node, node._grad)
                
                for parent, grad in zip(node._parents, gradients):
                    if parent._requires_grad:
                        if parent._grad is None:
                            parent._grad = grad
                        else:
                            parent._grad = parent._grad + grad
            
                # If the node is an intermediate node and we are not keeping gradients,
                # we clear its gradient to save memory.
                if node._tensor_type == TensorType.INTERMEDIATE:      
                    node._grad = None
               
        if not keep_graph:    
            for node in topo_order:
                if node == self:
                    node._parents = ()
                elif node._tensor_type == TensorType.INTERMEDIATE:
                    node._cleanup_references()
                    
        gc.collect()
            
class TensorUtils:
    @staticmethod
    def get_parameters(tensor: Tensor) -> List[Tensor]:
        """
        Collect all parameters in the computational graph starting from the given tensor.
        
        Args:
            tensor: The starting tensor from which to collect parameters.
            
        Returns:
            A list of Tensor objects that are parameters in the graph.
        """
        
        parameters = []
        visited = set()
        
        def collect_params(node):
            if node._id in visited:
                return
            visited.add(node._id)
            
            if node._tensor_type == TensorType.PARAMETER:
                parameters.append(node)
            
            for parent in (node._parents or ()):
                collect_params(parent)
        
        collect_params(tensor)
        return parameters
    
    @staticmethod
    def count_by_type(tensor: Tensor) -> Dict[TensorType, int]:
        """
        Counts the number of tensors of each type in the computational graph starting from the given tensor.
        
        Args:
            tensor: The starting tensor from which to count tensor types.
            
        Returns:
            A dictionary with counts of each tensor type (INPUT, PARAMETER, INTERMEDIATE).
        """
        
        counts = {TensorType.INPUT: 0, TensorType.PARAMETER: 0, TensorType.INTERMEDIATE: 0}
        visited = set()
        
        def count_nodes(node):
            if node._id in visited:
                return
            visited.add(node._id)
            counts[node._tensor_type] += 1
            
            for child in (node._parents or []):
                count_nodes(child)
        
        count_nodes(tensor)
        return counts