# ============================================================================

# Pestaña 3: PV Plant Design
#   - listar_entradas_potencia(): organiza los formularios de potencia por bloque.
#   - simular_configuracion_LV(): calcula configuraciones de inversores, cajas y strings.
#   - dibujar_conf_LV(): envía la configuración LV al entorno de AutoCAD.
#   - simular_polilineas_cable_mv(): traza polilíneas para el cableado de media tensión.
#   - dibujar_array(): representa el cableado de arrays en AutoCAD y en la interfaz.
# ============================================================================

#3.---------------------------TERCERA PESTAÑA - CONFIGURACION ELECTRICA --------------------


#------LAYOUT DE FRAMES PARA INTRODUCIR DATOS
# Crear un frame para meter en él dos frames y darles un margen común respecto a los bordes
frame_DFV_container = tk.Frame(DFV, background=BLANCO_ROTO)
frame_DFV_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)

# Introducir un nuevo notebook para diferenciar diseños de configuracion de MV, configuracion de LV y routing de cables de potencia
notebook_DFV = ttk.Notebook(frame_DFV_container, style='TNotebook')
notebook_DFV.pack(fill=tk.BOTH, expand=True)

# Crear las pestañas con el color de fondo definido
MV_design = tk.Frame(notebook_DFV, background=BLANCO_ROTO)
LV_design = tk.Frame(notebook_DFV, background=BLANCO_ROTO)
Cable_routing_design = tk.Frame(notebook_DFV, background=BLANCO_ROTO)

# Añadir las pestañas al notebook
notebook_DFV.add(MV_design, text='MV Configuration')
notebook_DFV.add(LV_design, text='LV Configuration')
notebook_DFV.add(Cable_routing_design, text='Main Cable Routing')





#------Frames MV
frame_MV_container= tk.Frame(MV_design, background=BLANCO_ROTO)
frame_MV_container.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

# Configurar la cuadrícula para partir el frame_DFV_container en dos verticales, uno para los datos y otro para una ventana de dibujos explicativos
frame_MV_container.grid_rowconfigure(0, weight=1)
frame_MV_container.grid_columnconfigure(0, weight=1)  
frame_MV_container.grid_columnconfigure(1, weight=1) 

    #Creamos subframe a la izquierda para meter potencia de las lineas y a la derecha para meter la configuracion
frame_MV_power = tk.Frame(frame_MV_container, background=BLANCO_ROTO)
frame_MV_power.grid(row=0, column=0, sticky='nsew', padx=10, pady=0)

frame_MV_lines = tk.Frame(frame_MV_container, background=BLANCO_ROTO)
frame_MV_lines.grid(row=0, column=1, sticky='nsew', padx=50, pady=0)


#------Frames LV
frame_LV_container = tk.Frame(LV_design, background=BLANCO_ROTO)
frame_LV_container.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
# Configurar la cuadrícula para partir el frame_DFV_container en tres verticales, uno para los datos y el boton de simulacion, otro para datos extra segun DCBoxes o INV string y otro para los botones de dibujo y lectura
frame_LV_container.grid_rowconfigure(0, weight=2)
frame_LV_container.grid_rowconfigure(1, weight=1)
frame_LV_container.grid_columnconfigure(0, weight=1)
frame_LV_container.grid_columnconfigure(1, weight=1)    
frame_LV_container.grid_columnconfigure(2, weight=1) 

# Creamos el frame para los datos de entrada y el boton de simulacion
frame_DLV_data = tk.Frame(frame_LV_container, background=BLANCO_ROTO)
frame_DLV_data.grid(row=0, column=0, sticky='nsew', padx=50, pady=0)

#     #Creamos la matriz que lo parta en cuatro filas para añadir luego mas subframes
# frame_DLV_data.grid_rowconfigure(0, weight=1)
# frame_DLV_data.grid_rowconfigure(1, weight=1)
# frame_DLV_data.grid_rowconfigure(2, weight=1)
# frame_DLV_data.grid_rowconfigure(3, weight=1)

#         #Añadimos el subframe de la interconexion el primero y el resto
# frame_DLV_inter = tk.Frame(frame_DLV_data, background=BLANCO_ROTO)
# frame_DLV_inter.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

#         #Configuracion LV
# frame_DLV_Config = tk.Frame(frame_DLV_data, background=BLANCO_ROTO)
# frame_DLV_Config.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)

#         #Posicion de cajas, nº de inversores y tipo de cable
# frame_DFV_caj_cable = tk.Frame(frame_DLV_data, background=BLANCO_ROTO)
# frame_DFV_caj_cable.grid(row=2, column=0, sticky='nsew', padx=0, pady=0)

#         #Para boton de simulacion
# frame_DLV_data_exe = tk.Frame(frame_DLV_data, background=BLANCO_ROTO)
# frame_DLV_data_exe.grid(row=3, column=0, sticky='nsew', padx=0, pady=0)

# Creamos el frame para las entradas extras de Inv de String y DCBoxes
frame_DLV_extra = tk.Frame(frame_LV_container, background=BLANCO_ROTO)
frame_DLV_extra.grid(row=0, column=1, sticky='nsew', padx=25, pady=0)

# Creamos el frame para el boton de simulacion
frame_DLV_sim = tk.Frame(frame_LV_container, background=BLANCO_ROTO)
frame_DLV_sim.grid(row=0, column=2, sticky='nsew', padx=25, pady=0)

# Creamos subframes para dibujo y lectura dependiendo de si es dcbox o inv de strings
frame_DLV_CAD = tk.Frame(frame_LV_container, background=BLANCO_ROTO)
frame_DLV_CAD.grid(row=1, column=1, sticky='nsew', padx=25, pady=20)

frame_DCB_buttons = tk.Frame(frame_DLV_CAD, background=BLANCO_ROTO)
frame_DCB_buttons.grid(row=0, column=0, columnspan=3, sticky='nsew')

frame_IS_buttons = tk.Frame(frame_DLV_CAD, background=BLANCO_ROTO)
frame_IS_buttons.grid(row=0, column=0, columnspan=3, sticky='nsew')
frame_DCB_buttons.grid_remove()
frame_IS_buttons.grid_remove()



#------Frames Cable Routing
frame_routing_container= tk.Frame(Cable_routing_design, background=BLANCO_ROTO)
frame_routing_container.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

# Configurar la cuadrícula para partir el frame_DFV_container en tres verticales, uno para MV, otro para subarray y otro para array
frame_routing_container.grid_rowconfigure(0, weight=1) 
frame_routing_container.grid_columnconfigure(0, weight=1)  
frame_routing_container.grid_columnconfigure(1, weight=1)  
frame_routing_container.grid_columnconfigure(2, weight=1)  


# Creamos el frame para incluir los procesos en los tres campos
frame_MV_routing = tk.Frame(frame_routing_container, background=BLANCO_ROTO)
frame_MV_routing.grid(row=0, column=0, sticky='nsew', padx=50, pady=0)

frame_Subarray_routing = tk.Frame(frame_routing_container, background=BLANCO_ROTO)
frame_Subarray_routing.grid(row=0, column=1, sticky='nsew', padx=50, pady=0)

frame_Array_routing = tk.Frame(frame_routing_container, background=BLANCO_ROTO)
frame_Array_routing.grid(row=0, column=2, sticky='nsew', padx=50, pady=0)











#3.1-------------- PESTAÑA MEDIA TENSION


#-------Potencia de los bloques
entradas_potencia_bloques = []  # Lista de tuplas: (Entry, StringVar)

def listar_entradas_potencia(valores_potencia_bloques):
    """Prepara la lista de parámetros relacionados con entradas la potencia."""
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
    """Aplica ajustes comunes sobre valor comun."""
    try:
        valor = int(valor_comun_potencia.get())
        for entry, var in entradas_potencia_bloques:
            var.set(str(valor))
    except ValueError:
        print("Introduce un valor numérico válido.")

