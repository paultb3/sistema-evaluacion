from django.db import models
from apps.usuarios.models import Usuario
import uuid

class PreferenciaNotificacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    preferencias = models.JSONField()

    def __str__(self):
        return f"Preferencias de {self.usuario.nombre}"
