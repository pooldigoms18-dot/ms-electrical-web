"""Pruebas de elementos de conversión y experiencia móvil."""

from django.test import (
    Client,
    TestCase,
    override_settings,
)
from django.urls import reverse


@override_settings(
    ALLOWED_HOSTS=[
        "testserver",
        "127.0.0.1",
        "localhost",
    ],
    SITE_URL="https://example.com",
)
class MobileConversionTests(TestCase):
    """Comprueba los elementos globales de conversión."""

    def setUp(self):
        """Prepara el cliente de pruebas."""

        self.client = Client()

    def test_home_contains_mobile_conversion_bar(self):
        """La portada debe incluir las acciones rápidas móviles."""

        response = self.client.get(
            reverse("core:home"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            'data-mobile-conversion',
        )

        self.assertContains(
            response,
            "Solicitar cotización",
        )

        self.assertContains(
            response,
            "WhatsApp",
        )

    def test_mobile_conversion_script_is_loaded(self):
        """La plantilla debe cargar el comportamiento móvil."""

        response = self.client.get(
            reverse("core:home"),
        )

        self.assertContains(
            response,
            "js/mobile-conversion.js",
        )

    def test_quote_page_keeps_mobile_actions(self):
        """La cotización debe conservar acceso rápido a WhatsApp."""

        response = self.client.get(
            reverse("quotes:create"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            'aria-label="Acciones rápidas"',
        )