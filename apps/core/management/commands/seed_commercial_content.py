"""Crea contenido comercial inicial para MS Electrical."""

from django.core.management.base import BaseCommand

from apps.core.models import GlobalFAQ


FAQS = [
    {
        "question": (
            "¿Qué información necesitan para realizar "
            "una primera evaluación?"
        ),
        "answer": (
            "Puedes enviarnos una descripción de lo que necesitas, "
            "la ubicación del proyecto, fotografías y medidas "
            "aproximadas. Con esa información realizaremos una "
            "primera revisión y te indicaremos los siguientes pasos."
        ),
        "display_order": 10,
        "show_on_home": True,
    },
    {
        "question": (
            "¿Es necesario tener medidas exactas antes de consultar?"
        ),
        "answer": (
            "No. Para una evaluación inicial puedes proporcionar "
            "medidas aproximadas y fotografías. Cuando el proyecto "
            "lo requiera, coordinaremos la verificación de medidas "
            "antes de fabricar o instalar."
        ),
        "display_order": 20,
        "show_on_home": True,
    },
    {
        "question": (
            "¿Atienden proyectos residenciales y comerciales?"
        ),
        "answer": (
            "Sí. Evaluamos proyectos para viviendas, negocios, "
            "instituciones y otros espacios, de acuerdo con el tipo "
            "de trabajo y las condiciones de instalación."
        ),
        "display_order": 30,
        "show_on_home": True,
    },
    {
        "question": (
            "¿En qué zonas trabajan?"
        ),
        "answer": (
            "Nuestra cobertura principal comprende Huancayo, "
            "El Tambo, Chilca y Chupaca. Para proyectos en otras "
            "zonas podemos revisar previamente la ubicación y "
            "las condiciones del servicio."
        ),
        "display_order": 40,
        "show_on_home": True,
    },
    {
        "question": (
            "¿Los trabajos incluyen garantía?"
        ),
        "answer": (
            "Las condiciones de garantía dependen del tipo de "
            "servicio, materiales y equipos utilizados. Antes de "
            "iniciar el proyecto se pueden precisar las condiciones "
            "aplicables al trabajo contratado."
        ),
        "display_order": 50,
        "show_on_home": True,
    },
    {
        "question": (
            "¿Realizan mantenimiento después de una instalación?"
        ),
        "answer": (
            "Podemos evaluar servicios de mantenimiento preventivo "
            "o correctivo según el tipo de instalación, sistema de "
            "automatización o equipo implementado."
        ),
        "display_order": 60,
        "show_on_home": True,
    },
    {
        "question": (
            "¿Cómo puedo solicitar una cotización?"
        ),
        "answer": (
            "Puedes completar el formulario de cotización del sitio "
            "y adjuntar hasta cinco fotografías. También puedes "
            "contactarnos directamente por WhatsApp para una "
            "consulta inicial."
        ),
        "display_order": 70,
        "show_on_home": False,
    },
    {
        "question": (
            "¿Puedo solicitar un trabajo similar a un proyecto "
            "publicado en la web?"
        ),
        "answer": (
            "Sí. Desde cada proyecto publicado puedes iniciar una "
            "solicitud utilizando ese trabajo como referencia. "
            "La solución final se adaptará a las medidas y "
            "necesidades específicas de tu proyecto."
        ),
        "display_order": 80,
        "show_on_home": False,
    },
]


class Command(BaseCommand):
    """Carga las preguntas frecuentes iniciales."""

    help = (
        "Crea o actualiza el contenido comercial inicial "
        "de MS Electrical."
    )

    def handle(self, *args, **options):
        """Ejecuta la carga de contenido."""

        created_count = 0
        updated_count = 0

        for faq_data in FAQS:
            question = faq_data["question"]

            defaults = {
                "answer": faq_data["answer"],
                "display_order": faq_data["display_order"],
                "show_on_home": faq_data["show_on_home"],
                "is_active": True,
            }

            faq, created = GlobalFAQ.objects.update_or_create(
                question=question,
                defaults=defaults,
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Contenido comercial cargado correctamente. "
                f"Creadas: {created_count}. "
                f"Actualizadas: {updated_count}."
            )
        )