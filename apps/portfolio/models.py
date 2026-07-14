"""Modelos del portafolio de proyectos de MS Electrical."""

from pathlib import Path

from django.db import models
from django.utils.text import slugify

from apps.services.models import Service


def generate_unique_slug(model, value, current_pk=None):
    """Genera un identificador URL único."""

    base_slug = slugify(value) or "proyecto"
    candidate = base_slug
    counter = 2

    queryset = model.objects.all()

    if current_pk:
        queryset = queryset.exclude(pk=current_pk)

    while queryset.filter(slug=candidate).exists():
        candidate = f"{base_slug}-{counter}"
        counter += 1

    return candidate


def project_cover_upload_path(instance, filename):
    """Organiza las portadas en una carpeta por proyecto."""

    folder = (
        instance.slug
        or slugify(instance.title)
        or "proyecto"
    )

    extension = Path(filename).suffix.lower()
    filename_slug = slugify(Path(filename).stem) or "portada"

    return (
        f"projects/{folder}/cover/"
        f"{filename_slug}{extension}"
    )


def project_gallery_upload_path(instance, filename):
    """Organiza las imágenes de galería por proyecto."""

    folder = (
        instance.project.slug
        or slugify(instance.project.title)
        or "proyecto"
    )

    extension = Path(filename).suffix.lower()
    filename_slug = slugify(Path(filename).stem) or "imagen"

    return (
        f"projects/{folder}/gallery/"
        f"{filename_slug}{extension}"
    )


class Project(models.Model):
    """Proyecto realizado o administrado por MS Electrical."""

    class ProjectType(models.TextChoices):
        """Tipos generales de proyecto."""

        RESIDENTIAL = "residential", "Residencial"
        COMMERCIAL = "commercial", "Comercial"
        INSTITUTIONAL = "institutional", "Institucional"
        INDUSTRIAL = "industrial", "Industrial"
        OTHER = "other", "Otro"

    title = models.CharField(
        "nombre del proyecto",
        max_length=180,
        unique=True,
    )

    slug = models.SlugField(
        "identificador URL",
        max_length=200,
        unique=True,
        blank=True,
        help_text=(
            "Se genera automáticamente a partir del nombre. "
            "Ejemplo: automatizacion-porton-residencial."
        ),
    )

    project_type = models.CharField(
        "tipo de proyecto",
        max_length=30,
        choices=ProjectType.choices,
        default=ProjectType.RESIDENTIAL,
    )

    services = models.ManyToManyField(
        Service,
        verbose_name="servicios realizados",
        related_name="projects",
        blank=True,
    )

    location = models.CharField(
        "ubicación",
        max_length=180,
        default="Huancayo, Junín",
    )

    completion_date = models.DateField(
        "fecha de finalización",
        blank=True,
        null=True,
    )

    short_description = models.CharField(
        "descripción breve",
        max_length=280,
        help_text=(
            "Resumen que aparecerá en las tarjetas del portafolio."
        ),
    )

    introduction = models.TextField(
        "presentación del proyecto",
        blank=True,
        help_text=(
            "Descripción general del trabajo realizado."
        ),
    )

    challenge = models.TextField(
        "necesidad o problema inicial",
        blank=True,
        help_text=(
            "Explica qué necesitaba resolver el cliente."
        ),
    )

    solution = models.TextField(
        "solución ejecutada",
        blank=True,
        help_text=(
            "Describe el trabajo, los equipos o materiales utilizados."
        ),
    )

    result = models.TextField(
        "resultado obtenido",
        blank=True,
        help_text=(
            "Explica los beneficios o mejoras logradas."
        ),
    )

    cover_image = models.ImageField(
        "imagen principal",
        upload_to=project_cover_upload_path,
        blank=True,
    )

    cover_alt_text = models.CharField(
        "texto alternativo de la portada",
        max_length=180,
        blank=True,
        help_text=(
            "Describe lo que aparece en la imagen principal."
        ),
    )

    display_order = models.PositiveSmallIntegerField(
        "orden de presentación",
        default=0,
        help_text="Los números menores aparecen primero.",
    )

    is_featured = models.BooleanField(
        "mostrar como proyecto destacado",
        default=False,
    )

    is_active = models.BooleanField(
        "proyecto publicado",
        default=True,
    )

    created_at = models.DateTimeField(
        "fecha de creación",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "última actualización",
        auto_now=True,
    )

    class Meta:
        ordering = (
            "display_order",
            "-completion_date",
            "title",
        )
        verbose_name = "proyecto"
        verbose_name_plural = "proyectos"

    def __str__(self):
        """Representa el proyecto en el administrador."""

        return self.title

    def save(self, *args, **kwargs):
        """Genera el identificador URL cuando esté vacío."""

        if not self.slug:
            self.slug = generate_unique_slug(
                Project,
                self.title,
                self.pk,
            )

        super().save(*args, **kwargs)


class ProjectImage(models.Model):
    """Imagen adicional perteneciente a un proyecto."""

    project = models.ForeignKey(
        Project,
        verbose_name="proyecto",
        related_name="images",
        on_delete=models.CASCADE,
    )

    image = models.ImageField(
        "archivo de imagen",
        upload_to=project_gallery_upload_path,
    )

    alt_text = models.CharField(
        "texto alternativo",
        max_length=180,
        help_text=(
            "Describe brevemente lo que aparece en la fotografía."
        ),
    )

    caption = models.CharField(
        "descripción visible",
        max_length=220,
        blank=True,
    )

    display_order = models.PositiveSmallIntegerField(
        "orden de presentación",
        default=0,
    )

    is_active = models.BooleanField(
        "imagen visible",
        default=True,
    )

    created_at = models.DateTimeField(
        "fecha de carga",
        auto_now_add=True,
    )

    class Meta:
        ordering = (
            "display_order",
            "id",
        )
        verbose_name = "imagen del proyecto"
        verbose_name_plural = "imágenes del proyecto"

    def __str__(self):
        """Representa la imagen en el administrador."""

        return f"Imagen de {self.project.title}"