from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from apps.usuarios.models import Usuario
from apps.docentes.models import Docente
from apps.alumnos.models import Estudiante
from apps.comision.models import Comision  # si vas a usarlo


def index(request):
    return render(request, 'core/base.html')  # o el template que quieras mostrar

def login_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        password = request.POST.get("password")

        try:
            usuario = Usuario.objects.get(correo=correo)

            if check_password(password, usuario.password):
                # ✅ ESTABLECER SESIÓN
                auth_logout(request)  # limpia sesiones anteriores si existen
                auth_login(request, usuario)  # 🔥 inicia sesión correctamente

                # Redirigir según el rol
                if hasattr(usuario, 'docente'):
                    return redirect('docentes:dashboard')
                elif hasattr(usuario, 'estudiante'):
                    return redirect('alumnos:dashboard')
                elif hasattr(usuario, 'comision'):
                    return redirect(reverse("comision:bienvenida_comision", kwargs={"usuario_id": usuario.id}))
                else:
                    error = "Tu cuenta no tiene un rol asignado."
                    return render(request, "core/login.html", {"error": error})
            else:
                error = "Contraseña incorrecta"
        except Usuario.DoesNotExist:
            error = "Usuario no encontrado"

        return render(request, "core/login.html", {"form": {}, "error": error})

    return render(request, "core/login.html", {"form": {}})
