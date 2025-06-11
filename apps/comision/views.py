from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Avg
from apps.comision.models import Comision
from apps.evaluacion.models import (
    ModuloPreguntas,
    Evaluacion,
    Respuesta,
    PeriodoEvaluacion,
)
from apps.docentes.models import Docente
from apps.core.models import Curso
from uuid import UUID
from apps.comision.forms import (
    PreguntaModuloForm,
    PreguntaModulo,
    PeriodoEvaluacionForm,
)
from django.contrib import messages
from django.db import models
from datetime import datetime, timedelta, date
from django.utils import timezone


# Helper functions for period management
def calcular_dias_restantes(fecha_fin):
    """Calculate remaining days until the end date"""
    if fecha_fin and fecha_fin >= date.today():
        return (fecha_fin - date.today()).days
    return 0


def calcular_dias_habiles(fecha_inicio, fecha_fin):
    """Calculate business days between two dates (excluding weekends)"""
    if not fecha_inicio or not fecha_fin:
        return 0

    current_date = fecha_inicio
    dias_habiles = 0

    while current_date <= fecha_fin:
        # Monday = 0, Sunday = 6
        if current_date.weekday() < 5:  # Monday to Friday
            dias_habiles += 1
        current_date += timedelta(days=1)

    return dias_habiles


def calcular_dias_habiles_restantes(fecha_fin):
    """Calculate remaining business days until the end date"""
    if not fecha_fin or fecha_fin < date.today():
        return 0

    return calcular_dias_habiles(date.today(), fecha_fin)


def calcular_progreso_dias_habiles(periodo):
    """Calculate progress based on business days"""
    if not periodo:
        return 0

    total_dias_habiles = calcular_dias_habiles(periodo.fecha_inicio, periodo.fecha_fin)
    if total_dias_habiles == 0:
        return 100

    hoy = date.today()
    if hoy < periodo.fecha_inicio:
        return 0
    elif hoy > periodo.fecha_fin:
        return 100

    dias_habiles_transcurridos = calcular_dias_habiles(periodo.fecha_inicio, hoy)
    return min(100, int((dias_habiles_transcurridos / total_dias_habiles) * 100))


def get_informacion_dias_habiles(periodo):
    """Get comprehensive business days information for a period"""
    if not periodo:
        return {
            "total_dias_habiles": 0,
            "dias_habiles_transcurridos": 0,
            "dias_habiles_restantes": 0,
            "progreso_dias_habiles": 0,
            "es_dia_habil": False,
        }

    hoy = date.today()
    total_dias_habiles = calcular_dias_habiles(periodo.fecha_inicio, periodo.fecha_fin)
    dias_habiles_transcurridos = calcular_dias_habiles(
        periodo.fecha_inicio, min(hoy, periodo.fecha_fin)
    )
    dias_habiles_restantes = calcular_dias_habiles_restantes(periodo.fecha_fin)
    progreso_dias_habiles = calcular_progreso_dias_habiles(periodo)
    es_dia_habil = hoy.weekday() < 5  # Monday to Friday

    return {
        "total_dias_habiles": total_dias_habiles,
        "dias_habiles_transcurridos": dias_habiles_transcurridos,
        "dias_habiles_restantes": dias_habiles_restantes,
        "progreso_dias_habiles": progreso_dias_habiles,
        "es_dia_habil": es_dia_habil,
        "dia_semana": [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo",
        ][hoy.weekday()],
    }


def get_periodo_status(periodo, fecha_actual):
    """Get the status label and CSS classes for a period"""
    if not periodo:
        return (
            "Sin periodo",
            "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400",
        )

    estado = periodo.estado
    if estado == "activo":
        return (
            "Período de evaluación activo",
            "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
        )
    elif estado == "pendiente":
        return (
            "Pendiente de inicio",
            "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
        )
    elif estado == "revision":
        return (
            "En revisión por comisión",
            "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
        )
    else:
        return (
            "Proceso cerrado",
            "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400",
        )


