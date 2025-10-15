"""
Proxies de algoritmos IXPHOS.

Estos módulos actúan como interfaz de carga diferida para 
los algoritmos implementados en `src.algorithms`. Cada proxy expone
las funciones de un algoritmo concreto con un prefijo `alg_` para 
identificarlos fácilmente.
"""

from . import diseno_cables_proxy as alg_cables
from . import diseno_planta_fv_proxy as alg_planta_fv
from . import diseno_subestacion_at_proxy as alg_subestacion_at
from . import diseno_zanjas_proxy as alg_zanjas
from . import puesta_a_tierra_proxy as alg_pat

__all__ = [
    "alg_cables",
    "alg_planta_fv",
    "alg_subestacion_at",
    "alg_zanjas",
    "alg_pat",
]