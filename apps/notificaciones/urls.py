from django.urls import path
from . import views

app_name = "notificaciones"
urlpatterns = [
    path(
        "obtener/<uuid:usuario_id>/",
        views.obtener_notificaciones,
        name="obtener_notificaciones",
    ),
    path(
        "marcar-leida/<uuid:notificacion_id>/",
        views.marcar_notificacion_leida,
        name="marcar_leida",
    ),
]
