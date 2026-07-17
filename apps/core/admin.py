"""Configuración del panel administrativo de MS Electrical."""

from django.contrib import admin

from .models import CompanyProfile, GlobalFAQ


admin.site.site_header = "Administración de MS Electrical"
admin.site.site_title = "MS Electrical"
admin.site.index_title = "Panel de gestión"


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    """Administración de los datos generales de la empresa."""

    list_display = (
        "commercial_name",
        "ruc",
        "responsible_name",
        "city",
        "is_active",
        "updated_at",
    )

    readonly_fields = (
        "updated_at",
        "whatsapp_preview",
    )

    fieldsets = (
        (
            "Identidad empresarial",
            {
                "fields": (
                    "commercial_name",
                    "logo",
                    "logo_alt_text",
                    "legal_name",
                    "ruc",
                    "responsible_name",
                    "founded_year",
                    "tagline",
                ),
            },
        ),
        (
            "Presentación",
            {
                "fields": (
                    "hero_description",
                    "history",
                ),
            },
        ),
        (
            "Contacto y atención",
            {
                "fields": (
                    "whatsapp",
                    "whatsapp_preview",
                    "email",
                    "business_hours",
                    "response_time",
                    "coverage",
                ),
            },
        ),
        (
            "Condiciones comerciales",
            {
                "fields": (
                    "warranty",
                    "maintenance",
                    "payment_methods",
                ),
            },
        ),
        (
            "Ubicación",
            {
                "fields": (
                    "city",
                    "region",
                    "country",
                    "public_address",
                    "postal_code",
                    "google_maps_url",
                    "latitude",
                    "longitude",
                ),
            },
        ),
        (
            "Redes sociales",
            {
                "fields": (
                    "facebook_url",
                    "youtube_url",
                    "instagram_url",
                ),
            },
        ),
        (
            "Control del registro",
            {
                "fields": (
                    "is_active",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.display(description="Vista del WhatsApp")
    def whatsapp_preview(self, obj):
        """Muestra el número con formato legible."""

        if not obj or not obj.whatsapp:
            return "Se mostrará después de guardar."

        return obj.whatsapp_display

    def has_add_permission(self, request):
        """Permite conservar una sola ficha empresarial."""

        if CompanyProfile.objects.exists():
            return False

        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        """Evita eliminar accidentalmente la ficha empresarial."""

        return False
@admin.register(GlobalFAQ)
class GlobalFAQAdmin(admin.ModelAdmin):
    """Administración de preguntas frecuentes."""

    list_display = (
        "question",
        "show_on_home",
        "is_active",
        "display_order",
        "updated_at",
    )

    list_editable = (
        "show_on_home",
        "is_active",
        "display_order",
    )

    list_filter = (
        "show_on_home",
        "is_active",
    )

    search_fields = (
        "question",
        "answer",
    )

    ordering = (
        "display_order",
        "question",
    )