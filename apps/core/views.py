from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from apps.usuarios.models import Usuario


def login_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo", "")
        password = request.POST.get("password", "")

        print(f"Correo recibido: {correo}")
        print(f"Password recibido: {password}")

        error = None  # Inicializa el error
        try:

            usuario = Usuario.objects.get(correo=correo)
            print(f"Usuario encontrado: {usuario}")
            print(f"Usuario ID: {usuario.password}")
            print(f"Usuario Rol: {type(usuario.rol)} {usuario.rol}")
            if usuario.password == password:
                # Login exitoso
                print(f"Usuario ID: {usuario.id}")

                if str(usuario.rol) == "comision":
                    url = reverse(
                        "comision:bienvenida_comision",
                        kwargs={"usuario_id": usuario.id},
                    )
                    return redirect(url)
                elif str(usuario.rol) == "alumno":
                    url = reverse(
                        "alumno:bienvenida_alumnos",
                        kwargs={"usuario_id": usuario.id},
                    )

                    return redirect(url)
                else:
                    error = "Rol no reconocido. Contacta con el administrador."
            else:
                error = "Contraseña incorrecta"

        except Usuario.DoesNotExist:
            error = "Usuario no encontrado"

        return render(request, "login.html", {"form": {}, "error": error})

    # Si es GET
    return render(request, "login.html", {"form": {}})


def logout_view(request):
    print("Cerrando sesión")
    # Aquí deberías implementar la lógica para cerrar sesión
    # Por ejemplo, limpiar la sesión del usuario
    request.session.flush()  # Limpia la sesión actual
    print("Sesión cerrada correctamente")
    # Puedes redirigir a una página de inicio o login después de cerrar sesión
    return render(
        request, "login.html", {"form": {}}
    )  # Redirige a la página de login o inicio
