"""
This module contains backward functions for various tensor operations in a computational graph.

All functions have a generic signature that takes a tensor and the any/tensor's gradient as inputs, 
and returns a tuple of gradients for each parent tensor.

Args:
    tensor: Result tensor from the forward operation
    grad: Gradient flowing back from the next layer
    
Returns:
    Tuple of gradients for each parent tensor
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

import numpy as np

if TYPE_CHECKING:
    from .tensor import Tensor

GradientTuple = Tuple[np.ndarray, ...]
"""
A tuple of gradients for each parent tensor.
"""

"""
Elemetary backward functions for tensor operations.
"""

def transpose_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for transpose operation.
    
    For :math:`z = x^T`:
    
    .. math::
        \frac{\partial z}{\partial x} = \text{grad}^T
    """
    return (grad.T,)

def add_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for addition operation.
    
    For :math:`z = x + y`:
    
    .. math::
        \frac{\partial z}{\partial x} = 1, \quad \frac{\partial z}{\partial y} = 1
    """
    return (grad, grad)

def add_scalar_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for tensor + scalar operation.
    
    For :math:`z = x + c` where :math:`c` is scalar:
    
    .. math::
        \frac{\partial z}{\partial x} = 1
    """
    return (grad,)

def sub_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for subtraction operation.
    
    For :math:`z = x - y`:
    
    .. math::
        \frac{\partial z}{\partial x} = 1, \quad \frac{\partial z}{\partial y} = -1
    """
    return (grad, -grad)

def sub_scalar_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for tensor - scalar operation.
    
    For :math:`z = x - c` where :math:`c` is scalar:
    
    .. math::
        \frac{\partial z}{\partial x} = 1
    """
    return (grad,)

def mul_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for element-wise multiplication.
    
    For :math:`z = x \odot y`:
    
    .. math::
        \frac{\partial z}{\partial x} = y, \quad \frac{\partial z}{\partial y} = x
    """
    x, y = tensor._parents
    return (grad * y._data, grad * x._data)

def mul_scalar_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for tensor * scalar operation.
    
    For :math:`z = x \cdot c` where :math:`c` is scalar:
    
    .. math::
        \frac{\partial z}{\partial x} = c
    """
    x = tensor._parents[0]
    scalar = tensor._extra.get('scalar_value', 1)
    return (grad * scalar,)

def matmul_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for matrix multiplication.
    
    For :math:`Z = X \cdot Y`:
    
    .. math::
        \frac{\partial Z}{\partial X} = \text{grad} \cdot Y^T, \quad 
        \frac{\partial Z}{\partial Y} = X^T \cdot \text{grad}
    """
    x, y = tensor._parents
    return (grad @ y._data.T, x._data.T @ grad)

def power_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for power operation.
    
    For :math:`z = x^n`:
    
    .. math::
        \frac{\partial z}{\partial x} = n \cdot x^{n-1}
    """
    x = tensor._parents[0]
    power = tensor._extra.get('power', 1)
    return (grad * (power * (x._data ** (power - 1))),)

def negate_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for negation operation.
    
    For :math:`z = -x`:
    
    .. math::
        \frac{\partial z}{\partial x} = -1
    """
    return (-grad,)

def abs_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for absolute value operation.
    
    For :math:`z = |x|`:
    
    .. math::
        \frac{\partial z}{\partial x} = \text{sign}(x) = \begin{cases}
        1 & \text{if } x > 0 \\
        -1 & \text{if } x < 0 \\
        0 & \text{if } x = 0
        \end{cases}
    """
    x = tensor._parents[0]
    return (grad * np.sign(x._data),)

def reshape_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for reshape operation.
    
    For :math:`z = \text{reshape}(x, \text{new\_shape})`:
    
    .. math::
        \frac{\partial z}{\partial x} = \text{reshape}(\text{grad}, \text{original\_shape})
    
    Since reshape only changes the view of the data without changing values,
    the gradient is simply reshaped back to the original shape.
    """
    input_shape = tensor._extra.get('original_shape')
    return (grad.reshape(input_shape),)


"""
Backward functions for reduction operations.
"""

def sum_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for sum operation.
    
    For :math:`z = \sum_{i \in \text{axis}} x_i`:
    
    .. math::
        \frac{\partial z}{\partial x_i} = \begin{cases}
        1 & \text{if } i \in \text{axis} \\
        0 & \text{otherwise}
        \end{cases}
    
    This function handles dimension reduction by broadcasting gradients back to the original shape.
    """
    
    input_shape = tensor._extra.get('input_shape')
    axis = tensor._extra.get('axis')
    keepdims = tensor._extra.get('keepdims', False)
    
    if axis is not None and not keepdims:
        if isinstance(axis, int):
            axis = (axis,)
        elif axis is None:
            axis = tuple(range(len(input_shape)))
        
        expanded_grad = grad
        for ax in sorted(axis):
            expanded_grad = np.expand_dims(expanded_grad, axis=ax)
    else:
        expanded_grad = grad

    broadcasted_grad = np.broadcast_to(expanded_grad, input_shape)
    
    return (broadcasted_grad,)

