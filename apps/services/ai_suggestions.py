"""Sugerencias de contenido con IA para el administrador de servicios.

Parte del nombre de un servicio (por ejemplo, "Expediente de banco de
medidores") y propone el resto de los campos: descripciones, SEO,
mensaje de WhatsApp, beneficios, características, proceso y preguntas
frecuentes. Las fotos siempre las carga una persona.

Proveedor: API de Google Gemini (nivel gratuito de Google AI Studio).
La clave se lee de la variable de entorno GEMINI_API_KEY y nunca se
envía al navegador.
"""

import json
import logging
import os
import time
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent"
)
# Flash-Lite: rápido (pocos segundos) y disponible en el nivel gratuito.
# El servidor corta las peticiones a los 60 s (nginx y gunicorn), así
# que dos intentos de 20 s como máximo caben con margen.
DEFAULT_MODEL = "gemini-flash-lite-latest"
REQUEST_TIMEOUT_SECONDS = 20
RETRYABLE_CODES = (429, 500, 502, 503, 504)
RETRY_DELAY_SECONDS = 2

# Límites alineados con los max_length de los modelos.
LIMITS = {
    "card_description": 260,
    "seo_title": 70,
    "seo_description": 170,
    "whatsapp_message": 400,
    "icon_key": 50,
    "benefit_title": 140,
    "feature_title": 140,
    "feature_description": 300,
    "step_title": 140,
    "faq_question": 240,
}

MAX_ITEMS = {
    "benefits": 4,
    "features": 6,
    "process_steps": 5,
    "faqs": 5,
}


class AISuggestionError(Exception):
    """Error presentable al usuario del administrador."""


def _env(name):
    """Lee una variable del entorno o, en local, del archivo .env.

    En el servidor, systemd entrega las variables (EnvironmentFile) y
    siempre tienen prioridad. En la PC de desarrollo el proyecto no
    carga el .env automáticamente, así que se consulta aquí.
    """

    value = os.getenv(name, "").strip()
    if value:
        return value

    try:
        from django.conf import settings
        from dotenv import dotenv_values
    except ImportError:
        return ""

    env_file = getattr(settings, "BASE_DIR", None)
    if env_file is None:
        return ""

    values = dotenv_values(env_file / ".env")
    return (values.get(name) or "").strip()


def is_configured():
    """Indica si hay una clave de API disponible."""

    return bool(_env("GEMINI_API_KEY"))


def build_prompt(service_name, categories, icon_keys, company):
    """Construye las instrucciones para el modelo."""

    system = (
        "Eres redactor comercial y técnico de MS Electrical, una empresa "
        "de Huancayo (Junín, Perú) que diseña, fabrica e instala puertas "
        "y accesos automáticos, instalaciones eléctricas, puestas a "
        "tierra, domótica e impresión 3D. Escribes en español de Perú, "
        "claro, profesional y cercano, orientado a que el cliente pida "
        "una cotización.\n"
        "Reglas estrictas:\n"
        "- No inventes precios, plazos exactos, cifras, certificaciones, "
        "marcas ni clientes.\n"
        "- Si mencionas normativa peruana (por ejemplo, el Código "
        "Nacional de Electricidad o requisitos de la distribuidora "
        "eléctrica), hazlo de forma general y sin citar artículos.\n"
        "- La garantía, cobertura y formas de pago solo pueden salir de "
        "los datos de la empresa que se te dan.\n"
        "- Respeta los límites de caracteres indicados.\n"
        "- Responde únicamente con el JSON pedido."
    )

    company_lines = "\n".join(
        f"- {label}: {value}"
        for label, value in company.items()
        if value
    )

    user = (
        f"Nombre del nuevo servicio: \"{service_name}\"\n\n"
        f"Datos de la empresa:\n{company_lines or '- (sin datos)'}\n\n"
        "Categorías existentes (elige la más adecuada, escrita "
        f"exactamente igual): {json.dumps(categories, ensure_ascii=False)}\n"
        "Iconos disponibles (elige uno o deja vacío): "
        f"{json.dumps(icon_keys, ensure_ascii=False)}\n\n"
        "Devuelve un objeto JSON con estas claves:\n"
        "{\n"
        '  "category": "una de las categorías existentes",\n'
        '  "icon_key": "uno de los iconos disponibles o \\"\\"",\n'
        f'  "card_description": "1-2 frases, máx. {LIMITS["card_description"]} caracteres",\n'
        '  "introduction": "2 o 3 párrafos separados por una línea en '
        'blanco: qué es, para quién y cómo lo resuelve MS Electrical",\n'
        f'  "whatsapp_message": "mensaje inicial del cliente, máx. {LIMITS["whatsapp_message"]}",\n'
        f'  "seo_title": "máx. {LIMITS["seo_title"]} caracteres, incluye Huancayo",\n'
        f'  "seo_description": "máx. {LIMITS["seo_description"]} caracteres",\n'
        f'  "benefits": [{{"title": "...", "description": "..."}}] (3 a {MAX_ITEMS["benefits"]}),\n'
        f'  "features": [{{"title": "...", "description": "máx. {LIMITS["feature_description"]}"}}] (3 a {MAX_ITEMS["features"]}),\n'
        f'  "process_steps": [{{"title": "...", "description": "..."}}] (3 a {MAX_ITEMS["process_steps"]}, en orden),\n'
        f'  "faqs": [{{"question": "...", "answer": "..."}}] (3 a {MAX_ITEMS["faqs"]})\n'
        "}"
    )

    return system, user


