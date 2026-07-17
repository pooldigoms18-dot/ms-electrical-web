"""Pruebas de páginas de error y seguridad CSRF."""

from django.core.exceptions import (
    PermissionDenied,
)
from django.test import (
    Client,
    RequestFactory,
    TestCase,
    override_settings,
)
from django.urls import reverse
from django.views import defaults


@override_settings(
    DEBUG=False,
    ALLOWED_HOSTS=[
        "testserver",
        "127.0.0.1",
        "localhost",
    ],
)
class ErrorHandlingTests(TestCase):
    """Comprueba las respuestas de error públicas."""

    def setUp(self):
        """Prepara clientes y solicitudes."""

        self.client = Client()

        self.request_factory = (
            RequestFactory()
        )

    def test_404_page_is_customized(self):
        """Una dirección inexistente debe usar nuestra página 404."""

        response = self.client.get(
            "/esta-ruta-no-existe/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertContains(
            response,
            "Página no encontrada.",
            status_code=404,
        )

    def test_400_template_is_available(self):
        """La página 400 debe poder renderizarse."""

        request = self.request_factory.get(
            "/solicitud-no-valida/"
        )

        response = defaults.bad_request(
            request,
            Exception(
                "Solicitud de prueba"
            ),
        )

        self.assertContains(
            response,
            "No pudimos procesar la solicitud.",
            status_code=400,
        )

    def test_403_template_is_available(self):
        """La página 403 debe poder renderizarse."""

        request = self.request_factory.get(
            "/recurso-protegido/"
        )

        response = (
            defaults.permission_denied(
                request,
                PermissionDenied(),
            )
        )

        self.assertContains(
            response,
            "No tienes acceso a esta página.",
            status_code=403,
        )

    def test_500_template_is_available(self):
        """La página 500 debe poder renderizarse sin contexto."""

        request = self.request_factory.get(
            "/error-interno/"
        )

        response = defaults.server_error(
            request,
        )

        self.assertContains(
            response,
            "Tuvimos un problema inesperado.",
            status_code=500,
        )

    def test_csrf_failure_uses_custom_page(self):
        """Una solicitud sin token CSRF debe usar la página segura."""

        csrf_client = Client(
            enforce_csrf_checks=True,
        )

        response = csrf_client.post(
            reverse(
                "quotes:create",
            ),
            data={
                "full_name": (
                    "Solicitud sin CSRF"
                ),
            },
        )

        self.assertContains(
            response,
            "No pudimos validar esta solicitud.",
            status_code=403,
        )