# -*- coding: utf-8 -*-
"""
Created on Wed May 14 19:38:50 2025

@author: mlopez
"""

import numpy as np


def lineas_MV_o_FO_por_caminos(polilineas_guia, lineas_MV_o_FO, MV_o_FO):
    import numpy as np
    import networkx as nx
    from shapely.geometry import LineString, Point

    #--------Generar lineas por el camino mas corto de la linea guia---------
    def convertir_a_pares(polilineas):
        polilineas_convertidas = []
        for linea in polilineas:
            if isinstance(linea, (tuple, list)):
                if all(isinstance(val, (int, float, np.float64)) for val in linea):
                    if len(linea) % 2 != 0:
                        raise ValueError("Línea con número impar de coordenadas (x, y)")
                    pares = [[linea[i], linea[i + 1]] for i in range(0, len(linea), 2)]
                    polilineas_convertidas.append(pares)
                else:
                    polilineas_convertidas.append([list(p) for p in linea])
            else:
                raise TypeError(f"Línea inválida: {linea}")
        return polilineas_convertidas

    def cuantizar_polilineas(polilineas, decimales=1):
        return [[list(np.round(p, decimales)) for p in linea] for linea in polilineas]

    def construir_grafo_y_segmentos(polilineas):
        G = nx.Graph()
        segmentos = []
        for linea in polilineas:
            for i in range(len(linea) - 1):
                a = tuple(np.round(linea[i], 5))
                b = tuple(np.round(linea[i + 1], 5))
                dist = np.linalg.norm(np.array(a) - np.array(b))
                G.add_edge(a, b, weight=dist)
                segmentos.append((a, b))
        return G, segmentos

    def proyectar_punto_sobre_segmentos(p, segmentos):
        punto = Point(p)
        mejor_proyeccion = None
        min_dist = float('inf')
        for a, b in segmentos:
            linea = LineString([a, b])
            proyeccion = linea.interpolate(linea.project(punto))
            dist = punto.distance(proyeccion)
            if dist < min_dist:
                min_dist = dist
                mejor_proyeccion = proyeccion
        return list(mejor_proyeccion.coords)[0]



    def ruta_minima(coord_inicio, coord_destino, G, segmentos):
        p_start_proj = proyectar_punto_sobre_segmentos(coord_inicio, segmentos)
        p_end_proj   = proyectar_punto_sobre_segmentos(coord_destino, segmentos)
    
        nodo_cerca_start = min(G.nodes, key=lambda n: np.linalg.norm(np.array(n) - np.array(coord_inicio)))
        nodo_cerca_end   = min(G.nodes, key=lambda n: np.linalg.norm(np.array(n) - np.array(coord_destino)))
    
        try:
            camino = nx.shortest_path(G, source=nodo_cerca_start, target=nodo_cerca_end, weight='weight')
            if len(camino) < 2:
                return None, True
    
            ruta_guiada = [list(p) for p in camino]
            
            ruta_final = [coord_inicio, p_start_proj] + ruta_guiada + [p_end_proj, coord_destino]
    
            return ruta_final, False
    
        except nx.NetworkXNoPath:
            print(f"No hay conexión entre {coord_inicio} y {coord_destino}")
            return None, True



    # Ejecucion
    polilineas_guia = convertir_a_pares(polilineas_guia)
    G, segmentos = construir_grafo_y_segmentos(polilineas_guia)

    errores_conexion = []
    
    for i, linea in enumerate(lineas_MV_o_FO):
        if i == 0:
            continue
        for j, tramo in enumerate(linea):
            if j==0: #el primer elemento de la linea es un string con el nombre "Line x" antes de empezar los tramos, se adapta en pol_cable_MV para ir alineados
                continue
            else:
                coord_inicio = tramo[0]
                coord_destino = tramo[1]
                ruta, err = ruta_minima(coord_inicio, coord_destino, G, segmentos)
                if err or ruta is None:
                    errores_conexion.append({
                        "origen": coord_inicio,
                        "destino": coord_destino,
                        "más_cercano_a_origen": min(G.nodes, key=lambda n: np.linalg.norm(np.array(n) - np.array(coord_inicio))),
                        "más_cercano_a_destino": min(G.nodes, key=lambda n: np.linalg.norm(np.array(n) - np.array(coord_destino)))
                    })
                else:
                    if len(tramo) == 2:
                        lineas_MV_o_FO[i][j].append(np.array(ruta).reshape(-1, 2))
                    else:
                        lineas_MV_o_FO[i][j][2] = np.array(ruta).reshape(-1, 2)

    
    return lineas_MV_o_FO, errores_conexion



def medicion_cable_MV(lineas_MV, pol_cable_MV, slack_cable_MV, desnivel_cable_MV, transicion_MV_PCS, transicion_MV_SS, safety_maj_MV):
    
    for i, linea in enumerate(pol_cable_MV):
        if i == 0:
            continue
        for j, tramo in enumerate(linea):      
            if j==0: #el primer elemento de la linea es un string con el nombre "Line x" antes de empezar los tramos, quizas sobra y se puede eliminar
                continue
            else:
                restas_de_coordenadas = np.diff(tramo[2], axis=0)
                distancias_segmentos = np.linalg.norm(restas_de_coordenadas, axis=1)
                distancia = np.nansum(distancias_segmentos)*(1+slack_cable_MV/100)*(1+desnivel_cable_MV/100) + transicion_MV_PCS
                if str(lineas_MV[i][j][1]).startswith('SR'):
                    distancia = distancia + transicion_MV_SS
                else:
                    distancia = distancia + transicion_MV_PCS
                    
                #Añadimos a la lista de lineas la longitud de cada tramo en instalacion y en medicion final [L1 [B1, B2, Pot_acum, med_inst, med]]
                if len(lineas_MV[i][j])==3:
                    lineas_MV[i][j].append(distancia)
                    lineas_MV[i][j].append(distancia*(1+safety_maj_MV/100))           
                else:
                    lineas_MV[i][j][3]=distancia
                    lineas_MV[i][j][4]=distancia*(1+safety_maj_MV/100)    
    
    return lineas_MV


def asignacion_secciones_cable_MV(lineas_MV, criterio_secciones_MV, asignacion_secciones_MV):
    
    if criterio_secciones_MV == 'Manual':
        for i, linea in enumerate(lineas_MV):
            if i == 0:
                continue
            for j, tramo in enumerate(linea): 
                if j==0: #el primer elemento de la linea es un string con el nombre "Line x" antes de empezar los tramos, quizas sobra y se puede eliminar
                    continue
                else:
                    lineas_MV[i][j].append(asignacion_secciones_MV[i][j]) 
                

    elif criterio_secciones_MV == 'Posicion':
        for i, linea in enumerate(lineas_MV):
            if i == 0:
                continue
            for j, tramo in enumerate(linea):
                if j==0: #el primer elemento de la linea es un string con el nombre "Line x" antes de empezar los tramos, quizas sobra y se puede eliminar
                    continue
                else:
                    lineas_MV[i][j].append(asignacion_secciones_MV[j]) 
            
    elif criterio_secciones_MV == 'Potencia':
        for i, linea in enumerate(lineas_MV):
            if i == 0:
                continue
            for j, tramo in enumerate(linea):
                if j==0: #el primer elemento de la linea es un string con el nombre "Line x" antes de empezar los tramos, quizas sobra y se puede eliminar
                    continue
                else:
                    potencia_tramo = tramo[2]
                    potencias = np.array(asignacion_secciones_MV)[:,0].astype(int)
                    potencias_ordenadas = potencias[potencias.argsort()]
                    indices_validos = np.where(potencias_ordenadas <= potencia_tramo)[0]
                    e_max = indices_validos[-1]
                    
                    lineas_MV[i][j].append(asignacion_secciones_MV[e_max]) 
                    
    return lineas_MV




def polilineas_de_circuitos_en_zanjas_DC(i,b,f,f_act,x_punto_activo,y_punto_activo,x_caja,indice_caja,a_caja,h_modulo,p,tipo_salto,pitch,filas_en_cajas,cajas_fisicas,orientacion,sep_zanja_tracker):
    #si la x del punto de la polilinea del cable activo está en el ancho del módulo, estamos en la linea de la caja, solo hay que extender la polilinea hasta su Y

    if abs(x_punto_activo-x_caja) < h_modulo/2+0.1: 
        p=p+1
        if x_punto_activo-x_caja > 0: #paramos antes de tocar la envolvente para que se vea la forma de la caja al meter la zanja, la longitud se considera parte de la transicion
            bord_caja=a_caja/2
        elif x_punto_activo-x_caja < 0:
            bord_caja=-a_caja/2
            
        x_punto_siguiente=x_caja + bord_caja
        y_punto_siguiente=cajas_fisicas[i,b,indice_caja,2] #Y de la caja
        
    else: #si estamos en un punto fuera de la fila de la caja, el siguiente punto estaría en la fila anexa en la dirección de la caja
        #hay que determinar si es hacia la izquierda o hacia la derecha
        if x_caja-x_punto_activo > 0: #si la resta es positiva la caja está a la derecha, si es negativa, a la izquierda #CUIDADO SISTEMAS COORDENADAS NEGATIVOS, POSIBLE OPTIMIZAR
            p=p+1
            #hay dos tipos de salto que van alternándose, el tipo 1 va desde la fila a la parte más cercana de la fila anexa, mientras que el tipo 2 va desde esa parte de la fila hasta el otro lado del módulo
            if tipo_salto==1:
                #Al salir de la primera pica va desde el eje hasta el extremo cercano (+pitch-h_modulo/2)
                if p==2:
                    if orientacion[i,b]=='S':
                        x_punto_siguiente=filas_en_cajas[i,b,f+1,2]-h_modulo/2 #se resta h_modulo/2 a la fila siguiente para no caer bajo la huella del módulo, se para la zanja en la izquierda del tracker, no en el eje
                        y_punto_siguiente=filas_en_cajas[i,b,f+1,3]-sep_zanja_tracker #dependiendo de la orientacion del bloque la y es la de la fila mas la separacion
                        f_act=f+1
                    elif orientacion[i,b]=='N':
                        x_punto_siguiente=filas_en_cajas[i,b,f-1,2]-h_modulo/2 #el signo es porque con orientacion N la fila de la derecha es la anterior
                        y_punto_siguiente=filas_en_cajas[i,b,f-1,3]+sep_zanja_tracker
                        f_act=f-1
                    tipo_salto=2 #si no viniesen de la izq se está saltando a la otra fila por lo que el siguiente salto tiene que ser tipo 2    
                    #EXCEPCION, SI YA VIENE UNA ZANJA DE LA IZQUIERDA (la fila anterior está en la misma caja) NO VAMOS A IR PRACTICAMENTE PARALELOS, AHORRAMOS ZANJA UNIENDOLAS A LA ALTURA DEL EXTREMO DEL MODULO DE LA MISMA FILA  
                    if orientacion[i,b]=='S':
                        if f>0: #el codigo abajo daria error si es la primera fila, en la que ademas nunca se va a dar la excepcion
                            if int(filas_en_cajas[i,b,f,0]) == int(filas_en_cajas[i,b,f-1,0]):
                                    x_punto_siguiente=x_punto_activo+h_modulo/2 #la x es la del extremo del modulo
                                    y_punto_siguiente=filas_en_cajas[i,b,f,3]-sep_zanja_tracker #la Y es la de la fila menos o mas la separacion
                                    f_act=f
                                    tipo_salto=1 #si viene otro de la izq se queda en la fila, sigue siendo salto tipo 1
                    elif orientacion[i,b]=='N':
                        if ~np.isnan(filas_en_cajas[i,b,f+1,0]): #el codigo abajo daria error si es la ultima fila con strings de la banda, en la que ademas nunca se va a dar la excepcion
                            if int(filas_en_cajas[i,b,f,0]) == int(filas_en_cajas[i,b,f+1,0]):
                                    x_punto_siguiente=x_punto_activo+h_modulo/2 
                                    y_punto_siguiente=filas_en_cajas[i,b,f,3]+sep_zanja_tracker #la Y es la de la fila mas la separacion
                                    f_act=f
                                    tipo_salto=1 #si viene otro de la izq se queda en la fila, sigue siendo salto tipo 1
                    #POSIBLE OPTIMIZAR, EN LUGAR DE SEGUIR LA LINEA DE TRACKER CUANDO HAY ESCALERA SE PODRÍA ACORTAR ESTUDIANDO EL POTENCIAL SIGUIENTE SALTO TIPO 1 Y NO TENIENDO EN CUENTA EL TRACKER SIGUIENTE SI HAY MARGEN    
                 #En el resto de saltos tipo 1 se va desde el borde de la fila hasta el borde opuesto de la otra (la x de insercion en filas_en_bandas)
                else: 
                    if orientacion[i,b]=='S':
                        x_punto_siguiente=filas_en_cajas[i,b,f_act+1,2]-h_modulo/2 #para no caer bajo la huella del módulo, se para la zanja en la izquierda del tracker, no en el eje
                        y_punto_siguiente=filas_en_cajas[i,b,f_act+1,3]-sep_zanja_tracker #dependiendo de la orientacion del bloque la y es la de la fila mas la separacion
                        f_act=f_act+1
                    elif orientacion[i,b]=='N': 
                        x_punto_siguiente=filas_en_cajas[i,b,f_act-1,2]-h_modulo/2
                        y_punto_siguiente=filas_en_cajas[i,b,f_act-1,3]+sep_zanja_tracker
                        f_act=f_act-1
                    tipo_salto=2 #actualizamos el tipo de salto para que el siguiente sea hasta el otro lado del tracker si todavia no ha llegado a la fila de la caja     
            
            elif tipo_salto==2:
                x_punto_siguiente=x_punto_activo+h_modulo
                y_punto_siguiente=y_punto_activo #POSIBLE OPTIMIZAR, EN LUGAR DE SEGUIR LA LINEA DE TRACKER CUANDO HAY ESCALERA SE PODRÍA ACORTAR ESTUDIANDO EL POTENCIAL SIGUIENTE SALTO TIPO 1 Y NO TENIENDO EN CUENTA EL TRACKER SIGUIENTE SI HAY MARGEN
                tipo_salto=1   
        else: #si la caja está a la izquierda repetimos invirtiendo signos y dando un +h_mod porque el punto de insercion es a la izquierda
                p=p+1               
                if tipo_salto==1:
                    if p==2:                                                       
                        if orientacion[i,b]=='S':
                            x_punto_siguiente=filas_en_cajas[i,b,f-1,2]+h_modulo/2
                            y_punto_siguiente=filas_en_cajas[i,b,f-1,3]-sep_zanja_tracker #dependiendo de la orientacion del bloque la y es la de la fila mas la separacion
                            f_act=f_act-1
                        elif orientacion[i,b]=='N':
                            x_punto_siguiente=filas_en_cajas[i,b,f+1,2]+h_modulo/2
                            y_punto_siguiente=filas_en_cajas[i,b,f+1,3]+sep_zanja_tracker
                            f_act=f_act+1
                        tipo_salto=2
                        #EXCEPCION
                        if orientacion[i,b]=='S':
                            if ~np.isnan(filas_en_cajas[i,b,f+1,0]): #el codigo abajo daria error si es la ultima fila con strings de la banda, en la que ademas nunca se va a dar la excepcion
                                if int(filas_en_cajas[i,b,f,0]) == int(filas_en_cajas[i,b,f+1,0]):
                                        x_punto_siguiente=x_punto_activo-h_modulo/2 #la x es la del extremo del modulo
                                        y_punto_siguiente=filas_en_cajas[i,b,f,3]-sep_zanja_tracker #la Y es la de la fila menos o mas la separacion
                                        f_act=f
                                        tipo_salto=1 #si viene otro de la izq se queda en la fila, sigue siendo salto tipo 1
                        elif orientacion[i,b]=='N':
                            if f>0: #el codigo abajo daria error si es la primera fila, en la que ademas nunca se va a dar la excepcion
                                if int(filas_en_cajas[i,b,f,0]) == int(filas_en_cajas[i,b,f-1,0]):
                                        x_punto_siguiente=x_punto_activo-h_modulo/2 
                                        y_punto_siguiente=filas_en_cajas[i,b,f,3]+sep_zanja_tracker #la Y es la de la fila mas la separacion
                                        f_act=f
                                        tipo_salto=1 #si viene otro de la izq se queda en la fila, sigue siendo salto tipo 1
                    else:
                        if orientacion[i,b]=='S':
                            x_punto_siguiente=filas_en_cajas[i,b,f_act-1,2]+h_modulo/2
                            y_punto_siguiente=filas_en_cajas[i,b,f_act-1,3]-sep_zanja_tracker #dependiendo de la orientacion del bloque la y es la de la fila mas la separacion
                            f_act=f_act-1
                        elif orientacion[i,b]=='N':
                            x_punto_siguiente=filas_en_cajas[i,b,f_act+1,2]+h_modulo/2
                            y_punto_siguiente=filas_en_cajas[i,b,f_act+1,3]+sep_zanja_tracker
                            f_act=f_act+1
                        tipo_salto=2 #actualizamos el tipo de salto para que el siguiente sea hasta el otro lado del tracker si todavia no ha llegado a la fila de la caja     
                
                elif tipo_salto==2:
                    x_punto_siguiente=x_punto_activo-h_modulo
                    y_punto_siguiente=y_punto_activo #POSIBLE OPTIMIZAR, EN LUGAR DE SEGUIR LA LINEA DE TRACKER CUANDO HAY ESCALERA SE PODRÍA ACORTAR ESTUDIANDO EL POTENCIAL SIGUIENTE SALTO TIPO 1 Y NO TENIENDO EN CUENTA EL TRACKER SIGUIENTE SI HAY MARGEN
                    tipo_salto=1
                            
    return x_punto_siguiente, y_punto_siguiente, tipo_salto, p, f_act



def polilineas_de_circuitos_cable_string(strings_fisicos, filas_en_cajas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_b,max_spf,max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, l_caja, a_caja, dist_primera_pica_extremo_tr):
    
    cable_string=np.full((n_bloques+1,max_b,max_f_str_b,max_spf,max_p,2),np.nan) #POSIBLE OPTIMIZAR, asumimos que no va a haber ningun cable de string con más de 50 puntos (polilinea con mas de 50 puntos), lo ideal quizás sería hacerlo con listas
    tubos_por_bloque = [[] for _ in range(n_bloques+1)]     #Los tubos no tienen porqué estar asociados a una fila concreta, es posible que luego se modifiquen y se decidan incluir más en algún lado o tirarlos desde otra pica, rompemos la asociacion con b y f

    
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b+1):      
                    if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía
                        almacen_destino = []
                        for s in range(0,max_spf):                                  
                            if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío 
                                cable_string[i,b,f,s,0]=strings_fisicos[i,b,f,s,[0,1]]
                                
                                cable_string[i,b,f,s,1,0]=strings_fisicos[i,b,f,0,0] #la x del segundo punto es la misma que la del inicial porque estan en la misma fila (primera pica)
                                if orientacion[i,b]=='S':
                                    cable_string[i,b,f,s,1,1]=strings_fisicos[i,b,f,0,1]+dist_primera_pica_extremo_tr # la Y del segundo punto cae en la del string del extremo menos o mas la distancia a la primera pica dependiendo de si está orientado al N o al S
                                elif orientacion[i,b]=='N':
                                    cable_string[i,b,f,s,1,1]=strings_fisicos[i,b,f,0,1]-dist_primera_pica_extremo_tr #tambien se podia hacer con filas_en_caja pero esto es mas general, se puede reusar codigo en otros casos

                                #A partir de la primera pica tenemos que ver en que fila estamos respecto a la caja para definir los siguientes puntos
                                p=1
                                indice_caja=int(filas_en_cajas[i,b,f,0])
                                x_caja=cajas_fisicas[i,b,indice_caja,1]
                                y_caja=cajas_fisicas[i,b,indice_caja,2]
                                tipo_salto=1 #hay dos tipos de salto como veremos después
                                
                                #si estamos inicialmente en la fila de la caja el recorrido final es inmediato, desde la primera pica a la zanja
                                if cable_string[i,b,f,s,1,0] - x_caja < 0.2: #tolerancia por modificaciones manuales
                                    cable_string[i,b,f,s,2,0] = x_caja
                                    if orientacion[i,b]=='S':
                                        cable_string[i,b,f,s,2,1] = y_caja + l_caja/2 #el l/caja se añade para quedarnos en el borde luego con las zanjas, esta longitud se mete como parte de la transicion
                                    elif orientacion[i,b]=='N':
                                        cable_string[i,b,f,s,2,1] = y_caja - l_caja/2 
                                
                                #si no estamos directamente en esa fila entramos en un while hasta llegar       
                                f_act=f
                                while abs(cable_string[i,b,f,s,p,0]-x_caja) > a_caja/2 + 0.1:
                                                                                                                                                                
                                    cable_string[i,b,f,s,p+1,0], cable_string[i,b,f,s,p+1,1], tipo_salto, p_salida, f_act = polilineas_de_circuitos_en_zanjas_DC(i,b,f,f_act,cable_string[i,b,f,s,p,0],cable_string[i,b,f,s,p,1],x_caja,indice_caja,a_caja,h_modulo,p,tipo_salto,pitch,filas_en_cajas,cajas_fisicas,orientacion,sep_zanja_tracker)
                                    p=p_salida

                                    # if p>max_p: Lo comentamos porque max_p se va a dejar con tamaño de sobra para futuras modificaciones en el CAD
                                    #     max_p=p
                                #El cable termina en el centro de la caja
                                cable_string[i,b,f,s,p+1,0] = x_caja
                                cable_string[i,b,f,s,p+1,1] = y_caja
                                
                                #Vemos si los strings de la fila van a la misma caja o a cajas diferentes
                                if (x_caja,y_caja) in almacen_destino:
                                    pass
                                else:
                                    tubos_por_bloque[i].append(cable_string[i,b,f,s,1:])
                                    almacen_destino.append((x_caja,y_caja))
                        
                                #PENDIENTE OPTIMIZAR - SE PUEDE MEDIR TUBO FIJO CON CODOS TAMBIEN


    
    # ---- conversión de los tubos a array rectangular ----
    max_tubos_bloque = max(len(lst) for lst in tubos_por_bloque)

    pol_tubo_corrugado_zanja_DC = np.full((n_bloques+1, max_tubos_bloque, max_p-1, 2), np.nan)

    for i, lista in enumerate(tubos_por_bloque):
        for t, arr in enumerate(lista):
            L = arr.shape[0]
            pol_tubo_corrugado_zanja_DC[i,t,:L,:] = arr
    
    return cable_string, pol_tubo_corrugado_zanja_DC, max_tubos_bloque

def polilineas_de_circuitos_DC_Bus(filas_en_cajas,filas_en_bandas,cajas_fisicas,orientacion,bloque_inicial,n_bloques,max_b,max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, largo_caja, ancho_caja, dist_primera_pica_extremo_tr, extender_DC_Bus):
    pol_DC_Bus=np.full((n_bloques+1,max_b,max_f_str_b,max_p,2),np.nan) #POSIBLE OPTIMIZAR, asumimos que no va a haber ningun cable de string con más de 50 puntos (polilinea con mas de 50 puntos), lo ideal quizás sería hacerlo con listas
    filas_con_dcb_extendido=np.zeros((n_bloques+1,max_b,max_f_str_b),dtype=bool)
    pol_tubo_corrugado_zanja_DC=np.full((n_bloques+1,max_b,max_f_str_b,max_p-1,2),np.nan)
    
    
    #SE PUEDE HACER POR DENTRO O POR FUERA DEL TORQUE, DE MOMENTO LO HACEMOS POR DENTRO
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            f=0
            if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía         
                for f in range (0,max_f_str_b):
                    if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía
                        #la peculiaridad del DC Bus por dentro del TT es que tiene que llegar hasta el principio del último tracker, si el ultimo tracker no es corto esos strings necesitaran extensiones                            
                        #sacamos el punto de inicio y el de la pica del DCBus
                            #calculamos el tracker mas al sur de la fila, se usa como inicio del DCBus en orientacion N y para la bajada a zanja en el S
                        tf=-1
                        for pos in np.array(filas_en_bandas[i,b,f].T[1]):
                            if ~np.isnan(pos):
                                tf=tf+1
                        
                        if orientacion[i,b]=='S': #si la banda tiene orientacion sur nos quedamos con el primer tracker listado en filas_en_bandas[] para el inicio del bus,su punto de inserción es el más al sur así que dependiendo de si se extiende al final o no se tiene que sumar su longitud                                            
                            pol_DC_Bus[i,b,f,0,0]= filas_en_bandas[i,b,f,0,2]+h_modulo/2 #hay que sumarle la del h_mod porque la x es la de insercion del tracker
                            
                            if extender_DC_Bus[['S','M','L','XL'].index(filas_en_bandas[i,b,f,0,0])]==True: #si se ha elegido extender el DCBus, el punto de partida es la parte mas al N del primer tracker
                                pol_DC_Bus[i,b,f,0,1]= filas_en_bandas[i,b,f,0,3]+filas_en_bandas[i,b,f,0,1]
                                filas_con_dcb_extendido[i,b,f]=True
                            else:
                                pol_DC_Bus[i,b,f,0,1]= filas_en_bandas[i,b,f,0,3] #si no se extiende el dcbus parte directamente del principio de ese tracker
                            
                            pol_DC_Bus[i,b,f,1,0]= filas_en_bandas[i,b,f,0,2]+h_modulo/2    #TODO
                            pol_DC_Bus[i,b,f,1,1]= filas_en_bandas[i,b,f,tf,3]+dist_primera_pica_extremo_tr #SI EL BUS VA POR DENTRO DEL TT SE ESTÁ COMIENDO LA DISTANCIA DE LA PRIMERA PICA, HAY QUE ARREGLARLO
                                    
                        elif orientacion[i,b]=='N': #si la banda tiene orientacion norte nos quedamos con el último tracker listado en filas_en_bandas[]para el inicio del bus,su punto de inserción es el más al sur así que hay que sumarle la longitud del tracker                              
                            pol_DC_Bus[i,b,f,0,0]= filas_en_bandas[i,b,f,tf,2]+h_modulo/2
                            
                            if extender_DC_Bus[['S','M','L','XL'].index(filas_en_bandas[i,b,f,tf,0])]==True: #si se ha elegido extender el DCBus, se saca directamente del punto de insercion del tracker, al S
                                pol_DC_Bus[i,b,f,0,1]= filas_en_bandas[i,b,f,tf,3]
                                filas_con_dcb_extendido[i,b,f]=True
                            else:
                                pol_DC_Bus[i,b,f,0,1]= filas_en_bandas[i,b,f,tf,3]+filas_en_bandas[i,b,f,tf,1] #si no se extiende el DCBus, el punto de partida es la parte mas al N del primer tracker

                            
                            pol_DC_Bus[i,b,f,1,0]= filas_en_bandas[i,b,f,tf,2]+h_modulo/2 
                            pol_DC_Bus[i,b,f,1,1]= filas_en_bandas[i,b,f,0,3]+filas_en_bandas[i,b,f,0,1]-dist_primera_pica_extremo_tr #la pica está en el tracker más al norte + su longitud (el punto de insercion es el sur) menos la distancia del extremo a la primera pica
                        
                #Una vez calculado el punto de inicio y el de la bajada a zanja DC, se puede usar el mismo proceso que para el cable de string, con la funcion de calculo de polilineas en zanjas dc
                for f in range (0,max_f_str_b): 
                    if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía 
                        p=1
                        indice_caja=int(filas_en_cajas[i,b,f,0])
                        x_caja=cajas_fisicas[i,b,indice_caja,1]
                        y_caja=cajas_fisicas[i,b,indice_caja,2]
                        tipo_salto=1 #hay dos tipos de salto como veremos después
                        
                        #si estamos inicialmente en la fila de la caja el recorrido final es inmediato, desde la primera pica a la zanja
                        if pol_DC_Bus[i,b,f,1,0] - x_caja < 0.2:
                            pol_DC_Bus[i,b,f,2,0] = x_caja
                            if orientacion[i,b]=='S':
                                pol_DC_Bus[i,b,f,2,1] = y_caja + largo_caja/2 #el l/caja se añade para quedarnos en el borde luego con las zanjas, esta longitud se mete como parte de la transicion
                            elif orientacion[i,b]=='N':
                                pol_DC_Bus[i,b,f,2,1] = y_caja - largo_caja/2 
                        
                        #si no estamos directamente en esa fila entramos en un while hasta llegar  
                        f_act=f
                        while abs(pol_DC_Bus[i,b,f,p,0]-x_caja) > ancho_caja/2 + 0.1:

                            pol_DC_Bus[i,b,f,p+1,0], pol_DC_Bus[i,b,f,p+1,1], tipo_salto, p_salida, f_act = polilineas_de_circuitos_en_zanjas_DC(i,b,f,f_act,pol_DC_Bus[i,b,f,p,0], pol_DC_Bus[i,b,f,p,1],x_caja,indice_caja,ancho_caja,h_modulo,p,tipo_salto,pitch,filas_en_cajas,cajas_fisicas,orientacion,sep_zanja_tracker)
                            p=p_salida
                        
                        # if p>max_p: Lo comentamos porque max_p se va a dejar con tamaño de sobra para futuras modificaciones en el CAD
                        #     max_p=p                                      
    
                        #El cable termina en el centro de la caja
                        pol_DC_Bus[i,b,f,p+1,0] = x_caja
                        pol_DC_Bus[i,b,f,p+1,1] = y_caja
                        
                        #Tras llegar al final podemos tirar la polilinea para el tubo (1 por fila por defecto)
                        #PENDIENTE OPTIMIZAR - SE PUEDE MEDIR TUBO FIJO CON CODOS TAMBIEN
                        pol_tubo_corrugado_zanja_DC[i,b,f]=pol_DC_Bus[i,b,f,1:]         
    
    #Los tubos no tienen porqué estar asociados a una fila concreta, es posible que luego se modifiquen y se decidan incluir más en algún lado o tirarlos desde otra pica, rompemos la asociacion con b y f, aplanándolos solo en funcion del bloque bxf=t (y borrando aquellos t que estan completamente vacios)
    mask_nan = np.isnan(pol_tubo_corrugado_zanja_DC).all(axis=(0, 3, 4))
    mask_valid = ~mask_nan
    b_valid, f_valid = np.where(mask_valid)
    max_tubos_bloque = len(b_valid)
    valid_segments = [pol_tubo_corrugado_zanja_DC[:, b, f, :, :] for b, f in zip(b_valid, f_valid)]
    pol_tubo_corrugado_zanja_DC_limpio = np.stack(valid_segments, axis=1)    
    
    return pol_DC_Bus, filas_con_dcb_extendido, pol_tubo_corrugado_zanja_DC_limpio, max_tubos_bloque

