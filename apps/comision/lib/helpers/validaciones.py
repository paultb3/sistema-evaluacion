"""
Helpers para validaciones en el módulo de comisión.
"""

from datetime import date, timedelta
from typing import List, Dict, Optional
from apps.evaluacion.models import PeriodoEvaluacion


class ValidacionHelper:
    """Helper para validaciones de negocio."""

    @staticmethod
    def validar_fechas_periodo(fecha_inicio: date, fecha_fin: date) -> List[str]:
        """
        Valida las fechas de un periodo de evaluación.

        Args:
            fecha_inicio: Fecha de inicio del periodo
            fecha_fin: Fecha de fin del periodo

        Returns:
            Lista de errores de validación (vacía si no hay errores)
        """
        errores = []

        if not fecha_inicio or not fecha_fin:
            errores.append("Las fechas de inicio y fin son obligatorias.")
            return errores

        if fecha_inicio >= fecha_fin:
            errores.append("La fecha de inicio debe ser anterior a la fecha de fin.")

        if fecha_fin < date.today():
            errores.append("La fecha de fin no puede ser anterior a la fecha actual.")

        # Validar duración mínima (al menos 3 días)
        if (fecha_fin - fecha_inicio).days < 3:
            errores.append("El periodo debe tener una duración mínima de 3 días.")

        # Validar duración máxima (no más de 90 días)
        if (fecha_fin - fecha_inicio).days > 90:
            errores.append("El periodo no puede tener una duración mayor a 90 días.")

        return errores

    @staticmethod
    def validar_solapamiento_periodos(
        fecha_inicio: date, fecha_fin: date, periodo_actual_id: Optional[int] = None
    ) -> List[str]:
        """
        Valida que no haya solapamiento con otros periodos.

        Args:
            fecha_inicio: Fecha de inicio del nuevo periodo
            fecha_fin: Fecha de fin del nuevo periodo
            periodo_actual_id: ID del periodo actual (para edición)

        Returns:
            Lista de errores de validación
        """
        errores = []

        # Buscar periodos que se solapen
        query = PeriodoEvaluacion.objects.filter(
            fecha_inicio__lte=fecha_fin, fecha_fin__gte=fecha_inicio
        )

        # Excluir el periodo actual si se está editando
        if periodo_actual_id:
            query = query.exclude(id=periodo_actual_id)

        periodos_solapados = query.exists()

        if periodos_solapados:
            errores.append(
                "Las fechas seleccionadas se solapan con otro periodo de evaluación existente."
            )

        return errores

    @staticmethod
    def validar_fechas_comision_cierre(
        fecha_fin: date, fecha_comision: date = None, fecha_cierre: date = None
    ) -> List[str]:
        """
        Valida las fechas de comisión y cierre.

        Args:
            fecha_fin: Fecha de fin del periodo
            fecha_comision: Fecha de reunión de comisión
            fecha_cierre: Fecha de cierre

        Returns:
            Lista de errores de validación
        """
        errores = []

        if fecha_comision and fecha_comision <= fecha_fin:
            errores.append(
                "La fecha de reunión de comisión debe ser posterior al fin del periodo."
            )

        if fecha_cierre and fecha_cierre <= fecha_fin:
            errores.append("La fecha de cierre debe ser posterior al fin del periodo.")

        if fecha_comision and fecha_cierre and fecha_cierre <= fecha_comision:
            errores.append(
                "La fecha de cierre debe ser posterior a la reunión de comisión."
            )

        return errores

    @staticmethod
    def sugerir_fechas_automaticas(
        fecha_inicio: date, fecha_fin: date
    ) -> Dict[str, date]:
        """
        Sugiere fechas automáticas para comisión y cierre.

        Args:
            fecha_inicio: Fecha de inicio del periodo
            fecha_fin: Fecha de fin del periodo

        Returns:
            Diccionario con fechas sugeridas
        """
        # Importar aquí para evitar importaciones circulares
        from apps.comision.lib.utils.dias_habiles import agregar_dias_habiles

        # Sugerir fecha de comisión: 2-3 días hábiles después del fin
        fecha_comision_sugerida = fecha_fin + timedelta(days=3)

        # Ajustar si cae en fin de semana
        while fecha_comision_sugerida.weekday() >= 5:  # Sábado o domingo
            fecha_comision_sugerida += timedelta(days=1)

        # Sugerir fecha de cierre: 5-7 días después del fin
        fecha_cierre_sugerida = fecha_fin + timedelta(days=5)

        # Ajustar si cae en fin de semana
        while fecha_cierre_sugerida.weekday() >= 5:  # Sábado o domingo
            fecha_cierre_sugerida += timedelta(days=1)

        return {
            "fecha_comision": fecha_comision_sugerida,
            "fecha_cierre": fecha_cierre_sugerida,
        }

    @staticmethod
    def validar_estado_periodo(
        periodo: PeriodoEvaluacion, nuevo_estado: str
    ) -> List[str]:
        """
        Valida la transición de estado de un periodo.

        Args:
            periodo: Instancia del periodo
            nuevo_estado: Nuevo estado propuesto

        Returns:
            Lista de errores de validación
        """
        errores = []
        estado_actual = periodo.estado

        # Definir transiciones válidas
        transiciones_validas = {
            "pendiente": ["activo", "cerrado"],
            "activo": ["revision", "cerrado"],
            "revision": ["cerrado"],
            "cerrado": [],  # No se puede cambiar desde cerrado
        }

        if nuevo_estado not in transiciones_validas.get(estado_actual, []):
            errores.append(
                f"No se puede cambiar el estado de '{estado_actual}' a '{nuevo_estado}'."
            )

        # Validaciones específicas por estado
        hoy = date.today()

        if nuevo_estado == "activo" and periodo.fecha_inicio > hoy:
            errores.append(
                "No se puede activar un periodo cuya fecha de inicio es futura."
            )

        if nuevo_estado == "revision" and periodo.fecha_fin > hoy:
            errores.append(
                "No se puede poner en revisión un periodo que aún no ha terminado."
            )

        return errores
