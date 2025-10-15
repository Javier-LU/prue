# =============================================================================
# Pestaña 4: “AASS & Conduits” se integra con AutoCAD.
#  UI: tres paneles:
#  - TUBOS (DC conduits): dibujar/leer tubos DC (por bloque o todos) y campo de “Safety Margin (%)”.
#  - AASS (LVAC & Ethernet): simular recorridos y dibujar/leer polilíneas (incluye CCTV, O&M, Warehouse).
#  - Fibra óptica (FO): UI con líneas y tramos (añadir/eliminar), leer configuración desde inputs, simular rutas FO y dibujar/leer polilíneas FO.

# =============================================================================

# ------------------------------ CONSTANTES -----------------------------------

XREF_UNIFIED = "XREF_Unified.dwg"
XREF_DC_CONDUITS = "XREF_DC_Conduits.dwg"
XREF_AASS_CABLES = "XREF_AASS_Cables.dwg"
XREF_FO = "XREF_FO.dwg"

MSG = {
    "draw_ok":          "Information added successfully to drawing. It is recommended to save it as {name}",
    "read_ok":          "Information successfully modified in IXPHOS model.",
    "acad_closed":      "AutoCAD could not be used, please check that AutoCAD is open.",
    "acad_busy":        "AutoCAD is busy. Please, do not interact with it while drawing.",
    "draw_err":         "There was an error while drawing, please check data.",
    "read_err":         "There was an error while reading, please retry.",
    "read_err_hint":    "There was an error while reading, please check that originally drawn elements have not been copypasted or retry.",
    "no_dc_polys":      "There are no tubos_DC polylines in the active document. Try to open XREF_DC_Conduits or activate the correct .dwg file",
    "no_aass_polys":    "There are no AASS_LVAC and ethernet polylines in the active document. Try to open XREF_AASS_Cables or activate the correct .dwg file",
    "no_fo_polys":      "There are no fiber optic polylines with the mentioned layer name in the active document. Check the layer name, try to open XREF_FO or activate the correct .dwg file",
    "proc_err":         "There was an error while processing, please check data.",
    "graph_err":        "There was an error while connecting routes, please check that all roads start and end from common vertex.",
}

# ------------------------------ LAYOUT/UI ------------------------------------

frame_aass_tubos_container = tk.Frame(AASS_NB, background=BLANCO_ROTO)
frame_aass_tubos_container.pack(side="left", padx=30, pady=30, fill="both", expand=True)

frame_tubos = tk.Frame(frame_aass_tubos_container, background=BLANCO_ROTO)
frame_tubos.pack(side="left", padx=30, pady=30, fill="both", expand=True)

frame_AASS = tk.Frame(frame_aass_tubos_container, background=BLANCO_ROTO)
frame_AASS.pack(side="left", padx=30, pady=30, fill="both", expand=True)

frame_FO_lines = tk.Frame(frame_aass_tubos_container, background=BLANCO_ROTO)
frame_FO_lines.pack(side="left", padx=30, pady=30, fill="both", expand=True)

# ------------------------- HELPERS (REUTILIZABLES) ---------------------------

def _show_info(text): messagebox.showinfo("Info", text)
def _show_error(text): messagebox.showerror("Error", text)

def _map_com_error(e):
    if getattr(e, "hresult", None) == -2147417846:
        return "acad_busy"
    return "draw_err"

class COMInit:
    """Contexto para inicializar y cerrar COM en hilos secundarios."""
    def __enter__(self):
        pythoncom.CoInitialize()
    def __exit__(self, exc_type, exc, tb):
        pythoncom.CoUninitialize()

def _run_with_spinner(task_fn, on_done):
    """Corre task_fn en un hilo y al terminar cierra spinner y llama on_done."""
    ventana_carga = crear_gif_espera()
    def _runner():
        task_fn()
        root.after(0, lambda: on_done(ventana_carga))
    threading.Thread(target=_runner, daemon=True).start()

def _with_acad_for_draw(ref_name, draw_callable):
    """Abre conexión para dibujar y ejecuta draw_callable(acad). Retorna clave de error o None."""
    try:
        with COMInit():
            acad = AutoCAD_extension.conexion_con_CAD_para_dibujar(ref_name)
            if acad is None:
                return "acad_closed"
            root.after(0, lambda: time.sleep(0.5))
            draw_callable(acad)
        return None
    except comtypes.COMError as e:
        return _map_com_error(e)
    except Exception:
        traceback.print_exc()
        return "draw_err"

