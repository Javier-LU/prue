from importlib import import_module
from typing import Any

_MODULE = "src.algorithms.Algoritmo_IXPHOS_2_Config_electrica"
_FUNCTIONS = [
    "ID_strings_e_inv_string",
    "ID_strings_y_cajas_para_Cable_de_String",
    "ID_strings_y_cajas_para_DC_Bus",
    "ID_strings_y_cajas_para_config_mixtas",
    "aplicar_flip_strings",
    "asignar_strings_a_inversores",
    "cajas_desde_filas_asociadas",
    "calculo_DC_Boxes",
    "combinacion_inv_en_bandas_optima",
    "filas_config_cajas_sin_mezclar_filas",
    "intercambio_strings_por_proximidad_a_puente",
    "obtener_filas_en_inv_como_filas_en_cajas",
    "obtener_inv_fisicos",
    "posicion_inv_string",
    "reconstruir_almacen_strings_y_puentes",
    "repartir_cajas_en_dos_inversores",
    "repartir_inversores_en_dos_cuadros",
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