"""Administración de solicitudes de cotización."""

from django.contrib import admin
from django.utils.html import format_html

from .models import QuoteAttachment, QuoteRequest


class QuoteAttachmentInline(admin.TabularInline):
    """Muestra las fotografías dentro de cada solicitud."""

    model = QuoteAttachment
    extra = 0

    fields = (
        "image",
        "image_preview",
        "caption",
        "created_at",
    )

    readonly_fields = (
        "image_preview",
        "created_at",
    )

    @admin.display(description="Vista previa")
    def image_preview(self, obj):
        """Muestra una miniatura de la fotografía."""

        if not obj or not obj.image:
            return "Sin fotografía"

        return format_html(
            '<a href="{}" target="_blank">'
            '<img src="{}" '
            'style="width:110px;height:80px;'
            'object-fit:cover;border-radius:8px;">'
            "</a>",
            obj.image.url,
            obj.image.url,
        )


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    """Gestión comercial de solicitudes recibidas."""

    list_display = (
        "reference_code",
        "full_name",
        "requested_service",
        "district",
        "preferred_contact",
        "status",
        "created_at",
    )

    list_editable = (
        "status",
    )

    list_filter = (
        "status",
        "preferred_contact",
        "project_type",
        "service",
        "created_at",
    )

    search_fields = (
        "reference_code",
        "full_name",
        "phone",
        "email",
        "district",
        "other_service",
        "description",
    )

    autocomplete_fields = (
        "service",
    )

    readonly_fields = (
        "reference_code",
        "public_id",
        "customer_whatsapp_link",
        "source_url",
        "privacy_consent",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "service",
    )

    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "reference_code",
                    "public_id",
                    "status",
                ),
            },
        ),
        (
            "Datos del cliente",
            {
                "fields": (
                    "full_name",
                    "phone",
                    "customer_whatsapp_link",
                    "email",
                    "preferred_contact",
                    "preferred_time",
                ),
            },
        ),
        (
            "Proyecto solicitado",
            {
                "fields": (
                    "service",
                    "other_service",
                    "project_type",
                    "district",
                    "address_reference",
                    "budget_range",
                    "desired_date",
                    "description",
                ),
            },
        ),
        (
            "Gestión interna",
            {
                "fields": (
                    "internal_notes",
                ),
            },
        ),
        (
            "Registro del formulario",
            {
                "fields": (
                    "source_url",
                    "privacy_consent",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    inlines = (
        QuoteAttachmentInline,
    )

    actions = (
        "mark_as_contacted",
        "mark_as_evaluating",
        "mark_as_quoted",
    )

    @admin.display(
        description="Servicio",
        ordering="service__name",
    )
    def requested_service(self, obj):
        """Muestra el nombre del servicio solicitado."""

        return obj.requested_service_name

    @admin.display(description="WhatsApp del cliente")
    def customer_whatsapp_link(self, obj):
        """Muestra un enlace directo para responder."""

        if not obj or not obj.phone:
            return "No disponible"

        return format_html(
            '<a href="{}" target="_blank" '
            'rel="noopener noreferrer">'
            "Abrir conversación con {}"
            "</a>",
            obj.customer_whatsapp_url,
            obj.phone,
        )

    @admin.action(description="Marcar como cliente contactado")
    def mark_as_contacted(self, request, queryset):
        """Actualiza solicitudes seleccionadas."""

        queryset.update(
            status=QuoteRequest.Status.CONTACTED,
        )

    @admin.action(description="Marcar como en evaluación")
    def mark_as_evaluating(self, request, queryset):
        """Actualiza solicitudes seleccionadas."""

        queryset.update(
            status=QuoteRequest.Status.EVALUATING,
        )

    @admin.action(description="Marcar como cotización enviada")
    def mark_as_quoted(self, request, queryset):
        """Actualiza solicitudes seleccionadas."""

        queryset.update(
            status=QuoteRequest.Status.QUOTED,
        )


@admin.register(QuoteAttachment)
class QuoteAttachmentAdmin(admin.ModelAdmin):
    """Administración independiente de fotografías."""

    list_display = (
        "quote_request",
        "caption",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "quote_request__reference_code",
        "quote_request__full_name",
        "caption",
    )

    autocomplete_fields = (
        "quote_request",
    )