def _with_acad_for_read(ref_name, read_callable):
    """Abre conexión para leer y ejecuta read_callable(acad) -> (ok:bool, reason:str|None)."""
    try:
        with COMInit():
            acad = AutoCAD_extension.conexion_con_CAD_para_leer(ref_name)
            if acad is None:
                return False, "acad_closed"
            root.after(0, lambda: time.sleep(0.5))
            ok, reason = read_callable(acad)
        return ok, reason
    except comtypes.COMError as e:
        return False, _map_com_error(e)
    except Exception:
        traceback.print_exc()
        return False, "read_err"

# ------------------------------ TUBOS DC -------------------------------------

entrada_all_blocks_tubos_DC = tk.BooleanVar(value=False)
all_blocks_tubos_DC = True
single_block_tubos_DC = 1

def update_single_block_tubos_DC():
    """Actualiza el bloque seleccionado asociado a los tubos DC."""
    global single_block_tubos_DC
    single_block_tubos_DC = int(spinbox_tubos_DC.get())

def activate_spinbox_tubos_DC():
    """Activa/desactiva el selector de bloque para tubos DC."""
    global all_blocks_tubos_DC, single_block_tubos_DC
    if entrada_all_blocks_tubos_DC.get():
        spinbox_tubos_DC.config(state="normal")
        all_blocks_tubos_DC = False
        single_block_tubos_DC = int(spinbox_tubos_DC.get())
    else:
        spinbox_tubos_DC.config(state="disabled")
        all_blocks_tubos_DC = True

spinbox_tubos_DC = tk.Spinbox(
    frame_tubos, from_=1, to=100, state="disabled",
    command=update_single_block_tubos_DC, width=2, font=("Montserrat", 10)
)
spinbox_tubos_DC.grid(row=2, column=0, padx=5, pady=5, sticky="w")

check_tubos_DC = ttk.Checkbutton(
    frame_tubos, text="Single block",
    variable=entrada_all_blocks_tubos_DC, command=activate_spinbox_tubos_DC
)
check_tubos_DC.grid(row=2, column=1, padx=5, pady=5, sticky="w")

def dibujar_tubos_DC():
    """Dibuja los tubos DC con los datos actuales."""
    def task():
        def draw(acad):
            AutoCAD_extension.CAD_draw_tubo_DC(
                acad, all_blocks_tubos_DC, single_block_tubos_DC,
                bloque_inicial, n_bloques, max_tubos_DC_bloque, pol_tubo_corrugado_zanja_DC
            )
        nonlocal_error[0] = _with_acad_for_draw(XREF_UNIFIED, draw)

    def done(win):
        win.destroy()
        err = nonlocal_error[0]
        if err is None:
            _show_info(MSG["draw_ok"].format(name="XREF_tubos_DC_Cables"))
        elif err == "acad_closed":
            _show_error(MSG["acad_closed"])
        elif err == "acad_busy":
            _show_error(MSG["acad_busy"])
        else:
            _show_error(MSG["draw_err"])

    nonlocal_error = [None]
    _run_with_spinner(task, done)

def leer_conf_tubos_DC():
    """Lee la configuración de tubos DC desde AutoCAD y actualiza variables."""
    def task():
        def read(acad):
            # Devuelve tupla (ok, reason). reason puede ser clave de error o None.
            nonlocal result
            # s1: pol_tubo_corrugado_zanja_DC, s2: max_tubos_DC_bloque
            s1, s2 = AutoCAD_extension.CAD_read_tubo_zanja_DC(
                acad, all_blocks_tubos_DC, single_block_tubos_DC,
                bloque_inicial, n_bloques, max_p, strings_fisicos, pol_tubo_corrugado_zanja_DC
            )
            if s1 is None:
                result = (False, "no_dc_polys")
            else:
                # Actualiza y guarda
                globals()["pol_tubo_corrugado_zanja_DC"] = s1
                globals()["max_tubos_DC_bloque"] = s2
                guardar_variables(
                    [pol_tubo_corrugado_zanja_DC, max_tubos_DC_bloque],
                    ["pol_tubo_corrugado_zanja_DC", "max_tubos_DC_bloque"]
                )
                result = (True, None)
        ok, reason = _with_acad_for_read(XREF_DC_CONDUITS, read)
        nonlocal_result[0] = (ok, reason)

    def done(win):
        win.destroy()
        ok, reason = nonlocal_result[0]
        if ok:
            _show_info(MSG["read_ok"])
        else:
            if reason in MSG:
                _show_error(MSG[reason])
            else:
                _show_error(MSG["read_err"])

    result = None
    nonlocal_result = [None]
    _run_with_spinner(task, done)

