import math
from datetime import datetime
from decimal import Decimal


def comparar_filas_con_esperadas(filas, esperados):
    assert len(filas) == len(esperados)
    for fila, esperado in zip(filas, esperados):
        for key in esperado:
            if isinstance(esperado[key], datetime) and isinstance(fila[key], datetime):
                diff = abs((esperado[key].replace(tzinfo=None) - fila[key].replace(tzinfo=None)).total_seconds())
                assert diff < 60, f"Error en fecha (tolerancia 1m): esperado {esperado[key]}, obtenido {fila[key]}"
            elif isinstance(esperado[key], Decimal) and isinstance(fila[key], float):
                valor_dec = Decimal(str(fila[key]))
                assert esperado[key] == valor_dec, f"Error en valor: esperado {esperado[key]}, obtenido {valor_dec}"
            elif isinstance(esperado[key], float) and isinstance(fila[key], Decimal):
                valor_dec = Decimal(str(esperado[key]))
                assert fila[key] == valor_dec, f"Error en valor: esperado {valor_dec}, obtenido {fila[key]}"
            elif isinstance(esperado[key], float) and isinstance(fila[key], float):
                assert math.isclose(esperado[key], fila[key], rel_tol=1e-9), f"Error en valor: esperado {esperado[key]}, obtenido {fila[key]}"
            else:
                assert esperado[key] == fila[key], f"Error en valor: esperado {esperado[key]}, obtenido {fila[key]}"
