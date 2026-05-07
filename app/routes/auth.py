from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, decode_token
from datetime import datetime, timedelta
from ..models import db, Usuario
from ..services.email_service import enviar_correo_recuperacion
from ..utils.helpers import admin_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('correo')
    password = data.get('contraseña')

    user = Usuario.query.filter_by(correo=email).first()

    if user and check_password_hash(user.contraseña, password):
        access_token = create_access_token(identity=str(user.id_usuario))
        response = make_response(jsonify({
            "status": "success",
            "message": f"Bienvenid@ {user.nombre}",
            "user": user.to_dict()
        }))
        set_access_cookies(response, access_token)        
        return response, 200

    return jsonify({"status": "error", "message": "Correo o contraseña incorrectos"}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    existe = Usuario.query.filter_by(correo=data.get('correo')).first()
    if existe:
        return jsonify({"status": "error", "message": "El correo ya está registrado"}), 400

    try:
        nuevo_usuario = Usuario(
            nombre=data.get('nombre'),
            apellido_paterno=data.get('apellido_paterno'),
            apellido_materno=data.get('apellido_materno'),
            rol=data.get('rol'), 
            telefono=data.get('telefono'),
            correo=data.get('correo'),
            contraseña=generate_password_hash(data.get('contraseña'))
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({"status": "success", "message": "Usuario creado exitosamente", "user": nuevo_usuario.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@auth_bp.route('/usuarios', methods=['GET'])
@jwt_required()
def get_usuarios():
    usuarios = Usuario.query.all()
    return jsonify({"status": "success", "users": [u.to_dict() for u in usuarios]}), 200

@auth_bp.route('/usuarios/<int:id>', methods=['GET'])
@jwt_required()
def get_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    return jsonify({"status": "success", "user": usuario.to_dict()}), 200

@auth_bp.route('/recuperar-password', methods=['POST'])
def solicitar_recuperacion():
    data = request.json
    correo = data.get('correo')
    usuario = Usuario.query.filter_by(correo=correo).first()
    
    if not usuario:
        return jsonify({"status": "error", "message": "El correo no está registrado"}), 404

    token = create_access_token(identity=str(usuario.id_usuario), expires_delta=timedelta(minutes=15))
    enlace = f"https://exper-track.vercel.app/reset-password?token={token}"
    
    if enviar_correo_recuperacion(correo, enlace):
        return jsonify({"status": "success", "message": "Correo enviado con éxito"}), 200
    else:
        return jsonify({"status": "error", "message": "Error al enviar el correo"}), 500

@auth_bp.route('/restablecer-password', methods=['POST'])
def restablecer_password():
    print(">>> Iniciando proceso de restablecimiento")
    try:
        data = request.get_json(silent=True) or {}
        token = data.get('token') or request.args.get('token')
        nueva_pass = data.get('password')

        if not token or not nueva_pass:
            return jsonify({"status": "error", "message": "Faltan datos (token o contraseña)"}), 200

        # Decodificación manual aislada
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
            usuario = Usuario.query.get(int(user_id))
        except Exception as jwt_err:
            print(f">>> Error JWT: {jwt_err}")
            return jsonify({"status": "error", "message": "Enlace inválido o caducado", "detail": str(jwt_err)}), 200

        if not usuario:
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 200
            
        usuario.contraseña = generate_password_hash(nueva_pass)
        db.session.commit()
        print(f">>> Éxito: Contraseña cambiada para {usuario.correo}")
        return jsonify({"status": "success", "message": "Contraseña actualizada correctamente"}), 200

    except Exception as e:
        print(f">>> Error General: {e}")
        return jsonify({"status": "error", "message": "Error interno", "detail": str(e)}), 200

@auth_bp.route('/usuarios/<int:id>', methods=['PUT'])
@jwt_required()
def update_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
        
    data = request.json
    try:
        if 'nombre' in data: usuario.nombre = data['nombre']
        if 'apellido_paterno' in data: usuario.apellido_paterno = data['apellido_paterno']
        if 'apellido_materno' in data: usuario.apellido_materno = data['apellido_materno']
        if 'rol' in data: usuario.rol = data['rol']
        if 'telefono' in data: usuario.telefono = data['telefono']
        if 'correo' in data: usuario.correo = data['correo']
        if 'estatus' in data: usuario.estatus = data['estatus']
        if 'contraseña' in data and data['contraseña']:
            usuario.contraseña = generate_password_hash(data['contraseña'])
            
        db.session.commit()
        return jsonify({"status": "success", "message": "Usuario actualizado", "user": usuario.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@auth_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@admin_required
def delete_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
        
    try:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"status": "success", "message": "Usuario eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
