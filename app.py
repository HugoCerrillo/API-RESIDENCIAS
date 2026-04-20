import os
from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, decode_token
import smtplib
from email.mime.text import MIMEText
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql
from datetime import timedelta
from functools import wraps  #para usar decoradores
from models import db, Usuario, Equipo, Periferico, Especificacion, CategoriaHecho, SintomaHecho, FallaHecho, Evento, Diagnostico, Mantenimiento, Alerta
from pyswip import Prolog

#---------------------------------------------------------
#----------Prolog ----------------
prolog = Prolog() #inicializamos el motor de prolog

#definimos la ruta de las reglas de prolog
base_path = os.path.dirname(__file__) #obtenemos la ruta del directorio actual
path_reglas = os.path.join(base_path, "motor_prolog", "reglas.pl").replace("\\", "/") #obtenemos la ruta de las reglas
prolog.consult(path_reglas) #cargamos las reglas en el motor de prolog

#---------------------------------------------------------

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

        # 1. limpiamos la memoria antes de procesar
        #usamos la regla que definimos en reglas.pl
        list(prolog.query("limpiar_memoria"))

        # 2. Inyectamos el historial
        for paso in historial:
            pregunta = paso['p'] #pregunta
            respuesta = paso['r'] # 'si' o 'no'
            #envolvemos el valor en comillas simples para Prolog
            prolog.assertz(f"respuesta('{pregunta}', {respuesta})")

        # 3. Ejecutamos la consulta principal
        query_str = f"siguiente_paso('{tipo}', '{sintoma}', Accion, Valor)" #consulta principal
        results = list(prolog.query(query_str)) #obtenemos los resultados

        # 4. Procesamos la respuesta
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

#------------------------------------------------------------------------------
#---- Endpoints para Modulo de Mantenimiento Preventivo/Correctivo-------------

#----------------------------------------------
@app.route('/eventos', methods=['POST'])
@jwt_required() #requiere sesion iniciada
def create_evento():
    data = request.json #obtenemos los datos en json
    id_equipo = data.get('id_equipo')
    
    try:
        #1. Buscar el equipo para cambiar su estado
        equipo = Equipo.query.get(id_equipo)
        if not equipo:
            return jsonify({"status": "error", "message": "El equipo especificado no existe"}), 404
            
        #2. Creamos el nuevo evento
        nuevo_evento = Evento(
            id_equipo=id_equipo, #equipo que se reporta
            id_usuario=data.get('id_usuario'), #técnico asignado
            falla_reportada=data.get('falla_reportada'), #falla reportada
            estado_fisico=data.get('estado_fisico'), #estado fisico del equipo
            estatus=data.get('estatus', 'Abierto'), #estatus del evento
            validado=False #por defecto inicia en False
        )
        
        #3. Automatización: Cambiamos el estado del equipo a 'En Mantenimiento'
        equipo.estado_operativo = 'En Mantenimiento'
        
        db.session.add(nuevo_evento) #agregamos el nuevo evento a la base de datos
        db.session.commit() #guardamos los cambios
        
        return jsonify({
            "status": "success",
            "message": "Evento registrado y equipo puesto en mantenimiento",
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
            if 'estatus' in data: evento.estatus = data['estatus']
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
            campos_prohibidos = ['id_equipo', 'id_usuario', 'falla_reportada', 'estatus', 'estado_fisico'] #campos prohibidos para el técnico
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
    
    #RESTRICCIÓN: El usuario solicitante no puede crear diagnósticos
    if usuario.rol == 'Usuario Solicitante':
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
        
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

if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=5000, debug=True)