"""Vistas públicas de solicitudes de cotización."""

from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import QuoteRequestForm
from .models import QuoteAttachment, QuoteRequest


@transaction.atomic
def quote_request_create(request):
    """Recibe y almacena una solicitud de cotización."""

    if request.method == "POST":
        form = QuoteRequestForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
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

            return redirect(
                "quotes:success",
                public_id=quote_request.public_id,
            )
    else:
        form = QuoteRequestForm()

    context = {
        "form": form,
    }

    return render(
        request,
        "quotes/request_form.html",
        context,
    )


def quote_request_success(request, public_id):
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