def get_comision_status(periodo, fecha_actual):
    """Get the commission meeting status"""
    if not periodo:
        return ("Sin periodo", "text-gray-500 dark:text-gray-400")

    if fecha_actual > periodo.fecha_fin and fecha_actual <= periodo.fecha_cierre:
        return ("En revisión", "text-amber-600 dark:text-amber-400")
    elif fecha_actual > periodo.fecha_cierre:
        return ("Completada", "text-green-600 dark:text-green-400")
    else:
        return ("Pendiente", "text-gray-500 dark:text-gray-400")


def get_publication_status(periodo, fecha_actual):
    """Get the publication status"""
    if not periodo:
        return ("Sin periodo", "text-gray-500 dark:text-gray-400")

    if fecha_actual > periodo.fecha_cierre:
        return ("Publicado", "text-green-600 dark:text-green-400")
    else:
        return ("Pendiente", "text-gray-500 dark:text-gray-400")


# Create your views here.


def index(request, usuario_id):
    comision = get_object_or_404(Comision, usuario__id=usuario_id)

    # Estadísticas generales
    total_docentes = Docente.objects.count()
    total_evaluaciones = Evaluacion.objects.filter(estado="enviada").count()
    total_modulos = ModuloPreguntas.objects.count()

    # Evaluaciones recientes
    evaluaciones_recientes = (
        Evaluacion.objects.filter(estado="enviada")
        .select_related("docente")
        .order_by("-fecha")[:5]
    )

    # Módulos con más preguntas
    modulos_populares = ModuloPreguntas.objects.annotate(
        total_preguntas=Count("preguntamodulo")
    ).order_by("-total_preguntas")[:5]

    context = {
        "usuario_id": usuario_id,
        "comision": comision,
        "total_docentes": total_docentes,
        "total_evaluaciones": total_evaluaciones,
        "total_modulos": total_modulos,
        "evaluaciones_recientes": evaluaciones_recientes,
        "modulos_populares": modulos_populares,
    }

    return render(request, "bienvenida_comision.html", context)


def perfil_comision(request, usuario_id):
    comision = get_object_or_404(Comision, usuario__id=usuario_id)

    # Obtener estadísticas de actividad
    evaluaciones_revisadas = Evaluacion.objects.filter(estado="enviada").count()

    # Obtener preguntas creadas por la comisión
    preguntas_creadas = PreguntaModulo.objects.count()

    context = {
        "comision": comision,
        "usuario_id": usuario_id,
        "evaluaciones_revisadas": evaluaciones_revisadas,
        "preguntas_creadas": preguntas_creadas,
    }

    return render(request, "perfil_comision.html", context)


# Nueva función para gestionar los periodos de evaluación
def gestionar_periodos(request, usuario_id):
    """Vista para administrar los periodos de evaluación"""
    comision = get_object_or_404(Comision, usuario__id=usuario_id)

    # Obtener periodos activos y pasados
    hoy = timezone.now().date()
    periodos_activos = PeriodoEvaluacion.objects.filter(fecha_fin__gte=hoy).order_by(
        "fecha_inicio"
    )
    periodos_pasados = PeriodoEvaluacion.objects.filter(fecha_fin__lt=hoy).order_by(
        "-fecha_inicio"
    )

    # Estadísticas de periodos
    total_periodos = periodos_activos.count() + periodos_pasados.count()
    proximos_periodos = periodos_activos.filter(fecha_inicio__gt=hoy).count()
    periodos_en_curso = periodos_activos.filter(
        fecha_inicio__lte=hoy
    ).count()  # Obtener periodo actual (si existe)
    periodo_actual = None
    info_dias_habiles_actual = None
    if periodos_activos.filter(fecha_inicio__lte=hoy).exists():
        periodo_actual = periodos_activos.filter(fecha_inicio__lte=hoy).first()

        # Calcular progreso
        duracion_total = (periodo_actual.fecha_fin - periodo_actual.fecha_inicio).days
        dias_transcurridos = (hoy - periodo_actual.fecha_inicio).days
        if duracion_total > 0:  # Evitar división por cero
            periodo_actual.progreso = min(
                100, int((dias_transcurridos / duracion_total) * 100)
            )
        else:
            periodo_actual.progreso = 100

        # Días restantes (calendario)
        periodo_actual.dias_restantes = max(0, (periodo_actual.fecha_fin - hoy).days)

        # Información sobre días hábiles
        info_dias_habiles_actual = get_informacion_dias_habiles(periodo_actual)

        # Obtener evaluaciones de este periodo
        evaluaciones = Evaluacion.objects.filter(
            fecha__range=(periodo_actual.fecha_inicio, periodo_actual.fecha_fin),
            estado="enviada",
        )
        periodo_actual.total_evaluaciones = evaluaciones.count()

    context = {
        "usuario_id": usuario_id,
        "comision": comision,
        "periodos_activos": periodos_activos,
        "periodos_pasados": periodos_pasados,
        "total_periodos": total_periodos,
        "proximos_periodos": proximos_periodos,
        "periodos_en_curso": periodos_en_curso,
        "periodo_actual": periodo_actual,
        "info_dias_habiles_actual": info_dias_habiles_actual,
        "hoy": hoy,
    }

    return render(request, "encuestas_comision/gestionar_periodos.html", context)


