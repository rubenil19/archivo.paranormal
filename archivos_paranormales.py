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
 
 
def _anadir_investigador_a_caso(id_caso, conn_externa=None):
    """
    Anade un investigador existente a un caso como miembro del equipo.
    Puede recibir una conexion externa (si se llama desde anadir_caso)
    o crear su propia conexion si se llama de forma independiente.
    Valida que:
      - Si el rol es Lider, el investigador tenga nivel Alto
      - No haya ya un Lider asignado al caso
      - El investigador no este ya asignado al mismo caso
    """
    # Determina si se usa una conexion ya abierta o se crea una nueva
    usar_conn_externa = conn_externa is not None
    conn = conn_externa if usar_conn_externa else conectar()
    if not conn:
        return
 
    try:
        cur = conn.cursor()
        # Muestra los investigadores ya asignados al caso
        ver_investigadores_de_caso(id_caso, conn)
 
        # Muestra todos los investigadores disponibles para anadir
        cur.execute("SELECT id_investigador, nombre, nivel_acceso FROM INVESTIGADOR")
        todos = cur.fetchall()
        print("\n  Todos los investigadores disponibles:")
        sep()
        for f in todos:
            print(f"  [{f[0]}] {f[1]} — Nivel: {f[2]}")
        sep()
 
        id_inv = input("ID del investigador a anadir: ").strip()
        rol    = input("Rol (Lider / Forense / Apoyo): ").strip()
 
        # Bloque de validacion especifica para el rol Lider
        if rol.strip().lower() in ("lider", "lider"):
            rol = "Lider"
            # Comprueba que el investigador tenga nivel Alto
            cur.execute("""
                SELECT nivel_acceso FROM INVESTIGADOR
                WHERE id_investigador = %s AND LOWER(nivel_acceso) = 'alto'
            """, (id_inv,))
            if not cur.fetchone():
                print(" Solo investigadores con nivel de acceso Alto pueden ser Lider.")
                return
 
            # Comprueba que no haya ya un Lider en el caso
            cur.execute("""
                SELECT COUNT(*) FROM CASO_INVESTIGADOR
                WHERE id_caso = %s AND rol = 'Lider'
            """, (id_caso,))
            if cur.fetchone()[0] > 0:
                print(" Ya existe un Lider asignado a este caso. Solo puede haber uno.")
                return
 
        # Comprueba que el investigador no este ya asignado a este caso
        cur.execute("""
            SELECT COUNT(*) FROM CASO_INVESTIGADOR
            WHERE id_caso = %s AND id_investigador = %s
        """, (id_caso, id_inv))
        if cur.fetchone()[0] > 0:
            print(" Este investigador ya esta asignado a este caso.")
            return
 
        # Inserta la relacion caso-investigador con el rol elegido
        cur.execute("""
            INSERT INTO CASO_INVESTIGADOR (id_caso, id_investigador, rol, fecha_asignacion)
            VALUES (%s, %s, %s, CURDATE())
        """, (id_caso, id_inv, rol))
 
        conn.commit()
        print(f" Investigador anadido al caso con rol: {rol}")
 
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        # Solo cierra la conexion si fue creada por esta funcion (no si es externa)
        if not usar_conn_externa:
            conn.close()
 
 