def polilineas_de_circuitos_both_types(filas_con_cable_string, strings_fisicos, filas_en_cajas, cajas_fisicas, orientacion,bloque_inicial, n_bloques, max_b, max_spf, max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, dist_primera_pica_extremo_tr, filas_en_bandas, largo_caja, ancho_caja, extender_DC_Bus):
    cable_string=np.full((n_bloques+1,max_b,max_f_str_b,max_spf,max_p,2),np.nan) #POSIBLE OPTIMIZAR, asumimos que no va a haber ningun cable de string con más de 50 puntos (polilinea con mas de 50 puntos), lo ideal quizás sería hacerlo con listas
    filas_con_dcb_extendido=np.zeros((n_bloques+1,max_b,max_f_str_b),dtype=bool)
    pol_DC_Bus=np.full((n_bloques+1,max_b,max_f_str_b,max_p,2),np.nan) #POSIBLE OPTIMIZAR, asumimos que no va a haber ningun cable de string con más de 50 puntos (polilinea con mas de 50 puntos), lo ideal quizás sería hacerlo con listas
    pol_tubo_corrugado_zanja_DC=np.full((n_bloques+1,max_b,max_f_str_b,max_p-1,2),np.nan)
    
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b+1):      
                    if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía   
                        if filas_con_cable_string[i,b,f]==True:
                            for s in range(0,max_spf):                                  
                                if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío 
                                    cable_string[i,b,f,s,0]=strings_fisicos[i,b,f,s,[0,1]]
                                    
                                    cable_string[i,b,f,s,1,0]=strings_fisicos[i,b,f,0,0] #la x del segundo punto es la misma que la del inicial porque estan en la misma fila (primera pica)
                                    if orientacion[i,b]=='S':
                                        cable_string[i,b,f,s,1,1]=strings_fisicos[i,b,f,0,1]+dist_primera_pica_extremo_tr # la Y del segundo punto cae en la del string del extremo menos o mas la distancia a la primera pica dependiendo de si está orientado al N o al S
                                    elif orientacion[i,b]=='N':
                                        cable_string[i,b,f,s,1,1]=strings_fisicos[i,b,f,0,1]-dist_primera_pica_extremo_tr #tambien se podia hacer con filas_en_caja pero esto es mas general, se puede reusar codigo en otros casos
    
                                    #A partir de la primera pica tenemos que ver en que fila estamos respecto a la caja para definir los siguientes puntos
                                    p=1
                                    indice_caja=int(filas_en_cajas[i,b,f,0])
                                    x_caja=cajas_fisicas[i,b,indice_caja,1]
                                    y_caja=cajas_fisicas[i,b,indice_caja,2]
                                    tipo_salto=1 #hay dos tipos de salto como veremos después
                                    
                                    #si estamos inicialmente en la fila de la caja el recorrido final es inmediato, desde la primera pica a la zanja
                                    if cable_string[i,b,f,s,1,0] - x_caja < 0.2:
                                        cable_string[i,b,f,s,2,0] = x_caja
                                        if orientacion[i,b]=='S':
                                            cable_string[i,b,f,s,2,1] = y_caja + largo_caja/2 #el l/caja se añade para quedarnos en el borde luego con las zanjas, esta longitud se mete como parte de la transicion
                                        elif orientacion[i,b]=='N':
                                            cable_string[i,b,f,s,2,1] = y_caja - largo_caja/2 
                                    
                                    #si no estamos directamente en esa fila entramos en un while hasta llegar       
                                    f_act=f
                                    while abs(cable_string[i,b,f,s,p,0]-x_caja) > ancho_caja/2 + 0.1:
                                                                                                                                                                    
                                        cable_string[i,b,f,s,p+1,0], cable_string[i,b,f,s,p+1,1], tipo_salto, p_salida, f_act = polilineas_de_circuitos_en_zanjas_DC(i,b,f,f_act,cable_string[i,b,f,s,p,0],cable_string[i,b,f,s,p,1],x_caja,indice_caja,ancho_caja,h_modulo,p,tipo_salto,pitch,filas_en_cajas,cajas_fisicas,orientacion,sep_zanja_tracker)
                                        p=p_salida
    
                                        # if p>max_p:
                                        #     max_p=p Lo comentamos porque max_p se va a dejar con tamaño de sobra para futuras modificaciones en el CAD
                                    
                                    #El cable termina en el centro de la caja
                                    cable_string[i,b,f,s,p+1,0] = x_caja
                                    cable_string[i,b,f,s,p+1,1] = y_caja
                                    
                                    #Tras llegar al final podemos tirar la polilinea para el tubo (1 por fila por defecto)
                                    #PENDIENTE OPTIMIZAR - SE PUEDE MEDIR TUBO FIJO CON CODOS TAMBIEN
                                    pol_tubo_corrugado_zanja_DC[i,b,f]=cable_string[i,b,f,0,1:]     
                                    
                        #SI TODAS TIENEN MAS DEL LIMITE, LA FILA VA CON DCBUS    
                        else:
                            tf=-1
                            for pos in np.array(filas_en_bandas[i,b,f].T[1]):
                                if ~np.isnan(pos):
                                    tf=tf+1
                            
                            if orientacion[i,b]=='S': #si la banda tiene orientacion sur nos quedamos con el primer tracker listado en filas_en_bandas[] para el inicio del bus,su punto de inserción es el más al sur así que dependiendo de si se extiende al final o no se tiene que sumar su longitud                                            
                                pol_DC_Bus[i,b,f,0,0]= filas_en_bandas[i,b,f,0,2]+h_modulo/2 #hay que sumarle la del h_mod porque la x es la de insercion del tracker
                                
                                if extender_DC_Bus[['S','M','L','XL'].index(filas_en_bandas[i,b,f,0,0])]==True: #si se ha elegido extender el DCBus, el punto de partida es la parte mas al N del primer tracker
                                    pol_DC_Bus[i,b,f,0,1]= filas_en_bandas[i,b,f,0,3]+filas_en_bandas[i,b,f,0,1]
                                    filas_con_dcb_extendido[i,b,f]=True
                                else:
                                    pol_DC_Bus[i,b,f,0,1]= filas_en_bandas[i,b,f,0,3] #si no se extiende el dcbus parte directamente del principio de ese tracker
                                
                                pol_DC_Bus[i,b,f,1,0]= filas_en_bandas[i,b,f,0,2]+h_modulo/2 
                                pol_DC_Bus[i,b,f,1,1]= filas_en_bandas[i,b,f,tf,3]+dist_primera_pica_extremo_tr
                                        
                            elif orientacion[i,b]=='N': #si la banda tiene orientacion norte nos quedamos con el último tracker listado en filas_en_bandas[]para el inicio del bus,su punto de inserción es el más al sur así que hay que sumarle la longitud del tracker                              
                                pol_DC_Bus[i,b,f,0,0]= filas_en_bandas[i,b,f,tf,2]+h_modulo/2
                                
                                if extender_DC_Bus[['S','M','L','XL'].index(filas_en_bandas[i,b,f,tf,0])]==True: #si se ha elegido extender el DCBus, se saca directamente del punto de insercion del tracker, al S
                                    pol_DC_Bus[i,b,f,0,1]= filas_en_bandas[i,b,f,tf,3]
                                    filas_con_dcb_extendido[i,b,f]=True
                                else:
                                    pol_DC_Bus[i,b,f,0,1]= filas_en_bandas[i,b,f,tf,3]+filas_en_bandas[i,b,f,tf,1] #si no se extiende el DCBus, el punto de partida es la parte mas al N del primer tracker
    
                                
                                pol_DC_Bus[i,b,f,1,0]= filas_en_bandas[i,b,f,tf,2]+h_modulo/2 
                                pol_DC_Bus[i,b,f,1,1]= filas_en_bandas[i,b,f,0,3]+filas_en_bandas[i,b,f,0,1]-dist_primera_pica_extremo_tr #la pica está en el tracker más al norte + su longitud (el punto de insercion es el sur) menos la distancia del extremo a la primera pica
                                
                #Una vez calculado el punto de inicio y el de la bajada a zanja DC, se puede usar el mismo proceso que para el cable de string, con la funcion de calculo de polilineas en zanjas dc
                for f in range (0,max_f_str_b): 
                    if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía
                        #ESTA MANERA DE COMPLETARLO SOLO ES NECESARIA EN EL CASO DCBUS, SI TODAS LAS FILAS DE LA CAJA TIENEN MAS DEL LIMITE
                        if filas_con_cable_string[i,b,f]==False:
                            p=1
                            indice_caja=int(filas_en_cajas[i,b,f,0])
                            x_caja=cajas_fisicas[i,b,indice_caja,1]
                            y_caja=cajas_fisicas[i,b,indice_caja,2]
                            tipo_salto=1 #hay dos tipos de salto como veremos después
                            
                            #si estamos inicialmente en la fila de la caja el recorrido final es inmediato, desde la primera pica a la zanja
                            if pol_DC_Bus[i,b,f,1,0] - x_caja < 0.2: #no ponemos == x_caja por si hay modificaciones manuales que cambien decimales
                                pol_DC_Bus[i,b,f,2,0] = x_caja
                                if orientacion[i,b]=='S':
                                    pol_DC_Bus[i,b,f,2,1] = y_caja + largo_caja/2 #el l/caja se añade para quedarnos en el borde luego con las zanjas, esta longitud se mete como parte de la transicion
                                elif orientacion[i,b]=='N':
                                    pol_DC_Bus[i,b,f,2,1] = y_caja - largo_caja/2 
                            
                            #si no estamos directamente en esa fila entramos en un while hasta llegar  
                            f_act=f
                            while abs(pol_DC_Bus[i,b,f,p,0]-x_caja) > ancho_caja/2 + 0.1:
    
                                pol_DC_Bus[i,b,f,p+1,0], pol_DC_Bus[i,b,f,p+1,1], tipo_salto, p_salida, f_act = polilineas_de_circuitos_en_zanjas_DC(i,b,f,f_act,pol_DC_Bus[i,b,f,p,0], pol_DC_Bus[i,b,f,p,1],x_caja,indice_caja,ancho_caja,h_modulo,p,tipo_salto,pitch,filas_en_cajas,cajas_fisicas,orientacion,sep_zanja_tracker)
                                p=p_salida
                            
                            # if p>max_p: Lo comentamos porque max_p se va a dejar con tamaño de sobra para futuras modificaciones en el CAD
                            #     max_p=p
                            
                            #El cable termina en el centro de la caja
                            pol_DC_Bus[i,b,f,p+1,0] = x_caja
                            pol_DC_Bus[i,b,f,p+1,1] = y_caja
                            
                            #Tras llegar al final podemos tirar la polilinea para el tubo (1 por fila por defecto)
                            #PENDIENTE OPTIMIZAR - SE PUEDE MEDIR TUBO FIJO CON CODOS TAMBIEN
                            pol_tubo_corrugado_zanja_DC[i,b,f]=pol_DC_Bus[i,b,f,1:]     
                            
    #Los tubos no tienen porqué estar asociados a una fila concreta, es posible que luego se modifiquen y se decidan incluir más en algún lado o tirarlos desde otra pica, rompemos la asociacion con b y f, aplanándolos solo en funcion del bloque bxf=t (y borrando aquellos t que estan completamente vacios)
    mask_nan = np.isnan(pol_tubo_corrugado_zanja_DC).all(axis=(0, 3, 4))
    mask_valid = ~mask_nan
    b_valid, f_valid = np.where(mask_valid)
    max_tubos_bloque = len(b_valid)
    valid_segments = [pol_tubo_corrugado_zanja_DC[:, b, f, :, :] for b, f in zip(b_valid, f_valid)]
    pol_tubo_corrugado_zanja_DC_limpio = np.stack(valid_segments, axis=1)

    
    return cable_string, pol_DC_Bus, filas_con_dcb_extendido, pol_tubo_corrugado_zanja_DC_limpio, max_tubos_bloque

def polilineas_de_circuitos_mixed(filas_con_cable_string, strings_fisicos, filas_en_cajas, cajas_fisicas, orientacion,bloque_inicial, n_bloques, max_b, max_spf, max_f_str_b, max_p, h_modulo, pitch, sep_zanja_tracker, dist_primera_pica_extremo_tr, filas_en_bandas, largo_caja, ancho_caja, extender_DC_Bus):
    cable_string=np.full((n_bloques+1,max_b,max_f_str_b,max_spf,max_p-1,2),np.nan) #POSIBLE OPTIMIZAR, asumimos que no va a haber ningun cable de string con más de 50 puntos (polilinea con mas de 50 puntos), lo ideal quizás sería hacerlo con listas
    filas_con_dcb_extendido=np.zeros((n_bloques+1,max_b,max_f_str_b),dtype=bool)
    pol_DC_Bus=np.full((n_bloques+1,max_b,max_f_str_b,max_p,2),np.nan) #POSIBLE OPTIMIZAR, asumimos que no va a haber ningun cable de string con más de 50 puntos (polilinea con mas de 50 puntos), lo ideal quizás sería hacerlo con listas
    pol_tubo_corrugado_zanja_DC=np.full((n_bloques+1,max_b,max_f_str_b,max_p,2),np.nan)
    
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b+1):      
                    if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía   
                        #SI LA FILA TIENE MENOS STRINGS QUE EL LIMITE PUESTO VAN CON CABLE DE STRING (si se pone 2 sera un tracker M o dos S)
                        if filas_con_cable_string[i,b,f]==True:
                            for s in range(0,max_spf):                                  
                                if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío 
                                    cable_string[i,b,f,s,0]=strings_fisicos[i,b,f,s,[0,1]]
                                    
                                    cable_string[i,b,f,s,1,0]=strings_fisicos[i,b,f,0,0] #la x del segundo punto es la misma que la del inicial porque estan en la misma fila (primera pica)
                                    if orientacion[i,b]=='S':
                                        cable_string[i,b,f,s,1,1]=strings_fisicos[i,b,f,0,1]+dist_primera_pica_extremo_tr # la Y del segundo punto cae en la del string del extremo menos o mas la distancia a la primera pica dependiendo de si está orientado al N o al S
                                    elif orientacion[i,b]=='N':
                                        cable_string[i,b,f,s,1,1]=strings_fisicos[i,b,f,0,1]-dist_primera_pica_extremo_tr #tambien se podia hacer con filas_en_caja pero esto es mas general, se puede reusar codigo en otros casos
    
                                    #A partir de la primera pica tenemos que ver en que fila estamos respecto a la caja para definir los siguientes puntos
                                    p=1
                                    indice_caja=int(filas_en_cajas[i,b,f,0])
                                    x_caja=cajas_fisicas[i,b,indice_caja,1]
                                    y_caja=cajas_fisicas[i,b,indice_caja,2]
                                    tipo_salto=1 #hay dos tipos de salto como veremos después
                                    
                                    #si estamos inicialmente en la fila de la caja el recorrido final es inmediato, desde la primera pica a la zanja
                                    if cable_string[i,b,f,s,1,0] - x_caja < 0.2:
                                        cable_string[i,b,f,s,2,0] = x_caja
                                        if orientacion[i,b]=='S':
                                            cable_string[i,b,f,s,2,1] = y_caja + largo_caja/2 #el l/caja se añade para quedarnos en el borde luego con las zanjas, esta longitud se mete como parte de la transicion
                                        elif orientacion[i,b]=='N':
                                            cable_string[i,b,f,s,2,1] = y_caja - largo_caja/2 
                                    
                                    #si no estamos directamente en esa fila entramos en un while hasta llegar       
                                    f_act=f
                                    while abs(cable_string[i,b,f,s,p,0]-x_caja) > ancho_caja/2 + 0.1:
                                                                                                                                                                    
                                        cable_string[i,b,f,s,p+1,0], cable_string[i,b,f,s,p+1,1], tipo_salto, p_salida, f_act = polilineas_de_circuitos_en_zanjas_DC(i,b,f,f_act,cable_string[i,b,f,s,p,0],cable_string[i,b,f,s,p,1],x_caja,indice_caja,ancho_caja,h_modulo,p,tipo_salto,pitch,filas_en_cajas,cajas_fisicas,orientacion,sep_zanja_tracker)
                                        p=p_salida
    
                                        # if p>max_p: Lo comentamos porque max_p se va a dejar con tamaño de sobra para futuras modificaciones en el CAD
                                        #     max_p=p
                                    
                                    #El cable termina en el centro de la caja
                                    cable_string[i,b,f,s,p+1,0] = x_caja
                                    cable_string[i,b,f,s,p+1,1] = y_caja
                                    
                                    #Tras llegar al final podemos tirar la polilinea para el tubo (1 por fila por defecto)
                                    #PENDIENTE OPTIMIZAR - SE PUEDE MEDIR TUBO FIJO CON CODOS TAMBIEN
                                    pol_tubo_corrugado_zanja_DC[i,b,f]=cable_string[i,b,f,0,1:]  
    
                        #SI LA FILA TIENE MAS DEL LIMITE VA CON DC BUS    
                        else:
                            tf=-1
                            for pos in np.array(filas_en_bandas[i,b,f].T[1]):
                                if ~np.isnan(pos):
                                    tf=tf+1
                            
                            if orientacion[i,b]=='S': #si la banda tiene orientacion sur nos quedamos con el primer tracker listado en filas_en_bandas[] para el inicio del bus,su punto de inserción es el más al sur así que dependiendo de si se extiende al final o no se tiene que sumar su longitud                                            
                                pol_DC_Bus[i,b,f,0,0]= filas_en_bandas[i,b,f,0,2]+h_modulo/2 #hay que sumarle la del h_mod porque la x es la de insercion del tracker
                                
                                if extender_DC_Bus[['S','M','L','XL'].index(filas_en_bandas[i,b,f,0,0])]==True: #si se ha elegido extender el DCBus, el punto de partida es la parte mas al N del primer tracker
                                    pol_DC_Bus[i,b,f,0,1]= filas_en_bandas[i,b,f,0,3]+filas_en_bandas[i,b,f,0,1]
                                    filas_con_dcb_extendido[i,b,f]=True
                                else:
                                    pol_DC_Bus[i,b,f,0,1]= filas_en_bandas[i,b,f,0,3] #si no se extiende el dcbus parte directamente del principio de ese tracker
                                
                                pol_DC_Bus[i,b,f,1,0]= filas_en_bandas[i,b,f,0,2]+h_modulo/2 
                                pol_DC_Bus[i,b,f,1,1]= filas_en_bandas[i,b,f,tf,3]+dist_primera_pica_extremo_tr
                                        
                            elif orientacion[i,b]=='N': #si la banda tiene orientacion norte nos quedamos con el último tracker listado en filas_en_bandas[]para el inicio del bus,su punto de inserción es el más al sur así que hay que sumarle la longitud del tracker                              
                                pol_DC_Bus[i,b,f,0,0]= filas_en_bandas[i,b,f,tf,2]+h_modulo/2
                                
                                if extender_DC_Bus[['S','M','L','XL'].index(filas_en_bandas[i,b,f,tf,0])]==True: #si se ha elegido extender el DCBus, se saca directamente del punto de insercion del tracker, al S
                                    pol_DC_Bus[i,b,f,0,1]= filas_en_bandas[i,b,f,tf,3]
                                    filas_con_dcb_extendido[i,b,f]=True
                                else:
                                    pol_DC_Bus[i,b,f,0,1]= filas_en_bandas[i,b,f,tf,3]+filas_en_bandas[i,b,f,tf,1] #si no se extiende el DCBus, el punto de partida es la parte mas al N del primer tracker
    
                                
                                pol_DC_Bus[i,b,f,1,0]= filas_en_bandas[i,b,f,tf,2]+h_modulo/2 
                                pol_DC_Bus[i,b,f,1,1]= filas_en_bandas[i,b,f,0,3]+filas_en_bandas[i,b,f,0,1]-dist_primera_pica_extremo_tr #la pica está en el tracker más al norte + su longitud (el punto de insercion es el sur) menos la distancia del extremo a la primera pica
                            
                #Una vez calculado el punto de inicio y el de la bajada a zanja DC, se puede usar el mismo proceso que para el cable de string, con la funcion de calculo de polilineas en zanjas dc
                for f in range (0,max_f_str_b): 
                    if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía
                        #ESTA MANERA DE COMPLETARLO SOLO ES NECESARIA EN EL CASO DCBUS
                        if filas_con_cable_string[i,b,f]==False:
                            p=1
                            indice_caja=int(filas_en_cajas[i,b,f,0])
                            x_caja=cajas_fisicas[i,b,indice_caja,1]
                            y_caja=cajas_fisicas[i,b,indice_caja,2]
                            tipo_salto=1 #hay dos tipos de salto como veremos después
                            
                            #si estamos inicialmente en la fila de la caja el recorrido final es inmediato, desde la primera pica a la zanja
                            if pol_DC_Bus[i,b,f,1,0] - x_caja < 0.2: #tolerancia por modificaciones manuales
                                pol_DC_Bus[i,b,f,2,0] = x_caja
                                if orientacion[i,b]=='S':
                                    pol_DC_Bus[i,b,f,2,1] = y_caja + largo_caja/2 #el l/caja se añade para quedarnos en el borde luego con las zanjas, esta longitud se mete como parte de la transicion
                                elif orientacion[i,b]=='N':
                                    pol_DC_Bus[i,b,f,2,1] = y_caja - largo_caja/2 
                            
                            #si no estamos directamente en esa fila entramos en un while hasta llegar  
                            f_act=f
                            while abs(pol_DC_Bus[i,b,f,p,0]-x_caja) > ancho_caja/2 + 0.1:
    
                                pol_DC_Bus[i,b,f,p+1,0], pol_DC_Bus[i,b,f,p+1,1], tipo_salto, p_salida, f_act = polilineas_de_circuitos_en_zanjas_DC(i,b,f,f_act,pol_DC_Bus[i,b,f,p,0], pol_DC_Bus[i,b,f,p,1],x_caja,indice_caja,ancho_caja,h_modulo,p,tipo_salto,pitch,filas_en_cajas,cajas_fisicas,orientacion,sep_zanja_tracker)
                                p=p_salida
                            
                            # if p>max_p: Lo comentamos porque max_p se va a dejar con tamaño de sobra para futuras modificaciones en el CAD
                            #     max_p=p       
                            
                            #El cable termina en el centro de la caja
                            pol_DC_Bus[i,b,f,p+1,0] = x_caja
                            pol_DC_Bus[i,b,f,p+1,1] = y_caja
                            
                            #Tras llegar al final podemos tirar la polilinea para el tubo (1 por fila por defecto)
                            #PENDIENTE OPTIMIZAR - SE PUEDE MEDIR TUBO FIJO CON CODOS TAMBIEN
                            pol_tubo_corrugado_zanja_DC[i,b,f]=cable_string[i,b,f,0,1:]  
    
    #Los tubos no tienen porqué estar asociados a una fila concreta, es posible que luego se modifiquen y se decidan incluir más en algún lado o tirarlos desde otra pica, rompemos la asociacion con b y f, aplanándolos solo en funcion del bloque bxf=t (y borrando aquellos t que estan completamente vacios)
    mask_nan = np.isnan(pol_tubo_corrugado_zanja_DC).all(axis=(0, 3, 4))
    mask_valid = ~mask_nan
    b_valid, f_valid = np.where(mask_valid)
    max_tubos_bloque = len(b_valid)
    valid_segments = [pol_tubo_corrugado_zanja_DC[:, b, f, :, :] for b, f in zip(b_valid, f_valid)]
    pol_tubo_corrugado_zanja_DC_limpio = np.stack(valid_segments, axis=1)
                            
    return cable_string, pol_DC_Bus, filas_con_cable_string, filas_con_dcb_extendido, pol_tubo_corrugado_zanja_DC_limpio, max_tubos_bloque





def pol_cable_string_en_inv_string(strings_fisicos, inv_string, posiciones, equi_ibv_to_fs, contorno_inf, contorno_sup, ori_str_ID, orientacion,
                                    strings_ID, bloque_inicial, n_bloques, max_b, max_inv, max_spf, max_f_str_b,
                                    max_p, h_modulo, pitch, sep_zanja_tracker, largo_caja, ancho_caja, dist_primera_pica_extremo_tr):

    cable_string = np.full((n_bloques+1, max_b, max_f_str_b, max_spf, max_p, 2), np.nan)
    pol_tubo_corrugado_zanja_DC = np.full((n_bloques+1, max_b, max_f_str_b, max_p-1, 2), np.nan)
    tubos_por_bloque = [[] for _ in range(n_bloques+1)]

    for i in range(bloque_inicial, n_bloques+1):
        for b in range(0, max_b):
            for f in range(0, max_f_str_b+1):
                almacen_destino=[]
                for s in range(0, max_spf):
                    if not np.isnan(strings_fisicos[i, b, f, s, 0]):
                        # Sacamos el ID global correspondiente a este string
                        sid = int(strings_fisicos[i, b, f, s, 2])
                        

                        # Coordenadas , buscamos en strings_ID que es la que ya tiene los strings girados
                        indice_match = np.where(strings_ID[...,4] == sid)
                        i_match, board_match, inv_match, s_match = indice_match[0][0], indice_match[1][0], indice_match[2][0], indice_match[3][0]
                        
                        x_string = strings_ID[i_match, board_match, inv_match, s_match, 1]
                        y_string = strings_ID[i_match, board_match, inv_match, s_match, 3] #la y_final, ya girada
                        cable_string[i, b, f, s, 0] = [x_string, y_string]

                        # Primera pica
                        cable_string[i, b, f, s, 1, 0] = strings_fisicos[i, b, f, 0, 0] #es equivalente a la seleccionada en strings_ID, permanece en la misma x
                        if ori_str_ID[sid][1] == 'S':
                            cable_string[i, b, f, s, 1, 1] = contorno_inf[i,b,f,1] + dist_primera_pica_extremo_tr
                        elif ori_str_ID[sid][1] == 'N':
                            cable_string[i, b, f, s, 1, 1] = contorno_sup[i,b,f,1] - dist_primera_pica_extremo_tr

                        # Buscamos a qué inversor está asociado el string sacando sus indices en inv_string 
                        matches_inv = np.argwhere(inv_string[..., 2] == sid)
                        if matches_inv.size == 0:
                            continue
                        i_inv, b_inv, inv, s_inv = matches_inv[0]
                        

                        # Posición inversor físico
                        x_caja = posiciones[i, b_inv, inv, 0]
                        y_caja = posiciones[i, b_inv, inv, 1]

                        # Definimos una banda de referencia fisica por la que se va moviendo el cable, inicialmente es la banda de origen, pero puede llegar a cambiar si se salta antes de encontrar el string:
                        b_ref = b


                        p = 1
                        tipo_salto = 1
                        f_act = f


                        if abs(cable_string[i, b, f, s, 1, 0] - x_caja) < 0.2:
                            p += 1
                            cable_string[i, b, f, s, p, 0] = x_caja
                            #Añadimos punto en el borde de la caja
                            if ori_str_ID[sid][1] == 'N':
                                cable_string[i, b, f, s, p, 1] = y_caja - largo_caja/2
                            elif ori_str_ID[sid][1] == 'S':
                                cable_string[i, b, f, s, p, 1] = y_caja + largo_caja/2
                            
                            #El cable acaba en el centro de la caja
                            p+=1
                            cable_string[i, b, f, s, p, 0] = x_caja
                            cable_string[i, b, f, s, p, 1] = y_caja
                                
                        else:
                            sentido_anterior = np.sign(x_caja - cable_string[i, b, f, s, p, 0]) if orientacion[i,b_ref] == 'S' else -np.sign(x_caja - cable_string[i, b, f, s, p, 0]) #inicializamos el sentido inicial para que sea igual
                            
                            while abs(cable_string[i, b, f, s, p, 0] - x_caja) > h_modulo/2 + 0.2:
                                x_actual = cable_string[i, b, f, s, p, 0]
                                y_actual = cable_string[i, b, f, s, p, 1]
                                
                                if orientacion[i,b_ref] == 'S':
                                    sentido = np.sign(x_caja - x_actual)
                                elif orientacion[i,b_ref] == 'N':
                                    sentido = np.sign(x_actual - x_caja) #cuando la banda esta orientada al norte las filas avanzan en sentido contrario, se invierte el sentido

                                if sentido_anterior != sentido: #si los strings de inversores en distintas bandas estan desalineados puede que al hacer un salto de fila nos pasemos, nos tenemos que quedar en el medio
                                    cable_string[i, b, f, s, p, 0] = x_caja
                                    cable_string[i, b, f, s, p, 1] = cable_string[i, b, f, s, p-1, 1] if abs(cable_string[i, b, f, s, p-1, 1] - y_caja) > abs(cable_string[i, b, f, s, p+1, 1] - y_caja) else cable_string[i, b, f, s, p, 1] #cogemos la y de donde viene que esté mas cercana al inversor
                                    break
                                
                                if tipo_salto == 1:                                       
                                    f_next = f_act + int(sentido)
                                    if (0 <= f_next <= max_f_str_b):        
                                        if ori_str_ID[sid][1] == 'N':
                                            fila_data = contorno_sup[i,b_ref,f_next]
                                        elif ori_str_ID[sid][1] == 'S':
                                            fila_data = contorno_inf[i,b_ref,f_next]
                                       
                                        if not np.isnan(fila_data[0]):
                                            #Determinamos si estamos en una fila extremo dentro de las asociadas a ese inversor o en una intermedia para reconducir el trazado
                                            filas = equi_ibv_to_fs[i, b, inv, :, 1]
                                            if np.all(np.isnan(filas)):
                                                print(f"[Advertencia] Todas las filas son NaN en bloque {i}, banda {b}, inversor {inv}")
                                                f_max_inv = f_min_inv = np.nan  # Evita el warning
                                            else:
                                                f_max_inv = np.nanmax(filas)
                                                f_min_inv = np.nanmin(filas)

                                            
                                            if f_act == f_max_inv or f_act == f_min_inv:
                                                f_rel_extremo = True
                                            else:
                                                f_rel_extremo = False
                                                                                    
                                            if p==1 and f_rel_extremo == False:    
                                                #Si acaba de salir de la pica y está en una fila intermedia no va directo a la fila siguiente sino al extremo del tracker en el mismo sentido
                                                x_next = x_actual + sentido * h_modulo/2 if orientacion[i,b_ref] == 'S' else x_actual - sentido * h_modulo/2
                                                y_next = contorno_inf[i,b,f,1] - sep_zanja_tracker if ori_str_ID[sid][1] == 'S' else contorno_sup[i,b,f,1] + sep_zanja_tracker
                                                tipo_salto == 1 #despues viene un salto a la siguiente fila
                                            else:
                                                #Situacion normal, salto a la siguiente fila, o fila de inicio, este salto al principio ahorra angulos fuertes evitables
                                                x_next = fila_data[0] - sentido * h_modulo/2 if orientacion[i,b_ref] == 'S' else fila_data[0] + sentido * h_modulo/2
                                                y_next = fila_data[1] - sep_zanja_tracker if ori_str_ID[sid][1] == 'S' else fila_data[1] + sep_zanja_tracker
                                                f_act = f_next
                                                tipo_salto = 2
                                        else:
                                            # Si no hay fila, forzamos salto directo
                                            x_next = x_actual + sentido * h_modulo
                                            y_next = y_actual
                                    else:
                                        #Si llega al final de la banda y no se ha puesto en el inversor de string (porque esta en otra banda) hacemos que salte hasta la altura de la otra banda
                                        b_ref = b_inv
                                        
                                        x_vals = strings_fisicos[i, b_ref, :, 0, 0]
                                        dist_x_caja = np.abs(x_vals - x_caja)
                                        dist_actual = np.abs(x_actual - x_caja)
                                                                               
                                        # Filtramos los que están más cerca a x_caja que x_actual
                                        mask = dist_x_caja < dist_actual + pitch/2 #tolerancia
                                        x_valids = x_vals[mask]
                                        
                                        if len(x_valids) == 0:
                                            raise ValueError("No hay valores válidos hacia la caja")
                                        
                                        # Elegimos el más cercano a x_actual
                                        f_next_virtual = np.argmin(np.abs(x_valids - x_actual))
                                        
                                        # Recuperamos el índice original en strings_fisicos (porque mask ha reducido el array)
                                        idxs_valids = np.where(mask)[0]
                                        f_next = idxs_valids[f_next_virtual]

                                        if ori_str_ID[sid][1] == 'N': #se cambian las orientaciones porque ha habido un salto a la banda opuesta
                                            ori_str_ID[sid][1] == 'S'
                                            fila_data = contorno_sup[i,b_ref,f_next]
                                        elif ori_str_ID[sid][1] == 'S':
                                            ori_str_ID[sid][1] == 'N'
                                            fila_data = contorno_inf[i,b_ref,f_next]
                                            
                                        x_next = fila_data[0] - sentido * h_modulo/2 if orientacion[i,b_ref] == 'S' else fila_data[0] + sentido * h_modulo/2
                                        y_next = fila_data[1] - sep_zanja_tracker if ori_str_ID[sid][1] == 'S' else fila_data[1] + sep_zanja_tracker
                                        
                                        f_act = f_next
                                        tipo_salto = 2

                                elif tipo_salto == 2:
                                    x_next = x_actual + sentido * h_modulo if orientacion[i,b_ref] == 'S' else x_actual - sentido * h_modulo
                                    y_next = y_actual
                                    tipo_salto = 1

                                p += 1
                                if p >= max_p:
                                    print(f"Se excede el máximo de puntos en i={i}, b={b}, f={f}, s={s}")
                                    break
                                cable_string[i, b, f, s, p, 0] = x_next
                                cable_string[i, b, f, s, p, 1] = y_next
                                
                                sentido_anterior = sentido

                            p += 1
                            if p < max_p:
                                #Creamos punto en el borde del inversor para luego terminar la zanja aqui
                                cable_string[i, b, f, s, p, 0] = x_caja + ancho_caja/2 * sentido if ori_str_ID[sid][1] == 'N' else x_caja - ancho_caja/2 * sentido
                                cable_string[i, b, f, s, p, 1] = y_caja
                                
                                p+=1
                                cable_string[i, b, f, s, p, 0] = x_caja
                                cable_string[i, b, f, s, p, 1] = y_caja


                        #Vemos si los strings de la fila van al mismo inversor o a cajas diferentes
                        if (x_caja,y_caja) in almacen_destino:
                            pass
                        else:
                            tubos_por_bloque[i].append(cable_string[i,b,f,s,1:])
                            almacen_destino.append((x_caja,y_caja))
                
                        #PENDIENTE OPTIMIZAR - SE PUEDE MEDIR TUBO FIJO CON CODOS TAMBIEN


    
    # ---- conversión de los tubos a array rectangular ----
    max_tubos_bloque = max(len(lst) for lst in tubos_por_bloque)

    pol_tubo_corrugado_zanja_DC = np.full((n_bloques+1, max_tubos_bloque, max_p-1, 2), np.nan)

    for i, lista in enumerate(tubos_por_bloque):
        for t, arr in enumerate(lista):
            L = arr.shape[0]
            pol_tubo_corrugado_zanja_DC[i,t,:L,:] = arr


    return cable_string, pol_tubo_corrugado_zanja_DC, max_tubos_bloque









