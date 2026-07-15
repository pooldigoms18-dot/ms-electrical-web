"""Rutas principales del proyecto MS Electrical."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
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
        "",
        include("apps.core.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )