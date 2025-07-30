# Django Gradual Throttle

A Django middleware library that provides gradual request throttling with configurable delay strategies. Unlike traditional rate limiting that immediately blocks requests, this library applies progressive delays to slow down excessive requests gracefully.

## Features

- **Gradual Throttling**: Apply progressive delays instead of hard blocking
- **Configurable Delay Strategies**: Linear, exponential, or custom delay algorithms
- **Flexible Key Functions**: Throttle by IP address, user ID, or custom keys
- **Django Cache Integration**: Works with any Django-compatible cache backend
- **Comprehensive Configuration**: Extensive settings for fine-tuning behavior
- **Monitoring & Debugging**: Built-in hooks and dry-run mode
- **Headers Support**: Optional response headers for client awareness
- **Path & User Exemptions**: Skip throttling for specific paths or user types

## Installation

```bash
pip install django-gradual-throttle
```

## Quick Start

1. Add the middleware to your Django settings:

```python
MIDDLEWARE = [
    # ... other middleware
    'django_gradual_throttle.middleware.GradualThrottleMiddleware',
    # ... rest of middleware
]
```

2. Basic configuration in `settings.py`:

```python
# Allow 60 requests per minute
DJANGO_GRADUAL_THROTTLE_RATE = 60
DJANGO_GRADUAL_THROTTLE_WINDOW = 60  # seconds

# Apply 0.2s delay per excess request, max 5s
DJANGO_GRADUAL_THROTTLE_BASE_DELAY = 0.2
DJANGO_GRADUAL_THROTTLE_MAX_DELAY = 5.0
```

3. That's it! The middleware will now apply gradual throttling to your Django application.

## Configuration

All settings are optional and have sensible defaults:

### Basic Settings

```python
# Enable/disable throttling (default: True)
DJANGO_GRADUAL_THROTTLE_ENABLED = True

# Requests allowed per time window (default: 60)
DJANGO_GRADUAL_THROTTLE_RATE = 60

# Time window in seconds (default: 60)
DJANGO_GRADUAL_THROTTLE_WINDOW = 60

# Base delay per excess request in seconds (default: 0.2)
DJANGO_GRADUAL_THROTTLE_BASE_DELAY = 0.2

# Maximum delay in seconds (default: 5.0)
DJANGO_GRADUAL_THROTTLE_MAX_DELAY = 5.0
```

### Advanced Settings

```python
# Cache backend to use (default: 'default')
DJANGO_GRADUAL_THROTTLE_CACHE_ALIAS = 'throttle_cache'

# Key function for identifying requests (default: IP/User based)
DJANGO_GRADUAL_THROTTLE_KEY_FUNC = 'myapp.utils.custom_key_func'

# Delay strategy class (default: linear)
DJANGO_GRADUAL_THROTTLE_DELAY_STRATEGY = 'myapp.strategies.CustomDelayStrategy'

# Paths to exempt from throttling
DJANGO_GRADUAL_THROTTLE_EXEMPT_PATHS = ['/admin/', '/health/']

# User attributes that exempt from throttling
DJANGO_GRADUAL_THROTTLE_EXEMPT_USERS = ['is_staff', 'is_superuser']

# Hook function for monitoring/logging
DJANGO_GRADUAL_THROTTLE_HOOK = 'myapp.monitoring.throttle_hook'

# Add throttling headers to responses (default: True)
DJANGO_GRADUAL_THROTTLE_HEADERS_ENABLED = True

# Hard limit - return 429 after this many requests (default: 0 = disabled)
DJANGO_GRADUAL_THROTTLE_HARD_LIMIT = 200

# Dry run mode - log delays instead of applying them (default: False)
DJANGO_GRADUAL_THROTTLE_DRY_RUN = False
```

## Delay Strategies

### Built-in Strategies

#### Linear Delay (Default)
```python
DJANGO_GRADUAL_THROTTLE_DELAY_STRATEGY = 'django_gradual_throttle.strategies.linear.LinearDelayStrategy'
```

Delay increases linearly: `delay = base_delay * excess_requests`

#### Exponential Delay
```python
DJANGO_GRADUAL_THROTTLE_DELAY_STRATEGY = 'django_gradual_throttle.strategies.exponential.ExponentialDelayStrategy'
```

Delay increases exponentially: `delay = base_delay * (multiplier ^ (excess_requests - 1))`

### Custom Delay Strategy