boton_aplicar_valor = ttk.Button(frame_MV_power, text="Set All", command=aplicar_valor_comun)
boton_aplicar_valor.grid(row=1, column=0, pady=(20, 5), padx=(100, 5), sticky='w')



def leer_potencia_bloques():
    """Lee los valores de la potencia los bloques introducidos en la interfaz."""
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



boton_leer_potencias = tk.Button(frame_MV_power, text="Read Values", command=leer_potencia_bloques, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_leer_potencias.grid(row=2, column=0, pady=50, padx=5)




#----Definir lineas MV

    #Crear entradas
entradas_lineas_MV = []
fila_actual_MV = 1

def agregar_linea_MV(frame):
    """Añade una nueva entrada relacionada con la línea MV."""
    global entradas_lineas_MV, contador_tramos_MV, fila_actual_MV

    fila_frame = ttk.Frame(frame)
    fila_frame.grid(row=fila_actual_MV, column=0, columnspan=3, sticky="w", pady=5)

    etiqueta = ttk.Label(fila_frame, text=f"Line {len(entradas_lineas_MV) + 1}")
    etiqueta.grid(row=0, column=0, padx=5)

    entradas_lineas_MV.append([etiqueta, []])
    contador_tramos_MV = 0
    fila_actual_MV += 1


def agregar_tramo_linea_MV(frame):
    """Añade una nueva entrada relacionada con el tramo la línea MV."""
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
    """Elimina el último elemento definido para ultimo elemento MV."""
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
    """Carga los datos almacenados para entradas las líneas MV en la interfaz."""
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
    """Lee los valores de MV introducidos en la interfaz."""
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


boton_leer_MV = tk.Button(frame_MV_lines, text="Read Values", command=leer_valores_MV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_leer_MV.grid(row=2, column=0, pady=50, padx=5)







#3.2----------PESTAÑA CONFIGURACION LV


#CREAR COMBOBOXES
def comboboxes_entradas_DFV(valores_comboboxes_DFV,valores_entradas_DFV, reiniciar_inv):
    """Inicializa los desplegables y entradas del diseño de la planta fotovoltaica."""
    global entrada_DCBoxes_o_Inv_String, entrada_Interconexionado, entrada_Polo_cercano, entrada_Posicion_optima_caja, entrada_n_inv, entrada_dif_str_inv, dos_inv
    
    #-------ENTRADAS COMUNES CONFIG LV
    #ENTRADAS INTERCONEXIONADO DE MODULOS
  
    #Combobox para el tipo de interconexion de modulos
    Interconnection_options = ["Daisy chain", "Leapfrog"]
    entrada_Interconexionado = tk.StringVar(value = valores_comboboxes_DFV[0])
    
    etiqueta_interconexion = tk.Label(frame_DLV_data, text='PV Modules Interconnection', fg=ROJO_GRS, font=('Montserrat', 10, 'bold'))
    etiqueta_interconexion.grid(row=0, column=0, pady=(25,0))
    combobox_inter=ttk.Combobox(frame_DLV_data, textvariable=entrada_Interconexionado, values=Interconnection_options)
    combobox_inter.grid(row=1, column=0, pady=(5,20))
    
    
    #Combobox para el polo mas cercano a cajas o inversores
    closer_pole_option = ["Positive", "Negative"]
    entrada_Polo_cercano = tk.StringVar(value = valores_comboboxes_DFV[1])
    
    etiqueta_polo = tk.Label(frame_DLV_data, fg=ROJO_GRS, text='Closer Pole', font=('Montserrat', 10, 'bold'))
    etiqueta_polo.grid(row=2, column=0)
    combobox_polo = ttk.Combobox(frame_DLV_data, textvariable=entrada_Polo_cercano, values=closer_pole_option)
    combobox_polo.grid(row=3, column=0, pady=(5,0))
            
    
    #DISEÑO CAJAS O INV
    
    #Combobox para las opciones LV
    opciones_LV = ["DC Boxes", "String Inverters"]
    entrada_DCBoxes_o_Inv_String = tk.StringVar(value = valores_comboboxes_DFV[2])
    
    etiqueta_DCBIS = tk.Label(frame_DLV_data, text='LV Configuration', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_DCBIS.grid(row=4, column=0, columnspan=1)
    combobox_DCBIS=ttk.Combobox(frame_DLV_data, textvariable=entrada_DCBoxes_o_Inv_String, values=opciones_LV)
    combobox_DCBIS.grid(row=5, column=0, columnspan=1, pady=(5,20))
    combobox_DCBIS.bind("<<ComboboxSelected>>", lambda e: on_lv_config_change())
    
    #ENTRADAS POSICION CAJAS O INV Y Nº INV/PCS
    
    # Hacemos Combobox para definir la posicion optima de la caja
    Posicion_optima_caja_options = ["Edge", "Center"]
    entrada_Posicion_optima_caja = tk.StringVar(value = valores_comboboxes_DFV[3])
    
    tk.Label(frame_DLV_data, text='DCB/SI Optimal location', fg=ROJO_GRS, font=('Montserrat', 10, 'bold')).grid(row=6, column=0)
    ttk.Combobox(frame_DLV_data, textvariable=entrada_Posicion_optima_caja, values=Posicion_optima_caja_options).grid(row=7, column=0, pady=(5,10))
    
    #Entradas y Combobox para el nº de inversores o cuadros, si es 2 se activa una entrada manual para introducir el maximo desequilibrio de strings entre ellos y un tick de si se reinicia la cuenta por board o no
    etiqueta_dif_str_inv = tk.Label(frame_DLV_data, text="Max. Str. Unbalance", fg=ROJO_GRS, bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold'))
    etiqueta_dif_str_inv.grid(row=9, column=0)
    valor_dif_str_inv = tk.StringVar()
    valor_dif_str_inv.set(valores_entradas_DFV[0])
    entrada_dif_str_inv = tk.Entry(frame_DLV_data, width=5)
    entrada_dif_str_inv.grid(row=9, column=1)
    
    def activar_equilibrio_strings(entrada):
        """Activa o desactiva opciones relacionadas con el equilibrio los strings."""
        global dos_inv
        if entrada == "2":
            entrada_dif_str_inv.config(state='normal')
            dos_inv = True
        else:
            entrada_dif_str_inv.config(state='disabled')
            dos_inv = False
            
    n_inv_options = ["1", "2"]
    entrada_n_inv = tk.StringVar(value = valores_comboboxes_DFV[5])
    
    etiqueta_n_inv = tk.Label(frame_DLV_data, text='No. inv.', fg=ROJO_GRS, font=('Montserrat', 10, 'bold'))
    etiqueta_n_inv.grid(row=8, column=0)
    combobox_n_inv = ttk.Combobox(frame_DLV_data, textvariable=entrada_n_inv, values=n_inv_options, width=5)
    combobox_n_inv.grid(row=8, column=1)
    combobox_n_inv.bind("<<ComboboxSelected>>", lambda event: activar_equilibrio_strings(entrada_n_inv.get()))
    
    
    entrada_reiniciar_inv = tk.BooleanVar(value=reiniciar_inv)
    def activar_reinicio_inv_en_board():
        """Activa o desactiva las opciones de reinicio de inversores en el cuadro."""
        global reiniciar_inv        
        if entrada_reiniciar_inv.get():
            reiniciar_inv=True
        else:
            reiniciar_inv=False
            
    etiqueta_reiniciar_inv = tk.Label(frame_DLV_data, text='Restart inv.', fg=ROJO_GRS, font=('Montserrat', 10, 'bold'))
    etiqueta_reiniciar_inv.grid(row=10, column=0)
    check_reiniciar_inv = ttk.Checkbutton(frame_DLV_data, variable=entrada_reiniciar_inv, command=activar_reinicio_inv_en_board)
    check_reiniciar_inv.grid(row=10, column=1, padx=5, pady=5, sticky='w')

    
    
    #--------ENTRADAS EXTRA PARA DC BOXES-----------
    def mostrar_configuracion_dc_boxes():
        """Muestra la configuración de cajas DC dentro de la interfaz."""
        global entrada_String_o_Bus, valor_masc, valor_misc
        
        for widget in frame_DLV_extra.winfo_children():
            widget.destroy()
        #Entradas manuales para el maximo y minimo numero de strings por caja
        etiqueta_n_strings_caja = tk.Label(frame_DLV_extra, text="Number of strings per DC Box", fg=ROJO_GRS, bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold'))
        etiqueta_n_strings_caja.grid(row=0, column=0, columnspan=1)
        
        etiqueta_masc = tk.Label(frame_DLV_extra, text="Max", fg=ROJO_GRS, bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold'))
        etiqueta_masc.grid(row=1, column=0)
        valor_masc = tk.StringVar()
        valor_masc.set(valores_entradas_DFV[1])
        entrada_masc = tk.Entry(frame_DLV_extra, textvariable=valor_masc, width=10)
        entrada_masc.grid(row=2, column=0, pady=(5,20))
        
        etiqueta_misc = tk.Label(frame_DLV_extra, text="Min", fg=ROJO_GRS, bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold'))
        etiqueta_misc.grid(row=1, column=1)
        valor_misc = tk.StringVar()
        valor_misc.set(valores_entradas_DFV[2])
        entrada_misc = tk.Entry(frame_DLV_extra, textvariable=valor_misc, width=10)
        entrada_misc.grid(row=2, column=1, pady=(5,20))
    
        #Combobox para el tipo de configuracion LVDC
        LVDC_cable_option = ["String Cable", "DC Bus", "Both types", "Mixed"]
        entrada_String_o_Bus = tk.StringVar(value = valores_comboboxes_DFV[4])
        
        etiqueta_main_cable_dc = tk.Label(frame_DLV_extra, text='DC cable configuration', fg=ROJO_GRS, font=('Montserrat', 10, 'bold'))
        etiqueta_main_cable_dc.grid(row=3, column=0)
        combobox_main_cable_dc = ttk.Combobox(frame_DLV_extra, textvariable=entrada_String_o_Bus, values=LVDC_cable_option)
        combobox_main_cable_dc.grid(row=4, column=0, pady=(5,20))
    

    #--------ENTRADAS EXTRA PARA INV STRING-----------
    
    def mostrar_configuraciones_string_inverters(config_inicial=None):
        """Muestra la configuración de los inversores string dentro de la interfaz."""
        global valor_dist_max_inter_bandas, valor_lim_str_interc
        
        for widget in frame_DLV_extra.winfo_children():
            widget.destroy()
        
        # Frame para parámetros superiores
        frame_parametros = ttk.Frame(frame_DLV_extra)
        frame_parametros.grid(row=0, column=0, sticky='ew', padx=10, pady=(5, 0))
            
        #Entrada de distancia y n maxima de intercambio de strings entre bandas
        etiqueta_dist_max_inter_bandas = tk.Label(frame_parametros, fg=ROJO_GRS, bg=BLANCO_ROTO, text="Max distance inter-bands", font=('Montserrat', 10, 'bold'))
        etiqueta_dist_max_inter_bandas.grid(row=0, column=0, sticky='w')
        valor_dist_max_inter_bandas = tk.StringVar()
        valor_dist_max_inter_bandas.set(dist_max_inter_bandas)
        entrada_dist_max_inter_bandas = ttk.Entry(frame_parametros, textvariable=valor_dist_max_inter_bandas, width=5)   #Valor maximo de separacion entre bandas para poder intercambiar strings, si lo damos muy alto el problema es que dos bandas que queriamos que fuesen independientes se puedan asociar, cargando mucho los calculos si hay bloques de bandas
        entrada_dist_max_inter_bandas.grid(row=0, column=1, padx=(5, 20))
        
        
        etiqueta_lim_str_interc = tk.Label(frame_parametros, fg=ROJO_GRS, bg=BLANCO_ROTO, text="Max inter-strings", font=('Montserrat', 10, 'bold'))
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
            """Añade una nueva entrada relacionada con configuración."""
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
            """Lee los valores de configuraciones introducidos en la interfaz."""
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
        """Actualiza la interfaz cuando cambian los parámetros de configuración LV."""
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
    """Calcula la asignación de strings y cajas DC en función del layout."""
    global strings_ID , DCBoxes_ID, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs, filas_con_cable_string, max_bus, tipos_cajas_por_entradas, TOT_n_cajas_str, TOT_n_cajas_bus, TOT_n_cajas_mix, TOT_n_cajas
    
    #Dependiendo de la opcion de LVDC se va por una nomenclatura u otra   
    if String_o_Bus == 'String Cable':   
        strings_ID , DCBoxes_ID, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs = alg_subestacion_at.ID_strings_y_cajas_para_Cable_de_String(strings_fisicos,filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_c,max_c_block,max_b, max_spf, max_f_str_b,masc, dist_ext_opuesto_str, dos_inv)  
        filas_con_cable_string=np.ones((n_bloques+1,max_b,max_f_str_b),dtype=bool) #necesario definirlo aqui aunque vaya a ser true siempre para poder usar despues la misma funcion de medicion y perdidas en las configuraciones mixtas
            
    elif String_o_Bus == 'DC Bus':
        strings_ID , DCBoxes_ID, max_bus, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs = alg_subestacion_at.ID_strings_y_cajas_para_DC_Bus(strings_fisicos,filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_c,max_c_block,max_b, max_spf, max_f_str_b,masc, dist_ext_opuesto_str, dos_inv)
        filas_con_cable_string=np.zeros((n_bloques+1,max_b,max_f_str_b),dtype=bool) #necesario definirlo aqui aunque vaya a ser np.nan para usar la misma funcion de harness en los tres casos
        
        guardar_variables([max_bus],['max_bus'])
        
    elif String_o_Bus == 'Both types':
        lim_cable_string=2      
        strings_ID , DCBoxes_ID, max_bus, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs, filas_con_cable_string = alg_subestacion_at.ID_strings_y_cajas_para_config_mixtas(strings_fisicos,filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_c,max_c_block,max_b,max_spf, max_f_str_b,masc, dist_ext_opuesto_str, String_o_Bus,lim_cable_string, dos_inv)

        guardar_variables([max_bus],['max_bus'])
        
    elif String_o_Bus == 'Mixed':
        lim_cable_string=2
        strings_ID , DCBoxes_ID, max_bus, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs, filas_con_cable_string = alg_subestacion_at.ID_strings_y_cajas_para_config_mixtas(strings_fisicos,filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_c,max_c_block,max_b,max_spf, max_f_str_b,masc, dist_ext_opuesto_str, String_o_Bus,lim_cable_string, dos_inv)
        
        guardar_variables([max_bus],['max_bus'])
    
    #Sacamos los tipos de DC_Boxes, se usa la misma funcion en todos los casos
    DCBoxes_ID, tipos_cajas_por_entradas, TOT_n_cajas_str, TOT_n_cajas_bus, TOT_n_cajas_mix, TOT_n_cajas = alg_subestacion_at.calculo_DC_Boxes(bloque_inicial, n_bloques, max_b, max_c, max_f_str_b, max_c_block, masc, filas_en_cajas, String_o_Bus, filas_con_cable_string, equi_ibc, DCBoxes_ID, cajas_fisicas)
    
    #Guardar variables en el dicionario
    guardar_variables([strings_ID , DCBoxes_ID, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs, filas_con_cable_string, dos_inv, tipos_cajas_por_entradas, TOT_n_cajas_str, TOT_n_cajas_bus, TOT_n_cajas_mix, TOT_n_cajas],['strings_ID' , 'DCBoxes_ID', 'equi_ibfs', 'equi_ibc', 'equi_reverse_ibc','equi_reverse_ibfs','filas_con_cable_string', 'dos_inv','tipos_cajas_por_entradas', 'TOT_n_cajas_str', 'TOT_n_cajas_bus', 'TOT_n_cajas_mix', 'TOT_n_cajas'])


def simular_configuracion_LV():
    """Simula configuración LV y actualiza los resultados."""
    def proceso_simular_configuracion_LV():
        """Ejecuta el proceso auxiliar encargado de simular configuración LV."""
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
                filas_en_cajas, max_c, max_c_block  = alg_subestacion_at.filas_config_cajas_sin_mezclar_filas(strings_fisicos, bloque_inicial, n_bloques, max_b, max_f_str_b, misc, masc)
                cajas_fisicas = alg_subestacion_at.cajas_desde_filas_asociadas(strings_fisicos, filas_en_cajas, orientacion, coord_PCS_DC_inputs, sep_caja_tracker, Posicion_optima_caja, bloque_inicial,n_bloques,max_b,max_f_str_b, max_c)
                
                #Evaluamos si hay uno o dos inversores por bloque y ajustamos variables dependientes
                if n_inv == "2":
                    dos_inv_por_bloque=True
                    lim_str_dif=int(entrada_dif_str_inv.get())
                    cajas_fisicas = alg_subestacion_at.repartir_cajas_en_dos_inversores(cajas_fisicas, coord_PCS_DC_inputs, lim_str_dif, bloque_inicial,n_bloques, max_b, max_c)
                    
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
                    alg_subestacion_at.combinacion_inv_en_bandas_optima(
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
                almacen_strings = alg_subestacion_at.intercambio_strings_por_proximidad_a_puente(
                    bloque_inicial, n_bloques, max_b, max_f_str_b, max_tpf, strings_fisicos,
                    matriz_intercambios_optima, puentes_fisicos, criterio_ceder_strings,
                    puntos_usados_global, orientacion
                )
                
                # 3 ASIGNACIÓN DE STRINGS A INVERSORES
                inv_string, max_inv, max_inv_block, max_str_pinv, equi_ibv_to_fs = (
                    alg_subestacion_at.asignar_strings_a_inversores(
                        bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, strings_fisicos,
                        conf_inversores, combinacion_optima, almacen_strings,
                        ori_str_ID, orientacion, puntos_usados_global,
                        criterio_ceder_strings, puentes_fisicos
                    )
                )
                ori_str_ID =  alg_subestacion_at.aplicar_flip_strings(
                    bloque_inicial, n_bloques, max_b, max_inv, max_str_pinv,
                    equi_ibv_to_fs, ori_str_ID, orientacion, strings_fisicos
                )

                # 4 POSICIONAMIENTO FÍSICO DE LOS INVERSORES
                inv_string[:, :, :, 0], comienzos_filas_strings = alg_subestacion_at.posicion_inv_string(
                    inv_string, strings_fisicos, sep_caja_tracker, coord_PCS_DC_inputs, contorno_bandas,
                    Posicion_optima_caja, equi_ibv_to_fs, orientacion, almacen_strings
                )
                posiciones_inv=inv_string[:, :, :, 0]
                # 5 AJUSTE PARA DOBLE INVERSOR (si aplica)
                if n_inv == "2":
                    dos_inv_por_bloque = True
                    lim_str_dif = int(entrada_dif_str_inv.get())
                    inv_string = alg_subestacion_at.repartir_inversores_en_dos_cuadros(
                        inv_string, coord_PCS_DC_inputs, lim_str_dif, bloque_inicial, n_bloques, max_b, max_inv, max_str_pinv
                    )
                    guardar_variables([lim_str_dif], ['lim_str_dif'])
                else:
                    dos_inv_por_bloque = False
                
                # 6 ASIGNACIÓN DE IDs DE STRINGS E INVERSORES
                strings_ID, String_Inverters_ID, equi_ibv, equi_reverse_ibv, inv_string, equi_ibv_to_fs = alg_subestacion_at.ID_strings_e_inv_string(
                    bloque_inicial, n_bloques, max_b, max_inv, max_inv_block, max_str_pinv,
                    inv_string, dos_inv_por_bloque, equi_ibv_to_fs, strings_fisicos, dist_ext_opuesto_str, ori_str_ID, orientacion
                )
                
                # 7 CREACION DE INV FISICOS (EQUIVALENTE A CAJAS FISICAS) Y FILAS_EN_INVERSORES (EQUIVALENTE A FILAS EN CAJA PARA INV DE STRING DE BANDA UNICA, USADO PARA TIRAR POLILINEAS DE CABLE)
                inv_como_cajas_fisicas = alg_subestacion_at.obtener_inv_fisicos(bloque_inicial, n_bloques, max_b, max_inv, inv_string)
                filas_en_inv_como_filas_en_cajas = alg_subestacion_at.obtener_filas_en_inv_como_filas_en_cajas(bloque_inicial, n_bloques, max_b, max_f_str_b, strings_fisicos)                
                
                guardar_variables([dist_max_inter_bandas, lim_str_interc, combinacion_optima, ganancias_perdidas_optima, matriz_intercambios_optima, puentes_fisicos, almacen_strings], ['dist_max_inter_bandas', 'lim_str_interc', 'combinacion_optima', 'ganancias_perdidas_optima', 'matriz_intercambios_optima', 'puentes_fisicos', 'almacen_strings'])
                
                guardar_variables([inv_string, max_inv, max_inv_block, max_str_pinv, equi_ibv_to_fs, dos_inv_por_bloque, reiniciar_inv, posiciones_inv, strings_ID, String_Inverters_ID, equi_ibv, equi_reverse_ibv, inv_como_cajas_fisicas, filas_en_inv_como_filas_en_cajas], ['inv_string', 'max_inv', 'max_inv_block', 'max_str_pinv', 'equi_ibv_to_fs', 'dos_inv_por_bloque', 'reiniciar_inv', 'posiciones_inv', 'strings_ID', 'String_Inverters_ID', 'equi_ibv', 'equi_reverse_ibv', 'inv_como_cajas_fisicas', 'filas_en_inv_como_filas_en_cajas'])
                                                                                                                                     

            guardar_variables([Interconexionado,Polo_cercano,DCBoxes_o_Inv_String, String_o_Bus, Posicion_optima_caja, n_inv,filas_con_cable_string],['Interconexionado','Polo_cercano','DCBoxes_o_Inv_String', 'String_o_Bus', 'Posicion_optima_caja','n_inv','filas_con_cable_string'])
        
        except:
            
             error_de_simulacion = 'Error'
             traceback.print_exc()
             
    def cerrar_ventana_tras_simular_LV(ventana_carga):
        """Cierra la ventana de carga tras  simular LV."""
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
        """Coordina la tarea asíncrona número 4."""
        proceso_simular_configuracion_LV()
        root.after(0, lambda: cerrar_ventana_tras_simular_LV(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_4) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
    
boton_LV = tk.Button(frame_DLV_sim, text="Simulate", command=simular_configuracion_LV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_LV.grid(row=0, column=0, pady=20)

var_com_uni_o_multipolar = 'Single Core' #inicializamos esta variable fuera de las funciones para cuando se cargue por primera vez, sin interferir en las importadas






#-------DIBUJAR Y LEER CONFIGURACION DE CAJAS
#Dibujar envolventes asociando filas a cajas
def dibujar_conf_LV():
    """Dibuja configuración LV con los datos actuales."""
    def proceso_dibujo_LV():
        """Ejecuta el proceso auxiliar encargado de dibujo LV."""
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
        """Cierra la ventana de carga tras  simular dibujo LV."""
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
        """Coordina la tarea asíncrona número 5."""
        proceso_dibujo_LV()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_LV(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_5) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_LV_CAD_draw = tk.Button(frame_DLV_CAD, text="Draw", command=dibujar_conf_LV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_LV_CAD_draw.grid(row=1, column=0, pady=20)

entrada_all_blocks_lv = tk.BooleanVar(value=False)
all_blocks_lv = True
single_block_lv=1 #se inicializa fuera del checkbutton para que permita dibujar todos los bloques de golpe sin que falte por definirse, luego cambia de valor sola

def update_single_block_lv():
    """Actualiza el bloque seleccionado asociado a LV."""
    global single_block_lv
    single_block_lv = int(spinbox_lv.get())

def activate_spinbox_lv():
    """Gestiona el estado del selector de bloque para LV."""
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
    """Lee los valores de configuración LV introducidos en la interfaz."""
    def proceso_leer_conf_LV():
        
        """Ejecuta el proceso auxiliar encargado de leer configuración LV."""
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
                    cajas_fisicas = alg_subestacion_at.cajas_desde_filas_asociadas(strings_fisicos, filas_en_cajas, orientacion, coord_PCS_DC_inputs, sep_caja_tracker,Posicion_optima_caja, bloque_inicial,n_bloques,max_b,max_f_str_b, max_c)
                                    
                    ID_strings_y_DCBoxes()
                    
                    #guardamos en el diccionario los valores actualizados (los de ID_strings_y_DC_Boxes se guardan dentro de la propia funcion)
                    guardar_variables([filas_en_cajas, max_c, max_c_block, cajas_fisicas],['filas_en_cajas', 'max_c', 'max_c_block', 'cajas_fisicas'])
                else:
                    
                     #Inv de string
                    inv_string, equi_ibv_to_fs = salida_leida
                    
                    #Revisamos el almacen de string intercambiados para incluir cambios introducidos a mano (se necesita para las posiciones de los inversores compartidos)
                    almacen_strings = alg_subestacion_at.reconstruir_almacen_strings_y_puentes(inv_string, strings_fisicos, contorno_bandas, bloque_inicial, n_bloques, max_b, max_inv, max_str_pinv)
                   
                    #ACTUALIZAMOS COMO EN EL ALGORITMO INICIAL
                    ori_str_ID = alg_subestacion_at.aplicar_flip_strings(
                        bloque_inicial, n_bloques, max_b, max_inv, max_str_pinv,
                        equi_ibv_to_fs, ori_str_ID, orientacion, strings_fisicos
                    )

                    # POSICIONAMIENTO FÍSICO DE LOS INVERSORES
                    inv_string[:, :, :, 0], comienzos_filas_strings = alg_subestacion_at.posicion_inv_string(
                        inv_string, strings_fisicos, sep_caja_tracker, coord_PCS_DC_inputs, contorno_bandas,
                        Posicion_optima_caja, equi_ibv_to_fs, orientacion, almacen_strings
                    )
                    posiciones_inv=inv_string[:, :, :, 0]
                    
                    #Info fisica
                    inv_como_cajas_fisicas = alg_subestacion_at.obtener_inv_fisicos(bloque_inicial, n_bloques, max_b, max_inv, inv_string)
                    
                    # ASIGNACIÓN DE IDs DE STRINGS E INVERSORES
                    strings_ID, String_Inverters_ID, equi_ibv, equi_reverse_ibv, inv_string, equi_ibv_to_fs = alg_subestacion_at.ID_strings_e_inv_string(
                        bloque_inicial, n_bloques, max_b, max_inv, max_inv_block, max_str_pinv,
                        inv_string, dos_inv_por_bloque, equi_ibv_to_fs, strings_fisicos, dist_ext_opuesto_str, ori_str_ID, orientacion,
                        False, None
                    )
                    
                    #VERIFICACION EN LAYOUTS COMPLICADOS
                    inv_string, equi_ibv_to_fs, equi_ibv, equi_reverse_ibv = AutoCAD_extension.CAD_read_tercer_barrido_configuracion(acad, capas_de_envolventes, bloque_inicial, n_bloques, max_inv_block, max_str_pinv, dos_inv_por_bloque, strings_ID, inv_string, equi_ibv, equi_reverse_ibv, 
                                                                                                                                                 equi_ibv_to_fs, max_b, max_inv, strings_fisicos)
                    ori_str_ID = alg_subestacion_at.aplicar_flip_strings(
                        bloque_inicial, n_bloques, max_b, max_inv, max_str_pinv,
                        equi_ibv_to_fs, ori_str_ID, orientacion, strings_fisicos
                    )
                    
                    # Recalcular camino a strings ID
                    inv_string[:, :, :, 0], comienzos_filas_strings = alg_subestacion_at.posicion_inv_string(
                        inv_string, strings_fisicos, sep_caja_tracker, coord_PCS_DC_inputs, contorno_bandas,
                        Posicion_optima_caja, equi_ibv_to_fs, orientacion, almacen_strings
                    )
                    posiciones_inv=inv_string[:, :, :, 0]
                    
                    inv_como_cajas_fisicas = alg_subestacion_at.obtener_inv_fisicos(bloque_inicial, n_bloques, max_b, max_inv, inv_string)
                    
                    strings_ID, String_Inverters_ID, equi_ibv, equi_reverse_ibv, inv_string, equi_ibv_to_fs = alg_subestacion_at.ID_strings_e_inv_string(
                        bloque_inicial, n_bloques, max_b, max_inv, max_inv_block, max_str_pinv,
                        inv_string, dos_inv_por_bloque, equi_ibv_to_fs, strings_fisicos, dist_ext_opuesto_str, ori_str_ID, orientacion,
                        True, equi_ibv
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
        """Cierra la ventana de carga tras  leer configuración LV."""
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
        """Coordina la tarea asíncrona número 6."""
        proceso_leer_conf_LV()
        root.after(0, lambda: cerrar_ventana_tras_leer_conf_LV(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_6) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
boton_LV_CAD_read = tk.Button(frame_DLV_CAD, text="Read changes", command=leer_conf_LV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_LV_CAD_read.grid(row=3, column=0, pady=20)


 


#--------DIBUJAR Y LEER POSICION DE CAJAS
def dibujar_DC_Boxes():
    """Dibuja DC las cajas con los datos actuales."""
    def proceso_dibujo_DC_Boxes():
        """Ejecuta el proceso auxiliar encargado de dibujo DC las cajas."""
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
        """Cierra la ventana de carga tras  simular dibujo las DC boxes."""
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
        """Coordina la tarea asíncrona para las DC boxes."""
        proceso_dibujo_DC_Boxes()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_dcboxes(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_dcboxes) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_CAD_dcboxes = tk.Button(frame_DLV_CAD, text="Draw DC Boxes/Str. Inv.", command=dibujar_DC_Boxes, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_dcboxes.grid(row=1, column=2, pady=10)

entrada_all_blocks_dcboxes = tk.BooleanVar(value=False)
all_blocks_dcboxes = True
single_block_dcboxes=1

def update_single_block_dcboxes():
    """Actualiza el bloque seleccionado asociado a las DC boxes."""
    global single_block_dcboxes
    single_block_dcboxes = int(spinbox_dcboxes.get())

def activate_spinbox_dcboxes():
    """Gestiona el estado del selector de bloque para las DC boxes."""
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
    """Lee los valores de la posición DC las cajas introducidos en la interfaz."""
    def proceso_leer_posicion_DC_Boxes():
        """Ejecuta el proceso auxiliar encargado de leer la posición DC las cajas."""
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
                    inv_como_cajas_fisicas = alg_subestacion_at.obtener_inv_fisicos(bloque_inicial, n_bloques, max_b, max_inv, inv_string)
                    
         
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
        """Cierra la ventana de carga tras  leer la posición DC las cajas."""
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
        """Coordina la tarea asíncrona para leer la posición DC las cajas."""
        proceso_leer_posicion_DC_Boxes()
        root.after(0, lambda: cerrar_ventana_tras_leer_posicion_DC_Boxes(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_leer_posicion_DC_Boxes) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
boton_DCB_loc_read = tk.Button(frame_DLV_CAD, text="Read changes", command=leer_posicion_DC_Boxes, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_DCB_loc_read.grid(row=3, column=2, pady=10)






#--------DIBUJAR Y LEER ORIENTACION DE STRINGS
def dibujar_orientacion_strings():
    """Dibuja la orientación los strings con los datos actuales."""
    def proceso_dibujo_orientacion_strings():
        """Ejecuta el proceso auxiliar encargado de dibujo la orientación los strings."""
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
        """Cierra la ventana de carga tras  simular dibujo orientación los strings."""
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
        """Coordina la tarea asíncrona para orientación los strings."""
        proceso_dibujo_orientacion_strings()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_ori_str(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_ori_str) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_CAD_ori_str = tk.Button(frame_DLV_CAD, text="Draw Str. Direction", command=dibujar_orientacion_strings, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_ori_str.grid(row=1, column=4, pady=10)

entrada_all_blocks_ori_str = tk.BooleanVar(value=False)
all_blocks_ori_str = True
single_block_ori_str=1

def update_single_block_ori_str():
    """Actualiza el bloque seleccionado asociado a orientación los strings."""
    global single_block_ori_str
    single_block_ori_str = int(spinbox_ori_str.get())

def activate_spinbox_ori_str():
    """Gestiona el estado del selector de bloque para orientación los strings."""
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
    """Lee los valores de la orientación los strings introducidos en la interfaz."""
    def proceso_leer_orientacion_strings():
        """Ejecuta el proceso auxiliar encargado de leer la orientación los strings."""
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
                
                                    
                strings_ID, _ , _, _, inv_string, equi_ibv_to_fs = alg_subestacion_at.ID_strings_e_inv_string(
                    bloque_inicial, n_bloques, max_b, max_inv, max_inv_block, max_str_pinv,
                    inv_string, dos_inv_por_bloque, equi_ibv_to_fs, strings_fisicos, dist_ext_opuesto_str, ori_str_ID, orientacion,
                    True, equi_ibv
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
        """Cierra la ventana de carga tras  leer la orientación los strings."""
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
        """Coordina la tarea asíncrona para leer la orientación los strings."""
        proceso_leer_orientacion_strings()
        root.after(0, lambda: cerrar_ventana_tras_leer_orientacion_strings(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_leer_orientacion_strings) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
boton_ori_str_read = tk.Button(frame_DLV_CAD, text="Read changes", command=leer_orientacion_strings, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_ori_str_read.grid(row=3, column=4, pady=10)







        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        




# #Cargar dibujos de interconexionado

# detalle_DFV_daisy = tk.Label(frame_DFV_drawings, image=imagen_DFV_daisy, bg=BLANCO_ROTO)
# detalle_DFV_daisy.grid(row=0, column=0)

# detalle_DFV_leapfrog = tk.Label(frame_DFV_drawings, image=imagen_DFV_leapfrog, bg=BLANCO_ROTO)
# detalle_DFV_leapfrog.grid(row=0, column=1, padx=100)











#3.3----------PESTAÑA MAIN CABLE ROUTING



#3.3.1 CABLE MV

    #3.3.1.1 SIMULAR POLILINEAS CABLE MV
def simular_polilineas_cable_mv():
    """Simula las polilíneas del cable de media tensión y actualiza los resultados."""
    def proceso_simular_polilineas_cable_mv():
        """Ejecuta la simulación de las polilíneas del cable de media tensión."""
        global pol_cable_MV, errores_grafo
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            pol_cable_MV, errores_grafo = alg_cables.lineas_MV_o_FO_por_caminos(pol_guia_MV_FO, pol_cable_MV, 'MV')
              
            guardar_variables([pol_cable_MV], ['pol_cable_MV'])
            
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                
    def cerrar_ventana_tras_simular_pol_mv(ventana_carga):
        """Cierra la ventana de carga tras simular las polilíneas del cable de media tensión."""
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
        """Coordina la tarea asíncrona para las polilíneas del cable de media tensión."""
        proceso_simular_polilineas_cable_mv()
        root.after(0, lambda: cerrar_ventana_tras_simular_pol_mv(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_polilineas_cable_mv) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
boton_polilineas_mv = tk.Button(frame_MV_routing, text="Simulate MV", command=simular_polilineas_cable_mv, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_polilineas_mv.grid(row=0, column=0, columnspan=1, pady=20)



    #3.3.1.2 DIBUJAR POLILINEAS CABLE MV
    
def dibujar_cable_MV():
    """Dibuja el cable de media tensión con los datos actuales."""
    def proceso_dibujo_cable_MV():
        """Gestiona el dibujo del cable de media tensión en AutoCAD."""
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
        """Cierra la ventana de carga tras dibujar el cable de media tensión."""
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
        """Coordina la tarea asíncrona para dibujar el cable MV."""
        proceso_dibujo_cable_MV()
        root.after(0, lambda: cerrar_ventana_tras_dibujar_cable_MV(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_dibujar_cable_MV) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_cable_MV_CAD_draw = tk.Button(frame_MV_routing, text="Draw MV Cables", command=dibujar_cable_MV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_cable_MV_CAD_draw.grid(row=1, column=0, pady=20)




    #3.3.2.3 LEER POLILINEAS CABLE MV DESDE EL CAD


def leer_polilineas_MV():

    """Lee los valores de las polilíneas MV introducidos en la interfaz."""
    def proceso_leer_polilineas_MV():
        """Ejecuta el proceso auxiliar encargado de leer las polilíneas MV."""
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
        """Cierra la ventana de carga tras  leer las polilíneas MV."""
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
        """Coordina la tarea asíncrona para las polilíneas MV."""
        proceso_leer_polilineas_MV()
        root.after(0, lambda: cerrar_ventana_tras_leer_polilineas_MV(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_polilineas_MV) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
    
boton_leer_polilineas_MV = tk.Button(frame_MV_routing, text="Read changes", command=leer_polilineas_MV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_leer_polilineas_MV.grid(row=2, column=0, pady=20)





def dibujar_grafo_guia():
    """Dibuja el grafo guía con los datos actuales."""
    def proceso_dibujo_grafo_guia():
        """Ejecuta el proceso auxiliar encargado de dibujo el grafo guía."""
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
        """Cierra la ventana de carga tras  dibujar el grafo guía."""
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
        """Coordina la tarea asíncrona para dibujar el grafo guía."""
        proceso_dibujo_grafo_guia()
        root.after(0, lambda: cerrar_ventana_tras_dibujar_grafo_guia(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_dibujar_grafo_guia) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_grafo_guia_CAD_draw = tk.Button(frame_MV_routing, text="Draw guiding graph", command=dibujar_grafo_guia, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_grafo_guia_CAD_draw.grid(row=5, column=0, pady=90)







#3.3.2 SUBARRAY

    #3.3.2.1 SIMULAR POLILINEAS SUBARRAY
def simular_polilineas_string_bus():
    """Simula las polilíneas del string bus y actualiza los resultados."""
    def proceso_simular_polilineas_string_bus():
        """Ejecuta la simulación de las polilíneas del string bus."""
        global max_p, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque, filas_con_dcb_extendido, Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID, extender_DC_Bus
        global error_de_simulacion   
        
        error_de_simulacion = 'Sin error'
        max_p=50 #PARAMETRO DE MAXIMOS PUNTOS QUE PUEDEN TENER LAS POLILINEAS DE STRING O DCBUS HASTA LAS CAJAS
        
        try:
            if DCBoxes_o_Inv_String == 'DC Boxes':
                if String_o_Bus == 'String Cable':
                    
                    pol_cable_string, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque = alg_cables.polilineas_de_circuitos_cable_string(strings_fisicos, filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_b,max_spf,max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, largo_caja, ancho_caja, dist_primera_pica_extremo_tr)
                    pol_DC_Bus = None #se define vacia porque es una entrada de la funcion de dibujo aunque en esta rama del diseño no se use
                    
                 
                elif String_o_Bus == 'DC Bus':
                                      
                    extender_DC_Bus=['No','No','No','No'] #Parametro de diseño que considera llevar el DCBus al final de los trackers (podria ahorrar harness en los trackers mas largos)         
                    
                    pol_cable_string = None
                    pol_DC_Bus, filas_con_dcb_extendido, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque = alg_cables.polilineas_de_circuitos_DC_Bus(filas_en_cajas,filas_en_bandas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_b,max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, largo_caja, ancho_caja, dist_primera_pica_extremo_tr, extender_DC_Bus)
                    
                    Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID = alg_cables.insercion_y_medicion_de_harness(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_tpf, filas_en_bandas, filas_con_cable_string, strings_ID, orientacion, String_o_Bus, Interconexionado, extender_DC_Bus, Polo_cercano, strings_fisicos, ori_str_ID, dist_ext_opuesto_str)
                    
                    guardar_variables([filas_con_dcb_extendido, Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID, extender_DC_Bus],['filas_con_dcb_extendido', 'Harness_pos_ID', 'Harness_neg_ID', 'tipos_harness_pos', 'med_tipos_h_pos', 'tipos_harness_neg', 'med_tipos_h_pos', 'med_tipos_h_neg', 'harness_pos', 'harness_neg', 'coord_harness_pos', 'coord_harness_neg', 'strings_ID','extender_DC_Bus'])
         
    
                elif String_o_Bus == 'Both types':
                  
                    extender_DC_Bus=['No','No','No','No'] #Parametro de diseño que considera llevar el DCBus al final de los trackers (podria ahorrar harness en los trackers mas largos)
                    
                    pol_cable_string , pol_DC_Bus, filas_con_dcb_extendido, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque = alg_cables.polilineas_de_circuitos_both_types(filas_con_cable_string, strings_fisicos, filas_en_cajas, cajas_fisicas, orientacion, bloque_inicial,n_bloques, max_b, max_spf, max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, dist_primera_pica_extremo_tr, filas_en_bandas, largo_caja, ancho_caja, extender_DC_Bus)
                    
                    Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID = alg_cables.insercion_y_medicion_de_harness(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_tpf, filas_en_bandas, filas_con_cable_string, strings_ID, orientacion, String_o_Bus, Interconexionado, extender_DC_Bus, Polo_cercano, strings_fisicos, ori_str_ID, dist_ext_opuesto_str)
                    
                    guardar_variables([filas_con_dcb_extendido, Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID, extender_DC_Bus],['filas_con_dcb_extendido', 'Harness_pos_ID', 'Harness_neg_ID', 'tipos_harness_pos', 'med_tipos_h_pos', 'tipos_harness_neg', 'med_tipos_h_pos', 'med_tipos_h_neg', 'harness_pos', 'harness_neg', 'coord_harness_pos', 'coord_harness_neg', 'strings_ID','extender_DC_Bus'])
                
                    
                elif String_o_Bus == 'Mixed':
        
                    extender_DC_Bus=['No','No','No','No'] #Parametro de diseño que considera llevar el DCBus al final de los trackers (podria ahorrar harness en los trackers mas largos)
                    
                    pol_cable_string, pol_DC_Bus, filas_con_dcb_extendido, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque = alg_cables.polilineas_de_circuitos_mixed(filas_con_cable_string, strings_fisicos, filas_en_cajas, cajas_fisicas, orientacion, bloque_inicial,n_bloques, max_b, max_spf, max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, dist_primera_pica_extremo_tr, filas_en_bandas, largo_caja, ancho_caja, extender_DC_Bus)
            
                    Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID = alg_cables.insercion_y_medicion_de_harness(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_tpf, filas_en_bandas, filas_con_cable_string, strings_ID, orientacion, String_o_Bus, Interconexionado, extender_DC_Bus, Polo_cercano, strings_fisicos, ori_str_ID, dist_ext_opuesto_str)
                    
                    guardar_variables([filas_con_dcb_extendido, Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID, extender_DC_Bus],['filas_con_dcb_extendido','Harness_pos_ID', 'Harness_neg_ID', 'tipos_harness_pos', 'med_tipos_h_pos', 'tipos_harness_neg', 'med_tipos_h_pos', 'med_tipos_h_neg', 'harness_pos', 'harness_neg', 'coord_harness_pos', 'coord_harness_neg', 'strings_ID','extender_DC_Bus'])
           
            else:#Inv de string
                    
                    pol_cable_string, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque = alg_cables.pol_cable_string_en_inv_string(strings_fisicos, inv_string, posiciones_inv, equi_ibv_to_fs, contorno_bandas_inf, contorno_bandas_sup, ori_str_ID, orientacion, strings_ID, bloque_inicial, n_bloques, max_b, max_inv, max_spf, max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, largo_caja, ancho_caja, dist_primera_pica_extremo_tr)
                    pol_DC_Bus = None #se define vacia porque es una entrada de la funcion de dibujo aunque en esta rama del diseño no se use
 
            guardar_variables([max_p, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque],['max_p','pol_cable_string', 'pol_DC_Bus', 'pol_tubo_corrugado_zanja_DC', 'max_tubos_DC_bloque'])
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                
    def cerrar_ventana_tras_simular_pol_str_bus(ventana_carga):
        """Cierra la ventana de carga tras simular las polilíneas del string bus."""
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
        """Coordina la tarea asíncrona número 7."""
        proceso_simular_polilineas_string_bus()
        root.after(0, lambda: cerrar_ventana_tras_simular_pol_str_bus(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_7) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
boton_polilineas_str_bus = tk.Button(frame_Subarray_routing, text="Simulate sub-array", command=simular_polilineas_string_bus, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_polilineas_str_bus.grid(row=0, column=0, columnspan=1, pady=20)



    #3.3.2.2 DIBUJAR POLILINEAS SUBARRAY

def dibujar_str_bus():
    """Dibuja el string bus con los datos actuales."""
    def proceso_dibujo_str_bus():
        """Realiza el dibujo del string bus en AutoCAD."""
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
        """Cierra la ventana de carga tras dibujar el string bus."""
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
        """Coordina la tarea asíncrona número 8."""
        proceso_dibujo_str_bus()
        root.after(0, lambda: cerrar_ventana_tras_dibujar_str_bus(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_8) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_str_bus_CAD_draw = tk.Button(frame_Subarray_routing, text="Draw", command=dibujar_str_bus, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_str_bus_CAD_draw.grid(row=1, column=0, pady=20)

entrada_all_blocks_str_bus = tk.BooleanVar(value=False)
all_blocks_str_bus = True
single_block_str_bus = 1 #se inicializa fuera del checkbutton para que permita dibujar todos los bloques de golpe sin que falte por definirse, luego cambia de valor sola

def update_single_block_str_bus():
    """Actualiza el bloque seleccionado asociado al string bus."""
    global single_block_str_bus
    single_block_str_bus = int(spinbox_str_bus.get())

def activate_spinbox_str_bus():
    """Gestiona el selector de bloque para el string bus."""
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
    """Lee la configuración del string bus introducida en la interfaz."""
    def proceso_leer_conf_str_bus():
        """Procesa la lectura de la configuración del string bus desde AutoCAD."""
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
        """Cierra la ventana de carga tras leer la configuración del string bus."""
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
        """Coordina la tarea asíncrona número 9."""
        proceso_leer_conf_str_bus()
        root.after(0, lambda: cerrar_ventana_tras_leer_dibujo_str_bus(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_9) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
boton_str_bus_CAD_read = tk.Button(frame_Subarray_routing, text="Read changes", command=leer_conf_str_bus, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_str_bus_CAD_read.grid(row=3, column=0, pady=20)








#-----------SIMULAR ARRAY Y DIBUJAR POLILINEAS

def simular_polilineas_array():

    """Simula las polilíneas del array y actualiza los resultados."""
    def proceso_simular_polilineas_array():
        """Ejecuta la simulación de las polilíneas del array."""
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
            
    
        try:
            global pol_array_cable, max_p_array, n_circuitos_max_lado_PCS, n_circuitos_max_entre_trackers, salida_zanja_LV_caja_inv
            
            salida_zanja_LV_caja_inv= 1 + largo_caja/2 #TODO salida del cable de array de la caja, de momento no se deja elegir al usuario a que distancia

            max_p_array = 100
            n_circuitos_max_lado_PCS = 14
            n_circuitos_max_entre_trackers = 8
            
            if entrada_DCBoxes_o_Inv_String.get() == 'DC Boxes':
                pol_array_cable = alg_cables.polilinea_array(max_p_array, bloque_inicial,n_bloques, max_b, max_f_str_b, max_c, coord_PCS_DC_inputs, orientacion, pitch, cajas_fisicas, filas_en_cajas, filas_en_bandas, bandas_anexas, bandas_separadas, bandas_aisladas, sep_caja_tracker, sep_zanja_tracker, salida_zanja_LV_caja_inv, largo_caja, n_circuitos_max_lado_PCS, n_circuitos_max_entre_trackers, DCBoxes_o_Inv_String)
            else:
                pol_array_cable = alg_cables.polilinea_array(max_p_array, bloque_inicial,n_bloques, max_b, max_f_str_b, max_inv, coord_PCS_DC_inputs, orientacion, pitch, inv_como_cajas_fisicas, filas_en_inv_como_filas_en_cajas, filas_en_bandas, bandas_anexas, bandas_separadas, bandas_aisladas, sep_caja_tracker, sep_zanja_tracker, salida_zanja_LV_caja_inv, largo_caja, n_circuitos_max_lado_PCS, n_circuitos_max_entre_trackers, DCBoxes_o_Inv_String)
                                                  
            guardar_variables([pol_array_cable, max_p_array, n_circuitos_max_lado_PCS, n_circuitos_max_entre_trackers, salida_zanja_LV_caja_inv],['pol_array_cable', 'max_p_array', 'n_circuitos_max_lado_PCS', 'n_circuitos_max_entre_trackers', 'salida_zanja_LV_caja_inv'])
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                
    def cerrar_ventana_tras_simular_pol_array(ventana_carga):
        """Cierra la ventana de carga tras simular las polilíneas del array."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")            
        except:
            print("Error al borrar el gif")
            
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_10():
        """Coordina la tarea asíncrona número 10."""
        proceso_simular_polilineas_array()
        root.after(0, lambda: cerrar_ventana_tras_simular_pol_array(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_10) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
boton_polilineas_array = tk.Button(frame_Array_routing, text="Simulate array", command=simular_polilineas_array, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_polilineas_array.grid(row=0, column=0, columnspan=1, pady=20)


#DIBUJAR Y LEER POLILINEAS DE ARRAY

def dibujar_array():
    """Dibuja el cableado del array con los datos actuales."""
    def proceso_dibujo_array():
        """Realiza el dibujo del cableado del array en AutoCAD."""
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
        """Cierra la ventana de carga tras dibujar el cableado del array."""
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
        """Coordina la tarea asíncrona número 11."""
        proceso_dibujo_array()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_array(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_11) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_array_CAD_draw = tk.Button(frame_Array_routing, text="Draw", command=dibujar_array, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_array_CAD_draw.grid(row=1, column=0, pady=20)

entrada_all_blocks_array = tk.BooleanVar(value=False)
all_blocks_array = True
single_block_array=1

def update_single_block_array():
    """Actualiza el bloque seleccionado asociado al array."""
    global single_block_array
    single_block_array = int(spinbox_array.get())

def activate_spinbox_array():
    """Gestiona el estado del selector de bloque dedicado al array."""
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
    """Lee la configuración del array introducida en la interfaz."""
    def proceso_leer_conf_array():
        """Procesa la lectura de la configuración del array desde AutoCAD."""
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
        """Cierra la ventana de carga tras leer la configuración del array."""
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
        """Coordina la tarea asíncrona número 12."""
        proceso_leer_conf_array()
        root.after(0, lambda: cerrar_ventana_tras_leer_array(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_12) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        
boton_array_CAD_read = tk.Button(frame_Array_routing, text="Read changes", command=leer_conf_array, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_array_CAD_read.grid(row=3, column=0, pady=20)







PV_PLANT_SECTION = TabSection(
    key="pv_plant",
    title="PV plant",
    icon="Pestaña 3.png",
    groups=FunctionalGroup(
        io={
            "draw_lv_configuration": dibujar_conf_LV,
            "draw_dc_boxes": dibujar_DC_Boxes,
            "draw_string_orientation": dibujar_orientacion_strings,
            "draw_mv_cables": dibujar_cable_MV,
            "draw_mv_guide": dibujar_grafo_guia,
            "draw_string_or_bus": dibujar_str_bus,
            "draw_array_cables": dibujar_array,
        },
        processing={
            "collect_block_power": leer_potencia_bloques,
            "read_mv_parameters": leer_valores_MV,
            "prepare_lv_configuration": ID_strings_y_DCBoxes,
            "simulate_lv": simular_configuracion_LV,
            "read_lv_layout": leer_conf_LV,
            "read_dcboxes_layout": leer_posicion_DC_Boxes,
            "read_string_orientation": leer_orientacion_strings,
            "simulate_mv_routing": simular_polilineas_cable_mv,
            "read_mv_routing": leer_polilineas_MV,
            "simulate_string_or_bus": simular_polilineas_string_bus,
            "read_string_or_bus": leer_conf_str_bus,
            "simulate_array_routing": simular_polilineas_array,
            "read_array_routing": leer_conf_array,
        },
        ui={
            "layout_block_power_form": listar_entradas_potencia,
            "apply_common_value": aplicar_valor_comun,
            "add_mv_line": agregar_linea_MV,
            "add_mv_segment": agregar_tramo_linea_MV,
            "remove_last_mv_element": eliminar_ultimo_elemento_MV,
            "render_mv_inputs": cargar_entradas_lineas_MV,
            "configure_dfv_comboboxes": comboboxes_entradas_DFV,
            "update_single_block_lv": update_single_block_lv,
            "activate_spinbox_lv": activate_spinbox_lv,
            "update_single_block_dcboxes": update_single_block_dcboxes,
            "activate_spinbox_dcboxes": activate_spinbox_dcboxes,
            "update_single_block_orientation": update_single_block_ori_str,
            "activate_spinbox_orientation": activate_spinbox_ori_str,
            "update_single_block_str_bus": update_single_block_str_bus,
            "activate_spinbox_str_bus": activate_spinbox_str_bus,
            "update_single_block_array": update_single_block_array,
            "activate_spinbox_array": activate_spinbox_array,
        },
    ),
)