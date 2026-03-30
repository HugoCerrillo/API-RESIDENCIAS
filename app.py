from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql
from models import db, Usuario

#driver para conectar Python con MySQL
pymysql.install_as_MySQLdb()

app = Flask(__name__)
CORS(app)

#configuracion para la bd en AWS RDS
DB_USER = "admin"
DB_PASS = "ResidenciasH2026*"
DB_HOST = "bd-resi.cixqu4s6y0t3.us-east-1.rds.amazonaws.com"
DB_NAME = "expertrack"

#construcción de la URI de conexión
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('correo')
    password = data.get('contraseña')

    #se busca el usuario usando el modelo
    user = Usuario.query.filter_by(correo=email).first()

    if user and user.contraseña == password:
        return jsonify({
            "status": "success",
            "message": f"Bienvenido, {user.nombre}",
            "user": user.to_dict()
        }), 200
    
    return jsonify({"status": "error", "message": "Credenciales inválidas"}), 401

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