from django.shortcuts import render, redirect
from apps.comision.models import Comision
from apps.evaluacion.models import ModuloPreguntas
from uuid import UUID
from apps.comision.forms import PreguntaModuloForm, PreguntaModulo
from django.shortcuts import get_object_or_404, HttpResponse
from uuid import UUID


# Create your views here.


def index(request, usuario_id):
    print(f"Usuario recibido: {usuario_id}")

    return render(request, "bienvenida_comision.html", {"usuario_id": usuario_id})


def perfil_comision(request, usuario_id):
    print(f"Usuario recibido: {usuario_id}")
    comision = get_object_or_404(Comision, usuario__id=usuario_id)
    print(f"Comisiones encontradas: {comision}")

    return render(
        request,
        "perfil_comision.html",
        {"comision": comision, "usuario_id": usuario_id},
    )


def realizar_encuesta(request, usuario_id):
    modulos = ModuloPreguntas.objects.prefetch_related("preguntamodulo_set").all()

    print(f"modulos: {modulos}")
    return render(
        request,
        "realizar_encuesta.html",
        {"modulos": modulos, "usuario_id": usuario_id},
    )


def editar_pregunta(request, id_pregunta, usuario_id):
    pregunta = get_object_or_404(PreguntaModulo, id_pregunta=id_pregunta)
    form = PreguntaModuloForm(request.POST or None, instance=pregunta)
    if form.is_valid():
        form.save()
        return redirect("comision:realizar_encuesta")
    return render(
        request,
        "editar_pregunta.html",
        {"form": form, "usuario_id": usuario_id},
    )


def eliminar_pregunta(request, id_pregunta, usuario_id):
    pregunta = get_object_or_404(PreguntaModulo, id_pregunta=id_pregunta)
    pregunta.delete()
    return redirect("comision:realizar_encuesta", usuario_id=usuario_id)


def agregar_pregunta(request, id_modulo, usuario_id):
    modulo = get_object_or_404(ModuloPreguntas, id_modulo=id_modulo)

    if request.method == "POST":
        form = PreguntaModuloForm(request.POST)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.id_modulo = modulo
            pregunta.save()
            return redirect("comision:realizar_encuesta")
    else:
        form = PreguntaModuloForm()

    return render(
        request,
        "agregar_pregunta.html",
        {"form": form, "modulo": modulo, "usuario_id": usuario_id},
    )
