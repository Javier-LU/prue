"""Estado compartido y utilidades comunes para la GUI de IXPHOS."""
# --- GUI y recursos gráficos --------------------------------------------------------
import tkinter as tk                                # Toolkit de interfaz gráfica base (ventana, frames, canvas, etc.)
from tkinter import (
                        ttk,                        # ttk: widgets “tematizados” (Notebook, Treeview, etc.)
                        filedialog,                 # filedialog: diálogos de abrir/guardar ficheros.
                        messagebox,                 # messagebox: cuadros de diálogo (info/alerta/error).
                        font                        # font: gestión de tipografías.
                    )
from PIL import Image, ImageTk, ImageSequence       # Carga/transforma imágenes y anima GIFs (spinner de carga)


# --- Algoritmos ---------------------------------------------------------------------
from .proxies import (
    diseno_cables_proxy as alg_cables,
    diseno_planta_fv_proxy as alg_planta_fv,
    diseno_subestacion_at_proxy as alg_subestacion_at,
    puesta_a_tierra_proxy as alg_pat,
    diseno_zanjas_proxy as alg_zanjas,
)

# --- Datos  ---------------------------------------------------------------------
import pandas as pd                                 # Estructuras/tablas de datos (DataFrame) usadas por las pestañas
import numpy as np                                  # Cálculo numérico, arrays y tipos numpy (integers/floating)
import json                                         # Serialización a JSON (estado del proyecto)
import gzip                                         # Compresión GZIP de los ficheros JSON guardados
import threading                                    # Hilos para tareas largas sin bloquear la GUI (guardado/cálculos)
import comtypes                                     # Interoperabilidad COM (p. ej., integrado con AutoCAD/COM)
import time                                         # Utilidades de tiempo/esperas (si se necesitan)
import traceback                                    # Trazas legibles en logs ante excepciones
import pythoncom                                    # Inicialización/uso de COM en hilos secundarios
import copy                                         # Copias superficiales/profundas de estructuras (si se requiere)
import itertools                                    # Utilidades combinatorias/iteración avanzada (agrupaciones, etc.)
from dataclasses import dataclass, field            # Modelos inmutables/ligeros para metadata (TabSection, grupos)
from typing import Any, Callable, Dict, Mapping     # Anotaciones de tipos para mayor claridad/ayuda del editor


# --- Servicios  --------------------------------------------------------------------
from ..services import AutoCAD_extension


# --- Configuración y rutas ----------------------------------------------------
from ..config import dicc_var_None

# --- Rutas ------------------------------------------------------------------------------
from pathlib import Path
from .constants import (    
    ROJO_SUAVE, ROJO_GRS, BLANCO_ROTO, GRIS_FUERTE, GRIS_SUAVE,         # Colores principales
    PACKAGE_DIR, ASSETS_DIR, ICONS_DIR, IMAGES_DIR,                     # Rutas
    TAB_METADATA,                                                       # Tabs
)


# =============================================================================
# ESTADO
# =============================================================================
dicc_var = dicc_var_None  # diccionario global serializable


# =============================================================================
# MODELOS DE DATOS (UI)
# =============================================================================
@dataclass(frozen=True)
class FunctionalGroup:
    """Agrupa los callbacks de una pestaña."""
    io: Mapping[str, Callable[..., Any]] = field(default_factory=dict)
    processing: Mapping[str, Callable[..., Any]] = field(default_factory=dict)
    ui: Mapping[str, Callable[..., Any]] = field(default_factory=dict)

    def all_handlers(self) -> Dict[str, Callable[..., Any]]:
        handlers: Dict[str, Callable[..., Any]] = {}
        handlers.update(self.io)
        handlers.update(self.processing)
        handlers.update(self.ui)
        return handlers


@dataclass(frozen=True)
class TabSection:
    """Metadatos y callbacks asociados a cada pestaña del cuaderno principal."""
    key: str
    title: str
    icon: str
    groups: FunctionalGroup

    @property
    def callbacks(self) -> Dict[str, Callable[..., Any]]:
        return self.groups.all_handlers()


