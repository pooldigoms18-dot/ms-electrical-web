"""Vistas de las páginas generales de MS Electrical."""

from django.conf import settings
from django.shortcuts import render

from apps.portfolio.models import Project
from apps.services.models import Service
from .models import GlobalFAQ

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
    home_faqs = (
        GlobalFAQ.objects
        .filter(
            is_active=True,
            show_on_home=True,
        )
        .order_by(
            "display_order",
            "question",
        )[:6]
    )

    context = {
        "services": featured_services,
        "featured_projects": featured_projects,
        "home_faqs": home_faqs,
    }

    return render(
        request,
        "core/home.html",
        context,
    )

def faq_list(request):
    """Muestra las preguntas frecuentes publicadas."""

    faqs = (
        GlobalFAQ.objects
        .filter(is_active=True)
        .order_by(
            "display_order",
            "question",
        )
    )

    context = {
        "faqs": faqs,
    }

    return render(
        request,
        "core/faq_list.html",
        context,
    )

def robots_txt(request):
    """Genera las instrucciones públicas para buscadores."""

    configured_url = getattr(
        settings,
        "SITE_URL",
        "",
    ).strip().rstrip("/")

    site_url = (
        configured_url
        or request.build_absolute_uri("/").rstrip("/")
    )

    context = {
        "site_url": site_url,
        "debug": settings.DEBUG,
    }

    return render(
        request,
        "robots.txt",
        context,
        content_type="text/plain",
    )