def medicion_cable_string(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_c_block, masc, max_inv_block, max_str_pinv, max_p, DCBoxes_o_Inv_String, strings_fisicos, strings_ID, pol_cable_string, equi_ibfs, Interconexionado, Polo_cercano, ancho_modulo, saliente_TT, desplaz_x_cable_modulos, dist_ext_opuesto_str, transicion_cable_string_tracker, transicion_cable_string_caja, slack_cable_string, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, mayoracion_cable_string, mayoracion_tubo_corrugado_zanja_DC, criterio_seccion, lim_dist_sld_seccion, lim_loc_seccion, secciones_cs, filas_con_cable_string, dos_inv, cajas_fisicas):
    #Como la función está construida para cajas los nombres respecto a inversores de string varían, pero la funcionalidad es la misma
    if DCBoxes_o_Inv_String == 'String Inverters':
        masc = max_str_pinv
        max_c_block = max_inv_block
        
    tramo_aereo_cable_string_pos=np.full((n_bloques+1,3,max_c_block+1,1,masc+1),np.nan)
    tramo_aereo_cable_string_neg=np.copy(tramo_aereo_cable_string_pos)
    tramo_subterraneo_cable_string=np.copy(tramo_aereo_cable_string_pos)
    
    med_inst_cable_string_pos=np.full((n_bloques+1,3,max_c_block+1,1,masc+1,2),np.nan) #la creamos como tramo aereo pero le metemos un elemento mas en al ultima dimension para incluir la seccion
    med_inst_cable_string_neg=np.copy(med_inst_cable_string_pos)
    med_cable_string_pos=np.copy(med_inst_cable_string_pos)
    med_cable_string_neg=np.copy(med_inst_cable_string_pos)

    sch_cable_de_string_pos=np.full((n_bloques+1,3,max_c_block+1,1,masc+1,3),np.nan, dtype=object)
    sch_cable_de_string_neg=np.copy(sch_cable_de_string_pos)
    
    med_tubo_corrugado_zanja_DC=np.full((n_bloques+1,max_b,max_f_str_b),np.nan)
    
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(strings_fisicos[i,0,0,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b+1):      
                    if ~np.isnan(strings_fisicos[i,b,f,0,0]) and filas_con_cable_string[i,b,f]==True: #si la fila no está vacía y la configuración es de cable de string            
                        for s in range(0,max_spf):                                  
                            if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío 
                            
                            #PASAMOS LA INFO CLASIFICADA POR BANDA Y FILA FISICA A POR CAJA DEL BLOQUE
                                if DCBoxes_o_Inv_String == 'DC Boxes':
                                    inv=int(equi_ibfs[i,b,f,s,1])
                                    caja=int(equi_ibfs[i,b,f,s,2])
                                    stri=int(equi_ibfs[i,b,f,s,4])
                                else:
                                    sid = strings_fisicos[i,b,f,s,2]
                                    matches = np.argwhere(strings_ID[..., 4] == sid)[0]
                                    i_match, board_match, inv_match, str_match = matches
                                    
                                    #Como la función está construida para cajas los nombres respecto a inversores de string varían, pero la funcionalidad es la misma
                                    inv=board_match
                                    caja=inv_match
                                    stri=str_match
                                                                        
                                    
                                if Interconexionado == 'Leapfrog':
                                    if Polo_cercano == 'Positive':
                                        tramo_aereo_cable_string_pos[i,inv,caja,0,stri]=(abs(pol_cable_string[i,b,f,s,0,1]-pol_cable_string[i,b,f,s,1,1]) + ancho_modulo/2 + saliente_TT + desplaz_x_cable_modulos)*(1+slack_cable_string/100) * (1+desnivel_cable_por_pendientes_tramo_aereo/100)
                                        tramo_aereo_cable_string_neg[i,inv,caja,0,stri]=(abs(pol_cable_string[i,b,f,s,0,1]-pol_cable_string[i,b,f,s,1,1]) + ancho_modulo/2 + ancho_modulo + saliente_TT + desplaz_x_cable_modulos)*(1+slack_cable_string/100) * (1+desnivel_cable_por_pendientes_tramo_aereo/100)
                                    elif Polo_cercano == 'Negative':
                                        tramo_aereo_cable_string_pos[i,inv,caja,0,stri]=(abs(pol_cable_string[i,b,f,s,0,1]-pol_cable_string[i,b,f,s,1,1]) + ancho_modulo/2 + ancho_modulo + saliente_TT + desplaz_x_cable_modulos)*(1+slack_cable_string/100) * (1+desnivel_cable_por_pendientes_tramo_aereo/100)
                                        tramo_aereo_cable_string_neg[i,inv,caja,0,stri]=(abs(pol_cable_string[i,b,f,s,0,1]-pol_cable_string[i,b,f,s,1,1]) + ancho_modulo/2 + saliente_TT + desplaz_x_cable_modulos)*(1+slack_cable_string/100) * (1+desnivel_cable_por_pendientes_tramo_aereo/100)

                                elif Interconexionado == 'Daisy chain':
                                    if Polo_cercano == 'Positive':
                                        tramo_aereo_cable_string_pos[i,inv,caja,0,stri]=(abs(pol_cable_string[i,b,f,s,0,1]-pol_cable_string[i,b,f,s,1,1]) + ancho_modulo/2 + saliente_TT + desplaz_x_cable_modulos)*(1+slack_cable_string/100) * (1+desnivel_cable_por_pendientes_tramo_aereo/100)
                                        tramo_aereo_cable_string_neg[i,inv,caja,0,stri]=(abs(pol_cable_string[i,b,f,s,0,1]-pol_cable_string[i,b,f,s,1,1]) + desplaz_x_cable_modulos + dist_ext_opuesto_str[i,inv,caja,0,stri] - ancho_modulo/2 - saliente_TT)*(1+slack_cable_string/100) * (1+desnivel_cable_por_pendientes_tramo_aereo/100)
                                    elif Polo_cercano == 'Negative':
                                        tramo_aereo_cable_string_pos[i,inv,caja,0,stri]=(abs(pol_cable_string[i,b,f,s,0,1]-pol_cable_string[i,b,f,s,1,1]) + desplaz_x_cable_modulos + dist_ext_opuesto_str[i,inv,caja,0,stri] - ancho_modulo/2 - saliente_TT)*(1+slack_cable_string/100) * (1+desnivel_cable_por_pendientes_tramo_aereo/100)
                                        tramo_aereo_cable_string_neg[i,inv,caja,0,stri]=(abs(pol_cable_string[i,b,f,s,0,1]-pol_cable_string[i,b,f,s,1,1]) + ancho_modulo/2 + saliente_TT + desplaz_x_cable_modulos)*(1+slack_cable_string/100) * (1+desnivel_cable_por_pendientes_tramo_aereo/100)
                            
                            #Calculamos el tramo subterráneo
                                restas_de_coordenadas = np.diff(pol_cable_string[i,b,f,s,1:], axis=0)
                                distancias_subterraneas = np.linalg.norm(restas_de_coordenadas, axis=1)
                                tramo_subterraneo_cable_string[i,inv,caja,0,stri]=np.nansum(distancias_subterraneas)*(1+slack_cable_string/100) * (1+desnivel_cable_por_pendientes_tramo_subt/100) #POSIBLE OPTIMIZAR VALOR PLANO + PENDIENTE CONSERVADORA

                                #Podemos aprovechar y medir el tubo desde cada fila de tracker hasta la caja 
                                if s==0:
                                    med_tubo_corrugado_zanja_DC[i,b,f]=np.nansum(distancias_subterraneas)*(1+mayoracion_tubo_corrugado_zanja_DC/100) + transicion_cable_string_caja
                                    
                                
                            #Calculamos el total
                                med_inst_cable_string_pos[i,inv,caja,0,stri,0]=tramo_aereo_cable_string_pos[i,inv,caja,0,stri] + transicion_cable_string_tracker + tramo_subterraneo_cable_string[i,inv,caja,0,stri] + transicion_cable_string_caja
                                med_inst_cable_string_neg[i,inv,caja,0,stri,0]=tramo_aereo_cable_string_neg[i,inv,caja,0,stri] + transicion_cable_string_tracker + tramo_subterraneo_cable_string[i,inv,caja,0,stri] + transicion_cable_string_caja
                                
                                #ASIGNACION DE SECCIONES
                                    #Criterio de distancia
                                if criterio_seccion == 'Distance':
                                    if med_inst_cable_string_pos[i,inv,caja,0,stri,0]+med_inst_cable_string_neg[i,inv,caja,0,stri,0] <= lim_dist_sld_seccion[0] * 2: #los dos polos
                                        med_inst_cable_string_pos[i,inv,caja,0,stri,1]=secciones_cs[0]
                                        med_inst_cable_string_neg[i,inv,caja,0,stri,1]=secciones_cs[0]
                                        
                                    elif med_inst_cable_string_pos[i,inv,caja,0,stri,0]+med_inst_cable_string_neg[i,inv,caja,0,stri,0] <= lim_dist_sld_seccion[1] * 2:
                                        med_inst_cable_string_pos[i,inv,caja,0,stri,1]=secciones_cs[1]
                                        med_inst_cable_string_neg[i,inv,caja,0,stri,1]=secciones_cs[1]
                                        
                                    else:
                                        med_inst_cable_string_pos[i,inv,caja,0,stri,1]=secciones_cs[2]
                                        med_inst_cable_string_neg[i,inv,caja,0,stri,1]=secciones_cs[2]
                                    #Criterio de posicion   
                                elif criterio_seccion == 'No. strings':
                                    if med_inst_cable_string_pos[i,inv,caja,0,stri,0]+med_inst_cable_string_neg[i,inv,caja,0,stri,0] <= lim_loc_seccion[0] * 2:
                                        med_inst_cable_string_pos[i,inv,caja,0,stri,1]=secciones_cs[0]
                                        med_inst_cable_string_neg[i,inv,caja,0,stri,1]=secciones_cs[0] 
                                        
                                    elif med_inst_cable_string_pos[i,inv,caja,0,stri,0]+med_inst_cable_string_neg[i,inv,caja,0,stri,0] <= lim_loc_seccion[1] * 2:
                                        med_inst_cable_string_pos[i,inv,caja,0,stri,1]=secciones_cs[1]
                                        med_inst_cable_string_neg[i,inv,caja,0,stri,1]=secciones_cs[1]
                                        
                                    else:
                                        med_inst_cable_string_pos[i,inv,caja,0,stri,1]=secciones_cs[2]
                                        med_inst_cable_string_neg[i,inv,caja,0,stri,1]=secciones_cs[2]
                                        
                                #obtenemos la medicion final para compra incluyendo la mayoracion de seguridad
                                med_cable_string_pos[i,inv,caja,0,stri,0] = med_inst_cable_string_pos[i,inv,caja,0,stri,0] * (1+mayoracion_cable_string/100)
                                med_cable_string_neg[i,inv,caja,0,stri,0] = med_inst_cable_string_neg[i,inv,caja,0,stri,0] * (1+mayoracion_cable_string/100)
                                #copiamos la seccion
                                med_cable_string_pos[i,inv,caja,0,stri,1] = med_inst_cable_string_pos[i,inv,caja,0,stri,1] 
                                med_cable_string_neg[i,inv,caja,0,stri,1] = med_inst_cable_string_neg[i,inv,caja,0,stri,1]
                                

                                #Sacamos schedules de cables
                                if dos_inv:
                                    sch_cable_de_string_pos[i,inv,caja,0,stri,0]=f"SC-{i}.{inv}.{caja}.{stri}.+"
                                    sch_cable_de_string_neg[i,inv,caja,0,stri,0]=f"SC-{i}.{inv}.{caja}.{stri}.-"
                                else:
                                    sch_cable_de_string_pos[i,inv,caja,0,stri,0]=f"SC-{i}.{caja}.{stri}.+"
                                    sch_cable_de_string_neg[i,inv,caja,0,stri,0]=f"SC-{i}.{caja}.{stri}.-"
                                
                                sch_cable_de_string_pos[i,inv,caja,0,stri,1]=med_inst_cable_string_pos[i,inv,caja,0,stri,1]
                                sch_cable_de_string_neg[i,inv,caja,0,stri,1]=med_inst_cable_string_neg[i,inv,caja,0,stri,1]
                                
                                sch_cable_de_string_pos[i,inv,caja,0,stri,2]=med_inst_cable_string_pos[i,inv,caja,0,stri,0]
                                sch_cable_de_string_neg[i,inv,caja,0,stri,2]=med_inst_cable_string_neg[i,inv,caja,0,stri,0]
                                    
                                
    
    return med_inst_cable_string_pos, tramo_aereo_cable_string_pos, med_inst_cable_string_neg, med_cable_string_pos, med_cable_string_neg, sch_cable_de_string_pos, sch_cable_de_string_neg, med_tubo_corrugado_zanja_DC
           



def medicion_DC_Bus(bloque_inicial,n_bloques, max_b, max_f_str_b, max_p, max_c_block, max_bus, filas_en_cajas, pol_DC_Bus, equi_ibfs, Interconexionado, Polo_cercano, dist_ext_opuesto_str, desnivel_cable_por_pendientes_tramo_aereo, desnivel_cable_por_pendientes_tramo_subt, transicion_DC_Bus_tracker, transicion_DC_Bus_caja, coca_DC_Bus, extension_primer_tracker, slack_DC_Bus, mayoracion_DC_Bus, mayoracion_tubo_corrugado_zanja_DC, criterio_seccion, lim_dist_sld_seccion, lim_loc_seccion, secciones_dcb, extender_DC_Bus, filas_con_dcb_extendido, filas_con_cable_string, dos_inv, cajas_fisicas):
    tramo_aereo_DC_Bus_pos=np.full((n_bloques+1,3,max_c_block+1,max_bus+1),np.nan)
    tramo_subterraneo_DC_Bus=np.copy(tramo_aereo_DC_Bus_pos)
    
    med_inst_DC_Bus_pos=np.full((n_bloques+1,3,max_c_block+1,max_bus+1,2),np.nan) #la creamos como tramo aereo pero le metemos un elemento mas en al ultima dimension para incluir la seccion
    med_inst_DC_Bus_neg=np.copy(med_inst_DC_Bus_pos)
    med_DC_Bus_pos=np.copy(med_inst_DC_Bus_pos)
    med_DC_Bus_neg=np.copy(med_inst_DC_Bus_pos)
    
    sch_DC_Bus_pos=np.full((n_bloques+1,3,max_c_block+1,max_bus+1,4),np.nan, dtype=object)
    sch_DC_Bus_neg=np.copy(sch_DC_Bus_pos)
    
    med_tubo_corrugado_zanja_DC=np.full((n_bloques+1,max_b,max_f_str_b),np.nan)
    

    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b+1):      
                    if ~np.isnan(filas_en_cajas[i,b,f,0]) and filas_con_cable_string[i,b,f]==False: #si la fila no está vacía y la configuracion es con DCBus
                        
                    #PASAMOS LA INFO CLASIFICADA POR BANDA Y FILA FISICA A POR CAJA DEL BLOQUE
                        inv =int(equi_ibfs[i,b,f,0,1])
                        caja=int(equi_ibfs[i,b,f,0,2])
                        bus =int(equi_ibfs[i,b,f,0,3])
                    
                    #no distinguimos entre tresbolillo o ida y vuelta porque se van a tirar hasta el mismo punto, se extiendan o no, por eso basta con calcular el positivo y copiar el negativo
                        if filas_con_dcb_extendido[i,b,f]==True:
                            tramo_aereo_DC_Bus_pos[i,inv,caja,bus]=(abs(pol_DC_Bus[i,b,f,0,1]-pol_DC_Bus[i,b,f,1,1]) + extension_primer_tracker + coca_DC_Bus)*(1+slack_DC_Bus/100) * (1+desnivel_cable_por_pendientes_tramo_aereo/100)
                        else:
                            tramo_aereo_DC_Bus_pos[i,inv,caja,bus]=(abs(pol_DC_Bus[i,b,f,0,1]-pol_DC_Bus[i,b,f,1,1]) + coca_DC_Bus*2)*(1+slack_DC_Bus/100) * (1+desnivel_cable_por_pendientes_tramo_aereo/100)

                    #Calculamos el tramo subterráneo
                        restas_de_coordenadas = np.diff(pol_DC_Bus[i,b,f,1:], axis=0)
                        distancias_subterraneas = np.linalg.norm(restas_de_coordenadas, axis=1)
                        tramo_subterraneo_DC_Bus[i,inv,caja,bus]=np.nansum(distancias_subterraneas)*(1+slack_DC_Bus/100)
                    #Calculamos el total
                        med_inst_DC_Bus_pos[i,inv,caja,bus,0]=tramo_aereo_DC_Bus_pos[i,inv,caja,bus] + transicion_DC_Bus_tracker + tramo_subterraneo_DC_Bus[i,inv,caja,bus] + transicion_DC_Bus_caja

                        #ASIGNACION DE SECCIONES
                            #Criterio de distancia
                        if criterio_seccion == 'Distance':
                            if med_inst_DC_Bus_pos[i,inv,caja,bus,0] <= lim_dist_sld_seccion[0]*2:
                                med_inst_DC_Bus_pos[i,inv,caja,bus,1]=secciones_dcb[0]
     
                            elif med_inst_DC_Bus_pos[i,inv,caja,bus,0] <= lim_dist_sld_seccion[1]*2:
                                med_inst_DC_Bus_pos[i,inv,caja,bus,1]=secciones_dcb[1] 
                                
                            else:
                                med_inst_DC_Bus_pos[i,inv,caja,bus,1]=secciones_dcb[2]
                                
                            #Criterio de posicion   
                        elif criterio_seccion == 'No. strings': #es equivalente al numero de strings que lleva el dc bus, el numero de string en el que se conectara
                            if med_inst_DC_Bus_pos[i,inv,caja,bus,0] <= lim_loc_seccion[0]:
                                med_inst_DC_Bus_pos[i,inv,caja,bus,1]=secciones_dcb[0]
                                
                            elif med_inst_DC_Bus_pos[i,inv,caja,bus,0] <= lim_loc_seccion[1]:
                                med_inst_DC_Bus_pos[i,inv,caja,bus,1]=secciones_dcb[1]
                                
                            else:
                                med_inst_DC_Bus_pos[i,inv,caja,bus,1]=secciones_dcb[2]
                                
                               
                        #obtenemos la medicion final para compra incluyendo la mayoracion de seguridad
                        med_DC_Bus_pos[i,inv,caja,bus,0] = med_inst_DC_Bus_pos[i,inv,caja,bus,0] * (1+mayoracion_DC_Bus/100)

                        #copiamos la seccion
                        med_DC_Bus_pos[i,inv,caja,bus,1] = med_inst_DC_Bus_pos[i,inv,caja,bus,1]
                        
                        #Copiamos el negativo y el positivo
                        med_inst_DC_Bus_neg[i,inv,caja,bus] = med_inst_DC_Bus_pos[i,inv,caja,bus]
                        med_DC_Bus_neg[i,inv,caja,bus] = med_DC_Bus_pos[i,inv,caja,bus]
                    
                    
                        #Sacamos schedules de cables
                        #POSIBLE OPTIMIZAR QUITANDO INV SI SOLO HAY UN INVERSOR
                        sch_DC_Bus_pos[i,inv,caja,bus,0]=f"DCBus-{i}.{inv}.{caja}.{bus}.+"
                        sch_DC_Bus_neg[i,inv,caja,bus,0]=f"DCBus-{i}.{inv}.{caja}.{bus}.-"
                        
                        sch_DC_Bus_pos[i,inv,caja,bus,1]=filas_en_cajas[i,b,f,1]
                        sch_DC_Bus_neg[i,inv,caja,bus,1]=filas_en_cajas[i,b,f,1]                      
                        
                        sch_DC_Bus_pos[i,inv,caja,bus,2]=med_inst_DC_Bus_pos[i,inv,caja,bus,1]
                        sch_DC_Bus_neg[i,inv,caja,bus,2]=med_inst_DC_Bus_neg[i,inv,caja,bus,1]
                        
                        sch_DC_Bus_pos[i,inv,caja,bus,3]=med_inst_DC_Bus_pos[i,inv,caja,bus,0]
                        sch_DC_Bus_neg[i,inv,caja,bus,3]=med_inst_DC_Bus_neg[i,inv,caja,bus,0]
                            
                        #MEDICION DE TUBO, PENDIENTE DE OPTIMIZAR CON MAYORACION                     
                        med_tubo_corrugado_zanja_DC[i,b,f]=np.nansum(distancias_subterraneas)*(1+mayoracion_tubo_corrugado_zanja_DC/100) + transicion_DC_Bus_caja
                        
                    
    
    return med_inst_DC_Bus_pos, med_inst_DC_Bus_neg, med_DC_Bus_pos, tramo_aereo_DC_Bus_pos, med_DC_Bus_neg, sch_DC_Bus_pos, sch_DC_Bus_neg, med_tubo_corrugado_zanja_DC


