"""Pruebas del comando convert_images_webp."""

import shutil
import tempfile
from io import BytesIO, StringIO

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from apps.portfolio.models import Project


def png_photo():
    buffer = BytesIO()
    Image.effect_noise((900, 600), 60).convert("RGB").save(buffer, "PNG")
    return buffer.getvalue()


class ConvertImagesWebPTests(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()

        self.project = Project.objects.create(
            title="Proyecto de prueba",
            location="Huancayo",
            short_description="Prueba",
        )
        # update() evita la optimización de save(): simula una foto
        # antigua subida antes de este cambio.
        name = Project._meta.get_field("cover_image").storage.save(
            "projects/prueba/cover/foto.png",
            ContentFile(png_photo()),
        )
        Project.objects.filter(pk=self.project.pk).update(cover_image=name)

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def run_command(self, *args):
        out = StringIO()
        call_command("convert_images_webp", *args, stdout=out)
        return out.getvalue()

    def test_dry_run_changes_nothing(self):
        output = self.run_command()

        self.project.refresh_from_db()
        self.assertTrue(self.project.cover_image.name.endswith(".png"))
        self.assertIn("Simulación", output)

    def test_apply_converts_and_keeps_original(self):
        original = self.project.cover_image.name

        self.run_command("--apply")

        self.project.refresh_from_db()
        self.assertTrue(self.project.cover_image.name.endswith(".webp"))
        storage = self.project.cover_image.storage
        self.assertTrue(storage.exists(self.project.cover_image.name))
        self.assertTrue(storage.exists(original))
