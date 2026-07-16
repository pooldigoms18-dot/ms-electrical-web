"""Utilidades para optimizar imágenes públicas."""

import os
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def prepare_image_for_save(
    image,
    image_format,
):
    """Prepara el modo de color según el formato de salida."""

    if image_format == "JPEG":
        if image.mode not in (
            "RGB",
            "L",
        ):
            return image.convert(
                "RGB",
            )

    return image


def get_save_options(
    image_format,
    quality=82,
):
    """Devuelve opciones de compresión apropiadas."""

    if image_format == "JPEG":
        return {
            "quality": quality,
            "optimize": True,
            "progressive": True,
        }

    if image_format == "WEBP":
        return {
            "quality": quality,
            "method": 6,
        }

    if image_format == "PNG":
        return {
            "optimize": True,
        }

    return {}


def get_image_format(
    image,
    filename,
):
    """Determina el formato usando Pillow o la extensión."""

    if image.format:
        image_format = image.format.upper()

        if image_format == "JPG":
            return "JPEG"

        return image_format

    extension = Path(
        filename,
    ).suffix.lower()

    formats = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".webp": "WEBP",
    }

    return formats.get(
        extension,
        "",
    )


def optimize_uploaded_image(
    uploaded_file,
    max_width=1920,
    max_height=1920,
    quality=82,
):
    """
    Optimiza una nueva imagen antes de almacenarla.

    Mantiene el formato original y solamente utiliza
    la versión optimizada cuando resulta más pequeña.
    """

    if not uploaded_file:
        return uploaded_file

    original_name = uploaded_file.name

    extension = Path(
        original_name,
    ).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        return uploaded_file

    try:
        uploaded_file.seek(0)

        original_data = uploaded_file.read()

        source_stream = BytesIO(
            original_data,
        )

        with Image.open(source_stream) as source:
            image_format = get_image_format(
                source,
                original_name,
            )

            if image_format not in {
                "JPEG",
                "PNG",
                "WEBP",
            }:
                uploaded_file.seek(0)
                return uploaded_file

            image = ImageOps.exif_transpose(
                source,
            )

            image.thumbnail(
                (
                    max_width,
                    max_height,
                ),
                Image.Resampling.LANCZOS,
            )

            image = prepare_image_for_save(
                image,
                image_format,
            )

            output = BytesIO()

            image.save(
                output,
                format=image_format,
                **get_save_options(
                    image_format,
                    quality,
                ),
            )

        optimized_data = output.getvalue()

        # No sustituimos el archivo cuando la optimización
        # produce una imagen de mayor tamaño.
        if len(optimized_data) >= len(original_data):
            return ContentFile(
                original_data,
                name=original_name,
            )

        return ContentFile(
            optimized_data,
            name=original_name,
        )

    except (
        OSError,
        ValueError,
    ):
        uploaded_file.seek(0)

        return uploaded_file


def optimize_image_path(
    file_path,
    max_width=1920,
    max_height=1920,
    quality=82,
    apply_changes=True,
):
    """
    Optimiza una imagen existente de forma segura.

    Primero crea un archivo temporal. Solo sustituye
    el archivo original cuando el resultado es menor.
    """

    path = Path(
        file_path,
    )

    if (
        not path.exists()
        or path.suffix.lower()
        not in SUPPORTED_EXTENSIONS
    ):
        return {
            "processed": False,
            "optimized": False,
            "original_size": 0,
            "final_size": 0,
        }

    original_size = path.stat().st_size

    temporary_path = None

    try:
        with Image.open(path) as source:
            image_format = get_image_format(
                source,
                path.name,
            )

            if image_format not in {
                "JPEG",
                "PNG",
                "WEBP",
            }:
                return {
                    "processed": False,
                    "optimized": False,
                    "original_size": original_size,
                    "final_size": original_size,
                }

            image = ImageOps.exif_transpose(
                source,
            )

            image.thumbnail(
                (
                    max_width,
                    max_height,
                ),
                Image.Resampling.LANCZOS,
            )

            image = prepare_image_for_save(
                image,
                image_format,
            )

            with NamedTemporaryFile(
                mode="wb",
                delete=False,
                dir=path.parent,
                suffix=path.suffix,
            ) as temporary_file:
                temporary_path = Path(
                    temporary_file.name,
                )

                image.save(
                    temporary_file,
                    format=image_format,
                    **get_save_options(
                        image_format,
                        quality,
                    ),
                )

        optimized_size = (
            temporary_path.stat().st_size
        )

        should_replace = (
            optimized_size
            < original_size
        )

        if (
            should_replace
            and apply_changes
        ):
            os.replace(
                temporary_path,
                path,
            )

            temporary_path = None

            return {
                "processed": True,
                "optimized": True,
                "original_size": original_size,
                "final_size": optimized_size,
            }

        return {
            "processed": True,
            "optimized": should_replace,
            "original_size": original_size,
            "final_size": (
                optimized_size
                if should_replace
                else original_size
            ),
        }

    except (
        OSError,
        ValueError,
    ):
        return {
            "processed": False,
            "optimized": False,
            "original_size": original_size,
            "final_size": original_size,
        }

    finally:
        if (
            temporary_path
            and temporary_path.exists()
        ):
            temporary_path.unlink(
                missing_ok=True,
            )
            