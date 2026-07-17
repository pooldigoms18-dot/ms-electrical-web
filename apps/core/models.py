"""Modelos generales del sitio de MS Electrical."""

import re

from django.core.validators import RegexValidator
from django.db import models


ruc_validator = RegexValidator(
    regex=r"^\d{11}$",
    message="El RUC debe contener exactamente 11 números.",
)

whatsapp_validator = RegexValidator(
    regex=r"^\d{9,15}$",
    message=(
        "El WhatsApp debe contener solamente números e incluir "
        "el código de país. Ejemplo: 51921127836."
    ),
)


class CompanyProfile(models.Model):
    """Información empresarial que se mostrará en el sitio web."""

    commercial_name = models.CharField(
        "nombre comercial",
        max_length=120,
        default="MS Electrical",
    )

    logo = models.ImageField(
        "logo de la empresa",
        upload_to="company/branding/",
        blank=True,
        help_text=(
            "Logo principal utilizado en la cabecera "
            "y el pie de página del sitio."
        ),
    )

    logo_alt_text = models.CharField(
        "texto alternativo del logo",
        max_length=150,
        blank=True,
        default="Logo de MS Electrical",
        help_text=(
            "Descripción breve del logo para accesibilidad."
        ),
    )

    legal_name = models.CharField(
        "razón social",
        max_length=180,
        default="MS Electrical",
        help_text=(
            "Este dato deberá reemplazarse si la razón social legal "
            "es diferente al nombre comercial."
        ),
    )

    ruc = models.CharField(
        "RUC",
        max_length=11,
        validators=[ruc_validator],
        default="10754525636",
    )

    responsible_name = models.CharField(
        "responsable",
        max_length=180,
        default="Pool Diego Medina Socualaya",
    )

    tagline = models.CharField(
        "eslogan",
        max_length=180,
        default="Seguridad, tecnología y diseño en cada acceso.",
    )

    hero_description = models.TextField(
        "descripción principal",
        default=(
            "Diseñamos, fabricamos e instalamos soluciones para "
            "viviendas, negocios y proyectos en Huancayo."
        ),
    )

    history = models.TextField(
        "historia de la empresa",
        blank=True,
        help_text=(
            "La historia definitiva se completará cuando se valide "
            "el origen y evolución de MS Electrical."
        ),
    )

    founded_year = models.PositiveSmallIntegerField(
        "año de inicio",
        default=2023,
    )

    whatsapp = models.CharField(
        "WhatsApp con código de país",
        max_length=15,
        validators=[whatsapp_validator],
        default="51921127836",
        help_text="Ejemplo para Perú: 51921127836.",
    )

    email = models.EmailField(
        "correo electrónico",
        default="pooldigoms18@gmail.com",
    )

    business_hours = models.CharField(
        "horario de atención",
        max_length=180,
        default="8:00 a. m. a 6:00 p. m.",
    )

    response_time = models.CharField(
        "tiempo estimado de respuesta",
        max_length=180,
        default="Hasta 8 horas dentro del horario de atención.",
    )

    coverage = models.TextField(
        "zona de atención",
        default="Huancayo, El Tambo, Chilca y Chupaca.",
    )

    warranty = models.TextField(
        "condiciones generales de garantía",
        default=(
            "Hasta un año de garantía, según el servicio, los equipos "
            "y las condiciones indicadas en la cotización."
        ),
    )

    maintenance = models.TextField(
        "mantenimiento",
        default=(
            "El seguimiento y mantenimiento se define de acuerdo "
            "con el servicio y las condiciones de la cotización."
        ),
    )

    payment_methods = models.CharField(
        "medios de pago",
        max_length=250,
        default="Yape, Plin, transferencia bancaria y Visa.",
    )

    city = models.CharField(
        "ciudad",
        max_length=100,
        default="Huancayo",
    )

    region = models.CharField(
        "región",
        max_length=100,
        default="Junín",
    )

    country = models.CharField(
        "país",
        max_length=100,
        default="Perú",
    )
    public_address = models.CharField(
        "dirección pública",
        max_length=255,
        blank=True,
        help_text=(
            "Completar únicamente si esta dirección puede "
            "mostrarse públicamente a los clientes."
        ),
    )

    postal_code = models.CharField(
        "código postal",
        max_length=20,
        blank=True,
    )

    google_maps_url = models.URLField(
        "enlace de Google Maps",
        max_length=500,
        blank=True,
    )

    latitude = models.DecimalField(
        "latitud",
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )

    longitude = models.DecimalField(
        "longitud",
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )

    facebook_url = models.URLField(
        "Facebook",
        blank=True,
        default="https://www.facebook.com/MSElectricaPeru",
    )

    youtube_url = models.URLField(
        "YouTube",
        blank=True,
        default="https://www.youtube.com/@superpool18",
    )

    instagram_url = models.URLField(
        "Instagram",
        blank=True,
    )

    is_active = models.BooleanField(
        "información activa",
        default=True,
    )

    updated_at = models.DateTimeField(
        "última actualización",
        auto_now=True,
    )

    class Meta:
        verbose_name = "información de la empresa"
        verbose_name_plural = "información de la empresa"

    def __str__(self):
        """Representa el registro dentro del administrador."""

        return self.commercial_name

    @property
    def whatsapp_url(self):
        """Devuelve el enlace básico de WhatsApp."""

        number = re.sub(r"\D", "", self.whatsapp)

        if not number:
            return "#"

        return f"https://wa.me/{number}"

    @property
    def whatsapp_display(self):
        """Presenta el número peruano con separación visual."""

        number = re.sub(r"\D", "", self.whatsapp)

        if number.startswith("51") and len(number) == 11:
            number = number[2:]

        if len(number) == 9:
            return f"{number[:3]} {number[3:6]} {number[6:]}"

        return number
class GlobalFAQ(models.Model):
    """Pregunta frecuente general de MS Electrical."""

    question = models.CharField(
        "pregunta",
        max_length=255,
    )

    answer = models.TextField(
        "respuesta",
    )

    display_order = models.PositiveIntegerField(
        "orden de visualización",
        default=0,
    )

    show_on_home = models.BooleanField(
        "mostrar en la portada",
        default=False,
    )

    is_active = models.BooleanField(
        "publicada",
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
        """Configuración administrativa."""

        verbose_name = "pregunta frecuente"
        verbose_name_plural = "preguntas frecuentes"

        ordering = (
            "display_order",
            "question",
        )

    def __str__(self):
        """Representación legible."""

        return self.question