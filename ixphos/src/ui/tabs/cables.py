# ============================================================================
# Pestaña 5: Cable Design
#---------------------------QUINTA PESTAÑA - MEDICION Y CALCULO DEL CABLE------------------------

#LAYOUT DE FRAMES PARA INTRODUCIR DATOS
# Crear un frame para meter en él dos frames y darles un margen común respecto a los bordes
frame_Med_Cables_container = tk.Frame(Cable_NB, background=BLANCO_ROTO)
frame_Med_Cables_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)


# Introducir un nuevo notebook para diferenciar entradas de medicion en cable MV, LV y AASS y COMS
notebook_med_cables = ttk.Notebook(frame_Med_Cables_container, style='TNotebook')
notebook_med_cables.pack(fill=tk.BOTH, expand=True)

# Crear las pestañas con el color de fondo definido
frame_Med_MV_cables = tk.Frame(notebook_med_cables, background=BLANCO_ROTO)
frame_Med_LV_cables = tk.Frame(notebook_med_cables, background=BLANCO_ROTO)
frame_Med_AASS_cables = tk.Frame(notebook_med_cables, background=BLANCO_ROTO)

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
frame_Med_MV_entradas =  tk.Frame(frame_Med_MV_cables, background=BLANCO_ROTO)
frame_Med_MV_entradas.grid(row=0, column=0, sticky='nsew', padx=50, pady=0)

    #Creamos el de los calculos
frame_Med_MV_calculos =  tk.Frame(frame_Med_MV_cables, background=BLANCO_ROTO)
frame_Med_MV_calculos.grid(row=0, column=1, sticky='nsew', padx=50, pady=0)





#    FRAME CABLE LV
# Configurar la cuadrícula para partir el frame en dos verticales, una para asignacion de entradas y otra para calculos 
frame_Med_LV_cables.grid_rowconfigure(0, weight=1) #añadimos row para que se expanda hasta abajo
frame_Med_LV_cables.grid_columnconfigure(0, weight=1)  
frame_Med_LV_cables.grid_columnconfigure(1, weight=1)  

    #Creamos el de las entradas
frame_Med_LV_entradas =  tk.Frame(frame_Med_LV_cables, background=BLANCO_ROTO)
frame_Med_LV_entradas.grid(row=0, column=0, sticky='nsew', padx=50, pady=0)

    #Creamos el de los calculos
frame_Med_LV_calculos =  tk.Frame(frame_Med_LV_cables, background=BLANCO_ROTO)
frame_Med_LV_calculos.grid(row=0, column=1, sticky='nsew', padx=50, pady=0)





# Creamos el frame para los criterios de mayoracion
frame_DCABLE_may = tk.Frame(frame_Med_LV_entradas, background=BLANCO_ROTO)
frame_DCABLE_may.grid(row=0, column=0, sticky='nsew', padx=50, pady=0)

    #Creamos la matriz que lo parta en dos para el cable solar/dcbus y el otro para el cable de array
frame_DCABLE_may.grid_rowconfigure(0, weight=1)
frame_DCABLE_may.grid_rowconfigure(1, weight=4)
# frame_DCABLE_may.grid_rowconfigure(2, weight=4)
# frame_DCABLE_may.grid_columnconfigure(0, weight=1)  

        #Añadimos el subframe del cable solar/dcbus arriba
frame_DCABLE_csb = tk.Frame(frame_DCABLE_may, background=GRIS_SUAVE)
frame_DCABLE_csb.grid(row=0, column=0, sticky='new', padx=0, pady=0)
        #Creamos la matriz que lo parta en header mas dos filas para añadir luego dos subframes, uno para entradas geometricas y otro para secciones
frame_DCABLE_csb.grid_columnconfigure(0, weight=4)
frame_DCABLE_csb.grid_columnconfigure(1, weight=1)   
         #Añadimos los dos subframes 
frame_DCABLE_geom = tk.Frame(frame_DCABLE_csb, background=GRIS_SUAVE)
frame_DCABLE_geom.grid(row=0, column=0, sticky='new', padx=0, pady=0)

frame_DCABLE_secciones = tk.Frame(frame_DCABLE_csb, background=GRIS_SUAVE)
frame_DCABLE_secciones.grid(row=0, column=1, sticky='new', padx=0, pady=0)


        #Añadimos el subframe del cable de array abajo
frame_DCABLE_arr = tk.Frame(frame_DCABLE_may, background=GRIS_SUAVE)
frame_DCABLE_arr.grid(row=1, column=0, sticky='new', padx=0, pady=(30,0))
        #Creamos la matriz que lo parta en header mas dos filas para añadir luego dos subframes, uno para entradas geometricas y otro para secciones
frame_DCABLE_arr.grid_columnconfigure(0, weight=4)
frame_DCABLE_arr.grid_columnconfigure(1, weight=1)  
         #Añadimos los dos subframes 
frame_DCABLE_arr_geom = tk.Frame(frame_DCABLE_arr, background=GRIS_SUAVE)
frame_DCABLE_arr_geom.grid(row=0, column=0, sticky='new', padx=0, pady=0)

frame_DCABLE_arr_secciones = tk.Frame(frame_DCABLE_arr, background=GRIS_SUAVE)
frame_DCABLE_arr_secciones.grid(row=0, column=1, sticky='new', padx=0, pady=0)


# Creamos el frame para los calculos de seccion
frame_DCABLE_calc = tk.Frame(frame_Med_LV_entradas, background=BLANCO_ROTO)
frame_DCABLE_calc.grid(row=1, column=0, sticky='', padx=0, pady=0)

    #Creamos la matriz que lo parta en dos columnas para añadir luego dos subframes, uno para el calculo local y otro para la afeccion a la planta
frame_DCABLE_calc.rowconfigure(0, weight=1)
frame_DCABLE_calc.columnconfigure(0, weight=1)  
frame_DCABLE_calc.columnconfigure(1, weight=2) 

        #Añadimos el subframe del calculo local
frame_DCABLE_calc_local = tk.Frame(frame_DCABLE_calc, background=BLANCO_ROTO)
frame_DCABLE_calc_local.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

        #Añadimos el subframe de la visualizacion a la derecha
frame_DCABLE_calc_vis = tk.Frame(frame_DCABLE_calc, background=BLANCO_ROTO)
frame_DCABLE_calc_vis.grid(row=0, column=1, sticky='nsew', padx=0, pady=0)









# LISTAR ENTRADAS MV

