from datetime import datetime
import pandas as pd
import pytz


def convertir_string_a_date(fecha, formato):
    """
    Convierte una cadena de texto a un objeto datetime, usando un formato personalizado.
    """
    formato_strftime = _mapear_formato_personalizado(formato)
    return datetime.strptime(fecha, formato_strftime)


def convertir_date_a_string(fecha, formato):
    """
    Convierte un objeto datetime a una cadena de texto, usando un formato personalizado.
    """
    formato_strftime = _mapear_formato_personalizado(formato)
    return fecha.strftime(formato_strftime)


def _mapear_formato_personalizado(formato: str) -> str:
    """
    Convierte un formato personalizado (por ejemplo: 'DD-MM-YYYY') en uno compatible con las funciones estándar de fechas en Python
    strftime/strptime (por ejemplo: '%d-%m-%Y').

    - `strftime` formatea objetos datetime como cadenas de texto.
    - `strptime` parsea cadenas de texto y las convierte en objetos datetime.
    """
    reemplazo_formatos = {
        "YYYY": "%Y",
        "YY": "%y",
        "MMMM": "%B",
        "MMM": "%b",
        "MM": "%m",
        "DD": "%d",
        "WD": "%A",
        "HH24": "%H",
        "HH12": "%I",
        "HH": "%H",
        "AMPM": "%p",
        "MI": "%M",
        "SS": "%S",
    }

    formato = formato.upper()
    for clave, valor in sorted(reemplazo_formatos.items(), key=lambda x: -len(x[0])):
        formato = formato.replace(clave, valor)
    return formato


def calcular_dia_semana(serie_fechas: pd.Series) -> pd.Series:
    """
    Convierte una serie de fechas en formato string o datetime a una serie de letras
    que representan el día de la semana según la siguiente codificación:
    L = Lunes, M = Martes, X = Miércoles, J = Jueves, V = Viernes, S = Sábado, D = Domingo.

    Args:
        serie_fechas (pd.Series): Serie con fechas en formato string 'YYYY-MM-dd' o datetime.

    Returns:
        pd.Series: Serie con la letra del día de la semana correspondiente a cada fecha.
    """
    dias_semana = {
        0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V', 5: 'S', 6: 'D'
    }
    return pd.to_datetime(serie_fechas).dt.weekday.map(dias_semana)

def convertir_fecha_madrid_a_utc(fecha):
    """
    Convierte una fecha en formato ISO 8601 (string o datetime sin zona horaria)
    que representa una hora en la zona horaria de Madrid a su equivalente en UTC.

    Args:
        fecha (str or datetime-like): Fecha y hora en formato ISO 8601 sin zona horaria,
                                      que se asume está en hora local de Madrid.

    Returns:
        datetime: Objeto datetime con zona horaria UTC equivalente a la fecha de entrada.
    """
    zona_horaria_madrid = pytz.timezone("Europe/Madrid")
    fecha_hora_local = pd.to_datetime(fecha).tz_localize(zona_horaria_madrid)
    fecha_hora_utc = fecha_hora_local.astimezone(pytz.utc)
    return fecha_hora_utc

