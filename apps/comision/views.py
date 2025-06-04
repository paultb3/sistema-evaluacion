from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Avg
from apps.comision.models import Comision
from apps.evaluacion.models import ModuloPreguntas, Evaluacion, Respuesta
from apps.docentes.models import Docente
from uuid import UUID
from apps.comision.forms import PreguntaModuloForm, PreguntaModulo
from django.contrib import messages


# Create your views here.


def index(request, usuario_id):
    comision = get_object_or_404(Comision, usuario__id=usuario_id)
    
    # Estadísticas generales
    total_docentes = Docente.objects.count()
    total_evaluaciones = Evaluacion.objects.filter(estado='enviada').count()
    total_modulos = ModuloPreguntas.objects.count()
    
    # Evaluaciones recientes
    evaluaciones_recientes = Evaluacion.objects.filter(
        estado='enviada'
    ).select_related('docente').order_by('-fecha')[:5]
    
    # Módulos con más preguntas
    modulos_populares = ModuloPreguntas.objects.annotate(
        total_preguntas=Count('preguntamodulo')
    ).order_by('-total_preguntas')[:5]
    
    context = {
        'usuario_id': usuario_id,
        'comision': comision,
        'total_docentes': total_docentes,
        'total_evaluaciones': total_evaluaciones,
        'total_modulos': total_modulos,
        'evaluaciones_recientes': evaluaciones_recientes,
        'modulos_populares': modulos_populares,
    }
    
    return render(request, "bienvenida_comision.html", context)


def perfil_comision(request, usuario_id):
    comision = get_object_or_404(Comision, usuario__id=usuario_id)
    
    # Obtener estadísticas de actividad
    evaluaciones_revisadas = Evaluacion.objects.filter(
        estado='enviada'
    ).count()
    
    # Obtener preguntas creadas por la comisión
    preguntas_creadas = PreguntaModulo.objects.count()
    
    context = {
        'comision': comision,
        'usuario_id': usuario_id,
        'evaluaciones_revisadas': evaluaciones_revisadas,
        'preguntas_creadas': preguntas_creadas,
    }
    
    return render(request, "perfil_comision.html", context)


def realizar_encuesta(request, usuario_id):
    modulos = ModuloPreguntas.objects.prefetch_related("preguntamodulo_set").all()

    print(f"modulos: {modulos}")
    return render(
        request,
        "realizar_encuesta.html",
        {"modulos": modulos, "usuario_id": usuario_id},
    )


def editar_pregunta(request, id_pregunta, usuario_id):
    comision = get_object_or_404(Comision, usuario__id=usuario_id)
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
    
    if request.method == "POST":
        pregunta.delete()
        messages.success(request, "Pregunta eliminada exitosamente.")
    return redirect("comision:realizar_encuesta", usuario_id=usuario_id)
    
    context = {
        'usuario_id': usuario_id,
        'comision': comision,
        'pregunta': pregunta,
    }
    
    return render(request, "confirmar_eliminar_pregunta.html", context)


def agregar_pregunta(request, id_modulo, usuario_id):
    comision = get_object_or_404(Comision, usuario__id=usuario_id)
    modulo = get_object_or_404(ModuloPreguntas, id_modulo=id_modulo)
    
    if request.method == "POST":
        form = PreguntaModuloForm(request.POST)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.id_modulo = modulo
            pregunta.save()
            messages.success(request, "Pregunta agregada exitosamente.")
            return redirect("comision:realizar_encuesta", usuario_id=usuario_id)
    else:
        form = PreguntaModuloForm()
    
    context = {
        'form': form,
        'modulo': modulo,
        'usuario_id': usuario_id,
        'comision': comision,
    }
    
    return render(request, "agregar_pregunta.html", context)
