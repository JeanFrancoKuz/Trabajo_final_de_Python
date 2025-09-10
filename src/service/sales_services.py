from database import get_connection
from datetime import datetime

# Crear venta
def create_sale(user_id, product_id, cantidad, total):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Validar stock suficiente
        cursor.execute("SELECT stock, precio FROM productos WHERE id=?", (product_id,))
        producto = cursor.fetchone()
        if not producto:
            return {"success": False, "message": "Producto no encontrado"}
        if producto["stock"] < cantidad:
            return {"success": False, "message": "Stock insuficiente"}
        
        # Registrar venta
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO sales (user_id, product_id, cantidad, total, fecha)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, product_id, cantidad, total, fecha))
        
        # Actualizar stock del producto
        nuevo_stock = producto["stock"] - cantidad
        cursor.execute("UPDATE productos SET stock=? WHERE id=?", (nuevo_stock, product_id))
        
        conn.commit()
        sale_id = cursor.lastrowid
        return get_sale_by_id(sale_id)
    
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Listar ventas
def get_sales(user_id=None, product_id=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM sales WHERE 1=1"
        params = []
        if user_id:
            query += " AND user_id=?"; params.append(user_id)
        if product_id:
            query += " AND product_id=?"; params.append(product_id)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        ventas = [dict(row) for row in rows]
        return {"success": True, "data": ventas}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Obtener venta por ID
def get_sale_by_id(sale_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sales WHERE id=?", (sale_id,))
        row = cursor.fetchone()
        if row:
            return {"success": True, "data": dict(row)}
        return {"success": False, "message": "Venta no encontrada"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Actualizar venta
def update_sale(sale_id, user_id=None, product_id=None, cantidad=None, total=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        updates, params = [], []
        if user_id: updates.append("user_id=?"); params.append(user_id)
        if product_id: updates.append("product_id=?"); params.append(product_id)
        if cantidad is not None: updates.append("cantidad=?"); params.append(cantidad)
        if total is not None: updates.append("total=?"); params.append(total)
        if not updates:
            return {"success": False, "message": "No se proporcionaron campos para actualizar"}
        params.append(sale_id)
        query = f"UPDATE sales SET {', '.join(updates)} WHERE id=?"
        cursor.execute(query, tuple(params))
        conn.commit()
        if cursor.rowcount == 0:
            return {"success": False, "message": "Venta no encontrada"}
        return {"success": True, "message": "Venta actualizada correctamente"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# Eliminar venta
def delete_sale(sale_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sales WHERE id=?", (sale_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return {"success": False, "message": "Venta no encontrada"}
        return {"success": True, "message": "Venta eliminada correctamente"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()
