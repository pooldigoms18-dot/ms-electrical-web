"""Vistas públicas del portafolio de proyectos."""

from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Project


def project_list(request):
    """Muestra todos los proyectos publicados."""

    projects = (
        Project.objects
        .filter(is_active=True)
        .prefetch_related("services")
        .order_by(
            "-is_featured",
            "display_order",
            "-completion_date",
            "title",
        )
    )

    context = {
        "projects": projects,
    }

    return render(
        request,
        "portfolio/project_list.html",
        context,
    )


def project_detail(request, slug):
    """Muestra el contenido completo de un proyecto."""

    project = get_object_or_404(
        Project.objects.prefetch_related(
            "services",
            "images",
        ),
        slug=slug,
        is_active=True,
    )

    gallery_images = (
        project.images
        .filter(is_active=True)
        .order_by(
            "display_order",
            "id",
        )
    )

    service_ids = list(
        project.services.values_list(
            "id",
            flat=True,
        )
    )

    related_projects = (
        Project.objects
        .filter(is_active=True)
        .exclude(pk=project.pk)
    )

    if service_ids:
        related_projects = related_projects.filter(
            Q(services__in=service_ids)
            | Q(project_type=project.project_type)
        )
    else:
        related_projects = related_projects.filter(
            project_type=project.project_type,
        )

    related_projects = (
        related_projects
        .distinct()
        .prefetch_related("services")
        .order_by(
            "-is_featured",
            "display_order",
            "-completion_date",
            "title",
        )[:3]
    )

    context = {
        "project": project,
        "gallery_images": gallery_images,
        "related_projects": related_projects,
    }

    return render(
        request,
        "portfolio/project_detail.html",
        context,
    )