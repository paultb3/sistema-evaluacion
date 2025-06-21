from django.db import models
from apps.docentes.models import Docente
from apps.alumnos.models import Estudiante
import uuid

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
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activa', 'Activa'),
            ('retirada', 'Retirada'),
            ('finalizada', 'Finalizada')
        ],
        default='activa'
    )
    
    class Meta:
        unique_together = ('estudiante', 'curso')  # Un estudiante solo puede matricularse una vez en cada curso
        
    def __str__(self):
        return f"{self.estudiante} en {self.curso}"
