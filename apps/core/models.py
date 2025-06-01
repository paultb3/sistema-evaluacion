from django.db import models
from apps.docentes.models import Docente
import uuid

class Curso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    semestre = models.CharField(max_length=10)
    docente = models.ForeignKey('docentes.Docente', models.DO_NOTHING)


    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
