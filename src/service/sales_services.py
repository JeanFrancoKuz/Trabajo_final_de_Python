from database import get_connection
from datetime import datetime
import openpyxl
import os

# service/sales_services.py

def create_sale(product_id, cantidad, total, user_id):
    from database import get_connection
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sales (user_id, product_id, cantidad, total) VALUES (?, ?, ?, ?)",
            (user_id, product_id, cantidad, total)
        )
        conn.commit()
        sale_id = cursor.lastrowid
        cursor.execute("SELECT * FROM sales WHERE id = ?", (sale_id,))
        venta = dict(cursor.fetchone())
        return {"success": True, "data": venta}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()


def get_sales(user_id=None, product_id=None):
    from database import get_connection
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM sales WHERE 1=1"
        params = []
        if user_id:
            query += " AND user_id=?"
            params.append(user_id)
        if product_id:
            query += " AND product_id=?"
            params.append(product_id)
        cursor.execute(query, tuple(params))
        ventas = [dict(row) for row in cursor.fetchall()]
        return {"success": True, "data": ventas}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()


def get_sale_by_id(sale_id):
    from database import get_connection
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


def update_sale(sale_id, cantidad, total):
    from database import get_connection
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sales SET cantidad=?, total=? WHERE id=?",
            (cantidad, total, sale_id)
        )
        conn.commit()
        cursor.execute("SELECT * FROM sales WHERE id=?", (sale_id,))
        return {"success": True, "data": dict(cursor.fetchone())}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()


def delete_sale(sale_id):
    from database import get_connection
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sales WHERE id=?", (sale_id,))
        conn.commit()
        if cursor.rowcount:
            return {"success": True, "message": "Venta eliminada"}
        return {"success": False, "message": "Venta no encontrada"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()
