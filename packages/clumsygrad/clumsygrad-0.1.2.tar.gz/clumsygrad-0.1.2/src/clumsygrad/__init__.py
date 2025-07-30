"""
A simple automatic differentiation library built on top of NumPy. 
It provides a `Tensor` class with support for building dynamic computation graphs.

For detailed documentation, refer: `https://clumsygrad.readthedocs.io/en/latest/` 
"""

from . import activation, grad, loss, math, optimizer, random, tensor

__version__ = "0.1.2"

__all__ = [
    "tensor",
    "grad",
    "activation",
    "optimizer",
    "loss",
    "random",
    "math",
    "__version__"
]