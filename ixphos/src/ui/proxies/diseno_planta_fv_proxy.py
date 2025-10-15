from importlib import import_module
from typing import Any

_MODULE = "src.algorithms.Algoritmo_IXPHOS_1_Config_fisica"
_FUNCTIONS = [
    "agrupacion_en_bandas",
    "agrupar_en_filas",
    "clasificacion_bandas",
    "contorno_de_las_bandas",
    "filas_de_strings",
    "ordenar_bandas",
    "ordenar_x_y",
    "orientacion_hacia_inversor",
    "preparar_datos_trackers",
    "sacar_y_ordenar_filas_en_bandas",
]

__all__ = _FUNCTIONS


def __getattr__(name: str) -> Any:
    if name in _FUNCTIONS:
        try:
            module = import_module(_MODULE)
        except ModuleNotFoundError as exc: 
            raise ModuleNotFoundError(
                f"{_MODULE} is required to use '{name}'"
            ) from exc
        return getattr(module, name)
    raise AttributeError(name)