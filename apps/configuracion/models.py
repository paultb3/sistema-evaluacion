from django.db import models
import uuid

class Parametro(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    valor = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nombre}: {self.valor}"
