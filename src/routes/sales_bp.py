from flask import Blueprint, request, jsonify
from service.sales_services import create_sale, get_sales, get_sale_by_id, update_sale, delete_sale
from service.product_service import get_product_by_id, update_product
from exports.export_sales import export_sales
from flask_jwt_extended import jwt_required
from collections import OrderedDict
from datetime import datetime
import os
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference

sales_bp = Blueprint("sales_bp", __name__)

# Formatear venta para la respuesta
def formatear_venta(venta):
    return OrderedDict([
        ("id", venta.get("id")),
        ("user_id", venta.get("user_id")),
        ("product_id", venta.get("product_id")),
        ("cantidad", venta.get("cantidad")),
        ("total", venta.get("total")),
        ("fecha", venta.get("fecha"))
    ])

# -------------------- CREAR VENTA --------------------
@sales_bp.route("/ventas", methods=["POST"])
@jwt_required()
def crear_venta():
    try:
        data = request.json
        required_fields = ["user_id", "product_id", "cantidad"]
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({"success": False, "message": f"Falta el campo {field}"}), 400

        # Obtener producto
        product_res = get_product_by_id(data["product_id"])
        if not product_res["success"]:
            return jsonify({"success": False, "message": "Producto no encontrado"}), 404
        producto = product_res["data"]

        # Validar stock
        if producto["stock"] < data["cantidad"]:
            return jsonify({"success": False, "message": "Stock insuficiente"}), 400

        total_venta = producto["precio"] * data["cantidad"]

        # Crear venta
        resultado = create_sale(data["user_id"], data["product_id"], data["cantidad"], total_venta)

        if resultado["success"]:
            # Actualizar stock
            update_product(producto["id"], stock=producto["stock"] - data["cantidad"])
            return jsonify({"success": True, "message": "Venta registrada correctamente",
                            "data": formatear_venta(resultado["data"])}), 201

        return jsonify({"success": False, "message": resultado.get("message", "Error al crear venta")}), 400

    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al crear venta: {e}"}), 500

# -------------------- LISTAR VENTAS --------------------
@sales_bp.route("/ventas", methods=["GET"])
@jwt_required()
def listar_ventas():
    try:
        user_id = request.args.get("user_id", type=int)
        product_id = request.args.get("product_id", type=int)
        resultado = get_sales(user_id=user_id, product_id=product_id)

        if resultado["success"]:
            ventas_formateadas = [formatear_venta(v) for v in resultado["data"]]
            return jsonify({"success": True, "data": ventas_formateadas}), 200

        return jsonify({"success": False, "message": "Error al listar ventas"}), 400

    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al listar ventas: {e}"}), 500

