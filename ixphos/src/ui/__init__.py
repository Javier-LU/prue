"""
Paquete de interfaz gráfica (UI) de IXPHOS.

Expone:
- proxies: interfaces hacia los algoritmos
- tabs: definición y carga de las pestañas del notebook
- app/gui/shared: inicialización y utilidades de la interfaz
"""

from . import proxies
from . import tabs
from . import app
from . import gui
from . import shared

__all__ = [
    "proxies",
    "tabs",
    "app",
    "gui",
    "shared",
]