# -*- coding: utf-8 -*-
"""
Created on Wed May 14 19:57:25 2025

@author: mlopez
"""


import numpy as np
import traceback
from shapely.geometry import Polygon, LinearRing



def simulacion_principal_elementos_PAT(bloque_inicial, n_bloques, max_b, max_c, max_f_str_b, max_tpf, cajas_fisicas, strings_fisicos, filas_en_bandas, h_modulo, sep, orientacion, dist_primera_pica_extremo_tr, zanjas_DC_ID, zanjas_LV_ID, zanjas_AS_ID, seccion):
    PAT_latiguillo_entre_trackers=np.full((n_bloques+1,max_b,max_f_str_b,max_tpf,2),np.nan) #POSIBLE OPTIMIZAR, asumimos que no va a haber ningun cable de string con más de 50 puntos (polilinea con mas de 50 puntos), lo ideal quizás sería hacerlo con listas
    PAT_latiguillo_primera_pica=np.full((n_bloques+1,max_b,max_f_str_b,2),np.nan)
    PAT_terminal_primera_pica=np.full((n_bloques+1,max_b,max_f_str_b,2),np.nan)
    PAT_terminal_DC_Box=np.full((n_bloques+1, max_b+1, max_c, 2),np.nan)   
    
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(strings_fisicos[i,b,0,0,0]): #si la banda no está vacía         
                for f in range (0,max_f_str_b):  
                    if ~np.isnan(strings_fisicos[i,b,f,0,0]): #si la fila no está vacía
                        #sacamos los puntos de salto entre trackers y la primera pica, usando como base los codigos ya empleados en DCBus
                        tf=-1
                        for pos in np.array(filas_en_bandas[i,b,f].T[1]):
                            if ~np.isnan(pos):
                                tf=tf+1
                            else: 
                                break
                        
                        if tf>0:
                            for salto in range(0,tf):
                                PAT_latiguillo_entre_trackers[i,b,f,salto,0]=filas_en_bandas[i,b,f,0,2]+h_modulo/2
                                PAT_latiguillo_entre_trackers[i,b,f,salto,1]=filas_en_bandas[i,b,f,salto,3]-sep-0.3
                                    
                        if orientacion[i,b]=='S':                    
                            PAT_latiguillo_primera_pica[i,b,f,0]=filas_en_bandas[i,b,f,tf,2]+h_modulo*3/4 #lo desfasamos para que no choque con el simbolo de la estructura
                            PAT_latiguillo_primera_pica[i,b,f,1]=filas_en_bandas[i,b,f,tf,3]
                            
                            PAT_terminal_primera_pica[i,b,f,0]=filas_en_bandas[i,b,f,tf,2]+h_modulo/2
                            PAT_terminal_primera_pica[i,b,f,1]=filas_en_bandas[i,b,f,tf,3]+dist_primera_pica_extremo_tr
                            
                                    
                        elif orientacion[i,b]=='N': #el punto de insercion está al sur del tracker, siendo el primer tracker el mas al N                
                            PAT_latiguillo_primera_pica[i,b,f,0]=filas_en_bandas[i,b,f,0,2]+h_modulo*3/4
                            PAT_latiguillo_primera_pica[i,b,f,1]=filas_en_bandas[i,b,f,0,3]+filas_en_bandas[i,b,f,0,1]-dist_primera_pica_extremo_tr
                            
                            PAT_terminal_primera_pica[i,b,f,0]=filas_en_bandas[i,b,f,0,2]+h_modulo/2
                            PAT_terminal_primera_pica[i,b,f,1]=filas_en_bandas[i,b,f,0,3]+filas_en_bandas[i,b,f,0,1]-dist_primera_pica_extremo_tr
    
                            
    
    PAT_terminal_DC_Box[...,0]=cajas_fisicas[...,1]
    PAT_terminal_DC_Box[...,1]=cajas_fisicas[...,2]
    
                
    PAT_Electrodo = []
    try:
        for zanja in zanjas_DC_ID:
            PAT_Electrodo.append([seccion,zanja[2],zanja[3],zanja[4],zanja[5]])
    except:
        pass
    
    try:
        for zanja in zanjas_LV_ID:
            PAT_Electrodo.append([seccion,zanja[7][0],zanja[7][1],zanja[7][2],zanja[7][3]])  
    except:
        pass    
    
    
    try:
        for zanja in zanjas_AS_ID:
            PAT_Electrodo.append([seccion,zanja[3],zanja[4],zanja[5],zanja[6]])      
    except:
        pass  
                   
                    
    return PAT_latiguillo_entre_trackers, PAT_latiguillo_primera_pica, PAT_terminal_primera_pica, PAT_terminal_DC_Box, PAT_Electrodo
                

def anillos_PAT(PAT_Electrodo, seccion, pol_envolventes_PAT, retranqueo):
    pol_anillos_PS_PAT=[]
    for i in range(len(pol_envolventes_PAT)):
        # Crear polígono con Shapely a partir de tuplas planas
        puntos = list(zip(pol_envolventes_PAT[i][::2], pol_envolventes_PAT[i][1::2]))
        ring = LinearRing(puntos)
        polygon = Polygon(ring)

        # Aplicar offset hacia fuera
        offset_dist = float(retranqueo)
        polygon_offset = polygon.buffer(offset_dist, join_style=2) #el jointstyle dos es con esquinas rectas, el 1 lo redondea y el 3 lo achaflana

        # Reemplazamos con lista de coordenadas [(x, y), ...]
        pol_anillos_PS_PAT.append(list(polygon_offset.exterior.coords))

    # Añadir segmentos como [seccion, x0, y0, x1, y1]
    for anillo in pol_anillos_PS_PAT:
        for j in range(len(anillo) - 1):
            x0, y0 = anillo[j]
            x1, y1 = anillo[j + 1]
            PAT_Electrodo.append([seccion, x0, y0, x1, y1])

    return PAT_Electrodo

                