def entradas_medicion_cables_MV(valores_dados_MV):    
    """Configura las entradas necesarias para medir los cables MV."""
    global valor_slopes_trench_MV, valor_slack_MV, valor_transicion_PCS, valor_transicion_SS, valor_safety_maj_MV, entradas_asignacion_secciones_MV
    
        #Pendientes en zanja
    etiqueta_slopes_trench_MV = tk.Label(frame_Med_MV_entradas, text="Average slope (%)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_slopes_trench_MV.grid(row=0, column=0, padx=(10,0),pady=(15,15))
    valor_slopes_trench_MV = tk.StringVar()
    valor_slopes_trench_MV.set(valores_dados_MV[0])
    entrada_slopes_trench_MV = tk.Entry(frame_Med_MV_entradas, textvariable=valor_slopes_trench_MV, width=5)
    entrada_slopes_trench_MV.grid(row=0, column=1, padx=(5,20), pady=(15,15))
    
        #Slack cable
    etiqueta_slack_MV = tk.Label(frame_Med_MV_entradas, text="Slack (%)", fg=ROJO_GRS,  bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_slack_MV.grid(row=1, column=0, pady=(10,0))
    valor_slack_MV = tk.StringVar()
    valor_slack_MV.set(valores_dados_MV[3])
    entrada_slack_MV = tk.Entry(frame_Med_MV_entradas, textvariable=valor_slack_MV, width=5)
    entrada_slack_MV.grid(row=1, column=1, padx=(5,20), pady=(10,0))

        #Transición zanja-PCS
    etiqueta_transicion_PCS = tk.Label(frame_Med_MV_entradas, text="Trench-PCS transition (m)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_transicion_PCS.grid(row=2, column=0, pady=(15,10))
    valor_transicion_PCS = tk.StringVar()
    valor_transicion_PCS.set(valores_dados_MV[2])
    entrada_transicion_PCS = tk.Entry(frame_Med_MV_entradas, textvariable=valor_transicion_PCS, width=5)
    entrada_transicion_PCS.grid(row=2, column=1, padx=(12,20), pady=(15,10))

        #Transición Subestacion
    etiqueta_transicion_SS = tk.Label(frame_Med_MV_entradas, text="Substation transition (m)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_transicion_SS.grid(row=3, column=0, pady=(10,0))
    valor_transicion_SS = tk.StringVar()
    valor_transicion_SS.set(valores_dados_MV[1])
    entrada_transicion_SS = tk.Entry(frame_Med_MV_entradas, textvariable=valor_transicion_SS, width=5)
    entrada_transicion_SS.grid(row=3, column=1, padx=(12,20), pady=(10,0))

        #Mayoracion de seguridad
    etiqueta_safety_maj_MV = tk.Label(frame_Med_MV_entradas, text="Safety margin (%)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
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
        """Añade una nueva entrada relacionada con par asignacion secciones."""
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
        """Elimina el último par de entradas añadido para asignación de secciones."""
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
        """Carga los datos almacenados para las filas seccion por la posición en la interfaz."""
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
        """Carga los datos almacenados para las filas seccion por la potencia en la interfaz."""
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
        """Carga los datos almacenados para las líneas MV para seccion en la interfaz."""
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
        """Habilita las entradas según el criterio de sección de MV seleccionado."""
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
    """Lee los valores asociados al criterio de sección de MV introducidos en la interfaz."""
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

    """Ejecuta la medición asociada al cable de media tensión."""
    def proceso_medicion_cable_MV():
        """Procesa en segundo plano la medición del cable de media tensión."""
        global lineas_MV
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:

            leer_valores_par_criterio_seccion_MV()
            lineas_MV = alg_cables.medicion_cable_MV(lineas_MV, pol_cable_MV, slack_cable_MV, desnivel_cable_MV, transicion_MV_PCS, transicion_MV_SS, safety_maj_MV)
            lineas_MV = alg_cables.asignacion_secciones_cable_MV(lineas_MV, criterio_secciones_MV, asignacion_secciones_MV)
                
            guardar_variables([lineas_MV],['lineas_MV'])

        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                  
    def cerrar_ventana_tras_medir_cable_MV(ventana_carga):
        """Cierra la ventana de carga tras  medir el cable MV."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
                
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_medir_cable_MV():
        """Coordina la tarea asíncrona para medir el cable MV."""
        proceso_medicion_cable_MV()
        root.after(0, lambda: cerrar_ventana_tras_medir_cable_MV(ventana_carga))
        
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_medir_cable_MV) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()



boton_medir_cable_MV = tk.Button(frame_Med_MV_entradas, text="Simulate", command=medir_cable_MV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_medir_cable_MV.grid(row=8, column=0, pady=20)











#Listado de entradas y funciones asociadas para mostrarlas y leerlas

def listar_inputs_adicionales_dc_bus(valor_coca_dado, valor_primer_tracker_dado):
    """Prepara las entradas adicionales asociadas al bus DC."""
    global valor_coca, valor_primer_tracker, encabezado_cable_string, encabezado_DC_Bus
    # #añadimos una etiqueta blanco roto para tapar parte de la extension de la fila superior y que parezca que la tabla tiene una pestaña de titulo en la fila 0
    # ext_tapar_fila0= tk.Label(frame_DCABLE_csb, text='', bg=BLANCO_ROTO)
    # ext_tapar_fila0.grid(row=0, column=6, columnspan=2, sticky='e', padx=(0,0), pady=(0,0))
        #Añadimos un encabezado dcbus para las adicionales
    encabezado_DC_Bus= tk.Label(frame_DCABLE_geom, text="DC BUS specifica data", fg=ROJO_GRS, bg=GRIS_FUERTE, font=('Montserrat', 10, 'bold'))
    encabezado_DC_Bus.grid(row=3, column=0, sticky='nsew', padx=(10,10), pady=(7,0))
        #Coca en el ultimo tracker (al principio de la fila)
    etiqueta_coca = tk.Label(frame_DCABLE_geom, text="Turning excess in last tr.", fg=ROJO_GRS, bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold'))
    etiqueta_coca.grid(row=3, column=1, pady=(30,0))
    valor_coca = tk.StringVar()
    valor_coca.set(valor_coca_dado)
    entrada_coca = tk.Entry(frame_DCABLE_geom, textvariable=valor_coca, width=5)
    entrada_coca.grid(row=3, column=2, padx=(5,20), pady=(30,0))
        #Mayoracion de seguridad
    etiqueta_primer_tracker = tk.Label(frame_DCABLE_geom, text="Excess in first tr.", fg=ROJO_GRS, bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold'))
    etiqueta_primer_tracker.grid(row=3, column=3, pady=(15,15))
    valor_primer_tracker = tk.StringVar()
    valor_primer_tracker.set(valor_primer_tracker_dado)
    entrada_primer_tracker = tk.Entry(frame_DCABLE_geom, textvariable=valor_primer_tracker, width=5)
    entrada_primer_tracker.grid(row=3, column=4, padx=(5,20), pady=(15,15))    



def entradas_medicion_cables_subarray(valores_dados_subarray):
    """Configura las entradas necesarias para medir los cables subarray."""
    global valor_sa_slopes_air, valor_sa_slopes_trench, valor_sa_transicion_tr, valor_sa_transicion_caja, valor_sa_slack, valor_sa_safety_maj
    
    #ENTRADAS GEOMETRICAS PARA MEDICION DE CABLE STRING/DCBUS
        #añadimos una etiqueta blanco roto para tapar parte de la fila superior y que parezca que la tabla tiene una pestaña de titulo en la fila 0
    tapar_fila0= tk.Label(frame_DCABLE_geom, bd=7, bg=BLANCO_ROTO)
    tapar_fila0.grid(row=0, column=1, columnspan=10, sticky='ew', padx=(0,0), pady=(0,0))
        #añadimos una etiqueta de encabezado
    encabezado_cable_string= tk.Label(frame_DCABLE_geom, text="SUBARRAY CABLE", fg=ROJO_GRS, bg=GRIS_FUERTE, font=('Montserrat', 10, 'bold'))
    encabezado_cable_string.grid(row=0, column=0, sticky='nsew', padx=(10,10), pady=(7,0))
        #Pendientes en el tracker
    etiqueta_slopes_air = tk.Label(frame_DCABLE_geom, text="Average slope - tracker (%)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_slopes_air.grid(row=1, column=0, padx=(10,0), pady=(10,0))
    valor_sa_slopes_air = tk.StringVar()
    valor_sa_slopes_air.set(valores_dados_subarray[0])
    entrada_slopes_air = tk.Entry(frame_DCABLE_geom, textvariable=valor_sa_slopes_air, width=5)
    entrada_slopes_air.grid(row=1, column=1, padx=(5,20), pady=(10,0))
        #Pendientes en zanja
    etiqueta_slopes_trench = tk.Label(frame_DCABLE_geom, text="Average slope - trench (%)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_slopes_trench.grid(row=2, column=0, padx=(10,0),pady=(15,10))
    valor_sa_slopes_trench = tk.StringVar()
    valor_sa_slopes_trench.set(valores_dados_subarray[1])
    entrada_slopes_trench = tk.Entry(frame_DCABLE_geom, textvariable=valor_sa_slopes_trench, width=5)
    entrada_slopes_trench.grid(row=2, column=1, padx=(5,20), pady=(15,10))
        #Transición tracker-zanja
    etiqueta_transicion_tracker = tk.Label(frame_DCABLE_geom, text="Tracker-trench transition (m)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_transicion_tracker.grid(row=1, column=2, pady=(10,0))
    valor_sa_transicion_tr = tk.StringVar()
    valor_sa_transicion_tr.set(valores_dados_subarray[2])
    entrada_transicion_tracker = tk.Entry(frame_DCABLE_geom, textvariable=valor_sa_transicion_tr, width=5)
    entrada_transicion_tracker.grid(row=1, column=3, padx=(5,20), pady=(10,0))
        #Transición zanja-caja
    etiqueta_transicion_caja = tk.Label(frame_DCABLE_geom, text="Trench-DCBox/SI transition (m)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_transicion_caja.grid(row=2, column=2, pady=(15,10))
    valor_sa_transicion_caja = tk.StringVar()
    valor_sa_transicion_caja.set(valores_dados_subarray[3])
    entrada_transicion_caja = tk.Entry(frame_DCABLE_geom, textvariable=valor_sa_transicion_caja, width=5)
    entrada_transicion_caja.grid(row=2, column=3, padx=(5,20), pady=(15,10))
        #Slack cable
    etiqueta_slack = tk.Label(frame_DCABLE_geom, text="Slack (%)", fg=ROJO_GRS,  bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_slack.grid(row=1, column=4, pady=(10,0))
    valor_sa_slack = tk.StringVar()
    valor_sa_slack.set(valores_dados_subarray[4])
    entrada_slack = tk.Entry(frame_DCABLE_geom, textvariable=valor_sa_slack, width=5)
    entrada_slack.grid(row=1, column=5, padx=(5,20), pady=(10,0))
        #Mayoracion de seguridad
    etiqueta_safety_maj = tk.Label(frame_DCABLE_geom, text="Safety margin (%)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_safety_maj.grid(row=2, column=4, pady=(15,10))
    valor_sa_safety_maj = tk.StringVar()
    valor_sa_safety_maj.set(valores_dados_subarray[5])
    entrada_safety_maj = tk.Entry(frame_DCABLE_geom, textvariable=valor_sa_safety_maj, width=5)
    entrada_safety_maj.grid(row=2, column=5, padx=(5,20), pady=(15,10))    
    
    
    #ENTRADAS PARA SECCIONES DE CABLE DE STRING/DCBUS
    global valor_sa_sld1, valor_sa_sld2, valor_sa_loc1, valor_sa_loc2, valor_sa_s1, valor_sa_s2, valor_sa_s3, var_criterio_seccion_string
        #Limites de seccion por distancia cable de string
    etiqueta_seccion_str_SL_Distance = tk.Label(frame_DCABLE_secciones, text="SL Distance", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
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
    etiqueta_seccion_str_location = tk.Label(frame_DCABLE_secciones, text="Location of string in row", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
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
    etiqueta_seccion_str = tk.Label(frame_DCABLE_secciones, text="String Cable Cross-sections", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
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
        """Habilita las entradas según el criterio de sección aplicado a los strings."""
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
    
    etiqueta_seccion_dcb_SL_Distance = tk.Label(frame_DCABLE_secciones, text="SL Distance", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
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
    etiqueta_seccion_dcb_location = tk.Label(frame_DCABLE_secciones, text="No. strings in DC Bus", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
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
    etiqueta_seccion_dcb = tk.Label(frame_DCABLE_secciones, text="DC Bus Cross-sections", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
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
        """Habilita las entradas según el criterio de sección del bus DC."""
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
    """Prepara la lista de parámetros relacionados con uni o multipolar."""
    global var_array_uni_o_multipolar
    #Combobox para cable de array unipolar o multipolar
    unipolar_o_multipolar_options = ["Single core", "Multicore"]
    var_array_uni_o_multipolar = tk.StringVar(value = var_com_uni_o_multipolar)
    
    etiqueta_uom = tk.Label(frame_DCABLE_arr_geom, fg=ROJO_GRS, text='Cable type', font=('Montserrat', 10, 'bold'))
    etiqueta_uom.grid(row=3, column=4)
    combobox_uom = ttk.Combobox(frame_DCABLE_arr_geom, textvariable=var_array_uni_o_multipolar, values=unipolar_o_multipolar_options)
    combobox_uom.grid(row=3, column=5, pady=(5,0))

         
def entradas_medicion_cables_array(valores_dados_array):
    """Configura las entradas necesarias para medir los cables del array."""
    global valor_slopes_trench_LV, valor_transicion_caja_LV, valor_transicion_PCS, valor_slack_arr, valor_safety_maj_arr, valor_sld1_arr, valor_loc1_arr, valor_s1_arr, valor_s2_arr, var_criterio_seccion_array, var_mat_array
    
    tapar_fila0= tk.Label(frame_DCABLE_arr_geom, bd=7, bg=BLANCO_ROTO)
    tapar_fila0.grid(row=0, column=1, columnspan=10, sticky='ew', padx=(0,0), pady=(0,0))
        #añadimos una etiqueta de encabezado
    encabezado_cable_arr= tk.Label(frame_DCABLE_arr_geom, text="ARRAY CABLE", fg=ROJO_GRS, bg=GRIS_FUERTE, font=('Montserrat', 10, 'bold'))
    encabezado_cable_arr.grid(row=0, column=0, sticky='nsew', padx=(10,10), pady=(7,0))
        #Pendientes en zanja
    etiqueta_slopes_trench_LV = tk.Label(frame_DCABLE_arr_geom, text="Average slope - trench (%)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_slopes_trench_LV.grid(row=1, column=0, rowspan=2, padx=(10,0),pady=(15,15))
    valor_slopes_trench_LV = tk.StringVar()
    valor_slopes_trench_LV.set(valores_dados_array[0])
    entrada_slopes_trench_LV = tk.Entry(frame_DCABLE_arr_geom, textvariable=valor_slopes_trench_LV, width=5)
    entrada_slopes_trench_LV.grid(row=1, column=1, rowspan=2, padx=(5,20), pady=(15,15))
        #Transición caja-zanja
    etiqueta_transicion_caja_LV = tk.Label(frame_DCABLE_arr_geom, text="DCBox/SI-trench transition (m)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_transicion_caja_LV.grid(row=1, column=2, pady=(10,0))
    valor_transicion_caja_LV = tk.StringVar()
    valor_transicion_caja_LV.set(valores_dados_array[1])
    entrada_transicion_caja_LV = tk.Entry(frame_DCABLE_arr_geom, textvariable=valor_transicion_caja_LV, width=5)
    entrada_transicion_caja_LV.grid(row=1, column=3, padx=(12,20), pady=(10,0))
        #Transición zanja-PCS
    etiqueta_transicion_PCS = tk.Label(frame_DCABLE_arr_geom, text="Trench-PCS transition (m)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_transicion_PCS.grid(row=2, column=2, pady=(15,10))
    valor_transicion_PCS = tk.StringVar()
    valor_transicion_PCS.set(valores_dados_array[2])
    entrada_transicion_PCS = tk.Entry(frame_DCABLE_arr_geom, textvariable=valor_transicion_PCS, width=5)
    entrada_transicion_PCS.grid(row=2, column=3, padx=(12,20), pady=(15,10))
        #Slack cable
    etiqueta_slack_arr = tk.Label(frame_DCABLE_arr_geom, text="Slack (%)", fg=ROJO_GRS,  bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_slack_arr.grid(row=1, column=4, pady=(10,0))
    valor_slack_arr = tk.StringVar()
    valor_slack_arr.set(valores_dados_array[3])
    entrada_slack_arr = tk.Entry(frame_DCABLE_arr_geom, textvariable=valor_slack_arr, width=5)
    entrada_slack_arr.grid(row=1, column=5, padx=(5,20), pady=(10,0))
        #Mayoracion de seguridad
    etiqueta_safety_maj_arr = tk.Label(frame_DCABLE_arr_geom, text="Safety margin (%)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_safety_maj_arr.grid(row=2, column=4, pady=(15,10))
    valor_safety_maj_arr = tk.StringVar()
    valor_safety_maj_arr.set(valores_dados_array[4])
    entrada_safety_maj_arr = tk.Entry(frame_DCABLE_arr_geom, textvariable=valor_safety_maj_arr, width=5)
    entrada_safety_maj_arr.grid(row=2, column=5, padx=(5,20), pady=(15,10))    
    
    #Combobox para material
    opciones_mat_array = ['Al','Cu']
    var_mat_array = tk.StringVar(value = valores_dados_array[9])
    
    etiqueta_mat_array = tk.Label(frame_DCABLE_arr_geom, text='Array Cable Material', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_mat_array.grid(row=3, column=2)
    combobox_mat_array=ttk.Combobox(frame_DCABLE_arr_geom, textvariable=var_mat_array, values=opciones_mat_array)
    combobox_mat_array.grid(row=3, column=3)
    
    #ENTRADAS PARA SECCIONES DE CABLE DE ARRAY    
        #Limites de seccion por distancia cable de array
    etiqueta_seccion_array_SL_Distance = tk.Label(frame_DCABLE_arr_secciones, text="SL Distance", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_seccion_array_SL_Distance.grid(row=0, column=1, pady=(15,10))
    valor_sld1_arr = tk.StringVar()
    valor_sld1_arr.set(valores_dados_array[5])
    entrada_seccion_array_SL_Distance_1 = tk.Entry(frame_DCABLE_arr_secciones, textvariable=valor_sld1_arr, width=5)
    entrada_seccion_array_SL_Distance_1.grid(row=0, column=2, padx=(5,5), pady=(15,10))   
        #Limites de seccion por localizacion cable de array
    etiqueta_seccion_array_location = tk.Label(frame_DCABLE_arr_secciones, text="No. strings border (<=)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_seccion_array_location.grid(row=1, column=1, pady=(15,10))
    valor_loc1_arr = tk.StringVar()
    valor_loc1_arr.set(valores_dados_array[6])
    entrada_seccion_array_location_1 = tk.Entry(frame_DCABLE_arr_secciones, textvariable=valor_loc1_arr, width=5)
    entrada_seccion_array_location_1.grid(row=1, column=2, padx=(5,5), pady=(15,10))   
 
        #Secciones de cable de array
    etiqueta_seccion_array = tk.Label(frame_DCABLE_arr_secciones, text="Array Cable Cross-sections", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
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
        """Habilita las entradas según el criterio de sección configurado para el array."""
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
    """Convierte una entrada textual en un entero seguro."""
    return int(entrada) if entrada.strip() else 0

def devolver_float(entrada):
    """Convierte una entrada textual en un número flotante seguro."""
    return float(entrada) if entrada.strip() else 0

def leer_valores_GUI_cable_string():
    """Lee los valores del cableado de strings introducidos en la interfaz."""
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
    """Lee los valores del bus DC introducidos en la interfaz gráfica."""
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
    """Lee los parámetros de las opciones mixtas introducidos en la interfaz gráfica."""
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
        
    """Calcula las mediciones correspondientes a los cables subarray."""
    def proceso_medicion_cables_subarray():
        """Ejecuta el proceso auxiliar encargado de la medición los cables subarray."""
        global med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg
        global med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg, med_tubo_corrugado_zanja_DC
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            if String_o_Bus == 'String Cable':
                leer_valores_GUI_cable_string()
                med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_zanja_DC = alg_cables.medicion_cable_string(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_c_block, masc, max_inv_block, max_str_pinv, max_p, DCBoxes_o_Inv_String, strings_fisicos, strings_ID, pol_cable_string, equi_ibfs, Interconexionado, Polo_cercano, ancho_modulo, saliente_TT, desplaz_x_cable_modulos, dist_ext_opuesto_str, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, mayoracion_cable_subarray, mayoracion_tubo_corrugado_DC, criterio_seccion_cs, lim_dist_sld_cs_seccion, lim_loc_cs_seccion, secciones_cs, filas_con_cable_string, dos_inv_por_bloque, cajas_fisicas)
         
                guardar_variables([med_inst_cable_string_pos, tramo_aereo_cable_string_pos,med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_zanja_DC],['med_inst_cable_string_pos','tramo_aereo_cable_string_pos','med_inst_cable_string_neg','med_cable_string_pos', 'med_cable_string_neg', 'sch_cable_de_string_pos', 'sch_cable_de_string_neg', 'med_tubo_corrugado_zanja_DC' ])
                
            elif String_o_Bus == 'DC Bus':
                leer_valores_GUI_DC_Bus()
                med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg, med_tubo_corrugado_zanja_DC = alg_cables.medicion_DC_Bus(bloque_inicial,n_bloques, max_b, max_f_str_b, max_p, max_c_block, max_bus, filas_en_cajas, pol_DC_Bus, equi_ibfs ,Interconexionado, Polo_cercano, dist_ext_opuesto_str, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, coca_DC_Bus, extension_primer_tracker, slack_cable_subarray, mayoracion_cable_subarray, mayoracion_tubo_corrugado_DC, criterio_seccion_dcb, lim_dist_sld_dcb_seccion, lim_loc_dcb_seccion, secciones_dcb, extender_DC_Bus, filas_con_dcb_extendido, filas_con_cable_string, dos_inv_por_bloque, cajas_fisicas)
                

                guardar_variables([med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg, med_tubo_corrugado_zanja_DC],['med_inst_DC_Bus_pos', 'med_inst_DC_Bus_neg', 'med_DC_Bus_pos', 'tramo_aereo_DC_Bus_pos', 'med_DC_Bus_neg', 'sch_DC_Bus_pos', 'sch_DC_Bus_neg', 'med_tubo_corrugado_zanja_DC'])
                    
            elif String_o_Bus == 'Both types':
                leer_valores_GUI_opciones_mixtas()
                med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_str_zanja_DC = alg_cables.medicion_cable_string(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_c_block, masc, max_inv_block, max_str_pinv, max_p, DCBoxes_o_Inv_String, strings_fisicos, strings_ID, pol_cable_string, equi_ibfs, Interconexionado, Polo_cercano, ancho_modulo, saliente_TT, desplaz_x_cable_modulos, dist_ext_opuesto_str, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, mayoracion_cable_subarray, mayoracion_tubo_corrugado_DC, criterio_seccion_cs, lim_dist_sld_cs_seccion, lim_loc_cs_seccion, secciones_cs, filas_con_cable_string, dos_inv_por_bloque, cajas_fisicas)
                med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg, med_tubo_corrugado_dcbus_zanja_DC = alg_cables.medicion_DC_Bus(bloque_inicial,n_bloques, max_b, max_f_str_b, max_p, max_c_block, max_bus, filas_en_cajas, pol_DC_Bus, equi_ibfs ,Interconexionado, Polo_cercano, dist_ext_opuesto_str, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, coca_DC_Bus, extension_primer_tracker, slack_cable_subarray, mayoracion_cable_subarray, mayoracion_tubo_corrugado_DC, criterio_seccion_dcb, lim_dist_sld_dcb_seccion, lim_loc_dcb_seccion, secciones_dcb, extender_DC_Bus, filas_con_dcb_extendido, filas_con_cable_string, dos_inv_por_bloque, cajas_fisicas)
                med_tubo_corrugado_zanja_DC = np.where(np.isnan(med_tubo_corrugado_str_zanja_DC), med_tubo_corrugado_dcbus_zanja_DC, med_tubo_corrugado_str_zanja_DC)
                
                guardar_variables([med_inst_cable_string_pos, tramo_aereo_cable_string_pos,med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_zanja_DC],['med_inst_cable_string_pos','tramo_aereo_cable_string_pos','med_inst_cable_string_neg','med_cable_string_pos', 'med_cable_string_neg', 'sch_cable_de_string_pos', 'sch_cable_de_string_neg', 'med_tubo_corrugado_zanja_DC'])
                guardar_variables([med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg],['med_inst_DC_Bus_pos', 'med_inst_DC_Bus_neg', 'med_DC_Bus_pos', 'tramo_aereo_DC_Bus_pos', 'med_DC_Bus_neg', 'sch_DC_Bus_pos', 'sch_DC_Bus_neg'])


            elif String_o_Bus == 'Mixed':
                leer_valores_GUI_opciones_mixtas()
                med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_zanja_DC = alg_cables.medicion_cable_string(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_c_block, masc, max_inv_block, max_str_pinv, max_p, DCBoxes_o_Inv_String, strings_fisicos, strings_ID, pol_cable_string, equi_ibfs, Interconexionado, Polo_cercano, ancho_modulo, saliente_TT, desplaz_x_cable_modulos, dist_ext_opuesto_str, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, slack_cable_subarray, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, mayoracion_cable_subarray, mayoracion_tubo_corrugado_DC, criterio_seccion_cs, lim_dist_sld_cs_seccion, lim_loc_cs_seccion, secciones_cs, filas_con_cable_string, dos_inv_por_bloque, cajas_fisicas)
                med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg, med_tubo_corrugado_dcbus_zanja_DC = alg_cables.medicion_DC_Bus(bloque_inicial,n_bloques, max_b, max_f_str_b, max_p, max_c_block, max_bus, filas_en_cajas, pol_DC_Bus, equi_ibfs ,Interconexionado, Polo_cercano, dist_ext_opuesto_str, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_cable_subarray_tracker, transicion_cable_subarray_caja, coca_DC_Bus, extension_primer_tracker, slack_cable_subarray, mayoracion_cable_subarray, mayoracion_tubo_corrugado_DC, criterio_seccion_dcb, lim_dist_sld_dcb_seccion, lim_loc_dcb_seccion, secciones_dcb, extender_DC_Bus, filas_con_dcb_extendido, filas_con_cable_string, dos_inv_por_bloque, cajas_fisicas)
                
                
                guardar_variables([med_inst_cable_string_pos, tramo_aereo_cable_string_pos,med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_zanja_DC],['med_inst_cable_string_pos','tramo_aereo_cable_string_pos','med_inst_cable_string_neg','med_cable_string_pos', 'med_cable_string_neg', 'sch_cable_de_string_pos', 'sch_cable_de_string_neg','med_tubo_corrugado_zanja_DC'])
                guardar_variables([med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg],['med_inst_DC_Bus_pos', 'med_inst_DC_Bus_neg', 'med_DC_Bus_pos', 'tramo_aereo_DC_Bus_pos', 'med_DC_Bus_neg', 'sch_DC_Bus_pos', 'sch_DC_Bus_neg'])
    
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                  
    def cerrar_ventana_tras_medir_subarrays(ventana_carga):
        """Cierra la ventana de carga tras  medir subarrays."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
                
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_medir_subarrays():
        """Coordina la tarea asíncrona para medir subarrays."""
        proceso_medicion_cables_subarray()
        root.after(0, lambda: cerrar_ventana_tras_medir_subarrays(ventana_carga))
        
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_medir_subarrays) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()




boton_array_CAD_read = tk.Button(frame_DCABLE_geom, text="Simulate", command=medicion_cables_subarray, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_array_CAD_read.grid(row=2, column=7, pady=20)







#------------MEDIR CABLE DE ARRAY

def leer_valores_GUI_cable_array():
    """Lee los valores del cableado del array introducidos en la interfaz."""
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
            uni_o_multipolar=1
        else:
            uni_o_multipolar=3
    else:
       if var_array_uni_o_multipolar.get() == 'Single core':
           uni_o_multipolar=1
       else:
           uni_o_multipolar=2
    
    lim_dist_array_sld_seccion = devolver_entero(valor_sld1_arr.get())
    lim_n_str_array_seccion = devolver_entero(valor_loc1_arr.get())
    seccion_array_1 = devolver_entero(valor_s1_arr.get())
    seccion_array_2 = devolver_entero(valor_s2_arr.get())

    secciones_array_sin_filtrar = np.array([seccion_array_1, seccion_array_2])
    secciones_array = secciones_array_sin_filtrar[secciones_array_sin_filtrar != 0].tolist()

        
    #Guardar variables en el dicionario
    guardar_variables([desnivel_cable_array_por_pendientes, transicion_array_cable_caja, transicion_array_cable_PCS, slack_array_cable, mayoracion_array_cable, uni_o_multipolar, criterio_seccion_array, lim_dist_array_sld_seccion, lim_n_str_array_seccion, seccion_array_1, seccion_array_2, secciones_array, material_array],['desnivel_cable_array_por_pendientes', 'transicion_array_cable_caja', 'transicion_array_cable_PCS', 'slack_array_cable', 'mayoracion_array_cable', 'uni_o_multipolar', 'criterio_seccion_array', 'lim_dist_array_sld_seccion', 'lim_n_str_array_seccion', 'seccion_array_1', 'seccion_array_2', 'secciones_array', 'material_array'])



def medicion_cable_array():

    """Calcula las mediciones correspondientes al cableado del array."""
    def proceso_medicion_cable_array():
        """Ejecuta la medición del cableado del array en un hilo auxiliar."""
        global med_inst_array_cable_pos, med_inst_array_cable_neg, med_array_cable_pos, med_array_cable_neg, med_array_cable, med_inst_array_cable, sch_array_cable_pos, sch_array_cable_neg, sch_array_cable
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            leer_valores_GUI_cable_array()
            
            if DCBoxes_o_Inv_String == 'DC Boxes':
                med_inst_array_cable_pos, med_inst_array_cable_neg, med_array_cable_pos, med_array_cable_neg, med_array_cable, med_inst_array_cable, sch_array_cable_pos, sch_array_cable_neg, sch_array_cable = alg_cables.medicion_array(bloque_inicial, n_bloques, DCBoxes_o_Inv_String, max_b, max_c, max_c_block, cajas_fisicas, pol_array_cable, equi_ibc, desnivel_cable_array_por_pendientes, transicion_array_cable_caja, transicion_array_cable_PCS, uni_o_multipolar, slack_array_cable, mayoracion_array_cable, lim_dist_array_sld_seccion, lim_n_str_array_seccion, criterio_seccion_array, secciones_array)
            else:
                med_inst_array_cable_pos, med_inst_array_cable_neg, med_array_cable_pos, med_array_cable_neg, med_array_cable, med_inst_array_cable, sch_array_cable_pos, sch_array_cable_neg, sch_array_cable = alg_cables.medicion_array(bloque_inicial, n_bloques, DCBoxes_o_Inv_String, max_b, max_inv, max_inv_block, inv_como_cajas_fisicas, pol_array_cable, equi_ibv, desnivel_cable_array_por_pendientes, transicion_array_cable_caja, transicion_array_cable_PCS, uni_o_multipolar, slack_array_cable, mayoracion_array_cable, lim_dist_array_sld_seccion, lim_n_str_array_seccion, criterio_seccion_array, secciones_array)               
            
            
            guardar_variables([med_inst_array_cable_pos, med_inst_array_cable_neg, med_array_cable_pos, med_array_cable_neg, med_array_cable, med_inst_array_cable, sch_array_cable_pos, sch_array_cable_neg, sch_array_cable],['med_inst_array_cable_pos', 'med_inst_array_cable_neg', 'med_array_cable_pos', 'med_array_cable_neg', 'med_array_cable', 'med_inst_array_cable', 'sch_array_cable_pos', 'sch_array_cable_neg', 'sch_array_cable'])
            

        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                  
    def cerrar_ventana_tras_medir_arrays(ventana_carga):
        """Cierra la ventana de carga tras medir el cableado del array."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
            else:
                messagebox.showinfo("Sucess", "Measurement was completed successfully.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_medir_arrays():
        """Coordina la tarea asíncrona para medir los arrays."""
        proceso_medicion_cable_array()
        root.after(0, lambda: cerrar_ventana_tras_medir_arrays(ventana_carga))
        
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_medir_arrays) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()



boton_array_CAD_read = tk.Button(frame_DCABLE_arr_secciones, text="Simulate", command=medicion_cable_array, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_array_CAD_read.grid(row=2, column=5, pady=20)





#-----CUADRO PARA CALCULO 
#     #Seccion
# etiqueta_calc_seccion = tk.Label(frame_DCABLE_calc_local, text="Cross section", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
# etiqueta_calc_seccion.grid(row=0, column=0, padx=(5,5),pady=(0,10))
# entrada_calc_seccion = tk.Entry(frame_DCABLE_calc_local, width=5)
# entrada_calc_seccion.grid(row=0, column=1, padx=(0,5), pady=(0,10))
#     #Material
# etiqueta_calc_mat = tk.Label(frame_DCABLE_calc_local, text="Material", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
# etiqueta_calc_mat.grid(row=1, column=0, padx=(5,5),pady=(0,10))
# entrada_calc_mat = tk.Entry(frame_DCABLE_calc_local, width=5)
# entrada_calc_mat.grid(row=1, column=1, padx=(0,5), pady=(0,10))
#     #Intensidad
# etiqueta_calc_int = tk.Label(frame_DCABLE_calc_local, text="Current (A)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
# etiqueta_calc_int.grid(row=2, column=0, padx=(5,5),pady=(0,10))
# entrada_calc_int = tk.Entry(frame_DCABLE_calc_local, width=5)
# entrada_calc_int.grid(row=2, column=1, padx=(0,5), pady=(0,10))
#     #Fases
# etiqueta_calc_fases = tk.Label(frame_DCABLE_calc_local, text="Phases", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
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


valores_iniciales_perdidas = [[],[],[],[],[58.14], [35.46]]

def entradas_calculo_perdidas(valores_dados_perdidas):    
    """Construye los campos de entrada para calculo las pérdidas."""
    global valor_cond_Cu, valor_cond_Al, valor_bif, valor_int_STC, valor_power_STC, valor_subarray_temp, valor_array_temp
    
    #Conductividad Cobre
    etiqueta_cond_Cu = tk.Label(frame_DCABLE_calc_local, text="Cond. Cu (20ºC)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_cond_Cu.grid(row=0, column=0, padx=(5,5),pady=(0,10))
    valor_cond_Cu = tk.StringVar()
    valor_cond_Cu.set(valores_dados_perdidas[0])
    entrada_cond_Cu = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_cond_Cu, width=5)
    entrada_cond_Cu.grid(row=0, column=1, padx=(0,5), pady=(0,10))
    
    #Conductividad Aluminio
    etiqueta_cond_Al = tk.Label(frame_DCABLE_calc_local, text="Cond. Al (20ºC)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_cond_Al.grid(row=1, column=0, padx=(5,5),pady=(0,10))
    valor_cond_Al = tk.StringVar()
    valor_cond_Al.set(valores_dados_perdidas[1])
    entrada_cond_Al = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_cond_Al, width=5)
    entrada_cond_Al.grid(row=1, column=1, padx=(0,5), pady=(0,10))
    
    #Bifacialidad
    etiqueta_bif = tk.Label(frame_DCABLE_calc_local, text="Bifaciality (%)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_bif.grid(row=0, column=2, padx=(5,5),pady=(0,10))
    valor_bif = tk.StringVar()
    valor_bif.set(valores_dados_perdidas[2])
    entrada_bif = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_bif, width=5)
    entrada_bif.grid(row=0, column=3, padx=(0,5), pady=(0,10))
    
    #Intensidad MPP del modulo en STC
    etiqueta_int_STC = tk.Label(frame_DCABLE_calc_local, text="Impp STC (A)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_int_STC.grid(row=1, column=2, padx=(5,5),pady=(0,10))
    valor_int_STC = tk.StringVar()
    valor_int_STC.set(valores_dados_perdidas[3])
    entrada_int_STC = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_int_STC, width=5)
    entrada_int_STC.grid(row=1, column=3, padx=(0,5), pady=(0,10))
    
    #Potencia MPP del modulo en STC
    etiqueta_power_STC = tk.Label(frame_DCABLE_calc_local, text="Power STC (Wp)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_power_STC.grid(row=2, column=2, padx=(5,5),pady=(0,10))
    valor_power_STC = tk.StringVar()
    valor_power_STC.set(valores_dados_perdidas[4])
    entrada_power_STC = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_power_STC, width=5)
    entrada_power_STC.grid(row=2, column=3, padx=(0,5), pady=(0,10))
    
    #Temperatura del cable de subarray para el calculo
    etiqueta_subarray_temp = tk.Label(frame_DCABLE_calc_local, text="Subarray cable temp (ºC)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_subarray_temp.grid(row=3, column=2, padx=(10,0),pady=(10,5))
    valor_subarray_temp = tk.StringVar()
    valor_subarray_temp.set(valores_dados_perdidas[5])
    entrada_subarray_temp = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_subarray_temp, width=5)
    entrada_subarray_temp.grid(row=3, column=3, padx=(5,20), pady=(10,5))

    #Temperatura del cable de array para el calculo
    etiqueta_array_temp = tk.Label(frame_DCABLE_calc_local, text="Array cable temp (ºC)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_array_temp.grid(row=4, column=2, padx=(10,0),pady=(10,5))
    valor_array_temp = tk.StringVar()
    valor_array_temp.set(valores_dados_perdidas[6])
    entrada_array_temp = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_array_temp, width=5)
    entrada_array_temp.grid(row=4, column=3, padx=(5,20), pady=(10,5))
    
    
    #-----------------------------Si es AC------------------------
    if DCBoxes_o_Inv_String == 'String Inverters':
        global valor_pot_inv, valor_cos_phi, valor_v_inv, valor_X_cable
        
        #Potencia activa inversor
        etiqueta_pot_inv = tk.Label(frame_DCABLE_calc_local, text="Active Power Inv (W)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
        etiqueta_pot_inv.grid(row=0, column=4, padx=(10,0),pady=(10,5))
        valor_pot_inv = tk.StringVar()
        valor_pot_inv.set(valores_dados_perdidas[7])
        entrada_pot_inv = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_pot_inv, width=10)
        entrada_pot_inv.grid(row=0, column=5, padx=(5,20), pady=(10,5))
        
        #Coseno de phi
        etiqueta_cos_phi = tk.Label(frame_DCABLE_calc_local, text="Cos Phi", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
        etiqueta_cos_phi.grid(row=1, column=4, padx=(10,0),pady=(10,5))
        valor_cos_phi = tk.StringVar()
        valor_cos_phi.set(valores_dados_perdidas[8])
        entrada_cos_phi = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_cos_phi, width=5)
        entrada_cos_phi.grid(row=1, column=5, padx=(5,20), pady=(10,5))
        
        #Tension nominal inversor
        etiqueta_v_inv = tk.Label(frame_DCABLE_calc_local, text="Nominal Voltage Inv (V)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
        etiqueta_v_inv.grid(row=2, column=4, padx=(10,0),pady=(10,5))
        valor_v_inv = tk.StringVar()
        valor_v_inv.set(valores_dados_perdidas[9])
        entrada_v_inv = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_v_inv, width=5)
        entrada_v_inv.grid(row=2, column=5, padx=(5,20), pady=(10,5))
        
        #Reactancia del cable de array
        etiqueta_X_cable = tk.Label(frame_DCABLE_calc_local, text="Cable Reactance (mOhm/m)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
        etiqueta_X_cable.grid(row=3, column=4, padx=(10,0),pady=(10,5))
        valor_X_cable = tk.StringVar()
        valor_X_cable.set(valores_dados_perdidas[10])
        entrada_X_cable = tk.Entry(frame_DCABLE_calc_local, textvariable=valor_X_cable, width=5)
        entrada_X_cable.grid(row=3, column=5, padx=(5,20), pady=(10,5))
        

    
    
def leer_valores_GUI_calculo_perdidas():
    """Lee los valores de la interfaz GUI calculo las pérdidas introducidos en la interfaz."""
    global bifaciality, int_mod_STC, power_mod_STC, subarray_temp, array_temp, cond_Cu_20, cond_Al_20
    
    #leemos las entradas previas
    cond_Al_20=float(valor_cond_Al.get())
    cond_Cu_20=float(valor_cond_Cu.get())
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
    guardar_variables([bifaciality, int_mod_STC, power_mod_STC, subarray_temp, array_temp, cond_Cu_20, cond_Al_20],['bifaciality', 'int_mod_STC', 'power_mod_STC', 'subarray_temp', 'array_temp', 'cond_Al_20', 'cond_Cu_20'])


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
        frame_tabla_resumen_perdidas = tk.Frame(frame_DCABLE_calc_vis, bg=GRIS_SUAVE, bd=0, highlightthickness=0)
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
    """Muestra la tabla resumen de pérdidas dentro de la interfaz."""
    _asegurar_frame_resumen()

    # Limpiar contenido previo
    for w in frame_tabla_resumen_perdidas.winfo_children():
        w.destroy()

    # Cabecera general
    tk.Label(frame_tabla_resumen_perdidas, text="Losses and Voltage Drop Summary",
             bg=GRIS_SUAVE, fg=ROJO_GRS, font=('Montserrat', 9, 'bold')
    ).grid(row=0, column=0, columnspan=6, pady=(0,6), sticky="w")

    # Helper fila
    def fila(r, c, texto, valor):
        """Inserta una fila formateada en el resumen de pérdidas."""
        tk.Label(frame_tabla_resumen_perdidas, text=texto,
                 bg=GRIS_SUAVE, font=('Montserrat', 8)
        ).grid(row=r, column=c, padx=(2,4), pady=1, sticky="w")

        tk.Label(frame_tabla_resumen_perdidas, text=_fmt_pct(valor),
                 bg=GRIS_SUAVE, font=('Montserrat', 8, 'bold')
        ).grid(row=r, column=c+1, pady=1, sticky="e")

    # --- Bloque 1: String Cable + DC Bus ---
    col1 = 0
    row = 1
    tk.Label(frame_tabla_resumen_perdidas, text="String Cable",
             bg=GRIS_SUAVE, fg="#444", font=('Montserrat', 8, 'bold', 'underline')
    ).grid(row=row, column=col1, columnspan=2, sticky="w"); row += 1
    fila(row, col1, "Máx. [%]",  max_perdidas_cable_string); row += 1
    fila(row, col1, "Media [%]", media_perdidas_cable_string); row += 1

    tk.Label(frame_tabla_resumen_perdidas, text="DC Bus",
             bg=GRIS_SUAVE, fg="#444", font=('Montserrat', 8, 'bold', 'underline')
    ).grid(row=row, column=col1, columnspan=2, sticky="w"); row += 1
    fila(row, col1, "Máx. [%]",  max_perdidas_DC_Bus); row += 1
    fila(row, col1, "Media [%]", media_perdidas_DC_Bus); row += 2  # espacio extra entre bloques

    # --- Bloque 2: Subarray + Array ---
    col2 = 3
    row = 1
    tk.Label(frame_tabla_resumen_perdidas, text="Subarray",
             bg=GRIS_SUAVE, fg="#444", font=('Montserrat', 8, 'bold', 'underline')
    ).grid(row=row, column=col2, columnspan=2, sticky="w"); row += 1
    fila(row, col2, "Media [%]", media_perdidas_subarray); row += 2

    tk.Label(frame_tabla_resumen_perdidas, text="Array",
             bg=GRIS_SUAVE, fg="#444", font=('Montserrat', 8, 'bold', 'underline')
    ).grid(row=row, column=col2, columnspan=2, sticky="w"); row += 1
    fila(row, col2, "Máx. [%]",  max_perdidas_array); row += 1
    fila(row, col2, "Media [%]", media_perdidas_array); row += 2

    # --- Bloque 3: Total DC ---
    col3 = 6
    row = 1
    tk.Label(frame_tabla_resumen_perdidas, text="DC Losses",
             bg=GRIS_SUAVE, fg=ROJO_GRS, font=('Montserrat', 9, 'bold', 'underline')
    ).grid(row=row, column=col3, columnspan=2, sticky="w"); row += 1
    fila(row, col3, "Media [%]", media_perdidas_DC); row += 2
    
    tk.Label(frame_tabla_resumen_perdidas, text="Array ΔV",
             bg=GRIS_SUAVE, fg=ROJO_GRS, font=('Montserrat', 8, 'bold', 'underline')
    ).grid(row=row, column=col3, columnspan=2, sticky="w"); row += 1
    fila(row, col3, "Máx. [%]",       max_cdt_array); row += 1
    fila(row, col3, "Media [%]",      media_cdt_array); row += 2
    



def calcular_perdidas_cables():
    """Calcula las pérdidas los cables a partir de los parámetros vigentes."""
    def proceso_calculo_perdidas():
        """Ejecuta el proceso auxiliar encargado de calculo las pérdidas."""
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            global perdidas_cables_string, perdidas_DC_Bus, perdidas_array, pot_string_STC, cdt_array
            
            leer_valores_GUI_calculo_perdidas()
            pot_string_STC = [power_mod_STC * n_mods_serie for _ in range(n_bloques+1)] #temporalmente consideramos que la potencia de los string es identica en todos los bloques (misma potencia de modulo en cada bloque, sin sorting)
            if String_o_Bus == 'String Cable':
                perdidas_cables_string = np.full(sch_cable_de_string_pos.shape[:-1] + (2,), np.nan, dtype=float)
                perdidas_cables_string = alg_cables.calculo_perdidas_cables_string(strings_fisicos,bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, perdidas_cables_string, equi_ibfs, med_inst_cable_string_pos, med_inst_cable_string_neg, pot_string_STC, filas_con_cable_string, int_mod_STC, subarray_temp, DCBoxes_o_Inv_String, strings_ID, bifaciality,  cond_Cu_20, cond_Al_20)

                guardar_variables([perdidas_cables_string],['perdidas_cables_string'])
                
            elif String_o_Bus == 'DC Bus':
                perdidas_DC_Bus = np.full(sch_DC_Bus_pos.shape[:-1] + (2,), np.nan, dtype=float)
                perdidas_DC_Bus = alg_cables.calculo_perdidas_DC_Bus(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, perdidas_DC_Bus, equi_ibfs, pot_string_STC, filas_con_cable_string, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, long_string, int_mod_STC, subarray_temp, med_inst_DC_Bus_pos, tramo_aereo_DC_Bus_pos, strings_fisicos, slack_cable_subarray, desnivel_cable_por_pendientes_tramo_aereo, bifaciality,  cond_Cu_20, cond_Al_20)

                guardar_variables([perdidas_DC_Bus],['perdidas_DC_Bus'])
   
            else:
                perdidas_cables_string = np.full(sch_cable_de_string_pos.shape[:-1] + (2,), np.nan, dtype=float)
                perdidas_DC_Bus = np.full(sch_DC_Bus_pos.shape[:-1] + (2,), np.nan, dtype=float)
                
                perdidas_cables_string = alg_cables.calculo_perdidas_cables_string(strings_fisicos,bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, perdidas_cables_string, equi_ibfs, med_inst_cable_string_pos, med_inst_cable_string_neg, pot_string_STC, filas_con_cable_string, int_mod_STC, subarray_temp, DCBoxes_o_Inv_String, strings_ID, bifaciality,  cond_Cu_20, cond_Al_20)
                perdidas_DC_Bus = alg_cables.calculo_perdidas_DC_Bus(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, perdidas_DC_Bus, equi_ibfs, pot_string_STC, filas_con_cable_string, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, long_string, int_mod_STC, subarray_temp, med_inst_DC_Bus_pos, tramo_aereo_DC_Bus_pos, strings_fisicos, slack_cable_subarray, desnivel_cable_por_pendientes_tramo_aereo, bifaciality, cond_Cu_20, cond_Al_20)
                
                guardar_variables([perdidas_cables_string,perdidas_DC_Bus],['perdidas_cables_string', 'perdidas_DC_Bus'])
           
             
            perdidas_array = np.full(sch_array_cable_pos.shape[:-1] + (2,), np.nan, dtype=float) if DCBoxes_o_Inv_String == 'DC Boxes' else np.full(sch_array_cable.shape[:-1] + (2,), np.nan, dtype=float)
            

            if DCBoxes_o_Inv_String == 'DC Boxes':
                cdt_array = None
                perdidas_array, cdt_array = alg_cables.calculo_perdidas_array(bloque_inicial,n_bloques, max_b, max_c, DCBoxes_o_Inv_String, cajas_fisicas, equi_ibc, med_array_cable_pos, med_array_cable_neg, med_array_cable, uni_o_multipolar, int_mod_STC, array_temp, perdidas_array, pot_string_STC, cdt_array, pot_inv, cos_phi, v_inv, X_cable, material_array)
            else:
                cdt_array = np.full(sch_array_cable.shape[:-1] + (2,), np.nan, dtype=float)
                perdidas_array, cdt_array = alg_cables.calculo_perdidas_array(bloque_inicial,n_bloques, max_b, max_inv, DCBoxes_o_Inv_String, inv_como_cajas_fisicas, equi_ibv, med_array_cable_pos, med_array_cable_neg, med_array_cable, uni_o_multipolar, int_mod_STC, array_temp, perdidas_array, pot_string_STC, cdt_array, pot_inv, cos_phi, v_inv, X_cable, material_array, bifaciality, cond_Cu_20, cond_Al_20)

            guardar_variables([perdidas_array, cdt_array],['perdidas_array', 'cdt_array'])
            
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
                  
    def cerrar_ventana_tras_calcular_perdidas(ventana_carga):
        """Cierra la ventana de carga tras  calcular las pérdidas."""
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
        """Coordina la tarea asíncrona para calcular las pérdidas."""
        proceso_calculo_perdidas()
        root.after(0, lambda: cerrar_ventana_tras_calcular_perdidas(ventana_carga))
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_calcular_perdidas) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()



boton_array_CAD_read = tk.Button(frame_DCABLE_calc_local, text="Calculate", command=calcular_perdidas_cables, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_array_CAD_read.grid(row=4, column=5, padx=20)


    
def preparar_polilineas_para_calculo_zanjas():
    
    def proceso_preparar_polilineas():
        global pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO
        global error_simulacion
        error_simulacion = 'Sin error'

        try:
            if DCBoxes_o_Inv_String == 'DC Boxes':                
                pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO = alg_zanjas.densificar_polilineas_con_puntos_comunes(bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, max_c, max_tubos_DC_bloque, cajas_fisicas, filas_en_cajas, strings_fisicos, filas_con_cable_string, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO, DCBoxes_o_Inv_String)
            else:
                pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO = alg_zanjas.densificar_polilineas_con_puntos_comunes(bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, max_inv, max_tubos_DC_bloque, inv_como_cajas_fisicas, filas_en_cajas, strings_fisicos, filas_con_cable_string, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO, DCBoxes_o_Inv_String)
                
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
    


CABLES_SECTION = TabSection(
    key="cables",
    title="Cable design",
    icon="Pestaña 5.png",
    groups=FunctionalGroup(
        io={},
        processing={
            "read_mv_section_parameters": leer_valores_par_criterio_seccion_MV,
            "measure_mv_cable": medir_cable_MV,
            "parse_string_cable_inputs": leer_valores_GUI_cable_string,
            "parse_dc_bus_inputs": leer_valores_GUI_DC_Bus,
            "parse_mixed_options": leer_valores_GUI_opciones_mixtas,
            "measure_subarray_cables": medicion_cables_subarray,
            "parse_array_cable_inputs": leer_valores_GUI_cable_array,
            "measure_array_cables": medicion_cable_array,
            "parse_losses_inputs": leer_valores_GUI_calculo_perdidas,
            "calculate_losses": calcular_perdidas_cables,
            "prepare_trench_polylines": preparar_polilineas_para_calculo_zanjas,
            "coerce_int": devolver_entero,
            "coerce_float": devolver_float,
        },
        ui={
            "render_mv_measurement_inputs": entradas_medicion_cables_MV,
            "list_extra_dc_bus_inputs": listar_inputs_adicionales_dc_bus,
            "render_subarray_measurement_inputs": entradas_medicion_cables_subarray,
            "list_conductor_types": listar_uni_o_multipolar,
            "render_array_measurement_inputs": entradas_medicion_cables_array,
            "render_loss_inputs": entradas_calculo_perdidas,
            "ensure_summary_frame": _asegurar_frame_resumen,
            "show_loss_summary": mostrar_tabla_resumen_perdidas,
        },
    ),
)