"""Carga inicial del catálogo comercial de MS Electrical."""

from django.core.management.base import BaseCommand

from apps.services.models import Service, ServiceCategory


CATEGORIES = [
    {
        "name": "Puertas y accesos",
        "slug": "puertas-y-accesos",
        "description": (
            "Fabricación, instalación y automatización "
            "de puertas y accesos."
        ),
        "icon_key": "door",
        "display_order": 10,
    },
    {
        "name": "Seguridad inteligente",
        "slug": "seguridad-inteligente",
        "description": (
            "Soluciones para controlar y administrar "
            "el ingreso de personas."
        ),
        "icon_key": "security",
        "display_order": 20,
    },
    {
        "name": "Electricidad y tecnología",
        "slug": "electricidad-y-tecnologia",
        "description": (
            "Instalaciones eléctricas, protección y "
            "automatización de funciones."
        ),
        "icon_key": "electricity",
        "display_order": 30,
    },
    {
        "name": "Fabricación digital",
        "slug": "fabricacion-digital",
        "description": (
            "Diseño de prototipos, adaptadores y piezas "
            "personalizadas mediante impresión 3D."
        ),
        "icon_key": "printer-3d",
        "display_order": 40,
    },
]


SERVICES = [
    {
        "category_slug": "puertas-y-accesos",
        "name": "Puertas metálicas",
        "slug": "puertas-metalicas",
        "card_description": (
            "Diseño, fabricación e instalación de puertas "
            "metálicas hechas a medida."
        ),
        "introduction": (
            "Fabricamos puertas metálicas adaptadas a las medidas, "
            "necesidades de seguridad y estilo de cada propiedad."
        ),
        "icon_key": "metal-door",
        "display_order": 10,
        "is_featured": True,
        "seo_title": "Puertas metálicas a medida en Huancayo",
        "seo_description": (
            "Fabricación e instalación de puertas metálicas "
            "personalizadas para viviendas y negocios en Huancayo."
        ),
    },
    {
        "category_slug": "puertas-y-accesos",
        "name": "Puertas metálicas tipo madera",
        "slug": "puertas-metalicas-tipo-madera",
        "card_description": (
            "Seguridad metálica con una apariencia cálida "
            "y acabados inspirados en madera."
        ),
        "introduction": (
            "Integramos estructuras metálicas y acabados tipo madera "
            "para obtener una puerta resistente y visualmente atractiva."
        ),
        "icon_key": "wood-door",
        "display_order": 20,
        "is_featured": False,
        "seo_title": "Puertas metálicas tipo madera en Huancayo",
        "seo_description": (
            "Puertas metálicas con acabado tipo madera, "
            "fabricadas a medida en Huancayo."
        ),
    },
    {
        "category_slug": "puertas-y-accesos",
        "name": "Puertas seccionales",
        "slug": "puertas-seccionales",
        "card_description": (
            "Puertas de apertura vertical para aprovechar "
            "mejor el espacio de la cochera."
        ),
        "introduction": (
            "Instalamos puertas seccionales residenciales y comerciales "
            "considerando las dimensiones y condiciones del acceso."
        ),
        "icon_key": "sectional-door",
        "display_order": 30,
        "is_featured": True,
        "seo_title": "Puertas seccionales para garaje en Huancayo",
        "seo_description": (
            "Instalación de puertas seccionales y sistemas "
            "automáticos para garajes en Huancayo."
        ),
    },
    {
        "category_slug": "puertas-y-accesos",
        "name": "Automatización de portones",
        "slug": "automatizacion-de-portones",
        "card_description": (
            "Sistemas de apertura automática para mejorar "
            "la comodidad y el control del acceso."
        ),
        "introduction": (
            "Evaluamos el portón, estructura, peso, recorrido y "
            "frecuencia de uso antes de seleccionar la automatización."
        ),
        "icon_key": "gate-motor",
        "display_order": 40,
        "is_featured": True,
        "seo_title": "Automatización de portones en Huancayo",
        "seo_description": (
            "Instalación de motores, controles y sensores "
            "para portones automáticos en Huancayo."
        ),
    },
    {
        "category_slug": "electricidad-y-tecnologia",
        "name": "Instalaciones eléctricas",
        "slug": "instalaciones-electricas",
        "card_description": (
            "Instalaciones, ampliaciones y revisiones eléctricas "
            "para viviendas y negocios."
        ),
        "introduction": (
            "Desarrollamos soluciones eléctricas ordenadas y funcionales "
            "según las necesidades del inmueble y del proyecto."
        ),
        "icon_key": "electric-panel",
        "display_order": 10,
        "is_featured": True,
        "seo_title": "Instalaciones eléctricas en Huancayo",
        "seo_description": (
            "Instalaciones y revisiones eléctricas para "
            "viviendas y negocios en Huancayo."
        ),
    },
    {
        "category_slug": "electricidad-y-tecnologia",
        "name": "Puestas a tierra",
        "slug": "puestas-a-tierra",
        "card_description": (
            "Implementación, revisión y mantenimiento "
            "de sistemas de puesta a tierra."
        ),
        "introduction": (
            "Evaluamos las condiciones del inmueble y desarrollamos "
            "el sistema de acuerdo con el alcance técnico requerido."
        ),
        "icon_key": "grounding",
        "display_order": 20,
        "is_featured": False,
        "seo_title": "Sistemas de puesta a tierra en Huancayo",
        "seo_description": (
            "Instalación, revisión y mantenimiento de "
            "sistemas de puesta a tierra en Huancayo."
        ),
    },
    {
        "category_slug": "electricidad-y-tecnologia",
        "name": "Domótica",
        "slug": "domotica",
        "card_description": (
            "Control de iluminación, accesos y funciones "
            "importantes desde dispositivos inteligentes."
        ),
        "introduction": (
            "Implementamos automatizaciones útiles para viviendas "
            "y negocios, priorizando facilidad de uso y estabilidad."
        ),
        "icon_key": "smart-home",
        "display_order": 30,
        "is_featured": True,
        "seo_title": "Domótica para viviendas y negocios en Huancayo",
        "seo_description": (
            "Automatización de iluminación, accesos y funciones "
            "inteligentes para inmuebles en Huancayo."
        ),
    },
    {
        "category_slug": "seguridad-inteligente",
        "name": "Cerraduras inteligentes",
        "slug": "cerraduras-inteligentes",
        "card_description": (
            "Acceso mediante huella, código, tarjeta, "
            "aplicación o llave de respaldo."
        ),
        "introduction": (
            "Evaluamos la puerta y el uso previsto para seleccionar "
            "una cerradura compatible y correctamente instalada."
        ),
        "icon_key": "smart-lock",
        "display_order": 10,
        "is_featured": False,
        "seo_title": "Cerraduras inteligentes en Huancayo",
        "seo_description": (
            "Instalación de cerraduras inteligentes en "
            "puertas de viviendas, oficinas y negocios."
        ),
    },
    {
        "category_slug": "seguridad-inteligente",
        "name": "Control de acceso",
        "slug": "control-de-acceso",
        "card_description": (
            "Sistemas para administrar el ingreso a viviendas, "
            "negocios, oficinas y condominios."
        ),
        "introduction": (
            "Diseñamos sistemas de control de acceso según usuarios, "
            "tipo de puerta, nivel de control y funcionamiento requerido."
        ),
        "icon_key": "access-control",
        "display_order": 20,
        "is_featured": False,
        "seo_title": "Control de acceso en Huancayo",
        "seo_description": (
            "Sistemas de control de acceso con huella, "
            "tarjeta o código para propiedades en Huancayo."
        ),
    },
    {
        "category_slug": "fabricacion-digital",
        "name": "Impresión 3D",
        "slug": "impresion-3d",
        "card_description": (
            "Diseño y fabricación de prototipos, soportes, "
            "adaptadores y piezas personalizadas."
        ),
        "introduction": (
            "Evaluamos la función, medidas y condiciones de uso "
            "antes de diseñar o reproducir una pieza."
        ),
        "icon_key": "printer-3d",
        "display_order": 10,
        "is_featured": True,
        "seo_title": "Servicio de impresión 3D en Huancayo",
        "seo_description": (
            "Diseño e impresión 3D de prototipos, soportes "
            "y piezas personalizadas en Huancayo."
        ),
    },
]


class Command(BaseCommand):
    """Crea las categorías y servicios iniciales."""

    help = "Carga el catálogo inicial de servicios de MS Electrical."

    def handle(self, *args, **options):
        """Ejecuta la carga inicial sin duplicar registros."""

        categories = {}
        created_categories = 0
        created_services = 0

        for category_data in CATEGORIES:
            category, created = ServiceCategory.objects.get_or_create(
                slug=category_data["slug"],
                defaults=category_data,
            )

            categories[category.slug] = category

            if created:
                created_categories += 1

        for service_data in SERVICES:
            category_slug = service_data["category_slug"]
            category = categories[category_slug]

            defaults = {
                key: value
                for key, value in service_data.items()
                if key != "category_slug"
            }

            defaults["category"] = category

            _, created = Service.objects.get_or_create(
                slug=service_data["slug"],
                defaults=defaults,
            )

            if created:
                created_services += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Carga finalizada. "
                f"Categorías nuevas: {created_categories}. "
                f"Servicios nuevos: {created_services}."
            )
        )