import os
from flask import Flask, request, jsonify, make_response, send_file
import io
from fpdf import FPDF
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, decode_token
import smtplib
from email.mime.text import MIMEText
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql
from datetime import timedelta, datetime
from sqlalchemy import func
from functools import wraps  #para usar decoradores
from models import db, Usuario, Equipo, Periferico, Especificacion, CategoriaHecho, SintomaHecho, FallaHecho, Evento, Diagnostico, Mantenimiento, Alerta
from pyswip import Prolog
from flask_apscheduler import APScheduler

#---------------------------------------------------------
#----------Prolog ----------------
prolog = Prolog() #inicializamos el motor de prolog

#definimos la ruta de las reglas de prolog
base_path = os.path.dirname(__file__) #obtenemos la ruta del directorio actual
path_reglas = os.path.join(base_path, "motor_prolog", "reglas.pl").replace("\\", "/") #obtenemos la ruta de las reglas
path_hechos = os.path.join(base_path, "motor_prolog", "hechos.pl").replace("\\", "/") #ruta del archivo de hechos
prolog.consult(path_reglas) #cargamos las reglas en el motor de prolog

#---------------------------------------------------------

#----------------------------------------------------
#driver para conectar Python con MySQL
pymysql.install_as_MySQLdb()
#----------------------------------------------------

#----------------------------------------------------
#inicializacion de la aplicacion
app = Flask(__name__)

#configuración del Planificador de Tareas (Scheduler)
scheduler = APScheduler()
app.config['SCHEDULER_API_ENABLED'] = True
#----------------------------------------------------

#----------------------------------------------------
#permitimos el acceso a la API desde el frontend para pruebas
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "https://exper-track.vercel.app"])
#----------------------------------------------------

#----------------------------------------------------
#configuracion para la bd en AWS RDS
DB_USER = "admin" #usuario de la bd
DB_PASS = "ResidenciasH2026*" #contraseña de la bd
DB_HOST = "bd-resi.cixqu4s6y0t3.us-east-1.rds.amazonaws.com" #host de la bd
DB_NAME = "expertrack" #nombre de la bd
#----------------------------------------------------

#----------------------------------------------------
#construcción de la URI de conexión
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}' #URI de conexión
app.config['SQLALCHEMY_BINDS'] = {
    'hechos': f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/hechos_se'
} #URI de conexión para hechos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #desactiva el seguimiento de modificaciones (sirve para ahorrar recursos)
#----------------------------------------------------

#----------------------------------------------------
#configuracion para el token JWT 
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2) #configuramos la duracion del token
app.config['JWT_SECRET_KEY'] = 'qJTJ%_(7(t(FW2ggS5X8#h!1ftm!i+' #clave secreta para firmar el token
app.config['JWT_TOKEN_LOCATION'] = ['cookies'] #guardamos el token en cookies
app.config['JWT_COOKIE_SECURE'] = True  #solo enviar por HTTPS (necesario ya desplegado)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False #desactivamos la proteccion CSRF (necesario si Vercel y AWS estan en dominios distintos)
app.config['JWT_ACCESS_COOKIE_PATH'] = '/' #ruta de la cookie
app.config['JWT_COOKIE_SAMESITE'] = 'None' #necesario si Vercel y AWS estan en dominios distintos (NONE para desplegado, LAX para local)
jwt = JWTManager(app) #inicializamos el JWT
db.init_app(app) #inicializamos la base de datos
scheduler.init_app(app) #inicializamos el scheduler
#----------------------------------------------------

#----------------------------------------------------
#Endpoint para verificar conexion a la bd en aws
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
#configuracion de correo (Gmail)
SMTP_SERVER = "smtp.gmail.com" #servidor de correo para Gmail
SMTP_PORT = 587 #puerto de correo
SMTP_USER = "trackexper@gmail.com" #correo de envio
SMTP_PASSWORD = "ehvxwcvwcveccqae" #contraseña de aplicación
#----------------------------------------------------

#----------------------------------------------------
#funcion para enviar correos, recibe el destinatario y el enlace para recuperar la contraseña
def enviar_correo_recuperacion(destinatario, enlace):
    msg = MIMEText(f"Haz clic en el siguiente enlace para recuperar tu contraseña:\n\n{enlace}") #creamos el mensaje
    msg['Subject'] = 'Recuperación de Contraseña - ExperTrack' #asunto del correo
    msg['From'] = SMTP_USER #correo de envio
    msg['To'] = destinatario #correo del destinatario

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

#---------------------------------------------------------------
#--------- Endpoints para Modulo de Gestión de Usuarios ---------

#endpoint para iniciar sesion, recibe el correo y la contraseña
@app.route('/login', methods=['POST'])
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
#----------------------------------------------------


#----------------------------------------------------
#endpoint para registrar usuarios; recibe el nombre, apellido paterno, apellido materno, rol, telefono, correo y contraseña
@app.route('/register', methods=['POST'])
def register():
    data = request.json #obtenemos los datos en json
    return crear_usuario_logica(data) #llamamos a la funcion que contiene la logica

def crear_usuario_logica(data):
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
#----------------------------------------------------

#----------------------------------------------------
#endpoint para obtener todos los usuarios
@app.route('/usuarios', methods=['GET'])
@jwt_required() #solo los usuarios autenticados pueden acceder a esta ruta
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
@jwt_required() #solo los usuarios autenticados pueden acceder a esta ruta
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
#----------------------------------------------------

#----------------------------------------------------
#endpoint para agregar un usuario mediante el rol de administrador 
@app.route('/usuarios', methods=['POST'])
@admin_required #solo los administradores pueden acceder a este endpoint, reutiliza la logica de registro
@jwt_required() #solo los usuarios autenticados pueden acceder a esta ruta
def admin_add_user():
    data = request.json #obtenemos los datos en json
    return crear_usuario_logica(data) #llamamos a la funcion que contiene la logica
#----------------------------------------------------