def mean_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for mean operation.
    
    For :math:`z = \frac{1}{n}\sum_{i \in \text{axis}} x_i`:
    
    .. math::
        \frac{\partial z}{\partial x_i} = \begin{cases}
        \frac{1}{n} & \text{if } i \in \text{axis} \\
        0 & \text{otherwise}
        \end{cases}
    
    where :math:`n` is the number of elements being averaged.
    """
    input_shape = tensor._extra.get('input_shape')
    axis = tensor._extra.get('axis')
    keepdims = tensor._extra.get('keepdims', False)
    
    if axis is None:
        n = np.prod(input_shape)
        broadcasted_grad = np.broadcast_to(grad / n, input_shape)
    else:
        if isinstance(axis, int):
            axis = (axis,)
        
        n = np.prod([input_shape[ax] for ax in axis])
        
        expanded_grad = grad / n
        if not keepdims:
            for ax in sorted(axis):
                expanded_grad = np.expand_dims(expanded_grad, axis=ax)
        
        broadcasted_grad = np.broadcast_to(expanded_grad, input_shape)
    
    return (broadcasted_grad,)

"""
Backward functions for mathematical operations.
"""

def exp_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for exponential operation.
    
    For :math:`z = e^x`:
    
    .. math::
        \frac{\partial z}{\partial x} = e^x
    """
    return (grad * tensor._data,)

def log_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for natural logarithm operation.
    
    For :math:`z = \ln(x)`:
    
    .. math::
        \frac{\partial z}{\partial x} = \frac{1}{x}
    """
    x = tensor._parents[0]
    return (grad / x._data,)

def sqrt_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for square root operation.
    
    For :math:`z = \sqrt{x}`:
    
    .. math::
        \frac{\partial z}{\partial x} = \frac{1}{2\sqrt{x}}
    """
    x = tensor._parents[0]
    return (grad / (2 * np.sqrt(x._data)),)

def sin_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for sine operation.
    
    For :math:`z = \sin(x)`:
    
    .. math::
        \frac{\partial z}{\partial x} = \cos(x)
    """
    x = tensor._parents[0]
    return (grad * np.cos(x._data),)

def cos_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for cosine operation.
    
    For :math:`z = \cos(x)`:
    
    .. math::
        \frac{\partial z}{\partial x} = -\sin(x)
    """
    x = tensor._parents[0]
    return (grad * -np.sin(x._data),)

def tan_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for tangent operation.
    
    For :math:`z = \tan(x)`:
    
    .. math::
        \frac{\partial z}{\partial x} = \sec^2(x)
    """
    x = tensor._parents[0]
    return (grad * (1 / np.cos(x._data) ** 2),)


"""
Backward functions for activation functions.
"""

def relu_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for ReLU activation.
    
    For :math:`z = \text{ReLU}(x) = \max(0, x)`:
    
    .. math::
        \frac{\partial z}{\partial x} = \begin{cases}
        1 & \text{if } x > 0 \\
        0 & \text{otherwise}
        \end{cases}
    """
    return (grad * (tensor._data > 0).astype(np.float32),)

def sigmoid_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for Sigmoid activation.
    
    For :math:`z = \sigma(x) = \frac{1}{1 + e^{-x}}`:
    
    .. math::
        \frac{\partial z}{\partial x} = \sigma(x) \cdot (1 - \sigma(x))
    """
    sigmoid_output = 1 / (1 + np.exp(-tensor._data))
    return (grad * sigmoid_output * (1 - sigmoid_output),)

def tanh_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for hyperbolic tangent activation.
    
    For :math:`z = \tanh(x)`:
    
    .. math::
        \frac{\partial z}{\partial x} = 1 - \tanh^2(x)
    """
    tanh_output = tensor._data
    return (grad * (1 - tanh_output ** 2),)

def softmax_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for softmax activation.
    
    For :math:`z_i = \frac{e^{x_i}}{\sum_{j} e^{x_j}}`:
    
    .. math::
        \frac{\partial z_i}{\partial x_j} = \begin{cases}
        z_i(1 - z_i) & \text{if } i = j \\
        -z_i z_j & \text{if } i \neq j
        \end{cases}
    
    The gradient computation simplifies to:
    
    .. math::
        \frac{\partial L}{\partial x} = z \odot \left(\text{grad} - \sum(z \odot \text{grad})\right)
    """
    softmax_output = tensor._data
    
    axis = tensor._extra.get('axis', -1)
    grad_input = softmax_output * (grad - np.sum(softmax_output * grad, axis=axis, keepdims=True))
    
    return (grad_input,)


"""
Backward functions for loss functions.
"""

def mse_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for Mean Squared Error loss.
    
    For :math:`L = (\text{pred} - \text{target})^2`:
    
    .. math::
        \frac{\partial L}{\partial \text{pred}} = 2(\text{pred} - \text{target})
        
        \frac{\partial L}{\partial \text{target}} = -2(\text{pred} - \text{target})
    """
    pred, target = tensor._parents
    diff = pred._data - target._data
    return (2 * diff * grad, -2 * diff * grad)

