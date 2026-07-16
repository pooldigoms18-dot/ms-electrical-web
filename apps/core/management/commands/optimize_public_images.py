"""Optimiza imágenes públicas ya almacenadas."""

from pathlib import Path

from django.core.management.base import BaseCommand

from apps.core.image_utils import optimize_image_path
from apps.portfolio.models import (
    Project,
    ProjectImage,
)
from apps.services.models import ServiceImage


def format_size(size):
    """Convierte bytes a una representación legible."""

    return f"{size / 1024:.1f} KB"


class Command(BaseCommand):
    """Optimiza fotografías públicas existentes."""

    help = (
        "Optimiza imágenes públicas de servicios y proyectos."
    )

    def add_arguments(self, parser):
        """Define opciones del comando."""

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Analiza las imágenes sin modificar "
                "los archivos originales."
            ),
        )

    def handle(self, *args, **options):
        """Ejecuta la optimización."""

        dry_run = options[
            "dry_run"
        ]

        image_fields = []

        for service_image in (
            ServiceImage.objects
            .exclude(image="")
        ):
            image_fields.append(
                service_image.image,
            )

        for project in (
            Project.objects
            .exclude(cover_image="")
        ):
            image_fields.append(
                project.cover_image,
            )

        for project_image in (
            ProjectImage.objects
            .exclude(image="")
        ):
            image_fields.append(
                project_image.image,
            )

        processed_paths = set()

        total_original = 0
        total_final = 0
        optimized_count = 0

        for image_field in image_fields:
            try:
                path = Path(
                    image_field.path,
                )
            except (
                ValueError,
                NotImplementedError,
            ):
                continue

            resolved_path = str(
                path.resolve(),
            )

            if resolved_path in processed_paths:
                continue

            processed_paths.add(
                resolved_path,
            )

            result = optimize_image_path(
                path,
                apply_changes=not dry_run,
            )

            if not result[
                "processed"
            ]:
                continue

            total_original += result[
                "original_size"
            ]

            total_final += result[
                "final_size"
            ]

            if result[
                "optimized"
            ]:
                optimized_count += 1

                self.stdout.write(
                    (
                        f"{path.name}: "
                        f"{format_size(result['original_size'])} "
                        "-> "
                        f"{format_size(result['final_size'])}"
                    )
                )

        saved_bytes = max(
            0,
            total_original - total_final,
        )

        mode = (
            "SIMULACIÓN"
            if dry_run
            else "OPTIMIZACIÓN"
        )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"{mode} completada. "
                f"Imágenes optimizables: {optimized_count}. "
                f"Ahorro estimado: "
                f"{format_size(saved_bytes)}."
            )
        )