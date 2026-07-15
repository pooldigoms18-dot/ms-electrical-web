"""Rutas principales del proyecto MS Electrical."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.sitemaps import SITEMAPS


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": SITEMAPS,
        },
        name="sitemap",
    ),
    path(
        "servicios/",
        include("apps.services.urls"),
    ),
    path(
        "proyectos/",
        include("apps.portfolio.urls"),
    ),
    path(
        "cotizacion/",
        include("apps.quotes.urls"),
    ),
    path(
        "",
        include("apps.core.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )