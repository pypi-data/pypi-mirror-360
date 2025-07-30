"""
Linear delay strategy for django-gradual-throttle.
"""

from .base import BaseDelayStrategy


class LinearDelayStrategy(BaseDelayStrategy):
    """
    Linear delay strategy that increases delay linearly with excess requests.
    """
    
    def calculate_delay(self, excess_requests: int) -> float:
        """
        Calculate linear delay.
        
        Args:
            excess_requests: Number of excess requests
            
        Returns:
            float: Delay in seconds
        """
        if excess_requests <= 0:
            return 0.0
        
        delay = self.base_delay * excess_requests
        return self._clamp_delay(delay)
