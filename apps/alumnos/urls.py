from django.urls import path
from . import views

app_name = "alumno"

urlpatterns = [
    path("<uuid:usuario_id>/", views.bienvenida_alumnos, name="bienvenida_alumnos"),
    path("perfil_alumno/<uuid:usuario_id>/", views.perfil_alumno, name="perfil_alumno"),
    path(
        "evaluar_docente/<uuid:usuario_id>/",
        views.evaluar_docente,
        name="evaluar_docente",
    ),
    path("explorar/<uuid:usuario_id>/", views.explorar, name="explorar"),
]
