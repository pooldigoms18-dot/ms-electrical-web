"""Pruebas de las utilidades SEO locales."""

import json
from types import SimpleNamespace

from django.test import (
    RequestFactory,
    SimpleTestCase,
    override_settings,
)

from apps.core.seo import (
    build_breadcrumb_schema,
    build_service_schema,
    normalize_peru_phone,
)


@override_settings(
    SITE_URL="https://example.com",
)
class LocalSeoSchemaTests(SimpleTestCase):
    """Comprueba los datos estructurados principales."""

    def setUp(self):
        """Prepara una solicitud de prueba."""

        self.request = RequestFactory().get(
            "/servicios/automatizacion-de-prueba/",
        )

    def test_peru_phone_is_normalized(self):
        """Un móvil peruano debe incluir código de país."""

        self.assertEqual(
            normalize_peru_phone(
                "921 127 836"
            ),
            "+51921127836",
        )

    def test_breadcrumb_schema_is_valid_json(self):
        """Los breadcrumbs deben generar JSON válido."""

        schema_json = build_breadcrumb_schema(
            self.request,
            [
                (
                    "Inicio",
                    "/",
                ),
                (
                    "Servicios",
                    "/servicios/",
                ),
            ],
        )

        schema = json.loads(
            str(schema_json)
        )

        self.assertEqual(
            schema["@type"],
            "BreadcrumbList",
        )

        self.assertEqual(
            len(
                schema["itemListElement"]
            ),
            2,
        )

    def test_service_schema_is_valid_json(self):
        """Un servicio debe generar datos estructurados."""

        category = SimpleNamespace(
            name="Puertas y accesos",
        )

        service = SimpleNamespace(
            slug="automatizacion-de-prueba",
            name="Automatización de prueba",
            card_description=(
                "Automatización de accesos "
                "para proyectos de prueba."
            ),
            seo_description="",
            category=category,
        )

        schema_json = build_service_schema(
            self.request,
            service,
        )

        schema = json.loads(
            str(schema_json)
        )

        self.assertEqual(
            schema["@type"],
            "Service",
        )

        self.assertEqual(
            schema["name"],
            "Automatización de prueba",
        )

        self.assertEqual(
            schema["provider"]["@id"],
            "https://example.com/#business",
        )