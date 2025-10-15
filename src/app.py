from flask import Flask, jsonify
from routes.users_bp import usuarios_bp   # Ajusta la ruta según tu estructura
from routes.products_bp import productos_bp
from routes.sales_bp import sales_bp 
from flask_jwt_extended import JWTManager
from service.auth_services import BLACKLIST
from datetime import timedelta
from database import init_db


# Crear la app de Flask
app = Flask(__name__)

# Inicializar la base de datos (si no existe)
init_db()

# Configuración JWT
app.config["JWT_SECRET_KEY"] = "TU_CLAVE_SECRETA_AQUI"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30) #Para pruebas
jwt = JWTManager(app)
app.config['DEBUG'] = True


app.config["JWT_BLACKLIST_ENABLED"] = True

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLACKLIST

# Registrar blueprints
app.register_blueprint(usuarios_bp, url_prefix="/api")
app.register_blueprint(productos_bp, url_prefix="/api")
app.register_blueprint(sales_bp, url_prefix="/api")

# Ruta principal de prueba
@app.route("/")
def index():
    return jsonify({"message": "API de E-commerce funcionando correctamente"}), 200

# Manejo global de errores 500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "message": "Error interno del servidor"}), 500

# Manejo de errores 404
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"success": False, "message": "Recurso no encontrado"}), 404

# Ejecutar la app
if __name__ == "__main__":
    app.run(debug=True)