boton_tubos_DC_CAD_draw = tk.Button(
    frame_tubos, text="Draw DC Conduits", command=dibujar_tubos_DC,
    bg=ROJO_GRS, fg="white", font=("Montserrat", 10, "bold")
)
boton_tubos_DC_CAD_draw.grid(row=1, column=0, pady=20)

boton_tubos_DC_CAD_read = tk.Button(
    frame_tubos, text="Read changes", command=leer_conf_tubos_DC,
    bg=ROJO_GRS, fg="white", font=("Montserrat", 10, "bold")
)
boton_tubos_DC_CAD_read.grid(row=3, column=0, pady=20)

# -------- Inputs medición (tubos DC)

def entradas_medicion_tubos_DC(valores_dados_dc_conduits):
    """Renderiza inputs de margen de seguridad para DC conduits."""
    global valor_safety_maj_dc_conduit
    etiqueta = tk.Label(
        frame_tubos, text="Safety Margin (%)", fg=ROJO_GRS, bg=GRIS_SUAVE,
        font=("Montserrat", 10, "bold")
    )
    etiqueta.grid(row=4, column=0, padx=(10, 0), pady=(15, 15))
    valor_safety_maj_dc_conduit = tk.StringVar(value=valores_dados_dc_conduits[0])
    tk.Entry(frame_tubos, textvariable=valor_safety_maj_dc_conduit, width=5).grid(
        row=4, column=1, padx=(5, 20), pady=(15, 15)
    )

valores_iniciales_tubos = [[]]

# ------------------- SERVICIOS AUXILIARES (LVAC & Ethernet) ------------------

def simular_polilineas_AASS_LVAC_y_ethernet():
    """Simula polilíneas AASS LVAC y Ethernet y guarda resultados."""
    global pol_AASS_LVAC, pol_ethernet, max_p_AASS_LVAC, max_p_AASS_eth, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC
    (pol_AASS_LVAC, pol_ethernet, max_p_AASS_LVAC, max_p_AASS_eth,
     pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC) = (
        alg_cables.polilineas_AASS_LVAC_y_ethernet(
            bloque_inicial, n_bloques, coord_PCS_AASS_inputs, coord_Comboxes,
            coord_Tracknets, coord_TBoxes, coord_AWS, coord_CCTV,
            coord_OyM_LVAC, coord_SS_LVAC, coord_Warehouse_LVAC
        )
    )
    guardar_variables(
        [pol_AASS_LVAC, pol_ethernet, max_p_AASS_LVAC, max_p_AASS_eth, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC],
        ["pol_AASS_LVAC", "pol_ethernet", "max_p_AASS_LVAC", "max_p_AASS_eth", "pol_CCTV_LVAC", "pol_OyM_supply_LVAC", "pol_Warehouse_supply_LVAC"]
    )

def dibujar_AASS_LVAC_y_ethernet():
    """Dibuja AASS LVAC y Ethernet."""
    def task():
        def draw(acad):
            AutoCAD_extension.CAD_draw_AASS_LVAC_y_ethernet(
                acad, bloque_inicial, n_bloques, pol_AASS_LVAC, pol_ethernet,
                pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC
            )
        nonlocal_error[0] = _with_acad_for_draw(XREF_UNIFIED, draw)

    def done(win):
        win.destroy()
        err = nonlocal_error[0]
        if err is None:
            _show_info(MSG["draw_ok"].format(name="XREF_AASS_Cables"))
        elif err == "acad_closed":
            _show_error(MSG["acad_closed"])
        elif err == "acad_busy":
            _show_error(MSG["acad_busy"])
        else:
            _show_error(MSG["draw_err"])

    nonlocal_error = [None]
    _run_with_spinner(task, done)