def mediciones_por_bloque_y_totales_cables(String_o_Bus, DCBoxes_o_Inv_String, secciones_cs, secciones_dcb, secciones_array, bloque_inicial, n_bloques, med_cable_string_pos, med_cable_string_neg, med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_DC_Bus_pos, med_DC_Bus_neg, med_inst_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_inst_DC_Bus_neg, PB_zanjas_DC_ID, n_tubos_max_DC1, med_array_cable_pos, med_array_cable_neg,med_array_cable, med_inst_array_cable_pos, med_inst_array_cable_neg, med_inst_array_cable, lineas_MV, secciones_MV):   
    
    #Inicializamos en None todas porque las vamos a devolver aunque no sean aplicables para usar en cualquier casuistica la misma funcion
    PB_med_cable_de_string_pos = None
    PB_med_cable_de_string_neg = None
    PB_inst_cable_de_string_pos = None
    PB_inst_cable_de_string_neg = None
    
    PB_med_DC_Bus_pos = None
    PB_med_DC_Bus_neg = None
    PB_inst_DC_Bus_pos = None
    PB_inst_DC_Bus_neg = None

    PB_inst_cable_de_array_pos = None
    PB_inst_cable_de_array_neg = None
    PB_med_cable_de_array_pos = None
    PB_med_cable_de_array_neg = None
    PB_inst_cable_de_array_AC = None
    PB_med_cable_de_array_AC = None

    TOT_inst_cable_MV = None  
    TOT_med_cable_MV = None  

    TOT_med_cable_de_string_pos = None
    TOT_med_cable_de_string_neg = None
    TOT_med_cable_de_string = None
    TOT_inst_cable_de_string_pos = None
    TOT_inst_cable_de_string_neg = None
    cable_string_en_tubo = None
    TOT_inst_cable_de_string = None
    
    TOT_med_DC_Bus_pos = None
    TOT_med_DC_Bus_neg = None
    TOT_med_DC_Bus = None
    TOT_inst_DC_Bus_pos = None
    TOT_inst_DC_Bus_neg = None
    DC_Bus_en_tubo = None
    TOT_inst_DC_Bus = None
    
    TOT_inst_cable_de_array_pos = None
    TOT_inst_cable_de_array_neg = None
    TOT_inst_cable_de_array = None
    TOT_med_cable_de_array_pos = None
    TOT_med_cable_de_array_neg = None
    TOT_med_cable_de_array = None
    TOT_inst_cable_de_array_AC = None
    TOT_med_cable_de_array_AC = None
    
    try:   
        #Mediciones por bloque
        if String_o_Bus == 'String Cable':
            PB_med_cable_de_string_pos=[[secciones_cs[0]],[secciones_cs[1]],[secciones_cs[2]]]
            PB_med_cable_de_string_neg=[[secciones_cs[0]],[secciones_cs[1]],[secciones_cs[2]]]
            PB_inst_cable_de_string_pos=[[secciones_cs[0]],[secciones_cs[1]],[secciones_cs[2]]]
            PB_inst_cable_de_string_neg=[[secciones_cs[0]],[secciones_cs[1]],[secciones_cs[2]]]
            
        elif String_o_Bus == 'DC Bus':
            PB_med_DC_Bus_pos=[[secciones_dcb[0]],[secciones_dcb[1]],[secciones_dcb[2]]]
            PB_med_DC_Bus_neg=[[secciones_dcb[0]],[secciones_dcb[1]],[secciones_dcb[2]]]
            PB_inst_DC_Bus_pos=[[secciones_dcb[0]],[secciones_dcb[1]],[secciones_dcb[2]]]
            PB_inst_DC_Bus_neg=[[secciones_dcb[0]],[secciones_dcb[1]],[secciones_dcb[2]]]
    
        else:
            PB_med_cable_de_string_pos=[[secciones_cs[0]],[secciones_cs[1]],[secciones_cs[2]]]
            PB_med_cable_de_string_neg=[[secciones_cs[0]],[secciones_cs[1]],[secciones_cs[2]]]
            PB_inst_cable_de_string_pos=[[secciones_cs[0]],[secciones_cs[1]],[secciones_cs[2]]]
            PB_inst_cable_de_string_neg=[[secciones_cs[0]],[secciones_cs[1]],[secciones_cs[2]]]
            PB_med_DC_Bus_pos=[[secciones_dcb[0]],[secciones_dcb[1]],[secciones_dcb[2]]]
            PB_med_DC_Bus_neg=[[secciones_dcb[0]],[secciones_dcb[1]],[secciones_dcb[2]]]
            PB_inst_DC_Bus_pos=[[secciones_dcb[0]],[secciones_dcb[1]],[secciones_dcb[2]]]
            PB_inst_DC_Bus_neg=[[secciones_dcb[0]],[secciones_dcb[1]],[secciones_dcb[2]]]
            
        
        if DCBoxes_o_Inv_String == 'DC Boxes':
            PB_inst_cable_de_array_pos=[[secciones_array[0]],[secciones_array[1]]]
            PB_inst_cable_de_array_neg=[[secciones_array[0]],[secciones_array[1]]]
            PB_med_cable_de_array_pos=[[secciones_array[0]],[secciones_array[1]]]
            PB_med_cable_de_array_neg=[[secciones_array[0]],[secciones_array[1]]]
        elif DCBoxes_o_Inv_String == 'String Inverters':
            PB_inst_cable_de_array_AC=[[secciones_array[0]],[secciones_array[1]]]
            PB_med_cable_de_array_AC=[[secciones_array[0]],[secciones_array[1]]]
        
        
        for i in range(bloque_inicial,n_bloques+1):
            for secc in range(0,3):               
                if String_o_Bus == 'String Cable':
                    PB_med_cable_de_string_pos[secc].append(int(np.nansum(med_cable_string_pos[i,...,0][med_cable_string_pos[i,...,1]==secciones_cs[secc]])))
                    PB_med_cable_de_string_neg[secc].append(int(np.nansum(med_cable_string_neg[i,...,0][med_cable_string_neg[i,...,1]==secciones_cs[secc]])))
                    PB_inst_cable_de_string_pos[secc].append(int(np.nansum(med_inst_cable_string_pos[i,...,0][med_inst_cable_string_pos[i,...,1]==secciones_cs[secc]])))
                    PB_inst_cable_de_string_neg[secc].append(int(np.nansum(med_inst_cable_string_neg[i,...,0][med_inst_cable_string_neg[i,...,1]==secciones_cs[secc]])))
                    
                elif String_o_Bus == 'DC Bus':
                    PB_med_DC_Bus_pos[secc].append(int(np.nansum(med_DC_Bus_pos[i,...,0][med_DC_Bus_pos[i,...,1]==secciones_dcb[secc]])))
                    PB_med_DC_Bus_neg[secc].append(int(np.nansum(med_DC_Bus_neg[i,...,0][med_DC_Bus_neg[i,...,1]==secciones_dcb[secc]])))
                    PB_inst_DC_Bus_pos[secc].append(int(np.nansum(med_inst_DC_Bus_pos[i,...,0][med_inst_DC_Bus_pos[i,...,1]==secciones_dcb[secc]])))
                    PB_inst_DC_Bus_neg[secc].append(int(np.nansum(med_inst_DC_Bus_neg[i,...,0][med_inst_DC_Bus_neg[i,...,1]==secciones_dcb[secc]])))   
                                    
                else:
                    PB_med_cable_de_string_pos[secc].append(int(np.nansum(med_cable_string_pos[i,...,0][med_cable_string_pos[i,...,1]==secciones_cs[secc]])))
                    PB_med_cable_de_string_neg[secc].append(int(np.nansum(med_cable_string_neg[i,...,0][med_cable_string_neg[i,...,1]==secciones_cs[secc]])))
                    PB_inst_cable_de_string_pos[secc].append(int(np.nansum(med_inst_cable_string_pos[i,...,0][med_inst_cable_string_pos[i,...,1]==secciones_cs[secc]])))
                    PB_inst_cable_de_string_neg[secc].append(int(np.nansum(med_inst_cable_string_neg[i,...,0][med_inst_cable_string_neg[i,...,1]==secciones_cs[secc]])))
                    
                    PB_med_DC_Bus_pos[secc].append(int(np.nansum(med_DC_Bus_pos[i,...,0][med_DC_Bus_pos[i,...,1]==secciones_dcb[secc]])))
                    PB_med_DC_Bus_neg[secc].append(int(np.nansum(med_DC_Bus_neg[i,...,0][med_DC_Bus_neg[i,...,1]==secciones_dcb[secc]])))
                    PB_inst_DC_Bus_pos[secc].append(int(np.nansum(med_inst_DC_Bus_pos[i,...,0][med_inst_DC_Bus_pos[i,...,1]==secciones_dcb[secc]])))
                    PB_inst_DC_Bus_neg[secc].append(int(np.nansum(med_inst_DC_Bus_neg[i,...,0][med_inst_DC_Bus_neg[i,...,1]==secciones_dcb[secc]])))     
            
            for secc in range(0,2):     
                if DCBoxes_o_Inv_String == 'DC Boxes':
                    PB_inst_cable_de_array_pos[secc].append(int(np.nansum(med_inst_array_cable_pos[i,...,0][med_inst_array_cable_pos[i,...,1]==secciones_array[secc]])))
                    PB_inst_cable_de_array_neg[secc].append(int(np.nansum(med_inst_array_cable_neg[i,...,0][med_inst_array_cable_neg[i,...,1]==secciones_array[secc]])))
                    PB_med_cable_de_array_pos[secc].append(int(np.nansum(med_array_cable_pos[i,...,0][med_inst_array_cable_pos[i,...,1]==secciones_array[secc]])))
                    PB_med_cable_de_array_neg[secc].append(int(np.nansum(med_array_cable_neg[i,...,0][med_inst_array_cable_neg[i,...,1]==secciones_array[secc]])))
                elif DCBoxes_o_Inv_String == 'String Inverters':
                    PB_inst_cable_de_array_AC[secc].append(int(np.nansum(med_inst_array_cable[i,...,0][med_inst_array_cable[i,...,1]==secciones_array[secc]])))
                    PB_med_cable_de_array_AC[secc].append(int(np.nansum(med_array_cable[i,...,0][med_inst_array_cable[i,...,1]==secciones_array[secc]])))
                    
        
        if String_o_Bus == 'String Cable':
             PB_med_cable_de_string_pos = np.array(PB_med_cable_de_string_pos).T
             PB_med_cable_de_string_neg = np.array(PB_med_cable_de_string_neg).T
             PB_inst_cable_de_string_pos = np.array(PB_inst_cable_de_string_pos).T
             PB_inst_cable_de_string_neg = np.array(PB_inst_cable_de_string_neg).T
        elif String_o_Bus == 'DC Bus':
             PB_med_DC_Bus_pos = np.array(PB_med_DC_Bus_pos).T
             PB_med_DC_Bus_neg = np.array(PB_med_DC_Bus_neg).T
             PB_inst_DC_Bus_pos = np.array(PB_inst_DC_Bus_pos).T
             PB_inst_DC_Bus_neg = np.array(PB_inst_DC_Bus_neg).T
        else:
             PB_med_cable_de_string_pos = np.array(PB_med_cable_de_string_pos).T
             PB_med_cable_de_string_neg = np.array(PB_med_cable_de_string_neg).T
             PB_inst_cable_de_string_pos = np.array(PB_inst_cable_de_string_pos).T
             PB_inst_cable_de_string_neg = np.array(PB_inst_cable_de_string_neg).T
             PB_med_DC_Bus_pos = np.array(PB_med_DC_Bus_pos).T
             PB_med_DC_Bus_neg = np.array(PB_med_DC_Bus_neg).T
             PB_inst_DC_Bus_pos = np.array(PB_inst_DC_Bus_pos).T
             PB_inst_DC_Bus_neg = np.array(PB_inst_DC_Bus_neg).T
             
        if DCBoxes_o_Inv_String == 'DC Boxes':  
             PB_med_cable_de_array_pos = np.array(PB_med_cable_de_array_pos).T
             PB_med_cable_de_array_neg = np.array(PB_med_cable_de_array_neg).T
             PB_inst_cable_de_array_pos = np.array(PB_inst_cable_de_array_pos).T
             PB_inst_cable_de_array_neg = np.array(PB_inst_cable_de_array_neg).T
        elif DCBoxes_o_Inv_String == 'String Inverters':
             PB_med_cable_de_array_AC = np.array(PB_med_cable_de_array_AC).T
             PB_inst_cable_de_array_AC = np.array(PB_inst_cable_de_array_AC).T
    
    
    
        #Mediciones totales   
        secciones_MV_numerico = secciones_MV.astype(int)
        TOT_inst_cable_MV = np.vstack((secciones_MV_numerico,np.zeros_like(secciones_MV_numerico)))
        TOT_med_cable_MV = np.copy(TOT_inst_cable_MV)
        
        if lineas_MV:
            for i, linea in enumerate(lineas_MV):
                if i == 0:
                    continue
                for j, tramo in enumerate(linea):
                    if j==0: #el primer elemento de la linea es un string con el nombre "Line x" antes de empezar los tramos, quizas sobra y se puede eliminar
                        continue
                    else:
                        ind_seccion = np.where(secciones_MV_numerico == tramo[5])[0]
                        TOT_inst_cable_MV[1,ind_seccion] = TOT_inst_cable_MV[1,ind_seccion] + tramo[3] * 3 #Se asume single core
                        TOT_med_cable_MV[1,ind_seccion] = TOT_med_cable_MV[1,ind_seccion] + tramo[4] * 3
        
        if String_o_Bus == 'String Cable':
            TOT_med_cable_de_string_pos=np.vstack((PB_med_cable_de_string_pos[0,:],np.sum(PB_med_cable_de_string_pos[1:,:],axis=0)))
            TOT_med_cable_de_string_neg=np.vstack((PB_med_cable_de_string_neg[0,:],np.sum(PB_med_cable_de_string_neg[1:,:],axis=0)))
            TOT_med_cable_de_string=np.vstack((TOT_med_cable_de_string_pos[0,:],TOT_med_cable_de_string_pos[1,:]+TOT_med_cable_de_string_neg[1,:]))  
            
            TOT_inst_cable_de_string_pos=np.vstack((PB_inst_cable_de_string_pos[0,:],np.sum(PB_inst_cable_de_string_pos[1:,:],axis=0)))
            TOT_inst_cable_de_string_neg=np.vstack((PB_inst_cable_de_string_neg[0,:],np.sum(PB_inst_cable_de_string_neg[1:,:],axis=0)))
            TOT_inst_cable_de_string=np.vstack((TOT_inst_cable_de_string_pos[0,:],TOT_inst_cable_de_string_pos[1,:]+TOT_inst_cable_de_string_neg[1,:]))
            
            cable_string_en_tubo = (1-(np.nansum(tramo_aereo_cable_string_pos)/np.sum(TOT_inst_cable_de_string_pos[1,:])))*100
    
        elif String_o_Bus == 'DC Bus':
            TOT_med_DC_Bus_pos=np.vstack((PB_med_DC_Bus_pos[0,:],np.sum(PB_med_DC_Bus_pos[1:,:],axis=0)))
            TOT_med_DC_Bus_neg=np.vstack((PB_med_DC_Bus_neg[0,:],np.sum(PB_med_DC_Bus_neg[1:,:],axis=0)))
            TOT_med_DC_Bus=np.vstack((TOT_med_DC_Bus_pos[0,:],TOT_med_DC_Bus_pos[1,:]+TOT_med_DC_Bus_neg[1,:]))
            
            TOT_inst_DC_Bus_pos=np.vstack((PB_inst_DC_Bus_pos[0,:],np.sum(PB_inst_DC_Bus_pos[1:,:],axis=0)))
            TOT_inst_DC_Bus_neg=np.vstack((PB_inst_DC_Bus_neg[0,:],np.sum(PB_inst_DC_Bus_neg[1:,:],axis=0)))
            TOT_inst_DC_Bus=np.vstack((TOT_inst_DC_Bus_pos[0,:],TOT_inst_DC_Bus_pos[1,:]+TOT_inst_DC_Bus_neg[1,:]))
            
            DC_Bus_en_tubo = (1-(np.nansum(tramo_aereo_DC_Bus_pos)/np.sum(TOT_inst_DC_Bus_pos[1,:])))*100
            
        else:
            TOT_med_cable_de_string_pos=np.vstack((PB_med_cable_de_string_pos[0,:],np.sum(PB_med_cable_de_string_pos[1:,:],axis=0)))
            TOT_med_cable_de_string_neg=np.vstack((PB_med_cable_de_string_neg[0,:],np.sum(PB_med_cable_de_string_neg[1:,:],axis=0)))
            TOT_med_cable_de_string=np.vstack((TOT_med_cable_de_string_pos[0,:],TOT_med_cable_de_string_pos[1,:]+TOT_med_cable_de_string_neg[1,:]))  
            
            TOT_inst_cable_de_string_pos=np.vstack((PB_inst_cable_de_string_pos[0,:],np.sum(PB_inst_cable_de_string_pos[1:,:],axis=0)))
            TOT_inst_cable_de_string_neg=np.vstack((PB_inst_cable_de_string_neg[0,:],np.sum(PB_inst_cable_de_string_neg[1:,:],axis=0)))
            TOT_inst_cable_de_string=np.vstack((TOT_inst_cable_de_string_pos[0,:],TOT_inst_cable_de_string_pos[1,:]+TOT_inst_cable_de_string_neg[1,:]))    
            
            TOT_med_DC_Bus_pos=np.vstack((PB_med_DC_Bus_pos[0,:],np.sum(PB_med_DC_Bus_pos[1:,:],axis=0)))
            TOT_med_DC_Bus_neg=np.vstack((PB_med_DC_Bus_neg[0,:],np.sum(PB_med_DC_Bus_neg[1:,:],axis=0)))
            TOT_med_DC_Bus=np.vstack((TOT_med_DC_Bus_pos[0,:],TOT_med_DC_Bus_pos[1,:]+TOT_med_DC_Bus_neg[1,:]))
            
            TOT_inst_DC_Bus_pos=np.vstack((PB_inst_DC_Bus_pos[0,:],np.sum(PB_inst_DC_Bus_pos[1:,:],axis=0)))
            TOT_inst_DC_Bus_neg=np.vstack((PB_inst_DC_Bus_neg[0,:],np.sum(PB_inst_DC_Bus_neg[1:,:],axis=0)))
            TOT_inst_DC_Bus=np.vstack((TOT_inst_DC_Bus_pos[0,:],TOT_inst_DC_Bus_pos[1,:]+TOT_inst_DC_Bus_neg[1,:]))
            
            cable_string_en_tubo = (1-(np.nansum(tramo_aereo_cable_string_pos)/np.sum(TOT_inst_cable_de_string_pos[1,:])))*100
            DC_Bus_en_tubo = (1-(np.nansum(tramo_aereo_DC_Bus_pos)/np.sum(TOT_inst_DC_Bus_pos[1,:])))*100
            
            
        if DCBoxes_o_Inv_String == 'DC Boxes':
            TOT_inst_cable_de_array_pos=np.vstack((PB_inst_cable_de_array_pos[0,:],np.sum(PB_inst_cable_de_array_pos[1:,:],axis=0)))
            TOT_inst_cable_de_array_neg=np.vstack((PB_inst_cable_de_array_neg[0,:],np.sum(PB_inst_cable_de_array_neg[1:,:],axis=0)))
            TOT_inst_cable_de_array=np.vstack((TOT_inst_cable_de_array_pos[0,:],TOT_inst_cable_de_array_pos[1,:]+TOT_inst_cable_de_array_neg[1,:]))  
            
            TOT_med_cable_de_array_pos=np.vstack((PB_med_cable_de_array_pos[0,:],np.sum(PB_med_cable_de_array_pos[1:,:],axis=0)))
            TOT_med_cable_de_array_neg=np.vstack((PB_med_cable_de_array_neg[0,:],np.sum(PB_med_cable_de_array_neg[1:,:],axis=0)))
            TOT_med_cable_de_array=np.vstack((TOT_med_cable_de_array_pos[0,:],TOT_med_cable_de_array_pos[1,:]+TOT_med_cable_de_array_neg[1,:]))  
       
        elif DCBoxes_o_Inv_String == 'String Inverters':
            TOT_inst_cable_de_array_AC=np.vstack((PB_inst_cable_de_array_AC[0,:],np.sum(PB_inst_cable_de_array_AC[1:,:],axis=0)))
            TOT_med_cable_de_array_AC=np.vstack((PB_med_cable_de_array_AC[0,:],np.sum(PB_med_cable_de_array_AC[1:,:],axis=0)))
            
        error_medicion_cables = ''
    except:
        traceback.print_exc()
        error_medicion_cables = 'Cables'
        
    return (
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
           )
    
    
