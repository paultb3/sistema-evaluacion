"""
Utilidades para el cálculo y manejo de días hábiles en periodos de evaluación.
"""

from datetime import date, timedelta
from typing import Dict, Optional
from apps.evaluacion.models import PeriodoEvaluacion


def calcular_dias_habiles(fecha_inicio: date, fecha_fin: date) -> int:
    """
    Calcula los días hábiles entre dos fechas (excluyendo fines de semana).

    Args:
        fecha_inicio: Fecha de inicio del periodo
        fecha_fin: Fecha de fin del periodo

    Returns:
        Número de días hábiles entre las fechas
    """
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


def calcular_dias_habiles_restantes(fecha_fin: date) -> int:
    """
    Calcula los días hábiles restantes hasta la fecha de fin.

    Args:
        fecha_fin: Fecha de fin del periodo

    Returns:
        Número de días hábiles restantes
    """
    if not fecha_fin or fecha_fin < date.today():
        return 0

    return calcular_dias_habiles(date.today(), fecha_fin)


def calcular_progreso_dias_habiles(periodo: PeriodoEvaluacion) -> int:
    """
    Calcula el progreso del periodo basado en días hábiles.

    Args:
        periodo: Instancia del periodo de evaluación

    Returns:
        Porcentaje de progreso basado en días hábiles (0-100)
    """
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


def get_informacion_dias_habiles(periodo: Optional[PeriodoEvaluacion]) -> Dict:
    """
    Obtiene información completa sobre días hábiles para un periodo.

    Args:
        periodo: Instancia del periodo de evaluación (puede ser None)

    Returns:
        Diccionario con información detallada sobre días hábiles
    """
    if not periodo:
        return {
            "total_dias_habiles": 0,
            "dias_habiles_transcurridos": 0,
            "dias_habiles_restantes": 0,
            "progreso_dias_habiles": 0,
            "es_dia_habil": False,
            "dia_semana": "N/A",
        }

    hoy = date.today()
    total_dias_habiles = calcular_dias_habiles(periodo.fecha_inicio, periodo.fecha_fin)
    dias_habiles_transcurridos = calcular_dias_habiles(
        periodo.fecha_inicio, min(hoy, periodo.fecha_fin)
    )
    dias_habiles_restantes = calcular_dias_habiles_restantes(periodo.fecha_fin)
    progreso_dias_habiles = calcular_progreso_dias_habiles(periodo)
    es_dia_habil = hoy.weekday() < 5  # Monday to Friday

    dias_semana = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo",
    ]
    dia_semana = dias_semana[hoy.weekday()]

    return {
        "total_dias_habiles": total_dias_habiles,
        "dias_habiles_transcurridos": dias_habiles_transcurridos,
        "dias_habiles_restantes": dias_habiles_restantes,
        "progreso_dias_habiles": progreso_dias_habiles,
        "es_dia_habil": es_dia_habil,
        "dia_semana": dia_semana,
    }


def es_dia_habil(fecha: date = None) -> bool:
    """
    Verifica si una fecha específica es día hábil.

    Args:
        fecha: Fecha a verificar (si es None, usa la fecha actual)

    Returns:
        True si es día hábil (lunes a viernes), False si es fin de semana
    """
    if fecha is None:
        fecha = date.today()

    return fecha.weekday() < 5
