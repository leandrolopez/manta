from abc import ABC, abstractmethod
from typing import Dict, Any, Union, Optional, List

class ValueFunction(ABC):
    """Abstract base class for value functions mapping issue values to utility."""
    
    @abstractmethod
    def __call__(self, value: Any) -> float:
        pass

class DiscreteValueFunction(ValueFunction):
    """Value function for discrete issues using a dictionary lookup."""
    
    def __init__(self, mapping: Dict[Any, float]):
        self.mapping = mapping
        
    def __call__(self, value: Any) -> float:
        return self.mapping.get(value, 0.0)

class LinearAdditiveUtility:
    """
    Linear Additive Utility Function.
    U(omega) = bias + sum(w_i * V_i(omega_i))
    """
    
    def __init__(self, 
                 weights: Dict[str, float], 
                 value_functions: Dict[str, ValueFunction], 
                 bias: float = 0.0):
        self.weights = weights
        self.value_functions = value_functions
        self.bias = bias
        
    def __call__(self, outcome: Dict[str, Any]) -> float:
        """Calculate the utility of an outcome."""
        utility = self.bias
        for issue, value in outcome.items():
            if issue in self.weights and issue in self.value_functions:
                weight = self.weights[issue]
                val_func = self.value_functions[issue]
                utility += weight * val_func(value)
        return utility
