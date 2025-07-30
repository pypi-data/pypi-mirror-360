"""
Tests for settings management.
"""

from django.test import TestCase, override_settings

from ..settings import ThrottleSettings


class ThrottleSettingsTest(TestCase):
    """Test cases for ThrottleSettings."""
    
    def test_default_settings(self):
        """Test that default settings are loaded correctly."""
        settings = ThrottleSettings()
        
        self.assertEqual(settings.rate, 60)
        self.assertEqual(settings.window, 60)
        self.assertEqual(settings.base_delay, 0.2)
        self.assertEqual(settings.max_delay, 5.0)
        self.assertTrue(settings.enabled)
        self.assertEqual(settings.cache_alias, 'default')
    
    @override_settings(
        DJANGO_GRADUAL_THROTTLE_RATE=100,
        DJANGO_GRADUAL_THROTTLE_WINDOW=120,
        DJANGO_GRADUAL_THROTTLE_ENABLED=False
    )
    def test_custom_settings(self):
        """Test that custom settings override defaults."""
        settings = ThrottleSettings()
        
        self.assertEqual(settings.rate, 100)
        self.assertEqual(settings.window, 120)
        self.assertFalse(settings.enabled)
    
    def test_get_method(self):
        """Test the get method with defaults."""
        settings = ThrottleSettings()
        
        self.assertEqual(settings.get('rate'), 60)
        self.assertEqual(settings.get('nonexistent', 'default'), 'default')
        self.assertIsNone(settings.get('nonexistent'))

