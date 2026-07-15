"""Pruebas del formulario de cotización."""

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.services.models import Service, ServiceCategory

from .models import QuoteRequest


@override_settings(
    ALLOWED_HOSTS=[
        "testserver",
        "127.0.0.1",
        "localhost",
    ]
)
class QuoteRequestViewsTests(TestCase):
    """Comprueba el registro básico de solicitudes."""

    def setUp(self):
        """Crea un servicio para utilizarlo en las pruebas."""

        category = ServiceCategory.objects.create(
            name="Puertas de prueba",
            slug="puertas-de-prueba",
            display_order=10,
        )

        self.service = Service.objects.create(
            category=category,
            name="Automatización de prueba",
            slug="automatizacion-de-prueba",
            card_description=(
                "Servicio utilizado únicamente para pruebas."
            ),
            display_order=10,
        )

        self.client = Client()

    def test_quote_form_loads(self):
        """El formulario público debe responder correctamente."""

        response = self.client.get(
            reverse("quotes:create"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_valid_request_is_created(self):
        """Un envío válido debe crear una solicitud."""

        response = self.client.post(
            reverse("quotes:create"),
            data={
                "full_name": "Cliente de prueba",
                "phone": "921127836",
                "email": "cliente@example.com",
                "preferred_contact": "whatsapp",
                "preferred_time": "any",
                "service": self.service.pk,
                "other_service": "",
                "project_type": "residential",
                "district": "Huancayo",
                "address_reference": "",
                "budget_range": "undefined",
                "desired_date": "",
                "description": (
                    "Necesito automatizar un portón existente "
                    "en una vivienda ubicada en Huancayo."
                ),
                "privacy_consent": "on",
                "website": "",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            QuoteRequest.objects.count(),
            1,
        )

        quote_request = QuoteRequest.objects.first()

        self.assertTrue(
            quote_request.reference_code.startswith("MS-")
        )

    def test_honeypot_rejects_automatic_submission(self):
        """El campo oculto debe bloquear un envío sospechoso."""

        response = self.client.post(
            reverse("quotes:create"),
            data={
                "full_name": "Robot",
                "phone": "921127836",
                "preferred_contact": "whatsapp",
                "preferred_time": "any",
                "service": self.service.pk,
                "project_type": "residential",
                "district": "Huancayo",
                "description": (
                    "Este texto contiene suficientes caracteres "
                    "para completar la validación."
                ),
                "privacy_consent": "on",
                "website": "sitio-automatico.example",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            QuoteRequest.objects.count(),
            0,
        )

    def test_service_can_be_preselected(self):
        """Un servicio enviado por URL debe quedar seleccionado."""

        response = self.client.get(
            reverse("quotes:create"),
            {
                "servicio": self.service.slug,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context["form"].initial["service"],
            self.service.pk,
        )

        self.assertEqual(
            response.context["selected_service"],
            self.service,
        )

    def test_invalid_service_slug_does_not_break_form(self):
        """Un slug inexistente no debe romper el formulario."""

        response = self.client.get(
            reverse("quotes:create"),
            {
                "servicio": "servicio-que-no-existe",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsNone(
            response.context["selected_service"],
        )