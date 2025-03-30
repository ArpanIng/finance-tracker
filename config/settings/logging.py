import os

from config.env import BASE_DIR

DJANGO_APPS_NAMES = ["tracker", "users"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime}:{levelname} - {name} {module}.py (line {lineno:d}). {message}",
            "style": "{",
        },
        "simple": {
            "format": "{asctime}:{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "django-log.log"),
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "level": "INFO",
            "handlers": ["console"],
        },
        "users": {
            "level": "INFO",
            "handlers": ["file"],
        },
        "config": {
            "level": "INFO",
            "handlers": ["file"],
        },
        "tracker": {
            "level": "INFO",
            "handlers": ["file"],
        },
    },
}
