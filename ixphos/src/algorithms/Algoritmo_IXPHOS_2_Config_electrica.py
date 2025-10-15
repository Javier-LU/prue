# -*- coding: utf-8 -*-
"""
Created on Wed May 14 19:37:17 2025

@author: mlopez
"""
import numpy as np
from collections import defaultdict
import itertools

def filas_config_cajas_sin_mezclar_filas(strings_fisicos,bloque_inicial, n_bloques, max_b, max_f_str_b, misc, masc):
    
    filas_en_cajas = np.full((n_bloques+1, max_b+1, max_f_str_b+1, 4), np.nan)
    max_c_block = 0
    max_cpb = 0
    for i in range(bloque_inicial, n_bloques+1):
        c_block = 0
        for b in range(0, max_b+1):
            if ~np.isnan(strings_fisicos[i, b, 0, 0, 0]): #si la banda no está vacia
                c = 0
                str_acum = 0
                last = False
                for f in range(0, max_f_str_b):

                    strings_en_fila = int(np.count_nonzero(~np.isnan(strings_fisicos[i, b, f, :, 0])))
                    if np.isnan(strings_fisicos[i, b, f+1, 0, 0]):
                        last = True  # NO SE USA ==np.nan porque en Python NaN no es igual a sí mismo
    
                    if str_acum + strings_en_fila <= masc and last == False:
                        filas_en_cajas[i, b, f, 0] = c
                        filas_en_cajas[i, b, f, 1] = strings_en_fila
                        filas_en_cajas[i, b, f, 2] = strings_fisicos[i, b, f, 0, 0]
                        filas_en_cajas[i, b, f, 3] = strings_fisicos[i, b, f, 0, 1]
    
                        str_acum = str_acum + strings_en_fila
    
                    else:
                        if strings_en_fila != 0:  # si todavia no hemos pasado la ultima fila, si la hemos pasado no se hace nada hasta que acabe el bucle
                            # si es mayor que la max adm y todavia no hemos llegado a la ultima fila
                            if str_acum + strings_en_fila > masc and last == False:
                                c = c+1
                                filas_en_cajas[i, b, f, 0] = c
                                filas_en_cajas[i, b, f, 1] = strings_en_fila # coord X fila
                                filas_en_cajas[i, b, f, 2] = strings_fisicos[i, b, f, 0, 0] # coord Y fila
                                filas_en_cajas[i, b, f, 3] = strings_fisicos[i, b, f, 0, 1] # el str_acum se actualiza al final para no chocar con str_acum<misc
                            # si es mayor que la max adm y hemos llegado a la ultima fila
                            elif str_acum + strings_en_fila > masc and last == True:
                                c = c+1
                                filas_en_cajas[i, b, f, 0] = c
                                filas_en_cajas[i, b, f, 1] = strings_en_fila #coord X fila
                                filas_en_cajas[i, b, f, 2] = strings_fisicos[i, b, f, 0, 0]# coord Y fila
                                filas_en_cajas[i, b, f, 3] = strings_fisicos[i, b, f, 0, 1]
                                str_acum = strings_en_fila
                            else:  # si no es mayor que la max adm y hemos llegado a la ultima fila
                                filas_en_cajas[i, b, f, 0] = c
                                filas_en_cajas[i, b, f, 1] = strings_en_fila #coord X fila
                                filas_en_cajas[i, b, f, 2] = strings_fisicos[i, b, f, 0, 0]# coord Y fila
                                filas_en_cajas[i, b, f, 3] = strings_fisicos[i, b, f, 0, 1]
                                str_acum = str_acum + strings_en_fila
    
                            if str_acum < misc and last == True:  # cuando misc y masc estan muy separados, lo normal es que solo se incumpla la condicion del minimo en la caja final
                                str_acum_inv = 0
                                c_inv = c
                                # recorremos hacia atrás todo lo escrito para ajustar y meter dentro del minimo esta caja
                                for f_inv in range(f, -1, -1):
                                    strings_en_fila_inv = filas_en_cajas[i,b, f_inv, 1]
                                    str_proy_inv = str_acum_inv+strings_en_fila_inv
                                    if str_proy_inv < misc and str_proy_inv <= masc:
                                        str_acum_inv = str_acum_inv + filas_en_cajas[i, b, f_inv, 1]
                                        filas_en_cajas[i, b, f_inv, 0] = c_inv
    
                                    elif str_proy_inv >= misc and str_proy_inv <= masc:
                                        # si no estoy invadiendo la caja anterior al coger a la inversa, sigo sumandole a la actual aunque haya pasado el minimo
                                        if filas_en_cajas[i, b, f_inv, 0] == c_inv:
                                            str_acum_inv = str_acum_inv + filas_en_cajas[i, b, f_inv, 1]
                                            filas_en_cajas[i, b, f_inv, 0] = c_inv
                                        else:
                                            if str_acum_inv >= misc:
                                                # llego a un cambio de caja en el que la actual ya ha cumplido, asi que cierro
                                                str_acum_inv = filas_en_cajas[i, b, f_inv, 1]
                                                c_inv = c_inv-1
                                                filas_en_cajas[i, b, f_inv, 0] = c_inv
                                            else:
                                                # como en el primer if del for, se cambia a la fila de caja para completar la anterior
                                                str_acum_inv = str_acum_inv + filas_en_cajas[i, b, f_inv, 1]
                                                filas_en_cajas[i, b,f_inv, 0] = c_inv
                                    elif str_proy_inv >= misc and str_proy_inv > masc:
                                        # si con esa fila nos pasamos del maximo cerramos y seguimos con la siguiente caja
                                        c_inv = c_inv-1
                                        filas_en_cajas[i, b, f_inv, 0] = c_inv
                                        str_acum_inv = filas_en_cajas[i, b, f_inv, 1]
    
                                    else:  # si necesitamos avanzar para rellenar la caja pero no podemos porque nos pasariamos del maximo
                                        # se deja igual,
                                        filas_en_cajas[i, b, f_inv, 0] = c_inv
    
                            elif str_acum < misc and last == False:  # si misc y masc estan demasiado juntos, habrá cajas intermedias en las que sin haber podido cumplir la condicion minima se estaría superando la maxima al incorporar la siguiente fila
                                str_acum = strings_en_fila
                                # Incumplimiento_misc=True  Se podria AVISAR QUE NO SE CUMPLEN LOS REQUISITOS MASC MISC
    
                            else:
                                str_acum = strings_en_fila  # si str_acum>misc, lo normal
                                
                    if c > max_cpb:
                        max_cpb = c
                c_block = c_block + c+1
        if c_block > max_c_block:
            max_c_block = c_block
               
    return filas_en_cajas, max_cpb+1, max_c_block+1



def posicion_caja(x_filas, y_filas, str_fila, coord_PCS_DC_inputs, sep_caja_tracker, i, criterio_diseño): 
    if len(x_filas) > 1:
        if criterio_diseño == 'Center':
            #hacemos la media ponderada de las distancias de cada fila a si la caja estuviese en cada una de ellas y nos quedamos con la menor (posible optimizar, si algun string pudiese girarse, la distancia  se reduciria)
            min_dist=100000 #valor grande para inicializar
            distancia_total=np.zeros(len(x_filas))
            for f in range(len(x_filas)):
                distancias = np.sqrt((np.array(x_filas) - x_filas[f])**2 + (np.array(y_filas) - y_filas[f])**2)
                distancias_ponderadas = distancias * np.array(str_fila)
                distancia_total[f]= np.sum(distancias_ponderadas)
                
                if distancia_total[f] < min_dist:
                    min_dist=distancia_total[f]
                    indice_caja=f
            
            # es posible que las filas sean pares y estén equilibradas, cayendo en el punto medio, vemos si alguna fila anexa está más cerca, tenemos cuidado de no salirnos de los indices de la lista
            if indice_caja==len(x_filas)-1:
                if abs(distancia_total[indice_caja-1]-distancia_total[indice_caja]) < 0.1 : #para el caso con dos filas identicas en el que se selecciona la segunda, el 0.1 es tolerancia pero significa que son iguales
                    if abs(x_filas[indice_caja-1] - coord_PCS_DC_inputs[i,0]) < abs(x_filas[indice_caja] - coord_PCS_DC_inputs[i,0]): #comprobamos solo la X para determinar la posicion relativa respecto al inversor
                        indice_caja=indice_caja-1
            elif indice_caja==0:  #para el caso con dos filas identicas en el que se selecciona la primera
                if abs(distancia_total[indice_caja+1]-distancia_total[indice_caja]) < 0.1 :
                    if abs(x_filas[indice_caja+1] - coord_PCS_DC_inputs[i,0]) < abs(x_filas[indice_caja] - coord_PCS_DC_inputs[i,0]):
                        indice_caja=indice_caja+1
            else: #si no está en un extremo tenemos que probar a ambos lados
                if abs(distancia_total[indice_caja+1]-distancia_total[indice_caja]) < 0.1 :
                    if abs(x_filas[indice_caja+1] - coord_PCS_DC_inputs[i,0]) < abs(x_filas[indice_caja] - coord_PCS_DC_inputs[i,0]):
                        indice_caja=indice_caja+1
                        
                elif abs(distancia_total[indice_caja-1]-distancia_total[indice_caja]) < 0.1 :
                    if abs(x_filas[indice_caja-1] - coord_PCS_DC_inputs[i,0]) < abs(x_filas[indice_caja] - coord_PCS_DC_inputs[i,0]):
                        indice_caja=indice_caja-1
                  
            x_caja=x_filas[indice_caja]
            y_caja=y_filas[indice_caja]+sep_caja_tracker
            
        elif criterio_diseño == 'Edge':
            indice_caja = np.nanargmin(np.abs(x_filas-coord_PCS_DC_inputs[i,0]))
            x_caja=x_filas[indice_caja]
            y_caja=y_filas[indice_caja]+sep_caja_tracker
            
    elif len(x_filas) == 1:
        x_caja = x_filas[0]
        y_caja = y_filas[0]+sep_caja_tracker
    else:
        x_caja = np.nan
        y_caja = np.nan
    return x_caja, y_caja




def cajas_desde_filas_asociadas(strings_fisicos, filas_en_cajas, orientacion, coord_PCS_DC_inputs, sep_caja_tracker, Posicion_optima_caja, bloque_inicial, n_bloques, max_b, max_f_str_b, max_c):
    cajas_fisicas = np.full((n_bloques+1, max_b+1, max_c, 4), np.nan) #el primer elemento es el numero de strings, el segundo la x, el tercero la y, el cuarto el inversor al que se asocia, que se define despues de esta funcion
    for i in range(bloque_inicial, n_bloques+1):
        for b in range(0, max_b):
            x_filas = []
            y_filas = []
            str_fila= []
            if orientacion[i, b] == 'S':
                sep_ct = -sep_caja_tracker
            else:
                sep_ct = sep_caja_tracker
            vacias = False
            c = 0
            str_en_caja = 0
            for f in range(0, max_f_str_b):
                if np.isnan(filas_en_cajas[i, b, f, 0]):
                    vacias = True  # NO SE USA ==np.nan porque en Python NaN no es igual a sí mismo
                if filas_en_cajas[i, b, f, 0] == filas_en_cajas[i, b, f+1, 0] and vacias == False:
                    str_en_caja = str_en_caja+filas_en_cajas[i, b, f, 1]
                    x_filas.append(strings_fisicos[i, b, f, 0, 0])
                    y_filas.append(strings_fisicos[i, b, f, 0, 1])
                    str_fila.append(filas_en_cajas[i, b, f, 1])
                    
                # se llega al final de la caja
                elif filas_en_cajas[i, b, f, 0] != filas_en_cajas[i, b, f+1, 0] and vacias == False:
                    str_en_caja = str_en_caja+filas_en_cajas[i, b, f, 1]
                    x_filas.append(strings_fisicos[i, b, f, 0, 0])
                    y_filas.append(strings_fisicos[i, b, f, 0, 1])
                    str_fila.append(filas_en_cajas[i, b, f, 1])

                    x_caja, y_caja = posicion_caja(x_filas, y_filas, str_fila, coord_PCS_DC_inputs, sep_ct, i, Posicion_optima_caja)
                                                
                    cajas_fisicas[i, b, c, 0] = str_en_caja
                    cajas_fisicas[i, b, c, 1] = x_caja
                    cajas_fisicas[i, b, c, 2] = y_caja
                    cajas_fisicas[i, b, c, 3] = 1 #por defecto se asigna la caja al inversor 1, luego si hay mas se modificaran las necesarias

                    c = c+1
                    x_filas = []
                    y_filas = []
                    str_fila= []
                    str_en_caja = 0
                # se pasa la ultima caja, no se hace nada

    return cajas_fisicas


