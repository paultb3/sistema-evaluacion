from django.shortcuts import render, redirect
from apps.comision.models import Comision
from apps.evaluacion.models import ModuloPreguntas
from uuid import UUID
from apps.comision.forms import PreguntaModuloForm, PreguntaModulo
from django.shortcuts import get_object_or_404, HttpResponse
from uuid import UUID


# Create your views here.


usuario_id = UUID("64237ce1-a65e-45b4-a410-4c2222545ae5")


def index(request, usuario_id):
    print(f"Usuario recibido: {usuario_id}")
    if Comision.objects.filter(usuario_id=usuario_id).exists():
        return render(request, "bienvenida_comision.html", {"usuario_id": usuario_id})
    else:
        return HttpResponse("No existe el usuario")


def perfil(request, usuario_id):
    print(f"Usuario recibido: {usuario_id}")
    if usuario_id:
        try:
            usuario_id = usuario_id
        except ValueError:
            return HttpResponse("ID de usuario no válido")
    else:
        return HttpResponse("No se proporcionó ID de usuario")

    list_comision = Comision.objects.filter(usuario_id=usuario_id)

    return render(
        request, "perfil.html", {"comision": list_comision, "usuario_id": usuario_id}
    )


def realizar_encuesta(request):
    modulos = ModuloPreguntas.objects.prefetch_related("preguntamodulo_set").all()
    return render(request, "realizar_encuesta.html", {"modulos": modulos})


def editar_pregunta(request, id_pregunta):
    pregunta = get_object_or_404(PreguntaModulo, id_pregunta=id_pregunta)
    form = PreguntaModuloForm(request.POST or None, instance=pregunta)
    if form.is_valid():
        form.save()
        return redirect("comision:realizar_encuesta")  # o al lugar que desees
    return render(request, "editar_pregunta.html", {"form": form})


def eliminar_pregunta(request, id_pregunta):
    pregunta = get_object_or_404(PreguntaModulo, id_pregunta=id_pregunta)
    pregunta.delete()
    return redirect("comision:realizar_encuesta")


def agregar_pregunta(request, id_modulo):
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

    return render(request, "agregar_pregunta.html", {"form": form, "modulo": modulo})