#----------------------------------------------------
#endpoint para actualizar un usuario mediante su id
@app.route('/usuarios/<int:id>', methods=['PUT'])
@jwt_required() #solo los usuarios autenticados pueden acceder a esta ruta
def update_usuario(id):
    usuario = Usuario.query.get(id) #obtenemos el usuario por id
    if not usuario: #si no se encuentra el usuario
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    
    data = request.json #obtenemos los datos en json
    
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
        return jsonify({
            "status": "success",
            "message": "Usuario actualizado correctamente",
            "user": usuario.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback() #si algo falla, cancelamos la operacion con un rollback
        return jsonify({"status": "error", "message": str(e)}), 500
#----------------------------------------------------

#----------------------------------------------------
#endpoint para eliminar un usuario mediante su id
@app.route('/usuarios/<int:id>', methods=['DELETE'])
@admin_required #solo los administradores pueden acceder a este endpoint
@jwt_required() #solo los usuarios autenticados pueden acceder a esta ruta
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
#----------------------------------------------------

#----------------------------------------------------
#endpoint para restablecer la contraseña, verifica el token y actualiza la contraseña
@app.route('/restablecer-password', methods=['POST'])
def restablecer_password():
    data = request.json #obtenemos los datos en json
    token = data.get('token') #obtenemos el token
    nueva_password = data.get('nueva_contraseña') #obtenemos la nueva contraseña
    
    if not token or not nueva_password: #si no se llega un token o una nueva contraseña
        return jsonify({"status": "error", "message": "Faltan datos requeridos (token o nueva_contraseña)"}), 400
        
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
#----------------------------------------------------

#--------------------------------------------------------------------------------------------------
#------------ Endpoints del Modulo de Gestión de Activos (EQUIPOS) ----------------------

#----------------------------------------------
#endpoint para crear un equipo
@app.route('/equipos', methods=['POST'])
@jwt_required()
def create_equipo():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    
    data = request.json #obtenemos los datos del equipo
    
    #Usuario Solicitante solo puede crear su propio equipo ("Alta Básica")
    #Administrador/Técnico pueden asignar a cualquier usuario
    id_propietario = usuario.id_usuario
    if usuario.rol in ['Administrador', 'Técnico'] and 'id_usuario' in data:
        id_propietario = data['id_usuario']

    try:
        #crear el Equipo 
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
        db.session.add(nuevo_equipo) #agregamos el equipo
        db.session.flush() #obtenemos el id_equipo antes del commit

        #agregar Periféricos (si los técnicos/admins los mandan)
        if usuario.rol != 'Usuario Solicitante' and 'perifericos' in data:
            for p in data['perifericos']: #recorremos los perifericos
                nuevo_p = Periferico(
                    id_equipo=nuevo_equipo.id_equipo,
                    tipo=p.get('tipo'),
                    marca=p.get('marca'),
                    numero_serie=p.get('numero_serie'),
                    id_inventario_interno=p.get('id_inventario_interno')
                )
                db.session.add(nuevo_p) #agregamos el periferico

        #agregar Especificación (Solo si no es Usuario Solicitante)
        if usuario.rol != 'Usuario Solicitante' and 'especificaciones' in data:
            specs = data['especificaciones'] #obtenemos las especificaciones
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
            db.session.add(nueva_spec) #agregamos la especificación

        db.session.commit() #guardamos los cambios
        return jsonify({
            "status": "success",
            "message": "Equipo registrado correctamente",
            "id_equipo": nuevo_equipo.id_equipo
        }), 201

    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay un error
        return jsonify({"status": "error", "message": str(e)}), 500
#----------------------------------------------------

#----------------------------------------------------
#endpoint para obtener los equipos registrados
@app.route('/equipos', methods=['GET'])
@jwt_required() #solo usuarios autenticados
def get_equipos():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #filtrado por rol
    query = db.session.query(Equipo, Usuario.nombre.label('dueño')).join(Usuario, Equipo.id_usuario == Usuario.id_usuario)
    
    if usuario.rol == 'Usuario Solicitante': #si el usuario es solicitante
        query = query.filter(Equipo.id_usuario == usuario.id_usuario) #solo muestra sus equipos
    
    resultados = query.all() #obtenemos todos los equipos
     
    lista_equipos = [] #creamos una lista para guardar los equipos
    for eq, dueño in resultados: #recorremos los equipos
        d = eq.to_dict() #convertimos el equipo a diccionario
        d['dueño'] = dueño #agregamos el dueño
        lista_equipos.append(d) #agregamos el equipo a la lista
        
    return jsonify({
        "status": "success",
        "equipos": lista_equipos
    }), 200
#----------------------------------------------------

#----------------------------------------------------
#endpoint para obtener los detalles de un equipo
@app.route('/equipos/<int:id>', methods=['GET'])
@jwt_required() #solo usuarios autenticados
def get_equipo_detalle(id):
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    equipo = Equipo.query.get(id) #obtenemos el equipo
    if not equipo:
        return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
        
    #Usuario Solicitante solo ve sus propios equipos
    if usuario.rol == 'Usuario Solicitante' and equipo.id_usuario != usuario.id_usuario:
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
    
    #obtenemos la especificación actual
    spec_actual = Especificacion.query.filter_by(id_equipo=id, es_actual=True).first()
    
    return jsonify({
        "status": "success",
        "equipo": equipo.to_dict(), #convertimos el equipo a diccionario
        "perifericos": [p.to_dict() for p in equipo.perifericos], #convertimos los perifericos a diccionario    
        "especificacion": spec_actual.to_dict() if spec_actual else None, #convertimos la especificación a diccionario
        "dueño": equipo.propietario.nombre if hasattr(equipo, 'propietario') else "Desconocido" #obtenemos el dueño
    }), 200
#----------------------------------------------------

#----------------------------------------------------
#endpoint para actualizar un equipo
@app.route('/equipos/<int:id>', methods=['PUT'])
@jwt_required() #solo usuarios autenticados
def update_equipo(id):
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    if usuario.rol not in ['Administrador', 'Técnico']: #si el usuario no es administrador o técnico
        return jsonify({"status": "error", "message": "No tienes permisos para editar equipos"}), 403
        
    equipo = Equipo.query.get(id) #obtenemos el equipo
    if not equipo: #si el equipo no existe
        return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
        
    data = request.json #obtenemos los datos del equipo
    
    try:
        # 1. Actualizar datos basicos
        if 'id_usuario' in data: equipo.id_usuario = data['id_usuario']        
        if 'marca' in data: equipo.marca = data['marca']
        if 'modelo' in data: equipo.modelo = data['modelo']
        if 'tipo_equipo' in data: equipo.tipo_equipo = data['tipo_equipo']
        if 'numero_serie' in data: equipo.numero_serie = data['numero_serie']
        if 'codigo_inventario' in data: equipo.codigo_inventario = data['codigo_inventario']
        if 'area' in data: equipo.area = data['area']
        if 'ubicacion' in data: equipo.ubicacion = data['ubicacion']
        if 'estado_operativo' in data: equipo.estado_operativo = data['estado_operativo']
        if 'en_garantia' in data: equipo.en_garantia = data['en_garantia']

        # 2. Logica de Versionado de Especificaciones
        if 'especificaciones' in data: #si hay especificaciones
            new_specs_data = data['especificaciones'] #obtenemos las especificaciones
            
            #buscar la especificacion actual
            current_spec = Especificacion.query.filter_by(id_equipo=id, es_actual=True).first()
            
            #solo crear nueva version si el registro actual es diferente o si no existe
            should_create_new = False #variable para verificar si se debe crear una nueva version
            if not current_spec: #si no existe la especificacion actual
                should_create_new = True #se crea una nueva version
            else:
                #verificar si algo cambio (omitiendo id y metadatos)
                fields_to_check = ['sistema_operativo', 'procesador', 'ram', 'tipo_ram', 'almacenamiento', 'almacenamiento_tipo']
                for field in fields_to_check: #recorremos los campos
                    if new_specs_data.get(field) != getattr(current_spec, field): #si algo cambio
                        should_create_new = True #se crea una nueva version
                        break
            
            if should_create_new: #si se debe crear una nueva version
                if current_spec: #si existe la especificacion actual
                    current_spec.es_actual = False # Versionamos la anterior
                
                #creamos el nuevo registro
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
                db.session.add(nueva_version) #agregamos la nueva version

        if 'perifericos' in data: #si hay perifericos
            #borramos los perifericos actuales para reemplazarlos con la nueva lista
            Periferico.query.filter_by(id_equipo=id).delete() #borramos los perifericos actuales
            
            for p in data['perifericos']: #recorremos los perifericos
                nuevo_p = Periferico(
                    id_equipo=id,
                    tipo=p.get('tipo'),
                    marca=p.get('marca'),
                    numero_serie=p.get('numero_serie'),
                    id_inventario_interno=p.get('id_inventario_interno')
                )
                db.session.add(nuevo_p) #agregamos el nuevo periferico

        db.session.commit() #guardamos los cambios
        return jsonify({"status": "success", "message": "Equipo y especificaciones actualizados"}), 200

    except Exception as e:
        db.session.rollback() #deshacemos los cambios con un rollback si hay un error
        return jsonify({"status": "error", "message": str(e)}), 500
#----------------------------------------------------

#----------------------------------------------------
#endpoint para eliminar un equipo
@app.route('/equipos/<int:id>', methods=['DELETE'])
@jwt_required() #solo usuarios autenticados
@admin_required #solo administradores
def delete_equipo(id):
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    if usuario.rol != 'Administrador': #si el usuario no es administrador
        return jsonify({"status": "error", "message": "Solo el administrador puede eliminar equipos"}), 403
        
    equipo = Equipo.query.get(id) #obtenemos el equipo
    if not equipo: #si el equipo no existe
        return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
        
    try:
        #el cascade configurado en models.py se encargará de Perifericos y Especificaciones
        db.session.delete(equipo) #eliminamos el equipo
        db.session.commit() #guardamos los cambios
        return jsonify({"status": "success", "message": "Equipo y todo su historial eliminados correctamente"}), 200
    except Exception as e:
        db.session.rollback() #deshacemos los cambios con un rollback si hay un error
        return jsonify({"status": "error", "message": str(e)}), 500
#----------------------------------------------------

#------------------------------------------------------------------------------
#clase para generar pdf de inventario general
class PDF_Inventario(FPDF):
    def header(self):
        #1. Logos institucionales 
        try:
            sep_path = os.path.join(base_path, 'static', 'logos', 'sep.png')
            tecnm_path = os.path.join(base_path, 'static', 'logos', 'tecnm.jpg') 
            itl_path = os.path.join(base_path, 'static', 'logos', 'itl.png')
            exper_path = os.path.join(base_path, 'static', 'logos', 'ExperTrack.png') 
                        
            self.image(sep_path, 10, 10, 35)
            self.image(tecnm_path, 55, 10, 35)
            self.image(itl_path, 110, 8, 28)
            self.image(exper_path, 155, 10, 45)
        except Exception as e:
            print(f"Error cargando logos en Inventario: {e}")

        self.ln(35) 
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, 'INVENTARIO GENERAL DE EQUIPO TECNOLOGICO', 0, 1, 'C')
        self.set_font('Helvetica', '', 10)
        self.cell(0, 5, 'ExperTrack - Sistema de Control de Activos', 0, 1, 'C')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        fecha_gen = (datetime.utcnow() + timedelta(hours=-6)).strftime("%d/%m/%Y %H:%M")
        self.cell(60, 10, f'Generado el: {fecha_gen}', 0, 0, 'L')
        self.cell(70, 10, '(c) 2026 ExperTrack - Todos los derechos reservados', 0, 0, 'C')
        self.cell(60, 10, f'Pagina {self.page_no()}/{{nb}}', 0, 0, 'R')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#endpoint para generar el inventario en pdf
@app.route('/reporte_inventario_pdf', methods=['GET'])
@jwt_required()
def export_inventario_pdf():
    try:
        #1. verificar permisos y obtener datos del solicitante
        usuario_id = get_jwt_identity()
        usuario_gen = Usuario.query.get(usuario_id)
        if usuario_gen.rol not in ['Administrador', 'Técnico']:
            return jsonify({"status": "error", "message": "No tienes permisos para generar este reporte"}), 403

        #2. obtener todos los equipos
        equipos = Equipo.query.order_by(Equipo.codigo_inventario).all()

        #3. crear pdf
        pdf = PDF_Inventario()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        #datos del solicitante en el cuerpo
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 7, f"Reporte generado por: {usuario_gen.nombre} {usuario_gen.apellido_paterno} ({usuario_gen.rol})", 0, 1, 'L')
        pdf.ln(5)

        #encabezados de tabla
        pdf.set_fill_color(80, 75, 56)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 9)
        
        pdf.cell(35, 10, 'Cod. Inventario', 1, 0, 'C', fill=True)
        pdf.cell(25, 10, 'Tipo', 1, 0, 'C', fill=True)
        pdf.cell(50, 10, 'Marca / Modelo', 1, 0, 'C', fill=True)
        pdf.cell(50, 10, 'Area / Ubicacion', 1, 0, 'C', fill=True)
        pdf.cell(30, 10, 'Estatus', 1, 1, 'C', fill=True)

        #cuerpo de la tabla
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Helvetica', '', 8)
        
        #iterar sobre los equipos
        for e in equipos:
            marca_modelo = f"{e.marca or ''} {e.modelo or ''}"
            area_ubic = e.area or "N/A"
            
            #calculamos altura dinamica para que no se vea mas chica una celda de la otra
            lineas_marca = pdf.multi_cell(50, 6, marca_modelo, split_only=True)
            lineas_area = pdf.multi_cell(50, 6, area_ubic, split_only=True)
            max_lineas = max(len(lineas_marca), len(lineas_area))
            h = max_lineas * 6
            if h < 8: h = 8

            pdf.cell(35, h, e.codigo_inventario or "N/A", 1, 0, 'C')
            pdf.cell(25, h, e.tipo_equipo or "N/A", 1, 0, 'C')
            
            #Marca/Modelo
            curr_x, curr_y = pdf.get_x(), pdf.get_y()
            pdf.multi_cell(50, h/len(lineas_marca), marca_modelo, 1, 'C')
            pdf.set_xy(curr_x + 50, curr_y)
            
            #Area
            curr_x, curr_y = pdf.get_x(), pdf.get_y()
            pdf.multi_cell(50, h/len(lineas_area), area_ubic, 1, 'C')
            pdf.set_xy(curr_x + 50, curr_y)
            
            pdf.cell(30, h, e.estado_operativo or "N/A", 1, 1, 'C')

        #4. exportar pdf
        pdf_bytes = pdf.output()
        buffer = io.BytesIO(pdf_bytes)
        buffer.seek(0)
        
        #5. enviar archivo descargable
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Inventario_ExperTrack_{datetime.now().strftime("%Y%m%d")}.pdf'
        )

    except Exception as e:
        print(f"Error reporte inventario: {e}")
        return jsonify({"status": "error", "message": f"Error interno: {str(e)}"}), 500

