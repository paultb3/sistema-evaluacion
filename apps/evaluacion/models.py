from django.db import models
from apps.alumnos.models import Estudiante
from apps.docentes.models import Docente
from apps.core.models import Curso
import uuid


# Criterios que serán usados por cada evaluación


class Calificacion(models.IntegerChoices):
    UNO = "1", "Muy Deficiente"
    DOS = "2", "Deficiente"
    TRES = "3", "Regular"
    CUATRO = "4", "Bueno"
    CINCO = "5", "Excelente"


class Criterio(models.Model):
    id_criterio = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    calificacion = models.IntegerField(
        choices=Calificacion.choices, default=Calificacion.UNO
    )

    def __str__(self):
        return self.get_calificacion_display()


# Evaluación realizada por un estudiante a un docente en un curso específico
class Evaluacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    criterio = models.ForeignKey(
        Criterio, on_delete=models.CASCADE, blank=True, null=True
    )
    docente = models.ForeignKey(
        Docente, on_delete=models.CASCADE, blank=True, null=True
    )
    estado = models.CharField(
        max_length=20,
        choices=[("borrador", "Borrador"), ("enviada", "Enviada")],
        default="borrador",
    )

    class Meta:
        unique_together = (
            "estudiante",
            "curso",
        )  # Evita que se evalúe más de una vez por curso

    def __str__(self):
        return f"{self.estudiante.usuario.nombre} → {self.docente.usuario.nombre} ({self.curso.nombre})"


# Respuesta específica a un criterio dentro de una evaluación
class Respuesta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluacion = models.ForeignKey(
        Evaluacion, on_delete=models.CASCADE, related_name="respuestas"
    )
    criterio = models.ForeignKey(Criterio, on_delete=models.CASCADE, blank=True)
    puntuacion = models.IntegerField(
        choices=[(i, f"{i} estrella{'s' if i > 1 else ''}") for i in range(1, 6)]
    )
    comentario = models.TextField(blank=True)

    def __str__(self):
        return f"{self.criterio.nombre} - {self.puntuacion}★"


class ModuloPreguntas(models.Model):
    id_modulo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class PreguntaModulo(models.Model):
    id_pregunta = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_modulo = models.ForeignKey(ModuloPreguntas, on_delete=models.CASCADE)
    pregunta = models.TextField(max_length=1000)

    def __str__(self):
        return (
            f"{self.id_modulo.id_modulo} - "
            + self.pregunta
            + f" ({self.id_modulo.nombre})"
        )
