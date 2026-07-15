"""Etiquetas de plantilla para datos estructurados."""

from django import template
from django.urls import reverse

from apps.core.seo import (
    build_breadcrumb_schema,
    build_project_schema,
    build_service_schema,
)


register = template.Library()


@register.simple_tag(takes_context=True)
def service_structured_data(
    context,
    service,
):
    """Genera el esquema de un servicio."""

    request = context.get(
        "request",
    )

    if not request:
        return ""

    return build_service_schema(
        request,
        service,
    )


@register.simple_tag(takes_context=True)
def service_breadcrumb_structured_data(
    context,
    service,
):
    """Genera breadcrumbs para un servicio."""

    request = context.get(
        "request",
    )

    if not request:
        return ""

    return build_breadcrumb_schema(
        request,
        [
            (
                "Inicio",
                reverse("core:home"),
            ),
            (
                "Servicios",
                reverse("services:list"),
            ),
            (
                service.name,
                reverse(
                    "services:detail",
                    kwargs={
                        "slug": service.slug,
                    },
                ),
            ),
        ],
    )


@register.simple_tag(takes_context=True)
def project_structured_data(
    context,
    project,
):
    """Genera el esquema de un proyecto."""

    request = context.get(
        "request",
    )

    if not request:
        return ""

    return build_project_schema(
        request,
        project,
    )


@register.simple_tag(takes_context=True)
def project_breadcrumb_structured_data(
    context,
    project,
):
    """Genera breadcrumbs para un proyecto."""

    request = context.get(
        "request",
    )

    if not request:
        return ""

    return build_breadcrumb_schema(
        request,
        [
            (
                "Inicio",
                reverse("core:home"),
            ),
            (
                "Proyectos",
                reverse("portfolio:list"),
            ),
            (
                project.title,
                reverse(
                    "portfolio:detail",
                    kwargs={
                        "slug": project.slug,
                    },
                ),
            ),
        ],
    )


@register.simple_tag(takes_context=True)
def section_breadcrumb_structured_data(
    context,
    label,
    route_name,
):
    """Genera breadcrumbs para una página principal."""

    request = context.get(
        "request",
    )

    if not request:
        return ""

    return build_breadcrumb_schema(
        request,
        [
            (
                "Inicio",
                reverse("core:home"),
            ),
            (
                label,
                reverse(route_name),
            ),
        ],
    )