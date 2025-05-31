from django.urls import path
from . import views


# definir el app name
app_name = "comision"

urlpatterns = [
    path("<uuid:usuario_id>", views.index, name="bienvenida_comision"),
    path(
        "realizar_encuesta/<uuid:usuario_id>/",
        views.realizar_encuesta,
        name="realizar_encuesta",
    ),
    path("perfil/<uuid:usuario_id>/", views.perfil, name="perfil"),
    path(
        "editar_pregunta/<uuid:usuario_id>/<uuid:id_pregunta>/",
        views.editar_pregunta,
        name="editar_pregunta",
    ),
    path(
        "eliminar_pregunta/<uuid:usuario_id>/<uuid:id_pregunta>/",
        views.eliminar_pregunta,
        name="eliminar_pregunta",
    ),
    path(
        "agregar_pregunta/<uuid:usuario_id>/<uuid:id_modulo>/",
        views.agregar_pregunta,
        name="agregar_pregunta",
    ),
]
