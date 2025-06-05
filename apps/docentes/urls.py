from django.urls import path
from . import views

app_name = 'docentes'

urlpatterns = [
    path('dashboard/', views.dashboard_docente, name='dashboard'),
    path('perfil/', views.perfil_docente, name='perfil'),
    path('editar-perfil/', views.editar_perfil_docente, name='editar_perfil'),
    path('logout/', views.logout_view, name='logout'),
]
