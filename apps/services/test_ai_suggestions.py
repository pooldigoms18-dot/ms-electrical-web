"""Pruebas del asistente de IA para servicios (sin llamar a internet)."""

import json
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .ai_suggestions import AISuggestionError, clean_suggestion
from .models import ServiceCategory


FAKE_RESPONSE = {
    "category": "Electricidad y tecnología",
    "icon_key": "electricity",
    "card_description": "Preparamos el expediente técnico de tu banco de medidores.",
    "introduction": "Párrafo uno.\n\nPárrafo dos.",
    "whatsapp_message": "Hola, quiero información del expediente de banco de medidores.",
    "seo_title": "Expediente de banco de medidores en Huancayo | MS Electrical " * 3,
    "seo_description": "Descripción SEO.",
    "benefits": [{"title": "Trámite ordenado", "description": "Detalle."}] * 6,
    "features": [{"title": "Planos", "description": "Planos eléctricos."}],
    "process_steps": [
        {"title": "Visita", "description": "Revisamos el predio."},
        {"title": "", "description": "Sin título: se descarta."},
    ],
    "faqs": [{"question": "¿Cuánto demora?", "answer": "Depende del caso."}],
}


class CleanSuggestionTests(TestCase):
    def test_respects_limits_and_choices(self):
        data = clean_suggestion(
            json.dumps(FAKE_RESPONSE),
            ["Electricidad y tecnología"],
            ["electricity"],
        )
        self.assertEqual(data["category"], "Electricidad y tecnología")
        self.assertLessEqual(len(data["seo_title"]), 70)
        self.assertEqual(len(data["benefits"]), 4)
        self.assertEqual(len(data["process_steps"]), 1)

    def test_unknown_category_and_icon_are_dropped(self):
        data = clean_suggestion(
            json.dumps(FAKE_RESPONSE), ["Otra"], ["door"],
        )
        self.assertEqual(data["category"], "")
        self.assertEqual(data["icon_key"], "")

    def test_invalid_json_raises(self):
        with self.assertRaises(AISuggestionError):
            clean_suggestion("no es json", [], [])


class RetryTests(TestCase):
    @mock.patch("apps.services.ai_suggestions.time.sleep")
    @mock.patch("apps.services.ai_suggestions._env", return_value="clave")
    @mock.patch("apps.services.ai_suggestions.urllib.request.urlopen")
    def test_retries_once_after_503(self, urlopen, _env, _sleep):
        import io
        import urllib.error
        from .ai_suggestions import call_gemini

        ok = mock.MagicMock()
        ok.__enter__.return_value.read.return_value = json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "{}"}]}}]}
        ).encode()
        urlopen.side_effect = [
            urllib.error.HTTPError("u", 503, "busy", {}, io.BytesIO()),
            ok,
        ]
        self.assertEqual(call_gemini("s", "u"), "{}")
        self.assertEqual(urlopen.call_count, 2)

    @mock.patch("apps.services.ai_suggestions.time.sleep")
    @mock.patch("apps.services.ai_suggestions._env", return_value="clave")
    @mock.patch("apps.services.ai_suggestions.urllib.request.urlopen")
    def test_gives_up_after_two_attempts(self, urlopen, _env, _sleep):
        import io
        import urllib.error
        from .ai_suggestions import call_gemini

        urlopen.side_effect = urllib.error.HTTPError(
            "u", 503, "busy", {}, io.BytesIO(),
        )
        with self.assertRaisesMessage(AISuggestionError, "saturada"):
            call_gemini("s", "u")
        self.assertEqual(urlopen.call_count, 2)


class AISuggestViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.category = ServiceCategory.objects.create(
            name="Electricidad y tecnología",
        )
        self.admin = get_user_model().objects.create_superuser(
            "admin", "admin@example.com", "clave-de-prueba-123",
        )
        self.url = reverse("admin:services_service_ai_suggest")

    def post(self, name):
        return self.client.post(
            self.url,
            data=json.dumps({"name": name}),
            content_type="application/json",
        )

    def test_requires_staff_login(self):
        response = self.post("Expediente de banco de medidores")
        self.assertEqual(response.status_code, 302)

    @mock.patch.dict("os.environ", {"GEMINI_API_KEY": "clave-falsa"})
    @mock.patch("apps.services.ai_suggestions.call_gemini")
    def test_returns_suggestion_with_category_id(self, call_gemini):
        call_gemini.return_value = json.dumps(FAKE_RESPONSE)
        self.client.force_login(self.admin)

        response = self.post("Expediente de banco de medidores")

        self.assertEqual(response.status_code, 200)
        suggestion = response.json()["suggestion"]
        self.assertEqual(suggestion["category_id"], self.category.pk)
        self.assertIn("banco de medidores", suggestion["card_description"])
        prompt = call_gemini.call_args.args[1]
        self.assertIn("Expediente de banco de medidores", prompt)

    @mock.patch("apps.services.ai_suggestions._env", return_value="")
    def test_missing_key_gives_clear_message(self, _env):
        self.client.force_login(self.admin)
        response = self.post("Expediente de banco de medidores")
        self.assertEqual(response.status_code, 400)
        self.assertIn("GEMINI_API_KEY", response.json()["error"])

    def test_short_name_rejected(self):
        self.client.force_login(self.admin)
        response = self.post("ab")
        self.assertEqual(response.status_code, 400)

    @mock.patch("apps.services.ai_suggestions.call_gemini")
    def test_rate_limit(self, call_gemini):
        call_gemini.return_value = json.dumps(FAKE_RESPONSE)
        self.client.force_login(self.admin)
        for _ in range(6):
            self.post("Expediente de banco de medidores")
        response = self.post("Expediente de banco de medidores")
        self.assertEqual(response.status_code, 429)

    def test_add_form_loads_assistant_script(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("admin:services_service_add"),
        )
        self.assertContains(response, "services/admin/ai-suggest.js")
