# -*- coding: utf-8 -*-
"""
Created on Wed May 14 19:35:10 2025

@author: mlopez
"""
import numpy as np

def preparar_datos_trackers(trackers_extraidos, n_bloques, max_n_tracker_por_bloque, long_XL, long_L, long_M, long_S):

    #Datos de trackers
        # Creamos un array tridimensional donde el numero de bloque se define en la 1a dimension, el numero de tracker en el bloque en la 2a y los datos en la 3a
    trackers_pb = np.empty((n_bloques+1, max_n_tracker_por_bloque, 4), dtype=object)
    trackers_pb[:] = np.nan #cambiamos None por np.nan para poder operar despues, no se puede poner directamente como full np.nan porque seria de tipo float y estamos metiendo strings
    
        # El primer dato sera el tipo, el segundo la longitud del tracker en funcion del tipo leido, el tercero su X y el cuarto su Y
    conteo_tracker = np.zeros(n_bloques+1)
    for tracker in trackers_extraidos:
        i = int(tracker[0])
        j = int(conteo_tracker[i])
        
        trackers_pb[i, j, 0] = tracker[1]
        
        if tracker[1] == 'XL':
            trackers_pb[i, j, 1] = long_XL
        elif tracker[1] == 'L':
            trackers_pb[i, j, 1] = long_L
        elif tracker[1] == 'M':
            trackers_pb[i, j, 1] = long_M
        else:
            trackers_pb[i, j, 1] = long_S
            
        trackers_pb[i, j, 2] = float(round(tracker[2],2))
        trackers_pb[i, j, 3] = float(round(tracker[3],2))
            
        #actualizamos el conteo para j
        conteo_tracker[i]=conteo_tracker[i]+1
        
    return trackers_pb


def ordenar_x_y(trackers_pb,bloque_inicial, n_bloques):
    for i in range(1, n_bloques + 1):
        # Ordenar por x
        trackers_pb[i] = trackers_pb[i][np.argsort(trackers_pb[i, :, 2].astype(float))]

        # Encontrar los índices donde x cambia
        x_values = trackers_pb[i, :, 2]
        unique_x, indices = np.unique(x_values, return_index=True)

        # Ordenar por y dentro de cada grupo de x iguales
        for j in range(len(indices)):
            start_idx = indices[j]
            end_idx = indices[j + 1] if j + 1 < len(indices) else len(x_values)
            trackers_pb[i, start_idx:end_idx] = trackers_pb[i, start_idx:end_idx][np.argsort(
                trackers_pb[i, start_idx:end_idx, 3].astype(np.float64))[::-1]]

    return trackers_pb


def agrupar_en_filas(trackers_pb,bloque_inicial, n_bloques, max_tpb, max_fpb, max_tpf, separacion):
    filas = np.empty((n_bloques+1, max_fpb, max_tpf, 4), dtype=object)
    filas[:] = np.nan  # cambiamos None por nan para poder operar posteriormente
    max_f = 0
    for i in range(bloque_inicial, n_bloques+1):
        f = 0
        t = 0
        filas[i, f, t] = trackers_pb[i, 0]
        for j in range(1, max_tpb):
            # en lugar de usar == damos un valor de tolerancia de 0.2m en eje x y 0.4m en eje Y por si hay alguna separacion mayor por algun motivo (por ejemplo espacio extra para giro de DCBus) pero siempre sin ser suficiente como para crear un pasillo que rompa bandas
            if abs(trackers_pb[i, j, 2]-trackers_pb[i, j-1, 2]) <= 0.2 and abs((trackers_pb[i, j-1, 3]-trackers_pb[i, j, 3])-(trackers_pb[i, j, 1]+separacion)) <= 0.4:
                t = t+1
                filas[i, f, t] = trackers_pb[i, j]
            else:
                t = 0
                if np.isnan(trackers_pb[i, j, 2]):
                    f = f
                else:
                    f = f+1
                    filas[i, f, t] = trackers_pb[i, j]
        if f > max_f:
            max_f = f
    # como hemos calculado el maximo numero de filas por bloque, acortamos el array
    filas = filas[:, :max_f+1, :, :]
    return filas, max_f
    # Seleccionar una parte del array para visualizar


def extremos_de_fila(fila):
    lim_sup_fila = round(fila[0, 3] + fila[0, 1], 2)
    lim_inf_fila = round(min(fila[:, 3]), 2)
    return lim_sup_fila, lim_inf_fila


