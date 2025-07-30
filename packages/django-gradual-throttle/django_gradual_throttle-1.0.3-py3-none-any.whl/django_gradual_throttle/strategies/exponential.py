"""
Exponential delay strategy for django-gradual-throttle.
"""

import math
from .base import BaseDelayStrategy


class ExponentialDelayStrategy(BaseDelayStrategy):
    """
    Exponential delay strategy that increases delay exponentially with excess requests.
    """
    
    def __init__(self, base_delay: float = 0.2, max_delay: float = 5.0, 
                 multiplier: float = 2.0):
        """
        Initialize exponential delay strategy.
        
        Args:
            base_delay: Base delay per excess request
            max_delay: Maximum delay allowed
            multiplier: Exponential multiplier
        """
        super().__init__(base_delay, max_delay)
        self.multiplier = multiplier
    
    def calculate_delay(self, excess_requests: int) -> float:
        """
        Calculate exponential delay.
        
        Args:
            excess_requests: Number of excess requests
            
        Returns:
            float: Delay in seconds
        """
        if excess_requests <= 0:
            return 0.0
        
        # Calculate exponential delay: base_delay * (multiplier ^ (excess_requests - 1))
        delay = self.base_delay * (self.multiplier ** (excess_requests - 1))
        return self._clamp_delay(delay)
