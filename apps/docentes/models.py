from django.db import models
from apps.usuarios.models import Usuario

class Docente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    departamento = models.CharField(max_length=100)

    def __str__(self):
        return self.usuario.nombre
