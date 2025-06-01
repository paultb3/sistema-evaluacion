from django.shortcuts import render, redirect
from apps.usuarios.models import Usuario
from apps.docentes.models import Docente
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

def register(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        departamento = request.POST.get('departamento')

        if Usuario.objects.filter(correo=correo).exists():
            messages.error(request, "Correo ya registrado.")
            return redirect('docentes:register')

        hashed_password = make_password(password)
        usuario = Usuario.objects.create(nombre=nombre, correo=correo, password=hashed_password)
        Docente.objects.create(usuario=usuario, departamento=departamento)

        messages.success(request, "Registro exitoso, ahora inicia sesión.")
        return redirect('docentes:login')

    return render(request, 'docentes/register.html')

def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        password = request.POST.get('password')

        try:
            usuario = Usuario.objects.get(correo=correo)
            if check_password(password, usuario.password):
                request.session['usuario_id'] = str(usuario.id)
                return redirect('docentes:dashboard')
            else:
                messages.error(request, "Contraseña incorrecta.")
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")

    return render(request, 'docentes/login.html')

def dashboard_docente(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('docentes:login')

    docente = Docente.objects.get(usuario__id=usuario_id)
    return render(request, 'docentes/dashboard.html', {'docente': docente})

def logout(request):
    request.session.flush()
    return redirect('docentes:login')

def perfil_docente(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('docentes:login')

    docente = Docente.objects.get(usuario__id=usuario_id)
    

    comentarios = [
        {"autor": "Estudiante A", "texto": "Excelente docente, explica muy bien."},
        {"autor": "Estudiante B", "texto": "Muy atento y dispuesto a ayudar."},
    ]

    return render(request, 'docentes/perfil.html', {
        'docente': docente,
        'comentarios': comentarios,
    })
