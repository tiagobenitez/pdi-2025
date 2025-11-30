import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import datetime
import os
import json
import shutil
import tempfile

ARCHIVO_COPIAS = "copias.json"

# ============================================
#   FUNCIONES BASE
# ============================================

def buscar_mysqldump():
    posibles_rutas = [
        r"C:\xampp\mysql\bin\mysqldump.exe",
        r"C:\Program Files\xampp\mysql\bin\mysqldump.exe",
        r"C:\Program Files (x86)\xampp\mysql\bin\mysqldump.exe",
        r"D:\xampp\mysql\bin\mysqldump.exe",
        r"D:\Program Files\xampp\mysql\bin\mysqldump.exe",
    ]
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return ruta
    for unidad in ["C:\\", "D:\\"]:
        for raiz, dirs, archivos in os.walk(unidad):
            if "mysqldump.exe" in archivos:
                return os.path.join(raiz, "mysqldump.exe")
    return None

def obtener_mysqldump_seguro():
    encontrado = buscar_mysqldump()
    if not encontrado:
        messagebox.showerror("mysqldump no encontrado",
                             "No se encontró mysqldump.exe. Instalá XAMPP.")
        return None
    temp_dir = os.path.join(tempfile.gettempdir(), "mysqldump_safe")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    destino = os.path.join(temp_dir, "mysqldump.exe")
    if not os.path.exists(destino) or os.path.getsize(destino) != os.path.getsize(encontrado):
        shutil.copy(encontrado, destino)
    return destino

