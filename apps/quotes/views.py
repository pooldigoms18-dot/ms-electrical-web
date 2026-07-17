"""Vistas públicas de solicitudes de cotización."""

from django.conf import settings
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
from django.utils import timezone

from apps.portfolio.models import Project
from apps.services.models import Service

from .forms import QuoteRequestForm
from .models import (
    QuoteAttachment,
    QuoteRequest,
)
from .notifications import (
    send_quote_notifications,
)


QUOTE_LAST_SUBMISSION_SESSION_KEY = (
    "quotes:last_successful_submission"
)


def get_quote_source(request):
    """Obtiene el servicio o proyecto desde donde llega el usuario."""

    service_slug = request.GET.get(
        "servicio",
        "",
    ).strip()

    project_slug = request.GET.get(
        "proyecto",
        "",
    ).strip()

    selected_service = None
    source_project = None

    if service_slug:
        selected_service = (
            Service.objects
            .filter(
                slug=service_slug,
                is_active=True,
                category__is_active=True,
            )
            .select_related("category")
            .first()
        )

    if project_slug:
        source_project = (
            Project.objects
            .filter(
                slug=project_slug,
                is_active=True,
            )
            .prefetch_related("services")
            .first()
        )

    return (
        selected_service,
        source_project,
    )


def quote_submission_is_too_fast(request):
    """Detecta un nuevo envío inmediatamente después de otro."""

    cooldown_seconds = max(
        0,
        int(
            getattr(
                settings,
                "QUOTE_SUBMISSION_COOLDOWN_SECONDS",
                30,
            )
        ),
    )

    if cooldown_seconds == 0:
        return False

    previous_timestamp = request.session.get(
        QUOTE_LAST_SUBMISSION_SESSION_KEY,
    )

    if previous_timestamp is None:
        return False

    try:
        previous_timestamp = float(
            previous_timestamp,
        )

    except (
        TypeError,
        ValueError,
    ):
        return False

    elapsed_seconds = (
        timezone.now().timestamp()
        - previous_timestamp
    )

    return (
        elapsed_seconds
        < cooldown_seconds
    )


@transaction.atomic
def quote_request_create(request):
    """Recibe y almacena una solicitud de cotización."""

    selected_service, source_project = (
        get_quote_source(
            request,
        )
    )

    if request.method == "POST":
        form = QuoteRequestForm(
            request.POST,
            request.FILES,
        )

        if quote_submission_is_too_fast(
            request,
        ):
            form.add_error(
                None,
                (
                    "Ya recibimos una solicitud hace unos segundos. "
                    "Espera un momento antes de realizar otro envío."
                ),
            )

        elif form.is_valid():
            quote_request = form.save(
                commit=False,
            )

            quote_request.source_url = (
                request.build_absolute_uri()
            )[:500]

            quote_request.save()

            for photo in form.cleaned_data.get(
                "photos",
                [],
            ):
                QuoteAttachment.objects.create(
                    quote_request=quote_request,
                    image=photo,
                )

            request.session[
                QUOTE_LAST_SUBMISSION_SESSION_KEY
            ] = timezone.now().timestamp()

            success_url = (
                request.build_absolute_uri(
                    reverse(
                        "quotes:success",
                        kwargs={
                            "public_id": (
                                quote_request.public_id
                            ),
                        },
                    )
                )
            )

            transaction.on_commit(
                lambda: send_quote_notifications(
                    quote_request.pk,
                    success_url,
                )
            )

            return redirect(
                "quotes:success",
                public_id=quote_request.public_id,
            )

    else:
        initial_data = {}

        if selected_service:
            initial_data[
                "service"
            ] = selected_service.pk

        form = QuoteRequestForm(
            initial=initial_data,
        )

    context = {
        "form": form,
        "selected_service": selected_service,
        "source_project": source_project,
    }

    return render(
        request,
        "quotes/request_form.html",
        context,
    )


def quote_request_success(
    request,
    public_id,
):
    """Muestra la confirmación después del registro."""

    quote_request = get_object_or_404(
        QuoteRequest.objects.select_related(
            "service",
        ),
        public_id=public_id,
    )

    context = {
        "quote_request": quote_request,
    }

    return render(
        request,
        "quotes/request_success.html",
        context,
    )