from django.shortcuts import render, get_object_or_404
from apps.alumnos.models import Estudiante
from apps.evaluacion.models import PreguntaModulo


def bienvenida_alumnos(request, usuario_id):
    print(f"Usuario recibido: {usuario_id}")
    return render(request, "bienvenida_alumno.html", {"usuario_id": usuario_id})


def perfil_alumno(request, usuario_id):
    print(f"Usuario recibido: {usuario_id}")

    alumno = get_object_or_404(Estudiante, usuario__id=usuario_id)

    print(f"Alumno encontrado: {alumno}")
    return render(
        request, "perfil_alumno.html", {"usuario_id": usuario_id, "alumno": alumno}
    )


def evaluar_docente(request, usuario_id):
    print(f"Usuario recibido: {usuario_id}")
    alumno = get_object_or_404(Estudiante, usuario__id=usuario_id)
    modulo = PreguntaModulo.objects.all()

    print(f"Alumno encontrado: {alumno}")
    return render(
        request,
        "evaluar_docente.html",
        {"usuario_id": usuario_id, "alumno": alumno, "modulo": modulo},
    )


def explorar(request, usuario_id):
    print(f"Usuario recibido: {usuario_id}")
    modulo = PreguntaModulo.objects.all()

    context = {"modulo": modulo, "usuario_id": usuario_id}
    return render(
        request, "explorar.html", {"usuario_id": usuario_id, "modulo": modulo}
    )
