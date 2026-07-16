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