def leer_AASS_LVAC_y_ethernet():
    """Lee polilíneas AASS LVAC y Ethernet y actualiza variables."""
    def task():
        def read(acad):
            nonlocal result
            s1, s2, s3, s4, s5 = AutoCAD_extension.CAD_read_AASS_LVAC_y_ethernet(
                acad, bloque_inicial, n_bloques, pol_AASS_LVAC, pol_ethernet,
                coord_Comboxes, coord_Tracknets, coord_TBoxes, coord_AWS, coord_PCS_AASS_inputs
            )
            if s1 is None and s2 is None and s3 == [] and s4 == [] and s5 == []:
                result = (False, "no_aass_polys")
            else:
                globals()["pol_AASS_LVAC"] = s1
                globals()["pol_CCTV_LVAC"] = s2
                globals()["pol_OyM_supply_LVAC"] = s3
                globals()["pol_Warehouse_supply_LVAC"] = s4
                globals()["pol_ethernet"] = s5
                guardar_variables(
                    [pol_AASS_LVAC, pol_CCTV_LVAC, pol_OyM_supply_LVAC, pol_Warehouse_supply_LVAC, pol_ethernet],
                    ["pol_AASS_LVAC", "pol_CCTV_LVAC", "pol_OyM_supply_LVAC", "pol_Warehouse_supply_LVAC", "pol_ethernet"]
                )
                result = (True, None)
        ok, reason = _with_acad_for_read(XREF_AASS_CABLES, read)
        nonlocal_result[0] = (ok, reason)

    def done(win):
        win.destroy()
        ok, reason = nonlocal_result[0]
        if ok:
            _show_info(MSG["read_ok"])
        else:
            _show_error(MSG.get(reason, MSG["read_err"]))

    result = None
    nonlocal_result = [None]
    _run_with_spinner(task, done)

boton_simular_LVAC_ETH = tk.Button(
    frame_AASS, text="Simulate AASS", command=simular_polilineas_AASS_LVAC_y_ethernet,
    bg=ROJO_GRS, fg="white", font=("Montserrat", 10, "bold")
)
boton_simular_LVAC_ETH.grid(row=0, column=0, pady=20)

boton_dibujar_LVAC_ETH = tk.Button(
    frame_AASS, text="Draw AASS", command=dibujar_AASS_LVAC_y_ethernet,
    bg=ROJO_GRS, fg="white", font=("Montserrat", 10, "bold")
)
boton_dibujar_LVAC_ETH.grid(row=1, column=0, pady=20)

boton_leer_LVAC_ETH = tk.Button(
    frame_AASS, text="Read changes", command=leer_AASS_LVAC_y_ethernet,
    bg=ROJO_GRS, fg="white", font=("Montserrat", 10, "bold")
)
boton_leer_LVAC_ETH.grid(row=3, column=0, pady=20)

# ----------------------------- FIBRA ÓPTICA ----------------------------------

entradas_lineas_FO = []
contador_tramos_FO = 0

# Canvas con scroll para FO
canvas_lineas_FO = tk.Canvas(frame_FO_lines, height=400)
scrollbar_lineas_FO = ttk.Scrollbar(frame_FO_lines, orient="vertical", command=canvas_lineas_FO.yview)
scrollable_frame_lineas_FO = ttk.Frame(canvas_lineas_FO)
scrollable_frame_lineas_FO.bind("<Configure>", lambda e: canvas_lineas_FO.configure(scrollregion=canvas_lineas_FO.bbox("all")))
canvas_frame_lineas_FO = canvas_lineas_FO.create_window((0, 0), window=scrollable_frame_lineas_FO, anchor="nw")
canvas_lineas_FO.configure(yscrollcommand=scrollbar_lineas_FO.set)
canvas_lineas_FO.grid(row=0, column=0, columnspan=3, sticky="nsew")
scrollbar_lineas_FO.grid(row=0, column=3, sticky="ns")

def agregar_linea_FO():
    """Añade una nueva línea FO (cabecera)."""
    global entradas_lineas_FO, contador_tramos_FO
    fila_frame = ttk.Frame(scrollable_frame_lineas_FO)
    fila_frame.pack(anchor="w", fill="x")
    etiqueta = ttk.Label(fila_frame, text=f"Line {len(entradas_lineas_FO) + 1}")
    etiqueta.pack(side="left", padx=5, pady=5)
    entradas_lineas_FO.append([etiqueta, []])
    contador_tramos_FO = 0

def agregar_tramo_linea_FO():
    """Añade un tramo a la última línea FO."""
    global entradas_lineas_FO, contador_tramos_FO
    if not entradas_lineas_FO:
        return
    contador_tramos_FO += 1
    sub_frame = ttk.Frame(scrollable_frame_lineas_FO)
    sub_frame.pack(anchor="w", fill="x", padx=20)
    ttk.Label(sub_frame, text=f"L {len(entradas_lineas_FO)}.{contador_tramos_FO}").pack(side="left", padx=5, pady=5)
    entry1 = ttk.Entry(sub_frame, width=10); entry1.pack(side="left", padx=5)
    entry2 = ttk.Entry(sub_frame, width=10); entry2.pack(side="left", padx=5)
    entradas_lineas_FO[-1][1].append([entry1, entry2])

