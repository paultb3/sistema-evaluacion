"""
Utilidades para el manejo de fechas en el sistema de evaluación.
"""

from datetime import date, timedelta
from typing import Optional


def calcular_dias_restantes(fecha_fin: date) -> int:
    """
    Calcula los días restantes hasta una fecha de fin.

    Args:
        fecha_fin: Fecha de fin del periodo

    Returns:
        Número de días restantes (0 si la fecha ya pasó)
    """
    if fecha_fin and fecha_fin >= date.today():
        return (fecha_fin - date.today()).days
    return 0


def calcular_duracion_periodo(fecha_inicio: date, fecha_fin: date) -> int:
    """
    Calcula la duración total de un periodo en días.

    Args:
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de fin

    Returns:
        Número total de días del periodo
    """
    if not fecha_inicio or not fecha_fin:
        return 0

    return (fecha_fin - fecha_inicio).days + 1


def calcular_progreso_calendario(
    fecha_inicio: date, fecha_fin: date, fecha_actual: Optional[date] = None
) -> int:
    """
    Calcula el progreso basado en días calendario.

    Args:
        fecha_inicio: Fecha de inicio del periodo
        fecha_fin: Fecha de fin del periodo
        fecha_actual: Fecha actual (si es None, usa today())

    Returns:
        Porcentaje de progreso (0-100)
    """
    if fecha_actual is None:
        fecha_actual = date.today()

    if fecha_actual < fecha_inicio:
        return 0
    elif fecha_actual > fecha_fin:
        return 100

    duracion_total = calcular_duracion_periodo(fecha_inicio, fecha_fin)
    if duracion_total <= 0:
        return 100

    dias_transcurridos = (fecha_actual - fecha_inicio).days + 1
    return min(100, int((dias_transcurridos / duracion_total) * 100))


def agregar_dias_habiles(fecha_inicio: date, dias_habiles: int) -> date:
    """
    Agrega una cantidad específica de días hábiles a una fecha.

    Args:
        fecha_inicio: Fecha de inicio
        dias_habiles: Número de días hábiles a agregar

    Returns:
        Nueva fecha después de agregar los días hábiles
    """
    fecha_actual = fecha_inicio
    dias_agregados = 0

    while dias_agregados < dias_habiles:
        fecha_actual += timedelta(days=1)
        # Si es día hábil (lunes a viernes)
        if fecha_actual.weekday() < 5:
            dias_agregados += 1

    return fecha_actual


def formatear_fecha_espanol(fecha: date) -> str:
    """
    Formatea una fecha en español.

    Args:
        fecha: Fecha a formatear

    Returns:
        Fecha formateada en español
    """
    meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ]

    return f"{fecha.day} de {meses[fecha.month - 1]} de {fecha.year}"


def es_fin_de_semana(fecha: date = None) -> bool:
    """
    Verifica si una fecha es fin de semana.

    Args:
        fecha: Fecha a verificar (si es None, usa la fecha actual)

    Returns:
        True si es sábado o domingo
    """
    if fecha is None:
        fecha = date.today()

    return fecha.weekday() >= 5  # Saturday = 5, Sunday = 6
