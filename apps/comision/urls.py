from os import name
from django.urls import path
from . import views


# definir el app name
app_name = "comision"

urlpatterns = [
    path(
        "realizar_encuesta/<uuid:usuario_id>/",
        views.realizar_encuesta,
        name="realizar_encuesta",
    ),
    path(
        "perfil_comision/<uuid:usuario_id>/",
        views.perfil_comision,
        name="perfil_comision",
    ),
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
            path("bienvenida/<uuid:usuario_id>/", views.index, name="bienvenida_comision"),
    path("reporte_general/<uuid:usuario_id>/",views.reporter_general, name="reporte_general"),
    path("reporte_curso/<uuid:usuario_id>/", views.reporte_curso, name="reporte_curso"),
            path("reporte_docente/<uuid:usuario_id>/",views.reporte_docente,name="reporte_docente")
]
