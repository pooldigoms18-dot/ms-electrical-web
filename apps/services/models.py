"""Modelos del catálogo de servicios de MS Electrical."""

from django.db import models
from django.utils.text import slugify
from apps.core.image_utils import optimize_uploaded_image

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
def service_image_upload_path(instance, filename):
    """Organiza las imágenes dentro de una carpeta por servicio."""

    return f"services/{instance.service.slug}/{filename}"


class ServiceBenefit(models.Model):
    """Beneficio comercial relacionado con un servicio."""

    service = models.ForeignKey(
        Service,
        verbose_name="servicio",
        related_name="benefits",
        on_delete=models.CASCADE,
    )

    title = models.CharField(
        "título",
        max_length=140,
    )

    description = models.TextField(
        "descripción",
    )

    display_order = models.PositiveSmallIntegerField(
        "orden de presentación",
        default=0,
    )

    is_active = models.BooleanField(
        "beneficio activo",
        default=True,
    )

    class Meta:
        ordering = (
            "display_order",
            "id",
        )
        verbose_name = "beneficio"
        verbose_name_plural = "beneficios"

    def __str__(self):
        return f"{self.service.name}: {self.title}"


class ServiceFeature(models.Model):
    """Característica o especificación de un servicio."""

    service = models.ForeignKey(
        Service,
        verbose_name="servicio",
        related_name="features",
        on_delete=models.CASCADE,
    )

    title = models.CharField(
        "característica",
        max_length=140,
    )

    description = models.CharField(
        "detalle",
        max_length=300,
    )

    display_order = models.PositiveSmallIntegerField(
        "orden de presentación",
        default=0,
    )

    is_active = models.BooleanField(
        "característica activa",
        default=True,
    )

    class Meta:
        ordering = (
            "display_order",
            "id",
        )
        verbose_name = "característica"
        verbose_name_plural = "características"

    def __str__(self):
        return f"{self.service.name}: {self.title}"


class ServiceProcessStep(models.Model):
    """Etapa del proceso específico de un servicio."""

    service = models.ForeignKey(
        Service,
        verbose_name="servicio",
        related_name="process_steps",
        on_delete=models.CASCADE,
    )

    title = models.CharField(
        "nombre de la etapa",
        max_length=140,
    )

    description = models.TextField(
        "descripción",
    )

    display_order = models.PositiveSmallIntegerField(
        "orden de presentación",
        default=0,
    )

    is_active = models.BooleanField(
        "etapa activa",
        default=True,
    )

    class Meta:
        ordering = (
            "display_order",
            "id",
        )
        verbose_name = "etapa del proceso"
        verbose_name_plural = "etapas del proceso"

    def __str__(self):
        return f"{self.service.name}: {self.title}"


class ServiceFAQ(models.Model):
    """Pregunta frecuente relacionada con un servicio."""

    service = models.ForeignKey(
        Service,
        verbose_name="servicio",
        related_name="faqs",
        on_delete=models.CASCADE,
    )

    question = models.CharField(
        "pregunta",
        max_length=240,
    )

    answer = models.TextField(
        "respuesta",
    )

    display_order = models.PositiveSmallIntegerField(
        "orden de presentación",
        default=0,
    )

    is_active = models.BooleanField(
        "pregunta activa",
        default=True,
    )

    class Meta:
        ordering = (
            "display_order",
            "id",
        )
        verbose_name = "pregunta frecuente"
        verbose_name_plural = "preguntas frecuentes"

    def __str__(self):
        return self.question


class ServiceImage(models.Model):
    """Imagen perteneciente a un servicio."""

    service = models.ForeignKey(
        Service,
        verbose_name="servicio",
        related_name="images",
        on_delete=models.CASCADE,
    )

    image = models.ImageField(
        "archivo de imagen",
        upload_to=service_image_upload_path,
    )

    alt_text = models.CharField(
        "texto alternativo",
        max_length=180,
        help_text=(
            "Describe brevemente lo que aparece en la imagen. "
            "Ejemplo: Portón corredizo automatizado en Huancayo."
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

    is_cover = models.BooleanField(
        "usar como imagen principal",
        default=False,
    )

    is_active = models.BooleanField(
        "imagen activa",
        default=True,
    )

    created_at = models.DateTimeField(
        "fecha de carga",
        auto_now_add=True,
    )

    class Meta:
        ordering = (
            "-is_cover",
            "display_order",
            "id",
        )
        verbose_name = "imagen del servicio"
        verbose_name_plural = "imágenes del servicio"

    def save(self, *args, **kwargs):
        """Optimiza nuevas fotografías antes de almacenarlas."""

        if (
            self.image
            and not self.image._committed
        ):
            self.image = optimize_uploaded_image(
                self.image,
            )

        super().save(
            *args,
            **kwargs,
        )
        
    def __str__(self):
        return f"Imagen de {self.service.name}"

    def save(self, *args, **kwargs):
        """Conserva una sola imagen principal por servicio."""

        if self.is_cover and self.service_id:
            (
                ServiceImage.objects
                .filter(
                    service_id=self.service_id,
                    is_cover=True,
                )
                .exclude(pk=self.pk)
                .update(is_cover=False)
            )

        super().save(*args, **kwargs)       