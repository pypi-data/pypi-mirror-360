"""
Default configuration values for django-gradual-throttle.
"""

# Default throttle rate (requests per window)
DEFAULT_RATE = 60

# Default time window in seconds
DEFAULT_WINDOW = 60

# Default base delay per excess request in seconds
DEFAULT_BASE_DELAY = 0.2

# Default maximum delay in seconds
DEFAULT_MAX_DELAY = 5.0

# Default enabled state
DEFAULT_ENABLED = True

# Default cache alias
DEFAULT_CACHE_ALIAS = 'default'

# Default key function
DEFAULT_KEY_FUNC = 'django_gradual_throttle.utils.default_key_func'

# Default exempt paths
DEFAULT_EXEMPT_PATHS = []

# Default exempt users
DEFAULT_EXEMPT_USERS = []

# Default delay strategy
DEFAULT_DELAY_STRATEGY = 'django_gradual_throttle.strategies.linear.LinearDelayStrategy'

# Default hook function
DEFAULT_HOOK = None

# Default headers enabled
DEFAULT_HEADERS_ENABLED = True

# Default hard limit (0 means no hard limit)
DEFAULT_HARD_LIMIT = 0

# Default dry run mode
DEFAULT_DRY_RUN = False
