# ============================================================================
# Pestaña 2: Dimensions
# ============================================================================

#---------------------------SEGUNDA PESTAÑA - ACOTACIONES Y DATOS DE TRACKERS--------------------

# Crear un frame para meter en él dos frames y darles un margen común respecto a los bordes
frame_DTR_container = tk.Frame(DTR, background=ROJO_SUAVE)
frame_DTR_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)

# Configurar la cuadrícula para que las filas y columnas se expandan en frame_DTR_container
frame_DTR_container.grid_rowconfigure(0, weight=1)  
frame_DTR_container.grid_columnconfigure(0, weight=1)  
frame_DTR_container.grid_columnconfigure(1, weight=10)  # ocupa 15 veces en x lo que ocupa el primero

# Crear un frame para meter en él los inputs de diseño
frame_DTR_datos = tk.Frame(frame_DTR_container, background=BLANCO_ROTO)
frame_DTR_datos.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

# Crear otro frame para meter en él los dibujos de los detalles
frame_DTR_dibujos = tk.Frame(frame_DTR_container, background=BLANCO_ROTO)
frame_DTR_dibujos.grid(row=0, column=1, sticky='nsew', padx=0, pady=0)

# Creamos las casillas de las acotaciones de los trackers en el primer frame
def crear_casillas_DTR(valores_dados_entradas, valores_dados_comboboxes):
    """Genera los campos y controles de la pestaña de dimensiones de trackers."""
    global entradas_DTR, entrada_config_tracker, entrada_pos_salto_motor_0, entrada_pos_salto_motor_1
    
    acotaciones_DTR = ["Max. SB (not isolated)", "RDSB", "String length","Pitch", "Separation", "H_mod", "W_mod", "Motor jump", "STT", "1st Pile distance", "Max no. tr per row", "W_B", "D_B", "Sep. Tr-B", "Sep. Trench-B", "No. mod/string"]
    entradas_DTR = []
    
    # Crear la fila inicial con los nombres de las columnas
    tk.Label(frame_DTR_datos, text="Dimension", bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold', 'underline')).grid(row=0, column=0, padx=0, pady=5, sticky='w')
    tk.Label(frame_DTR_datos, text="(m)", bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold', 'underline')).grid(row=0, column=1, padx=0, pady=5, sticky='e')
    
    # Crear las filas con las etiquetas y entradas
    max_row=0
    for i, acotaciones_DTR in enumerate(acotaciones_DTR):
        tk.Label(frame_DTR_datos, text=acotaciones_DTR, fg=ROJO_GRS, bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold')).grid(row=i+1, column=0, padx=0, pady=5, sticky='w')
        valor = tk.StringVar()
        valor.set(valores_dados_entradas[i])
        entrada = tk.Entry(frame_DTR_datos, textvariable = valor,  width=10)
        entrada.grid(row=i+1, column=1, padx=0, pady=5, sticky='e')
        entradas_DTR.append(entrada)
        max_row=max_row+1
    
    
    #Metemos una combobox para indicar si el tracker es monofila o bifila
    opciones_tr_conf = ["Single Row", "Double Row"]
    entrada_config_tracker = tk.StringVar(value = valores_dados_comboboxes[0])
    tk.Label(frame_DTR_datos, text='Tracker config.', fg=ROJO_GRS, bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold')).grid(row=max_row+1,column=0, padx=0,pady=5,sticky='w')
    ttk.Combobox(frame_DTR_datos, textvariable=entrada_config_tracker, values=opciones_tr_conf, width=11).grid(row=max_row+1,column=1, padx=0, pady=5,sticky='e')
    
    #Metemos otra combobox para indicar donde está el motor en trackers M
    opciones_mj_M = ["North", "Half", "South"]
    entrada_pos_salto_motor_0 = tk.StringVar(value = valores_dados_comboboxes[1])
    tk.Label(frame_DTR_datos, text='Motor loc. (M tracker)', fg=ROJO_GRS, bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold')).grid(row=max_row+2,column=0, padx=0,pady=5,sticky='w')
    ttk.Combobox(frame_DTR_datos, textvariable=entrada_pos_salto_motor_0, values=opciones_mj_M, width=11).grid(row=max_row+2,column=1, padx=0, pady=5,sticky='e')
    
    
    #Metemos otra combobox para indicar donde está el motor en trackers L
    opciones_mj_L = ["North", "Half", "South"]
    entrada_pos_salto_motor_1 = tk.StringVar(value = valores_dados_comboboxes[2])
    tk.Label(frame_DTR_datos, text='Motor loc. (L tracker)', fg=ROJO_GRS, bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold')).grid(row=max_row+3,column=0, padx=0,pady=5,sticky='w')
    ttk.Combobox(frame_DTR_datos, textvariable=entrada_pos_salto_motor_1, values=opciones_mj_L, width=11).grid(row=max_row+3,column=1, padx=0, pady=5,sticky='e')
    
    return max_row+3

valores_iniciales_entradas=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
valores_iniciales_comboboxes=[[],[],[]]
mr_casillas = crear_casillas_DTR(valores_iniciales_entradas,valores_iniciales_comboboxes)

#Importamos los dibujos de las acotaciones
imagen_DTR_Tracker_GEN = cargar_imagen("Dimensions - GEN.PNG", (250, 520))
imagen_DTR_Tracker_A   = cargar_imagen("Dimensions - Detail A.PNG", (350, 470))
imagen_DTR_Tracker_B   = cargar_imagen("Dimensions - Detail B.PNG", (300, 250))
imagen_DTR_Tracker_C   = cargar_imagen("Dimensions - Detail C.PNG", (390, 370))


detalle_DTR_Tracker_GEN = tk.Label(frame_DTR_dibujos, image=imagen_DTR_Tracker_GEN, bg=BLANCO_ROTO)
detalle_DTR_Tracker_GEN.place(relx=0.12, rely=0.15, anchor='n')

detalle_DTR_Tracker_A = tk.Label(frame_DTR_dibujos, image=imagen_DTR_Tracker_A, bg=BLANCO_ROTO)
detalle_DTR_Tracker_A.place(relx=0.4, rely=0.1, anchor='n')

detalle_DTR_Tracker_B = tk.Label(frame_DTR_dibujos, image=imagen_DTR_Tracker_B, bg=BLANCO_ROTO)
detalle_DTR_Tracker_B.place(relx=0.8, rely=0.05, anchor='n')

detalle_DTR_Tracker_C = tk.Label(frame_DTR_dibujos, image=imagen_DTR_Tracker_C, bg=BLANCO_ROTO)
detalle_DTR_Tracker_C.place(relx=0.8, rely=0.45, anchor='n')



# AÑADIMOS UN BOTON PARA EJECUTAR EL ALGORITMO CON ESTOS DATOS HASTA OBTENER LA POSICION FISICA DE CADA STRING
def simulacion_fisica_planta():
    
    """Lanza la simulación física de la planta y actualiza los resultados mostrados."""
    def proceso_sim_planta_fisica():
        """Ejecuta el proceso auxiliar encargado de la simulación la planta física."""
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
        
            filas, max_fpb = alg_planta_fv.agrupar_en_filas(trackers_pb, bloque_inicial,n_bloques, max_tpb, max_fpb, max_tpf, sep)
            
            # sin conocerlo, el maximo numero de bandas posible por bloque es como máximo igual al de filas (ninguna fila cercana a otra) aunque no sea real
            max_bpb = max_fpb
            
            bandas, max_b, max_fr = alg_planta_fv.agrupacion_en_bandas(filas, pitch, bloque_inicial,n_bloques, max_fpb, max_bpb, max_tpf, coord_PCS_DC_inputs)
            
            orientacion = alg_planta_fv.orientacion_hacia_inversor(bandas, coord_PCS_DC_inputs, bloque_inicial,n_bloques, max_b, max_fr)
            
            #sacamos las filas en las bandas y sus puntos de contorno, faltaria ordenarlas todavia
            filas_en_bandas, max_f_str_b = alg_planta_fv.sacar_y_ordenar_filas_en_bandas(bandas, orientacion, config_tracker, bloque_inicial,n_bloques, max_b, max_tpf, max_fr, h_modulo, pitch)
            
            contorno_bandas, contorno_bandas_sup, contorno_bandas_inf = alg_planta_fv.contorno_de_las_bandas(filas_en_bandas,bloque_inicial,n_bloques,max_b,max_f_str_b, h_modulo)
            
            #hallamos los tipos de bandas
            bandas_anexas, bandas_separadas, bandas_aisladas, bandas_intermedias_o_extremo = alg_planta_fv.clasificacion_bandas(bloque_inicial,n_bloques, max_b, contorno_bandas, coord_PCS_DC_inputs, orientacion, pasillo_entre_bandas, dist_min_b_separadas)
            
            #ordenamos las bandas segun criterio GRS y actualizamos las variables afectadas que luego se van a volver a usar
            bandas , orientacion,  bandas_anexas, bandas_separadas, bandas_intermedias_o_extremo, bandas_aisladas, filas_en_bandas, contorno_bandas, contorno_bandas_sup, contorno_bandas_inf = alg_planta_fv.ordenar_bandas(bandas,contorno_bandas, contorno_bandas_sup, contorno_bandas_inf, bandas_anexas, bandas_separadas, bandas_aisladas, bandas_intermedias_o_extremo, filas_en_bandas, orientacion,bloque_inicial,n_bloques,max_b, pasillo_entre_bandas)
            
            #calculamos la posicion fisica de cada string
            strings_fisicos, ori_str_ID, max_spf, dist_ext_opuesto_str = alg_planta_fv.filas_de_strings(bandas, filas_en_bandas, config_tracker, orientacion, bloque_inicial,n_bloques, max_b, max_f_str_b, max_tpf, h_modulo, pitch, salto_motor, pos_salto_motor_M, pos_salto_motor_L)
    
    
            guardar_variables([pasillo_entre_bandas, dist_min_b_separadas, long_string, pitch, sep, h_modulo, ancho_modulo, salto_motor, saliente_TT, dist_primera_pica_extremo_tr, max_tpf, ancho_caja, largo_caja, sep_caja_tracker, sep_zanja_tracker, config_tracker, pos_salto_motor_M, pos_salto_motor_L, n_mods_serie],['pasillo_entre_bandas', 'dist_min_b_separadas', 'long_string', 'pitch', 'sep', 'h_modulo', 'ancho_modulo', 'salto_motor', 'saliente_TT', 'dist_primera_pica_extremo_tr', 'max_tpf', 'ancho_caja', 'largo_caja', 'sep_caja_tracker', 'sep_zanja_tracker', 'config_tracker', 'pos_salto_motor_M', 'pos_salto_motor_L', 'n_mods_serie'])
            guardar_variables([filas, max_fpb, bandas, max_b, max_fr, orientacion, filas_en_bandas, max_f_str_b, contorno_bandas, contorno_bandas_sup, contorno_bandas_inf, bandas_anexas, bandas_separadas, bandas_aisladas, bandas_intermedias_o_extremo, strings_fisicos, ori_str_ID, max_spf, dist_ext_opuesto_str],['filas', 'max_fpb', 'bandas', 'max_b', 'max_fr', 'orientacion', 'filas_en_bandas', 'max_f_str_b', 'contorno_bandas', 'contorno_bandas_sup', 'contorno_bandas_inf', 'bandas_anexas', 'bandas_separadas', 'bandas_aisladas', 'bandas_intermedias_o_extremo', 'strings_fisicos', 'ori_str_ID', 'max_spf', 'dist_ext_opuesto_str'])
        
        except Exception:
            error_de_simulacion = 'Error'
            traceback.print_exc()
        
    def cerrar_ventana_tras_simular(ventana_carga):
        """Cierra la ventana de carga tras  simular."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
        except:
            print("Error al borrar el gif")

    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_3():
        """Coordina la tarea asíncrona número 3."""
        proceso_sim_planta_fisica()
        root.after(0, lambda: cerrar_ventana_tras_simular(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_3) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

        
boton_string_fisicos = tk.Button(frame_DTR_datos, text="Read model", command=simulacion_fisica_planta, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_string_fisicos.grid(row=mr_casillas+1, column=0, columnspan=2, pady=10)







DIMENSIONS_SECTION = TabSection(
    key="dimensions",
    title="Dimensions",
    icon="Pestaña 2.png",
    groups=FunctionalGroup(
        io={},
        processing={
            "simulate_physical_layout": simulacion_fisica_planta,
        },
        ui={
            "build_dimension_inputs": crear_casillas_DTR,
        },
    ),
)