def eliminar_ultimo_elemento_FO():
    """Elimina el último tramo o línea FO."""
    global entradas_lineas_FO, contador_tramos_FO
    if not entradas_lineas_FO:
        return
    etiqueta, subfilas = entradas_lineas_FO[-1]
    if subfilas:
        # destruir el sub_frame (padre de ambos Entry)
        sub_frame = subfilas.pop()[0].master
        sub_frame.destroy()
        contador_tramos_FO = max(0, contador_tramos_FO - 1)
    else:
        etiqueta.master.destroy()
        entradas_lineas_FO.pop()

ttk.Button(frame_FO_lines, text="Add FO Line", command=agregar_linea_FO).grid(row=1, column=0, pady=10, padx=5)
ttk.Button(frame_FO_lines, text="Add Connection", command=agregar_tramo_linea_FO).grid(row=1, column=1, pady=10, padx=5)
ttk.Button(frame_FO_lines, text="Remove Last", command=eliminar_ultimo_elemento_FO).grid(row=1, column=2, pady=10, padx=5)

def cargar_entradas_lineas_FO():
    """Carga líneas FO guardadas en la UI."""
    global entradas_lineas_FO, contador_tramos_FO
    while entradas_lineas_FO:
        eliminar_ultimo_elemento_FO()
    for item in lineas_FO:
        if item == [0]:
            continue
        etiqueta_texto, tramos = item
        agregar_linea_FO()
        entradas_lineas_FO[-1][0].config(text=etiqueta_texto)
        for val1, val2 in tramos:
            agregar_tramo_linea_FO()
            entry1, entry2 = entradas_lineas_FO[-1][1][-1]
            entry1.insert(0, str(val1))
            entry2.insert(0, str(val2))

def leer_config_FO():
    """Lee configuración FO desde la UI y genera pol_cable_FO + validaciones."""
    def task():
        nonlocal errors
        errors = []
        globals()["lineas_FO"] = [[0]]
        globals()["pol_cable_FO"] = [[0]]

        c_l = 0
        for etiqueta, subfilas in entradas_lineas_FO:
            texto = etiqueta.cget("text")
            valores_subfilas = []
            pol_cable_FO.append([0])
            c_l += 1
            for entrada_1, entrada_2 in subfilas:
                v1 = entrada_1.get()
                v2 = entrada_2.get()

                # Orígenes/destinos especiales o por bloque
                if v1 in ("O&M", "OyM", "OYM"):
                    coord_ini = coord_OyM_Control_Room
                elif v1 == "SS":
                    coord_ini = coord_SS_Control_Room
                else:
                    coord_ini = coord_Comboxes[int(v1)]

                if v2 in ("O&M", "OyM", "OYM"):
                    coord_fin = coord_OyM_Control_Room
                elif v2 == "SS":
                    coord_fin = coord_SS_Control_Room
                else:
                    coord_fin = coord_Comboxes[int(v2)]

                if v1 == v2:
                    errors.append([f"L{c_l}", f"B{v1}"])

                valores_subfilas.append([v1, v2])
                pol_cable_FO[c_l].append([coord_ini, coord_fin])

            lineas_FO.append([texto, valores_subfilas])

        guardar_variables([lineas_FO, pol_cable_FO], ["lineas_FO", "pol_cable_FO"])

    def done(win):
        win.destroy()
        if errors:
            _show_error(f"Introduced values are duplicated: {errors}")

    errors = []
    _run_with_spinner(task, done)

boton_leer_config_FO = tk.Button(
    frame_FO_lines, text="Read Values", command=leer_config_FO,
    bg=ROJO_GRS, fg="white", font=("Montserrat", 10, "bold")
)
boton_leer_config_FO.grid(row=2, column=0, pady=50, padx=5)

def simular_polilineas_cable_FO():
    """Simula polilíneas de FO siguiendo la guía."""
    def task():
        try:
            new_pol, error = alg_cables.lineas_MV_o_FO_por_caminos(
                pol_guia_MV_FO, pol_cable_FO, "FO"
            )
            globals()["pol_cable_FO"] = new_pol
            guardar_variables([pol_cable_FO], ["pol_cable_FO"])
            nonlocal_status[0] = None if not error else "graph_err"
        except Exception:
            traceback.print_exc()
            nonlocal_status[0] = "proc_err"

    def done(win):
        win.destroy()
        status = nonlocal_status[0]
        if status is None:
            return
        _show_error(MSG[status])

    nonlocal_status = [None]
    _run_with_spinner(task, done)