def repartir_cajas_en_dos_inversores(cajas_fisicas, coord_PCS_DC_inputs, lim_str_dif,bloque_inicial, n_bloques, max_b, max_c): #solo disponible para 2
    #Asociamos todas las cajas a la izquierda de la PCS a un inversor y todas las cajas a la derecha al otro, evaluamos cuantos strings hay de diferencia y equilibramos

        #Primera asignacion
    for i in range(bloque_inicial,n_bloques+1):
        #Creamos dos variables de equivalencia en almacenes que usaremos
        equiv_1=[]
        equiv_2=[]
        for b in range(0,max_b):
            if ~np.isnan(cajas_fisicas[i,b,0,0]): #si la banda no está vacía
                for c in range(0,max_c):
                    if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                        if cajas_fisicas[i,b,c,1] <= coord_PCS_DC_inputs[i,0]:
                            cajas_fisicas[i,b,c,3]=1
                            equiv_1.append([b,c])
                        else:
                            cajas_fisicas[i,b,c,3]=2
                            equiv_2.append([b,c])
        #Conteo
        strings_inv_1 = np.nansum(cajas_fisicas[i,:,:,0][cajas_fisicas[i,:,:,3]==1])
        strings_inv_2 = np.nansum(cajas_fisicas[i,:,:,0][cajas_fisicas[i,:,:,3]==2])
        
        if strings_inv_1 - strings_inv_2 > lim_str_dif: #sobran en la izquierda
            #creamos una lista con las cajas de la izquierda, de x mas cercana a mas lejana a la PCS
            distancias_x = np.abs(cajas_fisicas[i,:,:,1][cajas_fisicas[i,:,:,3]==1] - coord_PCS_DC_inputs[i,0])
            indices_reordenados = np.argsort(distancias_x)
            
            for ind in indices_reordenados:
                banda=equiv_1[ind][0]
                caja=equiv_1[ind][1]
                
                cajas_fisicas[i,banda,caja,3]=2
                
                if strings_inv_1 - strings_inv_2 < lim_str_dif:
                    break

        elif strings_inv_2 - strings_inv_1 > lim_str_dif: #sobran en la derecha
            distancias_x = np.abs(cajas_fisicas[i,:,:,1][cajas_fisicas[i,:,:,3]==2] - coord_PCS_DC_inputs[i,0])
            indices_reordenados = np.argsort(distancias_x)
            
            for ind in indices_reordenados:
                banda=equiv_2[ind][0]
                caja=equiv_2[ind][1]
                
                cajas_fisicas[i,banda,caja,3]=1
                
                if strings_inv_2 - strings_inv_1 < lim_str_dif:
                    break
                
    return cajas_fisicas                    


def ID_strings_y_cajas_para_Cable_de_String(strings_fisicos,filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_c, max_c_block, max_b, max_spf, max_f_str_b,masc, dist_ext_opuesto_str, dos_inv):    
    #ID de los strings
    strings_ID=np.full((n_bloques+1,3,max_c_block+1,1,masc+1, 5),np.nan, dtype=object)
    equi_ibfs = np.full((n_bloques+1,max_b,max_f_str_b,max_spf,5),np.nan) #creamos una matriz de equivalencia que relacione la clasificacion en bloque,inv,caja,bus,string en nomenclatura GRS con la clasificacion fisica bloque, banda, fila, string, que ademas tiene base 0 en todo menos el bloque
    equi_reverse_ibfs = np.full((n_bloques+1, 3, max_c_block+1, 1, masc+1, 4),np.nan)
    
    for i in range(bloque_inicial,n_bloques+1):
        caj=0
        sc=1
        for b in range(0,max_b):
            if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b+1):      
                    if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía                 
                        if f != 0 and filas_en_cajas[i,b,f,0]==filas_en_cajas[i,b,f-1,0]: #si la fila está en la misma caja que la anterior
                            for s in range(0,max_spf):
                                if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío 
                                    sc=sc+1 #sumamos un string en la caja
                                    inv = int(cajas_fisicas[i,b,int(filas_en_cajas[i,b,f,0]),3])
                                    if orientacion[i,b]=='N': #definimos los puntos de inicio y fin de acuerdo a la orientacion
                                        #POSIBLE OPTIMIZAR, SI NO QUEREMOS QUE SE MUESTRE EL INV SI SOLO HAY UNO EN LAS ETIQUETAS SE PUEDE METER OTRO IF
                                        if dos_inv==True:
                                            strings_ID[i,inv,caj,0,sc,0]=f"S-{i}-{inv}-{caj}-{sc}"
                                        else:
                                            strings_ID[i,inv,caj,0,sc,0]=f"S-{i}-{caj}-{sc}"
                                        strings_ID[i,inv,caj,0,sc,1]=strings_fisicos[i,b,f,s,0]
                                        strings_ID[i,inv,caj,0,sc,2]=strings_fisicos[i,b,f,s,1]-dist_ext_opuesto_str[i,b,f,s] #si la orientacion es N el inicio del string está al S, hay que restarle la long del string
                                        strings_ID[i,inv,caj,0,sc,3]=strings_fisicos[i,b,f,s,1]
                                        strings_ID[i,inv,caj,0,sc,4]=strings_fisicos[i,b,f,s,2]
                                    
                                    elif orientacion[i,b]=='S':
                                        if dos_inv==True:
                                            strings_ID[i,inv,caj,0,sc,0]=f"S-{i}-{inv}-{caj}-{sc}"
                                        else:
                                            strings_ID[i,inv,caj,0,sc,0]=f"S-{i}-{caj}-{sc}"
                                        strings_ID[i,inv,caj,0,sc,1]=strings_fisicos[i,b,f,s,0]
                                        strings_ID[i,inv,caj,0,sc,2]=strings_fisicos[i,b,f,s,1]+dist_ext_opuesto_str[i,b,f,s] #si la orientacion es S el inicio del string está al N, hay que sumarle la long del string
                                        strings_ID[i,inv,caj,0,sc,3]=strings_fisicos[i,b,f,s,1]
                                        strings_ID[i,inv,caj,0,sc,4]=strings_fisicos[i,b,f,s,2]
                                        
                                    equi_ibfs[i,b,f,s] = [i,inv,caj,0,sc] #al ser caja de string el bus vale 0 siempre, que se guarde como dimension no significa que se represente luego en la nomenclatura
                                    equi_reverse_ibfs[i,inv,caj,0,sc] = [i,b,f,s]
                                    
                        else: #si la fila está en otra caja
                            sc=0
                            caj=caj+1
                            for s in range(0,max_spf):
                                if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío 
                                    sc=sc+1 #sumamos un string en la caja
                                    inv = int(cajas_fisicas[i,b,int(filas_en_cajas[i,b,f,0]),3])
                                    if orientacion[i,b]=='N': #definimos los puntos de inicio y fin de acuerdo a la orientacion
                                        if dos_inv==True:
                                            strings_ID[i,inv,caj,0,sc,0]=f"S-{i}-{inv}-{caj}-{sc}"
                                        else:
                                            strings_ID[i,inv,caj,0,sc,0]=f"S-{i}-{caj}-{sc}"
                                        strings_ID[i,inv,caj,0,sc,1]=strings_fisicos[i,b,f,s,0]
                                        strings_ID[i,inv,caj,0,sc,2]=strings_fisicos[i,b,f,s,1]-dist_ext_opuesto_str[i,b,f,s] #si la orientacion es N el inicio del string está al S, hay que restarle la long del string
                                        strings_ID[i,inv,caj,0,sc,3]=strings_fisicos[i,b,f,s,1]
                                        strings_ID[i,inv,caj,0,sc,4]=strings_fisicos[i,b,f,s,2]
                                        
                                    elif orientacion[i,b]=='S':
                                        if dos_inv==True:
                                            strings_ID[i,inv,caj,0,sc,0]=f"S-{i}-{inv}-{caj}-{sc}"
                                        else:
                                            strings_ID[i,inv,caj,0,sc,0]=f"S-{i}-{caj}-{sc}"
                                        strings_ID[i,inv,caj,0,sc,1]=strings_fisicos[i,b,f,s,0]
                                        strings_ID[i,inv,caj,0,sc,2]=strings_fisicos[i,b,f,s,1]+dist_ext_opuesto_str[i,b,f,s] #si la orientacion es S el inicio del string está al N, hay que sumarle la long del string
                                        strings_ID[i,inv,caj,0,sc,3]=strings_fisicos[i,b,f,s,1]
                                        strings_ID[i,inv,caj,0,sc,4]=strings_fisicos[i,b,f,s,2]
                                        
                                    equi_ibfs[i,b,f,s] = [i,inv,caj,0,sc]
                                    equi_reverse_ibfs[i,inv,caj,0,sc] = [i,b,f,s]
                    
    # ID de las cajas
    DCBoxes_ID=np.full((n_bloques+1,3,max_c_block+1, 8),np.nan, dtype=object)
    equi_ibc = np.full((n_bloques+1, max_b, max_c, 3),np.nan) #creamos matriz de equivalencia para cajas
    equi_reverse_ibc = np.full((n_bloques+1, 3, max_c_block+1, 3),np.nan)
    
    for i in range(bloque_inicial,n_bloques+1):
        caj=1
        for b in range(0,max_b):
            for c in range(0,max_c):
                if ~np.isnan(cajas_fisicas[i,b,c,0]):
                    inv = int(cajas_fisicas[i,b,c,3])
                    if dos_inv==True:
                        DCBoxes_ID[i,inv,caj,0]=f"DCB-{i}.{inv}.{caj}"
                    else:
                        DCBoxes_ID[i,inv,caj,0]=f"DCB-{i}.{caj}"
                    DCBoxes_ID[i,inv,caj,1]=cajas_fisicas[i,b,c,1]
                    DCBoxes_ID[i,inv,caj,2]=cajas_fisicas[i,b,c,2] 
                    equi_ibc[i,b,c]=[i,inv,caj]
                    equi_reverse_ibc[i,inv,caj]=[i,b,c]
                    caj=caj+1
         
    
    return strings_ID , DCBoxes_ID, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs



def ID_strings_y_cajas_para_DC_Bus(strings_fisicos,filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial, n_bloques,max_c, max_c_block,max_b,max_spf, max_f_str_b,masc, dist_ext_opuesto_str, dos_inv):
        #ID de los strings
    strings_ID=np.full((n_bloques+1,3,max_c_block+1,masc+1,masc+1, 5),np.nan, dtype=object)
    equi_ibfs = np.full((n_bloques+1,max_b,max_f_str_b,max_spf,5),np.nan) #creamos una matriz de equivalencia que relacione la clasificacion en bloque,inv,caja,bus,string en nomenclatura GRS con la clasificacion fisica bloque, banda, fila, string, que ademas tiene base 0 en todo menos el bloque
    equi_reverse_ibfs = np.full((n_bloques+1, 3, max_c_block+1, masc+1, masc+1, 4),np.nan)
    
    max_bus=0

    max_sb=0
    for i in range(bloque_inicial,n_bloques+1):
        caj=0
        bus=0
        sb=1
        for b in range(0,max_b):
            if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b+1):      
                    if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía     
                        sb=0
                        if f != 0 and filas_en_cajas[i,b,f,0]==filas_en_cajas[i,b,f-1,0]: #si la fila está en la misma caja que la anterior
                            bus=bus+1                                
                            for s in range(0,max_spf):
                                if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío 
                                    sb=sb+1 #sumamos un string en la fila
                                    inv = int(cajas_fisicas[i,b,int(filas_en_cajas[i,b,f,0]),3])
                                    #definimos los puntos de inicio y fin de acuerdo a la orientacion 
                                    if orientacion[i,b]=='N':
                                         if dos_inv == True:
                                             strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{inv}-{caj}-{bus}-{sb}"
                                         else:
                                             strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{caj}-{bus}-{sb}"
                                         strings_ID[i,inv,caj,bus,sb,1]=strings_fisicos[i,b,f,s,0]
                                         strings_ID[i,inv,caj,bus,sb,2]=strings_fisicos[i,b,f,s,1]-dist_ext_opuesto_str[i,b,f,s] #si la orientacion es N el inicio del string está al S, hay que restarle la long del string
                                         strings_ID[i,inv,caj,bus,sb,3]=strings_fisicos[i,b,f,s,1]
                                         strings_ID[i,inv,caj,bus,sb,4]=strings_fisicos[i,b,f,s,2]
                                             
                                    elif orientacion[i,b]=='S':
                                         if dos_inv == True:
                                             strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{inv}-{caj}-{bus}-{sb}"
                                         else:
                                             strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{caj}-{bus}-{sb}"
                                         strings_ID[i,caj,bus,sb,1]=strings_fisicos[i,b,f,s,0]
                                         strings_ID[i,caj,bus,sb,2]=strings_fisicos[i,b,f,s,1]+dist_ext_opuesto_str[i,b,f,s]  #si la orientacion es S el inicio del string está al N, hay que sumarle la long del string
                                         strings_ID[i,caj,bus,sb,3]=strings_fisicos[i,b,f,s,1]
                                         strings_ID[i,caj,bus,sb,4]=strings_fisicos[i,b,f,s,2]  
                                         
                                    equi_ibfs[i,b,f,s] = [i,inv,caj,bus,sb] 
                                    equi_reverse_ibfs[i,inv,caj,bus,sb] = [i,b,f,s]
                                    
                            if bus > max_bus:
                                max_bus=bus
                            if sb > max_sb:
                                max_sb=sb
                        else: #si la fila está en otra caja o es la primera
                            bus=1
                            caj=caj+1
                            for s in range(0,max_spf):
                                if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío 
                                    sb=sb+1 #sumamos un string en la caja
                                    inv = int(cajas_fisicas[i,b,int(filas_en_cajas[i,b,f,0]),3])
                                    if orientacion[i,b]=='N':
                                        if dos_inv == True:
                                            strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{inv}-{caj}-{bus}-{sb}"
                                        else:
                                            strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{caj}-{bus}-{sb}"
                                        strings_ID[i,inv,caj,bus,sb,1]=strings_fisicos[i,b,f,s,0]
                                        strings_ID[i,inv,caj,bus,sb,2]=strings_fisicos[i,b,f,s,1]-dist_ext_opuesto_str[i,b,f,s] #si la orientacion es N el inicio del string está al S, hay que restarle la long del string
                                        strings_ID[i,inv,caj,bus,sb,3]=strings_fisicos[i,b,f,s,1]
                                        strings_ID[i,inv,caj,bus,sb,4]=strings_fisicos[i,b,f,s,2]
                                    
                                    elif orientacion[i,b]=='S':
                                        if dos_inv == True:
                                            strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{inv}-{caj}-{bus}-{sb}"
                                        else:
                                            strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{caj}-{bus}-{sb}"
                                        strings_ID[i,inv,caj,bus,sb,1]=strings_fisicos[i,b,f,s,0]
                                        strings_ID[i,inv,caj,bus,sb,2]=strings_fisicos[i,b,f,s,1]+dist_ext_opuesto_str[i,b,f,s]  #si la orientacion es S el inicio del string está al N, hay que sumarle la long del string
                                        strings_ID[i,inv,caj,bus,sb,3]=strings_fisicos[i,b,f,s,1]
                                        strings_ID[i,inv,caj,bus,sb,4]=strings_fisicos[i,b,f,s,2]
                                        
                                    equi_ibfs[i,b,f,s] = [i,inv,caj,bus,sb]
                                    equi_reverse_ibfs[i,inv,caj,bus,sb] = [i,b,f,s]
                                    
                            if sb > max_sb:
                                max_sb=sb                
        # ID de las cajas
    DCBoxes_ID=np.full((n_bloques+1,3,max_c_block+1, 8),np.nan, dtype=object)
    equi_ibc = np.full((n_bloques+1, max_b, max_c, 3),np.nan) #creamos matriz de equivalencia para cajas
    equi_reverse_ibc = np.full((n_bloques+1, 3, max_c_block+1, 3),np.nan)
    for i in range(bloque_inicial,n_bloques+1):
        caj=1
        for b in range(0,max_b):
            for c in range(0,max_c):
                if ~np.isnan(cajas_fisicas[i,b,c,0]):
                    inv = int(cajas_fisicas[i,b,c,3])
                    if dos_inv==True:
                        DCBoxes_ID[i,inv,caj,0]=f"DCB-{i}.{inv}.{caj}"
                    else:
                        DCBoxes_ID[i,inv,caj,0]=f"DCB-{i}.{caj}"
                    DCBoxes_ID[i,inv,caj,1]=cajas_fisicas[i,b,c,1]
                    DCBoxes_ID[i,inv,caj,2]=cajas_fisicas[i,b,c,2]
                    equi_ibc[i,b,c]=[i,inv,caj]
                    equi_reverse_ibc[i,inv,caj]=[i,b,c]
                    caj=caj+1
            
    # como hemos calculado el maximo numero de bus y strings por bus acortamos el array
    strings_ID = strings_ID[..., :max_bus+1, :max_sb+1, :] 
    equi_reverse_ibfs = equi_reverse_ibfs[..., :max_bus+1, :max_sb+1, :]
          
    return strings_ID , DCBoxes_ID, max_bus+1, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs


