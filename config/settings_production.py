"""Configuración de producción de MS Electrical."""

import os

from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F403, F401


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


DEBUG = False


# ============================================================
# Seguridad básica de configuración
# ============================================================

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "",
).strip()

if not SECRET_KEY:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY es obligatorio en producción."
    )


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
# Proxy HTTPS
# ============================================================

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"


# ============================================================
# Carga de archivos
# ============================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = (
    1 * 1024 * 1024
)

DATA_UPLOAD_MAX_MEMORY_SIZE = (
    5 * 1024 * 1024
)