def agrupacion_en_bandas(filas, pitch,bloque_inicial, n_bloques, max_fpb, max_bpb, max_tpf, coord_PCS_DC_inputs):
    bandas = np.empty((n_bloques+1, max_bpb+1, max_fpb, max_tpf, 4), dtype=object)
    bandas[:] = np.nan  # cambiamos None por nan para poder operar posteriormente

    def indice_tracker_mas_cercano_a_pcs(fila, coord_pcs):
        """
        Funcion auxiliar para adelantar la orientacion de la fila respecto a la PCS para resolver casos de dos filas de misma X y distinta Y que cumple
        """
        y_vals = fila[:, 3]
        valid = ~np.isnan(y_vals.astype(float))
        if not np.any(valid):
            return None  # No hay datos válidos
        idxs_validos = np.where(valid)[0]
        idx_primero = idxs_validos[0]
        idx_ultimo = idxs_validos[-1]
    
        y1 = float(y_vals[idx_primero])
        y2 = float(y_vals[idx_ultimo])
    
        d1 = abs(coord_pcs[1] - y1)
        d2 = abs(coord_pcs[1] - y2)
        return idx_primero if d1 < d2 else idx_ultimo


    max_b = 0
    max_f_r = 0
    for i in range(bloque_inicial, n_bloques+1):
        b = 0
        f_r = 0  # f_r es la fila relativa a la banda

        bandas[i, b, f_r] = filas[i, 0]
        p = 0
        a = 1
        # sacar longitud de filas reales (sin contar nan)
        long = int(np.sum([isinstance(x, float) and not np.isnan(x)for x in filas[i, :, 0, 3]]))
        # se crea una variable almacen a la cual se envian las filas de la misma x pero otra y que no encajan en la banda, para luego volver a analizarlas
        almacen = list(range(1, long))
        while a < long:
            indices_filas = almacen
            almacen = []
            for f in indices_filas:
                y_sup_fila_izq, y_inf_fila_izq = extremos_de_fila(bandas[i, b, f_r])
                y_sup_fila, y_inf_fila = extremos_de_fila(filas[i, f, :, :])
                
                if f < max_f_r:
                    y_sup_fila_siguiente, y_inf_fila_siguiente = extremos_de_fila(filas[i, f+1, :, :])

                # de momento no se usan como criterio las x
                x_fila_izq = bandas[i, b, f_r, 0, 2]
                x_fila = filas[i, f, 0, 2]

                p = p+1  # se define para identificar la primera iteracion del bloque y parar el while si hace falta
                # Condicion de X (se admite dentro de la misma banda hasta un hueco de tracker 4*pitch monofila 2*pitch Double Row)
                # Condicion de Y, tiene que haber alguna Y del tracker dentro del segmento del otro
                if (0 < (x_fila-x_fila_izq) <= pitch*4) and ((y_sup_fila_izq <= y_sup_fila and y_sup_fila_izq >= y_inf_fila) or (y_inf_fila_izq <= y_sup_fila and y_inf_fila_izq >= y_inf_fila) or (y_inf_fila_izq <= y_inf_fila and y_sup_fila_izq >= y_sup_fila) or (y_sup_fila_izq <= y_sup_fila and y_inf_fila_izq >= y_inf_fila)):
                    #excepcion, en WEN (B.41) pasó que se bloqueaba el pasillo con un tracker que cumple con dos trackers, por lo que se iba al de arriba, se evalua si la fila siguiente cumple tambien o no
                    if f < max_f_r and filas[i, f+1, 0, 2]==x_fila and ((y_sup_fila_izq <= y_sup_fila_siguiente and y_sup_fila_izq >= y_inf_fila_siguiente) or (y_inf_fila_izq <= y_sup_fila_siguiente and y_inf_fila_izq >= y_inf_fila_siguiente) or (y_inf_fila_izq <= y_inf_fila_siguiente and y_sup_fila_izq >= y_sup_fila_siguiente) or (y_sup_fila_izq <= y_sup_fila_siguiente and y_inf_fila_izq >= y_inf_fila_siguiente)): #si las dos siguientes estan alineadas y cumplen condicion ambas
                        idx_comp_fila_banda = indice_tracker_mas_cercano_a_pcs(bandas[i, b, f_r], coord_PCS_DC_inputs[i])
                        idx_comp_fila = indice_tracker_mas_cercano_a_pcs(filas[i, f], coord_PCS_DC_inputs[i])
                        idx_comp_fila_siguiente = indice_tracker_mas_cercano_a_pcs(filas[i, f+1], coord_PCS_DC_inputs[i])
                        
                        if abs(filas[i, f+1, idx_comp_fila_siguiente, 3]-bandas[i, b, f_r, idx_comp_fila_banda, 3]) < abs(filas[i, f, idx_comp_fila, 3]-bandas[i, b, f_r, idx_comp_fila_banda, 3]): #si el inferior está más cerca
                            almacen.append(f)
                        else:
                            f_r = f_r+1
                            bandas[i, b, f_r] = filas[i, f]
                            a = a+1
                    #comportamiento normal        
                    else: 
                        f_r = f_r+1
                        bandas[i, b, f_r] = filas[i, f]
                        a = a+1
                elif f == indices_filas[0] and p != 1:
                    f_r = 0
                    b = b+1
                    a = a+1
                    bandas[i, b, f_r] = filas[i, f]
                else:
                    almacen.append(f)

            if f_r > max_f_r:
                max_f_r = f_r
            if p == 50000:
                break
        if b > max_b:
            max_b = b

    # como hemos calculado el maximo numero de filas por banda y de banda por bloque, acortamos el array
    bandas = bandas[:, :max_b+1, :max_f_r+1, :]
    
    return bandas, max_b+1, max_f_r+1 #damos un + porque en futuros range no se tomaria en cuenta el limite superior



def orientacion_hacia_inversor(bandas, coord_PCS_DC_inputs,bloque_inicial, n_bloques, max_b, max_fr):
    suma_N = np.zeros((n_bloques+1, max_b), dtype=float)
    suma_S = np.zeros((n_bloques+1, max_b), dtype=float)
    orientacion = np.empty((n_bloques+1, max_b+1), dtype=object)
    for i in range(bloque_inicial, n_bloques+1):
        for b in range(0, max_b):
            for f in range(1, max_fr):
                x = bandas[i, b, f, 0, 2]
                y_N, y_S = extremos_de_fila(bandas[i, b, f])
                d_N = np.sqrt((coord_PCS_DC_inputs[i, 0]-x)**2+(coord_PCS_DC_inputs[i, 1]-y_N)**2)
                d_S = np.sqrt((coord_PCS_DC_inputs[i, 0]-x)**2+(coord_PCS_DC_inputs[i, 1]-y_S)**2)
                if not np.isnan(d_N) and not np.isnan(d_S):
                    suma_N[i, b] = suma_N[i, b]+d_N
                    suma_S[i, b] = suma_S[i, b]+d_S
            if suma_N[i, b] < suma_S[i, b]:
                orientacion[i, b] = 'N'
            elif suma_N[i, b] > suma_S[i, b]:
                orientacion[i, b] = 'S'
            else:
                orientacion[i, b] = 0
    return orientacion

def contorno_de_las_bandas(filas_en_bandas,bloque_inicial,n_bloques,max_b,max_f_str_b, h_modulo): #extrae y pone en dos dimensiones para cada banda todos sus puntos exteriores
    contorno_bandas=np.full((n_bloques+1,max_b,max_f_str_b*2,2),np.nan) #inicializamos una variable que necesitamos despues para definir el contorno de las bandas
    contorno_bandas_sup=np.full((n_bloques+1,max_b,max_f_str_b*2,2),np.nan) #guardamos las parciales tambien
    contorno_bandas_inf=np.full((n_bloques+1,max_b,max_f_str_b*2,2),np.nan) 
    
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(filas_en_bandas[i,b,0,0,2]):
                contorno_sup_banda=[]
                contorno_inf_banda=[]
                for f in range(0,max_f_str_b):
                    if ~np.isnan(filas_en_bandas[i,b,f,0,2]):
                        #añadimos las coordenadas de los contornos, centradas en la mitad del modulo
                        contorno_sup_banda.append([filas_en_bandas[i,b,f,0,2]+h_modulo/2,filas_en_bandas[i,b,f,0,3]+filas_en_bandas[i,b,f,0,1]]) #el primer tracker es el mas al N, mas su longitud es el extremo superior de la banda
                        contorno_inf_banda.append([filas_en_bandas[i,b,f,0,2]+h_modulo/2,np.nanmin(filas_en_bandas[i,b,f,:,3])]) #la minima Y de la fila es el tracker mas al sur, que ademas siempre tiene el punto de insercion al sur, por lo que es el punto mas inferior
                          
                contorno_sup_banda=np.array(contorno_sup_banda)
                contorno_inf_banda=np.array(contorno_inf_banda)

                conjunto=np.vstack((contorno_sup_banda,contorno_inf_banda))
                contorno_bandas[i,b,:conjunto.shape[0]]=conjunto
                contorno_bandas_sup[i,b,:contorno_sup_banda.shape[0]]=contorno_sup_banda
                contorno_bandas_inf[i,b,:contorno_inf_banda.shape[0]]=contorno_inf_banda
                
    return contorno_bandas, contorno_bandas_sup, contorno_bandas_inf