def mediciones_por_bloque_y_totales_zanjas(bloque_inicial, n_bloques, PB_zanjas_DC_ID, n_tubos_max_DC1, PB_zanjas_LV_ID, tipos_y_subtipos_unicos, zanjas_AS_ID):
    PB_Zanja_DC1 = None
    PB_Zanja_DC2 = None
    PB_Zanjas_LV = None     

    TOT_Zanja_DC1 = None
    TOT_Zanja_DC2 = None
    TOT_Zanjas_LV = None
    TOT_Zanjas_AS = None
    
    try:
        #ZANJAS DC
        PB_Zanja_DC1=[0]*bloque_inicial
        PB_Zanja_DC2=[0]*bloque_inicial
    
        for i in range(bloque_inicial,n_bloques+1):
            PB_Zanja_DC1.append(0)
            PB_Zanja_DC2.append(0)
            for z in range(0,len(PB_zanjas_DC_ID[i])):
                if PB_zanjas_DC_ID[i][z][0] <= n_tubos_max_DC1:
                    PB_Zanja_DC1[i]=PB_Zanja_DC1[i]+np.linalg.norm(PB_zanjas_DC_ID[i][z][[2,3]]-PB_zanjas_DC_ID[i][z][[4,5]])
                else:
                    PB_Zanja_DC2[i]=PB_Zanja_DC2[i]+np.linalg.norm(PB_zanjas_DC_ID[i][z][[2,3]]-PB_zanjas_DC_ID[i][z][[4,5]])        
            PB_Zanja_DC1[i]=float(PB_Zanja_DC1[i])
            PB_Zanja_DC2[i]=float(PB_Zanja_DC2[i])
                   
        TOT_Zanja_DC1=sum(PB_Zanja_DC1)
        TOT_Zanja_DC2=sum(PB_Zanja_DC2)
    except:
        traceback.print_exc()
        error_medicion_zanjas = 'Trenches'
        
        
    try:
        #ZANJAS LV
        PB_Zanjas_LV = [[] for _ in range(len(PB_zanjas_LV_ID))]
        TOT_Zanjas_LV = [[tipo, subtipo, 0] for tipo, subtipo in tipos_y_subtipos_unicos]
        for i in range(bloque_inicial,n_bloques+1):
            PB_Zanjas_LV[i] = [[tipo, subtipo, 0] for tipo, subtipo in tipos_y_subtipos_unicos]
            for zanja in PB_zanjas_LV_ID[i]:
                for ID in tipos_y_subtipos_unicos:
                    if zanja[1:3] == ID:
                        indice = tipos_y_subtipos_unicos.index(ID)
                        p1 = np.array(zanja[7][0:2])
                        p2 = np.array(zanja[7][2:4])
                        distancia = np.linalg.norm(p1 - p2)
                        PB_Zanjas_LV[i][indice][2] = PB_Zanjas_LV[i][indice][2]+distancia
                        TOT_Zanjas_LV[indice][2]= TOT_Zanjas_LV[indice][2]+distancia
        
        error_medicion_zanjas = ''
    except:
        traceback.print_exc()
        error_medicion_zanjas = 'Trenches'
    
    
    try:
        #ZANJAS AS
        
        TOT_Zanjas_AS = 0
        
        for zanja in zanjas_AS_ID:
            p1 = np.array(zanja[3:5])
            p2 = np.array(zanja[5:7])
            distancia = np.linalg.norm(p1 - p2)

            TOT_Zanjas_AS = TOT_Zanjas_AS + distancia

        error_medicion_zanjas = ''
    except:
        traceback.print_exc()
        error_medicion_zanjas = 'Trenches'
    
        
    
    
    
    
    return PB_Zanja_DC1, PB_Zanja_DC2, TOT_Zanja_DC1, TOT_Zanja_DC2, PB_Zanjas_LV, TOT_Zanjas_LV, error_medicion_zanjas, TOT_Zanjas_AS