# -------------------- OBTENER VENTA POR ID --------------------
@sales_bp.route("/ventas/<int:sale_id>", methods=["GET"])
@jwt_required()
def venta_por_id(sale_id):
    try:
        resultado = get_sale_by_id(sale_id)
        if resultado["success"]:
            return jsonify({"success": True, "data": formatear_venta(resultado["data"])}), 200
        return jsonify({"success": False, "message": "Venta no encontrada"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al obtener venta: {e}"}), 500

# -------------------- ACTUALIZAR VENTA --------------------
@sales_bp.route("/ventas/<int:sale_id>", methods=["PUT"])
@jwt_required()
def actualizar_venta(sale_id):
    try:
        data = request.json
        venta_res = get_sale_by_id(sale_id)
        if not venta_res["success"]:
            return jsonify({"success": False, "message": "Venta no encontrada"}), 404

        venta = venta_res["data"]
        producto_res = get_product_by_id(venta["product_id"])
        if not producto_res["success"]:
            return jsonify({"success": False, "message": "Producto de la venta no encontrado"}), 404
        producto = producto_res["data"]

        nueva_cantidad = data.get("cantidad", venta["cantidad"])
        ajuste_stock = producto["stock"] + venta["cantidad"] - nueva_cantidad
        if ajuste_stock < 0:
            return jsonify({"success": False, "message": "Stock insuficiente para la actualización"}), 400

        total = data.get("total", producto["precio"] * nueva_cantidad)
        resultado = update_sale(sale_id, cantidad=nueva_cantidad, total=total)

        if resultado["success"]:
            update_product(producto["id"], stock=ajuste_stock)
            return jsonify({"success": True, "message": "Venta actualizada correctamente",
                            "data": formatear_venta(get_sale_by_id(sale_id)["data"])}), 200

        return jsonify({"success": False, "message": resultado.get("message", "Error al actualizar venta")}), 400

    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al actualizar venta: {e}"}), 500

# -------------------- ELIMINAR VENTA --------------------
@sales_bp.route("/ventas/<int:sale_id>", methods=["DELETE"])
@jwt_required()
def eliminar_venta(sale_id):
    try:
        venta_res = get_sale_by_id(sale_id)
        if not venta_res["success"]:
            return jsonify({"success": False, "message": "Venta no encontrada"}), 404
        venta = venta_res["data"]

        producto_res = get_product_by_id(venta["product_id"])
        if producto_res["success"]:
            producto = producto_res["data"]
            update_product(producto["id"], stock=producto["stock"] + venta["cantidad"])

        resultado = delete_sale(sale_id)
        status = 200 if resultado["success"] else 404
        return jsonify(resultado), status

    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al eliminar venta: {e}"}), 500

# -------------------- EXPORTAR VENTAS --------------------
@sales_bp.route("/ventas/exportar", methods=["GET"])
@jwt_required()
def exportar_ventas():
    try:
        formato = request.args.get("formato", "json").lower()
        ventas = get_sales()["data"]
        resultado = export_sales(ventas, formato)
        status = 200 if resultado["success"] else 400
        return jsonify(resultado), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al exportar ventas: {e}"}), 500

# -------------------- REPORTE MENSUAL --------------------
@sales_bp.route("/ventas/reporte_mensual", methods=["GET"])
@jwt_required()
def reporte_mensual():
    try:
        mes = request.args.get("mes", type=int)
        año = request.args.get("año", type=int, default=datetime.now().year)
        if not mes or mes < 1 or mes > 12:
            return jsonify({"success": False, "message": "Mes inválido"}), 400

        ventas = get_sales()["data"]
        ventas_mes = [v for v in ventas if datetime.fromisoformat(v["fecha"]).month == mes
                      and datetime.fromisoformat(v["fecha"]).year == año]

        if not ventas_mes:
            return jsonify({"success": False, "message": "No hay ventas en ese mes"}), 404

        wb = Workbook()
        ws = wb.active
        ws.title = f"Ventas {mes}-{año}"
        ws.append(["ID Venta", "Usuario", "Producto", "Cantidad", "Total", "Fecha"])
        for v in ventas_mes:
            ws.append([v["id"], v["user_id"], v["product_id"], v["cantidad"], v["total"], v["fecha"]])

        chart = BarChart()
        data = Reference(ws, min_col=5, min_row=1, max_row=len(ventas_mes)+1)
        cats = Reference(ws, min_col=1, min_row=2, max_row=len(ventas_mes)+1)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        chart.title = "Ventas Totales"
        ws.add_chart(chart, "H2")

        os.makedirs("exports", exist_ok=True)
        path = f"exports/reporte_ventas_{mes}_{año}.xlsx"
        wb.save(path)

        return jsonify({"success": True, "message": f"Reporte generado: {path}"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Error al generar reporte mensual: {e}"}), 500

# -------------------- VENTAS POR USUARIO --------------------
@sales_bp.route("/ventas/usuario/<int:user_id>", methods=["GET"])
@jwt_required()
def ventas_por_usuario(user_id):
    try:
        resultado = get_sales(user_id=user_id)
        if resultado["success"]:
            if not resultado["data"]:
                return jsonify({"success": True, "message": "No hay ventas para este usuario", "data": []}), 200
            ventas_formateadas = [formatear_venta(v) for v in resultado["data"]]
            return jsonify({"success": True, "data": ventas_formateadas}), 200
        return jsonify({"success": False, "message": "Error al obtener ventas por usuario"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al obtener ventas por usuario: {e}"}), 500

# -------------------- VENTAS POR PRODUCTO --------------------
@sales_bp.route("/ventas/producto/<int:product_id>", methods=["GET"])
@jwt_required()
def ventas_por_producto(product_id):
    try:
        resultado = get_sales(product_id=product_id)
        if resultado["success"]:
            if not resultado["data"]:
                return jsonify({"success": True, "message": "No hay ventas para este producto", "data": []}), 200
            ventas_formateadas = [formatear_venta(v) for v in resultado["data"]]
            return jsonify({"success": True, "data": ventas_formateadas}), 200
        return jsonify({"success": False, "message": "Error al obtener ventas por producto"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al obtener ventas por producto: {e}"}), 500
