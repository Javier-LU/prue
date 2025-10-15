# ============================================================================
# Pestaña 8: Output data
#   - resumen_de_variables_totales(): consolida toda la información calculada.
#   - export_PV_Plant_results_to_excel(): genera el informe en formato Excel.
# ============================================================================

#LAYOUT DE FRAMES PARA INTRODUCIR DATOS
# Crear un frame para dar un margen respecto a los bordes
frame_salidas_container = tk.Frame(Output_NB, background=BLANCO_ROTO)
frame_salidas_container.pack(side='left', padx=30, pady=30, fill='both', expand=True)

frame_summary= tk.Frame(frame_salidas_container, background=BLANCO_ROTO)
frame_summary.pack(side='left', padx=30, pady=30, fill='both', expand=True)

frame_export= tk.Frame(frame_salidas_container, background=BLANCO_ROTO)
frame_export.pack(side='right', padx=30, pady=30, fill='both', expand=True)




def resumen_de_variables_totales():
    
    """Presenta un resumen general de las variables calculadas a lo largo de la aplicación."""
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
     
    ) = alg_pat.mediciones_por_bloque_y_totales_cables(String_o_Bus, DCBoxes_o_Inv_String, secciones_cs, secciones_dcb, secciones_array, bloque_inicial, n_bloques, med_cable_string_pos, med_cable_string_neg, med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_DC_Bus_pos, med_DC_Bus_neg, med_inst_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_inst_DC_Bus_neg, PB_zanjas_DC_ID, n_tubos_max_DC1, med_array_cable_pos, med_array_cable_neg,med_array_cable, med_inst_array_cable_pos, med_inst_array_cable_neg, med_inst_array_cable, lineas_MV, secciones_MV)
 
    #PROCESAR MEDICIONES DE ZANJAS
    PB_Zanja_DC1, PB_Zanja_DC2, TOT_Zanja_DC1, TOT_Zanja_DC2, PB_Zanjas_LV, TOT_Zanjas_LV, error_medicion_zanjas, TOT_Zanjas_AS = alg_pat.mediciones_por_bloque_y_totales_zanjas (bloque_inicial, n_bloques, PB_zanjas_DC_ID, n_tubos_max_DC1, PB_zanjas_LV_ID, tipos_y_subtipos_unicos, zanjas_AS_ID)
    
    #PROCESAR MEDICIONES DE CAJAS Y STRINGS
    if DCBoxes_o_Inv_String == 'DC Boxes':
        PB_n_strings, PB_n_DC_Boxes, PB_DC_Boxes, TOT_n_strings, TOT_n_DC_Boxes, TOT_DC_Boxes, error_medicion_cajas = alg_pat.mediciones_por_bloque_cajas_y_totales_strings(bloque_inicial, n_bloques, DCBoxes_ID)
    else:
        PB_n_strings, PB_n_String_Inverters, PB_String_Inverters, TOT_n_strings, TOT_n_String_Inverters, TOT_String_Inverters, error_medicion_cajas = alg_pat.mediciones_por_bloque_inv_string_y_totales_strings(bloque_inicial, n_bloques, String_Inverters_ID)
        
    #PROCESAR MEDICIONES DE PUESTA A TIERRA (el electrodo viene ya calculado de antes)
    PB_PAT_lat_entre_tr, PB_PAT_lat_prim_pica, PB_PAT_term_prim_pica, PB_PAT_term_DC_Box, TOT_PAT_lat_entre_tr, TOT_PAT_lat_prim_pica, TOT_PAT_term_prim_pica, TOT_PAT_term_DC_Box, TOT_PAT_Electrodo, error_medicion_PAT = alg_pat.mediciones_por_bloque_y_totales_PAT(bloque_inicial, n_bloques, PAT_latiguillo_entre_trackers,PAT_latiguillo_primera_pica,PAT_terminal_primera_pica,PAT_terminal_DC_Box, PAT_Electrodo, mayoracion_electrodo_PAT)

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
) = alg_pat.mediciones_por_bloque_y_totales_LV_material(bloque_inicial, n_bloques, n_mods_serie, Interconexionado, DCBoxes_o_Inv_String, String_o_Bus, strings_fisicos, filas_con_cable_string, harness_neg, sch_cable_de_string_neg, sch_DC_Bus_neg, sch_array_cable_neg, sch_array_cable, med_tubo_corrugado_zanja_DC, PB_n_strings, secciones_array)
    
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
                        if uni_o_multipolar == 1:
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
                        if uni_o_multipolar == 1:
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
            for i in range(TOT_Array_Terminal_Box.shape[1]):
                datos_resumen.append(["Array Cable Lugs", f"DC Box - {TOT_Array_Terminal_Box[0,i]} mm2", TOT_Array_Terminal_Box[1,i]])
                
            for i in range(TOT_Array_Terminal_PCS.shape[1]):           
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

boton_resumen_totales = tk.Button(frame_summary, text="Final Measurements and Summary", command=resumen_de_variables_totales, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_resumen_totales.grid(row=1, column=0, pady=20)   






#Exportacion de schedules y datos detallados a excel

def export_PV_Plant_results_to_excel():
    
    """Exporta los resultados del diseño fotovoltaico a un archivo de Excel."""
    def is_nan_array(arr):
        """Determina si un array contiene valores NaN."""
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
        
        intercalado = np.empty((n_total, 3), dtype=object)
        
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

    #___PICAS COMBOXES Y CAJAS O INV DE STRING
    if DCBoxes_o_Inv_String == 'DC Boxes': #LO LIMITAMOS DE MOMENTO PORQUE NO SE HA DESARROLLADO PARA INV DE STRING
        SCH_picas_cajas = alg_pat.schedule_picas_comboxes_cajas_inv_str(bloque_inicial, n_bloques, max_c_block, DCBoxes_ID, String_Inverters_ID, coord_Comboxes, DCBoxes_o_Inv_String, orientacion, largo_caja, equi_reverse_ibc)
        encabezados = ['ID', 'X coord.', 'Y coord.']
        df_SCH_picas_cajas = pd.DataFrame(SCH_picas_cajas, columns=encabezados)
        ruta_completa = carpeta_archivo + "Boxes Piles Schedule.xlsx"
        df_SCH_picas_cajas.to_excel(ruta_completa, index=False, header=True)

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



boton_informe_excel = tk.Button(frame_export, text="Export data", command=export_PV_Plant_results_to_excel, bg=ROJO_GRS, fg='white', font=('Montserrat', 10, 'bold'))
boton_informe_excel.grid(row=1, column=1, pady=20)   



OUTPUT_SECTION = TabSection(
    key="outputs",
    title="Outputs",
    icon="Pestaña 8.png",
    groups=FunctionalGroup(
        io={
            "export_pv_results": export_PV_Plant_results_to_excel,
        },
        processing={},
        ui={
            "summarise_variables": resumen_de_variables_totales,
        },
    ),
)