def ID_strings_y_cajas_para_config_mixtas(strings_fisicos,filas_en_cajas,cajas_fisicas, orientacion,bloque_inicial, n_bloques,max_c,max_c_block,max_b,max_spf, max_f_str_b,masc, dist_ext_opuesto_str, String_o_Bus,lim_cable_string, dos_inv):
    #ID de los strings
    strings_ID=np.full((n_bloques+1,3,max_c_block+1,masc+1,masc+1, 5),np.nan, dtype=object)
    filas_con_cable_string=np.zeros((n_bloques+1,max_b,max_f_str_b),dtype=bool)
    equi_ibfs = np.full((n_bloques+1,max_b,max_f_str_b,max_spf,5),np.nan) #creamos una matriz de equivalencia que relacione la clasificacion en bloque,inv,caja,bus,string en nomenclatura GRS con la clasificacion fisica bloque, banda, fila, string, que ademas tiene base 0 en todo menos el bloque
    equi_reverse_ibfs = np.full((n_bloques+1, 3, max_c_block+1, masc+1, masc+1, 4),np.nan)
    
    max_bus=0
    max_sb=0
    for i in range(bloque_inicial,n_bloques+1):
        caj=0
        bus=0
        sb=0
        for b in range(0,max_b):
            if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b+1):      
                    if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía     
                        caja_activa=filas_en_cajas[i,b,f,0]
                        filas_en_caja_activa=filas_en_cajas[i,b,:,0]==caja_activa
                        if f != 0 and filas_en_cajas[i,b,f,0]==filas_en_cajas[i,b,f-1,0]: #si la fila está en la misma caja que la anterior
                            #SI EL NUMERO DE STRINGS ES MENOR QUE EL LIMITE DE STRINGS EN CUALQUIERA DE LA CAJA O EN ESA FILA (EN CADA CASO CORRESPONDIENTE DE CONFIGURACION) LA CONSECUENCIA ES LA MISMA
                            if (String_o_Bus=='Both types' and min(filas_en_cajas[i,b,filas_en_caja_activa,1]) <= lim_cable_string) or (String_o_Bus=='Mixed' and filas_en_cajas[i,b,f,1] <= lim_cable_string):
                                bus=0 #se usa la nomenclatura del dcbus pero poniendole valor 0
                                filas_con_cable_string[i,b,f]=True
                            else:
                                bus=bus+1 
                                sb=0
                            for s in range(0,max_spf):
                                if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío 
                                    sb=sb+1 #sumamos un string en la fila
                                    inv = int(cajas_fisicas[i,b,int(filas_en_cajas[i,b,f,0]),3])
                                    if orientacion[i,b]=='N':
                                        if dos_inv == True:
                                            strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{inv}-{caj}-{bus}-{sb}"
                                        else:
                                            strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{caj}-{bus}-{sb}"
                                        strings_ID[i,inv,caj,bus,sb,1]=strings_fisicos[i,b,f,s,0]
                                        strings_ID[i,inv,caj,bus,sb,2]=strings_fisicos[i,b,f,s,1]-dist_ext_opuesto_str[i,b,f,s] #si la orientacion es N el inicio del string está al S, hay que restarle la long del string
                                        strings_ID[i,inv,caj,bus,sb,3]=strings_fisicos[i,b,f,s,1]
                                        strings_ID[i,inv,caj,bus,sb,4]=strings_fisicos[i,b,f,s,2]
                                    
                                    elif orientacion[i,b]=='S':
                                        if dos_inv == True:
                                            strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{inv}-{caj}-{bus}-{sb}"
                                        else:
                                            strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{caj}-{bus}-{sb}"
                                        strings_ID[i,inv,caj,bus,sb,1]=strings_fisicos[i,b,f,s,0]
                                        strings_ID[i,inv,caj,bus,sb,2]=strings_fisicos[i,b,f,s,1]+dist_ext_opuesto_str[i,b,f,s]  #si la orientacion es S el inicio del string está al N, hay que sumarle la long del string
                                        strings_ID[i,inv,caj,bus,sb,3]=strings_fisicos[i,b,f,s,1]
                                        strings_ID[i,inv,caj,bus,sb,4]=strings_fisicos[i,b,f,s,2]
                                        
                                    equi_ibfs[i,b,f,s] = [i,inv,caj,bus,sb]
                                    equi_reverse_ibfs[i,inv,caj,bus,sb] = [i,b,f,s]
                                        
                            if bus > max_bus:
                                max_bus=bus
                            if sb > max_sb:
                                max_sb=sb
                                
                        else: #si la fila está en otra caja o es la primera
                            sb=0
                            if (String_o_Bus=='Both types' and min(filas_en_cajas[i,b,filas_en_caja_activa,1]) <= lim_cable_string) or (String_o_Bus=='Mixed' and filas_en_cajas[i,b,f,1] <= lim_cable_string):
                                bus=0 #se usa la nomenclatura del dcbus pero poniendole valor 0
                                filas_con_cable_string[i,b,f]=True
                            else:
                                bus=1
                            caj=caj+1
                            for s in range(0,max_spf):
                                if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío 
                                    sb=sb+1 #sumamos un string en la caja
                                    inv = int(cajas_fisicas[i,b,int(filas_en_cajas[i,b,f,0]),3])
                                    if orientacion[i,b]=='N':
                                        if dos_inv == True:
                                            strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{inv}-{caj}-{bus}-{sb}"
                                        else:
                                            strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{caj}-{bus}-{sb}"
                                        strings_ID[i,inv,caj,bus,sb,1]=strings_fisicos[i,b,f,s,0]
                                        strings_ID[i,inv,caj,bus,sb,2]=strings_fisicos[i,b,f,s,1]-dist_ext_opuesto_str[i,b,f,s] #si la orientacion es N el inicio del string está al S, hay que restarle la long del string
                                        strings_ID[i,inv,caj,bus,sb,3]=strings_fisicos[i,b,f,s,1]
                                        strings_ID[i,inv,caj,bus,sb,4]=strings_fisicos[i,b,f,s,2]
                                    
                                    elif orientacion[i,b]=='S':
                                        if dos_inv == True:
                                            strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{inv}-{caj}-{bus}-{sb}"
                                        else:
                                            strings_ID[i,inv,caj,bus,sb,0]=f"S-{i}-{caj}-{bus}-{sb}"
                                        strings_ID[i,inv,caj,bus,sb,1]=strings_fisicos[i,b,f,s,0]
                                        strings_ID[i,inv,caj,bus,sb,2]=strings_fisicos[i,b,f,s,1]+dist_ext_opuesto_str[i,b,f,s]  #si la orientacion es S el inicio del string está al N, hay que sumarle la long del string
                                        strings_ID[i,inv,caj,bus,sb,3]=strings_fisicos[i,b,f,s,1]
                                        strings_ID[i,inv,caj,bus,sb,4]=strings_fisicos[i,b,f,s,2]
                                        
                                    equi_ibfs[i,b,f,s] = [i,inv,caj,bus,sb]
                                    equi_reverse_ibfs[i,inv,caj,bus,sb] = [i,b,f,s]

                            if sb > max_sb:
                                max_sb=sb
    # ID de las cajas
    DCBoxes_ID=np.full((n_bloques+1,3,max_c_block+1, 8),np.nan, dtype=object)
    equi_ibc = np.full((n_bloques+1, max_b, max_c, 3),np.nan) #creamos matriz de equivalencia para cajas
    equi_reverse_ibc = np.full((n_bloques+1, 3, max_c_block+1, 3),np.nan)
    for i in range(bloque_inicial,n_bloques+1):
        caj=1
        for b in range(0,max_b):
            for c in range(0,max_c):
                if ~np.isnan(cajas_fisicas[i,b,c,0]):
                    inv = int(cajas_fisicas[i,b,c,3])
                    if dos_inv==True:
                        DCBoxes_ID[i,inv,caj,0]=f"DCB-{i}.{inv}.{caj}"
                    else:
                        DCBoxes_ID[i,inv,caj,0]=f"DCB-{i}.{caj}"
                    DCBoxes_ID[i,inv,caj,1]=cajas_fisicas[i,b,c,1]
                    DCBoxes_ID[i,inv,caj,2]=cajas_fisicas[i,b,c,2]                    
                    equi_ibc[i,b,c]=[i,inv,caj]
                    equi_reverse_ibc[i,inv,caj]=[i,b,c]
                    caj=caj+1

            
    # como hemos calculado el maximo numero de bus acortamos el array
    
    strings_ID = strings_ID[..., :max_bus+1, :, :] 
    equi_reverse_ibfs = equi_reverse_ibfs[..., :max_bus+1, :, :]
    
    return strings_ID , DCBoxes_ID, max_bus+1, equi_ibfs, equi_ibc, equi_reverse_ibc, equi_reverse_ibfs, filas_con_cable_string


