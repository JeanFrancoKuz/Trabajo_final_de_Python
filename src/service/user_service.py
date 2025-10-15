from database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

# Crear usuario
def create_user(nombres, apellidos, edad, telefono, correo, password, ciudad, pais):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        hashed_pw = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (nombres, apellidos, edad, telefono, correo, clave_hash, ciudad, pais)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nombres, apellidos, edad, telefono, correo, hashed_pw, ciudad, pais))
        conn.commit()
        new_id = cursor.lastrowid
        return get_user_by_id(new_id)
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Verificar usuario (login)
def verify_user(correo, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, clave_hash FROM users WHERE correo=?", (correo,))
        user = cursor.fetchone()
        if user and check_password_hash(user["clave_hash"], password):
            return {"success": True, "user_id": user["id"]}
        return {"success": False, "message": "Correo o contraseña incorrectos."}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Obtener todos los usuarios con filtros opcionales
def get_users(pais=None, ciudad=None, edad_min=None, edad_max=None, correo=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE 1=1"
        params = []
        if pais:
            query += " AND pais=?"; params.append(pais)
        if ciudad:
            query += " AND ciudad=?"; params.append(ciudad)
        if edad_min is not None:
            query += " AND edad>=?"; params.append(edad_min)
        if edad_max is not None:
            query += " AND edad<=?"; params.append(edad_max)
        if correo is not None:
            query += " AND correo=?"; params.append(correo)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        users = [dict(row) for row in rows]
        return {"success": True, "data": users}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Obtener usuario por ID
def get_user_by_id(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        if row:
            return {"success": True, "data": dict(row)}
        return {"success": False, "message": "Usuario no encontrado"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Actualizar usuario
def update_user(user_id, nombres=None, apellidos=None, edad=None, telefono=None, correo=None, ciudad=None, pais=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        updates, params = [], []
        if nombres: updates.append("nombres=?"); params.append(nombres)
        if apellidos: updates.append("apellidos=?"); params.append(apellidos)
        if edad is not None: updates.append("edad=?"); params.append(edad)
        if telefono: updates.append("telefono=?"); params.append(telefono)
        if correo: updates.append("correo=?"); params.append(correo)
        if ciudad: updates.append("ciudad=?"); params.append(ciudad)
        if pais: updates.append("pais=?"); params.append(pais)
        if not updates:
            return {"success": False, "message": "No se proporcionaron campos para actualizar"}
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id=?"
        cursor.execute(query, tuple(params))
        conn.commit()
        if cursor.rowcount == 0:
            return {"success": False, "message": "Usuario no encontrado"}
        return {"success": True, "message": "Usuario actualizado correctamente"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Eliminar usuario
def delete_user(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return {"success": False, "message": "Usuario no encontrado"}
        return {"success": True, "message": "Usuario eliminado correctamente"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()
