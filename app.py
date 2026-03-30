from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql

# Driver para conectar Python con MySQL
pymysql.install_as_MySQLdb()

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE TU RDS ---
# Reemplaza con tus datos reales de AWS
DB_USER = "admin"
DB_PASS = "ResidenciasH2026*"
DB_HOST = "bd-resi.cixqu4s6y0t3.us-east-1.rds.amazonaws.com"
DB_NAME = "expertrack"

# Construcción de la URI de conexión
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- ENDPOINT DE PRUEBA ---
@app.route('/check-connection')
def check_connection():
    try:
        # Intentamos ejecutar una consulta simple de SQL
        # 'SELECT 1' es la forma más rápida de ver si la DB responde
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
    

#prueba de CD/CD
@app.route('/check')
def check():
    return {
        "status": "online",
        "message": "CI/CD is working perfectly!",
        "version": "1.0.1"
    }, 200

if __name__ == '__main__':
    # Puerto 5000 es el estándar de Flask
    app.run(host='0.0.0.0', port=5000, debug=True)