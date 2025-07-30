"""
Base delay strategy for django-gradual-throttle.
"""

from abc import ABC, abstractmethod


class BaseDelayStrategy(ABC):
    """
    Base class for delay strategies.
    """
    
    def __init__(self, base_delay: float = 0.2, max_delay: float = 5.0):
        """
        Initialize delay strategy.
        
        Args:
            base_delay: Base delay per excess request
            max_delay: Maximum delay allowed
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    @abstractmethod
    def calculate_delay(self, excess_requests: int) -> float:
        """
        Calculate delay based on excess requests.
        
        Args:
            excess_requests: Number of excess requests
            
        Returns:
            float: Delay in seconds
        """
        pass
    
    def _clamp_delay(self, delay: float) -> float:
        """
        Clamp delay to maximum allowed value.
        
        Args:
            delay: Calculated delay
            
        Returns:
            float: Clamped delay
        """
        return min(delay, self.max_delay)