def clasificacion_bandas(bloque_inicial,n_bloques, max_b, contorno_bandas, coord_PCS_DC_inputs, orientacion, pasillo_entre_bandas, dist_min_b_separadas):
    #distinguimos cuatro tipos de bandas, creando matrices booleanas para clasificar cada banda
    bandas_anexas=np.full((n_bloques+1,max_b,1),False)
    bandas_separadas=np.copy(bandas_anexas)
    bandas_aisladas=np.copy(bandas_anexas)
    bandas_intermedias_o_extremo=np.copy(bandas_anexas)
    
    dist_min_b_anexa=50
    
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(contorno_bandas[i,b,0,0]): #si la banda no está vacía 
            
                #BANDAS ANEXAS, SI LA DISTANCIA A LA PCS ES MENOR QUE LA MINIMA ESTABLECIDA
                dist_f_pcs_2=np.sum((contorno_bandas[i,b][:, np.newaxis] - coord_PCS_DC_inputs[i])**2, axis=2) #sacamos el cuadrado de la distancia porque evitar la raiz cuadrada es mas eficiente en tiempo de computacion
                if np.any(dist_f_pcs_2 < dist_min_b_anexa**2): #si esta cerca de la PCS es anexa
                    bandas_anexas[i,b]=True
                    
                #BANDAS SEPARADAS, SI LA DISTANCIA A LA PCS ES MAYOR DEL MINIMO PERO ESTÁ EN EL CAMINO (PENDIENTE OPTIMIZAR DE MOMENTO SE DEFINE LA ZONA DEL CAMINO ENFRENTANDO BANDAS Y CON UNA DISTANCIA MINIMA, NO SE HAN IMPORTADO PUNTOS DEL CAMINO)    
                if bandas_anexas[i,b]==False:
                    if orientacion[i,b]=='S':
                        for bc in range(0,max_b):
                            if b!=bc and ~np.isnan(contorno_bandas[i,b,0,0]): #si la banda no es ella misma ni está vacía
                                if orientacion[i,bc]=='N':
                                    distancias_al_cuadrado = np.sum((contorno_bandas[i,b][:, np.newaxis] - contorno_bandas[i,bc])**2, axis=2) #no sacamos la distancia porque evitar la raiz cuadrada es mas eficiente en tiempo de computacion
                                    if np.any(distancias_al_cuadrado < dist_min_b_separadas**2): #con esto estamos identificando que b está pegada al camino por lo que aunque no tenga contacto directo con la PCS, solo tiene que seguirlo para llegar a ella
                                        bandas_separadas[i,b]=True
                                        break                                     
                    
                    elif orientacion[i,b]=='N':
                        for bc in range(0,max_b):
                            if b!=bc and ~np.isnan(contorno_bandas[i,b,0,0]): #si la banda no es ella misma ni está vacía
                                if orientacion[i,bc]=='S':
                                    distancias_al_cuadrado = np.sum((contorno_bandas[i,b][:, np.newaxis] - contorno_bandas[i,bc])**2, axis=2) 
                                    if np.any(distancias_al_cuadrado < dist_min_b_separadas**2): 
                                        bandas_separadas[i,b]=True
                                        break      
                                    
                #BANDAS INTERMEDIAS O EXTREMO
                    #Si la banda tiene otra banda inmediatamente debajo de su contorno (hay un pasillo de sepracion que se puede regular) es intermedia o extrema
                    if bandas_separadas[i,b]==False:
                        if orientacion[i,b]=='S':
                            for bc in range(0,max_b):
                                if b!=bc and ~np.isnan(contorno_bandas[i,b,0,0]): #si la banda no es ella misma ni está vacía
                                    if orientacion[i,bc]=='S':
                                        for coord_contorno in contorno_bandas[i,b]:
                                            for coord_contorno_bc in contorno_bandas[i,bc]:
                                                if coord_contorno[1] > coord_contorno_bc[1] and np.linalg.norm(coord_contorno-coord_contorno_bc) < pasillo_entre_bandas + 5: #con esto estamos identificando que b tiene otra banda más al sur a distancia de pasillo entre bandas
                                                    bandas_intermedias_o_extremo[i,b]=True
                                                    break
                                            if bandas_intermedias_o_extremo[i,b]==True:
                                                break
                                    if bandas_intermedias_o_extremo[i,b]==True:
                                        break
                        elif orientacion[i,b]=='N':
                            for bc in range(0,max_b):
                                if b!=bc and ~np.isnan(contorno_bandas[i,b,0,0]): #si la banda no es ella misma ni está vacía
                                    if orientacion[i,bc]=='N':
                                        for coord_contorno in contorno_bandas[i,b]:
                                            for coord_contorno_bc in contorno_bandas[i,bc]:
                                                if coord_contorno[1] < coord_contorno_bc[1] and np.linalg.norm(coord_contorno-coord_contorno_bc) < pasillo_entre_bandas + 5: #con esto estamos identificando que b tiene otra banda más al norte (estando ambas al sur del camino) a distancia de pasillo entre bandas
                                                    bandas_intermedias_o_extremo[i,b]=True
                                                    break
                                            if bandas_intermedias_o_extremo[i,b]==True:
                                                break
                                    if bandas_intermedias_o_extremo[i,b]==True:
                                        break       
                 #BANDAS AISLADAS
                     #Las restantes son por definicion "aisladas", que no cumplen ninguno de los criterios anteriores
                        if bandas_intermedias_o_extremo[i,b]==False:
                            bandas_aisladas[i,b]=True #si no se cumple ninguno de esos criterios esa banda (y las que tenga extremas asociadas, el bloque de bandas) está "aislada" sin referencia clara, se llevaran al camino y de ahi a la PCS pero habra que tocarlas a mano
              
    return bandas_anexas, bandas_separadas, bandas_aisladas, bandas_intermedias_o_extremo

