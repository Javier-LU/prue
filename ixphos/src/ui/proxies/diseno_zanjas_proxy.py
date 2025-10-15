from importlib import import_module
from typing import Any

_MODULE = "src.algorithms.Algoritmo_IXPHOS_4_Zanjas"
_FUNCTIONS = [
    "calculo_anchos_zanjas_LV",
    "calculo_anchos_zanjas_MV",
    "combinaciones_circuitos_zanjas_LV",
    "combinaciones_circuitos_zanjas_MV",
    "combinar_todas_las_zanjas",
    "densificar_polilineas_con_puntos_comunes",
    "trazado_zanjas_AASS",
    "trazado_zanjas_DC_y_conteo_tubos_circuitos_en_zanja",
    "trazado_zanjas_LV",
    "trazado_zanjas_MV",
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