def mediciones_por_bloque_y_totales_LV_material(bloque_inicial, n_bloques, n_mods_serie, Interconexionado, DCBoxes_o_Inv_String, String_o_Bus, strings_fisicos, filas_con_cable_string, harness_neg, sch_cable_de_string_neg, sch_DC_Bus_neg, sch_array_cable_neg, sch_array_cable, med_tubo_corrugado_zanja_DC, PB_n_strings):
    PB_Ratchets = None
    PB_0_Cable_clips_2 = None
    PB_90_Cable_clips_2 = None
    PB_90_Cable_clips_4 = None
    PB_Straps_conduits = None
    PB_Cable_Ties = None
    PB_SC_Conector_String_pos = None
    PB_SC_Conector_String_neg = None
    PB_SC_Conector_Box_pos = None
    PB_SC_Conector_Box_neg = None
    PB_DCBus_Endcaps = None
    PB_DCBus_Terminals = None
    PB_Array_Terminal_Box = None
    PB_Array_Terminal_PCS = None
    PB_tubo_DC = None
   
    TOT_Ratchets = None
    TOT_0_Cable_clips_2 = None
    TOT_90_Cable_clips_2 = None
    TOT_90_Cable_clips_4 = None
    TOT_Straps_conduits = None
    TOT_Cable_Ties = None
    TOT_SC_Conector_String_pos = None
    TOT_SC_Conector_String_neg = None
    TOT_SC_Conector_Box_pos = None
    TOT_SC_Conector_Box_neg = None
    TOT_DCBus_Endcaps = None
    TOT_DCBus_Terminal = None
    TOT_Array_Terminal_Box = None
    TOT_Array_Terminal_PCS = None
    TOT_tubo_DC = None
    
    try:
        #Datos directos
        PB_Array_Terminal_Box = np.array([[0,0]]*(n_bloques+1))
        PB_Array_Terminal_PCS = np.array([[0,0]]*(n_bloques+1))
        PB_tubo_DC = np.array([0]*(n_bloques+1))
        #Datos fuente 
        PB_n_circuitos_DC_Bus = np.array([0]*(n_bloques+1))
        PB_n_circuitos_String_cable = np.array([0]*(n_bloques+1))
        PB_n_circuitos_Array_cable = np.array([0]*(n_bloques+1))
        PB_n_tubos_DC = np.array([0]*(n_bloques+1))


        #Rellenamos por bloque los datos fuente
        
            # Función para quitar filas con nan en los dtype=object
        def fila_valida(row):
            for x in row:
                if x in [None, '', 'nan', 'NaN', '-']:
                    return False
                if isinstance(x, float) and np.isnan(x):
                    return False
            return True
        
        for i in range(bloque_inicial,n_bloques+1): 
            if String_o_Bus != 'String Cable':
                DCBus_flat_sin_nan = np.array([tuple(row) for row in sch_DC_Bus_neg[i].reshape(-1, 4) if fila_valida(row)]) 
                PB_n_circuitos_DC_Bus[i] = DCBus_flat_sin_nan.shape[0]
            if String_o_Bus != 'DC Bus':
                String_cable_flat_sin_nan = np.array([tuple(row) for row in sch_cable_de_string_neg[i].reshape(-1, 3) if fila_valida(row)])    
                PB_n_circuitos_String_cable[i] = String_cable_flat_sin_nan.shape[0]
            
            if DCBoxes_o_Inv_String == 'DC Boxes':
                Array_cable_flat_sin_nan = np.array([tuple(row) for row in sch_array_cable_neg[i].reshape(-1, 3) if fila_valida(row)])          
            else:
                Array_cable_flat_sin_nan = np.array([tuple(row) for row in sch_array_cable[i].reshape(-1, 3) if fila_valida(row)]) 
                
            med_tubo_DC_flat_sin_nan = np.array([tuple(row) for row in med_tubo_corrugado_zanja_DC[i].reshape(-1,1) if not np.isnan(row).any()])
            
            
            
            PB_n_circuitos_Array_cable[i] = Array_cable_flat_sin_nan.shape[0]
            PB_n_tubos_DC[i] = med_tubo_DC_flat_sin_nan.shape[0]  # a un tubo por fila coincide con las filas
            
            #TODO, PONER BIEN PARA SECCIONES DETECTADAS Los terminales del array se sacan de aqui porque pueden tener varias secciones
            PB_Array_Terminal_Box[i,0] = sum(1 for fila in Array_cable_flat_sin_nan if int(float(fila[1])) == 300)
            PB_Array_Terminal_PCS[i,0] = sum(1 for fila in Array_cable_flat_sin_nan if int(float(fila[1])) == 300)
            
            PB_Array_Terminal_Box[i,1] = sum(1 for fila in Array_cable_flat_sin_nan if int(float(fila[1])) == 400)
            PB_Array_Terminal_PCS[i,1] = sum(1 for fila in Array_cable_flat_sin_nan if int(float(fila[1])) == 400)        
            
            PB_tubo_DC[i] = sum(med_tubo_DC_flat_sin_nan)
            
            
        #Derivamos los de material a partir de los fuente
        
        PB_Straps_conduits = PB_n_tubos_DC * 4      #Se asumen 4 agarraderas por tubo 
        
        if sch_cable_de_string_neg:
            PB_SC_Conector_String_pos = PB_n_circuitos_String_cable
            PB_SC_Conector_String_neg = PB_n_circuitos_String_cable
            PB_SC_Conector_Box_pos = PB_n_circuitos_String_cable
            PB_SC_Conector_Box_neg = PB_n_circuitos_String_cable
        
        if sch_DC_Bus_neg: 
            PB_Ratchets = PB_n_circuitos_DC_Bus                 #Se asume 1 agarradera final por circuito DC Bus
            PB_DCBus_Endcaps = PB_n_circuitos_DC_Bus * 2      #positivo y negativo
            PB_DCBus_Terminals = PB_n_circuitos_DC_Bus * 2    #positivo y negativo
            
        #Se multiplica para tener en cuenta doble o triple polaridad
        if DCBoxes_o_Inv_String == 'DC Boxes':
            PB_Array_Terminal_Box = PB_Array_Terminal_Box * 2 #pos + neg
            PB_Array_Terminal_PCS = PB_Array_Terminal_PCS * 2 #pos + neg
        else:
            PB_Array_Terminal_Box = PB_n_circuitos_Array_cable * 3 #tres fases
            PB_Array_Terminal_PCS = PB_n_circuitos_Array_cable * 3 #tres fases
        
        
        #Obtenemos los totales
        TOT_Ratchets                = np.sum(PB_Ratchets)
        TOT_Straps_conduits         = np.sum(PB_Straps_conduits)
        TOT_SC_Conector_String_pos  = np.sum(PB_SC_Conector_String_pos)
        TOT_SC_Conector_String_neg  = np.sum(PB_SC_Conector_String_neg)        
        TOT_SC_Conector_Box_pos     = np.sum(PB_SC_Conector_Box_pos)
        TOT_SC_Conector_Box_neg     = np.sum(PB_SC_Conector_Box_neg)
        TOT_DCBus_Endcaps           = np.sum(PB_DCBus_Endcaps)
        TOT_DCBus_Terminal          = np.sum(PB_DCBus_Terminals)
        
        secciones_Array = np.array([300, 400])
        TOT_Array_Terminal_Box      = np.row_stack((secciones_Array, np.sum(PB_Array_Terminal_Box, axis=0)))
        TOT_Array_Terminal_PCS      = np.row_stack((secciones_Array, np.sum(PB_Array_Terminal_PCS, axis=0)))
        
        TOT_tubo_DC                 = np.sum(PB_tubo_DC)
        
        #CALCULO DE CLIPS Y BRIDAS
        max_b = strings_fisicos.shape[1]
        max_f_str_b = strings_fisicos.shape[2]
        max_sf = strings_fisicos.shape[3]
        max_sh = harness_neg.shape[3]
        
        PB_90_Cable_clips_2 = np.array([0]*(n_bloques+1))
        PB_90_Cable_clips_4 = np.array([0]*(n_bloques+1))
        
        if Interconexionado == 'Leapfrog': #En funcion de si se cose al tresbolillo o ida y vuelta se tiene una configuracionu otra
            for i in range(bloque_inicial,n_bloques+1):
                for b in range(0,max_b):
                    if ~np.isnan(strings_fisicos[i,b,0,0,0]): #si la banda no está vacía
                        for f in range(0, max_f_str_b):
                            if ~np.isnan(strings_fisicos[i,b,f,0,0]): #si la fila no está vacía
                                if filas_con_cable_string[i,b,f] == True:  #si la fila tiene cables de string
                                    for s in range(0, max_sf):
                                        if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no esta vacio 
                                            cables_tramo = s*2
                                            #Como en tresbolillo los cables se unen a los tramos de dos en dos, la solucion es inmediata
                                            PB_90_Cable_clips_2[i] = PB_90_Cable_clips_2[i] + (cables_tramo % 4)/2 #resto de la division, los dos cables potencialmente sobrantes, puede valer 0 o 2 y por tanto resultar en 0 o 1
                                            PB_90_Cable_clips_4[i] = PB_90_Cable_clips_4[i] + cables_tramo// 4 #cociente entero, suma al de 4 cuando se supera el de 2

                                #TODO REVISAR BIEN CASUISTICAS CON STRING EXTENSION LARGAS
                                else:  #si la fila tiene DC Bus y ademas tiene un harness con string extension hay que poner cable clip de 2, como es tresbolillo siempre van a ir juntos, da igual el polo a evaluar) y se llevan en el mismo clip
                                    for s in range(0, max_sh):
                                        if harness_neg[i,b,f,s,2] > 0: #si hay un harness con string extension en la posicion
                                            PB_90_Cable_clips_2[i] = PB_90_Cable_clips_2[i] + harness_neg[i,b,f,s,2]
                        
                

        else: #si es ida y vuelta
            for i in range(bloque_inicial,n_bloques+1):
                for b in range(0,max_b):
                    if ~np.isnan(strings_fisicos[i,b,0,0,0]): #si la banda no está vacía
                        for f in range(0, max_f_str_b):
                            if ~np.isnan(strings_fisicos[i,b,f,0,0]): #si la fila no está vacía
                                if filas_con_cable_string[i,b,f] == True:  #si la fila tiene cables de string
                                    for s in range(0, max_sf):
                                        if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no esta vacio 
                                            cables_tramo = s*2+1 #se toma s como final del string, si es ida y vuelta para el string mas alejado llega el cable del polo contrario, y para el siguiente llegan los dos del anterior y acumulados
                                            
                                            PB_90_Cable_clips_4[i] = PB_90_Cable_clips_4[i] + cables_tramo// 4 #siempre que nos pasemos de 4 se agrupa con un clip de 4
                                            
                                            if cables_tramo % 4 == 3: #si los restantes son 3 entonces ya se ha superado el de 2 y hay que usar tambien el de 4
                                                PB_90_Cable_clips_4[i] = PB_90_Cable_clips_4[i] + 1
                                            else: #si es dos ouno se puede usar un clip de 2
                                                PB_90_Cable_clips_2[i] = PB_90_Cable_clips_2[i] + 1 #resto de la division, los dos cables potencialmente sobrantes, puede valer 0 o 2 y por tanto resultar en 0 o 1
                                
                                #TODO REVISAR BIEN CASUISTICAS CON STRING EXTENSION LARGAS
                                else:  #si la fila tiene DC Bus y ademas tiene un harness con string extension hay que poner cable clip de 2 #DEBE ARREGLARSE Y TENER EN CUENTA QUE PUEDA HABER TRAMOS CON UN SOLO CABLE DESDE LADOS DIFERENTES?
                                    for s in range(0, max_sh):
                                        if harness_neg[i,b,f,s,2] > 0: #si hay un harness con string extension en la posicion
                                            PB_90_Cable_clips_2[i] = PB_90_Cable_clips_2[i] + harness_neg[i,b,f,s,2]
                                             

    
        PB_90_Cable_clips_2 = PB_90_Cable_clips_2 * n_mods_serie
        PB_90_Cable_clips_4 = PB_90_Cable_clips_4 * n_mods_serie
        
        TOT_90_Cable_clips_2 = np.sum(PB_90_Cable_clips_2)
        TOT_90_Cable_clips_4 = np.sum(PB_90_Cable_clips_4)
        
        #Para clips de 0º (modulos) y bridas se asumen 1 de cada por cada modulo, lo importamos porque esta ya calculado del bloque de cajas
        PB_0_Cable_clips_2 = PB_n_strings * n_mods_serie 
        PB_Cable_Ties = PB_n_strings * n_mods_serie
        
        TOT_0_Cable_clips_2 = np.sum(PB_0_Cable_clips_2)
        TOT_Cable_Ties = np.sum(PB_Cable_Ties)
        
        
        
        #TODO Faltan los de los servicios auxiliares
        
    except:
        traceback.print_exc()


    return (
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
    TOT_tubo_DC)
    














    