def insercion_y_medicion_de_harness(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, max_tpf, filas_en_bandas, filas_con_cable_string, strings_ID, orientacion, String_o_Bus, Interconexionado, extender_DC_Bus, Polo_cercano, strings_fisicos, ori_str_ID, dist_ext_opuesto_str):
    #MEDICION HARNESS
    harness_pos=np.empty((n_bloques+1,max_b,max_f_str_b,max_spf+1,6), dtype=object) #creamos un array hasta el nivel de strings dandole un hueco mas porque la referencia del harness siempre es al espacio antes del string referenciado, por lo que si el ultimo string fuese hacia atras su hueco se define con un string adicional virtual, seis elementos, lista con strings asociados, nº de strings en el harness y numeros de extensiones de 1st, 2 str, 3str y 4 str utilizadas
    harness_pos[:] = np.nan #habia que hacerlo tipo object porque en 0 lleva una lista
    harness_neg=np.copy(harness_pos)
    #hacemos dos auxiliares de harness polo cercano y lejano por si la configuracion es ida y vuelta y el string acaba en lugares diferentes
    harness_p_cer=np.copy(harness_pos)
    harness_p_lej=np.copy(harness_pos)
    
    filas_en_bandas_giradas = np.empty((n_bloques + 1, max_b, max_f_str_b, max_tpf+1, 4), dtype=object) #le damos una dimension mas al tracker porque luego hay evaluaciones tr+1
    filas_en_bandas_giradas[:] = np.nan
    filas_en_bandas_giradas[:, :, :, :max_tpf, :] = filas_en_bandas

    def girar_string_asociado(orient_str,ori_banda, str_ID_info, y_fis_str, long_str): #definimos una funcion interna para girar el string
        if orient_str == 'S':
            orient_str = 'N'
        elif orient_str == 'N':
            orient_str = 'S'
            
        if ori_banda=='N' and orient_str == 'S': #si se ha girado el string
                str_ID_info[0,2] =  y_fis_str #si el string se ha girado ahora empieza en el N (punto original de strings_fisicos)y acaba en el S
                str_ID_info[0,3] =  y_fis_str-long_str 
                
        elif ori_banda=='S' and orient_str == 'N': #si se ha girado el string        
                str_ID_info[0,2] =  y_fis_str #si el string se ha girado ahora empieza en el S (punto original de strings_fisicos) y acaba en el N
                str_ID_info[0,3] =  y_fis_str+long_str 
        return orient_str, str_ID_info
    
    for i in range(bloque_inicial, n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(filas_en_bandas[i,b,0,0,1]): #si la banda no está vacía       
                for f in range(0,max_f_str_b):      
                    if ~np.isnan(filas_en_bandas[i,b,f,0,1]): #si la fila no está vacía
                        if String_o_Bus == 'DC Bus' or ((String_o_Bus == 'Both types' or String_o_Bus == 'Mixed') and filas_con_cable_string[i,b,f] == False): #Si la fila es de DCBus
                            #Giramos los de orientacion contaria
                            if orientacion[i,b]=='S': #vamos a recorrelos del tracker mas cercano al mas lejano asi que hay que hacer un reverse en la sur
                                indices_non_nan = ~np.isnan(filas_en_bandas_giradas[i,b,f,:,1].astype(float))
                                valores_non_nan_invertidos = filas_en_bandas_giradas[i,b,f,indices_non_nan,0][::-1]
                                filas_en_bandas_giradas[i,b,f,indices_non_nan,0] = valores_non_nan_invertidos
                            
                            #Inicializamos la primera columna en [] y el resto en en 0
                            for s in range(0,max_spf+1):
                                harness_pos[i,b,f,s,0]=[]
                            
                            harness_pos[i,b,f,:,1:]=0
                            
                            harness_neg[i,b,f]=harness_pos[i,b,f]
                            harness_p_cer[i,b,f]=harness_pos[i,b,f]
                            harness_p_lej[i,b,f]=harness_pos[i,b,f]
                            #Comenzamos el rellenos de los harness_pos
                            s_acum=0
                            for tr in range(0,max_tpf):
                                if ~np.isnan(filas_en_bandas[i,b,f,tr,1]): #si el tracker no está vacío
                                    if Interconexionado == 'Leapfrog': #solucion para tresbolillo, si los dos polos acaban en el lado cercano
        #TODO cambiar los L POR M Y XL POR L
        
                                        if filas_en_bandas_giradas[i,b,f,tr,0] == 'S': #corto, solo hay un string, siempre va hacia abajo
                                            harness_pos[i,b,f,s_acum,0].append(s_acum)
                                            harness_pos[i,b,f,s_acum,1] = harness_pos[i,b,f,s_acum,1] + 1
                                            s_acum=s_acum+1
                                            
                                        elif filas_en_bandas_giradas[i,b,f,tr,0] == 'M': #medio, hay dos strings, el primero va siempre hacia abajo
                                            if ~np.isnan(filas_en_bandas_giradas[i,b,f,tr+1,1]): #si ademas hay un tracker despues, interesa tirar el segundo hacia "arriba"
                                                harness_pos[i,b,f,s_acum,0].append(s_acum)
                                                harness_pos[i,b,f,s_acum,1] = harness_pos[i,b,f,s_acum,1] + 1
                                                
                                                harness_pos[i,b,f,s_acum+2,0].append(s_acum+1)
                                                harness_pos[i,b,f,s_acum+2,1] = harness_pos[i,b,f,s_acum+2,1] + 1                      
                                                #giramos la orientacion del string asociado
                                                indice_str_planta = strings_fisicos[i,b,f,s_acum+1,2]
                                                indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+1,1],dist_ext_opuesto_str[i,b,f,s_acum+1])
                                                
                                                
                                            else: #estamos ya en el tracker final, el segundo va tambien hacia abajo con una extension corta (1 str)
                                                harness_pos[i,b,f,s_acum,0].append(s_acum)
                                                harness_pos[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_pos[i,b,f,s_acum,1] = harness_pos[i,b,f,s_acum,1] + 2
                                                harness_pos[i,b,f,s_acum,2] = harness_pos[i,b,f,s_acum,2] + 1
                                            s_acum=s_acum+2
                                            
                                        elif filas_en_bandas_giradas[i,b,f,tr,0] == 'L': #largo, hay tres strings, como vamos al tresbolillo, el segundo string interesa tirarlo hacia abajo siempre, el tercero dependerá del precio de extension y bus y si hay tracker despues o no
                                            if ~np.isnan(filas_en_bandas_giradas[i,b,f,tr+1,1]): #hay un tracker despues, por lo que siempre interesa tirar el tercero hacia "arriba"
                                                harness_pos[i,b,f,s_acum,0].append(s_acum)
                                                harness_pos[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_pos[i,b,f,s_acum,1] = harness_pos[i,b,f,s_acum,1] + 2
                                                harness_pos[i,b,f,s_acum,2] = harness_pos[i,b,f,s_acum,2] + 1
                                                
                                                harness_pos[i,b,f,s_acum+3,0].append(s_acum+2)
                                                harness_pos[i,b,f,s_acum+3,1] = harness_pos[i,b,f,s_acum+3,1] + 1
                                                indice_str_planta = strings_fisicos[i,b,f,s_acum+2,2]
                                                indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+2,1],dist_ext_opuesto_str[i,b,f,s_acum+2])
                                                
                                            else: #estamos ya en el tracker final, dependiendo de costes puede interesar extender el bus
                                                harness_pos[i,b,f,s_acum,0].append(s_acum)
                                                harness_pos[i,b,f,s_acum,0].append(s_acum+1)
                                                
                                                harness_pos[i,b,f,s_acum,1] = harness_pos[i,b,f,s_acum,1] + 2
                                                harness_pos[i,b,f,s_acum,2] = harness_pos[i,b,f,s_acum,2] + 1
                                                
                                                
                                                if extender_DC_Bus[0] == 'Yes': #si se extiende el dcbus, el tercer string va hacia arriba
                                                    harness_pos[i,b,f,s_acum+3,0].append(s_acum+2)
                                                    harness_pos[i,b,f,s_acum+3,1] = harness_pos[i,b,f,s_acum+3,1] + 1
                                                    indice_str_planta = strings_fisicos[i,b,f,s_acum+2,2]
                                                    indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                    ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+2,1],dist_ext_opuesto_str[i,b,f,s_acum+2])
                                                    
                                                else: #si no se extiende, se tira una string extension de 2 strings al principio del tracker
                                                    harness_pos[i,b,f,s_acum,0].append(s_acum+2)
                                                    harness_pos[i,b,f,s_acum,1] = harness_pos[i,b,f,s_acum,1] + 1
                                                    harness_pos[i,b,f,s_acum,3] = harness_pos[i,b,f,s_acum,3] + 1                                            
                                            s_acum=s_acum+3
                                            
                                        elif filas_en_bandas_giradas[i,b,f,tr,0] == 'XL': #extralargo, hay cuatro strings, tresbolillo, los dos primeros van abajo si o si, los dos ultimos dependiendo de si hay un tracker despues o se extiende el dc bus
                                            if ~np.isnan(filas_en_bandas_giradas[i,b,f,tr+1,1]): #hay un tracker despues, se considera que interesa tirar el tercero hacia arriba tambien para ahorrar cable de string aunque las perdidas puedan ser algo mayores
                                                harness_pos[i,b,f,s_acum,0].append(s_acum)
                                                harness_pos[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_pos[i,b,f,s_acum,1] = harness_pos[i,b,f,s_acum,1] + 2
                                                harness_pos[i,b,f,s_acum,2] = harness_pos[i,b,f,s_acum,2] + 1
                                                
                                                harness_pos[i,b,f,s_acum+4,0].append(s_acum+2)
                                                harness_pos[i,b,f,s_acum+4,0].append(s_acum+3)
                                                harness_pos[i,b,f,s_acum+4,1] = harness_pos[i,b,f,s_acum+4,1] + 2
                                                harness_pos[i,b,f,s_acum+4,2] = harness_pos[i,b,f,s_acum+4,2] + 1
                                                
                                                indice_str_planta = strings_fisicos[i,b,f,s_acum+2,2]
                                                indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+2,1],dist_ext_opuesto_str[i,b,f,s_acum+2])
                                                
                                                indice_str_planta = strings_fisicos[i,b,f,s_acum+3,2]
                                                indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+3,1],dist_ext_opuesto_str[i,b,f,s_acum+3])
                                                
                                            else: #si es el tracker final hay que ver si se extiende o no el DC Bus
                                                #los dos primeros van abajo como antes
                                                harness_pos[i,b,f,s_acum,0].append(s_acum)
                                                harness_pos[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_pos[i,b,f,s_acum,1] = harness_pos[i,b,f,s_acum,1] + 2
                                                harness_pos[i,b,f,s_acum,2] = harness_pos[i,b,f,s_acum,2] + 1
                                                
                                                if extender_DC_Bus[1] == 'Yes': #si se extiende el dcbus, el tercer y cuarto string van hacia arriba, otra opcion seria subir solo el cuarto pero se entiende que asi se ahorra cable, si bien no se sabe si aumentan las perdidas o no
                                                    harness_pos[i,b,f,s_acum+4,0].append(s_acum+2)
                                                    harness_pos[i,b,f,s_acum+4,0].append(s_acum+3)
                                                    harness_pos[i,b,f,s_acum+4,1] = harness_pos[i,b,f,s_acum+4,1] + 2
                                                    harness_pos[i,b,f,s_acum+4,2] = harness_pos[i,b,f,s_acum+4,2] + 1
                                                    
                                                    indice_str_planta = strings_fisicos[i,b,f,s_acum+2,2]
                                                    indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                    ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+2,1],dist_ext_opuesto_str[i,b,f,s_acum+2])
                                                    
                                                    indice_str_planta = strings_fisicos[i,b,f,s_acum+3,2]
                                                    indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                    ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+3,1],dist_ext_opuesto_str[i,b,f,s_acum+3])                                               
                                                    
                                                else: #si no se extiende, se tiran string extensions de 2 y 3 strings al principio del tracker
                                                    harness_pos[i,b,f,s_acum,0].append(s_acum+2)
                                                    harness_pos[i,b,f,s_acum,1] = harness_pos[i,b,f,s_acum,1] + 2
                                                    harness_pos[i,b,f,s_acum,2] = harness_pos[i,b,f,s_acum,2] + 1
                                                    harness_pos[i,b,f,s_acum,3] = harness_pos[i,b,f,s_acum,3] + 1
                                            s_acum=s_acum+4         
                                        #Igualamos positivo y negativo al ser al tresbolillo
                                        harness_neg[i,b,f]=harness_pos[i,b,f]
                                                                       
                                    elif Interconexionado == 'Daisy chain': #solucion para tresbolillo, si los dos polos acaban en el lado cercano

        
                                        if filas_en_bandas_giradas[i,b,f,tr,0] == 'S': #corto, solo hay un string, en el polo cercano se conecta directo y en el lejano se pone una extension corta o se conecta directo dependiendo de si luego viene otro tracker o no
                                            harness_p_cer[i,b,f,s_acum,0].append(s_acum)
                                            harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                            
                                            if ~np.isnan(filas_en_bandas_giradas[i,b,f,tr+1,1]): #si hay un tracker despues, el polo alejado se puede conectar arriba directamente
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                            else:
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                harness_p_lej[i,b,f,s_acum,2] = harness_p_lej[i,b,f,s_acum,2] + 1
                                                
                                                indice_str_planta = strings_fisicos[i,b,f,s_acum,2]
                                                indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum,1],dist_ext_opuesto_str[i,b,f,s_acum])
                                            
                                            s_acum=s_acum+1
                                            
                                        elif filas_en_bandas_giradas[i,b,f,tr,0] == 'M': #medio, hay dos strings, los dos polos del primero van siempre hacia abajo, el segundo dependerá
                                            if ~np.isnan(filas_en_bandas_giradas[i,b,f,tr+1,1]): #si hay un tracker despues, interesa tirar el segundo hacia "arriba" tambien para los dos polos
                                                #Primer string
                                                harness_p_cer[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                harness_p_lej[i,b,f,s_acum,2] = harness_p_lej[i,b,f,s_acum,2] + 1
                                                
                                                #Segundo string, el polo cercano ahora esta en realidad mas lejos del punto de conexion y necesita extension
                                                harness_p_cer[i,b,f,s_acum+2,0].append(s_acum+1)
                                                harness_p_cer[i,b,f,s_acum+2,1] = harness_p_cer[i,b,f,s_acum+2,1] + 1
                                                harness_p_cer[i,b,f,s_acum+2,2] = harness_p_cer[i,b,f,s_acum+2,2] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum+2,0].append(s_acum+1)
                                                harness_p_lej[i,b,f,s_acum+2,1] = harness_p_lej[i,b,f,s_acum+2,1] + 1
                                                
                                                indice_str_planta = strings_fisicos[i,b,f,s_acum+1,2]
                                                indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+1,1],dist_ext_opuesto_str[i,b,f,s_acum+1])
                                                
                                            else: #estamos ya en el tracker final, el segundo va tambien hacia abajo con una extension de 1 str en el polo cercano y una de 2 str en el otro
                                                #Primer string
                                                harness_p_cer[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                harness_p_lej[i,b,f,s_acum,2] = harness_p_lej[i,b,f,s_acum,2] + 1
                                                
                                                #Segundo string
                                                harness_p_cer[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                harness_p_cer[i,b,f,s_acum,2] = harness_p_cer[i,b,f,s_acum,2] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                harness_p_lej[i,b,f,s_acum,3] = harness_p_lej[i,b,f,s_acum,3] + 1
                                                
                                            s_acum=s_acum+2
                                            
                                        elif filas_en_bandas_giradas[i,b,f,tr,0] == 'L': #largo, hay tres strings, como vamos en config ida y vuelta habria que hacer una extension de 3 strings, el segundo string interesa tirarlo hacia abajo siempre, el tercero dependerá del precio de extension y bus y si hay tracker despues o no
                                            if ~np.isnan(filas_en_bandas_giradas[i,b,f,tr+1,1]): #hay un tracker despues, por lo que siempre interesa tirar el tercero hacia "arriba"
                                                #Primer string, el cercano se conecta directo y el lejano con extension de 1str
                                                harness_p_cer[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                harness_p_lej[i,b,f,s_acum,2] = harness_p_lej[i,b,f,s_acum,2] + 1
                                                
                                                #Segundo string, el cercano tiene extension de 1 string y el lejano de 2 str
                                                harness_p_cer[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                harness_p_cer[i,b,f,s_acum,2] = harness_p_cer[i,b,f,s_acum,2] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                harness_p_lej[i,b,f,s_acum,3] = harness_p_lej[i,b,f,s_acum,3] + 1
                                                
                                                #Tercer string, el cercano ahora esta mas lejos del punto de conexion, necesita una extension de 1 str
                                                harness_p_cer[i,b,f,s_acum+3,0].append(s_acum+2)
                                                harness_p_cer[i,b,f,s_acum+3,1] = harness_p_cer[i,b,f,s_acum+3,1] + 1
                                                harness_p_cer[i,b,f,s_acum+3,2] = harness_p_cer[i,b,f,s_acum+3,2] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum+3,0].append(s_acum+2)
                                                harness_p_lej[i,b,f,s_acum+3,1] = harness_p_lej[i,b,f,s_acum+3,1] + 1
                                                
                                                indice_str_planta = strings_fisicos[i,b,f,s_acum+2,2]
                                                indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+2,1],dist_ext_opuesto_str[i,b,f,s_acum+2])
                                                
                                                
                                            else: #estamos ya en el tracker final, dependiendo de costes puede interesar extender el bus, si se extiende el caso es identico al anterior, si no se extiende entonces se necesita una string extension de 3 str (caso Carwarp)
                                                #Primer string, el cercano se conecta directo y el lejano con extension de 1str
                                                harness_p_cer[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                harness_p_lej[i,b,f,s_acum,2] = harness_p_lej[i,b,f,s_acum,2] + 1
                                                
                                                #Segundo string, el cercano tiene extension de 1 string y el lejano de 2 str
                                                harness_p_cer[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                harness_p_cer[i,b,f,s_acum,2] = harness_p_cer[i,b,f,s_acum,2] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                harness_p_lej[i,b,f,s_acum,3] = harness_p_lej[i,b,f,s_acum,3] + 1
                                                
                                                #Tercer string
                                                if extender_DC_Bus[0] == 'Yes': #si se extiende el dcbus, el tercer string va hacia arriba como antes
                                                    harness_p_cer[i,b,f,s_acum+3,0].append(s_acum+2)
                                                    harness_p_cer[i,b,f,s_acum+3,1] = harness_p_cer[i,b,f,s_acum+3,1] + 1
                                                    harness_p_cer[i,b,f,s_acum+3,2] = harness_p_cer[i,b,f,s_acum+3,2] + 1
                                                    
                                                    harness_p_lej[i,b,f,s_acum+3,0].append(s_acum+2)
                                                    harness_p_lej[i,b,f,s_acum+3,1] = harness_p_lej[i,b,f,s_acum+3,1] + 1
                                                    
                                                    indice_str_planta = strings_fisicos[i,b,f,s_acum+2,2]
                                                    indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                    ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+3,1],dist_ext_opuesto_str[i,b,f,s_acum+3])
                                                    
                                                else: #si no se extiende, se tira una string extension de 2 strings de largo para el cercano y otra de 3 strings de largo para el polo lejano
                                                    harness_p_cer[i,b,f,s_acum,0].append(s_acum+2)
                                                    harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                    harness_p_cer[i,b,f,s_acum,3] = harness_p_cer[i,b,f,s_acum,3] + 1
                                                    
                                                    harness_p_lej[i,b,f,s_acum,0].append(s_acum+2)
                                                    harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                    harness_p_lej[i,b,f,s_acum,4] = harness_p_lej[i,b,f,s_acum,4] + 1                                          
                                            s_acum=s_acum+3
                                            
                                            
                                        elif filas_en_bandas_giradas[i,b,f,tr,0] == 'XL': #extralargo, hay cuatro strings, tresbolillo, hay que extender el array ya si o si
                                            if ~np.isnan(filas_en_bandas_giradas[i,b,f,tr+1,1]): #hay un tracker despues, por lo que siempre interesa el cuarto hacia "arriba", el tercero se asume que interesa tambien para ahorrar cable aunque puedan subir las perdidas
                                                #Primer string, el cercano se conecta directo y el lejano con extension de 1str
                                                harness_p_cer[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                harness_p_lej[i,b,f,s_acum,2] = harness_p_lej[i,b,f,s_acum,2] + 1
                                                
                                                #Segundo string, el cercano tiene extension de 1 string y el lejano de 2 str
                                                harness_p_cer[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                harness_p_cer[i,b,f,s_acum,2] = harness_p_cer[i,b,f,s_acum,2] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                harness_p_lej[i,b,f,s_acum,3] = harness_p_lej[i,b,f,s_acum,3] + 1
                                                
                                                #Tercer string, se asumen que va hacia arriba, pero los string extension son un string mas largos que en el caso anterior
                                                harness_p_cer[i,b,f,s_acum+3,0].append(s_acum+2)
                                                harness_p_cer[i,b,f,s_acum+3,1] = harness_p_cer[i,b,f,s_acum+3,1] + 1
                                                harness_p_cer[i,b,f,s_acum+3,3] = harness_p_cer[i,b,f,s_acum+3,3] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum+3,0].append(s_acum+2)
                                                harness_p_lej[i,b,f,s_acum+3,1] = harness_p_lej[i,b,f,s_acum+3,1] + 1
                                                harness_p_lej[i,b,f,s_acum+3,2] = harness_p_lej[i,b,f,s_acum+3,2] + 1
                                                
                                                indice_str_planta = strings_fisicos[i,b,f,s_acum+2,2]
                                                indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+2,1],dist_ext_opuesto_str[i,b,f,s_acum+2])
                                                
                                                #Cuarto string, hacia arriba, similar al tercero en el caso L anterior
                                                harness_p_cer[i,b,f,s_acum+4,0].append(s_acum+3)
                                                harness_p_cer[i,b,f,s_acum+4,1] = harness_p_cer[i,b,f,s_acum+4,1] + 1
                                                harness_p_cer[i,b,f,s_acum+4,2] = harness_p_cer[i,b,f,s_acum+4,2] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum+4,0].append(s_acum+3)
                                                harness_p_lej[i,b,f,s_acum+4,1] = harness_p_lej[i,b,f,s_acum+4,1] + 1
                                                
                                                indice_str_planta = strings_fisicos[i,b,f,s_acum+3,2]
                                                indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+3,1],dist_ext_opuesto_str[i,b,f,s_acum+3])
                                                
                                            else: #estamos ya en el tracker final, dependiendo de costes puede interesar extender el bus, si se extiende el caso es identico al anterior, si no se extiende entonces se necesita una string extension de 4 str
                                                #Primer string, el cercano se conecta directo y el lejano con extension de 1str
                                                harness_p_cer[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                harness_p_lej[i,b,f,s_acum,2] = harness_p_lej[i,b,f,s_acum,2] + 1
                                                
                                                #Segundo string, el cercano tiene extension de 1 string y el lejano de 2 str
                                                harness_p_cer[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                harness_p_cer[i,b,f,s_acum,2] = harness_p_cer[i,b,f,s_acum,2] + 1
                                                
                                                harness_p_lej[i,b,f,s_acum,0].append(s_acum+1)
                                                harness_p_lej[i,b,f,s_acum,1] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                harness_p_lej[i,b,f,s_acum,3] = harness_p_lej[i,b,f,s_acum,3] + 1
                                                
                                                
                                                if extender_DC_Bus[1] == 'Yes': #si se extiende el dcbus, el tercer y cuarto string van hacia arriba como antes
                                                    #Tercer string
                                                    harness_p_cer[i,b,f,s_acum+3,0].append(s_acum+2)
                                                    harness_p_cer[i,b,f,s_acum+3,1] = harness_p_cer[i,b,f,s_acum+3,1] + 1
                                                    harness_p_cer[i,b,f,s_acum+3,3] = harness_p_cer[i,b,f,s_acum+3,3] + 1
                                                    
                                                    harness_p_lej[i,b,f,s_acum+3,0].append(s_acum+2)
                                                    harness_p_lej[i,b,f,s_acum+3,1] = harness_p_lej[i,b,f,s_acum+3,1] + 1
                                                    harness_p_lej[i,b,f,s_acum+3,2] = harness_p_lej[i,b,f,s_acum+3,2] + 1
                                                    
                                                    indice_str_planta = strings_fisicos[i,b,f,s_acum+2,2]
                                                    indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                    ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+2,1],dist_ext_opuesto_str[i,b,f,s_acum+2])
                                                    
                                                    #Cuarto string
                                                    harness_p_cer[i,b,f,s_acum+4,0].append(s_acum+3)
                                                    harness_p_cer[i,b,f,s_acum+4,1] = harness_p_cer[i,b,f,s_acum+4,1] + 1
                                                    harness_p_cer[i,b,f,s_acum+4,2] = harness_p_cer[i,b,f,s_acum+4,2] + 1
                                                    
                                                    harness_p_lej[i,b,f,s_acum+4,0].append(s_acum+3)
                                                    harness_p_lej[i,b,f,s_acum+4,1] = harness_p_lej[i,b,f,s_acum+4,1] + 1                                                
                                                    
                                                    indice_str_planta = strings_fisicos[i,b,f,s_acum+3,2]
                                                    indices_str_ID = np.where(strings_ID[...,4] == indice_str_planta)
                                                    ori_str_ID[int(indice_str_planta)][1], strings_ID[indices_str_ID] = girar_string_asociado(ori_str_ID[int(indice_str_planta)][1],orientacion[i,b],strings_ID[indices_str_ID],strings_fisicos[i,b,f,s_acum+3,1],dist_ext_opuesto_str[i,b,f,s_acum+3])
                                                    
                                                else: #si no se extiende
                                                    #Tercer string, se tira una string extension de 2 strings de largo para el cercano y otra de 3 strings de largo para el polo lejano
                                                    harness_p_cer[i,b,f,s_acum,0].append(s_acum+2)
                                                    harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                    harness_p_cer[i,b,f,s_acum,3] = harness_p_cer[i,b,f,s_acum,3] + 1
                                                    
                                                    harness_p_lej[i,b,f,s_acum,0].append(s_acum+2)
                                                    harness_p_lej[i,b,f,s_acum,4] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                    harness_p_lej[i,b,f,s_acum,4] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                    
                                                    #Cuarto string, se tira una string extension de 3 strings de largo para el cercano y otra de 4 strings de largo para el polo lejano
                                                    harness_p_cer[i,b,f,s_acum,0].append(s_acum+3)
                                                    harness_p_cer[i,b,f,s_acum,1] = harness_p_cer[i,b,f,s_acum,1] + 1
                                                    harness_p_cer[i,b,f,s_acum,4] = harness_p_cer[i,b,f,s_acum,4] + 1
                                                    
                                                    harness_p_lej[i,b,f,s_acum,0].append(s_acum+3)
                                                    harness_p_lej[i,b,f,s_acum,4] = harness_p_lej[i,b,f,s_acum,1] + 1
                                                    harness_p_lej[i,b,f,s_acum,5] = harness_p_lej[i,b,f,s_acum,5] + 1                                                
                                            s_acum=s_acum+4
                                        #Asignamos cercano y lejano con positivo/negativo
                                        if Polo_cercano == 'Positive':
                                            harness_pos[i,b,f] = harness_p_cer[i,b,f]
                                            harness_neg[i,b,f] = harness_p_lej[i,b,f]
                                        if Polo_cercano == 'Negative':
                                            harness_neg[i,b,f] = harness_p_cer[i,b,f]
                                            harness_pos[i,b,f] = harness_p_lej[i,b,f]
                                    
    # Asociamos los harness a los strings fisicos para sacar las coordenadas
    coord_harness_pos = np.full((n_bloques+1,max_b,max_f_str_b,max_spf+1,2), np.nan)
    coord_harness_neg = np.full((n_bloques+1,max_b,max_f_str_b,max_spf+1,2), np.nan)
    for i in range(bloque_inicial, n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(filas_en_bandas[i,b,0,0,1]): #si la banda no está vacía       
                for f in range(0,max_f_str_b):      
                    if ~np.isnan(filas_en_bandas[i,b,f,0,1]): #si la fila no está vacía en nans o en ceros
                        if String_o_Bus == 'DC Bus' or ((String_o_Bus == 'Both types' or String_o_Bus == 'Mixed') and filas_con_cable_string[i,b,f] == False): #Si la fila es de DCBus
                            for s in range(0,max_spf):
                                if ~np.isnan(harness_pos[i,b,f,s,1]) and np.any(harness_pos[i,b,f,s,1:] != 0): #excluimos los harness con nans y todo ceros
                                    coord_harness_pos[i,b,f,s] = [strings_fisicos[i,b,f,s,0],strings_fisicos[i,b,f,s,1]]
                                if ~np.isnan(harness_pos[i,b,f,s,1]) and np.any(harness_neg[i,b,f,s,1:] != 0):
                                    coord_harness_neg[i,b,f,s]  = [strings_fisicos[i,b,f,s,0],strings_fisicos[i,b,f,s,1]]
                            #si estamos en el extremo del ultimo tracker porque se ha extendido el dcbus
                            if ~np.isnan(harness_pos[i,b,f,s+1,1]) and np.any(harness_pos[i,b,f,s+1,1:] != 0):
                                if orientacion[i,b]=='S':
                                    coord_harness_pos[i,b,f,s+1] = [strings_fisicos[i,b,f,s,0],strings_fisicos[i,b,f,s,1]+dist_ext_opuesto_str[i,b,f,s]]
                                else:
                                    coord_harness_pos[i,b,f,s+1] = [strings_fisicos[i,b,f,s,0],strings_fisicos[i,b,f,s,1]-dist_ext_opuesto_str[i,b,f,s]]
                            if ~np.isnan(harness_neg[i,b,f,s+1,1]) and np.any(harness_neg[i,b,f,s+1,1:] != 0):
                                if orientacion[i,b]=='S':
                                    coord_harness_neg[i,b,f,s+1] = [strings_fisicos[i,b,f,s,0],strings_fisicos[i,b,f,s,1]+dist_ext_opuesto_str[i,b,f,s]]
                                else:
                                    coord_harness_neg[i,b,f,s+1] = [strings_fisicos[i,b,f,s,0],strings_fisicos[i,b,f,s,1]-dist_ext_opuesto_str[i,b,f,s]]
    # TRANSFORMACION DE DATOS A FORMATO DIBUJO - Aplana los array y filtra los valores NaN
    PB_harness_pos=[]
    PB_harness_neg=[]
    PB_coord_harness_pos=[]
    PB_coord_harness_neg=[]
    
    for i in range(bloque_inicial,n_bloques+1):
        flattened_harn_pos =  harness_pos[i,:,:,:,1:].reshape(-1, 5) #excluimos el primer termino que es una lista de strings asociados al harness
        flattened_harn_neg =  harness_neg[i,:,:,:,1:].reshape(-1, 5)
        flattened_coord_harn_pos = coord_harness_pos[i].reshape(-1, 2)
        flattened_coord_harn_neg = coord_harness_neg[i].reshape(-1, 2)
        
        flattened_harn_pos_sin_nan = np.array([tuple(row) for row in flattened_harn_pos.astype(float) if not np.isnan(row).any()])
        flattened_harn_neg_sin_nan = np.array([tuple(row) for row in flattened_harn_neg.astype(float) if not np.isnan(row).any()])
        flattened_coord_harn_pos_sin_nan = np.array([tuple(row) for row in flattened_coord_harn_pos if not np.isnan(row).any()])    
        flattened_coord_harn_neg_sin_nan = np.array([tuple(row) for row in flattened_coord_harn_neg if not np.isnan(row).any()])                         
        
        PB_harness_pos.append(flattened_harn_pos_sin_nan)
        PB_harness_neg.append(flattened_harn_neg_sin_nan)
        PB_coord_harness_pos.append(flattened_coord_harn_pos_sin_nan)
        PB_coord_harness_neg.append(flattened_coord_harn_neg_sin_nan)
        
    harness_pos_list = np.vstack(PB_harness_pos)
    harness_neg_list = np.vstack(PB_harness_neg)
    coord_harness_pos_list = np.vstack(PB_coord_harness_pos)
    coord_harness_neg_list = np.vstack(PB_coord_harness_neg)
    
    tipos_harness_pos, med_tipos_h_pos = np.unique(harness_pos_list, axis=0, return_counts=True) 
    tipos_harness_neg, med_tipos_h_neg = np.unique(harness_neg_list, axis=0, return_counts=True)
    
    #como tenemos una lista de coordenadas paralela a la lista de harness podemos listar el tipo de harness y juntarlo con ellas
    harness_pos_type_list=[]
    for i in range(0,len(harness_pos_list)):
        if np.any(harness_pos_list[i] != 0):
            cont=0
            for h_id_row in tipos_harness_pos:
                if np.all(harness_pos_list[i] == h_id_row):
                    harness_pos_type_list.append(cont)
                    break
                cont=cont+1
    harness_neg_type_list=[]     
    for i in range(0,len(harness_neg_list)):
        if np.any(harness_neg_list[i] != 0):
            cont=0
            for h_id_row in tipos_harness_neg:
                if np.all(harness_neg_list[i] == h_id_row):
                    harness_neg_type_list.append(cont)
                    break                    
                cont=cont+1
                
    Harness_pos_ID=np.column_stack((np.array(harness_pos_type_list),coord_harness_pos_list))
    Harness_neg_ID=np.column_stack((np.array(harness_neg_type_list),coord_harness_neg_list))
    
    return Harness_pos_ID, Harness_neg_ID, tipos_harness_pos, med_tipos_h_pos, tipos_harness_neg, med_tipos_h_pos, med_tipos_h_neg, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, strings_ID






def calculo_interno_polilinea_array(Array_cable_i_b_c, cajas_fisicas, x_fila_activa, y_fila_activa, filas_en_cajas, ori, ifa, ifax, ifp, i, b, c, p, max_c, sep_caja_tr, sal, l_caja):
    caja_en_fila_anexa=False
    punto_extra=False
    if ori =='S':                       
        x_fila_anexa=filas_en_cajas[i,b,ifax,2]
        y_fila_anexa=filas_en_cajas[i,b,ifax,3]+sep_caja_tr+sal+l_caja

        if np.any(np.abs(cajas_fisicas[i,b,:,1]-x_fila_anexa) < 0.1):
            caja_en_fila_anexa=True
            
        x_fila_posterior=filas_en_cajas[i,b,ifp,2]
        y_fila_posterior=filas_en_cajas[i,b,ifp,3]+sep_caja_tr+sal+l_caja
        
       
        if abs(y_fila_anexa - y_fila_activa) < 0.1: #si la anexa es igual a la activa
            if y_fila_posterior <= y_fila_activa: #como estamos con orientacion al S, si la posterior está más al sur el salto es posible
                Array_cable_i_b_c[p,0]=x_fila_posterior
                Array_cable_i_b_c[p,1]=y_fila_posterior
                ifa=ifp #indice de la fila activa actualizado a posterior
            else: #si estuviese más al N chocariamos con la fila anexa por lo que hay que saltar a ella
                Array_cable_i_b_c[p,0]=x_fila_anexa
                Array_cable_i_b_c[p,1]=y_fila_anexa
                ifa=ifax #indice de la fila activa actualizado a anexa
        elif y_fila_anexa < y_fila_activa: #si hay salto en la anexa hacia el S
            if y_fila_posterior - y_fila_anexa >= y_fila_anexa - y_fila_activa: #si la posterior está a la misma Y o mas al norte no se puede saltar porque choca con la anexa, pero es que además si es monofila es posible que esté por debajo de la S y tampoco se pueda si la pendiente es mayor (hay un cambio de pendiente)
                Array_cable_i_b_c[p,0]=x_fila_anexa
                Array_cable_i_b_c[p,1]=y_fila_anexa
                ifa=ifax 
            else: #si estamos mas al S incluso y con una pendiente aun menor (más pronunciada), ahí si puede darse el salto
                Array_cable_i_b_c[p,0]=x_fila_posterior
                Array_cable_i_b_c[p,1]=y_fila_posterior
                ifa=ifp 
        else: #si hay salto en la anexa hacia el N se puede hacer el salto a no ser que sea un caso monofila donde puede cambiar el largo del tracker o haya un cambio de pendiente a mayor en ese punto y choque con el anexo
            if y_fila_posterior - y_fila_anexa <= y_fila_anexa - y_fila_activa: #si la posterior está a la misma o menor pendiente que la anexa se puede saltar porque es un caso diente de sierra (Double Row) o alineado (monofila)
                Array_cable_i_b_c[p,0]=x_fila_posterior
                Array_cable_i_b_c[p,1]=y_fila_posterior
                ifa=ifp
            else: #si en la anexa hay cambio de pendiente a peor nos quedamos en ella
                Array_cable_i_b_c[p,0]=x_fila_anexa
                Array_cable_i_b_c[p,1]=y_fila_anexa
                ifa=ifax 
        
        #Independientemente de que haya un salto a la posterior, el salto en la anexa se deja registrado (sobre la linea calculada a la posterior) para evitar duplicar zanjas cuando vengan otras por pasillos o cuando salgan de zanjas 
        if Array_cable_i_b_c[p,0]==x_fila_posterior:
            Array_cable_i_b_c[p,0]=x_fila_anexa
            Array_cable_i_b_c[p,1]=(y_fila_activa+y_fila_posterior)/2 #la Y será la de la mitad del salto, como está en la mitad de la X, también será en la mitad de la Y de las dos anexa
            #hay una excepción que nos puede obligar a pararnos en la anexa en lugar de seguir a la posterior, si entra una caja en esa X se podrían desfasar los saltos si ambas van a posteriores, por lo que se deja en la anexa y se sincronizan los calculos
            #no hace falta "ir a ella" si estamos en un diente de sierra, lo hacemos sobre la recta de la posterior que habiamos proyectado
            if caja_en_fila_anexa==True: 
                ifa=ifax  
            else: #si no hay problematica de fila anexa confirmamos el salto a la posterior habiendo registrado ya el punto en la anexa
                Array_cable_i_b_c[p+1,0]=x_fila_posterior
                Array_cable_i_b_c[p+1,1]=y_fila_posterior
                punto_extra=True
            
    elif ori =='N':                       
        x_fila_anexa=filas_en_cajas[i,b,ifax,2]
        y_fila_anexa=filas_en_cajas[i,b,ifax,3]+sep_caja_tr+sal+l_caja
        
        if np.any(np.abs(cajas_fisicas[i,b,:,1]-x_fila_anexa) < 0.1):
            caja_en_fila_anexa=True
    
        x_fila_posterior=filas_en_cajas[i,b,ifp,2]
        y_fila_posterior=filas_en_cajas[i,b,ifp,3]+sep_caja_tr+sal+l_caja
        x_fila_posterior=filas_en_cajas[i,b,ifp,2]
        y_fila_posterior=filas_en_cajas[i,b,ifp,3]+sep_caja_tr+sal+l_caja
              
        if abs(y_fila_anexa - y_fila_activa) < 0.1: #si no hay caja y la anexa es igual a la activa
            if y_fila_posterior >= y_fila_activa: #como estamos con orientacion al N, si la posterior está más al norte el salto es posible
                Array_cable_i_b_c[p,0]=x_fila_posterior
                Array_cable_i_b_c[p,1]=y_fila_posterior
                ifa=ifp #indice de la fila activa actualizado a posterior
            else: #si estuviese más al S chocariamos con la fila anexa por lo que hay que saltar a ella
                Array_cable_i_b_c[p,0]=x_fila_anexa
                Array_cable_i_b_c[p,1]=y_fila_anexa
                ifa=ifax #indice de la fila activa actualizado a anexa
        elif y_fila_anexa < y_fila_activa: #si hay salto en la anexa hacia el S
            if y_fila_posterior - y_fila_anexa >= y_fila_anexa - y_fila_activa: #si la pendiente posterior-anexa es mayor (menos pronunciada negativa) que la anexa-activa, el salto es posible
                Array_cable_i_b_c[p,0]=x_fila_posterior
                Array_cable_i_b_c[p,1]=y_fila_posterior
                ifa=ifp 
            else: #si estamos mas al s incluso y con una pendiente aun menor (más pronunciada), no puede darse el salto
                Array_cable_i_b_c[p,0]=x_fila_anexa
                Array_cable_i_b_c[p,1]=y_fila_anexa
                ifa=ifax
        else: #si hay salto en la anexa hacia el N 
            if y_fila_posterior - y_fila_anexa <= y_fila_anexa - y_fila_activa: #si la posterior está a la misma o menor pendiente que la anexa se choca 
                Array_cable_i_b_c[p,0]=x_fila_anexa
                Array_cable_i_b_c[p,1]=y_fila_anexa
                ifa=ifax
            else: #si está a mayor pendiente el salto es posible gracias a la orientacion N
                Array_cable_i_b_c[p,0]=x_fila_posterior
                Array_cable_i_b_c[p,1]=y_fila_posterior
                ifa=ifp                
                
        #Independientemente de que haya un salto a la posterior, el salto en la anexa se deja registrado (sobre la linea calculada a la posterior) para evitar duplicar zanjas cuando vengan otras por pasillos o cuando salgan de zanjas 
        if Array_cable_i_b_c[p,0]==x_fila_posterior:
            Array_cable_i_b_c[p,0]=x_fila_anexa
            Array_cable_i_b_c[p,1]=(y_fila_activa+y_fila_posterior)/2 #la Y será la de la mitad del salto, como está en la mitad de la X, también será en la mitad de la Y de las dos anexa
            #hay una excepción que nos puede obligar a pararnos en la anexa en lugar de seguir a la posterior, si entra una caja en esa X se podrían desfasar los saltos si ambas van a posteriores, por lo que se deja en la anexa y se sincronizan los calculos
            #no hace falta "ir a ella" si estamos en un diente de sierra, lo hacemos sobre la recta de la posterior que habiamos proyectado
            if caja_en_fila_anexa==True: 
                ifa=ifax  
            else:
                Array_cable_i_b_c[p+1,0]=x_fila_posterior
                Array_cable_i_b_c[p+1,1]=y_fila_posterior
                punto_extra=True
            
    return Array_cable_i_b_c , ifa, punto_extra


def polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, p, max_f_str_b, max_c, Array_cable_i_b_c,cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas, referencia_PCS_puerto, distancia_condicion,sep_caja_tracker, orientacion, pitch):
    
    if p==0: #si el array se origina en la caja insertada
        Array_cable_i_b_c[0,0]=cajas_fisicas[i,b,c,1] #las coordenadas X de partida son las de la caja asociada al array                        
        Array_cable_i_b_c[1,0]=cajas_fisicas[i,b,c,1]  
        
        #posible optimizar, que la salida de la caja no se haga inicialmente en la direccion NS
        #las coordenadas Y dependen de la orientacion, son respectivamente al borde de la caja y la salida definida
        if orientacion[i,b]=='S': #la Y a la salida de la caja dependiendo de la orientacion
            Array_cable_i_b_c[0,1]=cajas_fisicas[i,b,c,2]-largo_caja/2
            Array_cable_i_b_c[1,1]=Array_cable_i_b_c[0,1]-salida_zanja_LV_caja_inv
        elif orientacion[i,b]=='N':
            Array_cable_i_b_c[0,1]=cajas_fisicas[i,b,c,2]
            Array_cable_i_b_c[1,1]=Array_cable_i_b_c[0,1]+salida_zanja_LV_caja_inv+largo_caja/2
        
        p=1 
    
    #salimos fuera del if, si viene ya empezado no hace lo del if (porque viene de otra banda) 
    
    ifa=np.nanargmin(abs(filas_en_cajas[i,b,:,2]-Array_cable_i_b_c[p,0]))
        
    #vemos si estamos a derecha o a izquierda                                    
    if Array_cable_i_b_c[p,0] - referencia_PCS_puerto < 0: #la caja está a la izquierda del punto de referencia (PCS o puerto)
        while abs(Array_cable_i_b_c[p,0]- referencia_PCS_puerto) > distancia_condicion + 0.1: #PENDIENTE OPTIMIZAR CON COORDENADAS PCS BIEN DEFINIDAS
                                #QUE PASA SI NO SE ALCANZA LA VERTICAL DE LA PCS
            
            #Hay que estudiar la posicion potencial si llevamos el siguiente punto a una fila anexa o a dos filas anexas para evitar los dientes de sierra en bandas no horizontales
            #Si la fila anexa tiene una Y diferente a la de la activa 
            #Si la fila anexa tiene la misma Y es posible que estemos en una banda horizontal o en un diente de sierra, hay que ver la Y de la anexa +1
                #si la Y de la anexa +1 es igual a la inicial estamos en una banda (o en una zona) horizontal
                #si la Y de la anexa cambia, entonces es posible que se pueda ahorrar el diente de sierra saltando directamente a ella (siempre que en la anexa no haya otra caja que entonces necesitamos poner un punto en su salida)
                    #que se pueda o no se pueda depende de como varíe esa Y, hay que evitar que la zanja se meta entre los modulos, se evaluará la orientación del bloque y la Y relativa para ver si hay espacio en el deinte de sierra o es un saliente que debe bordearse
            p=p+1
            
            x_fila_activa=Array_cable_i_b_c[p-1,0]
            y_fila_activa=Array_cable_i_b_c[p-1,1]   
            
            # if x_fila_activa >= np.nanmax(filas_en_cajas[i,b,:,2]): #si hemos llegado al limite de filas activas y nos devolvería np.nan
            #     p=p-1 #retrocedemos el avance del contador hecho y rompemos el while
            #     break
            # else:
            if orientacion[i,b] == 'S':
                ifax=ifa+1 #indice de la fila anexa
                ifp=ifa+2 #indice de la fila posterior
                
                sep_cj_tr= - sep_caja_tracker
                sal_LV= - salida_zanja_LV_caja_inv
                borde_caja= - largo_caja/2
                
                if ifp > np.count_nonzero(~np.isnan(filas_en_cajas[i,b,:,0]))-1: #acotamos los indices para evitar choques con los extremos de las filas
                    if ifax > np.count_nonzero(~np.isnan(filas_en_cajas[i,b,:,0]))-1:
                        ifax=ifa
                        ifp=ifa
                    else:
                        ifp=ifax
                        
            elif orientacion[i,b] == 'N':
                ifax=ifa-1 #indice de la fila anexa
                ifp=ifa-2 #indice de la fila posterior
                
                sep_cj_tr= sep_caja_tracker
                sal_LV= salida_zanja_LV_caja_inv
                borde_caja= largo_caja/2
                
                if ifp < 0: #acotamos los indices para evitar choques con los extremos de las filas
                    if ifax < 0:
                        ifax=ifa
                        ifp=ifa
                    else:
                        ifp=ifax
                
            Array_cable_i_b_c , ifa, punto_extra = calculo_interno_polilinea_array(Array_cable_i_b_c, cajas_fisicas, x_fila_activa, y_fila_activa, filas_en_cajas, orientacion[i,b], ifa, ifax, ifp, i, b, c, p, max_c, sep_cj_tr, sal_LV, borde_caja)
            if punto_extra == True:
                p=p+1
   
            if np.all(Array_cable_i_b_c[p] == Array_cable_i_b_c[p-1]): #si se llega al final de las filas de la banda y se empieza a repetir porque no cumple, nos vamos al pasillo de la derecha
                Array_cable_i_b_c[p,0]=Array_cable_i_b_c[p,0] + pitch/2
                Array_cable_i_b_c[p,1]=Array_cable_i_b_c[p,1]
                break
            
        if Array_cable_i_b_c[p,0] - referencia_PCS_puerto > 0: #si al meter el ultimo punto nos hemos pasado de la x limite, nos quedamos parados en el limite
            m_recta=(Array_cable_i_b_c[p,1]-Array_cable_i_b_c[p-1,1])/(Array_cable_i_b_c[p,0]-Array_cable_i_b_c[p-1,0])
            Array_cable_i_b_c[p,0] = referencia_PCS_puerto
            Array_cable_i_b_c[p,1] = Array_cable_i_b_c[p-1,1] + m_recta * (referencia_PCS_puerto-Array_cable_i_b_c[p-1,0])
            

    #la caja está a la derecha de la PCS                                            
    elif Array_cable_i_b_c[p,0] - referencia_PCS_puerto > 0: 
        while abs(referencia_PCS_puerto - Array_cable_i_b_c[p,0]) > distancia_condicion + 0.1: #PENDIENTE OPTIMIZAR CON COORDENADAS PCS BIEN DEFINIDAS
                                #QUE PASA SI NO SE ALCANZA LA VERTICAL DE LA PCS            
            p=p+1
            
            x_fila_activa=Array_cable_i_b_c[p-1,0]
            y_fila_activa=Array_cable_i_b_c[p-1,1]
            
            if orientacion[i,b] == 'S':
                ifax=ifa-1 #indice de la fila anexa
                ifp=ifa-2 #indice de la fila posterior
                
                sep_cj_tr= - sep_caja_tracker
                sal_LV= - salida_zanja_LV_caja_inv
                borde_caja= - largo_caja/2
                
                if ifp < 0: #acotamos los indices para evitar choques con los extremos de las filas
                    if ifax < 0:
                        ifax=ifa
                        ifp=ifa
                    else:
                        ifp=ifax
                        
            elif orientacion[i,b] == 'N':
                ifax=ifa+1 #indice de la fila anexa
                ifp=ifa+2 #indice de la fila posterior
                
                sep_cj_tr= sep_caja_tracker
                sal_LV= salida_zanja_LV_caja_inv
                borde_caja= largo_caja/2
                
                if ifp > np.count_nonzero(~np.isnan(filas_en_cajas[i,b,:,0]))-1: #acotamos los indices para evitar choques con los extremos de las filas
                    if ifax > np.count_nonzero(~np.isnan(filas_en_cajas[i,b,:,0]))-1:
                        ifax=ifa
                        ifp=ifa
                    else:
                        ifp=ifax

            Array_cable_i_b_c , ifa , punto_extra= calculo_interno_polilinea_array(Array_cable_i_b_c, cajas_fisicas, x_fila_activa, y_fila_activa, filas_en_cajas, orientacion[i,b], ifa, ifax, ifp, i, b, c, p, max_c, sep_cj_tr, sal_LV,borde_caja)
            if punto_extra == True:
                p=p+1
                
            if np.all(Array_cable_i_b_c[p] == Array_cable_i_b_c[p-1]): #si se llega al final de las filas de la banda y se empieza a repetir porque no cumple, nos vamos al pasillo de la izquierda
                Array_cable_i_b_c[p,0]=Array_cable_i_b_c[p,0] - pitch/2
                Array_cable_i_b_c[p,1]=Array_cable_i_b_c[p,1]
                break
            
        if Array_cable_i_b_c[p,0] - referencia_PCS_puerto < 0: #si al meter el ultimo punto nos hemos pasado de la x limite, nos quedamos paramos en el limite
            m_recta=(Array_cable_i_b_c[p,1]-Array_cable_i_b_c[p-1,1])/(Array_cable_i_b_c[p,0]-Array_cable_i_b_c[p-1,0])
            Array_cable_i_b_c[p,0] = referencia_PCS_puerto
            Array_cable_i_b_c[p,1] = Array_cable_i_b_c[p-1,1] + m_recta * (referencia_PCS_puerto-Array_cable_i_b_c[p-1,0])        
        
    return Array_cable_i_b_c, p 


def polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, b_comp, f_b_comp, pol_array_cable_i_b_c, p, orientacion_i_b, filas_en_cajas, referencia_puerto, pitch, bandas_anexas, bandas_aisladas, sep_salto_a_tracker, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas):
#Nota: por defecto la banda es separada, si es aislada se actua sobre ella despues    
    
    #REVISAMOS SI HACE FALTA RECORRER LA PROPIA BANDA EN DIRECCION N-S antes
      if bajada_necesaria==True: #si el cable estaba en la parte superior de la banda hay que bajarlo a la parte inferior primero
        #como llegamos por fuera (f_bc=max f activas en esa banda) no nos preocupa el ancho del pasillo, va en una sola zanja     
          puerto_x=filas_en_cajas[i,b_comp,f_b_comp,2]+pitch/2
          puerto_y=pol_array_cable_i_b_c[p,1]
         
          pol_array_cable_i_b_c[p+1,0] = puerto_x
          pol_array_cable_i_b_c[p+1,1] = puerto_y 
         
          pol_array_cable_i_b_c[p+2,0] = puerto_x
          pol_array_cable_i_b_c[p+2,1] = filas_en_cajas[i,b_comp,f_b_comp,3] - sep_caja_tracker - largo_caja/2 - salida_zanja_LV_caja_inv
         
          p=p+2
     
      #Al llegar al extremo de la banda separada (ya en la parte inferior), buscamos la anexa que debe estar en sus proximidades para saltar a ella horizontalmente y recorrerla hasta la PCS
     
      #REVISAMOS SI HAY ANEXA EN ESA ORIENTACION A LA QUE PODAMOS SALTAR LATERALMENTE
      if hay_anexa==False: #Si no hay anexa llevamos directamente el cable a la PCS en L
              pol_array_cable_i_b_c[p+1,0] = coord_PCS_DC_inputs[i,0]
              pol_array_cable_i_b_c[p+1,1] = pol_array_cable_i_b_c[p,1]
             
              pol_array_cable_i_b_c[p+2,0] = coord_PCS_DC_inputs[i,0]
              pol_array_cable_i_b_c[p+2,1] = coord_PCS_DC_inputs[i,1]
             
      else: #Si hay anexa se puede saltar a ella y recorrerla antes de ir a la PCS
     
          #la identificamos
          if orientacion_i_b == 'S':    
              if pol_array_cable_i_b_c[p,0] < coord_PCS_DC_inputs[i,0]: #Con orientacion sur, si estamos a la izquierda de la PCS la anexa tiene que tener un b mayor por estar a la derecha
                  for bch_pot in range(b_comp,max_b): 
                      if bandas_anexas[i,bch_pot]==True:
                          bch=bch_pot
                          #identificamos su fila más a la izquierda, POSIBLE OPTIMIZAR, a lo mejor la que está más a la izquierda está retranqueada por alguna restriccion, habria que ver cual de ese lado está más al sur, junto al camino
                          f_bh=0
                          break

                  #POSIBILIDAD DE NO ENCONTRAR SOLUCION
                  #Si la geometria es compleja (inclinaciones altas y separaciones grandes)puede pasar que el orden de las bandas se altere y haya que buscar en el sentido contrario
                  for bch_pot in range(b_comp,-1,-1):  #Con orientacion sur, si estamos a la derecha de la PCS la anexa tiene que tener un b menor por estar a la izquierda
                      if bandas_anexas[i,bch_pot]==True:
                          bch=bch_pot
                          f_bh=np.nanargmax(filas_en_cajas[i,bch,:,2])
                          break
                      
              else:
                  for bch_pot in range(b_comp,-1,-1):  #Con orientacion sur, si estamos a la derecha de la PCS la anexa tiene que tener un b menor por estar a la izquierda
                      if bandas_anexas[i,bch_pot]==True:
                          bch=bch_pot
                          f_bh=np.nanargmax(filas_en_cajas[i,bch,:,2])
                          break
                  #POSIBILIDAD DE NO ENCONTRAR SOLUCION
                  #Si la geometria es compleja (inclinaciones altas y separaciones grandes)puede pasar que el orden de las bandas se altere y haya que buscar en el sentido contrario
                  for bch_pot in range(b_comp,max_b): 
                      if bandas_anexas[i,bch_pot]==True:
                          bch=bch_pot
                          f_bh=0
                          break

                 
          elif orientacion_i_b == 'N':

              if pol_array_cable_i_b_c[p,0] < coord_PCS_DC_inputs[i,0]: #Con orientacion norte, si estamos a la izquierda de la PCS la anexa tiene que tener un b menor por estar a la derecha
                  encontrada = False
                  for bch_pot in range(b_comp,-1,-1):          
                      if bandas_anexas[i,bch_pot]==True:
                          encontrada = True
                          bch=bch_pot
                          f_bh=np.nanargmin(filas_en_cajas[i,bch,:,2])
                          break
                  #POSIBILIDAD DE NO ENCONTRAR SOLUCION
                  #Si la geometria es compleja (inclinaciones altas y separaciones grandes)puede pasar que el orden de las bandas se altere y haya que buscar en el sentido contrario
                  if encontrada == False:
                      for bch_pot in range(b_comp,max_b):  
                          if bandas_anexas[i,bch_pot]==True:
                              bch=bch_pot
                              f_bh=0
                              break
    
              else:
                  for bch_pot in range(b_comp,max_b):  #Con orientacion norte, si estamos a la derecha de la PCS la anexa tiene que tener un b mayor por estar a la izquierda
                      if bandas_anexas[i,bch_pot]==True:
                          bch=bch_pot
                          f_bh=0
                          break
                  #POSIBILIDAD DE NO ENCONTRAR SOLUCION
                  #Si la geometria es compleja (inclinaciones altas y separaciones grandes)puede pasar que el orden de las bandas se altere y haya que buscar en el sentido contrario
                  for bch_pot in range(b_comp,-1,-1):          
                      if bandas_anexas[i,bch_pot]==True:
                          encontrada = True
                          bch=bch_pot
                          f_bh=np.nanargmin(filas_en_cajas[i,bch,:,2])
                          break
                  
                  
          #revisamos el signo de la separacion a los trackers que van a dar con el salto, por defecto está puesto como si fuese orientacion S
          if orientacion[i,b]=='N':
              sep_salto_a_tracker=-sep_salto_a_tracker
         
          if bandas_aisladas[i,b_comp]==True: #si la banda en realidad es aislada, primero hay que llevarla a la altura de la anexa y luego se la une directamente (se hace una L), habrá que cambiarla a mano pero así la medida de cable es conservadora
              p=p+1
              pol_array_cable_i_b_c[p,0] = pol_array_cable_i_b_c[p-1,0] 
              pol_array_cable_i_b_c[p,1] = filas_en_cajas[i,bch,f_bh,3]+sep_salto_a_tracker
          #si era separada se asume que está a una altura parecida asi que se tira directamente en diagonal
         
          #Llevamos el array hasta la fila al extremo de la anexa y recorremos la banda anexa hasta el punto de espera, POTENCIAL PROBLEMA LUEGO EN LA ANEXA DE QUE SE SUMEN MAS CIRCUITOS DESDE ARRIBA Y NO SE HAYA PREVISTO PORQUE SOLO SE EVALUÓ EL LADO IZQUIERDO DE LA ANEXA SIN CONTAR OTRAS BANDAS SEPARADAS
          p=p+1

          pol_array_cable_i_b_c[p,0] = filas_en_cajas[i,bch,f_bh,2]
          pol_array_cable_i_b_c[p,1] = filas_en_cajas[i,bch,f_bh,3]+sep_salto_a_tracker
         
          pol_array_cable_i_b_c, p = polilinea_array_hasta_punto_de_espera_o_puerto(i, bch, c, p, max_f_str_b, max_c, pol_array_cable_i_b_c,cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas, referencia_puerto, pitch,sep_caja_tracker, orientacion, pitch)

          #alcanzado el punto de espera se acaba en la PCS
          p=p+1
          pol_array_cable_i_b_c[p,0] = coord_PCS_DC_inputs[i,0]
          pol_array_cable_i_b_c[p,1] = coord_PCS_DC_inputs[i,1]    
         
      return pol_array_cable_i_b_c


def polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable_i_b_c, circ_en_banda, n_c_max_pas, pitch):
    if circ_en_banda <= n_c_max_pas:  #podemos entrar por una sola zanja, entramos por el de la izquierda por defecto
        puerto_x=pol_array_cable_i_b_c[p,0]-pitch/2
        puerto_y=pol_array_cable_i_b_c[p,1]
        
        pol_array_cable_i_b_c[p+1,0] = puerto_x
        pol_array_cable_i_b_c[p+1,1] = puerto_y 
        
        pol_array_cable_i_b_c[p+2,0] = puerto_x
        pol_array_cable_i_b_c[p+2,1] = coord_PCS_DC_inputs[i,1]+5
        
        pol_array_cable_i_b_c[p+3,0] = coord_PCS_DC_inputs[i,0]
        pol_array_cable_i_b_c[p+3,1] = coord_PCS_DC_inputs[i,1]+5
    else: #hay que meter una zanja por el pasillo de la izquierda y otra por el de la derecha
        c_particion = circ_en_banda/2 
        
        if c <= c_particion: 
            puerto_x=pol_array_cable_i_b_c[p,0]-pitch/2 
        else:
            puerto_x=pol_array_cable_i_b_c[p,0]+pitch/2
        puerto_y=pol_array_cable_i_b_c[p,1]
        
        pol_array_cable_i_b_c[p+1,0] = puerto_x
        pol_array_cable_i_b_c[p+1,1] = puerto_y 
         
        pol_array_cable_i_b_c[p+2,0] = puerto_x
        pol_array_cable_i_b_c[p+2,1] = coord_PCS_DC_inputs[i,1]+5
         
        pol_array_cable_i_b_c[p+3,0] = coord_PCS_DC_inputs[i,0]
        pol_array_cable_i_b_c[p+3,1] = coord_PCS_DC_inputs[i,1]+5
        
    return  pol_array_cable_i_b_c




