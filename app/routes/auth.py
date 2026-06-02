import re
from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, decode_token, unset_jwt_cookies
from datetime import datetime, timedelta
from ..models import db, Usuario
from ..services.email_service import enviar_correo_recuperacion
from ..utils.helpers import admin_required

auth_bp = Blueprint('auth', __name__)

#endpoint para iniciar sesion, recibe el correo y la contraseña
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json #obtenemos los datos en json
    email = data.get('correo') #obtenemos el correo
    password = data.get('contraseña') #obtenemos la contraseña

    #se busca el usuario usando el modelo
    user = Usuario.query.filter_by(correo=email).first() #buscamos el usuario por correo

    if user and check_password_hash(user.contraseña, password): #verificamos que el usuario exista y la contraseña sea correcta
        access_token = create_access_token(identity=str(user.id_usuario)) #creamos el token
        response = make_response(jsonify({
            "status": "success",
            "message": f"Bienvenid@ {user.nombre}",
            "user": user.to_dict()
        }))

        #guardamos el token en una galleta
        set_access_cookies(response, access_token)        
        return response, 200

    #si no se encuentra el usuario o la contraseña es incorrecta
    return jsonify({"status": "error", "message": "Correo o contraseña incorrectos"}), 401
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para registrar usuarios; recibe el nombre, apellido paterno, apellido materno, rol, telefono, correo y contraseña
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json #obtenemos los datos en json
    return crear_usuario_logica(data) #llamamos a la funcion que contiene la logica

#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para obtener todos los usuarios
@auth_bp.route('/usuarios', methods=['GET'])
@jwt_required()
def get_usuarios():
    usuarios = Usuario.query.all() #obtenemos todos los usuarios
    return jsonify({
        "status": "success",
        "users": [u.to_dict() for u in usuarios] #convertimos los usuarios a diccionario
    }), 200
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para obtener un usuario mediante su id
@auth_bp.route('/usuarios/<int:id>', methods=['GET'])
@jwt_required()
def get_usuario(id):
    usuario = Usuario.query.get(id) #obtenemos el usuario por id
    if not usuario: #si no se encuentra el usuario 
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    
    #retornamos el usuario en formato diccionario
    return jsonify({
        "status": "success",
        "user": {
            **usuario.to_dict(),
            "apellido_paterno": usuario.apellido_paterno,
            "apellido_materno": usuario.apellido_materno,
            "telefono": usuario.telefono,
            "estatus": usuario.estatus,
            "fecha_registro": usuario.fecha_registro.isoformat() if usuario.fecha_registro else None
        }
    }), 200
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para agregar un usuario mediante el rol de administrador 
@auth_bp.route('/usuarios', methods=['POST'])
@admin_required #solo los administradores pueden acceder a este endpoint, reutiliza la logica de registro
@jwt_required() #solo los usuarios autenticados pueden acceder a esta ruta
def admin_add_user():
    data = request.json #obtenemos los datos en json
    return crear_usuario_logica(data) #llamamos a la funcion que contiene la logica