Create your own delay strategy by extending `BaseDelayStrategy`:

```python
# myapp/strategies.py
from django_gradual_throttle.strategies.base import BaseDelayStrategy

class CustomDelayStrategy(BaseDelayStrategy):
    def calculate_delay(self, excess_requests: int) -> float:
        if excess_requests <= 0:
            return 0.0
        
        # Custom logic here
        delay = self.base_delay * (excess_requests ** 1.5)
        return self._clamp_delay(delay)
```

## Custom Key Functions

By default, requests are keyed by IP address for anonymous users and user ID for authenticated users. You can customize this:

```python
# myapp/utils.py
def custom_key_func(request):
    """Custom key function example."""
    if hasattr(request, 'tenant'):
        return f"throttle:tenant:{request.tenant.id}"
    return f"throttle:ip:{get_client_ip(request)}"

# settings.py
DJANGO_GRADUAL_THROTTLE_KEY_FUNC = 'myapp.utils.custom_key_func'
```

## Monitoring & Hooks

Set up monitoring by providing a hook function:

```python
# myapp/monitoring.py
import logging

logger = logging.getLogger(__name__)

def throttle_hook(request, action, **kwargs):
    """Hook function for monitoring throttling events."""
    if action == 'throttled':
        logger.warning(
            f"Request throttled: {kwargs['current_count']} requests, "
            f"{kwargs['delay']:.2f}s delay"
        )
    elif action == 'hard_limit_exceeded':
        logger.error(f"Hard limit exceeded: {kwargs['current_count']} requests")

# settings.py
DJANGO_GRADUAL_THROTTLE_HOOK = 'myapp.monitoring.throttle_hook'
```

## Response Headers

When `DJANGO_GRADUAL_THROTTLE_HEADERS_ENABLED` is `True`, the following headers are added:

- `X-Throttle-Remaining`: Requests remaining in current window
- `X-Throttle-Limit`: Request limit per window
- `X-Throttle-Window`: Time window in seconds
- `X-Throttle-Delay`: Applied delay in seconds (if any)
- `X-Throttle-Excess`: Number of excess requests (if any)

## Cache Backends

The library works with any Django cache backend:

### Redis Example
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'throttle': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

DJANGO_GRADUAL_THROTTLE_CACHE_ALIAS = 'throttle'
```

## Testing

The library includes comprehensive tests. To run them:

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
python -m pytest

# Run with coverage
python -m pytest --cov=django_gradual_throttle --cov-report=html
```

### Dry Run Mode

For testing and development, use dry run mode to log delays without applying them:

```python
DJANGO_GRADUAL_THROTTLE_DRY_RUN = True
```

## Examples

### Basic Rate Limiting
```python
# 100 requests per 5 minutes, 0.1s delay per excess request
DJANGO_GRADUAL_THROTTLE_RATE = 100
DJANGO_GRADUAL_THROTTLE_WINDOW = 300
DJANGO_GRADUAL_THROTTLE_BASE_DELAY = 0.1
DJANGO_GRADUAL_THROTTLE_MAX_DELAY = 10.0
```

### API Throttling with Hard Limit
```python
# 1000 requests per hour, exponential delays, hard limit at 2000
DJANGO_GRADUAL_THROTTLE_RATE = 1000
DJANGO_GRADUAL_THROTTLE_WINDOW = 3600
DJANGO_GRADUAL_THROTTLE_DELAY_STRATEGY = 'django_gradual_throttle.strategies.exponential.ExponentialDelayStrategy'
DJANGO_GRADUAL_THROTTLE_HARD_LIMIT = 2000
```

### Development Setup
```python
# Exempt admin and health checks, enable dry run
DJANGO_GRADUAL_THROTTLE_EXEMPT_PATHS = ['/admin/', '/health/', '/metrics/']
DJANGO_GRADUAL_THROTTLE_EXEMPT_USERS = ['is_staff']
DJANGO_GRADUAL_THROTTLE_DRY_RUN = True  # For development
```

## Performance Considerations

- **Cache Performance**: Use Redis or Memcached for production deployments
- **Key Distribution**: Ensure your key function distributes load evenly
- **Window Size**: Larger windows use more memory but provide smoother throttling
- **Delay Granularity**: Very small delays (< 0.01s) may not be effective

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- Linear and exponential delay strategies
- Comprehensive configuration options
- Django cache integration
- Monitoring hooks and dry run mode
- Full test coverage