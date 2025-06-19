from django.urls import path
from . import views

app_name = 'docente'

urlpatterns = [
    path('bienvenido_docente/<uuid:usuario_id>/', views.bienvenido_docente, name='bienvenido_docente'),
    path('perfil_docente/<uuid:usuario_id>/', views.perfil_docente, name='perfil_docente'),
    path('ver_recomendaciones/<uuid:usuario_id>/', views.ver_recomendaciones, name='ver_recomendaciones'),
    path('ver_evaluacion/<uuid:usuario_id>/' , views.ver_evaluacion, name='ver_evaluacion')
]
