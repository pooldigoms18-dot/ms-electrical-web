"""Pruebas del contenido comercial público."""

from django.test import (
    Client,
    TestCase,
    override_settings,
)
from django.urls import reverse

from apps.core.models import GlobalFAQ


@override_settings(
    ALLOWED_HOSTS=[
        "testserver",
        "127.0.0.1",
        "localhost",
    ],
    SITE_URL="https://example.com",
)
class CommercialContentTests(TestCase):
    """Comprueba las preguntas frecuentes públicas."""

    def setUp(self):
        """Prepara preguntas frecuentes de prueba."""

        self.client = Client()

        self.home_faq = GlobalFAQ.objects.create(
            question="¿Pregunta visible en portada?",
            answer="Respuesta visible en portada.",
            display_order=10,
            show_on_home=True,
            is_active=True,
        )

        self.regular_faq = GlobalFAQ.objects.create(
            question="¿Pregunta visible únicamente en FAQ?",
            answer="Respuesta de la página completa.",
            display_order=20,
            show_on_home=False,
            is_active=True,
        )

        self.inactive_faq = GlobalFAQ.objects.create(
            question="¿Pregunta no publicada?",
            answer="Esta respuesta no debe mostrarse.",
            display_order=30,
            show_on_home=True,
            is_active=False,
        )

    def test_home_shows_featured_active_faq(self):
        """La portada debe mostrar preguntas destacadas activas."""

        response = self.client.get(
            reverse("core:home"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.home_faq.question,
        )

        self.assertNotContains(
            response,
            self.inactive_faq.question,
        )

    def test_faq_page_shows_active_questions(self):
        """La página FAQ debe mostrar preguntas publicadas."""

        response = self.client.get(
            reverse("core:faq"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.home_faq.question,
        )

        self.assertContains(
            response,
            self.regular_faq.question,
        )

    def test_faq_page_hides_inactive_questions(self):
        """Las preguntas inactivas no deben publicarse."""

        response = self.client.get(
            reverse("core:faq"),
        )

        self.assertNotContains(
            response,
            self.inactive_faq.question,
        )