# Nueva función para crear un periodo de evaluación
def crear_periodo(request, usuario_id):
    """Vista para crear un nuevo periodo de evaluación"""
    comision = get_object_or_404(Comision, usuario__id=usuario_id)

    if request.method == "POST":
        form = PeriodoEvaluacionForm(request.POST)
        if form.is_valid():
            periodo = form.save(commit=False)
            # Calcular automáticamente la fecha de reunión de comisión (3 días después del fin)
            periodo.fecha_comision = periodo.fecha_fin + timedelta(days=3)
            # Calcular automáticamente la fecha de cierre (5 días después del fin)
            periodo.fecha_cierre = periodo.fecha_fin + timedelta(days=5)
            # Establecer el estado inicial
            if periodo.fecha_inicio <= timezone.now().date():
                periodo.estado = "activo"
            else:
                periodo.estado = "pendiente"

            periodo.save()
            messages.success(request, "Periodo de evaluación creado exitosamente.")
            return redirect("comision:gestionar_periodos", usuario_id=usuario_id)
    else:
        # Valores predeterminados: inicio en la fecha actual, fin en 15 días
        fecha_inicio_default = timezone.now().date()
        fecha_fin_default = fecha_inicio_default + timedelta(days=15)
        form = PeriodoEvaluacionForm(
            initial={
                "fecha_inicio": fecha_inicio_default,
                "fecha_fin": fecha_fin_default,
            }
        )

    context = {
        "form": form,
        "usuario_id": usuario_id,
        "comision": comision,
    }

    return render(request, "encuestas_comision/crear_periodo.html", context)


# Nueva función para configurar un periodo de evaluación existente
def configurar_periodo(request, periodo_id, usuario_id):
    """Vista para configurar un periodo de evaluación existente"""
    comision = get_object_or_404(Comision, usuario__id=usuario_id)
    periodo = get_object_or_404(PeriodoEvaluacion, id=periodo_id)

    if request.method == "POST":
        form = PeriodoEvaluacionForm(request.POST, instance=periodo)
        if form.is_valid():
            periodo = form.save(commit=False)
            # Actualizar fechas de comisión y cierre si cambiaron las fechas principales
            periodo.fecha_comision = periodo.fecha_fin + timedelta(days=3)
            periodo.fecha_cierre = periodo.fecha_fin + timedelta(days=5)
            periodo.save()
            messages.success(request, "Periodo de evaluación actualizado exitosamente.")
            return redirect("comision:gestionar_periodos", usuario_id=usuario_id)
    else:
        form = PeriodoEvaluacionForm(instance=periodo)

    context = {
        "form": form,
        "periodo": periodo,
        "usuario_id": usuario_id,
        "comision": comision,
    }

    return render(request, "encuestas_comision/configurar_periodo.html", context)


# Nueva función para seleccionar el tipo de encuesta
def seleccionar_tipo_encuesta(request, periodo_id, usuario_id):
    """Vista para seleccionar si crear una encuesta nueva o usar una existente"""
    comision = get_object_or_404(Comision, usuario__id=usuario_id)
    periodo = get_object_or_404(PeriodoEvaluacion, id=periodo_id)

    context = {
        "usuario_id": usuario_id,
        "comision": comision,
        "periodo": periodo,
    }

    return render(request, "encuestas_comision/seleccionar_tipo_encuesta.html", context)


