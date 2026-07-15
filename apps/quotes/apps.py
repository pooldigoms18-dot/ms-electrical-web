"""Configuración de solicitudes de cotización."""

from django.apps import AppConfig


class QuotesConfig(AppConfig):
    """Configuración del módulo comercial de solicitudes."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.quotes"
    verbose_name = "Solicitudes de cotización"