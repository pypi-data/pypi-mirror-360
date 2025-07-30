"""
Django middleware for gradual throttling.
"""

import logging
import time
from typing import Callable, Optional

from django.core.cache import caches
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from .settings import throttle_settings
from .utils import (
    import_from_string, get_cache_key_info, update_cache_key_info,
    should_exempt_path, should_exempt_user, call_hook, get_throttle_reset_time_left
)

logger = logging.getLogger(__name__)


class GradualThrottleMiddleware(MiddlewareMixin):
    """
    Django middleware that applies gradual throttling to requests.
    """
    
    def __init__(self, get_response: Optional[Callable] = None):
        """
        Initialize middleware.
        
        Args:
            get_response: Django get_response callable
        """
        super().__init__(get_response)
        self.settings = throttle_settings
        self._key_func = None
        self._delay_strategy = None
        self._hook_func = None
        self._load_components()
    
    def _load_components(self):
        """Load key function, delay strategy, and hook function."""
        # Load key function
        try:
            self._key_func = import_from_string(self.settings.key_func)
        except ImportError as e:
            logger.error(f"Failed to load key function: {e}")
            raise
        
        # Load delay strategy
        try:
            strategy_class = import_from_string(self.settings.delay_strategy)
            self._delay_strategy = strategy_class(
                base_delay=self.settings.base_delay,
                max_delay=self.settings.max_delay
            )
        except ImportError as e:
            logger.error(f"Failed to load delay strategy: {e}")
            raise
        
        # Load hook function (optional)
        if self.settings.hook:
            try:
                self._hook_func = import_from_string(self.settings.hook)
            except ImportError as e:
                logger.warning(f"Failed to load hook function: {e}")
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Process incoming request and apply throttling if needed.
        
        Args:
            request: Django HTTP request
            
        Returns:
            HttpResponse: HTTP 429 response if hard limit exceeded, None otherwise
        """
        # Skip if throttling is disabled
        if not self.settings.enabled:
            return None
        
        # Check if path should be exempted
        if should_exempt_path(request.path, self.settings.exempt_paths):
            return None
        
        # Check if user should be exempted
        if should_exempt_user(request.user, self.settings.exempt_users):
            return None
        
        # Get cache key for this request
        cache_key = self._key_func(request)
        
        # Get current request count and window info
        current_count, window_start = get_cache_key_info(
            cache_key, self.settings.cache_alias
        )
        
        current_time = time.time()
        
        # Check if we need to reset the window
        if current_time - window_start >= self.settings.window:
            current_count = 0
            window_start = current_time
        
        # Increment request count
        current_count += 1
        
        # Update cache
        update_cache_key_info(
            cache_key, current_count, window_start, 
            self.settings.window, self.settings.cache_alias
        )
        
        # Calculate excess requests
        excess_requests = max(0, current_count - self.settings.rate)
        
        # Check hard limit
        if (self.settings.hard_limit > 0 and 
            current_count > self.settings.hard_limit):
            
            # Call hook if provided
            call_hook(self._hook_func, 
                     request=request, 
                     action='hard_limit_exceeded',
                     current_count=current_count,
                     excess_requests=excess_requests)
            
            response = HttpResponse(
                'Too Many Requests - Hard limit exceeded',
                status=429,
                content_type='text/plain'
            )
            
            if self.settings.headers_enabled:
                self._add_headers(response, current_count, excess_requests, 0, window_start)
            
            return response
        
        # Calculate delay
        delay = self._delay_strategy.calculate_delay(excess_requests)
        
        # Apply delay or log in dry run mode
        if delay > 0:
            if self.settings.dry_run:
                logger.info(f"DRY RUN: Would delay request by {delay:.2f}s "
                           f"(excess: {excess_requests}, key: {cache_key})")
            else:
                logger.debug(f"Delaying request by {delay:.2f}s "
                            f"(excess: {excess_requests}, key: {cache_key})")
                time.sleep(delay)
            
            # Call hook if provided
            call_hook(self._hook_func,
                     request=request,
                     action='throttled',
                     current_count=current_count,
                     excess_requests=excess_requests,
                     delay=delay,
                     dry_run=self.settings.dry_run)
        
        # Store throttling info in request for use in response processing
        request._throttle_info = {
            'current_count': current_count,
            'excess_requests': excess_requests,
            'delay': delay,
            'window_start': window_start
        }
        
        return None
    
    def process_response(self, request: HttpRequest, 
                        response: HttpResponse) -> HttpResponse:
        """
        Process response and add throttling headers if enabled.
        
        Args:
            request: Django HTTP request
            response: Django HTTP response
            
        Returns:
            HttpResponse: Response with throttling headers
        """
        if (self.settings.enabled and 
            self.settings.headers_enabled and 
            hasattr(request, '_throttle_info')):
            
            info = request._throttle_info
            self._add_headers(
                response, 
                info['current_count'], 
                info['excess_requests'], 
                info['delay'],
                info['window_start']
            )
        
        return response
    
    def _add_headers(self, response: HttpResponse, current_count: int, 
                    excess_requests: int, delay: float, window_start: float) -> None:
        """
        Add throttling headers to response.
        
        Args:
            response: Django HTTP response
            current_count: Current request count
            excess_requests: Number of excess requests
            delay: Applied delay in seconds
            window_start: Window start time
        """
        remaining = max(0, self.settings.rate - current_count)
        
        response['X-Throttle-Remaining'] = str(remaining)
        response['X-Throttle-Limit'] = str(self.settings.rate)
        response['X-Throttle-Window'] = str(self.settings.window)
        
        if delay > 0:
            response['X-Throttle-Delay'] = f"{delay:.2f}"
        
        if excess_requests > 0:
            response['X-Throttle-Excess'] = str(excess_requests)
            
        # Add Retry-After header with time left until window resets
        if excess_requests > 0:
            retry_after = get_throttle_reset_time_left(window_start, self.settings.window)
            response['Retry-After'] = str(int(retry_after))