def mediciones_por_bloque_cajas_y_totales_strings(bloque_inicial, n_bloques, DCBoxes_ID):
    PB_n_strings = None
    PB_n_DC_Boxes = None
    PB_DC_Boxes = None
    
    TOT_n_strings = None
    TOT_DC_Boxes = None
    TOT_n_DC_Boxes = None
    
    try:
        PB_n_strings=[0]*bloque_inicial #damos un primer valor (o varios dependiendo de cual es el numero de bloque inicial) para que empiecen el resto por el bloque inicial y no en base 0
 
        for i in range(bloque_inicial,n_bloques+1):
            PB_n_strings.append(int(np.nansum(DCBoxes_ID[i,:,:,7])))
      
        TOT_n_strings=sum(PB_n_strings)
    
        #Sacamos los por bloque de tipos de cajas, los totales no hacen falta porque se calcularon previamente en la funcion de tipos
        PB_n_DC_Boxes=[0]*bloque_inicial #damos un primer valor (o varios dependiendo de cual es el numero de bloque inicial) para que empiecen el resto por el bloque inicial y no en base 0
        PB_DC_Boxes = [0]*bloque_inicial
        
        
        for i in range(bloque_inicial,n_bloques+1):
            DC_Boxes_unicas_bloque = np.unique(DCBoxes_ID[i,...,4].astype(str),return_counts=True)
            PB_DC_Boxes.append(DC_Boxes_unicas_bloque[0])
            PB_n_DC_Boxes.append(DC_Boxes_unicas_bloque[1])
        
        DC_Boxes_unicas = np.unique(DCBoxes_ID[...,4].astype(str),return_counts=True)
        TOT_DC_Boxes=(DC_Boxes_unicas[0])
        TOT_n_DC_Boxes=(DC_Boxes_unicas[1])
        
        error_medicion_cajas = ''
    except:
        traceback.print_exc()
        error_medicion_cajas = 'DC Boxes'
        
    return PB_n_strings, PB_n_DC_Boxes, PB_DC_Boxes, TOT_n_strings, TOT_n_DC_Boxes, TOT_DC_Boxes, error_medicion_cajas


