from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Avg
from apps.comision.models import Comision
from apps.evaluacion.models import (
    ModuloPreguntas,
    Evaluacion,
    Respuesta,
    PeriodoEvaluacion,
)
from apps.comision.forms import (
    PreguntaModuloForm,
    PreguntaModulo,
    PeriodoEvaluacionForm,
)
from django.contrib import messages
from django.utils import timezone

# Import our new modularized helpers and services
from apps.comision.lib.utils.dias_habiles import (
    calcular_dias_habiles,
    calcular_dias_habiles_restantes,
    calcular_progreso_dias_habiles,
    get_informacion_dias_habiles,
)
from apps.comision.lib.utils.fechas import calcular_dias_restantes
from apps.comision.lib.services.periodo_status import PeriodoStatusService
from apps.comision.lib.services.estadisticas import EstadisticasService
from apps.comision.lib.helpers.context import ContextHelper
from apps.comision.lib.helpers.validaciones import ValidacionHelper


# Create your views here.


def index(request, usuario_id):
    comision = get_object_or_404(Comision, usuario__id=usuario_id)

    # Use statistics service
    estadisticas_service = EstadisticasService()
    estadisticas_generales = estadisticas_service.get_estadisticas_generales()

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
        "total_docentes": estadisticas_generales["total_docentes"],
        "total_evaluaciones": estadisticas_generales["total_evaluaciones"],
        "total_modulos": estadisticas_generales["total_modulos"],
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

    # Use statistics service for periods
    estadisticas_service = EstadisticasService()
    estadisticas_periodos = estadisticas_service.get_estadisticas_periodos(
        periodos_activos, periodos_pasados, hoy
    )

    # Obtener periodo actual (si existe)
    periodo_actual = None
    info_dias_habiles_actual = None
    if periodos_activos.filter(fecha_inicio__lte=hoy).exists():
        periodo_actual = periodos_activos.filter(fecha_inicio__lte=hoy).first()

        # Use context helper to prepare period data
        context_helper = ContextHelper()
        periodo_actual = context_helper.preparar_datos_periodo(periodo_actual, hoy)

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
        "total_periodos": estadisticas_periodos["total_periodos"],
        "proximos_periodos": estadisticas_periodos["proximos_periodos"],
        "periodos_en_curso": estadisticas_periodos["periodos_en_curso"],
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

            # Use validation helper
            validacion_helper = ValidacionHelper()
            context_helper = ContextHelper()

            # Validate period dates
            errores = validacion_helper.validar_fechas_periodo(
                periodo.fecha_inicio, periodo.fecha_fin
            )
            if not errores:
                # Calculate automatic dates using context helper
                periodo = context_helper.calcular_fechas_automaticas(periodo)

                # Set initial state
                periodo.estado = context_helper.determinar_estado_inicial(periodo)

                periodo.save()
                messages.success(request, "Periodo de evaluación creado exitosamente.")
                return redirect("comision:gestionar_periodos", usuario_id=usuario_id)
            else:
                for error in errores:
                    messages.error(request, error)
    else:
        # Use context helper for default values
        context_helper = ContextHelper()
        fechas_default = context_helper.get_fechas_default_periodo()
        form = PeriodoEvaluacionForm(initial=fechas_default)

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

            # Use validation helper
            validacion_helper = ValidacionHelper()
            context_helper = ContextHelper()

            # Validate period dates
            errores = validacion_helper.validar_fechas_periodo(
                periodo.fecha_inicio, periodo.fecha_fin
            )
            if not errores:
                # Update automatic dates using context helper
                periodo = context_helper.calcular_fechas_automaticas(periodo)

                periodo.save()
                messages.success(
                    request, "Periodo de evaluación actualizado exitosamente."
                )
                return redirect("comision:gestionar_periodos", usuario_id=usuario_id)
            else:
                for error in errores:
                    messages.error(request, error)
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
    fecha_actual = timezone.now().date()

    # Use services for status and statistics
    periodo_status_service = PeriodoStatusService()
    estadisticas_service = EstadisticasService()

    # Calculate status information using services
    dias_restantes = calcular_dias_restantes(periodo.fecha_fin) if periodo else 0
    status_label, status_color = periodo_status_service.get_periodo_status(
        periodo, fecha_actual
    )
    comision_status, comision_color = periodo_status_service.get_comision_status(
        periodo, fecha_actual
    )
    publication_status, publication_color = (
        periodo_status_service.get_publication_status(periodo, fecha_actual)
    )

    # Obtener información detallada sobre días hábiles
    info_dias_habiles = get_informacion_dias_habiles(periodo)

    # Obtener los módulos disponibles
    modulos = ModuloPreguntas.objects.prefetch_related("preguntamodulo_set").all()

    # Use statistics service for evaluation statistics
    estadisticas = {}
    if periodo:
        estadisticas = estadisticas_service.get_estadisticas_evaluacion(
            periodo, info_dias_habiles
        )

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
    # Use statistics service for general reports
    estadisticas_service = EstadisticasService()

    # Get general statistics
    estadisticas_generales = estadisticas_service.get_estadisticas_generales()

    # Get specific report data
    reporte_data = estadisticas_service.get_reporte_general()

    context = {
        "usuario_id": usuario_id,
        "total_docentes": estadisticas_generales["total_docentes"],
        "total_cursos": estadisticas_generales["total_cursos"],
        "total_evaluaciones": estadisticas_generales["total_evaluaciones"],
        "promedio_general": reporte_data["promedio_general"],
        "mejores_docentes": reporte_data["mejores_docentes"],
        "mejores_cursos": reporte_data["mejores_cursos"],
        "distribucion": reporte_data["distribucion"],
    }
    return render(request, "reportes/reporte_general.html", context)


def reporte_curso(request, usuario_id):
    # Use statistics service for course reports
    estadisticas_service = EstadisticasService()
    cursos_con_estadisticas = estadisticas_service.get_reporte_cursos()

    context = {
        "usuario_id": usuario_id,
        "cursos": cursos_con_estadisticas,
    }
    return render(request, "reportes/reporte_curso.html", context)


def reporte_docente(request, usuario_id):
    # Use statistics service for teacher reports
    estadisticas_service = EstadisticasService()
    docentes_con_estadisticas = estadisticas_service.get_reporte_docentes()

    context = {
        "usuario_id": usuario_id,
        "docentes": docentes_con_estadisticas,
    }
    return render(request, "reportes/reporte_docente.html", context)
