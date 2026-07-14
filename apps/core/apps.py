"""Configuración de la aplicación principal."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuración de las páginas generales del sitio."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Sitio principal"