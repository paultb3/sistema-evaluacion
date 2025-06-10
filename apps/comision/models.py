from django.db import models
from apps.usuarios.models import Usuario


class Comision(models.Model):
    usuario = models.OneToOneField(Usuario, primary_key=True, on_delete=models.CASCADE)
    facultad = models.CharField(max_length=100)

    def __str__(self):
        return f"Comisión de {self.usuario} ({self.facultad})"
