"""Configuración de la aplicación de portafolio."""

from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    """Configuración del portafolio de proyectos."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.portfolio"
    verbose_name = "Portafolio de proyectos"