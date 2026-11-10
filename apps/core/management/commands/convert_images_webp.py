"""Convierte a WebP las imágenes públicas que ya están subidas.

Las fotos nuevas ya se guardan como WebP al subirlas. Este comando
hace lo mismo con las anteriores (PNG/JPG de varios MB).

Seguridad:
- Por defecto solo muestra lo que haría. Para aplicar: --apply
- No borra los archivos originales: crea el .webp al lado y
  actualiza la referencia en la base de datos. Restaurar el
  respaldo de la base de datos deja todo como estaba.
- No llama a save() de los modelos (evita efectos secundarios).
"""

from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.core.image_utils import optimize_uploaded_image
from apps.core.models import CompanyProfile
from apps.portfolio.models import Project, ProjectImage
from apps.services.models import ServiceImage


# (modelo, campo, tamaño máximo en píxeles)
TARGETS = (
    (Project, "cover_image", 1920),
    (ProjectImage, "image", 1920),
    (ServiceImage, "image", 1920),
    # El logo se muestra a menos de 60 px: 512 px sobra.
    (CompanyProfile, "logo", 512),
)


def kb(size):
    return f"{size / 1024:,.0f} KB"


class Command(BaseCommand):
    help = "Convierte a WebP las imágenes públicas ya subidas."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Aplica los cambios (sin esto solo se simula).",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        total_before = 0
        total_after = 0
        converted = 0

        for model, field_name, max_size in TARGETS:
            queryset = model.objects.exclude(**{field_name: ""})

            for obj in queryset:
                field = getattr(obj, field_name)
                name = field.name

                if Path(name).suffix.lower() == ".webp":
                    continue

                if not field.storage.exists(name):
                    self.stdout.write(
                        self.style.WARNING(f"  falta el archivo: {name}")
                    )
                    continue

                with field.storage.open(name, "rb") as source:
                    original = ContentFile(
                        source.read(),
                        name=Path(name).name,
                    )

                before = original.size
                result = optimize_uploaded_image(
                    original,
                    max_width=max_size,
                    max_height=max_size,
                )
                after = result.size

                if not result.name.endswith(".webp") or after >= before:
                    self.stdout.write(f"  sin mejora: {name}")
                    continue

                total_before += before
                total_after += after
                converted += 1

                self.stdout.write(
                    f"  {name}: {kb(before)} -> {kb(after)}"
                )

                if apply_changes:
                    target = str(Path(name).with_suffix(".webp"))
                    result.seek(0)
                    saved_name = field.storage.save(target, result)
                    model.objects.filter(pk=obj.pk).update(
                        **{field_name: saved_name}
                    )

        verb = "Convertidas" if apply_changes else "Se convertirían"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} {converted} imágenes: "
                f"{kb(total_before)} -> {kb(total_after)}"
            )
        )

        if not apply_changes and converted:
            self.stdout.write(
                "Simulación. Ejecuta con --apply para aplicar "
                "(haz antes un respaldo de la base de datos)."
            )
