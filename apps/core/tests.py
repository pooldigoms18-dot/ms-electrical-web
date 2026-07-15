"""Pruebas técnicas de las páginas principales y SEO."""

from django.test import (
    Client,
    TestCase,
    override_settings,
)


@override_settings(
    ALLOWED_HOSTS=[
        "testserver",
        "127.0.0.1",
        "localhost",
    ],
    SITE_URL="https://example.com",
)
class SeoTechnicalTests(TestCase):
    """Comprueba elementos fundamentales para buscadores."""

    def setUp(self):
        """Prepara el cliente de pruebas."""

        self.client = Client()

    def test_home_contains_canonical_url(self):
        """La portada debe declarar una URL canónica."""

        response = self.client.get("/")

        self.assertEqual(
            response.status_code,
            200,
        )

        html = response.content.decode()

        self.assertIn(
            'rel="canonical"',
            html,
        )

        self.assertIn(
            "https://example.com/",
            html,
        )

    @override_settings(DEBUG=False)
    def test_robots_txt_is_available(self):
        """robots.txt debe estar disponible."""

        response = self.client.get(
            "/robots.txt",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response["Content-Type"],
            "text/plain",
        )

        content = response.content.decode()

        self.assertIn(
            "User-agent: *",
            content,
        )

        self.assertIn(
            "Disallow: /admin/",
            content,
        )

        self.assertIn(
            "https://example.com/sitemap.xml",
            content,
        )

    def test_sitemap_is_available(self):
        """El mapa del sitio debe responder correctamente."""

        response = self.client.get(
            "/sitemap.xml",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        content = response.content.decode()

        self.assertIn(
            "/servicios/",
            content,
        )

        self.assertIn(
            "/proyectos/",
            content,
        )