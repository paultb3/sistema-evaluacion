import uuid
from django.db import models
from django.utils.timezone import now
from apps.core.models import Facultad
from apps.evaluacion.models import PeriodoEvaluacion
from apps.usuarios.models import Usuario

# Create your models here.


class Notificaciones(models.Model):
    id_notificaciones = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    tipo = models.CharField("tipo", max_length=255)
    nombre = models.CharField("nombre", max_length=255)
    estado = models.CharField(
        "estado",
        max_length=20,
        choices=[
            ("enviado", "Enviado"),
            ("leido", "Leido"),
            ("pendiente", "Pendiente"),
        ],
        default="enviado",
    )
    periodo = models.ForeignKey(PeriodoEvaluacion, on_delete=models.CASCADE)
    escuela = models.ForeignKey(Facultad, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(default=now)
