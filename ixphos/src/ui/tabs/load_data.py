# Pestaña 1: Load Data
#   - seleccionar_archivo_y_cargar_proyecto(): importa proyectos guardados.
#   - proceso_leer_layout(): interpreta la geometría procedente de AutoCAD.
#   - seleccionar_archivo_y_cargar_datos_iniciales_desde_EXCEL(): carga datos base desde Excel.
#   - Iniciar_proyecto_desde_AutoCAD(): prepara un proyecto nuevo a partir de un layout.
#   - mostrar_resumen_datos_partida(): resume los valores iniciales cargados en la interfaz.
# ============================================================================
#------------------ PRIMERA PESTAÑA - CARGA DE DATOS-------------------






#-----------------------------------------IMPORTAR PROYECTO--------------------------------------------    

#______FUNCIONES DE CARGA DE DATOS___________ 

def si_None_vacio(entrada): #si el valor que se carga es None se devuelve vacio para que quede mejor si se importa un proyecto parcial
    """Normaliza entradas None devolviendo listas vacías para facilitar la carga de datos."""
    if entrada==None:
        return []
    else:
        return entrada
            
#Funcion para importar proyecto en JSON
def seleccionar_archivo_y_cargar_proyecto():
    
    """Permite seleccionar un archivo guardado y cargar su información en el proyecto."""
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
        """Ejecuta el proceso auxiliar encargado de la carga."""
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
        reiniciar_inv           = dicc_var.get('reiniciar_inv',False)               #boolean
        
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
        dos_inv                = dicc_var.get('dos_inv',False)                     #boolean
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
        
        if uni_o_multipolar == 1:
            var_com_uni_o_multipolar='Single core'
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
        global cond_Cu_20, cond_Al_20, bifaciality, int_mod_STC, power_mod_STC, subarray_temp, array_temp, pot_inv, cos_phi, v_inv, X_cable, valores_importados_perdidas
        cond_Cu_20    = si_None_vacio(dicc_var.get('cond_Cu_20',[]))             #int
        cond_Al_20    = si_None_vacio(dicc_var.get('cond_Al_20',[]))             #int
        bifaciality   = si_None_vacio(dicc_var.get('bifaciality',[]))             #int
        int_mod_STC   = si_None_vacio(dicc_var.get('int_mod_STC',[]))             #float
        power_mod_STC = si_None_vacio(dicc_var.get('power_mod_STC',[]))           #int    
        subarray_temp = si_None_vacio(dicc_var.get('subarray_temp',[]))           #int    
        array_temp    = si_None_vacio(dicc_var.get('array_temp',[]))              #int    
        pot_inv       = si_None_vacio(dicc_var.get('pot_inv',[]))              #int    
        cos_phi       = si_None_vacio(dicc_var.get('cos_phi',[]))              #float 
        v_inv         = si_None_vacio(dicc_var.get('v_inv',[]))                 #int    
        X_cable       = si_None_vacio(dicc_var.get('X_cable',[]))              #float
        
        
        valores_importados_perdidas = [cond_Cu_20, cond_Al_20, bifaciality, int_mod_STC, power_mod_STC, subarray_temp, array_temp, pot_inv, cos_phi, v_inv, X_cable, material_array]
        
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
        
        Metodo_ancho_zanjas_MV      = si_None_vacio(dicc_var.get('Metodo_ancho_zanjas_MV', []))         #str
        max_c_tz_mv                 = si_None_vacio(dicc_var.get('max_c_tz_mv',[]))                     #int
        
            #Salidas
        global config_circ_zanjas_LV,info_cada_zanja_LV,tipos_y_subtipos_unicos, anchos_tipos_LV
        config_circ_zanjas_LV       = np.array(dicc_var.get('config_circ_zanjas_LV', []))          #array numpy
        info_cada_zanja_LV          = dicc_var.get('info_cada_zanja_LV',[])            #list
        tipos_y_subtipos_unicos     = dicc_var.get('tipos_y_subtipos_unicos',[])            #list
        anchos_tipos_LV             = dicc_var.get('anchos_tipos_LV',[])            #list
        
        global config_circ_zanjas_MV,info_cada_zanja_MV,tipos_y_subtipos_unicos_MV, anchos_tipos_MV
        config_circ_zanjas_MV       = np.array(dicc_var.get('config_circ_zanjas_MV', []))          #array numpy
        info_cada_zanja_MV          = dicc_var.get('info_cada_zanja_MV',[])            #list
        tipos_y_subtipos_unicos_MV     = dicc_var.get('tipos_y_subtipos_unicos_MV',[])            #list
        anchos_tipos_MV             = dicc_var.get('anchos_tipos_MV',[])            #list

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
        
        global entradas_diseño_automatico_MV, ancho_min_MV_trench_auto, int_circ_MV_trench_auto, mat_cond_MV_trench_auto, mat_ais_MV_trench_auto, cross_sect_MV_trench_auto, cab_diam_MV_trench_auto, met_inst_MV_trench_auto, temp_MV_trench_auto, res_ter_MV_trench_auto
        ancho_min_MV_trench_auto    = si_None_vacio(dicc_var.get('ancho_min_MV_trench_auto', []))       #float
        int_circ_MV_trench_auto     = si_None_vacio(dicc_var.get('int_circ_MV_trench_auto', []))        #float
        cross_sect_MV_trench_auto   = si_None_vacio(dicc_var.get('cross_sect_MV_trench_auto', []))      #int
        cab_diam_MV_trench_auto     = si_None_vacio(dicc_var.get('cab_diam_MV_trench_auto', []))        #float
        temp_MV_trench_auto         = si_None_vacio(dicc_var.get('temp_MV_trench_auto', []))            #float    
        res_ter_MV_trench_auto      = si_None_vacio(dicc_var.get('res_ter_MV_trench_auto', []))         #float
        mat_cond_MV_trench_auto     = si_None_vacio(dicc_var.get('mat_cond_MV_trench_auto', []))        #str
        mat_ais_MV_trench_auto      = si_None_vacio(dicc_var.get('mat_ais_MV_trench_auto', []))         #str
        met_inst_MV_trench_auto     = si_None_vacio(dicc_var.get('met_inst_MV_trench_auto', []))        #str
        
        #para funciones
        entradas_diseño_automatico_MV = [ancho_min_MV_trench_auto, int_circ_MV_trench_auto, mat_cond_MV_trench_auto, mat_ais_MV_trench_auto, cross_sect_MV_trench_auto, cab_diam_MV_trench_auto, met_inst_MV_trench_auto, temp_MV_trench_auto, res_ter_MV_trench_auto]

        #para GUI
        global valores_importados_zanjas_DC, valores_importados_prediseño_zanjas_LV, valores_entradas_zanjas_LV_auto, valores_importados_prediseño_zanjas_MV, valores_entradas_zanjas_MV_auto
        valores_importados_zanjas_DC = [n_tubos_max_DC1, ancho_DC1, ancho_DC2]
        
        valores_importados_prediseño_zanjas_LV = [Metodo_ancho_zanjas_LV, max_c_tz]
        valores_entradas_zanjas_LV_auto=[ancho_min_LV_trench_auto, int_circ_LV_trench_auto, cross_sect_LV_trench_auto, cab_diam_LV_trench_auto, temp_LV_trench_auto, res_ter_LV_trench_auto, mat_cond_LV_trench_auto, mat_ais_LV_trench_auto, met_inst_LV_trench_auto]
        
        valores_importados_prediseño_zanjas_MV = [Metodo_ancho_zanjas_MV, max_c_tz_mv]
        valores_entradas_zanjas_MV_auto=[ancho_min_MV_trench_auto, int_circ_MV_trench_auto, cross_sect_MV_trench_auto, cab_diam_MV_trench_auto, temp_MV_trench_auto, res_ter_MV_trench_auto, mat_cond_MV_trench_auto, mat_ais_MV_trench_auto, met_inst_MV_trench_auto]
        
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
        """Actualiza la interfaz GUI tras la carga."""
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
        entradas_prediseño_zanjas_MV(valores_importados_prediseño_zanjas_MV)
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
        """Coordina la tarea asíncrona número 1."""
        proceso_carga()
        root.after(0, lambda: actualizar_GUI_tras_carga(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
    hilo_secundario = threading.Thread(target = tarea_1) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    





#______EJECUCION DE CARGA DE DATOS___________ 



#Funcion de proceso para leer el layout, se saca al global porque se va a usar tanto para leer de primeras como para volver a leer despues
def proceso_leer_layout():
    """Procesa el archivo de layout importado desde AutoCAD."""
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
    """Recarga el layout procedente de AutoCAD sin reiniciar la aplicación."""
    def cerrar_ventana_tras_releer_layout(ventana_carga):
        """Cierra la ventana de carga tras  releer el layout."""
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
        """Coordina la tarea asíncrona para releer el layout."""
        proceso_leer_layout()
        root.after(0, lambda: cerrar_ventana_tras_releer_layout(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_releer_layout) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
        








#---------------------------------------------INICIAR NUEVO PROYECTO-----------------------------------------------
    
#-----------Iniciación con datos de partida desde Excel
def seleccionar_archivo_y_cargar_datos_iniciales_desde_EXCEL():
    """Importa los datos iniciales del proyecto desde un libro de Excel."""
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
    
    """Inicializa un nuevo proyecto partiendo de los datos extraídos de AutoCAD."""
    def cerrar_ventana_tras_leer_layout(ventana_carga):
        """Cierra la ventana de carga tras  leer el layout."""
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
                entradas_prediseño_zanjas_MV(valores_iniciales_prediseño_zanjas_MV)    
                
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
        """Coordina la tarea asíncrona para leer el layout."""
        proceso_leer_layout()
        root.after(0, lambda: cerrar_ventana_tras_leer_layout(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
   
    ventana_carga = crear_gif_espera()
    
    hilo_secundario = threading.Thread(target = tarea_leer_layout) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
    hilo_secundario.start()
    
    
    
        
        
        

#Funciones de iniciacion  
        

    #Empezamos borrando los widgets de la pantalla de inicio
def borrar_widgets_inicio():    
    """Elimina los widgets temporales mostrados en la pantalla inicial."""
    label_logo_IXPHOS.destroy()
    label_texto_IXPHOS.destroy()
    label_texto_subt_GRS.destroy()
    boton_nuevo_proyecto_Excel.destroy()
    boton_nuevo_proyecto_CAD.destroy()
    boton_importar_proyecto.destroy()

def mostrar_resumen_datos_partida():
    """Despliega un resumen de los datos de partida cargados en la pestaña inicial."""
    #Empezamos borrando los widgets que pueda haber (si se relee el layout hay que borrar y crear de nuevo)
    for widget in frame_resumen_partida.winfo_children():
        widget.destroy()
        
    #Introducimos en el frame de la izquierda el resumen de datos
    tk.Label(frame_resumen_partida, text="Initial Block Number", bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))       .grid(row=0, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{bloque_inicial}', bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))          .grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(frame_resumen_partida, text="Last Block Number", bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))          .grid(row=1, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{n_bloques}', bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))               .grid(row=1, column=1, padx=10, pady=5)
    
    tk.Label(frame_resumen_partida, text="Total no. trackers", bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))         .grid(row=2, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{len(trackers_extraidos)}', bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold')) .grid(row=2, column=1, padx=10, pady=5)
    
    tk.Label(frame_resumen_partida, text="Max. no. trackers per block", bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold')).grid(row=3, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{max_tpb}', bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))                 .grid(row=3, column=1, padx=10, pady=5)
    
    if coord_PCS_DC_inputs.size > 0:
        n_PCS = np.sum(~np.isnan(coord_PCS_DC_inputs).any(axis=1))
    else:
        n_PCS=0
    tk.Label(frame_resumen_partida, text="No. PCSs", bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))                   .grid(row=4, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{n_PCS}', bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))                   .grid(row=4, column=1, padx=10, pady=5)

    if coord_Comboxes.size > 0:
        n_Comboxes = np.sum(~np.isnan(coord_Comboxes).any(axis=1))
    else:
        n_Comboxes=0
    n_Comboxes = np.sum(~np.isnan(coord_Comboxes).any(axis=1))
    tk.Label(frame_resumen_partida, text="No. Comboxes", bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))               .grid(row=5, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{n_Comboxes}', bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))              .grid(row=5, column=1, padx=10, pady=5)
    
    if coord_Tracknets.size > 0:
        n_Tracknets = np.sum(~np.isnan(coord_Tracknets).any(axis=1))
    else:
        n_Tracknets=0
    n_Tracknets = np.sum(~np.isnan(coord_Tracknets).any(axis=1))
    tk.Label(frame_resumen_partida, text="No. Tracknets", bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))              .grid(row=6, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{n_Tracknets}', bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))             .grid(row=6, column=1, padx=10, pady=5)
    
    if coord_TBoxes.size > 0:
        n_TBoxes = np.sum(~np.isnan(coord_TBoxes).any(axis=1))
    else:
        n_TBoxes=0    
    n_TBoxes = np.sum(~np.isnan(coord_TBoxes).any(axis=1))
    tk.Label(frame_resumen_partida, text="No. T-Boxes", bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))                .grid(row=7, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{n_TBoxes}', bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))                .grid(row=7, column=1, padx=10, pady=5)
    
    if coord_AWS.size > 0:
        n_AWS = np.sum(~np.isnan(coord_AWS).any(axis=1))
    else:
        n_AWS=0 
    n_AWS = np.sum(~np.isnan(coord_AWS).any(axis=1))
    tk.Label(frame_resumen_partida, text="No. AWS", bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))                    .grid(row=8, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{n_AWS}', bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))                   .grid(row=8, column=1, padx=10, pady=5)
    
    tk.Label(frame_resumen_partida, text="No. CCTV", bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))                   .grid(row=9, column=0, padx=10, pady=5)
    tk.Label(frame_resumen_partida, text=f'{len(coord_CCTV)}', bg=BLANCO_ROTO, font=('Montserrat', 9, 'bold'))         .grid(row=9, column=1, padx=10, pady=5)
    
    

