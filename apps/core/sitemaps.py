"""Mapas del sitio para los buscadores."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.portfolio.models import Project
from apps.services.models import Service


class StaticViewSitemap(Sitemap):
    """Páginas públicas principales."""

    changefreq = "weekly"

    pages = {
        "core:home": 1.0,
        "services:list": 0.9,
        "portfolio:list": 0.8,
        "quotes:create": 0.6,
    }

    def items(self):
        """Devuelve las rutas estáticas como una lista."""

        return list(self.pages.keys())

    def location(self, item):
        """Obtiene la URL de cada página."""

        return reverse(item)

    def priority(self, item):
        """Devuelve la prioridad configurada."""

        return self.pages[item]


class ServiceSitemap(Sitemap):
    """Servicios publicados."""

    changefreq = "monthly"
    priority = 0.8

    def items(self):
        """Devuelve los servicios activos."""

        return (
            Service.objects
            .filter(
                is_active=True,
                category__is_active=True,
            )
            .select_related("category")
        )

    def location(self, obj):
        """Construye la URL pública del servicio."""

        return reverse(
            "services:detail",
            kwargs={
                "slug": obj.slug,
            },
        )

    def lastmod(self, obj):
        """Devuelve la última modificación del servicio."""

        return obj.updated_at


class ProjectSitemap(Sitemap):
    """Proyectos publicados."""

    changefreq = "monthly"
    priority = 0.7

    def items(self):
        """Devuelve los proyectos publicados."""

        return Project.objects.filter(
            is_active=True,
        )

    def location(self, obj):
        """Construye la URL pública del proyecto."""

        return reverse(
            "portfolio:detail",
            kwargs={
                "slug": obj.slug,
            },
        )

    def lastmod(self, obj):
        """Devuelve la última modificación del proyecto."""

        return obj.updated_at


SITEMAPS = {
    "static": StaticViewSitemap,
    "services": ServiceSitemap,
    "projects": ProjectSitemap,
}