"""Envío de notificaciones para solicitudes de cotización."""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from apps.core.models import CompanyProfile

from .models import QuoteRequest


logger = logging.getLogger(__name__)


def get_active_company():
    """Obtiene la información empresarial activa."""

    return (
        CompanyProfile.objects
        .filter(is_active=True)
        .order_by("-updated_at")
        .first()
    )


def send_email_message(
    subject,
    recipient_list,
    text_template,
    html_template,
    context,
):
    """Construye y envía un correo en texto y HTML."""

    if not recipient_list:
        return False

    text_body = render_to_string(
        text_template,
        context,
    )

    html_body = render_to_string(
        html_template,
        context,
    )

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )

    message.attach_alternative(
        html_body,
        "text/html",
    )

    return message.send(
        fail_silently=False,
    ) > 0


def send_admin_notification(
    quote_request,
    success_url="",
):
    """Notifica a MS Electrical sobre una nueva solicitud."""

    company = get_active_company()

    context = {
        "quote_request": quote_request,
        "company": company,
        "success_url": success_url,
    }

    subject = (
        f"Nueva solicitud {quote_request.reference_code} "
        f"— {quote_request.full_name}"
    )

    sent = send_email_message(
        subject=subject,
        recipient_list=settings.COMPANY_NOTIFICATION_EMAILS,
        text_template=(
            "emails/quotes/admin_notification.txt"
        ),
        html_template=(
            "emails/quotes/admin_notification.html"
        ),
        context=context,
    )

    if sent:
        QuoteRequest.objects.filter(
            pk=quote_request.pk,
        ).update(
            admin_notification_sent_at=timezone.now(),
        )

    return sent


def send_customer_confirmation(
    quote_request,
    success_url="",
):
    """Envía al cliente una confirmación de recepción."""

    if not quote_request.email:
        return False

    company = get_active_company()

    context = {
        "quote_request": quote_request,
        "company": company,
        "success_url": success_url,
    }

    subject = (
        f"Recibimos tu solicitud "
        f"{quote_request.reference_code}"
    )

    sent = send_email_message(
        subject=subject,
        recipient_list=[
            quote_request.email,
        ],
        text_template=(
            "emails/quotes/customer_confirmation.txt"
        ),
        html_template=(
            "emails/quotes/customer_confirmation.html"
        ),
        context=context,
    )

    if sent:
        QuoteRequest.objects.filter(
            pk=quote_request.pk,
        ).update(
            customer_confirmation_sent_at=timezone.now(),
        )

    return sent


def send_quote_notifications(
    quote_request_id,
    success_url="",
):
    """
    Envía las notificaciones sin eliminar la solicitud
    cuando el servicio de correo falla.
    """

    quote_request = (
        QuoteRequest.objects
        .select_related("service")
        .get(pk=quote_request_id)
    )

    errors = []

    try:
        send_admin_notification(
            quote_request,
            success_url,
        )

    except Exception as exc:
        logger.exception(
            "Error enviando notificación interna "
            "de la solicitud %s.",
            quote_request.reference_code,
        )

        errors.append(
            f"Notificación interna: {exc}"
        )

    try:
        send_customer_confirmation(
            quote_request,
            success_url,
        )

    except Exception as exc:
        logger.exception(
            "Error enviando confirmación al cliente "
            "de la solicitud %s.",
            quote_request.reference_code,
        )

        errors.append(
            f"Confirmación al cliente: {exc}"
        )

    QuoteRequest.objects.filter(
        pk=quote_request.pk,
    ).update(
        notification_error="\n".join(errors),
    )

    return {
        "admin_notification": (
            not any(
                error.startswith(
                    "Notificación interna:"
                )
                for error in errors
            )
        ),
        "customer_confirmation": (
            not quote_request.email
            or not any(
                error.startswith(
                    "Confirmación al cliente:"
                )
                for error in errors
            )
        ),
        "errors": errors,
    }