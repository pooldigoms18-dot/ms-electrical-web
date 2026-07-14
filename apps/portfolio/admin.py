"""Administración del portafolio de proyectos."""

from django.contrib import admin

from .models import Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    """Permite cargar imágenes dentro de cada proyecto."""

    model = ProjectImage
    extra = 0

    fields = (
        "image",
        "alt_text",
        "caption",
        "display_order",
        "is_active",
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Administración de proyectos realizados."""

    list_display = (
        "title",
        "project_type",
        "location",
        "completion_date",
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
        "project_type",
        "is_featured",
        "is_active",
        "services",
    )

    search_fields = (
        "title",
        "location",
        "short_description",
        "introduction",
        "challenge",
        "solution",
        "result",
    )

    prepopulated_fields = {
        "slug": (
            "title",
        ),
    }

    filter_horizontal = (
        "services",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "completion_date"

    fieldsets = (
        (
            "Identificación del proyecto",
            {
                "fields": (
                    "title",
                    "slug",
                    "project_type",
                    "services",
                    "location",
                    "completion_date",
                ),
            },
        ),
        (
            "Presentación",
            {
                "fields": (
                    "short_description",
                    "introduction",
                ),
            },
        ),
        (
            "Caso de proyecto",
            {
                "fields": (
                    "challenge",
                    "solution",
                    "result",
                ),
            },
        ),
        (
            "Imagen principal",
            {
                "fields": (
                    "cover_image",
                    "cover_alt_text",
                ),
            },
        ),
        (
            "Publicación",
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
        ProjectImageInline,
    )


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    """Administración independiente de imágenes."""

    list_display = (
        "project",
        "alt_text",
        "display_order",
        "is_active",
        "created_at",
    )

    list_editable = (
        "display_order",
        "is_active",
    )

    list_filter = (
        "is_active",
        "project",
    )

    search_fields = (
        "project__title",
        "alt_text",
        "caption",
    )

    autocomplete_fields = (
        "project",
    )