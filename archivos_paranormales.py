"""
=================================================================
  PROYECTO: Sistema de Gestión de Archivos Paranormales
  Base de datos: MariaDB - Archivos_Paranormales
  Descripcion: Aplicacion de consola para gestionar casos
  paranormales, investigadores, lugares, evidencias,
  testigos e informes mediante operaciones CRUD.
=================================================================
"""
 
# Libreria de conexion con MariaDB
import mariadb
# Modulo del sistema (usado para salir en caso de error critico)
import sys
 
# ---------------------------------------------------------------
# CONFIGURACION DE LA BASE DE DATOS
# Diccionario con los parametros de conexion a MariaDB
# ---------------------------------------------------------------
CONFIG = {
    "host":     "127.0.0.1",   # Direccion del servidor (localhost)
    "port":     3306,           # Puerto por defecto de MariaDB
    "user":     "root",         # Usuario de la base de datos
    "password": "",             # Contrasena (vacia en entorno local)
    "database": "archivos_paranormales",  # Nombre de la base de datos
}
 
 
def conectar():
    """
    Establece y devuelve una conexion a la base de datos MariaDB.
    Desactiva el autocommit para controlar las transacciones manualmente.
    Devuelve el objeto conexion, o None si falla.
    """
    try:
        # Intenta conectar usando los parametros del diccionario CONFIG
        conn = mariadb.connect(**CONFIG)
        # Desactiva confirmacion automatica: los cambios deben hacerse con commit()
        conn.autocommit = False
        return conn
    except mariadb.Error as e:
        print(f" Error de conexion: {e}")
        return None  # Devuelve None para que las funciones que la llaman puedan comprobarlo
 
 
def pausar():
    """
    Pausa la ejecucion hasta que el usuario pulse ENTER.
    Se usa al final de cada operacion para que el usuario pueda leer el resultado.
    """
    input("\nPulsa ENTER para continuar...")
 
 
def sep():
    """
    Imprime una linea separadora de 55 guiones.
    Se usa para mejorar la legibilidad visual en la consola.
    """
    print("─" * 55)
 
 
# ===============================================================
# CRUD — INVESTIGADORES
# Operaciones: Ver, Anadir, Actualizar, Eliminar
# ===============================================================
 
def ver_investigadores():
    """
    Muestra por consola todos los investigadores registrados en la base de datos.
    Columnas mostradas: id, nombre, especialidad y nivel de acceso.
    """
    print("\n=== INVESTIGADORES ===")
    conn = conectar()
    if not conn:
        return  # Si no hay conexion, se sale de la funcion
    try:
        cur = conn.cursor()
        # Consulta todos los campos relevantes de la tabla INVESTIGADOR
        cur.execute("SELECT id_investigador, nombre, especialidad, nivel_acceso FROM INVESTIGADOR")
        filas = cur.fetchall()  # Obtiene todas las filas del resultado
        sep()
        for f in filas:
            # Imprime cada investigador con formato legible
            print(f"[{f[0]}] {f[1]} - {f[2]} ({f[3]})")
        sep()
    except mariadb.Error as e:
        print(f" Error: {e}")
    finally:
        conn.close()  # Cierra siempre la conexion, haya error o no
 
 
