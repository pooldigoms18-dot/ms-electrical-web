"""Rutas públicas de solicitudes de cotización."""

from django.urls import path

from . import views


app_name = "quotes"


urlpatterns = [
    path(
        "",
        views.quote_request_create,
        name="create",
    ),
    path(
        "gracias/<uuid:public_id>/",
        views.quote_request_success,
        name="success",
    ),
]