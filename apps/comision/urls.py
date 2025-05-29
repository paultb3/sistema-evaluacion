from django.urls import path
from . import views


# definir el app name
app_name = "comision"

urlpatterns = [
    path("", views.index, name="bienvenida_comision"),
    path("realizar_encuesta/", views.realizar_encuesta, name="realizar_encuesta"),
    path("perfil", views.perfil, name="perfil"),
    path(
        "editar_pregunta/<uuid:id_pregunta>/",
        views.editar_pregunta,
        name="editar_pregunta",
    ),
    path(
        "eliminar_pregunta/<uuid:id_pregunta>/",
        views.eliminar_pregunta,
        name="eliminar_pregunta",
    ),
    path(
        "agregar_pregunta/<uuid:id_modulo>/",
        views.agregar_pregunta,
        name="agregar_pregunta",
    ),
]