# Modificado para trabajar con un periodo de evaluación específico
def realizar_encuesta(request, usuario_id, periodo_id=None):
    """Vista para gestionar las preguntas de los módulos de evaluación"""

    # Obtener el periodo si se proporciona un ID, de lo contrario obtener el periodo activo
    periodo = None
    if periodo_id:
        periodo = get_object_or_404(PeriodoEvaluacion, id=periodo_id)
    else:
        # Intentar obtener un periodo activo
        hoy = timezone.now().date()
        periodos_activos = PeriodoEvaluacion.objects.filter(
            fecha_inicio__lte=hoy, fecha_fin__gte=hoy
        )
        if periodos_activos.exists():
            periodo = periodos_activos.first()

    # Get current date
    fecha_actual = (
        timezone.now().date()
    )  # Calculate status information using helper functions
    dias_restantes = calcular_dias_restantes(periodo.fecha_fin) if periodo else 0
    status_label, status_color = get_periodo_status(periodo, fecha_actual)
    comision_status, comision_color = get_comision_status(periodo, fecha_actual)
    publication_status, publication_color = get_publication_status(
        periodo, fecha_actual
    )

    # Obtener información detallada sobre días hábiles
    info_dias_habiles = get_informacion_dias_habiles(periodo)

    # Obtener los módulos disponibles
    modulos = ModuloPreguntas.objects.prefetch_related("preguntamodulo_set").all()

    # Calcular estadísticas si hay un periodo activo
    estadisticas = {}
    if periodo:
        # Estudiantes totales (estimado)
        estadisticas["total_estudiantes"] = (
            320  # En un sistema real, esto vendría de la base de datos
        )

        # Evaluaciones completadas en este periodo
        evaluaciones = Evaluacion.objects.filter(
            fecha__range=(periodo.fecha_inicio, periodo.fecha_fin), estado="enviada"
        )
        estadisticas["evaluaciones_completadas"] = evaluaciones.count()

        # Días restantes (calendario y hábiles)
        estadisticas["dias_restantes"] = dias_restantes
        estadisticas["dias_habiles_restantes"] = info_dias_habiles[
            "dias_habiles_restantes"
        ]

        # Docentes evaluados
        docentes_evaluados = evaluaciones.values("docente").distinct().count()
        total_docentes = Docente.objects.count()
        estadisticas["docentes_evaluados"] = f"{docentes_evaluados}/{total_docentes}"

        # Calcular progreso (basado en días calendario y días hábiles)
        if estadisticas["total_estudiantes"] > 0:
            estadisticas["progreso"] = min(
                100,
                int(
                    (
                        estadisticas["evaluaciones_completadas"]
                        / estadisticas["total_estudiantes"]
                    )
                    * 100
                ),
            )
        else:
            estadisticas["progreso"] = 0

        # Progreso basado en días hábiles
        estadisticas["progreso_dias_habiles"] = info_dias_habiles[
            "progreso_dias_habiles"
        ]

    context = {
        "modulos": modulos,
        "usuario_id": usuario_id,
        "periodo": periodo,
        "estadisticas": estadisticas,
        "fecha_actual": fecha_actual,
        "dias_restantes": dias_restantes,
        "info_dias_habiles": info_dias_habiles,
        "status_label": status_label,
        "status_color": status_color,
        "comision_status": comision_status,
        "comision_color": comision_color,
        "publication_status": publication_status,
        "publication_color": publication_color,
    }

    return render(request, "realizar_encuesta.html", context)


def editar_pregunta(request, id_pregunta, usuario_id):
    comision = get_object_or_404(Comision, usuario__id=usuario_id)
    pregunta = get_object_or_404(PreguntaModulo, id_pregunta=id_pregunta)
    form = PreguntaModuloForm(request.POST or None, instance=pregunta)
    if form.is_valid():
        form.save()
        return redirect("comision:realizar_encuesta", usuario_id=usuario_id)
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
        "usuario_id": usuario_id,
        "comision": comision,
        "pregunta": pregunta,
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
        "form": form,
        "modulo": modulo,
        "usuario_id": usuario_id,
        "comision": comision,
    }

    return render(request, "agregar_pregunta.html", context)


