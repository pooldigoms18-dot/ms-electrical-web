"""Vistas de las páginas generales de MS Electrical."""

from django.shortcuts import render

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

    context = {
        "services": featured_services,
    }

    return render(
        request,
        "core/home.html",
        context,
    )