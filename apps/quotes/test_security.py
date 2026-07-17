"""Pruebas de seguridad del formulario de cotización."""

from django.test import (
    Client,
    TestCase,
    override_settings,
)
from django.urls import reverse

from apps.services.models import (
    Service,
    ServiceCategory,
)

from .models import QuoteRequest


@override_settings(
    ALLOWED_HOSTS=[
        "testserver",
        "127.0.0.1",
        "localhost",
    ],
    QUOTE_SUBMISSION_COOLDOWN_SECONDS=60,
)
class QuoteSubmissionSecurityTests(
    TestCase
):
    """Comprueba la protección contra envíos consecutivos."""

    def setUp(self):
        """Prepara un servicio público."""

        category = (
            ServiceCategory.objects.create(
                name="Categoría de seguridad",
                slug="categoria-de-seguridad",
                display_order=10,
            )
        )

        self.service = (
            Service.objects.create(
                category=category,
                name="Servicio de seguridad",
                slug="servicio-de-seguridad",
                card_description=(
                    "Servicio utilizado para "
                    "comprobar la seguridad."
                ),
                display_order=10,
            )
        )

        self.client = Client()

    def get_valid_data(self):
        """Devuelve datos válidos del formulario."""

        return {
            "full_name": "Cliente de seguridad",
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
                "Necesito evaluar un proyecto "
                "para realizar una prueba segura "
                "del formulario de cotización."
            ),
            "privacy_consent": "on",
            "website": "",
        }

    def test_immediate_duplicate_is_rejected(self):
        """Dos envíos inmediatos no deben crear dos solicitudes."""

        first_response = self.client.post(
            reverse(
                "quotes:create",
            ),
            data=self.get_valid_data(),
        )

        self.assertEqual(
            first_response.status_code,
            302,
        )

        second_response = self.client.post(
            reverse(
                "quotes:create",
            ),
            data=self.get_valid_data(),
        )

        self.assertEqual(
            second_response.status_code,
            200,
        )

        self.assertContains(
            second_response,
            (
                "Ya recibimos una solicitud "
                "hace unos segundos."
            ),
        )

        self.assertEqual(
            QuoteRequest.objects.count(),
            1,
        )