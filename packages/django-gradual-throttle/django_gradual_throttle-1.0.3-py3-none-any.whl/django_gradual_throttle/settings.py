"""
Settings management for django-gradual-throttle.
"""

from django.conf import settings
from . import defaults


class ThrottleSettings:
    """
    Settings manager for django-gradual-throttle.
    """
    
    def __init__(self):
        self._settings = {}
        self._load_settings()
    
    def _load_settings(self):
        """Load settings from Django settings with defaults."""
        self._settings = {
            'rate': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_RATE', defaults.DEFAULT_RATE),
            'window': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_WINDOW', defaults.DEFAULT_WINDOW),
            'base_delay': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_BASE_DELAY', defaults.DEFAULT_BASE_DELAY),
            'max_delay': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_MAX_DELAY', defaults.DEFAULT_MAX_DELAY),
            'enabled': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_ENABLED', defaults.DEFAULT_ENABLED),
            'cache_alias': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_CACHE_ALIAS', defaults.DEFAULT_CACHE_ALIAS),
            'key_func': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_KEY_FUNC', defaults.DEFAULT_KEY_FUNC),
            'exempt_paths': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_EXEMPT_PATHS', defaults.DEFAULT_EXEMPT_PATHS),
            'exempt_users': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_EXEMPT_USERS', defaults.DEFAULT_EXEMPT_USERS),
            'delay_strategy': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_DELAY_STRATEGY', defaults.DEFAULT_DELAY_STRATEGY),
            'hook': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_HOOK', defaults.DEFAULT_HOOK),
            'headers_enabled': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_HEADERS_ENABLED', defaults.DEFAULT_HEADERS_ENABLED),
            'hard_limit': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_HARD_LIMIT', defaults.DEFAULT_HARD_LIMIT),
            'dry_run': getattr(settings, 'DJANGO_GRADUAL_THROTTLE_DRY_RUN', defaults.DEFAULT_DRY_RUN),
        }
    
    def __getattr__(self, name):
        """Get setting value."""
        if name in self._settings:
            return self._settings[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def get(self, name, default=None):
        """Get setting value with default."""
        return self._settings.get(name, default)


# Create global settings instance
throttle_settings = ThrottleSettings()