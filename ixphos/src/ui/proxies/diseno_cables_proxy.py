from importlib import import_module
from typing import Any

_MODULE = "src.algorithms.Algoritmo_IXPHOS_3_Cables"
_FUNCTIONS = [
    "asignacion_secciones_cable_MV",
    "calculo_perdidas_DC_Bus",
    "calculo_perdidas_array",
    "calculo_perdidas_cables_string",
    "insercion_y_medicion_de_harness",
    "lineas_MV_o_FO_por_caminos",
    "medicion_DC_Bus",
    "medicion_array",
    "medicion_cable_MV",
    "medicion_cable_string",
    "pol_cable_string_en_inv_string",
    "polilinea_array",
    "polilineas_AASS_LVAC_y_ethernet",
    "polilineas_de_circuitos_DC_Bus",
    "polilineas_de_circuitos_both_types",
    "polilineas_de_circuitos_cable_string",
    "polilineas_de_circuitos_mixed",
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