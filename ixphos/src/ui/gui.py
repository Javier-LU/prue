from __future__ import annotations

from typing import Any, Callable, Dict

from . import shared
from .tabs import load_sections

__all__ = ["TAB_SECTIONS", "get_tab_action", "main"]

_SECTIONS = load_sections()

TAB_SECTIONS: Dict[str, shared.TabSection] = {
    section.key: section for section in _SECTIONS
}


def get_tab_action(tab_key: str, category: str, name: str) -> Callable[..., Any]:
    """Recupera un callback registrado para la pestaña y categoría indicada."""

    section = TAB_SECTIONS[tab_key]
    groups = {
        "io": section.groups.io,
        "processing": section.groups.processing,
        "ui": section.groups.ui,
    }
    try:
        return groups[category][name]
    except KeyError as exc:  # pragma: no cover - acceso defensivo
        raise KeyError(f"Acción desconocida: {tab_key}.{category}.{name}") from exc


def main() -> None:
    """Lanza el bucle principal de Tkinter."""

    shared.root.mainloop()


if __name__ == "__main__":  # pragma: no cover
    main()




    
