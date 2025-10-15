# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 07:19:07 2025

@author: mlopez
"""

import time
import numpy as np



#Conexiones previas con AUTOCAD

def conexion_con_CAD_para_dibujar(referencia):
    from pyautocad import Autocad
    
    try:
        acad = Autocad(create_if_not_exists=False)
        docs = acad.app.Documents

        # Buscar el documento con el nombre de referencia
        for doc in docs:
            if doc.Name.lower() == referencia.lower():
                doc.Activate()  # Activar el dibujo
                time.sleep(0.3)
                doc.SetVariable("INSUNITS", 6) #poner las unidades en m
                time.sleep(0.1)
                acad = Autocad(create_if_not_exists=False)  # Reconectar con el activo
                return acad

        # Si no se encontró, crear uno nuevo
        doc = docs.Add()  # Crea un nuevo dibujo
        time.sleep(0.3)
        doc.SetVariable("INSUNITS", 6) #poner las unidades en m
        time.sleep(0.1)
        acad = Autocad(create_if_not_exists=False) #Conectar con el creado
        
        return acad
    
    except Exception as e:
        print(f"Error al conectar con AutoCAD: {e}")
        return None



def conexion_con_CAD_para_leer(referencia):
    from pyautocad import Autocad

    try:
        # Intentar conectar con AutoCAD
        acad = Autocad(create_if_not_exists=False)
        time.sleep(0.3)
        docs = acad.app.Documents

        # Buscar el documento con el nombre de referencia
        for doc in docs:
            if doc.Name.lower() == referencia.lower():
                doc.Activate()  # Activar el dibujo con ese nombre
                time.sleep(0.3)
                return Autocad(create_if_not_exists=False)  # Reconectar con el activo

        # Si no se encuentra el documento con ese nombre, usar el activo
        return acad

    except Exception as e:
        print(f"Error al conectar con AutoCAD: {e}")
        return None



#-----------------------------------------LEER LAYOUT INICIAL--------------------------------------------

#Funciones para identificar curvas en polilineas (se va a usar en los caminos) y densificarlas cada cierto paso para evitar cortes en recta directos
def densificar_polilinea(obj, paso=5.0):
    try:
        coords_raw = obj.Coordinates
        num_vertices = int(len(coords_raw) / 2)
    except Exception as e:
        print(f"No se pudo leer coordenadas: {e}")
        return []

    coords_planas = []

    for i in range(num_vertices - 1):
        pt1 = np.array([coords_raw[2*i], coords_raw[2*i+1]])
        pt2 = np.array([coords_raw[2*(i+1)], coords_raw[2*(i+1)+1]])
        try:
            bulge = obj.GetBulge(i)
        except:
            bulge = 0


        if bulge == 0:
            coords_planas.extend(pt1.tolist())
        else:
            puntos = interpolar_arco(pt1, pt2, bulge, paso)
            for pt in puntos[:-1]:  # evita duplicar pt2
                coords_planas.extend(pt.tolist())

    # Añadir el último punto
    coords_planas.extend([coords_raw[-2], coords_raw[-1]])

    return coords_planas


def interpolar_arco(p1, p2, bulge, paso=1.0):
    p1 = np.array(p1[:2], dtype=float)
    p2 = np.array(p2[:2], dtype=float)

    if abs(bulge) < 1e-5:
        return np.array([p1, p2])

    # Vector entre puntos
    chord_vec = p2 - p1
    chord = np.linalg.norm(chord_vec)

    if chord == 0:
        return np.array([p1])

    # Ángulo del arco
    theta = 4 * np.arctan(abs(bulge))

    # Radio del arco
    radius = chord / (2 * np.sin(theta / 2))

    # Dirección perpendicular para hallar el centro
    mid = (p1 + p2) / 2
    direction = chord_vec / chord
    perp = np.array([-direction[1], direction[0]])

    # Distancia desde el punto medio al centro
    h = radius * np.cos(theta / 2)
    offset = h if bulge > 0 else -h
    center = mid + perp * offset

    # Ángulos inicial y final
    theta1 = np.arctan2(p1[1] - center[1], p1[0] - center[0])
    theta2 = np.arctan2(p2[1] - center[1], p2[0] - center[0])

    # Asegurar dirección correcta (CCW o CW)
    if bulge > 0 and theta2 < theta1:
        theta2 += 2 * np.pi
    elif bulge < 0 and theta1 < theta2:
        theta1 += 2 * np.pi

    arc_angle = abs(theta2 - theta1)
    arc_length = radius * arc_angle
    if arc_length == 0 or np.isnan(arc_length):
        return np.array([p1, p2])

    n_steps = max(int(arc_length / paso), 1)
    thetas = np.linspace(theta1, theta2, n_steps + 1)
    x = center[0] + radius * np.cos(thetas)
    y = center[1] + radius * np.sin(thetas)
    puntos = np.stack([x, y], axis=1)

    # Forzar extremos
    puntos[0] = p1
    puntos[-1] = p2

    return puntos





#Funcion para leer el layout

def CAD_read_layout(acad):
    from shapely.geometry import LineString, Point
    import numpy as np
    
    trackers_extraidos = []
    PCS_DC_Inputs = []
    PCS_AASS_Inputs = []
    PCS_MV_Inputs = []
    Comboxes = []
    Tracknets = []
    TBoxes = []
    AWS = []
    
    coord_CCTV = []
    polilineas_caminos = []
    pol_guia_MV_FO = []
    pol_guia_MV_FO_refinadas = []
    pol_envolventes_PAT = []
    
    coord_SS_LVAC = None
    coord_OyM_LVAC = None
    coord_Warehouse_LVAC = None
    coord_MV_Switching_Room = [[None, None]]
    ind_Switching_Room=[0]
    coord_SS_Control_Room = None
    coord_OyM_Control_Room = None
    
    time.sleep(0.1) #le damos un tiempo para que autocad no se autobloquee
    
    for obj in acad.iter_objects_fast("AcDbBlockReference"):
        nombre_extraido = obj.EffectiveName
        
        if nombre_extraido[3:] in ['Tracker-S','Tracker-M','Tracker-L','Tracker-XL', 'Weather Station'] or nombre_extraido[:17]=='MV Switching Room' or nombre_extraido in ['PCS-DC Inputs', 'PCS-LV Inputs', 'PCS-AASS Inputs', 'PCS-MV Inputs', 'COMBOX', 'TRACKNET', 'T-BOX', 'CCTV', 'Substation LVAC Board','O&M LVAC Board', 'Warehouse LVAC Board', 'Substation Control Room', 'O&M Control Room']:
            punto_insercion = obj.InsertionPoint  # Esto es una tupla (x, y, z)
            nombre_capa = obj.Layer # Será 0_Block_XX, por lo que se descartan los 8 primeros caracteres, cuidado la base 0
            if nombre_capa[:8] == '0_Block_':
                bloque = int(nombre_capa[8:])
            
            #Leer trackers - Se crea una lista para guardar todos los trackers [Bloque , Tipo (S,M,L,XL), P.Insercion X, P.Insercion Y, P.Insercion Z]
            if nombre_extraido[3:]== 'Tracker-S':
                trackers_extraidos.append([bloque,'S',punto_insercion[0],punto_insercion[1]]) #de momento lo dejamos en 2D
            elif nombre_extraido[3:]== 'Tracker-M':
                trackers_extraidos.append([bloque,'M',punto_insercion[0],punto_insercion[1]]) #de momento lo dejamos en 2D
            elif nombre_extraido[3:]== 'Tracker-L':
                trackers_extraidos.append([bloque,'L',punto_insercion[0],punto_insercion[1]]) #de momento lo dejamos en 2D
            elif nombre_extraido[3:]== 'Tracker-XL':
                trackers_extraidos.append([bloque,'XL',punto_insercion[0],punto_insercion[1]]) #de momento lo dejamos en 2D
            
    
            #Leer PCS - Se crea una lista para guardar todas las entradas [Bloque , P.Insercion X, P.Insercion Y, P.Insercion Z]
            elif nombre_extraido == 'PCS-DC Inputs' or nombre_extraido == 'PCS-LV Inputs':
                PCS_DC_Inputs.append([bloque,punto_insercion[0],punto_insercion[1]]) #de momento lo dejamos en 2D
            elif nombre_extraido == 'PCS-AASS Inputs':
                PCS_AASS_Inputs.append([bloque,punto_insercion[0],punto_insercion[1]]) #de momento lo dejamos en 2D            
            elif nombre_extraido == 'PCS-MV Inputs':
                PCS_MV_Inputs.append([bloque,punto_insercion[0],punto_insercion[1]]) #de momento lo dejamos en 2D      
    
            #Leer cuadros LVAC de O&M, Warehouse y Subestacion, además de las control rooms para las fibras y ethernet
            elif nombre_extraido == 'Substation LVAC Board':
                coord_SS_LVAC = [punto_insercion[0],punto_insercion[1]]
            elif nombre_extraido == 'O&M LVAC Board':
                coord_OyM_LVAC = [punto_insercion[0],punto_insercion[1]]
            elif nombre_extraido == 'Warehouse LVAC Board':
                coord_Warehouse_LVAC = [punto_insercion[0],punto_insercion[1]]
                
            elif nombre_extraido[:17] == 'MV Switching Room':
                ind_Switching_Room.append(int(nombre_extraido[18:]))
                coord_MV_Switching_Room.append([punto_insercion[0],punto_insercion[1]]) 
                #Reordenar
                pares = list(zip(ind_Switching_Room, coord_MV_Switching_Room))
                pares_ordenados = sorted(pares, key=lambda x: x[0])
                coord_MV_Switching_Room = [coord for _, coord in pares_ordenados]
                
            elif nombre_extraido == 'Substation Control Room':
                coord_SS_Control_Room = [punto_insercion[0],punto_insercion[1]]
            elif nombre_extraido == 'O&M Control Room':
                coord_OyM_Control_Room = [punto_insercion[0],punto_insercion[1]]
                
            #Leer sistemas auxiliares
            elif nombre_extraido == 'COMBOX':
                Comboxes.append([bloque,punto_insercion[0],punto_insercion[1]]) #de momento lo dejamos en 2D
            elif nombre_extraido == 'TRACKNET':
                Tracknets.append([bloque,punto_insercion[0],punto_insercion[1]]) #de momento lo dejamos en 2D
            elif nombre_extraido == 'T-BOX':
                TBoxes.append([bloque,punto_insercion[0],punto_insercion[1]]) #de momento lo dejamos en 2D
            elif nombre_extraido[3:] == 'Weather Station':
                AWS.append([bloque,punto_insercion[0],punto_insercion[1]]) #de momento lo dejamos en 2D                 
      
            #Lee sistema de seguridad
            elif nombre_extraido == 'CCTV':
                if nombre_capa == 'CCTV_O&M': 
                    coord_CCTV.append(['O&M',punto_insercion[0],punto_insercion[1]])
                elif nombre_capa == 'CCTV_Substation':
                    coord_CCTV.append(['SS',punto_insercion[0],punto_insercion[1]])
                else:
                    coord_CCTV.append([bloque,punto_insercion[0],punto_insercion[1]])
                    
                    
    #Leer elementos de interés guardados como polilineas          
    for obj in acad.iter_objects_fast('Polyline'):
        if obj.Layer == '0_Road':
            if obj.ObjectName == "AcDbPolyline":
                coords = densificar_polilinea(obj, paso=5.0)
                if coords:
                    polilineas_caminos.append(coords) #hacemos una lista de tuples planas [x0,y0,x1,y1,x2,y2...]
            else:
                # Polilínea no compatible: descartamos o procesamos como simple
                print(f"Omitida polilínea no estándar: {obj.ObjectName}")
    
    
            
        #Leer pasillos de MV o FO
        elif obj.Layer == '0_MV_or_FO_corridor':   #DEBE CUMPLIR CONDICIONES PARA EL GRAFO, SEGMENTOS CON INICIO Y FINAL ENLAZADOS
            if obj.ObjectName == "AcDbPolyline":
                coords = densificar_polilinea(obj, paso=5.0)
                if coords:
                    pol_guia_MV_FO.append(coords) #En la referencia de entrada deberá de hacerse una copia de los caminos a esta capa y/o añadir las rutas de conexion adicionales por las que iran las zanjas
            else:
                # Polilínea no compatible: descartamos o procesamos como simple
                print(f"Omitida polilínea no estándar: {obj.ObjectName}")
                
        #Leer envolventes de PCS y edificios para tirar anillos de PAT
        elif obj.Layer == 'Enclosure':
            pol_envolventes_PAT.append(obj.Coordinates)  #hacemos una lista de tuples planas [x0,y0,x1,y1,x2,y2...]
            



            
        
    info_ausente = []
    # Preparar datos en formato que lea el algoritmo
    
    # Datos de bloques
    bloques = np.array([fila[0] for fila in trackers_extraidos])
    bloque_inicial = np.min(bloques)
    n_bloques = np.max(bloques)
    bloques_unicos , rep_bloq = np.unique(bloques, return_counts=True)
    max_n_tracker_por_bloque =  np.max(rep_bloq)


    #Datos de PCS y SSAA, está limitado a 1 por bloque  
    coord_PCS_DC_inputs = np.full((n_bloques+1, 2), np.nan)
    coord_PCS_AASS_inputs = np.copy(coord_PCS_DC_inputs)
    coord_PCS_MV_inputs = np.copy(coord_PCS_DC_inputs)
    coord_Comboxes = np.copy(coord_PCS_DC_inputs)
    coord_Tracknets = np.copy(coord_PCS_DC_inputs)
    coord_TBoxes = np.copy(coord_PCS_DC_inputs)
    coord_AWS = np.copy(coord_PCS_DC_inputs)

    
    
    for i in range(bloque_inicial, n_bloques+1):
        try:
            ind = next(idx for idx, fila in enumerate(PCS_DC_Inputs) if fila[0] == i)
            coord_PCS_DC_inputs[i, 0] = PCS_DC_Inputs[ind][1]
            coord_PCS_DC_inputs[i, 1] = PCS_DC_Inputs[ind][2]
        except StopIteration:
            pass
    
        try:
            ind = next(idx for idx, fila in enumerate(PCS_AASS_Inputs) if fila[0] == i)
            coord_PCS_AASS_inputs[i, 0] = PCS_AASS_Inputs[ind][1]
            coord_PCS_AASS_inputs[i, 1] = PCS_AASS_Inputs[ind][2]
        except StopIteration:
            pass
    
        try:
            ind = next(idx for idx, fila in enumerate(PCS_MV_Inputs) if fila[0] == i)
            coord_PCS_MV_inputs[i, 0] = PCS_MV_Inputs[ind][1]
            coord_PCS_MV_inputs[i, 1] = PCS_MV_Inputs[ind][2]
        except StopIteration:
            pass
    
        try:
            ind = next(idx for idx, fila in enumerate(Comboxes) if fila[0] == i)
            coord_Comboxes[i, 0] = Comboxes[ind][1]
            coord_Comboxes[i, 1] = Comboxes[ind][2]
        except StopIteration:
            pass
    
        try:
            ind = next(idx for idx, fila in enumerate(Tracknets) if fila[0] == i)
            coord_Tracknets[i, 0] = Tracknets[ind][1]
            coord_Tracknets[i, 1] = Tracknets[ind][2]
        except StopIteration:
            pass
    
        try:
            ind = next(idx for idx, fila in enumerate(TBoxes) if fila[0] == i)
            coord_TBoxes[i, 0] = TBoxes[ind][1]
            coord_TBoxes[i, 1] = TBoxes[ind][2]
        except StopIteration:
            pass

        try:
            ind = next(idx for idx, fila in enumerate(AWS) if fila[0] == i)
            coord_AWS[i, 0] = AWS[ind][1]
            coord_AWS[i, 1] = AWS[ind][2]
        except StopIteration:
            pass
        
    #El CCTV se pasa como lista porque puede alimentarse desde edificios y haber más de uno desde una misma fuente
    def clave(sublista):
        primero = sublista[0]
        if isinstance(primero, (int, float)):
            return (0, primero)
        else:  # asumimos que lo demás son strings
            return (1, str(primero).lower())
    try:
        coord_CCTV_ordenadas = sorted(coord_CCTV, key=clave)
    except:
        pass
    
    
    if bloques.size == 0:
        info_ausente.append('Trackers')
    if PCS_DC_Inputs == []:
        info_ausente.append('PCS DC Cabinet')
    if PCS_AASS_Inputs == []:
        info_ausente.append('PCS AASS Cabinet')
    if PCS_MV_Inputs == []:
        info_ausente.append('PCS MV Cabinet')
    if Comboxes == []:
        info_ausente.append('Comboxes')
    if Tracknets == []:
        info_ausente.append('Tracknets')
    if TBoxes == []:
        info_ausente.append('TBoxes')
    if AWS == []:
        info_ausente.append('AWS')
    if coord_CCTV == []:
        info_ausente.append('CCTV')
    if coord_SS_LVAC == None:
        info_ausente.append('SS AC Board')
    if coord_OyM_LVAC == None:
        info_ausente.append('O&M AC Board')
    if coord_Warehouse_LVAC == None:
        info_ausente.append('Warehouse AC Board')
    if coord_MV_Switching_Room == []:
        info_ausente.append('MV Switching Room')
    if coord_SS_Control_Room == None:
        info_ausente.append('SS Control Room')
    if coord_OyM_Control_Room == None:
        info_ausente.append('O&M Control Room')        
    if polilineas_caminos == []:
        info_ausente.append('Roads')
    if pol_envolventes_PAT == []:
        info_ausente.append('Enclosures')
    
    #Añadimos a las polilineas de caminos los vertices de inicio y destino en cada bloque que se usan en MV y FO.
    if pol_guia_MV_FO: #si hay info de caminos/pasillos
        # --- Convertir a formato [[x, y], ...] ---
        for linea in pol_guia_MV_FO:
            if all(isinstance(p, (float, int)) for p in linea):  # lista plana
                if len(linea) % 2 != 0:
                    raise ValueError("Línea con número impar de coordenadas (x, y)")
                puntos = [[linea[i], linea[i+1]] for i in range(0, len(linea), 2)]
            else:  # ya está en formato [[x, y], ...]
                puntos = [list(p) for p in linea]
            pol_guia_MV_FO_refinadas.append(puntos)

    
        # --- Extraer puntos válidos de interés ---
        puntos_interes = np.vstack([punto for array in (coord_Comboxes, coord_PCS_MV_inputs) if array is not None for punto in array if not np.isnan(punto).any()])
    
        # --- Proyectar cada punto sobre la mejor línea y segmento ---
        for punto in puntos_interes:
            punto_geom = Point(punto)
            min_dist = float('inf')
            mejor_linea = -1
            mejor_seg = -1
            proj_coords = None
    
            for i, linea in enumerate(pol_guia_MV_FO_refinadas):
                for j in range(len(linea) - 1):
                    try:
                        seg = LineString([linea[j], linea[j+1]])
                        proj = seg.interpolate(seg.project(punto_geom))
                        dist = proj.distance(punto_geom)
                    except Exception as e:
                        print(f"Error en segmento {j} de línea {i}: {e}")
                        continue
    
                    if dist < min_dist:
                        min_dist = dist
                        mejor_linea = i
                        mejor_seg = j
                        proj_coords = list(proj.coords[0])
    
            # Insertar el punto proyectado
            if mejor_linea != -1 and proj_coords:
                proj_coords = list(np.round(proj_coords, 5))
                linea = pol_guia_MV_FO_refinadas[mejor_linea]
                pol_guia_MV_FO_refinadas[mejor_linea] = (linea[:mejor_seg + 1] + [proj_coords] + linea[mejor_seg + 1:])
    
        # ---Desmembrar polilineas en uniones T sin vertices definidos o con vertices comunes en tramos individuales (las T con 2 polilineas se ponen como 3) ---       
        TOL = 1.0  # metros
        
        # --- 1) Insertar puntos de cruce que no existan como vértices ---
        for i_punto_linea, linea in enumerate(pol_guia_MV_FO_refinadas):
            for j_punto, p in enumerate(linea):
                p_geom = Point(p)
        
                for i_linea2, linea2 in enumerate(pol_guia_MV_FO_refinadas):
                    if i_punto_linea == i_linea2:
                        continue
        
                    for idx in range(len(linea2) - 1):
                        seg = LineString([linea2[idx], linea2[idx+1]])
                        # proyección del punto sobre el segmento
                        proj = seg.interpolate(seg.project(p_geom))
                        dist = proj.distance(p_geom)
        
                        if dist <= TOL and seg.distance(proj) < 1e-9:
                            # Chequear si la proyección ya está en la línea2
                            if not any(Point(v).distance(proj) < 1e-9 for v in linea2):
                                # Insertar en linea2
                                linea2.insert(idx+1, list(np.round(proj.coords[0], 5)))
        
        # --- 2) Detectar vértices comunes y partir ---
        nuevas_lineas = []
        partir_indices = {i: set() for i in range(len(pol_guia_MV_FO_refinadas))}
        
        for i1, linea1 in enumerate(pol_guia_MV_FO_refinadas):
            for j1, p1 in enumerate(linea1):
                P1 = Point(p1)
                for i2, linea2 in enumerate(pol_guia_MV_FO_refinadas):
                    if i1 >= i2:
                        continue
                    for j2, p2 in enumerate(linea2):
                        if P1.distance(Point(p2)) <= TOL:
                            if 0 < j1 < len(linea1)-1:
                                partir_indices[i1].add(j1)
                            if 0 < j2 < len(linea2)-1:
                                partir_indices[i2].add(j2)
        
        for i, linea in enumerate(pol_guia_MV_FO_refinadas):
            if not partir_indices[i]:
                nuevas_lineas.append(linea)
                continue
            cortes = sorted(partir_indices[i])
            ini = 0
            for c in cortes:
                nuevas_lineas.append(linea[ini:c+1])
                ini = c
            nuevas_lineas.append(linea[ini:])
        
        pol_guia_MV_FO_refinadas = nuevas_lineas

        
    
    salidas_PCS = [coord_PCS_DC_inputs, coord_PCS_AASS_inputs, coord_PCS_MV_inputs]
    salidas_SSAA = [coord_Comboxes, coord_Tracknets, coord_TBoxes, coord_AWS, coord_CCTV_ordenadas]
    salidas_facilities = [coord_SS_LVAC, coord_OyM_LVAC, coord_Warehouse_LVAC, coord_MV_Switching_Room, coord_SS_Control_Room, coord_OyM_Control_Room]
    
    return bloque_inicial, n_bloques, max_n_tracker_por_bloque, trackers_extraidos, salidas_PCS, salidas_SSAA, salidas_facilities, polilineas_caminos, pol_guia_MV_FO_refinadas, pol_envolventes_PAT, info_ausente





#----------------DIBUJAR POLILINEAS DE CAMINOS Y PASILLOS MV/FO PARA REVISION DE GRAFO--------------

def dibujar_pol_grafo(acad, pol_guia_MV_FO):
    from pyautocad import APoint, aDouble
    
    grafo_caminos = acad.doc.Layers.Add('Roads graph')
    grafo_caminos.Color = 7
    
    def dibujar_FO(coordenadas_FO): 
        # Filtrar puntos válidos (coordenadas no NaN)
        coordenadas_limpias = coordenadas_FO[~np.isnan(coordenadas_FO).any(axis=1)]
        
        # Definir los puntos
        points = [APoint(x, y) for x, y in coordenadas_limpias]
    
        # Dibujar polilínea
        points_double = aDouble(*[coord for point in points for coord in (point.x, point.y, 0)])
        polilinea_arr = acad.model.AddPolyline(points_double)
        polilinea_arr.ConstantWidth=0.05
        polilinea_arr.Layer = 'Roads graph' 


    for tramo in pol_guia_MV_FO:
        dibujar_FO(np.array(tramo).reshape(-1,2))

    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents














#----------------DIBUJAR CONFIGURACION DE BAJA TENSION --------------


#CASO DCBOXES (ENVOLVENTES DE FILAS ASOCIADAS A CAJAS)


def CAD_draw_config_LV(acad, all_blocks, single_block, bloque_inicial, n_bloques, max_b, max_c, max_f_str_b, max_c_block, filas_en_cajas, cajas_fisicas, contorno_bandas_inf, contorno_bandas_sup, equi_ibfs, equi_ibc, h_modulo):
    from pyautocad import APoint, aDouble
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    # Creamos las capas asociadas
    capas_de_envolventes=[]
    for caj in range(1,max_c_block+1):
        capa_envolvente = acad.doc.Layers.Add(f'R-DCB {caj}')
        capas_de_envolventes.append(f'R-DCB {caj}')
        if caj % 3 == 0:
            capa_envolvente.color = 140
        elif caj % 2 == 0:
            capa_envolvente.color = 11   
        else:
            capa_envolvente.color = 41
            
    # Definimos la funcion de dibujo de pyautocad           
    def dibujar_envolventes_filas_cajas(punto_N, punto_S, h_modulo, caja):
        p1 = APoint(punto_N[0]-h_modulo/2-0.5,punto_N[1]+0.1)
        p2 = APoint(punto_N[0]+h_modulo/2+0.5,punto_N[1]+0.1)
        p3 = APoint(punto_S[0]+h_modulo/2+0.5,punto_S[1]-0.1)
        p4 = APoint(punto_S[0]-h_modulo/2-0.5,punto_S[1]-0.1)
        
        points = aDouble(p1.x, p1.y, 0, p2.x, p2.y, 0, p3.x, p3.y, 0, p4.x, p4.y, 0,)
        envolvente = acad.model.AddPolyline(points)
        envolvente.Closed = True
        envolvente.ConstantWidth = 0.1
        envolvente.Layer = f'R-DCB {caja}'

    #Dibujamos con los valores recibidos
    if all_blocks==True:
        for i in range(bloque_inicial,n_bloques+1):
            for b in range(0,max_b):
                if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
                    for f in range (0,max_f_str_b):      
                        if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía
                            punto_N = contorno_bandas_sup[i,b,f]                        
                            punto_S = contorno_bandas_inf[i,b,f]
                            caja = int(equi_ibfs[i,b,f,0,2])
                            dibujar_envolventes_filas_cajas(punto_N, punto_S, h_modulo, caja)
    else: #solo un bloque
        i=single_block
        for b in range(0,max_b):
            if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
                for f in range (0,max_f_str_b):      
                    if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía
                        punto_N = contorno_bandas_sup[i,b,f]                        
                        punto_S = contorno_bandas_inf[i,b,f]
                        caja = int(equi_ibfs[i,b,f,0,2])
                        dibujar_envolventes_filas_cajas(punto_N, punto_S, h_modulo, caja)
    
    #Incluimos el numero de strings en cada caja asociada
    def insertar_texto_strings_per_box(texto, punto_referencia, caja):
        x = punto_referencia[0]
        y = punto_referencia[1]
        insercion_texto = APoint(x+1, y) #desplazamos la X un metro para que no choque con la forma del inversor
        texto_n_strings = acad.model.AddText(texto, insercion_texto, 1)  # 1 es el tamaño del texto 
        texto_n_strings.Layer = f'R-DCB {caja}'
    
    if all_blocks==True:    
        for i in range(bloque_inicial,n_bloques+1):
            for b in range(0,max_b):
                if ~np.isnan(cajas_fisicas[i,b,0,0]): #si la banda no está vacía       
                    for c in range (0,max_c):  
                        if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la caja no está vacía
                            caja = int(equi_ibc[i,b,c,2])
                            insertar_texto_strings_per_box(cajas_fisicas[i,b,c,0], cajas_fisicas[i,b,c,[1,2]], caja)
    else: #solo un bloque
        i=single_block
        for b in range(0,max_b):
            if ~np.isnan(cajas_fisicas[i,b,0,0]): #si la banda no está vacía       
                for c in range (0,max_c):  
                    if ~np.isnan(cajas_fisicas[i,b,c,0]): #si la caja no está vacía
                        caja = int(equi_ibc[i,b,c,2])
                        insertar_texto_strings_per_box(cajas_fisicas[i,b,c,0], cajas_fisicas[i,b,c,[1,2]], caja)

                    
    #centramos la ventana de AutoCAD en el dibujo                    
    doc = acad.app.ActiveDocument                    
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents                    
    return capas_de_envolventes







# CASO INVERSORES DE STRING (ENVOLVENTES DE STRINGS ASOCIADAS A INVERSORES)


def CAD_draw_config_LV_inv_string(acad, all_blocks, single_block, strings_ID, String_Inverters_ID, bloque_inicial, n_bloques, max_inv_block, max_str_pinv, h_modulo, dos_inv_por_bloque):
    from pyautocad import APoint, aDouble
    import time

    time.sleep(0.3)

    capas_de_envolventes = []
    colores = [130, 11, 30, 100, 200, 5]
    capa_flechas_orientacion= acad.doc.Layers.Add('Ori-Str.')
    capa_flechas_orientacion.color = 7
    
    if dos_inv_por_bloque:
        for inv in range(1, max_inv_block+1):
            for board in [1,2]:
                capa_envolvente = acad.doc.Layers.Add(f'S-INV {board}.{inv}')
                capas_de_envolventes.append(f'S-INV {board}.{inv}')
                color_index = colores[(inv - 1) % len(colores)]
                capa_envolvente.color = color_index
    else:
        for inv in range(1, max_inv_block+1):
            capa_envolvente = acad.doc.Layers.Add(f'S-INV {inv}')
            capas_de_envolventes.append(f'S-INV {inv}')
            color_index = colores[(inv - 1) % len(colores)]
            capa_envolvente.color = color_index
                
            
    def dibujar_envolvente_y_orientacion_string(x, y_fin, y_inicio, h_modulo, inv, y_medio, s_id_global):
        #envolvente
        alto = 0
        if y_inicio > y_fin:
            y1 = y_inicio
            y2 = y_fin + alto
        else:
            y1 = y_inicio
            y2 = y_fin - alto
            

        p1 = APoint(x - h_modulo/2 - 0.5, y1)
        p2 = APoint(x + h_modulo/2 + 0.5, y1)
        p3 = APoint(x + h_modulo/2 + 0.5, y2)
        p4 = APoint(x - h_modulo/2 - 0.5, y2)

        points = aDouble(p1.x, p1.y, 0, p2.x, p2.y, 0, p3.x, p3.y, 0, p4.x, p4.y, 0)
        envolvente = acad.model.AddPolyline(points)
        envolvente.Closed = True
        envolvente.ConstantWidth = 0.1
        if dos_inv_por_bloque:
            envolvente.Layer = f'S-INV {board}.{inv}'
        else:
            envolvente.Layer = f'S-INV {inv}'

        #orientacion    
        p_ini = APoint(x, y_medio)
        p_fin = APoint(x, y_medio + (y_fin-y_medio)/2)
        p_izq_fl = APoint(x-h_modulo/3, y_medio + (y_fin-y_medio)/2.2)
        p_der_fl = APoint(x+h_modulo/3, y_medio + (y_fin-y_medio)/2.2)
        
        points = aDouble(p_ini.x, p_ini.y, 0, p_fin.x, p_fin.y, 0, p_izq_fl.x, p_izq_fl.y, 0, p_fin.x, p_fin.y, 0, p_der_fl.x, p_der_fl.y, 0)
        flecha_ori = acad.model.AddPolyline(points)        
        flecha_ori.ConstantWidth = 0.1
        flecha_ori.Layer = 'Ori-Str.'
        insercion_texto = APoint(x+h_modulo/3, y_medio + (y_fin-y_medio)/3)
        texto_n_strings = acad.model.AddText(str(s_id_global), insercion_texto, 0.3)
        if dos_inv_por_bloque:
            texto_n_strings.Layer = f'S-INV {board}.{inv}'
        else:
            texto_n_strings.Layer = f'S-INV {inv}'
        

    def insertar_texto_strings_per_inv(texto, x, y, inv):
        insercion_texto = APoint(x+1, y)
        texto_n_strings = acad.model.AddText(texto, insercion_texto, 1)
        if dos_inv_por_bloque:
            texto_n_strings.Layer = f'S-INV {board}.{inv}'
        else:
            texto_n_strings.Layer = f'S-INV {inv}'

    # Evaluación central segura
    def no_es_nan(valor):
        return valor is not None and not (valor != valor)

    if all_blocks:
        for i in range(bloque_inicial, n_bloques+1):
            for board in range(0,3):
                #No se evalua si el primer inversor es nan porque si la numeracion es continua los inversores del board 1 aparecen como nan en el board 2
                for inv in range(1, max_inv_block+1):
                    if no_es_nan(strings_ID[i, board, inv, 1, 0]):
                        for s in range(1, max_str_pinv+1):
                            if no_es_nan(strings_ID[i, board, inv, s, 0]):
                                x = strings_ID[i, board, inv, s, 1]
                                y_inicio = strings_ID[i, board, inv, s, 2]
                                y_fin = strings_ID[i, board, inv, s, 3]
                                s_id_global = strings_ID[i, board, inv, s, 4]
                                y_medio = strings_ID[i, board, inv, s, 5]
                                dibujar_envolvente_y_orientacion_string(x, y_fin, y_inicio, h_modulo, inv, y_medio, s_id_global)     
                                
                        insertar_texto_strings_per_inv(String_Inverters_ID[i, board, inv, 3], float(String_Inverters_ID[i, board, inv, 1]), float(String_Inverters_ID[i, board, inv, 2]), inv)
    else:
        i = single_block
        for board in range(0,3):
            for inv in range(1, max_inv_block+1):
                if no_es_nan(strings_ID[i, board, inv, 1, 0]):
                    for s in range(1, max_str_pinv+1):
                        if no_es_nan(strings_ID[i, board, inv, s, 0]):
                            x = strings_ID[i, board, inv, s, 1]
                            y_inicio = strings_ID[i, board, inv, s, 2]
                            y_fin = strings_ID[i, board, inv, s, 3]
                            s_id_global = strings_ID[i, board, inv, s, 4]
                            y_medio = strings_ID[i, board, inv, s, 5]
                            dibujar_envolvente_y_orientacion_string(x, y_fin, y_inicio, h_modulo, inv, y_medio, s_id_global)     
                            
                    insertar_texto_strings_per_inv(String_Inverters_ID[i, board, inv, 3], float(String_Inverters_ID[i, board, inv, 1]), float(String_Inverters_ID[i, board, inv, 2]), inv)

    doc = acad.app.ActiveDocument
    doc.SendCommand("._zoom _extents\n")
    return capas_de_envolventes


                         
def CAD_draw_orientacion_strings(acad, all_blocks, single_block, strings_ID, bloque_inicial, n_bloques, max_inv_block, max_str_pinv, h_modulo):
    from pyautocad import APoint, aDouble
    import time

    time.sleep(0.3)

    capas_de_envolventes = []
    colores = [130, 11, 30, 100, 200, 5]
    capa_flechas_orientacion= acad.doc.Layers.Add('Ori-Str.')
    capa_flechas_orientacion.color = 7
    for inv in range(1, max_inv_block+1):
        capa_envolvente = acad.doc.Layers.Add(f'S-INV {inv}')
        capas_de_envolventes.append(f'S-INV {inv}')
        color_index = colores[(inv - 1) % len(colores)]
        capa_envolvente.color = color_index
        
    def dibujar_orientacion_string(x, y_fin, h_modulo, inv, y_medio, s_id_global):
        #orientacion    
        p_ini = APoint(x, y_medio)
        p_fin = APoint(x, y_medio + (y_fin-y_medio)/2)
        p_izq_fl = APoint(x-h_modulo/3, y_medio + (y_fin-y_medio)/2.2)
        p_der_fl = APoint(x+h_modulo/3, y_medio + (y_fin-y_medio)/2.2)
        
        points = aDouble(p_ini.x, p_ini.y, 0, p_fin.x, p_fin.y, 0, p_izq_fl.x, p_izq_fl.y, 0, p_fin.x, p_fin.y, 0, p_der_fl.x, p_der_fl.y, 0)
        flecha_ori = acad.model.AddPolyline(points)        
        flecha_ori.ConstantWidth = 0.1
        flecha_ori.Layer = 'Ori-Str.'
        insercion_texto = APoint(x+h_modulo/3, y_medio + (y_fin-y_medio)/3)
        texto_n_strings = acad.model.AddText(str(s_id_global), insercion_texto, 0.3)
        texto_n_strings.Layer = 'Ori-Str.'
        
    # Evaluación central segura
    def no_es_nan(valor):
        return valor is not None and not (valor != valor)

    if all_blocks:
        for i in range(bloque_inicial, n_bloques+1):
            for board in range(0,3):
                if no_es_nan(strings_ID[i, board, 1, 1, 0]):
                    for inv in range(1, max_inv_block+1):
                        if no_es_nan(strings_ID[i, board, inv, 1, 0]):
                            for s in range(1, max_str_pinv+1):
                                if no_es_nan(strings_ID[i, board, inv, s, 0]):
                                    x = strings_ID[i, board, inv, s, 1]                                   
                                    y_fin = strings_ID[i, board, inv, s, 3]
                                    s_id_global = strings_ID[i, board, inv, s, 4]
                                    y_medio = strings_ID[i, board, inv, s, 5]
                                    dibujar_orientacion_string(x, y_fin, h_modulo, inv, y_medio, s_id_global)     
    else:
        i=single_block
        for board in range(0,3):
            if no_es_nan(strings_ID[i, board, 1, 1, 0]):
                for inv in range(1, max_inv_block+1):
                    if no_es_nan(strings_ID[i, board, inv, 1, 0]):
                        for s in range(1, max_str_pinv+1):
                            if no_es_nan(strings_ID[i, board, inv, s, 0]):
                                x = strings_ID[i, board, inv, s, 1]                                   
                                y_fin = strings_ID[i, board, inv, s, 3]
                                s_id_global = strings_ID[i, board, inv, s, 4]
                                y_medio = strings_ID[i, board, inv, s, 5]
                                dibujar_orientacion_string(x, y_fin, h_modulo, inv, y_medio, s_id_global)                                      
                                    



#----------------LEER CONFIGURACION DE BAJA TENSION (ENVOLVENTES DE FILAS ASOCIADAS A CAJAS O STRINGS A INVERSORES DE STRING)--------------

# def CAD_read_config_LV(acad, all_blocks, single_block, bloque_inicial, n_bloques, max_b, max_f_str_b,capas_de_envolventes, filas_en_cajas, equi_reverse_ibc):
#     time.sleep(0.1) #le damos un tiempo para que autocad no se autobloquee
#     info_en_documento_activo=False
#     for obj in acad.iter_objects_fast('Polyline'):
#         if obj.Layer in capas_de_envolventes:
#             info_en_documento_activo=True
#             coordenadas_env = np.array(obj.Coordinates).reshape(-1,3) #convertimos la tupla a array
#             # coordenadas_env_2d = nuevas_coordenadas[:,[0,1]] #le quitamos la z porque esta version es en 2D
#             min_x = min(coordenadas_env[:,0])
#             max_x = max(coordenadas_env[:,0])
#             min_y = min(coordenadas_env[:,1])
#             max_y = max(coordenadas_env[:,1])
            
#             if all_blocks==True:
#                 for i in range(bloque_inicial,n_bloques+1):
#                     for b in range(0,max_b):
#                         if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
#                             for f in range (0,max_f_str_b):      
#                                 if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía
#                                     if min_x <= filas_en_cajas[i,b,f,2] <= max_x and min_y <= filas_en_cajas[i,b,f,3] <= max_y: #si la fila está dentro de la envolvente                                       
#                                         filas_en_cajas[i,b,f,0] = equi_reverse_ibc[i,1,int(capas_de_envolventes.index(obj.Layer)+1),2] #la capa de envolvente da la caja total del bloque, sacamos su equivalente inversa para sacar la caja en la banda (el no. inv da igual)
#             else:
#                 i=single_block
#                 for b in range(0,max_b):
#                     if ~np.isnan(filas_en_cajas[i,b,0,0]): #si la banda no está vacía       
#                         for f in range (0,max_f_str_b):      
#                             if ~np.isnan(filas_en_cajas[i,b,f,0]): #si la fila no está vacía
#                                 if min_x <= filas_en_cajas[i,b,f,2] <= max_x and min_y <= filas_en_cajas[i,b,f,3] <= max_y: #si la fila está dentro de la envolvente
#                                     try:
#                                         filas_en_cajas[i,b,f,0] = equi_reverse_ibc[i,1,int(capas_de_envolventes.index(obj.Layer)+1),2]
#                                     except (ValueError, IndexError):
#                                         # Si la capa no tiene equivalente (se está añadiendo una nueva caja respecto al original)
#                                         #Se actualiza(max_cpb + 1)
#                                         filas_en_cajas[i, b, f, 0] = max_filas_en_cajas + 1  # variable pasada como argumento
    
#     if info_en_documento_activo==True:                          
#         return filas_en_cajas
#     else:
#         return None
 

def CAD_read_config_LV(acad, all_blocks, single_block, bloque_inicial, n_bloques, max_b, max_f_str_b, capas_de_envolventes, filas_en_cajas, max_c, max_c_block):
    time.sleep(0.1)
    info_en_documento_activo = False

    registros_envolventes = []  # (i, b, f, id_caja_bloque)

    for obj in acad.iter_objects_fast('Polyline'):
        if obj.Layer in capas_de_envolventes:
            info_en_documento_activo = True
            coordenadas_env = np.array(obj.Coordinates).reshape(-1, 3)
            min_x = min(coordenadas_env[:, 0])
            max_x = max(coordenadas_env[:, 0])
            min_y = min(coordenadas_env[:, 1])
            max_y = max(coordenadas_env[:, 1])

            bloques = range(bloque_inicial, n_bloques+1) if all_blocks else [single_block]
            for i in bloques:
                for b in range(0, max_b):
                    if ~np.isnan(filas_en_cajas[i, b, 0, 0]):
                        for f in range(0, max_f_str_b):
                            if ~np.isnan(filas_en_cajas[i, b, f, 0]):
                                x = filas_en_cajas[i, b, f, 2]
                                y = filas_en_cajas[i, b, f, 3]
                                if min_x <= x <= max_x and min_y <= y <= max_y:
                                    id_caja_bloque = int(capas_de_envolventes.index(obj.Layer) + 1)
                                    registros_envolventes.append((i, b, f, id_caja_bloque))

    if not info_en_documento_activo:
        return None

    # Ordenamos los registros para pasar de la numeracion de caja por bloque (de las envolventes) a caja por banda, no vale usar equi_reverse_ibc si se han metido cajas nuevas o se han cambiado de orden en la numeracion por algun motivo
    registros_array = np.array(registros_envolventes, dtype=[('i', int), ('b', int), ('f', int), ('id_bloque', int)])
    registros_ordenados = np.sort(registros_array, order=['i', 'b', 'id_bloque'])

    id_actual = -1
    b_anterior = (-1, -1)
    mapa_ids = {}  # (i, b, id_bloque) → id_caja_banda

    # Para estadística de conteo
    cajas_por_banda = {}  # (i, b) → set(cajas)
    cajas_por_bloque = {}  # i → set(cajas)

    for reg in registros_ordenados:
        clave = (reg['i'], reg['b'], reg['id_bloque'])

        if (reg['i'], reg['b']) != b_anterior:
            id_actual = 0
            b_anterior = (reg['i'], reg['b'])
        elif clave not in mapa_ids:
            id_actual += 1

        mapa_ids[clave] = id_actual

        # Estadística
        cajas_por_banda.setdefault((reg['i'], reg['b']), set()).add(id_actual)
        cajas_por_bloque.setdefault(reg['i'], set()).add(id_actual)

    # Aplicar los nuevos IDs a filas_en_cajas
    for reg in registros_ordenados:
        nuevo_id = mapa_ids[(reg['i'], reg['b'], reg['id_bloque'])]
        filas_en_cajas[reg['i'], reg['b'], reg['f'], 0] = nuevo_id

    # Calculamos max_c y max_c_block
    max_c_nuevo = max(len(s) for s in cajas_por_banda.values()) +1 if cajas_por_banda else 0
    max_c_block_nuevo = max(len(s) for s in cajas_por_bloque.values()) +1 if cajas_por_bloque else 0

    if max_c_nuevo > max_c:
        max_c = max_c_nuevo
        
    if max_c_block_nuevo > max_c_block:
        max_c_block = max_c_block_nuevo
        
    return filas_en_cajas, max_c, max_c_block






#Para inversores de string la estratgia es similar pero buscamos por Strings_ID el punto medio del string y lo asociamos al string fisico que lo tuviese 


def CAD_read_config_LV_inv_string(acad, all_blocks, single_block, bloque_inicial, n_bloques,
                                   max_b, max_inv, max_inv_block, max_str_pinv,
                                   capas_de_envolventes, equi_reverse_ibv, equi_ibv_to_fs,
                                   strings_ID, inv_string, strings_fisicos, orientacion, dos_inv_por_bloque):

    def no_es_nan(valor):
        return valor is not None and not (valor != valor)

    #Comprobamos el tipo de polilinea para obtener las coordenadas de manera adecuada
    def filtrar_coord_tipos_polilinea(tipo_pol, coords):
        #Si la polilinea se ha metido a mano será del tipo AcDbPolyline, no es del tipo que se estaban insertando AcDb2dPolyline (Polilinea 2D), si nos hemos olvidado de aplanarlo en AutoCAD a polilinea 2D paradojicamente saldrá con X, Y pero sin Z, aunque la otra sale con 3, por lo que hay que añadirle un cero a la Z
        if tipo_pol == "AcDbPolyline":
            if len(coords) % 3 == 0 and coords[3]==0: #si sale bien, con 3 coordenadas siendo cero la tercera
                coords_array = np.array(coords).reshape(-1, 3) 
            elif len(coords) % 2 == 0:
                coords_array = np.array(coords).reshape(-1, 2)
                z = obj.Elevation
                coordenadas_3d = np.hstack([coords_array, np.full((coords_array.shape[0], 1), z)])
            else:
                print(f"Coordenadas mal formateadas: {obj.Handle}")
        else:
            #Leer cordenadas
            coordenadas_3d = np.array(obj.Coordinates).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
            
        #Convertimos a 2D
        coordenadas_2d = coordenadas_3d[:,[0,1]] #y le quitamos la z porque esta version es en 2D
     
        return coordenadas_2d

    time.sleep(0.1)

    info_en_documento_activo = False
    inv_string_list = inv_string.tolist()  # Para modificar

    #Cuando hay dos cuadros la equivalencia puede verse frustrada por la presencia de nans si se pasan inversores de un cuadro a otro, hay que agrupar equi_reverse_ibv en una sola lista o "cuadro conjunto"
    if dos_inv_por_bloque:
        from collections import defaultdict
        
        # stats_board[i][b][board] -> [count, sum_x]
        stats_pair = [ [defaultdict(lambda: [0, 0.0]) for _ in range(max_b)] for _ in range(n_bloques+1) ]
        
        def parse_board_inv_from_layer(layer: str):
            # asume último token "X.Y"
            ult = layer.split()[-1]
            a, b = ult.split(".")
            return int(a), int(b)  # respeta 1-based si así trabajas
        
        # --- PASO 1: REGISTRAMOS CUALES Y CUANTAS VECES APARECEN LOS S-INV EN CADA BANDA (por bloque) ---
        for obj in acad.iter_objects_fast('Polyline'):
            if obj.Layer not in capas_de_envolventes:
                continue
        
            # bbox de la envolvente
            t_pol = obj.ObjectName
            coords2d = filtrar_coord_tipos_polilinea(t_pol, obj.Coordinates)
            min_x, max_x = coords2d[:,0].min(), coords2d[:,0].max()
            min_y, max_y = coords2d[:,1].min(), coords2d[:,1].max()
        
            try:
                board_cap, inv_cap = parse_board_inv_from_layer(obj.Layer)
            except Exception:
                continue
        
            for i in range(bloque_inicial, n_bloques + 1):
                for board in range(0, 3):
                    if not no_es_nan(strings_ID[i, board, 1, 1, 0]): 
                        continue
                    for inv in range(1, max_inv_block + 1):
                        if not no_es_nan(strings_ID[i, board, inv, 1, 0]): 
                            continue
                        for s in range(1, max_str_pinv + 1):
                            if not no_es_nan(strings_ID[i, board, inv, s, 0]): 
                                continue
        
                            x_str = strings_ID[i, board, inv, s, 1]
                            y_str = strings_ID[i, board, inv, s, 5]
                            if not (min_x <= x_str <= max_x and min_y <= y_str <= max_y):
                                continue
        
                            sid = strings_ID[i, board, inv, s, 4]
                            m = np.where(strings_fisicos[...,2] == sid)
                            if m[0].size == 0:
                                continue
                            b_match = int(m[1][0])  # banda
        
                            stats_pair[i][b_match][(board_cap, inv_cap)][0] += 1
                            stats_pair[i][b_match][(board_cap, inv_cap)][1] += float(x_str)

        # --- PASO 2: EN EL REGISTRO SE ESTAN DUPLICANDO INVERSORES PORQUE LOS COMPARTIDOS APARECEN EN DOS BANDAS, SE BORRA EL QUE TENGA MENOS                                         ---
        for i in range(bloque_inicial, n_bloques + 1):
            # recolectar todas las parejas presentes en el bloque
            pairs = set()
            for b in range(0,max_b):
                pairs.update(stats_pair[i][b].keys())
        
            for par in pairs:
                apar = [(b, stats_pair[i][b][par][0]) 
                        for b in range(0,max_b) if par in stats_pair[i][b]]
                if len(apar) <= 1:
                    continue
        
                max_cnt = max(c for _,c in apar)
                keep = min(b for b,c in apar if c == max_cnt)
                
                # borrar de las demás bandas
                for b,c in apar:
                    if b != keep:
                        stats_pair[i][b].pop(par, None)

        
        # --- PASO 3: ordenar por X media y construir equi_ibv (i,b,k,3) = [i, board, inv_in_board] ---
        equi_ibv = np.full((n_bloques+1, max_b, max_inv+1, 3), np.nan, dtype=float)
        
        for i in range(bloque_inicial, n_bloques + 1):
            for b in range(0, max_b):
                candidatos = []
                for (board_cap, inv_cap), (cnt, sumx) in stats_pair[i][b].items():
                    if cnt <= 0: 
                        continue
                    mean_x = sumx / cnt
                    candidatos.append((mean_x, board_cap, inv_cap))
        
                # ordenar por orientación
                if orientacion[i, b] == 'S':
                    candidatos.sort(key=lambda t: t[0])            # X asc
                else:
                    candidatos.sort(key=lambda t: t[0], reverse=True)  # X desc
        
                # volcar
                for k, (_, board_cap, inv_cap) in enumerate(candidatos[:max_inv], start=1):
                    equi_ibv[i, b, k, 0] = i
                    equi_ibv[i, b, k, 1] = board_cap
                    equi_ibv[i, b, k, 2] = inv_cap

        
        #----Paso 4:  Crear inversa: (i, board, inv_in_board) -> [i, banda, inv_en_banda]
        equi_reverse_ibv = np.full((n_bloques+1, max_b, max_inv_block+1, 3), np.nan, dtype=float)
        
        for i in range(bloque_inicial, n_bloques + 1):
            for b in range(0,max_b):
                for k in range(1, equi_ibv.shape[2]):
                    row = equi_ibv[i, b, k]
                    if np.isnan(row[0]):
                        continue
                    board_val = int(row[1])
                    inv_val   = int(row[2])  # 1-based
                    if 0 <= board_val < max_b and 1 <= inv_val <= max_inv_block:
                        equi_reverse_ibv[i, board_val, inv_val, 0] = i
                        equi_reverse_ibv[i, board_val, inv_val, 1] = b
                        equi_reverse_ibv[i, board_val, inv_val, 2] = k
        
        

           
    for obj in acad.iter_objects_fast('Polyline'):
        if obj.Layer in capas_de_envolventes:
            info_en_documento_activo = True
            
            #Leer tipo de polilinea y cordenadas
            t_pol = obj.ObjectName
            coords = obj.Coordinates

            coordenadas_env = filtrar_coord_tipos_polilinea(t_pol, coords)
            min_x, max_x = coordenadas_env[:, 0].min(), coordenadas_env[:, 0].max()
            min_y, max_y = coordenadas_env[:, 1].min(), coordenadas_env[:, 1].max()


            for i in range(bloque_inicial, n_bloques + 1):
                for board in range(0, 3):
                    if no_es_nan(strings_ID[i, board, 1, 1, 0]):
                        for inv in range(1, max_inv_block + 1):
                            if no_es_nan(strings_ID[i, board, inv, 1, 0]):
                                for s in range(1, max_str_pinv + 1):
                                    if no_es_nan(strings_ID[i, board, inv, s, 0]):

                                        x_str = strings_ID[i, board, inv, s, 1]
                                        y_str = strings_ID[i, board, inv, s, 5]

                                        if min_x <= x_str <= max_x and min_y <= y_str <= max_y:
                                            sid_global = strings_ID[i, board, inv, s, 4]                                   

                                            #Lectura de la capa
                                            if dos_inv_por_bloque:
                                                parte = obj.Layer.split()[-1]   # por ejemplo "2.7"
                                                num1, num2 = parte.split(".")                                               
                                                board_extraido = int(num1)
                                                inv_extraido = int(num2)
                                            else:
                                                board_extraido = board
                                                inv_extraido = int(obj.Layer.split()[-1])
                                            

                                            # Nuevo destino                                       
                                            i_ins, b_ins, inv_ins = equi_reverse_ibv[i, board_extraido, inv_extraido]
                                            i_ins = int(i_ins)
                                            b_ins = int(b_ins)
                                            inv_ins = int(inv_ins)

                                            # if board == board_extraido and inv == inv_extraido:
                                            #     continue #Si el string permanece en el mismo inversor no hace falta borrar ni insertar

                                            # Borrado: buscar el primer elemento con sid == sid_global que NO es 'NUEVO'
                                            found = False
                                            for i in range(len(inv_string_list)):
                                                for b in range(len(inv_string_list[i])):
                                                    for inv in range(len(inv_string_list[i][b])):
                                                        for s, fila in enumerate(inv_string_list[i][b][inv]):
                                                            if (
                                                                len(fila) >= 3 and fila[2] == sid_global and
                                                                (len(fila) < 5 or fila[4] != 'NUEVO')  # Solo originales
                                                            ):
                                                                inv_string_list[i][b][inv][s][2] = 0  # Marcar para borrar (sid = 0)
                                                                found = True
                                                                break
                                                        if found: break
                                                    if found: break
                                                if found: break

                                            
                                            # Buscar string físico
                                            matches_phys = np.argwhere(strings_fisicos[..., 2] == sid_global)                                           
                                            
                                            if matches_phys.size == 0:
                                                continue
                                            i_sf, b_sf, f_sf, s_sf = matches_phys[0]

                                            x_ins = strings_fisicos[i_sf, b_sf, f_sf, s_sf, 0]
                                            y_ins = strings_fisicos[i_sf, b_sf, f_sf, s_sf, 1]
                                            sid_ins = strings_fisicos[i_sf, b_sf, f_sf, s_sf, 2]

                                            # Insertar en orden según orientación
                                            lista_destino = inv_string_list[i_ins][b_ins][inv_ins]
                                                
                                            ind_ins = len(lista_destino)

                                            for idx, val in enumerate(lista_destino[1:]):
                                                if orientacion[i, b_sf] == 'S':
                                                    if val[0] > x_ins or (val[0] == x_ins and val[1] < y_ins):
                                                        ind_ins = idx + 1
                                                        break
                                                elif orientacion[i, b_sf] == 'N':
                                                    if val[0] < x_ins or (val[0] == x_ins and val[1] < y_ins):
                                                        ind_ins = idx + 1
                                                        break
                                            lista_destino.insert(ind_ins, [x_ins, y_ins, sid_ins, board_extraido, 'NUEVO'])  # ⬅️ Campo temporal añadido

    for i in range(len(inv_string_list)):
        for b in range(len(inv_string_list[i])):
            for inv in range(len(inv_string_list[i][b])):
                nueva_lista = []
                for fila in inv_string_list[i][b][inv]:
                    if len(fila) >= 5 and fila[4] == 'NUEVO':
                        fila = fila[:4]  # Eliminar el campo temporal antes de guardar
                    if fila[2] != 0:     # No borrar si está marcado
                        nueva_lista.append(fila)
                inv_string_list[i][b][inv] = nueva_lista
    

    # Asegurar tamaño fijo por inversor
    for i in range(len(inv_string_list)):
        for b in range(len(inv_string_list[i])):
            for inv in range(len(inv_string_list[i][b])):
                inv_info = inv_string_list[i][b][inv][0]  # info auxiliar
                strings_validos = [s for s in inv_string_list[i][b][inv][1:] if not np.isnan(s[2])]
                
                # Rellenar si faltan
                while len(strings_validos) < max_str_pinv:
                    strings_validos.append([np.nan, np.nan, np.nan, np.nan])
                
                # Reconstruir la lista con inv_info + strings
                inv_string_list[i][b][inv] = [inv_info] + strings_validos[:max_str_pinv]



    # Volver a array
    inv_string = np.array(inv_string_list)

    # Reinicializamos las posiciones de los inversores a cero, se calcularan despues. Es necesario para evitar que nuevos inversores tengan np.nan en la primera fila y no se calculen
    mask = ~np.isnan(inv_string[..., 1, 0])
    inv_string[mask, 0, 0] = 0
    inv_string[mask, 0, 1] = 0
    

    # Actualizar equivalencias ibv_to_fs
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


    if info_en_documento_activo:
        return inv_string, equi_ibv_to_fs
    else:
        return None



                        

def CAD_read_orientacion_strings(acad, all_blocks, single_block, bloque_inicial, n_bloques,
                                  max_b, max_inv, max_inv_block, max_str_pinv,
                                  capas_de_envolventes, strings_ID, ori_str_ID):

    def no_es_nan(valor):
        return valor is not None and not (valor != valor)

    def filtrar_coord_tipos_polilinea(tipo_pol, coords, elevation=0):
        if tipo_pol == "AcDbPolyline":
            if len(coords) % 3 == 0 and coords[3] == 0:
                coords_array = np.array(coords).reshape(-1, 3)
            elif len(coords) % 2 == 0:
                coords_array = np.array(coords).reshape(-1, 2)
                coordenadas_3d = np.hstack([coords_array, np.full((coords_array.shape[0], 1), elevation)])
            else:
                return None
        else:
            coordenadas_3d = np.array(coords).reshape(-1, 3)

        return coordenadas_3d[:, [0, 1]]  # Solo X, Y

    import time
    time.sleep(0.1)

    info_en_documento_activo = False

    # === 1. Preprocesar todas las flechas de orientación ===
    flechas = []
    for obj2 in acad.iter_objects_fast('Polyline'):
        if obj2.Layer == "Ori-Str.":
            coords_flecha = obj2.Coordinates
            tipo = obj2.ObjectName
            coordenadas = filtrar_coord_tipos_polilinea(tipo, coords_flecha, obj2.Elevation)
            if coordenadas is not None:
                flechas.append(coordenadas)

    # === 2. Preprocesar todos los strings ===
    strings_index = []  # [(x, y, sid, i, board, inv, s)]
    bloques = range(bloque_inicial, n_bloques + 1) if all_blocks else [single_block]

    for i in bloques:
        for board in range(0, 3):
            if no_es_nan(strings_ID[i, board, 1, 1, 0]):
                for inv in range(1, max_inv_block + 1):
                    if no_es_nan(strings_ID[i, board, inv, 1, 0]):
                        for s in range(1, max_str_pinv + 1):
                            if no_es_nan(strings_ID[i, board, inv, s, 0]):
                                x = strings_ID[i, board, inv, s, 1]
                                y = strings_ID[i, board, inv, s, 5]
                                sid = strings_ID[i, board, inv, s, 4]
                                strings_index.append((x, y, sid, i, board, inv, s))

    # === 3. Procesar envolventes ===
    for obj in acad.iter_objects_fast('Polyline'):
        if obj.Layer in capas_de_envolventes:
            info_en_documento_activo = True

            t_pol = obj.ObjectName
            coords = obj.Coordinates
            coordenadas_env = filtrar_coord_tipos_polilinea(t_pol, coords, obj.Elevation)
            if coordenadas_env is None:
                continue

            min_x, max_x = coordenadas_env[:, 0].min(), coordenadas_env[:, 0].max()
            min_y, max_y = coordenadas_env[:, 1].min(), coordenadas_env[:, 1].max()

            # Buscar strings dentro de la envolvente
            strings_en_env = [
                (x, y, sid, i, board, inv, s)
                for x, y, sid, i, board, inv, s in strings_index
                if min_x <= x <= max_x and min_y <= y <= max_y
            ]

            if not strings_en_env:
                continue  # No hay strings dentro

            for x_str, y_str, sid_global, i, board, inv, s in strings_en_env:
                punto_medio = y_str
                y_inicio = strings_ID[i, board, inv, s, 2]
                y_fin = strings_ID[i, board, inv, s, 3]

                # Buscar flechas que estén dentro de la envolvente
                for coords_flecha in flechas:
                    if min_x <= coords_flecha[0, 0] <= max_x and min_y <= coords_flecha[0, 1] <= max_y:
                        if coords_flecha[-1, 1] > punto_medio:
                            ori_str_ID[sid_global][1] = 'N'
                            if y_fin < y_inicio:
                                strings_ID[i, board, inv, s, 2], strings_ID[i, board, inv, s, 3] = y_fin, y_inicio
                        else:
                            ori_str_ID[sid_global][1] = 'S'
                            if y_fin > y_inicio:
                                strings_ID[i, board, inv, s, 2], strings_ID[i, board, inv, s, 3] = y_fin, y_inicio

    if info_en_documento_activo:
        return ori_str_ID, strings_ID
    else:
        return None, None



#----------------------------DIBUJAR CAJAS O INVERSORES DE STRING-------------------------------

def CAD_draw_DC_Boxes(acad, all_blocks, single_block, bloque_inicial, n_bloques, handle_DC_Boxes, max_c_block, DC_Boxes_ID, ancho_caja, largo_caja, h_modulo, orientacion, equi_reverse_ibc):
    from pyautocad import APoint, aDouble
    
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    
    # Definimos las capas    
    capa_DC_Boxes = acad.doc.Layers.Add('DC Boxes')
    capa_DC_Boxes.color = 174
    
    capa_DC_Boxes_ID= acad.doc.Layers.Add('DC Boxes ID')
    capa_DC_Boxes_ID.color = 174 
    
    #Definimos el bloque que va a servir como caja y se insertara despues
    def definir_bloque_DC_Box(nombre_bloque_str, color, ancho_caja, largo_caja):
        nombre_bloque_var = acad.doc.Blocks.Add(APoint(0,0,0), nombre_bloque_str)
        point_pol_int_term_circ=aDouble(-ancho_caja/2, 0, 0   , ancho_caja/2, 0, 0)
        pol_interior_term_circ = nombre_bloque_var.AddPolyline(point_pol_int_term_circ)
        pol_interior_term_circ.ConstantWidth=largo_caja
        pol_interior_term_circ.color = color

        return nombre_bloque_var
    
    # Definimos la función para dibujar las cajas como una polilinea asi como su ID al lado 
    def dibujar_DC_Boxes_e_ID(x, y, largo, ancho, texto, h_modulo, ori_caja):     
        # Definir el punto de insercion en el centro de la caja
        p_insercion = APoint(x, y)

        # Insertar bloque de la caja
        bloque_insertado = acad.model.InsertBlock(p_insercion, 'DC Box Block', 1, 1, 1, 0)
        bloque_insertado.Layer = 'DC Boxes'

        # Añadir el texto
        if ori_caja == 'S':
            desfase_texto_x = h_modulo/2 + 1 + 0.2 #la mitad del modulo mas la altura del texto mas un margen de separacion, a la derecha
            desfase_texto_y = 0
        elif ori_caja == 'N':
            desfase_texto_x = -h_modulo/2 - 0.2 #la mitad del modulo mas un margen de separacion, a la izquierda
            desfase_texto_y = -6.7 #aproximacion, lo ideal seria alinear el texto pero no funciona bien
            
        insercion_texto = APoint(x + desfase_texto_x, y + desfase_texto_y) #desplazamos la X un metro para que no choque con la forma del inversor
        texto_caja = acad.model.AddText(texto, insercion_texto, 1)  # 1 es el tamaño del texto 
        texto_caja.Layer = 'DC Boxes ID'
        texto_caja.Rotation = np.pi / 2
        
        #Se comenta porque usar alignment parece que peta, usamos "desfase y" aunque no sea exacto
        # if ori_caja == 'N':
        #     texto_caja.Alignment = ACAD.acAlignmentRight #si estamos en una banda orientada hacia el norte el texto se alinea hacia el punto de insercion, con el inicio en la parte del pasillo y el final en la caja
        
        handle = bloque_insertado.Handle

        return handle 
    
    # Creamos el bloque
    definir_bloque_DC_Box('DC Box Block', 174, ancho_caja, largo_caja) #Nombre que debe coincidir y color de la polilinea por si acaso falla el de la capa
    
    # Recorremos DC_Boxes_ID de manera parecida a strings_ID para dibujarlas todas   
    if all_blocks==True:          
        for i in range(bloque_inicial,n_bloques+1):
            for inv in range(1,3):
                if ~np.isnan(DC_Boxes_ID[i,inv,1,1]): #si el inv no está vacío      
                    for caj in range (1,max_c_block+1):      
                        if ~np.isnan(DC_Boxes_ID[i,inv,caj,1]): #si la caja no está vacía    
                            b = int(equi_reverse_ibc[i,inv,caj,1]) #sacamos la banda
                            ori_caja = orientacion[i,b]
                            handle_DC_Boxes[i,inv,caj] = dibujar_DC_Boxes_e_ID(DC_Boxes_ID[i,inv,caj,1], DC_Boxes_ID[i,inv,caj,2], largo_caja, ancho_caja,DC_Boxes_ID[i,inv,caj,0], h_modulo, ori_caja)
                            
                        else:
                            break
                else:
                    break

    else:
        i = single_block
        for inv in range(1,3):
            if ~np.isnan(DC_Boxes_ID[i,inv,1,1]): #si el inv no está vacío      
                for caj in range (1,max_c_block+1):      
                    if ~np.isnan(DC_Boxes_ID[i,inv,caj,1]): #si la caja no está vacía    
                        b = int(equi_reverse_ibc[i,inv,caj,1]) #sacamos la banda
                        ori_caja = orientacion[i,b]
                        handle_DC_Boxes[i,inv,caj] = dibujar_DC_Boxes_e_ID(DC_Boxes_ID[i,inv,caj,1], DC_Boxes_ID[i,inv,caj,2], largo_caja, ancho_caja,DC_Boxes_ID[i,inv,caj,0], h_modulo, ori_caja)
                        
                    else:
                        break
            else:
                break
        
    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents
        
    return handle_DC_Boxes





def CAD_draw_Inv_String(acad, all_blocks, single_block, bloque_inicial, n_bloques, max_inv_block, String_Inverters_ID, ancho_caja, largo_caja, h_modulo, orientacion, equi_reverse_ibv, handle_inv_string):
    from pyautocad import APoint, aDouble
    
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    
    # Definimos las capas    
    capa_Inv_String = acad.doc.Layers.Add('String Inverters')
    capa_Inv_String.color = 174
    
    capa_Inv_String_ID= acad.doc.Layers.Add('String Inverters ID')
    capa_Inv_String_ID.color = 174 
    
    def no_es_nan(valor):
        return valor is not None and not (valor != valor)
    
    #Definimos el bloque que va a servir como caja y se insertara despues
    def definir_bloque_DC_Box(nombre_bloque_str, color, ancho_caja, largo_caja):
        nombre_bloque_var = acad.doc.Blocks.Add(APoint(0,0,0), nombre_bloque_str)
        point_pol_int_term_circ=aDouble(-ancho_caja/2, 0, 0   , ancho_caja/2, 0, 0)
        pol_interior_term_circ = nombre_bloque_var.AddPolyline(point_pol_int_term_circ)
        pol_interior_term_circ.ConstantWidth=largo_caja
        pol_interior_term_circ.color = color

        return nombre_bloque_var
    
    # Definimos la función para dibujar las cajas como una polilinea asi como su ID al lado 
    def dibujar_String_Inverters_e_ID(x, y, largo, ancho, texto, h_modulo, ori_caja):     
        # Definir el punto de insercion en el centro de la caja
        p_insercion = APoint(x, y)

        # Insertar bloque de la caja
        bloque_insertado = acad.model.InsertBlock(p_insercion, 'String Inverter Block', 1, 1, 1, 0)
        bloque_insertado.Layer = 'String Inverters'

        # Añadir el texto
        if ori_caja == 'S':
            desfase_texto_x = h_modulo/2 + 1 + 0.2 #la mitad del modulo mas la altura del texto mas un margen de separacion, a la derecha
            desfase_texto_y = 0
        elif ori_caja == 'N':
            desfase_texto_x = -h_modulo/2 - 0.2 #la mitad del modulo mas un margen de separacion, a la izquierda
            desfase_texto_y = -6.7 #aproximacion, lo ideal seria alinear el texto pero no funciona bien
            
        insercion_texto = APoint(x + desfase_texto_x, y + desfase_texto_y) #desplazamos la X un metro para que no choque con la forma del inversor
        texto_caja = acad.model.AddText(texto, insercion_texto, 1)  # 1 es el tamaño del texto 
        texto_caja.Layer = 'String Inverters ID'
        texto_caja.Rotation = np.pi / 2
        
        #Se comenta porque usar alignment parece que peta, usamos "desfase y" aunque no sea exacto
        # if ori_caja == 'N':
        #     texto_caja.Alignment = ACAD.acAlignmentRight #si estamos en una banda orientada hacia el norte el texto se alinea hacia el punto de insercion, con el inicio en la parte del pasillo y el final en la caja
        
        handle = bloque_insertado.Handle

        return handle 
    
    # Creamos el bloque
    definir_bloque_DC_Box('String Inverter Block', 174, ancho_caja, largo_caja) #Nombre que debe coincidir y color de la polilinea por si acaso falla el de la capa
    
    # Recorremos String_Inverters_ID de manera parecida a strings_ID para dibujarlas todas   
    
    if all_blocks==True:          
        for i in range(bloque_inicial,n_bloques+1):
            for board in range(0,3):
                if no_es_nan(np.float64(String_Inverters_ID[i,board,1,1])): #si el cuadro no está vacío    
                    for inv in range (1,max_inv_block+1):      
                        if no_es_nan(np.float64(String_Inverters_ID[i,board,inv,1])): #si la caja no está vacía  
                            b = int(equi_reverse_ibv[i,board,inv,1]) #sacamos la banda
                            ori_caja = orientacion[i,b]
                            handle_inv_string[i,board,inv] = dibujar_String_Inverters_e_ID(float(String_Inverters_ID[i,board,inv,1]), float(String_Inverters_ID[i,board,inv,2]), largo_caja, ancho_caja,String_Inverters_ID[i,board,inv,0], h_modulo, ori_caja)                            
                        else:
                            break


    else:
        i = single_block
        for board in range(0,3):
            if no_es_nan(np.float64(String_Inverters_ID[i,board,1,1])): #si el cuadro no está vacío      
                for inv in range (1,max_inv_block+1):      
                    if no_es_nan(np.float64(String_Inverters_ID[i,board,inv,1])): #si la caja no está vacía    
                        b = int(equi_reverse_ibv[i,board,inv,1]) #sacamos la banda
                        ori_caja = orientacion[i,b]
                        handle_inv_string[i,board,inv] = dibujar_String_Inverters_e_ID(float(String_Inverters_ID[i,board,inv,1]), float(String_Inverters_ID[i,board,inv,2]), largo_caja, ancho_caja,String_Inverters_ID[i,board,inv,0], h_modulo, ori_caja)                            
                    else:
                        break

    
    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents

    return handle_inv_string


    
#----------------LEER POSICIONES DE LAS CAJAS E INV DE STRING POTENCIALMENTE DESPLAZADAS SIN CAMBIAR SUS FILAS ASOCIADAS--------------
    
def CAD_read_DC_Boxes_loc(acad, all_blocks, single_block, bloque_inicial, n_bloques, cajas_fisicas, DCBoxes_ID, handle_DC_Boxes, equi_reverse_ibc):
    time.sleep(0.1) #le damos un tiempo para que autocad no se autobloquee
    info_en_documento_activo=False
    for obj in acad.iter_objects_fast('BlockReference'):
        if obj.Layer == "DC Boxes":
            info_en_documento_activo=True
            handle_extraido = obj.Handle
            indices_dcbox = np.where(handle_DC_Boxes == handle_extraido)
            
            bloque = int(indices_dcbox[0][0])
            inv = int(indices_dcbox[1][0])
            caja = int(indices_dcbox[2][0])
            
            ind_corr = equi_reverse_ibc[bloque,inv,caja]
                     
            i = int(ind_corr[0])
            b = int(ind_corr[1])
            c = int(ind_corr[2])
            
            nuevo_punto_insercion = np.array(obj.InsertionPoint).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
            nuevo_punto_insercion_2d = nuevo_punto_insercion[:,[0,1]] #y le quitamos la z porque esta version es en 2D
            
            cajas_fisicas[i,b,c,[1,2]]= nuevo_punto_insercion_2d
            DCBoxes_ID[i,inv,caja,[1,2]]= nuevo_punto_insercion_2d
            
            
    if info_en_documento_activo==True:                          
        return cajas_fisicas, DCBoxes_ID
    else:
        return None, None
    
           
# def CAD_read_inv_strings_loc(acad, all_blocks, single_block, bloque_inicial, n_bloques, inv_string, String_Inverters_ID, equi_reverse_ibv, handle_inv_string):
#     time.sleep(0.1) #le damos un tiempo para que autocad no se autobloquee
#     info_en_documento_activo=False
#     for obj in acad.iter_objects_fast('BlockReference'):
#         if obj.Layer == "String Inverters":
#             info_en_documento_activo=True
#             handle_extraido = obj.Handle
#             indices_inv_string = np.where(handle_inv_string == handle_extraido)
            
#             bloque = int(indices_inv_string[0][0])
#             board = int(indices_inv_string[1][0])
#             inv_b = int(indices_inv_string[2][0])
            
#             ind_corr = equi_reverse_ibv[bloque,board,inv_b]
                     
#             i = int(ind_corr[0])
#             b = int(ind_corr[1])
#             inv = int(ind_corr[2])
            
#             nuevo_punto_insercion = np.array(obj.InsertionPoint).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
#             nuevo_punto_insercion_2d = nuevo_punto_insercion[:,[0,1]] #y le quitamos la z porque esta version es en 2D
            
#             inv_string[i,b,inv,0,[0,1]]= nuevo_punto_insercion_2d
#             String_Inverters_ID[i,board,inv_b,[1,2]]= nuevo_punto_insercion_2d
            
            
#     if info_en_documento_activo==True:                          
#         return inv_string, String_Inverters_ID
#     else:
#         return None, None    
    
    
def CAD_read_inv_strings_loc(acad, all_blocks, single_block, bloque_inicial, n_bloques, inv_string, String_Inverters_ID, equi_reverse_ibv, dos_inv_por_bloque):
    time.sleep(0.1) #le damos un tiempo para que autocad no se autobloquee
    
    info_en_documento_activo=False
    
    bloques = []
    for obj in acad.iter_objects_fast('BlockReference'):
        if obj.Layer == "String Inverters":
            info_en_documento_activo=True
            
            nuevo_punto_insercion = np.array(obj.InsertionPoint).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
            nuevo_punto_insercion_2d = nuevo_punto_insercion[:,[0,1]] #y le quitamos la z porque esta version es en 2D
 
            bloques.append({
                "handle": obj.Handle,
                "coords": nuevo_punto_insercion_2d,
                "raw_obj": obj  # opcional, si quieres el objeto entero
            })

    textos = []
    for obj in acad.iter_objects_fast(['Text', 'MText']):  # prueba con estos tipos
        if obj.Layer == "String Inverters ID":              
            texto_punto_insercion = np.array(obj.InsertionPoint).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
            texto_punto_insercion_2d = texto_punto_insercion[:,[0,1]] #y le quitamos la z porque esta version es en 2D
    
            textos.append({
                "texto": obj.TextString,
                "coords": texto_punto_insercion_2d,
                "raw_obj": obj
            })


    for bloque in bloques:
        distancias = [np.linalg.norm(bloque["coords"] - t["coords"]) for t in textos]
        idx_min = int(np.argmin(distancias))

        texto_inv = textos[idx_min]['texto']
        parte = texto_inv.replace("INV-", "")  # quita el prefijo
        numeros = parte.split(".")
        numeros = [int(x) for x in numeros]
        
        if dos_inv_por_bloque:                 
            i, board, inv_b = numeros  
        else:
            i, inv_b = numeros
            board = 0  # o el valor que corresponda en tu modelo           
                                                

        ind_corr = equi_reverse_ibv[i,board,inv_b]
                 
        i = int(ind_corr[0])
        b = int(ind_corr[1])
        inv = int(ind_corr[2])
        
       
        inv_string[i,b,inv,0,[0,1]]= bloque["coords"]
        String_Inverters_ID[i,board,inv_b,[1,2]]= bloque["coords"]
        
            
    if info_en_documento_activo==True:                          
        return inv_string, String_Inverters_ID
    else:
        return None, None  


#-----------------------DIBUJAR POLILINEAS DE MEDIA TENSIÓN----------------
    
def CAD_draw_polilineas_MV(acad, pol_cable_MV):
    from pyautocad import APoint, aDouble
    
    colores_MV = [1,1,2,3,4,5,6,7,40,191]
    ind_color = 1
    
    for i in range(1,len(pol_cable_MV)):
        capa_MV= acad.doc.Layers.Add(f'Pol. MV Cable Line {i}')
        
        if ind_color == len(colores_MV):
            ind_color = 1
        capa_MV.color = colores_MV[ind_color]    
        ind_color = ind_color + 1

            
    def dibujar_MV(n_linea, coordenadas_MV): 
        # Filtrar puntos válidos (coordenadas no NaN)
        coordenadas_limpias = coordenadas_MV[~np.isnan(coordenadas_MV).any(axis=1)]
        
        # Definir los puntos
        points = [APoint(x, y) for x, y in coordenadas_limpias]
    
        # Dibujar polilínea
        points_double = aDouble(*[coord for point in points for coord in (point.x, point.y, 0)])
        polilinea_arr = acad.model.AddPolyline(points_double)
        polilinea_arr.ConstantWidth=0.05
        polilinea_arr.Layer = f'Pol. MV Cable Line {n_linea}' 


    for i, linea in enumerate(pol_cable_MV):
        if i==0:
            pass
        else:
            for j, tramo in enumerate(linea):
                if j==0:
                    pass
                else:
                    dibujar_MV(i, tramo[2])

    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents



#----------------------LEER POLILINEAS DE MEDIA TENSIÓN------------------------------

def CAD_read_polilineas_MV(acad, pol_cable_MV):
    
    time.sleep(0.1)  # le damos un tiempo para que AutoCAD no se autobloquee   
    info_en_documento_activo = False

    
    for obj in acad.iter_objects_fast('Polyline'):
        nombre_pol = obj.Layer
        if nombre_pol[:18] == 'Pol. MV Cable Line':
            linea = int(nombre_pol[19:])
            
            coordenadas_pol_MV = np.array(obj.Coordinates).reshape(-1,3)  # de lista plana de 3 elementos a np.array
            coordenadas_pol_MV_2d = coordenadas_pol_MV[:,[0,1]] #y le quitamos la z porque esta version es en 2D     
            
            info_en_documento_activo = True
            
            for j, tramo in enumerate(pol_cable_MV[linea]):
                diff=tramo[0]-coordenadas_pol_MV_2d[0]
                dist = np.linalg.norm(diff)
                if dist < 1:
                    pol_cable_MV[linea][j][2]=coordenadas_pol_MV_2d
   
    
    if not info_en_documento_activo:
        return None
    else:
        return pol_cable_MV
        










# ---------------------DIBUJAR POLILINEAS DE CABLE DE STRING Y DC BUS---------------------------

def CAD_draw_str_bus(acad, all_blocks, single_block, String_o_Bus, bloque_inicial, n_bloques, max_b, max_f_str_b, max_spf, pol_cable_string, pol_DC_Bus):
    from pyautocad import APoint, aDouble
    
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    
    # Creamos las capas asociadas
    capa_string_cable= acad.doc.Layers.Add('Pol. String Cable')
    capa_string_cable.color = 41
    
    capa_DC_Bus= acad.doc.Layers.Add('Pol. DC Bus')
    capa_DC_Bus.color = 253
    
    # Definimos las funciones de dibujo de pyautocad    
    def dibujar_cable_string(coordenadas_cable_string): #PENDIENTE OPTIMIZAR PARA PONER EN FUNCION DEL N DE TUBOS Y NO DE CIRCUITOS
        # Filtrar puntos válidos (coordenadas no NaN)
        coordenadas_limpias = coordenadas_cable_string[~np.isnan(coordenadas_cable_string).any(axis=1)]

        # Definir los puntos
        points = [APoint(x, y) for x, y in coordenadas_limpias]

        # Dibujar polilínea
        points_double = aDouble(*[coord for point in points for coord in (point.x, point.y, 0)])
        polilinea_cs = acad.model.AddPolyline(points_double)
        polilinea_cs.ConstantWidth=0.1
        polilinea_cs.Layer = 'Pol. String Cable'
        # handle = polilinea_cs.Handle

        # return handle  
    
    def dibujar_DC_Bus(coordenadas_DCBus): #PENDIENTE OPTIMIZAR PARA PONER EN FUNCION DEL N DE TUBOS Y NO DE CIRCUITOS
        # Filtrar puntos válidos (coordenadas no NaN)
        coordenadas_limpias = coordenadas_DCBus[~np.isnan(coordenadas_DCBus).any(axis=1)]

        # Definir los puntos
        points = [APoint(x, y) for x, y in coordenadas_limpias]

        # Dibujar polilínea
        points_double = aDouble(*[coord for point in points for coord in (point.x, point.y, 0)])
        polilinea_dcbus = acad.model.AddPolyline(points_double)
        polilinea_dcbus.ConstantWidth=0.1
        polilinea_dcbus.Layer = 'Pol. DC Bus'
        # handle = polilinea_dcbus.Handle
        
        # return handle   
    
    
    #Dibujamos con los valores recibidos
    if all_blocks==True:
        #Dibujar Cable de String
        if String_o_Bus != 'DC Bus':
            for i in range(bloque_inicial,n_bloques+1):
                for b in range(0,max_b):
                    if not np.isnan(pol_cable_string[i,b]).all(): #si la banda no está vacía, no tiene sentido evaluar la f=0 porque a lo mejor empieza la caja con cables de string       
                        for f in range (0,max_f_str_b):      
                            if ~np.isnan(pol_cable_string[i,b,f,0,0,0]): #si la fila no está vacía
                               for s in range (0,max_spf):      
                                   if ~np.isnan(pol_cable_string[i,b,f,s,0,0]): #si el string no está vacío
                                        
                                    # bloque = int(equi_ibfs[i,b,f,s,0])
                                    # inv = int(equi_ibfs[i,b,f,s,1])
                                    # caja = int(equi_ibfs[i,b,f,s,2])
                                    # bus = int(equi_ibfs[i,b,f,s,3])
                                    # stri = int(equi_ibfs[i,b,f,s,4])
                                    
                                    # handle_cable_string[bloque,inv,caja,0,stri]=dibujar_cable_string(pol_cable_string[i,b,f,s])
                                    dibujar_cable_string(pol_cable_string[i,b,f,s])
        #Dibujar DC Bus                        
        if String_o_Bus != 'String Cable':                  
            for i in range(bloque_inicial,n_bloques+1):
                for b in range(0,max_b):
                    if not np.isnan(pol_DC_Bus[i,b]).all(): #si la banda no está vacía, no tiene sentido evaluar la f=0 porque a lo mejor empieza la caja con cables de string
                        for f in range (0,max_f_str_b):      
                            if ~np.isnan(pol_DC_Bus[i,b,f,0,0]): #si la fila no está vacía
                            
                                # bloque = int(equi_ibfs[i,b,f,0,0])
                                # inv = int(equi_ibfs[i,b,f,0,1])
                                # caja = int(equi_ibfs[i,b,f,0,2])
                                # bus = int(equi_ibfs[i,b,f,0,3])
                                
                                # handle_dcbus[bloque,inv,caja,bus]=dibujar_DC_Bus(pol_DC_Bus[i,b,f])   
                                dibujar_DC_Bus(pol_DC_Bus[i,b,f])    
    else: #solo un bloque
        i=single_block
        #Dibujar Cable de String
        if String_o_Bus != 'DC Bus':
            for b in range(0,max_b):
                if not np.isnan(pol_cable_string[i,b]).all(): #si la banda no está vacía, no tiene sentido evaluar la f=0 porque a lo mejor empieza la caja con cables de string       
                    for f in range (0,max_f_str_b):      
                        if ~np.isnan(pol_cable_string[i,b,f,0,0,0]): #si la fila no está vacía 
                           for s in range (0,max_spf):      
                               if ~np.isnan(pol_cable_string[i,b,f,s,0,0]): #si el string no está vacío 
                                   # bloque = int(equi_ibfs[i,b,f,s,0])
                                   # inv = int(equi_ibfs[i,b,f,s,1])
                                   # caja = int(equi_ibfs[i,b,f,s,2])
                                   # bus = int(equi_ibfs[i,b,f,s,3])
                                   # stri = int(equi_ibfs[i,b,f,s,4])
                                    
                                   # handle_cable_string[bloque,inv,caja,0,stri]=dibujar_cable_string(pol_cable_string[i,b,f,s])
                                   dibujar_cable_string(pol_cable_string[i,b,f,s])
                        
        #Dibujar DC Bus                        
        if String_o_Bus != 'String Cable':       
            for b in range(0,max_b):  
                if not np.isnan(pol_DC_Bus[i,b]).all(): #si la banda no está vacía, no tiene sentido evaluar la f=0 porque a lo mejor empieza la caja con cables de string
                    for f in range (0,max_f_str_b):      
                        if ~np.isnan(pol_DC_Bus[i,b,f,0,0]): #si la fila no está vacía
                        
                            # bloque = int(equi_ibfs[i,b,f,0,0])
                            # inv = int(equi_ibfs[i,b,f,0,1])
                            # caja = int(equi_ibfs[i,b,f,0,2])
                            # bus = int(equi_ibfs[i,b,f,0,3])
                            
                            # handle_dcbus[bloque,inv,caja,bus]=dibujar_DC_Bus(pol_DC_Bus[i,b,f])      
                            dibujar_DC_Bus(pol_DC_Bus[i,b,f])  
                            
    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)
    doc = acad.app.ActiveDocument      
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee              
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents
                       
    


# ------------- LEER POLILINEAS DE CABLES DE STRING Y BUS SI SE HAN MODIFICADO (Y UNA PRIMERA VERSION DEL TUBO ASOCIADO)


# def CAD_read_str_bus_opcion_handle(acad, all_blocks, single_block, handle_cable_string, handle_dcbus, equi_reverse_ibfs, pol_cable_string, pol_DC_Bus, pol_tubo_corrugado_zanja_DC):
#     time.sleep(0.1) #le damos un tiempo para que autocad no se autobloquee

#     #Borramos toda la info preexistente en pol_array_cable (toda la variable si es para todos los bloques y solo el bloque designado si es para uno)
#     if all_blocks==True:
#         nueva_pol_cable_string = np.full_like(pol_cable_string,np.nan)
#         nueva_pol_DC_Bus = np.full_like(pol_DC_Bus,np.nan)
#         nueva_pol_tubo_corrugado_zanja_DC = np.full_like(pol_tubo_corrugado_zanja_DC,np.nan)
#     else:
#         nueva_pol_cable_string = pol_cable_string
#         nueva_pol_DC_Bus = pol_DC_Bus
#         nueva_pol_tubo_corrugado_zanja_DC = pol_tubo_corrugado_zanja_DC
        
#         nueva_pol_cable_string[single_block] = np.full_like(pol_cable_string[single_block],np.nan)
#         nueva_pol_DC_Bus[single_block] = np.full_like(pol_DC_Bus[single_block],np.nan)
#         nueva_pol_tubo_corrugado_zanja_DC[single_block] = np.full_like(nueva_pol_tubo_corrugado_zanja_DC[single_block],np.nan)
        
#     unregistered_object = []
#     t=[0]*len(nueva_pol_tubo_corrugado_zanja_DC[:,0]) #el orden en que se guardan los tubos es indiferente
#     for obj in acad.iter_objects_fast('Polyline'):
#         if obj.Layer == "Pol. String Cable":
#             info_en_documento_activo=True
#             handle_extraido = obj.Handle
#             indices_string_cable = np.where(handle_cable_string == handle_extraido)
            
#             if len(indices_string_cable[0]) == 0:
#                 unregistered_object.append(obj.Handle)
#             else:
#                 bloque = int(indices_string_cable[0][0])
#                 inv = int(indices_string_cable[1][0])
#                 caja = int(indices_string_cable[2][0])
#                 bus = int(indices_string_cable[3][0])
#                 stri = int(indices_string_cable[4][0])
                
#                 ind_corr = equi_reverse_ibfs[bloque,inv,caja,bus,stri]
                         
                
#                 i = int(ind_corr[0])
#                 b = int(ind_corr[1])
#                 f = int(ind_corr[2])
#                 s = int(ind_corr[3])
                
#                 nuevas_coordenadas = np.array(obj.Coordinates).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
#                 nuevas_coordenadas_2d = nuevas_coordenadas[:,[0,1]] #y le quitamos la z porque esta version es en 2D
                
#                 aux = np.copy(nueva_pol_cable_string[i,b,f,s])
#                 aux[:nuevas_coordenadas_2d.shape[0], :] = nuevas_coordenadas_2d
#                 nueva_pol_cable_string[i,b,f,s] = aux
                
#                 if s==0:
#                     nueva_pol_tubo_corrugado_zanja_DC[i,t[i]] = nueva_pol_cable_string[i,b,f,0,1:]
#                     t[i]=t[i]+1
            
#         elif obj.Layer == "Pol. DC Bus":
#             info_en_documento_activo=True
#             handle_extraido = obj.Handle
#             indices_DC_Bus = np.where(handle_dcbus == handle_extraido)
            
#             if len(indices_DC_Bus[0]) == 0:
#                 unregistered_object.append(obj.Handle)
#             else:
#                 bloque = int(indices_DC_Bus[0][0])
#                 inv = int(indices_DC_Bus[1][0])
#                 caja = int(indices_DC_Bus[2][0])
#                 bus = int(indices_DC_Bus[3][0])
                
#                 ind_corr = equi_reverse_ibfs[bloque,inv,caja,bus,1]
                
#                 i = int(ind_corr[0])
#                 b = int(ind_corr[1])
#                 f = int(ind_corr[2])
                
#                 nuevas_coordenadas = np.array(obj.Coordinates).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
#                 nuevas_coordenadas_2d = nuevas_coordenadas[:,[0,1]] #y le quitamos la z porque esta version es en 2D
                
#                 aux = np.copy(pol_DC_Bus[i,b,f])
#                 aux[:nuevas_coordenadas_2d.shape[0], :] = nuevas_coordenadas_2d
#                 nueva_pol_DC_Bus[i,b,f] = aux
                
#                 nueva_pol_tubo_corrugado_zanja_DC[i,t[i]] = nueva_pol_DC_Bus[i,b,f,1:]
#                 t[i]=t[i]+1
            
            
#     if info_en_documento_activo==True:
#         return nueva_pol_cable_string, nueva_pol_DC_Bus, nueva_pol_tubo_corrugado_zanja_DC, unregistered_object
#     else:
#         return None, None, None, None, None, None
    


def CAD_read_str_bus_opcion_proximidad(acad, all_blocks, single_block, bloque_inicial, n_bloques, max_b, max_c, max_p, cajas_fisicas, filas_en_cajas, strings_fisicos, pol_cable_string, pol_bus, pol_tubo_corrugado_zanja_DC):
    time.sleep(0.1) #le damos un tiempo para que autocad no se autobloquee
    
    #Borramos toda la info preexistente en pol_cable_string y pol_bus (toda la variable si es para todos los bloques y solo el bloque designado si es para uno)
    if all_blocks==True:
        nueva_pol_cable_string = np.full_like(pol_cable_string,np.nan)
        nueva_pol_bus = np.full_like(pol_bus,np.nan)
        nueva_pol_tubo_corrugado_zanja_DC = np.full_like(pol_tubo_corrugado_zanja_DC,np.nan)

    else:
        nueva_pol_cable_string = pol_cable_string
        nueva_pol_cable_string[single_block] = np.full_like(nueva_pol_cable_string[single_block],np.nan)
        nueva_pol_tubo_corrugado_zanja_DC = pol_tubo_corrugado_zanja_DC
 
        nueva_pol_bus = pol_bus
        nueva_pol_bus[single_block] = np.full_like(pol_bus[single_block],np.nan)
        nueva_pol_tubo_corrugado_zanja_DC[single_block] = np.full_like(nueva_pol_tubo_corrugado_zanja_DC[single_block],np.nan)
    
    #Definimos funcion para asociar cada polilinea con la caja si está en un radio dentro de la tolerancia asumida
    
    def dentro_de_tolerancia(coord_caja, coord_polilinea, tolerancia):
        dist_cuadrada=(coord_caja[0]-coord_polilinea[0])**2+(coord_caja[1]-coord_polilinea[1])**2
        if dist_cuadrada < tolerancia**2:
            return True
        else:
            return False
    
    #Comprobamos el tipo de polilinea para obtener las coordenadas de manera adecuada
    def filtrar_coord_tipos_polilinea(tipo_pol, coords):
        #Si la polilinea se ha metido a mano será del tipo AcDbPolyline, no es del tipo que se estaban insertando AcDb2dPolyline (Polilinea 2D), si nos hemos olvidado de aplanarlo en AutoCAD a polilinea 2D paradojicamente saldrá con X, Y pero sin Z, aunque la otra sale con 3, por lo que hay que añadirle un cero a la Z
        if tipo_pol == "AcDbPolyline":
            if len(coords) % 3 == 0 and coords[3]==0: #si sale bien, con 3 coordenadas siendo cero la tercera
                coords_array = np.array(coords).reshape(-1, 3) 
            elif len(coords) % 2 == 0:
                coords_array = np.array(coords).reshape(-1, 2)
                z = obj.Elevation
                coordenadas_3d = np.hstack([coords_array, np.full((coords_array.shape[0], 1), z)])
            else:
                print(f"Coordenadas mal formateadas: {obj.Handle}")
        else:
            #Leer cordenadas
            coordenadas_3d = np.array(obj.Coordinates).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
            
        #Convertimos a 2D
        coordenadas_2d = coordenadas_3d[:,[0,1]] #y le quitamos la z porque esta version es en 2D

        return coordenadas_2d  
    
    
    #Recorremos todas las polilineas buscando su caja asociada
    procesados = set()
    t=[0]*len(nueva_pol_tubo_corrugado_zanja_DC[:,0]) #el orden en que se guardan los tubos es indiferente
    for obj in acad.iter_objects_fast('Polyline'):
        if obj.Layer == "Pol. String Cable":
            #Evitar fallos de duplicados en API de AutoCAD
            handle = obj.Handle
            if handle in procesados:
                continue
            procesados.add(handle)
            
            #Leer tipo de polilinea y cordenadas
            t_pol = obj.ObjectName
            coords = obj.Coordinates

            coordenadas_extraidas_2d = filtrar_coord_tipos_polilinea(t_pol, coords)
            
            almacen_filas_cajas = []
            
            if all_blocks==True:
                for i in range(bloque_inicial, n_bloques+1):
                    for b in range(0,max_b):
                        if ~np.isnan(cajas_fisicas[i,b,0,0]):
                            for c in range(0,max_c):
                                if ~np.isnan(cajas_fisicas[i,b,c,0]):
                                    if dentro_de_tolerancia(cajas_fisicas[i,b,c,[1,2]],coordenadas_extraidas_2d[-1], 1):
                                        
                                        #Habiendo comprobado que la polilinea va a la caja ahora hay que ver de qué fila fisica se trata
                                        #no hace falta sacar las filas de la caja porque para una misma banda no hay filas con igual x, se puede buscar directamente
                                        idx_fila = np.where(abs(filas_en_cajas[i,b,:,2] - coordenadas_extraidas_2d[0,0]) < 1)[0][0]  #con la x dentro de 1 metro      
                                        #TO DO, Se ha puesto el limite de string en y a 10m por las extensiones manuales para el tubo,apaño de wandoan 2, hay que arreglarlo luego
                                        idx_string = np.where(abs(strings_fisicos[i,b,idx_fila,:,1] - coordenadas_extraidas_2d[0,1]) < 10)[0][0] #buscamos el string asociado al cable por y, con tolerancia de 1m
                                                                                
                                        aux = np.copy(nueva_pol_cable_string[i,b,idx_fila, idx_string])
                                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                        nueva_pol_cable_string[i,b,idx_fila, idx_string] = aux
                                        
                                        if ((i,b,c),coordenadas_extraidas_2d[-1]) in almacen_filas_cajas:
                                            pass
                                        else:
                                            nueva_pol_tubo_corrugado_zanja_DC[i,t[i]] = nueva_pol_cable_string[i,b,idx_fila,0,1:]
                                            almacen_filas_cajas.append(((i,b,c),coordenadas_extraidas_2d[-1]))
                                            t[i]=t[i]+1                                           
                                        break
                            
                                        
                                    elif dentro_de_tolerancia(cajas_fisicas[i,b,c,[1,2]],coordenadas_extraidas_2d[0], 1): #si la polilinea se ha dibujado al reves, de la caja al string     
                                        coordenadas_extraidas_2d = coordenadas_extraidas_2d[::-1] #le damos la vuelta a la polilinea
                                        
                                        idx_fila = np.where(abs(filas_en_cajas[i,b,:,2] - coordenadas_extraidas_2d[0,0]) < 1)[0][0]  #con la x dentro de 1 metro
                                        idx_string = np.where(abs(strings_fisicos[i,b,idx_fila,:,1] - coordenadas_extraidas_2d[0,1]) < 10)[0][0] #buscamos el string asociado al cable por y, con tolerancia de 1m
                                                                                
                                        aux = np.copy(nueva_pol_cable_string[i,b,idx_fila, idx_string])
                                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                        nueva_pol_cable_string[i,b,idx_fila, idx_string] = aux
                                        
                                        if idx_string==0:
                                            nueva_pol_tubo_corrugado_zanja_DC[i,t[i]] = nueva_pol_cable_string[i,b,idx_fila,0,1:]
                                            t[i]=t[i]+1                                           
                                        break

            else:
                i = single_block
                for b in range(0,max_b):
                    if ~np.isnan(cajas_fisicas[i,b,0,0]):
                        for c in range(0,max_c):
                            if ~np.isnan(cajas_fisicas[i,b,c,0]):
                                    if dentro_de_tolerancia(cajas_fisicas[i,b,c,[1,2]],coordenadas_extraidas_2d[-1], 1):
                                        idx_fila = np.where(abs(filas_en_cajas[i,b,:,2] - coordenadas_extraidas_2d[0,0]) < 1)[0][0]  #con la x dentro de 1 metro
                                        idx_string = np.where(abs(strings_fisicos[i,b,idx_fila,:,1] - coordenadas_extraidas_2d[0,1]) < 10)[0][0] #buscamos el string asociado al cable por y, con tolerancia de 1m
                                        
                                        aux = np.copy(nueva_pol_cable_string[i,b,idx_fila, idx_string])
                                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                        nueva_pol_cable_string[i,b,idx_fila, idx_string] = aux

                                        if idx_string==0:
                                            nueva_pol_tubo_corrugado_zanja_DC[i,t[i]] = nueva_pol_cable_string[i,b,idx_fila,0,1:]
                                            t[i]=t[i]+1                                           
                                        break
                                    
                                    elif dentro_de_tolerancia(cajas_fisicas[i,b,c,[1,2]],coordenadas_extraidas_2d[0], 1): #si la polilinea se ha dibujado al reves, de la caja al string
                                        coordenadas_extraidas_2d = coordenadas_extraidas_2d[::-1] #le damos la vuelta a la polilinea
                                        
                                        idx_fila = np.where(abs(filas_en_cajas[i,b,:,2] - coordenadas_extraidas_2d[0,0] < 1)[0][0])  #con la x dentro de 1 metro
                                        idx_string = np.where(abs(strings_fisicos[i,b,idx_fila,:,1] - coordenadas_extraidas_2d[0,1]) < 10)[0][0] #buscamos el string asociado al cable por y, con tolerancia de 1m
                                        
                                        aux = np.copy(nueva_pol_cable_string[i,b,idx_fila, idx_string])
                                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                        nueva_pol_cable_string[i,b,idx_fila, idx_string] = aux
               
                                        if idx_string==0:
                                            nueva_pol_tubo_corrugado_zanja_DC[i,t[i]] = nueva_pol_cable_string[i,b,idx_fila,0,1:]
                                            t[i]=t[i]+1                                            
                                        break
                                    
        elif obj.Layer == "Pol. DC Bus":
            #Evitar fallos de duplicados en API de AutoCAD
            handle = obj.Handle
            if handle in procesados:
                continue
            procesados.add(handle)
            
            #Leer cordenadas
            coordenadas_extraidas = np.array(obj.Coordinates).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
            coordenadas_extraidas_2d = coordenadas_extraidas[:,[0,1]] #y le quitamos la z porque esta version es en 2D
            
            if all_blocks==True:
                for i in range(bloque_inicial, n_bloques+1):
                    for b in range(0,max_b):
                        if ~np.isnan(cajas_fisicas[i,b,0,0]):
                            for c in range(0,max_c):
                                if ~np.isnan(cajas_fisicas[i,b,c,0]):
                                    if dentro_de_tolerancia(cajas_fisicas[i,b,c,[1,2]],coordenadas_extraidas_2d[-1], 1):
                                        
                                        #Habiendo comprobado que la polilinea va a la caja ahora hay que ver de qué fila fisica se trata
                                        #no hace falta sacar las filas de la caja porque para una misma banda no hay filas con igual x, se puede buscar directamente
                                        idx_fila = np.where(abs(filas_en_cajas[i,b,:,2] - coordenadas_extraidas_2d[0,0]) < 1)[0][0]  #con la x dentro de 1 metro
                                       
                                        aux = np.copy(nueva_pol_bus[i,b,idx_fila])
                                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                        nueva_pol_bus[i,b,idx_fila] = aux
                                        
                                        nueva_pol_tubo_corrugado_zanja_DC[i,t[i]] = nueva_pol_bus[i,b,idx_fila,1:]
                                        t[i]=t[i]+1
                                        break

                            
                                        
                                    elif dentro_de_tolerancia(cajas_fisicas[i,b,c,[1,2]],coordenadas_extraidas_2d[0], 1): #si la polilinea se ha dibujado al reves, de la caja al string
                                        coordenadas_extraidas_2d = coordenadas_extraidas_2d[::-1] #le damos la vuelta a la polilinea
                                        idx_fila = np.where(abs(filas_en_cajas[i,b,:,2] - coordenadas_extraidas_2d[0,0]) < 1)[0][0]  #con la x dentro de 1 metro
                                        
                                        aux = np.copy(nueva_pol_bus[i,b,idx_fila])
                                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                        nueva_pol_bus[i,b,idx_fila] = aux
                                        
                                        nueva_pol_tubo_corrugado_zanja_DC[i,t[i]] = nueva_pol_bus[i,b,idx_fila,1:]
                                        t[i]=t[i]+1
                                        break
            else:
                i = single_block
                for b in range(0,max_b):
                    if ~np.isnan(cajas_fisicas[i,b,0,0]):
                        for c in range(0,max_c):
                            if ~np.isnan(cajas_fisicas[i,b,c,0]):
                                    if dentro_de_tolerancia(cajas_fisicas[i,b,c,[1,2]],coordenadas_extraidas_2d[-1], 1):
                                        idx_fila = np.where(abs(filas_en_cajas[i,b,:,2] - coordenadas_extraidas_2d[0,0]) < 1)[0][0]  #con la x dentro de 1 metro
                                       
                                        aux = np.copy(nueva_pol_bus[i,b,idx_fila])
                                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                        nueva_pol_bus[i,b,idx_fila] = aux
                                        
                                        nueva_pol_tubo_corrugado_zanja_DC[i,t[i]] = nueva_pol_bus[i,b,idx_fila,1:]
                                        t[i]=t[i]+1
                                        break
                            
                                        
                                    elif dentro_de_tolerancia(cajas_fisicas[i,b,c,[1,2]],coordenadas_extraidas_2d[0], 1): #si la polilinea se ha dibujado al reves, de la caja al string
                                        coordenadas_extraidas_2d = coordenadas_extraidas_2d[::-1] #le damos la vuelta a la polilinea
                                        
                                        idx_fila = np.where(abs(filas_en_cajas[i,b,:,2] - coordenadas_extraidas_2d[0,0]) < 1)[0][0]  #con la x dentro de 1 metro
                                       
                                        aux = np.copy(nueva_pol_bus[i,b,idx_fila])
                                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                        nueva_pol_bus[i,b,idx_fila] = aux
                                        
                                        nueva_pol_tubo_corrugado_zanja_DC[i,t[i]] = nueva_pol_bus[i,b,idx_fila,1:]
                                        t[i]=t[i]+1
                                        break
    
    # ---- conversión de los tubos a array rectangular ----
    max_tubos_bloque = max(len(lst) for lst in tubos_por_bloque)

    nueva_pol_tubo_corrugado_zanja_DC = np.full((n_bloques+1, max_tubos_bloque, max_p-1, 2), np.nan)

    for i, lista in enumerate(tubos_por_bloque):
        for t, arr in enumerate(lista):
            L = arr.shape[0]
            nueva_pol_tubo_corrugado_zanja_DC[i,t,:L,:] = arr

    
    return nueva_pol_cable_string, nueva_pol_bus, nueva_pol_tubo_corrugado_zanja_DC, max_tubos_bloque




def CAD_read_str_cable_inv_string(acad, all_blocks, single_block, bloque_inicial, n_bloques, max_b, max_inv, max_p, inv_string, strings_fisicos, equi_ibv, equi_ibv_to_fs, strings_ID, pol_cable_string, pol_tubo_corrugado_zanja_DC):
    time.sleep(0.1) #le damos un tiempo para que autocad no se autobloquee
    
    #Borramos toda la info preexistente en pol_cable_string y pol_bus (toda la variable si es para todos los bloques y solo el bloque designado si es para uno)
    if all_blocks==True:
        nueva_pol_cable_string = np.full_like(pol_cable_string,np.nan)

    else:
        nueva_pol_cable_string = pol_cable_string
        nueva_pol_cable_string[single_block] = np.full_like(nueva_pol_cable_string[single_block],np.nan)
        nueva_pol_tubo_corrugado_zanja_DC = pol_tubo_corrugado_zanja_DC
        nueva_pol_tubo_corrugado_zanja_DC[single_block] = np.full_like(nueva_pol_tubo_corrugado_zanja_DC[single_block],np.nan) #TO DO, CORREGIR PARA nueva logica
    
    #Definimos funcion para asociar cada polilinea con la caja si está en un radio dentro de la tolerancia asumida
    
    def dentro_de_tolerancia(coord_caja, coord_polilinea, tolerancia):
        dist_cuadrada=(coord_caja[0]-coord_polilinea[0])**2+(coord_caja[1]-coord_polilinea[1])**2
        if dist_cuadrada < tolerancia**2:
            return True
        else:
            return False
    
    #Comprobamos el tipo de polilinea para obtener las coordenadas de manera adecuada
    def filtrar_coord_tipos_polilinea(tipo_pol, coords):
        #Si la polilinea se ha metido a mano será del tipo AcDbPolyline, no es del tipo que se estaban insertando AcDb2dPolyline (Polilinea 2D), si nos hemos olvidado de aplanarlo en AutoCAD a polilinea 2D paradojicamente saldrá con X, Y pero sin Z, aunque la otra sale con 3, por lo que hay que añadirle un cero a la Z
        if tipo_pol == "AcDbPolyline":
            if len(coords) % 3 == 0 and coords[3]==0: #si sale bien, con 3 coordenadas siendo cero la tercera
                coords_array = np.array(coords).reshape(-1, 3) 
            elif len(coords) % 2 == 0:
                coords_array = np.array(coords).reshape(-1, 2)
                z = obj.Elevation
                coordenadas_3d = np.hstack([coords_array, np.full((coords_array.shape[0], 1), z)])
            else:
                print(f"Coordenadas mal formateadas: {obj.Handle}")
        else:
            #Leer cordenadas
            coordenadas_3d = np.array(obj.Coordinates).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
            
        #Convertimos a 2D
        coordenadas_2d = coordenadas_3d[:,[0,1]] #y le quitamos la z porque esta version es en 2D

        return coordenadas_2d  
    
    
    #Recorremos todas las polilineas buscando su caja asociada
    procesados = set()
    sids_usados = set()
    almacen_filas_cajas = []
    tubos_por_bloque = [[] for _ in range(n_bloques+1)]     #El orden en que se guardan los tubos es indiferente
    
    for obj in acad.iter_objects_fast('Polyline'):
        if obj.Layer == "Pol. String Cable":
            #Evitar fallos de duplicados en API de AutoCAD
            handle = obj.Handle
            if handle in procesados:
                continue
            procesados.add(handle)
            
            #Leer tipo de polilinea y cordenadas
            t_pol = obj.ObjectName
            coords = obj.Coordinates

            coordenadas_extraidas_2d = filtrar_coord_tipos_polilinea(t_pol, coords)
            
            if all_blocks==True:
                for i in range(bloque_inicial, n_bloques+1):
                    for b in range(0,max_b):
                        if ~np.isnan(inv_string[i,b,1,0,0]):
                            for inv in range(1,max_inv):
                                if ~np.isnan(inv_string[i,b,inv,0,0]):
                                    if dentro_de_tolerancia(inv_string[i,b,inv,0,[0,1]],coordenadas_extraidas_2d[-1], 1):
                                        
                                        #Habiendo comprobado que la polilinea va a la caja ahora hay que ver de qué fila y string fisicos
                                        #En el caso de inversores de strings como ya se tiene el inversor se puede determinar que string global de los asociados es el que le toca y sacar del equi_ibv_to_fs fila y string
                                        #Como inv_string tiene info de strings fisicos pero los strings pueden estar girados hay que evaluar sobre Strings_ID para el punto de inicio

                                        board_equi = int(equi_ibv[i,b,inv,1])
                                        inv_equi = int(equi_ibv[i,b,inv,2])
                                        
                                        x_array = np.array(strings_ID[i, board_equi, inv_equi, :, 1], dtype=float)
                                        y_array = np.array(strings_ID[i, board_equi, inv_equi, :, 3], dtype=float)
                                        
                                        x_obj = float(coordenadas_extraidas_2d[0, 0])
                                        y_obj = float(coordenadas_extraidas_2d[0, 1])
                                        
                                        distancias = np.sqrt((x_array - x_obj)**2 + (y_array - y_obj)**2)

                                        # Obtenemos el que esta a menos de 2 metros (ojo que puede haber dos si se han girado strings y salen por mitad del tracker)
                                        candidatos = np.argwhere(distancias <= 2)
                                        for idx_str_candidato in candidatos:
                                            sid_candidato = int(strings_ID[i,board_equi,inv_equi,idx_str_candidato,4])
 
                                            if sid_candidato in sids_usados:
                                                pass
                                            else:
                                                sid = sid_candidato
                                                sids_usados.add(sid)
                                                break
                                                
                                        
                                        #Con el global, seleccionamos el indice en ibv correcto, pues coincide con el de equi_ibv_to_fs y la identificacion es inmediata
                                        ind_str_ibv = np.argwhere(inv_string[i,b,inv,:,2] == sid)[0]
                                       
                                        idx_banda = int(equi_ibv_to_fs[i,b,inv,ind_str_ibv,0])
                                        idx_fila = int(equi_ibv_to_fs[i,b,inv,ind_str_ibv,1])
                                        idx_string = int(equi_ibv_to_fs[i,b,inv,ind_str_ibv,2])
                                        
                                        aux = np.copy(nueva_pol_cable_string[i,idx_banda,idx_fila, idx_string])
                                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                        nueva_pol_cable_string[i,idx_banda,idx_fila, idx_string] = aux
                                        
                                        if (i,b,inv,idx_fila) in almacen_filas_cajas:
                                            pass
                                        else:
                                            tubos_por_bloque[i].append(nueva_pol_cable_string[i,idx_banda,idx_fila, idx_string,1:])
                                            almacen_filas_cajas.append((i,b,inv,idx_fila))                                                                                     
                                        break
                                    
                            
                                        
                                    elif dentro_de_tolerancia(inv_string[i,b,inv,0,[0,1]],coordenadas_extraidas_2d[0], 1): #si la polilinea se ha dibujado al reves, de la caja al string     
                                        coordenadas_extraidas_2d = coordenadas_extraidas_2d[::-1] #le damos la vuelta a la polilinea
                                        
                                        board_equi = int(equi_ibv[i,b,inv,1])
                                        inv_equi = int(equi_ibv[i,b,inv,2])
                                        
                                        x_array = np.array(strings_ID[i, board_equi, inv_equi, :, 1], dtype=float)
                                        y_array = np.array(strings_ID[i, board_equi, inv_equi, :, 3], dtype=float)
                                        
                                        x_obj = float(coordenadas_extraidas_2d[-1, 0])
                                        y_obj = float(coordenadas_extraidas_2d[-1, 1])
                                        
                                        distancias = np.sqrt((x_array - x_obj)**2 + (y_array - y_obj)**2)
                                        
                                        # Obtenemos el que esta a menso de dos metros
                                        candidatos = np.argwhere(distancias <= 2)
                                        for idx_str_candidato in candidatos:
                                            sid_candidato = int(strings_ID[i,board_equi,inv_equi,idx_str_candidato,4])
                                            if sid_candidato in sids_usados:
                                                pass
                                            else:
                                                sid = sid_candidato   
                                                sids_usados.add(sid)
                                                break
                                        
                                        #Con el global, seleccionamos el indice en ibv correcto, pues coincide con el de equi_ibv_to_fs y la identificacion es inmediata
                                        ind_str_ibv = np.argwhere(inv_string[i,b,inv,:,2] == sid)[0]
                                       
                                        idx_banda = int(equi_ibv_to_fs[i,b,inv,ind_str_ibv,0])
                                        idx_fila = int(equi_ibv_to_fs[i,b,inv,ind_str_ibv,1])
                                        idx_string = int(equi_ibv_to_fs[i,b,inv,ind_str_ibv,2])
                                        
                                        aux = np.copy(nueva_pol_cable_string[i,idx_banda,idx_fila, idx_string])
                                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                        nueva_pol_cable_string[i,idx_banda,idx_fila, idx_string] = aux
                                        
                                        if (i,b,inv,idx_fila) in almacen_filas_cajas:
                                            pass
                                        else:
                                            tubos_por_bloque[i].append(nueva_pol_cable_string[i,idx_banda,idx_fila, idx_string,1:])
                                            almacen_filas_cajas.append((i,b,inv,idx_fila))                                                                                     
                                        break
                                    
            else:
                i=single_block
                for b in range(0,max_b):
                    if ~np.isnan(inv_string[i,b,1,0,0]):
                        for inv in range(1,max_inv):
                            if ~np.isnan(inv_string[i,b,inv,0,0]):
                                if dentro_de_tolerancia(inv_string[i,b,inv,0,[0,1]],coordenadas_extraidas_2d[-1], 1):
                                    
                                    #Habiendo comprobado que la polilinea va a la caja ahora hay que ver de qué fila y string fisicos
                                    #En el caso de inversores de strings como ya se tiene el inversor se puede determinar que string global de los asociados es el que le toca y sacar del equi_ibv_to_fs fila y string
                                    #Como inv_string tiene info de strings fisicos pero los strings pueden estar girados hay que evaluar sobre Strings_ID para el punto de inicio

                                    board_equi = int(equi_ibv[i,b,inv,1])
                                    inv_equi = int(equi_ibv[i,b,inv,2])
                                    
                                    x_array = np.array(strings_ID[i, board_equi, inv_equi, :, 1], dtype=float)
                                    y_array = np.array(strings_ID[i, board_equi, inv_equi, :, 3], dtype=float)
                                    
                                    x_obj = float(coordenadas_extraidas_2d[0, 0])
                                    y_obj = float(coordenadas_extraidas_2d[0, 1])
                                    
                                    distancias = np.sqrt((x_array - x_obj)**2 + (y_array - y_obj)**2)

                                    # Obtenemos el que esta a menos de dos metros
                                    candidatos = np.argwhere(distancias <= 2)
                                    for idx_str_candidato in candidatos:
                                        sid_candidato = int(strings_ID[i,board_equi,inv_equi,idx_str_candidato,4])
                                        if sid_candidato in sids_usados:
                                            pass
                                        else:
                                            sid = sid_candidato
                                            sids_usados.add(sid)
                                            break
                                                
                                    #Con el global, seleccionamos el indice en ibv correcto, pues coincide con el de equi_ibv_to_fs y la identificacion es inmediata
                                    ind_str_ibv = np.argwhere(inv_string[i,b,inv,:,2] == sid)[0]
                                   
                                    idx_banda = int(equi_ibv_to_fs[i,b,inv,ind_str_ibv,0])
                                    idx_fila = int(equi_ibv_to_fs[i,b,inv,ind_str_ibv,1])
                                    idx_string = int(equi_ibv_to_fs[i,b,inv,ind_str_ibv,2])
                                    
                                    aux = np.copy(nueva_pol_cable_string[i,idx_banda,idx_fila, idx_string])
                                    aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                    nueva_pol_cable_string[i,idx_banda,idx_fila, idx_string] = aux
                                    
                                    if idx_string==0:
                                        nueva_pol_tubo_corrugado_zanja_DC[i,t[i]] = nueva_pol_cable_string[i,b,idx_fila,0,1:]
                                        t[i]=t[i]+1                                           
                                    break
                        
                                    
                                elif dentro_de_tolerancia(inv_string[i,b,inv,0,[0,1]],coordenadas_extraidas_2d[0], 1): #si la polilinea se ha dibujado al reves, de la caja al string     
                                    coordenadas_extraidas_2d = coordenadas_extraidas_2d[::-1] #le damos la vuelta a la polilinea
                                    
                                    board_equi = int(equi_ibv[i,b,inv,1])
                                    inv_equi = int(equi_ibv[i,b,inv,2])
                                    
                                    x_array = np.array(strings_ID[i, board_equi, inv_equi, :, 1], dtype=float)
                                    y_array = np.array(strings_ID[i, board_equi, inv_equi, :, 3], dtype=float)
                                    
                                    x_obj = float(coordenadas_extraidas_2d[-1, 0])
                                    y_obj = float(coordenadas_extraidas_2d[-1, 1])
                                    
                                    distancias = np.sqrt((x_array - x_obj)**2 + (y_array - y_obj)**2)
                                    
                                    # Obtenemos el que esta a menos de dos metros
                                    candidatos = np.argwhere(distancias <= 2)
                                    for idx_str_candidato in candidatos:
                                        sid_candidato = int(strings_ID[i,board_equi,inv_equi,idx_str_candidato,4])
                                        if sid_candidato in sids_usados:
                                            pass
                                        else:
                                            sid = sid_candidato
                                            sids_usados.add(sid)
                                            break
                                                
                                    #Con el global, seleccionamos el indice en ibv correcto, pues coincide con el de equi_ibv_to_fs y la identificacion es inmediata
                                    ind_str_ibv = np.argwhere(inv_string[i,b,inv,:,2] == sid)[0]
                                   
                                    idx_banda = int(equi_ibv_to_fs[i,b,inv,ind_str_ibv,0])
                                    idx_fila = int(equi_ibv_to_fs[i,b,inv,ind_str_ibv,1])
                                    idx_string = int(equi_ibv_to_fs[i,b,inv,ind_str_ibv,2])
                                    
                                    aux = np.copy(nueva_pol_cable_string[i,idx_banda,idx_fila, idx_string])
                                    aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                    nueva_pol_cable_string[i,idx_banda,idx_fila, idx_string] = aux
                                    
                                    if idx_string==0:
                                        nueva_pol_tubo_corrugado_zanja_DC[i,t[i]] = nueva_pol_cable_string[i,b,idx_fila,0,1:]
                                        t[i]=t[i]+1                                           
                                    break

    # ---- conversión de los tubos a array rectangular ----
    max_tubos_bloque = max(len(lst) for lst in tubos_por_bloque)

    nueva_pol_tubo_corrugado_zanja_DC = np.full((n_bloques+1, max_tubos_bloque, max_p-1, 2), np.nan)

    for i, lista in enumerate(tubos_por_bloque):
        for t, arr in enumerate(lista):
            L = arr.shape[0]
            nueva_pol_tubo_corrugado_zanja_DC[i,t,:L,:] = arr

    return nueva_pol_cable_string, None, nueva_pol_tubo_corrugado_zanja_DC, max_tubos_bloque

    
# -------------------DIBUJAR TUBOS EN ZANJAS DC--------------------------
def CAD_draw_tubo_DC(acad, all_blocks, single_block, bloque_inicial, n_bloques, max_tubo_bloque, pol_tubo_corrugado_zanja_DC):
    from pyautocad import APoint, aDouble
    
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    
    # Creamos las capas asociadas
    
    capa_array= acad.doc.Layers.Add('Pol. DC Conduit')
    capa_array.color = 30
    
    
    # Definimos las funciones de dibujo de pyautocad
    def dibujar_tubo_DC(coordenadas_AASS_LVAC): 
        # Filtrar puntos válidos (coordenadas no NaN)
        coordenadas_limpias = coordenadas_AASS_LVAC[~np.isnan(coordenadas_AASS_LVAC).any(axis=1)]
        
        # Definir los puntos
        points = [APoint(x, y) for x, y in coordenadas_limpias]
    
        # Dibujar polilínea
        points_double = aDouble(*[coord for point in points for coord in (point.x, point.y, 0)])
        polilinea_arr = acad.model.AddPolyline(points_double)
        polilinea_arr.ConstantWidth=0.1
        polilinea_arr.Layer = 'Pol. DC Conduit'

    #Dibujamos con los valores recibidos
    if all_blocks==True:
        for i in range(bloque_inicial,n_bloques+1):     
            for t in range (0,max_tubo_bloque):      
                if ~np.isnan(pol_tubo_corrugado_zanja_DC[i,t,0,0]): #si el tubo no está vacío                                                    
                    dibujar_tubo_DC(pol_tubo_corrugado_zanja_DC[i,t])
                            
    else: #solo un bloque
        i=single_block
        for i in range(bloque_inicial,n_bloques+1):     
            for t in range (0,max_tubo_bloque):      
                if ~np.isnan(pol_tubo_corrugado_zanja_DC[i,t,0,0]): #si el tubo no está vacío                                                    
                    dibujar_tubo_DC(pol_tubo_corrugado_zanja_DC[i,t])
                        
    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents    
    




# ------------- LEER TUBO ZANJAS DC---------------------------
#El bloque se va a sacar por cercania al string mas cercano al tubo, el resto da igual, no nos importa que un tubo que antes estuviese en el indice 1 se haya intercambiado por el indice 5 porque no se saca schedule asociado a strings ni trackers

def CAD_read_tubo_zanja_DC(acad, all_blocks, single_block, bloque_inicial, n_bloques, max_p, strings_fisicos, pol_tubo_corrugado_zanja_DC):
    time.sleep(0.1) #le damos un tiempo para que autocad no se autobloquee
    
    #Borramos toda la info preexistente en pol_array_cable (toda la variable si es para todos los bloques y solo el bloque designado si es para uno)
    if all_blocks==True:
        nueva_pol_tubo_corrugado_zanja_DC = np.full_like(pol_tubo_corrugado_zanja_DC,np.nan)
        lista_tubos = [[] for _ in range(n_bloques + 1)]
    else:
        nueva_pol_tubo_corrugado_zanja_DC = pol_tubo_corrugado_zanja_DC
        nueva_pol_tubo_corrugado_zanja_DC[single_block] = np.full_like(nueva_pol_tubo_corrugado_zanja_DC[single_block],np.nan)
        lista_tubos=[]

    
    #Extraemos coordenadas y buscamos el bloque asociado
    procesados = set()
    for obj in acad.iter_objects_fast('Polyline'):
        if obj.Layer == "Pol. DC Conduit":
            #Evitar fallos de duplicados en API de AutoCAD
            handle = obj.Handle
            if handle in procesados:
                continue
            procesados.add(handle)
            
            #Leer cordenadas
            coordenadas_extraidas = np.array(obj.Coordinates).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
            coordenadas_extraidas_2d = coordenadas_extraidas[:,[0,1]] #y le quitamos la z porque esta version es en 2D
            
            
            if all_blocks==True:
                diff = strings_fisicos[...,:2] - coordenadas_extraidas_2d[0]
                dist_cuadrado = np.sum(diff**2, axis=-1)
                mask_valid = ~np.isnan(dist_cuadrado)

                # Asignamos un valor grande a los que son NaN (para que no los escoja como mínimos)
                dist_cuadrado_masked = np.where(mask_valid, dist_cuadrado, np.inf)
                min_index_flat = np.argmin(dist_cuadrado_masked)
                i_min, b_min, f_min, s_min = np.unravel_index(min_index_flat, dist_cuadrado.shape)

                lista_tubos[i_min].append(coordenadas_extraidas_2d)

            else:
                lista_tubos.append(coordenadas_extraidas_2d)

    
    #Una vez realizada toda la extraccion en las listas analizamos los datos y sacamos el array
    if all_blocks==True:            
        max_tubos_bloque = max(len(tubos) for tubos in lista_tubos)
        
        nueva_pol_tubo_corrugado_zanja_DC = np.full((n_bloques+1,max_tubos_bloque,max_p-1,2),np.nan)
        
        for i, tubos in enumerate(lista_tubos):
            for t, tubo in enumerate(tubos):
                p_nuevo = tubo.shape[0]
                nueva_pol_tubo_corrugado_zanja_DC[i, t, :p_nuevo, :] = tubo
    else:
        max_tubos = len(lista_tubos)
        max_tubos_global = pol_tubo_corrugado_zanja_DC.shape[1]
        
        max_tubos_bloque = max(max_tubos, max_tubos_global)
        
        nueva_pol_tubo_corrugado_zanja_DC = np.full((n_bloques+1, max_tubos_bloque, max_p-1, 2), np.nan)
        
        # Copiamos los datos antiguos para todos los bloques excepto el que estamos actualizando
        for idx in range(n_bloques + 1):
            if idx == single_block:
                continue
        
            t_existente = pol_tubo_corrugado_zanja_DC.shape[1]
            nueva_pol_tubo_corrugado_zanja_DC[idx, :t_existente, :, :] = pol_tubo_corrugado_zanja_DC[idx]
            
        #Insertamos los nuevos tubos en el bloque actual
        for t, tubo in enumerate(lista_tubos):
            p_nuevo = tubo.shape[0]
            nueva_pol_tubo_corrugado_zanja_DC[single_block, t, :p_nuevo, :] = tubo


    return nueva_pol_tubo_corrugado_zanja_DC, max_tubos_bloque

    
# ----------------DIBUJAR POLILINEAS DE CABLE DE ARRAY----------------

def CAD_draw_array(acad, all_blocks, single_block, handle_cable_array, String_o_Bus, bloque_inicial, n_bloques, max_b, max_c, equi_ibc, pol_array_cable):
    from pyautocad import APoint, aDouble
    
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    
    # Creamos las capas asociadas
    
    capa_array= acad.doc.Layers.Add('Pol. Array Cable')
    capa_array.color = 9       
    
    # Definimos la funcion de dibujo de pyautocad
    def dibujar_array(coordenadas_array): 
        # Filtrar puntos válidos (coordenadas no NaN)
        coordenadas_limpias = coordenadas_array[~np.isnan(coordenadas_array).any(axis=1)]
        
        # Definir los puntos
        points = [APoint(x, y) for x, y in coordenadas_limpias]
    
        # Dibujar polilínea
        points_double = aDouble(*[coord for point in points for coord in (point.x, point.y, 0)])
        polilinea_arr = acad.model.AddPolyline(points_double)
        polilinea_arr.ConstantWidth=0.1
        polilinea_arr.Layer = 'Pol. Array Cable'
        # handle = polilinea_arr.Handle
        # return handle   

    #Dibujamos con los valores recibidos
    if all_blocks==True:            
        for i in range(bloque_inicial,n_bloques+1):
            for b in range(0,max_b):
                if ~np.isnan(pol_array_cable[i,b,0,0,0]): #si la banda no está vacía       
                    for c in range (0,max_c):      
                        if ~np.isnan(pol_array_cable[i,b,c,0,0]): #si la caja no está vacía
                        
                            # bloque = int(equi_ibc[i,b,c,0])
                            # inv = int(equi_ibc[i,b,c,1])
                            # caja = int(equi_ibc[i,b,c,2])     
                            # handle_cable_array[bloque,inv,caja]=dibujar_array(pol_array_cable[i,b,c]) 
                            
                            dibujar_array(pol_array_cable[i,b,c])
    else:
        i = single_block
        for b in range(0,max_b):
            if ~np.isnan(pol_array_cable[i,b,0,0,0]): #si la banda no está vacía       
                for c in range (0,max_c):      
                    if ~np.isnan(pol_array_cable[i,b,c,0,0]): #si la caja no está vacía
                    
                        # bloque = int(equi_ibc[i,b,c,0])
                        # inv = int(equi_ibc[i,b,c,1])
                        # caja = int(equi_ibc[i,b,c,2])
                        # handle_cable_array[bloque,inv,caja]=dibujar_array(pol_array_cable[i,b,c]) 
                        
                        dibujar_array(pol_array_cable[i,b,c]) 
                        
    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents
        
    # return handle_cable_array        
        
        
        
# ------------- LEER POLILINEAS DE CABLES DE ARRAY SI SE HAN MODIFICADO


def CAD_read_array_opcion_handle(acad, handle_array_cable, equi_reverse_ibc, pol_array_cable):
    time.sleep(0.1) #le damos un tiempo para que autocad no se autobloquee
    # for obj in dwg.ModelSpace:
    for obj in acad.iter_objects_fast('Polyline'):
        if obj.Layer == "Pol. Array Cable":
            handle_extraido = obj.Handle
            indices_array_cable = np.where(handle_array_cable == handle_extraido)
            
            if indices_array_cable != []:
                bloque = int(indices_array_cable[0][0])
                inv = int(indices_array_cable[1][0])
                caja = int(indices_array_cable[2][0])
                
                ind_corr = equi_reverse_ibc[bloque,inv,caja]
                
                
                i = int(ind_corr[0])
                b = int(ind_corr[1])
                c = int(ind_corr[2])
                
                nuevas_coordenadas = np.array(obj.Coordinates).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
                nuevas_coordenadas_2d = nuevas_coordenadas[:,[0,1]] #y le quitamos la z porque esta version es en 2D
                
                aux = np.full_like(pol_array_cable[i,b,c], np.nan)
                aux[:nuevas_coordenadas_2d.shape[0], :] = nuevas_coordenadas_2d
                pol_array_cable[i,b,c] = aux
    
    return pol_array_cable
        
        
        
        
def CAD_read_array_opcion_proximidad(acad, all_blocks, single_block, bloque_inicial, n_bloques, max_b, max_c, cajas_fisicas, pol_array_cable):
    time.sleep(0.1) #le damos un tiempo para que autocad no se autobloquee
    
    #Borramos toda la info preexistente en pol_array_cable (toda la variable si es para todos los bloques y solo el bloque designado si es para uno)
    if all_blocks==True:
        nueva_pol_array_cable = np.full_like(pol_array_cable,np.nan)
    else:
        nueva_pol_array_cable = pol_array_cable
        nueva_pol_array_cable[single_block] = np.full_like(pol_array_cable[single_block],np.nan)
    
    #Definimos funcion para asociar cada polilinea con la caja si está en un radio dentro de la tolerancia asumida
    
    def dentro_de_tolerancia(coord_caja, coord_array, tolerancia):
        dist_cuadrada=(coord_caja[0]-coord_array[0])**2+(coord_caja[1]-coord_array[1])**2
        if dist_cuadrada < tolerancia**2:
            return True
        else:
            return False
    
    #Comprobamos el tipo de polilinea para obtener las coordenadas de manera adecuada
    def filtrar_coord_tipos_polilinea(tipo_pol, coords):
        #Si la polilinea se ha metido a mano será del tipo AcDbPolyline, no es del tipo que se estaban insertando AcDb2dPolyline (Polilinea 2D), si nos hemos olvidado de aplanarlo en AutoCAD a polilinea 2D paradojicamente saldrá con X, Y pero sin Z, aunque la otra sale con 3, por lo que hay que añadirle un cero a la Z
        if tipo_pol == "AcDbPolyline":
            if len(coords) % 3 == 0 and coords[3]==0: #si sale bien, con 3 coordenadas siendo cero la tercera
                coords_array = np.array(coords).reshape(-1, 3) 
            elif len(coords) % 2 == 0:
                coords_array = np.array(coords).reshape(-1, 2)
                z = obj.Elevation
                coordenadas_3d = np.hstack([coords_array, np.full((coords_array.shape[0], 1), z)])
            else:
                print(f"Coordenadas mal formateadas: {obj.Handle}")
        else:
            #Leer cordenadas
            coordenadas_3d = np.array(obj.Coordinates).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
            
        #Convertimos a 2D
        coordenadas_2d = coordenadas_3d[:,[0,1]] #y le quitamos la z porque esta version es en 2D

        return coordenadas_2d                

            

    #Recorremos todas las polilineas de array buscando su caja asociada
    # for obj in dwg.ModelSpace:
    procesados = set()
    
    for obj in acad.iter_objects_fast('Polyline'):
        if obj.Layer == "Pol. Array Cable":
            #Evitar fallos de duplicados en API de AutoCAD
            handle = obj.Handle
            if handle in procesados:
                continue
            procesados.add(handle)
            
            #Leer tipo de polilinea y coordenadas
            t_pol = obj.ObjectName
            coords = obj.Coordinates

            coordenadas_extraidas_2d = filtrar_coord_tipos_polilinea(t_pol, coords)

            if all_blocks==True:
                for i in range(bloque_inicial, n_bloques+1):
                    for b in range(0,max_b):
                        if ~np.isnan(cajas_fisicas[i,b,0,0]):
                            for c in range(0,max_c):
                                if ~np.isnan(cajas_fisicas[i,b,c,0]):
                                    if dentro_de_tolerancia(cajas_fisicas[i,b,c,[1,2]],coordenadas_extraidas_2d[0], 1):
                                        aux = np.copy(nueva_pol_array_cable[i,b,c])
                                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                        nueva_pol_array_cable[i,b,c] = aux
                                        break
                            
                                        
                                    elif dentro_de_tolerancia(cajas_fisicas[i,b,c,[1,2]],coordenadas_extraidas_2d[-1], 1): #si la polilinea se ha dibujado al reves, de la PCS a la caja
                                        aux = np.copy(nueva_pol_array_cable[i,b,c])
                                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d[::-1,:]
                                        nueva_pol_array_cable[i,b,c] = aux
                                        break

            else:
                i = single_block
                for b in range(0,max_b):
                    if ~np.isnan(cajas_fisicas[i,b,0,0]):
                        for c in range(0,max_c):
                            if ~np.isnan(cajas_fisicas[i,b,c,0]):
                                if dentro_de_tolerancia(cajas_fisicas[i,b,c,[1,2]],coordenadas_extraidas_2d[0], 1):
                                    aux = np.copy(nueva_pol_array_cable[i,b,c])
                                    aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                                    nueva_pol_array_cable[i,b,c] = aux
                                    break
                                
                                elif dentro_de_tolerancia(cajas_fisicas[i,b,c,[1,2]],coordenadas_extraidas_2d[-1], 1): #si la polilinea se ha dibujado al reves, de la PCS a la caja
                                    aux = np.copy(nueva_pol_array_cable[i,b,c])
                                    aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d[::-1,:]
                                    nueva_pol_array_cable[i,b,c] = aux
                                    break
    
    return nueva_pol_array_cable

        
        
        
        
        
#-----------------------------------DIBUJAR POLILINEAS DE AASS LVAC Y ETHERNET-----------------------------------
        
def CAD_draw_AASS_LVAC_y_ethernet(acad, bloque_inicial, n_bloques, pol_AASS_LVAC, pol_ethernet, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC):
    from pyautocad import APoint, aDouble
    
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    
    # Creamos las capas asociadas
    
    capa_array= acad.doc.Layers.Add('Pol. AASS LVAC')
    capa_array.color = 10

    capa_array= acad.doc.Layers.Add('Pol. CCTV LVAC')
    capa_array.color = 10
        
    capa_array= acad.doc.Layers.Add('Pol. O&M LVAC')
    capa_array.color = 10
    
    capa_array= acad.doc.Layers.Add('Pol. Warehouse LVAC')
    capa_array.color = 10
    
    capa_array= acad.doc.Layers.Add('Pol. Ethernet')
    capa_array.color = 90       
    
    # Definimos las funciones de dibujo de pyautocad
    def dibujar_LVAC(coordenadas_AASS_LVAC, capa): 
        # Filtrar puntos válidos (coordenadas no NaN)
        coordenadas_limpias = coordenadas_AASS_LVAC[~np.isnan(coordenadas_AASS_LVAC).any(axis=1)]
        
        # Definir los puntos
        points = [APoint(x, y) for x, y in coordenadas_limpias]
    
        # Dibujar polilínea
        points_double = aDouble(*[coord for point in points for coord in (point.x, point.y, 0)])
        polilinea_arr = acad.model.AddPolyline(points_double)
        polilinea_arr.ConstantWidth=0.1
        polilinea_arr.Layer = capa 
            
    def dibujar_ethernet(coordenadas_ethernet): 
        # Filtrar puntos válidos (coordenadas no NaN)
        coordenadas_limpias = coordenadas_ethernet[~np.isnan(coordenadas_ethernet).any(axis=1)]
        
        # Definir los puntos
        points = [APoint(x, y) for x, y in coordenadas_limpias]
    
        # Dibujar polilínea
        points_double = aDouble(*[coord for point in points for coord in (point.x, point.y, 0)])
        polilinea_arr = acad.model.AddPolyline(points_double)
        polilinea_arr.ConstantWidth=0.05
        polilinea_arr.Layer = 'Pol. Ethernet' 

    #Dibujamos con los valores recibidos
    for i in range(bloque_inicial,n_bloques+1):
        for j in range(0,len(pol_AASS_LVAC[0,:,0,0])):
            if ~np.isnan(pol_AASS_LVAC[i,j,0,0]):
                dibujar_LVAC(pol_AASS_LVAC[i,j],'Pol. AASS LVAC') 

    for i in range(bloque_inicial,n_bloques+1):
        for j in range(0,len(pol_ethernet[0,:,0,0])):
            if ~np.isnan(pol_ethernet[i,j,0,0]):
                dibujar_ethernet(pol_ethernet[i,j]) 
    
    for linea in pol_CCTV_LVAC:
        coords = np.array(linea).reshape(-1,2)
        dibujar_LVAC(coords, 'Pol. CCTV LVAC')     

    for linea in pol_OyM_supply_LVAC:
        coords = np.array(linea).reshape(-1,2)
        dibujar_LVAC(coords, 'Pol. O&M LVAC')
        
    for linea in pol_Warehouse_supply_LVAC:
        coords = np.array(linea).reshape(-1,2)
        dibujar_LVAC(coords, 'Pol. Warehouse LVAC') 
        
    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents
                    


#----------------------LEER AASS LVAC Y ETHERNET------------------------------

def CAD_read_AASS_LVAC_y_ethernet(acad, bloque_inicial, n_bloques, pol_AASS_LVAC, pol_ethernet, coord_Comboxes, coord_Tracknets, coord_TBoxes, coord_AWS, coord_PCS_AASS_inputs):
    time.sleep(0.1) #le damos un tiempo para que autocad no se autobloquee
    
    #Borramos toda la info preexistente en pol_AASS_LVAC y pol_ethernet
    nueva_pol_AASS_LVAC = np.full_like(pol_AASS_LVAC,np.nan)
    nueva_pol_ethernet = np.full_like(pol_ethernet,np.nan)
    nueva_pol_CCTV_LVAC =[]
    nueva_pol_OyM_supply_LVAC = []
    nueva_pol_Warehouse_supply_LVAC = []
    
    #Definimos funcion para asociar cada polilinea con la caja si está en un radio dentro de la tolerancia asumida
    def dentro_de_tolerancia(coord_caja, coord_array, tolerancia):
        dist_cuadrada=(coord_caja[0]-coord_array[0])**2+(coord_caja[1]-coord_array[1])**2
        if dist_cuadrada < tolerancia**2:
            return True
        else:
            return False
        
    #Definimos funcion para comprobar que el formato de las coordenadas y el tipo de polilinea cuadran
    def filtrar_coord_tipos_polilinea(tipo_pol, coords):
        #Si la polilinea se ha metido a mano será del tipo AcDbPolyline, no es del tipo que se estaban insertando AcDb2dPolyline (Polilinea 2D), si nos hemos olvidado de aplanarlo en AutoCAD a polilinea 2D paradojicamente saldrá con X, Y pero sin Z, aunque la otra sale con 3, por lo que hay que añadirle un cero a la Z
        if tipo_pol == "AcDbPolyline":
            if len(coords) % 3 == 0 and coords[3]==0: #si sale bien, con 3 coordenadas siendo cero la tercera
                coords_array = np.array(coords).reshape(-1, 3) 
            elif len(coords) % 2 == 0:
                coords_array = np.array(coords).reshape(-1, 2)
                z = obj.Elevation
                coordenadas_3d = np.hstack([coords_array, np.full((coords_array.shape[0], 1), z)])
            else:
                print(f"Coordenadas mal formateadas: {obj.Handle}")
        else:
            #Leer cordenadas
            coordenadas_3d = np.array(obj.Coordinates).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
        
        #Convertimos a 2D
        coordenadas_2d = coordenadas_3d[:,[0,1]] #y le quitamos la z porque esta version es en 2D
        
        return coordenadas_2d
            
  
            
  
    #Recorremos todas las polilineas de AASS LVAC buscando sus elementos asociados
    procesados = set()
    for obj in acad.iter_objects_fast('Polyline'):
        if obj.Layer == "Pol. AASS LVAC":
            #Evitar fallos de duplicados en API de AutoCAD
            handle = obj.Handle
            if handle in procesados:
                continue
            procesados.add(handle)
            
            #Comprobamos el tipo de polilinea para obtener las coordenadas de manera adecuada
            t_pol = obj.ObjectName
            coord_extraidas = obj.Coordinates
            
            coordenadas_extraidas_2d = filtrar_coord_tipos_polilinea(t_pol, coord_extraidas)
           
            #Comparar con los distintos elementos de SSAA
            for i in range(bloque_inicial, n_bloques+1):
                #LVAC a Comboxes
                if ~np.isnan(coord_Comboxes[i,0]):
                    if dentro_de_tolerancia(coord_Comboxes[i],coordenadas_extraidas_2d[0], 0.5): #si la polilinea se ha dibujado al reves
                        aux = np.copy(nueva_pol_AASS_LVAC[i,0])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d[::-1,:]
                        nueva_pol_AASS_LVAC[i,0] = aux
                        break
                                   
                    elif dentro_de_tolerancia(coord_Comboxes[i],coordenadas_extraidas_2d[-1], 0.5): 
                        aux = np.copy(nueva_pol_AASS_LVAC[i,0])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                        nueva_pol_AASS_LVAC[i,0] = aux
                        break
                    
                #LVAC a Tracknet
                if ~np.isnan(coord_Tracknets[i,0]):
                    if dentro_de_tolerancia(coord_Tracknets[i],coordenadas_extraidas_2d[0], 0.5): #si la polilinea se ha dibujado al reves
                        aux = np.copy(nueva_pol_AASS_LVAC[i,1])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d[::-1,:]
                        nueva_pol_AASS_LVAC[i,1] = aux
                        break
                                   
                    elif dentro_de_tolerancia(coord_Tracknets[i],coordenadas_extraidas_2d[-1], 0.5): 
                        aux = np.copy(nueva_pol_AASS_LVAC[i,1])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                        nueva_pol_AASS_LVAC[i,1] = aux
                        break
                    
                #LVAC a T-Box
                if ~np.isnan(coord_TBoxes[i,0]):
                    if dentro_de_tolerancia(coord_TBoxes[i],coordenadas_extraidas_2d[0], 0.5): #si la polilinea se ha dibujado al reves
                        aux = np.copy(nueva_pol_AASS_LVAC[i,2])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d[::-1,:]
                        nueva_pol_AASS_LVAC[i,2] = aux
                        break
                                   
                    elif dentro_de_tolerancia(coord_TBoxes[i],coordenadas_extraidas_2d[-1], 0.5): 
                        aux = np.copy(nueva_pol_AASS_LVAC[i,2])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                        nueva_pol_AASS_LVAC[i,2] = aux       
                        break
                    
                #LVAC a AWS
                if ~np.isnan(coord_AWS[i,0]):
                    if dentro_de_tolerancia(coord_AWS[i],coordenadas_extraidas_2d[0], 0.5): #si la polilinea se ha dibujado al reves
                        aux = np.copy(nueva_pol_AASS_LVAC[i,3])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d[::-1,:]
                        nueva_pol_AASS_LVAC[i,3] = aux
                        break
                                   
                    elif dentro_de_tolerancia(coord_AWS[i],coordenadas_extraidas_2d[-1], 0.5):
                        aux = np.copy(nueva_pol_AASS_LVAC[i,3])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                        nueva_pol_AASS_LVAC[i,3] = aux 
                        break

     #Repetimos para el CCTV y edificios
        elif obj.Layer == "Pol. CCTV LVAC":
            #Evitar fallos de duplicados en API de AutoCAD
            handle = obj.Handle
            if handle in procesados:
                continue
            procesados.add(handle)
             
            #Comprobamos el tipo de polilinea para obtener las coordenadas de manera adecuada
            t_pol = obj.ObjectName
            coord_extraidas = obj.Coordinates
            
            coordenadas_extraidas_2d = filtrar_coord_tipos_polilinea(t_pol, coord_extraidas)
            
            #La posicion en la lista de lineas de CCTV da igual, lo añadimos como np.array de pares
            nueva_pol_CCTV_LVAC.append(np.array(coordenadas_extraidas_2d))
             
        elif obj.Layer == "Pol. O&M LVAC":
            #Evitar fallos de duplicados en API de AutoCAD
            handle = obj.Handle
            if handle in procesados:
                continue
            procesados.add(handle)
             
            #Comprobamos el tipo de polilinea para obtener las coordenadas de manera adecuada
            t_pol = obj.ObjectName
            coord_extraidas = obj.Coordinates
            
            coordenadas_extraidas_2d = filtrar_coord_tipos_polilinea(t_pol, coord_extraidas)
             
            #La posicion en la lista de lineas de CCTV da igual, lo añadimos como np.array de pares 
            nueva_pol_OyM_supply_LVAC.append(np.array(coordenadas_extraidas_2d))

        elif obj.Layer == "Pol. Warehouse LVAC":
            #Evitar fallos de duplicados en API de AutoCAD
            handle = obj.Handle
            if handle in procesados:
                continue
            procesados.add(handle)
             
            #Comprobamos el tipo de polilinea para obtener las coordenadas de manera adecuada
            t_pol = obj.ObjectName
            coord_extraidas = obj.Coordinates
            
            coordenadas_extraidas_2d = filtrar_coord_tipos_polilinea(t_pol, coord_extraidas)
             
            #La posicion en la lista de lineas de CCTV da igual, lo añadimos como np.array de pares
            nueva_pol_Warehouse_supply_LVAC.append(np.array(coordenadas_extraidas_2d))                
             
    #Repetimos para todas las polilineas de ethernet
        elif obj.Layer == "Pol. Ethernet":
            #Evitar fallos de duplicados en API de AutoCAD
            handle = obj.Handle
            if handle in procesados:
                continue
            procesados.add(handle)
            
            #Comprobamos el tipo de polilinea para obtener las coordenadas de manera adecuada
            t_pol = obj.ObjectName
            coord_extraidas = obj.Coordinates
            
            coordenadas_extraidas_2d = filtrar_coord_tipos_polilinea(t_pol, coord_extraidas)
            
            #Comparar con los distintos elementos de SSAA
            for i in range(bloque_inicial, n_bloques+1):
                #Ethernet a PCS (desde comboxes)
                if ~np.isnan(coord_Comboxes[i,0]):
                    if dentro_de_tolerancia(coord_PCS_AASS_inputs[i],coordenadas_extraidas_2d[0], 0.5): #si la polilinea se ha dibujado al reves
                        aux = np.copy(nueva_pol_ethernet[i,0])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d[::-1,:]
                        nueva_pol_ethernet[i,0] = aux
                        break
                                   
                    elif dentro_de_tolerancia(coord_PCS_AASS_inputs[i],coordenadas_extraidas_2d[-1], 0.5): 
                        aux = np.copy(nueva_pol_ethernet[i,0])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                        nueva_pol_ethernet[i,0] = aux
                        break
                #Ethernet a Tracknet
                if ~np.isnan(coord_Tracknets[i,0]):
                    if dentro_de_tolerancia(coord_Tracknets[i],coordenadas_extraidas_2d[0], 0.5): #si la polilinea se ha dibujado al reves
                        aux = np.copy(nueva_pol_ethernet[i,1])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d[::-1,:]
                        nueva_pol_ethernet[i,1] = aux
                        break
                                   
                    elif dentro_de_tolerancia(coord_Tracknets[i],coordenadas_extraidas_2d[-1], 0.5): 
                        aux = np.copy(nueva_pol_ethernet[i,1])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                        nueva_pol_ethernet[i,1] = aux
                        break
                #Ethernet a T-Box
                if ~np.isnan(coord_TBoxes[i,0]):
                    if dentro_de_tolerancia(coord_TBoxes[i],coordenadas_extraidas_2d[0], 0.5): #si la polilinea se ha dibujado al reves
                        aux = np.copy(nueva_pol_ethernet[i,2])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d[::-1,:]
                        nueva_pol_ethernet[i,2] = aux
                        break
                                   
                    elif dentro_de_tolerancia(coord_TBoxes[i],coordenadas_extraidas_2d[-1], 0.5): 
                        aux = np.copy(nueva_pol_ethernet[i,2])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                        nueva_pol_ethernet[i,2] = aux       
                        break        
                #Ethernet a AWS
                if ~np.isnan(coord_AWS[i,0]):
                    if dentro_de_tolerancia(coord_AWS[i],coordenadas_extraidas_2d[0], 0.5): #si la polilinea se ha dibujado al reves
                        aux = np.copy(nueva_pol_ethernet[i,3])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d[::-1,:]
                        nueva_pol_ethernet[i,3] = aux
                        break
                                   
                    elif dentro_de_tolerancia(coord_AWS[i],coordenadas_extraidas_2d[-1], 0.5): 
                        aux = np.copy(nueva_pol_ethernet[i,3])
                        aux[:coordenadas_extraidas_2d.shape[0], :] = coordenadas_extraidas_2d
                        nueva_pol_ethernet[i,3] = aux 
                        break
    
    return nueva_pol_AASS_LVAC, nueva_pol_CCTV_LVAC, nueva_pol_OyM_supply_LVAC, nueva_pol_Warehouse_supply_LVAC, nueva_pol_ethernet
 





#-----------------------DIBUJAR POLILINEAS FIBRA OPTICA----------------
    
def CAD_draw_polilineas_FO(acad, pol_cable_FO):
    from pyautocad import APoint, aDouble
    
    colores_FO = [1,1,2,3,4,5,6,7,40,191]
    ind_color = 1
    
    for i in range(1,len(pol_cable_FO)):
        capa_FO = acad.doc.Layers.Add(f'Pol. FO Cable Line {i}')
        
        if ind_color == len(colores_FO):
            ind_color = 1
        capa_FO.color = colores_FO[ind_color]    
        ind_color = ind_color + 1

            
    def dibujar_FO(n_linea, coordenadas_FO): 
        # Filtrar puntos válidos (coordenadas no NaN)
        coordenadas_limpias = coordenadas_FO[~np.isnan(coordenadas_FO).any(axis=1)]
        
        # Definir los puntos
        points = [APoint(x, y) for x, y in coordenadas_limpias]
    
        # Dibujar polilínea
        points_double = aDouble(*[coord for point in points for coord in (point.x, point.y, 0)])
        polilinea_arr = acad.model.AddPolyline(points_double)
        polilinea_arr.ConstantWidth=0.05
        polilinea_arr.Layer = f'Pol. FO Cable Line {n_linea}' 


    for i, linea in enumerate(pol_cable_FO):
        if i==0:
            pass
        else:
            for tramo in linea:
                dibujar_FO(i, tramo[2])
    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents



#----------------------LEER POLILINEAS DE MEDIA TENSIÓN------------------------------

def CAD_read_polilineas_FO(acad, pol_cable_FO):
    
    time.sleep(0.1)  # le damos un tiempo para que AutoCAD no se autobloquee   
    info_en_documento_activo = False


    #Definimos funcion para comprobar que el formato de las coordenadas y el tipo de polilinea cuadran
    def filtrar_coord_tipos_polilinea(tipo_pol, coords):
        #Si la polilinea se ha metido a mano será del tipo AcDbPolyline, no es del tipo que se estaban insertando AcDb2dPolyline (Polilinea 2D), si nos hemos olvidado de aplanarlo en AutoCAD a polilinea 2D paradojicamente saldrá con X, Y pero sin Z, aunque la otra sale con 3, por lo que hay que añadirle un cero a la Z
        if tipo_pol == "AcDbPolyline":
            if len(coords) % 3 == 0 and coords[2]==0: #si sale bien, con 3 coordenadas siendo cero la tercera
                coords_array = np.array(coords).reshape(-1, 3) 
            elif len(coords) % 2 == 0:
                coords_array = np.array(coords).reshape(-1, 2)
                z = obj.Elevation
                coordenadas_3d = np.hstack([coords_array, np.full((coords_array.shape[0], 1), z)])
            else:
                print(f"Coordenadas mal formateadas: {obj.Handle}")
        else:
            #Leer cordenadas
            coordenadas_3d = np.array(obj.Coordinates).reshape(-1,3) #extraemos las coordenadas, como salen en formato tuple las pasamos a array ordenado
        
        #Convertimos a 2D
        coordenadas_2d = coordenadas_3d[:,[0,1]] #y le quitamos la z porque esta version es en 2D
    
        return coordenadas_2d   
    
    
    
    for obj in acad.iter_objects_fast('Polyline'):
        nombre_pol = obj.Layer
        if nombre_pol[:18] == 'Pol. FO Cable Line':
            linea = int(nombre_pol[19:])
            
            coordenadas_extraidas = obj.Coordinates
            t_pol = obj.ObjectName
            
            coordenadas_pol_FO_2d = filtrar_coord_tipos_polilinea(t_pol,coordenadas_extraidas)
            
            info_en_documento_activo = True
            
            for j, tramo in enumerate(pol_cable_FO[linea]):
                diff=tramo[0]-coordenadas_pol_FO_2d[0]
                dist = np.linalg.norm(diff)
                if dist < 1:
                    pol_cable_FO[linea][j][2]=coordenadas_pol_FO_2d
   
    
    if not info_en_documento_activo:
        return None
    else:
        return pol_cable_FO



        
        
        
        
        
#------------------DIBUJAR ELECTRODO DE PUESTA A TIERRA-----------------------------              
              
def CAD_draw_Earthing_Electrode(acad, PAT_Electrodo):
    
    from pyautocad import APoint, aDouble
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    
    #Sacar tipos de secciones
    secciones = [segmento[0] for segmento in PAT_Electrodo]
    secciones_unicas = np.unique(np.array(secciones))
    
    colores_electrodo = [5, 10, 211]
    #Definir Capas
    c_color=0
    for seccion in secciones_unicas:
        capa_electrodo_PAT = acad.doc.Layers.Add(f'Earthing electrode {int(seccion)} mm2')
        capa_electrodo_PAT.color = colores_electrodo[c_color]
        c_color=c_color+1
    
    
    #Definir funciones de dibujo
        # Función para dibujar el electrodo de PAT
    def dibujar_electrodo_PAT(secc, x1, y1, x2, y2):
        p1 = APoint(x1, y1)
        p2 = APoint(x2, y2)
        # Dibujar polilínea
        points = aDouble(p1.x, p1.y, 0, p2.x, p2.y, 0)
        tramo_electrodo = acad.model.AddPolyline(points)
        #zanja_LV.Layer
        tramo_electrodo.ConstantWidth = 0.2
        tramo_electrodo.Layer = f'Earthing electrode {secc} mm2'
        
    for segmento in PAT_Electrodo:
        dibujar_electrodo_PAT(int(segmento[0]), segmento[1], segmento[2], segmento[3], segmento[4])
        

        
    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents        
        
        
        
#------------------LEER ELECTRODO DE PUESTA A TIERRA-----------------------------              
          
def CAD_read_Earthing_Electrode(acad, PAT_Electrodo, TOT_PAT_Electrodo):
    
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    info_en_documento_activo = False
    

    for obj in acad.iter_objects_fast('Polyline'):
        nombre_pol = obj.Layer
        for seccion in TOT_PAT_Electrodo:
            if nombre_pol[:18] == "Earthing electrode":
                PAT_Electrodo.append([nombre_pol[19:21], obj.Coordinates])  # lista plana [x0, y0, x1, y1, ...]
                info_en_documento_activo = True
                break
    


            
    if not info_en_documento_activo:
        return None
    else:
        return PAT_Electrodo
        
         
        
        
        
        
        
#------------------------DIBUJAR FLECHAS Y TEXTOS DE STRINGS-----------------------
def CAD_draw_flechas_strings_texto(acad, all_blocks, single_block, bloque_inicial, n_bloques, max_c_block, max_bus, masc, strings_ID, DCBoxes_o_Inv_String, max_inv_block, max_str_pinv):
    from pyautocad import APoint, aDouble
    
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    
    # Definimos las capas
    capa_Interconnection_text=acad.doc.Layers.Add('Interconnection text')
    capa_Interconnection_text.color = 7
    
    capa_Interconnection_arrows=acad.doc.Layers.Add('Interconnection arrows')
    capa_Interconnection_arrows.color = 7
    
    # Definimos la función para dibujar una flecha entre dos puntos
    def dibujar_flecha(punto_inicio, punto_fin):
        acorte_flechas = 4 #acortamos la longitud para que en algunos trackers la punta de una flecha no toque el inicio de la siguiente
        if punto_inicio[1] > punto_fin[1]:
            p1 = APoint(punto_inicio[0], punto_inicio[1]-acorte_flechas)
            p2 = APoint(punto_fin[0], punto_fin[1]+2+acorte_flechas) #la cabeza de la flecha se pone 2 m arriba si la orientacion es Sur
            p3 = APoint(punto_fin[0], punto_fin[1]+acorte_flechas) #final de linea
        else:
            p1 = APoint(punto_inicio[0], punto_inicio[1]+acorte_flechas)
            p2 = APoint(punto_fin[0], punto_fin[1]-2-acorte_flechas) #la cabeza de la flecha se pone 2 m abajo si la orientacion es Norte
            p3 = APoint(punto_fin[0], punto_fin[1]-acorte_flechas) #final de linea
            
        
        points = aDouble(p1.x, p1.y, 0, p2.x, p2.y, 0, p3.x, p3.y, 0)
        
        flecha = acad.model.AddPolyline(points)
        flecha.Layer = 'Interconnection arrows'
        flecha.ConstantWidth = 0
        flecha.SetWidth(0, 0.05, 0.05)
        flecha.SetWidth(1, 1, 0)
        
    # Definimos la función para dibujar texto girado 90º en el punto medio
    def dibujar_ID_string(texto, punto_inicio, punto_fin):
        # Calcular el punto medio
        desfase = -1 #se le mete un desfase a la x de insercion para que tras rotarlo 90º caiga en el centro
        
        punto_medio = APoint((punto_inicio[0]+desfase + punto_fin[0]) / 2, (punto_inicio[1]+desfase + punto_fin[1]) / 2)
        
        # Añadir el texto en el punto medio
        texto_obj = acad.model.AddMText(punto_medio, 1, texto)  # Damos 1 al tamaño del texto 
        texto_obj.BackgroundFill = True
        texto_obj.Height = 1  # Damos 1 al tamaño del texto 
        texto_obj.Layer = 'Interconnection text'
        # Girar el texto 90º
        texto_obj.Rotation = np.pi / 2
        # Dar el estilo de texto predefinido en GRS
        # try:
        #     texto_obj.StyleName = 'textos string'
        # except:
        #     pass
    
    
    #------CASO CON CAJAS-------
    if DCBoxes_o_Inv_String == 'DC Boxes':
        # Recorremos los strings ID para dibujar flechas y textos
        if all_blocks==True:          
            for i in range(bloque_inicial,n_bloques+1):
                for inv in range(1,3):
                    if ~np.isnan(strings_ID[i,inv,1,0,1,1]) or ~np.isnan(strings_ID[i,inv,1,1,1,1]): #si el inv no está vacío      
                        for caj in range (1,max_c_block+1):      
                            if ~np.isnan(strings_ID[i,inv,caj,0,1,1]) or ~np.isnan(strings_ID[i,inv,caj,1,1,1]): #si la caja no está vacía
                                for bus in range(0,max_bus):
                                    if ~np.isnan(strings_ID[i,inv,caj,0,1,1]) or ~np.isnan(strings_ID[i,inv,caj,bus,1,1]): #si es una caja de string o el bus no está vacío
                                        for s in range(1,masc+1):
                                            if ~np.isnan(strings_ID[i,inv,caj,bus,s,1]): #si el string no está vacío
                                            
                                                dibujar_flecha(strings_ID[i,inv,caj,bus,s,[1,2]], strings_ID[i,inv,caj,bus,s,[1,3]])
                                                dibujar_ID_string(strings_ID[i,inv,caj,bus,s,0],strings_ID[i,inv,caj,bus,s,[1,2]], strings_ID[i,inv,caj,bus,s,[1,3]])
                                                
                                            else:
                                                break
                            else:
                                break
                    else:
                        break
    
        else:
            i = single_block
            for inv in range(1,3):
                if ~np.isnan(strings_ID[i,inv,1,0,1,1]) or ~np.isnan(strings_ID[i,inv,1,1,1,1]): #si el inv no está vacío      
                    for caj in range (1,max_c_block+1):      
                        if ~np.isnan(strings_ID[i,inv,caj,0,1,1]) or ~np.isnan(strings_ID[i,inv,caj,1,1,1]): #si la caja no está vacía
                            for bus in range(1,max_bus):
                                if ~np.isnan(strings_ID[i,inv,caj,0,1,1]) or ~np.isnan(strings_ID[i,inv,caj,bus,1,1]): #si el bus no está vacío
                                    for s in range(1,masc):
                                        if ~np.isnan(strings_ID[i,inv,caj,bus,s,1]): #si el string no está vacío
                                        
                                            dibujar_flecha(strings_ID[i,inv,caj,bus,s,[1,2]], strings_ID[i,inv,caj,bus,s,[1,3]])
                                            dibujar_ID_string(strings_ID[i,inv,caj,bus,s,0],strings_ID[i,inv,caj,bus,s,[1,2]], strings_ID[i,inv,caj,bus,s,[1,3]])
                                            
                                        else:
                                            break
                        else:
                            break
                else:
                    break
             
    #------CASO CON INV DE STRING-------            
    else:
        # Recorremos los strings ID para dibujar flechas y textos
        if all_blocks==True:          
            for i in range(bloque_inicial,n_bloques+1):
                for board in range(0,3):
                    if ~np.isnan(strings_ID[i,board,1,1,1]): #si el inv no está vacío      
                        for inv in range (1,max_inv_block+1):      
                            if ~np.isnan(strings_ID[i,board,inv,1,1]): #si la inva no está vacía
                                for s in range(1,max_str_pinv+1):
                                    if ~np.isnan(strings_ID[i,board,inv,s,1]): #si el string no está vacío                                    
                                        dibujar_flecha(strings_ID[i,board,inv,s,[1,2]], strings_ID[i,board,inv,s,[1,3]])
                                        dibujar_ID_string(strings_ID[i,board,inv,s,0],strings_ID[i,board,inv,s,[1,2]], strings_ID[i,board,inv,s,[1,3]])
                                        
                                    else:
                                        break
                            else:
                                break

    
        else:
            i = single_block
            for board in range(0,3):
                if ~np.isnan(strings_ID[i,board,1,1,1]): #si el inv no está vacío      
                    for inv in range (1,max_inv_block+1):      
                        if ~np.isnan(strings_ID[i,board,inv,1,1]): #si la inva no está vacía
                            for s in range(1,max_str_pinv+1):
                                if ~np.isnan(strings_ID[i,board,inv,s,1]): #si el string no está vacío
                                
                                    dibujar_flecha(strings_ID[i,board,inv,s,[1,2]], strings_ID[i,board,inv,s,[1,3]])
                                    dibujar_ID_string(strings_ID[i,board,inv,s,0],strings_ID[i,board,inv,s,[1,2]], strings_ID[i,board,inv,s,[1,3]])
                                    
                                else:
                                    break
                        else:
                            break


                     
            
         
    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents
        




        
#-----------------------DIBUJAR HARNESS-----------------------
def CAD_draw_Harness(acad, dos_polos, bloque_inicial, Harness_pos_ID, Harness_neg_ID):
    from pyautocad import APoint
    
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    
    # Definimos las capas    
    capa_Harness_T1=acad.doc.Layers.Add('HT1')
    capa_Harness_T1.color = 11    
    
    capa_Harness_T2a=acad.doc.Layers.Add('HT2a')
    capa_Harness_T2a.color = 41    
    
    capa_Harness_T2b=acad.doc.Layers.Add('HT2b')
    capa_Harness_T2b.color = 71    
    
    capa_Harness_T3=acad.doc.Layers.Add('HT3')
    capa_Harness_T3.color = 151    
    
    # Función para dibujar harness
    def dibujar_harness(tipo, polo, coordx, coordy):
        punto_insercion = APoint(coordx, coordy)
        
        
        
        # Añadir el texto con el tipo de harness en el punto de insercion
        if tipo ==1:
            h_tipo_corr = '1'
        elif tipo == 2:
            h_tipo_corr = '2a'
        elif tipo == 3:
            h_tipo_corr = '2b'
        elif tipo == 4:
            h_tipo_corr = '3'   
            
            
        if polo=='n/a':
            texto=f"H{h_tipo_corr}"
        else:
            texto=f"H{h_tipo_corr}{polo}"
            
        texto_obj = acad.model.AddText(texto, punto_insercion, 1)  # Damos 1 al tamaño del texto porque se define en el estilo
        texto_obj.Layer = f"HT{h_tipo_corr}" 
    
    # Como los Harness se han listado conjuntamente en el algoritmo se recorre el mismo array
    if dos_polos==True:
        for i in range(len(Harness_pos_ID)):
            dibujar_harness(int(Harness_pos_ID[i,0]), '+', Harness_pos_ID[i,1], Harness_pos_ID[i,2])
            dibujar_harness(int(Harness_neg_ID[i,0]), '-',  Harness_neg_ID[i,1], Harness_neg_ID[i,2])
    else:
        for i in range(len(Harness_pos_ID)):
            dibujar_harness(int(Harness_pos_ID[i,0]), 'n/a', Harness_pos_ID[i,1], Harness_pos_ID[i,2])
        
        
    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents
                

       
        
#------------------DIBUJAR ZANJAS DC-----------------------------  
def CAD_draw_Zanjas_DC(acad, all_blocks, single_block, bloque_inicial, zanjas_DC_ID, PB_zanjas_DC_ID, n_tubos_max_DC1, ancho_DC1, ancho_DC2):   
    #Hay que trabajar directamente con WIN32 COM porque Pyautocad no soporta AddMLeader para añadir directrices, todo el proceso de dibujo tiene que ser en WIN32 porque no se pueden mezclar ambas librerias en un mismo proceso con dibujo activo
    import time
    import numpy as np
    import win32com.client
    import pythoncom

    time.sleep(0.3)

    # Obtener el nombre del documento activo desde pyautocad
    doc_name = acad.doc.Name

    # Conectar con AutoCAD usando win32com y obtener el documento correcto
    app = win32com.client.Dispatch("AutoCAD.Application")
    doc = next((d for d in app.Documents if d.Name.lower() == doc_name.lower()), None)
    if doc is None:
        raise RuntimeError(f"No se encontró el documento {doc_name} en AutoCAD")
    
    ms = doc.ModelSpace
    
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    
    # Definimos las capas 
    capa_DC1 = acad.doc.Layers.Add('DC1')
    capa_DC1.color = 12
    
    capa_DC2 = acad.doc.Layers.Add('DC2')
    capa_DC2.color = 11

    def funcion_unir_segmentos_DC(all_blocks, single_block, zanjas_DC_ID, PB_zanjas_DC_ID):
        # Almacenes básicos
        segmentos_por_clave = {}       # {(n_tubos, n_circuitos): [segmento1, segmento2, ...]}
        inicio_a_segmento = {}         # {(n_tubos, n_circuitos, punto_inicio): [segmentos]}
        fin_a_segmento = {}            # {(n_tubos, n_circuitos, punto_fin): [segmentos]}
    
        # Paso 1: Agrupar y registrar accesos
        if not all_blocks:
            zanjas_DC_ID = PB_zanjas_DC_ID[single_block]
    
        for i in range(len(zanjas_DC_ID)):
            n_tubos = int(zanjas_DC_ID[i, 0])
            n_circuitos = int(zanjas_DC_ID[i, 1])
            punto_inicio = tuple(zanjas_DC_ID[i, [2, 3]])
            punto_fin = tuple(zanjas_DC_ID[i, [4, 5]])
            coords = [punto_inicio, punto_fin]
    
            clave = (n_tubos, n_circuitos)
            segmento = {
                "inicio": punto_inicio,
                "fin": punto_fin,
                "coords": coords,
                "usado": False
            }
    
            # Agregar al grupo correspondiente
            segmentos_por_clave.setdefault(clave, []).append(segmento)
            inicio_a_segmento.setdefault((n_tubos, n_circuitos, punto_inicio), []).append(segmento)
            fin_a_segmento.setdefault((n_tubos, n_circuitos, punto_fin), []).append(segmento)
    
        # Paso 2: Unir segmentos
        pol_zanjas_DC = []
    
        for clave, lista_segmentos in segmentos_por_clave.items():
            n_tubos, n_circuitos = clave
            for seg in lista_segmentos:
                if seg["usado"]:
                    continue
    
                seg["usado"] = True
                coords = seg["coords"][:]
    
                # Extiende hacia adelante
                siguiente = seg["fin"]
                while True:
                    candidatos = inicio_a_segmento.get((n_tubos, n_circuitos, siguiente), [])
                    next_seg = next((s for s in candidatos if not s["usado"]), None)
                    if next_seg is None:
                        break
                    next_seg["usado"] = True
                    coords.append(next_seg["fin"])
                    siguiente = next_seg["fin"]
    
                # Extiende hacia atrás
                anterior = seg["inicio"]
                while True:
                    candidatos = fin_a_segmento.get((n_tubos, n_circuitos, anterior), [])
                    prev_seg = next((s for s in candidatos if not s["usado"]), None)
                    if prev_seg is None:
                        break
                    prev_seg["usado"] = True
                    coords = [prev_seg["inicio"]] + coords
                    anterior = prev_seg["inicio"]
    
                pol_zanjas_DC.append([n_tubos, n_circuitos, coords])
    
        return pol_zanjas_DC

    
    
    # Funcion para hallar el punto medio de la polilinea
    def punto_medio_polilinea(coords):
        coords = np.array(coords)
        segmentos = coords[1:] - coords[:-1]  # diferencias entre puntos consecutivos
        longitudes = np.linalg.norm(segmentos, axis=1)
        total = np.sum(longitudes)
        mitad = total / 2
    
        acumulado = 0
        for i, l in enumerate(longitudes):
            if acumulado + l >= mitad:
                sobra = mitad - acumulado
                t = sobra / l
                punto = coords[i] + t * segmentos[i]
                return tuple(punto)
            acumulado += l
    
        return tuple(coords[-1])

    

        
    def dibujar_zanjas_DC(coords, n_tubos, n_tubos_max_DC1, n_c, ancho_DC1, ancho_DC2):

        # Crear zanja con win32com
        puntos = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(coord) for x, y in coords for coord in (x, y, 0.0)])
        zanja = ms.AddPolyline(puntos)
        
        if n_tubos <= n_tubos_max_DC1:    
            t_z = 'DC1'
            ancho = ancho_DC1
        else:
            t_z = 'DC2'
            ancho = ancho_DC2
            
        zanja.Layer = t_z
        zanja.ConstantWidth = ancho
        
        # Crear directriz con win32com
        medio = punto_medio_polilinea(coords)  # Calcular el punto medio de la zanja para meter la directriz
        quiebro = [2, 1]
        desfase = [0.5, 0]
        texto_pto = (medio[0] + quiebro[0] + desfase[0], medio[1] + quiebro[1] + desfase[1])
        texto = f'{t_z} ({n_tubos},{n_c},1)'

        leader_points = [float(medio[0]), float(medio[1]), 0.0,float(texto_pto[0]), float(texto_pto[1]), 0.0]
        safe_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, leader_points)
        mleader_raw = ms.AddMLeader(safe_array, 0)
        mleader = mleader_raw[0] if isinstance(mleader_raw, tuple) else mleader_raw
        mleader = win32com.client.Dispatch(mleader)
        mleader.TextString = texto
        mleader.TextRotation = np.pi / 2
        mleader.Layer = t_z  
    

       
    pol_zanjas_DC = funcion_unir_segmentos_DC(all_blocks, single_block, zanjas_DC_ID, PB_zanjas_DC_ID)
    for n_tubos , n_circ, coord in pol_zanjas_DC:    
        dibujar_zanjas_DC(coord, n_tubos, n_tubos_max_DC1, n_circ, ancho_DC1, ancho_DC2)

          
    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents        
    
    
    
#------------------DIBUJAR ZANJAS LV-----------------------------  
def CAD_draw_Zanjas_LV(acad, all_blocks, single_block, bloque_inicial, zanjas_LV_ID, PB_zanjas_LV_ID, DCBoxes_o_Inv_String):
    #Hay que trabajar directamente con WIN32 COM porque Pyautocad no soporta AddMLeader para añadir directrices, todo el proceso de dibujo tiene que ser en WIN32 porque no se pueden mezclar ambas librerias en un mismo proceso con dibujo activo
    import time
    import numpy as np
    import win32com.client
    import pythoncom

    time.sleep(0.3)

    # Obtener el nombre del documento activo desde pyautocad
    doc_name = acad.doc.Name

    # Conectar con AutoCAD usando win32com y obtener el documento correcto
    app = win32com.client.Dispatch("AutoCAD.Application")
    doc = next((d for d in app.Documents if d.Name.lower() == doc_name.lower()), None)
    if doc is None:
        raise RuntimeError(f"No se encontró el documento {doc_name} en AutoCAD")
    
    ms = doc.ModelSpace
    layers = doc.Layers

    # Definir capas y colores
    if DCBoxes_o_Inv_String == 'DC Boxes':
        repositorio_y_colores_de_capas = {
            'LV1': 131,
            'LV2': 130,
            'LV3': 141,
            'LV4': 140,
            'LV5': 150,
            'LV6': 160,
            'LV7': 190,
            'LV8': 190,
            'LV9': 190,
            'LV10': 190,
            'LV11': 190,
            'LV12': 190,
            'LV13': 190,
            'LV1C': 2,
            'LV2C': 2,
            'LV3C': 2,
            'LV4C': 2,
            'LV5C': 2,
            'LV6C': 2,
            'LV7C': 2,
            'LV8C': 2,
            'LV9C': 2,
            'LV10C': 2,
            'LV11C': 2,
            'LV12C': 2,
            'LV13C': 2,
        }
    else:
        repositorio_y_colores_de_capas = {
            'AC1': 140,
            'AC2': 150,
            'AC3': 160,
            'AC4': 140,
            'AC5': 150,
            'AC6': 160,
            'AC7': 140,
            'AC8': 150,
            'AC9': 160,
            'AC10': 140,
            'AC11': 150,
            'AC12': 160,
            'AC13': 140,
            'AC1C': 40,
            'AC2C': 40,
            'AC3C': 40,
            'AC4C': 40,
            'AC5C': 40,
            'AC6C': 40,
            'AC7C': 40,
            'AC8C': 40,
            'AC9C': 40,
            'AC10C': 40,
            'AC11C': 40,
            'AC12C': 40,
            'AC13C': 40,
        }
    if DCBoxes_o_Inv_String == 'DC Boxes':   
        capas_usadas = list(set(fila[1] for fila in zanjas_LV_ID))
    else:
        capas_usadas = list(set(("AC" + fila[1][2:]) if fila[1].startswith("LV") else fila[1]for fila in zanjas_LV_ID))

    capas_existentes = [l.Name for l in layers]

    for nombre_capa in capas_usadas:
        if nombre_capa in repositorio_y_colores_de_capas and nombre_capa not in capas_existentes:
            nueva = layers.Add(nombre_capa)
            nueva.color = repositorio_y_colores_de_capas[nombre_capa]


    def funcion_unir_segmentos_LV(all_blocks, single_block, zanjas_LV_ID, PB_zanjas_LV_ID):
        segmentos_por_t = {}
        inicio_a_segmento = {}
        fin_a_segmento = {}

        if not all_blocks:
            zanjas_LV_ID = PB_zanjas_LV_ID[single_block]

        for i in range(len(zanjas_LV_ID)):
            ancho, tipo, subtipo = zanjas_LV_ID[i][0:3]
            n_circuitos = int(zanjas_LV_ID[i][3])
            n_aass_lvac = int(zanjas_LV_ID[i][4])
            n_ethernet = int(zanjas_LV_ID[i][5])
            n_FO =int(zanjas_LV_ID[i][6])
            p_ini = tuple(zanjas_LV_ID[i][7][0:2])
            p_fin = tuple(zanjas_LV_ID[i][7][2:4])
            tipologia = (ancho, tipo, subtipo, n_circuitos, n_aass_lvac, n_ethernet, n_FO)
            segmento = {"inicio": p_ini, "fin": p_fin, "coords": [p_ini, p_fin], "usado": False}

            segmentos_por_t.setdefault(tipologia, []).append(segmento)
            inicio_a_segmento.setdefault((tipologia, p_ini), []).append(segmento)
            fin_a_segmento.setdefault((tipologia, p_fin), []).append(segmento)

        pol_zanjas_LV = []
        for tipologia, lista in segmentos_por_t.items():
            for seg in lista:
                if seg["usado"]:
                    continue
                seg["usado"] = True
                coords = seg["coords"][:]

                siguiente = seg["fin"]
                while True:
                    candidatos = inicio_a_segmento.get((tipologia, siguiente), [])
                    next_seg = next((s for s in candidatos if not s["usado"]), None)
                    if not next_seg:
                        break
                    next_seg["usado"] = True
                    coords.append(next_seg["fin"])
                    siguiente = next_seg["fin"]

                anterior = seg["inicio"]
                while True:
                    candidatos = fin_a_segmento.get((tipologia, anterior), [])
                    prev_seg = next((s for s in candidatos if not s["usado"]), None)
                    if not prev_seg:
                        break
                    prev_seg["usado"] = True
                    coords = [prev_seg["inicio"]] + coords
                    anterior = prev_seg["inicio"]

                pol_zanjas_LV.append([*tipologia, coords])
        return pol_zanjas_LV

    def punto_medio_polilinea(coords):
        coords = np.array(coords)
        segmentos = coords[1:] - coords[:-1]
        longitudes = np.linalg.norm(segmentos, axis=1)
        mitad = np.sum(longitudes) / 2
        acumulado = 0
        for i, l in enumerate(longitudes):
            if acumulado + l >= mitad:
                t = (mitad - acumulado) / l
                return tuple(coords[i] + t * segmentos[i])
            acumulado += l
        return tuple(coords[-1])

    def dibujar_zanjas_LV(ancho, tipo, subtipo, n_circ, n_ac, n_eth, n_FO, coords):
        # Crear zanja con win32com
        puntos = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(coord) for x, y in coords for coord in (x, y, 0.0)])
        pline = ms.AddPolyline(puntos)
        pline.ConstantWidth = ancho
        pline.Layer = tipo
        
        # Crear directriz con win32com
        medio = punto_medio_polilinea(coords)
        quiebro = [2, 1]
        desfase = [0.5, 0]
        texto_pto = (medio[0] + quiebro[0] + desfase[0], medio[1] + quiebro[1] + desfase[1])
        texto = tipo + subtipo + f' ({n_circ},{n_ac},{n_eth},{n_FO},1)'

        leader_points = [float(medio[0]), float(medio[1]), 0.0,float(texto_pto[0]), float(texto_pto[1]), 0.0]
        safe_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, leader_points)
        mleader_raw = ms.AddMLeader(safe_array, 0)
        mleader = mleader_raw[0] if isinstance(mleader_raw, tuple) else mleader_raw
        mleader = win32com.client.Dispatch(mleader)
        mleader.TextString = texto
        mleader.Layer = tipo

    # Ejecutar
    zanjas = funcion_unir_segmentos_LV(all_blocks, single_block, zanjas_LV_ID, PB_zanjas_LV_ID)
    for ancho, tipo, subtipo, n_c, n_ac, n_eth, n_FO, coords in zanjas:
        if DCBoxes_o_Inv_String== 'String Inverters':
            if tipo.startswith("LV"):
                tipo = "AC" + tipo[2:]
            
        dibujar_zanjas_LV(ancho, tipo, subtipo, n_c, n_ac, n_eth, n_FO, coords)

    # Zoom extents
    time.sleep(0.1)
    doc.SendCommand("._zoom _extents\n")




#------------------DIBUJAR ZANJAS AS-----------------------------

def CAD_draw_zanjas_AS(acad, zanjas_AS_ID):
    #Hay que trabajar directamente con WIN32 COM porque Pyautocad no soporta AddMLeader para añadir directrices, todo el proceso de dibujo tiene que ser en WIN32 porque no se pueden mezclar ambas librerias en un mismo proceso con dibujo activo
    import time
    import numpy as np
    import win32com.client
    import pythoncom
    
    time.sleep(0.3)

    # Obtener el nombre del documento activo desde pyautocad
    doc_name = acad.doc.Name

    # Conectar con AutoCAD usando win32com y obtener el documento correcto
    app = win32com.client.Dispatch("AutoCAD.Application")
    doc = next((d for d in app.Documents if d.Name.lower() == doc_name.lower()), None)
    if doc is None:
        raise RuntimeError(f"No se encontró el documento {doc_name} en AutoCAD")
    
    ms = doc.ModelSpace

    
    #Definir Capas
    capa_AS1 = acad.doc.Layers.Add('AS1')
    capa_AS1.color = 82


    def punto_medio_polilinea(coords):
        coords = np.array(coords)
        segmentos = coords[1:] - coords[:-1]
        longitudes = np.linalg.norm(segmentos, axis=1)
        mitad = np.sum(longitudes) / 2
        acumulado = 0
        for i, l in enumerate(longitudes):
            if acumulado + l >= mitad:
                t = (mitad - acumulado) / l
                return tuple(coords[i] + t * segmentos[i])
            acumulado += l
        return tuple(coords[-1])
        
    # Función para dibujar zanjas DC
    def dibujar_zanjas_AS(coords, n_ac, n_eth, n_FO, ancho):
        # Crear zanja con win32com
        puntos = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(coord) for x, y in coords for coord in (x, y, 0.0)])
        pline = ms.AddPolyline(puntos)
        pline.ConstantWidth = ancho
        pline.Layer = 'AS1'
        
        # Crear directriz con win32com
        medio = punto_medio_polilinea(coords)
        quiebro = [2, 1]
        desfase = [0.5, 0]
        texto_pto = (medio[0] + quiebro[0] + desfase[0], medio[1] + quiebro[1] + desfase[1])
        texto = f'AS1({n_ac},{n_eth},{n_FO},1)'

        leader_points = [float(medio[0]), float(medio[1]), 0.0,float(texto_pto[0]), float(texto_pto[1]), 0.0]
        safe_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, leader_points)
        mleader_raw = ms.AddMLeader(safe_array, 0)
        mleader = mleader_raw[0] if isinstance(mleader_raw, tuple) else mleader_raw
        mleader = win32com.client.Dispatch(mleader)
        mleader.TextString = texto
        mleader.Layer = 'AS1'
        

            
    for zanja in zanjas_AS_ID:  
        n_ac = int(zanja[0])
        n_eth = int(zanja[1])
        n_FO = int(zanja[2])
        coords = [(zanja[3],zanja[4]),(zanja[5],zanja[6])]
        
        dibujar_zanjas_AS(coords, n_ac, n_eth, n_FO, 0.4)      
        
    
          
    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents             
        
        
        
        
        
        
        
        
        
        
        

#------------------DIBUJAR PUESTA A TIERRA-----------------------------              
            
def CAD_draw_PAT(acad, bloque_inicial, n_bloques, all_blocks, single_block, max_b, max_f_str_b, max_c, max_tpf, PAT_latiguillo_entre_trackers, PAT_latiguillo_primera_pica, PAT_terminal_primera_pica, PAT_terminal_DC_Box, sep, dist_primera_pica_extremo_tr, zanjas_DC_ID, PB_zanjas_DC_ID, zanjas_LV_ID, PB_zanjas_LV_ID):
    
    from pyautocad import APoint, aDouble
    
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee
    
    #Definir Capas
    capa_PAT_egpat = acad.doc.Layers.Add('Electrodo general PAT')
    capa_PAT_egpat.color = 5
    
    # capa_PAT_let = 
    acad.doc.Layers.Add('PAT Latiguillo entre trackers')
    
    # capa_PAT_lpp = 
    acad.doc.Layers.Add('PAT Latiguillo primera pica')

    # capa_PAT_tpp = 
    acad.doc.Layers.Add('PAT Estructura en primera pica')
    
    # capa_PAT_DC_Box = 
    acad.doc.Layers.Add('PAT DC Box')
      
    #Definir bloques que se usaran para insertar terminales y latiguillos
        
        #Creamos el bloque que da apariencia de punto y circunferencia con dos polilineas 
    def definir_bloque_terminal_circular(nombre_bloque_str, color):
        nombre_bloque_var = acad.doc.Blocks.Add(APoint(0,0,0), nombre_bloque_str)
        point_pol_int_term_circ=aDouble(0.025, 0, 0   , -0.025, 0, 0)
        pol_interior_term_circ = nombre_bloque_var.AddPolyline(point_pol_int_term_circ)
        pol_interior_term_circ.Closed = True
        pol_interior_term_circ.ConstantWidth=0.05
        pol_interior_term_circ.color = color
        for i in range(len(point_pol_int_term_circ) // 3):  # Dividir por 3 porque cada punto tiene x, y, z
            pol_interior_term_circ.SetBulge(i, 1)  # Ajusta el valor del bulge para convertir el segmento en arco
        
        point_pol_ext_term_circ = aDouble(0.25, 0, 0   , -0.25, 0, 0)
        pol_exterior_term_circ = nombre_bloque_var.AddPolyline(point_pol_ext_term_circ)
        pol_exterior_term_circ.Closed = True
        pol_exterior_term_circ.ConstantWidth=0.1
        pol_exterior_term_circ.color = color
        for i in range(len(point_pol_ext_term_circ) // 3):  # Dividir por 3 porque cada punto tiene x, y, z
            pol_exterior_term_circ.SetBulge(i, 1)  # Ajusta el valor del bulge para convertir el segmento en arco
        
        return nombre_bloque_var
    
    def definir_bloque_terminal_cuadrado(nombre_bloque_str, color):
        nombre_bloque_var = acad.doc.Blocks.Add(APoint(0,0,0), nombre_bloque_str)
        point_pol_int_term_circ=aDouble(0.025, 0, 0   , -0.025, 0, 0)
        pol_interior_term_circ = nombre_bloque_var.AddPolyline(point_pol_int_term_circ)
        pol_interior_term_circ.Closed = True
        pol_interior_term_circ.ConstantWidth=0.05
        pol_interior_term_circ.color = color
        for i in range(len(point_pol_int_term_circ) // 3):  # Dividir por 3 porque cada punto tiene x, y, z
            pol_interior_term_circ.SetBulge(i, 1)  # Ajusta el valor del bulge para convertir el segmento en arco
        
        point_pol_ext_term_circ = aDouble(0.2863, 0.2863, 0   , 0.2863, -0.2863, 0   , -0.2863, -0.2863, 0   , -0.2863, 0.2863, 0)
        pol_exterior_term_circ = nombre_bloque_var.AddPolyline(point_pol_ext_term_circ)
        pol_exterior_term_circ.Closed = True
        pol_exterior_term_circ.ConstantWidth=0.1
        pol_exterior_term_circ.color = color
        
        return nombre_bloque_var
    
    #Definir funciones de dibujo
        # Función para dibujar el electrodo de PAT
    def dibujar_electrodo_PAT(punto_inicio, punto_fin):
        p1 = APoint(punto_inicio[0], punto_inicio[1])
        p2 = APoint(punto_fin[0], punto_fin[1])
        # Dibujar polilínea
        points = aDouble(p1.x, p1.y, 0, p2.x, p2.y, 0)
        zanja_LV = acad.model.AddPolyline(points)
        #zanja_LV.Layer
        zanja_LV.ConstantWidth = 0.2
        zanja_LV.Layer = 'Electrodo general PAT'


    
    #Creamos los bloques de insercion
    #TERM PAT 
    # BL_term_estructura = 
    definir_bloque_terminal_circular('Term estr PAT', 4)
    # BL_term_caja = 
    definir_bloque_terminal_cuadrado('Term DCBox PAT', 1)
    
    
    
    #LAT PAT ENTRE TRACKERS
        #Creamos la definicion del bloque usado en los terminales del latiguillo
    # BL_term_lat_PAT_ett = 
    definir_bloque_terminal_circular('Term lat PAT', 1)     # para borrarlo acad.doc.Blocks.Item('BLOCK Lat PAT entre trackers').Delete()
    
    #Creamos la definicion del bloque latiguillo                            
    BL_PAT_lat_ett = acad.doc.Blocks.Add(APoint(0,0,0), 'BLOCK Lat PAT entre trackers')
        #le añadimos los cables
    BL_ver_PAT_lat_ett = BL_PAT_lat_ett.AddPolyline(aDouble(-0.05, 0.25, 0   , -0.05, sep+0.4, 0))
    BL_ver_PAT_lat_ett.color = 76
    BL_ver_PAT_lat_ett.ConstantWidth = 0.1
    BL_ama_PAT_lat_ett = BL_PAT_lat_ett.AddPolyline(aDouble(0.05, 0.25, 0   , 0.05, sep+0.4, 0))
    BL_ama_PAT_lat_ett.color = 2
    BL_ama_PAT_lat_ett.ConstantWidth = 0.1
        #le añadimos los terminales
    BL_PAT_lat_ett.InsertBlock(APoint(0,0,0), 'Term lat PAT', 1, 1, 1, 0)
    BL_PAT_lat_ett.InsertBlock(APoint(0,sep+0.65,0), 'Term lat PAT', 1, 1, 1, 0)
    
    
    
    #LAT PAT EN PRIMERA PICA
        #Creamos la definicion del bloque usado en los terminales del latiguillo
    # BL_term_lat_PAT_pp = 
    definir_bloque_terminal_circular('Term lat PAT', 1)     # para borrarlo acad.doc.Blocks.Item('BLOCK Lat PAT entre trackers').Delete()
    
    #Creamos la definicion del bloque latiguillo                            
    BL_PAT_lat_pp = acad.doc.Blocks.Add(APoint(0,0,0), 'BLOCK Lat PAT primera pica')
        #le añadimos los cables
    BL_ver_PAT_lat_pp = BL_PAT_lat_pp.AddPolyline(aDouble(-0.05, 0.25, 0   , -0.05, dist_primera_pica_extremo_tr-0.25, 0))
    BL_ver_PAT_lat_pp.color = 76
    BL_ver_PAT_lat_pp.ConstantWidth = 0.1
    BL_ama_PAT_lat_pp = BL_PAT_lat_pp.AddPolyline(aDouble(0.05, 0.25, 0   , 0.05, dist_primera_pica_extremo_tr-0.25, 0))
    BL_ama_PAT_lat_pp.color = 2
    BL_ama_PAT_lat_pp.ConstantWidth = 0.1
        #le añadimos los terminales
    BL_PAT_lat_pp.InsertBlock(APoint(0,0,0), 'Term lat PAT', 1, 1, 1, 0)
    BL_PAT_lat_pp.InsertBlock(APoint(0,dist_primera_pica_extremo_tr,0), 'Term lat PAT', 1, 1, 1, 0)


        
    
    
    #Dibujamos con los valores recibidos
    if all_blocks==True:
        for i in range(bloque_inicial,n_bloques+1):
            for b in range(0,max_b):
                if ~np.isnan(PAT_terminal_primera_pica[i,b,0,0]): #si la banda no está vacía
                    for f in range(0,max_f_str_b):      
                        if ~np.isnan(PAT_terminal_primera_pica[i,b,f,0]): #si la fila no está vacía
                        
                            #TERMINALES PRIMERA PICA
                            punto_insercion_tpp = APoint(PAT_terminal_primera_pica[i,b,f,0], PAT_terminal_primera_pica[i,b,f,1])
                            bloque_insertado = acad.model.InsertBlock(punto_insercion_tpp, 'Term estr PAT', 1, 1, 1, 0)
                            bloque_insertado.Layer = 'PAT Estructura en primera pica'
                            
                            #LATIGUILLO PRIMERA PICA
                            punto_insercion_lpp = APoint(PAT_latiguillo_primera_pica[i,b,f,0], PAT_latiguillo_primera_pica[i,b,f,1])
                            bloque_insertado = acad.model.InsertBlock(punto_insercion_lpp, 'BLOCK Lat PAT primera pica', 1, 1, 1, 0)
                            bloque_insertado.Layer = 'PAT Latiguillo primera pica'
                            
                            for salto in range(0,max_tpf):      
                               if ~np.isnan(PAT_latiguillo_entre_trackers[i,b,f,salto,0]): #si el primer salto no está vacio
                                   punto_insercion_let = APoint(PAT_latiguillo_entre_trackers[i,b,f,salto,0],PAT_latiguillo_entre_trackers[i,b,f,salto,1])
                                   bloque_insertado = acad.model.InsertBlock(punto_insercion_let, 'BLOCK Lat PAT entre trackers', 1, 1, 1, 0)
                                   bloque_insertado.Layer = 'PAT Latiguillo entre trackers'
                            
                    for c in range (0,max_c):        
                        #TERMINALES CAJAS
                        punto_insercion_dcb = APoint(PAT_terminal_DC_Box[i,b,c,0], PAT_terminal_DC_Box[i,b,c,1])
                        bloque_insertado = acad.model.InsertBlock(punto_insercion_dcb, 'Term DCBox PAT', 1, 1, 1, 0)
                        bloque_insertado.Layer = 'PAT DC Box'
                            
                           
    else: #solo un bloque
        i=single_block
        #Dibujar Cable de String
        for b in range(0,max_b):
            if ~np.isnan(PAT_terminal_primera_pica[i,b,0,0]): #si la banda no está vacía
                for f in range(0,max_f_str_b):      
                    if ~np.isnan(PAT_terminal_primera_pica[i,b,f,0]): #si la fila no está vacía
                    
                        #TERMINALES PRIMERA PICA
                        punto_insercion_tpp = APoint(PAT_terminal_primera_pica[i,b,f,0], PAT_terminal_primera_pica[i,b,f,1])
                        bloque_insertado = acad.model.InsertBlock(punto_insercion_tpp, 'Term estr PAT', 1, 1, 1, 0)
                        bloque_insertado.Layer = 'PAT Estructura en primera pica'
                        
                        #LATIGUILLO PRIMERA PICA
                        punto_insercion_lpp = APoint(PAT_latiguillo_primera_pica[i,b,f,0], PAT_latiguillo_primera_pica[i,b,f,1])
                        bloque_insertado = acad.model.InsertBlock(punto_insercion_lpp, 'BLOCK Lat PAT primera pica', 1, 1, 1, 0)
                        bloque_insertado.Layer = 'PAT Latiguillo primera pica'
                        
                        for salto in range(0,max_tpf):      
                           if ~np.isnan(PAT_latiguillo_entre_trackers[i,b,f,salto,0]): #si el primer salto no está vacio
                               punto_insercion_let = APoint(PAT_latiguillo_entre_trackers[i,b,f,salto,0],PAT_latiguillo_entre_trackers[i,b,f,salto,1])
                               bloque_insertado = acad.model.InsertBlock(punto_insercion_let, 'BLOCK Lat PAT entre trackers', 1, 1, 1, 0)
                               bloque_insertado.Layer = 'PAT Latiguillo entre trackers'
                        
                for c in range (0,max_c):        
                    #TERMINALES CAJAS
                    punto_insercion_dcb = APoint(PAT_terminal_DC_Box[i,b,c,0], PAT_terminal_DC_Box[i,b,c,1])
                    bloque_insertado = acad.model.InsertBlock(punto_insercion_dcb, 'Term DCBox PAT', 1, 1, 1, 0)
                    bloque_insertado.Layer = 'PAT DC Box'
    


                    

    # -----------------DIBUJAR ELECTRODO PAT----------------------
    
    #Simulamos de manera similar a las zanjas DC y LV       
    if all_blocks == True:
        for i in range(len(zanjas_DC_ID)):
            dibujar_electrodo_PAT(zanjas_DC_ID[i,[2,3]], zanjas_DC_ID[i,[4,5]])
        for i in range(len(zanjas_LV_ID)):    
            dibujar_electrodo_PAT(zanjas_LV_ID[i][3][4], zanjas_LV_ID[i][5][6]) 


    #centramos la ventana de AutoCAD en el dibujo
    time.sleep(0.1)            
    doc = acad.app.ActiveDocument        
    time.sleep(0.3) #le damos un tiempo para que autocad no se autobloquee            
    doc.SendCommand("._zoom _extents\n")  # Simula el comando Zoom Extents

    
   
            