def cargar_copias():
    if os.path.exists(ARCHIVO_COPIAS):
        try:
            with open(ARCHIVO_COPIAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_copias():
    with open(ARCHIVO_COPIAS, "w", encoding="utf-8") as f:
        json.dump(copias, f, indent=4, ensure_ascii=False)

copias = cargar_copias()

def carpeta_valida(path):
    path = path.lower().replace("/", "\\")
    prohibidas = [
        "c:\\program files",
        "c:\\program files (x86)",
        "c:\\windows",
        "c:\\programdata",
        "c:\\xampp\\mysql\\bin"
    ]
    return not any(path.startswith(p) for p in prohibidas)

# CORRECCIÓN 2: Modificado para aceptar is_programmed
def hacer_backup(is_programmed=False):
    usuario = entry_usuario.get().strip()
    contrasena = entry_contrasena.get().strip()
    base_datos = entry_bd.get().strip()
    destino = entry_destino.get().strip()
    
    if not usuario or not base_datos:
        messagebox.showerror("Error", "Completá usuario y base de datos.")
        return
    if not destino:
        messagebox.showerror("Error", "Seleccioná carpeta destino.")
        return
    if not carpeta_valida(destino):
        messagebox.showerror("Carpeta no permitida",
                             "Esa carpeta está protegida. Elegí otra.")
        return
    
    mysqldump_path = obtener_mysqldump_seguro()
    if not mysqldump_path:
        return
    
    # LÓGICA DE FECHA CORREGIDA
    if is_programmed and TAREA_PROGRAMADA["fecha"] and TAREA_PROGRAMADA["hora"]:
        # Usa la fecha y hora programadas para el nombre del archivo y el registro
        fecha_str = f"{TAREA_PROGRAMADA['fecha']}_{TAREA_PROGRAMADA['hora'].replace(':', '-')}"
        registro_hora = f"{TAREA_PROGRAMADA['fecha']} {TAREA_PROGRAMADA['hora']}:00"
    else:
        # Usa la fecha y hora actuales (para backup manual)
        ahora = datetime.datetime.now()
        fecha_str = ahora.strftime("%Y-%m-%d_%H-%M-%S")
        registro_hora = ahora.strftime("%Y-%m-%d %H:%M:%S")

    nombre_archivo = f"{base_datos}_backup_{fecha_str}.sql"
    ruta_completa = os.path.join(destino, nombre_archivo)
    
    try:
        comando = [mysqldump_path, "-u", usuario]
        if contrasena:
            comando.append(f"-p{contrasena}")
        comando.append(base_datos)
        with open(ruta_completa, "w", encoding="utf-8") as salida:
            resultado = subprocess.run(comando, stdout=salida, stderr=subprocess.PIPE, text=True)
        if resultado.returncode != 0:
            messagebox.showerror("Error", resultado.stderr)
            return
        
        # Llama a agregar_copia con la hora determinada
        agregar_copia(usuario, contrasena, base_datos, ruta_completa, registro_hora) 
        messagebox.showinfo("Éxito", f"Backup creado:\n{ruta_completa}")
    except Exception as e:
        messagebox.showerror("Error inesperado", str(e))

# CORRECCIÓN 2: Modificado para aceptar el parámetro 'hora'
def agregar_copia(usuario, contrasena, bd, ruta, hora=None):
    if hora is None:
        hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    copias.append({
        "usuario": usuario,
        "contrasena": contrasena,
        "bd": bd,
        "hora": hora,
        "ruta": ruta
    })
    guardar_copias()
    actualizar_tabla()

def seleccionar_destino():
    carpeta = filedialog.askdirectory()
    if carpeta:
        entry_destino.delete(0, tk.END)
        entry_destino.insert(0, carpeta)

def abrir_editar_copia(copia, indice):
    ventana_editar = tk.Toplevel(ventana)
    ventana_editar.title("✍️ Editar copia")
    ventana_editar.geometry("400x370")
    ventana_editar.configure(bg="#f4f4f9")

    frame_content = tk.Frame(ventana_editar, bg="#f4f4f9")
    frame_content.pack(fill="both", expand=True, padx=15, pady=15)

    # === CAMPOS ===
    tk.Label(frame_content, text="Usuario MySQL:", bg="#f4f4f9", fg="#333").pack(anchor="w")
    entry_usuario_edit = ttk.Entry(frame_content, width=40)
    entry_usuario_edit.pack(fill="x", pady=(0,5))
    entry_usuario_edit.insert(0, copia["usuario"])

    tk.Label(frame_content, text="Contraseña:", bg="#f4f4f9", fg="#333").pack(anchor="w")
    entry_contrasena_edit = ttk.Entry(frame_content, width=40, show="*")
    entry_contrasena_edit.pack(fill="x", pady=(0,5))
    entry_contrasena_edit.insert(0, copia["contrasena"])

    tk.Label(frame_content, text="Base de Datos:", bg="#f4f4f9", fg="#333").pack(anchor="w")
    entry_bd_edit = ttk.Entry(frame_content, width=40)
    entry_bd_edit.pack(fill="x", pady=(0,5))
    entry_bd_edit.insert(0, copia["bd"])

    tk.Label(frame_content, text="Ruta del archivo:", bg="#f4f4f9", fg="#333").pack(anchor="w")
    entry_ruta_edit = ttk.Entry(frame_content, width=40)
    entry_ruta_edit.pack(fill="x", pady=(0,5))
    entry_ruta_edit.insert(0, copia["ruta"])

    # === NUEVO → FECHA EDITABLE ===
    tk.Label(frame_content, text="Fecha (YYYY-MM-DD HH:MM:SS):", bg="#f4f4f9", fg="#333").pack(anchor="w")
    entry_fecha_edit = ttk.Entry(frame_content, width=40)
    entry_fecha_edit.pack(fill="x", pady=(0,10))
    entry_fecha_edit.insert(0, copia["hora"])

    # === GUARDAR CAMBIOS ===
    def guardar_cambios():
        nueva_fecha = entry_fecha_edit.get().strip()

        # Validación básica de fecha
        try:
            datetime.datetime.strptime(nueva_fecha, "%Y-%m-%d %H:%M:%S")
        except:
            messagebox.showerror("Fecha inválida",
                                 "El formato debe ser:\nYYYY-MM-DD HH:MM:SS")
            return

        copia["usuario"] = entry_usuario_edit.get().strip()
        copia["contrasena"] = entry_contrasena_edit.get().strip()
        copia["bd"] = entry_bd_edit.get().strip()
        copia["ruta"] = entry_ruta_edit.get().strip()
        copia["hora"] = nueva_fecha  # ← FECHA EDITADA

        copias[indice] = copia
        guardar_copias()
        actualizar_tabla()

        ventana_editar.destroy()
        messagebox.showinfo("Éxito", "Copia editada correctamente.")

    ttk.Button(frame_content, text="Guardar cambios", command=guardar_cambios).pack(pady=10)


def eliminar_copia_dialogo(indice):
    if messagebox.askyesno("Confirmar Eliminación", "¿Querés eliminar esta copia del registro?"):
        copias.pop(indice)
        guardar_copias()
        actualizar_tabla()
        messagebox.showinfo("Éxito", "Copia eliminada del registro.")

# ============================================
#   PROGRAMACIÓN AUTOMÁTICA
# ============================================

TAREA_PROGRAMADA = {"fecha": None, "hora": None}

def programar_backup():
    fecha = entry_fecha.get().strip()
    hora = entry_hora.get().strip()

    if not fecha or not hora or fecha == "YYYY-MM-DD" or hora == "HH:MM":
        messagebox.showerror("Error de Programación", "Debes ingresar una fecha (AAAA-MM-DD) y una hora (HH:MM) válidas.")
        return

    try:
        datetime.datetime.strptime(fecha, "%Y-%m-%d")
        datetime.datetime.strptime(hora, "%H:%M")
    except:
        messagebox.showerror("Error de Formato", "Formato incorrecto. Usá AAAA-MM-DD para la fecha y HH:MM (24h) para la hora.")
        return

    TAREA_PROGRAMADA["fecha"] = fecha
    TAREA_PROGRAMADA["hora"] = hora
    
    # Limpiar los campos después de programar
    entry_fecha.delete(0, tk.END)
    entry_hora.delete(0, tk.END)
    entry_fecha.insert(0, "YYYY-MM-DD")
    entry_hora.insert(0, "HH:MM")
    
    messagebox.showinfo("Guardado", f"Backup programado para:\n{fecha} {hora}")

# CORRECCIÓN 2: Llama a hacer_backup con is_programmed=True
def verificar_programacion():
    if TAREA_PROGRAMADA["fecha"] and TAREA_PROGRAMADA["hora"]:
        ahora = datetime.datetime.now()
        try:
            fecha_prog = datetime.datetime.strptime(TAREA_PROGRAMADA["fecha"], "%Y-%m-%d")
            hora_prog = datetime.datetime.strptime(TAREA_PROGRAMADA["hora"], "%H:%M").time()
            fecha_hora_prog = datetime.datetime.combine(fecha_prog, hora_prog)
            
            if ahora >= fecha_hora_prog:
                messagebox.showinfo("Backup Programado", f"Ejecutando backup programado para {TAREA_PROGRAMADA['fecha']} a las {TAREA_PROGRAMADA['hora']}...")
                
                hacer_backup(is_programmed=True) # Llamada corregida
                
                TAREA_PROGRAMADA["fecha"] = None
                TAREA_PROGRAMADA["hora"] = None
        except ValueError:
             TAREA_PROGRAMADA["fecha"] = None
             TAREA_PROGRAMADA["hora"] = None

    ventana.after(10000, verificar_programacion)


# ============================================
#   INTERFAZ PRINCIPAL
# ============================================

ventana = tk.Tk()
ventana.title("🛡️ Backup MySQL Pro")
ventana.geometry("850x650")
ventana.resizable(True, True)
ventana.configure(bg="#f4f4f9")

# --- Estilos (Diseño Profesional) ---
style = ttk.Style()
style.theme_create("ModernPro", parent="alt", settings={
    "TFrame": {"configure": {"background": "#f4f4f9"}},
    "TLabel": {"configure": {"background": "#f4f4f9", "font": ("Arial", 10)}},
    "TEntry": {"configure": {"padding": 5, "fieldbackground": "white", "relief": "flat"}},
    "TButton": {"configure": {"font": ("Arial", 10, "bold"), "padding": 8}},
    "Treeview": {"configure": {"background": "white", "foreground": "#333", "rowheight": 28, "fieldbackground": "white", "font": ("Arial", 9)},
                 "map": {"background": [("selected", "#3498db")]}},
    "Treeview.Heading": {"configure": {"font": ("Arial", 10, "bold"), "background": "#2c3e50", "foreground": "white", "relief": "flat"}},
})
style.theme_use("ModernPro")

style.configure("Green.TButton", background="#4CAF50", foreground="white")
style.configure("Orange.TButton", background="#FF9800", foreground="white")
style.configure("Menu.TButton", background="#2c3e50", foreground="white", font=("Arial", 10, "bold"))
style.map("Menu.TButton", background=[('active', '#34495e')])


# --- HEADER Y MENÚ DESPLEGABLE ---
header_frame = ttk.Frame(ventana, padding="10 10 10 0")
header_frame.pack(fill="x")

tk.Label(header_frame, text="🛡️ Backup MySQL Pro", font=("Arial", 18, "bold"), bg="#f4f4f9", fg="#2c3e50").pack(side=tk.LEFT)

menu_btn = ttk.Menubutton(header_frame, text="⚙️ Gestor de Copias", style="Menu.TButton", direction="below")
menu_btn.pack(side=tk.RIGHT, padx=10)

menu = tk.Menu(menu_btn, tearoff=0, bg="#ecf0f1", fg="#333", font=("Arial", 10))

menu.add_command(label="➕  Crear Backup (Manual)", command=lambda: hacer_backup(is_programmed=False)) # Ajuste para ser explícito

def abrir_menu_editar_callback():
    messagebox.showinfo("Instrucción", "Para EDITAR o ELIMINAR un registro, selecciónalo en la tabla inferior y usa los botones 'Editar' o 'Eliminar' que aparecen en la columna 'Acciones'.")

menu.add_command(label="✍️  Editar Copia (Usar Tabla)", command=abrir_menu_editar_callback)
menu.add_command(label="🗑️  Eliminar Copia (Usar Tabla)", command=abrir_menu_editar_callback)

menu_btn["menu"] = menu


# --- ENTRADAS DE CONFIGURACIÓN ---
frame_config = ttk.Frame(ventana, padding="15 15 15 5")
frame_config.pack(fill="x", padx=10)

labels = ["Usuario MySQL:", "Contraseña:", "Base de Datos:", "Carpeta destino:"]
default_values = {"Usuario MySQL:": "root", "Contraseña:": "", "Base de Datos:": "miguelhogar", "Carpeta destino:": ""}

entry_usuario, entry_contrasena, entry_bd, entry_destino = [None] * 4

for i, label_text in enumerate(labels):
    ttk.Label(frame_config, text=label_text, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", pady=2, padx=5)
    
    entry_frame = ttk.Frame(frame_config)
    entry_frame.grid(row=i, column=1, sticky="ew", pady=2)
    
    entry = ttk.Entry(entry_frame, width=40)
    entry.insert(0, default_values[label_text])
    entry.pack(side=tk.LEFT, fill="x", expand=True)

    if label_text == "Contraseña:":
        entry.config(show="*")
    
    if label_text == "Carpeta destino:":
        ttk.Button(entry_frame, text="Seleccionar", command=seleccionar_destino).pack(side=tk.LEFT, padx=5)
        entry_destino = entry
    elif label_text == "Usuario MySQL:":
        entry_usuario = entry
    elif label_text == "Contraseña:":
        entry_contrasena = entry
    elif label_text == "Base de Datos:":
        entry_bd = entry

frame_config.columnconfigure(1, weight=1)

# --- CAMPOS DE FECHA Y HORA PARA PROGRAMACIÓN ---
frame_programacion = ttk.Frame(ventana, padding="15 0 15 10")
frame_programacion.pack(fill="x", padx=10)

ttk.Label(frame_programacion, text="📅 Programar Fecha (AAAA-MM-DD):", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5)
entry_fecha = ttk.Entry(frame_programacion, width=15)
entry_fecha.insert(0, "YYYY-MM-DD")
entry_fecha.grid(row=0, column=1, sticky="w", padx=5)

ttk.Label(frame_programacion, text="⌚ Programar Hora (HH:MM):", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky="w", padx=(20, 5))
entry_hora = ttk.Entry(frame_programacion, width=10)
entry_hora.insert(0, "HH:MM")
entry_hora.grid(row=0, column=3, sticky="w", padx=5)

ttk.Button(frame_programacion, text="▶️ PROGRAMAR BACKUP AUTOMÁTICO", command=programar_backup,
           style="Orange.TButton").grid(row=0, column=4, sticky="e", padx=(30, 0))

frame_programacion.columnconfigure(4, weight=1)

# --- BOTÓN MANUAL ---
frame_botones = ttk.Frame(ventana, padding="15 0 15 10")
frame_botones.pack(fill="x", padx=10)

# Asegura que la llamada manual siempre usa la hora actual
ttk.Button(frame_botones, text="🚀 HACER BACKUP MANUAL AHORA", command=lambda: hacer_backup(is_programmed=False), 
           style="Green.TButton").pack(fill="x", expand=True)


# --- TABLA DE COPIAS ---
ttk.Label(ventana, text="Historial de Copias", font=("Arial", 12, "bold"), background="#f4f4f9", foreground="#2c3e50").pack(anchor="w", padx=15, pady=(10, 5))

columnas = ("ID", "Usuario", "Base de Datos", "Fecha", "Ruta", "Acciones")
tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=15)
tabla.pack(fill=tk.BOTH, padx=15, pady=(0, 10), expand=True)

tabla.column("ID", width=30, stretch=tk.NO, anchor="center")
tabla.column("Usuario", width=80, anchor="center")
tabla.column("Base de Datos", width=120, anchor="center")
tabla.column("Fecha", width=140, anchor="center")
tabla.column("Ruta", stretch=tk.YES, minwidth=150)
tabla.column("Acciones", width=120, stretch=tk.NO, anchor="center")


for col in columnas:
    tabla.heading(col, text=col)

botones_accion = {}

# CORRECCIÓN 1: Se modificó la lambda para abrir la ventana de edición
def actualizar_tabla():
    for fila in tabla.get_children():
        tabla.delete(fila)
    for btns in botones_accion.values():
        for b in btns:
            if b.winfo_exists():
                b.destroy()
    botones_accion.clear()

    for i, copia in enumerate(copias, 1):
        item = tabla.insert("", "end",
                            values=(i, copia["usuario"], copia["bd"], copia["hora"], copia["ruta"], ""))
        
        tabla.update_idletasks()
        try:
            bbox = tabla.bbox(item, "#6")
        except:
            continue
            
        if not bbox:
            continue
        
        x0, y0, width0, height0 = bbox
        
        # Botón EDITAR (CORREGIDO)
        btn_editar = tk.Label(tabla, text="✍️ Editar", bg="#3498db", fg="white", cursor="hand2", font=("Arial", 9, "bold"))
        btn_editar.place(x=x0 + 2, y=y0 + 2, width=width0//2 - 4, height=height0 - 4)
        # Se pasa la copia y el índice explícitamente a la lambda
        btn_editar.bind("<Button-1>", lambda e, idx=i-1, c=copia: abrir_editar_copia(c, idx)) 
        
        # Botón ELIMINAR
        btn_eliminar = tk.Label(tabla, text="🗑️ Eliminar", bg="#e74c3c", fg="white", cursor="hand2", font=("Arial", 9, "bold"))
        btn_eliminar.place(x=x0 + width0//2 + 2, y=y0 + 2, width=width0//2 - 4, height=height0 - 4)
        btn_eliminar.bind("<Button-1>", lambda e, idx=i-1: eliminar_copia_dialogo(idx))
        
        botones_accion[item] = (btn_editar, btn_eliminar)

tabla.bind("<Configure>", lambda e: actualizar_tabla())

actualizar_tabla()
verificar_programacion()
ventana.mainloop()