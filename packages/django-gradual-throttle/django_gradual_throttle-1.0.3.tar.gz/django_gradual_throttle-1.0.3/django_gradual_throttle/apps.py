from django.apps import AppConfig


class DjangoGradualThrottleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_gradual_throttle'
    verbose_name = 'Django Gradual Throttle'
