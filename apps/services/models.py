"""Modelos del catálogo de servicios de MS Electrical."""

from django.db import models
from django.utils.text import slugify


def generate_unique_slug(model, value, current_pk=None):
    """Genera un identificador URL único a partir de un texto."""

    base_slug = slugify(value) or "elemento"
    candidate = base_slug
    counter = 2

    queryset = model.objects.all()

    if current_pk:
        queryset = queryset.exclude(pk=current_pk)

    while queryset.filter(slug=candidate).exists():
        candidate = f"{base_slug}-{counter}"
        counter += 1

    return candidate


class ServiceCategory(models.Model):
    """Agrupa servicios relacionados dentro del catálogo."""

    name = models.CharField(
        "nombre",
        max_length=120,
        unique=True,
    )

    slug = models.SlugField(
        "identificador URL",
        max_length=140,
        unique=True,
        blank=True,
        help_text=(
            "Se genera automáticamente a partir del nombre. "
            "Ejemplo: puertas-y-accesos."
        ),
    )

    description = models.TextField(
        "descripción",
        blank=True,
    )

    icon_key = models.CharField(
        "nombre interno del icono",
        max_length=50,
        blank=True,
        help_text=(
            "Ejemplo: door, security, electricity o printer-3d."
        ),
    )

    display_order = models.PositiveSmallIntegerField(
        "orden de presentación",
        default=0,
        help_text="Los números menores aparecen primero.",
    )

    is_active = models.BooleanField(
        "categoría activa",
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
            "name",
        )
        verbose_name = "categoría de servicio"
        verbose_name_plural = "categorías de servicios"

    def __str__(self):
        """Representa la categoría dentro del administrador."""

        return self.name

    def save(self, *args, **kwargs):
        """Genera el slug cuando todavía no existe."""

        if not self.slug:
            self.slug = generate_unique_slug(
                ServiceCategory,
                self.name,
                self.pk,
            )

        super().save(*args, **kwargs)


class Service(models.Model):
    """Servicio comercial ofrecido por MS Electrical."""

    category = models.ForeignKey(
        ServiceCategory,
        verbose_name="categoría",
        related_name="services",
        on_delete=models.PROTECT,
    )

    name = models.CharField(
        "nombre",
        max_length=160,
        unique=True,
    )

    slug = models.SlugField(
        "identificador URL",
        max_length=180,
        unique=True,
        blank=True,
        help_text=(
            "Se genera automáticamente. "
            "Ejemplo: automatizacion-de-portones."
        ),
    )

    card_description = models.CharField(
        "descripción para tarjetas",
        max_length=260,
        help_text=(
            "Texto breve que aparecerá en listados y tarjetas."
        ),
    )

    introduction = models.TextField(
        "introducción del servicio",
        blank=True,
        help_text=(
            "Descripción amplia que utilizaremos en la página "
            "individual del servicio."
        ),
    )

    icon_key = models.CharField(
        "nombre interno del icono",
        max_length=50,
        blank=True,
    )

    whatsapp_message = models.CharField(
        "mensaje inicial de WhatsApp",
        max_length=400,
        blank=True,
        help_text=(
            "Mensaje que se preparará al consultar este servicio."
        ),
    )

    seo_title = models.CharField(
        "título SEO",
        max_length=70,
        blank=True,
    )

    seo_description = models.CharField(
        "descripción SEO",
        max_length=170,
        blank=True,
    )

    display_order = models.PositiveSmallIntegerField(
        "orden de presentación",
        default=0,
        help_text="Los números menores aparecen primero.",
    )

    is_featured = models.BooleanField(
        "mostrar como destacado",
        default=False,
    )

    is_active = models.BooleanField(
        "servicio activo",
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
            "category__display_order",
            "display_order",
            "name",
        )
        verbose_name = "servicio"
        verbose_name_plural = "servicios"

    def __str__(self):
        """Representa el servicio dentro del administrador."""

        return self.name

    def save(self, *args, **kwargs):
        """Genera el slug y el mensaje inicial cuando faltan."""

        if not self.slug:
            self.slug = generate_unique_slug(
                Service,
                self.name,
                self.pk,
            )

        if not self.whatsapp_message:
            self.whatsapp_message = (
                f"Hola, deseo información sobre el servicio "
                f"de {self.name}."
            )

        super().save(*args, **kwargs)