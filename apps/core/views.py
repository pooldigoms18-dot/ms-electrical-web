"""Vistas de las páginas generales de MS Electrical."""

from django.shortcuts import render

from apps.portfolio.models import Project
from apps.services.models import Service


def home(request):
    """Muestra la página principal del sitio."""

    featured_services = (
        Service.objects
        .filter(
            is_active=True,
            is_featured=True,
            category__is_active=True,
        )
        .select_related("category")
        .order_by(
            "category__display_order",
            "display_order",
            "name",
        )[:6]
    )

    featured_projects = (
        Project.objects
        .filter(
            is_active=True,
            is_featured=True,
        )
        .prefetch_related("services")
        .order_by(
            "display_order",
            "-completion_date",
            "title",
        )[:3]
    )

    context = {
        "services": featured_services,
        "featured_projects": featured_projects,
    }

    return render(
        request,
        "core/home.html",
        context,
    )