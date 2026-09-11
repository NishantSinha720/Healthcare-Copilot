import os

from .base import *


DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]


# ---------------------------------------------------------------------------
# Hosts
# ---------------------------------------------------------------------------

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1",
    ).split(",")
    if host.strip()
]


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get(
            "DB_NAME",
            "healthcare_copilot",
        ),
        "USER": os.environ.get(
            "DB_USER",
            "root",
        ),
        "PASSWORD": os.environ.get(
            "DB_PASSWORD",
            "",
        ),
        "HOST": os.environ.get(
            "DB_HOST",
            "127.0.0.1",
        ),
        "PORT": os.environ.get(
            "DB_PORT",
            "3306",
        ),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    },
}


# ---------------------------------------------------------------------------
# Redis
# ---------------------------------------------------------------------------

REDIS_HOST = os.environ.get(
    "REDIS_HOST",
    "127.0.0.1",
)

REDIS_PORT = os.environ.get(
    "REDIS_PORT",
    "6379",
)


# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------

CELERY_BROKER_URL = os.environ.get(
    "CELERY_BROKER_URL",
    f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
)

CELERY_RESULT_BACKEND = os.environ.get(
    "CELERY_RESULT_BACKEND",
    f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
)


# ---------------------------------------------------------------------------
# Django Channels
# ---------------------------------------------------------------------------

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address": f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
                    "socket_timeout": None,
                    "socket_connect_timeout": 5,
                }
            ],
        },
    },
}


# ---------------------------------------------------------------------------
# Static / Media
# ---------------------------------------------------------------------------

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

SECURE_SSL_REDIRECT = (
    os.environ.get(
        "SECURE_SSL_REDIRECT",
        "True",
    ).lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)

SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT

CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT


if SECURE_SSL_REDIRECT:
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )
else:
    SECURE_PROXY_SSL_HEADER = None


SECURE_HSTS_SECONDS = int(
    os.environ.get(
        "SECURE_HSTS_SECONDS",
        "31536000" if SECURE_SSL_REDIRECT else "0",
    )
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    SECURE_HSTS_SECONDS > 0
)

SECURE_HSTS_PRELOAD = (
    SECURE_HSTS_SECONDS > 0
)

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = (
    "strict-origin-when-cross-origin"
)

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"


# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "http://localhost,http://127.0.0.1",
    ).split(",")
    if origin.strip()
]


# ---------------------------------------------------------------------------
# Upload limits
# ---------------------------------------------------------------------------

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024