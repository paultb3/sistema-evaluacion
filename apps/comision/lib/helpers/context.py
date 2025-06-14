"""
Helpers para preparar contexto de templates en las vistas de comisión.
"""

from datetime import date
from typing import Dict, Optional
from apps.evaluacion.models import PeriodoEvaluacion
from apps.comision.lib.utils.dias_habiles import get_informacion_dias_habiles
from apps.comision.lib.utils.fechas import calcular_dias_restantes
from apps.comision.lib.services.periodo_status import PeriodoStatusService
from apps.comision.lib.services.estadisticas import EstadisticasService


class ContextHelper:
    """Helper para preparar contexto de templates."""

    @staticmethod
    def get_periodo_context(
        periodo: Optional[PeriodoEvaluacion], usuario_id: str
    ) -> Dict:
        """
        Prepara el contexto completo para un periodo de evaluación.

        Args:
            periodo: Instancia del periodo de evaluación
            usuario_id: ID del usuario actual

        Returns:
            Diccionario con contexto completo para templates
        """
        fecha_actual = date.today()

        # Información básica del periodo
        dias_restantes = calcular_dias_restantes(periodo.fecha_fin) if periodo else 0
        status_label, status_color = PeriodoStatusService.get_periodo_status(
            periodo, fecha_actual
        )
        comision_status, comision_color = PeriodoStatusService.get_comision_status(
            periodo, fecha_actual
        )
        publication_status, publication_color = (
            PeriodoStatusService.get_publication_status(periodo, fecha_actual)
        )

        # Información de días hábiles
        info_dias_habiles = get_informacion_dias_habiles(periodo)

        # Estadísticas del periodo
        estadisticas = EstadisticasService.calcular_estadisticas_periodo(periodo)

        # Agregar progreso de días hábiles a las estadísticas
        if periodo:
            estadisticas["progreso_dias_habiles"] = info_dias_habiles[
                "progreso_dias_habiles"
            ]

        return {
            "usuario_id": usuario_id,
            "periodo": periodo,
            "fecha_actual": fecha_actual,
            "dias_restantes": dias_restantes,
            "status_label": status_label,
            "status_color": status_color,
            "comision_status": comision_status,
            "comision_color": comision_color,
            "publication_status": publication_status,
            "publication_color": publication_color,
            "info_dias_habiles": info_dias_habiles,
            "estadisticas": estadisticas,
        }

    @staticmethod
    def get_gestionar_periodos_context(
        usuario_id: str, comision, periodos_data: Dict
    ) -> Dict:
        """
        Prepara el contexto para la vista de gestionar periodos.

        Args:
            usuario_id: ID del usuario actual
            comision: Instancia de la comisión
            periodos_data: Datos de periodos procesados

        Returns:
            Diccionario con contexto para template de gestionar periodos
        """
        context = {
            "usuario_id": usuario_id,
            "comision": comision,
            "hoy": date.today(),
        }

        # Agregar datos de periodos
        context.update(periodos_data)

        # Agregar información de días hábiles para el periodo actual
        if "periodo_actual" in periodos_data and periodos_data["periodo_actual"]:
            context["info_dias_habiles_actual"] = get_informacion_dias_habiles(
                periodos_data["periodo_actual"]
            )

        return context

    @staticmethod
    def get_form_context(form, usuario_id: str, comision, **extra_context) -> Dict:
        """
        Prepara el contexto para formularios.

        Args:
            form: Instancia del formulario
            usuario_id: ID del usuario actual
            comision: Instancia de la comisión
            **extra_context: Contexto adicional

        Returns:
            Diccionario con contexto para templates de formularios
        """
        context = {
            "form": form,
            "usuario_id": usuario_id,
            "comision": comision,
        }

        context.update(extra_context)
        return context

    @staticmethod
    def add_navigation_context(context: Dict, current_view: str) -> Dict:
        """
        Agrega contexto de navegación.

        Args:
            context: Contexto actual
            current_view: Vista actual

        Returns:
            Contexto actualizado con información de navegación
        """
        context.update(
            {
                "current_view": current_view,
                "breadcrumbs": ContextHelper._get_breadcrumbs(current_view),
            }
        )
        return context

    @staticmethod
    def _get_breadcrumbs(current_view: str) -> list:
        """
        Genera breadcrumbs para la navegación.

        Args:
            current_view: Vista actual

        Returns:
            Lista de breadcrumbs
        """
        breadcrumb_map = {
            "index": [{"name": "Inicio", "url": None}],
            "gestionar_periodos": [
                {"name": "Inicio", "url": "comision:index"},
                {"name": "Gestionar Periodos", "url": None},
            ],
            "crear_periodo": [
                {"name": "Inicio", "url": "comision:index"},
                {"name": "Gestionar Periodos", "url": "comision:gestionar_periodos"},
                {"name": "Crear Periodo", "url": None},
            ],
            "realizar_encuesta": [
                {"name": "Inicio", "url": "comision:index"},
                {"name": "Gestión de Preguntas", "url": None},
            ],
        }
        return breadcrumb_map.get(current_view, [])

    @staticmethod
    def preparar_datos_periodo(periodo, hoy):
        """
        Prepara los datos calculados para un período.

        Args:
            periodo: Instancia del período de evaluación
            hoy: Fecha actual

        Returns:
            Período con datos adicionales calculados
        """
        # Calcular progreso
        duracion_total = (periodo.fecha_fin - periodo.fecha_inicio).days
        dias_transcurridos = (hoy - periodo.fecha_inicio).days
        if duracion_total > 0:  # Evitar división por cero
            periodo.progreso = min(
                100, int((dias_transcurridos / duracion_total) * 100)
            )
        else:
            periodo.progreso = 100

        # Días restantes (calendario)
        periodo.dias_restantes = max(0, (periodo.fecha_fin - hoy).days)

        return periodo

    @staticmethod
    def calcular_fechas_automaticas(periodo):
        """
        Calcula las fechas automáticas para un período.

        Args:
            periodo: Instancia del período de evaluación

        Returns:
            Período con fechas automáticas calculadas
        """
        from datetime import timedelta

        # Calcular automáticamente la fecha de reunión de comisión (3 días después del fin)
        periodo.fecha_comision = periodo.fecha_fin + timedelta(days=3)
        # Calcular automáticamente la fecha de cierre (5 días después del fin)
        periodo.fecha_cierre = periodo.fecha_fin + timedelta(days=5)

        return periodo

    @staticmethod
    def determinar_estado_inicial(periodo):
        """
        Determina el estado inicial de un período basado en sus fechas.

        Args:
            periodo: Instancia del período de evaluación

        Returns:
            Estado inicial del período
        """
        from django.utils import timezone

        if periodo.fecha_inicio <= timezone.now().date():
            return "activo"
        else:
            return "pendiente"

    @staticmethod
    def get_fechas_default_periodo():
        """
        Obtiene las fechas predeterminadas para un nuevo período.

        Returns:
            Diccionario con fechas predeterminadas
        """
        from django.utils import timezone
        from datetime import timedelta

        fecha_inicio_default = timezone.now().date()
        fecha_fin_default = fecha_inicio_default + timedelta(days=15)

        return {
            "fecha_inicio": fecha_inicio_default,
            "fecha_fin": fecha_fin_default,
        }