#-------------------------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------------------------
#endpoint para actualizar un usuario mediante su id
@auth_bp.route('/usuarios/<int:id>', methods=['PUT'])
@jwt_required() #solo los usuarios autenticados pueden acceder a esta ruta
def update_usuario(id):
    usuario = Usuario.query.get(id) #obtenemos el usuario por id
    if not usuario: #si no se encuentra el usuario
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    
    data = request.json #obtenemos los datos en json
    
    # Detectar si el usuario actual se está quitando el rol de Administrador
    current_user_id = get_jwt_identity()
    is_self = (current_user_id and int(current_user_id) == id)
    se_quito_admin = False

    # Si se intenta cambiar el rol de un administrador a otro rol
    if 'rol' in data and data['rol'] != 'Administrador' and usuario.rol == 'Administrador':
        admins_count = Usuario.query.filter_by(rol='Administrador').count()
        if admins_count <= 1:
            return jsonify({
                "status": "error",
                "message": "No se puede cambiar el rol del único administrador del sistema. Debe quedar al menos un administrador."
            }), 400
        if is_self:
            se_quito_admin = True

    try:
        #actualizamos los datos del usuario si se envian
        if 'nombre' in data: usuario.nombre = data['nombre']
        if 'apellido_paterno' in data: usuario.apellido_paterno = data['apellido_paterno']
        if 'apellido_materno' in data: usuario.apellido_materno = data['apellido_materno']
        if 'rol' in data: usuario.rol = data['rol']
        if 'telefono' in data: usuario.telefono = data['telefono']
        if 'correo' in data: usuario.correo = data['correo']
        if 'estatus' in data: usuario.estatus = data['estatus']
        
        #si se modifica la contraseña, se hashea por seguridad
        if 'contraseña' in data: 
            usuario.contraseña = generate_password_hash(data['contraseña'])

        db.session.commit() #guardamos los cambios en la base de datos
        
        response_data = {
            "status": "success",
            "message": "Usuario actualizado correctamente",
            "user": usuario.to_dict()
        }
        
        # Si el administrador se quitó el privilegio a sí mismo, destruimos las cookies de sesión
        if se_quito_admin:
            response_data["session_terminated"] = True
            response_data["message"] = "Rol actualizado correctamente. Tu sesión ha sido cerrada debido al cambio de privilegios."
            response = make_response(jsonify(response_data), 200)
            unset_jwt_cookies(response)
            return response

        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback() #si algo falla, cancelamos la operacion con un rollback
        return jsonify({"status": "error", "message": str(e)}), 500


