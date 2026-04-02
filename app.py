from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
import smtplib
from email.mime.text import MIMEText
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql
from datetime import timedelta
from functools import wraps  #para usar decoradores
from models import db, Usuario, Equipo, Periferico, Especificacion

#----------------------------------------------------
#driver para conectar Python con MySQL
pymysql.install_as_MySQLdb()
#----------------------------------------------------

#----------------------------------------------------
#inicializacion de la aplicacion
app = Flask(__name__)
#----------------------------------------------------

#----------------------------------------------------
#permitimos el acceso a la API desde el frontend para pruebas
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "https://exper-track.vercel.app"])
#----------------------------------------------------

#----------------------------------------------------
#configuracion para la bd en AWS RDS
DB_USER = "admin"
DB_PASS = "ResidenciasH2026*"
DB_HOST = "bd-resi.cixqu4s6y0t3.us-east-1.rds.amazonaws.com"
DB_NAME = "expertrack"
#----------------------------------------------------

#----------------------------------------------------
#construcción de la URI de conexión
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#----------------------------------------------------

#----------------------------------------------------
#configuracion para el token JWT 
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2) #configuramos la duracion del token
app.config['JWT_SECRET_KEY'] = 'qJTJ%_(7(t(FW2ggS5X8#h!1ftm!i+' #clave secreta para firmar el token
app.config['JWT_TOKEN_LOCATION'] = ['cookies'] #guardamos el token en cookies
app.config['JWT_COOKIE_SECURE'] = True  #solo enviar por HTTPS (necesario en producción)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False #proteccion contra ataques CSRF
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_SAMESITE'] = 'None' #necesario si Vercel y AWS estan en dominios distintos (LAX PARA LOCAL por ahora)
jwt = JWTManager(app) #inicializamos el JWT
db.init_app(app) #inicializamos la base de datos
#----------------------------------------------------

#----------------------------------------------------
#decorador para restringir acceso a administradores
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
#----------------------------------------------------

#----------------------------------------------------
#configuracion de correo
SMTP_SERVER = "smtp.gmail.com" #servidor de correo
SMTP_PORT = 587 #puerto de correo
SMTP_USER = "expertrack2026@outlook.com" #correo de envio
SMTP_PASSWORD = "ExperTrack*" #contraseña del correo
#----------------------------------------------------

#----------------------------------------------------
#funcion para enviar correos, recibe el destinatario y el enlace para recuperar la contraseña
def enviar_correo_recuperacion(destinatario, enlace):
    msg = MIMEText(f"Haz clic en el siguiente enlace para recuperar tu contraseña:\n\n{enlace}")
    msg['Subject'] = 'Recuperación de Contraseña - ExperTrack'
    msg['From'] = SMTP_USER
    msg['To'] = destinatario

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT) #iniciamos la conexion con el servidor
        server.starttls() #iniciamos la conexion segura
        server.login(SMTP_USER, SMTP_PASSWORD) #iniciamos sesion
        server.sendmail(SMTP_USER, destinatario, msg.as_string()) #enviamos el correo
        server.quit() #cerramos la conexion
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False
#----------------------------------------------------

#----------------------------------------------------
#endpoint para iniciar sesion, recibe el correo y la contraseña
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('correo')
    password = data.get('contraseña')

    #se busca el usuario usando el modelo
    user = Usuario.query.filter_by(correo=email).first()

    if user and check_password_hash(user.contraseña, password):
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
#----------------------------------------------------

#----------------------------------------------------
#verificar conexion a la bd en aws
@app.route('/check-connection-bd')
def check_connection():
    try:
        db.session.execute(db.text('SELECT 1')) #ejecutamos una consulta simple para verificar la conexion
        return jsonify({
            "status": "success",
            "message": "¡Conexión establecida con AWS RDS!",
            "database": DB_NAME,
            "host": DB_HOST
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "No se pudo conectar a la base de datos",
            "error_detail": str(e)
        }), 500
#----------------------------------------------------

#----------------------------------------------------
#endpoint para registrar usuarios, recibe el nombre, apellido paterno, apellido materno, rol, telefono, correo y contraseña
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    return crear_usuario_logica(data)

def crear_usuario_logica(data):
    #primero verificamos si el correo ya existe
    existe = Usuario.query.filter_by(correo=data.get('correo')).first()
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
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Usuario creado exitosamente",
            "user": nuevo_usuario.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback() #si algo falla, cancelamos la operacion
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500
#----------------------------------------------------