#------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------
#---------- Endpoints para Modulo de Diagnostico con Sistema Experto

#----------------------------------------------
#endpoint para diagnosticar con Prolog
@app.route('/diagnosticar', methods=['POST'])
def diagnosticar():
    try:
        data = request.json #recibe los datos del frontend
        if not data:
            return jsonify({"status": "error", "mensaje": "No se recibieron datos"}), 400

        tipo = data.get('tipo') #tipo de equipo
        sintoma = data.get('sintoma') #sintoma (manifestación de falla) principal
        historial = data.get('historial', []) #historial de preguntas y respuestas

        #1. limpiamos la memoria antes de procesar
        #usamos la regla que definimos en reglas.pl
        list(prolog.query("limpiar_memoria"))

        #2. Inyectamos el historial
        for paso in historial:
            pregunta = paso['p'] #pregunta
            respuesta = paso['r'] # 'si' o 'no'
            #envolvemos el valor en comillas simples para Prolog
            prolog.assertz(f"respuesta('{pregunta}', {respuesta})")

        #3. Ejecutamos la consulta principal
        query_str = f"siguiente_paso('{tipo}', '{sintoma}', Accion, Valor)" #consulta principal
        results = list(prolog.query(query_str)) #obtenemos los resultados

        #4. Procesamos la respuesta
        if results:
            res = results[0]
            #procesamos los datos a string
            return jsonify({
                "status": "success",
                "accion": str(res['Accion']),
                "valor": str(res['Valor'])
            })
        else:
            return jsonify({
                "status": "error", 
                "mensaje": "El motor de inferencia no devolvió resultados"
            }), 404

    except Exception as e:
        print(f"Error en el diagnóstico: {e}")
        return jsonify({"status": "error", "mensaje": str(e)}), 500
#----------------------------------------------


#------------------------------------------------------------------------------
#---- Endpoints para Modulo de Mantenimiento Preventivo/Correctivo-------------