# =============================================================================
# UTILIDADES 
# =============================================================================
def convertir_a_serializable(obj: Any) -> Any:
    """Convierte estructuras complejas a tipos compatibles con JSON."""
    if isinstance(obj, dict):
        return {k: convertir_a_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [convertir_a_serializable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return convertir_a_serializable(obj.tolist())
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict()
    if isinstance(obj, pd.Series):
        return obj.tolist()
    return obj


def guardar_variables(var_list, var_names) -> None:
    """Actualiza `dicc_var` con variables generadas por la aplicación (JSON-safe)."""
    global dicc_var
    for i in range(len(var_list)):
        try:
            dicc_var[var_names[i]] = convertir_a_serializable(var_list[i])
        except Exception as e:
            print(f"Error guardando {var_names[i]}: {e}")
            dicc_var[var_names[i]] = None


def cargar_imagen(ruta: str | Path, tamaño: tuple[int, int]) -> ImageTk.PhotoImage:
    """Localiza y carga una imagen de recursos, ajustándola al tamaño indicado."""
    p = Path(ruta)
    if not p.is_absolute():
        icon_path = ICONS_DIR / p
        image_path = IMAGES_DIR / p
        p = icon_path if icon_path.exists() else image_path
    imagen = Image.open(p).resize(tamaño, Image.LANCZOS)
    return ImageTk.PhotoImage(imagen)


def centrar_ventana_emergente(ventana: tk.Misc, ancho: int, alto: int) -> str:
    """Geometría necesaria para centrar una Toplevel sobre la ventana principal."""
    ventana.update_idletasks()
    w = ventana.winfo_width()
    h = ventana.winfo_height()
    x0 = ventana.winfo_x()
    y0 = ventana.winfo_y()
    x = x0 + (w // 2) - (ancho // 2)
    y = y0 + (h // 2) - (alto // 2)
    return f"{ancho}x{alto}+{x}+{y}"


def crear_gif_espera() -> tk.Toplevel:
    """Abre una Toplevel con un GIF de espera mientras se procesa una tarea pesada."""
    ventana_carga = tk.Toplevel(root)
    ventana_carga.attributes("-topmost", True)
    ventana_carga.resizable(False, False)
    ventana_carga.overrideredirect(True)
    ventana_carga.geometry(centrar_ventana_emergente(root, 250, 250))

    marco_borde = tk.Frame(ventana_carga, bg=ROJO_GRS, bd=5)
    marco_borde.pack()

    label_gif = tk.Label(marco_borde, bg="white")
    label_gif.pack()

    gif_path = ICONS_DIR / "Gif_espera.gif"
    gif = Image.open(gif_path)
    frames = [ImageTk.PhotoImage(f.copy().convert("RGBA")) for f in ImageSequence.Iterator(gif)]

    def animar_gif(ind: int = 0) -> None:
        frame = frames[ind]
        ind = (ind + 1) % len(frames)
        label_gif.configure(image=frame)
        ventana_carga.after(50, animar_gif, ind)

    animar_gif()
    return ventana_carga


def guardar_proyecto() -> None:
    """Guarda el estado del proyecto en un archivo JSON comprimido (GZIP) sin bloquear la GUI."""
    global dicc_var

    file_path = filedialog.asksaveasfilename(
        defaultextension=".json.gz",
        filetypes=[("GZIP files", "*.json.gz"), ("All files", "*.*")],
    )
    if file_path and not file_path.endswith(".json.gz"):
        file_path += ".json.gz"

    def proceso_guardado() -> None:
        """Trabajo pesado de guardado (hilo secundario)."""
        global error_guardado
        error_guardado = "Sin error"
        try:
            if file_path:
                with gzip.open(file_path, "wt", encoding="utf-8") as f:
                    json.dump(dicc_var, f, indent=4)
        except Exception:
            error_guardado = "Error"
            traceback.print_exc()

    def cerrar_ventana_tras_guardar(vtop: tk.Toplevel) -> None:
        """Cierra el spinner y muestra error si procede (en el hilo principal)."""
        try:
            vtop.destroy()
            if error_guardado == "Error":
                messagebox.showerror("Error", "There was an error while saving; file may be corrupted.")
        except Exception:
            print("Error al cerrar la ventana de carga.")

    def tarea_guardado() -> None:
        proceso_guardado()
        root.after(0, lambda: cerrar_ventana_tras_guardar(ventana_carga))

    ventana_carga = crear_gif_espera()
    hilo = threading.Thread(target=tarea_guardado, daemon=True)
    hilo.start()


# =============================================================================
# CONSTRUCCIÓN DE INTERFAZ 
# =============================================================================

# --- VENTANA PRINCIPAL (ROOT) Y ESTILO ---------------------------------------
root = tk.Tk()

# Icono de la aplicación
icon = ImageTk.PhotoImage(file=str(ICONS_DIR / "Icono.png"))
root.iconphoto(False, icon)

# Ventana
root.title("IXPHOS")
root.geometry("1500x900")
root.resizable(True, True)
root.configure(background=BLANCO_ROTO)

# --- LAYOUT CON SCROLL (CANVAS + FRAMES) ------------------------------------
outer_frame = tk.Frame(root, background=ROJO_GRS)
outer_frame.pack(fill=tk.BOTH, expand=True)

scroll_frame = tk.Frame(outer_frame, background=BLANCO_ROTO)
scroll_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(scroll_frame, background=BLANCO_ROTO)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root_inner_frame = tk.Frame(canvas, width=1400, height=1150)
root_inner_frame.pack_propagate(False)
canvas.create_window((0, 0), window=root_inner_frame, anchor="nw")

scroll_y = tk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
scroll_x = tk.Scrollbar(outer_frame, orient=tk.HORIZONTAL, command=canvas.xview)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

def on_configure(_event) -> None:
    canvas.configure(scrollregion=canvas.bbox("all"))

def resize_inner_frame(_event) -> None:
    if scroll_frame.winfo_width() > 1450 and scroll_frame.winfo_height() > 850:
        root_inner_frame.config(width=scroll_frame.winfo_width(), height=scroll_frame.winfo_height())

root_inner_frame.bind("<Configure>", on_configure)
scroll_frame.bind("<Configure>", resize_inner_frame)

frame_notebook = tk.Frame(root_inner_frame)
frame_notebook.pack(fill="both", expand=True)

# --- NOTEBOOK (PESTAÑAS) -----------------------------------------------------
style = ttk.Style()
style.configure("TNotebook", background="white")
style.configure("TNotebook.Tab", background=BLANCO_ROTO, padding=[10, 10], font=("Montserrat", 10))
style.map("TNotebook.Tab", background=[("selected", BLANCO_ROTO), ("active", ROJO_GRS)])

notebook = ttk.Notebook(frame_notebook, style="TNotebook")
notebook.pack(fill=tk.BOTH, expand=True)

# Crear frames por pestaña
tab_frames: Dict[str, tk.Frame] = {}
for tab_key, tab_title, _icon_name in TAB_METADATA:
    frame = tk.Frame(notebook, background=BLANCO_ROTO)
    notebook.add(frame, text=tab_title)
    tab_frames[tab_key] = frame

# Aliases históricos
Carga_Excel  = tab_frames["load_data"]
DTR          = tab_frames["dimensions"]
DFV          = tab_frames["pv_plant"]
AASS_NB      = tab_frames["aass"]
Cable_NB     = tab_frames["cables"]
Trenches_NB  = tab_frames["trenches"]
Earthing_NB  = tab_frames["earthing"]
Output_NB    = tab_frames["outputs"]
AutoCAD_NB   = tab_frames["autocad"]

# Iconos de pestañas
TAB_ICONS: Dict[str, ImageTk.PhotoImage] = {
    tab_key: cargar_imagen(icon_name, (32, 32)) for tab_key, _title, icon_name in TAB_METADATA
}
for idx, (tab_key, _title, _icon) in enumerate(TAB_METADATA):
    notebook.tab(idx, image=TAB_ICONS[tab_key], compound="top")

# --- LOGO + BOTÓN GUARDAR ----------------------------------------------------
frame_logo_y_guardado = tk.Frame(notebook, background="white")
frame_logo_y_guardado.pack(padx=20, pady=18, anchor="ne")

logo_GRE = cargar_imagen("Logo_GRE.PNG", (175, 40))
label_logo_GRE = tk.Label(frame_logo_y_guardado, image=logo_GRE, background="white")
label_logo_GRE.grid(row=0, column=1)

boton_guardar_proyecto = tk.Button(
    frame_logo_y_guardado,
    text="Save Project",
    command=guardar_proyecto,
    bg=ROJO_GRS,
    fg="white",
    font=("Calibri", 10, "italic"),
)
boton_guardar_proyecto.grid(row=0, column=0, padx=40)