#----------------------------------------------------
#endpoint para obtener todos los usuarios
@app.route('/usuarios', methods=['GET'])
#@admin_required #solo los administradores pueden acceder a esta ruta
def get_usuarios():
    usuarios = Usuario.query.all() #obtenemos todos los usuarios
    return jsonify({
        "status": "success",
        "users": [u.to_dict() for u in usuarios] #convertimos los usuarios a diccionario
    }), 200
#----------------------------------------------------

#----------------------------------------------------
#endpoint para obtener un usuario mediante su id
@app.route('/usuarios/<int:id>', methods=['GET'])
@admin_required #solo los administradores pueden acceder a este endpoint
def get_usuario(id):
    usuario = Usuario.query.get(id) #obtenemos el usuario por id
    if not usuario:
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
#----------------------------------------------------

#----------------------------------------------------
#endpoint para agregar un usuario mediante el rol de administrador 
@app.route('/usuarios', methods=['POST'])
#@admin_required #solo los administradores pueden acceder a este endpoint, reutiliza la logica de registro
def admin_add_user():
    data = request.json
    return crear_usuario_logica(data)
#----------------------------------------------------

#----------------------------------------------------
#endpoint para actualizar un usuario mediante su id
@app.route('/usuarios/<int:id>', methods=['PUT'])
#@admin_required #solo los administradores pueden acceder a este endpoint
def update_usuario(id):
    usuario = Usuario.query.get(id) #obtenemos el usuario por id
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    
    data = request.json
    
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

        db.session.commit() #guardamos los cambios
        return jsonify({
            "status": "success",
            "message": "Usuario actualizado correctamente",
            "user": usuario.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback() #si algo falla, cancelamos la operacion
        return jsonify({"status": "error", "message": str(e)}), 500
#----------------------------------------------------

#----------------------------------------------------
#endpoint para eliminar un usuario mediante su id
@app.route('/usuarios/<int:id>', methods=['DELETE'])
#@admin_required #solo los administradores pueden acceder a este endpoint
def delete_usuario(id):
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
#----------------------------------------------------

#----------------------------------------------------
#endpoint para recuperar la contraseña, recibe el correo y envia un enlace para restablecer la contraseña
@app.route('/recuperar-password', methods=['POST'])
def recuperar_password():
    data = request.json
    email = data.get('correo')
    
    if not email:
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
#----------------------------------------------------

#----------------------------------------------------
#--- ENDPOINTS DE INVENTARIO (EQUIPOS) ---

@app.route('/equipos', methods=['POST'])
@jwt_required()
def create_equipo():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    
    data = request.json
    
    # Usuario Solicitante solo puede crear su propio equipo ("Alta Básica")
    # Administrador/Técnico pueden asignar a cualquier usuario
    id_propietario = usuario.id_usuario
    if usuario.rol in ['Administrador', 'Técnico'] and 'id_usuario' in data:
        id_propietario = data['id_usuario']

    try:
        # 1. Crear el Equipo
        nuevo_equipo = Equipo(
            id_usuario=id_propietario,
            tipo_equipo=data.get('tipo_equipo'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            numero_serie=data.get('numero_serie'),
            codigo_inventario=data.get('codigo_inventario'),
            area=data.get('area'),
            ubicacion=data.get('ubicacion'),
            fecha_adquisicion=data.get('fecha_adquisicion'),
            en_garantia=data.get('en_garantia', False)
        )
        db.session.add(nuevo_equipo)
        db.session.flush() # Para obtener el id_equipo antes del commit

        # 2. Agregar Periféricos (si los técnicos/admins los envían)
        if usuario.rol != 'Usuario Solicitante' and 'perifericos' in data:
            for p in data['perifericos']:
                nuevo_p = Periferico(
                    id_equipo=nuevo_equipo.id_equipo,
                    tipo=p.get('tipo'),
                    marca=p.get('marca'),
                    numero_serie=p.get('numero_serie'),
                    id_inventario_interno=p.get('id_inventario_interno')
                )
                db.session.add(nuevo_p)

        # 3. Agregar Especificación (Solo si no es Usuario Solicitante)
        if usuario.rol != 'Usuario Solicitante' and 'especificaciones' in data:
            specs = data['especificaciones']
            nueva_spec = Especificacion(
                id_equipo=nuevo_equipo.id_equipo,
                sistema_operativo=specs.get('sistema_operativo'),
                procesador=specs.get('procesador'),
                ram=specs.get('ram'),
                tipo_ram=specs.get('tipo_ram'),
                almacenamiento=specs.get('almacenamiento'),
                almacenamiento_tipo=specs.get('almacenamiento_tipo'),
                es_actual=True
            )
            db.session.add(nueva_spec)

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Equipo registrado correctamente",
            "id_equipo": nuevo_equipo.id_equipo
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/equipos', methods=['GET'])
@jwt_required()
def get_equipos():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    
    # Filtrado por rol
    query = db.session.query(Equipo, Usuario.nombre.label('dueño')).join(Usuario, Equipo.id_usuario == Usuario.id_usuario)
    
    if usuario.rol == 'Usuario Solicitante':
        query = query.filter(Equipo.id_usuario == usuario.id_usuario)
    
    resultados = query.all()
    
    lista_equipos = []
    for eq, dueño in resultados:
        d = eq.to_dict()
        d['dueño'] = dueño
        lista_equipos.append(d)
        
    return jsonify({
        "status": "success",
        "equipos": lista_equipos
    }), 200

@app.route('/equipos/<int:id>', methods=['GET'])
@jwt_required()
def get_equipo_detalle(id):
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    
    equipo = Equipo.query.get(id)
    if not equipo:
        return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
        
    # Seguridad: Usuario Solicitante solo ve sus propios equipos
    if usuario.rol == 'Usuario Solicitante' and equipo.id_usuario != usuario.id_usuario:
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
    
    # Obtener especificación actual
    spec_actual = Especificacion.query.filter_by(id_equipo=id, es_actual=True).first()
    
    return jsonify({
        "status": "success",
        "equipo": equipo.to_dict(),
        "perifericos": [p.to_dict() for p in equipo.perifericos],
        "especificacion": spec_actual.to_dict() if spec_actual else None,
        "dueño": equipo.propietario.nombre if hasattr(equipo, 'propietario') else "Desconocido"
    }), 200

@app.route('/equipos/<int:id>', methods=['PUT'])
@jwt_required()
def update_equipo(id):
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    
    if usuario.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No tienes permisos para editar equipos"}), 403
        
    equipo = Equipo.query.get(id)
    if not equipo:
        return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
        
    data = request.json
    
    try:
        # 1. Actualizar datos básicos
        if 'marca' in data: equipo.marca = data['marca']
        if 'modelo' in data: equipo.modelo = data['modelo']
        if 'tipo_equipo' in data: equipo.tipo_equipo = data['tipo_equipo']
        if 'numero_serie' in data: equipo.numero_serie = data['numero_serie']
        if 'codigo_inventario' in data: equipo.codigo_inventario = data['codigo_inventario']
        if 'area' in data: equipo.area = data['area']
        if 'ubicacion' in data: equipo.ubicacion = data['ubicacion']
        if 'estado_operativo' in data: equipo.estado_operativo = data['estado_operativo']
        if 'en_garantia' in data: equipo.en_garantia = data['en_garantia']

        # 2. Lógica de Versionado de Especificaciones
        if 'especificaciones' in data:
            new_specs_data = data['especificaciones']
            
            # Buscar la especificación actual
            current_spec = Especificacion.query.filter_by(id_equipo=id, es_actual=True).first()
            
            # Solo crear nueva versión si el registro actual es diferente o si no existe
            should_create_new = False
            if not current_spec:
                should_create_new = True
            else:
                # Verificar si algo cambió (omitiendo id y metadatos)
                fields_to_check = ['sistema_operativo', 'procesador', 'ram', 'tipo_ram', 'almacenamiento', 'almacenamiento_tipo']
                for field in fields_to_check:
                    if new_specs_data.get(field) != getattr(current_spec, field):
                        should_create_new = True
                        break
            
            if should_create_new:
                if current_spec:
                    current_spec.es_actual = False # Versionamos la anterior
                
                # Creamos el nuevo registro
                nueva_version = Especificacion(
                    id_equipo=id,
                    sistema_operativo=new_specs_data.get('sistema_operativo'),
                    procesador=new_specs_data.get('procesador'),
                    ram=new_specs_data.get('ram'),
                    tipo_ram=new_specs_data.get('tipo_ram'),
                    almacenamiento=new_specs_data.get('almacenamiento'),
                    almacenamiento_tipo=new_specs_data.get('almacenamiento_tipo'),
                    es_actual=True
                )
                db.session.add(nueva_version)

        db.session.commit()
        return jsonify({"status": "success", "message": "Equipo y especificaciones actualizados"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/equipos/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_equipo(id):
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    
    if usuario.rol != 'Administrador':
        return jsonify({"status": "error", "message": "Solo el administrador puede eliminar equipos"}), 403
        
    equipo = Equipo.query.get(id)
    if not equipo:
        return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
        
    try:
        # El cascade configurado en models.py se encargará de Perifericos y Especificaciones
        db.session.delete(equipo)
        db.session.commit()
        return jsonify({"status": "success", "message": "Equipo y todo su historial eliminados correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
#----------------------------------------------------

if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=5000, debug=True)