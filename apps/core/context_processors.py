"""Datos globales disponibles en todas las plantillas."""

import json

from django.conf import settings
from django.utils.safestring import mark_safe

from .models import CompanyProfile


def get_site_url(request):
    """Devuelve la URL principal configurada para el sitio."""

    configured_url = getattr(
        settings,
        "SITE_URL",
        "",
    ).strip().rstrip("/")

    if configured_url:
        return configured_url

    return request.build_absolute_uri("/").rstrip("/")


def build_local_business_schema(company, site_url):
    """Construye los datos estructurados del negocio."""

    if not company:
        return ""

    social_links = [
        url
        for url in (
            company.facebook_url,
            company.youtube_url,
            company.instagram_url,
        )
        if url
    ]

    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": company.commercial_name,
        "legalName": company.legal_name,
        "description": (
            company.hero_description
            or company.tagline
        ),
        "url": f"{site_url}/",
        "email": company.email,
        "taxID": company.ruc,
        "foundingDate": str(
            company.founded_year
        ),
        "address": {
            "@type": "PostalAddress",
            "addressLocality": company.city,
            "addressRegion": company.region,
            "addressCountry": company.country,
        },
        "areaServed": company.coverage,
    }

    if company.whatsapp:
        schema["telephone"] = (
            f"+{company.whatsapp}"
        )

    if social_links:
        schema["sameAs"] = social_links

    schema_json = json.dumps(
        schema,
        ensure_ascii=False,
    )

    # Evita que una cadena introducida desde el administrador
    # pueda cerrar accidentalmente la etiqueta <script>.
    schema_json = schema_json.replace(
        "</",
        "<\\/",
    )

    return mark_safe(schema_json)


def company_profile(request):
    """Entrega datos empresariales y SEO global a las plantillas."""

    company = (
        CompanyProfile.objects
        .filter(is_active=True)
        .order_by("-updated_at")
        .first()
    )

    site_url = get_site_url(
        request,
    )

    canonical_url = (
        f"{site_url}{request.path}"
    )

    local_business_schema = (
        build_local_business_schema(
            company,
            site_url,
        )
    )

    return {
        "company": company,
        "site_url": site_url,
        "canonical_url": canonical_url,
        "local_business_schema": (
            local_business_schema
        ),
    }