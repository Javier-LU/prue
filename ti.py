

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
from PIL import Image, ImageTk, ImageSequence
    
import pandas as pd
import numpy as np
import json
import gzip
import threading
import comtypes
import time
import traceback
import pythoncom
import copy
import itertools


import Algoritmo_IXPHOS_1_Config_fisica
import Algoritmo_IXPHOS_2_Config_electrica
import Algoritmo_IXPHOS_3_Cables
import Algoritmo_IXPHOS_4_Zanjas
import Algoritmo_IXPHOS_5_PAT_y_mediciones_finales
import AutoCAD_extension

from Variables_IXPHOS import dicc_var_None

# J
from pathlib import Path


dicc_var = dicc_var_None

BASE_DIR = Path(__file__).resolve().parent
ICONOS_DIR = BASE_DIR / "Iconos GUI" 

#Definimo las funcion de guardar variables en el diccionario que se importa

# def guardar_variables(var_list, var_names): #funcion para guardar las variables conforme se vayan definiendo (tras pulsar un boton de ejecucion de cada pestaña) en un diccionario, si no se han definido se dejan como None
#     global dicc_var
#     for i in range(0,len(var_list)):
#         try:
#             if isinstance(var_list[i], np.ndarray):
#                 dicc_var[var_names[i]] = var_list[i].tolist()
#             elif isinstance(var_list[i], np.int64):
#                 dicc_var[var_names[i]] = int(var_list[i])
#             elif isinstance(var_list[i], np.float64):
#                 dicc_var[var_names[i]] = float(var_list[i])
#             # elif isinstance(var_list[i], np.str_):
#             #     dicc_var[var_names[i]] = str(var_list[i])
#             elif isinstance(var_list[i], pd.DataFrame):
#                 dicc_var[var_names[i]] = var_list[i].to_dict()  # Convertir DataFrame a diccionario
#             else:
#                 dicc_var[var_names[i]] = var_list[i]
#         except Exception as e:
#             print(f"Error guardando {var_names[i]}: {e}")
#             dicc_var[var_names[i]]=None

# def guardar_listas_con_arrays(var_list, var_names): #cuando tenemos 
#     global dicc_var
#     for i in range(0,len(var_list)):
#         try:
#             lista_de_arrays_internos_serializados= [arr.tolist() for arr in var_list[i]]
#             dicc_var[var_names[i]] = lista_de_arrays_internos_serializados
#         except Exception as e:
#             print(f"Error guardando {var_names[i]}: {e}")
#             dicc_var[var_names[i]]=None
    

def convertir_a_serializable(obj):
    if isinstance(obj, dict):
        return {k: convertir_a_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [convertir_a_serializable(elem) for elem in obj]
    elif isinstance(obj, np.ndarray):
        return convertir_a_serializable(obj.tolist())
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    else:
        return obj

def guardar_variables(var_list, var_names):
    global dicc_var
    for i in range(len(var_list)):
        try:
            dicc_var[var_names[i]] = convertir_a_serializable(var_list[i])
        except Exception as e:
            print(f"Error guardando {var_names[i]}: {e}")
            dicc_var[var_names[i]] = None
            
            
# Crear raíz principal
root = tk.Tk()
# root.iconbitmap(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Icono.ico')

# icon = ImageTk.PhotoImage(file=r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Icono.png')  #icono de la ventana

icon = ImageTk.PhotoImage(file=str(ICONOS_DIR / "Icono.png"))

root.iconphoto(False, icon)

# Convertir valores RGB a hexadecimal
def rgb_to_hex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

# Definir colores usando valores RGB
rojo_suave = rgb_to_hex(255, 224, 224)  # RGB para rojo suave
rojo_GRS = rgb_to_hex(127, 0, 0)  # RGB para rojo grs
blanco_roto = rgb_to_hex(242, 242, 242)  # RGB para blanco roto
gris_fuerte = rgb_to_hex(180, 180, 180)
gris_suave = rgb_to_hex(200, 200, 200)

# Retocar ventana principal
root.title("IXPHOS")  # o IXLO o IXPHO o XPHO o XFO o IXFO o IXFOS
root.geometry("1500x900")
root.resizable(True, True)
root.configure(background=blanco_roto)





#Creamos las funciones que van a cargar y descargar el gif usado en los periodos de carga de otras funciones
after_ID = None
ventana_carga = None

def centrar_ventana_emergente(ventana, ancho, alto):
    # Obtener el tamaño de la ventana principal
    ventana.update_idletasks()
    ancho_ventana_principal = ventana.winfo_width()
    alto_ventana_principal = ventana.winfo_height()
    x_ventana_principal = ventana.winfo_x()
    y_ventana_principal = ventana.winfo_y()
    
    # Calcular la posición x e y para centrar la ventana emergente en la ventana principal
    x = x_ventana_principal + (ancho_ventana_principal // 2) - (ancho // 2)
    y = y_ventana_principal + (alto_ventana_principal // 2) - (alto // 2)
    
    # Establecer la geometría de la ventana emergente
    return f'{ancho}x{alto}+{x}+{y}'

   
def crear_gif_espera():
    ventana_carga = tk.Toplevel(root)
    # ventana_carga.transient(root) 
    ventana_carga.attributes("-topmost", True)
    ventana_carga.resizable(False, False)
    ventana_carga.overrideredirect(True)       # Elimina la barra de título y bordes de la ventana
    ventana_carga.geometry(centrar_ventana_emergente(root, 250, 250))  
    
    marco_borde = tk.Frame(ventana_carga, bg=rojo_GRS, bd=5)
    marco_borde.pack()

    label_gif = tk.Label(marco_borde, bg='white')
    label_gif.pack()
    
        # Cargar y mostrar el GIF animado
    #  gif_path = r"C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Gif_espera.gif"

    gif_path = ICONOS_DIR / "Gif_espera.gif"

    gif = Image.open(gif_path)
    frames = [ImageTk.PhotoImage(frame.copy().convert('RGBA')) for frame in ImageSequence.Iterator(gif)]
    
    def animar_gif(ind=0):
        frame = frames[ind]
        ind = (ind + 1) % len(frames)
        label_gif.configure(image=frame)
        ventana_carga.after(50, animar_gif, ind)
    
    animar_gif()  # Iniciar animación
    return ventana_carga

    
#----------CONFIGURAMOS EL ROOT PARA QUE SE PUEDA ADAPTAR A LOS DISTINTOS TAMAÑOS, MANTENIENDO EL MARCO AJUSTADO A LA VENTANA-----------------
# Crear el Frame que contendrá el Canvas y las barras de desplazamiento
outer_frame = tk.Frame(root, background=rojo_GRS)
outer_frame.pack(fill=tk.BOTH, expand=True)

# Crear el Frame intermedio para las barras de desplazamiento
scroll_frame = tk.Frame(outer_frame, background=blanco_roto)
scroll_frame.pack(fill=tk.BOTH, expand=True)

# Crear el Canvas dentro del Frame intermedio
canvas = tk.Canvas(scroll_frame, background=blanco_roto)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Crear un Frame dentro del Canvas para contener los widgets
root_inner_frame = tk.Frame(canvas, width=1400, height=1150)
root_inner_frame.pack_propagate(False)
canvas.create_window((0, 0), window=root_inner_frame, anchor="nw")

# Añadir las barras de desplazamiento al Frame intermedio
scroll_y = tk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
scroll_x = tk.Scrollbar(outer_frame, orient=tk.HORIZONTAL, command=canvas.xview)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

# Configurar el Canvas para usar las barras de desplazamiento
canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
# Ajustar el tamaño del inner_frame al tamaño del root CUANDO SE SUPERA EL TAMAÑO MINIMO
def resize_inner_frame(event):
    if scroll_frame.winfo_width() > 1450 and scroll_frame.winfo_height() > 850:
        root_inner_frame.config(width=scroll_frame.winfo_width(), height=scroll_frame.winfo_height())
    
root_inner_frame.bind("<Configure>", on_configure)
scroll_frame.bind("<Configure>", resize_inner_frame)

frame_notebook=tk.Frame(root_inner_frame)
frame_notebook.pack(fill='both', expand=True)

#-----------------CREAMOS EL NOTEBOOK PARA INCLUIR LAS DISTINTAS FUNCIONALIDADES------------------------------------------

# Crear estilo personalizado para el notebook (no se puede cambiar directamente, solo funciona a través de estilos)
style = ttk.Style()
style.configure('TNotebook', background='white')
style.configure('TNotebook.Tab', background=blanco_roto, padding=[10, 10], font=('Montserrat', 10))
style.map('TNotebook.Tab', background=[('selected', blanco_roto), ('active', rojo_GRS)])

# Crear el notebook (pestañas)
notebook = ttk.Notebook(frame_notebook, style='TNotebook')
notebook.pack(fill=tk.BOTH, expand=True)

# Crear las pestañas con el color de fondo definido
Carga_Excel = tk.Frame(notebook, background=blanco_roto)
DTR = tk.Frame(notebook, background=blanco_roto)
DFV = tk.Frame(notebook, background=blanco_roto)
AASS_NB = tk.Frame(notebook, background=blanco_roto)
Cable_NB = tk.Frame(notebook, background=blanco_roto)
Trenches_NB = tk.Frame(notebook, background=blanco_roto)
Earthing_NB = tk.Frame(notebook, background=blanco_roto)
Output_NB = tk.Frame(notebook, background=blanco_roto)
AutoCAD_NB = tk.Frame(notebook, background=blanco_roto)

# Añadir las pestañas al notebook
notebook.add(Carga_Excel, text='Load Data')
notebook.add(DTR, text='Dimensions')
notebook.add(DFV, text='PV Plant Design')
notebook.add(AASS_NB, text='AASS & Conduits')
notebook.add(Cable_NB, text='Cable Design')
notebook.add(Trenches_NB, text='Trenches Design')
notebook.add(Earthing_NB, text='Earthing')
notebook.add(Output_NB, text='Output data')
notebook.add(AutoCAD_NB, text='AutoCAD Export')

# Añadir imágenes a las pestañas del notebook
def cargar_imagen(ruta, tamaño):



    p = Path(ruta)
    if not p.is_absolute():
        p = ICONOS_DIR / p
    return ImageTk.PhotoImage(Image.open(p).resize(tamaño, Image.LANCZOS))


    imagen = Image.open(ruta)
    imagen = imagen.resize(tamaño, Image.LANCZOS)
    return ImageTk.PhotoImage(imagen)

imagen_Excel = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Pestaña 1.PNG', (32, 32))
imagen_DTR = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Pestaña 2.PNG', (32, 32))
imagen_DFV = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Pestaña 3.PNG', (32, 32))
imagen_AASS_NB = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Pestaña 4.PNG', (32, 32))
imagen_Cable_NB = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Pestaña 5.PNG', (32, 32))
imagen_Trenches_NB = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Pestaña 6.PNG', (32, 32))
imagen_Earthing_NB = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Pestaña 7.PNG', (32, 32))
imagen_Output_NB = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Pestaña 8.PNG', (32, 32))
imagen_AutoCAD_NB = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Pestaña 9.PNG', (32, 32))

notebook.tab(0, image=imagen_Excel, compound='top')
notebook.tab(1, image=imagen_DTR, compound='top')
notebook.tab(2, image=imagen_DFV, compound='top')
notebook.tab(3, image=imagen_AASS_NB, compound='top')
notebook.tab(4, image=imagen_Cable_NB, compound='top')
notebook.tab(5, image=imagen_Trenches_NB, compound='top')
notebook.tab(6, image=imagen_Earthing_NB, compound='top')
notebook.tab(7, image=imagen_Output_NB, compound='top')
notebook.tab(8, image=imagen_AutoCAD_NB, compound='top')


#Cargar y colocar el logo en la esquina superior derecha
frame_logo_y_guardado = tk.Frame(notebook, background='white')
frame_logo_y_guardado.pack(padx=20, pady=18, anchor='ne')

logo_GRE = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Logo_GRE.PNG', (175, 40))
label_logo_GRE = tk.Label(frame_logo_y_guardado, image=logo_GRE, background='white')
label_logo_GRE.grid(row=0, column=1)

# Definir el guardado y colocar el boton de guardado en la esquina superior derecha

def guardar_proyecto():
    global dicc_var

    
    file_path = filedialog.asksaveasfilename(defaultextension=".json.gz", filetypes=[("GZIP files", "*.json.gz"), ("All files", "*.*")])
    if file_path and not file_path.endswith(".json.gz"):
        file_path += ".json.gz"

    
    def proceso_guardado():
        global error_guardado
        error_guardado = 'Sin error'
        if file_path:
            # Guardar el diccionario en el archivo seleccionado
            # with open(file_path, 'w') as archivo:
            #     json.dump(dicc_var, archivo, indent=4)
            try:
                with gzip.open(file_path, 'wt', encoding='utf-8') as archivo:
                    json.dump(dicc_var, archivo, indent=4)
            except:
                error_guardado = 'Error'
                traceback.print_exc()
                
    def cerrar_ventana_tras_guardar(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_guardado == 'Error':
                messagebox.showerror("Error", "There was an error while saving, file has been corrupted.")
        except:
            print("Error al borrar el gif")
                
    def tarea_guardado():
        proceso_guardado()
        root.after(0, lambda: cerrar_ventana_tras_guardar(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_guardado) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
boton_guardar_proyecto = tk.Button(frame_logo_y_guardado, text="Save Project", command=guardar_proyecto,  bg=rojo_GRS, fg='white', font=('Calibri', 10, 'italic'))
boton_guardar_proyecto.grid(row=0, column=0, padx=40)





#%%
#------------------ PRIMERA PESTAÑA - CARGA DE DATOS-------------------






#-----------------------------------------IMPORTAR PROYECTO--------------------------------------------    

#______FUNCIONES DE CARGA DE DATOS___________ 

def si_None_vacio(entrada): #si el valor que se carga es None se devuelve vacio para que quede mejor si se importa un proyecto parcial
    if entrada==None:
        return []
    else:
        return entrada
            
#Funcion para importar proyecto en JSON
def seleccionar_archivo_y_cargar_proyecto():
    
    #borramos lo existente por si se toca el boton mas de una vez
    for widget in frame_aux_longitudes.winfo_children():
        widget.destroy()
    
    global carpeta_archivo
    ruta_archivo = filedialog.askopenfilename(filetypes=[("GZIP files", "*.json.gz")])
    sep = "\\" if "\\" in ruta_archivo else "/"
    carpeta_archivo =  ruta_archivo[:ruta_archivo.rfind(sep)]+"/"
    
    if not ruta_archivo:
        return
    
    ventana_carga = crear_gif_espera()
    
    #funcion del proceso que ira al hilo secundario
    def proceso_carga():    
        global dicc_var
    
        try:
            # Intentar abrir y cargar el JSON desde gzip
            with gzip.open(ruta_archivo, 'rt', encoding='utf-8') as file:
                dicc_var = json.load(file)
    
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON malformado o archivo truncado: {e}")
            return
        except Exception as e:
            print(f"[ERROR] Al leer el archivo comprimido: {e}")
            return
        
    
        #Cargar entradas/salidas de la primera pestaña (Load Data)
        global bloque_inicial, n_bloques, max_tpb, trackers_extraidos, coord_PCS_DC_inputs, coord_PCS_AASS_inputs, coord_PCS_MV_inputs, coord_Comboxes, coord_Tracknets, coord_TBoxes, coord_AWS, coord_CCTV, polilineas_caminos, pol_guia_MV_FO, pol_envolventes_PAT
        global coord_SS_LVAC, coord_OyM_LVAC, coord_Warehouse_LVAC, coord_MV_Switching_Room, coord_SS_Control_Room, coord_OyM_Control_Room
        global long_XL, long_L, long_M, long_S, trackers_pb
        
        trackers_extraidos      = dicc_var.get('trackers_extraidos',[]) #list

        bloque_inicial          = dicc_var.get('bloque_inicial',[]) #int
        n_bloques               = dicc_var.get('n_bloques',[]) #int
        max_tpb                 = dicc_var.get('max_tpb',[])   #int
        coord_PCS_DC_inputs     = np.array(dicc_var.get('coord_PCS_DC_inputs',[]))      #array numpy
        coord_PCS_AASS_inputs   = np.array(dicc_var.get('coord_PCS_AASS_inputs',[]))    #array numpy
        coord_PCS_MV_inputs     = np.array(dicc_var.get('coord_PCS_MV_inputs',[]))      #array numpy
        coord_Comboxes          = np.array(dicc_var.get('coord_Comboxes',[]))           #array numpy
        coord_Tracknets         = np.array(dicc_var.get('coord_Tracknets',[]))          #array numpy
        coord_TBoxes            = np.array(dicc_var.get('coord_TBoxes',[]))             #array numpy
        coord_AWS               = np.array(dicc_var.get('coord_AWS',[]))                #array numpy
        coord_CCTV              = dicc_var.get('coord_CCTV',[])                         #list
        
        polilineas_caminos      = dicc_var.get('polilineas_caminos', [])                #lista
        pol_guia_MV_FO          = dicc_var.get('pol_guia_MV_FO', [])                    #lista
        pol_envolventes_PAT     = dicc_var.get('pol_envolventes_PAT', [])               #lista
        
        coord_SS_LVAC           = dicc_var.get('coord_SS_LVAC',[])                      #list
        coord_OyM_LVAC          = dicc_var.get('coord_OyM_LVAC',[])                     #list
        coord_Warehouse_LVAC    = dicc_var.get('coord_Warehouse_LVAC',[])               #list
        coord_MV_Switching_Room = dicc_var.get('coord_MV_Switching_Room')               #list
        coord_SS_Control_Room   = dicc_var.get('coord_SS_Control_Room',[])              #list
        coord_OyM_Control_Room  = dicc_var.get('coord_OyM_Control_Room',[])             #list
        
        long_XL                 = dicc_var.get('long_XL',[]) #float
        long_L                  = dicc_var.get('long_L',[]) #float
        long_M                  = dicc_var.get('long_M',[]) #float
        long_S                  = dicc_var.get('long_S',[]) #float
        trackers_pb             = np.array(dicc_var.get('trackers_pb',[]),dtype=object) #array numpy de objects: str y floats
        
        
        #Cargar entradas de la segunda pestaña (Dimensions)
        global pasillo_entre_bandas, dist_min_b_separadas, long_string, pitch, sep, h_modulo, ancho_modulo, salto_motor, saliente_TT, dist_primera_pica_extremo_tr, max_tpf, ancho_caja, largo_caja, sep_caja_tracker, sep_zanja_tracker, config_tracker, pos_salto_motor_L, pos_salto_motor_M, n_mods_serie,        valores_cargados_entradas_dim, valores_cargados_comboboxes_dim
        pasillo_entre_bandas            = si_None_vacio(dicc_var.get('pasillo_entre_bandas',[]))   #float
        dist_min_b_separadas            = si_None_vacio(dicc_var.get('dist_min_b_separadas',[]))   #float 
        long_string                     = si_None_vacio(dicc_var.get('long_string',[]))            #float 
        pitch                           = si_None_vacio(dicc_var.get('pitch',[]))                  #float 
        sep                             = si_None_vacio(dicc_var.get('sep',[]))                    #float 
        h_modulo                        = si_None_vacio(dicc_var.get('h_modulo',[]))               #float
        ancho_modulo                    = si_None_vacio(dicc_var.get('ancho_modulo',[]))           #float
        salto_motor                     = si_None_vacio(dicc_var.get('salto_motor',[]))            #float 
        saliente_TT                     = si_None_vacio(dicc_var.get('saliente_TT',[]))            #float 
        dist_primera_pica_extremo_tr    = si_None_vacio(dicc_var.get('dist_primera_pica_extremo_tr',[])) #float
        max_tpf                         = si_None_vacio(dicc_var.get('max_tpf',[]))                 #float 
        ancho_caja                      = si_None_vacio(dicc_var.get('ancho_caja',[]))              #float 
        largo_caja                      = si_None_vacio(dicc_var.get('largo_caja',[]))              #float 
        sep_caja_tracker                = si_None_vacio(dicc_var.get('sep_caja_tracker',[]))        #float
        sep_zanja_tracker               = si_None_vacio(dicc_var.get('sep_zanja_tracker',[]))       #float
        config_tracker                  = si_None_vacio(dicc_var.get('config_tracker',[]))          #str
        pos_salto_motor_M               = si_None_vacio(dicc_var.get('pos_salto_motor_M',[]))       #str
        pos_salto_motor_L               = si_None_vacio(dicc_var.get('pos_salto_motor_L',[]))       #str
        n_mods_serie                    = si_None_vacio(dicc_var.get('n_mods_serie',[]))            #int  
        
        valores_cargados_entradas_dim = [pasillo_entre_bandas, dist_min_b_separadas-20, long_string, pitch, sep, h_modulo, ancho_modulo, salto_motor, saliente_TT, dist_primera_pica_extremo_tr, max_tpf, ancho_caja, largo_caja, np.round(sep_caja_tracker-largo_caja/2,2), sep_zanja_tracker, n_mods_serie]
        valores_cargados_comboboxes_dim = [config_tracker, pos_salto_motor_M, pos_salto_motor_L]

            #Salidas de la segunda pestaña (para evitar tener que simular de nuevo pestaña a pestaña)
        global filas, max_fpb, bandas, max_b, max_fr, orientacion, filas_en_bandas, max_f_str_b, contorno_bandas, contorno_bandas_sup, contorno_bandas_inf, bandas_anexas, bandas_separadas, bandas_aisladas, bandas_intermedias_o_extremo, strings_fisicos, ori_str_ID, max_spf, dist_ext_opuesto_str
        filas                            = np.array(dicc_var.get('filas',[]))            #array numpy - se lee lista y se pasa a array de numpy
        max_fpb                          = dicc_var.get('max_fpb ',[])                   #int
        bandas                           = np.array(dicc_var.get('bandas',[]))           #array numpy
        max_b                            = dicc_var.get('max_b',[])                      #int
        max_fr                           = dicc_var.get('max_fr',[])                     #int
        orientacion                      = np.array(dicc_var.get('orientacion',[]))      #array numpy
        filas_en_bandas                  = np.array(dicc_var.get('filas_en_bandas',[]),dtype=object) #array numpy de objects: str y floats
        max_f_str_b                      = dicc_var.get('max_f_str_b',[])                #int
        contorno_bandas                  = np.array(dicc_var.get('contorno_bandas',[]))     #array numpy
        contorno_bandas_sup              = np.array(dicc_var.get('contorno_bandas_sup',[])) #array numpy
        contorno_bandas_inf              = np.array(dicc_var.get('contorno_bandas_inf',[])) #array numpy
        bandas_anexas                    = np.array(dicc_var.get('bandas_anexas',[]))       #array numpy
        bandas_separadas                 = np.array(dicc_var.get('bandas_separadas',[]))    #array numpy
        bandas_aisladas                  = np.array(dicc_var.get('bandas_aisladas',[]))     #array numpy
        bandas_intermedias_o_extremo     = np.array(dicc_var.get('bandas_intermedias_o_extremo',[])) #array numpy
        strings_fisicos                  = np.array(dicc_var.get('strings_fisicos',[]))  #array numpy
        ori_str_ID                       = dicc_var.get('ori_str_ID',[])                 #list
        max_spf                          = dicc_var.get('max_spf',[])                    #int
        dist_ext_opuesto_str             = np.array(dicc_var.get('dist_ext_opuesto_str',[]))#array numpy
        
        
        
        #Cargar entradas de la tercera pestaña (PV Design)
        #3.1 MV DESIGN
        global potencia_bloques
        potencia_bloques  = dicc_var.get('potencia_bloques',[])   #list
        
        
        #3.2 CONFIG LV
        global DCBoxes_o_Inv_String, Interconexionado, Polo_cercano, Posicion_optima_caja, String_o_Bus, n_inv, dist_max_inter_bandas, lim_str_interc, conf_inversores, masc, misc, reiniciar_inv,lim_str_dif,   valores_cargados_comboboxes_DFV, valores_cargados_entradas_DFV
        Interconexionado     = si_None_vacio(dicc_var.get('Interconexionado',[]))      #str
        Polo_cercano         = si_None_vacio(dicc_var.get('Polo_cercano',[]))          #str
        DCBoxes_o_Inv_String = si_None_vacio(dicc_var.get('DCBoxes_o_Inv_String',[]))  #str 
        Posicion_optima_caja = si_None_vacio(dicc_var.get('Posicion_optima_caja',[]))  #str
        n_inv                = si_None_vacio(dicc_var.get('n_inv',[]))                 #str
        
            #inv string
        dist_max_inter_bandas   = si_None_vacio(dicc_var.get('dist_max_inter_bandas',[]))  #float
        lim_str_interc          = si_None_vacio(dicc_var.get('lim_str_interc',[]))  #int
        conf_inversores         = np.array(dicc_var.get('conf_inversores',[]))          #array numpy)
        lim_str_dif             = si_None_vacio(dicc_var.get('lim_str_interc',[]))  #int
        reiniciar_inv   = dicc_var.get('reiniciar_inv',[])               #boolean
        
        String_o_Bus        = si_None_vacio(dicc_var.get('String_o_Bus',[]))         #str
        masc                = si_None_vacio(dicc_var.get('masc',[]))                 #int
        misc                = si_None_vacio(dicc_var.get('misc',[]))                 #int
        
        valores_cargados_comboboxes_DFV = [Interconexionado, Polo_cercano, DCBoxes_o_Inv_String, Posicion_optima_caja, String_o_Bus, n_inv]
        valores_cargados_entradas_DFV = [lim_str_dif, masc, misc]
        
            #Salidas de la tercera pestaña (para evitar tener que simular de nuevo pestaña a pestaña)
        global dos_inv_por_bloque, filas_en_cajas, max_c, max_c_block, cajas_fisicas, strings_ID, DCBoxes_ID, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs, filas_con_cable_string, max_bus, capas_de_envolventes, dos_inv, handle_DC_Boxes, handle_inv_string
        global tipos_cajas_por_entradas, TOT_n_cajas_str, TOT_n_cajas_bus, TOT_n_cajas_mix, TOT_n_cajas
        dos_inv_por_bloque               = dicc_var.get('dos_inv_por_bloque',[])          #boolean
        filas_en_cajas                   = np.array(dicc_var.get('filas_en_cajas',[]))    #array numpy
        max_c                            = dicc_var.get('max_c',[])                       #float
        max_c_block                      = dicc_var.get('max_c_block',[])                 #float
        cajas_fisicas                    = np.array(dicc_var.get('cajas_fisicas',[]))     #array numpy
        
            #Simulacion configuracion LV y cajas
        strings_ID             = np.array(dicc_var.get('strings_ID',[]),dtype=object) #array numpy de objects: str y floats
        DCBoxes_ID             = np.array(dicc_var.get('DCBoxes_ID',[]),dtype=object) #array numpy de objects: str y floats
        equi_ibfs              = np.array(dicc_var.get('equi_ibfs',[]))         #array numpy
        equi_ibc               = np.array(dicc_var.get('equi_ibc',[]))          #array numpy
        equi_reverse_ibc       = np.array(dicc_var.get('equi_reverse_ibc',[]))  #array numpy
        equi_reverse_ibfs      = np.array(dicc_var.get('equi_reverse_ibfs',[])) #array numpy
        filas_con_cable_string  = np.array(dicc_var.get('filas_con_cable_string',[]))    #array numpy
        max_bus                = dicc_var.get('max_bus',[])                     #float
        capas_de_envolventes   = dicc_var.get('capas_de_envolventes',[])        #list
        dos_inv                = dicc_var.get('dos_inv',[])                     #boolean
        handle_DC_Boxes        = np.array(dicc_var.get('handle_DC_Boxes',[]))   #array numpy
        handle_inv_string      = np.array(dicc_var.get('handle_inv_string',[]))   #array numpy
        
        tipos_cajas_por_entradas = np.array(dicc_var.get('tipos_cajas_por_entradas',[]))   #array numpy
        TOT_n_cajas_str        = dicc_var.get('TOT_n_cajas_str',[])                     #int
        TOT_n_cajas_bus        = dicc_var.get('TOT_n_cajas_bus',[])                     #int
        TOT_n_cajas_mix        = dicc_var.get('TOT_n_cajas_mix',[])                     #int
        TOT_n_cajas            = dicc_var.get('TOT_n_cajas',[])                     #int
        
        
            #inv de string
        global almacen_strings        
        almacen_strings = dicc_var.get('almacen_strings',[])             #lista
        
        global inv_string, max_inv, max_inv_block, max_str_pinv, posiciones_inv, String_Inverters_ID, filas_en_inversores, inv_como_cajas_fisicas, filas_en_inv_como_filas_en_cajas, comienzos_filas_strings, equi_reverse_ibv, equi_ibv_to_fs, equi_ibv
        inv_string                        = np.array(dicc_var.get('inv_string',[]))                          #array numpy
        max_inv                           = dicc_var.get('max_inv',[])                                       #int
        max_inv_block                     = dicc_var.get('max_inv_block',[])                                 #int
        max_str_pinv                      = dicc_var.get('max_str_pinv',[])                                  #int
        posiciones_inv                    = np.array(dicc_var.get('posiciones_inv',[]))                      #array numpy
        String_Inverters_ID               = np.array(dicc_var.get('String_Inverters_ID',[]))                 #array numpy
        filas_en_inversores               = np.array(dicc_var.get('filas_en_inversores',[]))                 #array numpy
        inv_como_cajas_fisicas            = np.array(dicc_var.get('inv_como_cajas_fisicas',[]))              #array numpy
        filas_en_inv_como_filas_en_cajas  = np.array(dicc_var.get('filas_en_inv_como_filas_en_cajas',[]))    #array numpy
        comienzos_filas_strings           = np.array(dicc_var.get('comienzos_filas_strings',[]))             #array numpy
        equi_reverse_ibv                  = np.array(dicc_var.get('equi_reverse_ibv',[]))                    #array numpy
        equi_ibv_to_fs                    = np.array(dicc_var.get('equi_ibv_to_fs',[]))                      #array numpy
        equi_ibv                          = np.array(dicc_var.get('equi_ibv',[]))                            #array numpy
        
        #3.3 CABLE ROUTING   
            #Simulacion cable MV
        global lineas_MV, pol_cable_MV
        lineas_MV       = dicc_var.get('lineas_MV',[])                     #list
        
        if dicc_var.get('pol_cable_MV', []) is None:
            pol_cable_MV = []
        else:
            raw_data = copy.deepcopy(dicc_var.get('pol_cable_MV', [])) #se importa una copia porque si se hace directamente el proceso de carga modifica tambien internamente el diccionario y volver a guardarlo da problema de serializacion
            pol_cable_MV = []
            for linea in raw_data:
                linea_transformada = []
                for tramo in linea:
                    if isinstance(tramo, list) and len(tramo) == 3:
                        tramo[2] = np.array(tramo[2])  # Convertir la geometría (camino) a np.array
                    linea_transformada.append(tramo)
                pol_cable_MV.append(linea_transformada)

        
            #Simulacion cable string o DC Bus
        global max_p, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque, filas_con_dcb_extendido, Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, extender_DC_Bus
        max_p                   = dicc_var.get('max_p',[])              #int
        pol_cable_string        = None if dicc_var.get("pol_cable_string") is None else np.array(dicc_var.get('pol_cable_string',[]))    #array numpy
        pol_DC_Bus              = None if dicc_var.get("pol_DC_Bus") is None else np.array(dicc_var.get('pol_DC_Bus',[]))  #array numpy
        pol_tubo_corrugado_zanja_DC = np.array(dicc_var.get('pol_tubo_corrugado_zanja_DC',[]))    #array numpy
        max_tubos_DC_bloque     = dicc_var.get('max_tubos_DC_bloque',[])        #int
        filas_con_dcb_extendido = np.array(dicc_var.get('filas_con_dcb_extendido',[]))    #array numpy
        Harness_pos_ID          = np.array(dicc_var.get('Harness_pos_ID',[]))    #array numpy
        Harness_neg_ID          = np.array(dicc_var.get('Harness_neg_ID',[]))    #array numpy
        tipos_harness_pos       = dicc_var.get('tipos_harness_pos',[])        #list
        tipos_harness_neg       = dicc_var.get('tipos_harness_neg',[])        #list
        med_tipos_h_pos         = dicc_var.get('med_tipos_h_pos',[])        #list
        med_tipos_h_neg         = dicc_var.get('med_tipos_h_neg',[])        #list
        harness_pos             = np.array(dicc_var.get('harness_pos',[]),dtype=object)    #array numpy de objects: list y floats
        harness_neg             = np.array(dicc_var.get('harness_neg',[]),dtype=object)    #array numpy de objects: list y floats
        coord_harness_pos       = np.array(dicc_var.get('coord_harness_pos',[]))    #array numpy
        coord_harness_neg       = np.array(dicc_var.get('coord_harness_neg',[]))    #array numpy
        extender_DC_Bus         = dicc_var.get('extender_DC_Bus',[])                #list
        
            #Dibujo cable string o DC Bus
        global handle_cable_string, handle_dcbus
        handle_cable_string     = np.array(dicc_var.get('handle_cable_string',[]))    #array numpy
        handle_dcbus            = np.array(dicc_var.get('handle_dcbus',[]))    #array numpy
        
            #Simulacion cable array
        global pol_array_cable, max_p_array, n_circuitos_max_lado_PCS, n_circuitos_max_entre_trackers, salida_zanja_LV_caja_inv
        pol_array_cable                 = np.array(dicc_var.get('pol_array_cable',[]))             #array numpy
        max_p_array                     = dicc_var.get('max_p_array',[])                           #int
        n_circuitos_max_lado_PCS        = dicc_var.get('n_circuitos_max_lado_PCS',[])              #int
        n_circuitos_max_entre_trackers  = dicc_var.get('n_circuitos_max_entre_trackers',[])        #int 
        salida_zanja_LV_caja_inv        = dicc_var.get('salida_zanja_LV_caja_inv',[])              #float 
        
            #Dibujo cable array
        global handle_cable_array
        handle_cable_array= np.array(dicc_var.get('handle_cable_array',[]))    #array numpy
          
        #CARGAR VARIABLES CUARTA PESTAÑA (SERVICIOS AUXILIARES Y TUBOS)
        #Tubos
        global valores_importados_tubos
        mayoracion_tubo_corrugado_DC    = dicc_var.get('mayoracion_tubo_corrugado_DC',[])       #float
        
        valores_importados_tubos = [mayoracion_tubo_corrugado_DC]
        
        
        global pol_AASS_LVAC, pol_ethernet, max_p_AASS_LVAC, max_p_AASS_eth, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC
        pol_AASS_LVAC               = None if dicc_var.get("pol_AASS_LVAC") is None else np.array(dicc_var.get('pol_AASS_LVAC',[]))  #array numpy
        pol_ethernet                = None if dicc_var.get("pol_ethernet") is None else np.array(dicc_var.get('pol_ethernet',[]))  #array numpy
        max_p_AASS_LVAC             = dicc_var.get('max_p_AASS_LVAC',[])                         #int
        max_p_AASS_eth              = dicc_var.get('max_p_AASS_eth',[])                          #int
        
       #pol_CCTV_LVAC   
        if dicc_var.get('pol_CCTV_LVAC', []) is None: 
            pol_CCTV_LVAC = []
        else:
            raw_data = dicc_var.get('pol_CCTV_LVAC', []) #list of arrays (d,2)
            pol_CCTV_LVAC = []
            for circuito in raw_data:
                pol_CCTV_LVAC.append(np.array(circuito).reshape(-1,2))
                
       #pol_OyM_supply_LVAC        
        if dicc_var.get('pol_OyM_supply_LVAC', []) is None: 
            pol_OyM_supply_LVAC = []
        else:
            raw_data = dicc_var.get('pol_OyM_supply_LVAC', []) #list of arrays (d,2)
            pol_OyM_supply_LVAC = []
            for circuito in raw_data:
                pol_OyM_supply_LVAC.append(np.array(circuito).reshape(-1,2))
                
       #pol_Warehouse_supply_LVAC
        if dicc_var.get('pol_Warehouse_supply_LVAC', []) is None: 
            pol_Warehouse_supply_LVAC = []
        else:
            raw_data = dicc_var.get('pol_Warehouse_supply_LVAC', []) #list of arrays (d,2)
            pol_Warehouse_supply_LVAC = []
            for circuito in raw_data:
                pol_Warehouse_supply_LVAC.append(np.array(circuito).reshape(-1,2))
                
        
        #4. FIBER OPTIC
            #Simulacion cable FO
        global lineas_FO, pol_cable_FO
        lineas_FO       = dicc_var.get('lineas_FO',[])                     #list
        
        if dicc_var.get('pol_cable_FO', []) is None:
            pol_cable_FO = []
        else:
            raw_data = copy.deepcopy(dicc_var.get('pol_cable_FO', [])) #se importa una copia porque si se hace directamente el proceso de carga modifica tambien internamente el diccionario y volver a guardarlo da problema de serializacion
            pol_cable_FO = []
            for linea in raw_data:
                linea_transformada = []
                for tramo in linea:
                    if isinstance(tramo, list) and len(tramo) == 3:
                        tramo[2] = np.array(tramo[2])  # Convertir la geometría (camino) a np.array
                    linea_transformada.append(tramo)
                pol_cable_FO.append(linea_transformada)
        
        #4. Cargar entradas de la cuarta pestaña (Diseño y medicion de cable)
            #Cable MV
        global slack_cable_MV, desnivel_cable_MV, transicion_MV_PCS, transicion_MV_SS, safety_maj_MV, asignacion_secciones_MV, secciones_MV, valores_importados_cable_MV, criterio_secciones_MV
        slack_cable_MV          = si_None_vacio(dicc_var.get('slack_cable_MV',[]))      #float
        desnivel_cable_MV       = si_None_vacio(dicc_var.get('desnivel_cable_MV',[]))   #float
        transicion_MV_PCS       = si_None_vacio(dicc_var.get('transicion_MV_PCS',[]))   #float
        transicion_MV_SS        = si_None_vacio(dicc_var.get('transicion_MV_SS',[]))    #float
        safety_maj_MV           = si_None_vacio(dicc_var.get('safety_maj_MV',[]))       #float
        asignacion_secciones_MV = dicc_var.get('asignacion_secciones_MV',[])            #list
        secciones_MV            = np.array(dicc_var.get('secciones_MV',[]))             #array of numpy
        criterio_secciones_MV   = dicc_var.get('criterio_secciones_MV',[])            #string
        
        valores_importados_cable_MV = [slack_cable_MV, desnivel_cable_MV, transicion_MV_PCS, transicion_MV_SS, safety_maj_MV]
        
            #Cables de string y DC Bus
                #Geometricos y mayoraciones
        global desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, mayoracion_cable_subarray, coca_DC_Bus, extension_primer_tracker
        desnivel_cable_por_pendientes_tramo_aereo   = si_None_vacio(dicc_var.get('desnivel_cable_por_pendientes_tramo_aereo',[]))         #float
        desnivel_cable_por_pendientes_tramo_subt    = si_None_vacio(dicc_var.get('desnivel_cable_por_pendientes_tramo_subt',[]))      #float
        
        transicion_cable_subarray_tracker           = si_None_vacio(dicc_var.get('transicion_cable_subarray_tracker',[])) #float
        transicion_cable_subarray_caja              = si_None_vacio(dicc_var.get('transicion_cable_subarray_caja',[]))    #float
        
        slack_cable_subarray                        = si_None_vacio(dicc_var.get('slack_cable_subarray',[]))              #float
        mayoracion_cable_subarray                   = si_None_vacio(dicc_var.get('mayoracion_cable_subarray',[]))         #float
        
        coca_DC_Bus                                 = si_None_vacio(dicc_var.get('coca_DC_Bus',[]))               #float
        extension_primer_tracker                    = si_None_vacio(dicc_var.get('extension_primer_tracker',[]))     #float
            
               #Entradas brutas
        global seccion_str_SL_Distance_1, seccion_str_SL_Distance_2, seccion_str_location_1, seccion_str_location_2, seccion_str_1, seccion_str_2, seccion_str_3, criterio_seccion_cs, seccion_dcb_SL_Distance_1, seccion_dcb_SL_Distance_2, seccion_dcb_location_1, seccion_dcb_location_2, seccion_dcb_1, seccion_dcb_2, seccion_dcb_3, criterio_seccion_dcb, valores_importados_subarray, valor_marcador_str, valor_marcador_dcbus        
        seccion_str_SL_Distance_1   = si_None_vacio(dicc_var.get('seccion_str_SL_Distance_1',[])) #int
        seccion_str_SL_Distance_2   = si_None_vacio(dicc_var.get('seccion_str_SL_Distance_2',[])) #int
        seccion_str_location_1      = si_None_vacio(dicc_var.get('seccion_str_location_1',[]))    #int
        seccion_str_location_2      = si_None_vacio(dicc_var.get('seccion_str_location_2',[]))    #int
        seccion_str_1               = si_None_vacio(dicc_var.get('seccion_str_1',[]))             #int
        seccion_str_2               = si_None_vacio(dicc_var.get('seccion_str_2',[]))             #int
        seccion_str_3               = si_None_vacio(dicc_var.get('seccion_str_3',[]))             #int
        criterio_seccion_cs         = si_None_vacio(dicc_var.get('criterio_seccion_cs',[]))               #string
        
        seccion_dcb_SL_Distance_1   = si_None_vacio(dicc_var.get('seccion_dcb_SL_Distance_1',[])) #int
        seccion_dcb_SL_Distance_2   = si_None_vacio(dicc_var.get('seccion_dcb_SL_Distance_2',[])) #int
        seccion_dcb_location_1      = si_None_vacio(dicc_var.get('seccion_dcb_location_1',[]))    #int
        seccion_dcb_location_2      = si_None_vacio(dicc_var.get('seccion_dcb_location_2',[]))    #int
        seccion_dcb_1               = si_None_vacio(dicc_var.get('seccion_dcb_1',[]))             #int
        seccion_dcb_2               = si_None_vacio(dicc_var.get('seccion_dcb_2',[]))             #int
        seccion_dcb_3               = si_None_vacio(dicc_var.get('seccion_dcb_3',[]))             #int               
        criterio_seccion_dcb        = si_None_vacio(dicc_var.get('criterio_seccion_dcb',[]))              #string
            
        valores_importados_subarray=[desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, mayoracion_cable_subarray, seccion_str_SL_Distance_1, seccion_str_SL_Distance_2, seccion_str_location_1, seccion_str_location_2, seccion_str_1, seccion_str_2, seccion_str_3, seccion_dcb_SL_Distance_1, seccion_dcb_SL_Distance_2, seccion_dcb_location_1, seccion_dcb_location_2, seccion_dcb_1, seccion_dcb_2, seccion_dcb_3]  
        
        if criterio_seccion_cs == 'Distance':
            valor_marcador_str=1
        else:
            valor_marcador_str=2
            
        if criterio_seccion_dcb == 'Distance':
            valor_marcador_dcbus=1
        else:
            valor_marcador_dcbus=2
            
                #Entradas refinadas para funciones
        global lim_dist_sld_cs_seccion, lim_loc_cs_seccion, secciones_cs, lim_dist_sld_dcb_seccion, lim_loc_dcb_seccion, secciones_dcb

        lim_dist_sld_cs_seccion     = dicc_var.get('lim_dist_sld_cs_seccion',[]) #list
        lim_loc_cs_seccion          = dicc_var.get('lim_loc_cs_seccion',[])      #list
        secciones_cs                = dicc_var.get('secciones_cs',[])            #list
        
        lim_dist_sld_dcb_seccion    = dicc_var.get('lim_dist_sld_dcb_seccion',[]) #list
        lim_loc_dcb_seccion         = dicc_var.get('lim_loc_dcb_seccion',[])      #list
        secciones_dcb               = dicc_var.get('secciones_dcb',[])            #list
        
                #SALIDAS DE SIMULACION
        global med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg
        global med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg, med_tubo_corrugado_zanja_DC

        med_inst_cable_string_pos               = np.array(dicc_var.get('med_inst_cable_string_pos', [])) #array numpy
        med_inst_cable_string_neg               = np.array(dicc_var.get('med_inst_cable_string_neg', [])) #array numpy
        med_cable_string_pos                    = np.array(dicc_var.get('med_cable_string_pos', [])) #array numpy
        tramo_aereo_cable_string_pos            = np.array(dicc_var.get('tramo_aereo_cable_string_pos', [])) #array numpy
        med_cable_string_neg                    = np.array(dicc_var.get('med_cable_string_neg', [])) #array numpy
        sch_cable_de_string_pos                 = np.array(dicc_var.get('sch_cable_de_string_pos', [])) #array numpy
        sch_cable_de_string_neg                 = np.array(dicc_var.get('sch_cable_de_string_neg', [])) #array numpy
        
        med_inst_DC_Bus_pos                     = np.array(dicc_var.get('med_inst_DC_Bus_pos', [])) #array numpy
        med_inst_DC_Bus_neg                     = np.array(dicc_var.get('med_inst_DC_Bus_neg', [])) #array numpy
        med_DC_Bus_pos                          = np.array(dicc_var.get('med_DC_Bus_pos', [])) #array numpy
        tramo_aereo_DC_Bus_pos                  = np.array(dicc_var.get('tramo_aereo_DC_Bus_pos', [])) #array numpy
        med_DC_Bus_neg                          = np.array(dicc_var.get('med_DC_Bus_neg', [])) #array numpy
        sch_DC_Bus_pos                          = np.array(dicc_var.get('sch_DC_Bus_pos', [])) #array numpy
        sch_DC_Bus_neg                          = np.array(dicc_var.get('sch_DC_Bus_neg', [])) #array numpy
        
        med_tubo_corrugado_zanja_DC = np.array(dicc_var.get('med_tubo_corrugado_zanja_DC', [])) #array numpy
             
            #Cable array
                #ENTRADAS
        global desnivel_cable_array_por_pendientes, transicion_array_cable_caja, transicion_array_cable_PCS, slack_array_cable, mayoracion_array_cable, uni_o_multipolar, criterio_seccion_array, lim_dist_array_sld_seccion, lim_n_str_array_seccion, seccion_array_1, seccion_array_2, secciones_array, var_com_uni_o_multipolar, material_array, valor_marcador_array, valores_importados_array
        desnivel_cable_array_por_pendientes = si_None_vacio(dicc_var.get('desnivel_cable_array_por_pendientes',[]))   #float     
        transicion_array_cable_caja         = si_None_vacio(dicc_var.get('transicion_array_cable_caja',[]))           #float
        transicion_array_cable_PCS          = si_None_vacio(dicc_var.get('transicion_array_cable_PCS',[]))            #float
        slack_array_cable                   = si_None_vacio(dicc_var.get('slack_array_cable',[]))                     #float
        mayoracion_array_cable              = si_None_vacio(dicc_var.get('mayoracion_array_cable',[]))                #float
        
        uni_o_multipolar                    = si_None_vacio(dicc_var.get('uni_o_multipolar',[]))                      #int
        criterio_seccion_array              = si_None_vacio(dicc_var.get('criterio_seccion_array',[]))                #string
        lim_dist_array_sld_seccion          = si_None_vacio(dicc_var.get('lim_dist_array_sld_seccion',[]))            #int
        lim_n_str_array_seccion             = si_None_vacio(dicc_var.get('lim_n_str_array_seccion',[]))               #int
        seccion_array_1                     = si_None_vacio(dicc_var.get('seccion_array_1',[]))                       #int
        seccion_array_2                     = si_None_vacio(dicc_var.get('seccion_array_2',[]))                       #int
        secciones_array                     = si_None_vacio(dicc_var.get('secciones_array',[]))                       #list
        material_array                      = si_None_vacio(dicc_var.get('material_array',[]))                        #str
        
        valores_importados_array=[desnivel_cable_array_por_pendientes, transicion_array_cable_caja, transicion_array_cable_PCS, slack_array_cable, mayoracion_array_cable, lim_dist_array_sld_seccion, lim_n_str_array_seccion, seccion_array_1, seccion_array_2, material_array]
        
        if criterio_seccion_array == 'Distance':
            valor_marcador_array=1
        else:
            valor_marcador_array=2
        
        if uni_o_multipolar == 3:
            var_com_uni_o_multipolar='Single Core'
        else:
            var_com_uni_o_multipolar='Multicore'
                
                #SALIDAS
        global med_inst_array_cable_pos, med_inst_array_cable_neg, med_array_cable_pos, med_array_cable_neg, med_array_cable, med_inst_array_cable, sch_array_cable_pos, sch_array_cable_neg, sch_array_cable
        med_inst_array_cable_pos    = np.array(dicc_var.get('med_inst_array_cable_pos', [])) #array numpy
        med_inst_array_cable_neg    = np.array(dicc_var.get('med_inst_array_cable_neg', [])) #array numpy
        med_array_cable_pos         = np.array(dicc_var.get('med_array_cable_pos', []))      #array numpy
        med_array_cable_neg         = np.array(dicc_var.get('med_array_cable_neg', []))      #array numpy
        med_array_cable             = np.array(dicc_var.get('med_array_cable', []))          #array numpy
        med_inst_array_cable        = np.array(dicc_var.get('med_inst_array_cable', []))     #array numpy
        sch_array_cable_pos         = np.array(dicc_var.get('sch_array_cable_pos', []))      #array numpy
        sch_array_cable_neg         = np.array(dicc_var.get('sch_array_cable_neg', []))      #array numpy
        sch_array_cable             = np.array(dicc_var.get('sch_array_cable', []))          #array numpy
        
        
        #Calculos de perdidas
            #ENTRADAS
        global bifaciality, int_mod_STC, power_mod_STC, subarray_temp, array_temp, pot_inv, cos_phi, v_inv, X_cable, valores_importados_perdidas
        bifaciality   = si_None_vacio(dicc_var.get('bifaciality',[]))             #int
        int_mod_STC   = si_None_vacio(dicc_var.get('int_mod_STC',[]))             #float
        power_mod_STC = si_None_vacio(dicc_var.get('power_mod_STC',[]))           #int    
        subarray_temp = si_None_vacio(dicc_var.get('subarray_temp',[]))           #int    
        array_temp    = si_None_vacio(dicc_var.get('array_temp',[]))              #int    
        pot_inv       = si_None_vacio(dicc_var.get('pot_inv',[]))              #int    
        cos_phi       = si_None_vacio(dicc_var.get('cos_phi',[]))              #float 
        v_inv         = si_None_vacio(dicc_var.get('v_inv',[]))                 #int    
        X_cable       = si_None_vacio(dicc_var.get('X_cable',[]))              #float
        
        
        valores_importados_perdidas = [bifaciality, int_mod_STC, power_mod_STC, subarray_temp, array_temp, pot_inv, cos_phi, v_inv, X_cable, material_array]
        
            #SALIDAS
        global perdidas_cables_string, perdidas_DC_Bus, perdidas_array, cdt_array
        perdidas_cables_string = np.array(dicc_var.get('perdidas_cables_string', []))          #array numpy
        perdidas_DC_Bus        = np.array(dicc_var.get('perdidas_DC_Bus', []))          #array numpy
        perdidas_array         = np.array(dicc_var.get('perdidas_array', []))          #array numpy
        cdt_array              = np.array(dicc_var.get('cdt_array', []))          #array numpy
        
        
        
        #Cargar entradas de la quinta pestaña (Zanjas)
            #Entradas
        global n_tubos_max_DC1, ancho_DC1, ancho_DC2, capa_caminos
        n_tubos_max_DC1     = si_None_vacio(dicc_var.get('n_tubos_max_DC1', []))       #int
        ancho_DC1           = si_None_vacio(dicc_var.get('ancho_DC1', []))             #float
        ancho_DC2           = si_None_vacio(dicc_var.get('ancho_DC2', []))             #float
        capa_caminos        = si_None_vacio(dicc_var.get('capa_caminos', []))             #string
         
        
        global Metodo_ancho_zanjas_LV, max_c_tz
        Metodo_ancho_zanjas_LV      = si_None_vacio(dicc_var.get('Metodo_ancho_zanjas_LV', []))         #str
        max_c_tz                    = si_None_vacio(dicc_var.get('max_c_tz',[]))                        #int
        
            #Salidas
        global config_circ_zanjas_LV,info_cada_zanja_LV,tipos_y_subtipos_unicos, anchos_tipos_LV
        config_circ_zanjas_LV       = np.array(dicc_var.get('config_circ_zanjas_LV', []))          #array numpy
        info_cada_zanja_LV          = dicc_var.get('info_cada_zanja_LV',[])            #list
        tipos_y_subtipos_unicos     = dicc_var.get('tipos_y_subtipos_unicos',[])            #list
        anchos_tipos_LV             = dicc_var.get('anchos_tipos_LV',[])            #list
        
        global entradas_diseño_automatico, ancho_min_LV_trench_auto, int_circ_LV_trench_auto, mat_cond_LV_trench_auto, mat_ais_LV_trench_auto, cross_sect_LV_trench_auto, cab_diam_LV_trench_auto, met_inst_LV_trench_auto, temp_LV_trench_auto, res_ter_LV_trench_auto
        ancho_min_LV_trench_auto    = si_None_vacio(dicc_var.get('ancho_min_LV_trench_auto', []))       #float
        int_circ_LV_trench_auto     = si_None_vacio(dicc_var.get('int_circ_LV_trench_auto', []))        #float
        cross_sect_LV_trench_auto   = si_None_vacio(dicc_var.get('cross_sect_LV_trench_auto', []))      #int
        cab_diam_LV_trench_auto     = si_None_vacio(dicc_var.get('cab_diam_LV_trench_auto', []))        #float
        temp_LV_trench_auto         = si_None_vacio(dicc_var.get('temp_LV_trench_auto', []))            #float    
        res_ter_LV_trench_auto      = si_None_vacio(dicc_var.get('res_ter_LV_trench_auto', []))         #float
        mat_cond_LV_trench_auto     = si_None_vacio(dicc_var.get('mat_cond_LV_trench_auto', []))        #str
        mat_ais_LV_trench_auto      = si_None_vacio(dicc_var.get('mat_ais_LV_trench_auto', []))         #str
        met_inst_LV_trench_auto     = si_None_vacio(dicc_var.get('met_inst_LV_trench_auto', []))        #str
        
        #para funciones
        entradas_diseño_automatico = [ancho_min_LV_trench_auto, int_circ_LV_trench_auto, mat_cond_LV_trench_auto, mat_ais_LV_trench_auto, cross_sect_LV_trench_auto, cab_diam_LV_trench_auto, met_inst_LV_trench_auto, temp_LV_trench_auto, res_ter_LV_trench_auto]
        
        #para GUI
        global valores_importados_zanjas_DC, valores_importados_prediseño_zanjas_LV, valores_entradas_zanjas_LV_auto
        valores_importados_zanjas_DC = [n_tubos_max_DC1, ancho_DC1, ancho_DC2]
        valores_importados_prediseño_zanjas_LV = [Metodo_ancho_zanjas_LV, max_c_tz]
        valores_entradas_zanjas_LV_auto=[ancho_min_LV_trench_auto, int_circ_LV_trench_auto, cross_sect_LV_trench_auto, cab_diam_LV_trench_auto, temp_LV_trench_auto, res_ter_LV_trench_auto, mat_cond_LV_trench_auto, mat_ais_LV_trench_auto, met_inst_LV_trench_auto]
        
        global entradas_diseño_manual
        
                
        
        
            #Salidas normales
        global zanjas_DC_ID, PB_zanjas_DC_ID, prediseño_zanjas_LV_ID, prediseño_PB_zanjas_LV_ID, zanjas_LV_ID, PB_zanjas_LV_ID, tipos_zanjas, zanjas_AS_ID
        zanjas_DC_ID                = np.array(dicc_var.get('zanjas_DC_ID',[]))     #array numpy
       #PB_zanjas_DC_ID  ->abajo
        
       #prediseño_PB_zanjas_DC_ID ->abajo
        prediseño_zanjas_LV_ID      = np.array(dicc_var.get('prediseño_zanjas_LV_ID',[]))     #array numpy
        PB_zanjas_LV_ID             = dicc_var.get('PB_zanjas_LV_ID',[])            #list
        zanjas_LV_ID                = dicc_var.get('zanjas_LV_ID',[])               #list
        tipos_zanjas                = dicc_var.get('tipos_zanjas',[])               #list 
        
        zanjas_AS_ID                = np.array(dicc_var.get('zanjas_AS_ID',[]))     #array numpy
        
            #Salidas con arrays por block
        if dicc_var.get('PB_zanjas_DC_ID',[]) == None:
            PB_zanjas_DC_ID = None
        else:
            PB_zanjas_DC_ID = [np.array(arr) for arr in dicc_var.get('PB_zanjas_DC_ID',[])]             #list of arrays
        
        if dicc_var.get('prediseño_PB_zanjas_DC_ID',[]) == None:
            prediseño_PB_zanjas_LV_ID = None
        else:
            prediseño_PB_zanjas_LV_ID = [np.array(arr) for arr in dicc_var.get('prediseño_PB_zanjas_DC_ID',[])]             #list of arrays
            
            
            
        #PESTAÑA DE PUESTA A TIERRA
            #Entradas
        global seccion_PAT_principal, seccion_PAT_anillos, retranqueo_anillos_PAT, mayoracion_electrodo_PAT, valores_importados_electrodo_PAT
        seccion_PAT_principal       = dicc_var.get('seccion_PAT_principal',[])      #int
        seccion_PAT_anillos         = dicc_var.get('seccion_PAT_anillos',[])        #int
        retranqueo_anillos_PAT      = dicc_var.get('retranqueo_anillos_PAT',[])     #float
        mayoracion_electrodo_PAT    = dicc_var.get('mayoracion_electrodo_PAT',[])   #float
        
        valores_importados_electrodo_PAT = [seccion_PAT_principal, seccion_PAT_anillos, retranqueo_anillos_PAT, mayoracion_electrodo_PAT]
        
            #Salidas
        global PAT_latiguillo_entre_trackers, PAT_latiguillo_primera_pica, PAT_terminal_primera_pica, PAT_terminal_DC_Box, PAT_Electrodo
        PAT_latiguillo_entre_trackers   = np.array(dicc_var.get('PAT_latiguillo_entre_trackers', []))   #array numpy
        PAT_latiguillo_primera_pica     = np.array(dicc_var.get('PAT_latiguillo_primera_pica', []))     #array numpy
        PAT_terminal_primera_pica       = np.array(dicc_var.get('PAT_terminal_primera_pica', []))       #array numpy
        PAT_terminal_DC_Box             = np.array(dicc_var.get('PAT_terminal_DC_Box', []))             #array numpy
        PAT_Electrodo                   = dicc_var.get('PAT_Electrodo',[])                              #list


        
    def actualizar_GUI_tras_carga(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
        except:
            print("Error al borrar el gif")
        #Primera pestaña, carga de datos
        borrar_widgets_inicio()
        mostrar_resumen_datos_partida()
        insertar_tabla_trackers_por_bloque_con_longitudes()
        crear_casillas_EXCEL([long_XL,long_L,long_M,long_S])
        

        if potencia_bloques:
            listar_entradas_potencia(potencia_bloques)
        else:
            if n_bloques > 0:
                listar_entradas_potencia([ [] for _ in range(n_bloques+1)])
        
        if lineas_MV:
            cargar_entradas_lineas_MV()
        
        if lineas_MV:   
            entradas_medicion_cables_MV(valores_importados_cable_MV)
        if lineas_FO:
            cargar_entradas_lineas_FO()
            
        entradas_medicion_cables_subarray(valores_importados_subarray)
        entradas_medicion_tubos_DC(valores_importados_tubos)
        entradas_medicion_cables_array(valores_importados_array)
        entradas_calculo_perdidas(valores_importados_perdidas)
        entradas_zanjas_DC(valores_importados_zanjas_DC) 
        entradas_prediseño_zanjas_LV(valores_importados_prediseño_zanjas_LV)
        entradas_anillo_PAT(valores_importados_electrodo_PAT)

        if inv_string.size > 0:
            listar_uni_o_multipolar(var_com_uni_o_multipolar)
            
        if String_o_Bus != 'String Cable':
            listar_inputs_adicionales_dc_bus(coca_DC_Bus,extension_primer_tracker)
            
        if Metodo_ancho_zanjas_LV == 'Manual':
            entradas_zanjas_LV_manual(config_circ_zanjas_LV)
        else:
            entradas_zanjas_LV_auto(valores_entradas_zanjas_LV_auto)
            
        #Segunda pestaña Dimensions
        mr_casillas = crear_casillas_DTR(valores_cargados_entradas_dim, valores_cargados_comboboxes_dim)
        
        #Tercera pestaña DFV
        comboboxes_entradas_DFV(valores_cargados_comboboxes_DFV,valores_cargados_entradas_DFV, reiniciar_inv)
    
        
    #ejecutamos el proceso en paralelo al gif de carga 
    def tarea_1():
        proceso_carga()
        root.after(0, lambda: actualizar_GUI_tras_carga(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    hilo_secundario = threading.Thread(target = tarea_1) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    





#______EJECUCION DE CARGA DE DATOS___________ 



#Funcion de proceso para leer el layout, se saca al global porque se va a usar tanto para leer de primeras como para volver a leer despues
def proceso_leer_layout():
    global error_de_dibujo, info_ausente
    error_de_dibujo='Sin error'
    info_ausente=[]
    
    try:
        pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario
        
        #Buscamos la referencia especifica, si no está abierta va a leer sobre el archivo activo
        referencia = 'XREF_Project_Name.dwg'
        acad = AutoCAD_extension.conexion_con_CAD_para_leer(referencia)
        if acad is None:
            error_de_dibujo='AutoCAD no abierto'
            return #se corta la funcion antes de seguir
        
        root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
        
        #Leemos los cambios introducidos actualizando las variables afectadas
        global bloque_inicial, n_bloques, max_tpb, trackers_extraidos, polilineas_caminos, pol_guia_MV_FO, pol_envolventes_PAT
        global coord_PCS_DC_inputs, coord_PCS_AASS_inputs, coord_PCS_MV_inputs 
        global coord_Comboxes, coord_Tracknets, coord_TBoxes, coord_AWS, coord_CCTV
        global coord_SS_LVAC, coord_OyM_LVAC, coord_Warehouse_LVAC, coord_MV_Switching_Room, coord_SS_Control_Room, coord_OyM_Control_Room
       
        bloque_inicial, n_bloques, max_tpb, trackers_extraidos, salidas_PCS, salidas_SSAA, salidas_facilities, polilineas_caminos, pol_guia_MV_FO, pol_envolventes_PAT, info_ausente = AutoCAD_extension.CAD_read_layout(acad)
        
        coord_PCS_DC_inputs = salidas_PCS[0]
        coord_PCS_AASS_inputs = salidas_PCS[1]
        coord_PCS_MV_inputs = salidas_PCS[2]
        
        coord_Comboxes = salidas_SSAA[0]
        coord_Tracknets = salidas_SSAA[1]
        coord_TBoxes = salidas_SSAA[2]
        coord_AWS = salidas_SSAA[3]
        coord_CCTV =  salidas_SSAA[4]
        
        coord_SS_LVAC = salidas_facilities[0]
        coord_OyM_LVAC = salidas_facilities[1]
        coord_Warehouse_LVAC = salidas_facilities[2]
        coord_MV_Switching_Room = salidas_facilities[3]
        coord_SS_Control_Room = salidas_facilities[4]
        coord_OyM_Control_Room = salidas_facilities[5]
        
        #guardamos en el diccionario los valores actualizados 
        guardar_variables([bloque_inicial, n_bloques, max_tpb, trackers_extraidos, polilineas_caminos, pol_guia_MV_FO, pol_envolventes_PAT,
                           coord_PCS_DC_inputs, coord_PCS_AASS_inputs, coord_PCS_MV_inputs, 
                           coord_Comboxes, coord_Tracknets, coord_TBoxes, coord_AWS, coord_CCTV,
                           coord_SS_LVAC, coord_OyM_LVAC, coord_Warehouse_LVAC, coord_MV_Switching_Room, coord_SS_Control_Room, coord_OyM_Control_Room],
                          ['bloque_inicial', 'n_bloques', 'max_tpb', 'trackers_extraidos', 'polilineas_caminos', 'pol_guia_MV_FO', 'pol_envolventes_PAT',
                           'coord_PCS_DC_inputs', 'coord_PCS_AASS_inputs', 'coord_PCS_MV_inputs',
                           'coord_Comboxes', 'coord_Tracknets', 'coord_TBoxes', 'coord_AWS', 'coord_CCTV',
                           'coord_SS_LVAC', 'coord_OyM_LVAC', 'coord_Warehouse_LVAC', 'coord_MV_Switching_Room', 'coord_SS_Control_Room', 'coord_OyM_Control_Room'])

        pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
        
    except comtypes.COMError as e:
        if e.hresult == -2147417846:
            error_de_dibujo = 'Interaccion con AutoCAD'
        else:
            error_de_dibujo = 'Otro error'
    except Exception:
        error_de_dibujo = 'Otro error'
        traceback.print_exc()
 
    


def volver_a_leer_layout_desde_CAD():     
    def cerrar_ventana_tras_releer_layout(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Reading completed","Information successfully modified in IXPHOS model.")
                
                mostrar_resumen_datos_partida()
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")               
            else:
                # messagebox.showerror("Error", "There was an error while reading, please check that originally drawn elements have not been copypasted or retry.")
                messagebox.showerror("Error", "There was an error while reading, please retry.")
            
            if info_ausente != []:
                messagebox.showinfo("Warning", f'There is missing information in the model that could affect some functionalities. Data from {info_ausente} could not be imported from the active .dwg drawing.')
        except:
            print("Error al borrar el gif")
    
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_releer_layout():
        proceso_leer_layout()
        root.after(0, lambda: cerrar_ventana_tras_releer_layout(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_releer_layout) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        








#---------------------------------------------INICIAR NUEVO PROYECTO-----------------------------------------------
    
#-----------Iniciación con datos de partida desde Excel
def seleccionar_archivo_y_cargar_datos_iniciales_desde_EXCEL():
    global extraccion
    #borramos lo existente por si se toca el boton mas de una vez
    for widget in frame_Excel_longitudes.winfo_children():
        widget.destroy()
        
    ruta_archivo = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    try:
        extraccion = pd.read_excel(ruta_archivo)

        crear_casillas_EXCEL([[],[],[],[]])
        entradas_medicion_cables_subarray(valores_iniciales_subarray)
        listar_inputs_adicionales_dc_bus([],[])
        entradas_medicion_cables_array(valores_iniciales_array)
        entradas_zanjas_DC(valores_iniciales_zanjas_DC)
        entradas_prediseño_zanjas_LV(valores_iniciales_prediseño_zanjas_LV)
        
            
    except Exception as e:
        etiqueta_contenido = tk.Label(frame_tabla_trackers, text=f"{e}")
        etiqueta_contenido.pack(pady=5)        
        
        
        
        
        
#-----------Iniciación con datos de partida desde AutoCAD

def Iniciar_proyecto_desde_AutoCAD():     
    
    def cerrar_ventana_tras_leer_layout(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Reading completed","Information successfully loaded to IXPHOS.")
                
                #No hay fallo, se cargan en la GUI los valores y entradas dependientes
                borrar_widgets_inicio()
                mostrar_resumen_datos_partida()
                crear_tabla_trackers()
                crear_casillas_EXCEL([[],[],[],[]])
                listar_entradas_potencia([[] for _ in range(int(n_bloques+1))])
                entradas_medicion_tubos_DC(valores_iniciales_tubos)
                entradas_medicion_cables_subarray(valores_iniciales_subarray)
                entradas_medicion_cables_array(valores_iniciales_array)
                entradas_calculo_perdidas(valores_iniciales_perdidas)
                entradas_zanjas_DC(valores_iniciales_zanjas_DC)
                entradas_prediseño_zanjas_LV(valores_iniciales_prediseño_zanjas_LV)                
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")               
            else:
                # messagebox.showerror("Error", "There was an error while reading, please check that originally drawn elements have not been copypasted or retry.")
                messagebox.showerror("Error", "There was an error while reading, please retry.")
            
            if info_ausente != []:
                messagebox.showinfo("Warning", f'There is missing information in the model that could affect some functionalities. Data from {info_ausente} could not be imported from the active .dwg drawing.')
        except:
            traceback.print_exc()
            print("Error al borrar el gif")
    
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_leer_layout():
        proceso_leer_layout()
        root.after(0, lambda: cerrar_ventana_tras_leer_layout(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_leer_layout) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
    
    
        
        
        

#Funciones de iniciacion  
        

    #Empezamos borrando los widgets de la pantalla de inicio
def borrar_widgets_inicio():    
    label_logo_IXPHOS.destroy()
    label_texto_IXPHOS.destroy()
    label_texto_subt_GRS.destroy()
    boton_nuevo_proyecto_Excel.destroy()
    boton_nuevo_proyecto_CAD.destroy()
    boton_importar_proyecto.destroy()

def mostrar_resumen_datos_partida():
    #Empezamos borrando los widgets que pueda haber (si se relee el layout hay que borrar y crear de nuevo)
    for widget in frame_resumen_partida.winfo_children():
        widget.destroy()
        
    #Introducimos en el frame de la izquierda el resumen de datos
    tk.Label(frame_resumen_partida, text="Initial Block Number", bg=blanco_roto, font=('Montserrat', 9, 'bold'))       .grid(row=0, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{bloque_inicial}', bg=blanco_roto, font=('Montserrat', 9, 'bold'))          .grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(frame_resumen_partida, text="Last Block Number", bg=blanco_roto, font=('Montserrat', 9, 'bold'))          .grid(row=1, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{n_bloques}', bg=blanco_roto, font=('Montserrat', 9, 'bold'))               .grid(row=1, column=1, padx=10, pady=5)
    
    tk.Label(frame_resumen_partida, text="Total no. trackers", bg=blanco_roto, font=('Montserrat', 9, 'bold'))         .grid(row=2, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{len(trackers_extraidos)}', bg=blanco_roto, font=('Montserrat', 9, 'bold')) .grid(row=2, column=1, padx=10, pady=5)
    
    tk.Label(frame_resumen_partida, text="Max. no. trackers per block", bg=blanco_roto, font=('Montserrat', 9, 'bold')).grid(row=3, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{max_tpb}', bg=blanco_roto, font=('Montserrat', 9, 'bold'))                 .grid(row=3, column=1, padx=10, pady=5)
    
    if coord_PCS_DC_inputs.size > 0:
        n_PCS = np.sum(~np.isnan(coord_PCS_DC_inputs).any(axis=1))
    else:
        n_PCS=0
    tk.Label(frame_resumen_partida, text="No. PCSs", bg=blanco_roto, font=('Montserrat', 9, 'bold'))                   .grid(row=4, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{n_PCS}', bg=blanco_roto, font=('Montserrat', 9, 'bold'))                   .grid(row=4, column=1, padx=10, pady=5)

    if coord_Comboxes.size > 0:
        n_Comboxes = np.sum(~np.isnan(coord_Comboxes).any(axis=1))
    else:
        n_Comboxes=0
    n_Comboxes = np.sum(~np.isnan(coord_Comboxes).any(axis=1))
    tk.Label(frame_resumen_partida, text="No. Comboxes", bg=blanco_roto, font=('Montserrat', 9, 'bold'))               .grid(row=5, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{n_Comboxes}', bg=blanco_roto, font=('Montserrat', 9, 'bold'))              .grid(row=5, column=1, padx=10, pady=5)
    
    if coord_Tracknets.size > 0:
        n_Tracknets = np.sum(~np.isnan(coord_Tracknets).any(axis=1))
    else:
        n_Tracknets=0
    n_Tracknets = np.sum(~np.isnan(coord_Tracknets).any(axis=1))
    tk.Label(frame_resumen_partida, text="No. Tracknets", bg=blanco_roto, font=('Montserrat', 9, 'bold'))              .grid(row=6, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{n_Tracknets}', bg=blanco_roto, font=('Montserrat', 9, 'bold'))             .grid(row=6, column=1, padx=10, pady=5)
    
    if coord_TBoxes.size > 0:
        n_TBoxes = np.sum(~np.isnan(coord_TBoxes).any(axis=1))
    else:
        n_TBoxes=0    
    n_TBoxes = np.sum(~np.isnan(coord_TBoxes).any(axis=1))
    tk.Label(frame_resumen_partida, text="No. T-Boxes", bg=blanco_roto, font=('Montserrat', 9, 'bold'))                .grid(row=7, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{n_TBoxes}', bg=blanco_roto, font=('Montserrat', 9, 'bold'))                .grid(row=7, column=1, padx=10, pady=5)
    
    if coord_AWS.size > 0:
        n_AWS = np.sum(~np.isnan(coord_AWS).any(axis=1))
    else:
        n_AWS=0 
    n_AWS = np.sum(~np.isnan(coord_AWS).any(axis=1))
    tk.Label(frame_resumen_partida, text="No. AWS", bg=blanco_roto, font=('Montserrat', 9, 'bold'))                    .grid(row=8, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{n_AWS}', bg=blanco_roto, font=('Montserrat', 9, 'bold'))                   .grid(row=8, column=1, padx=10, pady=5)
    
    tk.Label(frame_resumen_partida, text="No. CCTV", bg=blanco_roto, font=('Montserrat', 9, 'bold'))                   .grid(row=9, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{len(coord_CCTV)}', bg=blanco_roto, font=('Montserrat', 9, 'bold'))         .grid(row=9, column=1, padx=10, pady=5)
    
    

def crear_tabla_trackers():
    titulos_trackers_extraidos = ['Block', 'Type', 'X coord.', 'Y coord.']
    
    tree = ttk.Treeview(frame_tabla_trackers, columns=titulos_trackers_extraidos, show='headings')
    tree.pack(side='left', fill='both', expand=True)
    
    scrollbar = ttk.Scrollbar(frame_tabla_trackers, orient='vertical', command=tree.yview)
    scrollbar.pack(side='right', fill='y')
    tree.configure(yscroll=scrollbar.set)

    # Configurar encabezados y columnas
    for col in titulos_trackers_extraidos:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')

    # Insertar datos de trackers_extraidos
    for fila in trackers_extraidos:
        tree.insert('', 'end', values=fila)

    
def crear_casillas_EXCEL(valor_inicial):
    etiq_trackers = ["XL", "L", "M", "S"]
    entradas = {}
    
    # Crear la fila inicial con los nombres de las columnas
    tk.Label(frame_aux_longitudes, text="Tracker type", bg=blanco_roto, font=('Montserrat', 10, 'bold')).grid(row=0, column=0, padx=10, pady=5)
    tk.Label(frame_aux_longitudes, text="Length (m)", bg=blanco_roto, font=('Montserrat', 10, 'bold')).grid(row=0, column=1, padx=10, pady=5)

    # Crear las filas con las etiquetas y entradas
    for i, etiq_tracker in enumerate(etiq_trackers):
        tk.Label(frame_aux_longitudes, text=etiq_tracker, fg=rojo_GRS, bg=blanco_roto, font=('Montserrat', 10, 'bold')).grid(row=i+1, column=0, padx=10, pady=5)
        
        valor = tk.StringVar()
        valor.set(valor_inicial[i])

        entrada = tk.Entry(frame_aux_longitudes, textvariable=valor, width=10)
        entrada.grid(row=i+1, column=1, padx=10, pady=5)
        entradas[etiq_tracker] = entrada
    
    def leer_long_trackers():  
        longitudes = {}
        for tracker, entrada in entradas.items():
            try:
                longitudes[tracker] = float(entrada.get())
            except ValueError:
                longitudes[tracker] = 0.0
        
        long_XL = longitudes["XL"]
        long_L = longitudes["L"]
        long_M = longitudes["M"]
        long_S = longitudes["S"]
        

        #funcion de proceso para el hilo secundario
        def proceso_leer_long_trackers():
            global trackers_pb
            trackers_pb_sin_ordenar = Algoritmo_IXPHOS_1_Config_fisica.preparar_datos_trackers(trackers_extraidos, n_bloques, max_tpb, long_XL, long_L, long_M, long_S)
            trackers_pb = Algoritmo_IXPHOS_1_Config_fisica.ordenar_x_y(trackers_pb_sin_ordenar, bloque_inicial,n_bloques)
            
            #Guardamos los valores de las variables en el diccionario
            guardar_variables([long_S,long_M,long_L,long_XL,trackers_pb],['long_S','long_M','long_L','long_XL','trackers_pb'])
            
        def actualizar_GUI_tras_leer_long_trackers(ventana_carga):
            try:
                ventana_carga.destroy() #se cierra el gif de carga
                
            except:
                print("Error al borrar el gif")

            insertar_tabla_trackers_por_bloque_con_longitudes()
            
            
        #ejecutamos el proceso en paralelo al gif de carga
        def tarea_leer_long_trackers():
            proceso_leer_long_trackers()
            root.after(0, lambda: actualizar_GUI_tras_leer_long_trackers(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
        ventana_carga = crear_gif_espera()
        
        hilo_secundario = threading.Thread(target = tarea_leer_long_trackers) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
        hilo_secundario.start()
        

    boton_leer = tk.Button(frame_aux_longitudes, text="Read values", command=leer_long_trackers, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
    boton_leer.grid(row=len(etiq_trackers) + 1, column=0, columnspan=2, pady=10)
    
    boton_volver_a_leer_layout = tk.Button(frame_aux_longitudes, text="Reload layout", command=volver_a_leer_layout_desde_CAD, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
    boton_volver_a_leer_layout.grid(row=len(etiq_trackers) + 2, column=0, columnspan=2, pady=80)
    

    
            
def insertar_tabla_trackers_por_bloque_con_longitudes():
    # Eliminar el árbol inicial
    for widget in frame_tabla_trackers.winfo_children():
        widget.destroy()
    
    # Función para actualizar la tabla basada en el valor de la spinbox
    def update_table():
        # Limpiar el contenido existente de la tabla
        for row in tree.get_children():
            tree.delete(row)
        
        # Obtener el índice seleccionado de la spinbox
        index = int(spinbox.get())
        
        # Rellenar la tabla con los datos del índice seleccionado del array
        for row in trackers_pb[index]:
            tree.insert('', 'end', values=list(row))
            
    # Crear etiqueta para el texto "Nº de bloque"
    label_bloque = tk.Label(frame_tabla_trackers, text="Block number", bg=blanco_roto, font=('Montserrat', 10, 'bold'), justify='center')
    label_bloque.grid(row=0, column=0, padx=5, pady=5, sticky='e')
    
    # Crear spinbox para seleccionar el índice de la primera dimensión
    spinbox = tk.Spinbox(frame_tabla_trackers, from_=bloque_inicial, to=trackers_pb.shape[0]-1, command=update_table, width=2, font=('Montserrat', 10))
    spinbox.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    # Crear Treeview para mostrar los datos del array
    estilo_tabla_trackers = ttk.Style()
    estilo_tabla_trackers.configure("Treeview", borderwidth=2, relief="solid", font=('Montserrat', 10))
    estilo_tabla_trackers.configure("Treeview.Heading", font=('Montserrat', 10, 'bold'), borderwidth=2, background=rojo_GRS)
    
    tree = ttk.Treeview(frame_tabla_trackers, columns=("Column 1", "Column 2", "Column 3", "Column 4"), show='headings', style='Treeview')
    tree.heading("Column 1", text="Tracker Type", anchor='center')
    tree.heading("Column 2", text="Length", anchor='center')
    tree.heading("Column 3", text="X Coordinate", anchor='center')
    tree.heading("Column 4", text="Y Coordinate", anchor='center')
    tree.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
    
    # Permitir que el Treeview se expanda
    frame_tabla_trackers.grid_rowconfigure(1, weight=1)
    frame_tabla_trackers.grid_columnconfigure(0, weight=1)
    frame_tabla_trackers.grid_columnconfigure(1, weight=1)
    
    # Crear barra de desplazamiento
    scrollbar = ttk.Scrollbar(frame_tabla_trackers, orient='vertical', command=tree.yview)
    scrollbar.grid(row=1, column=2, padx=5, pady=5, sticky='ns')
    tree.configure(yscroll=scrollbar.set)
    
    # Inicializar la tabla con los datos del primer índice del array
    update_table()
        
    # Centrar valores en las columnas
    for col in ("Column 1", "Column 2", "Column 3", "Column 4"):
        tree.column(col, anchor='center')

    #Aprovechamos a inicializar las spinbox de toda la GUI con los valores leidos previamente, porque mostrar resultados se usa tanto al importar el proyecto como al empezarlo desde cero
    spinbox_array.config(from_=bloque_inicial, to=n_bloques)
    spinbox_dcboxes.config(from_=bloque_inicial, to=n_bloques)
    spinbox_inter.config(from_=bloque_inicial, to=n_bloques)
    spinbox_lv.config(from_=bloque_inicial, to=n_bloques)
    spinbox_str_bus.config(from_=bloque_inicial, to=n_bloques)
    spinbox_zdc.config(from_=bloque_inicial, to=n_bloques)
    spinbox_zlv.config(from_=bloque_inicial, to=n_bloques)
    spinbox_PAT.config(from_=bloque_inicial, to=n_bloques)
    
    
    
    
    
    
    
#---------------------EJECUCION INICIAL PRIMERA PESTAÑA------------------------------
            
# Creamos un frame para meter en el tres frames y darles un margen comun respecto a los bordes
frame_inicio_container = tk.Frame(Carga_Excel, background=blanco_roto)
frame_inicio_container.pack(side='left', padx=50, pady=50, fill='both', expand=True)

#Lo dividimos en tres subframes para meter las funcionalidades despues
frame_inicio_container.grid_columnconfigure(0, weight=1)
frame_inicio_container.grid_columnconfigure(1, weight=3)
frame_inicio_container.grid_columnconfigure(2, weight=1)


#Creamos un frame para los datos importados de partida
frame_resumen_partida = tk.Frame(frame_inicio_container, background=blanco_roto)
frame_resumen_partida.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

# Creamos un frame para meter en el la tabla de datos y la scrollbar
frame_tabla_trackers = tk.Frame(frame_inicio_container, background=blanco_roto)
frame_tabla_trackers.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

# Creamos un nuevo frame para organizar más facilmente la insercion de las longitudes de trackers
frame_aux_longitudes = tk.Frame(frame_inicio_container, background=blanco_roto)
frame_aux_longitudes.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')


    # Cargar y colocar el logo y el nombre en ese frame, luego se elimina al cargar el archivo
logo_IXPHOS = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Logo_IXPHOS.png', (256, 256))

label_logo_IXPHOS = tk.Label(frame_inicio_container, image=logo_IXPHOS, background=blanco_roto)
label_logo_IXPHOS.place(relx=0.5, y=0, anchor='n')
label_texto_IXPHOS = tk.Label(frame_inicio_container, text='I X P H O S', bg=blanco_roto, fg=rojo_GRS, font=('Palatino Linotype', 40, 'bold', "underline"))
label_texto_IXPHOS.place(relx=0.5, y=320, anchor='n')
label_texto_subt_GRS = tk.Label(frame_inicio_container, text='PV Plant Design Software by Gransolar', bg=blanco_roto, fg=rojo_GRS, font=('Palatino Linotype', 10, 'bold', 'italic'))
label_texto_subt_GRS.place(relx=0.55, y=395, anchor='n')

boton_nuevo_proyecto_Excel = tk.Button(frame_inicio_container, text="Start new project from Excel", command=seleccionar_archivo_y_cargar_datos_iniciales_desde_EXCEL, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_nuevo_proyecto_Excel.place(relx=0.22, y=550)

boton_nuevo_proyecto_CAD = tk.Button(frame_inicio_container, text="Start new project from AutoCAD", command=Iniciar_proyecto_desde_AutoCAD, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_nuevo_proyecto_CAD.place(relx=0.47, y=550)

boton_importar_proyecto = tk.Button(frame_inicio_container, text="Import existing project", command=seleccionar_archivo_y_cargar_proyecto, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_importar_proyecto.place(relx=0.72, y=550)



#%%

#---------------------------SEGUNDA PESTAÑA - ACOTACIONES Y DATOS DE TRACKERS--------------------

# Crear un frame para meter en él dos frames y darles un margen común respecto a los bordes
frame_DTR_container = tk.Frame(DTR, background=rojo_suave)
frame_DTR_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)

# Configurar la cuadrícula para que las filas y columnas se expandan en frame_DTR_container
frame_DTR_container.grid_rowconfigure(0, weight=1)  
frame_DTR_container.grid_columnconfigure(0, weight=1)  
frame_DTR_container.grid_columnconfigure(1, weight=10)  # ocupa 15 veces en x lo que ocupa el primero

# Crear un frame para meter en él los inputs de diseño
frame_DTR_datos = tk.Frame(frame_DTR_container, background=blanco_roto)
frame_DTR_datos.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

# Crear otro frame para meter en él los dibujos de los detalles
frame_DTR_dibujos = tk.Frame(frame_DTR_container, background=blanco_roto)
frame_DTR_dibujos.grid(row=0, column=1, sticky='nsew', padx=0, pady=0)

# Creamos las casillas de las acotaciones de los trackers en el primer frame
def crear_casillas_DTR(valores_dados_entradas, valores_dados_comboboxes):
    global entradas_DTR, entrada_config_tracker, entrada_pos_salto_motor_0, entrada_pos_salto_motor_1
    
    acotaciones_DTR = ["Max. SB (not isolated)", "RDSB", "String length","Pitch", "Separation", "H_mod", "W_mod", "Motor jump", "STT", "1st Pile distance", "Max no. tr per row", "W_B", "D_B", "Sep. Tr-B", "Sep. Trench-B", "No. mod/string"]
    entradas_DTR = []
    
    # Crear la fila inicial con los nombres de las columnas
    tk.Label(frame_DTR_datos, text="Dimension", bg=blanco_roto, font=('Montserrat', 10, 'bold', 'underline')).grid(row=0, column=0, padx=0, pady=5, sticky='w')
    tk.Label(frame_DTR_datos, text="(m)", bg=blanco_roto, font=('Montserrat', 10, 'bold', 'underline')).grid(row=0, column=1, padx=0, pady=5, sticky='e')
    
    # Crear las filas con las etiquetas y entradas
    max_row=0
    for i, acotaciones_DTR in enumerate(acotaciones_DTR):
        tk.Label(frame_DTR_datos, text=acotaciones_DTR, fg=rojo_GRS, bg=blanco_roto, font=('Montserrat', 10, 'bold')).grid(row=i+1, column=0, padx=0, pady=5, sticky='w')
        valor = tk.StringVar()
        valor.set(valores_dados_entradas[i])
        entrada = tk.Entry(frame_DTR_datos, textvariable = valor,  width=10)
        entrada.grid(row=i+1, column=1, padx=0, pady=5, sticky='e')
        entradas_DTR.append(entrada)
        max_row=max_row+1
    
    
    #Metemos una combobox para indicar si el tracker es monofila o bifila
    opciones_tr_conf = ["Single Row", "Double Row"]
    entrada_config_tracker = tk.StringVar(value = valores_dados_comboboxes[0])
    tk.Label(frame_DTR_datos, text='Tracker config.', fg=rojo_GRS, bg=blanco_roto, font=('Montserrat', 10, 'bold')).grid(row=max_row+1,column=0, padx=0,pady=5,sticky='w')
    ttk.Combobox(frame_DTR_datos, textvariable=entrada_config_tracker, values=opciones_tr_conf, width=11).grid(row=max_row+1,column=1, padx=0, pady=5,sticky='e')
    
    #Metemos otra combobox para indicar donde está el motor en trackers M
    opciones_mj_M = ["North", "Half", "South"]
    entrada_pos_salto_motor_0 = tk.StringVar(value = valores_dados_comboboxes[1])
    tk.Label(frame_DTR_datos, text='Motor loc. (M tracker)', fg=rojo_GRS, bg=blanco_roto, font=('Montserrat', 10, 'bold')).grid(row=max_row+2,column=0, padx=0,pady=5,sticky='w')
    ttk.Combobox(frame_DTR_datos, textvariable=entrada_pos_salto_motor_0, values=opciones_mj_M, width=11).grid(row=max_row+2,column=1, padx=0, pady=5,sticky='e')
    
    
    #Metemos otra combobox para indicar donde está el motor en trackers L
    opciones_mj_L = ["North", "Half", "South"]
    entrada_pos_salto_motor_1 = tk.StringVar(value = valores_dados_comboboxes[2])
    tk.Label(frame_DTR_datos, text='Motor loc. (L tracker)', fg=rojo_GRS, bg=blanco_roto, font=('Montserrat', 10, 'bold')).grid(row=max_row+3,column=0, padx=0,pady=5,sticky='w')
    ttk.Combobox(frame_DTR_datos, textvariable=entrada_pos_salto_motor_1, values=opciones_mj_L, width=11).grid(row=max_row+3,column=1, padx=0, pady=5,sticky='e')
    
    return max_row+3

valores_iniciales_entradas=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
valores_iniciales_comboboxes=[[],[],[]]
mr_casillas = crear_casillas_DTR(valores_iniciales_entradas,valores_iniciales_comboboxes)

#Importamos los dibujos de las acotaciones
imagen_DTR_Tracker_GEN = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Dimensions - GEN.PNG', (250, 520))
imagen_DTR_Tracker_A = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Dimensions - Detail A.PNG', (350, 470))
imagen_DTR_Tracker_B = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Dimensions - Detail B.PNG', (300, 250))
imagen_DTR_Tracker_C = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Dimensions - Detail C.PNG', (390, 370))

#OPCION PARA HACERLO CON GRID Y SUBFRAMES
# # Crear los subframes
# frame_DTR_d1 = tk.Frame(frame_DTR_dibujos, bg=blanco_roto)
# frame_DTR_d2 = tk.Frame(frame_DTR_dibujos, bg=blanco_roto)
# frame_DTR_d3 = tk.Frame(frame_DTR_dibujos, bg=blanco_roto)

# # Empaquetar los subframes
# frame_DTR_d1.grid(row=0,column=0, sticky='n', padx=0, pady=0)
# frame_DTR_d2.grid(row=0,column=1, sticky='n', padx=0, pady=0)
# frame_DTR_d3.grid(row=0,column=2, sticky='n', padx=0, pady=0)

# # Configurar la cuadrícula para que las filas y columnas se expandan
# frame_DTR_dibujos.grid_columnconfigure(0, weight=1)
# frame_DTR_dibujos.grid_columnconfigure(1, weight=1)
# frame_DTR_dibujos.grid_columnconfigure(2, weight=1)

# #Creamos las etiquetas e insertamos en ellas las imagenes
# detalle_DTR_Tracker_GEN = tk.Label(frame_DTR_d1, image=imagen_DTR_Tracker_GEN, bg=blanco_roto)
# detalle_DTR_Tracker_GEN.pack(side='top',expand=True, fill='both', pady=50)

# detalle_DTR_Tracker_A = tk.Label(frame_DTR_d2, image=imagen_DTR_Tracker_A, bg=blanco_roto)
# detalle_DTR_Tracker_A.pack(side='top',expand=True, fill='both', pady=50)

# detalle_DTR_Tracker_B = tk.Label(frame_DTR_d3, image=imagen_DTR_Tracker_B, bg=blanco_roto)
# detalle_DTR_Tracker_B.pack(side='top',expand=True, fill='both', pady=50)

# detalle_DTR_Tracker_C = tk.Label(frame_DTR_d3, image=imagen_DTR_Tracker_C, bg=blanco_roto)
# detalle_DTR_Tracker_C.pack(side='bottom',expand=True, fill='y', pady=25)

detalle_DTR_Tracker_GEN = tk.Label(frame_DTR_dibujos, image=imagen_DTR_Tracker_GEN, bg=blanco_roto)
detalle_DTR_Tracker_GEN.place(relx=0.12, rely=0.15, anchor='n')

detalle_DTR_Tracker_A = tk.Label(frame_DTR_dibujos, image=imagen_DTR_Tracker_A, bg=blanco_roto)
detalle_DTR_Tracker_A.place(relx=0.4, rely=0.1, anchor='n')

detalle_DTR_Tracker_B = tk.Label(frame_DTR_dibujos, image=imagen_DTR_Tracker_B, bg=blanco_roto)
detalle_DTR_Tracker_B.place(relx=0.8, rely=0.05, anchor='n')

detalle_DTR_Tracker_C = tk.Label(frame_DTR_dibujos, image=imagen_DTR_Tracker_C, bg=blanco_roto)
detalle_DTR_Tracker_C.place(relx=0.8, rely=0.45, anchor='n')



# AÑADIMOS UN BOTON PARA EJECUTAR EL ALGORITMO CON ESTOS DATOS HASTA OBTENER LA POSICION FISICA DE CADA STRING
def simulacion_fisica_planta():
    
    def proceso_sim_planta_fisica():
        global pasillo_entre_bandas, dist_min_b_separadas, long_string, pitch, sep, h_modulo, ancho_modulo, salto_motor, saliente_TT, dist_primera_pica_extremo_tr, max_tpf, ancho_caja, largo_caja, sep_caja_tracker, sep_zanja_tracker, config_tracker, pos_salto_motor_M, pos_salto_motor_L, n_mods_serie
        global filas, max_fpb, bandas, max_b, max_fr, orientacion, filas_en_bandas, max_f_str_b, contorno_bandas, contorno_bandas_sup, contorno_bandas_inf, bandas_anexas, bandas_separadas, bandas_aisladas, bandas_intermedias_o_extremo, strings_fisicos, ori_str_ID, max_spf, dist_ext_opuesto_str
        global error_de_simulacion
        
        error_de_simulacion = 'Sin error'
        
        try:
            #Asociamos las entradas a los nombres de las variables del algoritmo al pulsarse el boton de simular
            pasillo_entre_bandas = float(entradas_DTR[0].get())    
            dist_min_b_separadas = float(entradas_DTR[1].get()) + 20
            long_string = float(entradas_DTR[2].get())
            pitch = float(entradas_DTR[3].get())
            sep = float(entradas_DTR[4].get())
            h_modulo = float(entradas_DTR[5].get())
            ancho_modulo = float(entradas_DTR[6].get())
            salto_motor = float(entradas_DTR[7].get())
            saliente_TT = float(entradas_DTR[8].get())
            dist_primera_pica_extremo_tr = float(entradas_DTR[9].get())
            max_tpf = int(entradas_DTR[10].get())
            ancho_caja = float(entradas_DTR[11].get())
            largo_caja = float(entradas_DTR[12].get())
            sep_caja_tracker = float(entradas_DTR[13].get()) + largo_caja/2
            sep_zanja_tracker = float(entradas_DTR[14].get())
            n_mods_serie=int(entradas_DTR[15].get())
            
            config_tracker = entrada_config_tracker.get()
    
            pos_salto_motor_M = entrada_pos_salto_motor_0.get()
            pos_salto_motor_L = entrada_pos_salto_motor_1.get()
        

            # sin conocerlo, el maximo numero de filas posible por bloque es como máximo igual al de trackers (ningun tracker alineado)
            max_fpb = max_tpb
        
            filas, max_fpb = Algoritmo_IXPHOS_1_Config_fisica.agrupar_en_filas(trackers_pb, bloque_inicial,n_bloques, max_tpb, max_fpb, max_tpf, sep)
            
            # sin conocerlo, el maximo numero de bandas posible por bloque es como máximo igual al de filas (ninguna fila cercana a otra) aunque no sea real
            max_bpb = max_fpb
            
            bandas, max_b, max_fr = Algoritmo_IXPHOS_1_Config_fisica.agrupacion_en_bandas(filas, pitch, bloque_inicial,n_bloques, max_fpb, max_bpb, max_tpf, coord_PCS_DC_inputs)
            
            orientacion = Algoritmo_IXPHOS_1_Config_fisica.orientacion_hacia_inversor(bandas, coord_PCS_DC_inputs, bloque_inicial,n_bloques, max_b, max_fr)
            
            #sacamos las filas en las bandas y sus puntos de contorno, faltaria ordenarlas todavia
            filas_en_bandas, max_f_str_b = Algoritmo_IXPHOS_1_Config_fisica.sacar_y_ordenar_filas_en_bandas(bandas, orientacion, config_tracker, bloque_inicial,n_bloques, max_b, max_tpf, max_fr, h_modulo, pitch)
            
            contorno_bandas, contorno_bandas_sup, contorno_bandas_inf = Algoritmo_IXPHOS_1_Config_fisica.contorno_de_las_bandas(filas_en_bandas,bloque_inicial,n_bloques,max_b,max_f_str_b, h_modulo)
            
            #hallamos los tipos de bandas
            bandas_anexas, bandas_separadas, bandas_aisladas, bandas_intermedias_o_extremo = Algoritmo_IXPHOS_1_Config_fisica.clasificacion_bandas(bloque_inicial,n_bloques, max_b, contorno_bandas, coord_PCS_DC_inputs, orientacion, pasillo_entre_bandas, dist_min_b_separadas)
            
            #ordenamos las bandas segun criterio GRS y actualizamos las variables afectadas que luego se van a volver a usar
            bandas , orientacion,  bandas_anexas, bandas_separadas, bandas_intermedias_o_extremo, bandas_aisladas, filas_en_bandas, contorno_bandas, contorno_bandas_sup, contorno_bandas_inf = Algoritmo_IXPHOS_1_Config_fisica.ordenar_bandas(bandas,contorno_bandas, contorno_bandas_sup, contorno_bandas_inf, bandas_anexas, bandas_separadas, bandas_aisladas, bandas_intermedias_o_extremo, filas_en_bandas, orientacion,bloque_inicial,n_bloques,max_b, pasillo_entre_bandas)
            
            #calculamos la posicion fisica de cada string
            strings_fisicos, ori_str_ID, max_spf, dist_ext_opuesto_str = Algoritmo_IXPHOS_1_Config_fisica.filas_de_strings(bandas, filas_en_bandas, config_tracker, orientacion, bloque_inicial,n_bloques, max_b, max_f_str_b, max_tpf, h_modulo, pitch, salto_motor, pos_salto_motor_M, pos_salto_motor_L)
    
    
            guardar_variables([pasillo_entre_bandas, dist_min_b_separadas, long_string, pitch, sep, h_modulo, ancho_modulo, salto_motor, saliente_TT, dist_primera_pica_extremo_tr, max_tpf, ancho_caja, largo_caja, sep_caja_tracker, sep_zanja_tracker, config_tracker, pos_salto_motor_M, pos_salto_motor_L, n_mods_serie],['pasillo_entre_bandas', 'dist_min_b_separadas', 'long_string', 'pitch', 'sep', 'h_modulo', 'ancho_modulo', 'salto_motor', 'saliente_TT', 'dist_primera_pica_extremo_tr', 'max_tpf', 'ancho_caja', 'largo_caja', 'sep_caja_tracker', 'sep_zanja_tracker', 'config_tracker', 'pos_salto_motor_M', 'pos_salto_motor_L', 'n_mods_serie'])
            guardar_variables([filas, max_fpb, bandas, max_b, max_fr, orientacion, filas_en_bandas, max_f_str_b, contorno_bandas, contorno_bandas_sup, contorno_bandas_inf, bandas_anexas, bandas_separadas, bandas_aisladas, bandas_intermedias_o_extremo, strings_fisicos, ori_str_ID, max_spf, dist_ext_opuesto_str],['filas', 'max_fpb', 'bandas', 'max_b', 'max_fr', 'orientacion', 'filas_en_bandas', 'max_f_str_b', 'contorno_bandas', 'contorno_bandas_sup', 'contorno_bandas_inf', 'bandas_anexas', 'bandas_separadas', 'bandas_aisladas', 'bandas_intermedias_o_extremo', 'strings_fisicos', 'ori_str_ID', 'max_spf', 'dist_ext_opuesto_str'])
        
        except Exception:
            error_de_simulacion = 'Error'
            traceback.print_exc()
        
    def cerrar_ventana_tras_simular(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
        except:
            print("Error al borrar el gif")

    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_3():
        proceso_sim_planta_fisica()
        root.after(0, lambda: cerrar_ventana_tras_simular(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_3) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

        
boton_string_fisicos = tk.Button(frame_DTR_datos, text="Read model", command=simulacion_fisica_planta, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_string_fisicos.grid(row=mr_casillas+1, column=0, columnspan=2, pady=10)





#%%

#3.---------------------------TERCERA PESTAÑA - CONFIGURACION ELECTRICA --------------------


#------LAYOUT DE FRAMES PARA INTRODUCIR DATOS
# Crear un frame para meter en él dos frames y darles un margen común respecto a los bordes
frame_DFV_container = tk.Frame(DFV, background=blanco_roto)
frame_DFV_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)

# Introducir un nuevo notebook para diferenciar diseños de configuracion de MV, configuracion de LV y routing de cables de potencia
notebook_DFV = ttk.Notebook(frame_DFV_container, style='TNotebook')
notebook_DFV.pack(fill=tk.BOTH, expand=True)

# Crear las pestañas con el color de fondo definido
MV_design = tk.Frame(notebook_DFV, background=blanco_roto)
LV_design = tk.Frame(notebook_DFV, background=blanco_roto)
Cable_routing_design = tk.Frame(notebook_DFV, background=blanco_roto)

# Añadir las pestañas al notebook
notebook_DFV.add(MV_design, text='MV Configuration')
notebook_DFV.add(LV_design, text='LV Configuration')
notebook_DFV.add(Cable_routing_design, text='Main Cable Routing')





#------Frames MV
frame_MV_container= tk.Frame(MV_design, background=blanco_roto)
frame_MV_container.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

# Configurar la cuadrícula para partir el frame_DFV_container en dos verticales, uno para los datos y otro para una ventana de dibujos explicativos
frame_MV_container.grid_rowconfigure(0, weight=1)
frame_MV_container.grid_columnconfigure(0, weight=1)  
frame_MV_container.grid_columnconfigure(1, weight=1) 

    #Creamos subframe a la izquierda para meter potencia de las lineas y a la derecha para meter la configuracion
frame_MV_power = tk.Frame(frame_MV_container, background=blanco_roto)
frame_MV_power.grid(row=0, column=0, sticky='nsew', padx=10, pady=0)

frame_MV_lines = tk.Frame(frame_MV_container, background=blanco_roto)
frame_MV_lines.grid(row=0, column=1, sticky='nsew', padx=50, pady=0)


#------Frames LV
frame_LV_container = tk.Frame(LV_design, background=blanco_roto)
frame_LV_container.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
# Configurar la cuadrícula para partir el frame_DFV_container en tres verticales, uno para los datos y el boton de simulacion, otro para datos extra segun DCBoxes o INV string y otro para los botones de dibujo y lectura
frame_LV_container.grid_rowconfigure(0, weight=2)
frame_LV_container.grid_rowconfigure(1, weight=1)
frame_LV_container.grid_columnconfigure(0, weight=1)
frame_LV_container.grid_columnconfigure(1, weight=1)    
frame_LV_container.grid_columnconfigure(2, weight=1) 

# Creamos el frame para los datos de entrada y el boton de simulacion
frame_DLV_data = tk.Frame(frame_LV_container, background=blanco_roto)
frame_DLV_data.grid(row=0, column=0, sticky='nsew', padx=50, pady=0)

#     #Creamos la matriz que lo parta en cuatro filas para añadir luego mas subframes
# frame_DLV_data.grid_rowconfigure(0, weight=1)
# frame_DLV_data.grid_rowconfigure(1, weight=1)
# frame_DLV_data.grid_rowconfigure(2, weight=1)
# frame_DLV_data.grid_rowconfigure(3, weight=1)

#         #Añadimos el subframe de la interconexion el primero y el resto
# frame_DLV_inter = tk.Frame(frame_DLV_data, background=blanco_roto)
# frame_DLV_inter.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

#         #Configuracion LV
# frame_DLV_Config = tk.Frame(frame_DLV_data, background=blanco_roto)
# frame_DLV_Config.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)

#         #Posicion de cajas, nº de inversores y tipo de cable
# frame_DFV_caj_cable = tk.Frame(frame_DLV_data, background=blanco_roto)
# frame_DFV_caj_cable.grid(row=2, column=0, sticky='nsew', padx=0, pady=0)

#         #Para boton de simulacion
# frame_DLV_data_exe = tk.Frame(frame_DLV_data, background=blanco_roto)
# frame_DLV_data_exe.grid(row=3, column=0, sticky='nsew', padx=0, pady=0)

# Creamos el frame para las entradas extras de Inv de String y DCBoxes
frame_DLV_extra = tk.Frame(frame_LV_container, background=blanco_roto)
frame_DLV_extra.grid(row=0, column=1, sticky='nsew', padx=25, pady=0)

# Creamos el frame para el boton de simulacion
frame_DLV_sim = tk.Frame(frame_LV_container, background=blanco_roto)
frame_DLV_sim.grid(row=0, column=2, sticky='nsew', padx=25, pady=0)

# Creamos subframes para dibujo y lectura dependiendo de si es dcbox o inv de strings
frame_DLV_CAD = tk.Frame(frame_LV_container, background=blanco_roto)
frame_DLV_CAD.grid(row=1, column=1, sticky='nsew', padx=25, pady=20)

frame_DCB_buttons = tk.Frame(frame_DLV_CAD, background=blanco_roto)
frame_DCB_buttons.grid(row=0, column=0, columnspan=3, sticky='nsew')

frame_IS_buttons = tk.Frame(frame_DLV_CAD, background=blanco_roto)
frame_IS_buttons.grid(row=0, column=0, columnspan=3, sticky='nsew')
frame_DCB_buttons.grid_remove()
frame_IS_buttons.grid_remove()



#------Frames Cable Routing
frame_routing_container= tk.Frame(Cable_routing_design, background=blanco_roto)
frame_routing_container.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

# Configurar la cuadrícula para partir el frame_DFV_container en tres verticales, uno para MV, otro para subarray y otro para array
frame_routing_container.grid_rowconfigure(0, weight=1) 
frame_routing_container.grid_columnconfigure(0, weight=1)  
frame_routing_container.grid_columnconfigure(1, weight=1)  
frame_routing_container.grid_columnconfigure(2, weight=1)  


# Creamos el frame para incluir los procesos en los tres campos
frame_MV_routing = tk.Frame(frame_routing_container, background=blanco_roto)
frame_MV_routing.grid(row=0, column=0, sticky='nsew', padx=50, pady=0)

frame_Subarray_routing = tk.Frame(frame_routing_container, background=blanco_roto)
frame_Subarray_routing.grid(row=0, column=1, sticky='nsew', padx=50, pady=0)

frame_Array_routing = tk.Frame(frame_routing_container, background=blanco_roto)
frame_Array_routing.grid(row=0, column=2, sticky='nsew', padx=50, pady=0)











#3.1-------------- PESTAÑA MEDIA TENSION


#-------Potencia de los bloques
entradas_potencia_bloques = []  # Lista de tuplas: (Entry, StringVar)

def listar_entradas_potencia(valores_potencia_bloques):
    global entradas_potencia_bloques
    entradas_potencia_bloques = []

    mitad = (n_bloques - bloque_inicial + 2) // 2

    for i in range(bloque_inicial, n_bloques + 1):
        idx = i - bloque_inicial
        valor_p = tk.StringVar()

        valor = valores_potencia_bloques[i]
        valor_str = str(valor) if isinstance(valor, (int, float)) else ""
        valor_p.set(valor_str)

        if idx < mitad:
            col_etiqueta = 0
            col_entry = 1
            row = idx
        else:
            col_etiqueta = 2
            col_entry = 3
            row = idx - mitad

        etiqueta_p = ttk.Label(scrollable_frame_potencias, text=f"BL.{i}")
        etiqueta_p.grid(row=row, column=col_etiqueta, padx=5, pady=2, sticky="w")

        entry_p = ttk.Entry(scrollable_frame_potencias, textvariable=valor_p, width=10)
        entry_p.grid(row=row, column=col_entry, padx=5, pady=2)

        entradas_potencia_bloques.append((entry_p, valor_p))  # <- se guarda también el StringVar

    canvas_potencias.update_idletasks()




# Canvas con scroll
canvas_potencias = tk.Canvas(frame_MV_power, height=400)
scrollbar_potencia = ttk.Scrollbar(frame_MV_power, orient="vertical", command=canvas_potencias.yview)
scrollable_frame_potencias = ttk.Frame(canvas_potencias)

# Actualizar región del scroll
scrollable_frame_potencias.bind("<Configure>",lambda e: canvas_potencias.configure(scrollregion=canvas_potencias.bbox("all")))

canvas_frame_potencias = canvas_potencias.create_window((0, 0), window=scrollable_frame_potencias, anchor="nw")
canvas_potencias.configure(yscrollcommand=scrollbar_potencia.set)

canvas_potencias.grid(row=0, column=0, columnspan=3, sticky="nsew")
scrollbar_potencia.grid(row=0, column=3, sticky="ns")

frame_MV_power.grid_rowconfigure(0, weight=1)
frame_MV_power.grid_columnconfigure(0, weight=1)


# Entrada para valor común
valor_comun_potencia = tk.StringVar()

entry_valor_comun = ttk.Entry(frame_MV_power, textvariable=valor_comun_potencia, width=10)
entry_valor_comun.grid(row=1, column=0, pady=(20, 5), padx=5, sticky='w')

def aplicar_valor_comun():
    try:
        valor = int(valor_comun_potencia.get())
        for entry, var in entradas_potencia_bloques:
            var.set(str(valor))
    except ValueError:
        print("Introduce un valor numérico válido.")

boton_aplicar_valor = ttk.Button(frame_MV_power, text="Set All", command=aplicar_valor_comun)
boton_aplicar_valor.grid(row=1, column=0, pady=(20, 5), padx=(100, 5), sticky='w')



def leer_potencia_bloques():
    global potencia_bloques
    potencia_bloques = [[] for _ in range(n_bloques + 1)]

    for i in range(bloque_inicial, n_bloques + 1):
        r = i - bloque_inicial
        _, var = entradas_potencia_bloques[r]
        try:
            potencia_bloques[i] = int(var.get())
        except ValueError:
            potencia_bloques[i] = 0  # o None si prefieres

    guardar_variables([potencia_bloques], ['potencia_bloques'])



boton_leer_potencias = tk.Button(frame_MV_power, text="Read Values", command=leer_potencia_bloques, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_leer_potencias.grid(row=2, column=0, pady=50, padx=5)




#----Definir lineas MV

    #Crear entradas
entradas_lineas_MV = []
fila_actual_MV = 1

def agregar_linea_MV(frame):
    global entradas_lineas_MV, contador_tramos_MV, fila_actual_MV

    fila_frame = ttk.Frame(frame)
    fila_frame.grid(row=fila_actual_MV, column=0, columnspan=3, sticky="w", pady=5)

    etiqueta = ttk.Label(fila_frame, text=f"Line {len(entradas_lineas_MV) + 1}")
    etiqueta.grid(row=0, column=0, padx=5)

    entradas_lineas_MV.append([etiqueta, []])
    contador_tramos_MV = 0
    fila_actual_MV += 1


def agregar_tramo_linea_MV(frame):
    global entradas_lineas_MV, contador_tramos_MV, fila_actual_MV

    if not entradas_lineas_MV:
        return  # Nada que anidar

    contador_tramos_MV += 1

    sub_frame = ttk.Frame(frame)
    sub_frame.grid(row=fila_actual_MV, column=0, columnspan=3, sticky="w", padx=20)

    sub_label = ttk.Label(sub_frame, text=f"L {len(entradas_lineas_MV)}.{contador_tramos_MV}")
    sub_label.grid(row=0, column=0, padx=5, pady=5)

    entry1 = ttk.Entry(sub_frame, width=10)
    entry1.grid(row=0, column=1, padx=5)

    entry2 = ttk.Entry(sub_frame, width=10)
    entry2.grid(row=0, column=2, padx=5)

    entradas_lineas_MV[-1][1].append([entry1, entry2])
    fila_actual_MV += 1


def eliminar_ultimo_elemento_MV():
    global entradas_lineas_MV, contador_tramos_MV, fila_actual_MV

    if not entradas_lineas_MV:
        return

    etiqueta, subfilas = entradas_lineas_MV[-1]

    if subfilas:
        entrada_1, entrada_2 = subfilas.pop()
        entrada_1.master.destroy()  # destruye sub_frame con ambos Entry
        contador_tramos_MV = max(0, contador_tramos_MV - 1)
        fila_actual_MV = max(1, fila_actual_MV - 1)
    else:
        etiqueta.master.destroy()  # destruye fila_frame
        entradas_lineas_MV.pop()
        fila_actual_MV = max(1, fila_actual_MV - 1)




# Canvas con scroll
canvas_lineas_MV = tk.Canvas(frame_MV_lines, height=400)
scrollbar_lineas_MV = ttk.Scrollbar(frame_MV_lines, orient="vertical", command=canvas_lineas_MV.yview)
scrollable_frame_lineas_MV = ttk.Frame(canvas_lineas_MV)

# Actualizar región del scroll
scrollable_frame_lineas_MV.bind("<Configure>",lambda e: canvas_lineas_MV.configure(scrollregion=canvas_lineas_MV.bbox("all")))

canvas_frame_lineas_MV = canvas_lineas_MV.create_window((0, 0), window=scrollable_frame_lineas_MV, anchor="nw")
canvas_lineas_MV.configure(yscrollcommand=scrollbar_lineas_MV.set)

canvas_lineas_MV.grid(row=0, column=0, columnspan=3, sticky="nsew")
scrollbar_lineas_MV.grid(row=0, column=3, sticky="ns")

# Botones
ttk.Button(frame_MV_lines, text="Add MV Line", command=lambda: agregar_linea_MV(scrollable_frame_lineas_MV)).grid(row=1, column=0, pady=10, padx=5)
ttk.Button(frame_MV_lines, text="Add Connection", command=lambda: agregar_tramo_linea_MV(scrollable_frame_lineas_MV)).grid(row=1, column=1, pady=10, padx=5)
ttk.Button(frame_MV_lines, text="Remove Last", command=eliminar_ultimo_elemento_MV).grid(row=1, column=2, pady=10, padx=5)


#Cargar entradas desde proyecto guardado (se lee al cargar el proyecto)
def cargar_entradas_lineas_MV():
    global entradas_lineas_MV, fila_actual_MV
    fila_actual_MV = 1
    entradas_lineas_MV = []

    for item in lineas_MV:
        if item == [0]:
            continue

        etiqueta_texto = item[0]
        tramos = item[1:]

        # Añadir línea visual
        agregar_linea_MV(scrollable_frame_lineas_MV)
        entradas_lineas_MV[-1][0].config(text=etiqueta_texto)

        # Añadir cada tramo visualmente
        for tramo in tramos:
            if len(tramo) < 2:
                continue
            val1, val2 = tramo[:2]
            agregar_tramo_linea_MV(scrollable_frame_lineas_MV)
            entry1, entry2 = entradas_lineas_MV[-1][1][-1]
            entry1.insert(0, str(val1))
            entry2.insert(0, str(val2))


#Leer entradas y pasar valores a polilinea de diseño
    
def leer_valores_MV():
    global lineas_MV, pol_cable_MV
    
    lineas_MV = [[0]]
    pol_cable_MV = [[0]]
    
    c_l=0
    for etiqueta, subfilas in entradas_lineas_MV:
        texto = etiqueta.cget("text")
        valores_subfilas = []
        
        pol_cable_MV.append([])        
        c_l=c_l+1
        pot_acum = 0
        pol_cable_MV[c_l]=[0]
        for entrada_1, entrada_2 in subfilas:
            bloque_inicio = int(entrada_1.get())
            
            pot_acum = pot_acum + int(potencia_bloques[bloque_inicio])
            
            valor_entrada_2 = entrada_2.get() #puede ser que vaya al switching room como SRx, por lo que hay que tratarlo diferente
            if valor_entrada_2.startswith("SR"):
                
                valores_subfilas.append([bloque_inicio, valor_entrada_2, pot_acum])
                
                pol_cable_MV[c_l].append([coord_PCS_MV_inputs[bloque_inicio],np.array(coord_MV_Switching_Room[int(valor_entrada_2[2:])])])
                
            else:
                bloque_destino = int(valor_entrada_2)
            
                valores_subfilas.append([bloque_inicio, bloque_destino, pot_acum])
                
                pol_cable_MV[c_l].append([coord_PCS_MV_inputs[bloque_inicio],coord_PCS_MV_inputs[bloque_destino]])
        
        lineas_MV.append([texto, *valores_subfilas])
        
        
    guardar_variables([lineas_MV, pol_cable_MV], ['lineas_MV', 'pol_cable_MV'])


boton_leer_MV = tk.Button(frame_MV_lines, text="Read Values", command=leer_valores_MV, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_leer_MV.grid(row=2, column=0, pady=50, padx=5)







#3.2----------PESTAÑA CONFIGURACION LV


#CREAR COMBOBOXES
def comboboxes_entradas_DFV(valores_comboboxes_DFV,valores_entradas_DFV, reiniciar_inv):
    global entrada_DCBoxes_o_Inv_String, entrada_Interconexionado, entrada_Polo_cercano, entrada_Posicion_optima_caja, entrada_n_inv, entrada_dif_str_inv, dos_inv
    
    #-------ENTRADAS COMUNES CONFIG LV
    #ENTRADAS INTERCONEXIONADO DE MODULOS
  
    #Combobox para el tipo de interconexion de modulos
    Interconnection_options = ["Daisy chain", "Leapfrog"]
    entrada_Interconexionado = tk.StringVar(value = valores_comboboxes_DFV[0])
    
    etiqueta_interconexion = tk.Label(frame_DLV_data, text='PV Modules Interconnection', fg=rojo_GRS, font=('Montserrat', 10, 'bold'))
    etiqueta_interconexion.grid(row=0, column=0, pady=(25,0))
    combobox_inter=ttk.Combobox(frame_DLV_data, textvariable=entrada_Interconexionado, values=Interconnection_options)
    combobox_inter.grid(row=1, column=0, pady=(5,20))
    
    
    #Combobox para el polo mas cercano a cajas o inversores
    closer_pole_option = ["Positive", "Negative"]
    entrada_Polo_cercano = tk.StringVar(value = valores_comboboxes_DFV[1])
    
    etiqueta_polo = tk.Label(frame_DLV_data, fg=rojo_GRS, text='Closer Pole', font=('Montserrat', 10, 'bold'))
    etiqueta_polo.grid(row=2, column=0)
    combobox_polo = ttk.Combobox(frame_DLV_data, textvariable=entrada_Polo_cercano, values=closer_pole_option)
    combobox_polo.grid(row=3, column=0, pady=(5,0))
            
    
    #DISEÑO CAJAS O INV
    
    #Combobox para las opciones LV
    opciones_LV = ["DC Boxes", "String Inverters"]
    entrada_DCBoxes_o_Inv_String = tk.StringVar(value = valores_comboboxes_DFV[2])
    
    etiqueta_DCBIS = tk.Label(frame_DLV_data, text='LV Configuration', fg=rojo_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_DCBIS.grid(row=4, column=0, columnspan=1)
    combobox_DCBIS=ttk.Combobox(frame_DLV_data, textvariable=entrada_DCBoxes_o_Inv_String, values=opciones_LV)
    combobox_DCBIS.grid(row=5, column=0, columnspan=1, pady=(5,20))
    combobox_DCBIS.bind("<<ComboboxSelected>>", lambda e: on_lv_config_change())
    
    #ENTRADAS POSICION CAJAS O INV Y Nº INV/PCS
    
    # Hacemos Combobox para definir la posicion optima de la caja
    Posicion_optima_caja_options = ["Edge", "Center"]
    entrada_Posicion_optima_caja = tk.StringVar(value = valores_comboboxes_DFV[3])
    
    tk.Label(frame_DLV_data, text='DCB/SI Optimal location', fg=rojo_GRS, font=('Montserrat', 10, 'bold')).grid(row=6, column=0)
    ttk.Combobox(frame_DLV_data, textvariable=entrada_Posicion_optima_caja, values=Posicion_optima_caja_options).grid(row=7, column=0, pady=(5,10))
    
    #Entradas y Combobox para el nº de inversores o cuadros, si es 2 se activa una entrada manual para introducir el maximo desequilibrio de strings entre ellos y un tick de si se reinicia la cuenta por board o no
    etiqueta_dif_str_inv = tk.Label(frame_DLV_data, text="Max. Str. Unbalance", fg=rojo_GRS, bg=blanco_roto, font=('Montserrat', 10, 'bold'))
    etiqueta_dif_str_inv.grid(row=9, column=0)
    valor_dif_str_inv = tk.StringVar()
    valor_dif_str_inv.set(valores_entradas_DFV[0])
    entrada_dif_str_inv = tk.Entry(frame_DLV_data, width=5)
    entrada_dif_str_inv.grid(row=9, column=1)
    
    def activar_equilibrio_strings(entrada):
        global dos_inv
        if entrada == "2":
            entrada_dif_str_inv.config(state='normal')
            dos_inv = True
        else:
            entrada_dif_str_inv.config(state='disabled')
            dos_inv = False
            
    n_inv_options = ["1", "2"]
    entrada_n_inv = tk.StringVar(value = valores_comboboxes_DFV[5])
    
    etiqueta_n_inv = tk.Label(frame_DLV_data, text='No. inv.', fg=rojo_GRS, font=('Montserrat', 10, 'bold'))
    etiqueta_n_inv.grid(row=8, column=0)
    combobox_n_inv = ttk.Combobox(frame_DLV_data, textvariable=entrada_n_inv, values=n_inv_options, width=5)
    combobox_n_inv.grid(row=8, column=1)
    combobox_n_inv.bind("<<ComboboxSelected>>", lambda event: activar_equilibrio_strings(entrada_n_inv.get()))
    
    
    entrada_reiniciar_inv = tk.BooleanVar(value=reiniciar_inv)
    def activar_reinicio_inv_en_board():
        global reiniciar_inv        
        if entrada_reiniciar_inv.get():
            reiniciar_inv=True
        else:
            reiniciar_inv=False
            
    etiqueta_reiniciar_inv = tk.Label(frame_DLV_data, text='Restart inv.', fg=rojo_GRS, font=('Montserrat', 10, 'bold'))
    etiqueta_reiniciar_inv.grid(row=10, column=0)
    check_reiniciar_inv = ttk.Checkbutton(frame_DLV_data, variable=entrada_reiniciar_inv, command=activar_reinicio_inv_en_board)
    check_reiniciar_inv.grid(row=10, column=1, padx=5, pady=5, sticky='w')

    
    
    #--------ENTRADAS EXTRA PARA DC BOXES-----------
    def mostrar_configuracion_dc_boxes():
        global entrada_String_o_Bus, valor_masc, valor_misc
        
        for widget in frame_DLV_extra.winfo_children():
            widget.destroy()
        #Entradas manuales para el maximo y minimo numero de strings por caja
        etiqueta_n_strings_caja = tk.Label(frame_DLV_extra, text="Number of strings per DC Box", fg=rojo_GRS, bg=blanco_roto, font=('Montserrat', 10, 'bold'))
        etiqueta_n_strings_caja.grid(row=0, column=0, columnspan=1)
        
        etiqueta_masc = tk.Label(frame_DLV_extra, text="Max", fg=rojo_GRS, bg=blanco_roto, font=('Montserrat', 10, 'bold'))
        etiqueta_masc.grid(row=1, column=0)
        valor_masc = tk.StringVar()
        valor_masc.set(valores_entradas_DFV[1])
        entrada_masc = tk.Entry(frame_DLV_extra, textvariable=valor_masc, width=10)
        entrada_masc.grid(row=2, column=0, pady=(5,20))
        
        etiqueta_misc = tk.Label(frame_DLV_extra, text="Min", fg=rojo_GRS, bg=blanco_roto, font=('Montserrat', 10, 'bold'))
        etiqueta_misc.grid(row=1, column=1)
        valor_misc = tk.StringVar()
        valor_misc.set(valores_entradas_DFV[2])
        entrada_misc = tk.Entry(frame_DLV_extra, textvariable=valor_misc, width=10)
        entrada_misc.grid(row=2, column=1, pady=(5,20))
    
        #Combobox para el tipo de configuracion LVDC
        LVDC_cable_option = ["String Cable", "DC Bus", "Both types", "Mixed"]
        entrada_String_o_Bus = tk.StringVar(value = valores_comboboxes_DFV[4])
        
        etiqueta_main_cable_dc = tk.Label(frame_DLV_extra, text='DC cable configuration', fg=rojo_GRS, font=('Montserrat', 10, 'bold'))
        etiqueta_main_cable_dc.grid(row=3, column=0)
        combobox_main_cable_dc = ttk.Combobox(frame_DLV_extra, textvariable=entrada_String_o_Bus, values=LVDC_cable_option)
        combobox_main_cable_dc.grid(row=4, column=0, pady=(5,20))
    

    #--------ENTRADAS EXTRA PARA INV STRING-----------
    
    def mostrar_configuraciones_string_inverters(config_inicial=None):
        global valor_dist_max_inter_bandas, valor_lim_str_interc
        
        for widget in frame_DLV_extra.winfo_children():
            widget.destroy()
        
        # Frame para parámetros superiores
        frame_parametros = ttk.Frame(frame_DLV_extra)
        frame_parametros.grid(row=0, column=0, sticky='ew', padx=10, pady=(5, 0))
            
        #Entrada de distancia y n maxima de intercambio de strings entre bandas
        etiqueta_dist_max_inter_bandas = tk.Label(frame_parametros, fg=rojo_GRS, bg=blanco_roto, text="Max distance inter-bands", font=('Montserrat', 10, 'bold'))
        etiqueta_dist_max_inter_bandas.grid(row=0, column=0, sticky='w')
        valor_dist_max_inter_bandas = tk.StringVar()
        valor_dist_max_inter_bandas.set(dist_max_inter_bandas)
        entrada_dist_max_inter_bandas = ttk.Entry(frame_parametros, textvariable=valor_dist_max_inter_bandas, width=5)   #Valor maximo de separacion entre bandas para poder intercambiar strings, si lo damos muy alto el problema es que dos bandas que queriamos que fuesen independientes se puedan asociar, cargando mucho los calculos si hay bloques de bandas
        entrada_dist_max_inter_bandas.grid(row=0, column=1, padx=(5, 20))
        
        
        etiqueta_lim_str_interc = tk.Label(frame_parametros, fg=rojo_GRS, bg=blanco_roto, text="Max inter-strings", font=('Montserrat', 10, 'bold'))
        etiqueta_lim_str_interc.grid(row=0, column=2, sticky='w')
        valor_lim_str_interc = tk.StringVar()
        valor_lim_str_interc.set(lim_str_interc)
        entrada_lim_str_interc = ttk.Entry(frame_parametros, textvariable=valor_lim_str_interc, width=5)  #parametro de diseño de maximo de strings que se pueden pasar de una banda a otra, se puede maximizar considerando el nº de strings de los inversores max(conf_inversores[0]) pero se cargan mucho los calculos
        entrada_lim_str_interc.grid(row=0, column=3, padx=(5, 0))
        
        
        # ===== Container con Canvas + Scrollbars =====
        container = ttk.Frame(frame_DLV_extra)
        container.grid(row=1, column=0, sticky='nsew', pady=(5, 20))
        
        # Asegurar que el contenedor se expanda
        frame_DLV_extra.grid_rowconfigure(2, weight=1)
        frame_DLV_extra.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Canvas
        canvas = tk.Canvas(container)
        canvas.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        
        h_scrollbar = ttk.Scrollbar(container, orient='horizontal', command=canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        # Content frame dentro del canvas
        content_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor='nw')

                
        # ===== Cabeceras fijas =====
        ttk.Label(content_frame, text="Bloque", style='Header.TLabel').grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        bloques_labels = []
        for i in range(bloque_inicial, n_bloques + 1):
            lbl = ttk.Label(content_frame, text=f"{i}", background='white', anchor='center')
            lbl.grid(row=i - bloque_inicial + 1, column=0, sticky='nsew', padx=2, pady=2)
            bloques_labels.append(lbl)
        
        # ===== Estructuras para almacenar inputs =====
        columnas_headers = []
        entradas_por_bloque = []
        
        def agregar_configuracion():
            col = len(columnas_headers) + 1
            header_var = tk.StringVar()
            header_entry = ttk.Entry(content_frame, textvariable=header_var, width=10)
            header_entry.grid(row=0, column=col, padx=5, pady=5)
            columnas_headers.append(header_var)
        
            col_entradas = []
            for row in range(1, n_bloques - bloque_inicial + 2):
                var = tk.StringVar()
                entry = ttk.Entry(content_frame, textvariable=var, width=10)
                entry.grid(row=row, column=col, padx=5, pady=2)
                col_entradas.append(var)
            entradas_por_bloque.append(col_entradas)
        
        def leer_configuraciones():
            global conf_inversores
        
            # Convertir headers a int, vacíos como 0
            headers = []
            for header in columnas_headers:
                valor = header.get().strip()
                try:
                    valor_num = int(valor) if valor else 0
                except ValueError:
                    valor_num = 0
                headers.append(valor_num)
        
            filas = []
            num_bloques = n_bloques - bloque_inicial + 1
        
            for i in range(num_bloques):
                fila = []
                for col in entradas_por_bloque:
                    valor = col[i].get().strip()
                    try:
                        valor_numerico = int(valor) if valor else 0
                    except ValueError:
                        valor_numerico = 0
                    fila.append(valor_numerico)
                filas.append(fila)
        
            conf_inversores_list = [headers] + filas
            conf_inversores = np.array(conf_inversores_list, dtype=int)
        
            guardar_variables([conf_inversores], ['conf_inversores'])
        


    
        # ===== Botones de acción =====
        botones_frame = ttk.Frame(frame_DLV_extra)
        botones_frame.grid(row=2, column=0, pady=(10, 10))
        
        boton_agregar_columna = ttk.Button(botones_frame, text="Add Strings/Inverter", command=agregar_configuracion)
        boton_agregar_columna.grid(row=0, column=0, padx=10)
        
        boton_leer_valores = ttk.Button(botones_frame, text="Read Configuration", command=leer_configuraciones)
        boton_leer_valores.grid(row=0, column=1, padx=10)
    
        # Estilo personalizado para cabeceras si lo deseas
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Segoe UI', 10, 'bold'), background='lightgray')
        
        
        # Si hay configuración inicial (cargar proyecto), reconstruir la interfaz
        if config_inicial is not None and len(config_inicial) > 0:
            headers_guardados = config_inicial[0]
            datos_guardados = config_inicial[1:]
        
            for header in headers_guardados:
                agregar_configuracion()
                columnas_headers[-1].set("" if int(header) == 0 else str(header))
        
            for fila_idx, fila_datos in enumerate(datos_guardados):
                for col_idx, valor in enumerate(fila_datos):
                    if col_idx < len(entradas_por_bloque):
                        valor_str = str(valor).strip()
                        valor_int = int(valor_str) if valor_str else 0
                        entradas_por_bloque[col_idx][fila_idx].set("" if valor_int == 0 else str(valor_int))

  
    
    # === Control para disparar el popup ===
    def on_lv_config_change(*args):
        seleccion = entrada_DCBoxes_o_Inv_String.get()
        
        # Mostrar inputs extra correspondientes
        if seleccion == "String Inverters":
            mostrar_configuraciones_string_inverters(config_inicial=conf_inversores)
            frame_DCB_buttons.grid_remove()
            frame_IS_buttons.grid()
        elif seleccion == "DC Boxes":
            mostrar_configuracion_dc_boxes()
            frame_IS_buttons.grid_remove()
            frame_DCB_buttons.grid()
        else:
            for widget in frame_DLV_extra.winfo_children():
                widget.destroy()
            frame_DCB_buttons.grid_remove()
            frame_IS_buttons.grid_remove()

    on_lv_config_change()


#Ejecutamos la funcion de comboboxes con valores iniciales desiertos
valores_iniciales_comboboxes_DFV=[[],[],[],[],[],[]]
valores_iniciales_entradas_DFV = [[],[],[]]
reiniciar_inv = False #inicializamos a la espera del checkbutton
comboboxes_entradas_DFV(valores_iniciales_comboboxes_DFV, valores_iniciales_entradas_DFV, reiniciar_inv)
dos_inv = False #inicializamos a la espera de la combobox
conf_inversores=None  #inicializamos a la espera de la combobox






#---------SIMULACION
#Definimos funciones de simulacion, hay que definir la de los IDs porque se necesita la variable de equivalencia ibfs si luego se quiere dibujar, lo hacemos como funcion porque se vuelve a usar para actualizar valores si se lee desde el CAD
def ID_strings_y_DCBoxes():
    global strings_ID , DCBoxes_ID, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs, filas_con_cable_string, max_bus, tipos_cajas_por_entradas, TOT_n_cajas_str, TOT_n_cajas_bus, TOT_n_cajas_mix, TOT_n_cajas
    
    #Dependiendo de la opcion de LVDC se va por una nomenclatura u otra   
    if String_o_Bus == 'String Cable':   
        strings_ID , DCBoxes_ID, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs = Algoritmo_IXPHOS_2_Config_electrica.ID_strings_y_cajas_para_Cable_de_String(strings_fisicos,filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_c,max_c_block,max_b, max_spf, max_f_str_b,masc, dist_ext_opuesto_str, dos_inv)  
        filas_con_cable_string=np.ones((n_bloques+1,max_b,max_f_str_b),dtype=bool) #necesario definirlo aqui aunque vaya a ser true siempre para poder usar despues la misma funcion de medicion y perdidas en las configuraciones mixtas
            
    elif String_o_Bus == 'DC Bus':
        strings_ID , DCBoxes_ID, max_bus, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs = Algoritmo_IXPHOS_2_Config_electrica.ID_strings_y_cajas_para_DC_Bus(strings_fisicos,filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_c,max_c_block,max_b, max_spf, max_f_str_b,masc, dist_ext_opuesto_str, dos_inv)
        filas_con_cable_string=np.zeros((n_bloques+1,max_b,max_f_str_b),dtype=bool) #necesario definirlo aqui aunque vaya a ser np.nan para usar la misma funcion de harness en los tres casos
        
        guardar_variables([max_bus],['max_bus'])
        
    elif String_o_Bus == 'Both types':
        lim_cable_string=2      
        strings_ID , DCBoxes_ID, max_bus, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs, filas_con_cable_string = Algoritmo_IXPHOS_2_Config_electrica.ID_strings_y_cajas_para_config_mixtas(strings_fisicos,filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_c,max_c_block,max_b,max_spf, max_f_str_b,masc, dist_ext_opuesto_str, String_o_Bus,lim_cable_string, dos_inv)

        guardar_variables([max_bus],['max_bus'])
        
    elif String_o_Bus == 'Mixed':
        lim_cable_string=2
        strings_ID , DCBoxes_ID, max_bus, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs, filas_con_cable_string = Algoritmo_IXPHOS_2_Config_electrica.ID_strings_y_cajas_para_config_mixtas(strings_fisicos,filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_c,max_c_block,max_b,max_spf, max_f_str_b,masc, dist_ext_opuesto_str, String_o_Bus,lim_cable_string, dos_inv)
        
        guardar_variables([max_bus],['max_bus'])
    
    #Sacamos los tipos de DC_Boxes, se usa la misma funcion en todos los casos
    DCBoxes_ID, tipos_cajas_por_entradas, TOT_n_cajas_str, TOT_n_cajas_bus, TOT_n_cajas_mix, TOT_n_cajas = Algoritmo_IXPHOS_2_Config_electrica.calculo_DC_Boxes(bloque_inicial, n_bloques, max_b, max_c, max_f_str_b, max_c_block, masc, filas_en_cajas, String_o_Bus, filas_con_cable_string, equi_ibc, DCBoxes_ID, cajas_fisicas)
    
    #Guardar variables en el dicionario
    guardar_variables([strings_ID , DCBoxes_ID, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs, filas_con_cable_string, dos_inv, tipos_cajas_por_entradas, TOT_n_cajas_str, TOT_n_cajas_bus, TOT_n_cajas_mix, TOT_n_cajas],['strings_ID' , 'DCBoxes_ID', 'equi_ibfs', 'equi_ibc', 'equi_reverse_ibc','equi_reverse_ibfs','filas_con_cable_string', 'dos_inv','tipos_cajas_por_entradas', 'TOT_n_cajas_str', 'TOT_n_cajas_bus', 'TOT_n_cajas_mix', 'TOT_n_cajas'])


def simular_configuracion_LV():
    def proceso_simular_configuracion_LV():
        #Leer entradas previas de las comboboxes
        global DCBoxes_o_Inv_String, String_o_Bus, Interconexionado, Polo_cercano, Posicion_optima_caja, n_inv, strings_fisicos, max_f_str_b, dos_inv_por_bloque
        global inv_string, max_str_pinv, max_inv_block
        
        global error_de_simulacion
        error_de_simulacion = 'Sin Error'
        
        try:
            DCBoxes_o_Inv_String = entrada_DCBoxes_o_Inv_String.get()
            Interconexionado = entrada_Interconexionado.get()
            Polo_cercano = entrada_Polo_cercano.get()
            Posicion_optima_caja = entrada_Posicion_optima_caja.get()
            n_inv = entrada_n_inv.get()
            
            if DCBoxes_o_Inv_String == 'DC Boxes':
                global filas_en_cajas, cajas_fisicas, max_c, max_c_block, masc, misc, lim_str_dif
                print('entra')
                #Procesar en modelo las entradas necesarias
                String_o_Bus = entrada_String_o_Bus.get()
                masc = int(valor_masc.get())
                misc = int(valor_misc.get())
                
                #Hace falta inicializar las de inv de string asi para llenar los parametros en las funciones de medicion aunque no se usen                
                inv_string=None
                max_str_pinv=None
                max_inv_block=None
                guardar_variables([inv_string, max_str_pinv, max_inv_block],['inv_string', 'max_str_pinv', 'max_inv_block'])
                
                #Sacamos las filas y cajas, no se representan todavia porque se necesita equi_ibfs que sale de las funciones conociendo la solucion del cable de subarray
                filas_en_cajas, max_c, max_c_block  = Algoritmo_IXPHOS_2_Config_electrica.filas_config_cajas_sin_mezclar_filas(strings_fisicos, bloque_inicial, n_bloques, max_b, max_f_str_b, misc, masc)
                cajas_fisicas = Algoritmo_IXPHOS_2_Config_electrica.cajas_desde_filas_asociadas(strings_fisicos, filas_en_cajas, orientacion, coord_PCS_DC_inputs, sep_caja_tracker, Posicion_optima_caja, bloque_inicial,n_bloques,max_b,max_f_str_b, max_c)
                
                #Evaluamos si hay uno o dos inversores por bloque y ajustamos variables dependientes
                if n_inv == "2":
                    dos_inv_por_bloque=True
                    lim_str_dif=int(entrada_dif_str_inv.get())
                    cajas_fisicas = Algoritmo_IXPHOS_2_Config_electrica.repartir_cajas_en_dos_inversores(cajas_fisicas, coord_PCS_DC_inputs, lim_str_dif, bloque_inicial,n_bloques, max_b, max_c)
                    
                    guardar_variables([lim_str_dif],['lim_str_dif'])
                else:
                    dos_inv_por_bloque=False
                    
                ID_strings_y_DCBoxes()
                
                #Guardamos variables en el diccionario
                guardar_variables([dos_inv_por_bloque, filas_en_cajas, max_c, max_c_block, cajas_fisicas, masc, misc],['dos_inv_por_bloque', 'filas_en_cajas', 'max_c', 'max_c_block', 'cajas_fisicas', 'masc', 'misc'])
        

            elif DCBoxes_o_Inv_String == 'String Inverters':
                global dist_max_inter_bandas, lim_str_interc, combinacion_optima, ganancias_perdidas_optima, matriz_intercambios_optima, puentes_fisicos, almacen_strings
                global max_inv, equi_ibv_to_fs, posiciones_inv
                global strings_ID, String_Inverters_ID, equi_ibv, equi_reverse_ibv, ori_str_ID, filas_en_inversores
                global inv_como_cajas_fisicas, filas_en_inv_como_filas_en_cajas, filas_con_cable_string
                
                # PARÁMETROS DE ENTRADA
                String_o_Bus = 'String Cable'
                criterio_ceder_strings = 'Rows'
                dist_max_inter_bandas = float(valor_dist_max_inter_bandas.get())
                lim_str_interc = int(valor_lim_str_interc.get())
                puntos_usados_global = [set() for _ in range(n_bloques+1)]
                filas_con_cable_string=np.ones((n_bloques+1,max_b,max_f_str_b),dtype=bool) #necesario definirlo aqui aunque vaya a ser true siempre para poder usar despues la misma funcion de medicion y perdidas en las configuraciones mixtas
                
                # 1 OBTENCIÓN DE COMBINACIÓN ÓPTIMA DE INVERSORES Y TRANSFERENCIAS
                salida_combinacion_inversores = (
                    Algoritmo_IXPHOS_2_Config_electrica.combinacion_inv_en_bandas_optima(
                        bloque_inicial, n_bloques, strings_fisicos, lim_str_interc,
                        conf_inversores, contorno_bandas, dist_max_inter_bandas, max_b, max_fr
                    )
                )
                if not salida_combinacion_inversores:
                    error_de_simulacion='Configuracion_fallida'
                    return
                else:
                    combinacion_optima, ganancias_perdidas_optima, matriz_intercambios_optima, puentes_fisicos = salida_combinacion_inversores
                    
                # 2 GENERACIÓN DE ALMACÉN DE STRINGS INTERCAMBIADOS (USANDO PROXIMIDAD A PUENTE)
                almacen_strings = Algoritmo_IXPHOS_2_Config_electrica.intercambio_strings_por_proximidad_a_puente(
                    bloque_inicial, n_bloques, max_b, max_f_str_b, max_tpf, strings_fisicos,
                    matriz_intercambios_optima, puentes_fisicos, criterio_ceder_strings,
                    puntos_usados_global, orientacion
                )
                
                # 3 ASIGNACIÓN DE STRINGS A INVERSORES
                inv_string, max_inv, max_inv_block, max_str_pinv, equi_ibv_to_fs = (
                    Algoritmo_IXPHOS_2_Config_electrica.asignar_strings_a_inversores(
                        bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, strings_fisicos,
                        conf_inversores, combinacion_optima, almacen_strings,
                        ori_str_ID, orientacion, puntos_usados_global,
                        criterio_ceder_strings, puentes_fisicos
                    )
                )
                ori_str_ID =  Algoritmo_IXPHOS_2_Config_electrica.aplicar_flip_strings(
                    bloque_inicial, n_bloques, max_b, max_inv, max_str_pinv,
                    equi_ibv_to_fs, ori_str_ID, orientacion, strings_fisicos
                )

                # 4 POSICIONAMIENTO FÍSICO DE LOS INVERSORES
                inv_string[:, :, :, 0], comienzos_filas_strings = Algoritmo_IXPHOS_2_Config_electrica.posicion_inv_string(
                    inv_string, strings_fisicos, sep_caja_tracker, coord_PCS_DC_inputs, contorno_bandas,
                    Posicion_optima_caja, equi_ibv_to_fs, orientacion, almacen_strings
                )
                posiciones_inv=inv_string[:, :, :, 0]
                # 5 AJUSTE PARA DOBLE INVERSOR (si aplica)
                if n_inv == "2":
                    dos_inv_por_bloque = True
                    lim_str_dif = int(entrada_dif_str_inv.get())
                    inv_string = Algoritmo_IXPHOS_2_Config_electrica.repartir_inversores_en_dos_cuadros(
                        inv_string, coord_PCS_DC_inputs, lim_str_dif, bloque_inicial, n_bloques, max_b, max_inv, max_str_pinv
                    )
                    guardar_variables([lim_str_dif], ['lim_str_dif'])
                else:
                    dos_inv_por_bloque = False
                
                # 6 ASIGNACIÓN DE IDs DE STRINGS E INVERSORES
                strings_ID, String_Inverters_ID, equi_ibv, equi_reverse_ibv, inv_string, equi_ibv_to_fs = Algoritmo_IXPHOS_2_Config_electrica.ID_strings_e_inv_string(
                    bloque_inicial, n_bloques, max_b, max_inv, max_inv_block, max_str_pinv,
                    inv_string, dos_inv_por_bloque, equi_ibv_to_fs, strings_fisicos, dist_ext_opuesto_str, ori_str_ID, orientacion
                )
                
                # 7 CREACION DE INV FISICOS (EQUIVALENTE A CAJAS FISICAS) Y FILAS_EN_INVERSORES (EQUIVALENTE A FILAS EN CAJA PARA INV DE STRING DE BANDA UNICA, USADO PARA TIRAR POLILINEAS DE CABLE)
                inv_como_cajas_fisicas = Algoritmo_IXPHOS_2_Config_electrica.obtener_inv_fisicos(bloque_inicial, n_bloques, max_b, max_inv, inv_string)
                filas_en_inv_como_filas_en_cajas = Algoritmo_IXPHOS_2_Config_electrica.obtener_filas_en_inv_como_filas_en_cajas(bloque_inicial, n_bloques, max_b, max_f_str_b, strings_fisicos)                
                
                guardar_variables([dist_max_inter_bandas, lim_str_interc, combinacion_optima, ganancias_perdidas_optima, matriz_intercambios_optima, puentes_fisicos, almacen_strings], ['dist_max_inter_bandas', 'lim_str_interc', 'combinacion_optima', 'ganancias_perdidas_optima', 'matriz_intercambios_optima', 'puentes_fisicos', 'almacen_strings'])
                
                guardar_variables([inv_string, max_inv, max_inv_block, max_str_pinv, equi_ibv_to_fs, dos_inv_por_bloque, reiniciar_inv, posiciones_inv, strings_ID, String_Inverters_ID, equi_ibv, equi_reverse_ibv, inv_como_cajas_fisicas, filas_en_inv_como_filas_en_cajas], ['inv_string', 'max_inv', 'max_inv_block', 'max_str_pinv', 'equi_ibv_to_fs', 'dos_inv_por_bloque', 'reiniciar_inv', 'posiciones_inv', 'strings_ID', 'String_Inverters_ID', 'equi_ibv', 'equi_reverse_ibv', 'inv_como_cajas_fisicas', 'filas_en_inv_como_filas_en_cajas'])
                                                                                                                                     

            guardar_variables([Interconexionado,Polo_cercano,DCBoxes_o_Inv_String, String_o_Bus, Posicion_optima_caja, n_inv,filas_con_cable_string],['Interconexionado','Polo_cercano','DCBoxes_o_Inv_String', 'String_o_Bus', 'Posicion_optima_caja','n_inv','filas_con_cable_string'])
        
        except:
            
             error_de_simulacion = 'Error'
             traceback.print_exc()
             
    def cerrar_ventana_tras_simular_LV(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
            elif error_de_simulacion=='Configuracion_fallida':
                messagebox.showerror("Error", "The combination of inverters is not possible, please check number of inverters, inverters configuration and exchange parameters.")
                
            #Aprovechamos para incluir una entrada extra necesaria para inversores de string cuando se mida el cable
            if DCBoxes_o_Inv_String == 'String Inverters':
                listar_uni_o_multipolar(var_com_uni_o_multipolar)
                
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_4():
        proceso_simular_configuracion_LV()
        root.after(0, lambda: cerrar_ventana_tras_simular_LV(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_4) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
    
boton_LV = tk.Button(frame_DLV_sim, text="Simulate", command=simular_configuracion_LV, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_LV.grid(row=0, column=0, pady=20)

var_com_uni_o_multipolar = 'Single Core' #inicializamos esta variable fuera de las funciones para cuando se cargue por primera vez, sin interferir en las importadas






#-------DIBUJAR Y LEER CONFIGURACION DE CAJAS
#Dibujar envolventes asociando filas a cajas
def dibujar_conf_LV():
    def proceso_dibujo_LV():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen
            global capas_de_envolventes
            
            if DCBoxes_o_Inv_String == 'DC Boxes':
                capas_de_envolventes = AutoCAD_extension.CAD_draw_config_LV(acad, all_blocks_lv, single_block_lv, bloque_inicial,n_bloques, max_b, max_c, max_f_str_b, max_c_block, filas_en_cajas, cajas_fisicas, contorno_bandas_inf, contorno_bandas_sup, equi_ibfs, equi_ibc, h_modulo)
            else:
                capas_de_envolventes = AutoCAD_extension.CAD_draw_config_LV_inv_string(acad, all_blocks_lv, single_block_lv, strings_ID, String_Inverters_ID, bloque_inicial, n_bloques, max_inv_block, max_str_pinv, h_modulo, dos_inv_por_bloque)
                
            #guardamos en el diccionario
            guardar_variables([capas_de_envolventes],['capas_de_envolventes'])

            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
               
    def cerrar_ventana_tras_simular_dibujo_LV(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_Config_LV")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_5():
        proceso_dibujo_LV()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_LV(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_5) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_LV_CAD_draw = tk.Button(frame_DLV_CAD, text="Draw", command=dibujar_conf_LV, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_LV_CAD_draw.grid(row=1, column=0, pady=20)

entrada_all_blocks_lv = tk.BooleanVar(value=False)
all_blocks_lv = True
single_block_lv=1 #se inicializa fuera del checkbutton para que permita dibujar todos los bloques de golpe sin que falte por definirse, luego cambia de valor sola

def update_single_block_lv():
    global single_block_lv
    single_block_lv = int(spinbox_lv.get())

def activate_spinbox_lv():
    global all_blocks_lv, single_block_lv
    
    if entrada_all_blocks_lv.get():
        spinbox_lv.config(state='normal')
        all_blocks_lv=False
        single_block_lv = int(spinbox_lv.get())
    else:
        spinbox_lv.config(state='disabled')
        all_blocks_lv=True
        
#Marcador y spinbox para dibujar o leer un solo bloque

spinbox_lv = tk.Spinbox(frame_DLV_CAD, from_=1, to=100, state='disabled', command=update_single_block_lv, width=2, font=('Montserrat', 10)) #se cambian los valores a bloque_inicial - n_bloques
spinbox_lv.grid(row=2, column=0, padx=5, pady=5, sticky='w')

check_lv = ttk.Checkbutton(frame_DLV_CAD, text="Single block", variable=entrada_all_blocks_lv, command=activate_spinbox_lv)
check_lv.grid(row=2, column=1, padx=5, pady=5, sticky='w')

#Leer envolventes modificadas manualmente en el CAD
def leer_conf_LV():
    def proceso_leer_conf_LV():
        
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            #Buscamos la referencia especifica, si no está abierta va a leer sobre el archivo activo
            referencia = 'XREF_Config_LV.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_leer(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Leemos los cambios introducidos actualizando las variables afectadas
            if DCBoxes_o_Inv_String == 'DC Boxes':      
                global filas_en_cajas, cajas_fisicas, max_c, max_c_block
                salida_leida = AutoCAD_extension.CAD_read_config_LV(acad, all_blocks_lv, single_block_lv, bloque_inicial,n_bloques, max_b, max_f_str_b,capas_de_envolventes, filas_en_cajas, max_c, max_c_block)
            else:           
                global inv_string, equi_ibv_to_fs, almacen_strings, ori_str_ID, posiciones_inv, inv_como_cajas_fisicas, comienzos_filas_strings, strings_ID, String_Inverters_ID, equi_ibv, equi_reverse_ibv
                #Inv de string
                salida_leida = AutoCAD_extension.CAD_read_config_LV_inv_string(acad, all_blocks_lv, single_block_lv, bloque_inicial, n_bloques,
                                                   max_b, max_inv, max_inv_block, max_str_pinv,
                                                   capas_de_envolventes, equi_reverse_ibv, equi_ibv_to_fs,
                                                   strings_ID, inv_string, strings_fisicos, orientacion, dos_inv_por_bloque)
                
                
            if salida_leida is None:
                error_de_dibujo='Informacion ausente'
            else:
                if DCBoxes_o_Inv_String == 'DC Boxes': 
                    
                    filas_en_cajas, max_c, max_c_block = salida_leida
                    cajas_fisicas = Algoritmo_IXPHOS_2_Config_electrica.cajas_desde_filas_asociadas(strings_fisicos, filas_en_cajas, orientacion, coord_PCS_DC_inputs, sep_caja_tracker,Posicion_optima_caja, bloque_inicial,n_bloques,max_b,max_f_str_b, max_c)
                                    
                    ID_strings_y_DCBoxes()
                    
                    #guardamos en el diccionario los valores actualizados (los de ID_strings_y_DC_Boxes se guardan dentro de la propia funcion)
                    guardar_variables([filas_en_cajas, max_c, max_c_block, cajas_fisicas],['filas_en_cajas', 'max_c', 'max_c_block', 'cajas_fisicas'])
                else:
                    
                     #Inv de string
                    inv_string, equi_ibv_to_fs = salida_leida
                    
                    #Revisamos el almacen de string intercambiados para incluir cambios introducidos a mano (se necesita para las posiciones de los inversores compartidos)
                    almacen_strings = Algoritmo_IXPHOS_2_Config_electrica.reconstruir_almacen_strings_y_puentes(inv_string, strings_fisicos, contorno_bandas, bloque_inicial, n_bloques, max_b, max_inv, max_str_pinv)
                   
                    #ACTUALIZAMOS COMO EN EL ALGORITMO INICIAL
                    ori_str_ID = Algoritmo_IXPHOS_2_Config_electrica.aplicar_flip_strings(
                        bloque_inicial, n_bloques, max_b, max_inv, max_str_pinv,
                        equi_ibv_to_fs, ori_str_ID, orientacion, strings_fisicos
                    )

                    # POSICIONAMIENTO FÍSICO DE LOS INVERSORES
                    inv_string[:, :, :, 0], comienzos_filas_strings = Algoritmo_IXPHOS_2_Config_electrica.posicion_inv_string(
                        inv_string, strings_fisicos, sep_caja_tracker, coord_PCS_DC_inputs, contorno_bandas,
                        Posicion_optima_caja, equi_ibv_to_fs, orientacion, almacen_strings
                    )
                    posiciones_inv=inv_string[:, :, :, 0]
                    
                    #Info fisica
                    inv_como_cajas_fisicas = Algoritmo_IXPHOS_2_Config_electrica.obtener_inv_fisicos(bloque_inicial, n_bloques, max_b, max_inv, inv_string)
                    
                    # ASIGNACIÓN DE IDs DE STRINGS E INVERSORES
                    strings_ID, String_Inverters_ID, equi_ibv, equi_reverse_ibv, inv_string, equi_ibv_to_fs = Algoritmo_IXPHOS_2_Config_electrica.ID_strings_e_inv_string(
                        bloque_inicial, n_bloques, max_b, max_inv, max_inv_block, max_str_pinv,
                        inv_string, dos_inv_por_bloque, equi_ibv_to_fs, strings_fisicos, dist_ext_opuesto_str, ori_str_ID, orientacion
                    )
                    
                    guardar_variables([inv_string, equi_ibv_to_fs, almacen_strings, ori_str_ID, comienzos_filas_strings, posiciones_inv, inv_como_cajas_fisicas, strings_ID, String_Inverters_ID, equi_ibv, equi_reverse_ibv], ['inv_string', 'equi_ibv_to_fs', 'almacen_strings', 'ori_str_ID', 'comienzos_filas_strings', 'posiciones_inv', 'inv_como_cajas_fisicas', 'strings_ID', 'String_Inverters_ID', 'equi_ibv', 'equi_reverse_ibv'])
                     
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
            
    def cerrar_ventana_tras_leer_conf_LV(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Reading completed","Information successfully modified in IXPHOS model.")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Informacion ausente':
                messagebox.showerror("Error", "There is no LV configuration info in the active document. Try to open XREF_Config_LV or activate the correct .dwg file")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while reading, please check that originally drawn elements have not been copypasted or retry.")
                
        except:
            print("Error al borrar el gif")
    
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_6():
        proceso_leer_conf_LV()
        root.after(0, lambda: cerrar_ventana_tras_leer_conf_LV(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_6) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
boton_LV_CAD_read = tk.Button(frame_DLV_CAD, text="Read changes", command=leer_conf_LV, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_LV_CAD_read.grid(row=3, column=0, pady=20)


 


#--------DIBUJAR Y LEER POSICION DE CAJAS
def dibujar_DC_Boxes():
    def proceso_dibujo_DC_Boxes():
        global error_de_dibujo, handle_DC_Boxes, handle_inv_string
        error_de_dibujo='Sin error'
        
        if DCBoxes_o_Inv_String == 'DC Boxes':
            handle_DC_Boxes = np.full((n_bloques+1,3,max_c_block+1),'nah', dtype=object)
            handle_inv_string = None
        else:
            handle_inv_string = np.full((n_bloques+1,3,max_inv_block+1),'nah', dtype=object)
            handle_DC_Boxes = None
            
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            if DCBoxes_o_Inv_String == 'DC Boxes':
                #Dibujamos con la funcion definida en la extension y guardamos el handle por si se modifica luego su posicion a mano
                handle_DC_Boxes = AutoCAD_extension.CAD_draw_DC_Boxes(acad, all_blocks_dcboxes, single_block_dcboxes, bloque_inicial, n_bloques, handle_DC_Boxes, max_c_block, DCBoxes_ID, ancho_caja, largo_caja, h_modulo, orientacion, equi_reverse_ibc)
                
                guardar_variables([handle_DC_Boxes],['handle_DC_Boxes'])
            else:
                handle_inv_string = AutoCAD_extension.CAD_draw_Inv_String(acad, all_blocks_dcboxes, single_block_dcboxes, bloque_inicial, n_bloques, max_inv_block, String_Inverters_ID, ancho_caja, largo_caja, h_modulo, orientacion, equi_reverse_ibv, handle_inv_string)
                
                guardar_variables([handle_inv_string],['handle_inv_string'])
                
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
               
    def cerrar_ventana_tras_simular_dibujo_dcboxes(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_DC_Boxes")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_dcboxes():
        proceso_dibujo_DC_Boxes()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_dcboxes(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_dcboxes) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_CAD_dcboxes = tk.Button(frame_DLV_CAD, text="Draw DC Boxes/Str. Inv.", command=dibujar_DC_Boxes, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_dcboxes.grid(row=1, column=2, pady=10)

entrada_all_blocks_dcboxes = tk.BooleanVar(value=False)
all_blocks_dcboxes = True
single_block_dcboxes=1

def update_single_block_dcboxes():
    global single_block_dcboxes
    single_block_dcboxes = int(spinbox_dcboxes.get())

def activate_spinbox_dcboxes():
    global all_blocks_dcboxes, single_block_dcboxes
    
    if entrada_all_blocks_dcboxes.get():
        spinbox_dcboxes.config(state='normal')
        all_blocks_dcboxes=False
        single_block_dcboxes = int(spinbox_dcboxes.get())
    else:
        spinbox_dcboxes.config(state='disabled')
        all_blocks_dcboxes=True
        
#Marcador y spinbox para dibujar o leer un solo bloque
bloque_inicial=1 #inicializamos bloque inicial en 1 para las spinbox antes de que se cargue el verdadero, al calcular bloque_inicial y n_bloques se cambian tanto from como to, 1 y 100 son solo para inicializar
spinbox_dcboxes = tk.Spinbox(frame_DLV_CAD, from_=1, to=100, state='disabled', command=update_single_block_dcboxes, width=2, font=('Montserrat', 10))
spinbox_dcboxes.grid(row=2, column=2, padx=5, pady=5, sticky='w')

check_dcboxes = ttk.Checkbutton(frame_DLV_CAD, text="Single block", variable=entrada_all_blocks_dcboxes, command=activate_spinbox_dcboxes)
check_dcboxes.grid(row=2, column=3, padx=5, pady=5, sticky='w')




#Leer posiciones de cajas modificadas manualmente en el CAD
def leer_posicion_DC_Boxes():
    def proceso_leer_posicion_DC_Boxes():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            if DCBoxes_o_Inv_String=="DC Boxes":
                #Buscamos la referencia especifica, si no está abierta va a leer sobre el archivo activo
                referencia = 'XREF_DC_Boxes.dwg'
                acad = AutoCAD_extension.conexion_con_CAD_para_leer(referencia)
                if acad is None:
                    error_de_dibujo='AutoCAD no abierto'
                    return #se corta la funcion antes de seguir
                
                root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
                
                #Leemos los cambios introducidos actualizando las variables afectadas
                global cajas_fisicas, DCBoxes_ID
                salida_leida_1, salida_leida_2 = AutoCAD_extension.CAD_read_DC_Boxes_loc(acad, all_blocks_dcboxes, single_block_dcboxes, bloque_inicial, n_bloques, cajas_fisicas, DCBoxes_ID, handle_DC_Boxes, equi_reverse_ibc)
                
                if salida_leida_1 is None:
                    error_de_dibujo='Informacion ausente'
                else:
                    cajas_fisicas  = salida_leida_1
                    DCBoxes_ID = salida_leida_2
                    
                    #guardamos en el diccionario los valores actualizados (los de ID_strings_y_DC_Boxes se guardan dentro de la propia funcion)
                    guardar_variables([cajas_fisicas,DCBoxes_ID],['cajas_fisicas','DCBoxes_ID'])
                    
            else:#PARA INVERSORES DE STRING
                #Buscamos la referencia especifica, si no está abierta va a leer sobre el archivo activo
                referencia = 'XREF_String_Inverters.dwg'
                acad = AutoCAD_extension.conexion_con_CAD_para_leer(referencia)
                if acad is None:
                    error_de_dibujo='AutoCAD no abierto'
                    return #se corta la funcion antes de seguir
                
                root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
                
                #Leemos los cambios introducidos actualizando las variables afectadas
                global inv_string, String_Inverters_ID, posiciones_inv, inv_como_cajas_fisicas
               
                salida_leida_1, salida_leida_2 = AutoCAD_extension.CAD_read_inv_strings_loc(acad, all_blocks_dcboxes, single_block_dcboxes, bloque_inicial, n_bloques, inv_string, String_Inverters_ID, equi_reverse_ibv, dos_inv_por_bloque)
                
                if salida_leida_1 is None:
                    error_de_dibujo='Informacion ausente'
                else:
                    inv_string  = salida_leida_1
                    String_Inverters_ID = salida_leida_2
                    
                    #Actualizamos variables dependientes de la posicion del inv en inv_string 
                    posiciones_inv=inv_string[:, :, :, 0]
                    inv_como_cajas_fisicas = Algoritmo_IXPHOS_2_Config_electrica.obtener_inv_fisicos(bloque_inicial, n_bloques, max_b, max_inv, inv_string)
                    
         
                    #guardamos en el diccionario los valores actualizados (los de ID_strings_y_DC_Boxes se guardan dentro de la propia funcion)
                    guardar_variables([inv_string, String_Inverters_ID, posiciones_inv, inv_como_cajas_fisicas],['inv_string', 'String_Inverters_ID', 'posiciones_inv', 'inv_como_cajas_fisicas'])
                    
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos        
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
            
    def cerrar_ventana_tras_leer_posicion_DC_Boxes(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Reading completed","Information successfully modified in IXPHOS model.")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Informacion ausente':
                messagebox.showerror("Error", "There is no DCBox/StringInverter info in the active document. Try to open XREF_DC_Boxes/XREF_String_Inverters or activate the correct .dwg file")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while reading, please check that originally drawn elements have not been copypasted or retry.")
                
        except:
            print("Error al borrar el gif")
    
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_leer_posicion_DC_Boxes():
        proceso_leer_posicion_DC_Boxes()
        root.after(0, lambda: cerrar_ventana_tras_leer_posicion_DC_Boxes(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_leer_posicion_DC_Boxes) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
boton_DCB_loc_read = tk.Button(frame_DLV_CAD, text="Read changes", command=leer_posicion_DC_Boxes, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_DCB_loc_read.grid(row=3, column=2, pady=10)






#--------DIBUJAR Y LEER ORIENTACION DE STRINGS
def dibujar_orientacion_strings():
    def proceso_dibujo_orientacion_strings():
        global error_de_dibujo
        error_de_dibujo='Sin error'
    
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Interconnection.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            if DCBoxes_o_Inv_String == 'DC Boxes':
                pass
            else:
                AutoCAD_extension.CAD_draw_orientacion_strings(acad, all_blocks_ori_str, single_block_ori_str, strings_ID, bloque_inicial, n_bloques, max_inv_block, max_str_pinv, h_modulo)
                
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
               
    def cerrar_ventana_tras_simular_dibujo_ori_str(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing.")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_ori_str():
        proceso_dibujo_orientacion_strings()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_ori_str(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_ori_str) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_CAD_ori_str = tk.Button(frame_DLV_CAD, text="Draw Str. Direction", command=dibujar_orientacion_strings, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_ori_str.grid(row=1, column=4, pady=10)

entrada_all_blocks_ori_str = tk.BooleanVar(value=False)
all_blocks_ori_str = True
single_block_ori_str=1

def update_single_block_ori_str():
    global single_block_ori_str
    single_block_ori_str = int(spinbox_ori_str.get())

def activate_spinbox_ori_str():
    global all_blocks_ori_str, single_block_ori_str
    
    if entrada_all_blocks_ori_str.get():
        spinbox_ori_str.config(state='normal')
        all_blocks_ori_str=False
        single_block_ori_str = int(spinbox_ori_str.get())
    else:
        spinbox_ori_str.config(state='disabled')
        all_blocks_ori_str=True
        
#Marcador y spinbox para dibujar o leer un solo bloque
bloque_inicial=1 #inicializamos bloque inicial en 1 para las spinbox antes de que se cargue el verdadero, al calcular bloque_inicial y n_bloques se cambian tanto from como to, 1 y 100 son solo para inicializar
spinbox_ori_str = tk.Spinbox(frame_DLV_CAD, from_=1, to=100, state='disabled', command=update_single_block_ori_str, width=2, font=('Montserrat', 10))
spinbox_ori_str.grid(row=2, column=4, padx=5, pady=5, sticky='w')

check_ori_str = ttk.Checkbutton(frame_DLV_CAD, text="Single block", variable=entrada_all_blocks_ori_str, command=activate_spinbox_ori_str)
check_ori_str.grid(row=2, column=5, padx=5, pady=5, sticky='w')




#Leer posiciones de cajas modificadas manualmente en el CAD
def leer_orientacion_strings():
    def proceso_leer_orientacion_strings():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            #Buscamos la referencia especifica, si no está abierta va a leer sobre el archivo activo
            referencia = 'XREF_Interconnection.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_leer(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Leemos los cambios introducidos actualizando las variables afectadas
            global ori_str_ID, strings_ID, ori_str_ID, equi_ibv_to_fs, equi_reverse_ibv, equi_ibv, inv_string
            
            salida_leida_1, salida_leida_2 = AutoCAD_extension.CAD_read_orientacion_strings(acad, all_blocks_ori_str, single_block_ori_str, bloque_inicial, n_bloques, max_b, max_inv, max_inv_block, max_str_pinv, capas_de_envolventes, strings_ID, ori_str_ID)

            if salida_leida_1 is None:
                error_de_dibujo='Informacion ausente'
            else:
                ori_str_ID  = salida_leida_1
                strings_ID = salida_leida_2
                
                                    
                strings_ID, _ , equi_ibv, equi_reverse_ibv, inv_string, equi_ibv_to_fs = Algoritmo_IXPHOS_2_Config_electrica.ID_strings_e_inv_string(
                    bloque_inicial, n_bloques, max_b, max_inv, max_inv_block, max_str_pinv,
                    inv_string, dos_inv_por_bloque, equi_ibv_to_fs, strings_fisicos, dist_ext_opuesto_str, ori_str_ID, orientacion
                )
                
                #guardamos en el diccionario los valores actualizados (los de ID_strings_y_DC_Boxes se guardan dentro de la propia funcion)
                guardar_variables([ori_str_ID,strings_ID, equi_ibv, equi_reverse_ibv, equi_ibv_to_fs, inv_string],['ori_str_ID','strings_ID', 'equi_ibv', 'equi_reverse_ibv', 'equi_ibv_to_fs', 'inv_string'])
                
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos        
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
            
    def cerrar_ventana_tras_leer_orientacion_strings(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Reading completed","Information successfully modified in IXPHOS model.")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Informacion ausente':
                messagebox.showerror("Error", "There is no LV configuration info in the active document. Try to open XREF_DC_Boxes or activate the correct .dwg file")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while reading, please check that originally drawn elements have not been copypasted or retry.")
                
        except:
            print("Error al borrar el gif")
    
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_leer_orientacion_strings():
        proceso_leer_orientacion_strings()
        root.after(0, lambda: cerrar_ventana_tras_leer_orientacion_strings(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_leer_orientacion_strings) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
boton_ori_str_read = tk.Button(frame_DLV_CAD, text="Read changes", command=leer_orientacion_strings, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_ori_str_read.grid(row=3, column=4, pady=10)







        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        




# #Cargar dibujos de interconexionado
# imagen_DFV_daisy = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Diseño FV - Daisy chain.PNG', (300, 150))
# imagen_DFV_leapfrog = cargar_imagen(r'C:\Users\mlopez\OneDrive - GRUPO GRANSOLAR\Desktop\IXPHOS\GUI\Diseño FV - Leapfrog.PNG', (300, 150))

# detalle_DFV_daisy = tk.Label(frame_DFV_drawings, image=imagen_DFV_daisy, bg=blanco_roto)
# detalle_DFV_daisy.grid(row=0, column=0)

# detalle_DFV_leapfrog = tk.Label(frame_DFV_drawings, image=imagen_DFV_leapfrog, bg=blanco_roto)
# detalle_DFV_leapfrog.grid(row=0, column=1, padx=100)











#3.3----------PESTAÑA MAIN CABLE ROUTING



#3.3.1 CABLE MV

    #3.3.1.1 SIMULAR POLILINEAS CABLE MV
def simular_polilineas_cable_mv():
    def proceso_simular_polilineas_cable_mv():
        global pol_cable_MV, errores_grafo
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            pol_cable_MV, errores_grafo = Algoritmo_IXPHOS_3_Cables.lineas_MV_o_FO_por_caminos(pol_guia_MV_FO, pol_cable_MV, 'MV')
              
            guardar_variables([pol_cable_MV], ['pol_cable_MV'])
            
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                
    def cerrar_ventana_tras_simular_pol_mv(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
                
            if errores_grafo:
                messagebox.showerror("Error", f"There was an error while connecting routes, please check that all roads start and end from common vertex: {errores_grafo}")

        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_polilineas_cable_mv():
        proceso_simular_polilineas_cable_mv()
        root.after(0, lambda: cerrar_ventana_tras_simular_pol_mv(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_polilineas_cable_mv) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
boton_polilineas_mv = tk.Button(frame_MV_routing, text="Simulate MV", command=simular_polilineas_cable_mv, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_polilineas_mv.grid(row=0, column=0, columnspan=1, pady=20)



    #3.3.1.2 DIBUJAR POLILINEAS CABLE MV
    
def dibujar_cable_MV():
    def proceso_dibujo_cable_MV():
        global error_de_dibujo
        error_de_dibujo='Sin error'
            
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario
            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen            
            AutoCAD_extension.CAD_draw_polilineas_MV(acad, pol_cable_MV)            

            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
    def cerrar_ventana_tras_dibujar_cable_MV(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_MV_Cables")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_dibujar_cable_MV():
        proceso_dibujo_cable_MV()
        root.after(0, lambda: cerrar_ventana_tras_dibujar_cable_MV(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_dibujar_cable_MV) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_cable_MV_CAD_draw = tk.Button(frame_MV_routing, text="Draw MV Cables", command=dibujar_cable_MV, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_cable_MV_CAD_draw.grid(row=1, column=0, pady=20)




    #3.3.2.3 LEER POLILINEAS CABLE MV DESDE EL CAD


def leer_polilineas_MV():

    def proceso_leer_polilineas_MV():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario
            
            #Buscamos la referencia especifica, si no está abierta va a leer sobre el archivo activo
            referencia = 'XREF_MV.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_leer(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Leemos los cambios introducidos actualizando las variables afectadas          
            global pol_cable_MV
            salida_leida = AutoCAD_extension.CAD_read_polilineas_MV(acad, pol_cable_MV)
            
            if salida_leida is None:
                error_de_dibujo='Informacion ausente'
            else:
                pol_cable_MV = salida_leida
                
                #guardamos en el diccionario los valores actualizados 
                guardar_variables([pol_cable_MV],['pol_cable_MV'])
                
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos   
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
    def cerrar_ventana_tras_leer_polilineas_MV(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Reading completed","Information successfully modified in IXPHOS model.")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Informacion ausente':
                messagebox.showerror("Error", "There are no fiber optic polylines with the mentioned layer name in the active document. Check the layer name, try to open XREF_MV or activate the correct .dwg file")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while reading, please check that originally drawn elements have not been copypasted or retry.")
                
        except:
            print("Error al borrar el gif")
    
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_polilineas_MV():
        proceso_leer_polilineas_MV()
        root.after(0, lambda: cerrar_ventana_tras_leer_polilineas_MV(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_polilineas_MV) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
    
boton_leer_polilineas_MV = tk.Button(frame_MV_routing, text="Read changes", command=leer_polilineas_MV, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_leer_polilineas_MV.grid(row=2, column=0, pady=20)





def dibujar_grafo_guia():
    def proceso_dibujo_grafo_guia():
        global error_de_dibujo
        error_de_dibujo='Sin error'
            
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario
            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen            
            AutoCAD_extension.dibujar_pol_grafo(acad, pol_guia_MV_FO)       

            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
    def cerrar_ventana_tras_dibujar_grafo_guia(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_MV_Cables")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_dibujar_grafo_guia():
        proceso_dibujo_grafo_guia()
        root.after(0, lambda: cerrar_ventana_tras_dibujar_grafo_guia(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_dibujar_grafo_guia) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_grafo_guia_CAD_draw = tk.Button(frame_MV_routing, text="Draw guiding graph", command=dibujar_grafo_guia, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_grafo_guia_CAD_draw.grid(row=5, column=0, pady=90)







#3.3.2 SUBARRAY

    #3.3.2.1 SIMULAR POLILINEAS SUBARRAY
def simular_polilineas_string_bus():
    def proceso_simular_polilineas_string_bus():
        global max_p, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque, filas_con_dcb_extendido, Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID, extender_DC_Bus
        global error_de_simulacion   
        
        error_de_simulacion = 'Sin error'
        max_p=50 #PARAMETRO DE MAXIMOS PUNTOS QUE PUEDEN TENER LAS POLILINEAS DE STRING O DCBUS HASTA LAS CAJAS
        
        try:
            if DCBoxes_o_Inv_String == 'DC Boxes':
                if String_o_Bus == 'String Cable':
                    
                    pol_cable_string, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque = Algoritmo_IXPHOS_3_Cables.polilineas_de_circuitos_cable_string(strings_fisicos, filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_b,max_spf,max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, largo_caja, ancho_caja, dist_primera_pica_extremo_tr)
                    pol_DC_Bus = None #se define vacia porque es una entrada de la funcion de dibujo aunque en esta rama del diseño no se use
                    
                 
                elif String_o_Bus == 'DC Bus':
                                      
                    extender_DC_Bus=['No','No','No','No'] #Parametro de diseño que considera llevar el DCBus al final de los trackers (podria ahorrar harness en los trackers mas largos)         
                    
                    pol_cable_string = None
                    pol_DC_Bus, filas_con_dcb_extendido, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque = Algoritmo_IXPHOS_3_Cables.polilineas_de_circuitos_DC_Bus(filas_en_cajas,filas_en_bandas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_b,max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, largo_caja, ancho_caja, dist_primera_pica_extremo_tr, extender_DC_Bus)
                    
                    Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID = Algoritmo_IXPHOS_3_Cables.insercion_y_medicion_de_harness(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_tpf, filas_en_bandas, filas_con_cable_string, strings_ID, orientacion, String_o_Bus, Interconexionado, extender_DC_Bus, Polo_cercano, strings_fisicos, ori_str_ID, dist_ext_opuesto_str)
                    
                    guardar_variables([filas_con_dcb_extendido, Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID, extender_DC_Bus],['filas_con_dcb_extendido', 'Harness_pos_ID', 'Harness_neg_ID', 'tipos_harness_pos', 'med_tipos_h_pos', 'tipos_harness_neg', 'med_tipos_h_pos', 'med_tipos_h_neg', 'harness_pos', 'harness_neg', 'coord_harness_pos', 'coord_harness_neg', 'strings_ID','extender_DC_Bus'])
         
    
                elif String_o_Bus == 'Both types':
                  
                    extender_DC_Bus=['No','No','No','No'] #Parametro de diseño que considera llevar el DCBus al final de los trackers (podria ahorrar harness en los trackers mas largos)
                    
                    pol_cable_string , pol_DC_Bus, filas_con_dcb_extendido, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque = Algoritmo_IXPHOS_3_Cables.polilineas_de_circuitos_both_types(filas_con_cable_string, strings_fisicos, filas_en_cajas, cajas_fisicas, orientacion, bloque_inicial,n_bloques, max_b, max_spf, max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, dist_primera_pica_extremo_tr, filas_en_bandas, largo_caja, ancho_caja, extender_DC_Bus)
                    
                    Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID = Algoritmo_IXPHOS_3_Cables.insercion_y_medicion_de_harness(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_tpf, filas_en_bandas, filas_con_cable_string, strings_ID, orientacion, String_o_Bus, Interconexionado, extender_DC_Bus, Polo_cercano, strings_fisicos, ori_str_ID, dist_ext_opuesto_str)
                    
                    guardar_variables([filas_con_dcb_extendido, Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID, extender_DC_Bus],['filas_con_dcb_extendido', 'Harness_pos_ID', 'Harness_neg_ID', 'tipos_harness_pos', 'med_tipos_h_pos', 'tipos_harness_neg', 'med_tipos_h_pos', 'med_tipos_h_neg', 'harness_pos', 'harness_neg', 'coord_harness_pos', 'coord_harness_neg', 'strings_ID','extender_DC_Bus'])
                
                    
                elif String_o_Bus == 'Mixed':
        
                    extender_DC_Bus=['No','No','No','No'] #Parametro de diseño que considera llevar el DCBus al final de los trackers (podria ahorrar harness en los trackers mas largos)
                    
                    pol_cable_string, pol_DC_Bus, filas_con_dcb_extendido, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque = Algoritmo_IXPHOS_3_Cables.polilineas_de_circuitos_mixed(filas_con_cable_string, strings_fisicos, filas_en_cajas, cajas_fisicas, orientacion, bloque_inicial,n_bloques, max_b, max_spf, max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, dist_primera_pica_extremo_tr, filas_en_bandas, largo_caja, ancho_caja, extender_DC_Bus)
            
                    Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID = Algoritmo_IXPHOS_3_Cables.insercion_y_medicion_de_harness(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_tpf, filas_en_bandas, filas_con_cable_string, strings_ID, orientacion, String_o_Bus, Interconexionado, extender_DC_Bus, Polo_cercano, strings_fisicos, ori_str_ID, dist_ext_opuesto_str)
                    
                    guardar_variables([filas_con_dcb_extendido, Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID, extender_DC_Bus],['filas_con_dcb_extendido','Harness_pos_ID', 'Harness_neg_ID', 'tipos_harness_pos', 'med_tipos_h_pos', 'tipos_harness_neg', 'med_tipos_h_pos', 'med_tipos_h_neg', 'harness_pos', 'harness_neg', 'coord_harness_pos', 'coord_harness_neg', 'strings_ID','extender_DC_Bus'])
           
            else:#Inv de string
                    
                    pol_cable_string, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque = Algoritmo_IXPHOS_3_Cables.pol_cable_string_en_inv_string(strings_fisicos, inv_string, posiciones_inv, equi_ibv_to_fs, contorno_bandas_inf, contorno_bandas_sup, ori_str_ID, orientacion, strings_ID, bloque_inicial, n_bloques, max_b, max_inv, max_spf, max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, largo_caja, ancho_caja, dist_primera_pica_extremo_tr)
                    pol_DC_Bus = None #se define vacia porque es una entrada de la funcion de dibujo aunque en esta rama del diseño no se use
 
            guardar_variables([max_p, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque],['max_p','pol_cable_string', 'pol_DC_Bus', 'pol_tubo_corrugado_zanja_DC', 'max_tubos_DC_bloque'])
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                
    def cerrar_ventana_tras_simular_pol_str_bus(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")

            #aprovechamos el pulsar el boton para ejecutar esta funcion de la pestaña DISEÑO DEL CABLE, que añade casillas adicionales si se selecciona dc bus
            if String_o_Bus != 'String Cable':
                listar_inputs_adicionales_dc_bus([],[])
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_7():
        proceso_simular_polilineas_string_bus()
        root.after(0, lambda: cerrar_ventana_tras_simular_pol_str_bus(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_7) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
boton_polilineas_str_bus = tk.Button(frame_Subarray_routing, text="Simulate sub-array", command=simular_polilineas_string_bus, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_polilineas_str_bus.grid(row=0, column=0, columnspan=1, pady=20)



    #3.3.2.2 DIBUJAR POLILINEAS SUBARRAY

def dibujar_str_bus():
    def proceso_dibujo_str_bus():
        global error_de_dibujo, handle_cable_string, handle_dcbus     
        error_de_dibujo='Sin error'
        
        # if DCBoxes_o_Inv_String == 'DC_Boxes':
        #     if String_o_Bus != 'DC Bus':
        #         handle_cable_string = np.full((n_bloques+1,3,max_c_block+1,1,masc+1),'nah', dtype=object)
        #     else:
        #         handle_cable_string = None
                
        #     if String_o_Bus != 'String Cable':    
        #         handle_dcbus = np.full((n_bloques+1,3,max_c_block+1,max_bus+1),'nah', dtype=object)
        #     else:
        #         handle_dcbus = None           
        # else:
        #     handle_cable_string = np.full((n_bloques+1,3,max_inv_block+1,1,max_str_pinv+1),'nah', dtype=object)
            
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen            
            # handle_cable_string, handle_dcbus = AutoCAD_extension.CAD_draw_str_bus(acad, all_blocks_str_bus, single_block_str_bus, handle_cable_string, handle_dcbus, String_o_Bus, bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, equi_ibfs, pol_cable_string, pol_DC_Bus)
            
            AutoCAD_extension.CAD_draw_str_bus(acad, all_blocks_str_bus, single_block_str_bus, String_o_Bus, bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, pol_cable_string, pol_DC_Bus)
            
            #guardamos en el diccionario
            # guardar_variables([handle_cable_string, handle_dcbus],['handle_cable_string', 'handle_dcbus'])
            
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos            
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
    def cerrar_ventana_tras_dibujar_str_bus(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_Subarray_Cables")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_8():
        proceso_dibujo_str_bus()
        root.after(0, lambda: cerrar_ventana_tras_dibujar_str_bus(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_8) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_str_bus_CAD_draw = tk.Button(frame_Subarray_routing, text="Draw", command=dibujar_str_bus, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_str_bus_CAD_draw.grid(row=1, column=0, pady=20)

entrada_all_blocks_str_bus = tk.BooleanVar(value=False)
all_blocks_str_bus = True
single_block_str_bus = 1 #se inicializa fuera del checkbutton para que permita dibujar todos los bloques de golpe sin que falte por definirse, luego cambia de valor sola

def update_single_block_str_bus():
    global single_block_str_bus
    single_block_str_bus = int(spinbox_str_bus.get())

def activate_spinbox_str_bus():
    global all_blocks_str_bus, single_block_str_bus
    
    if entrada_all_blocks_str_bus.get():
        spinbox_str_bus.config(state='normal')
        all_blocks_str_bus=False
        single_block_str_bus = int(spinbox_str_bus.get())
    else:
        spinbox_str_bus.config(state='disabled')
        all_blocks_str_bus=True
        
#Marcador y spinbox para dibujar o leer un solo bloque
spinbox_str_bus = tk.Spinbox(frame_Subarray_routing, from_=1, to=100, state='disabled', command=update_single_block_str_bus, width=2, font=('Montserrat', 10))
spinbox_str_bus.grid(row=2, column=0, padx=5, pady=5, sticky='w')

check_str_bus = ttk.Checkbutton(frame_Subarray_routing, text="Single block", variable=entrada_all_blocks_str_bus, command=activate_spinbox_str_bus)
check_str_bus.grid(row=2, column=1, padx=5, pady=5, sticky='w')



    #3.3.2.3 LEER POLILINEAS SUBARRAY
#Leer polilineas de subarray modificadas manualmente en el CAD
def leer_conf_str_bus():
    def proceso_leer_conf_str_bus():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario
            
            #Buscamos la referencia especifica, si no está abierta va a leer sobre el archivo activo
            referencia = 'XREF_Subarray_Cables_LV.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_leer(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Leemos los cambios introducidos actualizando las variables afectadas
            global pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque
            
            # s1, s2, s3, unregistered_object = AutoCAD_extension.CAD_read_str_bus_opcion_handle(acad, all_blocks_str_bus, single_block_str_bus, handle_cable_string, handle_dcbus, equi_reverse_ibfs, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC)
            
            if DCBoxes_o_Inv_String == 'DC Boxes':
                s1, s2, s3, s4 = AutoCAD_extension.CAD_read_str_bus_opcion_proximidad(acad, all_blocks_str_bus, single_block_str_bus, bloque_inicial, n_bloques, max_b, max_c, max_p, cajas_fisicas, filas_en_cajas, strings_fisicos, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC)
            else:
                s1, s2, s3, s4 = AutoCAD_extension.CAD_read_str_cable_inv_string(acad, all_blocks_str_bus, single_block_str_bus, bloque_inicial, n_bloques, max_b, max_inv, max_p, inv_string, strings_fisicos, equi_ibv, equi_ibv_to_fs, strings_ID, pol_cable_string, pol_tubo_corrugado_zanja_DC)

            if s1 is None and s2 is None:
                error_de_dibujo='Informacion ausente'
            else:
                pol_cable_string = s1
                pol_DC_Bus = s2
                pol_tubo_corrugado_zanja_DC = s3
                max_tubos_DC_bloque = s4
                
                # if unregistered_object !=[]:
                #     error_de_dibujo = 'Objecto no registrado'
                #guardamos en el diccionario los valores actualizados
                guardar_variables([pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque],['pol_cable_string', 'pol_DC_Bus', 'pol_tubo_corrugado_zanja_DC', 'max_tubos_DC_bloque'])
        
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'    
            traceback.print_exc()
            
    def cerrar_ventana_tras_leer_dibujo_str_bus(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Reading completed","Information successfully modified in IXPHOS model.")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Informacion ausente':
                messagebox.showerror("Error", "There are no subarray polylines in the active document. Try to open XREF_Subarray_Cables or activate the correct .dwg file")
            
            elif error_de_dibujo == 'Objecto no registrado':
                messagebox.showerror("Error", "There are polylines with a wrong handle number in the drawing, check that originally drawn elements have not been copypasted or retry.")

            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while reading, please check that originally drawn elements have not been copypasted or retry.")
                
        except:
            print("Error al borrar el gif")
    
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_9():
        proceso_leer_conf_str_bus()
        root.after(0, lambda: cerrar_ventana_tras_leer_dibujo_str_bus(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_9) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
boton_str_bus_CAD_read = tk.Button(frame_Subarray_routing, text="Read changes", command=leer_conf_str_bus, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_str_bus_CAD_read.grid(row=3, column=0, pady=20)








#-----------SIMULAR ARRAY Y DIBUJAR POLILINEAS

def simular_polilineas_array():
    
    def proceso_simular_polilineas_array():
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
            
    
        try:
            global pol_array_cable, max_p_array, n_circuitos_max_lado_PCS, n_circuitos_max_entre_trackers, salida_zanja_LV_caja_inv
            
            salida_zanja_LV_caja_inv= 1 + largo_caja/2 #TODO salida del cable de array de la caja, de momento no se deja elegir al usuario a que distancia

            max_p_array = 100
            n_circuitos_max_lado_PCS = 14
            n_circuitos_max_entre_trackers = 8
            
            if entrada_DCBoxes_o_Inv_String.get() == 'DC Boxes':
                pol_array_cable = Algoritmo_IXPHOS_3_Cables.polilinea_array(max_p_array, bloque_inicial,n_bloques, max_b, max_f_str_b, max_c, coord_PCS_DC_inputs, orientacion, pitch, cajas_fisicas, filas_en_cajas, filas_en_bandas, bandas_anexas, bandas_separadas, bandas_aisladas, sep_caja_tracker, sep_zanja_tracker, salida_zanja_LV_caja_inv, largo_caja, n_circuitos_max_lado_PCS, n_circuitos_max_entre_trackers)
            else:
                pol_array_cable = Algoritmo_IXPHOS_3_Cables.polilinea_array(max_p_array, bloque_inicial,n_bloques, max_b, max_f_str_b, max_inv, coord_PCS_DC_inputs, orientacion, pitch, inv_como_cajas_fisicas, filas_en_inv_como_filas_en_cajas, filas_en_bandas, bandas_anexas, bandas_separadas, bandas_aisladas, sep_caja_tracker, sep_zanja_tracker, salida_zanja_LV_caja_inv, largo_caja, n_circuitos_max_lado_PCS, n_circuitos_max_entre_trackers)
                                                  
            guardar_variables([pol_array_cable, max_p_array, n_circuitos_max_lado_PCS, n_circuitos_max_entre_trackers, salida_zanja_LV_caja_inv],['pol_array_cable', 'max_p_array', 'n_circuitos_max_lado_PCS', 'n_circuitos_max_entre_trackers', 'salida_zanja_LV_caja_inv'])
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                
    def cerrar_ventana_tras_simular_pol_array(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")            
        except:
            print("Error al borrar el gif")
            
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_10():
        proceso_simular_polilineas_array()
        root.after(0, lambda: cerrar_ventana_tras_simular_pol_array(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_10) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
boton_polilineas_array = tk.Button(frame_Array_routing, text="Simulate array", command=simular_polilineas_array, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_polilineas_array.grid(row=0, column=0, columnspan=1, pady=20)


#DIBUJAR Y LEER POLILINEAS DE ARRAY

def dibujar_array():
    def proceso_dibujo_array():
        global error_de_dibujo, handle_cable_array    
        error_de_dibujo='Sin error'
        
        # handle_cable_array = np.full((n_bloques+1,3,max_c_block+1),'nah', dtype=object)
            
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario
            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen
            if DCBoxes_o_Inv_String == 'DC Boxes':
                # handle_cable_array = AutoCAD_extension.CAD_draw_array(acad, all_blocks_array, single_block_array, handle_cable_array, String_o_Bus, bloque_inicial,n_bloques, max_b, max_c, equi_ibc, pol_array_cable)
                AutoCAD_extension.CAD_draw_array(acad, all_blocks_array, single_block_array, handle_cable_array, String_o_Bus, bloque_inicial,n_bloques, max_b, max_c, equi_ibc, pol_array_cable)
            else:
               AutoCAD_extension.CAD_draw_array(acad, all_blocks_array, single_block_array, handle_cable_array, String_o_Bus, bloque_inicial,n_bloques, max_b, max_inv, None, pol_array_cable)
            #guardamos en el diccionario
            # guardar_variables([handle_cable_array],['handle_cable_array'])
            
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'        
            traceback.print_exc()
            
    def cerrar_ventana_tras_simular_dibujo_array(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_Array_Cables")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_11():
        proceso_dibujo_array()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_array(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_11) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_array_CAD_draw = tk.Button(frame_Array_routing, text="Draw", command=dibujar_array, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_array_CAD_draw.grid(row=1, column=0, pady=20)

entrada_all_blocks_array = tk.BooleanVar(value=False)
all_blocks_array = True
single_block_array=1

def update_single_block_array():
    global single_block_array
    single_block_array = int(spinbox_array.get())

def activate_spinbox_array():
    global all_blocks_array, single_block_array
    
    if entrada_all_blocks_array.get():
        spinbox_array.config(state='normal')
        all_blocks_array=False
        single_block_array = int(spinbox_array.get())
    else:
        spinbox_array.config(state='disabled')
        all_blocks_array=True
        
#Marcador y spinbox para dibujar o leer un solo bloque
spinbox_array = tk.Spinbox(frame_Array_routing, from_=1, to=100, state='disabled', command=update_single_block_array, width=2, font=('Montserrat', 10))
spinbox_array.grid(row=2, column=0, padx=5, pady=5, sticky='w')

check_array = ttk.Checkbutton(frame_Array_routing, text="Single block", variable=entrada_all_blocks_array, command=activate_spinbox_array)
check_array.grid(row=2, column=1, padx=5, pady=5, sticky='w')


#Leer polilineas de subarray modificadas manualmente en el CAD
def leer_conf_array():
    def proceso_leer_conf_array():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos la referencia especifica, si no está abierta va a leer sobre el archivo activo
            referencia = 'XREF_Array_Cables.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_leer(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Leemos los cambios introducidos actualizando las variables afectadas
            global pol_array_cable
            # salida_leida = AutoCAD_extension.CAD_read_array_opcion_handle(acad, handle_cable_array, equi_reverse_ibc, pol_array_cable)
            if DCBoxes_o_Inv_String == 'DC Boxes':
                salida_leida = AutoCAD_extension.CAD_read_array_opcion_proximidad(acad, all_blocks_array, single_block_array, bloque_inicial, n_bloques, max_b, max_c, cajas_fisicas, pol_array_cable)
            else:
                salida_leida = AutoCAD_extension.CAD_read_array_opcion_proximidad(acad, all_blocks_array, single_block_array, bloque_inicial, n_bloques, max_b, max_inv, inv_como_cajas_fisicas, pol_array_cable)

            if salida_leida is None:
                error_de_dibujo='Informacion ausente'
            else:
                pol_array_cable = salida_leida
            
                #guardamos en el diccionario los valores actualizados 
                guardar_variables([pol_array_cable],['pol_array_cable'])
                
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
    def cerrar_ventana_tras_leer_array(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Reading completed","Information successfully modified in IXPHOS model.")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Informacion ausente':
                messagebox.showerror("Error", "There are no array polylines in the active document. Try to open XREF_Array_Cables or activate the correct .dwg file")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                # messagebox.showerror("Error", "There was an error while reading, please check that originally drawn elements have not been copypasted or retry.")
                messagebox.showerror("Error", "There was an error while reading, please retry.")
                
        except:
            print("Error al borrar el gif")
    
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_12():
        proceso_leer_conf_array()
        root.after(0, lambda: cerrar_ventana_tras_leer_array(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_12) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
boton_array_CAD_read = tk.Button(frame_Array_routing, text="Read changes", command=leer_conf_array, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_array_CAD_read.grid(row=3, column=0, pady=20)






#%%

#4.---------------------------CUARTA PESTAÑA - SERVICIOS AUXILIARES Y TUBOS------------------------

#LAYOUT DE FRAMES PARA INTRODUCIR DATOS
frame_aass_tubos_container = tk.Frame(AASS_NB, background=blanco_roto)
frame_aass_tubos_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)

frame_tubos= tk.Frame(frame_aass_tubos_container, background=blanco_roto)
frame_tubos.pack(side='left', padx=30, pady=30, fill='both', expand=True)

frame_AASS= tk.Frame(frame_aass_tubos_container, background=blanco_roto)
frame_AASS.pack(side='left', padx=30, pady=30, fill='both', expand=True)

frame_FO_lines= tk.Frame(frame_aass_tubos_container, background=blanco_roto)
frame_FO_lines.pack(side='left', padx=30, pady=30, fill='both', expand=True)

#------------------------TUBOS----------------------------------

#DIBUJAR Y LEER POLILINEAS

def dibujar_tubos_DC():
    def proceso_dibujo_tubos_DC():
        global error_de_dibujo, handle_cable_tubos_DC    
        error_de_dibujo='Sin error'
            
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario
            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension
            AutoCAD_extension.CAD_draw_tubo_DC(acad, all_blocks_tubos_DC, single_block_tubos_DC, bloque_inicial, n_bloques, max_tubos_DC_bloque, pol_tubo_corrugado_zanja_DC)
            
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'        
            traceback.print_exc()
            
    def cerrar_ventana_tras_simular_dibujo_tubos_DC(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_tubos_DC_Cables")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_dibujar_tubos_DC():
        proceso_dibujo_tubos_DC()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_tubos_DC(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_dibujar_tubos_DC) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_tubos_DC_CAD_draw = tk.Button(frame_tubos, text="Draw DC Conduits", command=dibujar_tubos_DC, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_tubos_DC_CAD_draw.grid(row=1, column=0, pady=20)

entrada_all_blocks_tubos_DC = tk.BooleanVar(value=False)
all_blocks_tubos_DC = True
single_block_tubos_DC=1

def update_single_block_tubos_DC():
    global single_block_tubos_DC
    single_block_tubos_DC = int(spinbox_tubos_DC.get())

def activate_spinbox_tubos_DC():
    global all_blocks_tubos_DC, single_block_tubos_DC
    
    if entrada_all_blocks_tubos_DC.get():
        spinbox_tubos_DC.config(state='normal')
        all_blocks_tubos_DC=False
        single_block_tubos_DC = int(spinbox_tubos_DC.get())
    else:
        spinbox_tubos_DC.config(state='disabled')
        all_blocks_tubos_DC=True
        
#Marcador y spinbox para dibujar o leer un solo bloque
spinbox_tubos_DC = tk.Spinbox(frame_tubos, from_=1, to=100, state='disabled', command=update_single_block_tubos_DC, width=2, font=('Montserrat', 10))
spinbox_tubos_DC.grid(row=2, column=0, padx=5, pady=5, sticky='w')

check_tubos_DC = ttk.Checkbutton(frame_tubos, text="Single block", variable=entrada_all_blocks_tubos_DC, command=activate_spinbox_tubos_DC)
check_tubos_DC.grid(row=2, column=1, padx=5, pady=5, sticky='w')


#Leer polilineas de subtubos_DC modificadas manualmente en el CAD
def leer_conf_tubos_DC():
    def proceso_leer_conf_tubos_DC():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos la referencia especifica, si no está abierta va a leer sobre el archivo activo
            referencia = 'XREF_DC_Conduits.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_leer(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Leemos los cambios introducidos actualizando las variables afectadas
            global pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque
            # salida_leida = AutoCAD_extension.CAD_read_tubos_DC_opcion_handle(acad, handle_cable_tubos_DC, equi_reverse_ibc, pol_tubos_DC_cable)
            s1, s2 = AutoCAD_extension.CAD_read_tubo_zanja_DC(acad, all_blocks_tubos_DC, single_block_tubos_DC, bloque_inicial, n_bloques, max_p, strings_fisicos, pol_tubo_corrugado_zanja_DC)
            
            
            if s1 is None:
                error_de_dibujo='Informacion ausente'
            else:
                pol_tubo_corrugado_zanja_DC = s1
                max_tubos_DC_bloque = s2
            
                #guardamos en el diccionario los valores actualizados 
                guardar_variables([pol_tubo_corrugado_zanja_DC,max_tubos_DC_bloque],['pol_tubo_corrugado_zanja_DC','max_tubos_DC_bloque'])
                
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos        
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
    def cerrar_ventana_tras_leer_tubos_DC(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Reading completed","Information successfully modified in IXPHOS model.")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Informacion ausente':
                messagebox.showerror("Error", "There are no tubos_DC polylines in the active document. Try to open XREF_DC_Conduits or activate the correct .dwg file")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                # messagebox.showerror("Error", "There was an error while reading, please check that originally drawn elements have not been copypasted or retry.")
                messagebox.showerror("Error", "There was an error while reading, please retry.")
                
        except:
            print("Error al borrar el gif")
    
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_leer_tubos_DC():
        proceso_leer_conf_tubos_DC()
        root.after(0, lambda: cerrar_ventana_tras_leer_tubos_DC(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_leer_tubos_DC) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
boton_tubos_DC_CAD_read = tk.Button(frame_tubos, text="Read changes", command=leer_conf_tubos_DC, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_tubos_DC_CAD_read.grid(row=3, column=0, pady=20)




def entradas_medicion_tubos_DC(valores_dados_dc_conduits):    
    global valor_safety_maj_dc_conduit
    
        #Mayoracion de seguridad dc_conduit
    etiqueta_safety_maj_dc_conduit = tk.Label(frame_tubos, text="Safety Margin (%)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_safety_maj_dc_conduit.grid(row=4, column=0, padx=(10,0),pady=(15,15))
    valor_safety_maj_dc_conduit = tk.StringVar()
    valor_safety_maj_dc_conduit.set(valores_dados_dc_conduits[0])
    entrada_safety_maj_dc_conduit = tk.Entry(frame_tubos, textvariable=valor_safety_maj_dc_conduit, width=5)
    entrada_safety_maj_dc_conduit.grid(row=4, column=1, padx=(5,20), pady=(15,15))

valores_iniciales_tubos=[[]]





#-------------------------------------------SERVICIOS AUXILIARES/COMUNICACIONES----------------------------------------

#---------Simular circuitos LVAC y ETH
def simular_polilineas_AASS_LVAC_y_ethernet():
    global pol_AASS_LVAC, pol_ethernet, max_p_AASS_LVAC, max_p_AASS_eth, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC
    
    pol_AASS_LVAC, pol_ethernet, max_p_AASS_LVAC, max_p_AASS_eth, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC = Algoritmo_IXPHOS_3_Cables.polilineas_AASS_LVAC_y_ethernet(bloque_inicial, n_bloques, coord_PCS_AASS_inputs, coord_Comboxes, coord_Tracknets, coord_TBoxes, coord_AWS, coord_CCTV, coord_OyM_LVAC, coord_SS_LVAC, coord_Warehouse_LVAC)

    guardar_variables([pol_AASS_LVAC, pol_ethernet, max_p_AASS_LVAC, max_p_AASS_eth, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC],['pol_AASS_LVAC', 'pol_ethernet', 'max_p_AASS_LVAC', 'max_p_AASS_eth', 'pol_CCTV_LVAC', 'pol_OyM_supply_LVAC', 'pol_Warehouse_supply_LVAC'] )


boton_simular_LVAC_ETH = tk.Button(frame_AASS, text="Simulate AASS", command=simular_polilineas_AASS_LVAC_y_ethernet, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_simular_LVAC_ETH.grid(row=0, column=0, pady=20)




#----------Dibujar LVAC y ethernet

def dibujar_AASS_LVAC_y_ethernet():
    def proceso_dibujo_AASS_LVAC_y_ethernet():
        global error_de_dibujo   
        error_de_dibujo='Sin error'
            
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen
            AutoCAD_extension.CAD_draw_AASS_LVAC_y_ethernet(acad, bloque_inicial, n_bloques, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC)
           
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'        
            traceback.print_exc()
            
    def cerrar_ventana_tras_simular_dibujo_AASS_LVAC_y_ethernet(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_AASS_Cables")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_11():
        proceso_dibujo_AASS_LVAC_y_ethernet()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_AASS_LVAC_y_ethernet(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_11) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()


boton_dibujar_LVAC_ETH = tk.Button(frame_AASS, text="Draw AASS", command=dibujar_AASS_LVAC_y_ethernet, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_dibujar_LVAC_ETH.grid(row=1, column=0, pady=20)




#---------------Leer LVAC y ethernet

def leer_AASS_LVAC_y_ethernet():
    def proceso_leer_AASS_LVAC_y_ethernet():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos la referencia especifica, si no está abierta va a leer sobre el archivo activo
            referencia = 'XREF_AASS_Cables.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_leer(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Leemos los cambios introducidos actualizando las variables afectadas
            global pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC

            s1, s2, s3, s4, s5 = AutoCAD_extension.CAD_read_AASS_LVAC_y_ethernet(acad, bloque_inicial, n_bloques, pol_AASS_LVAC, pol_ethernet, coord_Comboxes, coord_Tracknets, coord_TBoxes, coord_AWS, coord_PCS_AASS_inputs)
            
            if s1 is None and s2 is None and s3 is [] and s4 is [] and s5 is []:
                error_de_dibujo='Informacion ausente'
            else:
                pol_AASS_LVAC = s1
                pol_CCTV_LVAC = s2
                pol_OyM_supply_LVAC = s3
                pol_Warehouse_supply_LVAC = s4
                pol_ethernet = s5
                #guardamos en el diccionario los valores actualizados 
                guardar_variables([pol_AASS_LVAC, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_ethernet],['pol_AASS_LVAC', 'pol_CCTV_LVAC', 'pol_OyM_supply_LVAC', 'pol_Warehouse_supply_LVAC', 'pol_ethernet'])
            
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos        
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
    def cerrar_ventana_tras_leer_AASS_LVAC_y_ethernet(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Reading completed","Information successfully modified in IXPHOS model.")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Informacion ausente':
                messagebox.showerror("Error", "There are no AASS_LVAC and ethernet polylines in the active document. Try to open XREF_AASS_Cables or activate the correct .dwg file")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                # messagebox.showerror("Error", "There was an error while reading, please check that originally drawn elements have not been copypasted or retry.")
                messagebox.showerror("Error", "There was an error while reading, please retry.")
                
        except:
            print("Error al borrar el gif")
    
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_leer_AASS_LVAC_y_ethernet():
        proceso_leer_AASS_LVAC_y_ethernet()
        root.after(0, lambda: cerrar_ventana_tras_leer_AASS_LVAC_y_ethernet(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_leer_AASS_LVAC_y_ethernet) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
boton_leer_LVAC_ETH = tk.Button(frame_AASS, text="Read changes", command=leer_AASS_LVAC_y_ethernet, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_leer_LVAC_ETH.grid(row=3, column=0, pady=20)






#-----------TRAZAR FIBRA OPTICA

    #Crear entradas
entradas_lineas_FO = []

def agregar_linea_FO():
    global entradas_lineas_FO, contador_tramos_FO

    fila_frame = ttk.Frame(scrollable_frame_lineas_FO)
    fila_frame.pack(anchor="w", fill="x")

    etiqueta = ttk.Label(fila_frame, text=f"Line {len(entradas_lineas_FO) + 1}")
    etiqueta.pack(side="left", padx=5, pady=5)

    entradas_lineas_FO.append([etiqueta, []])
    contador_tramos_FO = 0

def agregar_tramo_linea_FO():
    global entradas_lineas_FO, contador_tramos_FO

    if not entradas_lineas_FO:
        return  # Nada a lo que anidar subentradas_lineas_FO
    
    contador_tramos_FO = contador_tramos_FO + 1
    
    sub_frame = ttk.Frame(scrollable_frame_lineas_FO)
    sub_frame.pack(anchor="w", fill="x", padx=20)

    sub_label = ttk.Label(sub_frame, text=f"L {len(entradas_lineas_FO)}.{contador_tramos_FO}")
    sub_label.pack(side="left", padx=5, pady=5)

    entry1 = ttk.Entry(sub_frame, width=10)
    entry1.pack(side="left", padx=5)
    entry2 = ttk.Entry(sub_frame, width=10)
    entry2.pack(side="left", padx=5)

    entradas_lineas_FO[-1][1].append([entry1, entry2])

def eliminar_ultimo_elemento_FO():
    global entradas_lineas_FO, contador_tramos_FO

    if not entradas_lineas_FO:
        return  # Nada que borrar

    etiqueta, subfilas = entradas_lineas_FO[-1]

    if subfilas:  # Hay tramos que borrar
        entrada_1, entrada_2 = subfilas.pop()
        entrada_1.master.destroy()  # destruye sub_frame que contiene ambos Entry
        contador_tramos_FO = max(0, contador_tramos_FO - 1)
    else:
        etiqueta.master.destroy()  # destruye fila_frame (la línea)
        entradas_lineas_FO.pop()



# Canvas con scroll
canvas_lineas_FO = tk.Canvas(frame_FO_lines, height=400)
scrollbar_lineas_FO = ttk.Scrollbar(frame_FO_lines, orient="vertical", command=canvas_lineas_FO.yview)
scrollable_frame_lineas_FO = ttk.Frame(canvas_lineas_FO)

# Actualizar región del scroll
scrollable_frame_lineas_FO.bind("<Configure>",lambda e: canvas_lineas_FO.configure(scrollregion=canvas_lineas_FO.bbox("all")))

canvas_frame_lineas_FO = canvas_lineas_FO.create_window((0, 0), window=scrollable_frame_lineas_FO, anchor="nw")
canvas_lineas_FO.configure(yscrollcommand=scrollbar_lineas_FO.set)

canvas_lineas_FO.grid(row=0, column=0, columnspan=3, sticky="nsew")
scrollbar_lineas_FO.grid(row=0, column=3, sticky="ns")

# Botones
ttk.Button(frame_FO_lines, text="Add FO Line", command=agregar_linea_FO).grid(row=1, column=0, pady=10, padx=5)
ttk.Button(frame_FO_lines, text="Add Connection", command=agregar_tramo_linea_FO).grid(row=1, column=1, pady=10, padx=5)
ttk.Button(frame_FO_lines, text="Remove Last", command=eliminar_ultimo_elemento_FO).grid(row=1, column=2, pady=10, padx=5)


#Cargar entradas desde proyecto guardado (se lee al cargar el proyecto)
def cargar_entradas_lineas_FO():
    global entradas_lineas_FO, contador_tramos_FO

    # Limpiar las entradas actuales
    while entradas_lineas_FO:
        eliminar_ultimo_elemento_FO()

    # Ignorar el primer elemento si es [0]
    for item in lineas_FO:
        if item == [0]:
            continue

        etiqueta_texto, tramos = item

        agregar_linea_FO()
        entradas_lineas_FO[-1][0].config(text=etiqueta_texto)  # renombrar etiqueta visual

        for val1, val2 in tramos:
            agregar_tramo_linea_FO()
            entry1, entry2 = entradas_lineas_FO[-1][1][-1]
            entry1.insert(0, str(val1))
            entry2.insert(0, str(val2))





    #Leer entradas y pasar valores a polilinea de diseño
def leer_config_FO():
    
    def proceso_leer_config_FO():
        global lineas_FO, pol_cable_FO
        global error_lectura
        error_lectura = []
        
        lineas_FO = [[0]]
        pol_cable_FO = [[0]]
        
        c_l=0
        for etiqueta, subfilas in entradas_lineas_FO:
            texto = etiqueta.cget("text")
            valores_subfilas = []
            
            pol_cable_FO.append([])
            c_l=c_l+1
            for entrada_1, entrada_2 in subfilas:
                valor_entrada_1 = entrada_1.get() #Pueden ser numeros de bloque, O&M (u OyM) o SS
                valor_entrada_2 = entrada_2.get() 
                
                if valor_entrada_1=='O&M' or valor_entrada_1=='OyM' or valor_entrada_1=='OYM':
                    valor_coord_inicio = coord_OyM_Control_Room
                else:
                    bloque_inicio= int(valor_entrada_1)
                    valor_coord_inicio = coord_Comboxes[bloque_inicio]
                    
                if valor_entrada_2=='O&M' or valor_entrada_2=='OyM' or valor_entrada_2=='OYM':
                    valor_coord_destino = coord_OyM_Control_Room        
                elif valor_entrada_2=='SS':
                    valor_coord_destino = coord_SS_Control_Room
                else:
                    bloque_destino = int(valor_entrada_2)
                    valor_coord_destino = coord_Comboxes[bloque_destino]
                    
                if valor_entrada_1 == valor_entrada_2:
                    error_lectura.append([f'L{c_l}',f'B{valor_entrada_1}'])
                
                valores_subfilas.append([valor_entrada_1, valor_entrada_2])
                
                pol_cable_FO[c_l].append([valor_coord_inicio,valor_coord_destino])
            
            lineas_FO.append([texto, valores_subfilas])
            
            
        guardar_variables([lineas_FO, pol_cable_FO], ['lineas_FO', 'pol_cable_FO'])

    def cerrar_ventana_tras_leer_config_FO(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_lectura != []:
                messagebox.showerror("Error", f"Introduced values are duplicated: {error_lectura}")

        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_leer_config_FO():
        proceso_leer_config_FO()
        root.after(0, lambda: cerrar_ventana_tras_leer_config_FO(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_leer_config_FO) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()


boton_leer_config_FO = tk.Button(frame_FO_lines, text="Read Values", command=leer_config_FO, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_leer_config_FO.grid(row=2, column=0, pady=50, padx=5)







def simular_polilineas_cable_FO():
    def proceso_simular_polilineas_cable_FO():
        global pol_cable_FO
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            pol_cable_FO, error = Algoritmo_IXPHOS_3_Cables.lineas_MV_o_FO_por_caminos(pol_guia_MV_FO, pol_cable_FO, 'FO')
            
            guardar_variables([pol_cable_FO], ['pol_cable_FO'])
            
            if error==True:
                error_de_simulacion = 'Grafo'
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                
    def cerrar_ventana_tras_simular_pol_FO(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
            elif error_de_simulacion == 'Grafo':
                messagebox.showerror("Error", "There was an error while connecting routes, please check that all roads start and end from common vertex.")

        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_polilineas_cable_FO():
        proceso_simular_polilineas_cable_FO()
        root.after(0, lambda: cerrar_ventana_tras_simular_pol_FO(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_polilineas_cable_FO) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
boton_polilineas_FO = tk.Button(frame_FO_lines, text="Simulate FO", command=simular_polilineas_cable_FO, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_polilineas_FO.grid(row=3, column=0, columnspan=1, pady=20)





def dibujar_cable_FO():
    def proceso_dibujo_cable_FO():
        global error_de_dibujo
        error_de_dibujo='Sin error'
            
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos si está la referencia unificada abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen            
            AutoCAD_extension.CAD_draw_polilineas_FO(acad, pol_cable_FO)            
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
        pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
        
    def cerrar_ventana_tras_dibujar_cable_FO(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_FO_Cables")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_dibujar_cable_FO():
        proceso_dibujo_cable_FO()
        root.after(0, lambda: cerrar_ventana_tras_dibujar_cable_FO(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_dibujar_cable_FO) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_cable_FO_CAD_draw = tk.Button(frame_FO_lines, text="Draw FO Cables", command=dibujar_cable_FO, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_cable_FO_CAD_draw.grid(row=3, column=1, pady=20)





def leer_polilineas_fibra_optica():

    def proceso_leer_polilineas_fibra_optica():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos la referencia especifica, si no está abierta va a leer sobre el archivo activo
            referencia = 'XREF_FO.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_leer(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Leemos los cambios introducidos actualizando las variables afectadas          
            global pol_cable_FO
            salida_leida = AutoCAD_extension.CAD_read_polilineas_FO(acad, pol_cable_FO)
            
            if salida_leida is None:
                error_de_dibujo='Informacion ausente'
            else:
                pol_cable_FO = salida_leida
                
                #guardamos en el diccionario los valores actualizados 
                guardar_variables([pol_cable_FO],['pol_cable_FO'])
                
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
    def cerrar_ventana_tras_leer_polilineas_FO(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Reading completed","Information successfully modified in IXPHOS model.")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Informacion ausente':
                messagebox.showerror("Error", "There are no fiber optic polylines with the mentioned layer name in the active document. Check the layer name, try to open XREF_FO or activate the correct .dwg file")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while reading, please check that originally drawn elements have not been copypasted or retry.")
                
        except:
            print("Error al borrar el gif")
    
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_polilineas_FO():
        proceso_leer_polilineas_fibra_optica()
        root.after(0, lambda: cerrar_ventana_tras_leer_polilineas_FO(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_polilineas_FO) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
    
boton_leer_polilineas_FO = tk.Button(frame_FO_lines, text="Read changes", command=leer_polilineas_fibra_optica, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_leer_polilineas_FO.grid(row=3, column=2, pady=20)


















#%%
#---------------------------QUINTA PESTAÑA - MEDICION Y CALCULO DEL CABLE------------------------

#LAYOUT DE FRAMES PARA INTRODUCIR DATOS
# Crear un frame para meter en él dos frames y darles un margen común respecto a los bordes
frame_Med_Cables_container = tk.Frame(Cable_NB, background=blanco_roto)
frame_Med_Cables_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)


# Introducir un nuevo notebook para diferenciar entradas de medicion en cable MV, LV y AASS y COMS
notebook_med_cables = ttk.Notebook(frame_Med_Cables_container, style='TNotebook')
notebook_med_cables.pack(fill=tk.BOTH, expand=True)

# Crear las pestañas con el color de fondo definido
frame_Med_MV_cables = tk.Frame(notebook_med_cables, background=blanco_roto)
frame_Med_LV_cables = tk.Frame(notebook_med_cables, background=blanco_roto)
frame_Med_AASS_cables = tk.Frame(notebook_med_cables, background=blanco_roto)

# Añadir las pestañas al notebook
notebook_med_cables.add(frame_Med_MV_cables, text='MV Cables')
notebook_med_cables.add(frame_Med_LV_cables, text='LV Cables')
notebook_med_cables.add(frame_Med_AASS_cables, text='AASS Cables')




#    FRAME CABLE MV
# Configurar la cuadrícula para partir el frame en dos verticales, una para asignacion de entradas y otra para calculos 
frame_Med_MV_cables.grid_rowconfigure(0, weight=1) #añadimos row para que se expanda hasta abajo
frame_Med_MV_cables.grid_columnconfigure(0, weight=1)  
frame_Med_MV_cables.grid_columnconfigure(1, weight=1)  

    #Creamos el de las entradas
frame_Med_MV_entradas =  tk.Frame(frame_Med_MV_cables, background=blanco_roto)
frame_Med_MV_entradas.grid(row=0, column=0, sticky='nsew', padx=50, pady=0)

    #Creamos el de los calculos
frame_Med_MV_calculos =  tk.Frame(frame_Med_MV_cables, background=blanco_roto)
frame_Med_MV_calculos.grid(row=0, column=1, sticky='nsew', padx=50, pady=0)





#    FRAME CABLE LV
# Configurar la cuadrícula para partir el frame en dos verticales, una para asignacion de entradas y otra para calculos 
frame_Med_LV_cables.grid_rowconfigure(0, weight=1) #añadimos row para que se expanda hasta abajo
frame_Med_LV_cables.grid_columnconfigure(0, weight=1)  
frame_Med_LV_cables.grid_columnconfigure(1, weight=1)  

    #Creamos el de las entradas
frame_Med_LV_entradas =  tk.Frame(frame_Med_LV_cables, background=blanco_roto)
frame_Med_LV_entradas.grid(row=0, column=0, sticky='nsew', padx=50, pady=0)

    #Creamos el de los calculos
frame_Med_LV_calculos =  tk.Frame(frame_Med_LV_cables, background=blanco_roto)
frame_Med_LV_calculos.grid(row=0, column=1, sticky='nsew', padx=50, pady=0)





# Creamos el frame para los criterios de mayoracion
frame_DCABLE_may = tk.Frame(frame_Med_LV_entradas, background=blanco_roto)
frame_DCABLE_may.grid(row=0, column=0, sticky='nsew', padx=50, pady=0)

    #Creamos la matriz que lo parta en dos para el cable solar/dcbus y el otro para el cable de array
frame_DCABLE_may.grid_rowconfigure(0, weight=1)
frame_DCABLE_may.grid_rowconfigure(1, weight=4)
# frame_DCABLE_may.grid_rowconfigure(2, weight=4)
# frame_DCABLE_may.grid_columnconfigure(0, weight=1)  

        #Añadimos el subframe del cable solar/dcbus arriba
frame_DCABLE_csb = tk.Frame(frame_DCABLE_may, background=gris_suave)
frame_DCABLE_csb.grid(row=0, column=0, sticky='new', padx=0, pady=0)
        #Creamos la matriz que lo parta en header mas dos filas para añadir luego dos subframes, uno para entradas geometricas y otro para secciones
frame_DCABLE_csb.grid_columnconfigure(0, weight=4)
frame_DCABLE_csb.grid_columnconfigure(1, weight=1)   
         #Añadimos los dos subframes 
frame_DCABLE_geom = tk.Frame(frame_DCABLE_csb, background=gris_suave)
frame_DCABLE_geom.grid(row=0, column=0, sticky='new', padx=0, pady=0)

frame_DCABLE_secciones = tk.Frame(frame_DCABLE_csb, background=gris_suave)
frame_DCABLE_secciones.grid(row=0, column=1, sticky='new', padx=0, pady=0)


        #Añadimos el subframe del cable de array abajo
frame_DCABLE_arr = tk.Frame(frame_DCABLE_may, background=gris_suave)
frame_DCABLE_arr.grid(row=1, column=0, sticky='new', padx=0, pady=(30,0))
        #Creamos la matriz que lo parta en header mas dos filas para añadir luego dos subframes, uno para entradas geometricas y otro para secciones
frame_DCABLE_arr.grid_columnconfigure(0, weight=4)
frame_DCABLE_arr.grid_columnconfigure(1, weight=1)  
         #Añadimos los dos subframes 
frame_DCABLE_arr_geom = tk.Frame(frame_DCABLE_arr, background=gris_suave)
frame_DCABLE_arr_geom.grid(row=0, column=0, sticky='new', padx=0, pady=0)

frame_DCABLE_arr_secciones = tk.Frame(frame_DCABLE_arr, background=gris_suave)
frame_DCABLE_arr_secciones.grid(row=0, column=1, sticky='new', padx=0, pady=0)


# Creamos el frame para los calculos de seccion
frame_DCABLE_calc = tk.Frame(frame_Med_LV_entradas, background=blanco_roto)
frame_DCABLE_calc.grid(row=1, column=0, sticky='', padx=0, pady=0)

    #Creamos la matriz que lo parta en dos columnas para añadir luego dos subframes, uno para el calculo local y otro para la afeccion a la planta
frame_DCABLE_calc.rowconfigure(0, weight=1)
frame_DCABLE_calc.columnconfigure(0, weight=1)  
frame_DCABLE_calc.columnconfigure(1, weight=2) 

        #Añadimos el subframe del calculo local
frame_DCABLE_calc_local = tk.Frame(frame_DCABLE_calc, background=blanco_roto)
frame_DCABLE_calc_local.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

        #Añadimos el subframe de la visualizacion a la derecha
frame_DCABLE_calc_vis = tk.Frame(frame_DCABLE_calc, background=blanco_roto)
frame_DCABLE_calc_vis.grid(row=0, column=1, sticky='nsew', padx=0, pady=0)









# LISTAR ENTRADAS MV

def entradas_medicion_cables_MV(valores_dados_MV):    
    global valor_slopes_trench_MV, valor_slack_MV, valor_transicion_PCS, valor_transicion_SS, valor_safety_maj_MV, entradas_asignacion_secciones_MV
    
        #Pendientes en zanja
    etiqueta_slopes_trench_MV = tk.Label(frame_Med_MV_entradas, text="Average slope (%)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_slopes_trench_MV.grid(row=0, column=0, padx=(10,0),pady=(15,15))
    valor_slopes_trench_MV = tk.StringVar()
    valor_slopes_trench_MV.set(valores_dados_MV[0])
    entrada_slopes_trench_MV = tk.Entry(frame_Med_MV_entradas, textvariable=valor_slopes_trench_MV, width=5)
    entrada_slopes_trench_MV.grid(row=0, column=1, padx=(5,20), pady=(15,15))
    
        #Slack cable
    etiqueta_slack_MV = tk.Label(frame_Med_MV_entradas, text="Slack (%)", fg=rojo_GRS,  bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_slack_MV.grid(row=1, column=0, pady=(10,0))
    valor_slack_MV = tk.StringVar()
    valor_slack_MV.set(valores_dados_MV[3])
    entrada_slack_MV = tk.Entry(frame_Med_MV_entradas, textvariable=valor_slack_MV, width=5)
    entrada_slack_MV.grid(row=1, column=1, padx=(5,20), pady=(10,0))

        #Transición zanja-PCS
    etiqueta_transicion_PCS = tk.Label(frame_Med_MV_entradas, text="Trench-PCS transition (m)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_transicion_PCS.grid(row=2, column=0, pady=(15,10))
    valor_transicion_PCS = tk.StringVar()
    valor_transicion_PCS.set(valores_dados_MV[2])
    entrada_transicion_PCS = tk.Entry(frame_Med_MV_entradas, textvariable=valor_transicion_PCS, width=5)
    entrada_transicion_PCS.grid(row=2, column=1, padx=(12,20), pady=(15,10))

        #Transición Subestacion
    etiqueta_transicion_SS = tk.Label(frame_Med_MV_entradas, text="Substation transition (m)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_transicion_SS.grid(row=3, column=0, pady=(10,0))
    valor_transicion_SS = tk.StringVar()
    valor_transicion_SS.set(valores_dados_MV[1])
    entrada_transicion_SS = tk.Entry(frame_Med_MV_entradas, textvariable=valor_transicion_SS, width=5)
    entrada_transicion_SS.grid(row=3, column=1, padx=(12,20), pady=(10,0))

        #Mayoracion de seguridad
    etiqueta_safety_maj_MV = tk.Label(frame_Med_MV_entradas, text="Safety margin (%)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_safety_maj_MV.grid(row=4, column=0, pady=(15,10))
    valor_safety_maj_MV = tk.StringVar()
    valor_safety_maj_MV.set(valores_dados_MV[4])
    entrada_safety_maj_MV = tk.Entry(frame_Med_MV_entradas, textvariable=valor_safety_maj_MV, width=5)
    entrada_safety_maj_MV.grid(row=4, column=1, padx=(5,20), pady=(15,10))    
    
    
    
    #ENTRADAS PARA SECCIONES - Creamos un canva donde se metan dos columnas y un radiobutton encima, 
    
        #Crear entradas
    entradas_asignacion_secciones_MV = []
    fila_actual_asignacion_MV = 1  # Fila 0 está ocupada por etiquetas

    def agregar_par_asignacion_secciones():
        global entradas_asignacion_secciones_MV, fila_actual_asignacion_MV
    
        # if not entradas_asignacion_secciones_MV:
        #     entradas_asignacion_secciones_MV.append([])
    
        entry1 = ttk.Entry(scrollable_frame_med_MV, width=15)
        entry1.grid(row=fila_actual_asignacion_MV, column=0, padx=5, pady=2)
    
        entry2 = ttk.Entry(scrollable_frame_med_MV, width=15)
        entry2.grid(row=fila_actual_asignacion_MV, column=1, padx=5, pady=2)
    
        entradas_asignacion_secciones_MV.append([entry1, entry2])
        fila_actual_asignacion_MV += 1


    
    def eliminar_ultimo_elemento_par():
        global entradas_asignacion_secciones_MV, fila_actual_asignacion_MV
    
        if not entradas_asignacion_secciones_MV:
            return
    
        if entradas_asignacion_secciones_MV[-1]:
            entrada_1, entrada_2 = entradas_asignacion_secciones_MV[-1].pop()
            entrada_1.destroy()
            entrada_2.destroy()
            fila_actual_asignacion_MV = max(1, fila_actual_asignacion_MV - 1)

                
    # Canvas con scroll
    canvas_med_MV = tk.Canvas(frame_Med_MV_entradas, height=250)
    scrollbar_med_MV = ttk.Scrollbar(frame_Med_MV_entradas, orient="vertical", command=canvas_med_MV.yview)
    scrollable_frame_med_MV = ttk.Frame(frame_Med_MV_entradas)
    
    config_label = ttk.Label(scrollable_frame_med_MV, text="Criteria")
    config_label.grid(row=0, column=0, padx=5, pady=5)
    section_label = ttk.Label(scrollable_frame_med_MV, text="Section")
    section_label.grid(row=0, column=1, padx=5, pady=5)
    
    # Actualizar región del scroll
    scrollable_frame_med_MV.bind("<Configure>",lambda e: canvas_med_MV.configure(scrollregion=canvas_med_MV.bbox("all")))

    canvas_frame_med_MV = canvas_med_MV.create_window((0, 0), window=scrollable_frame_med_MV, anchor="nw")
    canvas_med_MV.configure(yscrollcommand=scrollbar_med_MV.set)
    
    canvas_med_MV.grid(row=6, column=0, columnspan=2, sticky="ew")
    scrollbar_med_MV.grid(row=6, column=1, sticky="ns")
    
    ttk.Button(frame_Med_MV_entradas, text="Add Section", command=agregar_par_asignacion_secciones).grid(row=7, column=0, pady=10, padx=5)
    ttk.Button(frame_Med_MV_entradas, text="Remove Last", command=eliminar_ultimo_elemento_par).grid(row=7, column=1, pady=10, padx=5)
    
    
    
    #Cargar tramos si criterio de posicion
    def cargar_filas_seccion_por_posicion():
        global entradas_asignacion_secciones_MV, fila_actual_asignacion_MV
        fila_actual_asignacion_MV = 1
    
        # Calcular el número máximo de tramos entre todas las líneas
        max_tramos = max(len(linea[1:]) for linea in lineas_MV if linea != [0])
    
        for i in range(max_tramos):
            etiqueta = ttk.Label(scrollable_frame_med_MV, text=f"Pos {i+1}")
            etiqueta.grid(row=fila_actual_asignacion_MV, column=0, padx=5, pady=2)
    
            entrada = ttk.Entry(scrollable_frame_med_MV, width=10)
            entrada.grid(row=fila_actual_asignacion_MV, column=1, padx=5, pady=2)
    
            entradas_asignacion_secciones_MV.append(entrada)
            fila_actual_asignacion_MV += 1


    #Cargar potencias unicas acumuladas si criterio de potencia   
    def cargar_filas_seccion_por_potencia():
        global entradas_asignacion_secciones_MV, fila_actual_asignacion_MV
        fila_actual_asignacion_MV = 1
    
        # Extraer potencias únicas del tercer elemento de cada tramo
        potencias = set()
        for linea in lineas_MV:
            if linea == [0]:
                continue
            for tramo in linea[1:]:
                if len(tramo) >= 3:
                    try:
                        potencias.add(int(tramo[2]))
                    except ValueError:
                        pass  # ignora si no es convertible
    
        for pot in sorted(potencias):
            etiqueta = ttk.Label(scrollable_frame_med_MV, text=f"{pot} W")
            etiqueta.grid(row=fila_actual_asignacion_MV, column=0, padx=5, pady=2)
    
            entrada = ttk.Entry(scrollable_frame_med_MV, width=10)
            entrada.grid(row=fila_actual_asignacion_MV, column=1, padx=5, pady=2)
            
            entradas_asignacion_secciones_MV.append(entrada)    
            fila_actual_asignacion_MV += 1

    
    
    
    #Cargar lineas si criterio manual
    def cargar_lineas_MV_para_seccion():
        global fila_actual_MV, entradas_asignacion_secciones_MV, asignacion_secciones_MV
    
        fila_actual_MV = 1
        entradas_asignacion_secciones_MV = []
    
        for i, linea in enumerate(lineas_MV):
            if linea == [0]:
                continue
    
            tramos = linea[1:]
            entradas_linea = []
    
            for j, tramo in enumerate(tramos):
                val1, val2 = tramo[:2]
    
                # Etiqueta tipo "23 → 24"
                etiqueta = ttk.Label(scrollable_frame_med_MV, text=f"{val1} → {val2}")
                etiqueta.grid(row=fila_actual_MV, column=0, padx=5, pady=2, sticky="w")
    
                entrada = ttk.Entry(scrollable_frame_med_MV, width=10)
                entrada.grid(row=fila_actual_MV, column=1, padx=5, pady=2)
    
                try:
                    seccion_guardada = asignacion_secciones_MV[i][j+1]
                    if seccion_guardada not in ([], 0, None):
                        entrada.insert(0, str(seccion_guardada))
                except (IndexError, TypeError):
                    pass
    
                entradas_linea.append(entrada)
                fila_actual_MV += 1
    
            entradas_asignacion_secciones_MV.append(entradas_linea)


    
    
    #Radiobutton para elegir el criterio de seccion en cables de array
    def habilitar_entradas_segun_criterio_seccion_MV():
        global criterio_secciones_MV, fila_actual_asignacion_MV
    
        for widget in scrollable_frame_med_MV.winfo_children():
            widget.destroy()
    
        config_label = ttk.Label(scrollable_frame_med_MV, text="Criteria")
        config_label.grid(row=0, column=0, padx=5, pady=5)
        section_label = ttk.Label(scrollable_frame_med_MV, text="Section")
        section_label.grid(row=0, column=1, padx=5, pady=5)
    
        fila_actual_asignacion_MV = 1
    
        if var_criterio_seccion_MV.get() == 1:
            criterio_secciones_MV = 'Posicion'
            if lineas_MV:
                cargar_filas_seccion_por_posicion()
    
        elif var_criterio_seccion_MV.get() == 2:
            criterio_secciones_MV = 'Potencia'
            if lineas_MV:
                cargar_filas_seccion_por_potencia()
    
        elif var_criterio_seccion_MV.get() == 3:
            criterio_secciones_MV = 'Manual'
            if lineas_MV:
                cargar_lineas_MV_para_seccion()

        guardar_variables([criterio_secciones_MV],['criterio_secciones_MV'])
            
    var_criterio_seccion_MV = tk.IntVar()  # Sin habilitar marcador por defecto al iniciar

    if criterio_secciones_MV == 'Sin definir':
        pass
    elif criterio_secciones_MV == "Posicion":
        var_criterio_seccion_MV.set(1)
    elif criterio_secciones_MV == "Potencia":
        var_criterio_seccion_MV.set(2)
    elif criterio_secciones_MV == "Manual":
        var_criterio_seccion_MV.set(3)
    
    habilitar_entradas_segun_criterio_seccion_MV()        
    
    #Ponemos el radiobutton para cambios futuros
    radio_criterio_seccion_array_1 = ttk.Radiobutton(frame_Med_MV_entradas, text="Location", variable=var_criterio_seccion_MV, value=1, command=habilitar_entradas_segun_criterio_seccion_MV)
    radio_criterio_seccion_array_1.grid(row=5, column=0, padx=5, pady=5)
    radio_criterio_seccion_array_2 = ttk.Radiobutton(frame_Med_MV_entradas, text="Power", variable=var_criterio_seccion_MV, value=2, command=habilitar_entradas_segun_criterio_seccion_MV)
    radio_criterio_seccion_array_2.grid(row=5, column=1, padx=5, pady=5)
    radio_criterio_seccion_array_3 = ttk.Radiobutton(frame_Med_MV_entradas, text="Manual", variable=var_criterio_seccion_MV, value=3, command=habilitar_entradas_segun_criterio_seccion_MV)
    radio_criterio_seccion_array_3.grid(row=5, column=2, padx=5, pady=5)
 
    

    
criterio_secciones_MV='Sin definir'
valores_iniciales_MV=[[],[],[],[],[]]
entradas_medicion_cables_MV(valores_iniciales_MV)




#MEDIR CABLES MV

def leer_valores_par_criterio_seccion_MV():
    global slack_cable_MV, desnivel_cable_MV, transicion_MV_PCS, transicion_MV_SS, safety_maj_MV
    global asignacion_secciones_MV, secciones_MV

    # Leer entradas numéricas generales
    slack_cable_MV = float(valor_slack_MV.get())
    desnivel_cable_MV = float(valor_slopes_trench_MV.get())
    transicion_MV_PCS = float(valor_transicion_PCS.get())
    transicion_MV_SS = float(valor_transicion_SS.get())
    safety_maj_MV = float(valor_safety_maj_MV.get())

    asignacion_secciones_MV = [0]  # Dummy inicial

    if criterio_secciones_MV == 'Manual':
        for i, linea in enumerate(lineas_MV):
            if i == 0:
                continue
            else:
                asignacion_secciones_MV.append([])
            for j, tramo in enumerate(linea):
                asignacion_secciones_MV[i].append([])
                if j == 0:
                    continue
                              
                seccion = entradas_asignacion_secciones_MV[i - 1][j - 1].get()
                if seccion:
                    asignacion_secciones_MV[i][j]=int(seccion)
                    
        secciones_MV = np.sort(np.unique([int(x) for sublist in asignacion_secciones_MV[1:] for x in sublist if x != []]))
        
    else:
        for entrada in entradas_asignacion_secciones_MV:
            seccion = entrada.get()
            if seccion:
                asignacion_secciones_MV.append(int(seccion))
        secciones_MV = np.sort(np.unique([int(x) for x in asignacion_secciones_MV[1:]]))            

    guardar_variables([slack_cable_MV, desnivel_cable_MV, transicion_MV_PCS, transicion_MV_SS, safety_maj_MV, criterio_secciones_MV],['slack_cable_MV', 'desnivel_cable_MV', 'transicion_MV_PCS', 'transicion_MV_SS', 'safety_maj_MV', 'criterio_secciones_MV'])
    guardar_variables([asignacion_secciones_MV, secciones_MV], ['asignacion_secciones_MV', 'secciones_MV'])

    
def medir_cable_MV():
        
    def proceso_medicion_cable_MV():
        global lineas_MV
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:

            leer_valores_par_criterio_seccion_MV()
            lineas_MV = Algoritmo_IXPHOS_3_Cables.medicion_cable_MV(lineas_MV, pol_cable_MV, slack_cable_MV, desnivel_cable_MV, transicion_MV_PCS, transicion_MV_SS, safety_maj_MV)
            lineas_MV = Algoritmo_IXPHOS_3_Cables.asignacion_secciones_cable_MV(lineas_MV, criterio_secciones_MV, asignacion_secciones_MV)
                
            guardar_variables([lineas_MV],['lineas_MV'])

        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                  
    def cerrar_ventana_tras_medir_cable_MV(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
                
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_medir_cable_MV():
        proceso_medicion_cable_MV()
        root.after(0, lambda: cerrar_ventana_tras_medir_cable_MV(ventana_carga))
        
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_medir_cable_MV) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()



boton_medir_cable_MV = tk.Button(frame_Med_MV_entradas, text="Simulate", command=medir_cable_MV, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_medir_cable_MV.grid(row=8, column=0, pady=20)











#Listado de entradas y funciones asociadas para mostrarlas y leerlas

def listar_inputs_adicionales_dc_bus(valor_coca_dado, valor_primer_tracker_dado):
    global valor_coca, valor_primer_tracker, encabezado_cable_string, encabezado_DC_Bus
    # #añadimos una etiqueta blanco roto para tapar parte de la extension de la fila superior y que parezca que la tabla tiene una pestaña de titulo en la fila 0
    # ext_tapar_fila0= tk.Label(frame_DCABLE_csb, text='', bg=blanco_roto)
    # ext_tapar_fila0.grid(row=0, column=6, columnspan=2, sticky='e', padx=(0,0), pady=(0,0))
        #Añadimos un encabezado dcbus para las adicionales
    encabezado_DC_Bus= tk.Label(frame_DCABLE_geom, text="DC BUS specifica data", fg=rojo_GRS, bg=gris_fuerte, font=('Montserrat', 10, 'bold'))
    encabezado_DC_Bus.grid(row=3, column=0, sticky='nsew', padx=(10,10), pady=(7,0))
        #Coca en el ultimo tracker (al principio de la fila)
    etiqueta_coca = tk.Label(frame_DCABLE_geom, text="Turning excess in last tr.", fg=rojo_GRS, bg=blanco_roto, font=('Montserrat', 10, 'bold'))
    etiqueta_coca.grid(row=3, column=1, pady=(30,0))
    valor_coca = tk.StringVar()
    valor_coca.set(valor_coca_dado)
    entrada_coca = tk.Entry(frame_DCABLE_geom, textvariable=valor_coca, width=5)
    entrada_coca.grid(row=3, column=2, padx=(5,20), pady=(30,0))
        #Mayoracion de seguridad
    etiqueta_primer_tracker = tk.Label(frame_DCABLE_geom, text="Excess in first tr.", fg=rojo_GRS, bg=blanco_roto, font=('Montserrat', 10, 'bold'))
    etiqueta_primer_tracker.grid(row=3, column=3, pady=(15,15))
    valor_primer_tracker = tk.StringVar()
    valor_primer_tracker.set(valor_primer_tracker_dado)
    entrada_primer_tracker = tk.Entry(frame_DCABLE_geom, textvariable=valor_primer_tracker, width=5)
    entrada_primer_tracker.grid(row=3, column=4, padx=(5,20), pady=(15,15))    



def entradas_medicion_cables_subarray(valores_dados_subarray):
    global valor_sa_slopes_air, valor_sa_slopes_trench, valor_sa_transicion_tr, valor_sa_transicion_caja, valor_sa_slack, valor_sa_safety_maj
    
    #ENTRADAS GEOMETRICAS PARA MEDICION DE CABLE STRING/DCBUS
        #añadimos una etiqueta blanco roto para tapar parte de la fila superior y que parezca que la tabla tiene una pestaña de titulo en la fila 0
    tapar_fila0= tk.Label(frame_DCABLE_geom, bd=7, bg=blanco_roto)
    tapar_fila0.grid(row=0, column=1, columnspan=10, sticky='ew', padx=(0,0), pady=(0,0))
        #añadimos una etiqueta de encabezado
    encabezado_cable_string= tk.Label(frame_DCABLE_geom, text="SUBARRAY CABLE", fg=rojo_GRS, bg=gris_fuerte, font=('Montserrat', 10, 'bold'))
    encabezado_cable_string.grid(row=0, column=0, sticky='nsew', padx=(10,10), pady=(7,0))
        #Pendientes en el tracker
    etiqueta_slopes_air = tk.Label(frame_DCABLE_geom, text="Average slope - tracker (%)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_slopes_air.grid(row=1, column=0, padx=(10,0), pady=(10,0))
    valor_sa_slopes_air = tk.StringVar()
    valor_sa_slopes_air.set(valores_dados_subarray[0])
    entrada_slopes_air = tk.Entry(frame_DCABLE_geom, textvariable=valor_sa_slopes_air, width=5)
    entrada_slopes_air.grid(row=1, column=1, padx=(5,20), pady=(10,0))
        #Pendientes en zanja
    etiqueta_slopes_trench = tk.Label(frame_DCABLE_geom, text="Average slope - trench (%)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_slopes_trench.grid(row=2, column=0, padx=(10,0),pady=(15,10))
    valor_sa_slopes_trench = tk.StringVar()
    valor_sa_slopes_trench.set(valores_dados_subarray[1])
    entrada_slopes_trench = tk.Entry(frame_DCABLE_geom, textvariable=valor_sa_slopes_trench, width=5)
    entrada_slopes_trench.grid(row=2, column=1, padx=(5,20), pady=(15,10))
        #Transición tracker-zanja
    etiqueta_transicion_tracker = tk.Label(frame_DCABLE_geom, text="Tracker-trench transition (m)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_transicion_tracker.grid(row=1, column=2, pady=(10,0))
    valor_sa_transicion_tr = tk.StringVar()
    valor_sa_transicion_tr.set(valores_dados_subarray[2])
    entrada_transicion_tracker = tk.Entry(frame_DCABLE_geom, textvariable=valor_sa_transicion_tr, width=5)
    entrada_transicion_tracker.grid(row=1, column=3, padx=(5,20), pady=(10,0))
        #Transición zanja-caja
    etiqueta_transicion_caja = tk.Label(frame_DCABLE_geom, text="Trench-DCBox/SI transition (m)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_transicion_caja.grid(row=2, column=2, pady=(15,10))
    valor_sa_transicion_caja = tk.StringVar()
    valor_sa_transicion_caja.set(valores_dados_subarray[3])
    entrada_transicion_caja = tk.Entry(frame_DCABLE_geom, textvariable=valor_sa_transicion_caja, width=5)
    entrada_transicion_caja.grid(row=2, column=3, padx=(5,20), pady=(15,10))
        #Slack cable
    etiqueta_slack = tk.Label(frame_DCABLE_geom, text="Slack (%)", fg=rojo_GRS,  bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_slack.grid(row=1, column=4, pady=(10,0))
    valor_sa_slack = tk.StringVar()
    valor_sa_slack.set(valores_dados_subarray[4])
    entrada_slack = tk.Entry(frame_DCABLE_geom, textvariable=valor_sa_slack, width=5)
    entrada_slack.grid(row=1, column=5, padx=(5,20), pady=(10,0))
        #Mayoracion de seguridad
    etiqueta_safety_maj = tk.Label(frame_DCABLE_geom, text="Safety margin (%)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_safety_maj.grid(row=2, column=4, pady=(15,10))
    valor_sa_safety_maj = tk.StringVar()
    valor_sa_safety_maj.set(valores_dados_subarray[5])
    entrada_safety_maj = tk.Entry(frame_DCABLE_geom, textvariable=valor_sa_safety_maj, width=5)
    entrada_safety_maj.grid(row=2, column=5, padx=(5,20), pady=(15,10))    
    
    
    #ENTRADAS PARA SECCIONES DE CABLE DE STRING/DCBUS
    global valor_sa_sld1, valor_sa_sld2, valor_sa_loc1, valor_sa_loc2, valor_sa_s1, valor_sa_s2, valor_sa_s3, var_criterio_seccion_string
        #Limites de seccion por distancia cable de string
    etiqueta_seccion_str_SL_Distance = tk.Label(frame_DCABLE_secciones, text="SL Distance", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_seccion_str_SL_Distance.grid(row=0, column=1, pady=(15,10))
    valor_sa_sld1 = tk.StringVar()
    valor_sa_sld1.set(valores_dados_subarray[6])
    entrada_seccion_str_SL_Distance_1 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_sld1, width=5)
    entrada_seccion_str_SL_Distance_1.grid(row=0, column=2, padx=(5,5), pady=(15,10))   
    valor_sa_sld2 = tk.StringVar()
    valor_sa_sld2.set(valores_dados_subarray[7])
    entrada_seccion_str_SL_Distance_2 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_sld2, width=5)
    entrada_seccion_str_SL_Distance_2.grid(row=0, column=3, padx=(5,5), pady=(15,10))   
        #Limites de seccion por localizacion cable de string
    etiqueta_seccion_str_location = tk.Label(frame_DCABLE_secciones, text="Location of string in row", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_seccion_str_location.grid(row=1, column=1, pady=(15,10))
    valor_sa_loc1 = tk.StringVar()
    valor_sa_loc1.set(valores_dados_subarray[8])
    entrada_seccion_str_location_1 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_loc1, width=5)
    entrada_seccion_str_location_1.grid(row=1, column=2, padx=(5,5), pady=(15,10))   
    valor_sa_loc2 = tk.StringVar()
    valor_sa_loc2.set(valores_dados_subarray[9])
    entrada_seccion_str_location_2 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_loc2, width=5)
    entrada_seccion_str_location_2.grid(row=1, column=3, padx=(5,5), pady=(15,10))   
        #Secciones de cable de string
    etiqueta_seccion_str = tk.Label(frame_DCABLE_secciones, text="String Cable Cross-sections", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_seccion_str.grid(row=2, column=1, pady=(15,10))
    valor_sa_s1 = tk.StringVar()
    valor_sa_s1.set(valores_dados_subarray[10])
    entrada_seccion_str_1 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_s1, width=5)
    entrada_seccion_str_1.grid(row=2, column=2, padx=(5,5), pady=(15,10)) 
    valor_sa_s2 = tk.StringVar()
    valor_sa_s2.set(valores_dados_subarray[11])
    entrada_seccion_str_2 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_s2, width=5)
    entrada_seccion_str_2.grid(row=2, column=3, padx=(5,5), pady=(15,10))
    valor_sa_s3 = tk.StringVar()
    valor_sa_s3.set(valores_dados_subarray[12])    
    entrada_seccion_str_3 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_s3, width=5)
    entrada_seccion_str_3.grid(row=2, column=4, padx=(5,5), pady=(15,10))
    
    #Radiobutton para elegir el criterio de seccion en cables de string
    def habilitar_entradas_segun_criterio_seccion_string():        
        if var_criterio_seccion_string.get() == 1:
            entrada_seccion_str_SL_Distance_1.config(state='normal')
            entrada_seccion_str_SL_Distance_2.config(state='normal')
            entrada_seccion_str_location_1.config(state='disabled')
            entrada_seccion_str_location_2.config(state='disabled')
        elif var_criterio_seccion_string.get() == 2:
            entrada_seccion_str_SL_Distance_1.config(state='disabled')
            entrada_seccion_str_SL_Distance_2.config(state='disabled')
            entrada_seccion_str_location_1.config(state='normal')
            entrada_seccion_str_location_2.config(state='normal')

    
    var_criterio_seccion_string = tk.IntVar(value = valor_marcador_str)  
    habilitar_entradas_segun_criterio_seccion_string()
            
    radio_criterio_seccion_string_1 = ttk.Radiobutton(frame_DCABLE_secciones, text="", variable=var_criterio_seccion_string, value=1, command=habilitar_entradas_segun_criterio_seccion_string)
    radio_criterio_seccion_string_1.grid(row=0, column=0, padx=5, pady=5)
    radio_criterio_seccion_string_2 = ttk.Radiobutton(frame_DCABLE_secciones, text="", variable=var_criterio_seccion_string, value=2, command=habilitar_entradas_segun_criterio_seccion_string)
    radio_criterio_seccion_string_2.grid(row=1, column=0, padx=5, pady=5)
    
        #Limites de seccion por distancia DC_Bus
    global valor_sa_dcb_sld1, valor_sa_dcb_sld2, valor_sa_dcb_loc1, valor_sa_dcb_loc2, valor_sa_dcb_s1, valor_sa_dcb_s2, valor_sa_dcb_s3, var_criterio_seccion_dcbus
    
    etiqueta_seccion_dcb_SL_Distance = tk.Label(frame_DCABLE_secciones, text="SL Distance", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_seccion_dcb_SL_Distance.grid(row=3, column=1, pady=(15,10))
    valor_sa_dcb_sld1 = tk.StringVar()
    valor_sa_dcb_sld1.set(valores_dados_subarray[13])
    entrada_seccion_dcb_SL_Distance_1 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_dcb_sld1, width=5)
    entrada_seccion_dcb_SL_Distance_1.grid(row=3, column=2, padx=(5,5), pady=(15,10))
    valor_sa_dcb_sld2 = tk.StringVar()
    valor_sa_dcb_sld2.set(valores_dados_subarray[14])
    entrada_seccion_dcb_SL_Distance_2 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_dcb_sld2, width=5)
    entrada_seccion_dcb_SL_Distance_2.grid(row=3, column=3, padx=(5,5), pady=(15,10))   
        #Limites de seccion por numero de strings en DC_Bus
    etiqueta_seccion_dcb_location = tk.Label(frame_DCABLE_secciones, text="No. strings in DC Bus", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_seccion_dcb_location.grid(row=4, column=1, pady=(15,10))
    valor_sa_dcb_loc1 = tk.StringVar()
    valor_sa_dcb_loc1.set(valores_dados_subarray[15])
    entrada_seccion_dcb_location_1 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_dcb_loc1, width=5)
    entrada_seccion_dcb_location_1.grid(row=4, column=2, padx=(5,5), pady=(15,10)) 
    valor_sa_dcb_loc2 = tk.StringVar()
    valor_sa_dcb_loc2.set(valores_dados_subarray[16])
    entrada_seccion_dcb_location_2 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_dcb_loc2, width=5)
    entrada_seccion_dcb_location_2.grid(row=4, column=3, padx=(5,5), pady=(15,10))   
        #Secciones de DC_Bus
    etiqueta_seccion_dcb = tk.Label(frame_DCABLE_secciones, text="DC Bus Cross-sections", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_seccion_dcb.grid(row=5, column=1, pady=(15,10))
    valor_sa_dcb_s1 = tk.StringVar()
    valor_sa_dcb_s1.set(valores_dados_subarray[17])
    entrada_seccion_dcb_1 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_dcb_s1, width=5)
    entrada_seccion_dcb_1.grid(row=5, column=2, padx=(5,5), pady=(15,10)) 
    valor_sa_dcb_s2 = tk.StringVar()
    valor_sa_dcb_s2.set(valores_dados_subarray[18])
    entrada_seccion_dcb_2 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_dcb_s2, width=5)
    entrada_seccion_dcb_2.grid(row=5, column=3, padx=(5,5), pady=(15,10)) 
    valor_sa_dcb_s3 = tk.StringVar()
    valor_sa_dcb_s3.set(valores_dados_subarray[19])
    entrada_seccion_dcb_3 = tk.Entry(frame_DCABLE_secciones, textvariable=valor_sa_dcb_s3, width=5)
    entrada_seccion_dcb_3.grid(row=5, column=4, padx=(5,5), pady=(15,10))

    #Radiobutton para elegir el criterio de seccion en cables de string
    def habilitar_entradas_segun_criterio_seccion_dcbus():  
        if var_criterio_seccion_dcbus.get() == 1:
            entrada_seccion_dcb_SL_Distance_1.config(state='normal')
            entrada_seccion_dcb_SL_Distance_2.config(state='normal')
            entrada_seccion_dcb_location_1.config(state='disabled')
            entrada_seccion_dcb_location_2.config(state='disabled')
        else:
            entrada_seccion_dcb_SL_Distance_1.config(state='disabled')
            entrada_seccion_dcb_SL_Distance_2.config(state='disabled')
            entrada_seccion_dcb_location_1.config(state='normal')
            entrada_seccion_dcb_location_2.config(state='normal')
    
    var_criterio_seccion_dcbus = tk.IntVar(value = valor_marcador_dcbus)  # No habilitar ninguna por defecto hasta que se seleccione
    habilitar_entradas_segun_criterio_seccion_dcbus()
    
    radio_criterio_seccion_dcbus_1 = ttk.Radiobutton(frame_DCABLE_secciones, text="", variable=var_criterio_seccion_dcbus, value=1, command=habilitar_entradas_segun_criterio_seccion_dcbus)
    radio_criterio_seccion_dcbus_1.grid(row=3, column=0, padx=5, pady=5)
    radio_criterio_seccion_dcbus_2 = ttk.Radiobutton(frame_DCABLE_secciones, text="", variable=var_criterio_seccion_dcbus, value=2, command=habilitar_entradas_segun_criterio_seccion_dcbus)
    radio_criterio_seccion_dcbus_2.grid(row=4, column=0, padx=5, pady=5)




#Inicializamos las entradas vacias para cuando se empieza el proyecto
valores_iniciales_subarray=[[],[],[],[],[], [],[],[],[],[], [],[],[],[],[], [],[],[],[],[]]
valor_marcador_str=1 #esta entrada de marcador la inicializamos en 1 cuando se crea el proyecto, pero si se modifica y se guarda se mantendra modificada al cargarse
valor_marcador_dcbus=1 #esta entrada de marcador la inicializamos en 1 cuando se crea el proyecto, pero si se modifica y se guarda se mantendra modificada al cargarse



#TODO
desplaz_x_cable_modulos=2 #LO DEJAMOS METIDO AQUI POR DEFECTO, SIN QUE LO MODIFIQUE EL USUARIO, ES EL LLEVARLOS DESDE LA JB AL TORQUE TUBE EN LAS UNIONES Y LUEGO OTRA VEZ A LA MITAD DEL MODULO

    
    
    
    
    
    #ENTRADAS PARA MEDICION DE CABLE DE ARRAY
        #añadimos una etiqueta blanco roto para tapar parte de la fila superior y que parezca que la tabla tiene una pestaña de titulo en la fila 0
def listar_uni_o_multipolar(var_com_uni_o_multipolar):
    global var_array_uni_o_multipolar
    #Combobox para cable de array unipolar o multipolar
    unipolar_o_multipolar_options = ["Single core", "Multicore"]
    var_array_uni_o_multipolar = tk.StringVar(value = var_com_uni_o_multipolar)
    
    etiqueta_uom = tk.Label(frame_DCABLE_arr_geom, fg=rojo_GRS, text='Cable type', font=('Montserrat', 10, 'bold'))
    etiqueta_uom.grid(row=3, column=4)
    combobox_uom = ttk.Combobox(frame_DCABLE_arr_geom, textvariable=var_array_uni_o_multipolar, values=unipolar_o_multipolar_options)
    combobox_uom.grid(row=3, column=5, pady=(5,0))

         
def entradas_medicion_cables_array(valores_dados_array):    
    global valor_slopes_trench_LV, valor_transicion_caja_LV, valor_transicion_PCS, valor_slack_arr, valor_safety_maj_arr, valor_sld1_arr, valor_loc1_arr, valor_s1_arr, valor_s2_arr, var_criterio_seccion_array, var_mat_array
    
    tapar_fila0= tk.Label(frame_DCABLE_arr_geom, bd=7, bg=blanco_roto)
    tapar_fila0.grid(row=0, column=1, columnspan=10, sticky='ew', padx=(0,0), pady=(0,0))
        #añadimos una etiqueta de encabezado
    encabezado_cable_arr= tk.Label(frame_DCABLE_arr_geom, text="ARRAY CABLE", fg=rojo_GRS, bg=gris_fuerte, font=('Montserrat', 10, 'bold'))
    encabezado_cable_arr.grid(row=0, column=0, sticky='nsew', padx=(10,10), pady=(7,0))
        #Pendientes en zanja
    etiqueta_slopes_trench_LV = tk.Label(frame_DCABLE_arr_geom, text="Average slope - trench (%)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_slopes_trench_LV.grid(row=1, column=0, rowspan=2, padx=(10,0),pady=(15,15))
    valor_slopes_trench_LV = tk.StringVar()
    valor_slopes_trench_LV.set(valores_dados_array[0])
    entrada_slopes_trench_LV = tk.Entry(frame_DCABLE_arr_geom, textvariable=valor_slopes_trench_LV, width=5)
    entrada_slopes_trench_LV.grid(row=1, column=1, rowspan=2, padx=(5,20), pady=(15,15))
        #Transición caja-zanja
    etiqueta_transicion_caja_LV = tk.Label(frame_DCABLE_arr_geom, text="DCBox/SI-trench transition (m)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_transicion_caja_LV.grid(row=1, column=2, pady=(10,0))
    valor_transicion_caja_LV = tk.StringVar()
    valor_transicion_caja_LV.set(valores_dados_array[1])
    entrada_transicion_caja_LV = tk.Entry(frame_DCABLE_arr_geom, textvariable=valor_transicion_caja_LV, width=5)
    entrada_transicion_caja_LV.grid(row=1, column=3, padx=(12,20), pady=(10,0))
        #Transición zanja-PCS
    etiqueta_transicion_PCS = tk.Label(frame_DCABLE_arr_geom, text="Trench-PCS transition (m)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_transicion_PCS.grid(row=2, column=2, pady=(15,10))
    valor_transicion_PCS = tk.StringVar()
    valor_transicion_PCS.set(valores_dados_array[2])
    entrada_transicion_PCS = tk.Entry(frame_DCABLE_arr_geom, textvariable=valor_transicion_PCS, width=5)
    entrada_transicion_PCS.grid(row=2, column=3, padx=(12,20), pady=(15,10))
        #Slack cable
    etiqueta_slack_arr = tk.Label(frame_DCABLE_arr_geom, text="Slack (%)", fg=rojo_GRS,  bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_slack_arr.grid(row=1, column=4, pady=(10,0))
    valor_slack_arr = tk.StringVar()
    valor_slack_arr.set(valores_dados_array[3])
    entrada_slack_arr = tk.Entry(frame_DCABLE_arr_geom, textvariable=valor_slack_arr, width=5)
    entrada_slack_arr.grid(row=1, column=5, padx=(5,20), pady=(10,0))
        #Mayoracion de seguridad
    etiqueta_safety_maj_arr = tk.Label(frame_DCABLE_arr_geom, text="Safety margin (%)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_safety_maj_arr.grid(row=2, column=4, pady=(15,10))
    valor_safety_maj_arr = tk.StringVar()
    valor_safety_maj_arr.set(valores_dados_array[4])
    entrada_safety_maj_arr = tk.Entry(frame_DCABLE_arr_geom, textvariable=valor_safety_maj_arr, width=5)
    entrada_safety_maj_arr.grid(row=2, column=5, padx=(5,20), pady=(15,10))    
    
    #Combobox para material
    opciones_mat_array = ['Al','Cu']
    var_mat_array = tk.StringVar(value = valores_dados_array[9])
    
    etiqueta_mat_array = tk.Label(frame_DCABLE_arr_geom, text='Array Cable Material', fg=rojo_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_mat_array.grid(row=3, column=2)
    combobox_mat_array=ttk.Combobox(frame_DCABLE_arr_geom, textvariable=var_mat_array, values=opciones_mat_array)
    combobox_mat_array.grid(row=3, column=3)
    
    #ENTRADAS PARA SECCIONES DE CABLE DE ARRAY    
        #Limites de seccion por distancia cable de array
    etiqueta_seccion_array_SL_Distance = tk.Label(frame_DCABLE_arr_secciones, text="SL Distance", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_seccion_array_SL_Distance.grid(row=0, column=1, pady=(15,10))
    valor_sld1_arr = tk.StringVar()
    valor_sld1_arr.set(valores_dados_array[5])
    entrada_seccion_array_SL_Distance_1 = tk.Entry(frame_DCABLE_arr_secciones, textvariable=valor_sld1_arr, width=5)
    entrada_seccion_array_SL_Distance_1.grid(row=0, column=2, padx=(5,5), pady=(15,10))   
        #Limites de seccion por localizacion cable de array
    etiqueta_seccion_array_location = tk.Label(frame_DCABLE_arr_secciones, text="No. strings border (<=)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_seccion_array_location.grid(row=1, column=1, pady=(15,10))
    valor_loc1_arr = tk.StringVar()
    valor_loc1_arr.set(valores_dados_array[6])
    entrada_seccion_array_location_1 = tk.Entry(frame_DCABLE_arr_secciones, textvariable=valor_loc1_arr, width=5)
    entrada_seccion_array_location_1.grid(row=1, column=2, padx=(5,5), pady=(15,10))   
 
        #Secciones de cable de array
    etiqueta_seccion_array = tk.Label(frame_DCABLE_arr_secciones, text="Array Cable Cross-sections", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_seccion_array.grid(row=2, column=1, pady=(15,10))
    valor_s1_arr = tk.StringVar()
    valor_s1_arr.set(valores_dados_array[7])
    entrada_seccion_array_1 = tk.Entry(frame_DCABLE_arr_secciones, textvariable=valor_s1_arr, width=5)
    entrada_seccion_array_1.grid(row=2, column=2, padx=(5,5), pady=(15,10))
    valor_s2_arr = tk.StringVar()
    valor_s2_arr.set(valores_dados_array[8])
    entrada_seccion_array_2 = tk.Entry(frame_DCABLE_arr_secciones, textvariable=valor_s2_arr, width=5)
    entrada_seccion_array_2.grid(row=2, column=3, padx=(5,5), pady=(15,10))

    
    #Radiobutton para elegir el criterio de seccion en cables de array
    def habilitar_entradas_segun_criterio_seccion_array():
        if var_criterio_seccion_array.get() == 1:
            entrada_seccion_array_SL_Distance_1.config(state='normal')
            entrada_seccion_array_location_1.config(state='disabled')

        elif var_criterio_seccion_array.get() == 2:
            entrada_seccion_array_SL_Distance_1.config(state='disabled')
            entrada_seccion_array_location_1.config(state='normal')

    
    var_criterio_seccion_array = tk.IntVar(value = valor_marcador_array)  # Sin habilitar marcador por defecto al iniciar
    habilitar_entradas_segun_criterio_seccion_array()

            
    radio_criterio_seccion_array_1 = ttk.Radiobutton(frame_DCABLE_arr_secciones, text="", variable=var_criterio_seccion_array, value=1, command=habilitar_entradas_segun_criterio_seccion_array)
    radio_criterio_seccion_array_1.grid(row=0, column=0, padx=5, pady=5)
    radio_criterio_seccion_array_2 = ttk.Radiobutton(frame_DCABLE_arr_secciones, text="", variable=var_criterio_seccion_array, value=2, command=habilitar_entradas_segun_criterio_seccion_array)
    radio_criterio_seccion_array_2.grid(row=1, column=0, padx=5, pady=5)
    
valores_iniciales_array=[[],[],[],[],[], [],[],[],[],[]]
valor_marcador_array = 1
  
    




#---------------SIMULACION DE MEDICIONES DE CABLE---------------------------

def devolver_entero(entrada):
    return int(entrada) if entrada.strip() else 0

def devolver_float(entrada):
    return float(entrada) if entrada.strip() else 0

def leer_valores_GUI_cable_string():
    global desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, mayoracion_cable_subarray
    global criterio_seccion_cs, lim_dist_sld_cs_seccion, lim_loc_cs_seccion, secciones_cs
    global mayoracion_tubo_corrugado_DC    
    
    #leemos las entradas geometricas
    desnivel_cable_por_pendientes_tramo_aereo=devolver_float(valor_sa_slopes_air.get()) 
    desnivel_cable_por_pendientes_tramo_subt=devolver_float(valor_sa_slopes_trench.get()) 
    
    transicion_cable_subarray_tracker=devolver_float(valor_sa_transicion_tr.get()) 
    transicion_cable_subarray_caja=devolver_float(valor_sa_transicion_caja.get())
    
    slack_cable_subarray=devolver_float(valor_sa_slack.get()) 
    mayoracion_cable_subarray=devolver_float(valor_sa_safety_maj.get()) 
    
    #leemos las entradas de seccion
    if var_criterio_seccion_string.get() == 1:
        criterio_seccion_cs = 'Distance'
    else:
        criterio_seccion_cs = 'No. strings'
        
    seccion_str_SL_Distance_1 = devolver_entero(valor_sa_sld1.get())
    seccion_str_SL_Distance_2 = devolver_entero(valor_sa_sld2.get())
    seccion_str_location_1 = devolver_entero(valor_sa_loc1.get())
    seccion_str_location_2 = devolver_entero(valor_sa_loc2.get())
    seccion_str_1 = devolver_entero(valor_sa_s1.get())
    seccion_str_2 = devolver_entero(valor_sa_s2.get())
    seccion_str_3 = devolver_entero(valor_sa_s3.get())
   

    lim_dist_sld_cs_seccion = [seccion_str_SL_Distance_1, seccion_str_SL_Distance_2]
    lim_loc_cs_seccion = [seccion_str_location_1, seccion_str_location_2]
    secciones_cs = [seccion_str_1, seccion_str_2, seccion_str_3]
    mayoracion_tubo_corrugado_DC = devolver_float(valor_safety_maj_dc_conduit.get())
    
    #Guardar variables en el dicionario
    guardar_variables([desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, mayoracion_cable_subarray],['desnivel_cable_por_pendientes_tramo_aereo', 'desnivel_cable_por_pendientes_tramo_subt', 'transicion_cable_subarray_tracker', 'transicion_cable_subarray_caja', 'slack_cable_subarray', 'mayoracion_cable_subarray'])
    guardar_variables([criterio_seccion_cs, seccion_str_SL_Distance_1, seccion_str_SL_Distance_2, seccion_str_location_1, seccion_str_location_2, seccion_str_1, seccion_str_2, seccion_str_3],['criterio_seccion_cs', 'seccion_str_SL_Distance_1', 'seccion_str_SL_Distance_2', 'seccion_str_location_1', 'seccion_str_location_2', 'seccion_str_1', 'seccion_str_2', 'seccion_str_3'])
    guardar_variables([lim_dist_sld_cs_seccion, lim_loc_cs_seccion, secciones_cs],['lim_dist_sld_cs_seccion', 'lim_loc_cs_seccion', 'secciones_cs'])
    guardar_variables([mayoracion_tubo_corrugado_DC],['mayoracion_tubo_corrugado_DC'])


def leer_valores_GUI_DC_Bus():
    global desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, mayoracion_cable_subarray, coca_DC_Bus, extension_primer_tracker
    global criterio_seccion_dcb, lim_dist_sld_dcb_seccion, lim_loc_dcb_seccion, secciones_dcb
    global mayoracion_tubo_corrugado_DC    
        

    global valor_sa_dcb_sld1, valor_sa_dcb_sld2, valor_sa_dcb_loc1, valor_sa_dcb_loc2, valor_sa_dcb_s1, valor_sa_dcb_s2, valor_sa_dcb_s3, var_criterio_seccion_dcbus
    
    #leemos las entradas previas
    desnivel_cable_por_pendientes_tramo_aereo=devolver_float(valor_sa_slopes_air.get()) 
    desnivel_cable_por_pendientes_tramo_subt=devolver_float(valor_sa_slopes_trench.get()) 
    
    transicion_cable_subarray_tracker=devolver_float(valor_sa_transicion_tr.get()) 
    transicion_cable_subarray_caja=devolver_float(valor_sa_transicion_caja.get())
    
    slack_cable_subarray=devolver_float(valor_sa_slack.get()) 
    mayoracion_cable_subarray=devolver_float(valor_sa_safety_maj.get()) 
    
    coca_DC_Bus=devolver_float(valor_coca.get())
    extension_primer_tracker=devolver_float(valor_primer_tracker.get())    
    
    #leemos las entradas de seccion
    if var_criterio_seccion_dcbus.get() == 1:
        criterio_seccion_dcb = 'Distance'
    else:
        criterio_seccion_dcb = 'No. strings'

    seccion_dcb_SL_Distance_1 = devolver_entero(valor_sa_dcb_sld1.get())
    seccion_dcb_SL_Distance_2 = devolver_entero(valor_sa_dcb_sld2.get())
    seccion_dcb_location_1 = devolver_entero(valor_sa_dcb_loc1.get())
    seccion_dcb_location_2 = devolver_entero(valor_sa_dcb_loc2.get())
    seccion_dcb_1 = devolver_entero(valor_sa_dcb_s1.get())
    seccion_dcb_2 = devolver_entero(valor_sa_dcb_s2.get())
    seccion_dcb_3 = devolver_entero(valor_sa_dcb_s3.get())
       
    lim_dist_sld_dcb_seccion = [seccion_dcb_SL_Distance_1, seccion_dcb_SL_Distance_2]
    lim_loc_dcb_seccion = [seccion_dcb_location_1, seccion_dcb_location_2]
    secciones_dcb = [seccion_dcb_1, seccion_dcb_2, seccion_dcb_3]
    
    mayoracion_tubo_corrugado_DC = devolver_float(valor_safety_maj_dc_conduit.get())
    
    #Guardamos las variables en el diccionario
    guardar_variables([desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, mayoracion_cable_subarray, coca_DC_Bus, extension_primer_tracker],['desnivel_cable_por_pendientes_tramo_aereo', 'desnivel_cable_por_pendientes_tramo_subt', 'transicion_cable_subarray_tracker', 'transicion_cable_subarray_caja', 'slack_cable_subarray', 'mayoracion_cable_subarray', 'coca_DC_Bus', 'extension_primer_tracker'])
    guardar_variables([criterio_seccion_dcb, seccion_dcb_SL_Distance_1, seccion_dcb_SL_Distance_2, seccion_dcb_location_1, seccion_dcb_location_2, seccion_dcb_1, seccion_dcb_2, seccion_dcb_3],['criterio_seccion_dcb','seccion_dcb_SL_Distance_1', 'seccion_dcb_SL_Distance_2', 'seccion_dcb_location_1', 'seccion_dcb_location_2', 'seccion_dcb_1', 'seccion_dcb_2', 'seccion_dcb_3'])
    guardar_variables([lim_dist_sld_dcb_seccion, lim_loc_dcb_seccion, secciones_dcb],['lim_dist_sld_dcb_seccion', 'lim_loc_dcb_seccion', 'secciones_dcb'])
    guardar_variables([mayoracion_tubo_corrugado_DC],['mayoracion_tubo_corrugado_DC'])
    
    
def leer_valores_GUI_opciones_mixtas():
    global desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, mayoracion_cable_subarray, coca_DC_Bus, extension_primer_tracker
    global criterio_seccion_cs, criterio_seccion_dcb, lim_dist_sld_cs_seccion, lim_loc_cs_seccion, secciones_cs, lim_dist_sld_dcb_seccion, lim_loc_dcb_seccion, secciones_dcb
    global mayoracion_tubo_corrugado_DC
    
    #leemos las entradas previas
    desnivel_cable_por_pendientes_tramo_aereo=devolver_float(valor_sa_slopes_air.get()) 
    desnivel_cable_por_pendientes_tramo_subt=devolver_float(valor_sa_slopes_trench.get()) 
    
    transicion_cable_subarray_tracker=devolver_float(valor_sa_transicion_tr.get()) 
    transicion_cable_subarray_caja=devolver_float(valor_sa_transicion_caja.get())
    
    slack_cable_subarray=devolver_float(valor_sa_slack.get()) 
    mayoracion_cable_subarray=devolver_float(valor_sa_safety_maj.get()) 
    
    coca_DC_Bus=devolver_float(valor_coca.get())
    extension_primer_tracker=devolver_float(valor_primer_tracker.get())    

    #leemos las entradas de seccion
    if var_criterio_seccion_string.get() == 1:
        criterio_seccion_cs = 'Distance'
    else:
        criterio_seccion_cs = 'No. strings'
        
    if var_criterio_seccion_dcbus.get() == 1:
        criterio_seccion_dcb = 'Distance'
    else:
        criterio_seccion_dcb = 'No. strings'
    

    
    seccion_str_SL_Distance_1 = devolver_entero(valor_sa_sld1.get())
    seccion_str_SL_Distance_2 = devolver_entero(valor_sa_sld2.get())
    seccion_str_location_1 = devolver_entero(valor_sa_loc1.get())
    seccion_str_location_2 = devolver_entero(valor_sa_loc2.get())
    seccion_str_1 = devolver_entero(valor_sa_s1.get())
    seccion_str_2 = devolver_entero(valor_sa_s2.get())
    seccion_str_3 = devolver_entero(valor_sa_s3.get())
    
    seccion_dcb_SL_Distance_1 = devolver_entero(valor_sa_dcb_sld1.get())
    seccion_dcb_SL_Distance_2 = devolver_entero(valor_sa_dcb_sld2.get())
    seccion_dcb_location_1 = devolver_entero(valor_sa_dcb_loc1.get())
    seccion_dcb_location_2 = devolver_entero(valor_sa_dcb_loc2.get())
    seccion_dcb_1 = devolver_entero(valor_sa_dcb_s1.get())
    seccion_dcb_2 = devolver_entero(valor_sa_dcb_s2.get())
    seccion_dcb_3 = devolver_entero(valor_sa_dcb_s3.get())

    lim_dist_sld_cs_seccion = [seccion_str_SL_Distance_1, seccion_str_SL_Distance_2]
    lim_loc_cs_seccion = [seccion_str_location_1, seccion_str_location_2]
    secciones_cs = [seccion_str_1, seccion_str_2, seccion_str_3]
    
    lim_dist_sld_dcb_seccion = [seccion_dcb_SL_Distance_1, seccion_dcb_SL_Distance_2]
    lim_loc_dcb_seccion = [seccion_dcb_location_1, seccion_dcb_location_2]
    secciones_dcb = [seccion_dcb_1, seccion_dcb_2, seccion_dcb_3]
    
    
    mayoracion_tubo_corrugado_DC = devolver_float(valor_safety_maj_dc_conduit.get())

    #Guardar variables en el dicionario
    guardar_variables([desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, mayoracion_cable_subarray, coca_DC_Bus, extension_primer_tracker],['desnivel_cable_por_pendientes_tramo_aereo', 'desnivel_cable_por_pendientes_tramo_subt', 'transicion_cable_subarray_tracker', 'transicion_cable_subarray_caja', 'slack_cable_subarray', 'mayoracion_cable_subarray', 'coca_DC_Bus', 'extension_primer_tracker'])
    guardar_variables([criterio_seccion_cs, seccion_str_SL_Distance_1, seccion_str_SL_Distance_2, seccion_str_location_1, seccion_str_location_2, seccion_str_1, seccion_str_2, seccion_str_3, criterio_seccion_dcb, seccion_dcb_SL_Distance_1, seccion_dcb_SL_Distance_2, seccion_dcb_location_1, seccion_dcb_location_2, seccion_dcb_1, seccion_dcb_2, seccion_dcb_3],['criterio_seccion_cs', 'seccion_str_SL_Distance_1', 'seccion_str_SL_Distance_2', 'seccion_str_location_1', 'seccion_str_location_2', 'seccion_str_1', 'seccion_str_2', 'seccion_str_3', 'criterio_seccion_dcb','seccion_dcb_SL_Distance_1', 'seccion_dcb_SL_Distance_2', 'seccion_dcb_location_1', 'seccion_dcb_location_2', 'seccion_dcb_1', 'seccion_dcb_2', 'seccion_dcb_3'])
    guardar_variables([lim_dist_sld_cs_seccion, lim_loc_cs_seccion, secciones_cs, lim_dist_sld_dcb_seccion, lim_loc_dcb_seccion, secciones_dcb],['lim_dist_sld_cs_seccion', 'lim_loc_cs_seccion', 'secciones_cs', 'lim_dist_sld_dcb_seccion', 'lim_loc_dcb_seccion', 'secciones_dcb'])
    guardar_variables([mayoracion_tubo_corrugado_DC],['mayoracion_tubo_corrugado_DC'])

def medicion_cables_subarray():
        
    def proceso_medicion_cables_subarray():
        global med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg
        global med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg, med_tubo_corrugado_zanja_DC
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            if String_o_Bus == 'String Cable':
                leer_valores_GUI_cable_string()
                med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_zanja_DC = Algoritmo_IXPHOS_3_Cables.medicion_cable_string(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_c_block, masc, max_inv_block, max_str_pinv, max_p, DCBoxes_o_Inv_String, strings_fisicos, strings_ID, pol_cable_string, equi_ibfs, Interconexionado, Polo_cercano, ancho_modulo, saliente_TT, desplaz_x_cable_modulos, dist_ext_opuesto_str, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, mayoracion_cable_subarray, mayoracion_tubo_corrugado_DC, criterio_seccion_cs, lim_dist_sld_cs_seccion, lim_loc_cs_seccion, secciones_cs, filas_con_cable_string, dos_inv_por_bloque, cajas_fisicas)
         
                guardar_variables([med_inst_cable_string_pos, tramo_aereo_cable_string_pos,med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_zanja_DC],['med_inst_cable_string_pos','tramo_aereo_cable_string_pos','med_inst_cable_string_neg','med_cable_string_pos', 'med_cable_string_neg', 'sch_cable_de_string_pos', 'sch_cable_de_string_neg', 'med_tubo_corrugado_zanja_DC' ])
                
            elif String_o_Bus == 'DC Bus':
                leer_valores_GUI_DC_Bus()
                med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg, med_tubo_corrugado_zanja_DC = Algoritmo_IXPHOS_3_Cables.medicion_DC_Bus(bloque_inicial,n_bloques, max_b, max_f_str_b, max_p, max_c_block, max_bus, filas_en_cajas, pol_DC_Bus, equi_ibfs ,Interconexionado, Polo_cercano, dist_ext_opuesto_str, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, coca_DC_Bus, extension_primer_tracker, slack_cable_subarray, mayoracion_cable_subarray, mayoracion_tubo_corrugado_DC, criterio_seccion_dcb, lim_dist_sld_dcb_seccion, lim_loc_dcb_seccion, secciones_dcb, extender_DC_Bus, filas_con_dcb_extendido, filas_con_cable_string, dos_inv_por_bloque, cajas_fisicas)
                

                guardar_variables([med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg, med_tubo_corrugado_zanja_DC],['med_inst_DC_Bus_pos', 'med_inst_DC_Bus_neg', 'med_DC_Bus_pos', 'tramo_aereo_DC_Bus_pos', 'med_DC_Bus_neg', 'sch_DC_Bus_pos', 'sch_DC_Bus_neg', 'med_tubo_corrugado_zanja_DC'])
                    
            elif String_o_Bus == 'Both types':
                leer_valores_GUI_opciones_mixtas()
                med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_str_zanja_DC = Algoritmo_IXPHOS_3_Cables.medicion_cable_string(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_c_block, masc, max_inv_block, max_str_pinv, max_p, DCBoxes_o_Inv_String, strings_fisicos, strings_ID, pol_cable_string, equi_ibfs, Interconexionado, Polo_cercano, ancho_modulo, saliente_TT, desplaz_x_cable_modulos, dist_ext_opuesto_str, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, mayoracion_cable_subarray, mayoracion_tubo_corrugado_DC, criterio_seccion_cs, lim_dist_sld_cs_seccion, lim_loc_cs_seccion, secciones_cs, filas_con_cable_string, dos_inv_por_bloque, cajas_fisicas)
                med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg, med_tubo_corrugado_dcbus_zanja_DC = Algoritmo_IXPHOS_3_Cables.medicion_DC_Bus(bloque_inicial,n_bloques, max_b, max_f_str_b, max_p, max_c_block, max_bus, filas_en_cajas, pol_DC_Bus, equi_ibfs ,Interconexionado, Polo_cercano, dist_ext_opuesto_str, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, coca_DC_Bus, extension_primer_tracker, slack_cable_subarray, mayoracion_cable_subarray, mayoracion_tubo_corrugado_DC, criterio_seccion_dcb, lim_dist_sld_dcb_seccion, lim_loc_dcb_seccion, secciones_dcb, extender_DC_Bus, filas_con_dcb_extendido, filas_con_cable_string, dos_inv_por_bloque, cajas_fisicas)
                med_tubo_corrugado_zanja_DC = np.where(np.isnan(med_tubo_corrugado_str_zanja_DC), med_tubo_corrugado_dcbus_zanja_DC, med_tubo_corrugado_str_zanja_DC)
                
                guardar_variables([med_inst_cable_string_pos, tramo_aereo_cable_string_pos,med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_zanja_DC],['med_inst_cable_string_pos','tramo_aereo_cable_string_pos','med_inst_cable_string_neg','med_cable_string_pos', 'med_cable_string_neg', 'sch_cable_de_string_pos', 'sch_cable_de_string_neg', 'med_tubo_corrugado_zanja_DC'])
                guardar_variables([med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg],['med_inst_DC_Bus_pos', 'med_inst_DC_Bus_neg', 'med_DC_Bus_pos', 'tramo_aereo_DC_Bus_pos', 'med_DC_Bus_neg', 'sch_DC_Bus_pos', 'sch_DC_Bus_neg'])


            elif String_o_Bus == 'Mixed':
                leer_valores_GUI_opciones_mixtas()
                med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_zanja_DC = Algoritmo_IXPHOS_3_Cables.medicion_cable_string(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_c_block, masc, max_inv_block, max_str_pinv, max_p, DCBoxes_o_Inv_String, strings_fisicos, strings_ID, pol_cable_string, equi_ibfs, Interconexionado, Polo_cercano, ancho_modulo, saliente_TT, desplaz_x_cable_modulos, dist_ext_opuesto_str, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, mayoracion_cable_subarray, mayoracion_tubo_corrugado_DC, criterio_seccion_cs, lim_dist_sld_cs_seccion, lim_loc_cs_seccion, secciones_cs, filas_con_cable_string, dos_inv_por_bloque, cajas_fisicas)
                med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg, med_tubo_corrugado_dcbus_zanja_DC = Algoritmo_IXPHOS_3_Cables.medicion_DC_Bus(bloque_inicial,n_bloques, max_b, max_f_str_b, max_p, max_c_block, max_bus, filas_en_cajas, pol_DC_Bus, equi_ibfs ,Interconexionado, Polo_cercano, dist_ext_opuesto_str, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, coca_DC_Bus, extension_primer_tracker, slack_cable_subarray, mayoracion_cable_subarray, mayoracion_tubo_corrugado_DC, criterio_seccion_dcb, lim_dist_sld_dcb_seccion, lim_loc_dcb_seccion, secciones_dcb, extender_DC_Bus, filas_con_dcb_extendido, filas_con_cable_string, dos_inv_por_bloque, cajas_fisicas)
                
                
                guardar_variables([med_inst_cable_string_pos, tramo_aereo_cable_string_pos,med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_zanja_DC],['med_inst_cable_string_pos','tramo_aereo_cable_string_pos','med_inst_cable_string_neg','med_cable_string_pos', 'med_cable_string_neg', 'sch_cable_de_string_pos', 'sch_cable_de_string_neg','med_tubo_corrugado_zanja_DC'])
                guardar_variables([med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg],['med_inst_DC_Bus_pos', 'med_inst_DC_Bus_neg', 'med_DC_Bus_pos', 'tramo_aereo_DC_Bus_pos', 'med_DC_Bus_neg', 'sch_DC_Bus_pos', 'sch_DC_Bus_neg'])
    
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                  
    def cerrar_ventana_tras_medir_subarrays(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
                
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_medir_subarrays():
        proceso_medicion_cables_subarray()
        root.after(0, lambda: cerrar_ventana_tras_medir_subarrays(ventana_carga))
        
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_medir_subarrays) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()




boton_array_CAD_read = tk.Button(frame_DCABLE_geom, text="Simulate", command=medicion_cables_subarray, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_array_CAD_read.grid(row=2, column=7, pady=20)







#------------MEDIR CABLE DE ARRAY

def leer_valores_GUI_cable_array():
    global desnivel_cable_array_por_pendientes, transicion_array_cable_caja, transicion_array_cable_PCS, uni_o_multipolar, slack_array_cable, mayoracion_array_cable, lim_dist_array_sld_seccion, lim_n_str_array_seccion, criterio_seccion_array, secciones_array, material_array
    
    #leemos las entradas previas
    desnivel_cable_array_por_pendientes=devolver_float(valor_slopes_trench_LV.get()) 
    
    transicion_array_cable_caja=devolver_float(valor_transicion_caja_LV.get())
    transicion_array_cable_PCS=devolver_float(valor_transicion_PCS.get())
    
    slack_array_cable=devolver_float(valor_slack_arr.get()) 
    mayoracion_array_cable=devolver_float(valor_safety_maj_arr.get()) 
    
    
    #leemos las entradas de seccion y material
    if var_criterio_seccion_array.get() == 1:
        criterio_seccion_array = 'Distance'
    else:
        criterio_seccion_array = 'No. strings'
        
    material_array = var_mat_array.get()
        
    if DCBoxes_o_Inv_String == 'String Inverters':
        if var_array_uni_o_multipolar.get() == 'Single core':
            uni_o_multipolar=3
        else:
            uni_o_multipolar=1
    else:
       uni_o_multipolar=1
    
    lim_dist_array_sld_seccion = devolver_entero(valor_sld1_arr.get())
    lim_n_str_array_seccion = devolver_entero(valor_loc1_arr.get())
    seccion_array_1 = devolver_entero(valor_s1_arr.get())
    seccion_array_2 = devolver_entero(valor_s2_arr.get())

    secciones_array = [seccion_array_1, seccion_array_2]
        
    #Guardar variables en el dicionario
    guardar_variables([desnivel_cable_array_por_pendientes, transicion_array_cable_caja, transicion_array_cable_PCS, slack_array_cable, mayoracion_array_cable, uni_o_multipolar, criterio_seccion_array, lim_dist_array_sld_seccion, lim_n_str_array_seccion, seccion_array_1, seccion_array_2, secciones_array, material_array],['desnivel_cable_array_por_pendientes', 'transicion_array_cable_caja', 'transicion_array_cable_PCS', 'slack_array_cable', 'mayoracion_array_cable', 'uni_o_multipolar', 'criterio_seccion_array', 'lim_dist_array_sld_seccion', 'lim_n_str_array_seccion', 'seccion_array_1', 'seccion_array_2', 'secciones_array', 'material_array'])



def medicion_cable_array():
        
    def proceso_medicion_cable_array():
        global med_inst_array_cable_pos, med_inst_array_cable_neg, med_array_cable_pos, med_array_cable_neg, med_array_cable, med_inst_array_cable, sch_array_cable_pos, sch_array_cable_neg, sch_array_cable
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            leer_valores_GUI_cable_array()
            
            if DCBoxes_o_Inv_String == 'DC Boxes':
                med_inst_array_cable_pos, med_inst_array_cable_neg, med_array_cable_pos, med_array_cable_neg, med_array_cable, med_inst_array_cable, sch_array_cable_pos, sch_array_cable_neg, sch_array_cable = Algoritmo_IXPHOS_3_Cables.medicion_array(bloque_inicial, n_bloques, DCBoxes_o_Inv_String, max_b, max_c, max_c_block, cajas_fisicas, pol_array_cable, equi_ibc, desnivel_cable_array_por_pendientes, transicion_array_cable_caja, transicion_array_cable_PCS, uni_o_multipolar, slack_array_cable, mayoracion_array_cable, lim_dist_array_sld_seccion, lim_n_str_array_seccion, criterio_seccion_array, secciones_array)
            else:
                med_inst_array_cable_pos, med_inst_array_cable_neg, med_array_cable_pos, med_array_cable_neg, med_array_cable, med_inst_array_cable, sch_array_cable_pos, sch_array_cable_neg, sch_array_cable = Algoritmo_IXPHOS_3_Cables.medicion_array(bloque_inicial, n_bloques, DCBoxes_o_Inv_String, max_b, max_inv, max_inv_block, inv_como_cajas_fisicas, pol_array_cable, equi_ibv, desnivel_cable_array_por_pendientes, transicion_array_cable_caja, transicion_array_cable_PCS, uni_o_multipolar, slack_array_cable, mayoracion_array_cable, lim_dist_array_sld_seccion, lim_n_str_array_seccion, criterio_seccion_array, secciones_array)               
            
            
            guardar_variables([med_inst_array_cable_pos, med_inst_array_cable_neg, med_array_cable_pos, med_array_cable_neg, med_array_cable, med_inst_array_cable, sch_array_cable_pos, sch_array_cable_neg, sch_array_cable],['med_inst_array_cable_pos', 'med_inst_array_cable_neg', 'med_array_cable_pos', 'med_array_cable_neg', 'med_array_cable', 'med_inst_array_cable', 'sch_array_cable_pos', 'sch_array_cable_neg', 'sch_array_cable'])
            

        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                  
    def cerrar_ventana_tras_medir_arrays(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
                
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_medir_arrays():
        proceso_medicion_cable_array()
        root.after(0, lambda: cerrar_ventana_tras_medir_arrays(ventana_carga))
        
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_medir_arrays) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()



boton_array_CAD_read = tk.Button(frame_DCABLE_arr_secciones, text="Simulate", command=medicion_cable_array, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_array_CAD_read.grid(row=2, column=5, pady=20)





#-----CUADRO PARA CALCULO 
#     #Seccion
# etiqueta_calc_seccion = tk.Label(frame_DCABLE_calc_local, text="Cross section", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
# etiqueta_calc_seccion.grid(row=0, column=0, padx=(5,5),pady=(0,10))
# entrada_calc_seccion = tk.Entry(frame_DCABLE_calc_local, width=5)
# entrada_calc_seccion.grid(row=0, column=1, padx=(0,5), pady=(0,10))
#     #Material
# etiqueta_calc_mat = tk.Label(frame_DCABLE_calc_local, text="Material", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
# etiqueta_calc_mat.grid(row=1, column=0, padx=(5,5),pady=(0,10))
# entrada_calc_mat = tk.Entry(frame_DCABLE_calc_local, width=5)
# entrada_calc_mat.grid(row=1, column=1, padx=(0,5), pady=(0,10))
#     #Intensidad
# etiqueta_calc_int = tk.Label(frame_DCABLE_calc_local, text="Current (A)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
# etiqueta_calc_int.grid(row=2, column=0, padx=(5,5),pady=(0,10))
# entrada_calc_int = tk.Entry(frame_DCABLE_calc_local, width=5)
# entrada_calc_int.grid(row=2, column=1, padx=(0,5), pady=(0,10))
#     #Fases
# etiqueta_calc_fases = tk.Label(frame_DCABLE_calc_local, text="Phases", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
# etiqueta_calc_fases.grid(row=3, column=0, padx=(5,5),pady=(0,10))
# entrada_calc_fases = tk.Entry(frame_DCABLE_calc_local, width=5)
# entrada_calc_fases.grid(row=3, column=1, padx=(0,5), pady=(0,10))

# def update_values():
#     if var.get() == 1:
#         entry2.config(state='disabled')
#         entry1.config(state='normal')
#         value2.set(value1.get() * 2)  # Ejemplo de cálculo
#     elif var.get() == 2:
#         entry1.config(state='disabled')
#         entry2.config(state='normal')
#         value1.set(value2.get() / 2)  # Ejemplo de cálculo
#     else:
#         entry1.config(state='normal')
#         entry2.config(state='normal')

# var = tk.IntVar(value=1)  # Habilitar Marcador 1 por defecto

# radio1 = ttk.Radiobutton(frame_DCABLE_calc_local, text="Cable length", variable=var, value=1, command=update_values)
# radio1.grid(row=1, column=4, padx=5, pady=5)

# radio2 = ttk.Radiobutton(frame_DCABLE_calc_local, text="% Power losses", variable=var, value=2, command=update_values)
# radio2.grid(row=2, column=4, padx=5, pady=5)

# value1 = tk.DoubleVar()
# value2 = tk.DoubleVar()

# entry1 = ttk.Entry(frame_DCABLE_calc_local, textvariable=value1)
# entry1.grid(row=1, column=5, padx=5, pady=5)

# entry2 = ttk.Entry(frame_DCABLE_calc_local, textvariable=value2)
# entry2.grid(row=2, column=5, padx=5, pady=5)

# update_values()  # Actualizar valores al inicio


valores_iniciales_perdidas = [[],[],[],[]]

def entradas_calculo_perdidas(valores_dados_perdidas):    
    global valor_bif, valor_int_STC, valor_power_STC, valor_subarray_temp, valor_array_temp
    
    #Bifacialidad
    etiqueta_bif = tk.Label(frame_DCABLE_calc_local, text="Bifaciality (%)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_bif.grid(row=0, column=0, padx=(5,5),pady=(0,10))
    valor_bif = tk.StringVar()
    valor_bif.set(valores_dados_perdidas[0])
    entrada_bif = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_bif, width=5)
    entrada_bif.grid(row=0, column=1, padx=(0,5), pady=(0,10))
    
    #Intensidad MPP del modulo en STC
    etiqueta_int_STC = tk.Label(frame_DCABLE_calc_local, text="Impp STC (A)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_int_STC.grid(row=1, column=0, padx=(5,5),pady=(0,10))
    valor_int_STC = tk.StringVar()
    valor_int_STC.set(valores_dados_perdidas[1])
    entrada_int_STC = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_int_STC, width=5)
    entrada_int_STC.grid(row=1, column=1, padx=(0,5), pady=(0,10))
    
    #Potencia MPP del modulo en STC
    etiqueta_power_STC = tk.Label(frame_DCABLE_calc_local, text="Power STC (Wp)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_power_STC.grid(row=2, column=0, padx=(5,5),pady=(0,10))
    valor_power_STC = tk.StringVar()
    valor_power_STC.set(valores_dados_perdidas[2])
    entrada_power_STC = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_power_STC, width=5)
    entrada_power_STC.grid(row=2, column=1, padx=(0,5), pady=(0,10))
    
    #Temperatura del cable de subarray para el calculo
    etiqueta_subarray_temp = tk.Label(frame_DCABLE_calc_local, text="Subarray cable temp (ºC)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_subarray_temp.grid(row=3, column=0, padx=(10,0),pady=(10,5))
    valor_subarray_temp = tk.StringVar()
    valor_subarray_temp.set(valores_dados_perdidas[3])
    entrada_subarray_temp = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_subarray_temp, width=5)
    entrada_subarray_temp.grid(row=3, column=1, padx=(5,20), pady=(10,5))

    #Temperatura del cable de array para el calculo
    etiqueta_array_temp = tk.Label(frame_DCABLE_calc_local, text="Array cable temp (ºC)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_array_temp.grid(row=4, column=0, padx=(10,0),pady=(10,5))
    valor_array_temp = tk.StringVar()
    valor_array_temp.set(valores_dados_perdidas[4])
    entrada_array_temp = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_array_temp, width=5)
    entrada_array_temp.grid(row=4, column=1, padx=(5,20), pady=(10,5))
    
    
    #-----------------------------Si es AC------------------------
    if DCBoxes_o_Inv_String == 'String Inverters':
        global valor_pot_inv, valor_cos_phi, valor_v_inv, valor_X_cable
        
        #Potencia activa inversor
        etiqueta_pot_inv = tk.Label(frame_DCABLE_calc_local, text="Active Power Inv (W)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
        etiqueta_pot_inv.grid(row=0, column=2, padx=(10,0),pady=(10,5))
        valor_pot_inv = tk.StringVar()
        valor_pot_inv.set(valores_dados_perdidas[5])
        entrada_pot_inv = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_pot_inv, width=10)
        entrada_pot_inv.grid(row=0, column=3, padx=(5,20), pady=(10,5))
        
        #Coseno de phi
        etiqueta_cos_phi = tk.Label(frame_DCABLE_calc_local, text="Cos Phi", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
        etiqueta_cos_phi.grid(row=1, column=2, padx=(10,0),pady=(10,5))
        valor_cos_phi = tk.StringVar()
        valor_cos_phi.set(valores_dados_perdidas[6])
        entrada_cos_phi = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_cos_phi, width=5)
        entrada_cos_phi.grid(row=1, column=3, padx=(5,20), pady=(10,5))
        
        #Tension nominal inversor
        etiqueta_v_inv = tk.Label(frame_DCABLE_calc_local, text="Nominal Voltage Inv (V)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
        etiqueta_v_inv.grid(row=2, column=2, padx=(10,0),pady=(10,5))
        valor_v_inv = tk.StringVar()
        valor_v_inv.set(valores_dados_perdidas[7])
        entrada_v_inv = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_v_inv, width=5)
        entrada_v_inv.grid(row=2, column=3, padx=(5,20), pady=(10,5))
        
        #Reactancia del cable de array
        etiqueta_X_cable = tk.Label(frame_DCABLE_calc_local, text="Cable Reactance (mOhm/m)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
        etiqueta_X_cable.grid(row=3, column=2, padx=(10,0),pady=(10,5))
        valor_X_cable = tk.StringVar()
        valor_X_cable.set(valores_dados_perdidas[8])
        entrada_X_cable = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_X_cable, width=5)
        entrada_X_cable.grid(row=3, column=3, padx=(5,20), pady=(10,5))
        

    
    
def leer_valores_GUI_calculo_perdidas():
    global bifaciality, int_mod_STC, power_mod_STC, subarray_temp, array_temp
    
    #leemos las entradas previas
    bifaciality=float(valor_bif.get()) 
    int_mod_STC=float(valor_int_STC.get()) 
    power_mod_STC=float(valor_power_STC.get())  
    subarray_temp=float(valor_subarray_temp.get()) 
    array_temp=float(valor_array_temp.get())
    
    if DCBoxes_o_Inv_String == 'String Inverters':
        global pot_inv, cos_phi, v_inv, X_cable
        pot_inv=float(valor_pot_inv.get())
        cos_phi=float(valor_cos_phi.get())
        v_inv=float(valor_v_inv.get())
        X_cable=float(valor_X_cable.get())
        
        #Guardar variables en el dicionario
        guardar_variables([pot_inv, cos_phi, v_inv, X_cable],['pot_inv', 'cos_phi', 'v_inv', 'X_cable'])

        
    #Guardar variables en el dicionario
    guardar_variables([bifaciality, int_mod_STC, power_mod_STC, subarray_temp, array_temp],['bifaciality', 'int_mod_STC', 'power_mod_STC', 'subarray_temp', 'array_temp'])


def _fmt_pct(val):
    """Devuelve 'N/A' si no es numérico o es NaN; si es numérico -> 'xx.xx'."""
    if isinstance(val, str):
        return val
    try:
        v = float(val)
        if np.isnan(v):
            return "N/A"
        return f"{v:.2f}"
    except Exception:
        return "N/A"

def _asegurar_frame_resumen():
    """Crea el contenedor de la tabla si no existe."""
    global frame_tabla_resumen_perdidas
    try:
        frame_tabla_resumen_perdidas  # ya existe
    except NameError:
        # parent explícito: frame_DCABLE_calc_vis (como pediste)
        # ajusta fila/columna según tu layout
        frame_tabla_resumen_perdidas = tk.Frame(frame_DCABLE_calc_vis, bg=gris_suave, bd=0, highlightthickness=0)
        frame_tabla_resumen_perdidas.grid(row=0, column=3, rowspan=10, padx=20, pady=5, sticky="n")


def mostrar_tabla_resumen_perdidas(
    max_perdidas_cable_string,
    media_perdidas_cable_string,
    max_perdidas_DC_Bus,
    media_perdidas_DC_Bus,
    media_perdidas_subarray,
    max_perdidas_array,
    media_perdidas_array,
    media_perdidas_DC,
    max_cdt_array,
    media_cdt_array
):
    _asegurar_frame_resumen()

    # Limpiar contenido previo
    for w in frame_tabla_resumen_perdidas.winfo_children():
        w.destroy()

    # Cabecera general
    tk.Label(frame_tabla_resumen_perdidas, text="Losses and Voltage Drop Summary",
             bg=gris_suave, fg=rojo_GRS, font=('Montserrat', 9, 'bold')
    ).grid(row=0, column=0, columnspan=6, pady=(0,6), sticky="w")

    # Helper fila
    def fila(r, c, texto, valor):
        tk.Label(frame_tabla_resumen_perdidas, text=texto,
                 bg=gris_suave, font=('Montserrat', 8)
        ).grid(row=r, column=c, padx=(2,4), pady=1, sticky="w")

        tk.Label(frame_tabla_resumen_perdidas, text=_fmt_pct(valor),
                 bg=gris_suave, font=('Montserrat', 8, 'bold')
        ).grid(row=r, column=c+1, pady=1, sticky="e")

    # --- Bloque 1: String Cable + DC Bus ---
    col1 = 0
    row = 1
    tk.Label(frame_tabla_resumen_perdidas, text="String Cable",
             bg=gris_suave, fg="#444", font=('Montserrat', 8, 'bold', 'underline')
    ).grid(row=row, column=col1, columnspan=2, sticky="w"); row += 1
    fila(row, col1, "Máx. [%]",  max_perdidas_cable_string); row += 1
    fila(row, col1, "Media [%]", media_perdidas_cable_string); row += 1

    tk.Label(frame_tabla_resumen_perdidas, text="DC Bus",
             bg=gris_suave, fg="#444", font=('Montserrat', 8, 'bold', 'underline')
    ).grid(row=row, column=col1, columnspan=2, sticky="w"); row += 1
    fila(row, col1, "Máx. [%]",  max_perdidas_DC_Bus); row += 1
    fila(row, col1, "Media [%]", media_perdidas_DC_Bus); row += 2  # espacio extra entre bloques

    # --- Bloque 2: Subarray + Array ---
    col2 = 3
    row = 1
    tk.Label(frame_tabla_resumen_perdidas, text="Subarray",
             bg=gris_suave, fg="#444", font=('Montserrat', 8, 'bold', 'underline')
    ).grid(row=row, column=col2, columnspan=2, sticky="w"); row += 1
    fila(row, col2, "Media [%]", media_perdidas_subarray); row += 2

    tk.Label(frame_tabla_resumen_perdidas, text="Array",
             bg=gris_suave, fg="#444", font=('Montserrat', 8, 'bold', 'underline')
    ).grid(row=row, column=col2, columnspan=2, sticky="w"); row += 1
    fila(row, col2, "Máx. [%]",  max_perdidas_array); row += 1
    fila(row, col2, "Media [%]", media_perdidas_array); row += 2

    # --- Bloque 3: Total DC ---
    col3 = 6
    row = 1
    tk.Label(frame_tabla_resumen_perdidas, text="DC Losses",
             bg=gris_suave, fg=rojo_GRS, font=('Montserrat', 9, 'bold', 'underline')
    ).grid(row=row, column=col3, columnspan=2, sticky="w"); row += 1
    fila(row, col3, "Media [%]", media_perdidas_DC); row += 2
    
    tk.Label(frame_tabla_resumen_perdidas, text="Array ΔV",
             bg=gris_suave, fg=rojo_GRS, font=('Montserrat', 8, 'bold', 'underline')
    ).grid(row=row, column=col3, columnspan=2, sticky="w"); row += 1
    fila(row, col3, "Máx. [%]",       max_cdt_array); row += 1
    fila(row, col3, "Media [%]",      media_cdt_array); row += 2
    



def calcular_perdidas_cables():
    def proceso_calculo_perdidas():
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            global perdidas_cables_string, perdidas_DC_Bus, perdidas_array, pot_string_STC, cdt_array
            
            leer_valores_GUI_calculo_perdidas()
            pot_string_STC = [power_mod_STC * n_mods_serie for _ in range(n_bloques+1)] #temporalmente consideramos que la potencia de los string es identica en todos los bloques (misma potencia de modulo en cada bloque, sin sorting)
            if String_o_Bus == 'String Cable':
                perdidas_cables_string = np.full(sch_cable_de_string_pos.shape[:-1] + (2,), np.nan, dtype=float)
                perdidas_cables_string = Algoritmo_IXPHOS_3_Cables.calculo_perdidas_cables_string(strings_fisicos,bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, perdidas_cables_string, equi_ibfs, med_inst_cable_string_pos, med_inst_cable_string_neg, pot_string_STC, filas_con_cable_string, int_mod_STC, subarray_temp, DCBoxes_o_Inv_String, strings_ID)

                guardar_variables([perdidas_cables_string],['perdidas_cables_string'])
                
            elif String_o_Bus == 'DC Bus':
                perdidas_DC_Bus = np.full(sch_DC_Bus_pos.shape[:-1] + (2,), np.nan, dtype=float)
                perdidas_DC_Bus = Algoritmo_IXPHOS_3_Cables.calculo_perdidas_DC_Bus(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, perdidas_DC_Bus, equi_ibfs, pot_string_STC, filas_con_cable_string, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, long_string, int_mod_STC, subarray_temp, med_inst_DC_Bus_pos, tramo_aereo_DC_Bus_pos, strings_fisicos, slack_cable_subarray, desnivel_cable_por_pendientes_tramo_aereo)

                guardar_variables([perdidas_DC_Bus],['perdidas_DC_Bus'])
   
            else:
                perdidas_cables_string = np.full(sch_cable_de_string_pos.shape[:-1] + (2,), np.nan, dtype=float)
                perdidas_DC_Bus = np.full(sch_DC_Bus_pos.shape[:-1] + (2,), np.nan, dtype=float)
                
                perdidas_cables_string = Algoritmo_IXPHOS_3_Cables.calculo_perdidas_cables_string(strings_fisicos,bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, perdidas_cables_string, equi_ibfs, med_inst_cable_string_pos, med_inst_cable_string_neg, pot_string_STC, filas_con_cable_string, int_mod_STC, subarray_temp, DCBoxes_o_Inv_String, strings_ID)
                perdidas_DC_Bus = Algoritmo_IXPHOS_3_Cables.calculo_perdidas_DC_Bus(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, perdidas_DC_Bus, equi_ibfs, pot_string_STC, filas_con_cable_string, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, long_string, int_mod_STC, subarray_temp, med_inst_DC_Bus_pos, tramo_aereo_DC_Bus_pos, strings_fisicos, slack_cable_subarray, desnivel_cable_por_pendientes_tramo_aereo)
                
                guardar_variables([perdidas_cables_string,perdidas_DC_Bus],['perdidas_cables_string', 'perdidas_DC_Bus'])
           
             
            perdidas_array = np.full(sch_array_cable_pos.shape[:-1] + (2,), np.nan, dtype=float) if DCBoxes_o_Inv_String == 'DC Boxes' else np.full(sch_array_cable.shape[:-1] + (2,), np.nan, dtype=float)
            

            if DCBoxes_o_Inv_String == 'DC Boxes':
                cdt_array = None
                perdidas_array, cdt_array = Algoritmo_IXPHOS_3_Cables.calculo_perdidas_array(bloque_inicial,n_bloques, max_b, max_c, DCBoxes_o_Inv_String, cajas_fisicas, equi_ibc, med_array_cable_pos, med_array_cable_neg, med_array_cable, uni_o_multipolar, int_mod_STC, array_temp, perdidas_array, pot_string_STC, cdt_array, pot_inv, cos_phi, v_inv, X_cable, material_array)
            else:
                cdt_array = np.full(sch_array_cable.shape[:-1] + (2,), np.nan, dtype=float)
                perdidas_array, cdt_array = Algoritmo_IXPHOS_3_Cables.calculo_perdidas_array(bloque_inicial,n_bloques, max_b, max_inv, DCBoxes_o_Inv_String, inv_como_cajas_fisicas, equi_ibv, med_array_cable_pos, med_array_cable_neg, med_array_cable, uni_o_multipolar, int_mod_STC, array_temp, perdidas_array, pot_string_STC, cdt_array, pot_inv, cos_phi, v_inv, X_cable, material_array)

            guardar_variables([perdidas_array, cdt_array],['perdidas_array', 'cdt_array'])
            
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                  
    def cerrar_ventana_tras_calcular_perdidas(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
            else:
                if String_o_Bus == 'String Cable':
                    max_perdidas_cable_string = np.nanmax(perdidas_cables_string[...,1])
                    media_perdidas_cable_string = np.nansum(perdidas_cables_string[...,0]) / (np.count_nonzero(~np.isnan(perdidas_cables_string[...,1])) * np.mean(pot_string_STC)) * 100
                    max_perdidas_DC_Bus = 'N/A'
                    media_perdidas_DC_Bus = 'N/A'
                    media_perdidas_subarray = media_perdidas_cable_string
                elif String_o_Bus == 'DC Bus':
                    max_perdidas_cable_string = 'N/A'
                    media_perdidas_cable_string = 'N/A'
                    max_perdidas_DC_Bus = np.nanmax(perdidas_DC_Bus[...,1])
                    media_perdidas_DC_Bus = np.nansum(perdidas_DC_Bus[...,0]) / (np.count_nonzero(~np.isnan(perdidas_DC_Bus[...,1])) * np.mean(pot_string_STC)) * 100
                    media_perdidas_subarray = media_perdidas_DC_Bus
                else:   
                    max_perdidas_cable_string = np.nanmax(perdidas_cables_string[...,1])
                    media_perdidas_cable_string = np.nansum(perdidas_cables_string[...,0]) / (np.count_nonzero(~np.isnan(perdidas_cables_string[...,1])) * np.mean(pot_string_STC)) * 100
                    max_perdidas_DC_Bus = np.nanmax(perdidas_DC_Bus[...,1])
                    media_perdidas_DC_Bus = np.nansum(perdidas_DC_Bus[...,0]) / (np.count_nonzero(~np.isnan(perdidas_DC_Bus[...,1])) * np.mean(pot_string_STC)) * 100
                    media_perdidas_subarray = ( np.nansum(perdidas_cables_string[...,0]) + np.nansum(perdidas_DC_Bus[...,0]) ) / (np.count_nonzero(~np.isnan(inv_string[...,0,0])) * pot_inv)  * 100          
                
                if DCBoxes_o_Inv_String == 'DC Boxes':    
                    max_perdidas_array = np.nanmax(perdidas_array[...,1])
                    media_perdidas_array = np.nansum(perdidas_array[...,0]) / (np.count_nonzero(~np.isnan(strings_fisicos[...,1])) * np.mean(pot_string_STC)) * 100
                    max_cdt_array = []
                    media_cdt_array = []
                else:
                    max_perdidas_array = np.nanmax(perdidas_array[...,1])
                    media_perdidas_array = np.nansum(perdidas_array[...,0]) / (np.count_nonzero(~np.isnan(inv_string[...,0,0])) * pot_inv) *100
                    
                    max_cdt_array = np.nanmax(cdt_array[...,1])
                    media_cdt_array = np.nansum(cdt_array[...,1]) / np.count_nonzero(~np.isnan(inv_string[...,0,0])) 

                if DCBoxes_o_Inv_String == 'DC Boxes':
                    if String_o_Bus == 'DC Bus':
                        media_perdidas_DC = (np.nansum(perdidas_DC_Bus[...,0]) + np.nansum(perdidas_array[...,0])) / (np.count_nonzero(~np.isnan(strings_fisicos[...,1])) * np.mean(pot_string_STC)) * 100
                    elif String_o_Bus == 'String Cable':
                        media_perdidas_DC = (np.nansum(perdidas_cables_string[...,0]) + np.nansum(perdidas_array[...,0])) / (np.count_nonzero(~np.isnan(strings_fisicos[...,1])) * np.mean(pot_string_STC)) * 100
                    else:
                        media_perdidas_DC = (np.nansum(perdidas_cables_string[...,0]) + np.nansum(perdidas_DC_Bus[...,0]) + np.nansum(perdidas_array[...,0])) / (np.count_nonzero(~np.isnan(strings_fisicos[...,1])) * np.mean(pot_string_STC)) * 100
                else:
                    media_perdidas_DC = media_perdidas_cable_string
                    
                mostrar_tabla_resumen_perdidas(max_perdidas_cable_string, media_perdidas_cable_string, max_perdidas_DC_Bus, media_perdidas_DC_Bus, media_perdidas_subarray, max_perdidas_array, media_perdidas_array, media_perdidas_DC, max_cdt_array, media_cdt_array)        
            
        except:
            print("Error al borrar el gif o cargar resultados")
            traceback.print_exc()
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_calcular_perdidas():
        proceso_calculo_perdidas()
        root.after(0, lambda: cerrar_ventana_tras_calcular_perdidas(ventana_carga))
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_calcular_perdidas) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()



boton_array_CAD_read = tk.Button(frame_DCABLE_calc_local, text="Calculate", command=calcular_perdidas_cables, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_array_CAD_read.grid(row=2, column=5, padx=20)




#%%
#---------------------------SEXTA PESTAÑA - ZANJAS------------------------

#LAYOUT DE FRAMES PARA INTRODUCIR DATOS
# Crear un frame para dar un margen respecto a los bordes
frame_zanjas_container = tk.Frame(Trenches_NB, background=blanco_roto)
frame_zanjas_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)

#Dividimos el container en tres horizontales, uno para el boton de preparar zanjas, otro los procesos de DC, LV, MV, AS en un notebook y otro para el boton de combinar zanjas
frame_zanjas_container.grid_rowconfigure(0, weight=1)
frame_zanjas_container.grid_rowconfigure(1, weight=5)
frame_zanjas_container.grid_rowconfigure(2, weight=1)
frame_zanjas_container.grid_columnconfigure(0, weight=1) #añadimos el column para que se pueda expandir e-w aunque no pudiese desbordar

#Creamos los tres subframes
frame_preparar_polilineas =tk.Frame(frame_zanjas_container, background=blanco_roto)
frame_preparar_polilineas.grid(row=0, column=0, sticky='ew', padx=10, pady=0)
frame_preparar_polilineas.grid_columnconfigure(0, weight=1) #permitimos que se expanda

frame_procesos_zanjas =tk.Frame(frame_zanjas_container, background=blanco_roto)
frame_procesos_zanjas.grid(row=1, column=0, sticky='nsew', padx=10, pady=0)
frame_procesos_zanjas.grid_columnconfigure(0, weight=1) #permitimos que se expanda

frame_combinar_zanjas =tk.Frame(frame_zanjas_container, background=blanco_roto)
frame_combinar_zanjas.grid(row=2, column=0, sticky='ew', padx=10, pady=0)
frame_combinar_zanjas.grid_columnconfigure(0, weight=1) #permitimos que se expanda

        #Dividimos el subframe de procesos en dos, uno para zanjas dc y otro para lv
frame_procesos_zanjas.grid_columnconfigure(0, weight=1)
frame_procesos_zanjas.grid_columnconfigure(1, weight=2)

frame_zanjas_DC = tk.Frame(frame_procesos_zanjas, background=blanco_roto)
frame_zanjas_DC.grid(row=0, column=0, sticky='nsew', padx=10, pady=0)

frame_zanjas_LV = tk.Frame(frame_procesos_zanjas, background=blanco_roto)
frame_zanjas_LV.grid(row=0, column=1, sticky='nsew', padx=10, pady=0)

#Dividimos el frame de zanjas LV en dos subframes, uno para el prediseño y otro para los calculos de ancho de zanja
frame_zanjas_LV.grid_rowconfigure(0, weight=1)
frame_zanjas_LV.grid_rowconfigure(1, weight=7)

    #Creamos los dos dsubframes LV
frame_zanjas_LV_prediseño = tk.Frame(frame_zanjas_LV, background=blanco_roto)
frame_zanjas_LV_prediseño.grid(row=0, column=0, sticky='nsew', padx=20, pady=0)

frame_zanjas_LV_calculo = tk.Frame(frame_zanjas_LV, background=blanco_roto)
frame_zanjas_LV_calculo.grid(row=1, column=0, sticky='nsew', padx=20, pady=0)
        #Dividimos el subframe de calculo en 2 para albergar las dos tablas manuales
frame_zanjas_LV_calculo.grid_columnconfigure(0, weight=1)
frame_zanjas_LV_calculo.grid_columnconfigure(1, weight=1)
            #Creamos los dos subframes adicionales
frame_tabla_config_zanjas_LV = tk.Frame(frame_zanjas_LV_calculo, background=blanco_roto)
frame_tabla_config_zanjas_LV.grid(row=0, column=0, sticky='nsew', padx=10, pady=0)          

frame_tabla_anchos_zanjas_LV = tk.Frame(frame_zanjas_LV_calculo, background=blanco_roto)
frame_tabla_anchos_zanjas_LV.grid(row=0, column=1, sticky='nsew', padx=10, pady=0)         




#---------Preparar polilineas

    
def preparar_polilineas_para_calculo_zanjas():
    
    def proceso_preparar_polilineas():
        global pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO
        global error_simulacion
        error_simulacion = 'Sin error'

        try:
            if DCBoxes_o_Inv_String == 'DC Boxes':                
                pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO = Algoritmo_IXPHOS_4_Zanjas.densificar_polilineas_con_puntos_comunes(bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, max_c, max_tubos_DC_bloque, cajas_fisicas, filas_en_cajas, strings_fisicos, filas_con_cable_string, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO, DCBoxes_o_Inv_String)
            else:
                pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO = Algoritmo_IXPHOS_4_Zanjas.densificar_polilineas_con_puntos_comunes(bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, max_inv, max_tubos_DC_bloque, inv_como_cajas_fisicas, filas_en_cajas, strings_fisicos, filas_con_cable_string, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO, DCBoxes_o_Inv_String)
                
            guardar_variables([pol_cable_string, pol_DC_Bus, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO],['pol_cable_string', 'pol_DC_Bus', 'pol_array_cable', 'pol_AASS_LVAC', 'pol_ethernet', 'pol_CCTV_LVAC', 'pol_OyM_supply_LVAC', 'pol_Warehouse_supply_LVAC', 'pol_cable_MV', 'pol_cable_FO'])

        except:
            error_simulacion = 'Error'
            traceback.print_exc()


    def cerrar_ventana_tras_preparar_polilineas(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            
            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_preparar_polilineas():
        proceso_preparar_polilineas()
        root.after(0, lambda: cerrar_ventana_tras_preparar_polilineas(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_preparar_polilineas) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
    
boton_preparar_polilineas = tk.Button(frame_preparar_polilineas, text="Prepare all polylines", command=preparar_polilineas_para_calculo_zanjas, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'), anchor='center')
boton_preparar_polilineas.grid(row=0, column=0, pady=20)   





#-------Entradas diseño de zanjas
def entradas_zanjas_DC(valores_dados_zanjas_DC):
    global entrada_max_t_DC1, valor_ancho_DC1, valor_ancho_DC2

        #Maximo numero de tubos en DC1    
    etiqueta_max_t_DC1 = tk.Label(frame_zanjas_DC, text='Max. no. conduits in DC1', fg=rojo_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_max_t_DC1.grid(row=0, column=0)
    valor_max_t_DC1 = tk.StringVar()
    valor_max_t_DC1.set(valores_dados_zanjas_DC[0])
    entrada_max_t_DC1 = tk.Entry(frame_zanjas_DC, textvariable=valor_max_t_DC1, width=5)
    entrada_max_t_DC1.grid(row=0, column=1, padx=(5,20), pady=(15,10))

        #Ancho DC1
    etiqueta_ancho_DC1 = tk.Label(frame_zanjas_DC, text="DC1 width (m)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_ancho_DC1.grid(row=1, column=0, padx=(10,0),pady=(15,10))
    valor_ancho_DC1 = tk.StringVar()
    valor_ancho_DC1.set(valores_dados_zanjas_DC[1])
    entrada_ancho_DC1 = tk.Entry(frame_zanjas_DC, textvariable=valor_ancho_DC1, width=5)
    entrada_ancho_DC1.grid(row=1, column=1, padx=(5,20), pady=(15,10))

        #Ancho DC2
    etiqueta_ancho_DC2 = tk.Label(frame_zanjas_DC, text="DC2 width (m)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_ancho_DC2.grid(row=2, column=0, padx=(10,0),pady=(15,10))
    valor_ancho_DC2 = tk.StringVar()
    valor_ancho_DC2.set(valores_dados_zanjas_DC[2])
    entrada_ancho_DC2 = tk.Entry(frame_zanjas_DC, textvariable=valor_ancho_DC2, width=5)
    entrada_ancho_DC2.grid(row=2, column=1, padx=(5,20), pady=(15,10))        
        

valores_iniciales_zanjas_DC=[[],[],[]]


def entradas_prediseño_zanjas_LV(valores_iniciales_prediseño_zanjas_LV):
    global entrada_met_diseño, entrada_max_c_tz
    
        #Combobox para método de diseño
    opciones_met_diseño = ["Manual", "IEC 60364", "AS/NZS 3008"]
    entrada_met_diseño = tk.StringVar(value = valores_iniciales_prediseño_zanjas_LV[0])
    
    etiqueta_met_diseño = tk.Label(frame_zanjas_LV_prediseño, text='Design method', fg=rojo_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_met_diseño.grid(row=0, column=0)
    combobox_met_diseño=ttk.Combobox(frame_zanjas_LV_prediseño, textvariable=entrada_met_diseño, values=opciones_met_diseño)
    combobox_met_diseño.grid(row=0, column=1)
    
        #Maximo numero de circuitos por tipo de zanja
    opciones_max_c_tz = ['1', '2', '3', '4']
    entrada_max_c_tz = tk.StringVar(value = valores_iniciales_prediseño_zanjas_LV[1])
    
    etiqueta_max_c_tz = tk.Label(frame_zanjas_LV_prediseño, text='Max. no. circuits per trench type', fg=rojo_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_max_c_tz.grid(row=1, column=0)
    combobox_max_c_tz=ttk.Combobox(frame_zanjas_LV_prediseño, textvariable=entrada_max_c_tz, values=opciones_max_c_tz)
    combobox_max_c_tz.grid(row=1, column=1)
    



valores_iniciales_prediseño_zanjas_LV=[[],[],[]]





def entradas_zanjas_LV_auto(valores_zanjas_LV_auto):
    #Limpiamos los widgets existentes antes de rellenar el frame
    for widget in frame_tabla_config_zanjas_LV.winfo_children():
        widget.destroy()
    for widget in frame_tabla_anchos_zanjas_LV.winfo_children():
        widget.destroy()
    
    global valor_ancho_min, valor_int_circ, entrada_secciones_LV, valor_cab_diam, valor_temp, valor_res_ter, entrada_material_cond, entrada_material_ais, entrada_met_inst
    
    #Entradas para simulacion automatica
        #Ancho_minimo
    etiqueta_ancho_min = tk.Label(frame_tabla_config_zanjas_LV, text="Minimum width (m)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_ancho_min.grid(row=2, column=0, padx=(10,0),pady=(15,10))
    valor_ancho_min = tk.StringVar()
    valor_ancho_min.set(valores_zanjas_LV_auto[0])
    entrada_ancho_min = tk.Entry(frame_tabla_config_zanjas_LV, textvariable=valor_ancho_min, width=5)
    entrada_ancho_min.grid(row=2, column=1, padx=(5,20), pady=(15,10))
        #Intensidad de circuitos
    etiqueta_int_circ = tk.Label(frame_tabla_config_zanjas_LV, text="Circuit Current (A)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_int_circ.grid(row=3, column=0, padx=(10,0),pady=(15,10))
    valor_int_circ = tk.StringVar()
    valor_int_circ.set(valores_zanjas_LV_auto[1])
    entrada_int_circ = tk.Entry(frame_tabla_config_zanjas_LV, textvariable=valor_int_circ, width=5)
    entrada_int_circ.grid(row=3, column=1, padx=(5,20), pady=(15,10))

        #Combobox para seccion de conductor
    opciones_secciones_LV = ['120','150','185','240','300','400']
    entrada_secciones_LV = tk.StringVar(value = valores_zanjas_LV_auto[2])
    
    etiqueta_secciones_LV = tk.Label(frame_tabla_config_zanjas_LV, text='Cross section', fg=rojo_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_secciones_LV.grid(row=4, column=0)
    combobox_secciones_LV=ttk.Combobox(frame_tabla_config_zanjas_LV, textvariable=entrada_secciones_LV, values=opciones_secciones_LV)
    combobox_secciones_LV.grid(row=4, column=1)
        #Diametro cable
    etiqueta_cab_diam = tk.Label(frame_tabla_config_zanjas_LV, text="Cable diameter (mm)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_cab_diam.grid(row=5, column=0, padx=(10,0),pady=(15,10))
    valor_cab_diam = tk.StringVar()
    valor_cab_diam.set(valores_zanjas_LV_auto[3])
    entrada_cab_diam = tk.Entry(frame_tabla_config_zanjas_LV, textvariable=valor_cab_diam, width=5)
    entrada_cab_diam.grid(row=5, column=1, padx=(5,20), pady=(15,10))
        #Temperatura de suelo
    etiqueta_temp = tk.Label(frame_tabla_config_zanjas_LV, text="Soil temperature (ºC)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_temp.grid(row=6, column=0, padx=(10,0),pady=(15,10))
    valor_temp = tk.StringVar()
    valor_temp.set(valores_zanjas_LV_auto[4])
    entrada_temp = tk.Entry(frame_tabla_config_zanjas_LV, textvariable=valor_temp, width=5)
    entrada_temp.grid(row=6, column=1, padx=(5,20), pady=(15,10))
        #Resistividad termica
    etiqueta_res_ter = tk.Label(frame_tabla_config_zanjas_LV, text="Soil resistivity (W/m-K)", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_res_ter.grid(row=7, column=0, padx=(10,0),pady=(15,10))
    valor_res_ter = tk.StringVar()
    valor_res_ter.set(valores_zanjas_LV_auto[5])
    entrada_res_ter = tk.Entry(frame_tabla_config_zanjas_LV, textvariable=valor_res_ter, width=5)
    entrada_res_ter.grid(row=7, column=1, padx=(5,20), pady=(15,10))
    
        #Combobox para material del conductor
    opciones_material_cond = ["Cu", "Al"]
    entrada_material_cond = tk.StringVar(value = valores_zanjas_LV_auto[6])
    
    etiqueta_material_cond = tk.Label(frame_tabla_config_zanjas_LV, text='Conductor material', fg=rojo_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_material_cond.grid(row=8, column=0)
    combobox_material_cond=ttk.Combobox(frame_tabla_config_zanjas_LV, textvariable=entrada_material_cond, values=opciones_material_cond)
    combobox_material_cond.grid(row=8, column=1)
    
        #Combobox para material del aislante
    opciones_material_ais = ["PVC (70ºC)", "XLPE or EPR (90ºC)"]
    entrada_material_ais = tk.StringVar(value = valores_zanjas_LV_auto[7])
    
    etiqueta_material_ais = tk.Label(frame_tabla_config_zanjas_LV, text='Insulation material', fg=rojo_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_material_ais.grid(row=9, column=0)
    combobox_material_ais=ttk.Combobox(frame_tabla_config_zanjas_LV, textvariable=entrada_material_ais, values=opciones_material_ais)
    combobox_material_ais.grid(row=9, column=1)
    
        #Combobox para método de instalacion
    opciones_met_inst = ["Directly buried", "Buried in conduits"]
    entrada_met_inst = tk.StringVar(value = valores_zanjas_LV_auto[8])
    
    etiqueta_met_inst = tk.Label(frame_tabla_config_zanjas_LV, text='Installation method', fg=rojo_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_met_inst.grid(row=10, column=0)
    combobox_met_inst=ttk.Combobox(frame_tabla_config_zanjas_LV, textvariable=entrada_met_inst, values=opciones_met_inst)
    combobox_met_inst.grid(row=10, column=1)


    boton_sim_LV_trenches_auto = tk.Button(frame_tabla_config_zanjas_LV, text="Simulate LV Trenches", command=simular_zanjas_LV_automatico, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
    boton_sim_LV_trenches_auto.grid(row=11, column=0, pady=20)   
    
valores_entradas_zanjas_LV_auto=[[],[],[],[],[],  [],[],[],[]]






def entradas_zanjas_LV_manual(matriz_de_datos):
    if matriz_de_datos.size>0:
        #Limpiamos los widgets existentes antes de rellenar el frame (pero no rompemos los frames internos)
        for widget in frame_tabla_config_zanjas_LV.winfo_children():
            if not isinstance(widget, tk.Frame):
                widget.destroy()    

 
        # Canvas con scroll
        canvas_LV = tk.Canvas(frame_tabla_config_zanjas_LV, height=400)
        scrollbar_LV_x = tk.Scrollbar(frame_tabla_config_zanjas_LV, orient="horizontal", command=canvas_LV.xview)
        scrollbar_LV_y = tk.Scrollbar(frame_tabla_config_zanjas_LV, orient="vertical", command=canvas_LV.yview)
        canvas_LV.configure(xscrollcommand=scrollbar_LV_x.set)
        canvas_LV.configure(yscrollcommand=scrollbar_LV_y.set)
        
        scrollbar_LV_x.grid(row=1, column=0, sticky='ew')
        scrollbar_LV_y.grid(row=0, column=1, sticky='ns')
        canvas_LV.grid(row=0, column=0, sticky='nsew')
        
        frame_LV_manual = tk.Frame(canvas_LV)
        canvas_LV.create_window((0, 0), window=frame_LV_manual, anchor="nw")
        
        # Fuente uniforme tipo tabla
        tabla_fuente = font.Font(family="Courier", size=10)
        
        # Encabezados
        for j in range(0,len(matriz_de_datos[0,:])):
            if j==0 or j==1:
                ancho_celda = 10
            else:
                ancho_celda = 5
                
            header = tk.Label(frame_LV_manual, text=matriz_de_datos[0,j], bg="#f0f0f0", font=("Helvetica", 10, "bold"),relief="ridge", width=ancho_celda, anchor="center", borderwidth=1)
            header.grid(row=0, column=j, sticky="nsew")
        
        # Entradas tipo celda
        global entradas_subtipos
        entradas_subtipos=[0] #lista para almacenar luego los tk.entry, empieza en 1 por el header (se le añade un 0 al principio, aunque no se usara)
        for i in range(1,len(matriz_de_datos[:,0])):
            for j in range(0,len(matriz_de_datos[0,:])):
                if j==0 or j==1:
                    ancho_celda = 10
                else:
                    ancho_celda = 5
                                        
                if j == 1:
                    e = tk.Entry(frame_LV_manual, width=ancho_celda, font=tabla_fuente, relief="solid", borderwidth=1,justify="center", bg="#fff")
                    e.insert(0, matriz_de_datos[i,j])
                    e.grid(row=i+1, column=j, sticky="nsew")
                    entradas_subtipos.append(e)
                else:
                    lbl = tk.Label(frame_LV_manual, text=matriz_de_datos[i,j], width=ancho_celda, font=tabla_fuente, relief="solid", borderwidth=1, bg="#e6e6e6", anchor="center")
                    lbl.grid(row=i+1, column=j, sticky="nsew")
        
        # Ajustar scroll dinámico
        def ajustar_scroll(event):
            canvas_LV.configure(scrollregion=canvas_LV.bbox("all"))
        
        frame_LV_manual.bind("<Configure>", ajustar_scroll)
        
        
        
        #Aprovechamsos para crear ya los encabezados de la tabla de anchos
        
        header = tk.Label(frame_tabla_anchos_zanjas_LV, text="Trench type", bg="#f0f0f0", font=("Helvetica", 10, "bold"),relief="ridge", width=10, anchor="center", borderwidth=1)
        header.grid(row=0, column=0, sticky="nsew")

        header = tk.Label(frame_tabla_anchos_zanjas_LV, text="Subtype", bg="#f0f0f0", font=("Helvetica", 10, "bold"),relief="ridge", width=10, anchor="center", borderwidth=1)
        header.grid(row=0, column=1, sticky="nsew")       
        
        header = tk.Label(frame_tabla_anchos_zanjas_LV, text="Width (m)", bg="#f0f0f0", font=("Helvetica", 10, "bold"),relief="ridge", width=10, anchor="center", borderwidth=1)
        header.grid(row=0, column=2, sticky="nsew")
        
        
        boton_flecha = tk.Button(frame_tabla_config_zanjas_LV, text="→", font=("Helvetica", 20), command=entradas_anchos_manuales_LV)
        boton_flecha.grid(row=0, column=2)
    
    
        def exportar_tabla_subtipos_LV():
            df_subtipos_LV=pd.DataFrame(config_circ_zanjas_LV)
            df_subtipos_LV.to_excel("Circuits in LV Trenches.xlsx", index=False, header=False)
            messagebox.showinfo("Export completed","Table exported to: Circuits in LV Trenches, in same folder.")
        
        boton_flecha = tk.Button(frame_tabla_config_zanjas_LV, text="Export to Excel", command=exportar_tabla_subtipos_LV, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
        boton_flecha.grid(row=2, column=0)
        
        def importar_tabla_subtipos_LV():
            ruta_subtipos_LV = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
            if not ruta_subtipos_LV:
                print("No se seleccionó ningún archivo.")
                return []
        
            extraccion_subtipos_LV = pd.read_excel(ruta_subtipos_LV)
        
            # Calcular hasta dónde hay valores en 'Trench types'
            cantidad_valores = extraccion_subtipos_LV['Trench type'].notna().sum()
        
            # Obtener los subtipos hasta esa fila, reemplazando NaN por ''
            subtypes_LV = extraccion_subtipos_LV.loc[:cantidad_valores - 1, 'Subtype'].fillna('').tolist()
        
            # Actualizar GUI
            global entradas_subtipos
            
            for i in range(1, len(entradas_subtipos)):
                if i - 1 < len(subtypes_LV):
                    entradas_subtipos[i].delete(0, tk.END)
                    entradas_subtipos[i].insert(0, subtypes_LV[i - 1])
            
            return subtypes_LV
        
        boton_flecha = tk.Button(frame_tabla_config_zanjas_LV, text="Import from Excel", command=importar_tabla_subtipos_LV, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
        boton_flecha.grid(row=2, column=1)
        
def entradas_anchos_manuales_LV():
    global subtipos_introducidos, config_circ_zanjas_LV
    subtipos_introducidos = [entrada.get() for entrada in entradas_subtipos[1:]]
    subtipos_introducidos.insert(0,'Subtype')
    
    #Guardamos los valores introducidos en la primera tabla
    config_circ_zanjas_LV[:,1]=subtipos_introducidos
    
    guardar_variables([config_circ_zanjas_LV], ['config_circ_zanjas_LV'])
    
    
    
    #Sacamos valores unicos para la segunda tabla
    global tipos_y_subtipos_unicos
    identificadores = []
    for i in range(1,len(config_circ_zanjas_LV[:,0])):
        identificadores.append((str(config_circ_zanjas_LV[i,0]),subtipos_introducidos[i]))
    
    tipos_y_subtipos_unicos = list(dict.fromkeys(identificadores))


    #---GUI

    # Fuente uniforme tipo tabla
    tabla_fuente = font.Font(family="Courier", size=10)
    


    #Limpiamos los widgets existentes antes de rellenar el frame y volvemos a crear los encabezados
    for widget in frame_tabla_anchos_zanjas_LV.winfo_children():
        if not isinstance(widget, tk.Frame):
            widget.destroy() 
            
    header = tk.Label(frame_tabla_anchos_zanjas_LV, text="Trench type", bg="#f0f0f0", font=("Helvetica", 10, "bold"),relief="ridge", width=10, anchor="center", borderwidth=1)
    header.grid(row=0, column=0, sticky="nsew")

    header = tk.Label(frame_tabla_anchos_zanjas_LV, text="Subtype", bg="#f0f0f0", font=("Helvetica", 10, "bold"),relief="ridge", width=10, anchor="center", borderwidth=1)
    header.grid(row=0, column=1, sticky="nsew")       
    
    header = tk.Label(frame_tabla_anchos_zanjas_LV, text="Width (m)", bg="#f0f0f0", font=("Helvetica", 10, "bold"),relief="ridge", width=10, anchor="center", borderwidth=1)
    header.grid(row=0, column=2, sticky="nsew")

            
    #Entradas tipo celda
    global entradas_anchos_tipos_LV, anchos_tipos_LV
    
    if anchos_tipos_LV is None:
        anchos_tipos_LV = [''] * len(tipos_y_subtipos_unicos)
        
    entradas_anchos_tipos_LV = []
    
    for i in range(0,len(tipos_y_subtipos_unicos)):
        for j in range(0,3):
            ancho_celda = 10                 
            if j == 2:
                e_a = tk.Entry(frame_tabla_anchos_zanjas_LV, width=ancho_celda, font=tabla_fuente, relief="solid", borderwidth=1,justify="center", bg="#fff")
                e_a.insert(0, anchos_tipos_LV[i])
                e_a.grid(row=i+1, column=j, sticky="nsew")
                entradas_anchos_tipos_LV.append(e_a)
            else:
                lbl = tk.Label(frame_tabla_anchos_zanjas_LV, text=tipos_y_subtipos_unicos[i][j], width=ancho_celda, font=tabla_fuente, relief="solid", borderwidth=1, bg="#e6e6e6", anchor="center")
                lbl.grid(row=i+1, column=j, sticky="nsew")
    
        
    max_i=len(tipos_y_subtipos_unicos)
    
    boton_sim_LV_trenches_auto = tk.Button(frame_tabla_anchos_zanjas_LV, text="Simulate LV Trenches", command=simular_zanjas_LV_manual, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
    boton_sim_LV_trenches_auto.grid(row=max_i+1, column=0, pady=20) 
    

#-------Simular ZANJAS DC

def simular_zanjas_DC():
    
    def proceso_simular_zanjas_DC():
        
        global zanjas_DC_ID, PB_zanjas_DC_ID, n_tubos_max_DC1, ancho_DC1, ancho_DC2
        global error_simulacion
        error_simulacion = 'Sin error'

        try:
            #Leer entrada para luego resumen y dibujo
            n_tubos_max_DC1 = int(entrada_max_t_DC1.get())
            ancho_DC1 = float(valor_ancho_DC1.get())
            ancho_DC2 = float(valor_ancho_DC2.get())
            
            #Funcion de simulacion (independiente de las entradas)
            zanjas_DC_ID, PB_zanjas_DC_ID = Algoritmo_IXPHOS_4_Zanjas.trazado_zanjas_DC_y_conteo_tubos_circuitos_en_zanja(String_o_Bus,bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf,max_p, filas_en_cajas, strings_fisicos, pol_cable_string, pol_DC_Bus, filas_con_cable_string, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque)
                                                    
            guardar_variables([zanjas_DC_ID, PB_zanjas_DC_ID, n_tubos_max_DC1,ancho_DC1,ancho_DC2],['zanjas_DC_ID', 'PB_zanjas_DC_ID','n_tubos_max_DC1','ancho_DC1','ancho_DC2'])
        except:
            error_simulacion = 'Error'
            traceback.print_exc()
            
    def cerrar_ventana_tras_simular_zanjas_DC(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_zanjas_DC():
        proceso_simular_zanjas_DC()
        root.after(0, lambda: cerrar_ventana_tras_simular_zanjas_DC(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_zanjas_DC) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
boton_sim_zanjas_DC = tk.Button(frame_zanjas_DC, text="Simulate DC Trenches", command=simular_zanjas_DC, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_sim_zanjas_DC.grid(row=3, column=0, pady=20)





#----------Simular zanjas AS

def simular_trazado_zanjas_AS():
    
    def proceso_simular_zanjas_AS():
        global zanjas_AS_ID
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            zanjas_AS_ID = Algoritmo_IXPHOS_4_Zanjas.trazado_zanjas_AASS(bloque_inicial, n_bloques, pol_AASS_LVAC, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_ethernet, pol_cable_FO, max_p_AASS_LVAC, max_p_AASS_eth)
            
            guardar_variables([zanjas_AS_ID],['zanjas_AS_ID'])
        
        except:
            traceback.print_exc()
            
    def cerrar_ventana_tras_simular_zanjas_AS(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            
            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
        except:
            print("Error al borrar el gif")

    def tarea_zanjas_AS():
        proceso_simular_zanjas_AS()
        root.after(0, lambda: cerrar_ventana_tras_simular_zanjas_AS(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_zanjas_AS) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()    
    
boton_simular_zanjas_AS= tk.Button(frame_zanjas_DC, text="Route AS Trenches", command=simular_trazado_zanjas_AS, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_simular_zanjas_AS.grid(row=5, column=0, pady=20)






#-------Simular ZANJAS LV

#Definir metodo y sacar trazado listando entrandas necesarias segun el metodo - NO SE PONE PANTALLA DE CARGA PORQUE ES UN PROCESO RAPIDO

def prediseño_zanjas_LV():
    def simular_prediseño_zanjas_LV():
        global prediseño_PB_zanjas_LV_ID, prediseño_zanjas_LV_ID, tipos_zanjas, Metodo_ancho_zanjas_LV, max_c_tz
        global error_de_simulacion

        error_de_simulacion = 'Sin error'
        
        try: 
            #Leer valores de entrada
            Metodo_ancho_zanjas_LV = entrada_met_diseño.get() #Puede ser 'Manual','IEC 60364' o 'AS/NZS 3008'
            max_c_tz=int(entrada_max_c_tz.get()) #maximo de circuitos en un mismo tipo de zanja
            
            #Sacar tipos basicos sin calcular anchos, los arrays de zanjas llevan [n_circuitos, 4 coordenadas]
            if DCBoxes_o_Inv_String == 'DC Boxes':
                prediseño_PB_zanjas_LV_ID, prediseño_zanjas_LV_ID, tipos_zanjas = Algoritmo_IXPHOS_4_Zanjas.trazado_zanjas_LV(bloque_inicial, n_bloques, max_b, max_c, max_p_array, cajas_fisicas, pol_array_cable, max_c_tz)
            else:
                prediseño_PB_zanjas_LV_ID, prediseño_zanjas_LV_ID, tipos_zanjas = Algoritmo_IXPHOS_4_Zanjas.trazado_zanjas_LV(bloque_inicial, n_bloques, max_b, max_inv, max_p_array, inv_como_cajas_fisicas, pol_array_cable, max_c_tz)

                
            if Metodo_ancho_zanjas_LV =='Manual':
                global config_circ_zanjas_LV, info_cada_zanja_LV
                #Obtener tabla con distribucion de circuitos y tipos de zanjas protegidas
                if DCBoxes_o_Inv_String == 'DC Boxes':
                    config_circ_zanjas_LV , info_cada_zanja_LV = Algoritmo_IXPHOS_4_Zanjas.combinaciones_circuitos_zanjas_LV(bloque_inicial, n_bloques, max_b, max_c, max_p_array, cajas_fisicas, pol_array_cable, tipos_zanjas, polilineas_caminos)
                else:
                    config_circ_zanjas_LV , info_cada_zanja_LV = Algoritmo_IXPHOS_4_Zanjas.combinaciones_circuitos_zanjas_LV(bloque_inicial, n_bloques, max_b, max_inv, max_p_array, inv_como_cajas_fisicas, pol_array_cable, tipos_zanjas, polilineas_caminos)

                guardar_variables([config_circ_zanjas_LV,info_cada_zanja_LV],['config_circ_zanjas_LV','info_cada_zanja_LV'])
                
            #Guardar variables en el dicionario
            guardar_variables([prediseño_PB_zanjas_LV_ID, prediseño_zanjas_LV_ID, tipos_zanjas, Metodo_ancho_zanjas_LV, max_c_tz],['prediseño_PB_zanjas_LV_ID', 'prediseño_zanjas_LV_ID', 'tipos_zanjas', 'Metodo_ancho_zanjas_LV', 'max_c_tz'])
            
        except:
            error_de_simulacion = 'Error trazado zanjas'
            traceback.print_exc()
            
    
    def cerrar_ventana_y_listar_nuevas_entradas(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            
            if error_de_simulacion == 'Error trazado zanjas':
                messagebox.showerror("Error", "There was an error creating LV trenches, please check data.")

            else: #si no ha habido fallo listamos las entradas necesarias correspondientes al metodo elegido
                if Metodo_ancho_zanjas_LV =='Manual':
                    entradas_zanjas_LV_manual(config_circ_zanjas_LV)
                else:
                    entradas_zanjas_LV_auto(valores_entradas_zanjas_LV_auto)
                    
        except:
            print("Error al borrar el gif")
            traceback.print_exc()
        
    def tarea_prediseño_zanjas_LV():
        simular_prediseño_zanjas_LV()
        root.after(0, lambda: cerrar_ventana_y_listar_nuevas_entradas(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_prediseño_zanjas_LV) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()


boton_sim_LV_trenches = tk.Button(frame_zanjas_LV_prediseño, text="Route LV Trenches", command=prediseño_zanjas_LV, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_sim_LV_trenches.grid(row=1, column=3, pady=20)   


 

def simular_zanjas_LV_automatico():
       
    def proceso_simular_zanjas_LV_automatico():
        global PB_zanjas_LV_ID, zanjas_LV_ID, tipos_y_subtipos_unicos, entradas_diseño_automatico
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            entradas_diseño_automatico = np.zeros(9, dtype=object)
            
            #Leer valores de entrada
            ancho_min_LV_trench_auto = float(valor_ancho_min.get())
            int_circ_LV_trench_auto = float(valor_int_circ.get())
            mat_cond_LV_trench_auto = entrada_material_cond.get() #puede ser 'Cobre' o 'Aluminio'
            mat_ais_LV_trench_auto = entrada_material_ais.get()  #puede ser 'XLPE o EPR (90ºC)' o 'PVC (70ºC)'
            cross_sect_LV_trench_auto = int(entrada_secciones_LV.get()) #sqmm #restringido a los valores de la tabla
            cab_diam_LV_trench_auto = float(valor_cab_diam.get())    #mm
            met_inst_LV_trench_auto = entrada_met_inst.get() #puede ser 'Directamente enterrado' o 'Enterrado bajo tubo'
            temp_LV_trench_auto = float(valor_temp.get())  #ºC
            res_ter_LV_trench_auto = float(valor_res_ter.get())  #W/m-K
            
            entradas_diseño_automatico = [ancho_min_LV_trench_auto, int_circ_LV_trench_auto, mat_cond_LV_trench_auto, mat_ais_LV_trench_auto, cross_sect_LV_trench_auto, cab_diam_LV_trench_auto, met_inst_LV_trench_auto, temp_LV_trench_auto, res_ter_LV_trench_auto]
            
            PB_zanjas_LV_ID, zanjas_LV_ID, tipos_y_subtipos_unicos = Algoritmo_IXPHOS_4_Zanjas.calculo_anchos_zanjas_LV(DCBoxes_o_Inv_String, bloque_inicial, n_bloques, prediseño_PB_zanjas_LV_ID, tipos_zanjas, Metodo_ancho_zanjas_LV, entradas_diseño_automatico, 0)
            
            
            #Guardar variables en el dicionario
            guardar_variables([PB_zanjas_LV_ID, zanjas_LV_ID, tipos_y_subtipos_unicos, ancho_min_LV_trench_auto, int_circ_LV_trench_auto, mat_cond_LV_trench_auto, mat_ais_LV_trench_auto, cross_sect_LV_trench_auto, cab_diam_LV_trench_auto, met_inst_LV_trench_auto, temp_LV_trench_auto, res_ter_LV_trench_auto],['PB_zanjas_LV_ID', 'zanjas_LV_ID', 'tipos_y_subtipos_unicos', 'ancho_min_LV_trench_auto', 'int_circ_LV_trench_auto', 'mat_cond_LV_trench_auto', 'mat_ais_LV_trench_auto', 'cross_sect_LV_trench_auto', 'cab_diam_LV_trench_auto', 'met_inst_LV_trench_auto', 'temp_LV_trench_auto', 'res_ter_LV_trench_auto'])
        except:
            error_de_simulacion = 'Error calc automatico'
            traceback.print_exc()

    def cerrar_ventana_tras_lv_auto(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            
            if error_de_simulacion == 'Error trazado zanjas':
                messagebox.showerror("Error", "There was an error calculating trenches, please check data.")
            elif error_de_simulacion == 'Error calc automatico':
                messagebox.showerror("Error", "There was an error while calculating trenches width, please check data.")
        except:
            print("Error al borrar el gif")

        
    def tarea_simular_zanjas_LV_auto():
        proceso_simular_zanjas_LV_automatico()
        root.after(0, lambda: cerrar_ventana_tras_lv_auto(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARI

    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_simular_zanjas_LV_auto) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()






def simular_zanjas_LV_manual():
    
    def proceso_simular_zanjas_LV_manual():
        global PB_zanjas_LV_ID, zanjas_LV_ID
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            #Leemos los anchos tras pulsar el boton
            anchos_tipos_LV = [entrada.get() for entrada in entradas_anchos_tipos_LV]
            #Tras introducir anchos en los tipos y subtipos ahora toca traer los datos de vuelta con los identificadores sobre cada zanja, lo integramos en la funcion de calculo de anchos de zanja
            entradas_diseño_manual=[]
            entradas_diseño_manual.append(config_circ_zanjas_LV)
            entradas_diseño_manual.append(tipos_y_subtipos_unicos)
            entradas_diseño_manual.append(anchos_tipos_LV)
            entradas_diseño_manual.append(info_cada_zanja_LV)

                                        #tipos_y_subtipos unicos se mete a mano, ya no es salida
            PB_zanjas_LV_ID, zanjas_LV_ID, [] = Algoritmo_IXPHOS_4_Zanjas.calculo_anchos_zanjas_LV(DCBoxes_o_Inv_String, bloque_inicial, n_bloques, prediseño_PB_zanjas_LV_ID, tipos_zanjas, Metodo_ancho_zanjas_LV, 0, entradas_diseño_manual)
            
            #Guardar variables en el dicionario
            guardar_variables([tipos_y_subtipos_unicos, anchos_tipos_LV, PB_zanjas_LV_ID, zanjas_LV_ID],['tipos_y_subtipos_unicos', 'anchos_tipos_LV', 'PB_zanjas_LV_ID', 'zanjas_LV_ID'])
        except:
            error_de_simulacion = 'Error calc automatico'
            traceback.print_exc()
            
        
    def cerrar_ventana_tras_lv_trench_manual(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            
            if error_de_simulacion == 'Error trazado zanjas':
                messagebox.showerror("Error", "There was an error calculating trenches, please check data.")
            elif error_de_simulacion == 'Error calc automatico':
                messagebox.showerror("Error", "There was an error while calculating trenches width, please check data.")
        except:
            print("Error al borrar el gif")
        
    def tarea_simular_zanjas_LV_manual():
        proceso_simular_zanjas_LV_manual()
        root.after(0, lambda: cerrar_ventana_tras_lv_trench_manual(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    

    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_simular_zanjas_LV_manual) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()    
    
     
    
    


def combinar_zanjas():
    
    def proceso_combinar_zanjas():
        global zanjas_LV_ID, zanjas_AS_ID
        global error_simulacion
        error_simulacion = 'Sin error'

                
        zanjas_LV_ID, zanjas_AS_ID = Algoritmo_IXPHOS_4_Zanjas.combinar_todas_las_zanjas(bloque_inicial, n_bloques, PB_zanjas_LV_ID, zanjas_LV_ID, zanjas_AS_ID)
        
        # guardar_variables([zanjas_AS_ID],['zanjas_AS_ID'])
        
    def cerrar_ventana_tras_combinar_zanjas(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
        except:
            print("Error al borrar el gif")
            
        if error_de_simulacion == 'Error':
            messagebox.showerror("Error", "There was an error while processing, please check data.")


    def tarea_combinar_zanjas():
        proceso_combinar_zanjas()
        root.after(0, lambda: cerrar_ventana_tras_combinar_zanjas(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_combinar_zanjas) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()    
    
boton_combinar_zanjas= tk.Button(frame_combinar_zanjas, text="Combine trenches", command=combinar_zanjas, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'), anchor='center')
boton_combinar_zanjas.grid(row=0, column=0, pady=20)


    
    
    
        
#%%

#---------------------------SEPTIMA PESTAÑA PUESTA A TIERRA------------------------
#LAYOUT DE FRAMES PARA INTRODUCIR DATOS
# Crear un frame para dar un margen respecto a los bordes
frame_PAT_container = tk.Frame(Earthing_NB, background=blanco_roto)
frame_PAT_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)

frame_PAT_entradas = tk.Frame(frame_PAT_container, background=blanco_roto)
frame_PAT_entradas.pack(side='left', padx=30, pady=30, fill='both', expand=True)

frame_PAT_simulacion= tk.Frame(frame_PAT_container, background=blanco_roto)
frame_PAT_simulacion.pack(side='right', padx=30, pady=30, fill='both', expand=True)


#-------Entradas anillos PAT
def entradas_anillo_PAT(valores_dados_electrodo_PAT):
    global entrada_seccion_electrodo_principal, entrada_seccion_electrodo_anillos, valor_retranqueo_anillo_PAT, valor_mayoracion_electrodo

        #Seccion electrodo principal
    opciones_seccion_electrodo_principal = ['16', '35', '50', '70', '95']
    entrada_seccion_electrodo_principal = tk.StringVar(value = valores_dados_electrodo_PAT[0])
    
    etiqueta_seccion_electrodo_principal = tk.Label(frame_PAT_entradas, text='Main earthing electrode cross section', fg=rojo_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_seccion_electrodo_principal.grid(row=0, column=0)
    combobox_seccion_electrodo_principal=ttk.Combobox(frame_PAT_entradas, textvariable=entrada_seccion_electrodo_principal, values=opciones_seccion_electrodo_principal)
    combobox_seccion_electrodo_principal.grid(row=0, column=1)
    
        #Seccion electrodo anillos envolventes
    opciones_seccion_electrodo_anillos = ['16', '35', '50', '70', '95']
    entrada_seccion_electrodo_anillos = tk.StringVar(value = valores_dados_electrodo_PAT[1])
    
    etiqueta_seccion_electrodo_anillos = tk.Label(frame_PAT_entradas, text='Enclosures earthing ring cross section', fg=rojo_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_seccion_electrodo_anillos.grid(row=1, column=0)
    combobox_seccion_electrodo_anillos=ttk.Combobox(frame_PAT_entradas, textvariable=entrada_seccion_electrodo_anillos, values=opciones_seccion_electrodo_anillos)
    combobox_seccion_electrodo_anillos.grid(row=1, column=1)

        #Retranqueo
    etiqueta_retranqueo_anillo_PAT = tk.Label(frame_PAT_entradas, text="Earthing ring setback", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_retranqueo_anillo_PAT.grid(row=2, column=0, padx=(10,0),pady=(15,10))
    valor_retranqueo_anillo_PAT = tk.StringVar()
    valor_retranqueo_anillo_PAT.set(valores_dados_electrodo_PAT[2])
    entrada_retranqueo_anillo_PAT = tk.Entry(frame_PAT_entradas, textvariable=valor_retranqueo_anillo_PAT, width=5)
    entrada_retranqueo_anillo_PAT.grid(row=2, column=1, padx=(5,20), pady=(15,10))

        #Mayoracion
    etiqueta_mayoracion_electrodo = tk.Label(frame_PAT_entradas, text="Electrode majoration", fg=rojo_GRS, bg=gris_suave, font=('Montserrat', 10, 'bold'))
    etiqueta_mayoracion_electrodo.grid(row=3, column=0, padx=(10,0),pady=(15,10))
    valor_mayoracion_electrodo = tk.StringVar()
    valor_mayoracion_electrodo.set(valores_dados_electrodo_PAT[3])
    entrada_mayoracion_electrodo = tk.Entry(frame_PAT_entradas, textvariable=valor_mayoracion_electrodo, width=5)
    entrada_mayoracion_electrodo.grid(row=3, column=1, padx=(5,20), pady=(15,10))

valores_iniciales_electrodo_PAT=[[],[],[],[]]
entradas_anillo_PAT(valores_iniciales_electrodo_PAT)


#-------Simular PAT

def simular_PAT():
        
    def proceso_simular_PAT():
        global seccion_PAT_principal,seccion_PAT_anillos,retranqueo_anillos_PAT,mayoracion_electrodo_PAT
        global PAT_latiguillo_entre_trackers, PAT_latiguillo_primera_pica, PAT_terminal_primera_pica, PAT_terminal_DC_Box, PAT_Electrodo
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        #Leer entradas de PAT
        seccion_PAT_principal = int(entrada_seccion_electrodo_principal.get())
        seccion_PAT_anillos = int(entrada_seccion_electrodo_anillos.get())
        retranqueo_anillos_PAT = float(valor_retranqueo_anillo_PAT.get())
        mayoracion_electrodo_PAT = float(valor_mayoracion_electrodo.get())
        
        #Simular procesos
        try:
            if DCBoxes_o_Inv_String == 'DC Boxes':
                PAT_latiguillo_entre_trackers, PAT_latiguillo_primera_pica, PAT_terminal_primera_pica, PAT_terminal_DC_Box, PAT_Electrodo = Algoritmo_IXPHOS_5_PAT_y_mediciones_finales.simulacion_principal_elementos_PAT(bloque_inicial, n_bloques, max_b, max_c, max_f_str_b, max_tpf, cajas_fisicas, strings_fisicos, filas_en_bandas, h_modulo, sep, orientacion, dist_primera_pica_extremo_tr, zanjas_DC_ID, zanjas_LV_ID, zanjas_AS_ID, seccion_PAT_principal)
            else:
                PAT_latiguillo_entre_trackers, PAT_latiguillo_primera_pica, PAT_terminal_primera_pica, PAT_terminal_DC_Box, PAT_Electrodo = Algoritmo_IXPHOS_5_PAT_y_mediciones_finales.simulacion_principal_elementos_PAT(bloque_inicial, n_bloques, max_b, max_inv, max_f_str_b, max_tpf, inv_como_cajas_fisicas, strings_fisicos, filas_en_bandas, h_modulo, sep, orientacion, dist_primera_pica_extremo_tr, zanjas_DC_ID, zanjas_LV_ID, zanjas_AS_ID, seccion_PAT_principal)
            
            PAT_Electrodo = Algoritmo_IXPHOS_5_PAT_y_mediciones_finales.anillos_PAT(PAT_Electrodo, seccion_PAT_anillos, pol_envolventes_PAT, retranqueo_anillos_PAT)
            
            #Guardar variables en el dicionario
            guardar_variables([seccion_PAT_principal,seccion_PAT_anillos,retranqueo_anillos_PAT,mayoracion_electrodo_PAT],['seccion_PAT_principal','seccion_PAT_anillos','retranqueo_anillos_PAT','mayoracion_electrodo_PAT'])
            guardar_variables([PAT_latiguillo_entre_trackers, PAT_latiguillo_primera_pica, PAT_terminal_primera_pica, PAT_terminal_DC_Box, PAT_Electrodo],['PAT_latiguillo_entre_trackers', 'PAT_latiguillo_primera_pica', 'PAT_terminal_primera_pica', 'PAT_terminal_DC_Box', 'PAT_Electrodo'])
        
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
            
    def tarea_simular_PAT():
            proceso_simular_PAT()
            root.after(0, lambda: cerrar_ventana_tras_simular_PAT(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
            
    def cerrar_ventana_tras_simular_PAT(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
                
        except:
            print("Error al borrar el gif")
        

    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_simular_PAT) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
    


boton_simular_PAT = tk.Button(frame_PAT_simulacion, text="Measure Earthing", command=simular_PAT, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_simular_PAT.grid(row=0, column=0, pady=20)   




#--------Dibujar electrodos de PAT------
def dibujar_electrodos_PAT():
    def proceso_dibujo_electrodos_PAT():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen
            AutoCAD_extension.CAD_draw_Earthing_Electrode(acad, PAT_Electrodo)
                       
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
                            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
               
    def cerrar_ventana_tras_simular_dibujo_electrodos_PAT(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_Earthing")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_electrodos_PAT():
        proceso_dibujo_electrodos_PAT()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_electrodos_PAT(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_electrodos_PAT) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_dibujar_electrodos_PAT = tk.Button(frame_PAT_simulacion, text="Draw Earthing Electrode", command=dibujar_electrodos_PAT, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_dibujar_electrodos_PAT.grid(row=6, column=0, pady=20)




#-------------Leer electrodo de PAT--------------





#%%---------------------------OCTAVA PESTAÑA - RESUMEN DE SALIDAS E INFORME EN EXCEL--------------------------------

#LAYOUT DE FRAMES PARA INTRODUCIR DATOS
# Crear un frame para dar un margen respecto a los bordes
frame_salidas_container = tk.Frame(Output_NB, background=blanco_roto)
frame_salidas_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)

frame_summary= tk.Frame(frame_salidas_container, background=blanco_roto)
frame_summary.pack(side='left', padx=30, pady=30, fill='both', expand=True)

frame_export= tk.Frame(frame_salidas_container, background=blanco_roto)
frame_export.pack(side='right', padx=30, pady=30, fill='both', expand=True)




def resumen_de_variables_totales():
    
    #PROCESAR MEDICIONES DE CABLES
    (
     PB_med_cable_de_string_pos, PB_med_cable_de_string_neg,
     PB_inst_cable_de_string_pos, PB_inst_cable_de_string_neg,
     PB_med_DC_Bus_pos, PB_med_DC_Bus_neg,
     PB_inst_DC_Bus_pos, PB_inst_DC_Bus_neg,
     
     PB_inst_cable_de_array_pos, PB_inst_cable_de_array_neg,
     PB_med_cable_de_array_pos, PB_med_cable_de_array_neg,
     PB_inst_cable_de_array_AC, PB_med_cable_de_array_AC,
     
     TOT_med_cable_MV, TOT_inst_cable_MV,
     TOT_med_cable_de_string_pos, TOT_med_cable_de_string_neg, TOT_med_cable_de_string,
     TOT_inst_cable_de_string_pos, TOT_inst_cable_de_string_neg, TOT_inst_cable_de_string,
     TOT_med_DC_Bus_pos, TOT_med_DC_Bus_neg, TOT_med_DC_Bus,
     TOT_inst_DC_Bus_pos, TOT_inst_DC_Bus_neg, TOT_inst_DC_Bus,
     
     cable_string_en_tubo, DC_Bus_en_tubo,
     
     TOT_inst_cable_de_array_pos, TOT_inst_cable_de_array_neg, TOT_inst_cable_de_array,
     TOT_med_cable_de_array_pos, TOT_med_cable_de_array_neg, TOT_med_cable_de_array,
     TOT_inst_cable_de_array_AC, TOT_med_cable_de_array_AC,
     
     error_medicion_cables
     
    ) = Algoritmo_IXPHOS_5_PAT_y_mediciones_finales.mediciones_por_bloque_y_totales_cables(String_o_Bus, DCBoxes_o_Inv_String, secciones_cs, secciones_dcb, secciones_array, bloque_inicial, n_bloques, med_cable_string_pos, med_cable_string_neg, med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_DC_Bus_pos, med_DC_Bus_neg, med_inst_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_inst_DC_Bus_neg, PB_zanjas_DC_ID, n_tubos_max_DC1, med_array_cable_pos, med_array_cable_neg,med_array_cable, med_inst_array_cable_pos, med_inst_array_cable_neg, med_inst_array_cable, lineas_MV, secciones_MV)
 
    #PROCESAR MEDICIONES DE ZANJAS
    PB_Zanja_DC1, PB_Zanja_DC2, TOT_Zanja_DC1, TOT_Zanja_DC2, PB_Zanjas_LV, TOT_Zanjas_LV, error_medicion_zanjas, TOT_Zanjas_AS = Algoritmo_IXPHOS_5_PAT_y_mediciones_finales.mediciones_por_bloque_y_totales_zanjas (bloque_inicial, n_bloques, PB_zanjas_DC_ID, n_tubos_max_DC1, PB_zanjas_LV_ID, tipos_y_subtipos_unicos, zanjas_AS_ID)
    
    #PROCESAR MEDICIONES DE CAJAS Y STRINGS
    if DCBoxes_o_Inv_String == 'DC Boxes':
        PB_n_strings, PB_n_DC_Boxes, PB_DC_Boxes, TOT_n_strings, TOT_n_DC_Boxes, TOT_DC_Boxes, error_medicion_cajas = Algoritmo_IXPHOS_5_PAT_y_mediciones_finales.mediciones_por_bloque_cajas_y_totales_strings(bloque_inicial, n_bloques, DCBoxes_ID)
    else:
        PB_n_strings, PB_n_String_Inverters, PB_String_Inverters, TOT_n_strings, TOT_n_String_Inverters, TOT_String_Inverters, error_medicion_cajas = Algoritmo_IXPHOS_5_PAT_y_mediciones_finales.mediciones_por_bloque_inv_string_y_totales_strings(bloque_inicial, n_bloques, String_Inverters_ID)
        
    #PROCESAR MEDICIONES DE PUESTA A TIERRA (el electrodo viene ya calculado de antes)
    PB_PAT_lat_entre_tr, PB_PAT_lat_prim_pica, PB_PAT_term_prim_pica, PB_PAT_term_DC_Box, TOT_PAT_lat_entre_tr, TOT_PAT_lat_prim_pica, TOT_PAT_term_prim_pica, TOT_PAT_term_DC_Box, TOT_PAT_Electrodo, error_medicion_PAT = Algoritmo_IXPHOS_5_PAT_y_mediciones_finales.mediciones_por_bloque_y_totales_PAT(bloque_inicial, n_bloques, PAT_latiguillo_entre_trackers,PAT_latiguillo_primera_pica,PAT_terminal_primera_pica,PAT_terminal_DC_Box, PAT_Electrodo, mayoracion_electrodo_PAT)

    #PROCESAR MEDICIONES DE PEQUEÑO MATERIAL DE BAJA TENSION
    (
    PB_Ratchets,
    PB_0_Cable_clips_2,
    PB_90_Cable_clips_2,
    PB_90_Cable_clips_4,
    PB_Straps_conduits,
    PB_Cable_Ties,
    PB_SC_Conector_String_pos,
    PB_SC_Conector_String_neg,
    PB_SC_Conector_Box_pos,
    PB_SC_Conector_Box_neg,
    PB_DCBus_Endcaps,
    PB_DCBus_Terminals,
    PB_Array_Terminal_Box,
    PB_Array_Terminal_PCS,
    PB_tubo_DC,

    TOT_Ratchets,
    TOT_0_Cable_clips_2,
    TOT_90_Cable_clips_2,
    TOT_90_Cable_clips_4,
    TOT_Straps_conduits,
    TOT_Cable_Ties,
    TOT_SC_Conector_String_pos,
    TOT_SC_Conector_String_neg,
    TOT_SC_Conector_Box_pos,
    TOT_SC_Conector_Box_neg,
    TOT_DCBus_Endcaps,
    TOT_DCBus_Terminal,
    TOT_Array_Terminal_Box,
    TOT_Array_Terminal_PCS,
    TOT_tubo_DC
) = Algoritmo_IXPHOS_5_PAT_y_mediciones_finales.mediciones_por_bloque_y_totales_LV_material(bloque_inicial, n_bloques, n_mods_serie, Interconexionado, DCBoxes_o_Inv_String, String_o_Bus, strings_fisicos, filas_con_cable_string, harness_neg, sch_cable_de_string_neg, sch_DC_Bus_neg, sch_array_cable_neg, sch_array_cable, med_tubo_corrugado_zanja_DC, PB_n_strings)
    
    if error_medicion_cables != '' or error_medicion_zanjas != '' or error_medicion_cajas != '' or error_medicion_PAT != '':
        messagebox.showinfo('Missing output info',f'{error_medicion_cables} {error_medicion_zanjas} {error_medicion_cajas} {error_medicion_PAT} information is not being showed because simulation was not performed or an error ocurred')    
        
        
        
        
    #-----------Guardar valores en un diccionario para exportarlos despues-----------
    global variables_salida_pb_tot
    
    variables_salida_pb_tot = {
    # 'String Cable_pos': (PB_med_cable_de_string_pos, TOT_med_cable_de_string_pos),
    # 'PB_med_cable_de_string_neg': (PB_med_cable_de_string_neg, TOT_med_cable_de_string_neg),
    # 'PB_inst_cable_de_string_pos': (PB_inst_cable_de_string_pos, TOT_inst_cable_de_string_pos),
    # 'PB_inst_cable_de_string_neg': (PB_inst_cable_de_string_neg, TOT_inst_cable_de_string_neg),
    # 'PB_med_DC_Bus_pos': (PB_med_DC_Bus_pos, TOT_med_DC_Bus_pos),
    # 'PB_med_DC_Bus_neg': (PB_med_DC_Bus_neg, TOT_med_DC_Bus_neg),
    # 'PB_inst_DC_Bus_pos': (PB_inst_DC_Bus_pos, TOT_inst_DC_Bus_pos),
    # 'PB_inst_DC_Bus_neg': (PB_inst_DC_Bus_neg, TOT_inst_DC_Bus_neg),
    # 'PB_inst_cable_de_array_pos': (PB_inst_cable_de_array_pos, TOT_inst_cable_de_array_pos),
    # 'PB_inst_cable_de_array_neg': (PB_inst_cable_de_array_neg, TOT_inst_cable_de_array_neg),
    # 'PB_med_cable_de_array_pos': (PB_med_cable_de_array_pos, TOT_med_cable_de_array_pos),
    # 'PB_med_cable_de_array_neg': (PB_med_cable_de_array_neg, TOT_med_cable_de_array_neg),
    # 'PB_inst_cable_de_array_AC': (PB_inst_cable_de_array_AC, TOT_inst_cable_de_array_AC),
    # 'PB_med_cable_de_array_AC': (PB_med_cable_de_array_AC, TOT_med_cable_de_array_AC),

    # 'PB_Zanja_DC1': (PB_Zanja_DC1, TOT_Zanja_DC1),
    # 'PB_Zanja_DC2': (PB_Zanja_DC2, TOT_Zanja_DC2),
    # 'PB_Zanjas_LV': (PB_Zanjas_LV, TOT_Zanjas_LV),

    'PB_n_strings': (PB_n_strings, TOT_n_strings),
        
    'PB_PAT_lat_entre_tr': (PB_PAT_lat_entre_tr, TOT_PAT_lat_entre_tr),
    'PB_PAT_lat_prim_pica': (PB_PAT_lat_prim_pica, TOT_PAT_lat_prim_pica),
    'PB_PAT_term_prim_pica': (PB_PAT_term_prim_pica, TOT_PAT_term_prim_pica),
    'PB_PAT_term_DC_Box': (PB_PAT_term_DC_Box, TOT_PAT_term_DC_Box),

    'PB_Ratchets': (PB_Ratchets, TOT_Ratchets),
    'PB_0_Cable_clips_2': (PB_0_Cable_clips_2, TOT_0_Cable_clips_2),
    'PB_90_Cable_clips_2': (PB_90_Cable_clips_2, TOT_90_Cable_clips_2),
    'PB_90_Cable_clips_4': (PB_90_Cable_clips_4, TOT_90_Cable_clips_4),
    'PB_Straps_conduits': (PB_Straps_conduits, TOT_Straps_conduits),
    'PB_Cable_Ties': (PB_Cable_Ties, TOT_Cable_Ties),
    'PB_SC_Conector_String_pos': (PB_SC_Conector_String_pos, TOT_SC_Conector_String_pos),
    'PB_SC_Conector_String_neg': (PB_SC_Conector_String_neg, TOT_SC_Conector_String_neg),
    'PB_SC_Conector_Box_pos': (PB_SC_Conector_Box_pos, TOT_SC_Conector_Box_pos),
    'PB_SC_Conector_Box_neg': (PB_SC_Conector_Box_neg, TOT_SC_Conector_Box_neg),
    'PB_DCBus_Endcaps': (PB_DCBus_Endcaps, TOT_DCBus_Endcaps),
    'PB_DCBus_Terminals': (PB_DCBus_Terminals, TOT_DCBus_Terminal),
    'PB_Array_Terminal_Box': (PB_Array_Terminal_Box, TOT_Array_Terminal_Box),
    'PB_Array_Terminal_PCS': (PB_Array_Terminal_PCS, TOT_Array_Terminal_PCS),
    'PB_tubo_DC': (PB_tubo_DC, TOT_tubo_DC)}    
        
    if DCBoxes_o_Inv_String == 'DC Boxes':
        variables_salida_pb_tot.update({
            'PB_n_DC_Boxes': (PB_n_DC_Boxes, TOT_n_DC_Boxes),
            'PB_DC_Boxes': (PB_DC_Boxes, TOT_DC_Boxes),
        })  
    else:
        variables_salida_pb_tot.update({
            'PB_n_String_Inverters': (PB_n_String_Inverters, TOT_n_String_Inverters),
            'PB_String_Inverters': (PB_String_Inverters, TOT_String_Inverters),
        })  
    
        
    #-----------MOSTRAR EN PANTALLA VALORES APLICABLES-----------
    try:
            
        datos_resumen=[]

        datos_resumen.append(["", "GENERAL DATA", ""])
        datos_resumen.append(["No. Strings", "", TOT_n_strings])
        
        if DCBoxes_o_Inv_String == 'DC Boxes':
            if TOT_n_cajas is not None:
                datos_resumen.append(["Total No. DC Boxes", "", int(TOT_n_cajas)])
                
            
    #SUMINISTRO DE CABLES
        datos_resumen.append(["", "CABLE SUPPLY", ""])
        #Cable MV
        if lineas_MV:
            for i in range(0,len(secciones_MV)):
                datos_resumen.append(["MV cable supply", f'{secciones_MV[i]} mm2', TOT_med_cable_MV[1,i]])
                  
        #Cable de string
        if String_o_Bus != 'DC Bus':
            for i in range(0,len(secciones_cs)):
                if TOT_med_cable_de_string_pos is not None:
                    if secciones_cs[i] > 0 and TOT_med_cable_de_string_pos[0,i]>0:
                        datos_resumen.append(["String cable supply", f'{secciones_cs[i]} mm2 (+)', TOT_med_cable_de_string_pos[1,i]])
                        datos_resumen.append(["String cable supply", f'{secciones_cs[i]} mm2 (-)', TOT_med_cable_de_string_neg[1,i]])
                    
        #DC Bus
        if String_o_Bus != 'String Cable': 
            for i in range(0,len(secciones_dcb)):
                if TOT_med_DC_Bus_pos is not None:
                    if secciones_dcb[i] > 0 and TOT_med_DC_Bus_pos[0,i]>0:
                        datos_resumen.append(["DC Bus supply", f'{secciones_dcb[i]} mm2 (+)', TOT_med_DC_Bus_pos[1,i]])
                        datos_resumen.append(["DC Bus supply", f'{secciones_dcb[i]} mm2 (-)', TOT_med_DC_Bus_neg[1,i]])
                    
        #Cable de array
        for i in range(0,len(secciones_array)):
            if DCBoxes_o_Inv_String == 'DC Boxes':
                if TOT_med_cable_de_array_pos is not None:
                    if secciones_array[i] > 0 and TOT_med_cable_de_array_pos[0,i]>0:
                        datos_resumen.append(["Array cable supply", f'{secciones_array[i]} mm2, (+)', TOT_med_cable_de_array_pos[1,i]])
                        datos_resumen.append(["Array cable supply", f'{secciones_array[i]} mm2, (-)', TOT_med_cable_de_array_neg[1,i]])   
                    
            elif DCBoxes_o_Inv_String == 'String Inverters':
                if TOT_inst_cable_de_array_AC is not None:
                    if secciones_array[i] > 0 and TOT_med_cable_de_array_AC[0,i]>0:
                        if uni_o_multipolar == 3:
                            datos_resumen.append(["Array cable supply", f'AC, single core, {secciones_array[i]} mm2', TOT_med_cable_de_array_AC[1,i]])
                        else:
                            datos_resumen.append(["Array cable supply", f'AC, multicore, {secciones_array[i]} mm2', TOT_med_cable_de_array_AC[1,i]])
                        
    #INSTALACION DE CABLES        
        datos_resumen.append(["", "CABLE INSTALLATION", ""]) 
        
        #Cable MV
        if lineas_MV:
            for i in range(0,len(secciones_MV)):
                datos_resumen.append(["MV cable installation", f'{secciones_MV[i]} mm2', TOT_inst_cable_MV[1,i]])        
                
        #Cable de string
        if String_o_Bus != 'DC Bus':
            for i in range(0,len(secciones_cs)):
                if TOT_inst_cable_de_string_pos is not None:
                    if secciones_cs[i] > 0 and TOT_inst_cable_de_string_pos[0,i]>0:
                        datos_resumen.append(["String cable installation", f'{secciones_cs[i]} mm2 (+)', TOT_inst_cable_de_string_pos[1,i]])
                        datos_resumen.append(["String cable installation", f'{secciones_cs[i]} mm2 (-)', TOT_inst_cable_de_string_neg[1,i]])
            
            #% distancia en tubo
        if cable_string_en_tubo is not None:
            valor_redondeado = np.round(cable_string_en_tubo, 2)
        else:
            valor_redondeado = 0  # o cualquier valor por defecto que tenga sentido
        
        datos_resumen.append(["String cable installation", "% pulled through conduit", valor_redondeado])

        #DC Bus 
        if String_o_Bus != 'String Cable':         
            for i in range(0,len(secciones_dcb)):
                if TOT_inst_DC_Bus_pos is not None:
                    if secciones_dcb[i] > 0 and TOT_inst_DC_Bus_pos[0,i]>0:
                        datos_resumen.append(["DC Bus installation", f'{secciones_dcb[i]} mm2 (+)', TOT_inst_DC_Bus_pos[1,i]])
                        datos_resumen.append(["DC Bus installation", f'{secciones_dcb[i]} mm2 (-)', TOT_inst_DC_Bus_neg[1,i]])
                    
            #% distancia en tubo
        if DC_Bus_en_tubo is not None:
            datos_resumen.append(["DC Bus installation", "% pulled through conduit", np.round(DC_Bus_en_tubo,2)])
                
        #Cable de array
        for i in range(0,len(secciones_array)):
            if DCBoxes_o_Inv_String == 'DC Boxes':
                if TOT_inst_cable_de_array_pos is not None:
                    if secciones_array[i] > 0 and TOT_inst_cable_de_array_pos[0,i]>0:
                        datos_resumen.append(["Array cable installation", f'{secciones_array[i]} mm2 (+)', TOT_inst_cable_de_array_pos[1,i]])
                        datos_resumen.append(["Array cable installation", f'{secciones_array[i]} mm2 (-)', TOT_inst_cable_de_array_neg[1,i]])   
                    
            elif DCBoxes_o_Inv_String == 'String Inverters':
                if TOT_inst_cable_de_array_AC is not None:
                    if secciones_array[i] > 0 and TOT_inst_cable_de_array_AC[0,i]>0:
                        if uni_o_multipolar == 3:
                            datos_resumen.append(["Array cable installation", f'AC, single core, {secciones_array[i]} mm2', TOT_inst_cable_de_array_AC[1,i]])
                        else:
                            datos_resumen.append(["Array cable installation", f'AC, multicore, {secciones_array[i]} mm2', TOT_inst_cable_de_array_AC[1,i]])
                        
                        
    #HARNESS
        if String_o_Bus != 'String Cable':
            datos_resumen.append(["", "HARNESS", ""])                                            
            for i in range(0,len(tipos_harness_pos)):
                if tipos_harness_pos[i][0]>0.1 and med_tipos_h_pos[i] > 0:
                    datos_resumen.append([f'Harness Type {int(tipos_harness_pos[i][0])}', "(+)", med_tipos_h_pos[i]]) #TODO comprobar que positivo y negativos van a ir alineados
                    datos_resumen.append([f'Harness Type {int(tipos_harness_neg[i][0])}', "(-)", med_tipos_h_neg[i]]) 

    #DC BOXES
        if DCBoxes_o_Inv_String == 'DC Boxes':
            datos_resumen.append(["", "DC Boxes", ""]) 
            if TOT_DC_Boxes is not None:
                for i in range (0,len(TOT_DC_Boxes)-1): #el ultimo no se representa porque es nan
                    datos_resumen.append([f'DC Box Type {TOT_DC_Boxes[i]}', f'{tipos_cajas_por_entradas[i]} inputs', TOT_n_DC_Boxes[i]])
    #CONDUIT
        if TOT_tubo_DC is not None:
            datos_resumen.append(["", "CONDUITS", ""])
            datos_resumen.append(["DC TRENCH", "UG FLEX", int(TOT_tubo_DC)])
    
    #ZANJAS DC 
        if TOT_Zanja_DC1 is not None:
            datos_resumen.append(["", "DC TRENCHES", ""])
            datos_resumen.append(["DC1", "", int(TOT_Zanja_DC1)])
            datos_resumen.append(["DC2", "", int(TOT_Zanja_DC2)])
            
    #ZANJAS LV
        datos_resumen.append(["", "LV TRENCHES", ""])
        for i in range (0,len(TOT_Zanjas_LV)):
            datos_resumen.append([TOT_Zanjas_LV[i][0],TOT_Zanjas_LV[i][1], int(TOT_Zanjas_LV[i][2])]) 

    #ZANJAS AS
        datos_resumen.append(["", "AS TRENCHES", ""])
        if TOT_Zanjas_AS is not None:
            datos_resumen.append(["AS1","", int(TOT_Zanjas_AS)]) 
                
    #PUESTA A TIERRA
        datos_resumen.append(["", "EARTHING", ""])
        if TOT_PAT_Electrodo:
            for i in range(0,len(TOT_PAT_Electrodo)):
                datos_resumen.append(["Earthing electrode", f'{TOT_PAT_Electrodo[i][0]} mm2', int(TOT_PAT_Electrodo[i][1])])
        datos_resumen.append(["Earthing terminal arrangements", "DC Boxes", TOT_PAT_term_DC_Box])
        datos_resumen.append(["Earthing terminal arrangements", "1st pile of tracker", TOT_PAT_term_prim_pica])
        datos_resumen.append(["Earthing patchcords", "1st pile jumper", TOT_PAT_lat_prim_pica])
        datos_resumen.append(["Earthing patchcords", "Piles bonding jumper", 0])
        datos_resumen.append(["Earthing patchcords", "Jumper between trackers", TOT_PAT_lat_entre_tr])
        
    #MATERIAL LV
        datos_resumen.append(["", "LV MATERIAL", ""])
        datos_resumen.append(["Cable clips", "0º 2-c", TOT_0_Cable_clips_2])
        datos_resumen.append(["Cable clips", "90º 2-c", TOT_90_Cable_clips_2])
        datos_resumen.append(["Cable clips", "90º 4-c", TOT_90_Cable_clips_4])
        datos_resumen.append(["Steel Straps", "", TOT_Straps_conduits])      
        
        if TOT_Ratchets is not None:
           datos_resumen.append(["DC Bus Ratchet Support", "", TOT_Ratchets])
        
        if TOT_SC_Conector_String_pos is not None:
            datos_resumen.append(["MC4 Connector", "(+) Solar Cable", TOT_SC_Conector_String_pos])
            datos_resumen.append(["MC4 Connector", "(-) Solar Cable", TOT_SC_Conector_String_neg])
            datos_resumen.append(["Pin Terminal", "(+) at DC Box", TOT_SC_Conector_Box_pos])
            datos_resumen.append(["Pin Terminal", "(-) at DC Box", TOT_SC_Conector_Box_neg])     
            
        if TOT_DCBus_Terminal is not None:
            datos_resumen.append(["DC Bus Lugs", "(+ and -)", TOT_DCBus_Terminal])
            datos_resumen.append(["DC Bus Encaps", "(+ and -)", TOT_DCBus_Endcaps])
       
        if TOT_Array_Terminal_Box is not None:
            for i in range(0,len(TOT_Array_Terminal_Box)):
                datos_resumen.append(["Array Cable Lugs", f"DC Box - {TOT_Array_Terminal_Box[0,i]} mm2", TOT_Array_Terminal_Box[1,i]])
                
            for i in range(0,len(TOT_Array_Terminal_PCS)):            
                datos_resumen.append(["Array Cable Lugs", f"PCS - {TOT_Array_Terminal_Box[0,i]} mm2", TOT_Array_Terminal_PCS[1,i]])    
             

            
    #Creamos la tabla en la GUI y le damos los valores aplicables antes filtrados
        #Primero borramos si ya existe
        global tabla_resumen, scrollbar_resumen
        if tabla_resumen is not None and tabla_resumen.winfo_exists():
            tabla_resumen.destroy()
        
        if scrollbar_resumen is not None and scrollbar_resumen.winfo_exists():
            scrollbar_resumen.destroy()
        
        #Creamos
        tabla_resumen = ttk.Treeview(frame_summary, columns=("Columna1", "Columna2", "Columna3"), show="headings", height=20)
        tabla_resumen.heading("Columna1", text="Item")
        tabla_resumen.heading("Columna2", text="Attribute")
        tabla_resumen.heading("Columna3", text="Value")
    
        for i in range(0,len(datos_resumen)):
            tabla_resumen.insert("", "end", values=(datos_resumen[i][0], datos_resumen[i][1], datos_resumen[i][2]))

        #Añadir scrollbar
        scrollbar_resumen = ttk.Scrollbar(frame_summary, orient="vertical", command=tabla_resumen.yview)
        tabla_resumen.configure(yscrollcommand=scrollbar_resumen.set)
        
        #Posicionarlos en el frame
        tabla_resumen.grid(row=2, column=0, sticky="nsew")
        scrollbar_resumen.grid(row=2, column=1, sticky="ns")
    
    except:
        messagebox.showerror("Error", "There was an error while processing, please check data.") 
        traceback.print_exc()


tabla_resumen = None
scrollbar_resumen = None

boton_resumen_totales = tk.Button(frame_summary, text="Final Measurements and Summary", command=resumen_de_variables_totales, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_resumen_totales.grid(row=1, column=0, pady=20)   






#Exportacion de schedules y datos detallados a excel

def export_PV_Plant_results_to_excel():
    
    def is_nan_array(arr):
        return np.vectorize(lambda x: x is None or x == 'nan' or (isinstance(x, float) and np.isnan(x)))(arr)
    
    #------SCHEDULES
    
    
    #__DC BOXES__
        #Refinar array inicial
    if DCBoxes_o_Inv_String == 'DC Boxes':
        SCH_DC_Boxes_con_nan = np.vstack(DCBoxes_ID.reshape(-1, 8)).astype(object)
        
        SCH_DC_Boxes_con_nan[SCH_DC_Boxes_con_nan == "nan"] = np.nan # Convertir strings "nan" en np.nan
        
        mask_no_todo_nan = ~np.all(is_nan_array(SCH_DC_Boxes_con_nan), axis=1) # Crear máscara de filas que NO son completamente nan
        
        SCH_DC_Boxes_filtrado = SCH_DC_Boxes_con_nan[mask_no_todo_nan] # Filtrar filas
        
        SCH_DC_Boxes = np.where(is_nan_array(SCH_DC_Boxes_filtrado), "-", SCH_DC_Boxes_filtrado) #Reemplazar los nan por el string "-"
    
            #Crear headers y pasar a dataframe y de ahí excel
        encabezados = ['ID', 'X coord.', 'Y coord.', 'Config.', 'Type', 'Str. in Bus', 'Single Strings', 'Total no. Strings']
        df_SCH_DC_Boxes = pd.DataFrame(SCH_DC_Boxes, columns=encabezados)
        ruta_completa = carpeta_archivo + "DC Boxes Schedule.xlsx"
        df_SCH_DC_Boxes.to_excel(ruta_completa, index=False, header=True)



    #__SUBARRAY CABLES__
        #Refinar array inicial
    if String_o_Bus != 'DC Bus':
        SCH_String_cable_pos_con_nan = np.vstack(sch_cable_de_string_pos.reshape(-1, 3)).astype(object)
        SCH_String_cable_neg_con_nan = np.vstack(sch_cable_de_string_neg.reshape(-1, 3)).astype(object)
        
        mask_pos_no_todo_nan = ~np.all(is_nan_array(SCH_String_cable_pos_con_nan), axis=1) # Crear máscara de filas que NO son completamente nan
        mask_neg_no_todo_nan = ~np.all(is_nan_array(SCH_String_cable_neg_con_nan), axis=1) # Crear máscara de filas que NO son completamente nan
        
        SCH_String_cable_pos_filtrado = SCH_String_cable_pos_con_nan[mask_pos_no_todo_nan] # Filtrar filas       
        SCH_String_cable_neg_filtrado = SCH_String_cable_neg_con_nan[mask_neg_no_todo_nan] # Filtrar filas
    
        #Ordenar listas con numeros y polaridades
        n_pos = SCH_String_cable_pos_filtrado.shape[0]
        n_neg = SCH_String_cable_neg_filtrado.shape[0]
        n_total = n_pos + n_neg
        
        intercalado = np.empty((n_total, 3), dtype=object)
        
        # Intercalar hasta el tamaño mínimo
        min_len = min(n_pos, n_neg)
        intercalado[0:2*min_len:2] = SCH_String_cable_pos_filtrado[:min_len]
        intercalado[1:2*min_len:2] = SCH_String_cable_neg_filtrado[:min_len]

        SCH_String_cable_filtrado = intercalado
            #Crear headers y pasar a dataframe y de ahí excel
        encabezados = ['ID', 'Cross Section (mm2)', 'Length (m)']
        df_SCH_String_cable = pd.DataFrame(SCH_String_cable_filtrado, columns=encabezados)
        ruta_completa = carpeta_archivo + "String Cables Schedule.xlsx"
        df_SCH_String_cable.to_excel(ruta_completa, index=False, header=True)



    if String_o_Bus != 'String Cable':
        SCH_DC_Bus_pos_con_nan = np.vstack(sch_DC_Bus_pos.reshape(-1, 4)).astype(object)
        SCH_DC_Bus_neg_con_nan = np.vstack(sch_DC_Bus_neg.reshape(-1, 4)).astype(object)
        
        mask_pos_no_todo_nan = ~np.all(is_nan_array(SCH_DC_Bus_pos_con_nan), axis=1) # Crear máscara de filas que NO son completamente nan
        mask_neg_no_todo_nan = ~np.all(is_nan_array(SCH_DC_Bus_neg_con_nan), axis=1) # Crear máscara de filas que NO son completamente nan

        SCH_DC_Bus_pos_filtrado = SCH_DC_Bus_pos_con_nan[mask_pos_no_todo_nan] # Filtrar filas        
        SCH_DC_Bus_neg_filtrado = SCH_DC_Bus_neg_con_nan[mask_neg_no_todo_nan] # Filtrar filas

        #Ordenar listas con numeros y polaridades
        n_pos = SCH_DC_Bus_pos_filtrado.shape[0]
        n_neg = SCH_DC_Bus_neg_filtrado.shape[0]
        n_total = n_pos + n_neg
        
        intercalado = np.empty((n_total, 4), dtype=object)
        
        # Intercalar hasta el tamaño mínimo
        min_len = min(n_pos, n_neg)
        intercalado[0:2*min_len:2] = SCH_DC_Bus_pos_filtrado[:min_len]
        intercalado[1:2*min_len:2] = SCH_DC_Bus_neg_filtrado[:min_len]

        SCH_DC_Bus_filtrado = intercalado
  
            #Crear headers y pasar a dataframe y de ahí excel
        encabezados = ['ID', 'No. Strings', 'Cross Section (mm2)', 'Length (m)']
        df_SCH_DC_Bus = pd.DataFrame(SCH_DC_Bus_filtrado, columns=encabezados)
        ruta_completa = carpeta_archivo + "DC Buses Schedule.xlsx"
        df_SCH_DC_Bus.to_excel(ruta_completa, index=False, header=True)

    #__ARRAY CABLES__
    if DCBoxes_o_Inv_String == 'DC Boxes':
        SCH_array_pos_con_nan = np.vstack(sch_array_cable_pos.reshape(-1, 3)).astype(object)
        SCH_array_neg_con_nan = np.vstack(sch_array_cable_neg.reshape(-1, 3)).astype(object)
        
        mask_pos_no_todo_nan = ~np.all(is_nan_array(SCH_array_pos_con_nan), axis=1) # Crear máscara de filas que NO son completamente nan
        mask_neg_no_todo_nan = ~np.all(is_nan_array(SCH_array_neg_con_nan), axis=1) # Crear máscara de filas que NO son completamente nan

        SCH_array_pos_filtrado = SCH_array_pos_con_nan[mask_pos_no_todo_nan] # Filtrar filas        
        SCH_array_neg_filtrado = SCH_array_neg_con_nan[mask_neg_no_todo_nan] # Filtrar filas
        
        #Ordenar listas con numeros y polaridades
        n_pos = SCH_array_pos_filtrado.shape[0]
        n_neg = SCH_array_neg_filtrado.shape[0]
        n_total = n_pos + n_neg
        
        intercalado = np.empty((n_total, 4), dtype=object)
        
        # Intercalar hasta el tamaño mínimo
        min_len = min(n_pos, n_neg)
        intercalado[0:2*min_len:2] = SCH_array_pos_filtrado[:min_len]
        intercalado[1:2*min_len:2] = SCH_array_neg_filtrado[:min_len]

        SCH_array_filtrado = intercalado
        
    else:
        SCH_array_con_nan = np.vstack(sch_array_cable.reshape(-1, 3)).astype(object)
        
        mask_no_todo_nan = ~np.all(is_nan_array(SCH_array_con_nan), axis=1) # Crear máscara de filas que NO son completamente nan

        SCH_array_filtrado = SCH_array_con_nan[mask_no_todo_nan] # Filtrar filas  
        
    #Crear headers y pasar a dataframe y de ahí excel
    encabezados = ['ID', 'Cross Section (mm2)', 'Length (m)']
    df_SCH_Array = pd.DataFrame(SCH_array_filtrado, columns=encabezados)
    ruta_completa = carpeta_archivo + "Array Schedule.xlsx"
    df_SCH_Array.to_excel(ruta_completa, index=False, header=True)

        

    #----------LIST OF STRINGS-------
    if DCBoxes_o_Inv_String == 'DC Boxes':
        strings_ID_for_export = strings_ID
    else:
        strings_ID_for_export = strings_ID[...,:5]
        
    lista_strings_con_nan = np.vstack(strings_ID_for_export.reshape(-1, 5)).astype(object)
    mask_no_todo_nan = ~np.all(is_nan_array(lista_strings_con_nan), axis=1) # Crear máscara de filas que NO son completamente nan
    lista_strings_filtrado = lista_strings_con_nan[mask_no_todo_nan]
            #Crear headers y pasar a dataframe y de ahí excel
    encabezados = ['String ID', 'X', 'Y_start', 'Y_end', 'sid_global']
    df_list_strings = pd.DataFrame(lista_strings_filtrado, columns=encabezados)
    ruta_completa = carpeta_archivo + "List of strings.xlsx"
    df_list_strings.to_excel(ruta_completa, index=False, header=True)
    
    #----------BOQ POR BLOQUE---------

    # bloques = list(range(bloque_inicial, n_bloques + 1))
    # columnas = bloques + ['TOTAL']

    # df_dict = {}
    # for nombre_var, (pb_array, total_valor) in variables_salida_pb_tot.items():
    #     df_dict[nombre_var] = list(pb_array) + [total_valor]

    # df_pb = pd.DataFrame.from_dict(df_dict, orient='index', columns=columnas)
    # df_pb.index.name = 'Variable'

    # nombre_archivo = 'Mediciones.xlsx'
    # df_pb.to_excel(nombre_archivo)








    #--------ANEXOS DE CALCULO------
    #---Resumen de perdidas por bloque
    # perdidas_subarray_bloque = [[0,0] for _ in range(n_bloques+1)]
    # perdidas_array_bloque = [[0,0] for _ in range(n_bloques+1)]
    # perdidas_DC_bloque = [[0,0] for _ in range(n_bloques+1)]
    
    # for i in range(bloque_inicial, n_bloques+1):
    #     perdidas_cable_string_bruto = np.vstack(perdidas_cables_string[i,...,0])
    #     perdidas_DC_Bus_bruto = np.vstack(perdidas_DC_Bus[i,...,0])
    #     perdidas_subarray_bloque[i][0] = np.nansum(perdidas_cable_string_bruto) + np.nansum(perdidas_DC_Bus_bruto)
    #     perdidas_subarray_bloque[i][1] = perdidas_subarray_bloque[i][0] / (np.count_nonzero(~np.isnan(strings_fisicos[i,:,:,:,1])) * pot_string_STC[i]) * 100
        
    #     perdidas_array_bloque_bruto = np.vstack(perdidas_array[i,...,0])
    #     perdidas_array_bloque[i][0] = np.nansum(perdidas_array_bloque_bruto)
    #     perdidas_array_bloque[i][1] = perdidas_array_bloque[i][0] / (np.count_nonzero(~np.isnan(strings_fisicos[i,:,:,:,1])) * pot_string_STC[i]) * 100
        
    #     perdidas_DC_bloque[i][0] = perdidas_subarray_bloque[i][0] + perdidas_array_bloque[i][0]
    #     perdidas_DC_bloque[i][1] = perdidas_DC_bloque[i][0] / (np.count_nonzero(~np.isnan(strings_fisicos[i,:,:,:,1])) * pot_string_STC[i]) * 100
    
    # max_perdidas_DC = np.max(perdidas_DC_bloque[:][1])
    # media_perdidas_DC = np.sum(perdidas_DC_bloque[:][0]) / (np.count_nonzero(~np.isnan(strings_fisicos[:,:,:,:,1])) *  np.mean(pot_string_STC[i])) * 100

    # sub = np.array(perdidas_subarray_bloque)
    # arr = np.array(perdidas_array_bloque)
    # dc  = np.array(perdidas_DC_bloque)
    
    # # Calculamos máximo y media de pérdidas DC [%]
    # max_perdidas_DC = np.max(dc[:,1])
    # media_perdidas_DC = np.sum(dc[:,0]) / (np.count_nonzero(~np.isnan(strings_fisicos[:,:,:,:,1])) * np.mean(pot_string_STC)) * 100
    
    # # Construir el DataFrame para Excel
    # # 2 columnas por bloque de datos + columnas vacías entre grupos
    # columnas = [
    #     'Subarray [W]', 'Subarray [%]', '',
    #     'Array [W]', 'Array [%]', '',
    #     'Total DC [W]', 'Total DC [%]'
    # ]
    
    # # Crear la matriz de datos completa
    # n_filas = len(perdidas_DC_bloque) + 4  # 4 porque fila 0-3 son cabecera/vacías
    # datos = [[''] * len(columnas) for _ in range(n_filas)]
    
    # # Escribimos los valores de media y máximo en las filas 1 y 2
    # datos[1][6] = 'Máx. pérdida DC [%]'
    # datos[1][7] = f"{max_perdidas_DC:.2f}"
    
    # datos[2][6] = 'Media pérdida DC [%]'
    # datos[2][7] = f"{media_perdidas_DC:.2f}"
    
    # # Escribir los valores por bloque a partir de la fila 4
    # for i in range(bloque_inicial, len(perdidas_DC_bloque)):
    #     fila = i + 4  # empezamos en la fila 5
    #     datos[fila][0] = sub[i][0]
    #     datos[fila][1] = sub[i][1]
    #     datos[fila][3] = arr[i][0]
    #     datos[fila][4] = arr[i][1]
    #     datos[fila][6] = dc[i][0]
    #     datos[fila][7] = dc[i][1]
    
    # # Crear DataFrame
    # df_perdidas = pd.DataFrame(datos, columns=columnas)
    
    # # Guardar a Excel
    # df_perdidas.to_excel("Resumen_Pérdidas_DC.xlsx", index=False, header=True)

    #---Listado de perdidas por cable
    # if String_o_Bus != 'DC Bus':
    #     sch_filtrado = SCH_String_cable_filtrado.reshape(-1, 2, 3)  # [N_strings, 2 polaridades, 3 campos]
    #     ids_base = [fila[0][:-1] for fila in sch_filtrado]  # # Tomamos el ID sin la última letra (+/-) de cualquier polaridad
    #     cross_sections = [fila[1][1] for fila in sch_filtrado] # Tomamos la sección y tipo de cable de cualquiera
    #     lengths = [float(fila[0][2]) + float(fila[1][2]) for fila in sch_filtrado]
    #     perdidas = np.vstack(perdidas_cables_string.reshape(-1, 2)).astype(object) #Cargar pérdidas por string, previamente filtradas
    #     mask = ~np.all(is_nan_array(perdidas), axis=1)
    #     perdidas_filtradas = perdidas[mask]

    #     sch_perdidas = np.column_stack((ids_base, cross_sections, lengths, perdidas_filtradas)) #Crear DataFrame final combinando todo
    #     encabezados = ['ID', 'No. Strings', 'Cross Section (mm2)', 'Length (m)', 'Losses (W)', 'Losses (%)'] # Convertir a DataFrame y exportar
    #     df_SCH_String_perdidas = pd.DataFrame(sch_perdidas, columns=encabezados) 
    #     df_SCH_String_perdidas.to_excel("String Cables Losses.xlsx", index=False)

    
    # if String_o_Bus != 'String Cable':
    #     sch_dcbus = SCH_DC_Bus_filtrado.reshape(-1, 2, 4)
    #     ids_base = [fila[0][:-1] for fila in sch_dcbus[:, 0, 0]]  # quitar la polaridad
    #     cross_sections = [fila[1][2] for fila in sch_dcbus]       # cualquiera de las dos polaridades
    #     lengths = [float(fila[0][3]) + float(fila[1][3]) for fila in sch_dcbus]  # suma de longitudes
    #     perdidas = np.vstack(perdidas_DC_Bus.reshape(-1, 2)).astype(object)
    #     mask = ~np.all(is_nan_array(perdidas), axis=1)
    #     perdidas_filtradas = perdidas[mask]
        
    #     sch_dcbus_final = np.column_stack((ids_base, cross_sections, lengths, perdidas_filtradas))
    #     encabezados = ['ID', 'Cross Section (mm2)', 'Length (m)', 'Losses (W)', 'Losses (%)']
    #     df_SCH_DC_Bus = pd.DataFrame(sch_dcbus_final, columns=encabezados)
    #     df_SCH_DC_Bus.to_excel("DC Buses Losses.xlsx", index=False)



boton_informe_excel = tk.Button(frame_export, text="Export data", command=export_PV_Plant_results_to_excel, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_informe_excel.grid(row=1, column=1, pady=20)   


#%%
#---------------------------ULTIMA PESTAÑA - REPRESENTACION FINAL EN AUTOCAD------------------------



#LAYOUT DE FRAMES PARA INTRODUCIR DATOS
# Crear un frame para dar un margen respecto a los bordes
frame_ACAD_container = tk.Frame(AutoCAD_NB, background=blanco_roto)
frame_ACAD_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)




#-----DIBUJAR INTERCONEXIONADO

def dibujar_flechas_textos_strings():
    def proceso_dibujo_interconexion():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen
            AutoCAD_extension.CAD_draw_flechas_strings_texto(acad, all_blocks_inter, single_block_inter, bloque_inicial, n_bloques, max_c_block, max_bus, masc, strings_ID, DCBoxes_o_Inv_String, max_inv_block, max_str_pinv)
            
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
               
    def cerrar_ventana_tras_simular_dibujo_inter(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_Config_LV")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_interconexion():
        proceso_dibujo_interconexion()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_inter(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_interconexion) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_CAD_inter = tk.Button(frame_ACAD_container, text="Draw Interconnection", command=dibujar_flechas_textos_strings, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_inter.grid(row=1, column=0, pady=20)

entrada_all_blocks_inter = tk.BooleanVar(value=False)
all_blocks_inter = True
single_block_inter=1

def update_single_block_inter():
    global single_block_inter
    single_block_inter = int(spinbox_inter.get())

def activate_spinbox_inter():
    global all_blocks_inter, single_block_inter
    
    if entrada_all_blocks_inter.get():
        spinbox_inter.config(state='normal')
        all_blocks_inter=False
        single_block_inter = int(spinbox_inter.get())
    else:
        spinbox_inter.config(state='disabled')
        all_blocks_inter=True
        
#Marcador y spinbox para dibujar o leer un solo bloque
#TODO inicializar en el bloque real
bloque_inicial=1 #inicializamos bloque inicial en 1 para las spinbox antes de que se cargue el verdadero
spinbox_inter = tk.Spinbox(frame_ACAD_container, from_=1, to=100, state='disabled', command=update_single_block_inter, width=2, font=('Montserrat', 10))
spinbox_inter.grid(row=1, column=1, padx=5, pady=5, sticky='w')

check_inter = ttk.Checkbutton(frame_ACAD_container, text="Single block", variable=entrada_all_blocks_inter, command=activate_spinbox_inter)
check_inter.grid(row=1, column=2, padx=5, pady=5, sticky='w')



#-----DIBUJAR HARNESS
def dibujar_harness():
    def proceso_dibujo_harness():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen
            AutoCAD_extension.CAD_draw_Harness(acad, dos_polos, bloque_inicial, Harness_pos_ID, Harness_neg_ID)
            
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos    
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
               
    def cerrar_ventana_tras_simular_dibujo_harness(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_Config_LV")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_harness():
        proceso_dibujo_harness()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_harness(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_harness) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar harness    
boton_CAD_inter = tk.Button(frame_ACAD_container, text="Draw harnesses", command=dibujar_harness, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_inter.grid(row=2, column=0, pady=20)

#Checkbutton para dibujar ambos polos (recomendable si la interconexion es ida y vuelta)
entrada_dos_polos = tk.BooleanVar(value=False)
dos_polos = entrada_all_blocks_inter.get()

check_inter = ttk.Checkbutton(frame_ACAD_container, text="Both poles", variable=dos_polos)
check_inter.grid(row=2, column=1, padx=5, pady=5, sticky='w')





#---------DIBUJAR ZANJAS DC

def dibujar_zanjas_DC():
    def proceso_dibujo_zanjas_DC():
        global error_de_dibujo  
        error_de_dibujo='Sin error'

        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen
            AutoCAD_extension.CAD_draw_Zanjas_DC(acad, all_blocks_zdc, single_block_zdc, bloque_inicial, zanjas_DC_ID, PB_zanjas_DC_ID, n_tubos_max_DC1, ancho_DC1, ancho_DC2)
            
            
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'        
            traceback.print_exc()
            
    def cerrar_ventana_tras_dibujo_zdc(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_Config_LV")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_dibujar_zdc():
        proceso_dibujo_zanjas_DC()
        root.after(0, lambda: cerrar_ventana_tras_dibujo_zdc(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_dibujar_zdc) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_zdc_CAD_draw = tk.Button(frame_ACAD_container, text="Draw DC Trenches", command=dibujar_zanjas_DC, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_zdc_CAD_draw.grid(row=3, column=0, pady=20)

entrada_all_blocks_zdc = tk.BooleanVar(value=False)
all_blocks_zdc = True
single_block_zdc=1

def update_single_block_zdc():
    global single_block_zdc
    single_block_zdc = int(spinbox_zdc.get())

def activate_spinbox_zdc():
    global all_blocks_zdc, single_block_zdc
    
    if entrada_all_blocks_zdc.get():
        spinbox_zdc.config(state='normal')
        all_blocks_zdc=False
        single_block_zdc = int(spinbox_zdc.get())
    else:
        spinbox_zdc.config(state='disabled')
        all_blocks_zdc=True
        
#Marcador y spinbox para dibujar o leer un solo bloque
spinbox_zdc = tk.Spinbox(frame_ACAD_container, from_=1, to=100, state='disabled', command=update_single_block_zdc, width=2, font=('Montserrat', 10))
spinbox_zdc.grid(row=3, column=1, padx=5, pady=5, sticky='w')

check_zdc = ttk.Checkbutton(frame_ACAD_container, text="Single block", variable=entrada_all_blocks_zdc, command=activate_spinbox_zdc)
check_zdc.grid(row=3, column=2, padx=5, pady=5, sticky='w')



#---------DIBUJAR ZANJAS LV

def dibujar_zanjas_LV():
    def proceso_dibujo_zanjas_LV():
        global error_de_dibujo  
        error_de_dibujo='Sin error'

        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen
            AutoCAD_extension.CAD_draw_Zanjas_LV(acad, all_blocks_zlv, single_block_zlv, bloque_inicial, zanjas_LV_ID, PB_zanjas_LV_ID, DCBoxes_o_Inv_String)
            
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
            
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'        
            traceback.print_exc()
            
    def cerrar_ventana_tras_dibujo_zlv(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_Config_LV")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_dibujar_zlv():
        proceso_dibujo_zanjas_LV()
        root.after(0, lambda: cerrar_ventana_tras_dibujo_zlv(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_dibujar_zlv) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_zlv_CAD_draw = tk.Button(frame_ACAD_container, text="Draw LV Trenches", command=dibujar_zanjas_LV, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_zlv_CAD_draw.grid(row=4, column=0, pady=20)

entrada_all_blocks_zlv = tk.BooleanVar(value=False)
all_blocks_zlv = True
single_block_zlv=1

def update_single_block_zlv():
    global single_block_zlv
    single_block_zlv = int(spinbox_zlv.get())

def activate_spinbox_zlv():
    global all_blocks_zlv, single_block_zlv
    
    if entrada_all_blocks_zlv.get():
        spinbox_zlv.config(state='normal')
        all_blocks_zlv=False
        single_block_zlv = int(spinbox_zlv.get())
    else:
        spinbox_zlv.config(state='disabled')
        all_blocks_zlv=True
        
#Marcador y spinbox para dibujar o leer un solo bloque
spinbox_zlv = tk.Spinbox(frame_ACAD_container, from_=1, to=100, state='disabled', command=update_single_block_zlv, width=2, font=('Montserrat', 10))
spinbox_zlv.grid(row=4, column=1, padx=5, pady=5, sticky='w')

check_zlv = ttk.Checkbutton(frame_ACAD_container, text="Single block", variable=entrada_all_blocks_zlv, command=activate_spinbox_zlv)
check_zlv.grid(row=4, column=2, padx=5, pady=5, sticky='w')





#---------DIBUJAR ZANJAS AS

def dibujar_zanjas_AS():
    def proceso_dibujo_zanjas_AS():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen
            AutoCAD_extension.CAD_draw_zanjas_AS(acad, zanjas_AS_ID)
            
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
                                       
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
  
    def cerrar_ventana_tras_simular_dibujo_zanjas_AS(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_Earthing")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_zanjas_AS():
        proceso_dibujo_zanjas_AS()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_zanjas_AS(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_zanjas_AS) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_CAD_zanjas_AS = tk.Button(frame_ACAD_container, text="Draw AS Trenches", command=dibujar_zanjas_AS, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_zanjas_AS.grid(row=5, column=0, pady=20)



#------------DIBUJAR TODA LA PAT
def dibujar_PAT():
    def proceso_dibujo_PAT():
        global error_de_dibujo
        error_de_dibujo='Sin error'
        
        try:
            pythoncom.CoInitialize() #Inicializamos la API de autocad con python en el hilo secundario

            
            #Buscamos si está la referencia abierta y si no se crea un dibujo nuevo
            referencia = 'XREF_Unified.dwg'
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(referencia)
            if acad is None:
                error_de_dibujo='AutoCAD no abierto'
                return #se corta la funcion antes de seguir
            
            root.after(0,time.sleep(0.5)) #damos tiempo entre las funciones para evitar que AutoCAD se autobloquee al estar en un hilo secundario
            
            #Dibujamos con la funcion definida en la extension y guardamos las capas por si luego se leen
            AutoCAD_extension.CAD_draw_PAT(acad, bloque_inicial, n_bloques, all_blocks_PAT, single_block_PAT, max_b, max_f_str_b, max_c, max_tpf, PAT_latiguillo_entre_trackers, PAT_latiguillo_primera_pica, PAT_terminal_primera_pica, PAT_terminal_DC_Box, sep, dist_primera_pica_extremo_tr, zanjas_DC_ID, PB_zanjas_DC_ID, zanjas_LV_ID, PB_zanjas_LV_ID)
            
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
                                       
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
               
    def cerrar_ventana_tras_simular_dibujo_PAT(ventana_carga):
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_dibujo == 'Sin error':
                messagebox.showinfo("Drawing completed","Information added successfully to drawing. It is recommended to save it as XREF_Earthing")
                
            elif error_de_dibujo == 'AutoCAD no abierto':
                messagebox.showerror("Error", "AutoCAD could not be used, please check that AutoCAD is open.")
                
            elif error_de_dibujo == 'Interaccion con AutoCAD':
                messagebox.showerror("Error", "AutoCAD is busy. Please, do not interact with it while drawing.")
                
            else:
                messagebox.showerror("Error", "There was an error while drawing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_PAT():
        proceso_dibujo_PAT()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_PAT(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_PAT) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_CAD_PAT = tk.Button(frame_ACAD_container, text="Draw Earthing", command=dibujar_PAT, bg=rojo_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_PAT.grid(row=6, column=0, pady=20)

entrada_all_blocks_PAT = tk.BooleanVar(value=False)
all_blocks_PAT = True
single_block_PAT=1

def update_single_block_PAT():
    global single_block_PAT
    single_block_PAT = int(spinbox_PAT.get())

def activate_spinbox_PAT():
    global all_blocks_PAT, single_block_PAT
    
    if entrada_all_blocks_PAT.get():
        spinbox_PAT.config(state='normal')
        all_blocks_PAT=False
        single_block_PAT = int(spinbox_PAT.get())
    else:
        spinbox_PAT.config(state='disabled')
        all_blocks_PAT=True
        
#Marcador y spinbox para dibujar o leer un solo bloque
#TODO inicializar en el bloque real
bloque_inicial=1 #inicializamos bloque inicial en 1 para las spinbox antes de que se cargue el verdadero, al calcular bloque_inicial y n_bloques se cambian tanto from como to, 1 y 100 son solo para inicializar
spinbox_PAT = tk.Spinbox(frame_ACAD_container, from_=1, to=100, state='disabled', command=update_single_block_PAT, width=2, font=('Montserrat', 10))
spinbox_PAT.grid(row=6, column=1, padx=5, pady=5, sticky='w')

check_PAT = ttk.Checkbutton(frame_ACAD_container, text="Single block", variable=entrada_all_blocks_PAT, command=activate_spinbox_PAT)
check_PAT.grid(row=6, column=2, padx=5, pady=5, sticky='w')


# Ejecutar el bucle principal de la ventana
root.mainloop()



