"""
Tests for utility functions.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser

from ..utils import (
    default_key_func, get_client_ip, import_from_string,
    should_exempt_path, should_exempt_user
)


class UtilsTest(TestCase):
    """Test cases for utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
    
    def test_default_key_func_authenticated_user(self):
        """Test default key function with authenticated user."""
        request = self.factory.get('/')
        user = User.objects.create_user('test', 'test@test.com', 'pass')
        request.user = user
        
        key = default_key_func(request)
        self.assertEqual(key, f'throttle:user:{user.id}')
    
    def test_default_key_func_anonymous_user(self):
        """Test default key function with anonymous user."""
        request = self.factory.get('/')
        request.user = AnonymousUser()
        
        key = default_key_func(request)
        self.assertTrue(key.startswith('throttle:ip:'))
    
    def test_get_client_ip_remote_addr(self):
        """Test getting client IP from REMOTE_ADDR."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
    
    def test_get_client_ip_x_forwarded_for(self):
        """Test getting client IP from X-Forwarded-For header."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 198.51.100.1'
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '203.0.113.1')
    
    def test_import_from_string_success(self):
        """Test successful import from string."""
        result = import_from_string('django_gradual_throttle.strategies.linear.LinearDelayStrategy')
        from ..strategies.linear import LinearDelayStrategy
        self.assertEqual(result, LinearDelayStrategy)
    
    def test_import_from_string_failure(self):
        """Test import from string failure."""
        with self.assertRaises(ImportError):
            import_from_string('non.existent.module.Class')
    
    def test_should_exempt_path(self):
        """Test path exemption checking."""
        exempt_paths = ['/admin/', '/api/health/']
        
        self.assertTrue(should_exempt_path('/admin/users/', exempt_paths))
        self.assertTrue(should_exempt_path('/api/health/check', exempt_paths))
        self.assertFalse(should_exempt_path('/api/users/', exempt_paths))
        self.assertFalse(should_exempt_path('/', exempt_paths))
    
    def test_should_exempt_user(self):
        """Test user exemption checking."""
        # Anonymous user
        user = AnonymousUser()
        self.assertFalse(should_exempt_user(user, ['is_staff']))
        
        # Regular user
        user = User.objects.create_user('test', 'test@test.com', 'pass')
        self.assertFalse(should_exempt_user(user, ['is_staff']))
        
        # Staff user
        user.is_staff = True
        self.assertTrue(should_exempt_user(user, ['is_staff']))
        
        # Multiple attributes
        user.is_superuser = True
        self.assertTrue(should_exempt_user(user, ['is_staff', 'is_superuser']))
