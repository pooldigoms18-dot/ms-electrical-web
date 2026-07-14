"""Administración del catálogo de servicios."""

from django.contrib import admin

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