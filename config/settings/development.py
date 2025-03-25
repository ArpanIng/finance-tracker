from .base import *

INSTALLED_APPS += [
    "debug_toolbar",
    "django_extensions",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Email backend configuration
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# django debug toolbar configuration
INTERNAL_IPS = [
    "127.0.0.1",
]

# django extensions configuration
SHELL_PLUS_PRINT_SQL = True