def _quitar_investigador_de_caso(id_caso):
    """
    Retira un investigador de un caso eliminando su fila en CASO_INVESTIGADOR.
    Si el investigador a quitar es el Lider:
      - Solo se permite si hay mas de un investigador en el caso
      - Se pide confirmacion explicicta
      - Se pone a NULL el campo id_investigador_lead en la tabla CASO
    """
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Muestra los investigadores actuales del caso para elegir cual quitar
        filas = ver_investigadores_de_caso(id_caso, conn)
        if not filas:
            print(" No hay investigadores asignados a este caso.")
            return
 
        id_inv = input("ID del investigador a quitar: ").strip()
 
        # Verifica que el investigador elegido esta realmente asignado al caso
        cur.execute("""
            SELECT rol FROM CASO_INVESTIGADOR
            WHERE id_caso = %s AND id_investigador = %s
        """, (id_caso, id_inv))
        fila_rol = cur.fetchone()
        if not fila_rol:
            print(" Ese investigador no esta asignado a este caso.")
            return
 
        rol_actual = fila_rol[0]
 
        # Logica especial si el investigador a quitar es el Lider
        if rol_actual == "Lider":
            # Cuenta cuantos investigadores hay en total en el caso
            cur.execute("SELECT COUNT(*) FROM CASO_INVESTIGADOR WHERE id_caso = %s", (id_caso,))
            total = cur.fetchone()[0]
            if total <= 1:
                # No se puede dejar un caso sin ningun investigador
                print(" No puedes quitar al Lider si es el unico investigador del caso.")
                return
            print("  Atencion: vas a quitar al Lider del caso.")
            print("   El campo id_investigador_lead quedara vacio. Deberas asignar un nuevo Lider.")
            conf = input("¿Confirmar? (s/n): ").strip().lower()
            if conf != "s":
                print("Cancelado.")
                return
            # Pone a NULL el lider en la tabla CASO
            cur.execute("UPDATE CASO SET id_investigador_lead = NULL WHERE id_caso = %s", (id_caso,))
 
        # Elimina la fila de la tabla intermedia CASO_INVESTIGADOR
        cur.execute("""
            DELETE FROM CASO_INVESTIGADOR
            WHERE id_caso = %s AND id_investigador = %s
        """, (id_caso, id_inv))
 
        conn.commit()
        print(" Investigador retirado del caso.")
 
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def actualizar_caso():
    """
    Modifica los datos generales de un caso (titulo, categoria, estado, lugar).
    Tras actualizar los datos, abre un submenu para gestionar los
    investigadores asignados (ver, anadir o quitar).
    """
    print("\n=== MODIFICAR CASO ===")
    ver_casos()
    id_caso = input("ID del caso a modificar: ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Obtiene los datos actuales del caso
        cur.execute("""
            SELECT titulo, categoria, estado, id_lugar FROM CASO WHERE id_caso = %s
        """, (id_caso,))
        actual = cur.fetchone()
        if not actual:
            print(" Caso no encontrado.")
            return
 
        print(f"\n  Datos actuales:")
        print(f"  Titulo    : {actual[0]}")
        print(f"  Categoria : {actual[1]}")
        print(f"  Estado    : {actual[2]}")
        print(f"  ID Lugar  : {actual[3]}")
        print("  (Deja en blanco para mantener el valor actual)")
    except mariadb.Error as e:
        print(f" Error: {e}")
        conn.close()
        return
 
    ver_lugares()  # Muestra lugares disponibles para elegir nuevo ID si se desea
    titulo    = input("\nNuevo titulo       : ").strip() or actual[0]
    categoria = input("Nueva categoria    : ").strip() or actual[1]
    estado    = input("Nuevo estado       : ").strip() or actual[2]
    id_lugar  = input("Nuevo ID de lugar  : ").strip() or str(actual[3])
 
    try:
        cur.execute("""
            UPDATE CASO SET titulo=%s, categoria=%s, estado=%s, id_lugar=%s
            WHERE id_caso=%s
        """, (titulo, categoria, estado, id_lugar, id_caso))
        conn.commit()
        print(" Datos del caso actualizados.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
    # Submenu para gestionar el equipo de investigadores del caso
    while True:
        print(f"\n-- Gestion de investigadores del caso {id_caso} --")
        print("1. Ver investigadores asignados")
        print("2. Anadir investigador")
        print("3. Quitar investigador")
        print("0. Volver")
        sub = input("Elige: ").strip()
        if sub == "1":
            # Abre una conexion nueva solo para ver (la anterior ya fue cerrada)
            conn2 = conectar()
            if conn2:
                ver_investigadores_de_caso(id_caso, conn2)
                conn2.close()
        elif sub == "2":
            _anadir_investigador_a_caso(id_caso)   # Crea su propia conexion
        elif sub == "3":
            _quitar_investigador_de_caso(id_caso)  # Crea su propia conexion
        elif sub == "0":
            break
        else:
            print("Opcion no valida.")
 
 
def eliminar_caso():
    """
    Elimina un caso y todos sus registros dependientes en cascada manual:
    testigos, evidencias, informes, relaciones con investigadores y el propio caso.
    Pide confirmacion antes de proceder.
    Usa una transaccion explicita para que todo sea atomico.
    """
    print("\n=== ELIMINAR CASO ===")
    ver_casos()
    id_caso = input("ID a eliminar: ").strip()
    conf = input("¿Seguro? (s/n): ").strip().lower()
 
    if conf != "s":
        print("Cancelado.")
        return
 
    conn = conectar()
    if not conn:
        return
    try:
        conn.begin()  # Inicia la transaccion explicitamente
        cur = conn.cursor()
        # Elimina en orden para respetar las claves foraneas
        cur.execute("DELETE FROM TESTIGO WHERE id_caso=%s", (id_caso,))
        cur.execute("DELETE FROM EVIDENCIA WHERE id_caso=%s", (id_caso,))
        cur.execute("DELETE FROM INFORME WHERE id_caso=%s", (id_caso,))
        cur.execute("DELETE FROM CASO_INVESTIGADOR WHERE id_caso=%s", (id_caso,))
        cur.execute("DELETE FROM CASO WHERE id_caso=%s", (id_caso,))
        conn.commit()  # Confirma todos los DELETE a la vez
        print(" Caso eliminado.")
    except mariadb.Error as e:
        conn.rollback()  # Si algo falla, deshace todos los DELETE
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
# ===============================================================
# CRUD — TESTIGOS
# Operaciones: Ver, Anadir, Actualizar, Eliminar
# ===============================================================
 
def ver_testigos():
    """
    Muestra todos los testigos registrados con el titulo del caso al que pertenecen,
    su nombre y su nivel de fiabilidad.
    """
    print("\n=== TESTIGOS ===")
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # JOIN con CASO para mostrar el titulo en vez del id_caso
        cur.execute("""
            SELECT t.id_testigo, c.titulo, t.nombre, t.fiabilidad
            FROM TESTIGO t
            JOIN CASO c ON t.id_caso = c.id_caso
            ORDER BY t.id_testigo
        """)
        filas = cur.fetchall()
        sep()
        for f in filas:
            print(f"[{f[0]}] Caso: {f[1]} | Testigo: {f[2]} | Fiabilidad: {f[3]}")
        sep()
    except mariadb.Error as e:
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def anadir_testigo():
    """
    Registra un nuevo testigo vinculado a un caso existente.
    Recoge nombre, contacto, declaracion y nivel de fiabilidad (1-10).
    """
    print("\n=== AÑADIR TESTIGO ===")
    ver_casos()  # Muestra los casos para elegir a cual vincular el testigo
    id_caso     = input("ID del caso: ").strip()
    nombre      = input("Nombre del testigo: ").strip()
    contacto    = input("Contacto: ").strip()
    declaracion = input("Declaracion: ").strip()
    fiabilidad  = input("Fiabilidad (1-10): ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO TESTIGO (id_caso, nombre, contacto, declaracion, fiabilidad)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_caso, nombre, contacto, declaracion, fiabilidad))
        conn.commit()
        print(" Testigo anadido.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def actualizar_testigo():
    """
    Modifica los datos de un testigo existente.
    Los campos vacios conservan el valor actual.
    """
    print("\n=== MODIFICAR TESTIGO ===")
    ver_testigos()
    id_t = input("ID del testigo a modificar: ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT nombre, contacto, declaracion, fiabilidad
            FROM TESTIGO WHERE id_testigo = %s
        """, (id_t,))
        actual = cur.fetchone()
        if not actual:
            print(" Testigo no encontrado.")
            return
 
        print(f"\n  Datos actuales:")
        print(f"  Nombre      : {actual[0]}")
        print(f"  Contacto    : {actual[1]}")
        print(f"  Declaracion : {actual[2]}")
        print(f"  Fiabilidad  : {actual[3]}")
        print("  (Deja en blanco para mantener el valor actual)")
 
        nombre      = input("\nNombre      : ").strip() or actual[0]
        contacto    = input("Contacto    : ").strip() or actual[1]
        declaracion = input("Declaracion : ").strip() or actual[2]
        fiabilidad  = input("Fiabilidad (1-10): ").strip() or str(actual[3])
 
        cur.execute("""
            UPDATE TESTIGO
            SET nombre=%s, contacto=%s, declaracion=%s, fiabilidad=%s
            WHERE id_testigo=%s
        """, (nombre, contacto, declaracion, fiabilidad, id_t))
        conn.commit()
        print(" Testigo actualizado.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def eliminar_testigo():
    """
    Elimina un testigo de la base de datos por su ID.
    """
    print("\n=== ELIMINAR TESTIGO ===")
    ver_testigos()
    id_t = input("ID del testigo a eliminar: ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM TESTIGO WHERE id_testigo=%s", (id_t,))
        conn.commit()
        print(" Testigo eliminado.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
# ===============================================================
# CRUD — EVIDENCIAS
# Operaciones: Ver, Anadir, Actualizar, Eliminar
# ===============================================================
 
def ver_evidencias():
    """
    Muestra todas las evidencias con el titulo del caso al que pertenecen,
    su tipo y nivel de credibilidad.
    """
    print("\n=== EVIDENCIAS ===")
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # JOIN con CASO para mostrar titulo del caso en vez del ID
        cur.execute("""
            SELECT e.id_evidencia, c.titulo, e.tipo, e.nivel_credibilidad
            FROM EVIDENCIA e
            JOIN CASO c ON e.id_caso = c.id_caso
            ORDER BY e.id_evidencia
        """)
        filas = cur.fetchall()
        sep()
        for f in filas:
            print(f"[{f[0]}] Caso: {f[1]} | {f[2]} | Credibilidad: {f[3]}")
        sep()
    except mariadb.Error as e:
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def anadir_evidencia():
    """
    Registra una nueva evidencia vinculada a un caso existente.
    Recoge tipo, descripcion, nivel de credibilidad y fecha de recoleccion.
    """
    print("\n=== AÑADIR EVIDENCIA ===")
    ver_casos()  # Muestra los casos para elegir a cual vincular la evidencia
    id_caso = input("ID del caso   : ").strip()
    tipo    = input("Tipo          : ").strip()
    desc    = input("Descripcion   : ").strip()
    credib  = input("Credibilidad  : ").strip()
    fecha   = input("Fecha (YYYY-MM-DD): ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO EVIDENCIA (id_caso, tipo, descripcion, nivel_credibilidad, fecha_recoleccion)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_caso, tipo, desc, credib, fecha))
        conn.commit()
        print(" Evidencia registrada.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def actualizar_evidencia():
    """
    Modifica los datos de una evidencia existente.
    Los campos vacios conservan el valor actual.
    """
    print("\n=== MODIFICAR EVIDENCIA ===")
    ver_evidencias()
    id_ev = input("ID de la evidencia a modificar: ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT tipo, descripcion, nivel_credibilidad, fecha_recoleccion
            FROM EVIDENCIA WHERE id_evidencia = %s
        """, (id_ev,))
        actual = cur.fetchone()
        if not actual:
            print(" Evidencia no encontrada.")
            return
 
        print(f"\n  Datos actuales:")
        print(f"  Tipo          : {actual[0]}")
        print(f"  Descripcion   : {actual[1]}")
        print(f"  Credibilidad  : {actual[2]}")
        print(f"  Fecha         : {actual[3]}")
        print("  (Deja en blanco para mantener el valor actual)")
 
        tipo   = input("\nTipo          : ").strip() or actual[0]
        desc   = input("Descripcion   : ").strip() or actual[1]
        credib = input("Credibilidad  : ").strip() or str(actual[2])
        fecha  = input("Fecha (YYYY-MM-DD): ").strip() or str(actual[3])
 
        cur.execute("""
            UPDATE EVIDENCIA
            SET tipo=%s, descripcion=%s, nivel_credibilidad=%s, fecha_recoleccion=%s
            WHERE id_evidencia=%s
        """, (tipo, desc, credib, fecha, id_ev))
        conn.commit()
        print(" Evidencia actualizada.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def eliminar_evidencia():
    """
    Elimina una evidencia de la base de datos por su ID.
    """
    print("\n=== ELIMINAR EVIDENCIA ===")
    ver_evidencias()
    id_ev = input("ID a eliminar: ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM EVIDENCIA WHERE id_evidencia=%s", (id_ev,))
        conn.commit()
        print(" Evidencia eliminada.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
# ===============================================================
# CRUD — INFORMES
# Operaciones: Ver, Anadir, Actualizar, Eliminar
# Solo los investigadores asignados al caso pueden redactar informes
# ===============================================================
 
def ver_informes():
    """
    Muestra todos los informes con el titulo del caso, el nombre del investigador
    redactor, la conclusion y la fecha de emision.
    """
    print("\n=== INFORMES ===")
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # JOIN con CASO e INVESTIGADOR para mostrar nombres en vez de IDs
        cur.execute("""
            SELECT inf.id_informe, c.titulo, i.nombre, inf.conclusion, inf.fecha_emision
            FROM INFORME inf
            JOIN CASO c ON inf.id_caso = c.id_caso
            JOIN INVESTIGADOR i ON inf.id_investigador = i.id_investigador
            ORDER BY inf.id_informe
        """)
        filas = cur.fetchall()
        sep()
        for f in filas:
            print(f"[{f[0]}] Caso: {f[1]} | Redactor: {f[2]} | Conclusion: {f[3]} | Fecha: {f[4]}")
        sep()
    except mariadb.Error as e:
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def anadir_informe():
    """
    Registra un nuevo informe para un caso existente.
    Solo pueden redactar informes los investigadores asignados a ese caso.
    Valida que el investigador elegido este en CASO_INVESTIGADOR para ese caso.
    """
    print("\n=== AÑADIR INFORME ===")
    ver_casos()
    id_caso = input("ID del caso: ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Obtiene solo los investigadores asignados al caso elegido
        cur.execute("""
            SELECT ci.id_investigador, i.nombre, ci.rol
            FROM CASO_INVESTIGADOR ci
            JOIN INVESTIGADOR i ON ci.id_investigador = i.id_investigador
            WHERE ci.id_caso = %s
        """, (id_caso,))
        asignados = cur.fetchall()
        if not asignados:
            print(" No hay investigadores asignados a este caso.")
            return
        print("\n  Investigadores asignados a este caso:")
        sep()
        for f in asignados:
            print(f"  [{f[0]}] {f[1]} — Rol: {f[2]}")
        sep()
 
        id_inv = input("ID del investigador redactor: ").strip()
 
        # Verifica que el investigador elegido este realmente en el caso
        cur.execute("""
            SELECT COUNT(*) FROM CASO_INVESTIGADOR
            WHERE id_caso = %s AND id_investigador = %s
        """, (id_caso, id_inv))
        if cur.fetchone()[0] == 0:
            print(" Ese investigador no esta asignado a este caso.")
            return
 
        contenido  = input("Contenido      : ").strip()
        conclusion = input("Conclusion     : ").strip()
        fecha      = input("Fecha emision (YYYY-MM-DD): ").strip()
 
        cur.execute("""
            INSERT INTO INFORME (id_caso, id_investigador, contenido, conclusion, fecha_emision)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_caso, id_inv, contenido, conclusion, fecha))
        conn.commit()
        print(" Informe registrado.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def actualizar_informe():
    """
    Modifica el contenido, conclusion y fecha de emision de un informe existente.
    Los campos vacios conservan el valor actual.
    """
    print("\n=== MODIFICAR INFORME ===")
    ver_informes()
    id_inf = input("ID del informe a modificar: ").strip()
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT contenido, conclusion, fecha_emision FROM INFORME WHERE id_informe = %s
        """, (id_inf,))
        actual = cur.fetchone()
        if not actual:
            print(" Informe no encontrado.")
            return
 
        print(f"\n  Datos actuales:")
        print(f"  Contenido  : {actual[0]}")
        print(f"  Conclusion : {actual[1]}")
        print(f"  Fecha      : {actual[2]}")
        print("  (Deja en blanco para mantener el valor actual)")
 
        contenido  = input("\nNuevo contenido    : ").strip() or actual[0]
        conclusion = input("Nueva conclusion   : ").strip() or actual[1]
        fecha      = input("Nueva fecha emision (YYYY-MM-DD): ").strip() or str(actual[2])
 
        cur.execute("""
            UPDATE INFORME
            SET contenido=%s, conclusion=%s, fecha_emision=%s
            WHERE id_informe=%s
        """, (contenido, conclusion, fecha, id_inf))
        conn.commit()
        print(" Informe actualizado.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
def eliminar_informe():
    """
    Elimina un informe de la base de datos por su ID.
    Pide confirmacion antes de proceder.
    """
    print("\n=== ELIMINAR INFORME ===")
    ver_informes()
    id_inf = input("ID del informe a eliminar: ").strip()
    conf   = input("¿Seguro? (s/n): ").strip().lower()
    if conf != "s":
        print("Cancelado.")
        return
 
    conn = conectar()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM INFORME WHERE id_informe = %s", (id_inf,))
        conn.commit()
        print(" Informe eliminado.")
    except mariadb.Error as e:
        conn.rollback()
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
# ===============================================================
# ESTADISTICAS COMPLETAS
# Muestra resumenes agrupados por varias dimensiones
# ===============================================================
 
def ver_estadisticas():
    """
    Muestra un panel de estadisticas generales del sistema con 5 consultas:
      1. Casos por estado
      2. Casos asignados por investigador
      3. Evidencias por caso
      4. Testigos por caso
      5. Informes por caso
      6. Informes por investigador
    Todas usan GROUP BY y COUNT con LEFT JOIN para incluir registros sin datos asociados.
    """
    print("\n" + "═" * 60)
    print("  ESTADISTICAS GENERALES DEL SISTEMA")
    print("═" * 60)
 
    conn = conectar()
    if not conn:
        return
 
    try:
        cur = conn.cursor()
 
        # 1. Cuantos casos hay en cada estado
        print("\n  CASOS POR ESTADO")
        print("─" * 60)
        cur.execute("SELECT estado, COUNT(*) FROM CASO GROUP BY estado")
        for estado, total in cur.fetchall():
            print(f"• {estado:<20} → {total} caso(s)")
 
        # 2. Cuantos casos tiene asignados cada investigador
        print("\n  CASOS POR INVESTIGADOR")
        print("─" * 60)
        cur.execute("""
            SELECT i.nombre, COUNT(ci.id_caso)
            FROM INVESTIGADOR i
            LEFT JOIN CASO_INVESTIGADOR ci ON i.id_investigador = ci.id_investigador
            GROUP BY i.id_investigador
            ORDER BY COUNT(ci.id_caso) DESC
        """)
        for nombre, total in cur.fetchall():
            print(f"• {nombre:<20} → {total} caso(s)")
 
        # 3. Cuantas evidencias tiene registradas cada caso
        print("\n  EVIDENCIAS POR CASO")
        print("─" * 60)
        cur.execute("""
            SELECT c.titulo, COUNT(e.id_evidencia)
            FROM CASO c
            LEFT JOIN EVIDENCIA e ON c.id_caso = e.id_caso
            GROUP BY c.id_caso
            ORDER BY COUNT(e.id_evidencia) DESC
        """)
        for titulo, total in cur.fetchall():
            print(f"• {titulo:<30} → {total} evidencia(s)")
 
        # 4. Cuantos testigos tiene registrados cada caso
        print("\n  TESTIGOS POR CASO")
        print("─" * 60)
        cur.execute("""
            SELECT c.titulo, COUNT(t.id_testigo)
            FROM CASO c
            LEFT JOIN TESTIGO t ON c.id_caso = t.id_caso
            GROUP BY c.id_caso
            ORDER BY COUNT(t.id_testigo) DESC
        """)
        for titulo, total in cur.fetchall():
            print(f"• {titulo:<30} → {total} testigo(s)")
 
        # 5. Cuantos informes tiene cada caso
        print("\n  INFORMES POR CASO")
        print("─" * 60)
        cur.execute("""
            SELECT c.titulo, COUNT(inf.id_informe)
            FROM CASO c
            LEFT JOIN INFORME inf ON c.id_caso = inf.id_caso
            GROUP BY c.id_caso
            ORDER BY COUNT(inf.id_informe) DESC
        """)
        for titulo, total in cur.fetchall():
            print(f"• {titulo:<30} → {total} informe(s)")
 
        # 6. Cuantos informes ha redactado cada investigador
        print("\n  INFORMES POR INVESTIGADOR")
        print("─" * 60)
        cur.execute("""
            SELECT i.nombre, COUNT(inf.id_informe)
            FROM INVESTIGADOR i
            LEFT JOIN INFORME inf ON i.id_investigador = inf.id_investigador
            GROUP BY i.id_investigador
            ORDER BY COUNT(inf.id_informe) DESC
        """)
        for nombre, total in cur.fetchall():
            print(f"• {nombre:<20} → {total} informe(s)")
 
        print("\n" + "═" * 60)
 
    except mariadb.Error as e:
        print(f" Error: {e}")
    finally:
        conn.close()
 
 
# ===============================================================
# MENU PRINCIPAL
# Punto de entrada a todas las secciones del sistema
# ===============================================================
 
def menu_principal():
    """
    Bucle principal de la aplicacion. Muestra el menu de primer nivel
    y redirige a los submenus de cada entidad (Investigadores, Lugares,
    Casos, Evidencias, Testigos, Informes) o a las Estadisticas.
    El programa termina cuando el usuario elige la opcion 0.
    """
    while True:
        print("\n" + "═" * 55)
        print("   ARCHIVOS PARANORMALES")
        print("═" * 55)
        print("1. Investigadores")
        print("2. Lugares")
        print("3. Casos")
        print("4. Evidencias")
        print("5. Estadisticas")
        print("6. Testigos")
        print("7. Informes")
        print("0. Salir")
        print("─" * 55)
        op = input("Elige: ").strip()
 
        if op == "1":
            # Submenu de Investigadores
            while True:
                print("\n-- INVESTIGADORES --")
                print("1. Ver  2. Anadir  3. Modificar  4. Eliminar  0. Volver")
                sub = input("Elige: ").strip()
                if   sub == "1": ver_investigadores(); pausar()
                elif sub == "2": anadir_investigador(); pausar()
                elif sub == "3": actualizar_investigador(); pausar()
                elif sub == "4": eliminar_investigador(); pausar()
                elif sub == "0": break
 
        elif op == "2":
            # Submenu de Lugares
            while True:
                print("\n-- LUGARES --")
                print("1. Ver  2. Anadir  3. Modificar  4. Eliminar  0. Volver")
                sub = input("Elige: ").strip()
                if   sub == "1": ver_lugares(); pausar()
                elif sub == "2": anadir_lugar(); pausar()
                elif sub == "3": actualizar_lugar(); pausar()
                elif sub == "4": eliminar_lugar(); pausar()
                elif sub == "0": break
 
        elif op == "3":
            # Submenu de Casos
            while True:
                print("\n-- CASOS --")
                print("1. Ver  2. Anadir  3. Modificar  4. Eliminar  0. Volver")
                sub = input("Elige: ").strip()
                if   sub == "1": ver_casos(); pausar()
                elif sub == "2": anadir_caso(); pausar()
                elif sub == "3": actualizar_caso(); pausar()
                elif sub == "4": eliminar_caso(); pausar()
                elif sub == "0": break
 
        elif op == "4":
            # Submenu de Evidencias
            while True:
                print("\n-- EVIDENCIAS --")
                print("1. Ver  2. Anadir  3. Modificar  4. Eliminar  0. Volver")
                sub = input("Elige: ").strip()
                if   sub == "1": ver_evidencias(); pausar()
                elif sub == "2": anadir_evidencia(); pausar()
                elif sub == "3": actualizar_evidencia(); pausar()
                elif sub == "4": eliminar_evidencia(); pausar()
                elif sub == "0": break
 
        elif op == "5":
            # Muestra el panel de estadisticas y espera ENTER
            ver_estadisticas()
            pausar()
 
        elif op == "6":
            # Submenu de Testigos
            while True:
                print("\n-- TESTIGOS --")
                print("1. Ver  2. Anadir  3. Modificar  4. Eliminar  0. Volver")
                sub = input("Elige: ").strip()
                if   sub == "1": ver_testigos(); pausar()
                elif sub == "2": anadir_testigo(); pausar()
                elif sub == "3": actualizar_testigo(); pausar()
                elif sub == "4": eliminar_testigo(); pausar()
                elif sub == "0": break
 
        elif op == "7":
            # Submenu de Informes
            while True:
                print("\n-- INFORMES --")
                print("1. Ver  2. Anadir  3. Modificar  4. Eliminar  0. Volver")
                sub = input("Elige: ").strip()
                if   sub == "1": ver_informes(); pausar()
                elif sub == "2": anadir_informe(); pausar()
                elif sub == "3": actualizar_informe(); pausar()
                elif sub == "4": eliminar_informe(); pausar()
                elif sub == "0": break
 
        elif op == "0":
            # Cierra la aplicacion
            print("\nCerrando el Archivo...\n")
            break
 
        else:
            print("Opcion no valida.")
 
 
# ---------------------------------------------------------------
# PUNTO DE ENTRADA DEL PROGRAMA
# Solo se ejecuta si se lanza este archivo directamente,
# no si se importa como modulo desde otro script.
# ---------------------------------------------------------------
if __name__ == "__main__":
    menu_principal()