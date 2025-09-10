from flask import Blueprint, request, jsonify, Response
from service.product_service import create_product, get_products, get_product_by_id, update_product, delete_product
from exports.export_products import export_products
from bs4 import BeautifulSoup
import requests
import json
from collections import OrderedDict

productos_bp = Blueprint("productos_bp", __name__)

# Formatear producto para salida JSON (orden específico)
def formatear_producto(producto):
    return OrderedDict([
        ("id", producto.get("id")),
        ("nombre", producto.get("nombre")),
        ("descripcion", producto.get("descripcion")),
        ("precio", producto.get("precio")),
        ("categoria", producto.get("categoria")),
        ("stock", producto.get("stock")),
        ("registro", producto.get("registro"))
    ])

# Crear producto
@productos_bp.route("/productos", methods=["POST"])
def crear_producto():
    try:
        data = request.json
        required_fields = ["nombre", "precio", "categoria", "stock"]
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "message": f"Falta el campo {field}"}), 400

        resultado = create_product(
            nombre=data["nombre"],
            descripcion=data.get("descripcion", ""),
            precio=data["precio"],
            categoria=data["categoria"],
            stock=data["stock"]
        )
        if resultado:
            return jsonify({"success": True, "message": "Producto creado correctamente."}), 201
        else:
            return jsonify({"success": False, "message": "Error al crear producto."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado: {e}"}), 500

# Listar productos con filtros opcionales (nombre, categoria)
@productos_bp.route("/productos", methods=["GET"])
def listar_productos():
    try:
        nombre = request.args.get("nombre")
        categoria = request.args.get("categoria")
        resultado = get_products(nombre, categoria)
        if resultado["success"]:
            productos_formateados = [formatear_producto(p) for p in resultado["data"]]
            return Response(
                json.dumps({"success": True, "data": productos_formateados}, indent=2),
                mimetype="application/json"
            )
        else:
            return jsonify(resultado), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al listar productos: {e}"}), 500

# Obtener producto por ID
@productos_bp.route("/productos/<int:product_id>", methods=["GET"])
def producto_por_id(product_id):
    try:
        resultado = get_product_by_id(product_id)
        if resultado["success"]:
            return Response(
                json.dumps({"success": True, "data": formatear_producto(resultado["data"])}, indent=2),
                mimetype="application/json"
            )
        else:
            return jsonify(resultado), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al obtener producto: {e}"}), 500

# Actualizar producto
@productos_bp.route("/productos/<int:product_id>", methods=["PUT"])
def actualizar_producto(product_id):
    try:
        data = request.json
        resultado = update_product(
            product_id,
            nombre=data.get("nombre"),
            descripcion=data.get("descripcion"),
            precio=data.get("precio"),
            categoria=data.get("categoria"),
            stock=data.get("stock")
        )
        status = 200 if resultado["success"] else 400
        return jsonify(resultado), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al actualizar producto: {e}"}), 500

# Eliminar producto
@productos_bp.route("/productos/<int:product_id>", methods=["DELETE"])
def eliminar_producto(product_id):
    try:
        resultado = delete_product(product_id)
        status = 200 if resultado["success"] else 404
        return jsonify(resultado), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al eliminar producto: {e}"}), 500

# Exportar productos
@productos_bp.route("/productos/exportar", methods=["GET"])
def exportar_productos():
    try:
        formato = request.args.get("formato", "json").lower()
        productos = get_products()["data"]
        resultado = export_products(productos, formato)
        status = 200 if resultado["success"] else 400
        return jsonify(resultado), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al exportar productos: {e}"}), 500

# Importar productos vía web scraping (ejemplo simple)
@productos_bp.route("/productos/importar", methods=["POST"])
def importar_productos():
    try:
        url = request.json.get("url")
        if not url:
            return jsonify({"success": False, "message": "Falta el campo 'url'"}), 400

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # Aquí deberías definir la lógica de scraping específica
        # Ejemplo: extraer nombres y precios de algún selector
        productos_scrapeados = [
            {"nombre": "Producto Demo", "precio": 100, "categoria": "Demo", "stock": 10, "descripcion": "Demo"}
        ]
        # Guardar en DB
        for p in productos_scrapeados:
            create_product(p["nombre"], p["descripcion"], p["precio"], p["categoria"], p["stock"])

        return jsonify({"success": True, "message": "Productos importados correctamente."}), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al importar productos: {e}"}), 500