def polilinea_array(max_p_array,bloque_inicial, n_bloques, max_b, max_f_str_b, max_c, coord_PCS_DC_inputs, orientacion, pitch, cajas_fisicas, filas_en_cajas, filas_en_bandas, bandas_anexas, bandas_separadas, bandas_aisladas, sep_caja_tracker, sep_zanja_tracker, salida_zanja_LV_caja_inv, largo_caja, n_circuitos_max_lado_PCS, n_circuitos_max_entre_trackers, DCBoxes_o_Inv_String):    
    if DCBoxes_o_Inv_String == 'String Inverters':
        max_c = max_c+1
    pol_array_cable=np.full((n_bloques+1,max_b,max_c,max_p_array,2),np.nan) #posible optimizar, fijamos 100 como limite a los puntos de polilinea del cable de array    
    circuitos_en_banda=np.zeros((n_bloques+1,max_b))
    
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            banda_analizada=False
            if ~np.isnan(cajas_fisicas[i,b,0,0]): #si la banda no está vacía
            #Paso preliminar para despues, primero verificamos que haya anexa en esa orientacion, puede haber bloques que tengan separadas en un lado del camino sin que haya anexas
                b_anex=list(np.where(bandas_anexas[i,:] == True)[0])
                if orientacion[i,b]=='S':
                    if np.any(orientacion[i,b_anex] == "S"): #hay anexa
                        hay_anexa=True
                    else:
                        hay_anexa=False
                elif orientacion[i,b]=='N':
                    if np.any(orientacion[i,b_anex] == "N"): #hay anexa
                        hay_anexa=True
                    else:
                        hay_anexa=False
          #Comienzo de evaluacion                         
                if bandas_anexas[i,b]==True: #si la banda es anexa, PROVISIONALMENTE MANDAMOS LAS SERIES A LA PCS
                    for c in range(0,max_c):
                        if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía
                            pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0,  max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                            pol_array_cable[i,b,c,p+1,0] = coord_PCS_DC_inputs[i,0]
                            pol_array_cable[i,b,c,p+1,1] = pol_array_cable[i,b,c,p,1]
                           
                            pol_array_cable[i,b,c,p+2,0] = coord_PCS_DC_inputs[i,0]
                            pol_array_cable[i,b,c,p+2,1] = coord_PCS_DC_inputs[i,1]
                           
                elif bandas_separadas[i,b]==True or bandas_aisladas[i,b]==True: 
                    for c in range(0,max_c):
                        if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                            pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                            # #se da otro punto con el pitch para que recojan las que puedan venir de sus intermedias por el lateral
                            # if pol_array_cable[i,b,c,p,1] < coord_PCS_DC_inputs[i,0]:
                            #     pol_array_cable[i,b,c,p+1,0] = pol_array_cable[i,b,c,p,0]+pitch/2
                            # else:
                            #     pol_array_cable[i,b,c,p+1,0] = pol_array_cable[i,b,c,p,0]-pitch/2
                            # pol_array_cable[i,b,c,p+1,1] = pol_array_cable[i,b,c,p,1]
                            # p=p+1
                            #se define una funcion que lleva los cables desde la banda separada hasta la PCS enlazando con la anexa (si hay, si no se trata como anexa)
                            bajada_necesaria=False #se parte desde la parte inferior de la banda
                            pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, b, 0, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)

                #cuando la banda tiene alguna banda justo debajo, tendrá que meter zanjas entre sus trackers para llegar a la PCS. POSIBLE OPTIMIZAR, SE VA A LIMITAR EL ESTUDIO A BLOQUES CON HASTA 3 BANDAS CONSECUTIVAS EN DIRECCION N-S, SI HUBIESE ALGUN CASO ESPECIAL HABRIA QUE HACERLO A MANO
                else: #si la banda es extremo o intermedia, todas las otras son False, vemos qué tipo de extrema o intermedia tenemos (si enfila directamente con la PCS)  
                    if orientacion[i,b]=='S': 
                        for bc in range(b+1, max_b): #si está debajo (al sur) tiene que tener un numero de banda mayor
                            if orientacion[i,bc]=='S':
                                for fila in filas_en_cajas[i,b]:
                                    if banda_analizada==True:
                                        break #ponemos este break para que no se repitan las filas del for una vez se compruebe si ambas bandas estan debajo y se analice su paso de cable de array
                                                                     
                                    for fila_c in filas_en_cajas[i,bc]:
                                        if abs(fila[2] - fila_c[2]) < pitch: #si esto se cumple está pasando que b está encima de bc siendo bc una banda en el mismo lado del camino, por lo que habra que bajar sus circuitos por ella
                                            #SIN EMBARGO, que b esté encima de bc no significa que esté encima de la PCS directamente, aunque bc sea anexa, hay que ver si b llega a enfilar la PCS o no
                                            enfila_PCS = False
                                            for fila in filas_en_cajas[i,b]:
                                                if abs(fila[2] - coord_PCS_DC_inputs[i,0]) < 2*pitch:
                                                    enfila_PCS = True
                                                    break   
                                            if enfila_PCS==False: #si por mucho que nos movamos en la banda no vamos a encontrar la vertical de la PCS, veremos en qué lado de la PCS estamos y cuantos circuitos en ese lado de la PCS tienen el resto de bandas, si tienen demasiados alargaremos el recorrido para evitar zanjas demasiado grandes en ellas
                                                if filas_en_bandas[i,b,0,0,2] - coord_PCS_DC_inputs[i,0] < 0: #la banda se queda a la izquierda de la PCS
                                                    circuitos_izq_bc = np.count_nonzero(~np.isnan(cajas_fisicas[i,bc,cajas_fisicas[i,bc,:,1] < coord_PCS_DC_inputs[i,0],0]))
                                                    circuitos_en_banda[i,b] = np.count_nonzero(~np.isnan(cajas_fisicas[i,b,:,0]))
     
                                                    if circuitos_en_banda[i,b]+circuitos_izq_bc > n_circuitos_max_lado_PCS: #Si hay demasiados circuitos bordeamos por arriba la banda inferior hasta llegar a la altura de la PCS
                                                        for c in range(0,max_c):
                                                            if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                                                               
                                                                if bandas_anexas[i,bc]==True: #si la banda inferior es anexa a la PCS el punto de referencia para los cables es la PCS (aunque no lleguen en b, saltaran a bc y seguiran por ella)   
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                                else:
                                                                    #si la banda inferior no es anexa entonces no está garantizado que llegue más a la derecha que el extremo de la superior (podría ser una separada más a la izquierda o una intermedia más a la izquierda)
                                                                    #para evitar retroceder luego potencialmente con las cajas de esa banda, nos quedamos como puerto con la x menos cercana a la PCS entre los extremos más cercanos de las dos bandas
                                                                    referencia_x_puerto = np.nanmin([np.nanmax(filas_en_cajas[i,b,:,2]),np.nanmax(filas_en_cajas[i,bc,:,2])]) #si fuese la superior se estaría llegando al extremo igualmente
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,referencia_x_puerto,0,sep_caja_tracker, orientacion, pitch)                                                              

                                                                f_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(pol_array_cable[i,b,c,p,0]))) #vemos en que fila de la banda inferior caemos
                                                               
                                                                while abs(pol_array_cable[i,b,c,p,0] - coord_PCS_DC_inputs[i,0]) > pitch and f_bc < np.count_nonzero(~np.isnan(filas_en_cajas[i,bc,:,0]))-1: #se recorre la banda por arriba mientras no se alcance la PCS ni se llegue al final de las filas de la banda, si se daba alguna de esas casuisticas ya antes no se entra en el while
                                                                    pol_array_cable[i,b,c,p+1,0] = filas_en_cajas[i,bc,f_bc,2]
                                                                    pol_array_cable[i,b,c,p+1,1] = filas_en_bandas[i,bc,f_bc,0,3]+filas_en_bandas[i,bc,f_bc,0,1]+sep_zanja_tracker
                                                                    p=p+1
                                                                    f_bc=f_bc+1
                                                               
                                                                #SE HABIA SALTADO A UNA BANDA ANEXA 
                                                                if bandas_anexas[i,bc]==True: #si bc era anexa entonces ya hemos llegado a la vertical por definicion y tendriamos que meternos en el pasillo                                                                           
                                                                   
                                                                    pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable[i,b,c], circuitos_en_banda[i,b], n_circuitos_max_entre_trackers, pitch)

                                                                #SE HABIA SALTADO A UNA BANDA SEPARADA O AISLADA   
                                                                elif bandas_separadas[i,bc]==True or bandas_aisladas[i,bc]==True: #si era separada o aislada no hemos llegado a la PCS pero sí al borde de la banda
                                                                   
                                                                    bajada_necesaria=True
                                                                    pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc, f_bc, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas,coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)                                                              
                                                                                                                                     
                                                                #SE HABIA SALTADO A UNA BANDA INTERMEDIA
                                                                else: #si no es niguna de las dos anteriores es porque se trata de una banda intermedia y tiene otra banda (anexa o separada) debajo
                                                                    for bc_anex_pot in range(bc+1,max_b): #identificamos cual es la banda anexa o separada
                                                                        if bandas_anexas[i,bc_anex_pot]==True or bandas_separadas[i,bc_anex_pot]==True: #POTENCIAL PROBLEMA QUE SE VAYA A OTRA POSTERIOR?
                                                                            bc2=bc_anex_pot
                                                                            
                                                                    #buscamos la fila correspondiente dentro de dicha banda
                                                                    p=p+1
                                                                    f_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(pol_array_cable[i,b,c,p,0])))
                                                                    
                                                                    #recorremos la banda por encima, si antes no hemos entrado por abajo ahora con menos motivo, al llevar sumados los de la anterior
                                                                    while abs(pol_array_cable[i,b,c,p,0] - coord_PCS_DC_inputs[i,0]) > pitch and f_bc2 < np.count_nonzero(~np.isnan(filas_en_cajas[i,bc2,:,0]))-1: #se recorre la banda por arriba mientras no se alcance la PCS ni se llegue al final de las filas de la banda
                                                                        pol_array_cable[i,b,c,p+1,0] = filas_en_cajas[i,bc,f_bc2,2]
                                                                        pol_array_cable[i,b,c,p+1,1] = filas_en_bandas[i,bc,f_bc2,0,3]+filas_en_bandas[i,bc,f_bc2,0,1]+sep_zanja_tracker
                                                                        p=p+1
                                                                        f_bc2=f_bc2+1
                                                                        
                                                                    #SI LA BANDA DE ABAJO ES ANEXA - Se ha salido del while llegando a la altura de la PCS
                                                                    if bandas_anexas[i,bc2]==True: #si bc era anexa entonces hemos llegado a la vertical por definicion y tendriamos que meternos en el pasillo         
                                                                       
                                                                        #cuidado al comprobar si el numero de circuitos permite que haya una sola zanja o hay que ir por dos pasillos, pues ahora van dos bandas
                                                                        pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable[i,b,c], circuitos_en_banda[i,b]+circuitos_en_banda[i,bc], n_circuitos_max_entre_trackers, pitch)
                                                                        #TODO falta coordinar las bajadas en dos pasillo con los cables de las distintas bandas
                                                                                                                                                          
                                                                    #SI LA BANDA DE ABAJO ES SEPARADA O AISLADA - Se ha salido del while llegando a la ultima fila de la banda (se podria poner un else porque no hay mas saltos a intermedias contemplados)
                                                                    elif bandas_separadas[i,bc2]==True or bandas_aisladas[i,bc2]==True: #si era separada o aislada no hemos llegado a la PCS pero sí al borde de la banda
                                                                        
                                                                        bajada_necesaria = True
                                                                        pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc2, f_bc2, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)
                                                                   
                                                    elif circuitos_en_banda[i,b]+circuitos_izq_bc <= n_circuitos_max_lado_PCS: #Si no hay demasiados circuitos podemos bajar directamente a la inferior
                                                        for c in range(0,max_c):
                                                            if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                                                            
                                                            #TODO, faltaria por ver si se pueden meter en un pasillo o tienen que ser en 2
                                                            
                                                                if bandas_anexas[i,bc]==True:   
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                                else:                                                               
                                                                    referencia_x_puerto = np.nanmin([np.nanmax(filas_en_cajas[i,b,:,2]),np.nanmax(filas_en_cajas[i,bc,:,2])]) #si fuese la superior se estaría llegando al extremo igualmente
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,referencia_x_puerto,0,sep_caja_tracker, orientacion, pitch)                                                              

                                                                
                                                                f_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(pol_array_cable[i,b,c,p,0])))
                                                                
                                                                pol_array_cable[i,b,c,p+1,0] = pol_array_cable[i,b,c,p,0]+pitch/2
                                                                pol_array_cable[i,b,c,p+1,1] = pol_array_cable[i,b,c,p,1]
                                                                
                                                                pol_array_cable[i,b,c,p+2,0] = pol_array_cable[i,b,c,p+1,0]
                                                                pol_array_cable[i,b,c,p+2,1] = filas_en_cajas[i,bc,f_bc+1,3] - sep_caja_tracker - largo_caja/2 - salida_zanja_LV_caja_inv
                                                                
                                                                p=p+2
                                                                
                                                                #Independientemente de la banda a la que se salte, al ir ya por debajo se sigue la función del cable de array, pero sin tener que salir desde la caja, ya en la zona de zanja                                                           
                                                                if f_bc!=np.count_nonzero(~np.isnan(filas_en_cajas[i,bc,:,0]))-1: #hay una excepción, si estamos en el borde ya no entramos en la funcion de la polilinea porque sino volveriamos hacia atras
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, bc, c, p, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                                
                                                                #Ahora vuelve a abrirse el arbol, si las banda a la que se saltó era anexa o separada ya hemos llevado los cables a los puntos de espera en la PCS (PENDIENTE OPTIMIZAR, falta rematarlos)
                                                                if bandas_anexas[i,bc]==True:
                                                                    pol_array_cable[i,b,c,p,0] = coord_PCS_DC_inputs[i,0]
                                                                    pol_array_cable[i,b,c,p,1] = coord_PCS_DC_inputs[i,1]
                                                                    
                                                                elif bandas_separadas[i,bc]==True or bandas_aisladas[i,bc]==True: #si partimos del punto de espera de la separada, podemos intentar saltar horizontalmente hasta la banda anexa
                                                                    
                                                                    bajada_necesaria = False #ya estamos en la parte inferior de la banda separada o aislada
                                                                    pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc, f_bc, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)
                                                                           
                                                                else: #si por el contrario hemos saltado a una intermedia (y estamos en su parte baja) tenemos que dar otro grado de profundidad y bajar a la de abajo
                                                                #identificamos la banda de abajo
                                                                    for bc2_pot in range(bc+1,max_b): 
                                                                        if bandas_anexas[i,bc2_pot]==True:
                                                                            bc2=bc2_pot
                                                                        elif bandas_separadas[i,bc2_pot]==True:
                                                                            bc2=bc2_pot
                                                                        elif bandas_aisladas[i,bc2_pot]==True: #Estos tres ifs evitan que se coja otra intermedia en el bucle de busqueda
                                                                            bc2=bc2_pot                                                                      

                                                                        #LA BANDA DE ABAJO ERA ANEXA - hemos alcanzado la PCS
                                                                        if bandas_anexas[i,bc]==True: #si bc era anexa entonces hemos llegado a la vertical por definicion y tendriamos que meternos en el pasillo                                                                           
                                                                            
                                                                            #cuidado al comprobar si el numero de circuitos permite que haya una sola zanja o hay que ir por dos pasillos, pues ahora van dos bandas
                                                                            pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable[i,b,c], circuitos_en_banda[i,b]+circuitos_en_banda[i,bc], n_circuitos_max_entre_trackers, pitch)
                                                                            #TODO falta coordinar las bajadas en dos pasillo con los cables de las distintas bandas
                                                                                
                                                                        #LA BANDA DE ABAJO ERA SEPARADA O AISLADA - no se alcanzó la PCS al recorrer la parte inferior de la banda intermedia, pero se alcanzó la parte más a la derecha de ella
                                                                        else: 
                                                                            #Hay que llevar los circuitos hasta la parte más a la derecha de la banda de abajo (estamos en el extremo de la intermedia), para ello hay que ver si podemos bajar los circuitos para ir por debajo de la banda o hace falta recorrerla por encima
                                                                            circuitos_izq_bc2 = np.count_nonzero(~np.isnan(cajas_fisicas[i,bc,cajas_fisicas[i,bc2,:,1] < coord_PCS_DC_inputs[i,0],0]))
                                                                            
                                                                            if circuitos_en_banda[i,b] + circuitos_en_banda[i,bc] + circuitos_izq_bc2 > n_circuitos_max_lado_PCS: #si llevasemos demasiados circuitos por el pasillo del camino
                                                                                
                                                                                #buscamos la fila actualizada y seguimos recorriendo la banda por arriba hasta llegar a su limite
                                                                                f_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(pol_array_cable[i,b,c,p,0]-pitch/2)))
                                                                                
                                                                                while f_bc2 < np.count_nonzero(~np.isnan(filas_en_cajas[i,bc2,:,0]))-1: #se recorre la banda por arriba mientras no se llegue al final de las filas de la banda
                                                                                    pol_array_cable[i,b,c,p+1,0] = filas_en_cajas[i,bc,f_bc,2]
                                                                                    pol_array_cable[i,b,c,p+1,1] = filas_en_bandas[i,bc,f_bc,0,3]+filas_en_bandas[i,bc,f_bc,0,1]+sep_zanja_tracker
                                                                                    p=p+1
                                                                                    f_bc2=f_bc2+1
                                                                                    
                                                                                bajada_necesaria = True #hay que bajar por el extremo, hemos llegado al f_bc2 maximo
                                                                                pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc2, f_bc2, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)
                                                                                                                                           
                                                                            elif circuitos_en_banda[i,b] + circuitos_en_banda[i,bc] + circuitos_izq_bc2 <= n_circuitos_max_lado_PCS: #si los circuitos pueden ir por abajo, los bajamos para ahorrar zanja, repitiendo lo que se hizo desde la banda extrema a la intermedia       
                                                                                #TODO, faltaria por ver si se pueden meter en un pasillo o tienen que ser en 2
                             
                                                                                f_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(pol_array_cable[i,b,c,p,0])))
                                                                                
                                                                                pol_array_cable[i,b,c,p+1,0] = pol_array_cable[i,b,c,p,0]+pitch/2
                                                                                pol_array_cable[i,b,c,p+1,1] = pol_array_cable[i,b,c,p]
                                                                                
                                                                                pol_array_cable[i,b,c,p+2,0] = pol_array_cable[i,b,c,p+1,0]
                                                                                pol_array_cable[i,b,c,p+2,1] = filas_en_cajas[i,bc,f_bc+1,3] - sep_caja_tracker - largo_caja/2 - salida_zanja_LV_caja_inv
                                                                                
                                                                                p=p+2
                                                                                
                                                                                #Independientemente de la banda a la que se salte, al ir ya por debajo se sigue la función del cable de array, pero sin salir de la caja, sino tras haber enlazado con la más cercana
                                                                                pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, bc, c, p, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)        
                                                                                
                                                                                #Faltaria ir desde el punto de espera de la banda separada o aislada hasta la anexa, sin necesidad de bajada porque ya estamos en la parte inferior
                                                                                bajada_necesaria = False #hay que bajar por el extremo, hemos llegado al f_bc2 maximo
                                                                                pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc2, f_bc2, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)      
                                               
                                                elif filas_en_bandas[i,b,0,0,2] - coord_PCS_DC_inputs[i,0] > 0: #la banda se queda a la derecha de la PCS 
                                                    circuitos_der_bc = np.count_nonzero(~np.isnan(cajas_fisicas[i,bc,cajas_fisicas[i,bc,:,1] > coord_PCS_DC_inputs[i,0],0]))
                                                    circuitos_en_banda[i,b] = np.count_nonzero(~np.isnan(cajas_fisicas[i,b,:,0]))
     
                                                    if circuitos_en_banda[i,b]+circuitos_der_bc > n_circuitos_max_lado_PCS: #Si hay demasiados circuitos bordeamos por arriba la banda inferior hasta llegar a la altura de la PCS
                                                        for c in range(0,max_c):
                                                            if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía
                                                           
                                                                if bandas_anexas[i,bc]==True: #si la banda inferior es anexa a la PCS el punto de referencia para los cables es la PCS (aunque no lleguen en b, saltaran a bc y seguiran por ella)   
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                                else:
                                                                    #si la banda inferior no es anexa entonces no está garantizado que llegue más a la izquierda que el extremo de la superior (podría ser una separada más a la derecha o una intermedia más a la derecha)
                                                                    #para evitar retroceder luego potencialmente con las cajas de esa banda, nos quedamos como puerto con la x menos cercana a la PCS entre los extremos más cercanos de las dos bandas
                                                                    referencia_x_puerto = np.nanmax([np.nanmin(filas_en_cajas[i,b,:,2]),np.nanmin(filas_en_cajas[i,bc,:,2])]) #si fuese la superior se estaría llegando al extremo igualmente
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,referencia_x_puerto,0,sep_caja_tracker, orientacion, pitch)                                                              

                                                                f_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(pol_array_cable[i,b,c,p,0]))) #vemos en que fila de la banda inferior caemos                                                                   
                                                               
                                                                while abs(pol_array_cable[i,b,c,p,0] - coord_PCS_DC_inputs[i,0]) > pitch and f_bc > 0: #se recorre la banda por arriba mientras no se alcance la PCS ni se llegue al final de las filas de la banda
                                                                    pol_array_cable[i,b,c,p+1,0] = filas_en_cajas[i,bc,f_bc,2]
                                                                    pol_array_cable[i,b,c,p+1,1] = filas_en_bandas[i,bc,f_bc,0,3]+filas_en_bandas[i,bc,f_bc,0,1]+sep_zanja_tracker
                                                                    p=p+1
                                                                    f_bc=f_bc-1
                                                               
                                                                #SE HABIA SALTADO A UNA BANDA ANEXA 
                                                                if bandas_anexas[i,bc]==True: #si bc era anexa entonces hemos llegado a la vertical por definicion y tendriamos que meternos en el pasillo                                                                           
                                                                   
                                                                    pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable[i,b,c], circuitos_en_banda[i,b], n_circuitos_max_entre_trackers, pitch)

                                                                #SE HABIA SALTADO A UNA BANDA SEPARADA O AISLADA   
                                                                elif bandas_separadas[i,bc]==True or bandas_aisladas[i,bc]==True: #si era separada o aislada no hemos llegado a la PCS pero sí al borde de la banda
                                                                   
                                                                    bajada_necesaria=True
                                                                    pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc, f_bc, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)                                                              
                                                                                                                                     
                                                                #SE HABIA SALTADO A UNA BANDA INTERMEDIA
                                                                else: #si no es niguna de las dos anteriores es porque se trata de una banda intermedia y tiene otra banda (anexa o separada) debajo
                                                                    for bc_anex_pot in range(bc,-1, -1): #identificamos cual es la banda anexa o separada
                                                                        if bandas_anexas[i,bc_anex_pot]==True or bandas_separadas[i,bc_anex_pot]==True: #POTENCIAL PROBLEMA QUE SE VAYA A OTRA POSTERIOR?
                                                                            bc2=bc_anex_pot
                                                                            
                                                                    #buscamos la fila correspondiente dentro de dicha banda
                                                                    p=p+1
                                                                    f_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(pol_array_cable[i,b,c,p,0])))
                                                                    
                                                                    #recorremos la banda por encima, si antes no hemos entrado por abajo ahora con menos motivo, al llevar sumados los de la anterior
                                                                    while abs(pol_array_cable[i,b,c,p,0] - coord_PCS_DC_inputs[i,0]) > pitch and f_bc2 > 0: #se recorre la banda por arriba mientras no se alcance la PCS ni se llegue al final de las filas de la banda
                                                                        pol_array_cable[i,b,c,p+1,0] = filas_en_cajas[i,bc,f_bc2,2]
                                                                        pol_array_cable[i,b,c,p+1,1] = filas_en_bandas[i,bc,f_bc2,0,3]+filas_en_bandas[i,bc,f_bc2,0,1]+sep_zanja_tracker
                                                                        p=p+1
                                                                        f_bc2=f_bc2-1
                                                                        
                                                                    #SI LA BANDA DE ABAJO ES ANEXA - Se ha salido del while llegando a la altura de la PCS
                                                                    if bandas_anexas[i,bc2]==True: #si bc era anexa entonces hemos llegado a la vertical por definicion y tendriamos que meternos en el pasillo         
                                                                       
                                                                        #cuidado al comprobar si el numero de circuitos permite que haya una sola zanja o hay que ir por dos pasillos, pues ahora van dos bandas
                                                                        pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable[i,b,c], circuitos_en_banda[i,b]+circuitos_en_banda[i,bc], n_circuitos_max_entre_trackers, pitch)
                                                                        #TODO falta coordinar las bajadas en dos pasillo con los cables de las distintas bandas
                                                                                                                                                          
                                                                    #SI LA BANDA DE ABAJO ES SEPARADA O AISLADA - Se ha salido del while llegando a la ultima fila de la banda (se podria poner un else porque no hay mas saltos a intermedias contemplados)
                                                                    elif bandas_separadas[i,bc2]==True or bandas_aisladas[i,bc2]==True: #si era separada o aislada no hemos llegado a la PCS pero sí al borde de la banda
                                                                        
                                                                        bajada_necesaria = True
                                                                        pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc2, f_bc2, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)
                                                                                                                          
                                                    elif circuitos_en_banda[i,b]+circuitos_der_bc <= n_circuitos_max_lado_PCS: #Si no hay demasiados circuitos podemos bajar directamente a la inferior
                                                        for c in range(0,max_c):
                                                            if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                                                            
                                                            #TODO, faltaria por ver si se pueden meter en un pasillo o tienen que ser en 2
                                                                if bandas_anexas[i,bc]==True:   
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                                else:                                                               
                                                                    referencia_x_puerto = np.nanmax([np.nanmin(filas_en_cajas[i,b,:,2]),np.nanmin(filas_en_cajas[i,bc,:,2])]) #si fuese la superior se estaría llegando al extremo igualmente
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,referencia_x_puerto,0,sep_caja_tracker, orientacion, pitch)                                                              

                                                                f_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(pol_array_cable[i,b,c,p,0])))
                                                                
                                                                pol_array_cable[i,b,c,p+1,0] = pol_array_cable[i,b,c,p,0]-pitch/2
                                                                pol_array_cable[i,b,c,p+1,1] = pol_array_cable[i,b,c,p,1]
                                                                
                                                                pol_array_cable[i,b,c,p+2,0] = pol_array_cable[i,b,c,p+1,0]
                                                                pol_array_cable[i,b,c,p+2,1] = filas_en_cajas[i,bc,f_bc,3] - sep_caja_tracker - largo_caja/2 - salida_zanja_LV_caja_inv
                                                                
                                                                p=p+2
                                                                
                                                                #Independientemente de la banda a la que se salte, al ir ya por debajo se sigue la función del cable de array, pero sin tener que salir desde la caja, ya en la zona de zanja                                                           
                                                                if f_bc!=0: #hay una excepción, si estamos en el borde ya no entramos en la funcion de la polilinea porque sino volveriamos hacia atras
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, bc, c, p, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                                
                                                                #Ahora vuelve a abrirse el arbol, si las banda a la que se saltó era anexa o separada ya hemos llevado los cables a los puntos de espera en la PCS (PENDIENTE OPTIMIZAR, falta rematarlos)
                                                                if bandas_anexas[i,bc]==True:
                                                                    pol_array_cable[i,b,c,p,0] = coord_PCS_DC_inputs[i,0]
                                                                    pol_array_cable[i,b,c,p,1] = coord_PCS_DC_inputs[i,1]
                                                                    
                                                                elif bandas_separadas[i,bc]==True or bandas_aisladas[i,bc]==True: #si partimos del punto de espera de la separada, podemos intentar saltar horizontalmente hasta la banda anexa
                                                                    
                                                                    bajada_necesaria = False #ya estamos en la parte inferior de la banda separada o aislada
                                                                    pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc, f_bc, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)
                                                                           
                                                                else: #si por el contrario hemos saltado a una intermedia (y estamos en su parte baja) tenemos que dar otro grado de profundidad y bajar a la de abajo
                                                                #identificamos la banda de abajo
                                                                    for bc2_pot in range(bc,-1,-1): 
                                                                        if bandas_anexas[i,bc2_pot]==True:
                                                                            bc2=bc2_pot
                                                                        elif bandas_separadas[i,bc2_pot]==True:
                                                                            bc2=bc2_pot
                                                                        elif bandas_aisladas[i,bc2_pot]==True: #Estos tres ifs evitan que se coja otra intermedia en el bucle de busqueda
                                                                            bc2=bc2_pot                                                                      
                                                        
                                                                        #LA BANDA DE ABAJO ERA ANEXA - hemos alcanzado la PCS
                                                                        if bandas_anexas[i,bc]==True: #si bc era anexa entonces hemos llegado a la vertical por definicion y tendriamos que meternos en el pasillo                                                                           
                                                                            
                                                                            #cuidado al comprobar si el numero de circuitos permite que haya una sola zanja o hay que ir por dos pasillos, pues ahora van dos bandas
                                                                            pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable[i,b,c], circuitos_en_banda[i,b]+circuitos_en_banda[i,bc], n_circuitos_max_entre_trackers, pitch)
                                                                            #TODO falta coordinar las bajadas en dos pasillo con los cables de las distintas bandas
                                                                                
                                                                        #LA BANDA DE ABAJO ERA SEPARADA O AISLADA - no se alcanzó la PCS al recorrer la parte inferior de la banda intermedia, pero se alcanzó la parte más a la derecha de ella
                                                                        else: 
                                                                            #Hay que llevar los circuitos hasta la parte más a la derecha de la banda de abajo (estamos en el extremo de la intermedia), para ello hay que ver si podemos bajar los circuitos para ir por debajo de la banda o hace falta recorrerla por encima
                                                                            circuitos_der_bc2 = np.count_nonzero(~np.isnan(cajas_fisicas[i,bc,cajas_fisicas[i,bc2,:,1] > coord_PCS_DC_inputs[i,0],0]))
                                                                            
                                                                            if circuitos_en_banda[i,b] + circuitos_en_banda[i,bc] + circuitos_der_bc2 > n_circuitos_max_lado_PCS: #si llevasemos demasiados circuitos por el pasillo del camino
                                                                                
                                                                                #buscamos la fila actualizada y seguimos recorriendo la banda por arriba hasta llegar a su limite
                                                                                f_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(pol_array_cable[i,b,c,p,0]+pitch/2)))
                                                                                
                                                                                while f_bc2 > 0: #se recorre la banda por arriba mientras no se llegue al final de las filas de la banda
                                                                                    pol_array_cable[i,b,c,p+1,0] = filas_en_cajas[i,bc,f_bc,2]
                                                                                    pol_array_cable[i,b,c,p+1,1] = filas_en_bandas[i,bc,f_bc,0,3]+filas_en_bandas[i,bc,f_bc,0,1]+sep_zanja_tracker
                                                                                    p=p+1
                                                                                    f_bc2=f_bc2-1
                                                                                    
                                                                                bajada_necesaria = True #hay que bajar por el extremo, hemos llegado al f_bc2 maximo
                                                                                pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc2, f_bc2, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)
                                                                                                                                           
                                                                            elif circuitos_en_banda[i,b] + circuitos_en_banda[i,bc] + circuitos_der_bc2 <= n_circuitos_max_lado_PCS: #si los circuitos pueden ir por abajo, los bajamos para ahorrar zanja, repitiendo lo que se hizo desde la banda extrema a la intermedia       
                                                                                #TODO, faltaria por ver si se pueden meter en un pasillo o tienen que ser en 2
                                                        
                                                                                f_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(pol_array_cable[i,b,c,p,0])))
                                                                                
                                                                                pol_array_cable[i,b,c,p+1,0] = pol_array_cable[i,b,c,p,0]-pitch/2
                                                                                pol_array_cable[i,b,c,p+1,1] = pol_array_cable[i,b,c,p,1]
                                                                                
                                                                                pol_array_cable[i,b,c,p+2,0] = pol_array_cable[i,b,c,p+1,0]
                                                                                pol_array_cable[i,b,c,p+2,1] = filas_en_cajas[i,bc,f_bc,3] - sep_caja_tracker - largo_caja/2 - salida_zanja_LV_caja_inv
                                                                                
                                                                                p=p+2
                                                                                
                                                                                #Independientemente de la banda a la que se salte, al ir ya por debajo se sigue la función del cable de array, pero sin salir de la caja, sino tras haber enlazado con la más cercana
                                                                                pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, bc, c, p, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)        
                                                                                
                                                                                #Faltaria ir desde el punto de espera de la banda separada o aislada hasta la anexa, sin necesidad de bajada porque ya estamos en la parte inferior
                                                                                bajada_necesaria = False #hay que bajar por el extremo, hemos llegado al f_bc2 maximo
                                                                                pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc2, f_bc2, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)      

                                                                                                                               
                                            else: #sí que está situada directamente encima de la PCS
                                                  circuitos_en_banda[i,b] = np.count_nonzero(~np.isnan(cajas_fisicas[i,b,:,0])) #POSIBLE OPTIMIZAR, SE PUEDEN METER AQUI LOS CIRCUITOS DE OTRAS BANDAS Y RELLENAR ZANJAS
                                                 
                                                  if circuitos_en_banda[i,b] <= n_circuitos_max_entre_trackers: #si los circuitos caben en una sola zanja, hay un solo puerto, buscamos el punto más próximo a la vertical de la PCS y los bajamos desde ahí
                                                     
                                                      indice_fila_puerto=np.nanargmin(np.abs(filas_en_cajas[i,b,:,2]-coord_PCS_DC_inputs[i,0]))
                                                      puerto_x=filas_en_cajas[i,b,indice_fila_puerto,2]+pitch/2 #la X del puerto cae en la mitad del pasillo entre filas
                                                      if filas_en_cajas[i,b,indice_fila_puerto,3] <= filas_en_cajas[i,b,indice_fila_puerto+1,3]: #la Y del puerto tiene que ser la del lado que está más al sur, mas cerca de la PCS 
                                                          puerto_y=filas_en_cajas[i,b,indice_fila_puerto,3] - sep_caja_tracker - largo_caja/2 - salida_zanja_LV_caja_inv 
                                                      else:
                                                          puerto_y=filas_en_cajas[i,b,indice_fila_puerto+1,3] - sep_caja_tracker - largo_caja/2 - salida_zanja_LV_caja_inv
                                                         
                                                      for c in range(0,max_c):
                                                          if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                                                              pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                              pol_array_cable[i,b,c,p+1,0] = puerto_x
                                                              pol_array_cable[i,b,c,p+1,1] = puerto_y
                                                              #desde el puerto se baja hasta la altura inferior de la otra banda para dar ese punto de cara a la definición de la zanja, para ello se calcula cual es la fila de esa banda anexa en cuyo pasillo se está bajando
                                                              indice_fila_puerto_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(puerto_x-pitch/2)))
                                                              pol_array_cable[i,b,c,p+2,0] = puerto_x
                                                              pol_array_cable[i,b,c,p+2,1] = (filas_en_cajas[i,bc,indice_fila_puerto_bc,3]+filas_en_cajas[i,bc,indice_fila_puerto_bc+1,3])/2 #PROVISIONALMENTE LE DAMOS LA ALTURA MEDIA DE LAS DOS FILAS QUE FORMAN EL PASILLO
                                                            #llevamos dos bandas de profundidad, si estamos ya en la banda anexa al inversor la zanja va a la PCS, si no lo estamos, sigue bajando
                                                              if bandas_anexas[i,bc]==True:
                                                                  pol_array_cable[i,b,c,p+3,0] = coord_PCS_DC_inputs[i,0]
                                                                  pol_array_cable[i,b,c,p+3,1] = coord_PCS_DC_inputs[i,1]
                                                              elif bandas_separadas[i,bc]==True: #si estabamos en otro bloque de bandas y hemos llegado a una separada, PROVISIONALMENTE LA LLEVAMOS DIRECTOS A LA PCS (POSIBLE OPTIMIZAR SIGUIENDO EL CAMINO)
                                                                  pol_array_cable[i,b,c,p+3,0] = coord_PCS_DC_inputs[i,0]
                                                                  pol_array_cable[i,b,c,p+3,1] = coord_PCS_DC_inputs[i,1]
                                                              else: #en este caso bc era una banda intermedia, las polilineas de b tienen que seguir bajando hasta la anexa, que hay que identificar
                                                                 
                                                                  for bc_anex_pot in range(bc+1,max_b): #identificamos cual es la banda anexa
                                                                      if bandas_anexas[i,bc_anex_pot]==True:
                                                                          bc2=bc_anex_pot
                                                                         
                                                                  indice_fila_puerto_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(puerto_x-pitch/2)))
                                                                  pol_array_cable[i,b,c,p+3,0] = puerto_x
                                                                  pol_array_cable[i,b,c,p+3,1] = (filas_en_cajas[i,bc,indice_fila_puerto_bc2,3]+filas_en_cajas[i,bc,indice_fila_puerto_bc2+1,3])/2 #PROVISIONALMENTE LE DAMOS LA ALTURA MEDIA DE LAS DOS FILAS QUE FORMAN EL PASILLO
                                                                 
                                                                  pol_array_cable[i,b,c,p+4,0] = coord_PCS_DC_inputs[i,0]
                                                                  pol_array_cable[i,b,c,p+4,1] = coord_PCS_DC_inputs[i,1]
             
                                                                 
                                                  else:  #si no podemos tirar todo en una sola zanja, se definen dos "puertos" de paso
                                                      indice_fila_puerto_1=np.nanargmin(np.abs(filas_en_cajas[i,b,:,2]-(coord_PCS_DC_inputs[i,0]-pitch))) #entra en - pitch en lugar de -2 pitch para tener margen
                                                      puerto_1_x=filas_en_cajas[i,b,indice_fila_puerto_1,2]+pitch/2 
                                                      if filas_en_cajas[i,b,indice_fila_puerto_1,3] <= filas_en_cajas[i,b,indice_fila_puerto_1+1,3]: 
                                                          puerto_1_y=filas_en_cajas[i,b,indice_fila_puerto_1,3] - sep_caja_tracker - largo_caja - salida_zanja_LV_caja_inv 
                                                      else:
                                                          puerto_1_y=filas_en_cajas[i,b,indice_fila_puerto_1+1,3] - sep_caja_tracker - largo_caja - salida_zanja_LV_caja_inv
                                                      
                                                      indice_fila_puerto_2=np.nanargmin(np.abs(filas_en_cajas[i,b,:,2]-(coord_PCS_DC_inputs[i,0]+pitch)))
                                                      puerto_2_x=filas_en_cajas[i,b,indice_fila_puerto_2,2]-pitch/2
                                                      if filas_en_cajas[i,b,indice_fila_puerto_2,3] <= filas_en_cajas[i,b,indice_fila_puerto_2-1,3]:
                                                          puerto_2_y=filas_en_cajas[i,b,indice_fila_puerto_2,3] - sep_caja_tracker - largo_caja - salida_zanja_LV_caja_inv 
                                                      else:
                                                          puerto_2_y=filas_en_cajas[i,b,indice_fila_puerto_2-1,3] - sep_caja_tracker - largo_caja - salida_zanja_LV_caja_inv
                                                      
                                                      for c in range(0,max_c):
                                                          if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                                                              if c < circuitos_en_banda[i,b]/2 : #está limitado a 2 puertos, POSIBLE OPTIMIZAR, AHORA ESTA HECHO PARA LLEVAR  MITAD Y MITAD PERO PUEDE HACERSE DESIGUAL Y EVITAR CRUCES
                                                                  pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,puerto_1_x,pitch,sep_caja_tracker, orientacion, pitch) 
                                                                  pol_array_cable[i,b,c,p+1,0] = puerto_1_x #hasta la mitad del max las llevamos a un puerto a la izquierda de la PCS, 
                                                                  pol_array_cable[i,b,c,p+1,1] = puerto_1_y
                                                                  #desde el puerto se baja hasta la altura inferior de la otra banda, para ello se calcula cual es la fila de esa banda anexa en cuyo pasillo se está bajando (POSIBLE OPTIMIZAR IDENTIFICANDO EN QUE FILA CAEN DE ELLA POR SI HAY UN DESFASE DE PASILLOS)
                                                                  indice_fila_puerto_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(puerto_1_x-pitch/2)))
                                                                  pol_array_cable[i,b,c,p+2,0] = puerto_1_x
                                                                  pol_array_cable[i,b,c,p+2,1] = (filas_en_cajas[i,bc,indice_fila_puerto_bc,3]+filas_en_cajas[i,bc,indice_fila_puerto_bc+1,3])/2 #PROVISIONALMENTE
                                                              #llevamos dos bandas de profundidad, si estamos ya en la banda anexa al inversor la zanja va a la PCS, si no lo estamos, sigue bajando
                                                                  if bandas_anexas[i,bc]==True:
                                                                      pol_array_cable[i,b,c,p+3,0] = coord_PCS_DC_inputs[i,0]
                                                                      pol_array_cable[i,b,c,p+3,1] = coord_PCS_DC_inputs[i,1]
                                                                  elif bandas_separadas[i,bc]==True: #si estabamos en otro bloque de bandas y hemos llegado a una separada, PROVISIONALMENTE LA LLEVAMOS DIRECTOS A LA PCS (POSIBLE OPTIMIZAR SIGUIENDO EL CAMINO)
                                                                      pol_array_cable[i,b,c,p+3,0] = coord_PCS_DC_inputs[i,0]
                                                                      pol_array_cable[i,b,c,p+3,1] = coord_PCS_DC_inputs[i,1]
                                                                  else: #en este caso bc era una banda intermedia, las polilineas de b tienen que seguir bajando hasta la anexa, que hay que identificar
                                                                      
                                                                      for bc_anex_pot in range(bc+1,max_b): #identificamos cual es la banda anexa
                                                                          if bandas_anexas[i,bc_anex_pot]==True:
                                                                              bc2=bc_anex_pot
                                                                              
                                                                      indice_fila_puerto_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(puerto_x-pitch/2)))
                                                                      pol_array_cable[i,b,c,p+3,0] = puerto_1_x
                                                                      pol_array_cable[i,b,c,p+3,1] = (filas_en_cajas[i,bc,indice_fila_puerto_bc2,3]+filas_en_cajas[i,bc,indice_fila_puerto_bc2+1,3])/2 #PROVISIONALMENTE LE DAMOS LA ALTURA MEDIA DE LAS DOS FILAS QUE FORMAN EL PASILLO
                                                                      
                                                                      pol_array_cable[i,b,c,p+4,0] = coord_PCS_DC_inputs[i,0]
                                                                      pol_array_cable[i,b,c,p+4,1] = coord_PCS_DC_inputs[i,1]
                                                              else:
                                                                  pol_array_cable[i,b,c] , p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,puerto_2_x,pitch,sep_caja_tracker, orientacion, pitch) 
                                                                  pol_array_cable[i,b,c,p+1,0] = puerto_2_x  #mas alla de la mitad del max las llevamos a un puerto a la izquierda de la PCS
                                                                  pol_array_cable[i,b,c,p+1,1] = puerto_2_y 
                                                                  #desde el puerto se asume provisionalmente que van directos hasta la zona de aproximacion a la PCS atravesando cualquier banda intermedia (POSIBLE OPTIMIZAR IDENTIFICANDO EN QUE FILA CAEN DE ELLA POR SI HAY UN DESFASE DE PASILLOS)
                                                                  indice_fila_puerto_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(puerto_2_x-pitch/2)))
                                                                  pol_array_cable[i,b,c,p+2,0] = puerto_2_x
                                                                  pol_array_cable[i,b,c,p+2,1] = (filas_en_cajas[i,bc,indice_fila_puerto_bc,3]+filas_en_cajas[i,bc,indice_fila_puerto_bc+1,3])/2 #PROVISIONALMENTE
                                                              #llevamos dos bandas de profundidad, si estamos ya en la banda anexa al inversor la zanja va a la PCS, si no lo estamos, sigue bajando
                                                                  if bandas_anexas[i,bc]==True:
                                                                      pol_array_cable[i,b,c,p+3,0] = coord_PCS_DC_inputs[i,0]
                                                                      pol_array_cable[i,b,c,p+3,1] = coord_PCS_DC_inputs[i,1]
                                                                  elif bandas_separadas[i,bc]==True: #si estabamos en otro bloque de bandas y hemos llegado a una separada, PROVISIONALMENTE LA LLEVAMOS DIRECTOS A LA PCS (POSIBLE OPTIMIZAR SIGUIENDO EL CAMINO)
                                                                      pol_array_cable[i,b,c,p+3,0] = coord_PCS_DC_inputs[i,0]
                                                                      pol_array_cable[i,b,c,p+3,1] = coord_PCS_DC_inputs[i,1]
                                                                  else: #en este caso bc era una banda intermedia, las polilineas de b tienen que seguir bajando hasta la anexa, que hay que identificar
                                                                      
                                                                      for bc_anex_pot in range(bc+1,max_b): #identificamos cual es la banda anexa
                                                                          if bandas_anexas[i,bc_anex_pot]==True:
                                                                              bc2=bc_anex_pot
                                                                              
                                                                      indice_fila_puerto_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(puerto_x-pitch/2)))
                                                                      pol_array_cable[i,b,c,p+3,0] = puerto_2_x
                                                                      pol_array_cable[i,b,c,p+3,1] = (filas_en_cajas[i,bc,indice_fila_puerto_bc2,3]+filas_en_cajas[i,bc,indice_fila_puerto_bc2+1,3])/2 #PROVISIONALMENTE LE DAMOS LA ALTURA MEDIA DE LAS DOS FILAS QUE FORMAN EL PASILLO
                                                                      
                                                                      pol_array_cable[i,b,c,p+4,0] = coord_PCS_DC_inputs[i,0]
                                                                      pol_array_cable[i,b,c,p+4,1] = coord_PCS_DC_inputs[i,1]
                  
                                            #anotamos que se ha analizado ya la banda b para no entrar en los bucles for de busqueda de posicion relativa previos                                                                                                                         
                                            banda_analizada=True                 
                                            break #rompemos el bucle for
                            if banda_analizada==True:
                                break #ponemos break para que la transferencia de b solo se haga una vez, hasta bc
                               
                    elif orientacion[i,b]=='N': 
                        for bc in range(b-1,-1,-1): #si está encima (al norte) tiene que tener un numero de banda menor
                            if orientacion[i,bc]=='N':

                                for fila in filas_en_cajas[i,b]:
                                    if banda_analizada==True:
                                        break #ponemos este break para que no se repitan las filas del for una vez se compruebe si ambas bandas estan debajo y se analice su paso de cable de array
                                                                       
                                    for fila_c in filas_en_cajas[i,bc]:
                                        if abs(fila[2] - fila_c[2]) < pitch: #si esto se cumple está pasando que b está encima de bc siendo bc una banda en el mismo lado del camino, por lo que habra que bajar sus circuitos por ella
                                            #SIN EMBARGO, que b esté encima de bc no significa que esté encima de la PCS directamente, aunque bc sea anexa, hay que ver si b llega a enfilar la PCS o no
                                            enfila_PCS = False
                                            for fila in filas_en_cajas[i,b]:
                                                if abs(fila[2] - coord_PCS_DC_inputs[i,0]) < 2*pitch:
                                                    enfila_PCS = True
                                                    break
                                                
                                            if enfila_PCS==False: #si por mucho que nos movamos en la banda no vamos a encontrar la vertical de la PCS, veremos en qué lado de la PCS estamos y cuantos circuitos en ese lado de la PCS tienen el resto de bandas, si tienen demasiados alargaremos el recorrido para evitar zanjas demasiado grandes en ellas
                                                if filas_en_bandas[i,b,0,0,2] - coord_PCS_DC_inputs[i,0] < 0: #la banda se queda a la izquierda de la PCS
                                                    circuitos_izq_bc = np.count_nonzero(~np.isnan(cajas_fisicas[i,bc,cajas_fisicas[i,bc,:,1] < coord_PCS_DC_inputs[i,0],0]))

                                                    if circuitos_en_banda[i,b]+circuitos_izq_bc > n_circuitos_max_lado_PCS: #Si hay demasiados circuitos bordeamos por abajo la banda inferior hasta llegar a la altura de la PCS
                                                        for c in range(0,max_c):
                                                            if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                                                                
                                                                if bandas_anexas[i,bc]==True: #si la banda inferior es anexa a la PCS el punto de referencia para los cables es la PCS (aunque no lleguen en b, saltaran a bc y seguiran por ella)   
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                                else:
                                                                    #si la banda superior no es anexa entonces no está garantizado que llegue más a la derecha que el extremo de la inferior (podría ser una separada más a la izquierda o una intermedia más a la izquierda)
                                                                    #para evitar retroceder luego potencialmente con las cajas de esa banda, nos quedamos como puerto con la x menos cercana a la PCS entre los extremos más cercanos de las dos bandas
                                                                    referencia_x_puerto = np.nanmin([np.nanmax(filas_en_cajas[i,b,:,2]),np.nanmax(filas_en_cajas[i,bc,:,2])]) #si fuese la superior se estaría llegando al extremo igualmente
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,referencia_x_puerto,0,sep_caja_tracker, orientacion, pitch)                                                              
                    
                                                                f_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(pol_array_cable[i,b,c,p,0]))) #vemos en que fila de la banda inferior caemos
                                                                
                                                                while abs(pol_array_cable[i,b,c,p,0] - coord_PCS_DC_inputs[i,0]) > pitch and f_bc > 0: #se recorre la banda por abajo mientras no se alcance la PCS ni se llegue al final de las filas de la banda, si se daba alguna de esas casuisticas ya antes no se entra en el while
                                                                    pol_array_cable[i,b,c,p+1,0] = filas_en_cajas[i,bc,f_bc,2]
                                                                    pol_array_cable[i,b,c,p+1,1] = filas_en_bandas[i,bc,f_bc,0,3]-filas_en_bandas[i,bc,f_bc,0,1]-sep_zanja_tracker
                                                                    p=p+1
                                                                    f_bc=f_bc-1
                                                                
                                                                #SE HABIA SALTADO A UNA BANDA ANEXA 
                                                                if bandas_anexas[i,bc]==True: #si bc era anexa entonces ya hemos llegado a la vertical por definicion y tendriamos que meternos en el pasillo                                                                           
                                                                    
                                                                    pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable[i,b,c], circuitos_en_banda[i,b], n_circuitos_max_entre_trackers, pitch)
                    
                                                                #SE HABIA SALTADO A UNA BANDA SEPARADA O AISLADA   
                                                                elif bandas_separadas[i,bc]==True or bandas_aisladas[i,bc]==True: #si era separada o aislada no hemos llegado a la PCS pero sí al borde de la banda
                                                                    
                                                                    bajada_necesaria=True
                                                                    pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc, f_bc, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas,coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)                                                              
                                                                                                                                      
                                                                #SE HABIA SALTADO A UNA BANDA INTERMEDIA
                                                                else: #si no es niguna de las dos anteriores es porque se trata de una banda intermedia y tiene otra banda (anexa o separada) debajo
                                                                      for bc_anex_pot in range(bc,-1,-1): #identificamos cual es la banda anexa o separada
                                                                          if bandas_anexas[i,bc_anex_pot]==True or bandas_separadas[i,bc_anex_pot]==True: #POTENCIAL PROBLEMA QUE SE VAYA A OTRA POSTERIOR?
                                                                              bc2=bc_anex_pot
                                                                             
                                                                      #buscamos la fila correspondiente dentro de dicha banda
                                                                      p=p+1
                                                                      f_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(pol_array_cable[i,b,c,p,0])))
                                                                     
                                                                      #recorremos la banda por encima, si antes no hemos entrado por abajo ahora con menos motivo, al llevar sumados los de la anterior
                                                                      while abs(pol_array_cable[i,b,c,p,0] - coord_PCS_DC_inputs[i,0]) > pitch and f_bc2 > 0: #se recorre la banda por arriba mientras no se alcance la PCS ni se llegue al final de las filas de la banda
                                                                          pol_array_cable[i,b,c,p+1,0] = filas_en_cajas[i,bc,f_bc2,2]
                                                                          pol_array_cable[i,b,c,p+1,1] = filas_en_bandas[i,bc,f_bc2,0,3]-filas_en_bandas[i,bc,f_bc2,0,1]-sep_zanja_tracker
                                                                          p=p+1
                                                                          f_bc2=f_bc2-1
                                                                         
                                                                    #SI LA BANDA DE ABAJO ES ANEXA - Se ha salido del while llegando a la altura de la PCS
                                                                      if bandas_anexas[i,bc2]==True: #si bc era anexa entonces hemos llegado a la vertical por definicion y tendriamos que meternos en el pasillo         
                                                                        
                                                                        #cuidado al comprobar si el numero de circuitos permite que haya una sola zanja o hay que ir por dos pasillos, pues ahora van dos bandas
                                                                        pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable[i,b,c], circuitos_en_banda[i,b]+circuitos_en_banda[i,bc], n_circuitos_max_entre_trackers, pitch)
                                                                        #TODO falta coordinar las bajadas en dos pasillo con los cables de las distintas bandas
                                                                                                                                                           
                                                                      #SI LA BANDA DE ABAJO ES SEPARADA O AISLADA - Se ha salido del while llegando a la ultima fila de la banda (se podria poner un else porque no hay mas saltos a intermedias contemplados)
                                                                      elif bandas_separadas[i,bc2]==True or bandas_aisladas[i,bc2]==True: #si era separada o aislada no hemos llegado a la PCS pero sí al borde de la banda
                                                                         
                                                                          bajada_necesaria = True
                                                                          pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc2, f_bc2, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)
                                                                    
                                                    elif circuitos_en_banda[i,b]+circuitos_izq_bc <= n_circuitos_max_lado_PCS: #Si no hay demasiados circuitos podemos bajar directamente a la inferior
                                                          for c in range(0,max_c):
                                                              if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                                                              #TODO, faltaria por ver si se pueden meter en un pasillo o tienen que ser en 2
                                                                  if bandas_anexas[i,bc]==True:   
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                                  else:                                                               
                                                                    referencia_x_puerto = np.nanmin([np.nanmax(filas_en_cajas[i,b,:,2]),np.nanmax(filas_en_cajas[i,bc,:,2])]) #si fuese la superior se estaría llegando al extremo igualmente
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,referencia_x_puerto,0,sep_caja_tracker, orientacion, pitch)                                                              
                    
                                                                  f_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(pol_array_cable[i,b,c,p,0])))
                                                                 
                                                                  pol_array_cable[i,b,c,p+1,0] = pol_array_cable[i,b,c,p,0]+pitch/2
                                                                  pol_array_cable[i,b,c,p+1,1] = pol_array_cable[i,b,c,p,1]
                                                                 
                                                                  pol_array_cable[i,b,c,p+2,0] = pol_array_cable[i,b,c,p+1,0]
                                                                  pol_array_cable[i,b,c,p+2,1] = filas_en_cajas[i,bc,f_bc,3] + sep_caja_tracker + largo_caja/2 + salida_zanja_LV_caja_inv
                                                                 
                                                                  p=p+2
                                                                 
                                                                  #Independientemente de la banda a la que se salte, al ir ya por arriba se sigue la función del cable de array, pero sin tener que salir desde la caja, ya en la zona de zanja                                                           
                                                                  if f_bc!=0: #hay una excepción, si estamos en el borde ya no entramos en la funcion de la polilinea porque sino volveriamos hacia atras
                                                                      pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, bc, c, p, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                                 
                                                                  #Ahora vuelve a abrirse el arbol, si las banda a la que se saltó era anexa o separada ya hemos llevado los cables a los puntos de espera en la PCS (PENDIENTE OPTIMIZAR, falta rematarlos)
                                                                  if bandas_anexas[i,bc]==True:
                                                                      pol_array_cable[i,b,c,p,0] = coord_PCS_DC_inputs[i,0]
                                                                      pol_array_cable[i,b,c,p,1] = coord_PCS_DC_inputs[i,1]
                                                                     
                                                                  elif bandas_separadas[i,bc]==True or bandas_aisladas[i,bc]==True: #si partimos del punto de espera de la separada, podemos intentar saltar horizontalmente hasta la banda anexa
                                                                     
                                                                      bajada_necesaria = False #ya estamos en la parte inferior de la banda separada o aislada
                                                                      pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc, f_bc, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)
                                                                            
                                                                  else: #si por el contrario hemos saltado a una intermedia (y estamos en su parte baja) tenemos que dar otro grado de profundidad y bajar a la de abajo
                                                                  #identificamos la banda de abajo
                                                                      for bc2_pot in range(bc,-1,-1): 
                                                                          if bandas_anexas[i,bc2_pot]==True:
                                                                              bc2=bc2_pot
                                                                          elif bandas_separadas[i,bc2_pot]==True:
                                                                              bc2=bc2_pot
                                                                          elif bandas_aisladas[i,bc2_pot]==True: #Estos tres ifs evitan que se coja otra intermedia en el bucle de busqueda
                                                                              bc2=bc2_pot                                                                      
                    
                                                                          #LA BANDA DE ABAJO ERA ANEXA - hemos alcanzado la PCS
                                                                          if bandas_anexas[i,bc]==True: #si bc era anexa entonces hemos llegado a la vertical por definicion y tendriamos que meternos en el pasillo                                                                           
                                                                             
                                                                              #cuidado al comprobar si el numero de circuitos permite que haya una sola zanja o hay que ir por dos pasillos, pues ahora van dos bandas
                                                                              pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable[i,b,c], circuitos_en_banda[i,b]+circuitos_en_banda[i,bc], n_circuitos_max_entre_trackers, pitch)
                                                                              #TODO falta coordinar las bajadas en dos pasillo con los cables de las distintas bandas
                                                                                 
                                                                          #LA BANDA DE ABAJO ERA SEPARADA O AISLADA - no se alcanzó la PCS al recorrer la parte inferior de la banda intermedia, pero se alcanzó la parte más a la derecha de ella
                                                                          else: 
                                                                              #Hay que llevar los circuitos hasta la parte más a la derecha de la banda de abajo (estamos en el extremo de la intermedia), para ello hay que ver si podemos bajar los circuitos para ir por debajo de la banda o hace falta recorrerla por encima
                                                                              circuitos_izq_bc2 = np.count_nonzero(~np.isnan(cajas_fisicas[i,bc,cajas_fisicas[i,bc2,:,1] < coord_PCS_DC_inputs[i,0],0]))
                                                                             
                                                                              if circuitos_en_banda[i,b] + circuitos_en_banda[i,bc] + circuitos_izq_bc2 > n_circuitos_max_lado_PCS: #si llevasemos demasiados circuitos por el pasillo del camino
                                                                                 
                                                                                  #buscamos la fila actualizada y seguimos recorriendo la banda por aabajo hasta llegar a su limite
                                                                                  f_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(pol_array_cable[i,b,c,p,0]-pitch/2)))
                                                                                 
                                                                                  while f_bc2 > 0: #se recorre la banda por abajo mientras no se llegue al final de las filas de la banda
                                                                                      pol_array_cable[i,b,c,p+1,0] = filas_en_cajas[i,bc,f_bc,2]
                                                                                      pol_array_cable[i,b,c,p+1,1] = filas_en_bandas[i,bc,f_bc,0,3]-filas_en_bandas[i,bc,f_bc,0,1]-sep_zanja_tracker
                                                                                      p=p+1
                                                                                      f_bc2=f_bc2-1
                                                                                     
                                                                                  bajada_necesaria = True #hay que bajar por el extremo, hemos llegado al f_bc2 maximo
                                                                                  pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc2, f_bc2, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)
                                                                                                                                            
                                                                              elif circuitos_en_banda[i,b] + circuitos_en_banda[i,bc] + circuitos_izq_bc2 <= n_circuitos_max_lado_PCS: #si los circuitos pueden ir por abajo, los bajamos para ahorrar zanja, repitiendo lo que se hizo desde la banda extrema a la intermedia       
                                                                                  #TODO, faltaria por ver si se pueden meter en un pasillo o tienen que ser en 2
                              
                                                                                  f_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(pol_array_cable[i,b,c,p,0])))
                                                                                 
                                                                                  pol_array_cable[i,b,c,p+1,0] = pol_array_cable[i,b,c,p,0]+pitch/2
                                                                                  pol_array_cable[i,b,c,p+1,1] = pol_array_cable[i,b,c,p]
                                                                                 
                                                                                  pol_array_cable[i,b,c,p+2,0] = pol_array_cable[i,b,c,p+1,0]
                                                                                  pol_array_cable[i,b,c,p+2,1] = filas_en_cajas[i,bc,f_bc-1,3] - sep_caja_tracker - largo_caja/2 - salida_zanja_LV_caja_inv
                                                                                 
                                                                                  p=p+2
                                                                                 
                                                                                  #Independientemente de la banda a la que se salte, al ir ya por debajo se sigue la función del cable de array, pero sin salir de la caja, sino tras haber enlazado con la más cercana
                                                                                  pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, bc, c, p, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)        
                                                                                 
                                                                                  #Faltaria ir desde el punto de espera de la banda separada o aislada hasta la anexa, sin necesidad de bajada porque ya estamos en la parte inferior
                                                                                  bajada_necesaria = False #hay que bajar por el extremo, hemos llegado al f_bc2 maximo
                                                                                  pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc2, f_bc2, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)      
                                                
                                                elif filas_en_bandas[i,b,0,0,2] - coord_PCS_DC_inputs[i,0] > 0: #la banda se queda a la derecha de la PCS 
                                                    circuitos_der_bc = np.count_nonzero(~np.isnan(cajas_fisicas[i,bc,cajas_fisicas[i,bc,:,1] > coord_PCS_DC_inputs[i,0],0]))
                                                    circuitos_en_banda[i,b] = np.count_nonzero(~np.isnan(cajas_fisicas[i,b,:,0]))
                    
                                                    if circuitos_en_banda[i,b]+circuitos_der_bc > n_circuitos_max_lado_PCS: #Si hay demasiados circuitos bordeamos por arriba la banda inferior hasta llegar a la altura de la PCS
                                                        for c in range(0,max_c):
                                                            if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía
                                                            
                                                                if bandas_anexas[i,bc]==True: #si la banda inferior es anexa a la PCS el punto de referencia para los cables es la PCS (aunque no lleguen en b, saltaran a bc y seguiran por ella)   
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                                else:
                                                                    #si la banda inferior no es anexa entonces no está garantizado que llegue más a la izquierda que el extremo de la superior (podría ser una separada más a la derecha o una intermedia más a la derecha)
                                                                    #para evitar retroceder luego potencialmente con las cajas de esa banda, nos quedamos como puerto con la x menos cercana a la PCS entre los extremos más cercanos de las dos bandas
                                                                    referencia_x_puerto = np.nanmax([np.nanmin(filas_en_cajas[i,b,:,2]),np.nanmin(filas_en_cajas[i,bc,:,2])]) #si fuese la superior se estaría llegando al extremo igualmente
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,referencia_x_puerto,0,sep_caja_tracker, orientacion, pitch)                                                              
                    
                                                                f_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(pol_array_cable[i,b,c,p,0]))) #vemos en que fila de la banda inferior caemos                                                                   
                                                                
                                                                while abs(pol_array_cable[i,b,c,p,0] - coord_PCS_DC_inputs[i,0]) > pitch and f_bc < np.count_nonzero(~np.isnan(filas_en_cajas[i,bc,:,0]))-1: #se recorre la banda por arriba mientras no se alcance la PCS ni se llegue al final de las filas de la banda
                                                                    pol_array_cable[i,b,c,p+1,0] = filas_en_cajas[i,bc,f_bc,2]
                                                                    pol_array_cable[i,b,c,p+1,1] = filas_en_bandas[i,bc,f_bc,0,3]+filas_en_bandas[i,bc,f_bc,0,1]+sep_zanja_tracker
                                                                    p=p+1
                                                                    f_bc=f_bc+1
                                                                
                                                                #SE HABIA SALTADO A UNA BANDA ANEXA 
                                                                if bandas_anexas[i,bc]==True: #si bc era anexa entonces hemos llegado a la vertical por definicion y tendriamos que meternos en el pasillo                                                                           
                                                                    
                                                                    pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable[i,b,c], circuitos_en_banda[i,b], n_circuitos_max_entre_trackers, pitch)
                    
                                                                #SE HABIA SALTADO A UNA BANDA SEPARADA O AISLADA   
                                                                elif bandas_separadas[i,bc]==True or bandas_aisladas[i,bc]==True: #si era separada o aislada no hemos llegado a la PCS pero sí al borde de la banda
                                                                    
                                                                    bajada_necesaria=True
                                                                    pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc, f_bc, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)                                                              
                                                                                                                                      
                                                                #SE HABIA SALTADO A UNA BANDA INTERMEDIA
                                                                else: #si no es niguna de las dos anteriores es porque se trata de una banda intermedia y tiene otra banda (anexa o separada) debajo
                                                                      for bc_anex_pot in range(bc,-1, -1): #identificamos cual es la banda anexa o separada
                                                                          if bandas_anexas[i,bc_anex_pot]==True or bandas_separadas[i,bc_anex_pot]==True: #POTENCIAL PROBLEMA QUE SE VAYA A OTRA POSTERIOR?
                                                                              bc2=bc_anex_pot
                                                                             
                                                                      #buscamos la fila correspondiente dentro de dicha banda
                                                                      p=p+1
                                                                      f_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(pol_array_cable[i,b,c,p,0])))
                                                                     
                                                                      #recorremos la banda por encima, si antes no hemos entrado por abajo ahora con menos motivo, al llevar sumados los de la anterior
                                                                      while abs(pol_array_cable[i,b,c,p,0] - coord_PCS_DC_inputs[i,0]) > pitch and f_bc2 < np.count_nonzero(~np.isnan(filas_en_cajas[i,bc,:,0]))-1: #se recorre la banda por arriba mientras no se alcance la PCS ni se llegue al final de las filas de la banda
                                                                          pol_array_cable[i,b,c,p+1,0] = filas_en_cajas[i,bc,f_bc2,2]
                                                                          pol_array_cable[i,b,c,p+1,1] = filas_en_bandas[i,bc,f_bc2,0,3]+filas_en_bandas[i,bc,f_bc2,0,1]+sep_zanja_tracker
                                                                          p=p+1
                                                                          f_bc2=f_bc2+1
                                                                         
                                                                    #SI LA BANDA DE ABAJO ES ANEXA - Se ha salido del while llegando a la altura de la PCS
                                                                      if bandas_anexas[i,bc2]==True: #si bc era anexa entonces hemos llegado a la vertical por definicion y tendriamos que meternos en el pasillo         
                                                                        
                                                                        #cuidado al comprobar si el numero de circuitos permite que haya una sola zanja o hay que ir por dos pasillos, pues ahora van dos bandas
                                                                        pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable[i,b,c], circuitos_en_banda[i,b]+circuitos_en_banda[i,bc], n_circuitos_max_entre_trackers, pitch)
                                                                        #TODO falta coordinar las bajadas en dos pasillo con los cables de las distintas bandas
                                                                                                                                                           
                                                                      #SI LA BANDA DE ABAJO ES SEPARADA O AISLADA - Se ha salido del while llegando a la ultima fila de la banda (se podria poner un else porque no hay mas saltos a intermedias contemplados)
                                                                      elif bandas_separadas[i,bc2]==True or bandas_aisladas[i,bc2]==True: #si era separada o aislada no hemos llegado a la PCS pero sí al borde de la banda
                                                                         
                                                                          bajada_necesaria = True
                                                                          pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc2, f_bc2, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)
                                                                                                                           
                                                    elif circuitos_en_banda[i,b]+circuitos_der_bc <= n_circuitos_max_lado_PCS: #Si no hay demasiados circuitos podemos subir directamente a la superior
                                                          for c in range(0,max_c):
                                                              if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                                                             
                                                              #TODO, faltaria por ver si se pueden meter en un pasillo o tienen que ser en 2
                                                                  if bandas_anexas[i,bc]==True:   
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                                  else:                                                               
                                                                    referencia_x_puerto = np.nanmax([np.nanmin(filas_en_cajas[i,b,:,2]),np.nanmin(filas_en_cajas[i,bc,:,2])]) #si fuese la superior se estaría llegando al extremo igualmente
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,referencia_x_puerto,0,sep_caja_tracker, orientacion, pitch)                                                              
                    
                                                                  f_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(pol_array_cable[i,b,c,p,0])))
                                                                 
                                                                  pol_array_cable[i,b,c,p+1,0] = pol_array_cable[i,b,c,p,0]-pitch/2
                                                                  pol_array_cable[i,b,c,p+1,1] = pol_array_cable[i,b,c,p,1]
                                                                 
                                                                  pol_array_cable[i,b,c,p+2,0] = pol_array_cable[i,b,c,p+1,0]
                                                                  pol_array_cable[i,b,c,p+2,1] = filas_en_cajas[i,bc,f_bc,3] - sep_caja_tracker - largo_caja/2 - salida_zanja_LV_caja_inv
                                                                 
                                                                  p=p+2
                                                                 
                                                                  #Independientemente de la banda a la que se salte, al ir ya por debajo se sigue la función del cable de array, pero sin tener que salir desde la caja, ya en la zona de zanja                                                           
                                                                  if f_bc!= np.count_nonzero(~np.isnan(filas_en_cajas[i,bc,:,0]))-1: #hay una excepción, si estamos en el borde ya no entramos en la funcion de la polilinea porque sino volveriamos hacia atras
                                                                      pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, bc, c, p, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                                 
                                                                  #Ahora vuelve a abrirse el arbol, si las banda a la que se saltó era anexa o separada ya hemos llevado los cables a los puntos de espera en la PCS (PENDIENTE OPTIMIZAR, falta rematarlos)
                                                                  if bandas_anexas[i,bc]==True:
                                                                      pol_array_cable[i,b,c,p,0] = coord_PCS_DC_inputs[i,0]
                                                                      pol_array_cable[i,b,c,p,1] = coord_PCS_DC_inputs[i,1]
                                                                     
                                                                  elif bandas_separadas[i,bc]==True or bandas_aisladas[i,bc]==True: #si partimos del punto de espera de la separada, podemos intentar saltar horizontalmente hasta la banda anexa
                                                                     
                                                                      bajada_necesaria = False #ya estamos en la parte inferior de la banda separada o aislada
                                                                      pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc, f_bc, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)
                                                                            
                                                                  else: #si por el contrario hemos saltado a una intermedia (y estamos en su parte alta) tenemos que dar otro grado de profundidad y bajar a la de abajo
                                                                  #identificamos la banda de arriba
                                                                      for bc2_pot in range(bc,-1,-1): 
                                                                          if bandas_anexas[i,bc2_pot]==True:
                                                                              bc2=bc2_pot
                                                                          elif bandas_separadas[i,bc2_pot]==True:
                                                                              bc2=bc2_pot
                                                                          elif bandas_aisladas[i,bc2_pot]==True: #Estos tres ifs evitan que se coja otra intermedia en el bucle de busqueda
                                                                              bc2=bc2_pot                                                                      
                                                         
                                                                          #LA BANDA DE ABAJO ERA ANEXA - hemos alcanzado la PCS
                                                                          if bandas_anexas[i,bc]==True: #si bc era anexa entonces hemos llegado a la vertical por definicion y tendriamos que meternos en el pasillo                                                                           
                                                                             
                                                                              #cuidado al comprobar si el numero de circuitos permite que haya una sola zanja o hay que ir por dos pasillos, pues ahora van dos bandas
                                                                              pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_contorno_superior_de_banda_anexa(i, c, p, coord_PCS_DC_inputs, pol_array_cable[i,b,c], circuitos_en_banda[i,b]+circuitos_en_banda[i,bc], n_circuitos_max_entre_trackers, pitch)
                                                                              #TODO falta coordinar las bajadas en dos pasillo con los cables de las distintas bandas
                                                                                 
                                                                          #LA BANDA DE ABAJO ERA SEPARADA O AISLADA - no se alcanzó la PCS al recorrer la parte inferior de la banda intermedia, pero se alcanzó la parte más a la derecha de ella
                                                                          else: 
                                                                              #Hay que llevar los circuitos hasta la parte más a la derecha de la banda de abajo (estamos en el extremo de la intermedia), para ello hay que ver si podemos bajar los circuitos para ir por debajo de la banda o hace falta recorrerla por encima
                                                                              circuitos_der_bc2 = np.count_nonzero(~np.isnan(cajas_fisicas[i,bc,cajas_fisicas[i,bc2,:,1] > coord_PCS_DC_inputs[i,0],0]))
                                                                             
                                                                              if circuitos_en_banda[i,b] + circuitos_en_banda[i,bc] + circuitos_der_bc2 > n_circuitos_max_lado_PCS: #si llevasemos demasiados circuitos por el pasillo del camino
                                                                                 
                                                                                  #buscamos la fila actualizada y seguimos recorriendo la banda por arriba hasta llegar a su limite
                                                                                  f_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(pol_array_cable[i,b,c,p,0]+pitch/2)))
                                                                                 
                                                                                  while f_bc2 < np.count_nonzero(~np.isnan(filas_en_cajas[i,bc,:,0]))-1: #se recorre la banda por arriba mientras no se llegue al final de las filas de la banda
                                                                                      pol_array_cable[i,b,c,p+1,0] = filas_en_cajas[i,bc,f_bc,2]
                                                                                      pol_array_cable[i,b,c,p+1,1] = filas_en_bandas[i,bc,f_bc,0,3]+filas_en_bandas[i,bc,f_bc,0,1]+sep_zanja_tracker
                                                                                      p=p+1
                                                                                      f_bc2=f_bc2+1
                                                                                     
                                                                                  bajada_necesaria = True #hay que bajar por el extremo, hemos llegado al f_bc2 maximo
                                                                                  pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc2, f_bc2, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)
                                                                                                                                            
                                                                              elif circuitos_en_banda[i,b] + circuitos_en_banda[i,bc] + circuitos_der_bc2 <= n_circuitos_max_lado_PCS: #si los circuitos pueden ir por abajo, los bajamos para ahorrar zanja, repitiendo lo que se hizo desde la banda extrema a la intermedia       
                                                                                  #TODO, faltaria por ver si se pueden meter en un pasillo o tienen que ser en 2
                                                         
                                                                                  f_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(pol_array_cable[i,b,c,p,0])))
                                                                                 
                                                                                  pol_array_cable[i,b,c,p+1,0] = pol_array_cable[i,b,c,p,0]-pitch/2
                                                                                  pol_array_cable[i,b,c,p+1,1] = pol_array_cable[i,b,c,p,1]
                                                                                 
                                                                                  pol_array_cable[i,b,c,p+2,0] = pol_array_cable[i,b,c,p+1,0]
                                                                                  pol_array_cable[i,b,c,p+2,1] = filas_en_cajas[i,bc,f_bc,3] - sep_caja_tracker - largo_caja/2 - salida_zanja_LV_caja_inv
                                                                                 
                                                                                  p=p+2
                                                                                 
                                                                                  #Independientemente de la banda a la que se salte, al ir ya por debajo se sigue la función del cable de array, pero sin salir de la caja, sino tras haber enlazado con la más cercana
                                                                                  pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, bc, c, p, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)        
                                                                                 
                                                                                  #Faltaria ir desde el punto de espera de la banda separada o aislada hasta la anexa, sin necesidad de bajada porque ya estamos en la parte inferior
                                                                                  bajada_necesaria = False #hay que bajar por el extremo, hemos llegado al f_bc2 maximo
                                                                                  pol_array_cable[i,b,c] = polilinea_cable_de_array_finalizacion_desde_banda_separada_o_aislada(i, b, c, hay_anexa, bajada_necesaria, bc2, f_bc2, pol_array_cable[i,b,c], p, orientacion[i,b], filas_en_cajas, coord_PCS_DC_inputs[i,0], pitch, bandas_anexas, bandas_aisladas, -sep_caja_tracker - largo_caja/2 -salida_zanja_LV_caja_inv, sep_caja_tracker, largo_caja, salida_zanja_LV_caja_inv, max_b, max_c, max_f_str_b, coord_PCS_DC_inputs, orientacion, cajas_fisicas)      
                    
                                                                                                                                
                                            else: #sí que está situada directamente encima de la PCS
                                                  circuitos_en_banda[i,b] = np.count_nonzero(~np.isnan(cajas_fisicas[i,b,:,0])) #POSIBLE OPTIMIZAR, SE PUEDEN METER AQUI LOS CIRCUITOS DE OTRAS BANDAS Y RELLENAR ZANJAS
                                                  
                                                  if circuitos_en_banda[i,b] <= n_circuitos_max_entre_trackers: #si los circuitos caben en una sola zanja, hay un solo puerto, buscamos el punto más próximo a la vertical de la PCS y los bajamos desde ahí
                                                      
                                                      indice_fila_puerto=np.nanargmin(np.abs(filas_en_cajas[i,b,:,2]-coord_PCS_DC_inputs[i,0]))
                                                      puerto_x=filas_en_cajas[i,b,indice_fila_puerto,2]+pitch/2 #la X del puerto cae en la mitad del pasillo entre filas
                                                      if filas_en_cajas[i,b,indice_fila_puerto,3] <= filas_en_cajas[i,b,indice_fila_puerto-1,3]: #la Y del puerto tiene que ser la del lado que está más al sur, mas cerca de la PCS 
                                                          puerto_y=filas_en_cajas[i,b,indice_fila_puerto,3] + sep_caja_tracker + largo_caja/2 + salida_zanja_LV_caja_inv 
                                                      else:
                                                          puerto_y=filas_en_cajas[i,b,indice_fila_puerto+1,3] + sep_caja_tracker + largo_caja/2 + salida_zanja_LV_caja_inv
                                                          
                                                      for c in range(0,max_c):
                                                          if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                                                              pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,coord_PCS_DC_inputs[i,0],pitch,sep_caja_tracker, orientacion, pitch)
                                                              pol_array_cable[i,b,c,p+1,0] = puerto_x
                                                              pol_array_cable[i,b,c,p+1,1] = puerto_y
                                                              #desde el puerto se baja hasta la altura inferior de la otra banda para dar ese punto de cara a la definición de la zanja, para ello se calcula cual es la fila de esa banda anexa en cuyo pasillo se está bajando
                                                              indice_fila_puerto_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(puerto_x-pitch/2)))
                                                              pol_array_cable[i,b,c,p+2,0] = puerto_x
                                                              pol_array_cable[i,b,c,p+2,1] = (filas_en_cajas[i,bc,indice_fila_puerto_bc,3]+filas_en_cajas[i,bc,indice_fila_puerto_bc-1,3])/2 #PROVISIONALMENTE LE DAMOS LA ALTURA MEDIA DE LAS DOS FILAS QUE FORMAN EL PASILLO
                                                            #llevamos dos bandas de profundidad, si estamos ya en la banda anexa al inversor la zanja va a la PCS, si no lo estamos, sigue bajando
                                                              if bandas_anexas[i,bc]==True:
                                                                  pol_array_cable[i,b,c,p+3,0] = coord_PCS_DC_inputs[i,0]
                                                                  pol_array_cable[i,b,c,p+3,1] = coord_PCS_DC_inputs[i,1]
                                                              elif bandas_separadas[i,bc]==True: #si estabamos en otro bloque de bandas y hemos llegado a una separada, PROVISIONALMENTE LA LLEVAMOS DIRECTOS A LA PCS (POSIBLE OPTIMIZAR SIGUIENDO EL CAMINO)
                                                                  pol_array_cable[i,b,c,p+3,0] = coord_PCS_DC_inputs[i,0]
                                                                  pol_array_cable[i,b,c,p+3,1] = coord_PCS_DC_inputs[i,1]
                                                              else: #en este caso bc era una banda intermedia, las polilineas de b tienen que seguir bajando hasta la anexa, que hay que identificar
                                                                  
                                                                  for bc_anex_pot in range(bc,-1,-1): #identificamos cual es la banda anexa
                                                                      if bandas_anexas[i,bc_anex_pot]==True:
                                                                          bc2=bc_anex_pot
                                                                          
                                                                  indice_fila_puerto_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(puerto_x-pitch/2)))
                                                                  pol_array_cable[i,b,c,p+3,0] = puerto_x
                                                                  pol_array_cable[i,b,c,p+3,1] = (filas_en_cajas[i,bc,indice_fila_puerto_bc2,3]+filas_en_cajas[i,bc,indice_fila_puerto_bc2-1,3])/2 #PROVISIONALMENTE LE DAMOS LA ALTURA MEDIA DE LAS DOS FILAS QUE FORMAN EL PASILLO
                                                                  
                                                                  pol_array_cable[i,b,c,p+4,0] = coord_PCS_DC_inputs[i,0]
                                                                  pol_array_cable[i,b,c,p+4,1] = coord_PCS_DC_inputs[i,1]
                    
                                                                  
                                                  else:  #si no podemos tirar todo en una sola zanja, se definen dos "puertos" de paso
                                                        indice_fila_puerto_1=np.nanargmin(np.abs(filas_en_cajas[i,b,:,2]-(coord_PCS_DC_inputs[i,0]-pitch))) #entra en - pitch en lugar de -2 pitch para tener margen
                                                        puerto_1_x=filas_en_cajas[i,b,indice_fila_puerto_1,2]+pitch/2 
                                                        if filas_en_cajas[i,b,indice_fila_puerto_1,3] <= filas_en_cajas[i,b,indice_fila_puerto_1-1,3]: 
                                                            puerto_1_y=filas_en_cajas[i,b,indice_fila_puerto_1,3] + sep_caja_tracker + largo_caja + salida_zanja_LV_caja_inv 
                                                        else:
                                                            puerto_1_y=filas_en_cajas[i,b,indice_fila_puerto_1-1,3] - sep_caja_tracker - largo_caja - salida_zanja_LV_caja_inv
                                                       
                                                        indice_fila_puerto_2=np.nanargmin(np.abs(filas_en_cajas[i,b,:,2]-(coord_PCS_DC_inputs[i,0]+pitch)))
                                                        puerto_2_x=filas_en_cajas[i,b,indice_fila_puerto_2,2]-pitch/2
                                                        if filas_en_cajas[i,b,indice_fila_puerto_2,3] <= filas_en_cajas[i,b,indice_fila_puerto_2+1,3]:
                                                            puerto_2_y=filas_en_cajas[i,b,indice_fila_puerto_2,3] + sep_caja_tracker + largo_caja + salida_zanja_LV_caja_inv 
                                                        else:
                                                            puerto_2_y=filas_en_cajas[i,b,indice_fila_puerto_2+1,3] + sep_caja_tracker + largo_caja + salida_zanja_LV_caja_inv
                                                       
                                                        for c in range(0,max_c):
                                                            if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                                                                if c < circuitos_en_banda[i,b]/2 : #está limitado a 2 puertos, POSIBLE OPTIMIZAR, AHORA ESTA HECHO PARA LLEVAR  MITAD Y MITAD PERO PUEDE HACERSE DESIGUAL Y EVITAR CRUCES
                                                                    pol_array_cable[i,b,c], p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,puerto_1_x,pitch,sep_caja_tracker, orientacion, pitch) 
                                                                    pol_array_cable[i,b,c,p+1,0] = puerto_1_x #hasta la mitad del max las llevamos a un puerto a la izquierda de la PCS, 
                                                                    pol_array_cable[i,b,c,p+1,1] = puerto_1_y
                                                                    #desde el puerto se baja hasta la altura inferior de la otra banda, para ello se calcula cual es la fila de esa banda anexa en cuyo pasillo se está bajando (POSIBLE OPTIMIZAR IDENTIFICANDO EN QUE FILA CAEN DE ELLA POR SI HAY UN DESFASE DE PASILLOS)
                                                                    indice_fila_puerto_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(puerto_1_x-pitch/2)))
                                                                    pol_array_cable[i,b,c,p+2,0] = puerto_1_x
                                                                    pol_array_cable[i,b,c,p+2,1] = (filas_en_cajas[i,bc,indice_fila_puerto_bc,3]+filas_en_cajas[i,bc,indice_fila_puerto_bc-1,3])/2 #PROVISIONALMENTE
                                                                #llevamos dos bandas de profundidad, si estamos ya en la banda anexa al inversor la zanja va a la PCS, si no lo estamos, sigue bajando
                                                                    if bandas_anexas[i,bc]==True:
                                                                        pol_array_cable[i,b,c,p+3,0] = coord_PCS_DC_inputs[i,0]
                                                                        pol_array_cable[i,b,c,p+3,1] = coord_PCS_DC_inputs[i,1]
                                                                    elif bandas_separadas[i,bc]==True: #si estabamos en otro bloque de bandas y hemos llegado a una separada, PROVISIONALMENTE LA LLEVAMOS DIRECTOS A LA PCS (POSIBLE OPTIMIZAR SIGUIENDO EL CAMINO)
                                                                        pol_array_cable[i,b,c,p+3,0] = coord_PCS_DC_inputs[i,0]
                                                                        pol_array_cable[i,b,c,p+3,1] = coord_PCS_DC_inputs[i,1]
                                                                    else: #en este caso bc era una banda intermedia, las polilineas de b tienen que seguir bajando hasta la anexa, que hay que identificar
                                                                       
                                                                        for bc_anex_pot in range(bc,-1,-1): #identificamos cual es la banda anexa
                                                                            if bandas_anexas[i,bc_anex_pot]==True:
                                                                                bc2=bc_anex_pot
                                                                               
                                                                        indice_fila_puerto_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(puerto_x-pitch/2)))
                                                                        pol_array_cable[i,b,c,p+3,0] = puerto_1_x
                                                                        pol_array_cable[i,b,c,p+3,1] = (filas_en_cajas[i,bc,indice_fila_puerto_bc2,3]+filas_en_cajas[i,bc,indice_fila_puerto_bc2-1,3])/2 #PROVISIONALMENTE LE DAMOS LA ALTURA MEDIA DE LAS DOS FILAS QUE FORMAN EL PASILLO
                                                                       
                                                                        pol_array_cable[i,b,c,p+4,0] = coord_PCS_DC_inputs[i,0]
                                                                        pol_array_cable[i,b,c,p+4,1] = coord_PCS_DC_inputs[i,1]
                                                                else:
                                                                    pol_array_cable[i,b,c] , p = polilinea_array_hasta_punto_de_espera_o_puerto(i, b, c, 0, max_f_str_b, max_c, pol_array_cable[i,b,c],cajas_fisicas,largo_caja,salida_zanja_LV_caja_inv,filas_en_cajas,puerto_2_x,pitch,sep_caja_tracker, orientacion, pitch) 
                                                                    pol_array_cable[i,b,c,p+1,0] = puerto_2_x  #mas alla de la mitad del max las llevamos a un puerto a la izquierda de la PCS
                                                                    pol_array_cable[i,b,c,p+1,1] = puerto_2_y 
                                                                    #desde el puerto se asume provisionalmente que van directos hasta la zona de aproximacion a la PCS atravesando cualquier banda intermedia (POSIBLE OPTIMIZAR IDENTIFICANDO EN QUE FILA CAEN DE ELLA POR SI HAY UN DESFASE DE PASILLOS)
                                                                    indice_fila_puerto_bc=np.nanargmin(np.abs(filas_en_cajas[i,bc,:,2]-(puerto_2_x-pitch/2)))
                                                                    pol_array_cable[i,b,c,p+2,0] = puerto_2_x
                                                                    pol_array_cable[i,b,c,p+2,1] = (filas_en_cajas[i,bc,indice_fila_puerto_bc,3]+filas_en_cajas[i,bc,indice_fila_puerto_bc-1,3])/2 #PROVISIONALMENTE
                                                                #llevamos dos bandas de profundidad, si estamos ya en la banda anexa al inversor la zanja va a la PCS, si no lo estamos, sigue bajando
                                                                    if bandas_anexas[i,bc]==True:
                                                                        pol_array_cable[i,b,c,p+3,0] = coord_PCS_DC_inputs[i,0]
                                                                        pol_array_cable[i,b,c,p+3,1] = coord_PCS_DC_inputs[i,1]
                                                                    elif bandas_separadas[i,bc]==True: #si estabamos en otro bloque de bandas y hemos llegado a una separada, PROVISIONALMENTE LA LLEVAMOS DIRECTOS A LA PCS (POSIBLE OPTIMIZAR SIGUIENDO EL CAMINO)
                                                                        pol_array_cable[i,b,c,p+3,0] = coord_PCS_DC_inputs[i,0]
                                                                        pol_array_cable[i,b,c,p+3,1] = coord_PCS_DC_inputs[i,1]
                                                                    else: #en este caso bc era una banda intermedia, las polilineas de b tienen que seguir bajando hasta la anexa, que hay que identificar
                                                                       
                                                                        for bc_anex_pot in range(bc,-1,-1): #identificamos cual es la banda anexa
                                                                            if bandas_anexas[i,bc_anex_pot]==True:
                                                                                bc2=bc_anex_pot
                                                                               
                                                                        indice_fila_puerto_bc2=np.nanargmin(np.abs(filas_en_cajas[i,bc2,:,2]-(puerto_x-pitch/2)))
                                                                        pol_array_cable[i,b,c,p+3,0] = puerto_2_x
                                                                        pol_array_cable[i,b,c,p+3,1] = (filas_en_cajas[i,bc,indice_fila_puerto_bc2,3]+filas_en_cajas[i,bc,indice_fila_puerto_bc2-1,3])/2 #PROVISIONALMENTE LE DAMOS LA ALTURA MEDIA DE LAS DOS FILAS QUE FORMAN EL PASILLO
                                                                       
                                                                        pol_array_cable[i,b,c,p+4,0] = coord_PCS_DC_inputs[i,0]
                                                                        pol_array_cable[i,b,c,p+4,1] = coord_PCS_DC_inputs[i,1]
                    
                                            #anotamos que se ha analizado ya la banda b para no entrar en los bucles for de busqueda de posicion relativa previos                                                                                                                         
                                            banda_analizada=True                 
                                            break #rompemos el bucle for
                            if banda_analizada==True:
                                break #ponemos break para que la transferencia de b solo se haga una vez, hasta bc    
                                  
    
    return pol_array_cable            



    #MEDICIONES DE CABLE ARRAY
    #PENDIENTE OPTIMIZAR EN FUNCION DE SECCIONES
