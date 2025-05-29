from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .forms import LoginForm
from apps.usuarios.models import Usuario


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            correo = form.cleaned_data.get("correo")
            password = form.cleaned_data.get("password")

            user = Usuario.objects.filter(correo=correo, password=password).first()

            rol_nombre = str(user.rol).lower()
            if user is not None:
                if rol_nombre == "comision":
                    return redirect("comision:bienvenida_comision")
            else:
                messages.error(request, "Correo o contraseña incorrectos")

    return render(request, "login.html", {"form": form})
