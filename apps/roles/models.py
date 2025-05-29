from django.db import models

import uuid


class ModosRoles:
    COMISION = "comision"
    ADMIN = "admin"
    PROFESOR = "profesor"
    ALUMNO = "alumno"


class Rol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(
        max_length=50,
        unique=True,
        choices=[
            (ModosRoles.COMISION, ModosRoles.COMISION),
            (ModosRoles.ADMIN, ModosRoles.ADMIN),
            (ModosRoles.PROFESOR, ModosRoles.PROFESOR),
            (ModosRoles.ALUMNO, ModosRoles.ALUMNO),
        ],
    )
    permisos = models.JSONField()

    def __str__(self):
        return self.nombre
