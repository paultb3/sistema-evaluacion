from django.contrib import admin

# Register your models here.


from apps.evaluacion.models import (
    Evaluacion,
    Respuesta,
    ModuloPreguntas,
    PreguntaModulo,
)

admin.site.register([Evaluacion, Respuesta, ModuloPreguntas, PreguntaModulo])
