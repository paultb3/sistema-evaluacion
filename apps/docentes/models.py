from django.db import models
from apps.usuarios.models import Usuario  # asegúrate de usar tu modelo personalizado

class Docente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    departamento = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=150, blank=True)
    grado_academico = models.CharField(
        max_length=50,
        choices=[
            ('LIC', 'Licenciatura'),
            ('MAE', 'Maestría'),
            ('DOC', 'Doctorado'),
            ('POS', 'Posdoctorado'),
        ],
        default='LIC'
    )
    fecha_ingreso = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.nombre} - {self.departamento}"
    



class EvaluacionDocente(models.Model):
    docente = models.ForeignKey('Docente', on_delete=models.CASCADE, related_name='evaluaciones')
    alumno = models.ForeignKey('alumnos.Estudiante', on_delete=models.SET_NULL, null=True, blank=True)
    puntuacion = models.IntegerField()
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)