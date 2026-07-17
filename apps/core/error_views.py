"""Vistas utilizadas para errores de seguridad."""

import logging

from django.shortcuts import render


logger = logging.getLogger(__name__)


def csrf_failure(request, reason=""):
    """Muestra un error amigable cuando falla la validación CSRF."""

    logger.warning(
        "Solicitud rechazada por validación CSRF en %s.",
        request.path,
    )

    return render(
        request,
        "403_csrf.html",
        status=403,
    )