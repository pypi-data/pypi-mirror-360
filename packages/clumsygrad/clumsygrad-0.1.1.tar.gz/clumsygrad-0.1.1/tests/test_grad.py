import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import src.clumsygrad.grad as grad_module
from src.clumsygrad.math import abs, cos, exp, log, mean, sin, sqrt, sum, tan
from src.clumsygrad.tensor import Tensor, TensorType


class TestElementaryGradFunctions:
    """Tests for backward functions of elementary tensor operations."""

    def test_transpose_backward(self):
        x_data = np.array([[1., 2., 3.], [4., 5., 6.]])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = x.T() # Forward pass
        incoming_grad = np.ones_like(child_tensor.data)
        
        grad_x_tuple = grad_module.transpose_backward(child_tensor, incoming_grad)
        
        expected_grad_x = incoming_grad.T
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_add_backward(self):
        x_data = np.array([1., 2., 3.])
        y_data = np.array([4., 5., 6.])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        y = Tensor(y_data, tensor_type=TensorType.PARAMETER)
        child_tensor = x + y # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])
        
        grad_x_tuple = grad_module.add_backward(child_tensor, incoming_grad)
        
        np.testing.assert_array_almost_equal(grad_x_tuple[0], incoming_grad)
        np.testing.assert_array_almost_equal(grad_x_tuple[1], incoming_grad)

    def test_add_scalar_backward(self):
        x_data = np.array([1., 2., 3.])
        scalar_val = 5.0
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = x + scalar_val # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])

        grad_x_tuple = grad_module.add_scalar_backward(child_tensor, incoming_grad)
        np.testing.assert_array_almost_equal(grad_x_tuple[0], incoming_grad)

    def test_sub_backward(self):
        x_data = np.array([1., 2., 3.])
        y_data = np.array([4., 5., 6.])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        y = Tensor(y_data, tensor_type=TensorType.PARAMETER)
        child_tensor = x - y # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])
        
        grad_x_tuple = grad_module.sub_backward(child_tensor, incoming_grad)
        
        np.testing.assert_array_almost_equal(grad_x_tuple[0], incoming_grad)
        np.testing.assert_array_almost_equal(grad_x_tuple[1], -incoming_grad)

    def test_sub_scalar_backward(self):
        x_data = np.array([1., 2., 3.])
        scalar_val = 5.0
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = x - scalar_val # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])

        grad_x_tuple = grad_module.sub_scalar_backward(child_tensor, incoming_grad)
        np.testing.assert_array_almost_equal(grad_x_tuple[0], incoming_grad)

    def test_mul_backward(self):
        x_data = np.array([1., 2., 3.])
        y_data = np.array([4., 5., 6.])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        y = Tensor(y_data, tensor_type=TensorType.PARAMETER)
        child_tensor = x * y # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])
        
        grad_x_tuple = grad_module.mul_backward(child_tensor, incoming_grad)
        
        expected_grad_x = incoming_grad * y_data
        expected_grad_y = incoming_grad * x_data
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)
        np.testing.assert_array_almost_equal(grad_x_tuple[1], expected_grad_y)

    def test_mul_scalar_backward(self):
        x_data = np.array([1., 2., 3.])
        scalar_val = 5.0
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = x * scalar_val # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])

        grad_x_tuple = grad_module.mul_scalar_backward(child_tensor, incoming_grad)
        expected_grad_x = incoming_grad * scalar_val
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_matmul_backward(self):
        x_data = np.array([[1., 2.], [3., 4.]])
        y_data = np.array([[5., 6.], [7., 8.]])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        y = Tensor(y_data, tensor_type=TensorType.PARAMETER)
        child_tensor = x @ y # Forward pass
        incoming_grad = np.array([[0.1, 0.2], [0.3, 0.4]])
        
        grad_x_tuple = grad_module.matmul_backward(child_tensor, incoming_grad)
        
        expected_grad_x = incoming_grad @ y_data.T
        expected_grad_y = x_data.T @ incoming_grad
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)
        np.testing.assert_array_almost_equal(grad_x_tuple[1], expected_grad_y)

    def test_power_backward(self):
        x_data = np.array([1., 2., 3.])
        power_val = 3.0
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = x ** power_val # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])
        
        grad_x_tuple = grad_module.power_backward(child_tensor, incoming_grad)
        
        expected_grad_x = incoming_grad * (power_val * (x_data ** (power_val - 1)))
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_negate_backward(self):
        x_data = np.array([1., -2., 3.])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = -x # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])
        
        grad_x_tuple = grad_module.negate_backward(child_tensor, incoming_grad)
        
        expected_grad_x = -incoming_grad
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_abs_backward(self):
        x_data = np.array([-1., 0., 3.])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = abs(x) # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])
        
        grad_x_tuple = grad_module.abs_backward(child_tensor, incoming_grad)
        
        expected_grad_x = incoming_grad * np.sign(x_data)
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_reshape_backward(self):
        x_data = np.array([[1., 2., 3.], [4., 5., 6.]])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        new_shape = (3, 2)
        child_tensor = x.reshape(new_shape) # Forward pass
        incoming_grad = np.ones(new_shape)
        
        grad_x_tuple = grad_module.reshape_backward(child_tensor, incoming_grad)
        
        expected_grad_x = incoming_grad.reshape(x_data.shape)
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)


