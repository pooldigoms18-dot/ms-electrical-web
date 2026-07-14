"""Vistas públicas de las páginas principales."""

from django.shortcuts import render


def home(request):
    """Muestra la página de inicio provisional de MS Electrical."""

    services = [
        {
            "number": "01",
            "title": "Puertas metálicas",
            "description": (
                "Diseño, fabricación e instalación de puertas "
                "metálicas hechas a medida."
            ),
        },
        {
            "number": "02",
            "title": "Automatización de portones",
            "description": (
                "Sistemas de apertura automática para mejorar "
                "la comodidad y el control del acceso."
            ),
        },
        {
            "number": "03",
            "title": "Puertas seccionales",
            "description": (
                "Soluciones modernas que aprovechan mejor "
                "el espacio disponible en la cochera."
            ),
        },
        {
            "number": "04",
            "title": "Instalaciones eléctricas",
            "description": (
                "Instalaciones, ampliaciones y revisiones "
                "eléctricas para viviendas y negocios."
            ),
        },
        {
            "number": "05",
            "title": "Domótica y acceso inteligente",
            "description": (
                "Control de iluminación, cerraduras, accesos "
                "y funciones importantes desde el celular."
            ),
        },
        {
            "number": "06",
            "title": "Impresión 3D",
            "description": (
                "Diseño y fabricación de prototipos, soportes, "
                "adaptadores y piezas personalizadas."
            ),
        },
    ]

    context = {
        "services": services,
    }

    return render(request, "core/home.html", context)