def medicion_array(bloque_inicial, n_bloques, DCBoxes_o_Inv_String, max_b, max_c, max_c_block, cajas_fisicas, pol_array_cable, equi_ibc, desnivel_cable_array_por_pendientes, transicion_array_cable_caja, transicion_array_cable_PCS, uni_o_multipolar, slack_array_cable, mayoracion_array_cable, lim_dist_array_sld_seccion, lim_n_str_array_seccion, criterio_seccion, secciones_array):
    
    #Inicializamos las variables en None para usar el mismo return con String Inverters
    med_inst_array_cable_pos = None
    med_inst_array_cable_neg = None
    med_array_cable_pos = None
    med_array_cable_neg = None
    med_array_cable = None
    med_inst_array_cable = None
    sch_array_cable_pos = None
    sch_array_cable_neg = None
    sch_array_cable = None


    tramo_subterraneo_array_cable=np.full((n_bloques+1,max_b,max_c,2),np.nan)
    
    if DCBoxes_o_Inv_String !='String Inverters':
        med_inst_array_cable_pos=np.full((n_bloques+1,3,max_c_block+1,2),np.nan)
        med_inst_array_cable_neg=np.copy(med_inst_array_cable_pos)
        med_array_cable_pos=np.copy(med_inst_array_cable_pos)
        med_array_cable_neg=np.copy(med_inst_array_cable_pos)
        sch_array_cable_pos=np.full((n_bloques+1,3,max_c_block+1,3),np.nan, dtype=object)
        sch_array_cable_neg=np.full((n_bloques+1,3,max_c_block+1,3),np.nan, dtype=object)
        
    elif DCBoxes_o_Inv_String == 'String Inverters':
        med_inst_array_cable = np.full((n_bloques+1,3,max_c_block+1,2),np.nan)
        med_array_cable = np.copy(med_inst_array_cable)
        sch_array_cable=np.full((n_bloques+1,3,max_c_block+1,3),np.nan, dtype=object)
        
    
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(cajas_fisicas[i,b,0,0]): #si la banda no está vacía       
                for c in range(0,max_c):      
                    if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la fila no está vacía      
                       #En inv de srting tenemos base 1, hay que sumarle a c esa unidad
                        if DCBoxes_o_Inv_String == 'String Inverters':
                            c_ibc = c+1
                        else:
                            c_ibc = c
                    #Calculamos el tramo subterráneo
                        restas_de_coordenadas = np.diff(pol_array_cable[i,b,c], axis=0)
                        distancias_subterraneas = np.linalg.norm(restas_de_coordenadas, axis=1)
                        tramo_subterraneo_array_cable[i,b,c,0]=np.nansum(distancias_subterraneas)*(1+slack_array_cable/100)*(1+desnivel_cable_array_por_pendientes/100)
                    #Calculamos el total

                        #Sacamos las equivalencias en nomenclatura GRS                        
                        inv = int(equi_ibc[i,b,c_ibc,1])
                        caja = int(equi_ibc[i,b,c_ibc,2])
                        
                        
                        if DCBoxes_o_Inv_String == 'DC Boxes':
                            med_inst_array_cable_pos[i,inv,caja,0]=transicion_array_cable_caja + tramo_subterraneo_array_cable[i,b,c,0] + transicion_array_cable_PCS
                            med_inst_array_cable_neg[i,inv,caja,0]=transicion_array_cable_caja + tramo_subterraneo_array_cable[i,b,c,0] + transicion_array_cable_PCS
                            
                            #ASIGNACION DE SECCIONES
                                #Criterio de distancia
                            if criterio_seccion == 'Distance':
                                if med_inst_array_cable_pos[i,inv,caja,0]+med_inst_array_cable_neg[i,inv,caja,0] <= lim_dist_array_sld_seccion * 2: #los dos polos
                                    med_inst_array_cable_pos[i,inv,caja,1]=secciones_array[0]
                                    med_inst_array_cable_neg[i,inv,caja,1]=secciones_array[0] 
                                        
                                else:
                                    med_inst_array_cable_pos[i,inv,caja,1]=secciones_array[1]
                                    med_inst_array_cable_neg[i,inv,caja,1]=secciones_array[1]
                        
                                #Criterio de numero de strings  
                            elif criterio_seccion == 'No. strings':
                                if cajas_fisicas[i,b,c,0] <= lim_n_str_array_seccion:
                                    med_inst_array_cable_pos[i,inv,caja,1]=secciones_array[0]
                                    med_inst_array_cable_neg[i,inv,caja,1]=secciones_array[0] 
                                        
                                else:
                                    med_inst_array_cable_pos[i,inv,caja,1]=secciones_array[1]
                                    med_inst_array_cable_neg[i,inv,caja,1]=secciones_array[1]
                                
                            #MEDICION DE CABLE MAYORADA
                            med_array_cable_pos[i,inv,caja,0] = med_inst_array_cable_pos[i,inv,caja,0] * (1+mayoracion_array_cable/100)
                            med_array_cable_neg[i,inv,caja,0] = med_inst_array_cable_neg[i,inv,caja,0] * (1+mayoracion_array_cable/100)
                            med_array_cable_pos[i,inv,caja,1] = med_inst_array_cable_pos[i,inv,caja,1]
                            med_array_cable_neg[i,inv,caja,1] = med_inst_array_cable_pos[i,inv,caja,1]
                            
                        elif DCBoxes_o_Inv_String == 'String Inverters':
                            med_inst_array_cable[i,inv,caja,0]=(transicion_array_cable_caja + tramo_subterraneo_array_cable[i,b,c,0] + transicion_array_cable_PCS)*uni_o_multipolar
                      
                            #ASIGNACION DE SECCIONES
                                #Criterio de distancia
                            if criterio_seccion == 'Distance':
                                if med_inst_array_cable[i,inv,caja,0] <= lim_dist_array_sld_seccion: 
                                    med_inst_array_cable[i,inv,caja,1]=secciones_array[0]
                                else:
                                    med_inst_array_cable[i,inv,caja,1]=secciones_array[1]

                                #Criterio de numero de strings  
                            elif criterio_seccion == 'No. strings':
                                if cajas_fisicas[i,b,c,0] <= lim_n_str_array_seccion:
                                    med_inst_array_cable[i,inv,caja,1]=secciones_array[0]     
                                else:
                                    med_inst_array_cable[i,inv,caja,1]=secciones_array[1]

                            #MEDICION DE CABLE MAYORADA
                            med_array_cable[i,inv,caja,0] = med_inst_array_cable[i,inv,caja,0] * (1+mayoracion_array_cable/100)
                            med_array_cable[i,inv,caja,1] = med_inst_array_cable[i,inv,caja,1]


                        
                        #Sacamos schedules de cables
                        #POSIBLE OPTIMIZAR QUITANDO INV SI SOLO HAY UN INVERSOR
                        if DCBoxes_o_Inv_String == 'DC Boxes':
                            sch_array_cable_pos[i,inv,caja,0]=f"Array-{i}.{inv}.{caja:02d}.+"
                            sch_array_cable_neg[i,inv,caja,0]=f"Array-{i}.{inv}.{caja:02d}.-"
                            
                            sch_array_cable_pos[i,inv,caja,1]=med_inst_array_cable_pos[i,inv,caja,1]
                            sch_array_cable_neg[i,inv,caja,1]=med_inst_array_cable_neg[i,inv,caja,1]
                            
                            sch_array_cable_pos[i,inv,caja,2]=med_inst_array_cable_pos[i,inv,caja,0]
                            sch_array_cable_neg[i,inv,caja,2]=med_inst_array_cable_neg[i,inv,caja,0]      
                            
                        elif DCBoxes_o_Inv_String == 'String Inverters':
                            sch_array_cable[i,inv,caja,0]=f"Array-{i}.{inv}.{caja:02d}.L1"
                            
                            sch_array_cable[i,inv,caja,1]=med_inst_array_cable[i,inv,caja,1]

                            sch_array_cable[i,inv,caja,2]=med_inst_array_cable[i,inv,caja,0]


    return med_inst_array_cable_pos, med_inst_array_cable_neg, med_array_cable_pos, med_array_cable_neg, med_array_cable, med_inst_array_cable, sch_array_cable_pos, sch_array_cable_neg, sch_array_cable
   
    
   
    
   
    
   
    
   
    
   