class TestReductionGradFunctions:
    """Tests for backward functions of reduction operations."""

    def test_sum_backward_no_axis(self):
        x_data = np.array([[1., 2.], [3., 4.]])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = sum(x) # Forward pass
        incoming_grad = np.array(0.5) # Scalar gradient
        
        grad_x_tuple = grad_module.sum_backward(child_tensor, incoming_grad)
        
        expected_grad_x = np.full_like(x_data, 0.5)
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_sum_backward_with_axis_keepdims_false(self):
        x_data = np.array([[1., 2., 3.], [4., 5., 6.]])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = sum(x, axis=0, keepdims=False) # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])
        
        grad_x_tuple = grad_module.sum_backward(child_tensor, incoming_grad)
        
        # Expected: incoming_grad broadcasted
        # incoming_grad is (3,), x_data is (2,3)
        # expanded_grad becomes (1,3) then broadcast to (2,3)
        expected_grad_x = np.array([[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]])
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_sum_backward_with_axis_keepdims_true(self):
        x_data = np.array([[1., 2., 3.], [4., 5., 6.]])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = sum(x, axis=1, keepdims=True) # Forward pass (shape (2,1))
        incoming_grad = np.array([[0.1], [0.2]])
        
        grad_x_tuple = grad_module.sum_backward(child_tensor, incoming_grad)
        
        expected_grad_x = np.array([[0.1, 0.1, 0.1], [0.2, 0.2, 0.2]])
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_mean_backward_no_axis(self):
        x_data = np.array([[1., 2.], [3., 4.]]) # size = 4
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = mean(x) # Forward pass
        incoming_grad = np.array(0.5) # Scalar gradient
        
        grad_x_tuple = grad_module.mean_backward(child_tensor, incoming_grad)
        
        n = x_data.size
        expected_grad_x = np.full_like(x_data, 0.5 / n)
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_mean_backward_with_axis_keepdims_false(self):
        x_data = np.array([[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]]) # axis=0, n=3 for each column
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = mean(x, axis=0, keepdims=False) # Forward pass, shape (3,)
        incoming_grad = np.array([0.1, 0.2, 0.3])
        
        grad_x_tuple = grad_module.mean_backward(child_tensor, incoming_grad)
        
        n = x_data.shape[0] # Number of elements averaged over (axis 0)
        expected_grad_x = np.array([
            [0.1/n, 0.2/n, 0.3/n],
            [0.1/n, 0.2/n, 0.3/n],
            [0.1/n, 0.2/n, 0.3/n]
        ])
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)


class TestMathOpGradFunctions:
    """Tests for backward functions of standard mathematical operations."""

    def test_exp_backward(self):
        x_data = np.array([0., 1., -1.])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = exp(x) # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])
        
        grad_x_tuple = grad_module.exp_backward(child_tensor, incoming_grad)
        
        expected_grad_x = incoming_grad * child_tensor.data # child_tensor.data is exp(x_data)
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_log_backward(self):
        x_data = np.array([1., 2., 3.]) # log requires positive values
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = log(x) # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])
        
        grad_x_tuple = grad_module.log_backward(child_tensor, incoming_grad)
        
        expected_grad_x = incoming_grad / x_data
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_sqrt_backward(self):
        x_data = np.array([1., 4., 9.])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = sqrt(x) # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])

        grad_x_tuple = grad_module.sqrt_backward(child_tensor, incoming_grad)
        expected_grad_x = incoming_grad / (2 * np.sqrt(x_data))
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)
        
    def test_sin_backward(self):
        x_data = np.array([0., np.pi/2, np.pi])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = sin(x) # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])

        grad_x_tuple = grad_module.sin_backward(child_tensor, incoming_grad)
        expected_grad_x = incoming_grad * np.cos(x_data)
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_cos_backward(self):
        x_data = np.array([0., np.pi/2, np.pi])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = cos(x) # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])

        grad_x_tuple = grad_module.cos_backward(child_tensor, incoming_grad)
        expected_grad_x = incoming_grad * -np.sin(x_data)
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

    def test_tan_backward(self):
        x_data = np.array([0., np.pi/4, -np.pi/4])
        x = Tensor(x_data, tensor_type=TensorType.PARAMETER)
        child_tensor = tan(x) # Forward pass
        incoming_grad = np.array([0.1, 0.2, 0.3])

        grad_x_tuple = grad_module.tan_backward(child_tensor, incoming_grad)
        expected_grad_x = incoming_grad * (1 / np.cos(x_data)**2)
        np.testing.assert_array_almost_equal(grad_x_tuple[0], expected_grad_x)

if __name__ == "__main__":
    pytest.main([__file__])
