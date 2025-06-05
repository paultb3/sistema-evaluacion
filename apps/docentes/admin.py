from django.contrib import admin
from .models import Docente

@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'departamento', 'especialidad', 'grado_academico', 'activo')
    search_fields = ('usuario__nombre', 'departamento')
    list_filter = ('activo', 'grado_academico')
