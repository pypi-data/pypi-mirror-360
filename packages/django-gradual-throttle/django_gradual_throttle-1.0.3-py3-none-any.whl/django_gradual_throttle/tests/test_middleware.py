"""
Tests for GradualThrottleMiddleware.
"""

import time
from unittest.mock import Mock, patch

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse
from django.core.cache import cache

from ..middleware import GradualThrottleMiddleware
from ..strategies.linear import LinearDelayStrategy
from ..strategies.exponential import ExponentialDelayStrategy


class GradualThrottleMiddlewareTest(TestCase):
    """Test cases for GradualThrottleMiddleware."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.middleware = GradualThrottleMiddleware()
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_middleware_disabled(self):
        """Test that middleware does nothing when disabled."""
        with override_settings(DJANGO_GRADUAL_THROTTLE_ENABLED=False):
            middleware = GradualThrottleMiddleware()
            request = self.factory.get('/')
            request.user = AnonymousUser()
            
            result = middleware.process_request(request)
            self.assertIsNone(result)
    
    def test_exempt_paths(self):
        """Test that exempt paths are not throttled."""
        with override_settings(DJANGO_GRADUAL_THROTTLE_EXEMPT_PATHS=['/admin/', '/api/health/']):
            middleware = GradualThrottleMiddleware()
            request = self.factory.get('/admin/users/')
            request.user = AnonymousUser()
            
            result = middleware.process_request(request)
            self.assertIsNone(result)
    
    def test_exempt_users(self):
        """Test that exempt users are not throttled."""
        with override_settings(DJANGO_GRADUAL_THROTTLE_EXEMPT_USERS=['is_staff']):
            middleware = GradualThrottleMiddleware()
            request = self.factory.get('/')
            
            # Create staff user
            user = User.objects.create_user('staff', 'staff@test.com', 'pass')
            user.is_staff = True
            request.user = user
            
            result = middleware.process_request(request)
            self.assertIsNone(result)
    
    @patch('time.sleep')
    def test_throttling_with_delay(self, mock_sleep):
        """Test that throttling applies delay when rate is exceeded."""
        with override_settings(
            DJANGO_GRADUAL_THROTTLE_RATE=2,
            DJANGO_GRADUAL_THROTTLE_BASE_DELAY=0.5,
            DJANGO_GRADUAL_THROTTLE_WINDOW=60
        ):
            middleware = GradualThrottleMiddleware()
            
            # Make requests within rate limit
            for i in range(2):
                request = self.factory.get('/')
                request.user = AnonymousUser()
                result = middleware.process_request(request)
                self.assertIsNone(result)
            
            # Third request should be delayed
            request = self.factory.get('/')
            request.user = AnonymousUser()
            result = middleware.process_request(request)
            self.assertIsNone(result)
            
            # Check that sleep was called with expected delay
            mock_sleep.assert_called_once_with(0.5)  # 1 excess * 0.5 base_delay
    
    def test_hard_limit_exceeded(self):
        """Test that hard limit returns 429 response."""
        with override_settings(
            DJANGO_GRADUAL_THROTTLE_RATE=2,
            DJANGO_GRADUAL_THROTTLE_HARD_LIMIT=3,
            DJANGO_GRADUAL_THROTTLE_WINDOW=60
        ):
            middleware = GradualThrottleMiddleware()
            
            # Make requests up to hard limit
            for i in range(3):
                request = self.factory.get('/')
                request.user = AnonymousUser()
                result = middleware.process_request(request)
                self.assertIsNone(result)
            
            # Fourth request should return 429
            request = self.factory.get('/')
            request.user = AnonymousUser()
            result = middleware.process_request(request)
            
            self.assertIsNotNone(result)
            self.assertEqual(result.status_code, 429)
    
    @patch('time.sleep')
    def test_dry_run_mode(self, mock_sleep):
        """Test that dry run mode logs but doesn't sleep."""
        with override_settings(
            DJANGO_GRADUAL_THROTTLE_RATE=1,
            DJANGO_GRADUAL_THROTTLE_DRY_RUN=True,
            DJANGO_GRADUAL_THROTTLE_WINDOW=60
        ):
            middleware = GradualThrottleMiddleware()
            
            # Make first request (within limit)
            request = self.factory.get('/')
            request.user = AnonymousUser()
            result = middleware.process_request(request)
            self.assertIsNone(result)
            
            # Second request should trigger dry run
            request = self.factory.get('/')
            request.user = AnonymousUser()
            result = middleware.process_request(request)
            self.assertIsNone(result)
            
            # Sleep should not be called in dry run mode
            mock_sleep.assert_not_called()
    
    def test_headers_added_to_response(self):
        """Test that throttling headers are added to response."""
        with override_settings(
            DJANGO_GRADUAL_THROTTLE_RATE=5,
            DJANGO_GRADUAL_THROTTLE_HEADERS_ENABLED=True
        ):
            middleware = GradualThrottleMiddleware()
            request = self.factory.get('/')
            request.user = AnonymousUser()
            
            # Process request
            middleware.process_request(request)
            
            # Process response
            response = HttpResponse()
            response = middleware.process_response(request, response)
            
            # Check headers
            self.assertIn('X-Throttle-Remaining', response)
            self.assertIn('X-Throttle-Limit', response)
            self.assertIn('X-Throttle-Window', response)
            self.assertEqual(response['X-Throttle-Remaining'], '4')  # 5 - 1
            self.assertEqual(response['X-Throttle-Limit'], '5')


class DelayStrategyTest(TestCase):
    """Test cases for delay strategies."""
    
    def test_linear_delay_strategy(self):
        """Test linear delay strategy calculations."""
        strategy = LinearDelayStrategy(base_delay=0.2, max_delay=2.0)
        
        # No excess requests
        self.assertEqual(strategy.calculate_delay(0), 0.0)
        
        # Linear scaling
        self.assertEqual(strategy.calculate_delay(1), 0.2)
        self.assertEqual(strategy.calculate_delay(2), 0.4)
        self.assertEqual(strategy.calculate_delay(5), 1.0)
        
        # Max delay clamping
        self.assertEqual(strategy.calculate_delay(20), 2.0)
    
    def test_exponential_delay_strategy(self):
        """Test exponential delay strategy calculations."""
        strategy = ExponentialDelayStrategy(base_delay=0.1, max_delay=1.0, multiplier=2.0)
        
        # No excess requests
        self.assertEqual(strategy.calculate_delay(0), 0.0)
        
        # Exponential scaling
        self.assertEqual(strategy.calculate_delay(1), 0.1)  # 0.1 * 2^0
        self.assertEqual(strategy.calculate_delay(2), 0.2)  # 0.1 * 2^1
        self.assertEqual(strategy.calculate_delay(3), 0.4)  # 0.1 * 2^2
        
        # Max delay clamping
        self.assertEqual(strategy.calculate_delay(10), 1.0)
