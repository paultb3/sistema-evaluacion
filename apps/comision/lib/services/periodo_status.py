"""
Servicio para el manejo de estados y etiquetas de periodos de evaluación.
"""

from datetime import date
from typing import Tuple, Optional
from apps.evaluacion.models import PeriodoEvaluacion


class PeriodoStatusService:
    """Servicio para manejar estados y información de periodos."""

    @staticmethod
    def get_periodo_status(
        periodo: Optional[PeriodoEvaluacion], fecha_actual: date = None
    ) -> Tuple[str, str]:
        """
        Obtiene la etiqueta de estado y las clases CSS para un periodo.

        Args:
            periodo: Instancia del periodo de evaluación
            fecha_actual: Fecha actual (si es None, usa today())

        Returns:
            Tupla con (etiqueta_estado, clases_css)
        """
        if fecha_actual is None:
            fecha_actual = date.today()

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

    @staticmethod
    def get_comision_status(
        periodo: Optional[PeriodoEvaluacion], fecha_actual: date = None
    ) -> Tuple[str, str]:
        """
        Obtiene el estado de la reunión de comisión.

        Args:
            periodo: Instancia del periodo de evaluación
            fecha_actual: Fecha actual (si es None, usa today())

        Returns:
            Tupla con (estado_comision, clases_css)
        """
        if fecha_actual is None:
            fecha_actual = date.today()

        if not periodo:
            return ("Sin periodo", "text-gray-500 dark:text-gray-400")

        if fecha_actual > periodo.fecha_fin and fecha_actual <= periodo.fecha_cierre:
            return ("En revisión", "text-amber-600 dark:text-amber-400")
        elif fecha_actual > periodo.fecha_cierre:
            return ("Completada", "text-green-600 dark:text-green-400")
        else:
            return ("Pendiente", "text-gray-500 dark:text-gray-400")

    @staticmethod
    def get_publication_status(
        periodo: Optional[PeriodoEvaluacion], fecha_actual: date = None
    ) -> Tuple[str, str]:
        """
        Obtiene el estado de publicación.

        Args:
            periodo: Instancia del periodo de evaluación
            fecha_actual: Fecha actual (si es None, usa today())

        Returns:
            Tupla con (estado_publicacion, clases_css)
        """
        if fecha_actual is None:
            fecha_actual = date.today()

        if not periodo:
            return ("Sin periodo", "text-gray-500 dark:text-gray-400")

        if fecha_actual > periodo.fecha_cierre:
            return ("Publicado", "text-green-600 dark:text-green-400")
        else:
            return ("Pendiente", "text-gray-500 dark:text-gray-400")

    @staticmethod
    def get_icono_estado(estado: str) -> str:
        """
        Obtiene el icono FontAwesome correspondiente al estado.

        Args:
            estado: Estado del periodo

        Returns:
            Clase del icono FontAwesome
        """
        iconos = {
            "activo": "fa-check-circle",
            "pendiente": "fa-clock",
            "revision": "fa-search",
            "cerrado": "fa-lock",
        }
        return iconos.get(estado, "fa-question-circle")

    @staticmethod
    def get_color_progreso(progreso: int) -> str:
        """
        Obtiene el color de la barra de progreso según el porcentaje.

        Args:
            progreso: Porcentaje de progreso (0-100)

        Returns:
            Clase CSS para el color de la barra
        """
        if progreso >= 90:
            return "bg-red-600"
        elif progreso >= 70:
            return "bg-yellow-600"
        elif progreso >= 40:
            return "bg-blue-600"
        else:
            return "bg-green-600"
