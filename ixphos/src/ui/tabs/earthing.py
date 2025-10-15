# ============================================================================
# Pestaña 7: Earthing
#   - entradas_anillo_PAT(): define las entradas del sistema de puesta a tierra.
#   - simular_PAT(): calcula los electrodos y mediciones de la malla PAT.
#   - dibujar_electrodos_PAT(): envía los elementos de puesta a tierra a AutoCAD.
# ============================================================================

#---------------------------SEPTIMA PESTAÑA PUESTA A TIERRA------------------------
#LAYOUT DE FRAMES PARA INTRODUCIR DATOS
# Crear un frame para dar un margen respecto a los bordes
frame_PAT_container = tk.Frame(Earthing_NB, background=BLANCO_ROTO)
frame_PAT_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)

frame_PAT_entradas = tk.Frame(frame_PAT_container, background=BLANCO_ROTO)
frame_PAT_entradas.pack(side='left', padx=30, pady=30, fill='both', expand=True)

frame_PAT_simulacion= tk.Frame(frame_PAT_container, background=BLANCO_ROTO)
frame_PAT_simulacion.pack(side='right', padx=30, pady=30, fill='both', expand=True)


#-------Entradas anillos PAT
def entradas_anillo_PAT(valores_dados_electrodo_PAT):
    """Construye los campos de entrada para el anillo pat."""
    global entrada_seccion_electrodo_principal, entrada_seccion_electrodo_anillos, valor_retranqueo_anillo_PAT, valor_mayoracion_electrodo

        #Seccion electrodo principal
    opciones_seccion_electrodo_principal = ['16', '35', '50', '70', '95']
    entrada_seccion_electrodo_principal = tk.StringVar(value = valores_dados_electrodo_PAT[0])
    
    etiqueta_seccion_electrodo_principal = tk.Label(frame_PAT_entradas, text='Main earthing electrode cross section', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_seccion_electrodo_principal.grid(row=0, column=0)
    combobox_seccion_electrodo_principal=ttk.Combobox(frame_PAT_entradas, textvariable=entrada_seccion_electrodo_principal, values=opciones_seccion_electrodo_principal)
    combobox_seccion_electrodo_principal.grid(row=0, column=1)
    
        #Seccion electrodo anillos envolventes
    opciones_seccion_electrodo_anillos = ['16', '35', '50', '70', '95']
    entrada_seccion_electrodo_anillos = tk.StringVar(value = valores_dados_electrodo_PAT[1])
    
    etiqueta_seccion_electrodo_anillos = tk.Label(frame_PAT_entradas, text='Enclosures earthing ring cross section', fg=ROJO_GRS, font=('Montserrat', 10,'bold'))
    etiqueta_seccion_electrodo_anillos.grid(row=1, column=0)
    combobox_seccion_electrodo_anillos=ttk.Combobox(frame_PAT_entradas, textvariable=entrada_seccion_electrodo_anillos, values=opciones_seccion_electrodo_anillos)
    combobox_seccion_electrodo_anillos.grid(row=1, column=1)

        #Retranqueo
    etiqueta_retranqueo_anillo_PAT = tk.Label(frame_PAT_entradas, text="Earthing ring setback", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_retranqueo_anillo_PAT.grid(row=2, column=0, padx=(10,0),pady=(15,10))
    valor_retranqueo_anillo_PAT = tk.StringVar()
    valor_retranqueo_anillo_PAT.set(valores_dados_electrodo_PAT[2])
    entrada_retranqueo_anillo_PAT = tk.Entry(frame_PAT_entradas, textvariable=valor_retranqueo_anillo_PAT, width=5)
    entrada_retranqueo_anillo_PAT.grid(row=2, column=1, padx=(5,20), pady=(15,10))

        #Mayoracion
    etiqueta_mayoracion_electrodo = tk.Label(frame_PAT_entradas, text="Electrode majoration", fg=ROJO_GRS, bg=GRIS_SUAVE, font=('Montserrat', 10, 'bold'))
    etiqueta_mayoracion_electrodo.grid(row=3, column=0, padx=(10,0),pady=(15,10))
    valor_mayoracion_electrodo = tk.StringVar()
    valor_mayoracion_electrodo.set(valores_dados_electrodo_PAT[3])
    entrada_mayoracion_electrodo = tk.Entry(frame_PAT_entradas, textvariable=valor_mayoracion_electrodo, width=5)
    entrada_mayoracion_electrodo.grid(row=3, column=1, padx=(5,20), pady=(15,10))

valores_iniciales_electrodo_PAT=[[],[],[],[]]
entradas_anillo_PAT(valores_iniciales_electrodo_PAT)


#-------Simular PAT

def simular_PAT():
        
    """Simula pat y actualiza los resultados."""
    def proceso_simular_PAT():
        """Ejecuta el proceso auxiliar encargado de simular pat."""
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
                PAT_latiguillo_entre_trackers, PAT_latiguillo_primera_pica, PAT_terminal_primera_pica, PAT_terminal_DC_Box, PAT_Electrodo = alg_pat.simulacion_principal_elementos_PAT(bloque_inicial, n_bloques, max_b, max_c, max_f_str_b, max_tpf, cajas_fisicas, strings_fisicos, filas_en_bandas, h_modulo, sep, orientacion, dist_primera_pica_extremo_tr, zanjas_DC_ID, zanjas_LV_ID, zanjas_AS_ID, seccion_PAT_principal)
            else:
                PAT_latiguillo_entre_trackers, PAT_latiguillo_primera_pica, PAT_terminal_primera_pica, PAT_terminal_DC_Box, PAT_Electrodo = alg_pat.simulacion_principal_elementos_PAT(bloque_inicial, n_bloques, max_b, max_inv, max_f_str_b, max_tpf, inv_como_cajas_fisicas, strings_fisicos, filas_en_bandas, h_modulo, sep, orientacion, dist_primera_pica_extremo_tr, zanjas_DC_ID, zanjas_LV_ID, zanjas_AS_ID, seccion_PAT_principal)
            
            PAT_Electrodo = alg_pat.anillos_PAT(PAT_Electrodo, seccion_PAT_anillos, pol_envolventes_PAT, retranqueo_anillos_PAT)
            
            #Guardar variables en el dicionario
            guardar_variables([seccion_PAT_principal,seccion_PAT_anillos,retranqueo_anillos_PAT,mayoracion_electrodo_PAT],['seccion_PAT_principal','seccion_PAT_anillos','retranqueo_anillos_PAT','mayoracion_electrodo_PAT'])
            guardar_variables([PAT_latiguillo_entre_trackers, PAT_latiguillo_primera_pica, PAT_terminal_primera_pica, PAT_terminal_DC_Box, PAT_Electrodo],['PAT_latiguillo_entre_trackers', 'PAT_latiguillo_primera_pica', 'PAT_terminal_primera_pica', 'PAT_terminal_DC_Box', 'PAT_Electrodo'])
        
        except:
            error_de_simulacion = 'Error'
            traceback.print_exc()
            
    def tarea_simular_PAT():
        """Coordina la tarea asíncrona para simular pat."""
        proceso_simular_PAT()
        root.after(0, lambda: cerrar_ventana_tras_simular_PAT(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
            
    def cerrar_ventana_tras_simular_PAT(ventana_carga):
        """Cierra la ventana de carga tras  simular pat."""
        try:
            ventana_carga.destroy() #se cierra el gif de carga

            if error_de_simulacion == 'Error':
                messagebox.showerror("Error", "There was an error while processing, please check data.")
                
        except:
            print("Error al borrar el gif")
        

    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_simular_PAT) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
    


boton_simular_PAT = tk.Button(frame_PAT_simulacion, text="Measure Earthing", command=simular_PAT, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_simular_PAT.grid(row=0, column=0, pady=20)   




#--------Dibujar electrodos de PAT------
def dibujar_electrodos_PAT():
    """Dibuja los electrodos pat con los datos actuales."""
    def proceso_dibujo_electrodos_PAT():
        """Ejecuta el proceso auxiliar encargado de dibujo los electrodos pat."""
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
        """Cierra la ventana de carga tras  simular dibujo los electrodos pat."""
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
        """Coordina la tarea asíncrona para los electrodos pat."""
        proceso_dibujo_electrodos_PAT()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_electrodos_PAT(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_electrodos_PAT) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_dibujar_electrodos_PAT = tk.Button(frame_PAT_simulacion, text="Draw Earthing Electrode", command=dibujar_electrodos_PAT, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_dibujar_electrodos_PAT.grid(row=6, column=0, pady=20)




#-------------Leer electrodo de PAT--------------






EARTHING_SECTION = TabSection(
    key="earthing",
    title="Earthing",
    icon="Pestaña 7.png",
    groups=FunctionalGroup(
        io={
            "draw_pat": dibujar_electrodos_PAT,
        },
        processing={
            "simulate_pat": simular_PAT,
        },
        ui={
            "render_pat_inputs": entradas_anillo_PAT,
        },
    ),
)