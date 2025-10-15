"""Carga dinámica de las secciones de pestañas de la interfaz."""

from __future__ import annotations

from pathlib import Path
from typing import List

from .. import shared

__all__ = ["load_sections"]

_TAB_SOURCES = [
    ("load_data", "LOAD_DATA_SECTION"),
    ("dimensions", "DIMENSIONS_SECTION"),
    ("pv_plant", "PV_PLANT_SECTION"),
    ("aass", "AASS_SECTION"),
    ("cables", "CABLES_SECTION"),
    ("trenches", "TRENCHES_SECTION"),
    ("earthing", "EARTHING_SECTION"),
    ("outputs", "OUTPUT_SECTION"),
    ("autocad", "AUTOCAD_SECTION"),
]

_LOADED = False
_SECTIONS: List[shared.TabSection] = []


def load_sections() -> List[shared.TabSection]:
    """Ejecuta los módulos de pestañas dentro del namespace compartido."""

    global _LOADED

    if _LOADED:
        return list(_SECTIONS)

    base_path = Path(__file__).resolve().parent
    for module_name, section_attr in _TAB_SOURCES:
        module_path = base_path / f"{module_name}.py"
        code = module_path.read_text(encoding="utf-8")
        exec(compile(code, str(module_path), "exec"), shared.__dict__)
        _SECTIONS.append(shared.__dict__[section_attr])

    _LOADED = True
    return list(_SECTIONS)