def ordenar_bandas(bandas,contorno_bandas, contorno_bandas_sup, contorno_bandas_inf, bandas_anexas, bandas_separadas, bandas_aisladas, bandas_intermedias_o_extremo, filas_en_bandas, orientacion,bloque_inicial,n_bloques,max_b, pasillo_entre_bandas):
    for i in range(bloque_inicial, n_bloques+1):
        orden_final_bandas = []  
        orden_N = [[] for _ in range(0,max_b)]
        bandas_norte = list(np.where(orientacion[i, :] == "S")[0])
        bandas_norte.reverse()  # hay que hacer un reverse porque si el orden es de izq a derecha el ultimo en procesarse es el que está mas a la derecha, y en igualdad de condiciones va a salir por encima del de la izquierda
        if bandas_norte != []: #si el bloque solo tiene bandas al sur no entramos porque daria error
            banda_insertada=False
            copia_bandas_norte=np.copy(bandas_norte)
            for b in copia_bandas_norte:
                if bandas_anexas[i,b]==True or bandas_separadas[i,b]==True: #si estan en el camino son la ultima fila del lado norte, como van de derecha a izquierda se pueden insertar en ese orden
                    orden_N[0].append(b)
                    banda_insertada=True
                    bandas_norte.remove(b) #una vez clasificada se quita de la bolsa inicial            
            
            if banda_insertada==True:
                bb = 0  #se define un bloque de bandas horizontal con ese primer nivel, asignado a la lista 0 de orden_N las siguientes estaran por encima (CUIDADO LAS AISLADAS)
                banda_insertada=False
                copia_bandas_norte=np.copy(bandas_norte)
                for b in orden_N[bb]: #partimos de las ya guardadas, sigue estando el orden invertido
                    for bc in copia_bandas_norte: #recorremos de nuevo la bolsa para clasificar las extremas o intermedias que están en contacto con las ya guardadas
                        if bandas_intermedias_o_extremo[i,bc]==True:
                            #buscamos la relacion de bandas que está cumpliendo la condición de extremo o intermedia
                            distancias_al_cuadrado = np.sum((contorno_bandas[i,b][:, np.newaxis] - contorno_bandas[i,bc])**2, axis=2) #no sacamos la distancia porque evitar la raiz cuadrada es mas eficiente en tiempo de computacion
                            if np.any(distancias_al_cuadrado < (pasillo_entre_bandas + 5)**2):
                                #se añade la banda de la bolsa a un nuevo nivel, siguiendo el orden de la de abajo (nuevo bloque de bandas)
                                orden_N[bb+1].append(bc)
                                banda_insertada=True
                                bandas_norte.remove(bc)
                if banda_insertada==True:
                    bb = 1
                    #volvemos a repetir la operacion porque el maximo de bandas enlazadas N-S que contempla el diseño es 3 (aunque es raro, lo normal es 2)
                    banda_insertada=False
                    copia_bandas_norte=np.copy(bandas_norte)
                    for b in orden_N[bb]: 
                        for bc in copia_bandas_norte:
                            if bandas_intermedias_o_extremo[i,bc]==True:
                                distancias_al_cuadrado = np.sum((contorno_bandas[i,b][:, np.newaxis] - contorno_bandas[i,bc])**2, axis=2) #no sacamos la distancia porque evitar la raiz cuadrada es mas eficiente en tiempo de computacion
                                if np.any(distancias_al_cuadrado < (pasillo_entre_bandas + 5)**2):
                                    #se añade la banda de la bolsa a un nuevo nivel, siguiendo el orden de la de abajo (nuevo bloque de bandas)
                                    orden_N[bb+1].append(bc)
                                    banda_insertada=True
                                    bandas_norte.remove(bc)
                    if banda_insertada==True:
                        bb = 2            

            #invertimos los ordenes dentro de cada lista para dar prioridad de izquierda a derecha
            for blqb in range(0,max_b):
                orden_N[blqb].reverse()
            
            #las bandas que queden en la bolsa son aisladas o intermedias/extremas encima de aisladas
            for b in bandas_norte:
                banda_en_limite_derecho=True
                banda_en_limite_izquierdo=True
                for lv in range(0,bb+1):
                    for bc in orden_N[lv]:
                        if bc not in bandas_norte: #si se habia leido ya una del grupo de aisladas ya hay que evitar contarla porque no se estaría evaluando sobre el bloque original
                            #Evaluamos si la banda aislada está metida dentro de alguna otra (se activan las filas de abajo) o está en un extremo
                            if np.nanmin(contorno_bandas[i,b,:,0]) < np.nanmax(contorno_bandas[i,bc,:,0]):
                                banda_en_limite_derecho=False
                            if np.nanmax(contorno_bandas[i,b,:,0]) > np.nanmin(contorno_bandas[i,bc,:,0]):
                                banda_en_limite_izquierdo=False
                        
                #Si no se activan las bandas anteriores sabemos que se va a insertar en un extremo del bloque de bandas, hay que ver a qué nivel, empezando desde arriba                    
                if banda_en_limite_derecho==True:
                    banda_insertada=False
                    for lv in range(bb,-1,-1):
                        if banda_insertada==True:
                            break
                        for bc in orden_N[lv]:
                            if np.nanmin(contorno_bandas_inf[i,b,:,1]) >= np.nanmin(contorno_bandas_inf[i,bc,:,1]) or lv==0: #si la parte baja de esa banda está por encima de la parte baja de una banda de ese nivel entonces está en ese nivel, si estamos en el nivel mas bajo tambien vale
                                #se puede dar la casuistica remota de que se metan en un mismo nivel una aislada y su intermedia o extrema superior, evaluamos primero si la ultima insertada estaba en la bolsa de aisladas+asociadas o no
                                if orden_N[lv][-1] in bandas_norte: #si no se ha borrado hasta este punto es porque era aislada o intermedia/extremo encima de una aislada
                                    if bandas_aisladas[i,b]==True: #si es aislada va debajo de la intermedia asi que se mete a la derecha
                                        orden_N[lv].append(b)
                                    elif bandas_intermedias_o_extremo[i,b]==True: #si es intermedia o extremos va por encima de la aislda. POSIBLE OPTIMIZAR, SI ES UNA EXTREMO SOBRE UNA INTERMEDIA PODRIA PONER POR ENCIMA LA QUE NO ES
                                        orden_N[lv].insert(-2,b)
                                #si no se ha insertado previamente ninguna aislada
                                orden_N[lv].append(b) #lo insertamos el ultimo elemento por estar mas a la derecha
                                banda_insertada=True
                                break                
                    if banda_insertada==False: #si se recorren todos los niveles y la banda aislada está por encima, se le asigna al siguiente nivel vacío (irá la primera después)
                        if orden_N[bb+1]==[]: #si no se ha insertado previamente ninguna aislada                   
                            orden_N[bb+1].append(b) #la insertamos en el nuevo nivel                      
                        else: #si resulta que ya se habia insertado una del grupo de aisladas
                            if bandas_aisladas[i,b]==True: 
                                orden_N[bb+1].append(b)
                            elif bandas_intermedias_o_extremo[i,b]==True: 
                                orden_N[lv].insert(0,b)

                elif banda_en_limite_izquierdo==True:
                    banda_insertada=False
                    for lv in range(0,bb+1):
                        if banda_insertada==True:
                            break
                        for bc in orden_N[lv]:
                            if np.nanmin(contorno_bandas_inf[i,b,:,1]) >= np.nanmin(contorno_bandas_inf[i,bc,:,1]) or lv==0:
                                if orden_N[lv][0] in bandas_norte: 
                                    if bandas_aisladas[i,b]==True: 
                                        orden_N[lv].insert(1,b)
                                    elif bandas_intermedias_o_extremo[i,b]==True: #si es intermedia o extremos va por encima de la aislda. POSIBLE OPTIMIZAR, SI ES UNA EXTREMO SOBRE UNA INTERMEDIA PODRIA PONER POR ENCIMA LA QUE NO ES
                                        orden_N[lv].insert(0,b)                                        
                                orden_N[lv].insert(0,b) #lo insertamos en el primer elemento de ese nivel por estar mas a la izquierda
                                banda_insertada=True
                                break                            
                    if banda_insertada==False: 
                        if orden_N[bb+1]==[]:                   
                            orden_N[bb+1].append(b)                       
                        else: 
                            if bandas_aisladas[i,b]==True: 
                                orden_N[bb+1].append(b)
                            elif bandas_intermedias_o_extremo[i,b]==True: 
                                orden_N[lv].insert(0,b)
                                
                else: #Si hay bandas aisladas que caen encima de un bloque de bandas (porque estan mas separadas que la altura del pasillo), buscamos desde arriba hasta abajo si se está encima de alguna banda
                    banda_insertada=False
                    for lv in range(bb,-1,-1):
                        if banda_insertada==True:
                            break
                        for bc in orden_N[lv]:
                            if banda_insertada==True:
                                break
                            for coord_contorno in contorno_bandas[i,b]:
                                if banda_insertada==True:
                                    break
                                for coord_contorno_bc in contorno_bandas[i,bc]:
                                    if coord_contorno[0]==coord_contorno_bc[0]: #buscamos la x en la que coinciden
                                        if coord_contorno[1]>coord_contorno_bc[1]: #b está encima de bc, ahora hay que diferenciar dependiendo del nivel en el que se haya llevado a cabo la coincidencia
                                            if lv == bb:  #ya estabamos en el nivel más alto, se crea otro nuevo para insertar la banda
                                                if orden_N[bb+1]==[]: #si no se ha insertado previamente ninguna aislada                   
                                                    orden_N[bb+1].append(b) #la insertamos en el nuevo nivel                      
                                                else: #si resulta que ya se habia insertado una del grupo de aisladas
                                                    if bandas_aisladas[i,b]==True: 
                                                        orden_N[bb+1].append(b)
                                                    elif bandas_intermedias_o_extremo[i,b]==True: 
                                                        orden_N[lv].insert(0,b)
                                                banda_insertada=True
                                                break
                                                
                                            else: #si se ha bajado de nivel entonces hay que buscar en que x del nivel anterior estaba cayendo esa aislada
                                                for bc2 in orden_N[lv+1]:
                                                    if np.nanmax(contorno_bandas[i,b,0]) < np.nanmin(contorno_bandas[i,bc2,0]): #si estamos a la izquierda de bc2 entonces tenemos prioridad sobre ella y por tanto se inserta antes
                                                        pos = orden_N[lv+1].index(bc2)
                                                        orden_N[lv+1].insert(pos, b)
                                                        banda_insertada=True
                                                        break
                                                break
                if not banda_insertada:
                    orden_N[bb+1].append(b)
                    banda_insertada = True
                    
                    
            #invertimos el orden de las listas para dar prioridad de arriba a abajo
            orden_N.reverse()
                                    
        # REPETIMOS PARA EL SUR
        orden_S = [[] for _ in range(0,max_b)]
        bandas_sur = list(np.where(orientacion[i, :] == "N")[0])
        # no hay que hacer un reverse porque si el orden es de izq a derecha el ultimo en procesarse es el que está mas a la derecha, y en igualdad de condiciones va a salir por encima del de la izquierda
        if bandas_sur != []: #si el bloque solo tiene bandas al sur no entramos porque daria error
            banda_insertada=False
            copia_bandas_sur=np.copy(bandas_sur)
            for b in copia_bandas_sur:
                if bandas_anexas[i,b]==True or bandas_separadas[i,b]==True: #si estan en el camino son la ultima fila del lado sur, como van de derecha a izquierda se pueden insertar en ese orden
                    orden_S[0].append(b)
                    banda_insertada=True
                    bandas_sur.remove(b) #una vez clasificada se quita de la bolsa inicial            
            if banda_insertada==True:        
                bb = 0  #se define un bloque de bandas horizontal con ese primer nivel, asignado a la lista 0 de orden_S las siguientes estaran por encima (CUIDADO LAS AISLADAS)
                banda_insertada=False
                copia_bandas_sur=np.copy(bandas_sur)
                for b in orden_S[bb]: #partimos de las ya guardadas
                    for bc in copia_bandas_sur: #recorremos de nuevo la bolsa para clasificar las extremas o intermedias que están en contacto con las ya guardadas
                        if bandas_intermedias_o_extremo[i,bc]==True:
                            distancias_al_cuadrado = np.sum((contorno_bandas[i,b][:, np.newaxis] - contorno_bandas[i,bc])**2, axis=2) #no sacamos la distancia porque evitar la raiz cuadrada es mas eficiente en tiempo de computacion
                            if np.any(distancias_al_cuadrado < (pasillo_entre_bandas + 5)**2):
                                #se añade la banda de la bolsa a un nuevo nivel, siguiendo el orden de la de abajo (nuevo bloque de bandas)
                                orden_S[bb+1].append(bc)
                                banda_insertada=True
                                bandas_sur.remove(bc)
                if banda_insertada==True:
                    bb = 1
                    #volvemos a repetir la operacion porque el maximo de bandas enlazadas N-S que contempla el diseño es 3 (aunque es raro, lo normal es 2)
                    banda_insertada=False
                    copia_bandas_sur=np.copy(bandas_sur)
                    for b in orden_S[bb]: 
                        banda_insertada=False
                        for bc in copia_bandas_sur:
                            if bandas_intermedias_o_extremo[i,bc]==True:
                                distancias_al_cuadrado = np.sum((contorno_bandas[i,b][:, np.newaxis] - contorno_bandas[i,bc])**2, axis=2) #no sacamos la distancia porque evitar la raiz cuadrada es mas eficiente en tiempo de computacion
                                if np.any(distancias_al_cuadrado < (pasillo_entre_bandas + 5)**2):
                                    #se añade la banda de la bolsa a un nuevo nivel, siguiendo el orden de la de abajo (nuevo bloque de bandas)
                                    orden_S[bb+1].append(bc)
                                    banda_insertada=True
                                    bandas_sur.remove(bc)
                    if banda_insertada==True:
                        bb = 2            

            #invertimos los ordenes dentro de cada lista para dar prioridad de derecha a izquierda
            for blqb in range(0,max_b):
                orden_S[blqb].reverse()
            
            #las bandas que queden en la bolsa son aisladas o intermedias/extremas encima de aisladas
            for b in bandas_sur:
                banda_en_limite_derecho=True
                banda_en_limite_izquierdo=True
                for lv in range(0,bb+1):
                    for bc in orden_S[lv]:
                        #Evaluamos si la banda aislada está metida dentro de alguna otra (se activan las filas de abajo) o está en un extremo
                        if np.nanmin(contorno_bandas[i,b,:,0]) < np.nanmax(contorno_bandas[i,bc,:,0]):
                            banda_en_limite_derecho=False
                        if np.nanmax(contorno_bandas[i,b,:,0]) > np.nanmin(contorno_bandas[i,bc,:,0]):
                            banda_en_limite_izquierdo=False
                        
                #Si no se activan las bandas anteriores sabemos que se va a insertar en un extremo del bloque de bandas, hay que ver a qué nivel, empezando desde abajo               
                if banda_en_limite_derecho==True:
                    banda_insertada=False
                    for lv in range(bb+1,-1,-1):
                        if banda_insertada==True:
                            break
                        for bc in orden_S[lv]:
                            if np.nanmax(contorno_bandas_sup[i,b,:,1]) <= np.nanmax(contorno_bandas_sup[i,bc,:,1]) or lv==0: #si tiene algun punto por ENCIMA (S) del contorno superior de cualquier banda del primer nivel, estará en ese primer nivel, y si no se actualizara el for y se ira al siguiente
                                #se puede dar la casuistica remota de que se metan en un mismo nivel una aislada y su intermedia o extrema superior, evaluamos primero si la ultima insertada estaba en la bolsa de aisladas+asociadas o no
                                if orden_S[lv][0] in bandas_sur: #si no se ha borrado hasta este punto es porque era aislada o intermedia/extremo encima de una aislada
                                    if bandas_aisladas[i,b]==True: #si es aislada va debajo de la intermedia asi que se mete a la izquierda
                                        orden_S[lv].insert(0,b)
                                    elif bandas_intermedias_o_extremo[i,b]==True: #si es intermedia o extremos va por encima de la aislada. POSIBLE OPTIMIZAR, SI ES UNA EXTREMO SOBRE UNA INTERMEDIA PODRIA PONER POR ENCIMA LA QUE NO ES
                                        orden_S[lv].insert(1,b)
                                #si no se ha insertado previamente ninguna aislada
                                orden_S[lv].insert(0,b) #lo insertamos el primer elemento por estar mas a la derecha
                                banda_insertada=True
                                break
                    if banda_insertada==False: #si se recorren todos los niveles y la banda aislada está por debajo, se le asigna al siguiente nivel vacío 
                        if orden_S[bb+1]==[]: #si no se ha insertado previamente ninguna aislada                   
                            orden_S[bb+1].append(b) #la insertamos en el nuevo nivel                      
                        else: #si resulta que ya se habia insertado una del grupo de aisladas
                            if bandas_aisladas[i,b]==True: 
                                orden_S[bb+1].insert(0,b)
                            elif bandas_intermedias_o_extremo[i,b]==True: 
                                orden_S[lv].append(b)

                elif banda_en_limite_izquierdo==True:
                    banda_insertada=False
                    for lv in range(bb+1,-1,-1):
                        if banda_insertada==True:
                            break
                        for bc in orden_S[lv]:
                            if np.nanmax(contorno_bandas_sup[i,b,:,1]) <= np.nanmax(contorno_bandas_sup[i,bc,:,1]) or lv==0: #si tiene algun punto por encima del contorno inferior de cualquier banda del primer nivel, estará en ese primer nivel
                                if orden_S[lv][-1] in bandas_sur: 
                                    if bandas_aisladas[i,b]==True: 
                                        orden_S[lv].insert(-1,b)
                                    elif bandas_intermedias_o_extremo[i,b]==True: #si es intermedia o extremos va por encima de la aislda. POSIBLE OPTIMIZAR, SI ES UNA EXTREMO SOBRE UNA INTERMEDIA PODRIA PONER POR ENCIMA LA QUE NO ES
                                        orden_S[lv].append(b)                                        
                                orden_S[lv].append(b) #lo insertamos en el ultimo elemento de ese nivel por estar mas a la izquierda
                                banda_insertada=True
                                break                            
                    if banda_insertada==False: 
                        if orden_S[bb+1]==[]:                   
                            orden_S[bb+1].append(b)                       
                        else: 
                            if bandas_aisladas[i,b]==True: 
                                orden_S[bb+1].append(b)
                            elif bandas_intermedias_o_extremo[i,b]==True: 
                                orden_S[lv].insert(0,b)
                                
                else: #Si hay bandas aisladas que caen debajo de un bloque de bandas (porque estan mas separadas que la altura del pasillo), buscamos desde abajo hasta arriba si se está debajo de alguna banda
                    banda_insertada=False
                    for lv in range(bb,-1,-1):
                        if banda_insertada==True:
                            break
                        for bc in orden_S[lv]:
                            if banda_insertada==True:
                                break
                            for coord_contorno in contorno_bandas[i,b]:
                                if banda_insertada==True:
                                    break
                                for coord_contorno_bc in contorno_bandas[i,bc]:
                                    if coord_contorno[0]==coord_contorno_bc[0]: #buscamos la x en la que coinciden
                                        if coord_contorno[1]<coord_contorno_bc[1]: #b está debajo de bc, ahora hay que diferenciar dependiendo del nivel en el que se haya llevado a cabo la coincidencia
                                            if lv == bb:  #ya estabamos en el nivel más bajo, se crea otro nuevo para insertar la banda
                                                if orden_S[bb+1]==[]: #si no se ha insertado previamente ninguna aislada                   
                                                    orden_S[bb+1].append(b) #la insertamos en el nuevo nivel                      
                                                else: #si resulta que ya se habia insertado una del grupo de aisladas
                                                    if bandas_aisladas[i,b]==True: 
                                                        orden_S[bb+1].append(b)
                                                    elif bandas_intermedias_o_extremo[i,b]==True: 
                                                        orden_S[lv].insert(0,b)
                                                banda_insertada=True
                                                break
                                                
                                            else: #si se ha subido de nivel entonces hay que buscar en que x del nivel anterior estaba cayendo esa aislada
                                                for bc2 in orden_S[lv+1]:
                                                    if np.nanmax(contorno_bandas[i,b,0]) > np.nanmin(contorno_bandas[i,bc2,0]): #si estamos a la derecha de bc2 entonces tenemos prioridad sobre ella y por tanto se inserta antes
                                                        orden_S[lv+1].insert(bc2,b)                    
                                                        banda_insertada=True
                                                        break
                                                break
                                                        
            #no hace falta invertir el orden de la lista de listas porque ya se da prioridad de arriba a abajo
            
            
        orden_final_bandas = [banda for sublist in orden_N for banda in sublist]
        orden_final_bandas_sur=[banda for sublist in orden_S for banda in sublist]
        orden_final_bandas.extend(orden_final_bandas_sur)
    
        # usamos una variable almacen y actualizamos los numeros de bandas en todas las variables que se habian calculado y se van a seguir usando despues
        almacen_bandas = np.copy(bandas[i])
        almacen_orientacion=np.copy(orientacion[i])
        almacen_bandas_anexas=np.copy(bandas_anexas[i])
        almacen_bandas_separadas=np.copy(bandas_separadas[i])
        almacen_bandas_intermedias_o_extremo=np.copy(bandas_intermedias_o_extremo[i])
        almacen_bandas_aisladas=np.copy(bandas_aisladas[i])
        almacen_filas_en_bandas=np.copy(filas_en_bandas[i])
        almacen_contorno_bandas=np.copy(contorno_bandas[i])
        almacen_contorno_bandas_sup=np.copy(contorno_bandas_sup[i])
        almacen_contorno_bandas_inf=np.copy(contorno_bandas_inf[i])
        
        for b in range(0, len(orden_final_bandas)):
            bandas[i, b] = almacen_bandas[orden_final_bandas[b]]
            orientacion[i, b] = almacen_orientacion[orden_final_bandas[b]]    
            bandas_anexas[i,b] = almacen_bandas_anexas[orden_final_bandas[b]]
            bandas_separadas[i, b] = almacen_bandas_separadas[orden_final_bandas[b]]
            bandas_intermedias_o_extremo[i, b] = almacen_bandas_intermedias_o_extremo[orden_final_bandas[b]]
            bandas_aisladas[i, b] = almacen_bandas_aisladas[orden_final_bandas[b]]
            filas_en_bandas[i, b] = almacen_filas_en_bandas[orden_final_bandas[b]]
            contorno_bandas[i, b] = almacen_contorno_bandas[orden_final_bandas[b]]
            contorno_bandas_sup[i, b] = almacen_contorno_bandas_sup[orden_final_bandas[b]]
            contorno_bandas_inf[i, b] = almacen_contorno_bandas_inf[orden_final_bandas[b]]
    
    return bandas , orientacion,  bandas_anexas, bandas_separadas, bandas_intermedias_o_extremo, bandas_aisladas, filas_en_bandas, contorno_bandas, contorno_bandas_sup, contorno_bandas_inf