def mediciones_por_bloque_inv_string_y_totales_strings(bloque_inicial, n_bloques, String_Inverters_ID):
    PB_n_strings = None
    PB_n_String_Inverters = None
    PB_String_Inverters = None
    
    TOT_n_strings = None
    TOT_String_Inverters = None
    TOT_n_String_Inverters = None
    
    try:
        PB_n_strings=[0]*bloque_inicial #damos un primer valor (o varios dependiendo de cual es el numero de bloque inicial) para que empiecen el resto por el bloque inicial y no en base 0
 
        for i in range(bloque_inicial,n_bloques+1):
            arr = np.array(String_Inverters_ID[i,:,:,3], dtype=str)
            arr[arr == "nan"] = np.nan
            vals = arr.astype(float)
            PB_n_strings.append(int(np.nansum(vals)))

      
        TOT_n_strings=sum(PB_n_strings)
    
        #Sacamos los por bloque de tipos de cajas, los totales no hacen falta porque se calcularon previamente en la funcion de tipos
        PB_n_String_Inverters=[0]*bloque_inicial #damos un primer valor (o varios dependiendo de cual es el numero de bloque inicial) para que empiecen el resto por el bloque inicial y no en base 0
        PB_String_Inverters = [0]*bloque_inicial
        
        
        for i in range(bloque_inicial,n_bloques+1):
            String_Inverters_unicas_bloque = np.unique(String_Inverters_ID[i,...,3].astype(str),return_counts=True)
            PB_String_Inverters.append(String_Inverters_unicas_bloque[0])
            PB_n_String_Inverters.append(String_Inverters_unicas_bloque[1])
        
        String_Inverters_unicas = np.unique(String_Inverters_ID[...,3].astype(str),return_counts=True)
        TOT_String_Inverters=(String_Inverters_unicas[0])
        TOT_n_String_Inverters=(String_Inverters_unicas[1])
        
        error_medicion_cajas = ''
    except:
        traceback.print_exc()
        error_medicion_cajas = 'DC Boxes'
        
    return PB_n_strings, PB_n_String_Inverters, PB_String_Inverters, TOT_n_strings, TOT_n_String_Inverters, TOT_String_Inverters, error_medicion_cajas


