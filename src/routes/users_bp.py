from flask import Blueprint, request, jsonify
from service.user_service import create_user, verify_user, get_users, get_user_by_id, update_user, delete_user
from exports.export_users import export_users
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from collections import OrderedDict
#para el logout
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
        ("pais", usuario.get("pais")),
        ("clave_hash", usuario.get("clave_hash"))
    ])

# Registro de usuario
@usuarios_bp.route("/registro", methods=["POST"])
def registro():
    try:
        data = request.json
        required_fields = ["nombres", "apellidos", "edad", "telefono", "correo", "password", "ciudad", "pais"]
        for field in required_fields:
            if field not in data:
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

        if resultado:
            return jsonify({"success": True, "message": "Usuario creado correctamente."}), 201
        else:
            return jsonify({"success": False, "message": "Error al crear usuario. Correo o teléfono duplicado."}), 409
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
            # Convertimos el user_id a string para evitar errores de JWT
            access_token = create_access_token(identity=str(resultado["user_id"]))
            return jsonify({
                "success": True,
                "user_id": resultado["user_id"],
                "token": access_token
            }), 200
        else:
            return jsonify({"success": False, "message": resultado["message"]}), 401
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado en login: {e}"}), 500


# Listar usuarios con filtros opcionales
@usuarios_bp.route("/usuarios", methods=["GET"])
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
        else:
            return jsonify(resultado), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al listar usuarios: {e}"}), 500

# Obtener usuario por ID
@usuarios_bp.route("/usuarios/<int:user_id>", methods=["GET"])
def usuario_por_id(user_id):
    try:
        resultado = get_user_by_id(user_id)
        if resultado["success"]:
            return jsonify({"success": True, "data": formatear_usuario(resultado["data"])}), 200
        else:
            return jsonify(resultado), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al obtener usuario: {e}"}), 500

# Obtener usuario por correo
@usuarios_bp.route("/usuarios/correo/<string:correo>", methods=["GET"])
def usuario_por_correo(correo):
    try:
        resultado = get_users()
        if resultado["success"]:
            usuario = next((u for u in resultado["data"] if u["correo"] == correo), None)
            if usuario:
                return jsonify({"success": True, "data": formatear_usuario(usuario)}), 200
            return jsonify({"success": False, "message": "Usuario no encontrado."}), 404
        return jsonify(resultado), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al obtener usuario por correo: {e}"}), 500

# Obtener usuarios por país
@usuarios_bp.route("/usuarios/pais/<string:pais>", methods=["GET"])
def usuarios_por_pais(pais):
    try:
        resultado = get_users(pais=pais)
        if resultado["success"]:
            usuarios_formateados = [formatear_usuario(u) for u in resultado["data"]]
            if usuarios_formateados:
                return jsonify({"success": True, "data": usuarios_formateados}), 200
            return jsonify({"success": False, "message": f"No se encontraron usuarios en {pais}"}), 404
        return jsonify(resultado), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al obtener usuarios por país: {e}"}), 500

# Actualizar usuario
@usuarios_bp.route("/usuarios/<int:user_id>", methods=["PUT"])
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
        status = 200 if resultado["success"] else 400
        return jsonify(resultado), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al actualizar usuario: {e}"}), 500

# Eliminar usuario
@usuarios_bp.route("/usuarios/<int:user_id>", methods=["DELETE"])
def eliminar_usuario(user_id):
    try:
        resultado = delete_user(user_id)
        status = 200 if resultado["success"] else 404
        return jsonify(resultado), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al eliminar usuario: {e}"}), 500

# Exportar usuarios
@usuarios_bp.route("/usuarios/exportar", methods=["GET"])
def exportar_usuarios():
    try:
        formato = request.args.get("formato", "json").lower()
        usuarios = get_users()["data"]
        resultado = export_users(usuarios, formato)
        status = 200 if resultado["success"] else 400
        return jsonify(resultado), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado al exportar usuarios: {e}"}), 500

@usuarios_bp.route("/logout", methods=["POST"])
@jwt_required()  # <- Esto es obligatorio
def logout_usuario():
    try:
        token_jti = get_jwt()["jti"]  # Ahora funciona porque el token está presente
        BLACKLIST.add(token_jti)      # Agregas a la blacklist
        return jsonify({"success": True, "message": "Logout exitoso"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado en logout: {e}"}), 500

