"""Modelos para las solicitudes de cotización."""

import re
import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    RegexValidator,
)
from django.db import models
from django.utils.text import slugify

from apps.services.models import Service


phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s-]{7,20}$",
    message=(
        "Ingresa un número válido usando solamente números, "
        "espacios, guiones y, opcionalmente, el símbolo +."
    ),
)


def validate_image_size(image):
    """Limita cada fotografía a un máximo de 8 MB."""

    maximum_size = 8 * 1024 * 1024

    if image.size > maximum_size:
        raise ValidationError(
            "Cada fotografía debe pesar como máximo 8 MB."
        )


def quote_attachment_upload_path(instance, filename):
    """Organiza las fotografías por código de solicitud."""

    request_identifier = (
        instance.quote_request.reference_code
        or str(instance.quote_request.public_id)
    )

    extension = Path(filename).suffix.lower()
    original_name = slugify(Path(filename).stem) or "fotografia"
    unique_suffix = uuid.uuid4().hex[:8]

    return (
        f"quotes/{request_identifier}/"
        f"{original_name}-{unique_suffix}{extension}"
    )


class QuoteRequest(models.Model):
    """Solicitud enviada por un posible cliente."""

    class ProjectType(models.TextChoices):
        """Tipo general del proyecto."""

        RESIDENTIAL = "residential", "Vivienda"
        COMMERCIAL = "commercial", "Negocio o comercio"
        INSTITUTIONAL = "institutional", "Institución"
        INDUSTRIAL = "industrial", "Industrial"
        OTHER = "other", "Otro"

    class PreferredContact(models.TextChoices):
        """Medio preferido para responder al cliente."""

        WHATSAPP = "whatsapp", "WhatsApp"
        PHONE = "phone", "Llamada telefónica"
        EMAIL = "email", "Correo electrónico"

    class PreferredTime(models.TextChoices):
        """Momento preferido para contactar."""

        MORNING = "morning", "Mañana"
        AFTERNOON = "afternoon", "Tarde"
        ANY = "any", "Cualquier horario"

    class BudgetRange(models.TextChoices):
        """Rango referencial del presupuesto."""

        UNDER_1000 = "under_1000", "Menos de S/ 1,000"
        FROM_1000_TO_3000 = "1000_3000", "S/ 1,000 a S/ 3,000"
        FROM_3000_TO_7000 = "3000_7000", "S/ 3,000 a S/ 7,000"
        OVER_7000 = "over_7000", "Más de S/ 7,000"
        UNDEFINED = "undefined", "Aún no lo he definido"

    class Status(models.TextChoices):
        """Estado interno de la solicitud."""

        NEW = "new", "Nueva"
        CONTACTED = "contacted", "Cliente contactado"
        EVALUATING = "evaluating", "En evaluación"
        QUOTED = "quoted", "Cotización enviada"
        APPROVED = "approved", "Aprobada"
        CLOSED = "closed", "Finalizada"
        REJECTED = "rejected", "No concretada"

    public_id = models.UUIDField(
        "identificador público",
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    reference_code = models.CharField(
        "código de solicitud",
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )

    full_name = models.CharField(
        "nombre completo",
        max_length=180,
    )

    phone = models.CharField(
        "teléfono o WhatsApp",
        max_length=20,
        validators=[phone_validator],
    )

    email = models.EmailField(
        "correo electrónico",
        blank=True,
    )

    preferred_contact = models.CharField(
        "medio de contacto preferido",
        max_length=20,
        choices=PreferredContact.choices,
        default=PreferredContact.WHATSAPP,
    )

    preferred_time = models.CharField(
        "horario preferido",
        max_length=20,
        choices=PreferredTime.choices,
        default=PreferredTime.ANY,
    )

    service = models.ForeignKey(
        Service,
        verbose_name="servicio solicitado",
        related_name="quote_requests",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    other_service = models.CharField(
        "otro servicio o necesidad",
        max_length=180,
        blank=True,
    )

    project_type = models.CharField(
        "tipo de proyecto",
        max_length=30,
        choices=ProjectType.choices,
        default=ProjectType.RESIDENTIAL,
    )

    district = models.CharField(
        "distrito o ubicación",
        max_length=160,
    )

    address_reference = models.CharField(
        "referencia de la ubicación",
        max_length=250,
        blank=True,
    )

    budget_range = models.CharField(
        "presupuesto referencial",
        max_length=30,
        choices=BudgetRange.choices,
        blank=True,
    )

    desired_date = models.DateField(
        "fecha deseada para el trabajo",
        blank=True,
        null=True,
    )

    description = models.TextField(
        "descripción del proyecto",
        help_text=(
            "Describe las medidas aproximadas, el problema actual "
            "y el resultado que deseas obtener."
        ),
    )

    privacy_consent = models.BooleanField(
        "aceptación del uso de datos",
        default=False,
    )

    status = models.CharField(
        "estado de la solicitud",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    internal_notes = models.TextField(
        "notas internas",
        blank=True,
        help_text=(
            "Este contenido solo será visible para los "
            "administradores."
        ),
    )

    source_url = models.URLField(
        "página de origen",
        max_length=500,
        blank=True,
    )

    created_at = models.DateTimeField(
        "fecha de recepción",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "última actualización",
        auto_now=True,
    )

    class Meta:
        ordering = (
            "-created_at",
        )
        verbose_name = "solicitud de cotización"
        verbose_name_plural = "solicitudes de cotización"

    def __str__(self):
        """Representa la solicitud en el administrador."""

        reference = self.reference_code or "Sin código"

        return f"{reference} — {self.full_name}"

    def save(self, *args, **kwargs):
        """Genera el código de referencia después del primer guardado."""

        super().save(*args, **kwargs)

        if not self.reference_code:
            reference_code = (
                f"MS-{self.created_at:%Y%m%d}-{self.pk:05d}"
            )

            type(self).objects.filter(
                pk=self.pk,
            ).update(
                reference_code=reference_code,
            )

            self.reference_code = reference_code

    @property
    def requested_service_name(self):
        """Devuelve el servicio seleccionado o el texto alternativo."""

        if self.service:
            return self.service.name

        return self.other_service or "Servicio no especificado"

    @property
    def phone_digits(self):
        """Devuelve únicamente los números del teléfono."""

        return re.sub(r"\D", "", self.phone)

    @property
    def customer_whatsapp_url(self):
        """Construye el enlace de WhatsApp del cliente."""

        number = self.phone_digits

        if len(number) == 9:
            number = f"51{number}"

        if not number:
            return "#"

        return f"https://wa.me/{number}"


class QuoteAttachment(models.Model):
    """Fotografía adjunta a una solicitud."""

    quote_request = models.ForeignKey(
        QuoteRequest,
        verbose_name="solicitud",
        related_name="attachments",
        on_delete=models.CASCADE,
    )

    image = models.ImageField(
        "fotografía",
        upload_to=quote_attachment_upload_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                ]
            ),
            validate_image_size,
        ],
    )

    caption = models.CharField(
        "descripción de la fotografía",
        max_length=200,
        blank=True,
    )

    created_at = models.DateTimeField(
        "fecha de carga",
        auto_now_add=True,
    )

    class Meta:
        ordering = (
            "created_at",
            "id",
        )
        verbose_name = "fotografía adjunta"
        verbose_name_plural = "fotografías adjuntas"

    def __str__(self):
        """Representa el archivo en el administrador."""

        return f"Fotografía de {self.quote_request.reference_code}"