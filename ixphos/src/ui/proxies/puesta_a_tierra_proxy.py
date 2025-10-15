from importlib import import_module
from typing import Any

_MODULE = "src.algorithms.Algoritmo_IXPHOS_5_PAT_y_mediciones_finales"
_FUNCTIONS = [
    "anillos_PAT",
    "mediciones_por_bloque_cajas_y_totales_strings",
    "mediciones_por_bloque_inv_string_y_totales_strings",
    "mediciones_por_bloque_y_totales_LV_material",
    "mediciones_por_bloque_y_totales_PAT",
    "mediciones_por_bloque_y_totales_cables",
    "mediciones_por_bloque_y_totales_zanjas",
    "schedule_picas_comboxes_cajas_inv_str",
    "simulacion_principal_elementos_PAT",
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