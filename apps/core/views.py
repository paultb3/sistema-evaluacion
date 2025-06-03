from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from apps.usuarios.models import Usuario
import uuid


def login_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        password = request.POST.get("password")

        try:
            usuario = Usuario.objects.get(correo=correo)
            if (
                usuario.password == password
            ):  # Reemplaza esto con `check_password()` si usas hashes
                # Login exitoso
                url = reverse(
                    "comision:bienvenida_comision", kwargs={"usuario_id": usuario.id}
                )
                return redirect(url)  # o a donde quieras redirigir
            else:
                error = "Contraseña incorrecta"
        except Usuario.DoesNotExist:
            error = "Usuario no encontrado"

        return render(request, "login.html", {"form": {}, "error": error})

    return render(request, "login.html", {"form": {}})
