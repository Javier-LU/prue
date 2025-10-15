# ============================================================================
# Pestaña 6: Trenches Design
#   - preparar_polilineas_para_calculo_zanjas(): prepara la geometría de zanjas.
#   - entradas_zanjas_DC(): recopila datos para zanjas de corriente continua.
#   - simular_zanjas_LV_automatico(): genera zanjas de baja tensión de forma automática.
#   - simular_zanjas_MV_manual(): permite definir manualmente zanjas de media tensión.
#   - combinar_zanjas(): fusiona resultados de DC, LV y MV en un único esquema.
# ============================================================================
#---------------------------SEXTA PESTAÑA - ZANJAS------------------------

#LAYOUT DE FRAMES PARA INTRODUCIR DATOS
# Crear un frame para dar un margen respecto a los bordes
frame_zanjas_container = tk.Frame(Trenches_NB, background=BLANCO_ROTO)
frame_zanjas_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)

#Dividimos el container en tres horizontales, uno para el boton de preparar zanjas, otro los procesos de DC, LV, MV, AS en un notebook y otro para el boton de combinar zanjas
frame_zanjas_container.grid_rowconfigure(0, weight=1)
frame_zanjas_container.grid_rowconfigure(1, weight=5)
frame_zanjas_container.grid_rowconfigure(2, weight=1)
frame_zanjas_container.grid_columnconfigure(0, weight=1) #añadimos el column para que se pueda expandir e-w aunque no pudiese desbordar

#Creamos los tres subframes
frame_preparar_polilineas =tk.Frame(frame_zanjas_container, background=BLANCO_ROTO)
frame_preparar_polilineas.grid(row=0, column=0, sticky='ew', padx=10, pady=0)
frame_preparar_polilineas.grid_columnconfigure(0, weight=1) #permitimos que se expanda

frame_procesos_zanjas =tk.Frame(frame_zanjas_container, background=BLANCO_ROTO)
frame_procesos_zanjas.grid(row=1, column=0, sticky='nsew', padx=10, pady=0)
frame_procesos_zanjas.grid_columnconfigure(0, weight=1) #permitimos que se expanda

frame_combinar_zanjas =tk.Frame(frame_zanjas_container, background=BLANCO_ROTO)
frame_combinar_zanjas.grid(row=2, column=0, sticky='ew', padx=10, pady=0)
frame_combinar_zanjas.grid_columnconfigure(0, weight=1) #permitimos que se expanda

        #Dividimos el subframe de procesos en dos, uno para zanjas dc y otro para lv
frame_procesos_zanjas.grid_columnconfigure(0, weight=1)
frame_procesos_zanjas.grid_columnconfigure(1, weight=2)

frame_zanjas_DC = tk.Frame(frame_procesos_zanjas, background=BLANCO_ROTO)
frame_zanjas_DC.grid(row=0, column=0, sticky='nsew', padx=10, pady=0)


# Crear el notebook para LV y MV
notebook_LV_MV = ttk.Notebook(frame_procesos_zanjas)
notebook_LV_MV.grid(row=0, column=1, columnspan=2, sticky='nsew', padx=10, pady=0)

frame_zanjas_LV = tk.Frame(frame_procesos_zanjas, background=BLANCO_ROTO)
frame_zanjas_MV = tk.Frame(frame_procesos_zanjas, background=BLANCO_ROTO)

# Añadir los frames como pestañas
notebook_LV_MV.add(frame_zanjas_LV, text='LV Trenches')
notebook_LV_MV.add(frame_zanjas_MV, text='MV Trenches')



#Dividimos el frame de zanjas LV en dos subframes, uno para el prediseño y otro para los calculos de ancho de zanja
frame_zanjas_LV.grid_rowconfigure(0, weight=1)
frame_zanjas_LV.grid_rowconfigure(1, weight=7)

    #Creamos los dos subframes LV
frame_zanjas_LV_prediseño = tk.Frame(frame_zanjas_LV, background=BLANCO_ROTO)
frame_zanjas_LV_prediseño.grid(row=0, column=0, sticky='nsew', padx=20, pady=0)

frame_zanjas_LV_calculo = tk.Frame(frame_zanjas_LV, background=BLANCO_ROTO)
frame_zanjas_LV_calculo.grid(row=1, column=0, sticky='nsew', padx=20, pady=0)
        #Dividimos el subframe de calculo en 2 para albergar las dos tablas manuales
frame_zanjas_LV_calculo.grid_columnconfigure(0, weight=1)
frame_zanjas_LV_calculo.grid_columnconfigure(1, weight=1)
            #Creamos los dos subframes adicionales
frame_tabla_config_zanjas_LV = tk.Frame(frame_zanjas_LV_calculo, background=BLANCO_ROTO)
frame_tabla_config_zanjas_LV.grid(row=0, column=0, sticky='nsew', padx=10, pady=0)          

frame_tabla_anchos_zanjas_LV = tk.Frame(frame_zanjas_LV_calculo, background=BLANCO_ROTO)
frame_tabla_anchos_zanjas_LV.grid(row=0, column=1, sticky='nsew', padx=10, pady=0)         




#Dividimos el frame de zanjas MV en dos subframes, uno para el prediseño y otro para los calculos de ancho de zanja
frame_zanjas_MV.grid_rowconfigure(0, weight=1)
frame_zanjas_MV.grid_rowconfigure(1, weight=7)

    #Creamos los dos subframes MV
frame_zanjas_MV_prediseño = tk.Frame(frame_zanjas_MV, background=BLANCO_ROTO)
frame_zanjas_MV_prediseño.grid(row=0, column=0, sticky='nsew', padx=20, pady=0)

frame_zanjas_MV_calculo = tk.Frame(frame_zanjas_MV, background=BLANCO_ROTO)
frame_zanjas_MV_calculo.grid(row=1, column=0, sticky='nsew', padx=20, pady=0)
        #Dividimos el subframe de calculo en 2 para albergar las dos tablas manuales
frame_zanjas_MV_calculo.grid_columnconfigure(0, weight=1)
frame_zanjas_MV_calculo.grid_columnconfigure(1, weight=1)
            #Creamos los dos subframes adicionales
frame_tabla_config_zanjas_MV = tk.Frame(frame_zanjas_MV_calculo, background=BLANCO_ROTO)
frame_tabla_config_zanjas_MV.grid(row=0, column=0, sticky='nsew', padx=10, pady=0)          

frame_tabla_anchos_zanjas_MV = tk.Frame(frame_zanjas_MV_calculo, background=BLANCO_ROTO)
frame_tabla_anchos_zanjas_MV.grid(row=0, column=1, sticky='nsew', padx=10, pady=0)         



