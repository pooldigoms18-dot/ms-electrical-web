"""Formularios públicos para solicitudes de cotización."""

from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from apps.services.models import Service

from .models import QuoteRequest


class MultipleImageInput(forms.ClearableFileInput):
    """Permite seleccionar varias fotografías."""

    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """Valida cada imagen seleccionada por el usuario."""

    widget = MultipleImageInput

    def clean(self, data, initial=None):
        """Procesa una o varias imágenes."""

        if not data:
            return []

        single_image_clean = super().clean

        if isinstance(data, (list, tuple)):
            return [
                single_image_clean(image, initial)
                for image in data
            ]

        return [
            single_image_clean(data, initial)
        ]


class QuoteRequestForm(forms.ModelForm):
    """Formulario público de solicitud de cotización."""

    photos = MultipleImageField(
        label="Fotografías del proyecto",
        required=False,
        help_text=(
            "Puedes adjuntar hasta cinco fotografías en formato "
            "JPG, PNG o WEBP. Máximo 8 MB por imagen."
        ),
        widget=MultipleImageInput(
            attrs={
                "accept": "image/jpeg,image/png,image/webp",
            }
        ),
    )

    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
        label="",
    )

    class Meta:
        model = QuoteRequest

        fields = (
            "full_name",
            "phone",
            "email",
            "preferred_contact",
            "preferred_time",
            "service",
            "other_service",
            "project_type",
            "district",
            "address_reference",
            "budget_range",
            "desired_date",
            "description",
            "privacy_consent",
        )

        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "placeholder": "Nombres y apellidos",
                    "autocomplete": "name",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Ejemplo: 921 127 836",
                    "autocomplete": "tel",
                    "inputmode": "tel",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "correo@ejemplo.com",
                    "autocomplete": "email",
                }
            ),
            "other_service": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Escribe aquí cuando tu necesidad "
                        "no aparezca en la lista"
                    ),
                }
            ),
            "district": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Ejemplo: El Tambo, Huancayo"
                    ),
                    "autocomplete": "address-level2",
                }
            ),
            "address_reference": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Referencia aproximada. No es obligatorio "
                        "colocar una dirección exacta."
                    ),
                }
            ),
            "desired_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 7,
                    "placeholder": (
                        "Describe qué necesitas, medidas aproximadas, "
                        "estado actual y cualquier detalle importante."
                    ),
                }
            ),
            "privacy_consent": forms.CheckboxInput(),
        }

        labels = {
            "privacy_consent": (
                "Autorizo el uso de estos datos para atender "
                "mi solicitud de cotización."
            ),
        }

    def __init__(self, *args, **kwargs):
        """Limita el selector a servicios actualmente publicados."""

        super().__init__(*args, **kwargs)

        self.fields["service"].queryset = (
            Service.objects
            .filter(
                is_active=True,
                category__is_active=True,
            )
            .select_related("category")
            .order_by(
                "category__display_order",
                "display_order",
                "name",
            )
        )

        self.fields["service"].required = False
        self.fields["service"].empty_label = (
            "Selecciona un servicio"
        )

        self.fields["other_service"].required = False

    def clean_website(self):
        """Rechaza envíos automáticos que completen el campo oculto."""

        value = self.cleaned_data.get("website", "").strip()

        if value:
            raise ValidationError(
                "No fue posible procesar la solicitud."
            )

        return value

    def clean_desired_date(self):
        """Impide seleccionar fechas anteriores al día actual."""

        desired_date = self.cleaned_data.get("desired_date")

        if desired_date and desired_date < date.today():
            raise ValidationError(
                "La fecha deseada no puede estar en el pasado."
            )

        return desired_date

    def clean_photos(self):
        """Valida cantidad y tamaño de las fotografías."""

        photos = self.cleaned_data.get("photos", [])

        if len(photos) > 5:
            raise ValidationError(
                "Puedes adjuntar como máximo cinco fotografías."
            )

        maximum_size = 8 * 1024 * 1024

        for photo in photos:
            if photo.size > maximum_size:
                raise ValidationError(
                    f"La fotografía «{photo.name}» supera los 8 MB."
                )

        return photos

    def clean(self):
        """Valida los datos relacionados entre sí."""

        cleaned_data = super().clean()

        service = cleaned_data.get("service")
        other_service = cleaned_data.get(
            "other_service",
            "",
        ).strip()

        description = cleaned_data.get(
            "description",
            "",
        ).strip()

        if not service and not other_service:
            self.add_error(
                "service",
                (
                    "Selecciona un servicio o describe tu necesidad "
                    "en el campo «Otro servicio»."
                ),
            )

        if description and len(description) < 30:
            self.add_error(
                "description",
                (
                    "Describe el proyecto con al menos "
                    "30 caracteres."
                ),
            )

        return cleaned_data