def mae_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for Mean Absolute Error loss.
    
    For :math:`L = |\text{pred} - \text{target}|`:
    
    .. math::
        \frac{\partial L}{\partial \text{pred}} = \frac{1}{n} \cdot \text{sign}(\text{pred} - \text{target})
        
        \frac{\partial L}{\partial \text{target}} = -\frac{1}{n} \cdot \text{sign}(\text{pred} - \text{target})
    
    where :math:`n` is the number of elements.
    """
    pred, target = tensor._parents
    diff = pred._data - target._data
    n = pred._data.size
    sign_diff = np.sign(diff)
    
    return (grad * sign_diff / n, grad * (-sign_diff) / n)

"""
Backward functions fro broadcasting operations.
"""

def add_broadcast_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for broadcasted addition operation.
    
    For :math:`z = x + y` where :math:`x` and :math:`y` have different but broadcastable shapes:
    
    .. math::
        \frac{\partial z}{\partial x} = \text{reduce}(\text{grad}, \text{left\_shape})
        
        \frac{\partial z}{\partial y} = \text{reduce}(\text{grad}, \text{right\_shape})
    
    The gradients are reduced (summed) along broadcasted dimensions and reshaped 
    to match the original tensor shapes.
    """
    left_shape = tensor._extra.get('left_shape')
    right_shape = tensor._extra.get('right_shape')
    
    left_grad = _reduce_gradient_to_shape(grad, left_shape)
    right_grad = _reduce_gradient_to_shape(grad, right_shape)
    
    return (left_grad, right_grad)

def sub_broadcast_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for broadcasted subtraction operation.
    
    For :math:`z = x - y` where :math:`x` and :math:`y` have different but broadcastable shapes:
    
    .. math::
        \frac{\partial z}{\partial x} = \text{reduce}(\text{grad}, \text{left\_shape})
        
        \frac{\partial z}{\partial y} = \text{reduce}(-\text{grad}, \text{right\_shape})
    
    The gradient for the first operand is positive, for the second operand is negative.
    Both are reduced to match the original tensor shapes.
    """
    left_shape = tensor._extra.get('left_shape')
    right_shape = tensor._extra.get('right_shape')
    
    left_grad = _reduce_gradient_to_shape(grad, left_shape)
    right_grad = _reduce_gradient_to_shape(-grad, right_shape)
    
    return (left_grad, right_grad)

def mul_broadcast_backward(tensor: Tensor, grad: np.ndarray) -> GradientTuple:
    r"""
    Backward function for broadcasted element-wise multiplication.
    
    For :math:`z = x \odot y` where :math:`x` and :math:`y` have different but broadcastable shapes:
    
    .. math::
        \frac{\partial z}{\partial x} = \text{reduce}(\text{grad} \odot \text{broadcast}(y), \text{left\_shape})
        
        \frac{\partial z}{\partial y} = \text{reduce}(\text{grad} \odot \text{broadcast}(x), \text{right\_shape})
    
    Each tensor's gradient is the gradient times the other tensor's values,
    then reduced to match the original tensor shapes.
    """
    
    left_shape = tensor._extra.get('left_shape')
    right_shape = tensor._extra.get('right_shape')
    x, y = tensor._parents
    
    y_broadcasted = np.broadcast_to(y._data, grad.shape)
    x_broadcasted = np.broadcast_to(x._data, grad.shape)
    
    left_grad = _reduce_gradient_to_shape(grad * y_broadcasted, left_shape)
    right_grad = _reduce_gradient_to_shape(grad * x_broadcasted, right_shape)
    
    return (left_grad, right_grad)

def _reduce_gradient_to_shape(grad: np.ndarray, target_shape: tuple) -> np.ndarray:
    r"""
    Reduce gradient from broadcasted shape back to target shape.
    
    Args:
        grad: Gradient with broadcasted shape
        target_shape: Original tensor shape to reduce back to
        
    Returns:
        Gradient reduced to target shape
    """

    if target_shape == ():
        return np.sum(grad)
    
    result = grad
    
    ndim_added = result.ndim - len(target_shape)
    
    if ndim_added > 0:
        axes_to_sum = tuple(range(ndim_added))
        result = np.sum(result, axis=axes_to_sum)

    for i, (result_dim, target_dim) in enumerate(zip(result.shape, target_shape)):
        if target_dim == 1 and result_dim > 1:
            result = np.sum(result, axis=i, keepdims=True)

    result = result.reshape(target_shape)
    
    return result