#---------Preparar polilineas

    
def preparar_polilineas_para_calculo_zanjas():
    
    """Prepara las polilíneas para calculo las zanjas a partir de los datos disponibles."""
    def proceso_preparar_polilineas():
        """Ejecuta el proceso auxiliar encargado de preparar las polilíneas."""
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
        """Cierra la ventana de carga tras  preparar las polilíneas."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            
            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_preparar_polilineas():
        """Coordina la tarea asíncrona para preparar las polilíneas."""
        proceso_preparar_polilineas()
        root.after(0, lambda: cerrar_ventana_tras_preparar_polilineas(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_preparar_polilineas) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
    
boton_preparar_polilineas = tk.Button(frame_preparar_polilineas, text="Prepare all polylines", command=preparar_polilineas_para_calculo_zanjas, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'), anchor='center')
boton_preparar_polilineas.grid(row=0, column=0, pady=20)   





#-------Entradas diseño de zanjas
def entradas_zanjas_DC(valores_dados_zanjas_DC):
    """Construye los campos de entrada para las zanjas DC."""
    global entrada_max_t_DC1, valor_ancho_DC1, valor_ancho_DC2

        #Maximo numero de tubos en DC1    
    etiqueta_max_t_DC1 = tk.Label(frame_zanjas_DC, text='Max. no. conduits in DC1', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_max_t_DC1.grid(row=0, column=0)
    valor_max_t_DC1 = tk.StringVar()
    valor_max_t_DC1.set(valores_dados_zanjas_DC[0])
    entrada_max_t_DC1 = tk.Entry(frame_zanjas_DC, textvariable=valor_max_t_DC1, width=5)
    entrada_max_t_DC1.grid(row=0, column=1, padx=(5,20), pady=(15,10))

        #Ancho DC1
    etiqueta_ancho_DC1 = tk.Label(frame_zanjas_DC, text="DC1 width (m)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_ancho_DC1.grid(row=1, column=0, padx=(10,0),pady=(15,10))
    valor_ancho_DC1 = tk.StringVar()
    valor_ancho_DC1.set(valores_dados_zanjas_DC[1])
    entrada_ancho_DC1 = tk.Entry(frame_zanjas_DC, textvariable=valor_ancho_DC1, width=5)
    entrada_ancho_DC1.grid(row=1, column=1, padx=(5,20), pady=(15,10))

        #Ancho DC2
    etiqueta_ancho_DC2 = tk.Label(frame_zanjas_DC, text="DC2 width (m)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
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
    
    etiqueta_met_diseño = tk.Label(frame_zanjas_LV_prediseño, text='Design method', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_met_diseño.grid(row=0, column=0)
    combobox_met_diseño=ttk.Combobox(frame_zanjas_LV_prediseño, textvariable=entrada_met_diseño, values=opciones_met_diseño)
    combobox_met_diseño.grid(row=0, column=1)
    
        #Maximo numero de circuitos por tipo de zanja
    opciones_max_c_tz = ['1', '2', '3', '4']
    entrada_max_c_tz = tk.StringVar(value = valores_iniciales_prediseño_zanjas_LV[1])
    
    etiqueta_max_c_tz = tk.Label(frame_zanjas_LV_prediseño, text='Max. no. circuits per trench type', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_max_c_tz.grid(row=1, column=0)
    combobox_max_c_tz=ttk.Combobox(frame_zanjas_LV_prediseño, textvariable=entrada_max_c_tz, values=opciones_max_c_tz)
    combobox_max_c_tz.grid(row=1, column=1)
    



valores_iniciales_prediseño_zanjas_LV=[[],[],[]]





def entradas_zanjas_LV_auto(valores_zanjas_LV_auto):
    """Construye los campos de entrada para las zanjas LV auto."""
    #Limpiamos los widgets existentes antes de rellenar el frame
    for widget in frame_tabla_config_zanjas_LV.winfo_children():
        widget.destroy()
    for widget in frame_tabla_anchos_zanjas_LV.winfo_children():
        widget.destroy()
    
    global valor_ancho_min, valor_int_circ, entrada_secciones_LV, valor_cab_diam, valor_temp, valor_res_ter, entrada_material_cond, entrada_material_ais, entrada_met_inst
    
    #Entradas para simulacion automatica
        #Ancho_minimo
    etiqueta_ancho_min = tk.Label(frame_tabla_config_zanjas_LV, text="Minimum width (m)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_ancho_min.grid(row=2, column=0, padx=(10,0),pady=(15,10))
    valor_ancho_min = tk.StringVar()
    valor_ancho_min.set(valores_zanjas_LV_auto[0])
    entrada_ancho_min = tk.Entry(frame_tabla_config_zanjas_LV, textvariable=valor_ancho_min, width=5)
    entrada_ancho_min.grid(row=2, column=1, padx=(5,20), pady=(15,10))
        #Intensidad de circuitos
    etiqueta_int_circ = tk.Label(frame_tabla_config_zanjas_LV, text="Circuit Current (A)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_int_circ.grid(row=3, column=0, padx=(10,0),pady=(15,10))
    valor_int_circ = tk.StringVar()
    valor_int_circ.set(valores_zanjas_LV_auto[1])
    entrada_int_circ = tk.Entry(frame_tabla_config_zanjas_LV, textvariable=valor_int_circ, width=5)
    entrada_int_circ.grid(row=3, column=1, padx=(5,20), pady=(15,10))

        #Combobox para seccion de conductor
    opciones_secciones_LV = ['120','150','185','240','300','400']
    entrada_secciones_LV = tk.StringVar(value = valores_zanjas_LV_auto[2])
    
    etiqueta_secciones_LV = tk.Label(frame_tabla_config_zanjas_LV, text='Cross section', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_secciones_LV.grid(row=4, column=0)
    combobox_secciones_LV=ttk.Combobox(frame_tabla_config_zanjas_LV, textvariable=entrada_secciones_LV, values=opciones_secciones_LV)
    combobox_secciones_LV.grid(row=4, column=1)
        #Diametro cable
    etiqueta_cab_diam = tk.Label(frame_tabla_config_zanjas_LV, text="Cable diameter (mm)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_cab_diam.grid(row=5, column=0, padx=(10,0),pady=(15,10))
    valor_cab_diam = tk.StringVar()
    valor_cab_diam.set(valores_zanjas_LV_auto[3])
    entrada_cab_diam = tk.Entry(frame_tabla_config_zanjas_LV, textvariable=valor_cab_diam, width=5)
    entrada_cab_diam.grid(row=5, column=1, padx=(5,20), pady=(15,10))
        #Temperatura de suelo
    etiqueta_temp = tk.Label(frame_tabla_config_zanjas_LV, text="Soil temperature (ºC)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_temp.grid(row=6, column=0, padx=(10,0),pady=(15,10))
    valor_temp = tk.StringVar()
    valor_temp.set(valores_zanjas_LV_auto[4])
    entrada_temp = tk.Entry(frame_tabla_config_zanjas_LV, textvariable=valor_temp, width=5)
    entrada_temp.grid(row=6, column=1, padx=(5,20), pady=(15,10))
        #Resistividad termica
    etiqueta_res_ter = tk.Label(frame_tabla_config_zanjas_LV, text="Soil resistivity (W/m-K)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_res_ter.grid(row=7, column=0, padx=(10,0),pady=(15,10))
    valor_res_ter = tk.StringVar()
    valor_res_ter.set(valores_zanjas_LV_auto[5])
    entrada_res_ter = tk.Entry(frame_tabla_config_zanjas_LV, textvariable=valor_res_ter, width=5)
    entrada_res_ter.grid(row=7, column=1, padx=(5,20), pady=(15,10))
    
        #Combobox para material del conductor
    opciones_material_cond = ["Cu", "Al"]
    entrada_material_cond = tk.StringVar(value = valores_zanjas_LV_auto[6])
    
    etiqueta_material_cond = tk.Label(frame_tabla_config_zanjas_LV, text='Conductor material', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_material_cond.grid(row=8, column=0)
    combobox_material_cond=ttk.Combobox(frame_tabla_config_zanjas_LV, textvariable=entrada_material_cond, values=opciones_material_cond)
    combobox_material_cond.grid(row=8, column=1)
    
        #Combobox para material del aislante
    opciones_material_ais = ["PVC (70ºC)", "XLPE or EPR (90ºC)"]
    entrada_material_ais = tk.StringVar(value = valores_zanjas_LV_auto[7])
    
    etiqueta_material_ais = tk.Label(frame_tabla_config_zanjas_LV, text='Insulation material', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_material_ais.grid(row=9, column=0)
    combobox_material_ais=ttk.Combobox(frame_tabla_config_zanjas_LV, textvariable=entrada_material_ais, values=opciones_material_ais)
    combobox_material_ais.grid(row=9, column=1)
    
        #Combobox para método de instalacion
    opciones_met_inst = ["Directly buried", "Buried in conduits"]
    entrada_met_inst = tk.StringVar(value = valores_zanjas_LV_auto[8])
    
    etiqueta_met_inst = tk.Label(frame_tabla_config_zanjas_LV, text='Installation method', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_met_inst.grid(row=10, column=0)
    combobox_met_inst=ttk.Combobox(frame_tabla_config_zanjas_LV, textvariable=entrada_met_inst, values=opciones_met_inst)
    combobox_met_inst.grid(row=10, column=1)


    boton_sim_LV_trenches_auto = tk.Button(frame_tabla_config_zanjas_LV, text="Simulate LV Trenches", command=simular_zanjas_LV_automatico, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
    boton_sim_LV_trenches_auto.grid(row=11, column=0, pady=20)   
    
valores_entradas_zanjas_LV_auto=[[],[],[],[],[],  [],[],[],[]]



#Inicializamos estos por si se llega sin haber guardado antes
anchos_tipos_MV = []
anchos_tipos_LV = []


def entradas_zanjas_LV_manual(matriz_de_datos):
    """Construye los campos de entrada para las zanjas LV manual."""
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
            """Actualiza la región de scroll para mostrar toda la tabla manual."""
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
            """Exporta la tabla subtipos LV a un archivo externo."""
            df_subtipos_LV=pd.DataFrame(config_circ_zanjas_LV)
            df_subtipos_LV.to_excel("Circuits in LV Trenches.xlsx", index=False, header=False)
            messagebox.showinfo("Export completed","Table exported to: Circuits in LV Trenches, in same folder.")
        
        boton_flecha = tk.Button(frame_tabla_config_zanjas_LV, text="Export to Excel", command=exportar_tabla_subtipos_LV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
        boton_flecha.grid(row=2, column=0)
        
        def importar_tabla_subtipos_LV():
            """Importa la tabla subtipos LV desde un archivo externo."""
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
        
        boton_flecha = tk.Button(frame_tabla_config_zanjas_LV, text="Import from Excel", command=importar_tabla_subtipos_LV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
        boton_flecha.grid(row=2, column=1)
        
def entradas_anchos_manuales_LV():
    """Construye los campos de entrada para los anchos manuales LV."""
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
    
    if not anchos_tipos_LV:
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
    
    boton_sim_LV_trenches_auto = tk.Button(frame_tabla_anchos_zanjas_LV, text="Simulate LV Trenches", command=simular_zanjas_LV_manual, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
    boton_sim_LV_trenches_auto.grid(row=max_i+1, column=0, pady=20) 
    
    
    
    
    
    
def entradas_prediseño_zanjas_MV(valores_iniciales_prediseño_zanjas_MV):
    global entrada_met_diseño_mv, entrada_max_c_tz_mv
    
        #Combobox para método de diseño
    opciones_met_diseño_mv = ["Manual", "IEC 60364", "AS/NZS 3008"]
    entrada_met_diseño_mv = tk.StringVar(value = valores_iniciales_prediseño_zanjas_MV[0])
    
    etiqueta_met_diseño_mv = tk.Label(frame_zanjas_MV_prediseño, text='Design method', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_met_diseño_mv.grid(row=0, column=0)
    combobox_met_diseño_mv=ttk.Combobox(frame_zanjas_MV_prediseño, textvariable=entrada_met_diseño_mv, values=opciones_met_diseño_mv)
    combobox_met_diseño_mv.grid(row=0, column=1)
    
        #Maximo numero de circuitos por tipo de zanja
    opciones_max_c_tz_mv = ['1', '2', '3', '4']
    entrada_max_c_tz_mv = tk.StringVar(value = valores_iniciales_prediseño_zanjas_MV[1])
    
    etiqueta_max_c_tz_mv = tk.Label(frame_zanjas_MV_prediseño, text='Max. no. circuits per trench type', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_max_c_tz_mv.grid(row=1, column=0)
    combobox_max_c_tz_mv=ttk.Combobox(frame_zanjas_MV_prediseño, textvariable=entrada_max_c_tz_mv, values=opciones_max_c_tz_mv)
    combobox_max_c_tz_mv.grid(row=1, column=1)
    



valores_iniciales_prediseño_zanjas_MV=[[],[],[]]    
    
    

def entradas_zanjas_MV_auto(valores_zanjas_MV_auto):
    """Construye los campos de entrada para las zanjas MV auto."""
    #Limpiamos los widgets existentes antes de rellenar el frame
    for widget in frame_tabla_config_zanjas_MV.winfo_children():
        widget.destroy()
    for widget in frame_tabla_anchos_zanjas_MV.winfo_children():
        widget.destroy()
    
    global valor_ancho_min, valor_int_circ, entrada_secciones_MV, valor_cab_diam, valor_temp, valor_res_ter, entrada_material_cond, entrada_material_ais, entrada_met_inst
    
    #Entradas para simulacion automatica
        #Ancho_minimo
    etiqueta_ancho_min = tk.Label(frame_tabla_config_zanjas_MV, text="Minimum width (m)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_ancho_min.grid(row=2, column=0, padx=(10,0),pady=(15,10))
    valor_ancho_min = tk.StringVar()
    valor_ancho_min.set(valores_zanjas_MV_auto[0])
    entrada_ancho_min = tk.Entry(frame_tabla_config_zanjas_MV, textvariable=valor_ancho_min, width=5)
    entrada_ancho_min.grid(row=2, column=1, padx=(5,20), pady=(15,10))
        #Intensidad de circuitos
    etiqueta_int_circ = tk.Label(frame_tabla_config_zanjas_MV, text="Circuit Current (A)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_int_circ.grid(row=3, column=0, padx=(10,0),pady=(15,10))
    valor_int_circ = tk.StringVar()
    valor_int_circ.set(valores_zanjas_MV_auto[1])
    entrada_int_circ = tk.Entry(frame_tabla_config_zanjas_MV, textvariable=valor_int_circ, width=5)
    entrada_int_circ.grid(row=3, column=1, padx=(5,20), pady=(15,10))

        #Combobox para seccion de conductor
    opciones_secciones_MV = ['120','150','185','240','300','400']
    entrada_secciones_MV = tk.StringVar(value = valores_zanjas_MV_auto[2])
    
    etiqueta_secciones_MV = tk.Label(frame_tabla_config_zanjas_MV, text='Cross section', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_secciones_MV.grid(row=4, column=0)
    combobox_secciones_MV=ttk.Combobox(frame_tabla_config_zanjas_MV, textvariable=entrada_secciones_MV, values=opciones_secciones_MV)
    combobox_secciones_MV.grid(row=4, column=1)
        #Diametro cable
    etiqueta_cab_diam = tk.Label(frame_tabla_config_zanjas_MV, text="Cable diameter (mm)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_cab_diam.grid(row=5, column=0, padx=(10,0),pady=(15,10))
    valor_cab_diam = tk.StringVar()
    valor_cab_diam.set(valores_zanjas_MV_auto[3])
    entrada_cab_diam = tk.Entry(frame_tabla_config_zanjas_MV, textvariable=valor_cab_diam, width=5)
    entrada_cab_diam.grid(row=5, column=1, padx=(5,20), pady=(15,10))
        #Temperatura de suelo
    etiqueta_temp = tk.Label(frame_tabla_config_zanjas_MV, text="Soil temperature (ºC)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_temp.grid(row=6, column=0, padx=(10,0),pady=(15,10))
    valor_temp = tk.StringVar()
    valor_temp.set(valores_zanjas_MV_auto[4])
    entrada_temp = tk.Entry(frame_tabla_config_zanjas_MV, textvariable=valor_temp, width=5)
    entrada_temp.grid(row=6, column=1, padx=(5,20), pady=(15,10))
        #Resistividad termica
    etiqueta_res_ter = tk.Label(frame_tabla_config_zanjas_MV, text="Soil resistivity (W/m-K)", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_res_ter.grid(row=7, column=0, padx=(10,0),pady=(15,10))
    valor_res_ter = tk.StringVar()
    valor_res_ter.set(valores_zanjas_MV_auto[5])
    entrada_res_ter = tk.Entry(frame_tabla_config_zanjas_MV, textvariable=valor_res_ter, width=5)
    entrada_res_ter.grid(row=7, column=1, padx=(5,20), pady=(15,10))
    
        #Combobox para material del conductor
    opciones_material_cond = ["Cu", "Al"]
    entrada_material_cond = tk.StringVar(value = valores_zanjas_MV_auto[6])
    
    etiqueta_material_cond = tk.Label(frame_tabla_config_zanjas_MV, text='Conductor material', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_material_cond.grid(row=8, column=0)
    combobox_material_cond=ttk.Combobox(frame_tabla_config_zanjas_MV, textvariable=entrada_material_cond, values=opciones_material_cond)
    combobox_material_cond.grid(row=8, column=1)
    
        #Combobox para material del aislante
    opciones_material_ais = ["PVC (70ºC)", "XLPE or EPR (90ºC)"]
    entrada_material_ais = tk.StringVar(value = valores_zanjas_MV_auto[7])
    
    etiqueta_material_ais = tk.Label(frame_tabla_config_zanjas_MV, text='Insulation material', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_material_ais.grid(row=9, column=0)
    combobox_material_ais=ttk.Combobox(frame_tabla_config_zanjas_MV, textvariable=entrada_material_ais, values=opciones_material_ais)
    combobox_material_ais.grid(row=9, column=1)
    
        #Combobox para método de instalacion
    opciones_met_inst = ["Directly buried", "Buried in conduits"]
    entrada_met_inst = tk.StringVar(value = valores_zanjas_MV_auto[8])
    
    etiqueta_met_inst = tk.Label(frame_tabla_config_zanjas_MV, text='Installation method', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_met_inst.grid(row=10, column=0)
    combobox_met_inst=ttk.Combobox(frame_tabla_config_zanjas_MV, textvariable=entrada_met_inst, values=opciones_met_inst)
    combobox_met_inst.grid(row=10, column=1)


    boton_sim_MV_trenches_auto = tk.Button(frame_tabla_config_zanjas_MV, text="Simulate MV Trenches", command=simular_zanjas_MV_automatico, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
    boton_sim_MV_trenches_auto.grid(row=11, column=0, pady=20)   
    
valores_entradas_zanjas_MV_auto=[[],[],[],[],[],  [],[],[],[]]





def entradas_zanjas_MV_manual(matriz_de_datos):
    """Construye los campos de entrada para las zanjas MV manual."""
    if matriz_de_datos.size>0:
        #Limpiamos los widgets existentes antes de rellenar el frame (pero no rompemos los frames internos)
        for widget in frame_tabla_config_zanjas_MV.winfo_children():
            if not isinstance(widget, tk.Frame):
                widget.destroy()    

 
        # Canvas con scroll
        canvas_MV = tk.Canvas(frame_tabla_config_zanjas_MV, height=400)
        scrollbar_MV_x = tk.Scrollbar(frame_tabla_config_zanjas_MV, orient="horizontal", command=canvas_MV.xview)
        scrollbar_MV_y = tk.Scrollbar(frame_tabla_config_zanjas_MV, orient="vertical", command=canvas_MV.yview)
        canvas_MV.configure(xscrollcommand=scrollbar_MV_x.set)
        canvas_MV.configure(yscrollcommand=scrollbar_MV_y.set)
        
        scrollbar_MV_x.grid(row=1, column=0, sticky='ew')
        scrollbar_MV_y.grid(row=0, column=1, sticky='ns')
        canvas_MV.grid(row=0, column=0, sticky='nsew')
        
        frame_MV_manual = tk.Frame(canvas_MV)
        canvas_MV.create_window((0, 0), window=frame_MV_manual, anchor="nw")
        
        # Fuente uniforme tipo tabla
        tabla_fuente = font.Font(family="Courier", size=10)
        
        # Encabezados
        for j in range(0,len(matriz_de_datos[0,:])):
            if j==0 or j==1:
                ancho_celda = 10
            else:
                ancho_celda = 5
                
            header = tk.Label(frame_MV_manual, text=matriz_de_datos[0,j], bg="#f0f0f0", font=("HeMVetica", 10, "bold"),relief="ridge", width=ancho_celda, anchor="center", borderwidth=1)
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
                    e = tk.Entry(frame_MV_manual, width=ancho_celda, font=tabla_fuente, relief="solid", borderwidth=1,justify="center", bg="#fff")
                    e.insert(0, matriz_de_datos[i,j])
                    e.grid(row=i+1, column=j, sticky="nsew")
                    entradas_subtipos.append(e)
                else:
                    lbl = tk.Label(frame_MV_manual, text=matriz_de_datos[i,j], width=ancho_celda, font=tabla_fuente, relief="solid", borderwidth=1, bg="#e6e6e6", anchor="center")
                    lbl.grid(row=i+1, column=j, sticky="nsew")
        
        # Ajustar scroll dinámico
        def ajustar_scroll(event):
            """Actualiza la región de scroll para mostrar toda la tabla manual."""
            canvas_MV.configure(scrollregion=canvas_MV.bbox("all"))
        
        frame_MV_manual.bind("<Configure>", ajustar_scroll)
        
        
        
        #Aprovechamsos para crear ya los encabezados de la tabla de anchos
        
        header = tk.Label(frame_tabla_anchos_zanjas_MV, text="Trench type", bg="#f0f0f0", font=("HeMVetica", 10, "bold"),relief="ridge", width=10, anchor="center", borderwidth=1)
        header.grid(row=0, column=0, sticky="nsew")

        header = tk.Label(frame_tabla_anchos_zanjas_MV, text="Subtype", bg="#f0f0f0", font=("HeMVetica", 10, "bold"),relief="ridge", width=10, anchor="center", borderwidth=1)
        header.grid(row=0, column=1, sticky="nsew")       
        
        header = tk.Label(frame_tabla_anchos_zanjas_MV, text="Width (m)", bg="#f0f0f0", font=("HeMVetica", 10, "bold"),relief="ridge", width=10, anchor="center", borderwidth=1)
        header.grid(row=0, column=2, sticky="nsew")
        
        
        boton_flecha = tk.Button(frame_tabla_config_zanjas_MV, text="→", font=("HeMVetica", 20), command=entradas_anchos_manuales_MV)
        boton_flecha.grid(row=0, column=2)
    
    
        def exportar_tabla_subtipos_MV():
            """Exporta la tabla subtipos MV a un archivo externo."""
            df_subtipos_MV=pd.DataFrame(config_circ_zanjas_MV)
            df_subtipos_MV.to_excel("Circuits in MV Trenches.xlsx", index=False, header=False)
            messagebox.showinfo("Export completed","Table exported to: Circuits in MV Trenches, in same folder.")
        
        boton_flecha = tk.Button(frame_tabla_config_zanjas_MV, text="Export to Excel", command=exportar_tabla_subtipos_MV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
        boton_flecha.grid(row=2, column=0)
        
        def importar_tabla_subtipos_MV():
            """Importa la tabla subtipos MV desde un archivo externo."""
            ruta_subtipos_MV = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
            if not ruta_subtipos_MV:
                print("No se seleccionó ningún archivo.")
                return []
        
            extraccion_subtipos_MV = pd.read_excel(ruta_subtipos_MV)
        
            # Calcular hasta dónde hay valores en 'Trench types'
            cantidad_valores = extraccion_subtipos_MV['Trench type'].notna().sum()
        
            # Obtener los subtipos hasta esa fila, reemplazando NaN por ''
            subtypes_MV = extraccion_subtipos_MV.loc[:cantidad_valores - 1, 'Subtype'].fillna('').tolist()
        
            # Actualizar GUI
            global entradas_subtipos
            
            for i in range(1, len(entradas_subtipos)):
                if i - 1 < len(subtypes_MV):
                    entradas_subtipos[i].delete(0, tk.END)
                    entradas_subtipos[i].insert(0, subtypes_MV[i - 1])
            
            return subtypes_MV
        
        boton_flecha = tk.Button(frame_tabla_config_zanjas_MV, text="Import from Excel", command=importar_tabla_subtipos_MV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
        boton_flecha.grid(row=2, column=1)
        
def entradas_anchos_manuales_MV():
    """Construye los campos de entrada para los anchos manuales MV."""
    global subtipos_introducidos, config_circ_zanjas_MV
    subtipos_introducidos = [entrada.get() for entrada in entradas_subtipos[1:]]
    subtipos_introducidos.insert(0,'Subtype')
    
    #Guardamos los valores introducidos en la primera tabla
    config_circ_zanjas_MV[:,1]=subtipos_introducidos
    
    guardar_variables([config_circ_zanjas_MV], ['config_circ_zanjas_MV'])
    
    
    
    #Sacamos valores unicos para la segunda tabla
    global tipos_y_subtipos_unicos_MV
    identificadores = []
    for i in range(1,len(config_circ_zanjas_MV[:,0])):
        identificadores.append((str(config_circ_zanjas_MV[i,0]),subtipos_introducidos[i]))
    
    tipos_y_subtipos_unicos_MV = list(dict.fromkeys(identificadores))


    #---GUI

    # Fuente uniforme tipo tabla
    tabla_fuente = font.Font(family="Courier", size=10)
    


    #Limpiamos los widgets existentes antes de rellenar el frame y voMVemos a crear los encabezados
    for widget in frame_tabla_anchos_zanjas_MV.winfo_children():
        if not isinstance(widget, tk.Frame):
            widget.destroy() 
            
    header = tk.Label(frame_tabla_anchos_zanjas_MV, text="Trench type", bg="#f0f0f0", font=("HeMVetica", 10, "bold"),relief="ridge", width=10, anchor="center", borderwidth=1)
    header.grid(row=0, column=0, sticky="nsew")

    header = tk.Label(frame_tabla_anchos_zanjas_MV, text="Subtype", bg="#f0f0f0", font=("HeMVetica", 10, "bold"),relief="ridge", width=10, anchor="center", borderwidth=1)
    header.grid(row=0, column=1, sticky="nsew")       
    
    header = tk.Label(frame_tabla_anchos_zanjas_MV, text="Width (m)", bg="#f0f0f0", font=("HeMVetica", 10, "bold"),relief="ridge", width=10, anchor="center", borderwidth=1)
    header.grid(row=0, column=2, sticky="nsew")

            
    #Entradas tipo celda
    global entradas_anchos_tipos_MV, anchos_tipos_MV
    
    if not anchos_tipos_MV:
        anchos_tipos_MV = [''] * len(tipos_y_subtipos_unicos_MV)
        
    entradas_anchos_tipos_MV = []
    
    for i in range(0,len(tipos_y_subtipos_unicos_MV)):
        for j in range(0,3):
            ancho_celda = 10                 
            if j == 2:
                e_a = tk.Entry(frame_tabla_anchos_zanjas_MV, width=ancho_celda, font=tabla_fuente, relief="solid", borderwidth=1,justify="center", bg="#fff")
                e_a.insert(0, anchos_tipos_MV[i])
                e_a.grid(row=i+1, column=j, sticky="nsew")
                entradas_anchos_tipos_MV.append(e_a)
            else:
                lbl = tk.Label(frame_tabla_anchos_zanjas_MV, text=tipos_y_subtipos_unicos_MV[i][j], width=ancho_celda, font=tabla_fuente, relief="solid", borderwidth=1, bg="#e6e6e6", anchor="center")
                lbl.grid(row=i+1, column=j, sticky="nsew")
    
        
    max_i=len(tipos_y_subtipos_unicos_MV)
    
    boton_sim_MV_trenches_auto = tk.Button(frame_tabla_anchos_zanjas_MV, text="Simulate MV Trenches", command=simular_zanjas_MV_manual, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
    boton_sim_MV_trenches_auto.grid(row=max_i+1, column=0, pady=20) 
    
        
    
    
    
    

#-------Simular ZANJAS DC

def simular_zanjas_DC():
    
    """Simula las zanjas DC y actualiza los resultados."""
    def proceso_simular_zanjas_DC():
        
        """Ejecuta el proceso auxiliar encargado de simular las zanjas DC."""
        global zanjas_DC_ID, PB_zanjas_DC_ID, n_tubos_max_DC1, ancho_DC1, ancho_DC2
        global error_simulacion
        error_simulacion = 'Sin error'

        try:
            #Leer entrada para luego resumen y dibujo
            n_tubos_max_DC1 = int(entrada_max_t_DC1.get())
            ancho_DC1 = float(valor_ancho_DC1.get())
            ancho_DC2 = float(valor_ancho_DC2.get())
            
            #Funcion de simulacion (independiente de las entradas)
            zanjas_DC_ID, PB_zanjas_DC_ID = alg_zanjas.trazado_zanjas_DC_y_conteo_tubos_circuitos_en_zanja(String_o_Bus,bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf,max_p, filas_en_cajas, strings_fisicos, pol_cable_string, pol_DC_Bus, filas_con_cable_string, pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque)
                                                    
            guardar_variables([zanjas_DC_ID, PB_zanjas_DC_ID, n_tubos_max_DC1,ancho_DC1,ancho_DC2],['zanjas_DC_ID', 'PB_zanjas_DC_ID','n_tubos_max_DC1','ancho_DC1','ancho_DC2'])
        except:
            error_simulacion = 'Error'
            traceback.print_exc()
            
    def cerrar_ventana_tras_simular_zanjas_DC(ventana_carga):
        """Cierra la ventana de carga tras  simular las zanjas DC."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
        except:
            print("Error al borrar el gif")
        
    #ejecutamos el proceso en paralelo al gif de carga
    def tarea_zanjas_DC():
        """Coordina la tarea asíncrona para las zanjas DC."""
        proceso_simular_zanjas_DC()
        root.after(0, lambda: cerrar_ventana_tras_simular_zanjas_DC(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_zanjas_DC) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
boton_sim_zanjas_DC = tk.Button(frame_zanjas_DC, text="Simulate DC Trenches", command=simular_zanjas_DC, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_sim_zanjas_DC.grid(row=3, column=0, pady=20)





#----------Simular zanjas AS

def simular_trazado_zanjas_AS():
    
    """Simula trazado las zanjas as y actualiza los resultados."""
    def proceso_simular_zanjas_AS():
        """Ejecuta el proceso auxiliar encargado de simular las zanjas as."""
        global zanjas_AS_ID
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            zanjas_AS_ID = alg_zanjas.trazado_zanjas_AASS(bloque_inicial, n_bloques, pol_AASS_LVAC, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_ethernet, pol_cable_FO, max_p_AASS_LVAC, max_p_AASS_eth)
            
            guardar_variables([zanjas_AS_ID],['zanjas_AS_ID'])
        
        except:
            traceback.print_exc()
            
    def cerrar_ventana_tras_simular_zanjas_AS(ventana_carga):
        """Cierra la ventana de carga tras  simular las zanjas as."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            
            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
        except:
            print("Error al borrar el gif")

    def tarea_zanjas_AS():
        """Coordina la tarea asíncrona para las zanjas as."""
        proceso_simular_zanjas_AS()
        root.after(0, lambda: cerrar_ventana_tras_simular_zanjas_AS(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_zanjas_AS) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()    
    
boton_simular_zanjas_AS= tk.Button(frame_zanjas_DC, text="Route AS Trenches", command=simular_trazado_zanjas_AS, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
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
                prediseño_PB_zanjas_LV_ID, prediseño_zanjas_LV_ID, tipos_zanjas = alg_zanjas.trazado_zanjas_LV(bloque_inicial, n_bloques, max_b, max_c, max_p_array, cajas_fisicas, pol_array_cable, max_c_tz)
            else:
                prediseño_PB_zanjas_LV_ID, prediseño_zanjas_LV_ID, tipos_zanjas = alg_zanjas.trazado_zanjas_LV(bloque_inicial, n_bloques, max_b, max_inv, max_p_array, inv_como_cajas_fisicas, pol_array_cable, max_c_tz)

                
            if Metodo_ancho_zanjas_LV =='Manual':
                global config_circ_zanjas_LV, info_cada_zanja_LV
                #Obtener tabla con distribucion de circuitos y tipos de zanjas protegidas
                if DCBoxes_o_Inv_String == 'DC Boxes':
                    config_circ_zanjas_LV , info_cada_zanja_LV = alg_zanjas.combinaciones_circuitos_zanjas_LV(bloque_inicial, n_bloques, max_b, max_c, max_p_array, cajas_fisicas, pol_array_cable, tipos_zanjas, polilineas_caminos)
                else:
                    config_circ_zanjas_LV , info_cada_zanja_LV = alg_zanjas.combinaciones_circuitos_zanjas_LV(bloque_inicial, n_bloques, max_b, max_inv, max_p_array, inv_como_cajas_fisicas, pol_array_cable, tipos_zanjas, polilineas_caminos)

                guardar_variables([config_circ_zanjas_LV,info_cada_zanja_LV],['config_circ_zanjas_LV','info_cada_zanja_LV'])
                
            #Guardar variables en el dicionario
            guardar_variables([prediseño_PB_zanjas_LV_ID, prediseño_zanjas_LV_ID, tipos_zanjas, Metodo_ancho_zanjas_LV, max_c_tz],['prediseño_PB_zanjas_LV_ID', 'prediseño_zanjas_LV_ID', 'tipos_zanjas', 'Metodo_ancho_zanjas_LV', 'max_c_tz'])
            
        except:
            error_de_simulacion = 'Error trazado zanjas'
            traceback.print_exc()
            
    
    def cerrar_ventana_y_listar_nuevas_entradas(ventana_carga):
        """Cierra la ventana de carga tras y listar nuevas entradas."""
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


boton_sim_LV_trenches = tk.Button(frame_zanjas_LV_prediseño, text="Route LV Trenches", command=prediseño_zanjas_LV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_sim_LV_trenches.grid(row=1, column=3, pady=20)   


 

def simular_zanjas_LV_automatico():
       
    """Simula las zanjas LV automático y actualiza los resultados."""
    def proceso_simular_zanjas_LV_automatico():
        """Ejecuta el proceso auxiliar encargado de simular las zanjas LV automático."""
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
            
            PB_zanjas_LV_ID, zanjas_LV_ID, tipos_y_subtipos_unicos = alg_zanjas.calculo_anchos_zanjas_LV(DCBoxes_o_Inv_String, bloque_inicial, n_bloques, prediseño_PB_zanjas_LV_ID, tipos_zanjas, Metodo_ancho_zanjas_LV, entradas_diseño_automatico, 0)
            
            
            #Guardar variables en el dicionario
            guardar_variables([PB_zanjas_LV_ID, zanjas_LV_ID, tipos_y_subtipos_unicos, ancho_min_LV_trench_auto, int_circ_LV_trench_auto, mat_cond_LV_trench_auto, mat_ais_LV_trench_auto, cross_sect_LV_trench_auto, cab_diam_LV_trench_auto, met_inst_LV_trench_auto, temp_LV_trench_auto, res_ter_LV_trench_auto],['PB_zanjas_LV_ID', 'zanjas_LV_ID', 'tipos_y_subtipos_unicos', 'ancho_min_LV_trench_auto', 'int_circ_LV_trench_auto', 'mat_cond_LV_trench_auto', 'mat_ais_LV_trench_auto', 'cross_sect_LV_trench_auto', 'cab_diam_LV_trench_auto', 'met_inst_LV_trench_auto', 'temp_LV_trench_auto', 'res_ter_LV_trench_auto'])
        except:
            error_de_simulacion = 'Error calc automatico'
            traceback.print_exc()

    def cerrar_ventana_tras_lv_auto(ventana_carga):
        """Cierra la ventana de carga tras  LV auto."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            
            if error_de_simulacion == 'Error trazado zanjas':
                messagebox.showerror("Error", "There was an error calculating trenches, please check data.")
            elif error_de_simulacion == 'Error calc automatico':
                messagebox.showerror("Error", "There was an error while calculating trenches width, please check data.")
        except:
            print("Error al borrar el gif")

        
    def tarea_simular_zanjas_LV_auto():
        """Coordina la tarea asíncrona para simular las zanjas LV auto."""
        proceso_simular_zanjas_LV_automatico()
        root.after(0, lambda: cerrar_ventana_tras_lv_auto(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARI

    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_simular_zanjas_LV_auto) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()






def simular_zanjas_LV_manual():
    
    """Simula las zanjas LV manual y actualiza los resultados."""
    def proceso_simular_zanjas_LV_manual():
        """Ejecuta el proceso auxiliar encargado de simular las zanjas LV manual."""
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
            PB_zanjas_LV_ID, zanjas_LV_ID, [] = alg_zanjas.calculo_anchos_zanjas_LV(DCBoxes_o_Inv_String, bloque_inicial, n_bloques, prediseño_PB_zanjas_LV_ID, tipos_zanjas, Metodo_ancho_zanjas_LV, 0, entradas_diseño_manual)
            
            #Guardar variables en el dicionario
            guardar_variables([tipos_y_subtipos_unicos, anchos_tipos_LV, PB_zanjas_LV_ID, zanjas_LV_ID],['tipos_y_subtipos_unicos', 'anchos_tipos_LV', 'PB_zanjas_LV_ID', 'zanjas_LV_ID'])
        except:
            error_de_simulacion = 'Error calc automatico'
            traceback.print_exc()
            
        
    def cerrar_ventana_tras_lv_trench_manual(ventana_carga):
        """Cierra la ventana de carga tras  LV trench manual."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            
            if error_de_simulacion == 'Error trazado zanjas':
                messagebox.showerror("Error", "There was an error calculating trenches, please check data.")
            elif error_de_simulacion == 'Error calc automatico':
                messagebox.showerror("Error", "There was an error while calculating trenches width, please check data.")
        except:
            print("Error al borrar el gif")
        
    def tarea_simular_zanjas_LV_manual():
        """Coordina la tarea asíncrona para simular las zanjas LV manual."""
        proceso_simular_zanjas_LV_manual()
        root.after(0, lambda: cerrar_ventana_tras_lv_trench_manual(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    

    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_simular_zanjas_LV_manual) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()    
    
     
    
    
#-------Simular ZANJAS MV

#Definir metodo y sacar trazado listando entrandas necesarias segun el metodo - NO SE PONE PANTALLA DE CARGA PORQUE ES UN PROCESO RAPIDO

def prediseño_zanjas_MV():
    def simular_prediseño_zanjas_MV():
        global prediseño_zanjas_MV_ID, tipos_zanjas_MV, Metodo_ancho_zanjas_MV, max_c_tz_mv
        global error_de_simulacion

        error_de_simulacion = 'Sin error'
        
        try: 
            #Leer valores de entrada
            Metodo_ancho_zanjas_MV = entrada_met_diseño.get() #Puede ser 'Manual','IEC 60364' o 'AS/NZS 3008'
            max_c_tz_mv=int(entrada_max_c_tz_mv.get()) #maximo de circuitos en un mismo tipo de zanja
            
            #Sacar tipos basicos sin calcular anchos, los arrays de zanjas llevan [n_circuitos, 4 coordenadas]
            prediseño_zanjas_MV_ID, tipos_zanjas_MV = alg_zanjas.trazado_zanjas_MV(pol_cable_MV, max_c_tz_mv)

                
            if Metodo_ancho_zanjas_MV =='Manual':
                global config_circ_zanjas_MV, info_cada_zanja_MV
                #Obtener tabla con distribucion de circuitos y tipos de zanjas protegidas
                config_circ_zanjas_MV , info_cada_zanja_MV = alg_zanjas.combinaciones_circuitos_zanjas_MV(pol_cable_MV, lineas_MV, tipos_zanjas_MV, polilineas_caminos)
                
                guardar_variables([config_circ_zanjas_MV,info_cada_zanja_MV],['config_circ_zanjas_MV','info_cada_zanja_MV'])
                
            #Guardar variables en el dicionario
            guardar_variables([prediseño_zanjas_MV_ID, tipos_zanjas_MV, Metodo_ancho_zanjas_MV, max_c_tz_mv],['prediseño_zanjas_MV_ID', 'tipos_zanjas_MV', 'Metodo_ancho_zanjas_MV', 'max_c_tz_mv'])
            
        except:
            error_de_simulacion = 'Error trazado zanjas'
            traceback.print_exc()
            
    
    def cerrar_ventana_y_listar_nuevas_entradas(ventana_carga):
        """Cierra la ventana de carga tras y listar nuevas entradas."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            
            if error_de_simulacion == 'Error trazado zanjas':
                messagebox.showerror("Error", "There was an error creating MV trenches, please check data.")

            else: #si no ha habido fallo listamos las entradas necesarias correspondientes al metodo elegido
                if Metodo_ancho_zanjas_MV =='Manual':
                    entradas_zanjas_MV_manual(config_circ_zanjas_MV)
                else:
                    entradas_zanjas_MV_auto(valores_entradas_zanjas_MV_auto)
                    
        except:
            print("Error al borrar el gif")
            traceback.print_exc()
        
    def tarea_prediseño_zanjas_MV():
        simular_prediseño_zanjas_MV()
        root.after(0, lambda: cerrar_ventana_y_listar_nuevas_entradas(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_prediseño_zanjas_MV) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()


boton_sim_MV_trenches = tk.Button(frame_zanjas_MV_prediseño, text="Route MV Trenches", command=prediseño_zanjas_MV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_sim_MV_trenches.grid(row=1, column=3, pady=20)   


 

def simular_zanjas_MV_automatico():
       
    """Simula las zanjas MV automático y actualiza los resultados."""
    def proceso_simular_zanjas_MV_automatico():
        """Ejecuta el proceso auxiliar encargado de simular las zanjas MV automático."""
        global zanjas_MV_ID, tipos_y_subtipos_unicos, entradas_diseño_automatico
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            entradas_diseño_automatico = np.zeros(9, dtype=object)
            
            #Leer valores de entrada
            ancho_min_MV_trench_auto = float(valor_ancho_min.get())
            int_circ_MV_trench_auto = float(valor_int_circ.get())
            mat_cond_MV_trench_auto = entrada_material_cond.get() #puede ser 'Cobre' o 'Aluminio'
            mat_ais_MV_trench_auto = entrada_material_ais.get()  #puede ser 'XLPE o EPR (90ºC)' o 'PVC (70ºC)'
            cross_sect_MV_trench_auto = int(entrada_secciones_MV.get()) #sqmm #restringido a los valores de la tabla
            cab_diam_MV_trench_auto = float(valor_cab_diam.get())    #mm
            met_inst_MV_trench_auto = entrada_met_inst.get() #puede ser 'Directamente enterrado' o 'Enterrado bajo tubo'
            temp_MV_trench_auto = float(valor_temp.get())  #ºC
            res_ter_MV_trench_auto = float(valor_res_ter.get())  #W/m-K
            
            entradas_diseño_automatico = [ancho_min_MV_trench_auto, int_circ_MV_trench_auto, mat_cond_MV_trench_auto, mat_ais_MV_trench_auto, cross_sect_MV_trench_auto, cab_diam_MV_trench_auto, met_inst_MV_trench_auto, temp_MV_trench_auto, res_ter_MV_trench_auto]
            
            zanjas_MV_ID, tipos_y_subtipos_unicos_MV = alg_zanjas.calculo_anchos_zanjas_MV(DCBoxes_o_Inv_String, bloque_inicial, n_bloques, tipos_zanjas_MV, Metodo_ancho_zanjas_MV, entradas_diseño_automatico, 0)
            
            
            #Guardar variables en el dicionario
            guardar_variables([zanjas_MV_ID, tipos_y_subtipos_unicos_MV, ancho_min_MV_trench_auto, int_circ_MV_trench_auto, mat_cond_MV_trench_auto, mat_ais_MV_trench_auto, cross_sect_MV_trench_auto, cab_diam_MV_trench_auto, met_inst_MV_trench_auto, temp_MV_trench_auto, res_ter_MV_trench_auto],['zanjas_MV_ID', 'tipos_y_subtipos_unicos_MV', 'ancho_min_MV_trench_auto', 'int_circ_MV_trench_auto', 'mat_cond_MV_trench_auto', 'mat_ais_MV_trench_auto', 'cross_sect_MV_trench_auto', 'cab_diam_MV_trench_auto', 'met_inst_MV_trench_auto', 'temp_MV_trench_auto', 'res_ter_MV_trench_auto'])
        except:
            error_de_simulacion = 'Error calc automatico'
            traceback.print_exc()

    def cerrar_ventana_tras_MV_auto(ventana_carga):
        """Cierra la ventana de carga tras  MV auto."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            
            if error_de_simulacion == 'Error trazado zanjas':
                messagebox.showerror("Error", "There was an error calculating trenches, please check data.")
            elif error_de_simulacion == 'Error calc automatico':
                messagebox.showerror("Error", "There was an error while calculating trenches width, please check data.")
        except:
            print("Error al borrar el gif")

        
    def tarea_simular_zanjas_MV_auto():
        """Coordina la tarea asíncrona para simular las zanjas MV auto."""
        proceso_simular_zanjas_MV_automatico()
        root.after(0, lambda: cerrar_ventana_tras_MV_auto(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARI

    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_simular_zanjas_MV_auto) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()






def simular_zanjas_MV_manual():
    
    """Simula las zanjas MV manual y actualiza los resultados."""
    def proceso_simular_zanjas_MV_manual():
        """Ejecuta el proceso auxiliar encargado de simular las zanjas MV manual."""
        global zanjas_MV_ID
        global error_de_simulacion
        error_de_simulacion = 'Sin error'
        
        try:
            #Leemos los anchos tras pulsar el boton
            anchos_tipos_MV = [entrada.get() for entrada in entradas_anchos_tipos_MV]
            #Tras introducir anchos en los tipos y subtipos ahora toca traer los datos de vuelta con los identificadores sobre cada zanja, lo integramos en la funcion de calculo de anchos de zanja
            entradas_diseño_manual=[]
            entradas_diseño_manual.append(config_circ_zanjas_MV)
            entradas_diseño_manual.append(tipos_y_subtipos_unicos_MV)
            entradas_diseño_manual.append(anchos_tipos_MV)
            entradas_diseño_manual.append(info_cada_zanja_MV)

                                        #tipos_y_subtipos unicos se mete a mano, ya no es salida
            zanjas_MV_ID = alg_zanjas.calculo_anchos_zanjas_MV(tipos_zanjas_MV, Metodo_ancho_zanjas_MV, 0, entradas_diseño_manual)
            
            #Guardar variables en el dicionario
            guardar_variables([zanjas_MV_ID],['zanjas_MV_ID'])
        except:
            error_de_simulacion = 'Error calc automatico'
            traceback.print_exc()
            
        
    def cerrar_ventana_tras_MV_trench_manual(ventana_carga):
        """Cierra la ventana de carga tras  MV trench manual."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga
            
            if error_de_simulacion == 'Error trazado zanjas':
                messagebox.showerror("Error", "There was an error calculating trenches, please check data.")
            elif error_de_simulacion == 'Error calc automatico':
                messagebox.showerror("Error", "There was an error while calculating trenches width, please check data.")
            elif error_de_simulacion == 'Sin error':
                messagebox.showinfo("Success", "MV Trenches calculated successfully")
        except:
            print("Error al borrar el gif")
        
    def tarea_simular_zanjas_MV_manual():
        """Coordina la tarea asíncrona para simular las zanjas MV manual."""
        proceso_simular_zanjas_MV_manual()
        root.after(0, lambda: cerrar_ventana_tras_MV_trench_manual(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    

    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_simular_zanjas_MV_manual) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()    
    
    
    

#-----------Combinar zanjas

def combinar_zanjas():
    
    """Combina las zanjas para obtener un resultado global."""
    def proceso_combinar_zanjas():
        """Ejecuta el proceso auxiliar encargado de combinar las zanjas."""
        global zanjas_LV_ID, zanjas_AS_ID, zanjas_MV_ID
        global error_de_simulacion
        error_de_simulacion = 'Sin error'

        try:        
            zanjas_LV_ID, zanjas_AS_ID, zanjas_MV_ID = alg_zanjas.combinar_todas_las_zanjas(bloque_inicial, n_bloques, PB_zanjas_LV_ID, zanjas_LV_ID, zanjas_AS_ID, zanjas_MV_ID)
        
            guardar_variables([zanjas_LV_ID, zanjas_AS_ID, zanjas_MV_ID],['zanjas_LV_ID', 'zanjas_AS_ID', 'zanjas_MV_ID'])
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
            
    def cerrar_ventana_tras_combinar_zanjas(ventana_carga):
        """Cierra la ventana de carga tras  combinar las zanjas."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga
        except:
            print("Error al borrar el gif")
            
        if error_de_simulacion == 'Error':
            messagebox.showerror("Error", "There was an error while processing, please check data.")
        elif error_de_simulacion == 'Sin error':
            messagebox.showinfo("Success", "Trenches were successfully combined.")
            


    def tarea_combinar_zanjas():
        """Coordina la tarea asíncrona para combinar las zanjas."""
        proceso_combinar_zanjas()
        root.after(0, lambda: cerrar_ventana_tras_combinar_zanjas(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
    
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_combinar_zanjas) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()    
    
boton_combinar_zanjas= tk.Button(frame_combinar_zanjas, text="Combine trenches", command=combinar_zanjas, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'), anchor='center')
boton_combinar_zanjas.grid(row=0, column=0, pady=20)


    
    
    
        

TRENCHES_SECTION = TabSection(
    key="trenches",
    title="Trench design",
    icon="Pestaña 6.png",
    groups=FunctionalGroup(
        io={},
        processing={
            "simulate_dc_trenches": simular_zanjas_DC,
            "simulate_auxiliary_routes": simular_trazado_zanjas_AS,
            "preset_lv_trenches": prediseño_zanjas_LV,
            "simulate_lv_trenches_auto": simular_zanjas_LV_automatico,
            "simulate_lv_trenches_manual": simular_zanjas_LV_manual,
            "preset_mv_trenches": prediseño_zanjas_MV,
            "simulate_mv_trenches_auto": simular_zanjas_MV_automatico,
            "simulate_mv_trenches_manual": simular_zanjas_MV_manual,
            "combine_trenches": combinar_zanjas,
        },
        ui={
            "render_dc_trench_inputs": entradas_zanjas_DC,
            "render_lv_preset_inputs": entradas_prediseño_zanjas_LV,
            "render_lv_auto_inputs": entradas_zanjas_LV_auto,
            "render_lv_manual_inputs": entradas_zanjas_LV_manual,
            "render_lv_manual_widths": entradas_anchos_manuales_LV,
            "render_mv_preset_inputs": entradas_prediseño_zanjas_MV,
            "render_mv_auto_inputs": entradas_zanjas_MV_auto,
            "render_mv_manual_inputs": entradas_zanjas_MV_manual,
            "render_mv_manual_widths": entradas_anchos_manuales_MV,
        },
    ),
)