"""
Utility functions for django-gradual-throttle.
"""

import importlib
import logging
import time
from typing import Any, Callable, Optional

from django.core.cache import caches
from django.http import HttpRequest

logger = logging.getLogger(__name__)


def default_key_func(request: HttpRequest) -> str:
    """
    Default key function that uses IP address or user ID.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        str: Cache key for the request
    """
    if request.user.is_authenticated:
        return f"throttle:user:{request.user.id}"
    
    # Get IP address from request
    ip = get_client_ip(request)
    return f"throttle:ip:{ip}"


def get_client_ip(request: HttpRequest) -> str:
    """
    Get client IP address from request.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip.strip()
    
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


def import_from_string(import_string: str) -> Any:
    """
    Import a class or function from a string path.
    
    Args:
        import_string: Dot-separated import path
        
    Returns:
        Any: Imported object
        
    Raises:
        ImportError: If import fails
    """
    try:
        module_path, class_name = import_string.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ValueError, ImportError, AttributeError) as e:
        raise ImportError(f"Could not import '{import_string}': {e}")


def get_cache_key_info(cache_key: str, cache_alias: str = 'default') -> tuple:
    """
    Get request count and window start time from cache.
    
    Args:
        cache_key: Cache key for the request
        cache_alias: Django cache alias
        
    Returns:
        tuple: (request_count, window_start_time)
    """
    cache = caches[cache_alias]
    data = cache.get(cache_key)
    
    if data is None:
        return 0, time.time()
    
    return data.get('count', 0), data.get('window_start', time.time())


def update_cache_key_info(cache_key: str, count: int, window_start: float, 
                         window_seconds: int, cache_alias: str = 'default') -> None:
    """
    Update request count and window start time in cache.
    
    Args:
        cache_key: Cache key for the request
        count: New request count
        window_start: Window start time
        window_seconds: Window duration in seconds
        cache_alias: Django cache alias
    """
    cache = caches[cache_alias]
    data = {
        'count': count,
        'window_start': window_start
    }
    
    # Set timeout to window duration + buffer
    timeout = window_seconds + 60
    cache.set(cache_key, data, timeout)


def should_exempt_path(request_path: str, exempt_paths: list) -> bool:
    """
    Check if request path should be exempted from throttling.
    
    Args:
        request_path: Request path
        exempt_paths: List of exempt path prefixes
        
    Returns:
        bool: True if path should be exempted
    """
    return any(request_path.startswith(path) for path in exempt_paths)


def should_exempt_user(user, exempt_users: list) -> bool:
    """
    Check if user should be exempted from throttling.
    
    Args:
        user: Django user object
        exempt_users: List of user attributes to check
        
    Returns:
        bool: True if user should be exempted
    """
    if not user.is_authenticated:
        return False
    
    return any(getattr(user, attr, False) for attr in exempt_users)


def call_hook(hook_func: Optional[Callable], **kwargs) -> None:
    """
    Call hook function if provided.
    
    Args:
        hook_func: Hook function to call
        **kwargs: Arguments to pass to hook function
    """
    if hook_func:
        try:
            hook_func(**kwargs)
        except Exception as e:
            logger.warning(f"Hook function failed: {e}")

def get_throttle_reset_time_left(window_start: float, window_seconds: int) -> float:
    """
    Calculate the time left until the current throttle window resets.
    
    Args:
        window_start: Start time of the throttle window
        window_seconds: Duration of the throttle window in seconds
        
    Returns:
        float: Time left in seconds until window resets
    """
    current_time = time.time()
    window_end = window_start + window_seconds
    return max(0, window_end - current_time)