def calculo_DC_Boxes(bloque_inicial, n_bloques, max_b, max_c, max_f_str_b, max_c_block, masc, filas_en_cajas, String_o_Bus, filas_con_cable_string, equi_ibc, DCBoxes_ID, cajas_fisicas):
    descripcion_DC_Boxes=np.zeros((n_bloques+1,max_b,max_c,masc,3))
    tipos_cajas_str_por_entradas = None
    tipos_cajas_bus_por_entradas = None
    tipos_cajas_mix_por_entradas = None
    n_tipos_cajas_str = 0
    n_tipos_cajas_bus = 0
    n_tipos_cajas_mix = 0
    
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(filas_en_cajas[i,b,0,0]):
                c_ant=0
                e_str=0
                e_bus=0
                for f in range(0,max_f_str_b):
                    if ~np.isnan(filas_en_cajas[i,b,f,0]):
                        c = int(filas_en_cajas[i,b,f,0]) #identificamos la caja donde se inserta la fila
                        if c_ant != c:
                            #Empieza nueva caja, inicializamos contadores de entradas
                            e_str=0
                            e_bus=0
                            #Al hacer cambio de caja evaluamos que tipos de entradas tiene la anterior y la clasificamos como string, DCBus o mixta en la columna 3, en la 4 dejamos libre para el tipo de caja, en la 5 el numero de entradas de strings y en la 6 el numero de entradas de bus, la 7 muestra el numero de strings asociados
                            inv = int(equi_ibc[i,b,c_ant,1])
                            caj = int(equi_ibc[i,b,c_ant,2])
                            
                            if np.sum(descripcion_DC_Boxes[i,b,c_ant,:,0]) > 0.1:
                                if np.sum(descripcion_DC_Boxes[i,b,c_ant,:,1]) > 0.1:
                                    DCBoxes_ID[i,inv,caj,3]='Mix'
                                    DCBoxes_ID[i,inv,caj,5]=int(np.sum(descripcion_DC_Boxes[i,b,c_ant,:,0]))
                                    DCBoxes_ID[i,inv,caj,6]=int(np.sum(descripcion_DC_Boxes[i,b,c_ant,:,1]))
                                    DCBoxes_ID[i,inv,caj,7]=int(cajas_fisicas[i,b,c_ant,0])
                                else:
                                    DCBoxes_ID[i,inv,caj,3]='Strings'
                                    DCBoxes_ID[i,inv,caj,5]=int(np.sum(descripcion_DC_Boxes[i,b,c_ant,:,0]))
                                    DCBoxes_ID[i,inv,caj,7]=int(cajas_fisicas[i,b,c_ant,0])
                            else:
                                if np.sum(descripcion_DC_Boxes[i,b,c_ant,:,1]) > 0.1:
                                    DCBoxes_ID[i,inv,caj,3]='DC Buses'
                                    DCBoxes_ID[i,inv,caj,6]=int(np.sum(descripcion_DC_Boxes[i,b,c_ant,:,1]))
                                    DCBoxes_ID[i,inv,caj,7]=int(cajas_fisicas[i,b,c_ant,0])
                                    
                        #diferenciamos entre filas con strings y filas con dcbus para determinar el numero de entradas de string (columna 0) y el de entradas de dcbus(columna 1) con su respectivo numero de strings asociado (columna 3)
                        if filas_con_cable_string[i,b,f]==True:
                            for rep in range(0,int(filas_en_cajas[i,b,f,1])):
                                descripcion_DC_Boxes[i,b,c,e_str,0]=1
                                e_str=e_str+1
                        else:
                            descripcion_DC_Boxes[i,b,c,e_bus,1]=1
                            descripcion_DC_Boxes[i,b,c,e_bus,2]=filas_en_cajas[i,b,f,1]
                            e_bus=e_bus+1                        
                        c_ant=c
                        
                        
                #Cuando se han recorrido todas las f existentes de la banda hay que leer la ultima caja, porque no llega a realizarse c_ant
                        if np.isnan(filas_en_cajas[i,b,f+1,0]) or f == max_f_str_b-1:
                            inv = int(equi_ibc[i,b,c_ant,1])
                            caj = int(equi_ibc[i,b,c_ant,2])
                            
                            if np.sum(descripcion_DC_Boxes[i,b,c_ant,:,0]) > 0.1:
                                if np.sum(descripcion_DC_Boxes[i,b,c_ant,:,1]) > 0.1:
                                    DCBoxes_ID[i,inv,caj,3]='Mix'
                                    DCBoxes_ID[i,inv,caj,5]=int(np.sum(descripcion_DC_Boxes[i,b,c_ant,:,0]))
                                    DCBoxes_ID[i,inv,caj,6]=int(np.sum(descripcion_DC_Boxes[i,b,c_ant,:,1]))
                                    DCBoxes_ID[i,inv,caj,7]=int(cajas_fisicas[i,b,c_ant,0])
                                else:
                                    DCBoxes_ID[i,inv,caj,3]='Strings'
                                    DCBoxes_ID[i,inv,caj,5]=int(np.sum(descripcion_DC_Boxes[i,b,c_ant,:,0]))
                                    DCBoxes_ID[i,inv,caj,7]=int(cajas_fisicas[i,b,c_ant,0])
                            else:
                                if np.sum(descripcion_DC_Boxes[i,b,c_ant,:,1]) > 0.1:
                                    DCBoxes_ID[i,inv,caj,3]='DC Buses'
                                    DCBoxes_ID[i,inv,caj,6]=int(np.sum(descripcion_DC_Boxes[i,b,c_ant,:,1]))
                                    DCBoxes_ID[i,inv,caj,7]=int(cajas_fisicas[i,b,c_ant,0])
                                    
                                    
    if String_o_Bus == 'String Cable':
        descripcion_DC_Boxes_flat = descripcion_DC_Boxes[...,0].reshape(-1, descripcion_DC_Boxes[...,0].shape[-1])
        descripcion_DC_Boxes_flat_sin_ceros = descripcion_DC_Boxes_flat[~np.all(descripcion_DC_Boxes_flat == 0, axis=1)]
        
        tipos_cajas_str, n_tipos_cajas_str = np.unique(descripcion_DC_Boxes_flat_sin_ceros ,axis=0,return_counts=True)
        tipos_cajas_str_por_entradas = np.sum(tipos_cajas_str,axis=1)
        
        tipos_cajas_por_entradas = tipos_cajas_str_por_entradas
        
    elif String_o_Bus == 'DC Bus':    
        descripcion_DC_Boxes_flat = descripcion_DC_Boxes[...,1].reshape(-1, descripcion_DC_Boxes[...,0].shape[-1])
        descripcion_DC_Boxes_flat_sin_ceros = descripcion_DC_Boxes_flat[~np.all(descripcion_DC_Boxes_flat == 0, axis=1)]
        
        tipos_cajas_bus, n_tipos_cajas = np.unique(descripcion_DC_Boxes_flat_sin_ceros ,axis=0,return_counts=True)
        tipos_cajas_bus_por_entradas = np.sum(tipos_cajas_bus,axis=1)
        
        tipos_cajas_por_entradas = tipos_cajas_bus_por_entradas
        
    elif String_o_Bus == 'Both types':
        descripcion_DC_Boxes_str_flat = descripcion_DC_Boxes[...,0].reshape(-1, descripcion_DC_Boxes[...,0].shape[-1])
        descripcion_DC_Boxes_str_flat_sin_ceros = descripcion_DC_Boxes_str_flat[~np.all(descripcion_DC_Boxes_str_flat == 0, axis=1)]
        descripcion_DC_Boxes_bus_flat = descripcion_DC_Boxes[...,1].reshape(-1, descripcion_DC_Boxes[...,0].shape[-1])
        descripcion_DC_Boxes_bus_flat_sin_ceros = descripcion_DC_Boxes_bus_flat[~np.all(descripcion_DC_Boxes_bus_flat == 0, axis=1)]
        
        tipos_cajas_str, n_tipos_cajas_str = np.unique(descripcion_DC_Boxes_str_flat_sin_ceros ,axis=0 ,return_counts=True)
        tipos_cajas_bus, n_tipos_cajas_bus = np.unique(descripcion_DC_Boxes_bus_flat_sin_ceros ,axis=0 ,return_counts=True)
        
        tipos_cajas_str_por_entradas = np.sum(tipos_cajas_str,axis=1).astype(int)
        tipos_cajas_bus_por_entradas = np.sum(tipos_cajas_bus,axis=1).astype(int)      
        
        tipos_cajas_por_entradas = np.hstack((tipos_cajas_bus_por_entradas,tipos_cajas_str_por_entradas))
        
    elif String_o_Bus == 'Mixed':    
        descripcion_DC_Boxes_trasposed = np.moveaxis(descripcion_DC_Boxes[...,[0,1]],-1,-2)
        descripcion_DC_Boxes_flat = descripcion_DC_Boxes_trasposed.reshape(-1, masc*2)
        
        descripcion_DC_Boxes_str_flat = descripcion_DC_Boxes_flat[np.all(descripcion_DC_Boxes_flat[:, :masc] == 0, axis=1)]
        descripcion_DC_Boxes_str_flat_sin_ceros = descripcion_DC_Boxes_str_flat[~np.all(descripcion_DC_Boxes_str_flat == 0, axis=1)]
        
        descripcion_DC_Boxes_bus_flat = descripcion_DC_Boxes_flat[np.all(descripcion_DC_Boxes_flat[:, masc:] == 0, axis=1)]
        descripcion_DC_Boxes_bus_flat_sin_ceros = descripcion_DC_Boxes_bus_flat[~np.all(descripcion_DC_Boxes_bus_flat == 0, axis=1)]
    
        descripcion_DC_Boxes_mix_flat = descripcion_DC_Boxes_flat[np.any(descripcion_DC_Boxes_flat[:, masc:] != 0, axis=1) & np.any(descripcion_DC_Boxes_flat[:, :masc] != 0, axis=1)]
        descripcion_DC_Boxes_mix_flat_sin_ceros = descripcion_DC_Boxes_mix_flat[~np.all(descripcion_DC_Boxes_mix_flat == 0, axis=1)]
        
        tipos_cajas_str, n_tipos_cajas_str = np.unique(descripcion_DC_Boxes_str_flat_sin_ceros,axis=0,return_counts=True)
        tipos_cajas_bus, n_tipos_cajas_bus = np.unique(descripcion_DC_Boxes_bus_flat_sin_ceros,axis=0,return_counts=True)
        tipos_cajas_mix, n_tipos_cajas_mix = np.unique(descripcion_DC_Boxes_mix_flat_sin_ceros,axis=0,return_counts=True)
        
        tipos_cajas_str_por_entradas = np.sum(tipos_cajas_str,axis=1).astype(int)
        tipos_cajas_bus_por_entradas = np.sum(tipos_cajas_bus,axis=1).astype(int) 
        tipos_cajas_mix_por_entradas = np.stack([np.sum(tipos_cajas_mix[:,masc:],axis=1).astype(int), np.sum(tipos_cajas_mix[:,:masc],axis=1).astype(int)], axis=1)
        
        tipos_cajas_por_entradas = np.hstack((tipos_cajas_bus_por_entradas,tipos_cajas_mix_por_entradas, tipos_cajas_str_por_entradas))
        
    #Completamos añadiendo el tipo de caja a DCBoxes_ID
    for i in range(bloque_inicial,n_bloques+1):
        for inv in range(1,3):
            if ~np.isnan(DCBoxes_ID[i,inv,1,1]):
                for caj in range(1,max_c_block+1):
                    if ~np.isnan(DCBoxes_ID[i,inv,caj,1]):
                        if DCBoxes_ID[i,inv,caj,3]=='Mix':
                            tipo = int(np.where((tipos_cajas_mix_por_entradas[0] == DCBoxes_ID[i,inv,caj,5]) & (tipos_cajas_mix_por_entradas[1] == DCBoxes_ID[i,inv,caj,6])))
                            DCBoxes_ID[i,inv,caj,4]= f'M-{tipo+1}'
                            
                        elif DCBoxes_ID[i,inv,caj,3]=='Strings':
                            tipo = int(np.where(tipos_cajas_str_por_entradas == DCBoxes_ID[i,inv,caj,5])[0])
                            DCBoxes_ID[i,inv,caj,4]= f'S-{tipo+1}'
                            
                        elif DCBoxes_ID[i,inv,caj,3]=='DC Buses':
                            tipo = int(np.where(tipos_cajas_bus_por_entradas == DCBoxes_ID[i,inv,caj,6])[0])
                            DCBoxes_ID[i,inv,caj,4]= f'B-{tipo+1}'


    n_tipos_cajas_str = np.sum(n_tipos_cajas_str)
    n_tipos_cajas_bus = np.sum(n_tipos_cajas_bus)
    n_tipos_cajas_mix = np.sum(n_tipos_cajas_mix)
    n_cajas_totales = n_tipos_cajas_str + n_tipos_cajas_bus + n_tipos_cajas_mix
    
    

    return DCBoxes_ID, tipos_cajas_por_entradas, n_tipos_cajas_str, n_tipos_cajas_bus, n_tipos_cajas_mix, n_cajas_totales
























#FUNCIONES INVERSORES DE STRING

