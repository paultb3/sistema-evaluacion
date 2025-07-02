from django.db import models
from apps.docentes.models import Docente
from apps.alumnos.models import Estudiante
import uuid


class Escuela(models.Model):
    id_escuela = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre


class Facultad(models.Model):
    id_facultad = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=45)
    escuela = models.ForeignKey(Escuela, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    semestre = models.CharField(max_length=10)
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Matricula(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_matricula = models.DateTimeField(auto_now_add=True)

    class Estado(models.TextChoices):
        ACTIVA = "activa", "Activa"
        RETIRADA = "retirada", "Retirada"
        FINALIZADA = "finalizada", "Finalizada"

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVA,
    )

    class Meta:
        unique_together = ("estudiante", "curso")

    def __str__(self):
        return f"{self.estudiante} en {self.curso}"
