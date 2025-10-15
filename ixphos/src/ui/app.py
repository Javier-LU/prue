"""Bootstrap helpers for running the IXPHOS user interface."""

from . import gui

__all__ = ["main"]


def main() -> None:
    """Launch the graphical interface."""
    gui.main()