def combinacion_inv_en_bandas_optima(bloque_inicial,n_bloques, strings_fisicos, lim_str_interc, conf_inversores, contorno_bandas, dist_max_inter_bandas, max_b, max_fr):                   
    matriz_bandas_cercanas = np.zeros((n_bloques+1,max_b, max_b), dtype=bool)  
    puente  = np.full((n_bloques+1,max_b, max_b, contorno_bandas.shape[2], 5), np.nan)  
    combinacion_optima=[]
    ganancias_perdidas_optima=[]
    matriz_intercambios_optima=[]

    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(contorno_bandas[i,b,0,0]):
                p_contorno_max = np.where(~np.isnan(contorno_bandas[i,b]).all(axis=1))[0][-1]
                for bc in range(b+1,max_b):
                    if ~np.isnan(contorno_bandas[i,bc,0,0]):
                        pc_contorno_max = np.where(~np.isnan(contorno_bandas[i,bc]).all(axis=1))[0][-1]
                        
                        #vemos que puntos del contorno_bandas estan dentro de la distancia minima
                        n=0       
                        min_dist_puente=dist_max_inter_bandas
                        puente_establecido=False  
                        
                        for p in range(0,p_contorno_max-1):
                            for pc in range(0,pc_contorno_max-1):
                                dist=np.linalg.norm(contorno_bandas[i,b,p]-contorno_bandas[i,bc,pc])
                                if dist < dist_max_inter_bandas: #hay conexion entre las bandas, ahora vemos cual los posibles puentes para p es más corto para quedarnos con el
                                    if dist <= min_dist_puente:
                                        min_dist_puente=dist
                                        x_p_puente=contorno_bandas[i,b,p,0]
                                        y_p_puente=contorno_bandas[i,b,p,1]
                                        x_pc_puente=contorno_bandas[i,bc,pc,0]
                                        y_pc_puente=contorno_bandas[i,bc,pc,1]
                                        puente_establecido=True
                                    
                            if puente_establecido==True: #a este if se llega tras evaluar todos los p y pc
                                n=n+1
                                matriz_bandas_cercanas[i,b,bc]=True
                                matriz_bandas_cercanas[i,bc,b]=True
                                
                                puente[i,b,bc,n,0]=min_dist_puente
                                puente[i,b,bc,n,1]=x_p_puente
                                puente[i,b,bc,n,2]=y_p_puente
                                puente[i,b,bc,n,3]=x_pc_puente
                                puente[i,b,bc,n,4]=y_pc_puente
                                #el simetrico tambien es igual, pero con los puntos invertidos
                                puente[i,bc,b,n,0]=min_dist_puente
                                puente[i,bc,b,n,1]=x_pc_puente
                                puente[i,bc,b,n,2]=y_pc_puente
                                puente[i,bc,b,n,3]=x_p_puente
                                puente[i,bc,b,n,4]=y_p_puente
                                
                                #POSIBILIDAD DE OPTIMIZAR INTRODUCIENDO A MANO QUÉ BANDAS QUEREMOS QUE INTERCAMBIEN STRINGS EN LUGAR DE HACERLO POR DISTANCIA
                #añadimos otra columna a la matriz de identidades con el numero de conexiones directas de cada banda
                conexiones_mat=np.sum(matriz_bandas_cercanas[i],axis=1)
            
        #calculamos las combinaciones posibles de inversores
        valid_combinations=[]
        for b in range(0,max_b):
            str_b=np.count_nonzero(~np.isnan(strings_fisicos[i,b,:,:,1])) #para cada banda, contamos el numero de strings fisicos
            #creamos una matriz bidimensional en la que se listan todas las posibles combinaciones de los inversores de ese bloque
            rangos=[range(x, -1, -1) for x in conf_inversores[i]]
            combinations = np.array(np.meshgrid(*rangos)).T.reshape(-1, len(conf_inversores[i]))
            #multiplicamos las columnas de la matriz por los strings de cada tipo de inversor, las sumamos (op. directa con np.dot) y le restamos el valor de strings en la banda para ver qué combinación es más precisa, nos quedamos solo con aquesllas configuraciones con dif menores al max n strings/inv
            diff_of_combinations = str_b-np.dot(combinations,conf_inversores[0])
            combinations_in_range=abs(diff_of_combinations) < lim_str_interc
            
            valid_combinations.append(np.hstack((combinations[combinations_in_range],diff_of_combinations[combinations_in_range].reshape(-1,1)))) #nos quedamos unicamente con las combinaciones validas y una columna adicional con la diferencia respecto a los strings reales
            
        all_combinations = list(itertools.product(*valid_combinations)) #ahora combinamos las combinaciones de las distintas bandas
        filtered_combinations = []
        potential_combinations=[]
        for comb in all_combinations:
           
            total_diff = sum([band[-1] for band in comb])
            inv_sum = sum([sum(band[:-1]) for band in comb])
            if total_diff == 0 and inv_sum == np.sum(conf_inversores[i]): #para poder cuadrar el bloque entero, la suma de las diferencias en las posibles combinaciones de todas las bandas debe dar cero
                filtered_combinations.append(comb)  
        
        for comb in filtered_combinations:
            for band in comb:
                n=0
                comb_aislada=False
                if band[-1]!=0 and conexiones_mat[n]==0: #si hay un bloque aislado pero se cuenta un intercambio esa opcion no es valida
                    comb_aislada=True
                n=n+1
            if comb_aislada==False:
                potential_combinations.append(comb)
    
        potential_combinations=np.array(potential_combinations) #no olvidar potential combinations luego se va a actualizar, si se quiere examinar se debe hacer una copia
        
        if potential_combinations.shape[0]==0:
            print("Esta combinacion no es posible, debe revisarse el numero de inversores, si está bien debe cambiarse el nº de strings o permitir unir bandas de trackers mas separadas subiendo dist_max_inter_bandas")
            return False

        #HIPOTESIS DEL CUELLO DE BOTELLA, es posible que haya bandas con diferencia neta 0 (u otro valor) que venga de que cogen -x de una banda para ceder +x a otra ya que no existe conexion entre ellas
        #se puede contrastar si hay conexion entre las bandas positivas y las bandas negativas, en caso de no haberla sabemos que tiene que haber una banda puente en la que se están produciendo saltos
        
        #se cogen las bandas positivas y se evaluan las ganancias y pérdidas en conexiones directas, actualizando el valor neto
            #si todos los valores terminan siendo cero no hay bandas puente
            #si queda algun positivo y negativo habra que trazar un camino entre ambas, puede haber varios caminos posibles, pero evaluaremos el más corto (el que involucre a menos bandas y en caso de igualdad el de menor distancia)
            #en cada una de las bandas puente se hace un balance de cada lado (sin tener en cuenta su valor), los resultados son los strings que tiene que tomar y ceder de cada banda anexa
     
        #empezamos desde las bandas con menor numero de conexiones a las de mayor para evitar tener que probar muchas configuraciones que no sean posibles #POSIBILIDAD DE OPTIMIZAR EL DISEÑO EVALUANDOLAS TODAS TAMBIEN
        orden_ev_comb=sorted(range(len(conexiones_mat)), key=lambda k: conexiones_mat[k])
        ganancias_perdidas=np.zeros((potential_combinations.shape[0],potential_combinations.shape[1],2)) #creamos una matriz parecida para almacenar ganancias y perdidas, comb se va a ir actualizando y reduciendo al tiempo de los intercambios
        matriz_intercambio=np.zeros((n_bloques+1,potential_combinations.shape[0],potential_combinations.shape[1],potential_combinations.shape[1]))
        gp=0
        for comb in potential_combinations:
            for b in orden_ev_comb:
                for bc in range(0,max_b):
                    if matriz_bandas_cercanas[i,b,bc]==True and comb[b,-1] != 0 and comb[b,-1]*comb[bc,-1]<0: #solo se evaluan combinaciones en las que haya conexion directa, haga falta y ocurra que una coja y la otra reciba (una + y otra -)
                        if comb[b,-1] < 0:
                            if comb[b,-1]+comb[bc,-1] >= 0:  #si la suma de ambas es de signo contrario a la inicial es porque se acaban los strings a intercambiar, aqui b es - y bc +
                                ganancias_perdidas[gp,b,0]=ganancias_perdidas[gp,b,0]+comb[b,-1]    #acumulamos las ganancias necesarias (-) del intercambio, recordar que las 0 tienen que ser - y las 1 +
                                ganancias_perdidas[gp,bc,1]=ganancias_perdidas[gp,bc,1]-comb[b,-1]  #acumulamos las perdidas necesarias (+) del intercambio
                                
                                matriz_intercambio[i,gp,b,bc]=comb[b,-1] #se guardan el intercambio en otro formato para mas tarde, como el inicial es negativo, el orden b-bc es negativo
                                matriz_intercambio[i,gp,bc,b]=-comb[b,-1] #como bc es positivo, hay que poner un signo - para que b cuadra - REGLA: [bc,b][b] si el primer termino y el tercero son diferentes, el tercero tiene que llevar un signo negativo
                                
                                comb[bc,-1]=comb[bc,-1]+comb[b,-1]  #actualizamos comb tras el intercambio
                                comb[b,-1]=0                        #actualizamos comb tras el intercambio
                                 
                            elif comb[b,-1]+comb[bc,-1] < 0: #si la suma de ambas es del mismo signo a la inicial es porque bc se acaba antes de b
                                ganancias_perdidas[gp,b,0]=ganancias_perdidas[gp,b,0]-comb[bc,-1]   #acumulamos las ganancias necesarias (-) del intercambio
                                ganancias_perdidas[gp,bc,1]=ganancias_perdidas[gp,bc,1]+comb[bc,-1] #acumulamos las perdidas necesarias (+) del intercambio
                                
                                matriz_intercambio[i,gp,b,bc]=-comb[bc,-1]
                                matriz_intercambio[i,gp,bc,b]=+comb[bc,-1]
                                
                                comb[b,-1]=comb[b,-1]+comb[bc,-1]   #actualizamos comb tras el intercambio
                                comb[bc,-1]=0                       #actualizamos comb tras el intercambio
                                
                        elif comb[b,-1] > 0:                                                                                                                        #aqui b es + y bc -
                            if comb[b,-1]+comb[bc,-1] >= 0:
                                ganancias_perdidas[gp,b,1]=ganancias_perdidas[gp,b,1]-comb[bc,-1]    #recordar que las 0 tienen que ser - y las 1 +
                                ganancias_perdidas[gp,bc,0]=ganancias_perdidas[gp,bc,0]+comb[bc,-1] 
                                
                                matriz_intercambio[i,gp,b,bc]=-comb[bc,-1]
                                matriz_intercambio[i,gp,bc,b]=+comb[bc,-1]
                                
                                comb[b,-1]=comb[b,-1]+comb[bc,-1]   
                                comb[bc,-1]=0                      
                                
                            elif comb[b,-1]+comb[bc,-1] < 0:
                                ganancias_perdidas[gp,b,1]=ganancias_perdidas[gp,b,1]+comb[b,-1]    
                                ganancias_perdidas[gp,bc,0]=ganancias_perdidas[gp,bc,0]-comb[b,-1]  
                                
                                matriz_intercambio[i,gp,b,bc]=+comb[b,-1]
                                matriz_intercambio[i,gp,bc,b]=-comb[b,-1]
                                
                                comb[bc,-1]=comb[bc,-1]+comb[b,-1] 
                                comb[b,-1]=0                        
            
            potential_combinations[gp]=comb #actualizamos el array tras las modificaciones en la iteracion flotante
            gp=gp+1                        
                                    # #tras este for tenemos unas potential combinations en las que se han hecho los intercambios directos (guardados en ganancias_perdidas)
        
        #ahora toca unir los restantes, evaluamos cuantos saltos de bandas hay que dar para que cada positivo llegue a cada negativo #POSIBILIDAD DE OPTIMIZAR, DE MOMENTO SOLO VA A FUNCIONAR BIEN SI HAY UN POSITIVO Y UN NEGATIVO
        
        gp=0
        for comb in potential_combinations:
            for b in range(0,max_b):
                for bc in range(b+1,max_b): #evitamos repetir evaluar la misma combinacion cuando se inviertan b y bc
                    if comb[b,-1] != 0 and comb[bc,-1] != 0 and comb[b,-1]*comb[bc,-1]<0:
                        alcanzado_por_todos_caminos_posibles=False
                        caminos_validos=[]
                        caminos_evaluados=[]
                        matriz_b_bc=np.copy(matriz_bandas_cercanas[i])
                        while alcanzado_por_todos_caminos_posibles==False:
                            alcanzado=False
                            camino_potencial=[b]        
                            ba=b #banda a analizar de partida
                            bandas_analizadas=[b]
                            while alcanzado==False:
                                col=0
                                for conexion in matriz_b_bc[ba,:]:              #recorro las conexiones directas de la banda a analizar, en el primer caso la de partida, por eso arriba ba=b
                                    salto=False
                                    if bandas_analizadas not in caminos_evaluados:
                                        if col==bc and conexion==True:                              #si encontramos la banda de destino con conexion se cierra el salto
                                            alcanzado=True
                                            caminos_evaluados.append(bandas_analizadas)
                                            camino_potencial.append(bc)
                                            caminos_validos.append(camino_potencial)
                                            
                                            break
                                        else:
                                            if conexion==True and col not in bandas_analizadas:     #si hace conexion y es la primera vez que se va por esa banda, para evitar retornos circulares
                                                b_presalto=ba
                                                bandas_analizadas.append(col)                       #se registra que se esta analizando este camino
                                                ba=col                                              #se actualiza la banda de la que se tienen que analizar las conexiones directas                    
                                                camino_potencial.append(col)
                                                salto=True
                                                break
                                            else:
                                                col=col+1                                           #si no se cumple se busca en la banda siguiente
    
                                if salto==False: #si se pasan todas las bandas de la fila en la matriz y no hay camino valido (porque ya se han recorrido o porque no se permite)
                                    if ba != b:
                                        matriz_b_bc[b_presalto,ba]=False #se cierra el camino en la banda previa para que al volver no se vuelva a meter por ahi
                                        break #se sale del while aunque no se haya alcanzado de nuevo un camino valido
                                    else:
                                        alcanzado_por_todos_caminos_posibles=True #el bucle está hecho para que se vayan evitando repeticiones parando antes en un nivel superior, si se llega al nivel inicial ba=b es porque se han agotado las iteraciones (no puede haber conexiones directas porque estamos analizando los casos en los que ya se han agotado)
                                        break #se sale del while aunque no se haya alcanzado de nuevo un camino valido
                        #obtenidos los caminos validos en la combinacion b, bc, nos quedamos con los de longitud minima y de ellos con el que tenga menos distancia de saltos
                        if caminos_validos != []:
                            long_cam_min=min(len(cam) for cam in caminos_validos)
                            cam_min_pot = [cam for cam in caminos_validos if len(cam)==long_cam_min]
                            min_dist_cam=10000
                            for cam in cam_min_pot:
                                dist_cam=0
                                c_anterior=cam[0]
                                for c in cam[1:]:
                                    n_min=np.nanargmin(puente[i,c_anterior,c,:,0])
                                    dist_cam=dist_cam+puente[i,c_anterior,c,n_min,0]
                                    c_anterior=c
                                if dist_cam < min_dist_cam:
                                    cam_min=cam
                        #hemos obtenido el camino minimo en una relacion b-bc exitosa, ahora hay que hacer balances locales en cada bloque del camino para ver los intercambios ocultos
                            comb_modif=np.copy(comb)
                            primer_signo=[]
                            for c in cam_min:
                                desbalance_minimo=min(abs(comb[b,-1]),abs(comb[bc,-1])) #no se pueden intercambiar mas del minimo desbalance que haya en el camino (si fuesen necesarias varias bandas pdoria haber un desbalance mayor que el que ese camino pudiese aportar y descuadraria)
                               
                                if c == cam_min[0] or c == cam_min[-1]: #si estamos en un extremo del intercambio
                                    if comb[c,-1] < 0:
                                        comb_modif[c,-1]=comb_modif[c,-1]+desbalance_minimo
                                        ganancias_perdidas[gp,c,0]=ganancias_perdidas[gp,c,0]-desbalance_minimo
                                            
                                    elif comb[c,-1] > 0:
                                        comb_modif[c,-1]=comb_modif[c,-1]-desbalance_minimo
                                        ganancias_perdidas[gp,c,1]=ganancias_perdidas[gp,c,1]+desbalance_minimo
                                        
                                else: #si estamos en una banda puente
                                    ganancias_perdidas[gp,c,0]=ganancias_perdidas[gp,c,0]-desbalance_minimo
                                    ganancias_perdidas[gp,c,1]=ganancias_perdidas[gp,c,1]+desbalance_minimo
                                
                                
                                if c == cam_min[0]:
                                    if comb[c,-1] < 0:
                                       matriz_intercambio[i,gp,c,cam_min[1]]=matriz_intercambio[i,gp,c,cam_min[1]]-desbalance_minimo
                                       primer_signo ='ganar' #si la banda de inicio, que va en el camino "hacia adelante" (c -> cam[1]")  gana strings, el resto de movimientos "hacia atrás" deben de ser cediendo strings y al contrario
                                    else:
                                       matriz_intercambio[i,gp,c,cam_min[1]]=matriz_intercambio[i,gp,c,cam_min[1]]+desbalance_minimo
                                       primer_signo ='ceder'
                                                                    
                                else:
                                    if c == cam_min[-1]:
                                        if  primer_signo == 'ganar': 
                                            matriz_intercambio[i,gp,c,cam_min[cam_min.index(c)-1]]=matriz_intercambio[i,gp,c,cam_min[cam_min.index(c)-1]]+desbalance_minimo
                                        else:
                                            matriz_intercambio[i,gp,c,cam_min[cam_min.index(c)-1]]=matriz_intercambio[i,gp,c,cam_min[cam_min.index(c)-1]]-desbalance_minimo

                                    else:
                                        if  primer_signo == 'ganar':
                                            matriz_intercambio[i,gp,c,cam_min[cam_min.index(c)-1]]=matriz_intercambio[i,gp,c,cam_min[cam_min.index(c)-1]]+desbalance_minimo
                                            matriz_intercambio[i,gp,c,cam_min[cam_min.index(c)+1]]=matriz_intercambio[i,gp,c,cam_min[cam_min.index(c)+1]]-desbalance_minimo
                                        else:
                                            matriz_intercambio[i,gp,c,cam_min[cam_min.index(c)-1]]=matriz_intercambio[i,gp,c,cam_min[cam_min.index(c)-1]]-desbalance_minimo
                                            matriz_intercambio[i,gp,c,cam_min[cam_min.index(c)+1]]=matriz_intercambio[i,gp,c,cam_min[cam_min.index(c)+1]]+desbalance_minimo

                            
                            comb=comb_modif #actualizamos comb para el siguiente analisis b-bc por si no se ha completado la banda
            
            potential_combinations[gp]=comb            
            gp=gp+1
        
        #HABIENDO CALCULADO LOS INTERCAMBIOS REALES DE STRINGS EN LAS COMBINACIONES, NOS QUEDAMOS CON LA COMBINACION QUE MENOS TENGA - POSIBLE OPTIMIZAR COGIENDO LAS 3 O 4 MEJORES PARA VER DIFERENTES VALIDAS
        min_int=1000
        gp=0
        for comb_gp in ganancias_perdidas:
            intercambios_strings_def=np.sum(abs(comb_gp))
            if intercambios_strings_def < min_int:
                comb_gp_optima=comb_gp
                min_int=intercambios_strings_def
                comb_optima=potential_combinations[gp,:,:-1]
                gp_optima=gp
            gp=gp+1
            
        combinacion_optima.append(comb_optima)
        ganancias_perdidas_optima.append(comb_gp_optima)
        matriz_intercambios_optima.append(matriz_intercambio[i,gp_optima])
    #Creamos una matriz que recoja el nº de strings que intercambia cada banda con las otras en la configuracion optima
    
    
    #ponemos en formato array con el i empezando en uno    
    combinacion_optima=np.concatenate((np.zeros((1,)+np.array(combinacion_optima).shape[1:]),np.array(combinacion_optima)),axis=0)
    ganancias_perdidas_optima=np.concatenate((np.zeros((1,)+np.array(ganancias_perdidas_optima).shape[1:]),np.array(ganancias_perdidas_optima)),axis=0)
    matriz_intercambios_optima=np.concatenate((np.zeros((1,)+np.array(matriz_intercambios_optima).shape[1:]),np.array(matriz_intercambios_optima)),axis=0)
    
    return [combinacion_optima , ganancias_perdidas_optima , matriz_intercambios_optima, puente]



