"""Utilidades para SEO y datos estructurados."""

import json
import re
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe


def get_site_url(request):
    """Devuelve la URL principal configurada del sitio."""

    configured_url = getattr(
        settings,
        "SITE_URL",
        "",
    ).strip().rstrip("/")

    if configured_url:
        return configured_url

    return request.build_absolute_uri("/").rstrip("/")


def absolute_url(request, path):
    """Convierte una ruta interna en una URL absoluta."""

    base_url = f"{get_site_url(request)}/"

    return urljoin(
        base_url,
        str(path).lstrip("/"),
    )


def serialize_schema(data):
    """Convierte un diccionario en JSON seguro para JSON-LD."""

    schema_json = json.dumps(
        data,
        ensure_ascii=False,
    )

    schema_json = schema_json.replace(
        "</",
        "<\\/",
    )

    return mark_safe(
        schema_json,
    )


def normalize_peru_phone(phone):
    """Normaliza un teléfono peruano al formato internacional."""

    digits = re.sub(
        r"\D",
        "",
        phone or "",
    )

    if not digits:
        return ""

    if len(digits) == 9:
        digits = f"51{digits}"

    return f"+{digits}"


def build_breadcrumb_schema(request, items):
    """
    Construye un BreadcrumbList.

    items debe ser una lista de tuplas:
    [
        ("Inicio", "/"),
        ("Servicios", "/servicios/"),
        ("Servicio actual", "/servicios/servicio/")
    ]
    """

    item_list = []

    for position, item in enumerate(
        items,
        start=1,
    ):
        name, path = item

        breadcrumb_item = {
            "@type": "ListItem",
            "position": position,
            "name": name,
        }

        if path:
            breadcrumb_item["item"] = absolute_url(
                request,
                path,
            )

        item_list.append(
            breadcrumb_item,
        )

    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": item_list,
    }

    return serialize_schema(
        schema,
    )


def build_service_schema(request, service):
    """Construye datos estructurados para un servicio."""

    service_path = reverse(
        "services:detail",
        kwargs={
            "slug": service.slug,
        },
    )

    service_url = absolute_url(
        request,
        service_path,
    )

    description = (
        getattr(
            service,
            "seo_description",
            "",
        )
        or service.card_description
    )

    schema = {
        "@context": "https://schema.org",
        "@type": "Service",
        "@id": f"{service_url}#service",
        "name": service.name,
        "serviceType": service.name,
        "description": description,
        "url": service_url,
        "provider": {
            "@id": (
                f"{get_site_url(request)}/#business"
            ),
        },
    }

    category = getattr(
        service,
        "category",
        None,
    )

    if category:
        schema["category"] = category.name

    return serialize_schema(
        schema,
    )


def build_project_schema(request, project):
    """Construye datos estructurados para un proyecto realizado."""

    project_path = reverse(
        "portfolio:detail",
        kwargs={
            "slug": project.slug,
        },
    )

    project_url = absolute_url(
        request,
        project_path,
    )

    schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "@id": f"{project_url}#project",
        "name": project.title,
        "description": project.short_description,
        "url": project_url,
        "creator": {
            "@id": (
                f"{get_site_url(request)}/#business"
            ),
        },
    }

    if project.location:
        schema["contentLocation"] = {
            "@type": "Place",
            "name": project.location,
        }

    if project.completion_date:
        schema["dateCreated"] = (
            project.completion_date.isoformat()
        )

    if project.cover_image:
        schema["image"] = absolute_url(
            request,
            project.cover_image.url,
        )

    related_services = []

    for service in project.services.all():
        related_services.append(
            {
                "@type": "Service",
                "name": service.name,
                "url": absolute_url(
                    request,
                    reverse(
                        "services:detail",
                        kwargs={
                            "slug": service.slug,
                        },
                    ),
                ),
            }
        )

    if related_services:
        schema["about"] = related_services

    return serialize_schema(
        schema,
    )