def sacar_y_ordenar_filas_en_bandas(bandas, orientacion, config_tracker,bloque_inicial, n_bloques, max_b, max_tpf, max_fr, h_modulo, pitch):
    copia = np.copy(bandas)
    if config_tracker == 'Monofila':
        mono_o_bif = 1
    else:
        mono_o_bif = 2

    # numero maximo posible de filas de strings por banda
    max_f_str_b = max_fr*mono_o_bif+2

    filas_en_bandas = np.empty((n_bloques+1, max_b, max_f_str_b, max_tpf, 4),dtype=object)
    filas_en_bandas[:] = np.nan

    for i in range(bloque_inicial, n_bloques+1):
        for b in range(0, max_b):
            f=0
            if orientacion[i,b] == "S":
                for ft in range(0, max_fr): #para cada fila de trackers
                    for iteraciones in range(mono_o_bif):
                        filas_en_bandas[i,b,f,:,[0,1,3]]=copia[i,b,ft,:,[0,1,3]]
                        filas_en_bandas[i,b,f,:,2]=copia[i,b,ft,:,2]+pitch*iteraciones
                        f=f+1    
                        
            elif orientacion[i,b] == "N":
                indice = np.argmax(bandas[i, b, :, 0, 2])
                for f_inv in range(indice, -1, -1):
                    for iteraciones in range(mono_o_bif):
                        filas_en_bandas[i,b,f,:,[0,1,3]]=copia[i,b,f_inv,:,[0,1,3]]
                        if iteraciones==0:
                            filas_en_bandas[i,b,f,:,2]=copia[i,b,f_inv,:,2]+pitch
                        else:
                            filas_en_bandas[i,b,f,:,2]=copia[i,b,f_inv,:,2]
                        f=f+1   
    return filas_en_bandas, max_f_str_b
                    
