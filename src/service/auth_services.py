# auth_services.py
from flask_jwt_extended import decode_token

BLACKLIST = set()  # <-- define aquí

def logout(token):
    try:
        decoded = decode_token(token)
        jti = decoded["jti"]
        BLACKLIST.add(jti)
        return {"success": True, "message": "Logout exitoso"}
    except Exception as e:
        return {"success": False, "message": str(e)}
