from django.db import models
from apps.usuarios.models import Usuario

# Create your models here.


class Estudiante(models.Model):
    usuario = models.OneToOneField(Usuario, primary_key=True, on_delete=models.CASCADE)
    semestre = models.CharField(max_length=10)
    carrera = models.CharField(max_length=100)

    def __str__(self):
        return self.usuario.nombre