def filas_de_strings(bandas, filas_en_bandas, config_tracker, orientacion,bloque_inicial, n_bloques, max_b, max_f_str_b, max_tpf, h_modulo, pitch, salto_motor, pos_salto_motor_M, pos_salto_motor_L): 
    strings_fisicos = np.full((n_bloques+1, max_b+1, max_f_str_b+2, max_tpf*3, 3), np.nan) #Ademas de las coordenadas le damos un ID global de la planta, creamos un array de orientacion ligado a ese id global (incluyendo su banda original) para que no se vea afectado por futuras transformaciones que cambien los strings de banda
    dist_ext_opuesto_str=np.full((n_bloques+1, max_b+1, max_f_str_b+2, max_tpf*3), np.nan)
    str_ID_general=1
    ori_str_ID=['-']
    max_s=0
    for i in range(bloque_inicial, n_bloques+1):
        for b in range(0, max_b):
            k = 0  # contador de filas de strings
            for f in range(0, max_f_str_b):
                s = 0
                for t in range(0, max_tpf):
                    if filas_en_bandas[i, b, f, t, 0] == "S":
                        dist_ext_opuesto_str[i,b,k,s]=filas_en_bandas[i, b, f, t, 1]
                        strings_fisicos[i, b, k, s, 0] = filas_en_bandas[i, b, f, t, 2]+h_modulo/2
                        strings_fisicos[i, b, k, s, 1] = filas_en_bandas[i, b, f, t, 3]
                        strings_fisicos[i, b, k, s, 2] = str_ID_general
                        ori_str_ID.append([b,orientacion[i,b]])
                        str_ID_general= str_ID_general +1                     
                        s = s+1
                  
                    elif filas_en_bandas[i, b, f, t, 0] == "M":
                        long_string=(filas_en_bandas[i, b, f, t, 1]-salto_motor)/2
                        
                        #String 1, el mas al N
                        strings_fisicos[i, b, k, s, 0] = filas_en_bandas[i, b, f, t, 2]+h_modulo/2  # por defecto el primer string es el mas al norte, para cuadrar con el primer tracker de la fila
                        
                        if pos_salto_motor_M=='North':
                            strings_fisicos[i, b, k, s, 1] = filas_en_bandas[i, b, f, t, 3]+long_string
                            dist_ext_opuesto_str[i,b,k,s] = long_string+salto_motor
                        else:
                            strings_fisicos[i, b, k, s, 1] = filas_en_bandas[i, b, f, t, 3]+long_string+salto_motor
                            dist_ext_opuesto_str[i,b,k,s] = long_string
                            
                        strings_fisicos[i, b, k, s, 2] = str_ID_general
                        ori_str_ID.append([b,orientacion[i,b]])
                        str_ID_general= str_ID_general +1
                        
                        #String 2, el mas al S
                        if pos_salto_motor_M=='South':
                            dist_ext_opuesto_str[i,b,k,s+1]=long_string+salto_motor
                        else:
                            dist_ext_opuesto_str[i,b,k,s+1]=long_string
                            
                        strings_fisicos[i, b, k, s+1, 0] = filas_en_bandas[i, b, f, t, 2]+h_modulo/2                        
                        strings_fisicos[i, b, k, s+1, 1] = filas_en_bandas[i, b, f, t, 3]
                        strings_fisicos[i, b, k, s+1, 2] = str_ID_general
                        ori_str_ID.append([b,orientacion[i,b]])
                        str_ID_general= str_ID_general +1
                        s = s+2
                        
                    elif filas_en_bandas[i, b, f, t, 0] == "L":
                        long_string=(filas_en_bandas[i, b, f, t, 1]-salto_motor)/3
                        
                        #String 1, el mas al N
                        strings_fisicos[i, b, k, s, 0] = filas_en_bandas[i, b, f, t, 2]+h_modulo/2
                        
                        if pos_salto_motor_L=='North':
                            strings_fisicos[i, b, k, s, 1] = filas_en_bandas[i, b, f, t, 3]+long_string+long_string #POSIBLE OPTIMIZAR, detalle minimo, podrian cambiar longitudes con el tipo de tracker
                            dist_ext_opuesto_str[i,b,k,s] = long_string + salto_motor
                        else:
                            strings_fisicos[i, b, k, s, 1] = filas_en_bandas[i, b, f, t, 3]+long_string+salto_motor+long_string
                            dist_ext_opuesto_str[i,b,k,s] = long_string
                            
                        strings_fisicos[i, b, k, s, 2] = str_ID_general
                        ori_str_ID.append([b,orientacion[i,b]])
                        str_ID_general= str_ID_general +1
                                           
                        #String 2, el de enmedio
                        strings_fisicos[i, b, k, s+1, 0] = filas_en_bandas[i, b, f, t, 2]+h_modulo/2
                        
                        if pos_salto_motor_L=='South':
                            strings_fisicos[i, b, k, s+1, 1] = filas_en_bandas[i, b, f, t, 3]+long_string+salto_motor
                            dist_ext_opuesto_str[i,b,k,s+1] = long_string
                        else:    
                            strings_fisicos[i, b, k, s+1, 1] = filas_en_bandas[i, b, f, t, 3]+long_string
                            if pos_salto_motor_L=='North':
                                dist_ext_opuesto_str[i,b,k,s+1] = long_string
                            else:                                                       #el motor esta en el medio del tracker y por tanto en medio del string
                                dist_ext_opuesto_str[i,b,k,s+1] = long_string+salto_motor
                            
                        strings_fisicos[i, b, k, s+1, 2] = str_ID_general
                        ori_str_ID.append([b,orientacion[i,b]])
                        str_ID_general= str_ID_general +1
                        
                        #String 3, el mas al sur
                        if pos_salto_motor_M=='South':
                            dist_ext_opuesto_str[i,b,k,s+2]=long_string+salto_motor
                        else:
                            dist_ext_opuesto_str[i,b,k,s+2]=long_string
                            
                        strings_fisicos[i, b, k, s+2, 0] = filas_en_bandas[i, b, f, t, 2]+h_modulo/2
                        strings_fisicos[i, b, k, s+2, 1] = filas_en_bandas[i, b, f, t, 3]
                        strings_fisicos[i, b, k, s+2, 2] = str_ID_general
                        ori_str_ID.append([b,orientacion[i,b]])
                        str_ID_general= str_ID_general +1
                        s = s+3
                        
                    elif filas_en_bandas[i, b, f, t, 0] == "XL": #se asume que el motor va en el centro del tracker
                        long_string=(filas_en_bandas[i, b, f, t, 1]-salto_motor)/4
                        dist_ext_opuesto_str[i,b,k,s]=long_string
                        dist_ext_opuesto_str[i,b,k,s+1]=long_string
                        dist_ext_opuesto_str[i,b,k,s+2]=long_string
                        dist_ext_opuesto_str[i,b,k,s+3]=long_string
                        
                        #String 1, el mas al N
                        strings_fisicos[i, b, k, s, 0] = filas_en_bandas[i, b, f, t, 2]+h_modulo/2
                        strings_fisicos[i, b, k, s, 1] = filas_en_bandas[i, b, f, t, 3]+long_string*3+salto_motor #POSIBLE OPTIMIZAR, detalle minimo, podrian cambiar longitudes con el tipo de tracker  
                        strings_fisicos[i, b, k, s, 2] = str_ID_general
                        ori_str_ID.append([b,orientacion[i,b]])
                        str_ID_general= str_ID_general +1
                                           
                        #String 2, el de enmedio N
                        strings_fisicos[i, b, k, s+1, 0] = filas_en_bandas[i, b, f, t, 2]+h_modulo/2
                        strings_fisicos[i, b, k, s+1, 1] = filas_en_bandas[i, b, f, t, 3]+long_string*2+salto_motor
                        strings_fisicos[i, b, k, s+1, 2] = str_ID_general
                        ori_str_ID.append([b,orientacion[i,b]])
                        str_ID_general= str_ID_general +1

                        #String 3, el de enmedio S
                        strings_fisicos[i, b, k, s+2, 0] = filas_en_bandas[i, b, f, t, 2]+h_modulo/2
                        strings_fisicos[i, b, k, s+2, 1] = filas_en_bandas[i, b, f, t, 3]+long_string
                        strings_fisicos[i, b, k, s+2, 2] = str_ID_general
                        ori_str_ID.append([b,orientacion[i,b]])
                        str_ID_general= str_ID_general +1      
                        
                        #String 4, el mas al sur
                        strings_fisicos[i, b, k, s+3, 0] = filas_en_bandas[i, b, f, t, 2]+h_modulo/2
                        strings_fisicos[i, b, k, s+3, 1] = filas_en_bandas[i, b, f, t, 3]
                        strings_fisicos[i, b, k, s+3, 2] = str_ID_general
                        ori_str_ID.append([b,orientacion[i,b]])
                        str_ID_general= str_ID_general +1
                        s = s+4        
                        
                    if s > max_s:
                        max_s=s
                k = k+1
    # corregimos las filas con orientacion S para que el primer string (s=0) sea el que está más al sur,
    strings_fisicos = ordenar_strings_segun_orientacion(strings_fisicos, orientacion,bloque_inicial, n_bloques, max_b, max_f_str_b, dist_ext_opuesto_str)
    return strings_fisicos, ori_str_ID, max_s, dist_ext_opuesto_str