def strings_mas_proximos_a_puente(pc, puentes_minimos, strings_fisicos, i, b, bc, puntos_excluidos=set(), puntos_usados_global=set()):
    mejor_suma_distancias = np.inf
    mejor_puente = None
    mejores_puntos = None

    for puente in puentes_minimos:
        x_puente_ceder = puente[1]
        y_puente_ceder = puente[2]

        # Selección de los strings disponibles en la banda b
        mascara = ~np.isnan(strings_fisicos[i, b, :, :, 0])
        indices_validos = np.argwhere(mascara)
        indices_validos = [tuple(idx) for idx in indices_validos 
                            if (idx[0], idx[1]) not in puntos_excluidos 
                            and (b, idx[0], idx[1]) not in puntos_usados_global]

        if len(indices_validos) < pc:
            continue  # No hay suficientes strings para este puente

        # Cálculo de distancias a este puente
        coords = np.array([np.linalg.norm(strings_fisicos[i, b, idx[0], idx[1], :2] - np.array([x_puente_ceder, y_puente_ceder]))
                           for idx in indices_validos])

        indices_ordenados = np.argsort(coords)[:pc]
        puntos_mas_cercanos = [indices_validos[idx] for idx in indices_ordenados]
        suma_distancias = np.sum(coords[indices_ordenados])

        if suma_distancias < mejor_suma_distancias:
            mejor_suma_distancias = suma_distancias
            mejor_puente = puente
            mejores_puntos = puntos_mas_cercanos

    return mejor_puente, mejores_puntos







def strings_mas_proximos_a_puente_por_filas(pc, puentes_minimos, strings_fisicos, i, b, bc, puntos_excluidos=set(), puntos_usados_global=set()):
    mejor_suma_distancias = np.inf
    mejor_puente = None
    mejores_puntos = None

    num_filas = strings_fisicos.shape[2]
    num_strings = strings_fisicos.shape[3]

    for puente in puentes_minimos:
        x_puente = puente[1]
        y_puente = puente[2]

        distancias_fila = []
        for f in range(num_filas):
            mascara_fila = ~np.isnan(strings_fisicos[i, b, f, :, 0])
            if not np.any(mascara_fila):
                continue

            coords_fila = strings_fisicos[i, b, f, mascara_fila, :2]
            distancia_media_fila = np.mean(np.linalg.norm(coords_fila - np.array([x_puente, y_puente]), axis=1))
            distancias_fila.append((f, distancia_media_fila))

        filas_ordenadas = [f for f, _ in sorted(distancias_fila, key=lambda x: x[1])]

        puntos_seleccionados = []
        for f in filas_ordenadas:
            puntos_fila = []
            for s in range(num_strings):
                if np.isnan(strings_fisicos[i, b, f, s, 0]):
                    continue
                if (f, s) in puntos_excluidos or (b, f, s) in puntos_usados_global:
                    continue
                puntos_fila.append((f, s))

            puntos_fila.sort(key=lambda fs: np.linalg.norm(strings_fisicos[i, b, fs[0], fs[1], :2] - np.array([x_puente, y_puente])))

            for fs in puntos_fila:
                if len(puntos_seleccionados) >= pc:
                    break
                puntos_seleccionados.append(fs)

            if len(puntos_seleccionados) >= pc:
                break

        if len(puntos_seleccionados) < pc:
            continue

        # Evaluamos la suma de distancias de los puntos seleccionados en esta iteración
        suma_dist = np.sum([
            np.linalg.norm(strings_fisicos[i, b, f, s, :2] - np.array([x_puente, y_puente]))
            for (f, s) in puntos_seleccionados
        ])

        if suma_dist < mejor_suma_distancias:
            mejor_suma_distancias = suma_dist
            mejor_puente = puente
            mejores_puntos = puntos_seleccionados

    return mejor_puente, mejores_puntos









def intercambio_strings_por_proximidad_a_puente(
    bloque_inicial, n_bloques, max_b, max_f_str_b, max_tpf,
    strings_fisicos, matriz_intercambios_optima, puente, criterio_ceder_strings, 
    puntos_usados_global, orientacion
):
    """
    Selecciona los strings a intercambiar entre bandas, eligiendo los strings más próximos al puente de conexión.
    """

    almacen_strings = [
        [[[] for _ in range(max_b)] for _ in range(max_b)] 
        for _ in range(n_bloques + 1)
    ]
    puntos_usados_banda = [
        [set() for _ in range(max_b)] 
        for _ in range(n_bloques + 1)
    ]

    for i in range(bloque_inicial, n_bloques + 1):
        for b in range(max_b):
            for bc in range(max_b):
                
                n_str_inter = int(matriz_intercambios_optima[i, b, bc])
                if n_str_inter <= 0:
                    continue

                valid_rows = ~np.isnan(puente[i, b, bc, :, 0])
                if not np.any(valid_rows):
                    continue

                # Seleccionamos todos los puentes mínimos (todos los que esten dentro de la distancia minima mas una tolerancia de +5m para dar flexibilidad)
                min_val = np.nanmin(puente[i, b, bc, valid_rows, 0])
                puentes_minimos = puente[i, b, bc][(puente[i, b, bc, :, 0] < min_val + 5) & valid_rows]

                # Elegimos función según el criterio
                if criterio_ceder_strings == 'Rows':
                    mejor_puente, strings_a_ceder = strings_mas_proximos_a_puente_por_filas(
                        n_str_inter, puentes_minimos, strings_fisicos, i, b, bc,
                        puntos_usados_banda[i][b], puntos_usados_global[i]
                    )
                else:
                    mejor_puente, strings_a_ceder = strings_mas_proximos_a_puente(
                        n_str_inter, puentes_minimos, strings_fisicos, i, b, bc,
                        puntos_usados_banda[i][b], puntos_usados_global[i]
                    )

                # Si no se consiguen suficientes strings para ceder, omitimos este intercambio (caso extremo)
                if strings_a_ceder is None or len(strings_a_ceder) < n_str_inter:
                    print(f"Advertencia: No se pudo completar el intercambio {n_str_inter} de {b} a {bc} en bloque {i}")
                    continue

                # Guardamos los strings seleccionados
                grupo = [(b, f, s) for (f, s) in strings_a_ceder]
                almacen_strings[i][b][bc].append((grupo, mejor_puente))


                # Actualizamos los puntos usados (localmente y globalmente)
                puntos_usados_banda[i][b].update((f, s) for (_, f, s) in grupo)
                puntos_usados_global[i].update((b, f, s) for (_, f, s) in grupo)

    return almacen_strings







def asignar_strings_a_inversores(
    bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, strings_fisicos, conf_inversores,
    combinacion_optima, almacen_strings, ori_str_ID, orientacion, puntos_usados_global,
    criterio_ceder_strings, puente
):

    max_inv_block = int(np.max(np.sum(conf_inversores[1:], axis=1)))
    max_inv = int(np.max(np.sum(conf_inversores[1:], axis=1)))
    max_str_pinv = int(np.max(conf_inversores[0]))

    inv_string = np.full((n_bloques + 1, max_b, max_inv + 1, max_str_pinv + 1, 4), np.nan)
    equi_ibv_to_fs = np.full((n_bloques + 1, max_b, max_inv + 1, max_str_pinv + 1, 3), np.nan)

    for i in range(bloque_inicial, n_bloques + 1):
        grupos_transferidos = dict()
        for b in range(max_b):
            for bc in range(max_b):
                for grupo, puente_usado in almacen_strings[i][b][bc]:  
                    grupos_transferidos.setdefault((i, bc), []).append((grupo, puente_usado))

        for b in range(max_b):
            capacidades = conf_inversores[0]
            cantidades = combinacion_optima[i, b].copy()
            tipo_idx = 0
            inv_idx = 1
            str_idx = 1

            def avanzar_tipo(idx):
                while idx < len(cantidades) and cantidades[idx] == 0:
                    idx += 1
                return idx if idx < len(cantidades) else None

            tipo_idx = avanzar_tipo(tipo_idx)
            if tipo_idx is None:
                continue

            grupo_transferido = grupos_transferidos.get((i, b), [])

            # Primero asignamos strings transferidos
            for grupo, puente_usado in grupo_transferido:
                for b_ced, f_ced, s_ced in grupo:
                    if np.isnan(strings_fisicos[i, b_ced, f_ced, s_ced, 0]):
                        continue

                    inv_string[i, b, inv_idx, str_idx, 0:3] = strings_fisicos[i, b_ced, f_ced, s_ced]
                    inv_string[i, b, inv_idx, str_idx, 3] = 0
                    equi_ibv_to_fs[i, b, inv_idx, str_idx] = [b_ced, f_ced, s_ced]
                    puntos_usados_global[i].add((b_ced, f_ced, s_ced))

                    ID_global = int(strings_fisicos[i, b_ced, f_ced, s_ced, 2])
                    ori_str_ID[ID_global][0] = b

                    str_idx += 1
                    if str_idx > capacidades[tipo_idx]:
                        cantidades[tipo_idx] -= 1
                        inv_idx += 1
                        str_idx = 1
                        tipo_idx = avanzar_tipo(tipo_idx)
                        if tipo_idx is None:
                            break

                if tipo_idx is None:
                    continue

                n_restantes = capacidades[tipo_idx] - (str_idx - 1)

                puntos_usados_banda_receptora = set()
                for inv_tmp in range(1, max_inv + 1):
                    for s_tmp in range(1, max_str_pinv + 1):
                        if not np.isnan(equi_ibv_to_fs[i, b, inv_tmp, s_tmp, 0]):
                            _, f_used, s_used = equi_ibv_to_fs[i, b, inv_tmp, s_tmp]
                            puntos_usados_banda_receptora.add((f_used, s_used))

                if criterio_ceder_strings == 'Rows':
                    _, strings_a_usar = strings_mas_proximos_a_puente_por_filas(
                        n_restantes, [puente_usado], strings_fisicos, i, b, b,
                        puntos_usados_banda_receptora, puntos_usados_global[i]
                    )
                else:
                    _, strings_a_usar = strings_mas_proximos_a_puente(
                        n_restantes, [puente_usado], strings_fisicos, i, b, b,
                        puntos_usados_banda_receptora, puntos_usados_global[i]
                    )

                if strings_a_usar is None or len(strings_a_usar) < n_restantes:
                    print(f"Advertencia: No hay suficientes strings en banda {b} para completar inversor en bloque {i}")
                    continue

                for f_local, s_local in strings_a_usar:
                    inv_string[i, b, inv_idx, str_idx, 0:3] = strings_fisicos[i, b, f_local, s_local]
                    inv_string[i, b, inv_idx, str_idx, 3] = 0
                    equi_ibv_to_fs[i, b, inv_idx, str_idx] = [b, f_local, s_local]
                    puntos_usados_global[i].add((b, f_local, s_local))
                    puntos_usados_banda_receptora.add((f_local, s_local))

                    str_idx += 1
                    if str_idx > capacidades[tipo_idx]:
                        cantidades[tipo_idx] -= 1
                        inv_idx += 1
                        str_idx = 1
                        tipo_idx = avanzar_tipo(tipo_idx)
                        if tipo_idx is None:
                            break

            if tipo_idx is None:
                continue

            # Finalmente asignamos los locales normales
            puntos_usados_banda = set()

            while tipo_idx is not None:
                n_restantes = capacidades[tipo_idx] - (str_idx - 1)

                strings_a_usar = []
                for f in range(max_f_str_b):
                    for s in range(max_spf):
                        if len(strings_a_usar) >= n_restantes:
                            break
                        if np.isnan(strings_fisicos[i, b, f, s, 0]):
                            continue
                        if (b, f, s) in puntos_usados_global[i] or (f, s) in puntos_usados_banda:
                            continue
                        strings_a_usar.append((f, s))
                    if len(strings_a_usar) >= n_restantes:
                        break

                if not strings_a_usar:
                    break

                for f_local, s_local in strings_a_usar:
                    inv_string[i, b, inv_idx, str_idx, 0:3] = strings_fisicos[i, b, f_local, s_local]
                    inv_string[i, b, inv_idx, str_idx, 3] = 0
                    equi_ibv_to_fs[i, b, inv_idx, str_idx] = [b, f_local, s_local]
                    puntos_usados_global[i].add((b, f_local, s_local))
                    puntos_usados_banda.add((f_local, s_local))

                    str_idx += 1
                    if str_idx > capacidades[tipo_idx]:
                        cantidades[tipo_idx] -= 1
                        inv_idx += 1
                        str_idx = 1
                        tipo_idx = avanzar_tipo(tipo_idx)
                        if tipo_idx is None:
                            break

    return inv_string, max_inv, max_inv_block, max_str_pinv, equi_ibv_to_fs




