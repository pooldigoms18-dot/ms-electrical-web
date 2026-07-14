"""Configuración de la aplicación de servicios."""

from django.apps import AppConfig


class ServicesConfig(AppConfig):
    """Configuración del catálogo comercial."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.services"
    verbose_name = "Catálogo de servicios"