def call_gemini(system, user):
    """Llama a la API de Gemini y devuelve el texto de la respuesta."""

    api_key = _env("GEMINI_API_KEY")

    if not api_key:
        raise AISuggestionError(
            "La IA no está configurada. Falta GEMINI_API_KEY en el "
            "archivo de entorno del servidor."
        )

    model = _env("GEMINI_MODEL") or DEFAULT_MODEL
    # El nivel gratuito a veces responde 503 (modelo saturado) o
    # tarda demasiado: se reintenta una vez.
    attempts = [model, model]

    payload = json.dumps({
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.6,
        },
    }).encode("utf-8")

    body = None
    for attempt, model in enumerate(attempts):
        request = urllib.request.Request(
            GEMINI_ENDPOINT.format(model=model),
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request,
                timeout=REQUEST_TIMEOUT_SECONDS,
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as error:
            logger.warning(
                "Gemini (%s) respondió HTTP %s", model, error.code,
            )
            if error.code in RETRYABLE_CODES and attempt < len(attempts) - 1:
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            if error.code == 429:
                raise AISuggestionError(
                    "Se alcanzó el límite gratuito de la IA. Intenta de "
                    "nuevo en un minuto."
                ) from error
            if error.code in (500, 502, 503, 504):
                raise AISuggestionError(
                    "La IA de Google está saturada en este momento. "
                    "Intenta de nuevo en unos segundos."
                ) from error
            if error.code in (400, 401, 403):
                raise AISuggestionError(
                    "Google rechazó la clave de la IA. Revisa "
                    "GEMINI_API_KEY."
                ) from error
            raise AISuggestionError(
                f"La IA respondió con un error ({error.code})."
            ) from error
        except (urllib.error.URLError, TimeoutError) as error:
            logger.warning("No se pudo contactar a Gemini: %s", error)
            if attempt < len(attempts) - 1:
                continue
            raise AISuggestionError(
                "No se pudo contactar al servicio de IA."
            ) from error

    try:
        return body["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as error:
        raise AISuggestionError(
            "La IA no devolvió contenido. Prueba con otro nombre."
        ) from error


def _text(value, limit=None):
    """Normaliza un valor a texto y respeta el límite de caracteres."""

    if not isinstance(value, str):
        return ""

    value = value.strip()

    if limit and len(value) > limit:
        cut = value[: limit - 1].rsplit(" ", 1)[0]
        value = cut.rstrip(",.;: ") + "…"

    return value


def _items(raw, key_a, key_b, max_items, limit_a=None, limit_b=None):
    """Valida una lista de pares (título/descripción o pregunta/respuesta)."""

    if not isinstance(raw, list):
        return []

    cleaned = []

    for item in raw[:max_items]:
        if not isinstance(item, dict):
            continue
        a = _text(item.get(key_a), limit_a)
        b = _text(item.get(key_b), limit_b)
        if a and b:
            cleaned.append({key_a: a, key_b: b})

    return cleaned


def clean_suggestion(raw_text, categories, icon_keys):
    """Convierte la respuesta del modelo en datos seguros para el formulario."""

    try:
        data = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as error:
        raise AISuggestionError(
            "La respuesta de la IA no tuvo el formato esperado."
        ) from error

    if not isinstance(data, dict):
        raise AISuggestionError(
            "La respuesta de la IA no tuvo el formato esperado."
        )

    category = _text(data.get("category"))
    icon_key = _text(data.get("icon_key"), LIMITS["icon_key"])

    return {
        "category": category if category in categories else "",
        "icon_key": icon_key if icon_key in icon_keys else "",
        "card_description": _text(
            data.get("card_description"), LIMITS["card_description"]
        ),
        "introduction": _text(data.get("introduction")),
        "whatsapp_message": _text(
            data.get("whatsapp_message"), LIMITS["whatsapp_message"]
        ),
        "seo_title": _text(data.get("seo_title"), LIMITS["seo_title"]),
        "seo_description": _text(
            data.get("seo_description"), LIMITS["seo_description"]
        ),
        "benefits": _items(
            data.get("benefits"), "title", "description",
            MAX_ITEMS["benefits"], LIMITS["benefit_title"],
        ),
        "features": _items(
            data.get("features"), "title", "description",
            MAX_ITEMS["features"], LIMITS["feature_title"],
            LIMITS["feature_description"],
        ),
        "process_steps": _items(
            data.get("process_steps"), "title", "description",
            MAX_ITEMS["process_steps"], LIMITS["step_title"],
        ),
        "faqs": _items(
            data.get("faqs"), "question", "answer",
            MAX_ITEMS["faqs"], LIMITS["faq_question"],
        ),
    }


def suggest_service(service_name, categories, icon_keys, company):
    """Punto de entrada: devuelve los campos sugeridos para un servicio."""

    service_name = _text(service_name, 160)

    if len(service_name) < 3:
        raise AISuggestionError(
            "Escribe primero el nombre del servicio."
        )

    system, user = build_prompt(
        service_name, categories, icon_keys, company,
    )
    raw_text = call_gemini(system, user)

    return clean_suggestion(raw_text, categories, icon_keys)
