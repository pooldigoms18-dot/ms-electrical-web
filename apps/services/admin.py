"""Administración del catálogo de servicios."""

import json

from django.contrib import admin
from django.core.cache import cache
from django.http import JsonResponse
from django.urls import path

from apps.core.models import CompanyProfile

from .ai_suggestions import (
    AISuggestionError,
    is_configured,
    suggest_service,
)
from .models import (
    Service,
    ServiceBenefit,
    ServiceCategory,
    ServiceFAQ,
    ServiceFeature,
    ServiceImage,
    ServiceProcessStep,
)


class ServiceInline(admin.TabularInline):
    """Muestra servicios dentro de cada categoría."""

    model = Service
    extra = 0

    fields = (
        "name",
        "display_order",
        "is_featured",
        "is_active",
    )

    show_change_link = True


class ServiceBenefitInline(admin.StackedInline):
    """Permite administrar beneficios dentro del servicio."""

    model = ServiceBenefit
    extra = 0

    fields = (
        "title",
        "description",
        "display_order",
        "is_active",
    )


class ServiceFeatureInline(admin.TabularInline):
    """Permite administrar características del servicio."""

    model = ServiceFeature
    extra = 0

    fields = (
        "title",
        "description",
        "display_order",
        "is_active",
    )


class ServiceProcessStepInline(admin.StackedInline):
    """Permite definir el proceso propio del servicio."""

    model = ServiceProcessStep
    extra = 0

    fields = (
        "title",
        "description",
        "display_order",
        "is_active",
    )


class ServiceFAQInline(admin.StackedInline):
    """Permite registrar preguntas frecuentes."""

    model = ServiceFAQ
    extra = 0

    fields = (
        "question",
        "answer",
        "display_order",
        "is_active",
    )


class ServiceImageInline(admin.TabularInline):
    """Permite cargar las imágenes de cada servicio."""

    model = ServiceImage
    extra = 0

    fields = (
        "image",
        "alt_text",
        "caption",
        "display_order",
        "is_cover",
        "is_active",
    )


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Administración de las categorías de servicios."""

    list_display = (
        "name",
        "service_count",
        "display_order",
        "is_active",
        "updated_at",
    )

    list_editable = (
        "display_order",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": (
            "name",
        ),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = (
        ServiceInline,
    )

    fieldsets = (
        (
            "Información de la categoría",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "icon_key",
                ),
            },
        ),
        (
            "Presentación",
            {
                "fields": (
                    "display_order",
                    "is_active",
                ),
            },
        ),
        (
            "Registro",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.display(description="Servicios")
    def service_count(self, obj):
        return obj.services.count()


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Administración de los servicios comerciales."""

    list_display = (
        "name",
        "category",
        "display_order",
        "is_featured",
        "is_active",
        "updated_at",
    )

    list_editable = (
        "display_order",
        "is_featured",
        "is_active",
    )

    list_filter = (
        "category",
        "is_featured",
        "is_active",
    )

    search_fields = (
        "name",
        "card_description",
        "introduction",
    )

    prepopulated_fields = {
        "slug": (
            "name",
        ),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Identidad del servicio",
            {
                "fields": (
                    "category",
                    "name",
                    "slug",
                    "icon_key",
                ),
            },
        ),
        (
            "Contenido principal",
            {
                "fields": (
                    "card_description",
                    "introduction",
                ),
            },
        ),
        (
            "Contacto",
            {
                "fields": (
                    "whatsapp_message",
                ),
            },
        ),
        (
            "Posicionamiento SEO",
            {
                "fields": (
                    "seo_title",
                    "seo_description",
                ),
            },
        ),
        (
            "Presentación",
            {
                "fields": (
                    "display_order",
                    "is_featured",
                    "is_active",
                ),
            },
        ),
        (
            "Registro",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    inlines = (
        ServiceBenefitInline,
        ServiceFeatureInline,
        ServiceProcessStepInline,
        ServiceFAQInline,
        ServiceImageInline,
    )

    # Asistente de IA: sugiere los campos a partir del nombre.
    AI_RATE_LIMIT_PER_MINUTE = 6

    class Media:
        css = {
            "all": (
                "services/admin/ai-suggest.css",
            ),
        }
        js = (
            "services/admin/ai-suggest.js",
        )

    def get_urls(self):
        """Agrega la ruta del asistente de IA al administrador."""

        custom_urls = [
            path(
                "ai-suggest/",
                self.admin_site.admin_view(self.ai_suggest_view),
                name="services_service_ai_suggest",
            ),
        ]
        return custom_urls + super().get_urls()

    def ai_suggest_view(self, request):
        """Devuelve en JSON los campos sugeridos para un servicio."""

        if request.method != "POST":
            return JsonResponse(
                {"configured": is_configured()},
            )

        return _ai_suggest_post(self, request)


def _ai_suggest_post(model_admin, request):
    if not (
        model_admin.has_add_permission(request)
        or model_admin.has_change_permission(request)
    ):
        return JsonResponse({"error": "Sin permiso."}, status=403)

    rate_key = f"services-ai-suggest:{request.user.pk}"
    used = cache.get(rate_key, 0)
    if used >= model_admin.AI_RATE_LIMIT_PER_MINUTE:
        return JsonResponse(
            {"error": "Demasiadas solicitudes. Espera un minuto."},
            status=429,
        )
    cache.set(rate_key, used + 1, 60)

    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Solicitud inválida."}, status=400)

    categories = list(
        ServiceCategory.objects
        .filter(is_active=True)
        .values_list("name", flat=True)
    )
    icon_keys = sorted(
        {
            key
            for key in (
                list(Service.objects.values_list("icon_key", flat=True))
                + list(
                    ServiceCategory.objects.values_list(
                        "icon_key", flat=True,
                    )
                )
            )
            if key
        }
    )

    profile = (
        CompanyProfile.objects
        .filter(is_active=True)
        .order_by("-updated_at")
        .first()
    )
    company = {}
    if profile:
        company = {
            "Ciudad": f"{profile.city}, {profile.region}",
            "Cobertura": profile.coverage,
            "Garantía": profile.warranty,
            "Mantenimiento": profile.maintenance,
            "Formas de pago": profile.payment_methods,
            "Tiempo de respuesta": profile.response_time,
        }

    try:
        suggestion = suggest_service(
            payload.get("name", ""),
            categories,
            icon_keys,
            company,
        )
    except AISuggestionError as error:
        return JsonResponse({"error": str(error)}, status=400)

    category_ids = dict(
        ServiceCategory.objects.values_list("name", "pk")
    )
    suggestion["category_id"] = category_ids.get(suggestion["category"])

    return JsonResponse({"suggestion": suggestion})