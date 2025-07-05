from django.db import models
from apps.usuarios.models import Usuario

# Create your models here.


class Estudiante(models.Model):
    usuario = models.OneToOneField(Usuario, primary_key=True, on_delete=models.CASCADE)
    semestre = models.CharField(max_length=10)
    carrera = models.ForeignKey('core.Escuela', on_delete=models.CASCADE, blank=True)
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return self.usuario.nombre