def reporter_general(request, usuario_id):
    # Estadísticas generales
    total_docentes = Docente.objects.count()
    total_cursos = Curso.objects.count()
    total_evaluaciones = Evaluacion.objects.filter(estado="enviada").count()

    # Promedio general de calificaciones usando las respuestas
    promedio_general = (
        Evaluacion.objects.filter(estado="enviada")
        .annotate(promedio_respuestas=Avg("respuestas__puntuacion"))
        .aggregate(promedio=Avg("promedio_respuestas"))["promedio"]
        or 0
    )

    # Top 5 docentes mejor calificados
    mejores_docentes = Docente.objects.annotate(
        promedio=Avg(
            "evaluacion__respuestas__puntuacion",
            filter=models.Q(evaluacion__estado="enviada"),
        )
    ).order_by("-promedio")[:5]

    for docente in mejores_docentes:
        print(docente)

    # Top 5 cursos mejor calificados
    mejores_cursos = Curso.objects.annotate(
        promedio=Avg(
            "evaluacion__respuestas__puntuacion",
            filter=models.Q(evaluacion__estado="enviada"),
        )
    ).order_by("-promedio")[:5]

    # Distribución de calificaciones
    distribucion = (
        Respuesta.objects.filter(evaluacion__estado="enviada")
        .values("puntuacion")
        .annotate(total=Count("id"))
        .order_by("puntuacion")
    )

    context = {
        "usuario_id": usuario_id,
        "total_docentes": total_docentes,
        "total_cursos": total_cursos,
        "total_evaluaciones": total_evaluaciones,
        "promedio_general": promedio_general,
        "mejores_docentes": mejores_docentes,
        "mejores_cursos": mejores_cursos,
        "distribucion": distribucion,
    }
    return render(request, "reportes/reporte_general.html", context)


def reporte_curso(request, usuario_id):
    # Obtener todos los cursos con sus evaluaciones
    cursos = (
        Curso.objects.prefetch_related("evaluacion_set", "evaluacion_set__respuestas")
        .select_related("docente")
        .all()
    )

    # Para cada curso, calcular estadísticas
    for curso in cursos:
        # Obtener evaluaciones del curso
        evaluaciones = curso.evaluacion_set.filter(estado="enviada")

        # Calcular promedio de calificaciones usando las respuestas
        curso.promedio_calificacion = (
            evaluaciones.annotate(
                promedio_respuestas=Avg("respuestas__puntuacion")
            ).aggregate(promedio=Avg("promedio_respuestas"))["promedio"]
            or 0
        )

        # Contar total de evaluaciones
        curso.total_evaluaciones = evaluaciones.count()

        # Calcular calificación para cada evaluación
        for evaluacion in evaluaciones:
            evaluacion.calificacion = (
                evaluacion.respuestas.aggregate(promedio=Avg("puntuacion"))["promedio"]
                or 0
            )

    context = {
        "usuario_id": usuario_id,
        "cursos": cursos,
    }
    return render(request, "reportes/reporte_curso.html", context)


def reporte_docente(request, usuario_id):
    # Obtener todos los docentes con sus evaluaciones y cursos
    docentes = Docente.objects.prefetch_related("evaluacion_set", "curso_set").all()

    # Para cada docente, calcular estadísticas
    for docente in docentes:
        # Obtener evaluaciones del docente
        evaluaciones = docente.evaluacion_set.filter(estado="enviada")

        # Calcular promedio de calificaciones usando las respuestas
        docente.promedio_calificacion = (
            evaluaciones.annotate(
                promedio_respuestas=Avg("respuestas__puntuacion")
            ).aggregate(promedio=Avg("promedio_respuestas"))["promedio"]
            or 0
        )

        # Contar total de evaluaciones
        docente.total_evaluaciones = evaluaciones.count()

        # Obtener cursos del docente
        docente.cursos = docente.curso_set.all()

    context = {
        "usuario_id": usuario_id,
        "docentes": docentes,
    }
    return render(request, "reportes/reporte_docente.html", context)
