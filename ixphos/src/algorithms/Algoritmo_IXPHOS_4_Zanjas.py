# -*- coding: utf-8 -*-
"""
Created on Wed May 14 19:41:59 2025

@author: mlopez
"""

import numpy as np




#--------------------PREPARAR POLILINEAS PARA QUE LAS QUE SON COLINEARES TENGAN PUNTOS COMUNES------------------
#Sacamos todos los puntos de todas las polilineas y les hacemos un np.unique
#Buscamos en cada una de las polilineas si hay algun punto de la base de datos que sea colineal en los segmentos que define la polilinea
#En caso afirmativo se inserta ese punto en la polilinea

def densificar_polilineas_con_puntos_comunes(bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, max_c, max_tubos_bloque, cajas_fisicas, filas_en_cajas, strings_fisicos, filas_con_cable_string, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO, DCBoxes_o_Inv_String):
    from scipy.spatial import cKDTree
    
    # Inicializar una lista para almacenar todas las polilíneas válidas
    all_polylines = []
    
    if pol_cable_string is not None:
        filtered_pol_cable_string = pol_cable_string[..., 1:, :] #quitamos el indice 0 para que no se densifiquen los cables de string con los inicios de cada string en el mismo tracker, fastidiandose la zanja DC
        flat_pol_string = filtered_pol_cable_string.reshape(-1, 2)
        all_polylines.append(flat_pol_string)
    
    if pol_DC_Bus is not None:
        flat_pol_DC_Bus = pol_DC_Bus.reshape(-1, 2)
        all_polylines.append(flat_pol_DC_Bus)
    
    if pol_tubo_corrugado_zanja_DC is not None:
        flat_pol_tubo_corrugado_zanja_DC = pol_tubo_corrugado_zanja_DC.reshape(-1,2)
        all_polylines.append(flat_pol_tubo_corrugado_zanja_DC)
    
    if pol_array_cable is not None:
        flat_pol_array_cable = pol_array_cable.reshape(-1, 2)
        all_polylines.append(flat_pol_array_cable)
    
    if pol_AASS_LVAC is not None:
        flat_pol_AASS_LVAC = pol_AASS_LVAC.reshape(-1, 2)
        all_polylines.append(flat_pol_AASS_LVAC)
    
    if pol_ethernet is not None:
        flat_pol_ethernet = pol_ethernet.reshape(-1, 2)
        all_polylines.append(flat_pol_ethernet)
    
    if pol_CCTV_LVAC:
        flat_pol_CCTV_LVAC = np.vstack(pol_CCTV_LVAC).reshape(-1, 2)
        all_polylines.append(flat_pol_CCTV_LVAC)
    
    if pol_OyM_supply_LVAC:
        flat_pol_OyM_supply_LVAC = np.vstack(pol_OyM_supply_LVAC).reshape(-1, 2)
        all_polylines.append(flat_pol_OyM_supply_LVAC)
    
    if pol_Warehouse_supply_LVAC:
        flat_pol_Warehouse_supply_LVAC = np.vstack(pol_Warehouse_supply_LVAC).reshape(-1, 2)
        all_polylines.append(flat_pol_Warehouse_supply_LVAC)
    
    if pol_cable_MV is not None:
        coords_MV = []
        for i, linea in enumerate(pol_cable_MV):
            if i != 0:
                for j, tramo in enumerate(linea):
                    if j==0:
                        continue
                    coords_MV.append(np.array(tramo[2]).reshape(-1, 2))
        if coords_MV:
            flat_pol_cable_MV = np.vstack(coords_MV)
            all_polylines.append(flat_pol_cable_MV)
    
    if pol_cable_FO is not None:
        coords_FO = []
        for i, linea in enumerate(pol_cable_FO):
            if i != 0:
                for tramo in linea:
                    coords_FO.append(np.array(tramo[2]).reshape(-1, 2))
        if coords_FO:
            flat_pol_cable_FO = np.vstack(coords_FO)
            all_polylines.append(flat_pol_cable_FO)
    
    # Hacer el vstack solo si hay arrays en la lista
    if all_polylines:
        flattened_data_todas_pol = np.vstack(all_polylines)
        flattened_data_todas_pol_sin_nan = np.array([row for row in flattened_data_todas_pol if not np.isnan(row).any()])
    else:
        flattened_data_todas_pol_sin_nan = np.empty((0, 2))
    
        
        
    
    
    
    
    
    #Obtener puntos unicos mediante el metodo de centroides (puntos dentro de un mismo radio de tolerancia)    
    arbol_inicial = cKDTree(flattened_data_todas_pol_sin_nan)

    tolerancia_agrupamiento = 0.15
    clusters = arbol_inicial.query_ball_tree(arbol_inicial, r=tolerancia_agrupamiento)
    
    visited = set()
    centroides = []
    
    for group in clusters:
        group_set = set(group)
        if not group_set.isdisjoint(visited):
            continue  # Ya fue procesado
        visited.update(group_set)
        puntos = flattened_data_todas_pol_sin_nan[list(group_set)]
        centroide = np.mean(puntos, axis=0)
        centroides.append(centroide)
    
    puntos_unicos_con_centroides = np.array(centroides) #array con punto unicos habiendo simplificado los proximos en sus centroides




    #Corregimos los puntos de las polilineas que se han movido a cada centroide
    arbol_con_centroides = cKDTree(puntos_unicos_con_centroides) #para agilizar
    
    def mover_punto_a_centroide(punto, tree, tolerancia):
        if np.isnan(punto).any():
            return punto  # Devolver tal cual si es NaN
        idx = tree.query_ball_point(punto, r=tolerancia)
        if idx:  # Hay centroides cercanos
            return tree.data[idx[0]]  # Usamos el primero encontrado
        return punto  # No se redirige si no hay centroide cercano

    def mover_puntos_dentro_de_polilineas(polilinea, centroides_tree, tolerancia):
        new_polilinea = np.copy(polilinea)
        it = np.nditer(polilinea[..., 0], flags=['multi_index'])
        
        for _ in it:
            idx = it.multi_index
            punto = polilinea[idx]
            if not np.isnan(punto).any():
                new_polilinea[idx] = mover_punto_a_centroide(punto, centroides_tree, tolerancia)
        return new_polilinea
    

    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(strings_fisicos[i,b,0,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b+1):      
                    if ~np.isnan(strings_fisicos[i,b,f,0,0]): #si la fila no está vacía 
                               
                        #CABLES DE STRING
                        if filas_con_cable_string[i,b,f]==True: 
                            for s in range(0,max_spf):                                  
                                if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío
                                    pol_cable_string[i,b,f,s] = mover_puntos_dentro_de_polilineas(pol_cable_string[i,b,f,s], arbol_con_centroides, tolerancia_agrupamiento)
 
                        #DC BUSES
                        if filas_con_cable_string[i,b,f]==False:
                            if ~np.isnan(strings_fisicos[i,b,f,0,0]): #si el string no está vacío
                                pol_DC_Bus[i,b,f] = mover_puntos_dentro_de_polilineas(pol_DC_Bus[i,b,f], arbol_con_centroides, tolerancia_agrupamiento)
                            
                #CABLES DE ARRAY
                for c in range(0,max_c):
                    if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía
                        pol_array_cable[i,b,c] = mover_puntos_dentro_de_polilineas(pol_array_cable[i,b,c], arbol_con_centroides, tolerancia_agrupamiento)
                        
        #CABLES AASS LVAC (Combox + PVH + AWS en bloques)
        if pol_AASS_LVAC is not None:
            for serv_AC in range(0,4):
                if ~np.isnan(pol_AASS_LVAC[i,serv_AC,0,0]): 
                    pol_AASS_LVAC[i,serv_AC] = mover_puntos_dentro_de_polilineas(pol_AASS_LVAC[i,serv_AC], arbol_con_centroides, tolerancia_agrupamiento)
                    
                
        #CABLES ETHERNET (Combox + PVH + AWS en bloques)
        if pol_ethernet is not None:
            for serv_eth in range(0,4):
                if ~np.isnan(pol_ethernet[i,serv_eth,0,0]): 
                    pol_ethernet[i,serv_eth] = mover_puntos_dentro_de_polilineas(pol_ethernet[i,serv_eth], arbol_con_centroides, tolerancia_agrupamiento)
        

    #CABLES CCTV LVAC Y EDIFICIOS (listas planas)
    for i , circuito in enumerate(pol_CCTV_LVAC):
        pol_CCTV_LVAC[i] = mover_puntos_dentro_de_polilineas(circuito, arbol_con_centroides, tolerancia_agrupamiento)
        
    for i , circuito in enumerate(pol_OyM_supply_LVAC):
        pol_OyM_supply_LVAC[i] = mover_puntos_dentro_de_polilineas(circuito, arbol_con_centroides, tolerancia_agrupamiento)
        
    for i , circuito in enumerate(pol_Warehouse_supply_LVAC):
        pol_Warehouse_supply_LVAC[i] = mover_puntos_dentro_de_polilineas(circuito, arbol_con_centroides, tolerancia_agrupamiento)
        
        
    #CABLES MV (tramos de lineas con coord de ID en tramo[0] y tramo[1])
    for i, linea in enumerate(pol_cable_MV):
        if i==0:
            continue
        for j, tramo in enumerate(linea):
            if j==0:
                continue
            pol_cable_MV[i][j][2] = mover_puntos_dentro_de_polilineas(tramo[2], arbol_con_centroides, tolerancia_agrupamiento)
            
    #CABLES FO (tramos de lineas con coord de ID en tramo[0] y tramo[1])
    for i, linea in enumerate(pol_cable_FO):
        for j, tramo in enumerate(linea):
            if i==0:
                pass
            else:
                pol_cable_FO[i][j][2] = mover_puntos_dentro_de_polilineas(tramo[2], arbol_con_centroides, tolerancia_agrupamiento)


    #TUBOS DC
    for i in range(bloque_inicial,n_bloques+1):    
        for t in range (0,max_tubos_bloque):
            if ~np.isnan(pol_tubo_corrugado_zanja_DC[i,t,0,0]): #si el tubo no esta vacio
                pol_tubo_corrugado_zanja_DC[i,t] = mover_puntos_dentro_de_polilineas(pol_tubo_corrugado_zanja_DC[i,t], arbol_con_centroides, tolerancia_agrupamiento)


    #La segunda funcionalidad requerida es, una vez unificados los puntos, evaluar los segmentos que pasan cerca de ellos (a una distancia perpendicular menor a la tolerancia) e insertar el punto en ellos

    #Sacar los segmentos, una vez sacados los segmentos se les da un ancho de la tolerancia, en este caso 0.15, se evaluan los puntos de entre los unicos que tienen las x e y en la bbox del segmento para ver si caen dentro del area definida (la tolerancia)
    def distancia_perpendicular(p, a, b):
        """Devuelve la distancia perpendicular de p al segmento a-b"""
        ab = b - a
        ap = p - a
        ab_norm = np.dot(ab, ab)
        
        if ab_norm == 0:
            return np.linalg.norm(ap), False
    
        # Proyección del punto p sobre el segmento ab
        t = np.dot(ap, ab) / ab_norm
        t = max(0, min(1, t))  # Limitar la proyección al segmento (dentro de [0, 1])
        
        proyeccion = a + t * ab
        distancia = np.linalg.norm(p - proyeccion)
        
        return distancia, True
    
    def extraer_segmentos(polilinea):
        """Extrae los segmentos consecutivos de la polilínea"""
        segmentos = []
        for i in range(len(polilinea) - 1):
            segmentos.append((polilinea[i], polilinea[i + 1]))
        return segmentos
    
    def bbox_segmento(a, b, tolerancia):
        """Devuelve la bounding box (bbox) del segmento a-b con un ancho de tolerancia"""
        min_x = min(a[0], b[0]) - tolerancia
        max_x = max(a[0], b[0]) + tolerancia
        min_y = min(a[1], b[1]) - tolerancia
        max_y = max(a[1], b[1]) + tolerancia
        return (min_x, min_y), (max_x, max_y)
    
    def puntos_dentro_bbox(puntos, bbox_min, bbox_max):
        """Devuelve los puntos dentro de la bounding box definida"""
        return [p for p in puntos if bbox_min[0] <= p[0] <= bbox_max[0] and bbox_min[1] <= p[1] <= bbox_max[1]]
    
    def evaluar_puntos_en_segmentos(polilinea, puntos, tolerancia):
        segmentos = extraer_segmentos(polilinea)

        puntos_imprimidos = set()  # Usamos un set para asegurarnos de no imprimir puntos duplicados
        
        for a, b in segmentos:
            # # Obtener la bounding box del segmento con la tolerancia
            # bbox_min, bbox_max = bbox_segmento(a, b, tolerancia)
            
            # # Filtrar los puntos dentro de la bbox
            # puntos_en_bbox = puntos_dentro_bbox(puntos, bbox_min, bbox_max)
            
            
            mid_point = (a + b) / 2
            segment_length = np.linalg.norm(b - a)
            query_radius = segment_length / 2 + tolerancia
            
            # Buscar puntos en circulo alrededor del segmento
            idx = arbol_con_centroides.query_ball_point(mid_point, query_radius)
            
            puntos_en_bbox = puntos[idx]


            for p in puntos_en_bbox:
                # Convertir el punto a una tupla para poder agregarlo al set
                p_tuple = tuple(p)
                
                # Si el punto pertenece a los puntos extremos (a o b) del segmento, lo ignoramos
                if np.array_equal(p, a) or np.array_equal(p, b):
                    continue
                
                # Calcular la distancia perpendicular de p al segmento (a, b)
                distancia, _ = distancia_perpendicular(np.array(p), np.array(a), np.array(b))
                
                # Si la distancia es menor que la tolerancia, y el punto no ha sido tratado antes
                if distancia < tolerancia and p_tuple not in puntos_imprimidos:
                    puntos_imprimidos.add(p_tuple)  # Agregar el punto al set para evitar duplicados
        return np.array(list(puntos_imprimidos), dtype=np.float64)


    #Identificados los puntos en tolerancia se insertan en la polilinea a traves de una lista convertida a array y recortada posteriormente
    def insertar_puntos_en_polilinea(polilinea, puntos, tolerancia):
        """Inserta puntos dentro de la tolerancia en los segmentos correspondientes"""
        max_p_original = polilinea.shape[0]
        polilinea_sin_nan = polilinea[~np.isnan(polilinea[:, 0])]
        
        segmentos = extraer_segmentos(polilinea_sin_nan)
        nueva_polilinea = []
        
        puntos_imprimidos = set()
    
        for a, b in segmentos:
            nueva_polilinea.append(a)
    
            mid_point = (a + b) / 2
            segment_length = np.linalg.norm(b - a)
            query_radius = segment_length / 2 + tolerancia
            idx = arbol_con_centroides.query_ball_point(mid_point, query_radius)
            puntos_en_bbox = puntos[idx]
    
            puntos_a_insertar = []
    
            ab = b - a
            ab_norm_sq = np.dot(ab, ab)
            if ab_norm_sq == 0:
                continue  # evitar división por cero en segmentos degenerados
    
            for p in puntos_en_bbox:
                if np.array_equal(p, a) or np.array_equal(p, b):
                    continue
    
                distancia, _ = distancia_perpendicular(np.array(p), np.array(a), np.array(b))
                if distancia < tolerancia:
                    p_tuple = tuple(p)
                    if p_tuple in puntos_imprimidos:
                        continue
    
                    # Proyección del punto sobre el segmento: t ∈ [0,1]
                    ap = np.array(p) - a
                    t = np.dot(ap, ab) / ab_norm_sq
                    puntos_a_insertar.append((t, p))
                    puntos_imprimidos.add(p_tuple)
    
            # Ordenar por posición a lo largo del segmento
            puntos_a_insertar.sort(key=lambda x: x[0])
    
            for _, p in puntos_a_insertar:
                nueva_polilinea.append(p)
    
        nueva_polilinea.append(polilinea_sin_nan[-1])  # Agregar el punto final
        
        n = len(nueva_polilinea)
        
        if n < max_p_original:
            resultado = np.full_like(polilinea, np.nan)
            resultado[:n] = nueva_polilinea
            return resultado
    
        return np.array(nueva_polilinea)
    
        






    tolerancia_desvio = 0.15
    
    #Recorremos las polilineas actualizando
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(strings_fisicos[i,b,0,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b+1):      
                    if ~np.isnan(strings_fisicos[i,b,f,0,0]): #si la fila no está vacía 
                               
                        #CABLES DE STRING
                        if filas_con_cable_string[i,b,f]==True: 
                            for s in range(0,max_spf):                                  
                                if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío
                                    pol_cable_string[i,b,f,s] = insertar_puntos_en_polilinea(pol_cable_string[i,b,f,s], puntos_unicos_con_centroides, tolerancia_desvio)
 
                        #DC BUSES
                        if filas_con_cable_string[i,b,f]==False:  
                            if ~np.isnan(strings_fisicos[i,b,f,0,0]): #si el string no está vacío
                                pol_DC_Bus[i,b,f] = insertar_puntos_en_polilinea(pol_DC_Bus[i,b,f], puntos_unicos_con_centroides, tolerancia_desvio)
                            
                #CABLES DE ARRAY
                for c in range(0,max_c):
                    if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía
                        pol_array_cable[i,b,c] = insertar_puntos_en_polilinea(pol_array_cable[i,b,c], puntos_unicos_con_centroides, tolerancia_desvio)
                        
        #CABLES AASS LVAC (Combox + PVH + AWS en bloques)
        if pol_AASS_LVAC is not None:
            for serv_AC in range(0,4):
                if ~np.isnan(pol_AASS_LVAC[i,serv_AC,0,0]): 
                    pol_AASS_LVAC[i,serv_AC] = insertar_puntos_en_polilinea(pol_AASS_LVAC[i,serv_AC], puntos_unicos_con_centroides, tolerancia_desvio)
                    
                    
        #CABLES ETHERNET (Combox + PVH + AWS en bloques)
        if pol_ethernet is not None:
            for serv_eth in range(0,4):
                if ~np.isnan(pol_ethernet[i,serv_eth,0,0]): 
                    pol_ethernet[i,serv_eth] = insertar_puntos_en_polilinea(pol_ethernet[i,serv_eth], puntos_unicos_con_centroides, tolerancia_desvio)
        

    #CABLES CCTV LVAC Y EDIFICIOS (listas planas)
    for i , circuito in enumerate(pol_CCTV_LVAC):
        pol_CCTV_LVAC[i] = insertar_puntos_en_polilinea(circuito, puntos_unicos_con_centroides, tolerancia_desvio)
        
    for i , circuito in enumerate(pol_OyM_supply_LVAC):
        pol_OyM_supply_LVAC[i] = insertar_puntos_en_polilinea(circuito, puntos_unicos_con_centroides, tolerancia_desvio)
        
    for i , circuito in enumerate(pol_Warehouse_supply_LVAC):
        pol_Warehouse_supply_LVAC[i] = insertar_puntos_en_polilinea(circuito, puntos_unicos_con_centroides, tolerancia_desvio)
        
        
    #CABLES MV (tramos de lineas con coord de ID en tramo[0] y tramo[1])
    for i, linea in enumerate(pol_cable_MV):
        if i==0:
            continue
        for j, tramo in enumerate(linea): 
            if j==0:
                continue
            pol_cable_MV[i][j][2] = insertar_puntos_en_polilinea(tramo[2], puntos_unicos_con_centroides, tolerancia_desvio)
            
    #CABLES FO (tramos de lineas con coord de ID en tramo[0] y tramo[1])
    for i, linea in enumerate(pol_cable_FO):
        for j, tramo in enumerate(linea):
            if i==0:
                pass
            else:
                pol_cable_FO[i][j][2] = insertar_puntos_en_polilinea(tramo[2], puntos_unicos_con_centroides, tolerancia_desvio)

            
    #TUBOS DC
    for i in range(bloque_inicial,n_bloques+1):    
        for t in range (0,max_tubos_bloque):
            if ~np.isnan(pol_tubo_corrugado_zanja_DC[i,t,0,0]): #si el tubo no esta vacio
                pol_tubo_corrugado_zanja_DC[i,t] = insertar_puntos_en_polilinea(pol_tubo_corrugado_zanja_DC[i,t], puntos_unicos_con_centroides, tolerancia_desvio)



    return pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC, pol_array_cable, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_cable_MV, pol_cable_FO














        
def normalizar_segmentos(segmentos): #Funcion para ordenar pares de puntos XY de menor a mayor para que al comparar segmentos unicos de zanjas no haya iguales que se identifiquen como diferentes por estar con los vertices invertidos
    """
    Ordena los puntos de cada segmento de forma consistente para que
    [x0, y0, x1, y1] y [x1, y1, x0, y0] se consideren el mismo segmento.
    """
    normalizados = []
    for seg in segmentos:
        p1 = seg[:2]
        p2 = seg[2:]
        if tuple(p1) <= tuple(p2):  # orden normal
            normalizados.append(np.concatenate([p1, p2]))
        else:  # invertir
            normalizados.append(np.concatenate([p2, p1]))
    return np.array(normalizados)






def zanjas_protegidas_camino(segmento,polilinea):
    
    def ccw(A, B, C):
        """Devuelve True si los puntos A, B y C están en sentido antihorario"""
        Ax, Ay = float(A[0]), float(A[1])
        Bx, By = float(B[0]), float(B[1])
        Cx, Cy = float(C[0]), float(C[1])
        return (Cy - Ay) * (Bx - Ax) > (By - Ay) * (Cx - Ax)
    
    def segments_intersect(A, B, C, D):
        """Devuelve True si el segmento AB se cruza con CD"""
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)
    
    def check_intersection(seg_start, seg_end, polyline_coords):
        """Verifica si el segmento (seg_start -> seg_end) se cruza con la polilínea"""
        # Convierte la lista plana en pares (x, y)
        poly_points = [(float(polyline_coords[i]), float(polyline_coords[i+1])) 
                       for i in range(0, len(polyline_coords)-1, 2)]
    
        A = (float(seg_start[0]), float(seg_start[1]))
        B = (float(seg_end[0]), float(seg_end[1]))
    
        for i in range(len(poly_points) - 1):
            C = poly_points[i]
            D = poly_points[i+1]
            if segments_intersect(A, B, C, D):
                return True
        return False

    

    hay_interseccion = check_intersection(segmento[0], segmento[1], polilinea)
    
    return hay_interseccion






def trazado_zanjas_MV(pol_cable_MV, max_c_tz):
    #De la estructura de FO basada en lineas con listas y np arrays sacamos los segmentos 
    if pol_cable_MV:
        segmentos_MV = []
        for i, linea in enumerate(pol_cable_MV):
            if i==0:
                pass
            else:
                for tramo in linea:
                    puntos = tramo[2]  # ya es (N, 2)
                    if puntos.shape[0] < 2:
                        continue  # saltar si hay menos de 2 puntos
            
                    for k in range(len(puntos) - 1):
                        segmento = np.concatenate((puntos[k], puntos[k + 1]))  # [x0, y0, x1, y1]
                        segmentos_MV.append(segmento)
        
        trazados_MV = normalizar_segmentos(np.array(segmentos_MV)) #normalizamos para evitar fallos de identidad unica con vertices opuestos
        coord_MV, n_c_MV = np.unique(trazados_MV, axis=0, return_counts=True)
    else:
        coord_MV = np.empty((0, 4))
    
    
    #Creamos columnas con ceros para incluir mas adelante cable AC, cable de fibra y PAT
    n_c_MV.reshape(-1, 1)
    cables = np.stack((n_c_MV.reshape(-1, 1) , np.zeros((n_c_MV.reshape(-1, 1).shape[0],3), dtype = int)))
    #Añadimos a las c
    zanjas_MV_ID = np.hstack((cables, coord_MV))    

    
    
    rango_tipos_zanjas=[0,max_c_tz]
    tdz_act=1
    for nc in range(1,int(np.nanmax(zanjas_MV_ID[:,0]))+1): #desde 1 hasta el maximo numero de circuitos en una sola zanja
        if nc > rango_tipos_zanjas[tdz_act]: #si el numero de circuitos es mayor que el del tipo de zanja hace falta actualizar el tipo (si hay 3 circuitos en la LV1 y ael max de c por zanja es 2, el tdz pasa a LV2)
            rango_tipos_zanjas.append(rango_tipos_zanjas[tdz_act]+max_c_tz) #guardamos el tipo de zanja y su numero de circuitos maximo
            tdz_act=tdz_act+1
    
    
    return zanjas_MV_ID, rango_tipos_zanjas





def trazado_zanjas_DC_y_conteo_tubos_circuitos_en_zanja(String_o_Bus,bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf,max_p, filas_en_cajas, strings_fisicos, pol_cable_string, pol_DC_Bus, filas_con_cable_string, pol_tubo_corrugado_zanja_DC, max_tubos_bloque):     
    #TRAZADO DE ZANJAS DC Y CONTEO DE TUBOS EN ZANJA
    #creamos un array de trazado de zanjas donde se guarda la polilinea del cable de string en formato [px py p+1x p+1y] a partir del p2 y sin contar el ultimo
    if String_o_Bus == 'String Cable':
        trazados_zanjas_DC=np.full((n_bloques+1,max_b,max_f_str_b,max_spf,max_p,4),np.nan) 
        trazado_tubo_corrugado_zanja_DC=np.full((n_bloques+1,max_b,max_f_str_b,max_p,4),np.nan) 
        for i in range(bloque_inicial,n_bloques+1):
            for b in range(0,max_b):
                if ~np.isnan(strings_fisicos[i,b,0,0,0]): #si la banda no está vacía       
                    for f in range (0,max_f_str_b+1):      
                        if ~np.isnan(strings_fisicos[i,b,f,0,0]): #si la fila no está vacía                 
                            for s in range(0,max_spf):                                  
                                if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío 
                                    for p in range(1,max_p-1):
                                        if ~np.isnan(pol_cable_string[i,b,f,s,p+1,0]): #el ultimo punto es debajo de la caja pero la zanja llega al penultimo, en el borde
                                            trazados_zanjas_DC[i,b,f,s,p,0]=pol_cable_string[i,b,f,s,p,0]
                                            trazados_zanjas_DC[i,b,f,s,p,1]=pol_cable_string[i,b,f,s,p,1]
                                            trazados_zanjas_DC[i,b,f,s,p,2]=pol_cable_string[i,b,f,s,p+1,0]
                                            trazados_zanjas_DC[i,b,f,s,p,3]=pol_cable_string[i,b,f,s,p+1,1]
                                
                            
    elif String_o_Bus == 'DC Bus':  
        trazados_zanjas_DC=np.full((n_bloques+1,max_b,max_f_str_b,max_p,4),np.nan) 
        trazado_tubo_corrugado_zanja_DC=np.full((n_bloques+1,max_b,max_f_str_b,max_p,4),np.nan) 
        for i in range(bloque_inicial,n_bloques+1):
            for b in range(0,max_b):
                if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
                    for f in range (0,max_f_str_b+1):      
                        if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía                  
                            for p in range(1,max_p-1):
                                if ~np.isnan(pol_DC_Bus[i,b,f,p-1,0]): #si la polilinea no ha llegado al borde
                                    trazados_zanjas_DC[i,b,f,p,0]=pol_DC_Bus[i,b,f,p,0]
                                    trazados_zanjas_DC[i,b,f,p,1]=pol_DC_Bus[i,b,f,p,1]
                                    trazados_zanjas_DC[i,b,f,p,2]=pol_DC_Bus[i,b,f,p+1,0]
                                    trazados_zanjas_DC[i,b,f,p,3]=pol_DC_Bus[i,b,f,p+1,1]
                    
                    
    else: #si es both types o mixed
        trazados_string_zanjas_DC=np.full((n_bloques+1,max_b,max_f_str_b,max_spf,max_p,4),np.nan) 
        trazados_bus_zanjas_DC=np.full((n_bloques+1,max_b,max_f_str_b,max_p,4),np.nan) 
        trazado_tubo_corrugado_zanja_DC=np.full((n_bloques+1,max_b,max_f_str_b,max_p,4),np.nan) 
        for i in range(bloque_inicial,n_bloques+1):
            for b in range(0,max_b):
                if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
                    for f in range (0,max_f_str_b+1):      
                        if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía                            
                            #SI LA FILA ES DE STRING
                            if filas_con_cable_string[i,b,f]==True: 
                                for s in range(0,max_spf):                                  
                                    if ~np.isnan(strings_fisicos[i,b,f,s,0]): #si el string no está vacío 
                                        for p in range(1,max_p-1):
                                            if ~np.isnan(pol_cable_string[i,b,f,s,p+1,0]): #si la polilinea no ha llegado al final
                                                trazados_string_zanjas_DC[i,b,f,s,p,0]=pol_cable_string[i,b,f,s,p,0]
                                                trazados_string_zanjas_DC[i,b,f,s,p,1]=pol_cable_string[i,b,f,s,p,1]
                                                trazados_string_zanjas_DC[i,b,f,s,p,2]=pol_cable_string[i,b,f,s,p+1,0]
                                                trazados_string_zanjas_DC[i,b,f,s,p,3]=pol_cable_string[i,b,f,s,p+1,1]                             
                                
                            else: #SI LA FILA ES DE DCBUS
                                for p in range(1,max_p-1):
                                    if ~np.isnan(pol_DC_Bus[i,b,f,p+1,0]): #si la polilinea no ha llegado al final
                                        trazados_bus_zanjas_DC[i,b,f,p,0]=pol_DC_Bus[i,b,f,p,0]
                                        trazados_bus_zanjas_DC[i,b,f,p,1]=pol_DC_Bus[i,b,f,p,1]
                                        trazados_bus_zanjas_DC[i,b,f,p,2]=pol_DC_Bus[i,b,f,p+1,0]
                                        trazados_bus_zanjas_DC[i,b,f,p,3]=pol_DC_Bus[i,b,f,p+1,1]
                                        

    #Sacamos el trazado de los tubos a partir de las polilineas de tubos de subarray (que van en zanjas DC), que han podido ser editadas
    trazado_tubo_corrugado_zanja_DC=np.full((n_bloques+1,max_tubos_bloque,max_p,4),np.nan) 
    for i in range(bloque_inicial,n_bloques+1):    
        for t in range (0,max_tubos_bloque):
            if ~np.isnan(pol_tubo_corrugado_zanja_DC[i,t,0,0]): #si el tubo no esta vacio
                for p in range(0,max_p-2):
                    if ~np.isnan(pol_tubo_corrugado_zanja_DC[i,t,p+1,0]): #si la polilinea no ha llegado al final
                        trazado_tubo_corrugado_zanja_DC[i,t,p,0]=pol_tubo_corrugado_zanja_DC[i,t,p,0]
                        trazado_tubo_corrugado_zanja_DC[i,t,p,1]=pol_tubo_corrugado_zanja_DC[i,t,p,1]
                        trazado_tubo_corrugado_zanja_DC[i,t,p,2]=pol_tubo_corrugado_zanja_DC[i,t,p+1,0]
                        trazado_tubo_corrugado_zanja_DC[i,t,p,3]=pol_tubo_corrugado_zanja_DC[i,t,p+1,1]
    
                                
    # Sacamos las zanjas por bloque
    PB_zanjas_DC_ID=[np.array([0,0,0,0,0,0])]*bloque_inicial
    for i in range(bloque_inicial,n_bloques+1):   
        #Aplanamos los trazados de zanjas correspondientes a cables DC Bus o String, son "segmentos de zanjas"
        if String_o_Bus == 'String Cable' or String_o_Bus == 'DC Bus':
            flattened_data = trazados_zanjas_DC[i].reshape(-1, 4)
        else:
            flattened_data = np.vstack((trazados_string_zanjas_DC[i].reshape(-1, 4),trazados_bus_zanjas_DC[i].reshape(-1, 4))) #UNIMOS EN UNO LOS TRAZADOS TANTO DE CABLE DE STRING COMO DE DCBUS
          
        flattened_data_sin_nan = np.array([tuple(row) for row in flattened_data if not np.isnan(row).any()])
        # flattened_data_sin_nan = cuantizar_segmentos(flattened_data_sin_nan, 0.01)  #Ya no hace falta cuantizar porque se ha hecho una agrupacion de puntos por centroides previa a las polilineas
        
        #Sacamos los segmentos unicos, las veces que se repiten son el numero de circuitos DCBus + String que hay en ellos
        coord_zanjas_DC, n_circuitos_zanja_DC = np.unique(flattened_data_sin_nan, axis=0, return_counts=True)
        
        #Aplanamos los tubos del formato trazado, obtenemos "segmentos de tubo"
        flat_tubo_corr_DC = trazado_tubo_corrugado_zanja_DC[i].reshape(-1, 4)
        flat_tubo_corr_DC_sin_nan = np.array([tuple(row_t) for row_t in flat_tubo_corr_DC if not np.isnan(row_t).any()])
        # flat_tubo_corr_DC_sin_nan = cuantizar_segmentos(flat_tubo_corr_DC_sin_nan, 0.01)  #Ya no hace falta cuantizar porque se ha hecho una agrupacion de puntos por centroides previa a las polilineas
        
        #Sacamos los segmentos unicos, las veces que se repiten son el numero de tubos que hay en cada segmento, que coincidira con zanjas DC
        coord_tubos_DC , n_tubos = np.unique(flat_tubo_corr_DC_sin_nan, axis=0, return_counts=True)
        
        #Creamos un array de ceros con long igual al de zanjas DC para añadir el n de tubos correspondiente
        n_tubos_zanja_DC = np.zeros(len(coord_zanjas_DC[:,0]))
        #Buscamos que coordenadas de los segmentos de tubos DC coinciden con las coordenadas de los zanjas DC y le añadimos el numero de tubos
        c_t=-1
        for coord_tubos in coord_tubos_DC:
            c_t=c_t+1
            c_z=-1
            for coords_zanjas in coord_zanjas_DC:
                c_z=c_z+1
                if np.allclose(coord_tubos,coords_zanjas, rtol=0, atol=1e-3):
                    n_tubos_zanja_DC[c_z] = n_tubos[c_t]
                    
        PB_zanjas_DC_ID.append(np.hstack((n_tubos_zanja_DC.reshape(-1, 1), n_circuitos_zanja_DC.reshape(-1, 1), coord_zanjas_DC)))    
        
    #Obtenemos los de toda la planta apilando los de cada bloque    
    zanjas_DC_ID = np.vstack(PB_zanjas_DC_ID[bloque_inicial:])

    return zanjas_DC_ID, PB_zanjas_DC_ID





    
def trazado_zanjas_LV(bloque_inicial, n_bloques, max_b, max_c, max_p_array, cajas_fisicas, pol_array_cable, max_c_tz):             
    #TRAZADO DE ZANJAS LV
    #creamos un array de trazado de zanjas donde se guarda la polilinea del cable de array en formato [px py p+1x p+1y] a partir del p2 y sin contar el ultimo
    trazados_zanjas_LV=np.full((n_bloques+1,max_b,max_c,max_p_array,4),np.nan) #posible optimizar este 100 a max_p_lv
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(cajas_fisicas[i,b,0,0]): #si la banda no está vacía       
                for c in range(0,max_c):
                    if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                        for p in range(0,100): #posible optimizar este 100 a max_p_lv-1
                            if ~np.isnan(pol_array_cable[i,b,c,p,0]): #si la polilinea no ha llegado al final
                                trazados_zanjas_LV[i,b,c,p,0]=pol_array_cable[i,b,c,p,0]
                                trazados_zanjas_LV[i,b,c,p,1]=pol_array_cable[i,b,c,p,1]
                                trazados_zanjas_LV[i,b,c,p,2]=pol_array_cable[i,b,c,p+1,0]
                                trazados_zanjas_LV[i,b,c,p,3]=pol_array_cable[i,b,c,p+1,1]

    
    # TRANSFORMACION DE DATOS A FORMATO DIBUJO - Aplana los array y filtra los valores NaN
    PB_zanjas_LV_ID=[[0,0,0,0,0]]*bloque_inicial    
    for i in range(bloque_inicial,n_bloques+1):
        
        flattened_data = trazados_zanjas_LV[i].reshape(-1, 4)
        flattened_data_sin_nan = np.array([tuple(row) for row in flattened_data if not np.isnan(row).any()])  
        # flattened_data_sin_nan = cuantizar_segmentos(flattened_data_sin_nan, 0.01) #Ya no hace falta cuantizar porque se ha hecho una agrupacion de puntos por centroides previa a las polilineas

        zanjas_LV, n_circuitos_zanja_LV = np.unique(flattened_data_sin_nan, axis=0, return_counts=True)
        PB_zanjas_LV_ID.append(np.hstack((n_circuitos_zanja_LV.reshape(-1, 1),zanjas_LV)))    
        #si el codigo es correcto los dos arrays deben coincidir en forma y su unica diferencia es el numero, la columna 0
    zanjas_LV_ID = np.vstack(PB_zanjas_LV_ID) 
    
    
    tipos_zanjas=[0,max_c_tz]
    tdz_act=1
    for nc in range(1,int(np.nanmax(zanjas_LV_ID[:,0]))+1): #desde 1 hasta el maximo numero de circuitos en una sola zanja
        if nc > tipos_zanjas[tdz_act]: #si el numero de circuitos es mayor que el del tipo de zanja hace falta actualizar el tipo (si hay 3 circuitos en la LV1 y ael max de c por zanja es 2, el tdz pasa a LV2)
            tipos_zanjas.append(tipos_zanjas[tdz_act]+max_c_tz) #guardamos el tipo de zanja y su numero de circuitos maximo
            tdz_act=tdz_act+1
    
    return PB_zanjas_LV_ID, zanjas_LV_ID, tipos_zanjas




def combinaciones_circuitos_zanjas_LV(bloque_inicial, n_bloques, max_b, max_c, max_p_array, cajas_fisicas, pol_array_cable, tipos_zanjas, polilineas_caminos):
#TODO Se puede poner en funcion de la salida del routin en lugar de recorrer otra vez las polilineas de cable             
    #TRAZADO DE ZANJAS LV
    #creamos un array de trazado de zanjas donde se guarda la polilinea del cable de array en formato [px py p+1x p+1y] a partir del p2 y sin contar el ultimo
    trazados_zanjas_LV=np.full((n_bloques+1,max_b,max_c,max_p_array,6),np.nan) #posible optimizar este 100 a max_p_lv
    for i in range(bloque_inicial,n_bloques+1):
        for b in range(0,max_b):
            if ~np.isnan(cajas_fisicas[i,b,0,0]): #si la banda no está vacía       
                for c in range(0,max_c):
                    if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la celda de la caja no está vacía 
                        for p in range(0,100): #posible optimizar este 100 a max_p_lv-1
                            if ~np.isnan(pol_array_cable[i,b,c,p,0]): #si la polilinea no ha llegado al final
                                trazados_zanjas_LV[i,b,c,p,0]=pol_array_cable[i,b,c,p,0]
                                trazados_zanjas_LV[i,b,c,p,1]=pol_array_cable[i,b,c,p,1]
                                trazados_zanjas_LV[i,b,c,p,2]=pol_array_cable[i,b,c,p+1,0]
                                trazados_zanjas_LV[i,b,c,p,3]=pol_array_cable[i,b,c,p+1,1]
                                
                                
                                trazados_zanjas_LV[i,b,c,p,5]=int(cajas_fisicas[i,b,c,0]) #numero de circuitos en zanja                                
                                
                                
                                trazados_zanjas_LV[i,b,c,p,4]=0
                                for camino in polilineas_caminos:
                                    interseccion_con_camino = zanjas_protegidas_camino(((trazados_zanjas_LV[i,b,c,p,0],trazados_zanjas_LV[i,b,c,p,1]),(trazados_zanjas_LV[i,b,c,p,2],trazados_zanjas_LV[i,b,c,p,3])), camino)
        
                                    if interseccion_con_camino == True:
                                        trazados_zanjas_LV[i,b,c,p,4]=1

    
    
    flattened_data = trazados_zanjas_LV.reshape(-1, 6)
    flattened_data_sin_nan = np.array([tuple(row) for row in flattened_data if not np.isnan(row).any()])
    # flattened_data_sin_nan = cuantizar_segmentos(flattened_data_sin_nan, 0.01)  #Ya no hace falta cuantizar porque se ha hecho una agrupacion de puntos por centroides previa a las polilineas

    comb_strings_en_zanja_LV, n_comb_strings_en_zanja_LV = np.unique(flattened_data_sin_nan, axis=0, return_counts=True)
    
    info_circ_coord_zanjas_LV = []
    contador_protegidas = 0
    for i in range(len(comb_strings_en_zanja_LV)):
        clave = tuple(comb_strings_en_zanja_LV[i, [0, 1, 2, 3, 4]])  # coordenadas + protegida
        encontrada = False
        contador_protegidas += clave[4]
        for entrada in info_circ_coord_zanjas_LV:
            if entrada[0] == clave:
                entrada[1].append([comb_strings_en_zanja_LV[i, 5], n_comb_strings_en_zanja_LV[i]])
                encontrada = True
                break
        if not encontrada:
            info_circ_coord_zanjas_LV.append([clave, [[comb_strings_en_zanja_LV[i, 5], n_comb_strings_en_zanja_LV[i]]]])
    
    listas_ordenadas = []
    for clave, lista in info_circ_coord_zanjas_LV:
        n_circuitos_config = int(sum(par[1] for par in lista))
        protegida = int(clave[4])  # 1 = protegida → LVC
        nueva_config = [[int(par[0]), int(par[1])] for par in lista]
        nueva_config.insert(0, protegida)
        nueva_config.insert(0, n_circuitos_config)
        listas_ordenadas.append(nueva_config)
    
    # Eliminar duplicados teniendo en cuenta también el valor de 'protegida'
    listas_ordenadas_unicas = list({
        (config[0], config[1], *[tuple(x) for x in config[2:]])
        for config in listas_ordenadas
    })
    listas_ordenadas = [
        [item[0], item[1]] + [list(par) for par in item[2:]]
        for item in listas_ordenadas_unicas
    ]
    
    # Ordenar por número de circuitos y por valor de protegida
    listas_ordenadas = sorted(listas_ordenadas, key=lambda x: (x[0], x[1]))
    
    # Extraer los string_id únicos
    strings_en_circuitos = sorted({int(par[0]) for config in listas_ordenadas for par in config[2:]}, reverse=True)
    
    # Crear la tabla
    tabla_circuitos_en_zanjas = np.zeros((len(listas_ordenadas), len(strings_en_circuitos)), dtype=object)
    for fila in range(len(listas_ordenadas)):
        for par in listas_ordenadas[fila][2:]:
            columna = strings_en_circuitos.index(par[0])
            valor = int(par[1])
            tabla_circuitos_en_zanjas[fila][columna] = valor
    
    # Añadir fila de cabecera
    tabla_circuitos_en_zanjas_con_indices = np.vstack((strings_en_circuitos, tabla_circuitos_en_zanjas))
    
    # Añadir columnas de tipo LV/LVC
    columnas_tipos_zanja = np.zeros((len(listas_ordenadas) + 1, 2), dtype=object)
    columnas_tipos_zanja[0, 0] = 'Trench type'
    columnas_tipos_zanja[0, 1] = 'Subtype'
    for i in range(1, len(columnas_tipos_zanja)):
        protegida = listas_ordenadas[i - 1][1]
        tipo = np.where(np.array(tipos_zanjas) >= listas_ordenadas[i - 1][0])[0][0]
        if protegida == 1:
            columnas_tipos_zanja[i, 0] = f'LV{tipo}C'
        else:
            columnas_tipos_zanja[i, 0] = f'LV{tipo}'
        columnas_tipos_zanja[i, 1] = ''
    
    tabla_a_rellenar_subtipos_zanjas = np.hstack((columnas_tipos_zanja, tabla_circuitos_en_zanjas_con_indices))

    #ORDENACION
    # Eliminar cabecera y preparar datos
    datos = tabla_a_rellenar_subtipos_zanjas[1:]
    
    datos_ordenables = []
    for fila in datos:
        tipo_str = fila[0]  # 'LV2C' o 'LV2'
        
        # Extraer número del tipo
        tipo_num = int(''.join(filter(str.isdigit, tipo_str)))
        
        # Es protegida (LVxC)? → van después, por eso usamos 1 si C, 0 si no
        es_protegida = 1 if tipo_str.endswith('C') else 0
        
        # Circuitos desde columna 2 en adelante
        circuitos = [int(x) if x != 0 else 0 for x in fila[2:]]
    
        # Clave de ordenación: (tipo_num, es_protegida, -circuitos...)
        # Ahora invertimos los valores de los circuitos para que se ordenen de forma descendente
        clave_orden = (tipo_num, es_protegida, [-x for x in circuitos])
        datos_ordenables.append((clave_orden, fila))
    
    # Ordenar por clave
    datos_ordenables.sort(key=lambda x: x[0])
    
    # Extraer filas ordenadas
    datos_ordenados = [fila for _, fila in datos_ordenables]
    
    # Reconstruir tabla con cabecera
    tabla_ordenada = np.vstack((tabla_a_rellenar_subtipos_zanjas[0], datos_ordenados))
    
    
    
    
    return tabla_ordenada, info_circ_coord_zanjas_LV #Sacamos tambien la segunda variable porque contiene todas las zanjas con su info de coordenadas, si estan protegidas y el numero de circuitos de cada tipo






def calculo_zanja_IEC_60364(DCBoxes_o_Inv_String, n_circuitos,intensidad_circuitos,material_conductor,material_aislante,seccion,diametro_cable,metodo_instalacion,temperatura_suelo,K_suelo,ancho_min):
    #TODO - IEC 60364 SIMPLIFICADA, DEBERIA USARSE 60287, TENEMOS QUE COMPRARLA QUE ESTA DEL 2001
    IEC_tabla_de_secciones_cable =        [1.5,2.5,4,6,10, 16, 25, 35, 50, 70, 95,120,150,185,240,300]
    
    IEC_tabla_de_ampacidades_2_cond_XLPE=[[25,33,43,53,71, 91,116,139,164,203,239,271,306,343,395,446],
                                          [27,35,46,58,77,100,129,155,183,225,270,306,343,387,448,502],
                                          [ 0,26,33,42,55, 71, 90,108,128,158,186,211,238,267,307,346],
                                          [ 0, 0, 0, 0, 0, 76, 98,117,139,170,204,233,261,296,343,386]] #Cobre EBT, Cobre DE, Aluminio EBT, Aluminio DE
    
    IEC_tabla_de_ampacidades_2_cond_PVC =[[22,29,37,46,60, 78, 99,119,140,173,204,231,261,292,336,379],
                                          [22,28,38,48,61, 83,110,132,156,192,230,261,293,331,382,427],
                                          [ 0,22,29,36,47, 61, 77, 93,109,135,159,180,204,228,262,296],
                                          [ 0, 0, 0, 0, 0, 63, 82, 98,117,145,173,200,224,255,298,336]] #Cobre EBT, Cobre DE, Aluminio EBT, Aluminio DE
    
    IEC_tabla_de_ampacidades_3_cond_XLPE =[[21,17,25,44,58,75, 96,115,135,167,197,223,251,281,324,365],
                                          [ 23,30,39,49,65,84,107,129,153,188,226,257,287,324,375,419],
                                          [ 0, 22,28,35,46,59, 75, 90,106,130,154,174,197,220,253,286],
                                          [ 0, 0, 0, 0, 0, 64, 82, 98,117,144,172,197,220,250,290,326]] #Cobre EBT, Cobre DE, Aluminio EBT, Aluminio DE    
    
    IEC_tabla_de_ampacidades_3_cond_PVC =[[18,24,30,38,50, 64, 82, 98,116,143,169,192,217,243,280,316],
                                          [19,24,33,41,54, 70, 92,110,130,162,193,220,246,278,320,359],
                                          [0,18.5,24,30,39,50, 64, 77, 91,112,132,150,169,190,218,247],
                                          [ 0, 0, 0, 0, 0, 53, 69, 83, 99,122,148,169,189,214,250,282]] #Cobre EBT, Cobre DE, Aluminio EBT, Aluminio DE
    
        #CUIDADO QUE LA IEC NO DA TABLA PARA DIRECTAMENTE ENTERRADO, SE USA ENTUBADO
    IEC_tabla_correccion_temp_suelo_20C = [[  10,  15,20,  25,  30,  35,  40,  45,  50,  55,  60],
                                           [ 1.1,1.05, 1,0.95,0.89,0.84,0.77,0.71,0.63,0.55,0.45],
                                           [1.07,1.04, 1,0.96,0.93,0.89,0.85, 0.8,0.76,0.71,0.65]] #Temperatura suelo, Factor para PVC 70, Factor para XLPE 90
    
    IEC_tabla_correccion_K_2ymedio= [[ 0.5, 0.7,  1,    1.5,  2,    2.5,  3   ],
                                     [1.28, 1.2,  1.18, 1.1,  1.05, 1  ,  0.96],
                                     [1.88, 1.62, 1.5,  1.28, 1.12, 1  ,  0.90]] #Resistividad termica, Entubados, Directamente enterrados
        #CUIDADO QUE LA SEPARACION ES DE EXTREMO DE CABLE A EXTREMO DE CABLE
    IEC_tabla_correccion_separacion_DE = [[  2 ,  3 , 4 ,  5 ,  6 , 7  , 8  , 9  , 12 , 16 , 20 ],
                                          [0.75,0.65,0.6,0.55, 0.5,0.45,0.43,0.41,0.36,0.32,0.29],
                                          [0.8 ,0.7, 0.6,0.55,0.55,0.51,0.48,0.46,0.42,0.38,0.35],
                                          [0.85,0.75,0.7,0.65, 0.6,0.59,0.57,0.55,0.51,0.47,0.44],
                                          [0.9, 0.8, 0.75,0.7, 0.7,0.67,0.65,0.63,0.59,0.56,0.53],
                                          [0.9, 0.85,0.8, 0.8, 0.8,0.76,0.75,0.74,0.71,0.68,0.66]] #Nºcircuitos, Pegados, A 1 diametro, A 0.125m, A 0.25m, A 0.5m
    #TODO meter los bajo tubo
    
    if material_conductor == 'Cu':
        if metodo_instalacion == 'Buried in conduits':
            columna_tabla_amp = 0
        elif metodo_instalacion == 'Directly buried':
            columna_tabla_amp = 1
    elif material_conductor == 'Al':
        if metodo_instalacion == 'Buried in conduits':
            columna_tabla_amp = 2
        elif metodo_instalacion == 'Directly buried':
            columna_tabla_amp = 3
            
    indice_amp=IEC_tabla_de_secciones_cable.index(seccion)    
    
    if DCBoxes_o_Inv_String == 'DC Boxes':
        if material_aislante == 'XLPE or EPR (90ºC)':
            ampacidad_inicial = IEC_tabla_de_ampacidades_2_cond_XLPE[columna_tabla_amp][indice_amp]
        elif material_aislante == 'PVC (70ºC)':
            ampacidad_inicial = IEC_tabla_de_ampacidades_2_cond_PVC[columna_tabla_amp][indice_amp]
    if DCBoxes_o_Inv_String == 'String Inverters':
        if material_aislante == 'XLPE or EPR (90ºC)':
            ampacidad_inicial = IEC_tabla_de_ampacidades_3_cond_XLPE[columna_tabla_amp][indice_amp]
        elif material_aislante == 'PVC (70ºC)':
            ampacidad_inicial = IEC_tabla_de_ampacidades_3_cond_PVC[columna_tabla_amp][indice_amp]    

        #definimos factores de correccion interpolando el valor introducido de cada factor en las tablas dadas
        
            #CORRECCION POR TEMP SUELO
    
    if material_aislante == 'XLPE or EPR (90ºC)':
        columna_corr_temp = 1
    elif material_aislante == 'PVC (70ºC)':
        columna_corr_temp = 0
        
    FCpT= np.interp(temperatura_suelo,IEC_tabla_correccion_temp_suelo_20C[0],IEC_tabla_correccion_temp_suelo_20C[columna_corr_temp])
        
            #CORRECCION POR RESISTIVIDAD TERMICA SUELO  
    
    if metodo_instalacion == 'Buried in conduits':
        columna_corr_res = 0
    elif metodo_instalacion == 'Directly buried':
        columna_corr_res = 1
        
    FCpR= np.interp(K_suelo,IEC_tabla_correccion_K_2ymedio[0],IEC_tabla_correccion_K_2ymedio[columna_corr_res])
    
            #CORRECCION POR AGRUPACION DE CIRCUITOS
            #interpolamos el nº de circuitos existente enttre las 5 configuraciones de separacion tabuladas para obtener una lista con valores interpolados en cada una de ellas (podria darse un n de circ no tabulado)
    lista_FCpS=[]
    for i in range(1,len(IEC_tabla_correccion_separacion_DE)):
        lista_FCpS.append(np.interp(n_circuitos, IEC_tabla_correccion_separacion_DE[0], IEC_tabla_correccion_separacion_DE[i]))
    
    if n_circuitos > max(IEC_tabla_correccion_separacion_DE[0]):
        print('La solución para',n_circuitos,'circuitos excede el alcance de la IEC, el ancho de zanja no es válido')        
        
    lista_sep=[0,diametro_cable/1000,0.125,0.25,0.5]
    cont=0
    ampacidad_corr=0
    for FCpS in lista_FCpS:
        amp_ant=ampacidad_corr
        ampacidad_corr = ampacidad_inicial * FCpT * FCpR * FCpS
        if ampacidad_corr > intensidad_circuitos:
            if cont==0 or cont==1: #si la distancia que cumple es pegando o a un diametro lo dejamos asi
                sep=lista_sep[cont]
            else: #si es mayor de eso, afinamos un poco interpolando linealmente sobre las ampacidades virtuales de las 2 distancias limite
                sep = np.interp(intensidad_circuitos, [amp_ant,ampacidad_corr] , [lista_sep[cont-1],lista_sep[cont]])
            break #rompemos el for una vez la ampacidad supera la intensidad de los circuitos
        cont=cont+1
    
    if n_circuitos == 1:
        ancho_zanja = ancho_min
    else:
        ancho_zanja = 0.05+n_circuitos*(diametro_cable/1000*2+sep)-sep+0.05
    
    return ancho_zanja






def calculo_anchos_zanjas_LV(DCBoxes_o_Inv_String, bloque_inicial, n_bloques, prediseño_PB_zanjas_LV_ID, tipos_zanjas, Metodo_ancho_zanjas_LV, entradas_diseño_automatico, entradas_diseño_manual): 
    #A MANO - CYMCAP
    if Metodo_ancho_zanjas_LV == 'Manual':
        #Transferimos los anchos a config y revertimos la tabla de strings al formato de pares previo, incluyendo si es protegida a la derecha del ancho
        config_circ_zanjas_LV = entradas_diseño_manual[0]
        tipos_y_subtipos_unicos = entradas_diseño_manual[1]
        anchos_tipos_LV = entradas_diseño_manual[2]
        info_cada_zanja_LV = entradas_diseño_manual[3]
        
        anchos_en_configuraciones_LV = [[] for _ in range(len(config_circ_zanjas_LV))]
        headers=config_circ_zanjas_LV[0,2:]
        for i in range(1,len(config_circ_zanjas_LV)):
            indice_ancho = tipos_y_subtipos_unicos.index((config_circ_zanjas_LV[i,[0]],config_circ_zanjas_LV[i,[1]]))
            anchos_en_configuraciones_LV[i]=[anchos_tipos_LV[indice_ancho]]
            anchos_en_configuraciones_LV[i].append(str(config_circ_zanjas_LV[i,0]))
            anchos_en_configuraciones_LV[i].append(str(config_circ_zanjas_LV[i,1]))
            anchos_en_configuraciones_LV[i].append(1 if config_circ_zanjas_LV[i,0][-1]=='C' else 0)
            
            
            fila_relacionada = []
            for j_rel, valor in enumerate(config_circ_zanjas_LV[i, 2:]):
                valor_int=int(valor)
                if valor_int != 0:
                    fila_relacionada.append([float(headers[j_rel]), valor_int])
            fila_relacionada.sort(key=lambda x: x[0])
            anchos_en_configuraciones_LV[i].append(fila_relacionada)

        tipos_y_anchos_en_zanjas=[[] for _ in range(len(info_cada_zanja_LV))]
        for i, (coord_prot, comb) in enumerate(info_cada_zanja_LV):
            clave = [int(coord_prot[4]), comb]
            for idx, fila in enumerate(anchos_en_configuraciones_LV[1:]):
                if fila[3:5] == clave:
                    #El esquema de informacion es [ancho, tipo, subtipo, n_circ_LV                        LVAC,   ethernet/RS485,   FO,     coordenadas]
                    tipos_y_anchos_en_zanjas[i]=[fila[0],fila[1],fila[2],sum(circ[1] for circ in fila[4]),  0,          0,          0,     coord_prot[0:4]]
                    
        
        nueva_PB_zanjas_LV_ID = [[0, 0, 0, 0, 0, 0, 0, 0] for _ in range(bloque_inicial)]
        for i in range(bloque_inicial,n_bloques+1):
            nueva_PB_zanjas_LV_ID.append([])
            for zanja in prediseño_PB_zanjas_LV_ID[i]:
                clave = tuple(float(x.item()) if hasattr(x, "item") else float(x) for x in zanja[1:5])
                for idx, fila in enumerate(tipos_y_anchos_en_zanjas):
                    if fila[7] == clave:
                        nueva_PB_zanjas_LV_ID[i].append(fila)
                        
        nueva_zanjas_LV_ID = tipos_y_anchos_en_zanjas
        
        tipos_LV_usados = [] #en el metodo manual se rellenaran los tipos y subtipos unicos a mano mas adelante
        
    else: #AUTOMATICO - SE TIENEN QUE ASUMIR TODOS LOS CIRCUITOS DE LA MISMA SECCION E INTENSIDAD
        ancho_min               = entradas_diseño_automatico[0]
        intensidad_circuitos    = entradas_diseño_automatico[1]
        material_conductor      = entradas_diseño_automatico[2] #puede ser 'Cobre' o 'Aluminio'
        material_aislante       = entradas_diseño_automatico[3] #puede ser 'XLPE o EPR (90ºC)' o 'PVC (70ºC)'
        seccion_conductor       = entradas_diseño_automatico[4] #sqmm #restringir a los valores de la tabla
        diametro_cable          = entradas_diseño_automatico[5] #mm
        metodo_instalacion      = entradas_diseño_automatico[6] #puede ser 'Directamente enterrado' o 'Enterrado bajo tubo'
        temperatura_suelo       = entradas_diseño_automatico[7] #ºC
        K_suelo                 = entradas_diseño_automatico[8] #W/m-K
    
    
    

        #IEC 60364, seria mas correcto usar la 60287 pero la tenemos desactualizada
        if Metodo_ancho_zanjas_LV == 'IEC 60364':
            
            #calculamos el ancho de cada tipo de zanja
            ancho_dis_zanjas_LV=[0]
            for tdz in range(1,len(tipos_zanjas)):
                ancho_dis_zanjas_LV.append(round(calculo_zanja_IEC_60364(DCBoxes_o_Inv_String, tipos_zanjas[tdz],intensidad_circuitos,material_conductor,material_aislante,seccion_conductor,diametro_cable,metodo_instalacion,temperatura_suelo,K_suelo,ancho_min),2))
                
            PB_tipo_y_ancho_LV_ID=[[] for _ in range(bloque_inicial)]                               
            for bloque_zanjas_LV_ID in prediseño_PB_zanjas_LV_ID[bloque_inicial:]:
                tipo_y_ancho_LV_ID =[]
                z=0
                for zanja in bloque_zanjas_LV_ID:
                    for tdz in range(1,len(tipos_zanjas)):
                        if zanja[0] > tipos_zanjas[tdz-1] and zanja[0] <= tipos_zanjas[tdz]: #si el numero de circuitos de la zanja es mayor que el tipo de zanja previo y menor que el activo, está en el activo, se suma, si no, se pasa al siguiente                   
                            tipo_y_ancho_LV_ID.append([
                            float(ancho_dis_zanjas_LV[tdz]), # ancho
                            f'LV{int(tdz)}',                 # tipo
                            '',                              # subtipo (vacío)
                            int(zanja[0]),                   # n_c
                            0,                               # LVAC
                            0,                               # ethernet/RS485
                            0,                               # FO
                            zanja[1:5].tolist()              # coordenadas (formato como en el manual)
                        ])

                            break
                    z=z+1
                PB_tipo_y_ancho_LV_ID.append(tipo_y_ancho_LV_ID)
            
            
        #AS/NZS 3008 , mas detallada que la iec en realidad
    
        
    
    
    
        #Actualizar variables de zanjas tras calculo
        nueva_PB_zanjas_LV_ID = [[] for _ in range(n_bloques+1)]          
        #Creamos una lista de listas en las que se añaden datos en el mismo formato que en el manual
        for i in range(bloque_inicial,n_bloques+1):
            nueva_PB_zanjas_LV_ID[i] = PB_tipo_y_ancho_LV_ID[i]
            
        nueva_zanjas_LV_ID = [fila for item in nueva_PB_zanjas_LV_ID if item is not None for fila in item]  #volvemos a sacar el de toda la planta como lista plana
    
    
        #Obtener todos los tipos únicos usados, se deja le subtipo en blanco porque el metodo automatico no lo contempla
        tipos_LV_usados = list({
            (fila[1], fila[2])
            for bloque in PB_tipo_y_ancho_LV_ID
            for fila in bloque
            if isinstance(fila, (list, tuple)) and len(fila) > 2
        })

        
    return nueva_PB_zanjas_LV_ID, nueva_zanjas_LV_ID, tipos_LV_usados    
    
    
    
    
def trazado_zanjas_AASS(bloque_inicial, n_bloques, pol_AASS_LVAC, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_ethernet, pol_cable_FO, max_p_AASS_LVAC, max_p_AASS_eth):
    trazado_AASS_LVAC = np.full((n_bloques+1,4,max_p_AASS_LVAC,4),np.nan)
    trazado_ethernet = np.full((n_bloques+1,4,max_p_AASS_eth,4),np.nan)
    
    for i in range(bloque_inicial,n_bloques+1):       
        for serv_AC in range(0,4):
            for p in range (0,max_p_AASS_LVAC-1):
                trazado_AASS_LVAC[i,serv_AC,p,0] = pol_AASS_LVAC[i,serv_AC,p,0]
                trazado_AASS_LVAC[i,serv_AC,p,1] = pol_AASS_LVAC[i,serv_AC,p,1]
                trazado_AASS_LVAC[i,serv_AC,p,2] = pol_AASS_LVAC[i,serv_AC,p+1,0]
                trazado_AASS_LVAC[i,serv_AC,p,3] = pol_AASS_LVAC[i,serv_AC,p+1,1]
        
        for serv_eth in range(0,4):
            for p in range (0,max_p_AASS_eth-1):
                trazado_ethernet[i,serv_eth,p,0] = pol_ethernet[i,serv_eth,p,0]
                trazado_ethernet[i,serv_eth,p,1] = pol_ethernet[i,serv_eth,p,1]
                trazado_ethernet[i,serv_eth,p,2] = pol_ethernet[i,serv_eth,p+1,0]
                trazado_ethernet[i,serv_eth,p,3] = pol_ethernet[i,serv_eth,p+1,1] 
            
    #Sacamos arrays planos de coordenadas de cada tipo de SSAA y sus repeticiones para ver el numero de circuitos en cada tramo
    flat_AC = trazado_AASS_LVAC.reshape(-1,4)
    flat_AC_sin_nan =  np.array([tuple(row) for row in flat_AC if not np.isnan(row).any()])
    # flat_AC_sin_nan = cuantizar_segmentos(flat_AC_sin_nan, 0.01) #Ya no hace falta cuantizar porque se ha hecho una agrupacion de puntos por centroides previa a las polilineas
    flat_AC_sin_nan = normalizar_segmentos(flat_AC_sin_nan) #normalizamos para evitar fallos de identidad unica con vertices opuestos
    coord_LVAC_AS, n_LVAC_AS = np.unique(flat_AC_sin_nan, axis=0, return_counts=True)              
    
    flat_ethernet = trazado_ethernet.reshape(-1,4)
    flat_ethernet_sin_nan =  np.array([tuple(row) for row in flat_ethernet if not np.isnan(row).any()])
    flat_ethernet_sin_nan = normalizar_segmentos(flat_ethernet_sin_nan) #normalizamos para evitar fallos de identidad unica con vertices opuestos
    coord_ethernet_AS, n_ethernet_AS = np.unique(flat_ethernet_sin_nan, axis=0, return_counts=True)
    
    
    #De las listas planas de LVAC de cctv y edificios obtenemos los segmentos y los trazados
    segmentos_CCTV_LVAC = []
    segmentos_OyM_supply_LVAC = []
    segmentos_Warehouse_supply_LVAC = []
    
    if pol_CCTV_LVAC:
        for linea_CCTV in pol_CCTV_LVAC:
            puntos = np.array(linea_CCTV).reshape(-1, 2)
            for i in range(len(puntos) - 1):
                segmento = np.concatenate((puntos[i], puntos[i+1]))  # [x0, y0, x1, y1]
                segmentos_CCTV_LVAC.append(segmento)
                    
        trazados_CCTV_LVAC = normalizar_segmentos(np.array(segmentos_CCTV_LVAC)) #normalizamos para evitar fallos de identidad unica con vertices opuestos
        coord_CCTV_LVAC_AS, n_CCTV_LVAC_AS = np.unique(trazados_CCTV_LVAC, axis=0, return_counts=True)   
    else:
        coord_CCTV_LVAC_AS = np.empty((0, 4))
    
    
    if pol_OyM_supply_LVAC:
        for linea_OyM_supply in pol_OyM_supply_LVAC:
            puntos = np.array(linea_OyM_supply).reshape(-1, 2)
            for i in range(len(puntos) - 1):
                segmento = np.concatenate((puntos[i], puntos[i+1]))  # [x0, y0, x1, y1]
                segmentos_OyM_supply_LVAC.append(segmento)
                    
        trazados_OyM_supply_LVAC = normalizar_segmentos(np.array(segmentos_OyM_supply_LVAC)) #normalizamos para evitar fallos de identidad unica con vertices opuestos
        coord_OyM_supply_LVAC_AS, n_OyM_supply_LVAC_AS = np.unique(trazados_OyM_supply_LVAC, axis=0, return_counts=True) 
    else:
        coord_OyM_supply_LVAC_AS = np.empty((0, 4))
    
    
    if pol_Warehouse_supply_LVAC:
        for linea_Warehouse_supply in pol_Warehouse_supply_LVAC:
            puntos = np.array(linea_Warehouse_supply).reshape(-1, 2)
            for i in range(len(puntos) - 1):
                segmento = np.concatenate((puntos[i], puntos[i+1]))  # [x0, y0, x1, y1]
                segmentos_Warehouse_supply_LVAC.append(segmento)
                    
        trazados_Warehouse_supply_LVAC = normalizar_segmentos(np.array(segmentos_Warehouse_supply_LVAC)) #normalizamos para evitar fallos de identidad unica con vertices opuestos
        coord_Warehouse_supply_LVAC_AS, n_Warehouse_supply_LVAC_AS = np.unique(trazados_Warehouse_supply_LVAC, axis=0, return_counts=True)     
    else:
        coord_Warehouse_supply_LVAC_AS = np.empty((0, 4))
        
        
    #De la estructura de FO basada en lineas con listas y np arrays sacamos los segmentos 
    if pol_cable_FO:
        segmentos_FO = []
        for i, linea in enumerate(pol_cable_FO):
            if i==0:
                pass
            else:
                for tramo in linea:
                    puntos = tramo[2]  # ya es (N, 2)
                    if puntos.shape[0] < 2:
                        continue  # saltar si hay menos de 2 puntos
            
                    for k in range(len(puntos) - 1):
                        segmento = np.concatenate((puntos[k], puntos[k + 1]))  # [x0, y0, x1, y1]
                        segmentos_FO.append(segmento)
        
        trazados_FO = normalizar_segmentos(np.array(segmentos_FO)) #normalizamos para evitar fallos de identidad unica con vertices opuestos
        coord_FO_AS, n_FO_AS = np.unique(trazados_FO, axis=0, return_counts=True)
    else:
        coord_FO_AS = np.empty((0, 4))
    
    

    
    #Obtenemos los valores unicos de coordenadas de los trazados, que representarán las coordenadas de las zanjas de SSAA
    coord_combinados_AS = np.vstack((coord_LVAC_AS, coord_ethernet_AS, coord_FO_AS, coord_CCTV_LVAC_AS, coord_OyM_supply_LVAC_AS, coord_Warehouse_supply_LVAC_AS))
    coord_AS = np.unique(coord_combinados_AS, axis=0)
    
    #Creamos otro array con 3 columnas y largo igual a coord_AS para añadir en el los cables de los diferentes servicios en cada zanja AS, como comparte indice con coord_AS podemos buscar la clave y rellenar
    cables_AS_zeros = np.zeros((len(coord_AS),3))
    
    #Rellenamos el numero de cables usando contadores para los indices
    #LVAC de SSAA de bloques

    c_c=-1
    for coords in coord_LVAC_AS:
        c_c=c_c+1
        c_z=-1
        for coords_unicas in coord_AS:
            c_z=c_z+1
            if np.allclose(coords, coords_unicas, rtol=0, atol=1e-3):
                ind = np.where(np.all(coord_AS==coords, axis=1))[0]
                cables_AS_zeros[ind,0] = cables_AS_zeros[ind,0] + n_LVAC_AS[c_c]
                break
            
    #LVAC de CCTV
    if pol_CCTV_LVAC:
        c_c=-1
        for coords in coord_CCTV_LVAC_AS:
            c_c=c_c+1
            c_z=-1
            for coords_unicas in coord_AS:
                c_z=c_z+1
                if np.allclose(coords, coords_unicas, rtol=0, atol=1e-3):
                    ind = np.where(np.all(coord_AS==coords, axis=1))[0]
                    cables_AS_zeros[ind,0] = cables_AS_zeros[ind,0] + n_CCTV_LVAC_AS[c_c]
                
    #LVAC de suministro de OyM
    if pol_OyM_supply_LVAC:
        c_c=-1
        for coords in coord_OyM_supply_LVAC_AS:
            c_c=c_c+1
            c_z=-1
            for coords_unicas in coord_AS:
                c_z=c_z+1
                if np.allclose(coords, coords_unicas, rtol=0, atol=1e-3):
                    ind = np.where(np.all(coord_AS==coords, axis=1))[0]
                    cables_AS_zeros[ind,0] = cables_AS_zeros[ind,0] + n_OyM_supply_LVAC_AS[c_c]
                
    #LVAC de suministro de Warehouse
    if pol_Warehouse_supply_LVAC:
        c_c=-1
        for coords in coord_Warehouse_supply_LVAC_AS:
            c_c=c_c+1
            c_z=-1
            for coords_unicas in coord_AS:
                c_z=c_z+1
                if np.allclose(coords, coords_unicas, rtol=0, atol=1e-3):
                    ind = np.where(np.all(coord_AS==coords, axis=1))[0]
                    cables_AS_zeros[ind,0] = cables_AS_zeros[ind,0] + n_Warehouse_supply_LVAC_AS[c_c] 
                
    #Ethernet
    c_c=-1
    for coords in coord_ethernet_AS:
        c_c=c_c+1
        c_z=-1
        for coords_unicas in coord_AS:
            c_z=c_z+1
            if np.allclose(coords, coords_unicas, rtol=0, atol=1e-3):
                ind = np.where(np.all(coord_AS==coords, axis=1))[0]
                cables_AS_zeros[ind,1] = cables_AS_zeros[ind,1] + n_ethernet_AS[c_c]
    #FO
    if pol_cable_FO:
        c_c=-1
        for coords in coord_FO_AS:
            c_c=c_c+1
            c_z=-1
            for coords_unicas in coord_AS:
                c_z=c_z+1
                if np.allclose(coords, coords_unicas, rtol=0, atol=1e-3):
                    ind = np.where(np.all(coord_AS==coords, axis=1))[0]
                    cables_AS_zeros[ind,2] = cables_AS_zeros[ind,2] + n_FO_AS[c_c]
    
    #Unimos las dos matrices en una para tener [n_LVAC, n_ethernet, n_FO, coord_x0, coord_y0, coord_x1, coord_y1]
    zanjas_AS_ID = np.hstack((cables_AS_zeros,coord_AS))
    
    #Eliminamos las zanjas AS que en realidad representan a un cable de SSAA dentro de una de esas zanjas
    # for zanja_DC in zanjas_DC_ID
        
    
    return zanjas_AS_ID






#------------------HOMOGENEIZAR Y COMBINAR TIPOS DE ZANJAS-----------------------
#En un paso previo se habían sacado todos los vertices comunes de las polilineas, ahora se acaban de sacar los segmentos de dichas polilineas y obtenido unas primeras zanjas con trazados comunes, falta:
    #1)Normalizar, que un segmento que sea igual a otro pero en direccion opuesta (porque un cable entraba y otro salia) no haga que se cuenten dos zanjas
    #2)Combinar tipos de zanjas, se han calculado las zanjas con los trazados individuales, ahora hay que ver si un tipo se superpone a otro porque una zanja comparte varios tipos de cable (por ejemplo MV y AS, que pasará siempre con la fibra, o LV y AS por ethernet o AC)

            
    
def combinar_todas_las_zanjas(bloque_inicial, n_bloques, PB_zanjas_LV_ID, zanjas_LV_ID, zanjas_AS_ID):
    
    #Normalizamos poniendo en todas las coordenadas de zanjas el punto inicial como el mas al oeste y si coinciden (vertical) el mas al sur, siempre el menor
    
    def normalizar_zanja(coords):
        p1 = coords[:2]
        p2 = coords[2:]
        if tuple(p1) <= tuple(p2):  # orden normal
            return np.concatenate([p1, p2])
        else:  # invertir
            return np.concatenate([p2, p1])
        
    # for i in range(bloque_inicial, n_bloques+1):
    #     for z, zanja in enumerate(PB_zanjas_LV_ID):
    #         PB_zanjas_LV_ID[i][z][7] = normalizar_zanja(zanja[7])

    for z, zanja in enumerate(zanjas_LV_ID):
        zanjas_LV_ID[z][7] = normalizar_zanja(zanja[7])
            
    for z, zanja in enumerate(zanjas_AS_ID):
        zanjas_AS_ID[z,3:7] = normalizar_zanja(zanja[3:7])     
    
    
    #Ahora mismo las unicas conmbinaciones permitidas en los diseños de GRS son AS con zanjas LV o MV
    zanjas_AS_a_eliminar=[]
        #Integrar AS en LV
    for z_lv, zanja_lv in enumerate(zanjas_LV_ID):
        for z_as, zanja_as in enumerate(zanjas_AS_ID):
            if np.allclose(zanja_lv[7]==zanja_as[3:7]):
                #Mostramos los circuitos en la zanja LV
                zanjas_LV_ID[z_lv][4] = int(zanja_as[0])
                zanjas_LV_ID[z_lv][5] = int(zanja_as[1])
                zanjas_LV_ID[z_lv][6] = int(zanja_as[2])
                
                #Guardamos el indice de las zanjas AS a eliminar
                zanjas_AS_a_eliminar.append(z_as)
    
    
    #Borrar zanjas AS integradas
    zanjas_AS_ID_sin_LV = np.delete(zanjas_AS_ID, zanjas_AS_a_eliminar, axis=0)
        
    return zanjas_LV_ID, zanjas_AS_ID_sin_LV
                    