def crear_tabla_trackers():
    """Construye la tabla con el inventario de trackers por bloque."""
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
    """Genera las casillas de entrada para importar datos procedentes de Excel."""
    etiq_trackers = ["XL", "L", "M", "S"]
    entradas = {}
    
    # Crear la fila inicial con los nombres de las columnas
    tk.Label(frame_aux_longitudes, text="Tracker type", bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold')).grid(row=0, column=0, padx=10, pady=5)
    tk.Label(frame_aux_longitudes, text="Length (m)", bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold')).grid(row=0, column=1, padx=10, pady=5)

    # Crear las filas con las etiquetas y entradas
    for i, etiq_tracker in enumerate(etiq_trackers):
        tk.Label(frame_aux_longitudes, text=etiq_tracker, fg=ROJO_GRS, bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold')).grid(row=i+1, column=0, padx=10, pady=5)
        
        valor = tk.StringVar()
        valor.set(valor_inicial[i])

        entrada = tk.Entry(frame_aux_longitudes, textvariable=valor, width=10)
        entrada.grid(row=i+1, column=1, padx=10, pady=5)
        entradas[etiq_tracker] = entrada
    
    def leer_long_trackers():
        """Lee las longitudes de los trackers introducidas en la interfaz."""
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
            """Procesa en segundo plano la lectura de las longitudes de los trackers."""
            global trackers_pb
            trackers_pb_sin_ordenar = alg_planta_fv.preparar_datos_trackers(trackers_extraidos, n_bloques, max_tpb, long_XL, long_L, long_M, long_S)
            trackers_pb = alg_planta_fv.ordenar_x_y(trackers_pb_sin_ordenar, bloque_inicial,n_bloques)
            
            #Guardamos los valores de las variables en el diccionario
            guardar_variables([long_S,long_M,long_L,long_XL,trackers_pb],['long_S','long_M','long_L','long_XL','trackers_pb'])
            
        def actualizar_GUI_tras_leer_long_trackers(ventana_carga):
            """Actualiza la interfaz gráfica tras leer las longitudes de los trackers."""
            try:
                ventana_carga.destroy() #se cierra el gif de carga
                
            except:
                print("Error al borrar el gif")

            insertar_tabla_trackers_por_bloque_con_longitudes()
            
            
        #ejecutamos el proceso en paralelo al gif de carga
        def tarea_leer_long_trackers():
            """Coordina la tarea asíncrona de lectura de longitudes de trackers."""
            proceso_leer_long_trackers()
            root.after(0, lambda: actualizar_GUI_tras_leer_long_trackers(ventana_carga)) #ACTUALIZAR GUI UNA VEZ SE HAN CARGADO LOS DATOS FUERA DEL HILO SECUNDARIO
        
        ventana_carga = crear_gif_espera()
        
        hilo_secundario = threading.Thread(target = tarea_leer_long_trackers) #creamos un hilo de ejecucion paralelo a la interfaz grafica principal para que se actualice la ventana de carga y no se quede bloqueada mientras se ejecuta el proceso principal (en el hilo secundario, al reves da problemas en tkinter)
        hilo_secundario.start()
        

    boton_leer = tk.Button(frame_aux_longitudes, text="Read values", command=leer_long_trackers, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
    boton_leer.grid(row=len(etiq_trackers) + 1, column=0, columnspan=2, pady=10)
    
    boton_volver_a_leer_layout = tk.Button(frame_aux_longitudes, text="Reload layout", command=volver_a_leer_layout_desde_CAD, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
    boton_volver_a_leer_layout.grid(row=len(etiq_trackers) + 2, column=0, columnspan=2, pady=80)
    

    
            
def insertar_tabla_trackers_por_bloque_con_longitudes():
    """Inserta la tabla de trackers agrupados por bloque junto con sus longitudes."""
    # Eliminar el árbol inicial
    for widget in frame_tabla_trackers.winfo_children():
        widget.destroy()
    
    # Función para actualizar la tabla basada en el valor de la spinbox
    def update_table():
        """Actualiza la tabla con la información del bloque seleccionado."""
        # Limpiar el contenido existente de la tabla
        for row in tree.get_children():
            tree.delete(row)
        
        # Obtener el índice seleccionado de la spinbox
        index = int(spinbox.get())
        
        # Rellenar la tabla con los datos del índice seleccionado del array
        for row in trackers_pb[index]:
            tree.insert('', 'end', values=list(row))
            
    # Crear etiqueta para el texto "Nº de bloque"
    label_bloque = tk.Label(frame_tabla_trackers, text="Block number", bg=BLANCO_ROTO, font=('Montserrat', 10, 'bold'), justify='center')
    label_bloque.grid(row=0, column=0, padx=5, pady=5, sticky='e')
    
    # Crear spinbox para seleccionar el índice de la primera dimensión
    spinbox = tk.Spinbox(frame_tabla_trackers, from_=bloque_inicial, to=trackers_pb.shape[0]-1, command=update_table, width=2, font=('Montserrat', 10))
    spinbox.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    # Crear Treeview para mostrar los datos del array
    estilo_tabla_trackers = ttk.Style()
    estilo_tabla_trackers.configure("Treeview", borderwidth=2, relief="solid", font=('Montserrat', 10))
    estilo_tabla_trackers.configure("Treeview.Heading", font=('Montserrat', 10, 'bold'), borderwidth=2, background=ROJO_GRS)
    
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
    
    

LOAD_DATA_SECTION = TabSection(
    key="load_data",
    title="Load data",
    icon="Pestaña 1.png",
    groups=FunctionalGroup(
        io={
            "save_project": guardar_proyecto,
            "import_project": seleccionar_archivo_y_cargar_proyecto,
            "import_initial_data": seleccionar_archivo_y_cargar_datos_iniciales_desde_EXCEL,
            "bootstrap_from_autocad": Iniciar_proyecto_desde_AutoCAD,
        },
        processing={
            "read_layout": proceso_leer_layout,
            "reload_layout": volver_a_leer_layout_desde_CAD,
        },
        ui={
            "reset_welcome": borrar_widgets_inicio,
            "show_initial_summary": mostrar_resumen_datos_partida,
            "build_tracker_table": crear_tabla_trackers,
            "build_tracker_inputs": crear_casillas_EXCEL,
            "render_trackers_by_block": insertar_tabla_trackers_por_bloque_con_longitudes,
        },
    ),
)


    
    
    
    
    
#---------------------EJECUCION INICIAL PRIMERA PESTAÑA------------------------------
            
# Creamos un frame para meter en el tres frames y darles un margen comun respecto a los bordes
frame_inicio_container = tk.Frame(Carga_Excel, background=BLANCO_ROTO)
frame_inicio_container.pack(side='left', padx=50, pady=50, fill='both', expand=True)

#Lo dividimos en tres subframes para meter las funcionalidades despues
frame_inicio_container.grid_columnconfigure(0, weight=1)
frame_inicio_container.grid_columnconfigure(1, weight=3)
frame_inicio_container.grid_columnconfigure(2, weight=1)


#Creamos un frame para los datos importados de partida
frame_resumen_partida = tk.Frame(frame_inicio_container, background=BLANCO_ROTO)
frame_resumen_partida.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

# Creamos un frame para meter en el la tabla de datos y la scrollbar
frame_tabla_trackers = tk.Frame(frame_inicio_container, background=BLANCO_ROTO)
frame_tabla_trackers.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

# Creamos un nuevo frame para organizar más facilmente la insercion de las longitudes de trackers
frame_aux_longitudes = tk.Frame(frame_inicio_container, background=BLANCO_ROTO)
frame_aux_longitudes.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')


    # Cargar y colocar el logo y el nombre en ese frame, luego se elimina al cargar el archivo
logo_IXPHOS = cargar_imagen("Logo_IXPHOS.png", (256, 256))


label_logo_IXPHOS = tk.Label(frame_inicio_container, image=logo_IXPHOS, background=BLANCO_ROTO)
label_logo_IXPHOS.place(relx=0.5, y=0, anchor='n')
label_texto_IXPHOS = tk.Label(frame_inicio_container, text='I X P H O S', bg=BLANCO_ROTO, fg=ROJO_GRS, font=('Palatino Linotype', 40, 'bold', "underline"))
label_texto_IXPHOS.place(relx=0.5, y=320, anchor='n')
label_texto_subt_GRS = tk.Label(frame_inicio_container, text='PV Plant Design Software by Gransolar', bg=BLANCO_ROTO, fg=ROJO_GRS, font=('Palatino Linotype', 10, 'bold', 'italic'))
label_texto_subt_GRS.place(relx=0.55, y=395, anchor='n')

boton_nuevo_proyecto_Excel = tk.Button(frame_inicio_container, text="Start new project from Excel", command=seleccionar_archivo_y_cargar_datos_iniciales_desde_EXCEL, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_nuevo_proyecto_Excel.place(relx=0.22, y=550)

boton_nuevo_proyecto_CAD = tk.Button(frame_inicio_container, text="Start new project from AutoCAD", command=Iniciar_proyecto_desde_AutoCAD, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_nuevo_proyecto_CAD.place(relx=0.47, y=550)

boton_importar_proyecto = tk.Button(frame_inicio_container, text="Import existing project", command=seleccionar_archivo_y_cargar_proyecto, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_importar_proyecto.place(relx=0.72, y=550)