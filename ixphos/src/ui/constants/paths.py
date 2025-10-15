from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[2] / "src" / "ui"
ASSETS_DIR  = PACKAGE_DIR.parent.parent.parent / "assets"
ICONS_DIR   = ASSETS_DIR / "icons"
IMAGES_DIR  = ASSETS_DIR / "jpg"