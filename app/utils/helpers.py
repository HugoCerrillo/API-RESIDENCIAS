from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Usuario

def admin_required(fn):
    @wraps(fn)
    @jwt_required()    
    def wrapper(*args, **kwargs):
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        if not usuario or usuario.rol != 'Administrador':
            return jsonify({
                "status": "error",
                "message": "Acceso denegado. Se requiere rol de Administrador."
            }), 403
        return fn(*args, **kwargs)
    return wrapper

def success_response(message, data=None, status_code=200):
    response = {"status": "success", "message": message}
    if data:
        response.update(data)
    return jsonify(response), status_code

def error_response(message, status_code=500):
    return jsonify({"status": "error", "message": message}), status_code
