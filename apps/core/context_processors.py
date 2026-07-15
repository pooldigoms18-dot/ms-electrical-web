"""Datos globales disponibles en todas las plantillas."""

import re

from django.conf import settings

from .models import CompanyProfile
from .seo import (
    get_site_url,
    normalize_peru_phone,
    serialize_schema,
)


def get_coverage_areas(coverage):
    """Convierte la cobertura escrita en una lista de zonas."""

    if not coverage:
        return []

    normalized = re.sub(
        r"\s+y\s+",
        ", ",
        coverage,
        flags=re.IGNORECASE,
    )

    return [
        area.strip().rstrip(".")
        for area in normalized.split(",")
        if area.strip()
    ]


def build_local_business_schema(
    company,
    site_url,
):
    """Construye los datos estructurados de MS Electrical."""

    if not company:
        return ""

    business_name = (
        company.commercial_name
        or "MS Electrical"
    )

    schema = {
        "@context": "https://schema.org",
        "@type": [
            "HomeAndConstructionBusiness",
            "Electrician",
        ],
        "@id": f"{site_url}/#business",
        "name": business_name,
        "url": f"{site_url}/",
    }

    if company.legal_name:
        schema["legalName"] = (
            company.legal_name
        )

    description = (
        company.hero_description
        or company.tagline
    )

    if description:
        schema["description"] = (
            description
        )

    if company.ruc:
        schema["taxID"] = (
            company.ruc
        )

    if company.email:
        schema["email"] = (
            company.email
        )

    telephone = normalize_peru_phone(
        company.whatsapp,
    )

    if telephone:
        schema["telephone"] = telephone

    if company.founded_year:
        schema["foundingDate"] = str(
            company.founded_year
        )

    address = {
        "@type": "PostalAddress",
    }

    if company.public_address:
        address["streetAddress"] = (
            company.public_address
        )

    if company.city:
        address["addressLocality"] = (
            company.city
        )

    if company.region:
        address["addressRegion"] = (
            company.region
        )

    if company.postal_code:
        address["postalCode"] = (
            company.postal_code
        )

    if company.country:
        country = company.country.strip()

        if country.lower() in (
            "perú",
            "peru",
            "pe",
        ):
            country = "PE"

        address["addressCountry"] = (
            country
        )

    if len(address) > 1:
        schema["address"] = address

    coverage_areas = get_coverage_areas(
        company.coverage,
    )

    if coverage_areas:
        schema["areaServed"] = [
            {
                "@type": "AdministrativeArea",
                "name": area,
            }
            for area in coverage_areas
        ]

    if (
        company.latitude is not None
        and company.longitude is not None
    ):
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(
                company.latitude
            ),
            "longitude": str(
                company.longitude
            ),
        }

    if company.google_maps_url:
        schema["hasMap"] = (
            company.google_maps_url
        )

    social_links = [
        url
        for url in (
            company.facebook_url,
            company.youtube_url,
            company.instagram_url,
        )
        if url
    ]

    if social_links:
        schema["sameAs"] = social_links

    if telephone or company.email:
        contact_point = {
            "@type": "ContactPoint",
            "contactType": (
                "customer service"
            ),
            "areaServed": "PE",
            "availableLanguage": [
                "Spanish",
            ],
        }

        if telephone:
            contact_point["telephone"] = (
                telephone
            )

        if company.email:
            contact_point["email"] = (
                company.email
            )

        schema["contactPoint"] = (
            contact_point
        )

    return serialize_schema(
        schema,
    )


def company_profile(request):
    """Entrega información empresarial y SEO global."""

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

    google_site_verification = getattr(
        settings,
        "GOOGLE_SITE_VERIFICATION",
        "",
    )

    return {
        "company": company,
        "site_url": site_url,
        "canonical_url": canonical_url,
        "local_business_schema": (
            local_business_schema
        ),
        "google_site_verification": (
            google_site_verification
        ),
    }