from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from apps.usuarios.models import Usuario
import uuid


def index(request):
    return render(request, 'core/base.html')


def login_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        password = request.POST.get("password")

        try:
            usuario = Usuario.objects.get(correo=correo)
            # Si usas contraseña en texto plano (no recomendado), compara así:
            # if usuario.password == password:
            # Si usas hash, usa check_password:
            if check_password(password, usuario.password):
                # Login exitoso
                url = reverse(
                    "comision:bienvenida_comision", kwargs={"usuario_id": usuario.id}
                )
                return redirect(url)  # redirige a la página deseada
            else:
                error = "Contraseña incorrecta"
        except Usuario.DoesNotExist:
            error = "Usuario no encontrado"

        return render(request, "core/login.html", {"form": {}, "error": error})

    return render(request, "core/login.html", {"form": {}})
