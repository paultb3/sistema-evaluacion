from django.urls import path
from . import views

app_name = 'docentes'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard_docente, name='dashboard'),
    path('logout/', views.logout, name='logout'),
    path('perfil/', views.perfil_docente, name='perfil'),
]

