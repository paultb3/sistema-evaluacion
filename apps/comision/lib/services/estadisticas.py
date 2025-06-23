"""
Servicio para el cálculo de estadísticas de evaluación.
"""

from typing import Dict, Optional
from django.db.models import Count, Avg, Q
from django.utils import timezone
from apps.evaluacion.models import (
    PeriodoEvaluacion,
    Evaluacion,
    Respuesta,
    ModuloPreguntas,
)
from apps.docentes.models import Docente
from apps.alumnos.models import Estudiante
from apps.core.models import Curso


class EstadisticasService:
    """Servicio para calcular estadísticas de evaluación."""

    @staticmethod
    def calcular_estadisticas_periodo(periodo: Optional[PeriodoEvaluacion]) -> Dict:
        """
        Calcula las estadísticas completas para un periodo.

        Args:
            periodo: Instancia del periodo de evaluación

        Returns:
            Diccionario con estadísticas del periodo
        """
        if not periodo:
            return {
                "total_estudiantes": 0,
                "evaluaciones_completadas": 0,
                "dias_restantes": 0,
                "dias_habiles_restantes": 0,
                "docentes_evaluados": "0/0",
                "progreso": 0,
                "progreso_dias_habiles": 0,
            }

        # Importar aquí para evitar importaciones circulares
        from apps.comision.lib.utils.fechas import calcular_dias_restantes
        from apps.comision.lib.utils.dias_habiles import calcular_dias_habiles_restantes

        # Estudiantes totales (esto debería venir de la base de datos en un sistema real)
        total_estudiantes = Estudiante.objects.count() or 320  # Valor por defecto

        # Evaluaciones completadas en este periodo
        evaluaciones = Evaluacion.objects.filter(
            fecha__range=(periodo.fecha_inicio, periodo.fecha_fin), estado="enviada"
        )
        evaluaciones_completadas = evaluaciones.count()

        # Días restantes
        dias_restantes = calcular_dias_restantes(periodo.fecha_fin)
        dias_habiles_restantes = calcular_dias_habiles_restantes(periodo.fecha_fin)

        # Docentes evaluados
        docentes_evaluados = evaluaciones.values("docente").distinct().count()
        total_docentes = Docente.objects.count()
        docentes_evaluados_str = f"{docentes_evaluados}/{total_docentes}"

        # Calcular progreso
        progreso = 0
        if total_estudiantes > 0:
            progreso = min(
                100, int((evaluaciones_completadas / total_estudiantes) * 100)
            )

        return {
            "total_estudiantes": total_estudiantes,
            "evaluaciones_completadas": evaluaciones_completadas,
            "dias_restantes": dias_restantes,
            "dias_habiles_restantes": dias_habiles_restantes,
            "docentes_evaluados": docentes_evaluados_str,
            "progreso": progreso,
        }

    @staticmethod
    def get_estadisticas_generales() -> Dict:
        """
        Obtiene estadísticas generales del sistema.

        Returns:
            Diccionario con estadísticas generales
        """
        return {
            "total_docentes": Docente.objects.count(),
            "total_estudiantes": Estudiante.objects.count(),
            "total_evaluaciones": Evaluacion.objects.filter(estado="enviada").count(),
            "total_modulos": ModuloPreguntas.objects.count(),
            "total_cursos": Curso.objects.count(),
            "periodos_activos": PeriodoEvaluacion.objects.filter(
                fecha_inicio__lte=timezone.now().date(),
                fecha_fin__gte=timezone.now().date(),
            ).count(),
        }

    @staticmethod
    def get_estadisticas_periodos(periodos_activos, periodos_pasados, hoy) -> Dict:
        """
        Obtiene estadísticas específicas de períodos.

        Args:
            periodos_activos: QuerySet de períodos activos
            periodos_pasados: QuerySet de períodos pasados
            hoy: Fecha actual

        Returns:
            Diccionario con estadísticas de períodos
        """
        total_periodos = periodos_activos.count() + periodos_pasados.count()
        proximos_periodos = periodos_activos.filter(fecha_inicio__gt=hoy).count()
        periodos_en_curso = periodos_activos.filter(fecha_inicio__lte=hoy).count()

        return {
            "total_periodos": total_periodos,
            "proximos_periodos": proximos_periodos,
            "periodos_en_curso": periodos_en_curso,
        }

    @staticmethod
    def get_estadisticas_evaluacion(
        periodo: Optional[PeriodoEvaluacion], info_dias_habiles: Dict
    ) -> Dict:
        """
        Obtiene estadísticas completas de evaluación para un período.

        Args:
            periodo: Instancia del período de evaluación
            info_dias_habiles: Información sobre días hábiles

        Returns:
            Diccionario con estadísticas de evaluación
        """
        if not periodo:
            return {}

        # Estudiantes totales (estimado)
        total_estudiantes = 320  # En un sistema real, esto vendría de la base de datos

        # Evaluaciones completadas en este periodo
        evaluaciones = Evaluacion.objects.filter(
            fecha__range=(periodo.fecha_inicio, periodo.fecha_fin), estado="enviada"
        )
        evaluaciones_completadas = evaluaciones.count()

        # Días restantes (calendario y hábiles)
        from apps.comision.lib.utils.fechas import calcular_dias_restantes

        dias_restantes = calcular_dias_restantes(periodo.fecha_fin)
        dias_habiles_restantes = info_dias_habiles["dias_habiles_restantes"]

        # Docentes evaluados
        docentes_evaluados = evaluaciones.values("docente").distinct().count()
        total_docentes = Docente.objects.count()
        docentes_evaluados_str = f"{docentes_evaluados}/{total_docentes}"

        # Calcular progreso (basado en días calendario y días hábiles)
        progreso = 0
        if total_estudiantes > 0:
            progreso = min(
                100, int((evaluaciones_completadas / total_estudiantes) * 100)
            )

        # Progreso basado en días hábiles
        progreso_dias_habiles = info_dias_habiles["progreso_dias_habiles"]

        return {
            "total_estudiantes": total_estudiantes,
            "evaluaciones_completadas": evaluaciones_completadas,
            "dias_restantes": dias_restantes,
            "dias_habiles_restantes": dias_habiles_restantes,
            "docentes_evaluados": docentes_evaluados_str,
            "progreso": progreso,
            "progreso_dias_habiles": progreso_dias_habiles,
        }

    @staticmethod
    def get_reporte_general() -> Dict:
        """
        Obtiene datos para el reporte general.

        Returns:
            Diccionario con datos del reporte general
        """
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
                filter=Q(evaluacion__estado="enviada"),
            )
        ).order_by("-promedio")[:5]

        # Top 5 cursos mejor calificados
        mejores_cursos = Curso.objects.annotate(
            promedio=Avg(
                "evaluacion__respuestas__puntuacion",
                filter=Q(evaluacion__estado="enviada"),
            )
        ).order_by("-promedio")[:5]

        # Distribución de calificaciones
        distribucion = (
            Respuesta.objects.filter(evaluacion__estado="enviada")
            .values("puntuacion")
            .annotate(total=Count("id"))
            .order_by("puntuacion")
        )

        return {
            "promedio_general": promedio_general,
            "mejores_docentes": mejores_docentes,
            "mejores_cursos": mejores_cursos,
            "distribucion": distribucion,
        }

    @staticmethod
    def get_reporte_cursos():
        """
        Obtiene datos para el reporte de cursos.

        Returns:
            QuerySet de cursos con estadísticas calculadas
        """
        # Obtener todos los cursos con sus evaluaciones
        cursos = (
            Curso.objects.prefetch_related(
                "evaluacion_set", "evaluacion_set__respuestas"
            )
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
                    evaluacion.respuestas.aggregate(promedio=Avg("puntuacion"))[
                        "promedio"
                    ]
                    or 0
                )

        return cursos

    @staticmethod
    def get_reporte_docentes():
        """
        Obtiene datos para el reporte de docentes.

        Returns:
            QuerySet de docentes con estadísticas calculadas
        """
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

        return docentes

    @staticmethod
    def calcular_progreso_evaluaciones(periodo: PeriodoEvaluacion) -> Dict:
        """
        Calcula el progreso detallado de evaluaciones.

        Args:
            periodo: Instancia del periodo de evaluación

        Returns:
            Diccionario con progreso detallado
        """
        if not periodo:
            return {"porcentaje": 0, "completadas": 0, "pendientes": 0}

        evaluaciones = Evaluacion.objects.filter(
            fecha__range=(periodo.fecha_inicio, periodo.fecha_fin)
        )

        completadas = evaluaciones.filter(estado="enviada").count()
        total_posibles = EstadisticasService._calcular_evaluaciones_posibles(periodo)
        pendientes = max(0, total_posibles - completadas)

        porcentaje = 0
        if total_posibles > 0:
            porcentaje = int((completadas / total_posibles) * 100)

        return {
            "porcentaje": porcentaje,
            "completadas": completadas,
            "pendientes": pendientes,
            "total_posibles": total_posibles,
        }

    @staticmethod
    def _calcular_evaluaciones_posibles(periodo: PeriodoEvaluacion) -> int:
        """
        Calcula el número total de evaluaciones posibles para un periodo.

        Args:
            periodo: Instancia del periodo de evaluación

        Returns:
            Número total de evaluaciones posibles
        """
        # En un sistema real, esto sería más complejo
        # considerando cursos activos, estudiantes matriculados, etc.
        total_estudiantes = Estudiante.objects.count()
        total_docentes = Docente.objects.count()

        # Estimación simple: cada estudiante puede evaluar a cada docente
        # En la realidad sería más específico por cursos
        return (
            total_estudiantes * total_docentes
            if total_estudiantes and total_docentes
            else 0
        )