#-------------SERVICIOS AUXILIARES (LVAC Y ETHERNET)-----------------      
#Servicios AASS LVAC -> 0 = Combox, 1 = Tracknet, 2 = T-Box, 3 = AWS

def polilineas_AASS_LVAC_y_ethernet(bloque_inicial, n_bloques, coord_PCS_AASS_inputs, coord_Comboxes, coord_Tracknets, coord_TBoxes, coord_AWS, coord_CCTV, coord_OyM_LVAC, coord_SS_LVAC, coord_Warehouse_LVAC):
    max_p_AASS_LVAC = 20
    max_p_AASS_eth = 20
    pol_AASS_LVAC = np.full((n_bloques+1,4,max_p_AASS_LVAC,2),np.nan)
    pol_ethernet = np.full((n_bloques+1,4,max_p_AASS_eth,2),np.nan)
    pol_CCTV_LVAC = []
    pol_OyM_supply_LVAC = []
    pol_Warehouse_supply_LVAC = []
    
    for i in range(bloque_inicial,n_bloques+1):       
        if ~np.isnan(coord_Comboxes[i,0]):
            pol_AASS_LVAC[i,0,0] = [coord_PCS_AASS_inputs[i,0], coord_PCS_AASS_inputs[i,1]] #Primer punto en el cabinet de SSAA de la PCS
            pol_AASS_LVAC[i,0,1] = [coord_PCS_AASS_inputs[i,0], coord_PCS_AASS_inputs[i,1]-2] #TODO Segundo punto saliendo 2 m hacia el S, optimizar con entradas de la GUI
            pol_AASS_LVAC[i,0,2] = [coord_Comboxes[i,0], coord_Comboxes[i,1]-1] #Tercer punto 1 m hacia el S del elemento
            pol_AASS_LVAC[i,0,3] = [coord_Comboxes[i,0], coord_Comboxes[i,1]] #Cuarto punto en el elemento
            
            pol_ethernet[i,0,0] = [coord_Comboxes[i,0], coord_Comboxes[i,1]]
            pol_ethernet[i,0,1] = [coord_Comboxes[i,0], coord_Comboxes[i,1]-1]
            pol_ethernet[i,0,2] = [coord_PCS_AASS_inputs[i,0], coord_PCS_AASS_inputs[i,1]-2]  
            pol_ethernet[i,0,3] = [coord_PCS_AASS_inputs[i,0], coord_PCS_AASS_inputs[i,1]]
            
        if ~np.isnan(coord_Tracknets[i,0]):
            pol_AASS_LVAC[i,1,0] = [coord_PCS_AASS_inputs[i,0], coord_PCS_AASS_inputs[i,1]] 
            pol_AASS_LVAC[i,1,1] = [coord_PCS_AASS_inputs[i,0], coord_PCS_AASS_inputs[i,1]-2] 
            pol_AASS_LVAC[i,1,2] = [coord_Tracknets[i,0], coord_Tracknets[i,1]-1] 
            pol_AASS_LVAC[i,1,3] = [coord_Tracknets[i,0], coord_Tracknets[i,1]] 
            
            pol_ethernet[i,1,0] = [coord_Comboxes[i,0], coord_Comboxes[i,1]]
            pol_ethernet[i,1,1] = [coord_Comboxes[i,0], coord_Comboxes[i,1]-1]
            pol_ethernet[i,1,2] = [coord_Tracknets[i,0], coord_Tracknets[i,1]-1]  
            pol_ethernet[i,1,3] = [coord_Tracknets[i,0], coord_Tracknets[i,1]] 
                        
        if ~np.isnan(coord_TBoxes[i,0]):
            pol_AASS_LVAC[i,2,0] = [coord_PCS_AASS_inputs[i,0], coord_PCS_AASS_inputs[i,1]] 
            pol_AASS_LVAC[i,2,1] = [coord_PCS_AASS_inputs[i,0], coord_PCS_AASS_inputs[i,1]-2] 
            pol_AASS_LVAC[i,2,2] = [coord_TBoxes[i,0], coord_TBoxes[i,1]-1] 
            pol_AASS_LVAC[i,2,3] = [coord_TBoxes[i,0], coord_TBoxes[i,1]] 
            
            pol_ethernet[i,2,0] = [coord_Comboxes[i,0], coord_Comboxes[i,1]]
            pol_ethernet[i,2,1] = [coord_Comboxes[i,0], coord_Comboxes[i,1]-1]
            pol_ethernet[i,2,2] = [coord_TBoxes[i,0], coord_TBoxes[i,1]-1]  
            pol_ethernet[i,2,3] = [coord_TBoxes[i,0], coord_TBoxes[i,1]] 
                
        if ~np.isnan(coord_AWS[i,0]):
            pol_AASS_LVAC[i,3,0] = [coord_PCS_AASS_inputs[i,0], coord_PCS_AASS_inputs[i,1]] 
            pol_AASS_LVAC[i,3,1] = [coord_PCS_AASS_inputs[i,0], coord_PCS_AASS_inputs[i,1]-2] 
            pol_AASS_LVAC[i,3,2] = [coord_AWS[i,0], coord_AWS[i,1]-1] 
            pol_AASS_LVAC[i,3,3] = [coord_AWS[i,0], coord_AWS[i,1]] 

            pol_ethernet[i,3,0] = [coord_Comboxes[i,0], coord_Comboxes[i,1]]
            pol_ethernet[i,3,1] = [coord_Comboxes[i,0], coord_Comboxes[i,1]-1]
            pol_ethernet[i,3,2] = [coord_AWS[i,0], coord_AWS[i,1]-1]   
            pol_ethernet[i,3,3] = [coord_AWS[i,0], coord_AWS[i,1]]   
    
    
    #Sacamos las polilineas para el CCTV como una lista pares [ [x0,y0],[x1,y1]...]
    if coord_CCTV:    
        for CCTV in coord_CCTV:
            if CCTV[0]=='O&M':
                pol_CCTV_LVAC.append([[coord_OyM_LVAC[0],coord_OyM_LVAC[1]], [CCTV[1],CCTV[2]]])
                
            elif CCTV[0]=='SS':
                pol_CCTV_LVAC.append([[coord_SS_LVAC[0],coord_SS_LVAC[1]], [CCTV[1],CCTV[2]]])
                 
            else:    
                i = int(CCTV[0])
                pol_CCTV_LVAC.append([[coord_PCS_AASS_inputs[i,0],coord_PCS_AASS_inputs[i,1]], [CCTV[1],CCTV[2]]])
    
    
    #Sacamos las polilineas para la alimentacion de edificios tambien como una lista de pares 
    if coord_SS_LVAC != None and coord_OyM_LVAC != None:
        pol_OyM_supply_LVAC.append([[coord_SS_LVAC[0],coord_SS_LVAC[1]], [coord_OyM_LVAC[0],coord_OyM_LVAC[1]]])

    
    if coord_OyM_LVAC != None and coord_Warehouse_LVAC != None:
        pol_Warehouse_supply_LVAC.append([[coord_OyM_LVAC[0],coord_OyM_LVAC[1]], [coord_Warehouse_LVAC[0],coord_Warehouse_LVAC[1]]])
    
    
    
    return pol_AASS_LVAC, pol_ethernet, max_p_AASS_LVAC, max_p_AASS_eth, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC
    
  

















#------------------------------------------FUNCIONES DE CALCULO------------------------------------------------------



def calculo_perdidas_circuito_individual(n_cables, longitud, seccion, material, intensidad, temp_cable):
    res_Al_20deg = 0.0282 #Ohm-mm2/m equivale a una conductividad de 35.46 m/Ohm-mm2
    res_Cu_20deg = 0.0172 #Ohm-mm2/m, equivale a una conductividad de 58.14 m/Ohm-mm2
    
    alpha_Al = 0.00403 #factor de cambio de resistividad con temperatura
    alpha_Cu = 0.00393 #factor de cambio de resistividad con temperatura
    
    if material == 'Al':
        rho_corr = 1 / (res_Al_20deg *(1+alpha_Al*(temp_cable-20)))
    elif material == 'Cu':
        rho_corr = 1 / (res_Cu_20deg *(1+alpha_Cu*(temp_cable-20)))
    
    #Las perdidas de potencia en el cable de string son perdidas por efecto Joule, definidas desarrollando la ley de Ohm : P = n * R*I^2
    #La resistencia se calcula a partir de la conductividad, la seccion y la longiutd: R = long / (secc * conduct)
    
    R =  longitud / (seccion*rho_corr) #la seccion en mm2 y la longitud en m
    P = n_cables * R * intensidad**2
    
    return P


def calculo_perdidas_cables_string(strings_fisicos,bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, perdidas_cables_string, equi_ibfs, med_pos, med_neg, pot_string_STC, filas_con_cable_string, int_string, temp_cable, DCBoxes_o_Inv_String, strings_ID):
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(strings_fisicos[i,b,0,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b+1):      
                    if ~np.isnan(strings_fisicos[i,b,f,0,0]) and filas_con_cable_string[i,b,f]==True: #si la fila no está vacía ni tiene cables de string
                        for s in range(0,max_spf+1): 
                            if ~np.isnan(strings_fisicos[i,b,f,s,0]):   
                                #Sacamos las equivalencias en nomenclatura GRS
                                if DCBoxes_o_Inv_String == 'DC Boxes':                        
                                    inv = int(equi_ibfs[i,b,f,s,1])
                                    caja = int(equi_ibfs[i,b,f,s,2])
                                    stri = int(equi_ibfs[i,b,f,s,4])
                                else:
                                    matches = np.argwhere(strings_ID[...,4] == strings_fisicos[i,b,f,s,2])[0]                                    
                                    i, inv, caja, stri = matches


                                perdidas_pos = calculo_perdidas_circuito_individual(1, med_pos[i,inv,caja,0,stri,0], med_pos[i,inv,caja,0,stri,1], 'Cu', int_string, temp_cable)
                                perdidas_neg = calculo_perdidas_circuito_individual(1, med_neg[i,inv,caja,0,stri,0], med_neg[i,inv,caja,0,stri,1], 'Cu', int_string, temp_cable)                                

                                perdidas_cables_string[i,inv,caja,0,stri,0] = perdidas_pos + perdidas_neg
                                perdidas_cables_string[i,inv,caja,0,stri,1] = (perdidas_pos + perdidas_neg) / pot_string_STC[i]*100
                                
    return perdidas_cables_string

                           
def calculo_perdidas_DC_Bus(bloque_inicial,n_bloques, max_b, max_f_str_b, max_spf, perdidas_DC_Bus, equi_ibfs, pot_string_STC, filas_con_cable_string, harness_pos, harness_neg, coord_harness_pos, coord_harness_neg, long_string, int_string, temp_cable, med_inst_DC_Bus_pos, tramo_aereo_DC_Bus_pos, strings_fisicos, slack_DC_Bus, desnivel_cable_por_pendientes_tramo_aereo):
    #A diferencia del caso con el cable individual, en el caso del bus hay que tener en cuenta que se tienen intensidades diferentes en cada seccion en la que se van agregando cables con los harness+IPC
    #La referencia son los harness, vamos midiendo con ellos hasta el final del tramo aéreo del DCBus, donde ya se usa la polilinea normal
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(strings_fisicos[i,b,0,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b+1):      
                    if ~np.isnan(strings_fisicos[i,b,f,0,0]) and filas_con_cable_string[i,b,f]==False: #si la fila no está vacía ni tiene cables de string
                        #Sacamos las equivalencias en nomenclatura GRS
                        inv = int(equi_ibfs[i,b,f,0,1])
                        caja = int(equi_ibfs[i,b,f,0,2])
                        bus = int(equi_ibfs[i,b,f,0,3])
                        
                        seccion_DCBus = med_inst_DC_Bus_pos[i,inv,caja,bus,1]
                        perd_bus=0
                        s_acum_pos=0
                        s_acum_neg=0
                        for s in range(0,max_spf+1):
                            if harness_pos[i,b,f,s,1] > 0 or harness_neg[i,b,f,s,1] > 0: #si la posicion del harness en el bus no está vacía
                                perd_harness_pos_basicas = 0
                                perd_harness_pos_string_extensions = 0
                                perd_harness_neg_basicas = 0
                                perd_harness_neg_string_extensions = 0
                                perdidas_tramo_pos=0
                                perdidas_tramo_neg=0
                                
                                if harness_pos[i,b,f,s,1] > 0: #si la posicion del harness positivo no está vacía
                                    perd_harness_pos_basicas = calculo_perdidas_circuito_individual(harness_pos[i,b,f,s,1], 1, 6, 'Cu', int_string, temp_cable) #1m de base para la conexion del harness
                                    for se in range(2,6):
                                        if harness_pos[i,b,f,s,se] > 0: #si hay algun string extension
                                            perd_harness_pos_string_extensions = perd_harness_pos_string_extensions + calculo_perdidas_circuito_individual(harness_pos[i,b,f,s,se], (se-1)*long_string, 6, 'Cu', int_string, temp_cable) #se-1 porque el indice 2 es el que tiene el string extension corto, de 1str, los siguientes son correlativos
                                
                                if harness_neg[i,b,f,s,1] > 0: #si la posicion del harness positivo no está vacía
                                    perd_harness_neg_basicas = calculo_perdidas_circuito_individual(harness_neg[i,b,f,s,1], 1, 6, 'Cu', int_string, temp_cable) #1m de base para la conexion del harness
                                    for se in range(2,6):
                                        if harness_neg[i,b,f,s,se] > 0: #si hay algun string extension
                                            perd_harness_neg_string_extensions = perd_harness_neg_string_extensions + calculo_perdidas_circuito_individual(harness_neg[i,b,f,s,se], (se-1)*long_string, 6, 'Cu', int_string, temp_cable)
                                
                                #Calculamos el tramo desde el harness hasta el anterior y la total
                                if s==0:
                                    perdidas_tramo = calculo_perdidas_circuito_individual(2, med_inst_DC_Bus_pos[i,inv,caja,bus,0]-tramo_aereo_DC_Bus_pos[i,inv,caja,bus], seccion_DCBus, 'Al', np.nansum(harness_pos[i,b,f,:,1])*int_string , temp_cable) #se usa el positivo porque van a ser igual y asi evitamos duplicar la operacion
                                    perd_bus = perd_bus + perdidas_tramo + perd_harness_pos_basicas + perd_harness_neg_basicas + perd_harness_pos_string_extensions + perd_harness_neg_string_extensions
                                    
                                    s_acum_pos = harness_pos[i,b,f,s,1]
                                    s_acum_neg = harness_neg[i,b,f,s,1]
                                    s_pos_ant = s #actualizamos el s anterior para la siguiente vuelta del for
                                    s_neg_ant = s
                                    
                                else:
                                    if harness_pos[i,b,f,s,1] > 0: #si la posicion del harness positivo no está vacía
                                        perdidas_tramo_pos = calculo_perdidas_circuito_individual(1, abs(coord_harness_pos[i,b,f,s,1]-coord_harness_pos[i,b,f,s_pos_ant,1])*(1+slack_DC_Bus/100)*(1+desnivel_cable_por_pendientes_tramo_aereo/100), seccion_DCBus, 'Al', (np.nansum(harness_pos[i,b,f,:,1]) - s_acum_pos)*int_string, temp_cable)
                                        s_pos_ant = s 
                                        s_acum_pos = s_acum_pos + harness_pos[i,b,f,s,1]
                                    if harness_neg[i,b,f,s,1] > 0: #si la posicion del harness negativo no está vacía
                                        perdidas_tramo_neg = calculo_perdidas_circuito_individual(1, abs(coord_harness_neg[i,b,f,s,1]-coord_harness_pos[i,b,f,s_neg_ant,1])*(1+slack_DC_Bus/100)*(1+desnivel_cable_por_pendientes_tramo_aereo/100), seccion_DCBus, 'Al', (np.nansum(harness_neg[i,b,f,:,1]) - s_acum_neg)*int_string, temp_cable) #se deja la seccion del positivo porque no tiene sentido que cambie entre polos y asi ahorramos pasar otra variable
                                        s_neg_ant = s
                                        s_acum_neg = s_acum_neg + harness_neg[i,b,f,s,1]
                                      
                                    perd_bus = perd_bus + perdidas_tramo_pos + perdidas_tramo_neg + perd_harness_pos_basicas + perd_harness_neg_basicas + perd_harness_pos_string_extensions + perd_harness_neg_string_extensions
                        
                        
                        perdidas_DC_Bus[i,inv,caja,bus,0] = perd_bus
                        perdidas_DC_Bus[i,inv,caja,bus,1] = perd_bus / (np.nansum(harness_pos[i,b,f,:,1])*pot_string_STC[i])*100
                        
    return perdidas_DC_Bus


def calculo_cdt_trifasica(intensidad, long, material, temp_cable, seccion, reactancia_mOhm, cos_phi):
    reactancia = reactancia_mOhm / 1000
    
    res_Al_20deg = 0.0282 #Ohm-mm2/m equivale a una conductividad de 35.46 m/Ohm-mm2
    res_Cu_20deg = 0.0172 #Ohm-mm2/m, equivale a una conductividad de 58.14 m/Ohm-mm2
    
    alpha_Al = 0.00403 #factor de cambio de resistividad con temperatura
    alpha_Cu = 0.00393 #factor de cambio de resistividad con temperatura
    
    if material == 'Al':
        res_corr = res_Al_20deg *(1+alpha_Al*(temp_cable-20))
    elif material == 'Cu':
        res_corr = res_Cu_20deg *(1+alpha_Cu*(temp_cable-20))
        
        
    cdt = np.sqrt(3)*intensidad*long*res_corr/seccion + np.sqrt(3)*intensidad*long*reactancia*np.sin(np.acos(cos_phi))
    
    return cdt



def calculo_perdidas_array(bloque_inicial,n_bloques, max_b, max_c, DCBoxes_o_Inv_String, cajas_fisicas, equi_ibc, med_pos, med_neg, med, uni_o_multipolar, int_string, temp_array, perdidas_array, pot_string_STC, cdt_array, pot_inv, cos_phi, v_inv, X_cable, material_array):
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(cajas_fisicas[i,b,0,0]): #si la banda no está vacía       
                for c in range(0,max_c):      
                    if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la caja no está vacía  
                    
                        #Pasamos de base 0 a base 1
                        if DCBoxes_o_Inv_String == 'String Inverters':
                            c=c+1
                            
                        #Sacamos las equivalencias en nomenclatura GRS
                        inv = int(equi_ibc[i,b,c,1])
                        caja = int(equi_ibc[i,b,c,2])
                        
                        if DCBoxes_o_Inv_String == 'DC Boxes':
                            perdidas_pos = calculo_perdidas_circuito_individual(1, med_pos[i,inv,caja,0], med_pos[i,inv,caja,1], material_array, cajas_fisicas[i,b,c,0] * int_string, temp_array)
                            perdidas_neg = calculo_perdidas_circuito_individual(1, med_neg[i,inv,caja,0], med_neg[i,inv,caja,1], material_array, cajas_fisicas[i,b,c,0] * int_string, temp_array)
                            
                            perdidas_array[i,inv,caja,0] = perdidas_pos + perdidas_neg
                            perdidas_array[i,inv,caja,1] = perdidas_array[i,inv,caja,0] / (cajas_fisicas[i,b,c,0] * pot_string_STC[i]) * 100
                            
                        elif DCBoxes_o_Inv_String == 'String Inverters':
                            int_inv = pot_inv/np.sqrt(3)/v_inv
                            perdidas_array[i,inv,caja,0] = calculo_perdidas_circuito_individual(3, med[i,inv,caja,0]/3, med[i,inv,caja,1], material_array, int_inv, temp_array) #la medicion incluye los 3 polos, se divide por 3 y se ponen 3 circuitos en lugar de 1, es lo mismo pero formalmente es lo correcto
                            perdidas_array[i,inv,caja,1] = perdidas_array[i,inv,caja,0] / pot_inv * 100
                            
                            cdt_array[i,inv,caja,0] = calculo_cdt_trifasica(int_inv, med[i,inv,caja,0]/uni_o_multipolar, material_array, temp_array, med[i,inv,caja,1], X_cable, cos_phi)
                            cdt_array[i,inv,caja,1] = cdt_array[i,inv,caja,0]/v_inv*100                        
                        
                                
    return perdidas_array, cdt_array

















