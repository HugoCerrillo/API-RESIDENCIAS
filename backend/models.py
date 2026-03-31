from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'Usuario' # Nombre exacto de tu tabla en MySQL
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido_paterno = db.Column(db.String(50), nullable=False)
    apellido_materno = db.Column(db.String(50))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    # Usamos String para el Enum en SQLAlchemy para mayor compatibilidad
    rol = db.Column(db.String(50), nullable=False) 
    estatus = db.Column(db.Boolean, default=True)
    telefono = db.Column(db.String(15))
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        """Convierte el objeto a diccionario para enviarlo como JSON"""
        return {
            "id": self.id_usuario,
            "nombre": self.nombre,
            "rol": self.rol,
            "correo": self.correo
        }