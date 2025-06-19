from django.urls import path
from . import views

app_name = "alumno"

urlpatterns = [
    path("bienvenido_alumno/<uuid:usuario_id>/", views.bienvenida_alumnos, name="bienvenida_alumno"),
    path("perfil_alumno/<uuid:usuario_id>/", views.perfil_alumno, name="perfil_alumno"),
    path("evaluaciones/<uuid:usuario_id>/",views.evaluar_docente,name="evaluaciones",),
    path("explorar/<uuid:usuario_id>/", views.explorar, name="explorar"),
]
