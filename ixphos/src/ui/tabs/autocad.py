# ============================================================================
# Pestaña 9: AutoCAD Export
#   - dibujar_flechas_textos_strings(): añade anotaciones de interconexión.
#   - dibujar_harness(): representa los harness y conectores en el plano CAD.
#   - dibujar_zanjas_MV()/dibujar_zanjas_LV(): proyectan las zanjas calculadas.
#   - dibujar_PAT(): exporta el sistema de puesta a tierra al modelo CAD.
# ============================================================================



#LAYOUT DE FRAMES PARA INTRODUCIR DATOS
# Crear un frame para dar un margen respecto a los bordes
frame_ACAD_container = tk.Frame(AutoCAD_NB, background=BLANCO_ROTO)
frame_ACAD_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)




#-----DIBUJAR INTERCONEXIONADO

def dibujar_flechas_textos_strings():
    """Dibuja las flechas y textos de strings con los datos actuales."""
    def proceso_dibujo_interconexion():
        """Gestiona el dibujo de la interconexión de strings en AutoCAD."""
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
        """Cierra la ventana de carga tras  simular dibujo la interconexión."""
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
        """Coordina la tarea asíncrona para la interconexión."""
        proceso_dibujo_interconexion()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_inter(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_interconexion) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_CAD_inter = tk.Button(frame_ACAD_container, text="Draw Interconnection", command=dibujar_flechas_textos_strings, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_inter.grid(row=1, column=0, pady=20)

entrada_all_blocks_inter = tk.BooleanVar(value=False)
all_blocks_inter = True
single_block_inter=1

def update_single_block_inter():
    """Actualiza el bloque seleccionado asociado a la interconexión."""
    global single_block_inter
    single_block_inter = int(spinbox_inter.get())

def activate_spinbox_inter():
    """Gestiona el estado del selector de bloque para la interconexión."""
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
    """Dibuja el harness con los datos actuales."""
    def proceso_dibujo_harness():
        """Ejecuta el proceso auxiliar encargado de dibujo el harness."""
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
        """Cierra la ventana de carga tras  simular dibujo el harness."""
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
        """Coordina la tarea asíncrona para el harness."""
        proceso_dibujo_harness()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_harness(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_harness) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar harness    
boton_CAD_inter = tk.Button(frame_ACAD_container, text="Draw harnesses", command=dibujar_harness, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_inter.grid(row=2, column=0, pady=20)

#Checkbutton para dibujar ambos polos (recomendable si la interconexion es ida y vuelta)
entrada_dos_polos = tk.BooleanVar(value=False)
dos_polos = entrada_all_blocks_inter.get()

check_inter = ttk.Checkbutton(frame_ACAD_container, text="Both poles", variable=dos_polos)
check_inter.grid(row=2, column=1, padx=5, pady=5, sticky='w')



#---------DIBUJAR ZANJAS MV

def dibujar_zanjas_MV():
    """Dibuja las zanjas MV con los datos actuales."""
    def proceso_dibujo_zanjas_MV():
        """Ejecuta el proceso auxiliar encargado de dibujo las zanjas MV."""
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
            AutoCAD_extension.CAD_draw_zanjas_MV(acad, zanjas_MV_ID)
            
            pythoncom.CoUninitialize() #Cerramos en el hilo secundario para ahorrar recursos
                                       
        except comtypes.COMError as e:
            if e.hresult == -2147417846:
                error_de_dibujo = 'Interaccion con AutoCAD'
            else:
                error_de_dibujo = 'Otro error'
        except Exception:
            error_de_dibujo = 'Otro error'
            traceback.print_exc()
            
  
    def cerrar_ventana_tras_simular_dibujo_zanjas_MV(ventana_carga):
        """Cierra la ventana de carga tras  simular dibujo las zanjas MV."""
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
    def tarea_zanjas_MV():
        """Coordina la tarea asíncrona para las zanjas MV."""
        proceso_dibujo_zanjas_MV()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_zanjas_MV(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_zanjas_MV) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_CAD_zanjas_MV = tk.Button(frame_ACAD_container, text="Draw MV Trenches", command=dibujar_zanjas_MV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_zanjas_MV.grid(row=3, column=0, pady=20)




#---------DIBUJAR ZANJAS DC

def dibujar_zanjas_DC():
    """Dibuja las zanjas DC con los datos actuales."""
    def proceso_dibujo_zanjas_DC():
        """Ejecuta el proceso auxiliar encargado de dibujo las zanjas DC."""
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
        """Cierra la ventana de carga tras  dibujo zdc."""
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
    def tarea_dibujar_zdc():
        """Coordina la tarea asíncrona para dibujar zdc."""
        proceso_dibujo_zanjas_DC()
        root.after(0, lambda: cerrar_ventana_tras_dibujo_zdc(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_dibujar_zdc) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_zdc_CAD_draw = tk.Button(frame_ACAD_container, text="Draw DC Trenches", command=dibujar_zanjas_DC, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_zdc_CAD_draw.grid(row=4, column=0, pady=20)

entrada_all_blocks_zdc = tk.BooleanVar(value=False)
all_blocks_zdc = True
single_block_zdc=1

def update_single_block_zdc():
    """Actualiza el bloque seleccionado asociado a zdc."""
    global single_block_zdc
    single_block_zdc = int(spinbox_zdc.get())

def activate_spinbox_zdc():
    """Gestiona el estado del selector de bloque para zdc."""
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
spinbox_zdc.grid(row=4, column=1, padx=5, pady=5, sticky='w')

check_zdc = ttk.Checkbutton(frame_ACAD_container, text="Single block", variable=entrada_all_blocks_zdc, command=activate_spinbox_zdc)
check_zdc.grid(row=4, column=2, padx=5, pady=5, sticky='w')



#---------DIBUJAR ZANJAS LV

def dibujar_zanjas_LV():
    """Dibuja las zanjas LV con los datos actuales."""
    def proceso_dibujo_zanjas_LV():
        """Ejecuta el proceso auxiliar encargado de dibujo las zanjas LV."""
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
        """Cierra la ventana de carga tras  dibujo zlv."""
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
    def tarea_dibujar_zlv():
        """Coordina la tarea asíncrona para dibujar zlv."""
        proceso_dibujo_zanjas_LV()
        root.after(0, lambda: cerrar_ventana_tras_dibujo_zlv(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_dibujar_zlv) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

#Boton para dibujar todos los bloques    
boton_zlv_CAD_draw = tk.Button(frame_ACAD_container, text="Draw LV Trenches", command=dibujar_zanjas_LV, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_zlv_CAD_draw.grid(row=5, column=0, pady=20)

entrada_all_blocks_zlv = tk.BooleanVar(value=False)
all_blocks_zlv = True
single_block_zlv=1

def update_single_block_zlv():
    """Actualiza el bloque seleccionado asociado a zlv."""
    global single_block_zlv
    single_block_zlv = int(spinbox_zlv.get())

def activate_spinbox_zlv():
    """Gestiona el estado del selector de bloque para zlv."""
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
spinbox_zlv.grid(row=5, column=1, padx=5, pady=5, sticky='w')

check_zlv = ttk.Checkbutton(frame_ACAD_container, text="Single block", variable=entrada_all_blocks_zlv, command=activate_spinbox_zlv)
check_zlv.grid(row=5, column=2, padx=5, pady=5, sticky='w')





#---------DIBUJAR ZANJAS AS

def dibujar_zanjas_AS():
    """Dibuja las zanjas as con los datos actuales."""
    def proceso_dibujo_zanjas_AS():
        """Ejecuta el proceso auxiliar encargado de dibujo las zanjas as."""
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
        """Cierra la ventana de carga tras  simular dibujo las zanjas as."""
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
    def tarea_zanjas_AS():
        """Coordina la tarea asíncrona para las zanjas as."""
        proceso_dibujo_zanjas_AS()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_zanjas_AS(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_zanjas_AS) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_CAD_zanjas_AS = tk.Button(frame_ACAD_container, text="Draw AS Trenches", command=dibujar_zanjas_AS, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_zanjas_AS.grid(row=6, column=0, pady=20)



#------------DIBUJAR TODA LA PAT
def dibujar_PAT():
    """Dibuja pat con los datos actuales."""
    def proceso_dibujo_PAT():
        """Ejecuta el proceso auxiliar encargado de dibujo pat."""
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
        """Cierra la ventana de carga tras  simular dibujo pat."""
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
    def tarea_PAT():
        """Coordina la tarea asíncrona para pat."""
        proceso_dibujo_PAT()
        root.after(0, lambda: cerrar_ventana_tras_simular_dibujo_PAT(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_PAT) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()

    
#Boton para dibujar todos los bloques    
boton_CAD_PAT = tk.Button(frame_ACAD_container, text="Draw Earthing", command=dibujar_PAT, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_CAD_PAT.grid(row=7, column=0, pady=20)

entrada_all_blocks_PAT = tk.BooleanVar(value=False)
all_blocks_PAT = True
single_block_PAT=1

def update_single_block_PAT():
    """Actualiza el bloque seleccionado asociado a pat."""
    global single_block_PAT
    single_block_PAT = int(spinbox_PAT.get())

def activate_spinbox_PAT():
    """Gestiona el estado del selector de bloque para pat."""
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
spinbox_PAT.grid(row=7, column=1, padx=5, pady=5, sticky='w')

check_PAT = ttk.Checkbutton(frame_ACAD_container, text="Single block", variable=entrada_all_blocks_PAT, command=activate_spinbox_PAT)
check_PAT.grid(row=7, column=2, padx=5, pady=5, sticky='w')



AUTOCAD_SECTION = TabSection(
    key="autocad",
    title="AutoCAD",
    icon="Pestaña 9.png",
    groups=FunctionalGroup(
        io={
            "draw_string_annotations": dibujar_flechas_textos_strings,
            "draw_harness": dibujar_harness,
            "draw_mv_trenches": dibujar_zanjas_MV,
            "draw_dc_trenches": dibujar_zanjas_DC,
            "draw_lv_trenches": dibujar_zanjas_LV,
            "draw_auxiliary_trenches": dibujar_zanjas_AS,
            "draw_pat_export": dibujar_PAT,
        },
        processing={},
        ui={
            "update_single_block_inter": update_single_block_inter,
            "activate_spinbox_inter": activate_spinbox_inter,
            "update_single_block_zdc": update_single_block_zdc,
            "activate_spinbox_zdc": activate_spinbox_zdc,
            "update_single_block_zlv": update_single_block_zlv,
            "activate_spinbox_zlv": activate_spinbox_zlv,
            "update_single_block_pat": update_single_block_PAT,
            "activate_spinbox_pat": activate_spinbox_PAT,
        },
    ),
)