import gc
import os
import random
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.clumsygrad.math import abs, cos, exp, log, mean, sin, sum, tan
from src.clumsygrad.tensor import Tensor, TensorType, TensorUtils


class TestTensorCreation:
    """Test tensor creation and basic properties."""
    
    def test_tensor_init_with_list(self):
        data = [1, 2, 3, 4]
        tensor = Tensor(data)
        assert tensor.shape == (4,)
        assert tensor.data.dtype == np.float32
        assert tensor._tensor_type == TensorType.INPUT
        assert not tensor.requires_grad
    
    def test_tensor_init_with_numpy_array(self):
        data = np.array([[1, 2], [3, 4]])
        tensor = Tensor(data)
        assert tensor.shape == (2, 2)
        np.testing.assert_array_equal(tensor.data, data.astype(np.float32))
    
    def test_tensor_init_parameter_type(self):
        tensor = Tensor([1, 2, 3], tensor_type=TensorType.PARAMETER)
        assert tensor._tensor_type == TensorType.PARAMETER
        assert tensor.requires_grad


class TestTensorProperties:
    """Test tensor properties and setters."""
    
    def test_data_property(self):
        data = [1, 2, 3]
        tensor = Tensor(data)
        np.testing.assert_array_equal(tensor.data, np.array(data, dtype=np.float32))
    
    def test_shape_property(self):
        tensor = Tensor([[1, 2], [3, 4]])
        assert tensor.shape == (2, 2)
    
    def test_grad_property(self):
        tensor = Tensor([1, 2, 3], tensor_type=TensorType.PARAMETER)
        assert tensor.grad is None
        
        grad = np.array([0.1, 0.2, 0.3])
        tensor.grad = grad
        np.testing.assert_array_equal(tensor.grad, grad)