def aplicar_flip_strings(
    bloque_inicial, n_bloques, max_b, max_inv, max_str_pinv,
    equi_ibv_to_fs, ori_str_ID, orientacion, strings_fisicos
):
    """
    Aplica el flip de orientación a los strings de los inversores compartidos,
    tras haberse asignado todos los strings.
    """

    for i in range(bloque_inicial, n_bloques + 1):
        for b in range(max_b):
            for inv_idx in range(1, max_inv + 1):

                # Extraemos las bandas de todos los strings de este inversor
                bandas_involucradas = set()
                strings_por_banda = dict()

                for s_idx in range(1, max_str_pinv + 1):
                    if np.isnan(equi_ibv_to_fs[i, b, inv_idx, s_idx, 0]):
                        continue

                    b_ced, f_ced, s_ced = equi_ibv_to_fs[i, b, inv_idx, s_idx].astype(int)
                    bandas_involucradas.add(b_ced)
                    strings_por_banda.setdefault(b_ced, []).append((s_idx, f_ced, s_ced))


                if len(bandas_involucradas) < 1:
                    #datos vacios de inv, todo np.nan
                    continue
                
                elif len(bandas_involucradas) == 1:               
                    banda = next(iter(bandas_involucradas))
                    # Inversor local: todos los strings tienen la orientacion de la banda
                    for s_idx, f_ced, s_ced in strings_por_banda[banda]:
                        ID_global = int(strings_fisicos[i, banda, f_ced, s_ced, 2])

                        # Unificamos la orientación
                        ori_str_ID[ID_global][1] = 'S' if orientacion[i,banda] == 'S' else 'N'
                    continue
                
                # Detectamos si es un compartido S-S o N-N
                b1, b2 = sorted(bandas_involucradas)
                ori_b1 = orientacion[i, b1]
                ori_b2 = orientacion[i, b2]

                if ori_b1 != ori_b2:
                    # Orientaciones distintas: no hay flip
                    continue

                # Determinamos la banda que requiere flip
                if ori_b1 == 'S':
                    banda_a_girar = b2  # mayor índice
                elif ori_b1 == 'N':
                    banda_a_girar = b1  # menor índice
                else:
                    banda_a_girar = None

                # Aplicamos el flip solo a los strings de la banda a girar
                if banda_a_girar is not None:
                    for s_idx, f_ced, s_ced in strings_por_banda[banda_a_girar]:
                        ID_global = int(strings_fisicos[i, banda_a_girar, f_ced, s_ced, 2])
                        orientacion_origen = orientacion[i, banda_a_girar]

                        # Giramos la orientación
                        ori_str_ID[ID_global][1] = 'S' if orientacion_origen == 'N' else 'N'

    return ori_str_ID


def posicion_inv_string(
    inv_string,
    strings_fisicos,
    sep_caja_tracker,
    coord_PCS_DC_inputs,
    contorno_bandas,
    Posicion_optima_caja,
    equi_ibv_to_fs,
    orientacion,
    almacen_strings
):
    n_bloques, max_b, max_inv, max_str, _ = inv_string.shape
    posiciones = np.full((n_bloques, max_b, max_inv, 4), np.nan)
    comienzo_fila = np.full((n_bloques, max_b, max_inv, max_str, 3), np.nan)


    for i in range(n_bloques):
        for b in range(max_b):
            for inv in range(1, max_inv):
                coords = inv_string[i, b, inv, 1:, :2]
                ids = inv_string[i, b, inv, 1:, 2]
                valid_idx = ~np.isnan(coords[:, 0])
                coords = coords[valid_idx]
                ids = ids[valid_idx]
                if coords.size == 0:
                    continue

                filas, str_por_fila, bandas_origen = {}, {}, []
                b_cedente = None

                for s_local, (coord, sid) in enumerate(zip(coords, ids), start=1):
                    b_fisico, f_fisico, s_fisico = equi_ibv_to_fs[i, b, inv, s_local]

                    if not np.isnan(b_fisico):
                        comienzo_fila[i, b, inv, s_local] = [
                            strings_fisicos[i, int(b_fisico), int(f_fisico), 0, 0],
                            strings_fisicos[i, int(b_fisico), int(f_fisico), 0, 1],
                            sid
                        ]

                        str_coord = strings_fisicos[i, int(b_fisico), int(f_fisico), int(s_fisico), :2]
                        filas.setdefault(f_fisico, []).append((str_coord, sid))
                        str_por_fila[f_fisico] = str_por_fila.get(f_fisico, 0) + 1
                        bandas_origen.append(int(b_fisico))

                        if int(b_fisico) != b:
                            b_cedente = int(b_fisico)

                if len(filas) == 0:
                    continue

                bandas_unicas, counts = np.unique(bandas_origen, return_counts=True)
                    
                # CASO COMPARTIDO
                if len(bandas_unicas) > 1:
                    puente_usado = None
                    if b_cedente is not None and len(almacen_strings[i][b_cedente][b]) > 0:
                        grupo, puente_tmp = almacen_strings[i][b_cedente][b][0]
                        puente_usado = puente_tmp
                    elif b_cedente is not None and len(almacen_strings[i][b][b_cedente]) > 0:
                        grupo, puente_tmp = almacen_strings[i][b][b_cedente][0]
                        puente_usado = puente_tmp

                    # #Inversor en posicion de banda invertida
                    # if orientacion[i,b]=='N':
                    #     if orientacion[i,b_cedente]=='N':
                    #         pos_ori_inv = 'S'
                    #     else:
                            # pos_ori_inv = 
                    
                    #Determinar posicion
                    if puente_usado is not None:
                        x_caja = puente_usado[1]
                        y_caja = puente_usado[2] + sep_caja_tracker 
                        posiciones[i, b, inv] = [x_caja, y_caja, np.nan, np.nan]
                    else:
                        posiciones[i, b, inv] = [np.nan, np.nan, np.nan, np.nan]

                # CASO LOCAL (aquí la restricción buena)
                else:
                    banda_fisica = bandas_unicas[0]
                    filas_banda_fisica = filas

                    filas_validas = []
                    for f in filas_banda_fisica:
                        sid_cabecera = strings_fisicos[i, banda_fisica, int(f), 0, 2]
                        if sid_cabecera in ids:
                            filas_validas.append(f)

                    filas_ordenadas = sorted(filas_validas if filas_validas else filas_banda_fisica.keys())

                    x_filas = np.array([np.mean([pt[0] for pt, _ in filas_banda_fisica[f]]) for f in filas_ordenadas])
                    y_filas = np.array([np.mean([pt[1] for pt, _ in filas_banda_fisica[f]]) for f in filas_ordenadas])
                    str_fila = np.array([str_por_fila[f] for f in filas_ordenadas])

                    if Posicion_optima_caja == 'Center':
                        distancia_total = np.zeros(len(x_filas))
                        for f_idx in range(len(x_filas)):
                            dist = np.sqrt((x_filas - x_filas[f_idx])**2 + (y_filas - y_filas[f_idx])**2)
                            distancia_total[f_idx] = np.sum(dist * str_fila)
                        idx_caja = np.argmin(distancia_total)
                    elif Posicion_optima_caja == 'Edge':
                        ref_x = coord_PCS_DC_inputs[i, 0]
                        idx_caja = np.argmin(np.abs(x_filas - ref_x))
                    else:
                        raise ValueError("Posicion_optima_caja debe ser 'Center' o 'Edge'.")

                    fila_seleccionada = filas_ordenadas[idx_caja]
                    puntos_fila = np.array([pt for pt, _ in filas_banda_fisica[fila_seleccionada]])
                    x_caja = np.min(puntos_fila[:, 0])
                    ori = orientacion[i, banda_fisica]

                    if ori == 'S':
                        y_caja = np.min(puntos_fila[:, 1]) - sep_caja_tracker
                    elif ori == 'N':
                        y_caja = np.max(puntos_fila[:, 1]) + sep_caja_tracker
                    else:
                        y_caja = np.mean(puntos_fila[:, 1]) + sep_caja_tracker

                    posiciones[i, b, inv] = [x_caja, y_caja, np.nan, np.nan]

    return posiciones, comienzo_fila




    
def repartir_inversores_en_dos_cuadros(inv_string, coord_PCS_DC_inputs, lim_str_dif, bloque_inicial, n_bloques, max_b, max_inv, max_str_pinv):
    """
    Reparte los inversores en dos cuadros (izquierda y derecha de la PCS) y balancea en caso de desequilibrio.
    """
    
    # Función auxiliar para rebalanceo
    def rebalancear(origen, destino, code_origen, code_destino, dif_izq_der):
        inv_origen = np.array(origen)
        # Ordenamos por distancia al centro
        distancias = np.abs(inv_string[i, inv_origen[:, 0], inv_origen[:, 1], 0, 0] - coord_PCS_DC_inputs[i, 0])
        orden = np.argsort(distancias)
        inv_origen = inv_origen[orden]
        
        for b, v in inv_origen:
            for s in range(1, max_str_pinv+1):
                if ~np.isnan(inv_string[i, b, v, s, 3]):
                    inv_string[i, b, v, s, 3] = code_destino
                
            nonlocal strings_izq, strings_der
            strings_izq = np.sum(inv_string[i, ..., 3] == 1)
            strings_der = np.sum(inv_string[i, ..., 3] == 2)

            if abs(strings_izq - strings_der) <= lim_str_dif or np.sign(dif_izq_der) != np.sign(strings_izq - strings_der):
                break


    #Flujo principal
    for i in range(bloque_inicial, n_bloques + 1):
        inv_izq = []
        inv_der = []

        for b in range(max_b):
            for v in range(max_inv):
                if not np.isnan(inv_string[i, b, v, 0, 0]):
                    x_pos = inv_string[i, b, v, 0, 0]
                    if x_pos <= coord_PCS_DC_inputs[i, 0]:
                        for s in range(1, max_str_pinv+1):
                            if ~np.isnan(inv_string[i, b, v, s, 3]):
                                inv_string[i, b, v, s, 3] = 1
                        inv_izq.append((b, v))
                    else:
                        for s in range(1, max_str_pinv+1):
                            if ~np.isnan(inv_string[i, b, v, s, 3]):
                                inv_string[i, b, v, s, 3] = 2
                        inv_der.append((b, v))

        # Calculamos strings totales por cuadro
        strings_izq = np.sum(inv_string[i, ..., 3] == 1)
        strings_der = np.sum(inv_string[i, ..., 3] == 2)


        # Rebalanceamos si es necesario
        if strings_izq - strings_der > lim_str_dif:
            dif_izq_der = strings_izq - strings_der
            rebalancear(inv_izq, inv_der, 1, 2, dif_izq_der)
            
        elif strings_der - strings_izq > lim_str_dif:
            dif_izq_der = strings_izq - strings_der
            rebalancear(inv_der, inv_izq, 2, 1, dif_izq_der)

    return inv_string