def mediciones_por_bloque_y_totales_PAT(bloque_inicial, n_bloques, PAT_latiguillo_entre_trackers,PAT_latiguillo_primera_pica,PAT_terminal_primera_pica,PAT_terminal_DC_Box, PAT_Electrodo, mayoracion_electrodo_PAT):
    PB_PAT_lat_entre_tr = None 
    PB_PAT_lat_prim_pica = None 
    PB_PAT_term_prim_pica = None 
    PB_PAT_term_DC_Box = None
    
    TOT_PAT_lat_entre_tr = None
    TOT_PAT_lat_prim_pica = None
    TOT_PAT_term_prim_pica = None
    TOT_PAT_term_DC_Box = None  
    TOT_PAT_Electrodo = None  
    try:
        PB_PAT_lat_entre_tr=[0]*bloque_inicial #damos un primer valor para que empiecen el resto por el bloque 1 y no en base 0
        PB_PAT_lat_prim_pica=[0]*bloque_inicial
        PB_PAT_term_prim_pica=[0]*bloque_inicial
        PB_PAT_term_DC_Box=[0]*bloque_inicial
        
        for i in range(bloque_inicial,n_bloques+1):     
            PB_PAT_lat_entre_tr.append(np.count_nonzero(~np.isnan(PAT_latiguillo_entre_trackers[i,:,:,:,0])))
            PB_PAT_lat_prim_pica.append(np.count_nonzero(~np.isnan(PAT_latiguillo_primera_pica[i,:,:,0])))
            PB_PAT_term_prim_pica.append(np.count_nonzero(~np.isnan(PAT_terminal_primera_pica[i,:,:,0])))
            PB_PAT_term_DC_Box.append(np.count_nonzero(~np.isnan(PAT_terminal_DC_Box[i,:,:,0])))
                
        TOT_PAT_lat_entre_tr=sum(PB_PAT_lat_entre_tr)
        TOT_PAT_lat_prim_pica=sum(PB_PAT_lat_prim_pica)
        TOT_PAT_term_prim_pica=sum(PB_PAT_term_prim_pica)
        TOT_PAT_term_DC_Box=sum(PB_PAT_term_DC_Box)  
           
        
    

        TOT_PAT_Electrodo = []
        for segmento in PAT_Electrodo:
            seccion = segmento[0]
            p1 = np.array(segmento[1:3])
            p2 = np.array(segmento[3:5])
            distancia = np.linalg.norm(p1 - p2)
        
            # Buscar si ya existe una entrada con ese nombre
            indices = [i for i, fila in enumerate(TOT_PAT_Electrodo) if fila[0] == seccion]
            if indices:
                indice = indices[0]
                TOT_PAT_Electrodo[indice][1] += distancia*(1+mayoracion_electrodo_PAT/100)
            else:
                TOT_PAT_Electrodo.append([seccion, distancia*(1+mayoracion_electrodo_PAT/100)])
                
        TOT_PAT_Electrodo_ordenado = sorted(TOT_PAT_Electrodo, key=lambda x: x[0])


                
        error_medicion_PAT = ''
    except:
        traceback.print_exc()
        error_medicion_PAT = 'Earthing'
        
    return PB_PAT_lat_entre_tr, PB_PAT_lat_prim_pica, PB_PAT_term_prim_pica, PB_PAT_term_DC_Box, TOT_PAT_lat_entre_tr, TOT_PAT_lat_prim_pica, TOT_PAT_term_prim_pica, TOT_PAT_term_DC_Box, TOT_PAT_Electrodo_ordenado, error_medicion_PAT
