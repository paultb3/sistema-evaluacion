from django.contrib import admin
from apps.core.models import Curso, Matricula

# Register your models here.

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'semestre', 'docente')
    list_filter = ('semestre', 'docente')
    search_fields = ('nombre', 'codigo', 'docente__usuario__nombre')

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'curso', 'estado', 'fecha_matricula')
    list_filter = ('estado', 'curso', 'curso__semestre')
    search_fields = ('estudiante__usuario__nombre', 'estudiante__codigo', 'curso__nombre', 'curso__codigo')
    date_hierarchy = 'fecha_matricula'
    list_select_related = ('estudiante', 'curso', 'estudiante__usuario', 'curso__docente')