#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para eliminar un usuario mediante su id
@auth_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@admin_required #solo los administradores pueden acceder a este endpoint
@jwt_required() #solo los usuarios autenticados pueden acceder a esta ruta
def delete_usuario(id):
    # Evitar que el usuario administrador se elimine a sí mismo
    current_user_id = get_jwt_identity()
    if current_user_id and int(current_user_id) == id:
        return jsonify({"status": "error", "message": "No puedes eliminar tu propia cuenta"}), 400

    usuario = Usuario.query.get(id) #obtenemos el usuario por id
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    
    try:
        db.session.delete(usuario) #eliminamos el usuario
        db.session.commit() #guardamos los cambios
        return jsonify({
            "status": "success",
            "message": "Usuario eliminado físicamente de la base de datos"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
#-------------------------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------------------------
##endpoint para recuperar la contraseña, recibe el correo y envia un enlace para restablecer la contraseña
@auth_bp.route('/recuperar-password', methods=['POST'])
def recuperar_password():
    data = request.json #obtenemos los datos en json
    email = data.get('correo') #obtenemos el correo
    
    if not email: #si no se llega un correo
        return jsonify({"status": "error", "message": "Por favor ingresa un correo electrónico"}), 400

    #primero buscamos si el usuario existe
    user = Usuario.query.filter_by(correo=email).first()
    if not user:
        return jsonify({"status": "error", "message": "El correo no está registrado"}), 404
        
    #generamos un token con expiracion de 15 minutos
    reset_token = create_access_token(identity=str(user.id_usuario), expires_delta=timedelta(minutes=15))
    
    #construimos el enlace
    enlace = f"https://exper-track.vercel.app/reset-password?token={reset_token}"
    
    #enviamos el correo
    if enviar_correo_recuperacion(email, enlace):
        return jsonify({"status": "success", "message": "Se ha enviado un correo con las instrucciones"}), 200
    else:
        return jsonify({"status": "error", "message": "Hubo un problema al intentar enviar el correo. Revisa tus credenciales SMTP."}), 500

#-------------------------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------------------------
#endpoint para restablecer la contraseña, verifica el token y actualiza la contraseña
@auth_bp.route('/restablecer-password', methods=['POST'])
def restablecer_password():
    data = request.json #obtenemos los datos en json
    token = data.get('token') #obtenemos el token
    nueva_password = data.get('nueva_contraseña') #obtenemos la nueva contraseña
    
    if not token or not nueva_password: #si no se llega un token o una nueva contraseña
        return jsonify({"status": "error", "message": "Faltan datos requeridos (token o nueva_contraseña)"}), 400
        
    # Validación de complejidad de la contraseña
    if len(nueva_password) < 8:
        return jsonify({
            "status": "error",
            "message": "La contraseña debe tener al menos 8 caracteres"
        }), 400
    if not re.search(r"[A-Z]", nueva_password):
        return jsonify({
            "status": "error",
            "message": "La contraseña debe contener al menos una letra mayúscula"
        }), 400
    if not re.search(r"\d", nueva_password):
        return jsonify({
            "status": "error",
            "message": "La contraseña debe contener al menos un número"
        }), 400
    if not re.search(r"[^a-zA-Z0-9]", nueva_password):
        return jsonify({
            "status": "error",
            "message": "La contraseña debe contener al menos un carácter especial (ej: * . @ $ ! % &)"
        }), 400
        
    try:
        #decodificamos el token (si ya expiro los 15 min, lanzara excepcion automaticamente)
        decoded_token = decode_token(token)
        usuario_id = decoded_token['sub'] #obtenemos el id del usuario del token
        
        user = Usuario.query.get(usuario_id) #buscamos al usuario
        if not user:
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
            
        #hasheamos y guardamos la nueva contraseña
        user.contraseña = generate_password_hash(nueva_password)
        db.session.commit() #guardamos los cambios
        
        return jsonify({"status": "success", "message": "Contraseña actualizada exitosamente"}), 200
        
    except Exception as e:
        #captura errores como token expirado o firma invalida
        return jsonify({"status": "error", "message": "El enlace es inválido o ha expirado"}), 401


#------------------------------------------------------------------------------------------------------------
#logica para crear usuarios
def crear_usuario_logica(data):
    contrasena = data.get('contraseña')
    if not contrasena:
        return jsonify({
            "status": "error",
            "message": "La contraseña es requerida"
        }), 400

    # Validación de complejidad de la contraseña
    if len(contrasena) < 8:
        return jsonify({
            "status": "error",
            "message": "La contraseña debe tener al menos 8 caracteres"
        }), 400
    if not re.search(r"[A-Z]", contrasena):
        return jsonify({
            "status": "error",
            "message": "La contraseña debe contener al menos una letra mayúscula"
        }), 400
    if not re.search(r"\d", contrasena):
        return jsonify({
            "status": "error",
            "message": "La contraseña debe contener al menos un número"
        }), 400
    if not re.search(r"[^a-zA-Z0-9]", contrasena):
        return jsonify({
            "status": "error",
            "message": "La contraseña debe contener al menos un carácter especial (ej: * . @ $ ! % &)"
        }), 400

    #primero verificamos si el correo ya existe
    existe = Usuario.query.filter_by(correo=data.get('correo')).first() #buscamos el usuario por correo
    if existe:
        return jsonify({
            "status": "error", 
            "message": "El correo ya está registrado"
        }), 400

    try:
        #creamos una nueva instancia del modelo
        nuevo_usuario = Usuario(
            nombre=data.get('nombre'),
            apellido_paterno=data.get('apellido_paterno'),
            apellido_materno=data.get('apellido_materno'),
            rol=data.get('rol'), 
            telefono=data.get('telefono'),
            correo=data.get('correo'),
            contraseña=generate_password_hash(data.get('contraseña')) #encriptamos la contraseña
        )

        #guardamos el usuario en la base de datos
        db.session.add(nuevo_usuario)
        db.session.commit() #confirmamos la transaccion

        return jsonify({
            "status": "success",
            "message": "Usuario creado exitosamente",
            "user": nuevo_usuario.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback() #si algo falla, cancelamos la operacion con un rollback
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500
#------------------------------------------------------------------------------------------------------------