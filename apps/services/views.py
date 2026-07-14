"""Vistas públicas del catálogo de servicios."""

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from .models import Service, ServiceCategory


def service_list(request):
    """Muestra todas las categorías y servicios activos."""

    active_services = (
        Service.objects
        .filter(
            is_active=True,
            category__is_active=True,
        )
        .select_related("category")
        .order_by(
            "category__display_order",
            "display_order",
            "name",
        )
    )

    categories = (
        ServiceCategory.objects
        .filter(
            is_active=True,
            services__is_active=True,
        )
        .distinct()
        .order_by(
            "display_order",
            "name",
        )
        .prefetch_related(
            Prefetch(
                "services",
                queryset=active_services,
                to_attr="active_services",
            )
        )
    )

    context = {
        "categories": categories,
    }

    return render(
        request,
        "services/service_list.html",
        context,
    )


def service_detail(request, slug):
    """Muestra la información de un servicio específico."""

    service = get_object_or_404(
        Service.objects.select_related("category"),
        slug=slug,
        is_active=True,
        category__is_active=True,
    )

    related_services = (
        Service.objects
        .filter(
            category=service.category,
            category__is_active=True,
            is_active=True,
        )
        .exclude(pk=service.pk)
        .select_related("category")
        .order_by(
            "display_order",
            "name",
        )[:3]
    )

    context = {
        "service": service,
        "related_services": related_services,
    }

    return render(
        request,
        "services/service_detail.html",
        context,
    )