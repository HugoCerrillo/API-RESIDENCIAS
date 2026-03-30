from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
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
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "https://tu-proyecto.vercel.app"])

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
app.config['JWT_COOKIE_SECURE'] = False  # Solo enviar por HTTPS (necesario en producción)
app.config['JWT_COOKIE_CSRF_PROTECT'] = True # Protección contra ataques CSRF
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_SAMESITE'] = 'None' # Necesario si Vercel y AWS están en dominios distintos (LAX PARA LOCAL por ahora)
jwt = JWTManager(app)
db.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('correo')
    password = data.get('contraseña')

    #se busca el usuario usando el modelo
    user = Usuario.query.filter_by(correo=email).first()

    if user and user.contraseña == password:
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
    

if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=5000, debug=True)