class TestTensorArithmetic:
    """Test tensor arithmetic operations."""
    
    def test_tensor_addition(self):
        a = Tensor([1, 2, 3], tensor_type=TensorType.PARAMETER)
        b = Tensor([4, 5, 6], tensor_type=TensorType.PARAMETER)
        c = a + b
        
        expected = np.array([5, 7, 9], dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
        assert c.requires_grad
        assert len(c._parents) == 2
    
    def test_tensor_addition_shape_mismatch(self):
        a = Tensor([1, 2, 3])
        b = Tensor([[1, 2], [3, 4]])
        
        with pytest.raises(ValueError, match="Shape mismatch for addition"):
            a + b
    
    def test_scalar_addition(self):
        a = Tensor([1, 2, 3], tensor_type=TensorType.PARAMETER)
        c = a + 5
        
        expected = np.array([6, 7, 8], dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
        assert c.requires_grad
        assert len(c._parents) == 1
    
    def test_tensor_subtraction(self):
        a = Tensor([5, 7, 9], tensor_type=TensorType.PARAMETER)
        b = Tensor([1, 2, 3], tensor_type=TensorType.PARAMETER)
        c = a - b
        
        expected = np.array([4, 5, 6], dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
        assert c.requires_grad
    
    def test_scalar_subtraction(self):
        a = Tensor([5, 6, 7], tensor_type=TensorType.PARAMETER)
        c = a - 2
        
        expected = np.array([3, 4, 5], dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
    
    def test_tensor_multiplication(self):
        a = Tensor([2, 3, 4], tensor_type=TensorType.PARAMETER)
        b = Tensor([5, 6, 7], tensor_type=TensorType.PARAMETER)
        c = a * b
        
        expected = np.array([10, 18, 28], dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
        assert c.requires_grad
    
    def test_scalar_multiplication(self):
        a = Tensor([2, 3, 4], tensor_type=TensorType.PARAMETER)
        c = a * 3
        
        expected = np.array([6, 9, 12], dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
    
    def test_tensor_negation(self):
        a = Tensor([1, -2, 3], tensor_type=TensorType.PARAMETER)
        c = -a
        
        expected = np.array([-1, 2, -3], dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
        assert c.requires_grad

class TestMatrixOperations:
    """Test matrix operations."""
    
    def test_matrix_multiplication(self):
        a = Tensor([[1, 2], [3, 4]], tensor_type=TensorType.PARAMETER)
        b = Tensor([[5, 6], [7, 8]], tensor_type=TensorType.PARAMETER)
        c = a @ b
        
        expected = np.array([[19, 22], [43, 50]], dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
        assert c.requires_grad
    
    def test_matrix_multiplication_shape_error(self):
        a = Tensor([[1, 2, 3]], tensor_type=TensorType.PARAMETER)
        b = Tensor([[1, 2], [3, 4]], tensor_type=TensorType.PARAMETER)
        
        with pytest.raises(ValueError, match="Matrix shapes not aligned"):
            a @ b
    
    def test_matrix_multiplication_dimension_error(self):
        a = Tensor([1, 2, 3], tensor_type=TensorType.PARAMETER)
        b = Tensor([4, 5, 6], tensor_type=TensorType.PARAMETER)
        
        with pytest.raises(ValueError, match="Matrix multiplication requires at least 2D tensors"):
            a @ b
    
    def test_transpose(self):
        a = Tensor([[1, 2, 3], [4, 5, 6]], tensor_type=TensorType.PARAMETER)
        b = a.T()
        
        expected = np.array([[1, 4], [2, 5], [3, 6]], dtype=np.float32)
        np.testing.assert_array_equal(b.data, expected)
        assert b.shape == (3, 2)
        assert b.requires_grad
    
    def test_double_transpose_optimization(self):
        a = Tensor([[1, 2], [3, 4]], tensor_type=TensorType.PARAMETER)
        b = a.T().T()
        
        assert b is a


class TestMathOperations:
    """Test mathematical operations."""
    
    def test_power(self):
        a = Tensor([2, 3, 4], tensor_type=TensorType.PARAMETER)
        c = a ** 2
        
        expected = np.array([4, 9, 16], dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
        assert c.requires_grad
    
    def test_sum_operation(self):
        a = Tensor([[1, 2], [3, 4]], tensor_type=TensorType.PARAMETER)
        c = sum(a)
        
        expected = np.array(10, dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
        assert c.requires_grad
    
    def test_sum_with_axis(self):
        a = Tensor([[1, 2], [3, 4]], tensor_type=TensorType.PARAMETER)
        c = sum(a, axis=0)
        
        expected = np.array([4, 6], dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
    
    def test_mean_operation(self):
        a = Tensor([[2, 4], [6, 8]], tensor_type=TensorType.PARAMETER)
        c = mean(a)
        
        expected = np.array(5.0, dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
        assert c.requires_grad
    
    def test_abs_operation(self):
        a = Tensor([-1, 2, -3], tensor_type=TensorType.PARAMETER)
        c = abs(a)
        
        expected = np.array([1, 2, 3], dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
    
    def test_exp_operation(self):
        a = Tensor([0, 1, 2], tensor_type=TensorType.PARAMETER)
        c = exp(a)
        
        expected = np.exp(np.array([0, 1, 2], dtype=np.float32))
        np.testing.assert_array_almost_equal(c.data, expected)
    
    def test_log_operation(self):
        a = Tensor([1, 2, 3], tensor_type=TensorType.PARAMETER)
        c = log(a)
        
        expected = np.log(np.array([1, 2, 3], dtype=np.float32))
        np.testing.assert_array_almost_equal(c.data, expected)
    
    def test_reshape_operation(self):
        a = Tensor([1, 2, 3, 4, 5, 6], tensor_type=TensorType.PARAMETER)
        c = a.reshape((2, 3))
        
        expected = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
        np.testing.assert_array_equal(c.data, expected)
        assert c.shape == (2, 3)
    
    def test_reshape_invalid_size(self):
        a = Tensor([1, 2, 3, 4], tensor_type=TensorType.PARAMETER)
        
        with pytest.raises(ValueError, match="New shape must have the same number of elements"):
            a.reshape((2, 3))

class TestBackpropagation:
    """Test backward propagation."""
    
    def test_backward_scalar_output(self):
        a = Tensor([2, 3], tensor_type=TensorType.PARAMETER)
        b = Tensor([4, 5], tensor_type=TensorType.PARAMETER)
        c = a + b
        d = sum(c)  
        
        d.backward()
        
        np.testing.assert_array_equal(a.grad, np.array([1, 1], dtype=np.float32))
        np.testing.assert_array_equal(b.grad, np.array([1, 1], dtype=np.float32))
    
    def test_backward_with_custom_gradient(self):
        a = Tensor([[1, 2], [3, 4]], tensor_type=TensorType.PARAMETER)
        b = a * 2
        
        custom_grad = np.array([[1, 1], [1, 1]], dtype=np.float32)
        b.backward(custom_grad)
        
        expected_grad = np.array([[2, 2], [2, 2]], dtype=np.float32)
        np.testing.assert_array_equal(a.grad, expected_grad)
    
    def test_backward_no_grad_error(self):
        a = Tensor([1, 2, 3])  # INPUT type, no grad
        
        with pytest.raises(RuntimeError, match="Tensor does not require gradients"):
            a.backward()
    
    def test_backward_non_scalar_error(self):
        a = Tensor([1, 2, 3], tensor_type=TensorType.PARAMETER)
        
        with pytest.raises(RuntimeError, match="Gradient can only be implicitly created for scalar outputs"):
            a.backward()

class TestTensorUtils:
    """Test TensorUtils functionality."""
    
    def test_get_parameters(self):
        a = Tensor([1, 2], tensor_type=TensorType.PARAMETER)
        b = Tensor([3, 4], tensor_type=TensorType.PARAMETER)
        c = Tensor([5, 6])  # INPUT type
        d = a + b + c
        
        params = TensorUtils.get_parameters(d)
        assert len(params) == 2
        assert a in params
        assert b in params
        assert c not in params
    
    def test_count_by_type(self):
        a = Tensor([1, 2], tensor_type=TensorType.PARAMETER)
        b = Tensor([3, 4], tensor_type=TensorType.PARAMETER)
        c = Tensor([5, 6])  # INPUT type
        d = a + b  # INTERMEDIATE type
        e = d + c  # INTERMEDIATE type
        
        counts = TensorUtils.count_by_type(e)
        assert counts[TensorType.PARAMETER] == 2
        assert counts[TensorType.INPUT] == 1
        assert counts[TensorType.INTERMEDIATE] == 2


class TestComplexOperations:
    """Test complex operation chains."""
    testing_values = [0.617, 0.591, 0.505, 0.956, 0.047, 0.128, 0.144, 0.452, 0.53, 0.74]

    def test_complex_expression1(self):
        for value in self.testing_values:
            x = Tensor(random.random(), tensor_type=TensorType.PARAMETER)
            
            y = (x**2 + sin(x))*exp(cos(x))
            deriv_y = (2*x + cos(x))*exp(cos(x)) - (x**2 + sin(x))*exp(cos(x))*sin(x)
            y.backward()
            
            np.testing.assert_array_almost_equal(x.grad, deriv_y.data, decimal=3)
        
    def test_complex_expression2(self):
        for value in self.testing_values:
            x = Tensor(value, tensor_type=TensorType.PARAMETER)
            
            y = log(x**3 + tan(x)) * cos(exp(x))
            deriv_y = ((3 * x**2 + (cos(x)**-1)**2) * cos(exp(x))) * (x**3 + tan(x))**-1 - exp(x) * sin(exp(x)) * log(x**3 + tan(x))
            y.backward()
            
            np.testing.assert_array_almost_equal(x.grad, deriv_y.data, decimal=3)
    
    def test_complex_expression3(self):
        for value in self.testing_values:
            x = Tensor(value, tensor_type=TensorType.PARAMETER)
            
            y = (exp(2 * x) + sin(3 * x)) * (log(x) + cos(x**2))**-1
            deriv_y = ((2 * exp(2 * x) + 3 * cos(3 * x)) * (log(x) + cos(x**2)) - (exp(2 * x) + sin(3 * x)) * (x**-1 - 2 * x * sin(x**2))) * (log(x) + cos(x**2))**-2
            y.backward()
            
            np.testing.assert_array_almost_equal(x.grad, deriv_y.data, decimal=3)
    
    def test_complex_expression4(self):
        for value in self.testing_values:
            x = Tensor(value, tensor_type=TensorType.PARAMETER)
            
            y = (cos(4 * x) + log(x**2 + 1))**3
            deriv_y = 3 * (cos(4 * x) + log(x**2 + 1))**2 * (-4 * sin(4 * x) + (2 * x) * (x**2 + 1)**-1)
            y.backward()
            
            np.testing.assert_array_almost_equal(x.grad, deriv_y.data, decimal=3)
    
    def test_complex_expression5(self):
        for value in self.testing_values:
            x = Tensor(value, tensor_type=TensorType.PARAMETER)
            
            y = x * tan(x**0.5) - exp(sin(5 * x))
            deriv_y = tan(x**0.5) + 0.5 * x**0.5 * (cos(x**0.5))**-2 - 5 * cos(5 * x) * exp(sin(5 * x))
            y.backward()
            
            np.testing.assert_array_almost_equal(x.grad, deriv_y.data, decimal=3)
    
    def test_complex_forward_pass(self):
        # Test: (a * b + c) @ d
        a = Tensor([[1, 2]], tensor_type=TensorType.PARAMETER)
        b = Tensor([[3, 4]], tensor_type=TensorType.PARAMETER)
        c = Tensor([[5, 6]], tensor_type=TensorType.PARAMETER)
        d_val = np.array([[7], [8]], dtype=np.float32)
        d = Tensor(d_val, tensor_type=TensorType.PARAMETER)
        
        result = (a * b + c) @ d
        
        # a * b = [[1*3, 2*4]] = [[3, 8]]
        # a * b + c = [[3+5, 8+6]] = [[8, 14]]
        # (a * b + c) @ d = [[8*7 + 14*8]] = [[56 + 112]] = [[168]]
        expected = np.array([[168]], dtype=np.float32)
        np.testing.assert_array_equal(result.data, expected)

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_matmul_type_error(self):
        a = Tensor([[1, 2]], tensor_type=TensorType.PARAMETER)
        
        with pytest.raises(TypeError, match="Right operand must be a Tensor"):
            a @ 5
    
    def test_gradient_accumulation(self):
        a = Tensor([1.0], tensor_type=TensorType.PARAMETER)
        
        # First computation
        b1 = a * 2
        b1.backward()
        first_grad = a.grad.copy()
        
        # Second computation without zero_grad
        b2 = a * 3
        b2.backward()
        
        # Gradients should accumulate
        expected_grad = first_grad + np.array([3.0], dtype=np.float32)
        np.testing.assert_array_equal(a.grad, expected_grad)

class TestMemoryManagement:
    """Test memory management to prevent leaks."""

    def test_memory_leak_training_loop(self):
        """Check for memory leaks during a simple training loop."""
        
        # Initial memory usage
        gc.collect()
        initial_memory = len(gc.get_objects())
        
        x = Tensor(np.random.rand(10), tensor_type=TensorType.PARAMETER)
        y = Tensor(np.random.rand(10), tensor_type=TensorType.PARAMETER)
        z = Tensor(np.random.rand(10), tensor_type=TensorType.PARAMETER)
        
        for _ in range(100):
            loss = sum(log(x**3 + tan(y)) * cos(exp(z)))
            loss.backward()

        # memory growth from the start to the end of the loop
        memory_growth = len(gc.get_objects()) - initial_memory
        percentage_memory_growth = (memory_growth / initial_memory) * 100

        # This should check if the number of objects remains stable
        # after the training loop, indicating no memory leak.
        # The difference in the number of objects should not exceed 1% of the initial memory, when graph is disposed.
        assert percentage_memory_growth < 1.0, f"Memory leak detected during training loop (growth exceeded 1.0%): {percentage_memory_growth: .3f}%"

if __name__ == "__main__":
    pytest.main([__file__])