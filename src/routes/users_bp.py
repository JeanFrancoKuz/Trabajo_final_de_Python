from flask import Blueprint, request, jsonify
from service.user_service import create_user, verify_user, get_users, get_user_by_id, update_user, delete_user
from exports.export_users import export_users
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from collections import OrderedDict
from service.auth_services import BLACKLIST

usuarios_bp = Blueprint("usuarios_bp", __name__)

# Formatear usuario para salida JSON (sin clave_hash)
def formatear_usuario(usuario):
    return OrderedDict([
        ("id", usuario.get("id")),
        ("nombres", usuario.get("nombres")),
        ("apellidos", usuario.get("apellidos")),
        ("edad", usuario.get("edad")),
        ("correo", usuario.get("correo")),
        ("telefono", usuario.get("telefono")),
        ("ciudad", usuario.get("ciudad")),
        ("pais", usuario.get("pais"))
    ])

# Registro de usuario
@usuarios_bp.route("/registro", methods=["POST"])
def registro():
    try:
        data = request.json
        required_fields = ["nombres", "apellidos", "edad", "telefono", "correo", "password", "ciudad", "pais"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"success": False, "message": f"Falta el campo {field}"}), 400

        resultado = create_user(
            nombres=data["nombres"],
            apellidos=data["apellidos"],
            edad=data["edad"],
            telefono=data["telefono"],
            correo=data["correo"],
            password=data["password"],
            ciudad=data["ciudad"],
            pais=data["pais"]
        )

        if resultado["success"]:
            return jsonify({"success": True, "message": "Usuario creado correctamente."}), 201
        else:
            return jsonify({"success": False, "message": resultado.get("message", "Correo o teléfono duplicado")}), 409
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado en registro: {e}"}), 500

# Login de usuario
@usuarios_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        correo = data.get("correo")
        password = data.get("password")
        if not correo or not password:
            return jsonify({"success": False, "message": "Correo y contraseña son obligatorios."}), 400

        resultado = verify_user(correo, password)
        if resultado["success"]:
            user_id = resultado.get("user_id")
            if user_id is None:
                return jsonify({"success": False, "message": "ID de usuario no válido"}), 500

            access_token = create_access_token(identity=str(user_id))
            
            return jsonify({
                "success": True,
                "user_id": user_id,
                "token": access_token
            }), 200
        else:
            return jsonify({"success": False, "message": resultado["message"]}), 401
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado en login: {e}"}), 500

# Listar usuarios
@usuarios_bp.route("/usuarios", methods=["GET"])
@jwt_required()
def listar_usuarios():
    try:
        pais = request.args.get("pais")
        ciudad = request.args.get("ciudad")
        edad_min = request.args.get("edad_min", type=int)
        edad_max = request.args.get("edad_max", type=int)

        resultado = get_users(pais, ciudad, edad_min, edad_max)
        if resultado["success"]:
            usuarios_formateados = [formatear_usuario(u) for u in resultado["data"]]
            return jsonify({"success": True, "data": usuarios_formateados}), 200
        return jsonify({"success": False, "message": "Error al listar usuarios"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al listar usuarios: {e}"}), 500

# Obtener usuario por ID
@usuarios_bp.route("/usuarios/<int:user_id>", methods=["GET"])
@jwt_required()
def usuario_por_id(user_id):
    try:
        resultado = get_user_by_id(user_id)
        if resultado["success"]:
            return jsonify({"success": True, "data": formatear_usuario(resultado["data"])}), 200
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al obtener usuario: {e}"}), 500

# Actualizar usuario
@usuarios_bp.route("/usuarios/<int:user_id>", methods=["PUT"])
@jwt_required()
def actualizar_usuario(user_id):
    try:
        data = request.json
        resultado = update_user(
            user_id,
            nombres=data.get("nombres"),
            apellidos=data.get("apellidos"),
            edad=data.get("edad"),
            telefono=data.get("telefono"),
            correo=data.get("correo"),
            ciudad=data.get("ciudad"),
            pais=data.get("pais")
        )
        if resultado["success"]:
            return jsonify({"success": True, "message": "Usuario actualizado correctamente"}), 200
        else:
            # Si la actualización falla por duplicidad
            if "duplicado" in resultado.get("message", "").lower():
                return jsonify({"success": False, "message": resultado.get("message")}), 409
            return jsonify({"success": False, "message": resultado.get("message")}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al actualizar usuario: {e}"}), 500

# Eliminar usuario
@usuarios_bp.route("/usuarios/<int:user_id>", methods=["DELETE"])
@jwt_required()
def eliminar_usuario(user_id):
    try:
        resultado = delete_user(user_id)
        if resultado["success"]:
            return jsonify({"success": True, "message": "Usuario eliminado correctamente"}), 200
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al eliminar usuario: {e}"}), 500

# Exportar usuarios
@usuarios_bp.route("/usuarios/exportar", methods=["GET"])
@jwt_required()
def exportar_usuarios():
    try:
        formato = request.args.get("formato", "json").lower()
        usuarios = get_users()["data"]
        resultado = export_users(usuarios, formato)
        status = 200 if resultado["success"] else 400
        return jsonify(resultado), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al exportar usuarios: {e}"}), 500

# Logout
@usuarios_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout_usuario():
    token_jti = get_jwt()["jti"]
    BLACKLIST.add(token_jti)
    return jsonify({"success": True, "message": "Logout exitoso"}), 200


