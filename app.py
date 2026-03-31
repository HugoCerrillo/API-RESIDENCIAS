from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
import smtplib
from email.mime.text import MIMEText
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql
from datetime import timedelta
from models import db, Usuario

#driver para conectar Python con MySQL
pymysql.install_as_MySQLdb()

app = Flask(__name__)
#CORS(app)

# 1. CORS: Permitimos cualquier origen temporalmente para pruebas
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "https://exper-track.vercel.app"])

#configuracion para la bd en AWS RDS
DB_USER = "admin"
DB_PASS = "ResidenciasH2026*"
DB_HOST = "bd-resi.cixqu4s6y0t3.us-east-1.rds.amazonaws.com"
DB_NAME = "expertrack"

#construcción de la URI de conexión
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2) # <--- Aquí configuramos las 2 horas
app.config['JWT_SECRET_KEY'] = 'qJTJ%_(7(t(FW2ggS5X8#h!1ftm!i+'

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = True  # Solo enviar por HTTPS (necesario en producción)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False # Protección contra ataques CSRF
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_SAMESITE'] = 'None' # Necesario si Vercel y AWS están en dominios distintos (LAX PARA LOCAL por ahora)
jwt = JWTManager(app)
db.init_app(app)

# --- CONFIGURACION DE CORREO (Reemplaza con tus datos reales) ---
SMTP_SERVER = "smtp.gmail.com" 
SMTP_PORT = 587
SMTP_USER = "expertrack2026@outlook.com"
SMTP_PASSWORD = "ExperTrack*"

def enviar_correo_recuperacion(destinatario, enlace):
    msg = MIMEText(f"Haz clic en el siguiente enlace para recuperar tu contraseña:\n\n{enlace}")
    msg['Subject'] = 'Recuperación de Contraseña - ExperTrack'
    msg['From'] = SMTP_USER
    msg['To'] = destinatario

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('correo')
    password = data.get('contraseña')

    #se busca el usuario usando el modelo
    user = Usuario.query.filter_by(correo=email).first()

    if user and check_password_hash(user.contraseña, password):
        access_token = create_access_token(identity=str(user.id_usuario))        
        response = make_response(jsonify({
            "status": "success",
            "message": f"Bienvenid@ {user.nombre}",
            "user": user.to_dict()
        }))

        # Seteamos la cookie en el navegador
        set_access_cookies(response, access_token)
        
        return response, 200
    
    return jsonify({"status": "error", "message": "Correo o contraseña incorrectos"}), 401

#verificar conexiona la bd en aws
@app.route('/check-connection-bd')
def check_connection():
    try:
        db.session.execute(db.text('SELECT 1'))
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
    

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    
    # 1. Validar si el correo ya existe
    existe = Usuario.query.filter_by(correo=data.get('correo')).first()
    if existe:
        return jsonify({
            "status": "error", 
            "message": "El correo ya está registrado"
        }), 400

    try:
        # 2. Crear la nueva instancia del modelo
        nuevo_usuario = Usuario(
            nombre=data.get('nombre'),
            apellido_paterno=data.get('apellido_paterno'),
            apellido_materno=data.get('apellido_materno'),
            rol=data.get('rol'), # 'Usuario Solicitante', 'Técnico' o 'Cliente'
            telefono=data.get('telefono'),
            correo=data.get('correo'),
            contraseña=generate_password_hash(data.get('contraseña')) # Contraseña encriptada
        )

        # 3. Guardar en la base de datos de AWS
        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Usuario registrado exitosamente",
            "user": nuevo_usuario.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback() # Si algo falla, cancelamos la operación
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500
    

@app.route('/recuperar-password', methods=['POST'])
def recuperar_password():
    data = request.json
    email = data.get('correo')
    
    if not email:
        return jsonify({"status": "error", "message": "Por favor ingresa un correo electrónico"}), 400

    # 1. Buscar si el usuario existe
    user = Usuario.query.filter_by(correo=email).first()
    if not user:
        return jsonify({"status": "error", "message": "El correo no está registrado"}), 404
        
    # 2. Generar token con expiración corta (15 min) 
    reset_token = create_access_token(identity=str(user.id_usuario), expires_delta=timedelta(minutes=15))
    
    # 3. Construir enlace
    enlace = f"https://exper-track.vercel.app/reset-password?token={reset_token}"
    
    # 4. Enviar correo
    if enviar_correo_recuperacion(email, enlace):
        return jsonify({"status": "success", "message": "Se ha enviado un correo con las instrucciones"}), 200
    else:
        return jsonify({"status": "error", "message": "Hubo un problema al intentar enviar el correo. Revisa tus credenciales SMTP."}), 500

if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=5000, debug=True)