#----------------------------------------------
@app.route('/eventos', methods=['POST'])
@jwt_required() #requiere sesion iniciada
def create_evento():
    usuario_id_creador = get_jwt_identity() #id del usuario que crea el evento
    usuario_creador = Usuario.query.get(usuario_id_creador) #obtenemos el usuario
    
    data = request.json #obtenemos los datos en json
    id_equipo = data.get('id_equipo')
    
    #id final del técnico que se asignará al evento
    id_tecnico_asignado = None
    
    try:
        #1. determinamos el tecnico asignado
        if usuario_creador.rol == 'Técnico':
            #si el creador es tecnico, se lo asigna a sí mismo
            id_tecnico_asignado = usuario_id_creador
        
        elif usuario_creador.rol == 'Usuario Solicitante':
            #si es solicitante, buscamos al técnico con menos eventos abiertos (validado=False)
            tecnico_menos_ocupado = db.session.query(
                Usuario
            ).outerjoin(Evento, (Usuario.id_usuario == Evento.id_usuario) & (Evento.validado == False))\
             .filter(Usuario.rol == 'Técnico')\
             .group_by(Usuario.id_usuario)\
             .order_by(func.count(Evento.id_evento).asc(), Usuario.id_usuario.asc())\
             .first()
            
            if not tecnico_menos_ocupado:
                return jsonify({"status": "error", "message": "No hay técnicos registrados en el sistema para asignar el evento"}), 500
            
            id_tecnico_asignado = tecnico_menos_ocupado.id_usuario #obtenemos el id del técnico
        
        else:
            #Administradores u otros roles no generan eventos
            return jsonify({"status": "error", "message": "Tu rol no tiene permisos para generar eventos"}), 403

        #2. buscar el equipo para cambiar su estado
        equipo = Equipo.query.get(id_equipo)
        if not equipo:
            return jsonify({"status": "error", "message": "El equipo especificado no existe"}), 404
            
        #3. creamos el nuevo evento
        nuevo_evento = Evento(
            id_equipo=id_equipo, #equipo que se reporta
            id_usuario=id_tecnico_asignado, #técnico asignado automáticamente
            falla_reportada=data.get('falla_reportada'), #falla reportada
            estado_fisico=data.get('estado_fisico'), #estado fisico del equipo
            validado=False #por defecto inicia en False
        )
        
        #4. automatizacion: cambiamos el estado del equipo a 'En Mantenimiento'
        equipo.estado_operativo = 'En Mantenimiento'
        
        db.session.add(nuevo_evento) #agregamos el nuevo evento a la base de datos
        db.session.commit() #guardamos los cambios
        
        return jsonify({
            "status": "success",
            "message": f"Evento registrado y asignado al técnico ID: {id_tecnico_asignado}",
            "evento": nuevo_evento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500

#----------------------------------------------

#----------------------------------------------
#endpoint para visualizar todos los eventos registrados
@app.route('/eventos', methods=['GET'])
@jwt_required() #requiere sesion iniciada
def get_eventos():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    
    #RESTRICCIÓN: El usuario solicitante no puede ver el listado de eventos
    if usuario.rol == 'Usuario Solicitante':
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
        
    try:
        eventos = Evento.query.all() #traemos todos los eventos
        return jsonify({
            "status": "success",
            "eventos": [e.to_dict() for e in eventos] #convertimos los eventos a diccionario
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

#----------------------------------------------

#----------------------------------------------
#endpoint para actualizar un evento (con restricciones de rol)
@app.route('/eventos/<int:id>', methods=['PUT'])
@jwt_required() #requiere sesion iniciada
def update_evento(id):
    usuario_id = get_jwt_identity() #id del usuario en sesion
    usuario = Usuario.query.get(usuario_id) #datos del usuario
    
    evento = Evento.query.get(id) #buscamos el evento
    if not evento:
        return jsonify({"status": "error", "message": "Evento no encontrado"}), 404
        
    data = request.json #datos a actualizar
    
    try:
        #LOGICA PARA ADMINISTRADOR: puede modificar todo
        if usuario.rol == 'Administrador':
            if 'id_equipo' in data: evento.id_equipo = data['id_equipo']
            if 'id_usuario' in data: evento.id_usuario = data['id_usuario']
            if 'falla_reportada' in data: evento.falla_reportada = data['falla_reportada']
            if 'estado_fisico' in data: evento.estado_fisico = data['estado_fisico']
            
            #Automatización al validar 
            if 'validado' in data:
                #Si se quiere validar (pasar a True)
                if data['validado'] == True and evento.validado == False: #si el evento no está validado y se quiere validar
                    evento.validado = True #se valida el evento
                    
                    #CONSULTA DE SEGURIDAD: hay otros eventos sin validar para este equipo?
                    pendientes = Evento.query.filter(
                        Evento.id_equipo == evento.id_equipo, 
                        Evento.validado == False,
                        Evento.id_evento != evento.id_evento #Excluimos el actual por seguridad
                    ).count() #contamos los eventos sin validar
                    
                    if pendientes == 0: #si no hay eventos sin validar
                        if evento.equipo: #si el evento tiene equipo
                            evento.equipo.estado_operativo = 'Operativo' #el equipo se pone como operativo
                    else:
                        if evento.equipo: #si el evento tiene equipo
                            evento.equipo.estado_operativo = 'En Mantenimiento' #el equipo se pone como en mantenimiento
                else:
                    evento.validado = data['validado'] #se actualiza el validado
            
        #LOGICA PARA TÉCNICO: solo puede validar
        elif usuario.rol == 'Técnico':
            #verificamos que NO intente cambiar otros atributos
            campos_prohibidos = ['id_equipo', 'id_usuario', 'falla_reportada', 'estado_fisico']
            for campo in campos_prohibidos: #recorremos los campos prohibidos
                if campo in data: #si el campo está en los datos
                    return jsonify({
                        "status": "error", 
                        "message": "Como técnico, no tienes permisos para modificar otros atributos del evento"
                    }), 403
            
            #verificamos la condicion de validado (de False a True)
            if 'validado' in data:
                if evento.validado == False and data['validado'] == True: #si el evento no está validado y se quiere validar
                    evento.validado = True #se valida el evento
                    
                    #CONSULTA DE SEGURIDAD: ¿Hay otros eventos sin validar para este equipo?
                    pendientes = Evento.query.filter(
                        Evento.id_equipo == evento.id_equipo, 
                        Evento.validado == False,
                        Evento.id_evento != evento.id_evento #excluimos el actual por seguridad
                    ).count() #contamos los eventos sin validar
                    
                    if pendientes == 0: #si no hay eventos sin validar
                        if evento.equipo: #si el evento tiene equipo
                            evento.equipo.estado_operativo = 'Operativo' #el equipo se pone como operativo
                    else:
                        if evento.equipo: #si el evento tiene equipo
                            evento.equipo.estado_operativo = 'En Mantenimiento' #el equipo se pone como en mantenimiento
                else:
                    return jsonify({"status": "error", "message": "Un técnico solo puede validar un evento (pasar de False a True)"}), 403
            else:
                return jsonify({"status": "error", "message": "No se enviaron cambios permitidos para el técnico"}), 400
        
        else:
            return jsonify({"status": "error", "message": "No tienes permisos para actualizar eventos"}), 403

        db.session.commit() #confirmamos la transaccion
        return jsonify({
            "status": "success",
            "message": "Evento actualizado correctamente",
            "evento": evento.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


#------------------------------------------------------------------------------

#----------------------------------------------
#endpoint para crear un diagnóstico nuevo
@app.route('/diagnosticos', methods=['POST'])
@jwt_required() #requiere sesion iniciada
def create_diagnostico():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
        
    data = request.json #obtenemos los datos en json
    id_evento = data.get('id_evento') #obtenemos el id del evento
    
    if not id_evento:
        return jsonify({"status": "error", "message": "id_evento es requerido"}), 400
        
    try:
        #1. Verificar que el evento exista
        evento = Evento.query.get(id_evento) #obtenemos el evento
        if not evento:
            return jsonify({"status": "error", "message": "El evento no existe"}), 404
            
        #2. Verificar que no exista ya un diagnóstico para este evento (Relación 1:1)
        existe = Diagnostico.query.get(id_evento) #verificamos si ya existe un diagnóstico para este evento
        if existe:
            return jsonify({
                "status": "error", 
                "message": "Ya existe un diagnóstico registrado para este evento. Usa PUT para editarlo."
            }), 400
            
        #3. Crear el diagnóstico
        nuevo_diagnostico = Diagnostico(
            id_evento=id_evento,
            log_chatbot=data.get('log_chatbot'),
            resultado_preeliminar=data.get('resultado_preeliminar'),
            validacion_tecnico=data.get('validacion_tecnico')
        )
        
        db.session.add(nuevo_diagnostico) #agregamos el nuevo diagnostico a la base de datos
        db.session.commit() #confirmamos la transaccion
        
        return jsonify({
            "status": "success",
            "message": "Diagnóstico registrado correctamente",
            "diagnostico": nuevo_diagnostico.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500

#----------------------------------------------

#----------------------------------------------
#endpoint para visualizar los diagnosticos registrados
@app.route('/diagnosticos', methods=['GET'])
@jwt_required() #requiere sesion iniciada
def get_diagnosticos():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    
    #RESTRICCIÓN: El usuario solicitante no puede ver el listado de diagnosticos
    if usuario.rol == 'Usuario Solicitante':
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
        
    try:
        diagnosticos = Diagnostico.query.all() #traemos todos los diagnosticos
        return jsonify({
            "status": "success",
            "diagnosticos": [d.to_dict() for d in diagnosticos] #convertimos los diagnosticos a diccionario
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

#----------------------------------------------

#----------------------------------------------
#endpoint para editar un diagnostico (solo técnicos y administradores)
@app.route('/diagnosticos/<int:id_evento>', methods=['PUT'])
@jwt_required() #requiere sesion iniciada
def update_diagnostico(id_evento):
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #RESTRICCIÓN: Solo Admins o Técnicos pueden editar el diagnóstico
    if usuario.rol not in ['Administrador', 'Técnico']:
        return jsonify({
            "status": "error", 
            "message": "No tienes permisos para editar diagnósticos técnicos"
        }), 403
    
    #1. Verificar que el evento asociado exista y su estado de validación
    evento = Evento.query.get(id_evento)
    if not evento:
        return jsonify({"status": "error", "message": "El evento asociado no existe"}), 404
        
    #2. Si el evento ya está VALIDADO (True), solo el Admin puede seguir editando
    if evento.validado == True and usuario.rol != 'Administrador':
        return jsonify({
            "status": "error", 
            "message": "Este evento ya ha sido validado. Solo un administrador puede realizar cambios en el diagnóstico."
        }), 403
        
    diagnostico = Diagnostico.query.get(id_evento)
    if not diagnostico:
        return jsonify({"status": "error", "message": "Diagnóstico no encontrado"}), 404
        
    data = request.json #obtenemos los datos en json
    
    try:
        if 'log_chatbot' in data: diagnostico.log_chatbot = data['log_chatbot'] #actualizamos el log del chatbot
        if 'resultado_preeliminar' in data: diagnostico.resultado_preeliminar = data['resultado_preeliminar'] #actualizamos el resultado preliminar
        if 'validacion_tecnico' in data: diagnostico.validacion_tecnico = data['validacion_tecnico'] #actualizamos la validacion tecnica
        
        db.session.commit() #confirmamos la transaccion
        return jsonify({
            "status": "success",
            "message": "Diagnóstico actualizado correctamente",
            "diagnostico": diagnostico.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500

#------------------------------------------------------------------------------

#----------------------------------------------
#endpoint para crear un mantenimiento (Solo Técnicos)
@app.route('/mantenimientos', methods=['POST'])
@jwt_required()
def create_mantenimiento():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #RESTRICCIÓN: Solo el Técnico puede crear el mantenimiento
    if usuario.rol != 'Técnico':
        return jsonify({
            "status": "error", 
            "message": "Solo el técnico asignado puede registrar el mantenimiento final"
        }), 403
        
    data = request.json #obtenemos los datos en json
    id_evento = data.get('id_evento') #obtenemos el id del evento
    
    if not id_evento:
        return jsonify({"status": "error", "message": "id_evento es requerido"}), 400
        
    try:
        #1. Verificar existencia del evento
        evento = Evento.query.get(id_evento)
        if not evento:
            return jsonify({"status": "error", "message": "El evento no existe"}), 404
            
        #2. Verificar duplicados
        existe = Mantenimiento.query.get(id_evento) #verificamos si ya existe un mantenimiento para este evento
        if existe:
            return jsonify({
                "status": "error", 
                "message": "Ya existe un registro de mantenimiento para este evento"
            }), 400
            
        #3. Crear mantenimiento
        nuevo_mantenimiento = Mantenimiento(
            id_evento=id_evento,
            tipo=data.get('tipo'), # 'Preventivo' o 'Correctivo'
            fecha_entrega=data.get('fecha_entrega'),
            descripcion_trabajo=data.get('descripcion_trabajo'),
            piezas_reemplazadas=data.get('piezas_reemplazadas')
        )
        
        db.session.add(nuevo_mantenimiento) #agregamos el nuevo mantenimiento a la base de datos
        db.session.commit() #confirmamos la transaccion
        
        return jsonify({
            "status": "success",
            "message": "Mantenimiento registrado con éxito",
            "mantenimiento": nuevo_mantenimiento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500

#----------------------------------------------

#----------------------------------------------
#endpoint para visualizar mantenimientos (Admin y Técnico)
@app.route('/mantenimientos', methods=['GET'])
@jwt_required()
def get_mantenimientos():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #RESTRICCIÓN: Usuario Solicitante no puede ver esta lista
    if usuario.rol == 'Usuario Solicitante':
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
        
    try:
        mantenimientos = Mantenimiento.query.all() #traemos todos los mantenimientos
        return jsonify({
            "status": "success",
            "mantenimientos": [m.to_dict() for m in mantenimientos] #convertimos los mantenimientos a diccionario
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

#----------------------------------------------

#----------------------------------------------
#endpoint para editar mantenimientos (Administrador y Técnico bajo condición)
@app.route('/mantenimientos/<int:id_evento>', methods=['PUT'])
@jwt_required()
def update_mantenimiento(id_evento):
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #1. Verificar permisos basicos de rol
    if usuario.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No tienes permisos para editar mantenimientos"}), 403
        
    #2. Verificar que el evento asociado exista y su estado de validacion
    evento = Evento.query.get(id_evento) #verificamos si el evento existe
    if not evento:
        return jsonify({"status": "error", "message": "El evento asociado no existe"}), 404
        
    #3. Restriccion dinamica: Si esta VALIDADO, solo Admin puede editar
    if evento.validado == True and usuario.rol != 'Administrador':
        return jsonify({
            "status": "error", 
            "message": "Este evento ya ha sido validado. Solo un administrador puede realizar cambios en el mantenimiento."
        }), 403
        
    mantenimiento = Mantenimiento.query.get(id_evento) #obtenemos el mantenimiento
    if not mantenimiento:
        return jsonify({"status": "error", "message": "Mantenimiento no encontrado"}), 404
        
    data = request.json #obtenemos los datos en json
    
    try:
        if 'tipo' in data: mantenimiento.tipo = data['tipo']
        if 'fecha_entrega' in data: mantenimiento.fecha_entrega = data['fecha_entrega']
        if 'descripcion_trabajo' in data: mantenimiento.descripcion_trabajo = data['descripcion_trabajo']
        if 'piezas_reemplazadas' in data: mantenimiento.piezas_reemplazadas = data['piezas_reemplazadas']
        
        db.session.commit() #confirmamos la transaccion
        return jsonify({
            "status": "success",
            "message": "Mantenimiento actualizado por el administrador",
            "mantenimiento": mantenimiento.to_dict() #convertimos el mantenimiento a diccionario
        }), 200
        
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#clase para generar pdf de expediente tecnico
class PDF_Expediente(FPDF):
    def header(self):
        #1. logos institucionales (SEP, TecNM, ITL, ExperTrack)
        #ajustamos tamaños y posiciones para que quepan en una fila
        try:            
            sep_path = os.path.join(base_path, 'static', 'logos', 'sep.png')
            tecnm_path = os.path.join(base_path, 'static', 'logos', 'tecnm.jpg')
            itl_path = os.path.join(base_path, 'static', 'logos', 'itl.png')
            exper_path = os.path.join(base_path, 'static', 'logos', 'ExperTrack.png')

            self.image(sep_path, 10, 10, 35)
            self.image(tecnm_path, 55, 10, 35)
            self.image(itl_path, 110, 8, 28)
            self.image(exper_path, 155, 10, 45)
        except Exception as e:
            print(f"Error al cargar logos en PDF: {e}")

        self.ln(35)
        #2. titulo del reporte
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, 'EXPEDIENTE TECNICO DE EQUIPO', 0, 1, 'C')
        self.set_font('Helvetica', '', 10)
        self.cell(0, 5, 'Sistema Gestor de Mantenimiento ExperTrack', 0, 1, 'C')
        self.ln(10)
        
        #linea divisoria
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    #pie de pagina del pdf
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        
        #fecha actual
        fecha_gen = (datetime.utcnow() + timedelta(hours=-6)).strftime("%d/%m/%Y %H:%M")
        
        #fecha
        self.cell(60, 10, f'Fecha: {fecha_gen}', 0, 0, 'L')
        
        #derechos de author
        self.cell(70, 10, '(c) 2026 ExperTrack - Todos los derechos reservados', 0, 0, 'C')
        
        #paginacion
        self.cell(60, 10, f'Pagina {self.page_no()}/{{nb}}', 0, 0, 'R')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#endpoint para generar pdf de expediente tecnico
@app.route('/equipos/<int:id>/expediente_pdf', methods=['GET'])
@jwt_required()
def export_expediente_pdf(id):
    try:
        #1. obtener datos
        equipo = Equipo.query.get(id)
        if not equipo:
            return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
        spec = Especificacion.query.filter_by(id_equipo=id, es_actual=True).first()
        historial = db.session.query(Evento, Usuario, Mantenimiento)\
            .join(Usuario, Evento.id_usuario == Usuario.id_usuario)\
            .outerjoin(Mantenimiento, Evento.id_evento == Mantenimiento.id_evento)\
            .filter(Evento.id_equipo == id)\
            .order_by(Evento.fecha_creacion.desc())\
            .all()

        #2. diseñar pdf
        pdf = PDF_Expediente()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)

        #seccion de identificacion del equipo
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, '  IDENTIFICACION DEL EQUIPO', 0, 1, 'L', fill=True)
        pdf.ln(2)
        
        pdf.set_font('Helvetica', '', 10)
        col1, col2 = 40, 60
        
        #datos del equipo
        datos_equipo = [
            ('Codigo Inventario:', equipo.codigo_inventario or "N/A", 'Marca:', equipo.marca or "N/A"),
            ('No. de Serie:', equipo.numero_serie or "N/A", 'Modelo:', equipo.modelo or "N/A"),
            ('Tipo de Equipo:', equipo.tipo_equipo or "N/A", 'Area:', equipo.area or "N/A"),
            ('Ubicacion:', equipo.ubicacion or "N/A", 'Estatus:', equipo.estado_operativo or "N/A")
        ] 
        
        #iteramos sobre los datos del equipo
        for d in datos_equipo:
            pdf.set_font('Helvetica', 'B', 10); pdf.cell(col1, 7, d[0], 0)
            pdf.set_font('Helvetica', '', 10); pdf.cell(col2, 7, d[1], 0)
            pdf.set_font('Helvetica', 'B', 10); pdf.cell(col1, 7, d[2], 0)
            pdf.set_font('Helvetica', '', 10); pdf.cell(col2, 7, d[3], 0)
            pdf.ln()

        pdf.ln(5)

        #seccion de especificaciones tecnicas
        if spec:
            pdf.set_font('Helvetica', 'B', 12); pdf.cell(0, 8, '  ESPECIFICACIONES TECNICAS ACTUALES', 0, 1, 'L', fill=True)
            pdf.ln(2)
            
            specs_list = [
                ('CPU:', spec.procesador, 'S.O:', spec.sistema_operativo),
                ('RAM:', f"{spec.ram} {spec.tipo_ram}", 'Disco:', f"{spec.almacenamiento} {spec.almacenamiento_tipo}")
            ]
            for s in specs_list:
                pdf.set_font('Helvetica', 'B', 10); pdf.cell(col1, 7, s[0], 0)
                pdf.set_font('Helvetica', '', 10); pdf.cell(col2, 7, s[1], 0)
                pdf.set_font('Helvetica', 'B', 10); pdf.cell(col1, 7, s[2], 0)
                pdf.set_font('Helvetica', '', 10); pdf.cell(col2, 7, s[3], 0)
                pdf.ln()
        
        pdf.ln(10)

        #seccion de historial de mantenimientos y eventos
        pdf.set_font('Helvetica', 'B', 12); pdf.cell(0, 8, '  HISTORIAL DE MANTENIMIENTOS Y EVENTOS', 0, 1, 'L', fill=True)
        pdf.ln(3)

        pdf.set_font('Helvetica', 'B', 9); pdf.set_fill_color(220, 220, 220)
        pdf.cell(25, 8, 'Fecha', 1, 0, 'C', fill=True)
        pdf.cell(40, 8, 'Tecnico', 1, 0, 'C', fill=True)
        pdf.cell(30, 8, 'Tipo', 1, 0, 'C', fill=True)
        pdf.cell(95, 8, 'Descripcion del Trabajo / Falla', 1, 1, 'C', fill=True)

        pdf.set_font('Helvetica', '', 8)
        for ev, tec, mant in historial:
            desc = mant.descripcion_trabajo if mant else ev.falla_reportada or "Sin descripcion"
            fecha = ev.fecha_creacion.strftime("%d/%m/%Y")
            nombre_tec = f"{tec.nombre} {tec.apellido_paterno}"
            tipo = mant.tipo if mant else "Evento/Diag"
            #calculamos cuantas lineas ocupara la descripcion (ancho 95)
            #usamos split_only para obtener la lista de lineas sin dibujarlas aun
            lineas_desc = pdf.multi_cell(95, 6, desc, split_only=True)
            altura_fila = len(lineas_desc) * 6 #interlineado de 6
            if altura_fila < 8: altura_fila = 8 #altura minima por fila
            
            #dibujamos las primeras 3 celdas con la altura total calculada
            #el parametro 0 al final indica que no salte de linea aun
            pdf.cell(25, altura_fila, fecha, 1, 0, 'C')
            pdf.cell(40, altura_fila, nombre_tec[:22], 1, 0, 'C')
            pdf.cell(30, altura_fila, tipo, 1, 0, 'C')
            
            #dibujamos la multicelda al final
            #dividimos la altura_fila entre el numero de lineas para que rellene todo el espacio
            h_cada_linea = altura_fila / len(lineas_desc)
            pdf.multi_cell(95, h_cada_linea, desc, 1, 'L')        

        #retornamos el pdf
        pdf_bytes = pdf.output()
        buffer = io.BytesIO(pdf_bytes)
        buffer.seek(0)
            
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Expediente_ID_{equipo.id_equipo}.pdf'
        )

    except Exception as e:
        print(f"Error generando PDF: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

#----------------------------------------------------

#----------------------------------------------
#endpoint para obtener los sintomas de la bd (bd extra)
@app.route('/sintomas', methods=['GET'])
@jwt_required() #solo usuarios autenticados
def get_sintomas():
    try:
        #recibimos el tipo desde los parametros de la URL: /api/sintomas?tipo=PC
        tipo = request.args.get('tipo')
        
        query = SintomaHecho.query #consulta a la tabla SintomaHecho
        
        if tipo:
            #hacemos un JOIN con la tabla de fallas (FallaHecho) para filtrar solo los síntomas
            #que tengan al menos una falla registrada para ese tipo de equipo (PC o Laptop)
            query = query.join(FallaHecho).filter(FallaHecho.tipo_equipo == tipo).distinct()
        
        sintomas = query.all() #obtenemos todos los sintomas
        
        return jsonify({
            "status": "success",
            "sintomas": [s.to_dict() for s in sintomas]
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al obtener síntomas: {str(e)}"
        }), 500
#----------------------------------------------------

#----------------------------------------------------
#endpoint para sincronizar la base de datos con prolog
def sincronizar_hechos_prolog():
    """Consulta la base de datos y regenera el archivo hechos.pl para Prolog"""
    try:
        fallas = FallaHecho.query.all() #consulta a la tabla de fallas en la bd
        
        lines = [
            "% --- hechos.pl: GENERADO AUTOMATICAMENTE DESDE LA BASE DE DATOS ---",
            "% No editar este archivo manualmente.",
            f"% Ultima actualizacion: {timedelta(hours=-6) + datetime.utcnow()}", 
            "\n"
        ] #lista de lineas que se van a escribir en el archivo hechos.pl
        
        for f in fallas:
            #escapar comillas simples duplicandolas para Prolog
            diag = f.diagnostico.replace("'", "''")
            rec = f.recomendacion.replace("'", "''")
            pregunta = f.pregunta_pista.replace("'", "''")
            
            #generar lineas de hechos
            lines.append(f"falla_info({f.id}, '{f.tipo_equipo}', '{diag}', '{rec}').")
            sintoma_clave = f.sintoma.clave if f.sintoma else "sintoma_desconocido"
            lines.append(f"condicion({f.id}, {sintoma_clave}, '{pregunta}').")
        
        #escribir el archivo
        with open(path_hechos, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))
            
        #recargar el motor de Prolog para que reconozca los nuevos hechos
        prolog.consult(path_reglas)
        print(">>> Sincronización con Prolog exitosa.") #imprimimos en consola que se sincronizo correctamente
        return True
    except Exception as e:
        print(f">>> Error sincronizando con Prolog: {str(e)}")
        return False

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#endpoint para registrar nuevas categorías (para los hechos)
@app.route('/categorias_hechos', methods=['POST'])
@jwt_required()
def create_categoria_hecho():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #solo los técnicos pueden agregar hechos
    if usuario.rol != 'Técnico':
        return jsonify({"status": "error", "message": "Solo los técnicos tienen permisos para alimentar la base de conocimientos"}), 403
        
    data = request.json #obtenemos los datos en json
    nombre = data.get('nombre') #obtenemos el nombre de la categoría
    
    if not nombre:
        return jsonify({"status": "error", "message": "El nombre de la categoría es requerido"}), 400
        
    try:
        nueva_cat = CategoriaHecho(nombre=nombre) #creamos la nueva categoría
        db.session.add(nueva_cat) #agregamos la nueva categoría
        db.session.commit() #confirmamos la transaccion
        return jsonify({
            "status": "success",
            "message": "Categoría de diagnóstico registrada correctamente",
            "categoria": nueva_cat.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": "Error al registrar categoría (posible nombre duplicado)"}), 500

#------------------------------------------------------------------------------
#endpoint para obtener todas las categorias de diagnostico
@app.route('/categorias_hechos', methods=['GET'])
@jwt_required() #solo usuarios autenticados
def get_categorias_hechos():
    try:
        categorias = CategoriaHecho.query.all()
        return jsonify({
            "status": "success",
            "categorias": [c.to_dict() for c in categorias]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al obtener categorías: {str(e)}"}), 500
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#endpoint para registrar nuevos sintomas iniciales
@app.route('/sintomas_hechos', methods=['POST'])
@jwt_required() #solo usuarios autenticados
def create_sintoma_hecho():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #solo los técnicos pueden agregar hechos
    if usuario.rol != 'Técnico':
        return jsonify({"status": "error", "message": "Solo los técnicos tienen permisos para alimentar la base de conocimientos"}), 403
        
    data = request.json #obtenemos los datos en json
    
    #datos del síntoma (manifestacion de falla)
    clave = data.get('clave')
    descripcion = data.get('descripcion')
    
    #datos de la falla obligatoria (para evitar sintomas huerfanitos)
    tipo_equipo = data.get('tipo_equipo')
    categoria_id = data.get('categoria_id')
    pregunta_pista = data.get('pregunta_pista')
    diagnostico = data.get('diagnostico')
    recomendacion = data.get('recomendacion')
    
    #validamos que todos los campos del sintoma y la falla esten presentes
    campos_requeridos = [clave, descripcion, tipo_equipo, categoria_id, pregunta_pista, diagnostico, recomendacion]
    if not all(campos_requeridos):
        return jsonify({
            "status": "error", 
            "message": "Para registrar un sintoma inicial, es obligatorio incluir los datos de su primera falla asociada (tipo_equipo, categoria_id, etc.)"
        }), 400
        
    #verificamos que la categoria exista    
    if tipo_equipo not in ['PC', 'Laptop']:
        return jsonify({"status": "error", "message": "El tipo_equipo de la falla debe ser 'PC' o 'Laptop'"}), 400

    try:
        #iniciamos el guardado, primero el sintoma
        nuevo_sintoma = SintomaHecho(clave=clave, descripcion=descripcion)
        db.session.add(nuevo_sintoma)
        db.session.flush() #obtenemos el ID del sintoma sin confirmar la transaccion aun

        #creamos la falla ligada al nuevo sintoma
        nueva_falla = FallaHecho(
            tipo_equipo=tipo_equipo,
            sintoma_id=nuevo_sintoma.id,
            categoria_id=categoria_id,
            pregunta_pista=pregunta_pista,
            diagnostico=diagnostico,
            recomendacion=recomendacion
        )
        
        db.session.add(nueva_falla)
        db.session.commit() #confirmamos ambos
        
        #sincronizamos con prolog
        sincronizar_hechos_prolog()
        
        return jsonify({
            "status": "success",
            "message": "Síntoma inicial y su falla asociada registrados y sincronizados correctamente",
            "sintoma": nuevo_sintoma.to_dict(),
            "falla_inicial": nueva_falla.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al registrar: {str(e)}"}), 500

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#endpoint para registrar nuevas fallas
@app.route('/fallas_hechos', methods=['POST'])
@jwt_required() #solo usuarios autenticados
def create_falla_hecho():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #solo los técnicos pueden agregar hechos
    if usuario.rol != 'Técnico':
        return jsonify({"status": "error", "message": "Solo los técnicos tienen permisos para alimentar la base de conocimientos"}), 403
        
    data = request.json #obtenemos los datos en json
    tipo_equipo = data.get('tipo_equipo') #obtenemos el tipo de equipo
    sintoma_id = data.get('sintoma_id') #obtenemos el id del sintoma
    categoria_id = data.get('categoria_id') #obtenemos el id de la categoria
    pregunta_pista = data.get('pregunta_pista') #obtenemos la pregunta pista
    diagnostico = data.get('diagnostico') #obtenemos el diagnostico
    recomendacion = data.get('recomendacion') #obtenemos la recomendacion
    
    #verificamos que todos los campos sean obligatorios
    if not all([tipo_equipo, sintoma_id, categoria_id, pregunta_pista, diagnostico, recomendacion]):
        return jsonify({"status": "error", "message": "Todos los campos son obligatorios para registrar una falla"}), 400

    #verificamos que el tipo de equipo sea correcto
    if tipo_equipo not in ['PC', 'Laptop']:
        return jsonify({"status": "error", "message": "El tipo_equipo debe ser 'PC' o 'Laptop'"}), 400

    try:
        #verificamos que existan la categoría y el sintoma individualmente para dar un error descriptivo
        if not CategoriaHecho.query.get(categoria_id):
            return jsonify({"status": "error", "message": f"La categoría con ID {categoria_id} no existe"}), 404
            
        #verificamos que el sintoma exista
        if not SintomaHecho.query.get(sintoma_id):
            return jsonify({"status": "error", "message": f"El síntoma inicial con ID {sintoma_id} no existe. Toda falla debe estar ligada a un síntoma existente."}), 404

        nueva_falla = FallaHecho(
            tipo_equipo=tipo_equipo,
            sintoma_id=sintoma_id,
            categoria_id=categoria_id,
            pregunta_pista=pregunta_pista,
            diagnostico=diagnostico,
            recomendacion=recomendacion
        ) #creamos la nueva falla
        
        db.session.add(nueva_falla) #agregamos la nueva falla
        db.session.commit() #confirmamos la transaccion
        
        # sincronizamos con el archivo fisico de Prolog
        sincronizar_hechos_prolog()
        
        return jsonify({
            "status": "success",
            "message": "Nueva falla/regla de diagnóstico registrada correctamente y sincronizada con Prolog",
            "falla": nueva_falla.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#endpoint para obtener todas las fallas registradas
@app.route('/fallas_hechos', methods=['GET'])
@jwt_required() #solo usuarios autenticados
def get_fallas_hechos():
    try:              
        tipo = request.args.get('tipo')
        sintoma_id = request.args.get('sintoma_id')
        categoria_id = request.args.get('categoria_id')
        
        query = FallaHecho.query #obtenemos todas las fallas
        
        #filtros
        if tipo:
            query = query.filter(FallaHecho.tipo_equipo == tipo)
        if sintoma_id:
            query = query.filter(FallaHecho.sintoma_id == sintoma_id)
        if categoria_id:
            query = query.filter(FallaHecho.categoria_id == categoria_id)
            
        fallas = query.all()
        
        #construimos la respuesta 
        resultado = []
        for f in fallas:
            f_dict = f.to_dict()
            #agregamos nombres descriptivos gracias a las relaciones
            f_dict['sintoma_descripcion'] = f.sintoma.descripcion if f.sintoma else "N/A"
            f_dict['categoria_nombre'] = f.categoria.nombre if f.categoria else "N/A"
            resultado.append(f_dict)
            
        return jsonify({
            "status": "success",
            "total": len(resultado),
            "fallas": resultado
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al obtener fallas: {str(e)}"}), 500
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#endpoint para descargar el archivo hechos.pl (para presentacion/backup)
@app.route('/exportar_hechos', methods=['GET'])
@jwt_required() #solo usuarios autenticados
def exportar_hechos():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #solo los administradores y técnicos pueden descargar la base de conocimientos
    if usuario.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No tienes permisos para descargar la base de conocimientos"}), 403
        
    #forzamos una sincronizacion antes de descargar para tener lo ultimo en la bd
    sincronizar_hechos_prolog()
    
    try:
        return send_file(
            path_hechos,
            as_attachment=True,
            download_name='hechos.pl',
            mimetype='text/plain'
        ) #retornamos el archivo hechos.pl
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al descargar: {str(e)}"}), 500

#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#---- Endpoints para Módulo de Alertas -------------
#------------------------------------------------------------------------------

#endpoint para crear una nueva alerta
@app.route('/alertas', methods=['POST'])
@jwt_required() #solo usuarios autenticados
def create_alerta():
    usuario_id_auth = get_jwt_identity() #obtenemos el id del usuario
    usuario_auth = Usuario.query.get(usuario_id_auth) #obtenemos el usuario
    
    #solo los administradores y técnicos pueden crear alertas
    if usuario_auth.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No tienes permisos para crear alertas"}), 403

    data = request.json
    id_equipo = data.get('id_equipo') # id del equipo al que se le enviara la alerta
    id_usuario = data.get('id_usuario') # id del usuario al que se le enviara la alerta
    titulo = data.get('titulo') # titulo de la alerta
    descripcion = data.get('descripcion') # descripcion de la alerta
    fecha_programada = data.get('fecha_programada') # fecha en la que se enviara la alerta

    if not all([id_equipo, id_usuario, titulo, fecha_programada]):
        return jsonify({"status": "error", "message": "Faltan campos obligatorios"}), 400

    try:
        #verificamos existencia
        if not Equipo.query.get(id_equipo):
            return jsonify({"status": "error", "message": "El equipo no existe"}), 404
        if not Usuario.query.get(id_usuario):
            return jsonify({"status": "error", "message": "El usuario responsable no existe"}), 404

        #creamos la alerta
        nueva_alerta = Alerta(
            id_equipo=id_equipo,
            id_usuario=id_usuario,
            titulo=titulo,
            descripcion=descripcion,
            fecha_programada=datetime.strptime(fecha_programada, '%Y-%m-%d').date()
        ) 
        
        db.session.add(nueva_alerta) #agregamos la alerta a la base de datos
        db.session.commit() #confirmamos la transaccion
        return jsonify({"status": "success", "message": "Alerta creada correctamente", "alerta": nueva_alerta.to_dict()}), 201
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500

#--------------------------------------------------

#--------------------------------------------------
#endpoint para visualizar todas las alertas
@app.route('/alertas', methods=['GET'])
@jwt_required() #solo usuarios autenticados
def get_alertas():
    usuario_auth = Usuario.query.get(get_jwt_identity()) #obtenemos el id del usuario
    
    #solo los administradores y técnicos pueden ver las alertas
    if usuario_auth.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403

    try:
        #filtro por estatus
        estatus = request.args.get('estatus')
        query = db.session.query(Alerta, Equipo, Usuario).join(Equipo, Alerta.id_equipo == Equipo.id_equipo).join(Usuario, Alerta.id_usuario == Usuario.id_usuario)
        
        #aplicamos el filtro si se proporciona
        if estatus:
            query = query.filter(Alerta.estatus == estatus)
            
        #ejecutamos la consulta
        alertas = query.all()
        resultado = []
        for al, eq, us in alertas:
            al_dict = al.to_dict()
            al_dict['codigo_equipo'] = eq.codigo_inventario
            al_dict['nombre_responsable'] = f"{us.nombre} {us.apellido_paterno}"
            resultado.append(al_dict)
            
        return jsonify({"status": "success", "alertas": resultado}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
#--------------------------------------------------

#--------------------------------------------------
#endpoint para editar una alerta existente
@app.route('/alertas/<int:id>', methods=['PUT'])
@jwt_required() #solo usuarios autenticados
def update_alerta(id):
    usuario_auth = Usuario.query.get(get_jwt_identity()) #obtenemos el id del usuario
    
    #solo los administradores y técnicos pueden editar las alertas
    if usuario_auth.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No tienes permisos"}), 403

    alerta = Alerta.query.get(id) #obtenemos la alerta
    
    #verificamos que la alerta exista
    if not alerta:
        return jsonify({"status": "error", "message": "Alerta no encontrada"}), 404

    data = request.json #obtenemos los datos de la alerta
    try:
        if 'titulo' in data: alerta.titulo = data['titulo']
        if 'descripcion' in data: alerta.descripcion = data['descripcion']
        if 'estatus' in data: alerta.estatus = data['estatus']
        if 'id_usuario' in data: alerta.id_usuario = data['id_usuario']
        if 'fecha_programada' in data: 
            alerta.fecha_programada = datetime.strptime(data['fecha_programada'], '%Y-%m-%d').date()
            
        db.session.commit() #confirmamos la transaccion
        return jsonify({"status": "success", "message": "Alerta actualizada", "alerta": alerta.to_dict()}), 200
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500
#--------------------------------------------------

#--------------------------------------------------
#endpoint para eliminar una alerta (exclusivo para admin)
@app.route('/alertas/<int:id>', methods=['DELETE'])
@jwt_required() #solo usuarios autenticados
def delete_alerta(id):
    usuario_auth = Usuario.query.get(get_jwt_identity()) #obtenemos el id del usuario
    
    #solo los administradores pueden eliminar las alertas
    if usuario_auth.rol != 'Administrador':
        return jsonify({"status": "error", "message": "Solo el administrador puede eliminar alertas"}), 403

    alerta = Alerta.query.get(id) #obtenemos la alerta
    
    #verificamos que la alerta exista
    if not alerta:
        return jsonify({"status": "error", "message": "Alerta no encontrada"}), 404

    try:
        db.session.delete(alerta) #eliminamos la alerta
        db.session.commit()
        return jsonify({"status": "success", "message": "Alerta eliminada correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

#------------------------------------------------------------------------------

#--------------------------------------------------------
#función para verificar las alertas pendientes y enviar correos 
def verificar_alertas_programadas():
    """Lógica central para procesar alertas (2 días antes)"""
    with app.app_context():
        try:
            hoy = (datetime.utcnow() + timedelta(hours=-6)).date()
            #obtenemos alertas pendientes junto con los datos del usuario y equipo
            query = db.session.query(Alerta, Usuario, Equipo)\
                .join(Usuario, Alerta.id_usuario == Usuario.id_usuario)\
                .join(Equipo, Alerta.id_equipo == Equipo.id_equipo)\
                .filter(Alerta.estatus == 'Pendiente')
            
            alertas = query.all()
            count = 0
            
            if not alertas:
                return 0

            #iniciamos conexión SMTP
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            
            for al, user, eq in alertas:
                fecha_disparo = al.fecha_programada - timedelta(days=2)
                
                if hoy >= fecha_disparo:
                    #redactamos el correo con MIMEText
                    cuerpo = (f"Hola {user.nombre},\n\n"
                             f"Esta es una notificacion automatica de ExperTrack.\n"
                             f"Tienes una actividad programada para el equipo: {eq.codigo_inventario} ({eq.marca} {eq.modelo}).\n\n"
                             f"Detalles de la alerta:\n"
                             f"- Titulo: {al.titulo}\n"
                             f"- Descripcion: {al.descripcion}\n"
                             f"- Fecha Programada: {al.fecha_programada}\n\n"
                             f"Por favor, toma las medidas necesarias.\n\n"
                             f"Atentamente,\nSistema ExperTrack")
                    
                    msg = MIMEText(cuerpo)
                    msg['Subject'] = f"ALERTA PREVENTIVA: {al.titulo}"
                    msg['From'] = SMTP_USER
                    msg['To'] = user.correo
                    
                    #enviamos
                    server.sendmail(SMTP_USER, user.correo, msg.as_string())
                    
                    #marcamos como enviada
                    al.estatus = 'Enviada'
                    count += 1
                    print(f">>> Alerta enviada a {user.correo}")

            server.quit() #cerramos la conexion
            
            #si se envio al menos una alerta, confirmamos la transaccion
            if count > 0:
                db.session.commit()
            return count
            
        except Exception as e:
            print(f"Error en verificacion de alertas: {e}")
            return 0
#--------------------------------------------------------


#----------------------------------------------------------------
#endpoint para verificacion manual desde el frontend
@app.route('/alertas/verificar_manual', methods=['POST'])
@jwt_required() #solo usuarios autenticados
def trigger_verificacion_alertas():
    #solo permitimos a técnicos o admins disparar esto
    usuario = Usuario.query.get(get_jwt_identity())
    if usuario.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No autorizado"}), 403
    
    procesadas = verificar_alertas_programadas() #obtenemos las alertas pendientes
    return jsonify({
        "status": "success", 
        "message": f"Verificación completada. Se enviaron {procesadas} alertas.",
        "enviadas": procesadas
    }), 200

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#---- Endpoint para Dashboard
#------------------------------------------------------------------------------

@app.route('/dashboard/stats', methods=['GET'])
@jwt_required() #solo usuarios autenticados
def get_dashboard_stats():    
    usuario_id_auth = get_jwt_identity() #obtenemos el id del usuario
    usuario_auth = Usuario.query.get(usuario_id_auth) #obtenemos el usuario
    
    #verificamos que el usuario exista
    if not usuario_auth:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    try:
        #1. NIVEL ADMINISTRATIVO: Gráficas y proactividad
        if usuario_auth.rol == 'Administrador':
            #distribucion de estados
            stats_equipos = db.session.query(
                Equipo.estado_operativo, func.count(Equipo.id_equipo)
            ).group_by(Equipo.estado_operativo).all()
            
            #frecuencia de fallas reportadas
            total_eventos = Evento.query.count()
            eventos_validados = Evento.query.filter_by(validado=True).count()
            
            #indice de generación de alertas (Proactividad)
            total_alertas = Alerta.query.count()
            alertas_enviadas = Alerta.query.filter_by(estatus='Enviada').count()
            
            return jsonify({
                "status": "success",
                "rol": "Administrador",
                "data": {
                    "distribucion_estados": dict(stats_equipos),
                    "frecuencia_fallas": {
                        "total": total_eventos,
                        "validados": eventos_validados,
                        "pendientes": total_eventos - eventos_validados
                    },
                    "indice_proactividad": {
                        "total_alertas": total_alertas,
                        "enviadas": alertas_enviadas,
                        "pendientes": total_alertas - alertas_enviadas
                    },
                    "resumen_general": {
                        "total_usuarios": Usuario.query.count(),
                        "total_equipos": Equipo.query.count()
                    }
                }
            }), 200

        #2. NIVEL TÉCNICO: Diagnósticos y sugerencias
        elif usuario_auth.rol == 'Técnico':
            #Listado prioritario de diagnosticos pendientes de validacion
            #unimos con Equipo para mostrar datos relevantes en el dashboard
            pendientes = db.session.query(Evento, Equipo).join(
                Equipo, Evento.id_equipo == Equipo.id_equipo
            ).filter(Evento.validado == False).order_by(Evento.fecha_creacion.desc()).limit(10).all()
            
            #resumen de sugerencias preventivas (Alertas enviadas recientemente)
            recientes = Alerta.query.order_by(Alerta.id_alerta.desc()).limit(5).all()
            
            return jsonify({
                "status": "success",
                "rol": "Técnico",
                "data": {
                    "diagnosticos_pendientes": [
                        {
                            "id_evento": ev.id_evento,
                            "falla": ev.falla_reportada,
                            "equipo": eq.codigo_inventario,
                            "fecha": ev.fecha_creacion.isoformat()
                        } for ev, eq in pendientes
                    ],
                    "sugerencias_recientes": [a.to_dict() for a in recientes]
                }
            }), 200

        #3. NIVEL USUARIO SOLICITANTE: Sus reportes y alertas vinculadas
        else:
            #estatus de reportes
            mis_reportes = Evento.query.filter_by(id_usuario=usuario_id_auth).order_by(Evento.fecha_creacion.desc()).all()
            
            #alertas de recomendacion vinculadas a sus equipos
            mis_equipos_ids = [e.id_equipo for e in usuario_auth.equipos]
            mis_alertas = Alerta.query.filter(Alerta.id_equipo.in_(mis_equipos_ids)).order_by(Alerta.fecha_programada.asc()).all()
            
            return jsonify({
                "status": "success",
                "rol": "Solicitante",
                "data": {
                    "mis_reportes": [r.to_dict() for r in mis_reportes],
                    "notificaciones_preventivas": [a.to_dict() for a in mis_alertas]
                }
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

#------------------------------------------------------------------------------



#inicializacion de servicios
#------------------------------------------------------------------------------
with app.app_context():
    try:
        #1. Sincronizar hechos con Prolog
        sincronizar_hechos_prolog()
        
        #2. Iniciar el planificador de tareas automático (30 minutos)
        if not scheduler.running:
            #agregamos la tarea recurrente
            scheduler.add_job(
                id='job_alertas_30min', 
                func=verificar_alertas_programadas, 
                trigger='interval', 
                minutes=30
            )
            scheduler.start()
            print(">>> Scheduler activo: Revisión de alertas cada 30 minutos.")
            
    except Exception as e:
        print(f"Error en el arranque: {e}")

#------------------------------------------------------------------------------

if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=5000, debug=True)