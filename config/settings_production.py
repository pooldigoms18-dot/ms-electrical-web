"""Configuración de producción de MS Electrical."""

import os

from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F401, F403


def get_csv_environment(name):
    """Convierte una variable separada por comas en una lista."""

    return [
        value.strip()
        for value in os.getenv(
            name,
            "",
        ).split(",")
        if value.strip()
    ]


def get_bool_environment(
    name,
    default=False,
):
    """Convierte una variable de entorno en booleano."""

    value = os.getenv(
        name,
        str(default),
    ).strip().lower()

    return value in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_int_environment(
    name,
    default,
):
    """Obtiene un entero desde una variable de entorno."""

    value = os.getenv(
        name,
        str(default),
    ).strip()

    try:
        return int(
            value,
        )

    except ValueError as exc:
        raise ImproperlyConfigured(
            f"{name} debe contener un número entero."
        ) from exc


# ============================================================
# Entorno
# ============================================================

DEBUG = False


# ============================================================
# Clave privada
# ============================================================

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "",
).strip()

if not SECRET_KEY:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY es obligatorio en producción."
    )


# ============================================================
# Hosts y dominio
# ============================================================

ALLOWED_HOSTS = get_csv_environment(
    "DJANGO_ALLOWED_HOSTS",
)

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS es obligatorio en producción."
    )


CSRF_TRUSTED_ORIGINS = get_csv_environment(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
)


SITE_URL = os.getenv(
    "DJANGO_SITE_URL",
    "",
).strip().rstrip("/")

if not SITE_URL:
    raise ImproperlyConfigured(
        "DJANGO_SITE_URL es obligatorio en producción."
    )


# ============================================================
# Archivos estáticos
# ============================================================

STATIC_ROOT = (
    BASE_DIR  # noqa: F405
    / "staticfiles"
)


STORAGES = {
    "default": {
        "BACKEND": (
            "django.core.files.storage."
            "FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage."
            "ManifestStaticFilesStorage"
        ),
    },
}


# ============================================================
# HTTPS y proxy inverso
# ============================================================

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True


# ============================================================
# Seguridad de cookies
# ============================================================

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SAMESITE = "Lax"


# ============================================================
# Cabeceras de seguridad
# ============================================================

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = (
    "strict-origin-when-cross-origin"
)

SECURE_CROSS_ORIGIN_OPENER_POLICY = (
    "same-origin"
)

X_FRAME_OPTIONS = "DENY"


# ============================================================
# HTTP Strict Transport Security
# ============================================================

SECURE_HSTS_SECONDS = get_int_environment(
    "DJANGO_SECURE_HSTS_SECONDS",
    3600,
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    get_bool_environment(
        "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
        False,
    )
)

SECURE_HSTS_PRELOAD = get_bool_environment(
    "DJANGO_SECURE_HSTS_PRELOAD",
    False,
)


# ============================================================
# Límites de solicitudes
# ============================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = (
    1 * 1024 * 1024
)

DATA_UPLOAD_MAX_MEMORY_SIZE = (
    5 * 1024 * 1024
)

DATA_UPLOAD_MAX_NUMBER_FIELDS = 500

DATA_UPLOAD_MAX_NUMBER_FILES = 10


# ============================================================
# Logging
# ============================================================

LOG_LEVEL = os.getenv(
    "DJANGO_LOG_LEVEL",
    "INFO",
).strip().upper()

if LOG_LEVEL not in {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}:
    LOG_LEVEL = "INFO"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "production": {
            "format": (
                "{asctime} "
                "{levelname} "
                "{name}: "
                "{message}"
            ),
            "style": "{",
        },
    },

    "handlers": {
        "console": {
            "class": (
                "logging.StreamHandler"
            ),
            "formatter": "production",
        },
    },

    "loggers": {
        "django": {
            "handlers": [
                "console",
            ],
            "level": "WARNING",
            "propagate": False,
        },

        "django.request": {
            "handlers": [
                "console",
            ],
            "level": "ERROR",
            "propagate": False,
        },

        "django.security": {
            "handlers": [
                "console",
            ],
            "level": "WARNING",
            "propagate": False,
        },

        "apps": {
            "handlers": [
                "console",
            ],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}