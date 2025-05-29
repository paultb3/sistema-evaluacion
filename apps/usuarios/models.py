from django.db import models
from apps.roles.models import Rol
import uuid
from django.contrib.auth.models import AbstractBaseUser


class Usuario(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=100, default="")
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = ["nombre", "rol"]

    def __str__(self):
        return self.nombre
