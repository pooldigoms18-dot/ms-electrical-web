"""Rutas públicas de la aplicación principal."""

from django.urls import path

from . import views


app_name = "core"


urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),
    path(
        "robots.txt",
        views.robots_txt,
        name="robots",
    ),
    path(
        "preguntas-frecuentes/",
        views.faq_list,
        name="faq",
    ),
]