def anadir_investigador():
    """
    Solicita los datos de un nuevo investigador por consola
    y los inserta en la tabla INVESTIGADOR.
    Si hay error, hace rollback para no dejar datos a medias.
    """
    print("\n=== AÑADIR INVESTIGADOR ===")
    # Recoge los datos del nuevo investigador por teclado
    nombre       = input("Nombre       : ").strip()
    especialidad = input("Especialidad : ").strip()
    nivel        = input("Nivel acceso (Alto/Medio/Bajo): ").strip()
    fecha        = input("Fecha ingreso (YYYY-MM-DD): ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Inserta el nuevo registro usando parametros para evitar SQL injection
        cur.execute("""
            INSERT INTO INVESTIGADOR (nombre, especialidad, nivel_acceso, fecha_ingreso)
            VALUES (%s, %s, %s, %s)
        """, (nombre, especialidad, nivel, fecha))
        conn.commit()  # Confirma la transaccion
        print(f" Investigador '{nombre}' añadido.")
    except mariadb.Error as e:
        conn.rollback()  # Deshace los cambios si hay error
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def actualizar_investigador():
    """
    Permite modificar los datos de un investigador existente.
    Muestra los datos actuales y permite dejar campos en blanco
    para mantener el valor original.
    """
    print("\n=== MODIFICAR INVESTIGADOR ===")
    ver_investigadores()  # Muestra la lista para que el usuario elija un ID
    id_inv = input("ID a modificar: ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Obtiene los datos actuales del investigador a modificar
        cur.execute("""
            SELECT nombre, especialidad, nivel_acceso, fecha_ingreso
            FROM INVESTIGADOR WHERE id_investigador = %s
        """, (id_inv,))
        actual = cur.fetchone()  # Devuelve una sola fila o None
        if not actual:
            print(" Investigador no encontrado.")
            return
 
        # Muestra los valores actuales antes de editar
        print(f"\n  Datos actuales:")
        print(f"  Nombre       : {actual[0]}")
        print(f"  Especialidad : {actual[1]}")
        print(f"  Nivel acceso : {actual[2]}")
        print(f"  Fecha ingreso: {actual[3]}")
        print("  (Deja en blanco para mantener el valor actual)")
 
        # Si el usuario no escribe nada, se conserva el valor original usando "or"
        nombre       = input("\nNombre       : ").strip() or actual[0]
        especialidad = input("Especialidad : ").strip() or actual[1]
        nivel        = input("Nivel acceso (Alto/Medio/Bajo): ").strip() or actual[2]
        fecha        = input("Fecha ingreso (YYYY-MM-DD): ").strip() or str(actual[3])
 
        # Actualiza el registro con los nuevos valores
        cur.execute("""
            UPDATE INVESTIGADOR
            SET nombre=%s, especialidad=%s, nivel_acceso=%s, fecha_ingreso=%s
            WHERE id_investigador=%s
        """, (nombre, especialidad, nivel, fecha, id_inv))
        conn.commit()
        print(" Investigador actualizado.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def eliminar_investigador():
    """
    Elimina un investigador de la base de datos por su ID.
    Si tiene registros asociados (casos, informes...) la BD lo impedira
    y se mostrara un mensaje de error.
    """
    print("\n=== ELIMINAR INVESTIGADOR ===")
    ver_investigadores()  # Muestra la lista para elegir ID
    id_inv = input("ID a eliminar: ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM INVESTIGADOR WHERE id_investigador=%s", (id_inv,))
        conn.commit()
        print(" Investigador eliminado.")
    except mariadb.Error as e:
        conn.rollback()
        # La BD lanzara error si hay restricciones de clave foranea
        print(f" No se puede eliminar (tiene registros asociados): {e}")
    finally:
        conn.close()
 
 
# ===============================================================
# CRUD — LUGARES
# Operaciones: Ver, Anadir, Actualizar, Eliminar
# ===============================================================
 
def ver_lugares():
    """
    Muestra todos los lugares registrados en la base de datos.
    Columnas mostradas: id, nombre, pais, region y tipo de zona.
    """
    print("\n=== LUGARES ===")
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_lugar, nombre, pais, region, tipo_zona FROM LUGAR")
        filas = cur.fetchall()
        sep()
        for f in filas:
            print(f"[{f[0]}] {f[1]} - {f[2]} / {f[3]} ({f[4]})")
        sep()
    except mariadb.Error as e:
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def anadir_lugar():
    """
    Solicita los datos de un nuevo lugar y lo inserta en la tabla LUGAR.
    Incluye coordenadas geograficas (latitud y longitud) y tipo de zona.
    """
    print("\n=== AÑADIR LUGAR ===")
    nombre = input("Nombre      : ").strip()
    pais   = input("Pais        : ").strip()
    region = input("Region      : ").strip()
    lat    = input("Latitud     : ").strip()
    lon    = input("Longitud    : ").strip()
    zona   = input("Tipo zona   : ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO LUGAR (nombre, pais, region, latitud, longitud, tipo_zona)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, pais, region, lat, lon, zona))
        conn.commit()
        print(" Lugar añadido.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def actualizar_lugar():
    """
    Permite modificar los datos de un lugar existente.
    Muestra valores actuales; campos vacios conservan el valor original.
    """
    print("\n=== MODIFICAR LUGAR ===")
    ver_lugares()
    id_lugar = input("ID a modificar: ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Obtiene todos los campos del lugar a modificar
        cur.execute("""
            SELECT nombre, pais, region, latitud, longitud, tipo_zona
            FROM LUGAR WHERE id_lugar = %s
        """, (id_lugar,))
        actual = cur.fetchone()
        if not actual:
            print(" Lugar no encontrado.")
            return
 
        print(f"\n  Datos actuales:")
        print(f"  Nombre    : {actual[0]}")
        print(f"  Pais      : {actual[1]}")
        print(f"  Region    : {actual[2]}")
        print(f"  Latitud   : {actual[3]}")
        print(f"  Longitud  : {actual[4]}")
        print(f"  Tipo zona : {actual[5]}")
        print("  (Deja en blanco para mantener el valor actual)")
 
        # El operador "or" conserva el valor actual si el campo queda vacio
        nombre = input("\nNombre      : ").strip() or actual[0]
        pais   = input("Pais        : ").strip() or actual[1]
        region = input("Region      : ").strip() or actual[2]
        lat    = input("Latitud     : ").strip() or str(actual[3])
        lon    = input("Longitud    : ").strip() or str(actual[4])
        zona   = input("Tipo zona   : ").strip() or actual[5]
 
        cur.execute("""
            UPDATE LUGAR
            SET nombre=%s, pais=%s, region=%s, latitud=%s, longitud=%s, tipo_zona=%s
            WHERE id_lugar=%s
        """, (nombre, pais, region, lat, lon, zona, id_lugar))
        conn.commit()
        print(" Lugar actualizado.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def eliminar_lugar():
    """
    Elimina un lugar de la base de datos por su ID.
    Si tiene casos asociados, la clave foranea de la BD impedira la eliminacion.
    """
    print("\n=== ELIMINAR LUGAR ===")
    ver_lugares()
    id_lugar = input("ID a eliminar: ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM LUGAR WHERE id_lugar=%s", (id_lugar,))
        conn.commit()
        print(" Lugar eliminado.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" No se puede eliminar (tiene casos asociados): {e}")
    finally:
        conn.close()
 
 
# ===============================================================
# CRUD — CASOS
# Operaciones: Ver, Anadir, Actualizar, Eliminar
# Incluye gestion de investigadores asignados al caso
# ===============================================================
 
def ver_casos():
    """
    Muestra todos los casos con su titulo, estado, investigador lider y lugar.
    Usa JOINs para obtener los nombres en lugar de los IDs numericos.
    """
    print("\n=== CASOS ===")
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # JOIN con INVESTIGADOR y LUGAR para mostrar nombres en vez de IDs
        cur.execute("""
            SELECT c.id_caso, c.titulo, c.estado, i.nombre, l.nombre
            FROM CASO c
            LEFT JOIN INVESTIGADOR i ON c.id_investigador_lead = i.id_investigador
            LEFT JOIN LUGAR l ON c.id_lugar = l.id_lugar
            ORDER BY c.id_caso
        """)
        filas = cur.fetchall()
        sep()
        for f in filas:
            print(f"[{f[0]}] {f[1]} | {f[2]} | Lider: {f[3]} | Lugar: {f[4]}")
        sep()
    except mariadb.Error as e:
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def ver_investigadores_de_caso(id_caso, conn):
    """
    Muestra los investigadores asignados a un caso concreto.
    Recibe la conexion como parametro para poder reutilizarla
    dentro de una transaccion ya abierta sin abrir una nueva.
    Devuelve la lista de filas para que la funcion llamante pueda usarla.
    """
    cur = conn.cursor()
    # Consulta la tabla intermedia CASO_INVESTIGADOR con JOIN a INVESTIGADOR
    cur.execute("""
        SELECT ci.id_investigador, i.nombre, ci.rol
        FROM CASO_INVESTIGADOR ci
        JOIN INVESTIGADOR i ON ci.id_investigador = i.id_investigador
        WHERE ci.id_caso = %s
        ORDER BY ci.rol
    """, (id_caso,))
    filas = cur.fetchall()
    sep()
    print(f"  Investigadores asignados al caso {id_caso}:")
    if filas:
        for f in filas:
            print(f"  [{f[0]}] {f[1]} — Rol: {f[2]}")
    else:
        print("  (Ninguno)")
    sep()
    return filas  # Se devuelve para que el llamante pueda comprobar si hay investigadores
 
 
def anadir_caso():
    """
    Crea un nuevo caso paranormal en la base de datos.
    Solo permite asignar como lider a investigadores con nivel de acceso 'Alto'.
    Tras crear el caso, lo registra automaticamente en CASO_INVESTIGADOR como Lider
    y ofrece anadir investigadores adicionales en bucle.
    """
    print("\n=== AÑADIR CASO ===")
    print("\nSolo investigadores con nivel de acceso ALTO pueden ser Lider:")
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Filtra solo investigadores con nivel Alto para elegir lider
        cur.execute("""
            SELECT id_investigador, nombre, especialidad
            FROM INVESTIGADOR
            WHERE LOWER(nivel_acceso) = 'alto'
        """)
        lideres = cur.fetchall()
        sep()
        if not lideres:
            print(" No hay investigadores con nivel de acceso Alto disponibles.")
            conn.close()
            return
        for f in lideres:
            print(f"[{f[0]}] {f[1]} - {f[2]}")
        sep()
    except mariadb.Error as e:
        print(f" Error: {e}")
        conn.close()
        return
 
    ver_lugares()  # Muestra los lugares disponibles para elegir ID
 
    # Recoge los datos del nuevo caso
    titulo    = input("Titulo       : ").strip()
    categoria = input("Categoria    : ").strip()
    estado    = input("Estado       : ").strip()
    fecha     = input("Fecha incidente (YYYY-MM-DD): ").strip()
    id_inv    = input("ID del investigador Lider (nivel Alto): ").strip()
 
    try:
        cur = conn.cursor()
        # Valida que el investigador elegido realmente tenga nivel Alto
        cur.execute("""
            SELECT nivel_acceso FROM INVESTIGADOR
            WHERE id_investigador = %s AND LOWER(nivel_acceso) = 'alto'
        """, (id_inv,))
        fila = cur.fetchone()
        if not fila:
            print(" El investigador seleccionado no existe o no tiene nivel de acceso Alto.")
            conn.close()
            return
    except mariadb.Error as e:
        print(f" Error al validar investigador: {e}")
        conn.close()
        return
 
    id_lugar = input("ID del lugar: ").strip()
 
    try:
        # Inserta el nuevo caso en la tabla CASO
        cur.execute("""
            INSERT INTO CASO (titulo, categoria, estado, fecha_incidente, id_investigador_lead, id_lugar)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (titulo, categoria, estado, fecha, id_inv, id_lugar))
 
        # Obtiene el ID del caso recien insertado
        id_caso = cur.lastrowid
 
        # Registra automaticamente al lider en la tabla intermedia CASO_INVESTIGADOR
        cur.execute("""
            INSERT INTO CASO_INVESTIGADOR (id_caso, id_investigador, rol, fecha_asignacion)
            VALUES (%s, %s, 'Lider', CURDATE())
        """, (id_caso, id_inv))
 
        conn.commit()
        print(f" Caso '{titulo}' creado.")
        print(f" Investigador asignado automaticamente como: Lider")
 
        # Bucle para anadir investigadores adicionales al caso
        while True:
            extra = input("\n¿Quieres anadir un investigador adicional al caso? (s/n): ").strip().lower()
            if extra == "s":
                # Llama a la funcion auxiliar pasando la conexion existente
                _anadir_investigador_a_caso(id_caso, conn)
            elif extra == "n":
                print(" No se anadiran mas investigadores.")
                break
            else:
                print("Opcion no valida.")
 
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