def ID_strings_e_inv_string(
    bloque_inicial, n_bloques, max_b, max_inv, max_inv_block, max_str_pinv,
    inv_string, dos_inv, equi_ibv_to_fs, strings_fisicos, dist_ext_opuesto_str, ori_str_ID, orientacion
):
    """
    Asigna IDs finales a inversores y strings, generando los mapas de equivalencia necesarios.
    """

    #----FASE PREVIA---
    # Reordenar strings segun criterio similar a inv con power stations
    for i in range(bloque_inicial, n_bloques + 1):
        for b in range(0, max_b):
            if ~np.isnan(inv_string[i, b, 1, 0, 0]):
                for inv in range(1, max_inv + 1):
                    if ~np.isnan(inv_string[i, b, inv, 0, 0]):
                        # subset de strings (ignoramos fila 0, trabajamos en 1:)                       
                        subset = inv_string[i, b, inv, 1:, :]
                        mask = ~np.isnan(subset[:, 0]) & ~np.isnan(subset[:, 1]) & ~np.isnan(subset[:, 2])
                        subset_valid = subset[mask]
                        
                        sids = subset_valid[:, 2].astype(int)
                        orients = [ori_str_ID[sid] for sid in sids]

                        # separar indices N y S
                        idx_N = [k for k, o in enumerate(orients) if o[1] == 'N']
                        idx_S = [k for k, o in enumerate(orients) if o[1] == 'S']
        
                        # orden para S (X asc, Y asc)
                        if idx_S:
                            coords_S = subset[idx_S][:, [0,1]]
                            order_S = np.lexsort((coords_S[:,1], coords_S[:,0]))
                            idx_S_sorted = [idx_S[k] for k in order_S]
                        else:
                            idx_S_sorted = []
        
                        # orden para N (X desc, Y desc)
                        if idx_N:
                            coords_N = subset[idx_N][:, [0,1]]
                            order_N = np.lexsort((-coords_N[:,1], -coords_N[:,0]))
                            idx_N_sorted = [idx_N[k] for k in order_N]
                        else:
                            idx_N_sorted = []
        
                        # concatenar orden: primero S, luego N
                        idx_final = idx_S_sorted + idx_N_sorted
        
                        # aplicar el reordenamiento en la copia
                        inv_string[i, b, inv, 1:1+len(idx_final), :] = subset[idx_final]
                        
    # Actualizar equi_ibv_to_fs, que se usará después en la asignación
    equi_ibv_to_fs[:] = np.nan # Limpiar todas las equivalencias antes de recalcular
    
    for i in range(bloque_inicial, n_bloques + 1):
        for b in range(0, max_b):
            if ~np.isnan(inv_string[i, b, 1, 0, 0]):
                for inv in range(1, max_inv + 1):
                    if ~np.isnan(inv_string[i, b, inv, 0, 0]):
                        for s in range(1, max_str_pinv + 1):
                            if ~np.isnan(inv_string[i, b, inv, s, 0]):
                                sid_global = inv_string[i, b, inv, s, 2]
                                matches = np.argwhere(strings_fisicos[..., 2] == sid_global)
                                if matches.size > 0:
                                    i_sf, b_sf, f_sf, s_sf = matches[0]
                                    equi_ibv_to_fs[i, b, inv, s] = [b_sf, f_sf, s_sf]    
    
    
    #----ASIGNACION STRINGS IDS----
    strings_ID = np.full((n_bloques + 1, 3, max_inv_block + 1, max_str_pinv + 1, 6), np.nan, dtype=object)
    String_Inverters_ID = np.full((n_bloques + 1, 3, max_inv_block + 1, 4), np.nan, dtype=object)
    equi_ibv = np.full((n_bloques + 1, max_b, max_inv, 3), np.nan)
    equi_reverse_ibv = np.full((n_bloques + 1, 3, max_inv_block + 1, 3), np.nan)
    
    for i in range(bloque_inicial, n_bloques + 1):
        id_inv_local = 0
        inv_board_1 = 0
        inv_board_2 = 0

        for b in range(0,max_b):
            for v in range(1,max_inv+1):
                if np.isnan(inv_string[i, b, v, 0, 0]):
                    continue
                
                board = int(inv_string[i, b, v, 1, 3])
                
                if board == 0:
                    id_inv_local += 1
                elif board == 1:
                    inv_board_1 += 1
                    id_inv_local = inv_board_1
                elif board == 2:
                    inv_board_2 += 1
                    id_inv_local = inv_board_2                
                
                # ID de inversor
                if dos_inv:
                    String_Inverters_ID[i, board, id_inv_local, 0] = f"INV-{i}.{board}.{id_inv_local:02d}"
                else:
                    String_Inverters_ID[i, board, id_inv_local, 0] = f"INV-{i}.{id_inv_local:02d}"

                String_Inverters_ID[i, board, id_inv_local, 1] = inv_string[i, b, v, 0, 0]
                String_Inverters_ID[i, board, id_inv_local, 2] = inv_string[i, b, v, 0, 1]
                String_Inverters_ID[i, board, id_inv_local, 3] = np.count_nonzero(~np.isnan(inv_string[i, b, v, 1:, 0]))

                equi_ibv[i, b, v] = [i, board, id_inv_local]
                equi_reverse_ibv[i, board, id_inv_local] = [i, b, v]

                s_local_id = 0
                for s in range(1, max_str_pinv + 1):
                    if np.isnan(inv_string[i, b, v, s, 0]):
                        continue

                    s_local_id += 1
                    b_fisica, f_real, s_real = equi_ibv_to_fs[i, b, v, s].astype(int)
                    ID_global = int(strings_fisicos[i, b_fisica, f_real, s_real, 2])
                    orientacion_string = ori_str_ID[ID_global][1]
                    
                    if dos_inv:
                        string_id = f"S-{i}.{board}.{id_inv_local:02d}.{s_local_id:02d}"
                    else:
                        string_id = f"S-{i}.{id_inv_local:02d}.{s_local_id:02d}"

                    strings_ID[i, board, id_inv_local, s_local_id, 0] = string_id

                    x = strings_fisicos[i, b_fisica, f_real, s_real, 0]
                    y = strings_fisicos[i, b_fisica, f_real, s_real, 1]
                    dist_opuesta = dist_ext_opuesto_str[i, b_fisica, f_real, s_real]

                    if orientacion[i,b_fisica]=='N':
                        if orientacion_string == 'N':
                            y_inicio, y_fin = y - dist_opuesta, y
                        elif orientacion_string == 'S':
                            y_inicio, y_fin = y, y - dist_opuesta
                        else:
                            y_inicio, y_fin = np.nan, np.nan
                            
                    if orientacion[i,b_fisica]=='S':
                        if orientacion_string == 'N':
                            y_inicio, y_fin = y, y + dist_opuesta
                        elif orientacion_string == 'S':
                            y_inicio, y_fin = y + dist_opuesta, y
                        else:
                            y_inicio, y_fin = np.nan, np.nan
                    # if orientacion_string == 'N':
                    #     y_inicio, y_fin = y - dist_opuesta, y
                    # elif orientacion_string == 'S':
                    #     y_inicio, y_fin = y + dist_opuesta, y
                    # else:
                    #     y_inicio, y_fin = np.nan, np.nan
                            
                            
                    strings_ID[i, board, id_inv_local, s_local_id, 1] = x
                    strings_ID[i, board, id_inv_local, s_local_id, 2] = y_inicio
                    strings_ID[i, board, id_inv_local, s_local_id, 3] = y_fin
                    strings_ID[i, board, id_inv_local, s_local_id, 4] = ID_global
                    y_medio = (y_inicio + y_fin)/2
                    strings_ID[i, board, id_inv_local, s_local_id, 5] = y_medio
              
    return strings_ID, String_Inverters_ID, equi_ibv, equi_reverse_ibv, inv_string, equi_ibv_to_fs


    


def reconstruir_almacen_strings_y_puentes(
    inv_string, strings_fisicos, contorno_bandas,
    bloque_inicial, n_bloques, max_b, max_inv, max_str_pinv
):
    """
    A partir de inv_string modificado, detecta qué strings han cambiado de banda (usando strings_fisicos)
    y calcula dinámicamente el punto de puente óptimo para cada intercambio real,
    usando solo los puntos de contorno cercanos a los strings involucrados.
    Devuelve: almacen_strings[i][b_orig][b_dest] = [(grupo, mejor_puente)]
    """


    def calcular_puente_minimo_desde_strings(contorno_b, contorno_bc, strings):
        mejor_puente = None
        min_distancia = np.inf

        puntos_b_validos = [p for p in contorno_b if not np.isnan(p).any()]
        puntos_bc_validos = [p for p in contorno_bc if not np.isnan(p).any()]

        for p in puntos_b_validos:
            for pc in puntos_bc_validos:
                distancia = np.linalg.norm(p[:2] - pc[:2])

                suma_dists = sum(
                    np.linalg.norm(np.array([x, y]) - p[:2]) +
                    np.linalg.norm(np.array([x, y]) - pc[:2])
                    for (_, _, x, y) in strings
                )

                if suma_dists < min_distancia:
                    min_distancia = suma_dists
                    mejor_puente = [distancia, *p[:2], *pc[:2]]

        return mejor_puente

    almacen_strings = [
        [[[] for _ in range(max_b)] for _ in range(max_b)]
        for _ in range(n_bloques + 1)
    ]

    movimientos = defaultdict(list)  # clave: (i, b_orig, b_dest) → [(inv, s, x, y)]

    for i in range(bloque_inicial, n_bloques + 1):
        for b_actual in range(max_b):
            for inv in range(len(inv_string[i][b_actual])):
                for s in range(len(inv_string[i][b_actual][inv])):
                    try:
                        x, y, sid, _ = inv_string[i][b_actual][inv][s]
                    except (IndexError, ValueError):
                        continue

                    if np.isnan(sid):
                        continue

                    # Obtener la banda original desde strings_fisicos
                    matches = np.argwhere(strings_fisicos[..., 2] == sid)
                    if matches.size == 0:
                        continue
                    i_sf, b_sf, f_sf, s_sf = matches[0]
                    b_orig = int(b_sf)

                    if b_orig == b_actual:
                        continue  # No hubo intercambio

                    movimientos[(i, b_orig, b_actual)].append((inv, s, x, y))

    # Calcular puentes para cada intercambio real
    for (i, b_orig, b_dest), strings in movimientos.items():
        contorno_b = contorno_bandas[i, b_orig]
        contorno_bc = contorno_bandas[i, b_dest]

        mejor_puente = calcular_puente_minimo_desde_strings(
            contorno_b, contorno_bc, strings
        )

        if mejor_puente is not None:
            grupo = [(b_orig, inv, s) for (inv, s, _, _) in strings]
            almacen_strings[i][b_orig][b_dest].append((grupo, mejor_puente))

    return almacen_strings



def obtener_filas_en_inv_como_filas_en_cajas(bloque_inicial, n_bloques, max_b, max_f_str_b, strings_fisicos):

    filas_en_inv_como_filas_en_cajas = np.full((n_bloques+1, max_b+1, max_f_str_b+1, 4), np.nan)

    for i in range(bloque_inicial, n_bloques+1):
        for b in range(0, max_b+1):
            if ~np.isnan(strings_fisicos[i, b, 0, 0, 0]): #si la banda no está vacia
                for f in range(0, max_f_str_b):
                    if ~np.isnan(strings_fisicos[i, b, f, 0, 0]): #si la fila no está vacia
                        # strings_en_fila = int(np.count_nonzero(~np.isnan(strings_fisicos[i, b, f, :, 0]))) #este parametro da igual porque no se va a usar para la construccion del array, se deja como para cajas                      
                        filas_en_inv_como_filas_en_cajas[i, b, f, 0] = 99 #aqui vendria "c", para la construccion del array este parametro solo se usa como contador diferente de nan, por lo que se va a fijar a 99
                        filas_en_inv_como_filas_en_cajas[i, b, f, 1] = 99 # aqui vendria "strings_en_fila" este parametro da igual porque no se va a usar para la construccion del array, por lo que se va a fijar en 99
                        filas_en_inv_como_filas_en_cajas[i, b, f, 2] = strings_fisicos[i, b, f, 0, 0]
                        filas_en_inv_como_filas_en_cajas[i, b, f, 3] = strings_fisicos[i, b, f, 0, 1]
    
    return filas_en_inv_como_filas_en_cajas

def obtener_inv_fisicos(bloque_inicial, n_bloques, max_b, max_inv, inv_string):
    "Equivalente a variable cajas_fisicas necesaria para poder reutilizar todas las funciones de calculo de array"
    inv_fisicos = np.full((n_bloques+1, max_b+1, max_inv, 4), np.nan) #el primer elemento es el numero de strings, el segundo la x, el tercero la y, el cuarto el inversor al que se asocia, que se define despues de esta funcion
    for i in range(bloque_inicial, n_bloques+1):
        for b in range(0, max_b):
            if ~np.isnan(inv_string[i,b,1,0,0]):
                for inv in range(1,max_inv+1):
                    if ~np.isnan(inv_string[i,b,inv,0,0]):
                        #Lo ponemos en base cero porque las cajas fisicas empezaban asi, desde el indice 0
                        inv_fisicos[i, b, inv-1, 0] = np.count_nonzero(~np.isnan(inv_string[i,b,inv,:,2]))
                        inv_fisicos[i, b, inv-1, 1] = inv_string[i,b,inv,0,0]
                        inv_fisicos[i, b, inv-1, 2] = inv_string[i,b,inv,0,1]
                        inv_fisicos[i, b, inv-1, 3] = inv_string[i,b,inv,1,3]


    return inv_fisicos