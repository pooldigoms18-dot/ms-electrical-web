"""Administración del catálogo de servicios."""

from django.contrib import admin

from .models import Service, ServiceCategory


class ServiceInline(admin.TabularInline):
    """Muestra los servicios dentro de cada categoría."""

    model = Service
    extra = 0

    fields = (
        "name",
        "display_order",
        "is_featured",
        "is_active",
    )

    show_change_link = True


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
        """Muestra cuántos servicios contiene la categoría."""

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
            "Contenido",
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