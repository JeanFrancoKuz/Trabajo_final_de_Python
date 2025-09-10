from flask import Blueprint, request, jsonify
from service.sales_services import create_sale, get_sales, get_sale_by_id, update_sale, delete_sale
from exports.export_sales import export_sales
from collections import OrderedDict

sales_bp = Blueprint("sales_bp", __name__)

# Formatear venta para salida JSON
def formatear_venta(venta):
    return OrderedDict([
        ("id", venta.get("id")),
        ("user_id", venta.get("user_id")),
        ("product_id", venta.get("product_id")),
        ("cantidad", venta.get("cantidad")),
        ("total", venta.get("total")),
        ("fecha", venta.get("fecha"))
    ])

# Crear nueva venta
@sales_bp.route("/ventas", methods=["POST"])
def crear_venta():
    try:
        data = request.json
        required_fields = ["user_id", "product_id", "cantidad", "total"]
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "message": f"Falta el campo {field}"}), 400

        resultado = create_sale(
            user_id=data["user_id"],
            product_id=data["product_id"],
            cantidad=data["cantidad"],
            total=data["total"]
        )
        if resultado["success"]:
            return jsonify({"success": True, "message": "Venta registrada correctamente.", "data": formatear_venta(resultado["data"])}), 201
        return jsonify(resultado), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al registrar venta: {e}"}), 500

# Listar ventas (opcionalmente filtradas)
@sales_bp.route("/ventas", methods=["GET"])
def listar_ventas():
    try:
        user_id = request.args.get("user_id", type=int)
        product_id = request.args.get("product_id", type=int)

        resultado = get_sales(user_id=user_id, product_id=product_id)
        if resultado["success"]:
            ventas_formateadas = [formatear_venta(v) for v in resultado["data"]]
            return jsonify({"success": True, "data": ventas_formateadas}), 200
        return jsonify(resultado), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al listar ventas: {e}"}), 500

# Obtener venta por ID
@sales_bp.route("/ventas/<int:sale_id>", methods=["GET"])
def venta_por_id(sale_id):
    try:
        resultado = get_sale_by_id(sale_id)
        if resultado["success"]:
            return jsonify({"success": True, "data": formatear_venta(resultado["data"])}), 200
        return jsonify(resultado), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al obtener venta: {e}"}), 500

# Actualizar venta
@sales_bp.route("/ventas/<int:sale_id>", methods=["PUT"])
def actualizar_venta(sale_id):
    try:
        data = request.json
        resultado = update_sale(
            sale_id,
            user_id=data.get("user_id"),
            product_id=data.get("product_id"),
            cantidad=data.get("cantidad"),
            total=data.get("total")
        )
        status = 200 if resultado["success"] else 400
        return jsonify(resultado), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al actualizar venta: {e}"}), 500

# Eliminar venta
@sales_bp.route("/ventas/<int:sale_id>", methods=["DELETE"])
def eliminar_venta(sale_id):
    try:
        resultado = delete_sale(sale_id)
        status = 200 if resultado["success"] else 404
        return jsonify(resultado), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al eliminar venta: {e}"}), 500

# Exportar ventas
@sales_bp.route("/ventas/exportar", methods=["GET"])
def exportar_ventas():
    try:
        formato = request.args.get("formato", "json").lower()
        ventas = get_sales()["data"]
        resultado = export_sales(ventas, formato)
        status = 200 if resultado["success"] else 400
        return jsonify(resultado), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al exportar ventas: {e}"}), 500
