"""Pruebas de optimización de imágenes."""

from io import BytesIO

from django.core.files.uploadedfile import (
    SimpleUploadedFile,
)
from django.test import SimpleTestCase
from PIL import Image

from apps.core.image_utils import (
    optimize_uploaded_image,
)


class ImageOptimizationTests(SimpleTestCase):
    """Comprueba la optimización básica de fotografías."""

    def test_large_image_is_resized(self):
        """Una imagen grande debe limitar sus dimensiones."""

        source = Image.new(
            "RGB",
            (
                2400,
                1600,
            ),
        )

        source_buffer = BytesIO()

        source.save(
            source_buffer,
            format="JPEG",
            quality=95,
        )

        uploaded_file = SimpleUploadedFile(
            "large-test-image.jpg",
            source_buffer.getvalue(),
            content_type="image/jpeg",
        )

        optimized_file = optimize_uploaded_image(
            uploaded_file,
        )

        optimized_file.seek(0)

        with Image.open(
            optimized_file,
        ) as optimized_image:
            self.assertLessEqual(
                optimized_image.width,
                1920,
            )

            self.assertLessEqual(
                optimized_image.height,
                1920,
            )

class WebPConversionTests(SimpleTestCase):
    """Las fotos subidas se guardan como WebP, más livianas."""

    def _upload(self, mode, name, image_format):
        # Ruido para que se parezca a una foto y no comprima trivialmente.
        source = Image.effect_noise((1200, 800), 60).convert(mode)
        if mode == "RGBA":
            source.putalpha(Image.linear_gradient("L").resize((1200, 800)))
        buffer = BytesIO()
        source.save(buffer, format=image_format)
        return SimpleUploadedFile(name, buffer.getvalue())

    def test_png_photo_becomes_smaller_webp(self):
        uploaded = self._upload("RGB", "fachada.png", "PNG")
        original_size = uploaded.size

        optimized = optimize_uploaded_image(uploaded)

        self.assertTrue(optimized.name.endswith("fachada.webp"))
        self.assertLess(optimized.size, original_size)
        optimized.seek(0)
        with Image.open(optimized) as image:
            self.assertEqual(image.format, "WEBP")

    def test_transparency_is_kept(self):
        uploaded = self._upload("RGBA", "pieza.png", "PNG")

        optimized = optimize_uploaded_image(uploaded)

        optimized.seek(0)
        with Image.open(optimized) as image:
            self.assertEqual(image.format, "WEBP")
            self.assertIn("A", image.getbands())

    def test_service_image_has_single_save(self):
        """Antes un segundo save() anulaba la optimización."""

        from apps.services.models import ServiceImage

        self.assertIn(
            "optimize_uploaded_image",
            ServiceImage.save.__code__.co_names,
        )
