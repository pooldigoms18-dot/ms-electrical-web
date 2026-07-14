"""Datos globales disponibles en todas las plantillas."""

from .models import CompanyProfile


def company_profile(request):
    """Entrega la ficha activa de la empresa a las plantillas."""

    company = (
        CompanyProfile.objects
        .filter(is_active=True)
        .order_by("-updated_at")
        .first()
    )

    return {
        "company": company,
    }
