from flask import Blueprint, request, jsonify, Response
from service.product_service import create_product, get_products, get_product_by_id, update_product, delete_product
from exports.export_products import export_products
from bs4 import BeautifulSoup
from flask_jwt_extended import jwt_required
import requests
import json
from collections import OrderedDict

productos_bp = Blueprint("productos_bp", __name__)

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

@productos_bp.route("/productos", methods=["POST"])
@jwt_required()
def crear_producto():
    try:
        data = request.json
        required_fields = ["nombre", "precio", "categoria", "stock"]
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({"success": False, "message": f"Falta el campo {field}"}), 400

        resultado = create_product(
            nombre=data["nombre"],
            descripcion=data.get("descripcion", ""),
            precio=data["precio"],
            categoria=data["categoria"],
            stock=data["stock"]
        )

        if resultado["success"]:
            return jsonify({"success": True, "message": "Producto creado correctamente."}), 201
        else:
            return jsonify({"success": False, "message": resultado.get("message", "Producto duplicado")}), 409
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al crear producto: {e}"}), 500


@productos_bp.route("/productos", methods=["GET"])
@jwt_required()
def listar_productos():
    try:
        nombre = request.args.get("nombre")
        categoria = request.args.get("categoria")
        resultado = get_products(nombre, categoria)
        if resultado["success"]:
            productos_formateados = [formatear_producto(p) for p in resultado["data"]]
            return Response(json.dumps({"success": True, "data": productos_formateados}, indent=2), mimetype="application/json")
        return jsonify({"success": False, "message": "Error al listar productos"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al listar productos: {e}"}), 500


@productos_bp.route("/productos/<int:product_id>", methods=["GET"])
@jwt_required()
def producto_por_id(product_id):
    try:
        resultado = get_product_by_id(product_id)
        if resultado["success"]:
            return Response(json.dumps({"success": True, "data": formatear_producto(resultado["data"])}, indent=2), mimetype="application/json")
        return jsonify({"success": False, "message": "Producto no encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al obtener producto: {e}"}), 500


@productos_bp.route("/productos/<int:product_id>", methods=["PUT"])
@jwt_required()
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
        if resultado["success"]:
            return jsonify({"success": True, "message": "Producto actualizado correctamente"}), 200
        else:
            if "duplicado" in resultado.get("message", "").lower():
                return jsonify({"success": False, "message": resultado.get("message")}), 409
            return jsonify({"success": False, "message": resultado.get("message")}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al actualizar producto: {e}"}), 500


@productos_bp.route("/productos/<int:product_id>", methods=["DELETE"])
@jwt_required()
def eliminar_producto(product_id):
    try:
        resultado = delete_product(product_id)
        if resultado["success"]:
            return jsonify({"success": True, "message": "Producto eliminado correctamente"}), 200
        return jsonify({"success": False, "message": "Producto no encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al eliminar producto: {e}"}), 500


@productos_bp.route("/productos/exportar", methods=["GET"])
@jwt_required()
def exportar_productos():
    try:
        formato = request.args.get("formato", "json").lower()
        productos = get_products()["data"]
        resultado = export_products(productos, formato)
        status = 200 if resultado["success"] else 400
        return jsonify(resultado), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al exportar productos: {e}"}), 500


@productos_bp.route("/productos/nombre/<string:nombre>", methods=["GET"])
@jwt_required()
def productos_por_nombre(nombre):
    try:
        resultado = get_products(nombre=nombre)
        if resultado["success"]:
            if not resultado["data"]:
                return jsonify({"success": True, "message": "No se encontraron productos con ese nombre", "data": []}), 200
            productos_formateados = [formatear_producto(p) for p in resultado["data"]]
            return jsonify({"success": True, "data": productos_formateados}), 200
        return jsonify({"success": False, "message": "Error al buscar productos por nombre"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al buscar productos por nombre: {e}"}), 500

@productos_bp.route("/productos/categoria/<string:categoria>", methods=["GET"])
@jwt_required()
def productos_por_categoria(categoria):
    try:
        resultado = get_products(categoria=categoria)
        if resultado["success"]:
            if not resultado["data"]:
                return jsonify({"success": True, "message": "No se encontraron productos en esta categoría", "data": []}), 200
            productos_formateados = [formatear_producto(p) for p in resultado["data"]]
            return jsonify({"success": True, "data": productos_formateados}), 200
        return jsonify({"success": False, "message": "Error al buscar productos por categoría"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al buscar productos por categoría: {e}"}), 500


# WEB SCRAPING (Importar productos desde web)
@productos_bp.route("/productos/importar", methods=["POST"])
@jwt_required()
def importar_productos():
    """
    Extrae productos desde una web pública de prueba (sin autenticación)
    y los inserta en la base de datos.
    """
    try:
        url = "https://webscraper.io/test-sites/e-commerce/static/computers/laptops"
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.text, "html.parser")

        productos_extraidos = []
        items = soup.select(".thumbnail")

        for item in items:
            nombre = item.select_one(".title").get_text(strip=True)
            descripcion = item.select_one(".description").get_text(strip=True)
            precio = float(item.select_one(".price").get_text(strip=True).replace("$", ""))
            categoria = "Laptops"
            stock = 10  # valor por defecto

            resultado = create_product(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                categoria=categoria,
                stock=stock
            )

            if resultado["success"]:
                productos_extraidos.append(nombre)

        if not productos_extraidos:
            return jsonify({"success": False, "message": "No se importaron nuevos productos (posiblemente duplicados)."}), 200

        return jsonify({
            "success": True,
            "message": f"{len(productos_extraidos)} productos importados exitosamente.",
            "productos": productos_extraidos
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": f"Error en web scraping: {e}"}), 500