boton_polilineas_FO = tk.Button(
    frame_FO_lines, text="Simulate FO", command=simular_polilineas_cable_FO,
    bg=ROJO_GRS, fg="white", font=("Montserrat", 10, "bold")
)
boton_polilineas_FO.grid(row=3, column=0, columnspan=1, pady=20)

def dibujar_cable_FO():
    """Dibuja polilíneas FO en CAD."""
    def task():
        def draw(acad):
            AutoCAD_extension.CAD_draw_polilineas_FO(acad, pol_cable_FO)
        nonlocal_error[0] = _with_acad_for_draw(XREF_UNIFIED, draw)

    def done(win):
        win.destroy()
        err = nonlocal_error[0]
        if err is None:
            _show_info(MSG["draw_ok"].format(name="XREF_FO_Cables"))
        elif err == "acad_closed":
            _show_error(MSG["acad_closed"])
        elif err == "acad_busy":
            _show_error(MSG["acad_busy"])
        else:
            _show_error(MSG["draw_err"])

    nonlocal_error = [None]
    _run_with_spinner(task, done)

boton_cable_FO_CAD_draw = tk.Button(
    frame_FO_lines, text="Draw FO Cables", command=dibujar_cable_FO,
    bg=ROJO_GRS, fg="white", font=("Montserrat", 10, "bold")
)
boton_cable_FO_CAD_draw.grid(row=3, column=1, pady=20)

def leer_polilineas_fibra_optica():
    """Lee polilíneas FO desde CAD y actualiza pol_cable_FO."""
    def task():
        def read(acad):
            nonlocal result
            salida = AutoCAD_extension.CAD_read_polilineas_FO(acad, pol_cable_FO)
            if salida is None:
                result = (False, "no_fo_polys")
            else:
                globals()["pol_cable_FO"] = salida
                guardar_variables([pol_cable_FO], ["pol_cable_FO"])
                result = (True, None)
        ok, reason = _with_acad_for_read(XREF_FO, read)
        nonlocal_result[0] = (ok, reason)

    def done(win):
        win.destroy()
        ok, reason = nonlocal_result[0]
        if ok:
            _show_info(MSG["read_ok"])
        else:
            # para lectura FO preferimos el mensaje con pista
            if reason == "no_fo_polys":
                _show_error(MSG["no_fo_polys"])
            elif reason == "acad_closed":
                _show_error(MSG["acad_closed"])
            elif reason == "acad_busy":
                _show_error(MSG["acad_busy"])
            else:
                _show_error(MSG["read_err_hint"])

    result = None
    nonlocal_result = [None]
    _run_with_spinner(task, done)

boton_leer_polilineas_FO = tk.Button(
    frame_FO_lines, text="Read changes", command=leer_polilineas_fibra_optica,
    bg=ROJO_GRS, fg="white", font=("Montserrat", 10, "bold")
)
boton_leer_polilineas_FO.grid(row=3, column=2, pady=20)

# ----------------------------- REGISTRO PESTAÑA ------------------------------

AASS_SECTION = TabSection(
    key="aass",
    title="AASS & conduits",
    icon="Pestaña 4.png",
    groups=FunctionalGroup(
        io={
            "draw_dc_tubes": dibujar_tubos_DC,
            "draw_aux_services": dibujar_AASS_LVAC_y_ethernet,
            "draw_fiber_optic": dibujar_cable_FO,
        },
        processing={
            "read_dc_tubes": leer_conf_tubos_DC,
            "simulate_aux_services": simular_polilineas_AASS_LVAC_y_ethernet,
            "read_aux_services": leer_AASS_LVAC_y_ethernet,
            "read_fiber_optic_config": leer_config_FO,
            "simulate_fiber_optic": simular_polilineas_cable_FO,
            "read_fiber_optic_polylines": leer_polilineas_fibra_optica,
        },
        ui={
            "render_dc_tube_inputs": entradas_medicion_tubos_DC,
            "update_single_block_tubes": update_single_block_tubos_DC,
            "activate_spinbox_tubes": activate_spinbox_tubos_DC,
            "add_fiber_line": agregar_linea_FO,
            "add_fiber_segment": agregar_tramo_linea_FO,
            "remove_last_fiber_element": eliminar_ultimo_elemento_FO,
            "render_fiber_inputs": cargar_entradas_lineas_FO,
        },
    ),
)
