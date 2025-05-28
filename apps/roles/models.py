from django.db import models
import uuid

class Rol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=50, unique=True)
    permisos = models.JSONField()

    def __str__(self):
        return self.nombre