def ordenar_strings_segun_orientacion(strings_fisicos, orientacion,bloque_inicial, n_bloques, max_b, max_f_str_b, dist_ext_opuesto_str):
    copia = np.copy(strings_fisicos)
    for i in range(bloque_inicial, n_bloques+1):
        for b in range(0, max_b+1):
            if orientacion[i, b] == 'S':
                for f in range(0, max_f_str_b):
                    if ~np.isnan(strings_fisicos[i, b, f, 0, 0]): #obviamos las filas vacias
                        indice = np.nanargmin(strings_fisicos[i, b, f, :, 1]) #cogemos el valor minimo de la fila (a partir de el valen nan) y lo invertimos en el orden
                        s = 0
                        for k in range(indice, -1, -1):
                            strings_fisicos[i, b, f, s] = copia[i, b, f, k]
                            s = s+1
            if orientacion[i, b] == 'N': #si la orientacion es al norte, el punto de referencia del string es del más al norte, aprovechamos para subirlo, si bien ya esta orientado correctamente (el s1 es el más al norte)
                for f in range(0, max_f_str_b):
                    if ~np.isnan(strings_fisicos[i, b, f, 0, 0]): #obviamos las filas vacias
                        indice = np.nanargmin(strings_fisicos[i, b, f, :, 1])
                        for s in range(0,indice+1):
                            if ~np.isnan(strings_fisicos[i, b, f, s, 0]): #obviamos los strings vacios
                                strings_fisicos[i, b, f, s, 1] = copia[i, b, f, s, 1]+dist_ext_opuesto_str[i,b,f,s]
                       
    return strings_fisicos
