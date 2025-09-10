from database import get_connection

# Crear producto
def create_product(nombre, descripcion, precio, categoria, stock):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, descripcion, precio, categoria, stock)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, descripcion, precio, categoria, stock))
        conn.commit()
        new_id = cursor.lastrowid
        return get_product_by_id(new_id)
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Listar productos
def get_products(nombre=None, categoria=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM productos WHERE 1=1"
        params = []
        if nombre:
            query += " AND nombre LIKE ?"
            params.append(f"%{nombre}%")
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        productos = [dict(row) for row in rows]
        return {"success": True, "data": productos}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Obtener por ID
def get_product_by_id(product_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        if row:
            return {"success": True, "data": dict(row)}
        return {"success": False, "message": "Producto no encontrado"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Actualizar producto
def update_product(product_id, nombre=None, descripcion=None, precio=None, categoria=None, stock=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        updates, params = [], []
        if nombre: updates.append("nombre=?"); params.append(nombre)
        if descripcion is not None: updates.append("descripcion=?"); params.append(descripcion)
        if precio is not None: updates.append("precio=?"); params.append(precio)
        if categoria: updates.append("categoria=?"); params.append(categoria)
        if stock is not None: updates.append("stock=?"); params.append(stock)
        if not updates:
            return {"success": False, "message": "No se proporcionaron campos para actualizar"}
        params.append(product_id)
        query = f"UPDATE productos SET {', '.join(updates)} WHERE id=?"
        cursor.execute(query, tuple(params))
        conn.commit()
        if cursor.rowcount == 0:
            return {"success": False, "message": "Producto no encontrado"}
        return {"success": True, "message": "Producto actualizado correctamente"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Eliminar producto
def delete_product(product_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id=?", (product_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return {"success": False, "message": "Producto no encontrado"}
        return {"success": True, "message": "Producto eliminado correctamente"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()
