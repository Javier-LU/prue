# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 11:16:08 2025

@author: mlopez
"""

dicc_var_None = {
    "coord_PCS_DC_Inputs": None,
    "coord_PCS_AASS_inputs": None,
    "coord_PCS_MV_inputs": None,
    "coord_Comboxes": None,
    "coord_Tracknets": None,
    "coord_TBoxes": None,
    "coord_AWS": None,
    "coord_CCTV": None,     
    
    "coord_SS_LVAC": None,
    "coord_OyM_LVAC": None, 
    "coord_Warehouse_LVAC": None,
    "coord_MV_Switching_Room": None,
    "coord_SS_Control_Room": None,
    "coord_OyM_Control_Room": None,
    
    "polilineas_caminos": None,
    "pol_guia_MV_FO": None,
    "pol_envolventes_PAT": None,
    
    "long_XL": None,
    "long_L": None,
    "long_M": None,
    "long_S": None,
    
    "trackers_pb": None,
    "bloque_inicial": None,
    "n_bloques": None,
    "max_tpb": None,
    "PCSs": None,
    
    "pasillo_entre_bandas": None,
    "dist_min_b_separadas": None,
    "long_string": None,
    "pitch": None,
    "sep": None,
    "h_modulo": None,
    "ancho_modulo": None,
    "salto_motor": None,
    "saliente_TT": None,
    "dist_primera_pica_extremo_tr": None,
    "max_tpf": None,
    "ancho_caja": None,
    "largo_caja": None,
    "sep_caja_tracker": None,
    "sep_zanja_tracker": None,
    
    "config_tracker": None,
    "pos_salto_motor_M": None,
    "pos_salto_motor_L": None,
    
    "filas": None,
    "max_fpb": None,
    "bandas": None,
    "max_b": None,
    "max_fr": None,
    "orientacion": None,
    "filas_en_bandas": None,
    "max_f_str_b": None,
    "contorno_bandas": None,
    "contorno_bandas_sup": None,
    "contorno_bandas_inf": None,
    "bandas_anexas": None,
    "bandas_separadas": None,
    "bandas_aisladas": None,
    "bandas_intermedias_o_extremo": None,
    "strings_fisicos": None,
    "ori_str_ID": None,
    "max_spf": None,
    "dist_ext_opuesto_str": None,
    
    #Simulacion MV
    "potencia_bloques": None,
    "lineas_MV": None,
    "pol_cable_MV": None,
    
    #Simulacion configuracion LV
    "Interconexionado": None,
    "Polo_cercano": None,
    "DCBoxes_o_Inv_String": None,
    "Posicion_optima_caja": None,
    "String_o_Bus": None,
    "lim_str_dif": None,
    "n_inv": None,
    "dos_inv_por_bloque": None,
    "filas_en_cajas": None,
    "max_c": None,
    "max_c_block": None,
    "cajas_fisicas": None,
    "masc": None,
    "misc": None,
    "strings_ID": None,
    "DCBoxes_ID": None,
    "equi_ibfs": None,
    "equi_ibc": None,
    "equi_reverse_ibc": None,
    "equi_reverse_ibfs": None,
    "max_bus": None,
    "dos_inv": None,
    "extender_DC_Bus": None,
    
    "tipos_cajas_por_entradas": None,
    "TOT_n_cajas_str": None,
    "TOT_n_cajas_bus": None,
    "TOT_n_cajas_mix": None,
    "TOT_n_cajas": None,
    
        #inv string
        #Entradas
    "dist_max_inter_bandas":None,
    "lim_str_interc":None,
    "reiniciar_inv":None,
        #Intermedias
    "combinacion_optima":None,
    "ganancias_perdidas_optima":None,
    "matriz_intercambios_optima":None,
    "puentes_fisicos":None,
    "almacen_strings":None,
    "equi_ibv_to_fs":None,
    "equi_ibv":None,
    "equi_reverse_ibv":None,
        #Salidas
    "inv_string":None,
    "max_inv":None,
    "max_inv_block":None,
    "max_str_pinv":None,
    "posiciones_inv":None,
    "String_Inverters_ID":None,
    "filas_en_inversores":None,
    "inv_como_cajas_fisicas":None,
    "filas_en_inv_como_filas_en_cajas":None,
    "comienzos_filas_strings":None,
    
    
    #Dibujo configuracion LV y cajas
    "capas_de_envolventes": None,
    "handle_DC_Boxes":None,
    "handle_inv_string":None,
    
    
    #Simulacion cable string o DC Bus
    "max_p": None,
    "pol_cable_string": None,
    "pol_DC_Bus": None,
    "pol_tubo_corrugado_zanja_DC": None,
    "max_tubos_DC_bloque": None,
    "filas_con_cable_string": None,
    "filas_con_dcb_extendido": None,
    "Harness_pos_ID": None,
    "Harness_neg_ID": None,
    "tipos_harness_pos": None,
    "med_tipos_h_pos": None,
    "tipos_harness_neg": None,
    "med_tipos_h_pos": None,
    "med_tipos_h_neg": None,
    "harness_pos": None,
    "harness_neg": None,
    "coord_harness_pos": None,
    "coord_harness_neg": None,
    
    #Dibujo cable string o DC Bus
    "handle_cable_string": None,
    "handle_dcbus": None,
    
    #Simulacion cable array
    "pol_array_cable": None,
    "max_p_array": None,
    "n_circuitos_max_lado_PCS": None,
    "n_circuitos_max_entre_trackers": None,
    "salida_zanja_LV_caja_inv": None,
    
    #Dibujo cable array
    "handle_cable_array": None,
    
    
    #Simulacion servicios auxiliares y tubos
    "pol_AASS_LVAC": None,               
    "pol_ethernet": None,                
    "max_p_AASS_LVAC": None,             
    "max_p_AASS_eth": None,              
    "pol_CCTV_LVAC": None,               
    "pol_OyM_supply_LVAC": None,         
    "pol_Warehouse_supply_LVAC": None,
    
    "lineas_FO": None,
    "pol_cable_FO": None,
    
    #Medicion cable MV
    "asignacion_secciones_MV": None,
    "secciones_MV": None,
    "slack_cable_MV": None,
    "desnivel_cable_MV": None,
    "transicion_MV_PCS": None,
    "transicion_MV_SS": None,
    "safety_maj_MV": None,
    
    #Medicion cable subarray
        #ENTRADAS
    "desnivel_cable_por_pendientes_tramo_aereo": None,
    "desnivel_cable_por_pendientes_tramo_subt": None, 
    "transicion_cable_subarray_tracker": None,
    "transicion_cable_subarray_caja": None,
    "slack_cable_subarray": None,
    "mayoracion_cable_subarray": None,
    "coca_DC_Bus": None,
    "extension_primer_tracker": None,
        
    "seccion_str_SL_Distance_1": None,
    "seccion_str_SL_Distance_2": None,
    "seccion_str_location_1": None,
    "seccion_str_location_2": None,
    "seccion_str_1": None,
    "seccion_str_2": None,
    "seccion_str_3": None,
    "criterio_seccion_cs": None,
    
    "seccion_dcb_SL_Distance_1": None,
    "seccion_dcb_SL_Distance_2": None,
    "seccion_dcb_location_1": None,
    "seccion_dcb_location_2": None,
    "seccion_dcb_1": None,
    "seccion_dcb_2": None,
    "seccion_dcb_3": None,
    "criterio_seccion_dcb": None,
        
    "lim_dist_sld_cs_seccion": None,
    "lim_loc_cs_seccion": None,
    "secciones_cs": None,
    "lim_dist_sld_dcb_seccion": None,
    "lim_loc_dcb_seccion": None,
    "secciones_dcb": None,
        
        #SALIDAS DE SIMULACION
    "med_inst_cable_string_pos": None,
    "med_inst_cable_string_neg": None,
    "med_cable_string_pos": None,
    "tramo_aereo_cable_string_pos": None,
    "med_cable_string_neg": None,
    "sch_cable_de_string_pos": None,
    "sch_cable_de_string_neg": None,
    
    "med_inst_DC_Bus_pos": None,
    "med_inst_DC_Bus_neg": None,
    "med_DC_Bus_pos": None,
    "tramo_aereo_DC_Bus_pos": None,
    "med_DC_Bus_neg": None,
    "sch_DC_Bus_pos": None,
    "sch_DC_Bus_neg": None,

    "med_tubo_corrugado_zanja_DC": None,

    #Medicion cable array
        #ENTRADAS
    "desnivel_cable_array_por_pendientes": None,     
    "transicion_array_cable_caja": None,       
    "transicion_array_cable_PCS": None,       
    "slack_array_cable": None,                  
    "mayoracion_array_cable": None,         
    
    "uni_o_multipolar": None,                  
    "criterio_seccion_array": None,            
    "lim_dist_array_sld_seccion": None,          
    "lim_n_str_array_seccion": None,            
    "seccion_array_1": None,                 
    "seccion_array_2": None,                  
        
        #SALIDAS
    "med_inst_array_cable_pos": None,
    "med_inst_array_cable_neg": None,
    "med_array_cable_pos": None,
    "med_array_cable_neg": None,
    "med_array_cable": None,
    "med_inst_array_cable": None,
    "sch_array_cable_pos": None,
    "sch_array_cable_neg": None,
    "sch_array_cable": None,
    
    #Calculos
    "bifaciality":None,
    "int_mod_STC":None,
    "power_mod_STC":None,
    "n_mods_serie":None,   
    "subarray_temp":None,
    "array_temp":None,
    "pot_inv":None,
    "cos_phi":None,
    "v_inv":None,
    "X_cable":None,
    "material_array":None,
    
    #Simulacion zanjas DC
    "n_tubos_max_DC1":None,
    "ancho_DC1":None,
    "ancho_DC2":None,
    "zanjas_DC_ID": None,
    "PB_zanjas_DC_ID": None,
    
    #Simulacion zanjas LV
        #ENTRADAS
    "Metodo_ancho_zanjas_LV": None,
    "max_c_tz": None,
    
    "capa_caminos": None,
    
    "ancho_min_LV_trench_auto": None,
    "int_circ_LV_trench_auto": None,
    "mat_cond_LV_trench_auto": None,
    "mat_ais_LV_trench_auto": None,
    "cross_sect_LV_trench_auto": None,
    "cab_diam_LV_trench_auto": None,
    "met_inst_LV_trench_auto": None,
    "temp_LV_trench_auto": None,
    "res_ter_LV_trench_auto": None,
    
    
        #SALIDAS
    "config_circ_zanjas_LV": None,
    "info_cada_zanja_LV": None,
    "tipos_y_subtipos_unicos": None,
    "anchos_tipos_LV": None,
        
    "zanjas_LV_ID": None,
    "PB_zanjas_LV_ID": None,
    "tipos_zanjas": None,
    
    #Puesta a tierra
        #ENTRADAS
    "seccion_PAT_principal": None,
    "seccion_PAT_anillos": None,
    "retranqueo_anillos_PAT": None,
    "mayoracion_electrodo_PAT":None,
    
        #SALIDAS
    "PAT_latiguillo_entre_trackers": None,
    "PAT_latiguillo_primera_pica": None,
    "PAT_terminal_primera_pica": None,
    "PAT_terminal_DC_Box": None,
    "PAT_Electrodo": None,

    #Pestaña de resultados
        #ENTRADAS
    "n_mods_serie": None
}
