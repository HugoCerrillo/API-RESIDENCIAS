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
 
    # Relación con Equipo (el dueño del equipo)
    equipos = db.relationship('Equipo', backref='propietario', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        """Convierte el objeto a diccionario completo para el frontend"""
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "apellido_paterno": self.apellido_paterno,
            "apellido_materno": self.apellido_materno or "",
            "rol": self.rol,
            "estatus": self.estatus,
            "telefono": self.telefono or "",
            "correo": self.correo,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None
        }

class Equipo(db.Model):
    __tablename__ = 'Equipo'
    
    id_equipo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario', ondelete='CASCADE'), nullable=False)
    tipo_equipo = db.Column(db.String(30), nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    numero_serie = db.Column(db.String(100), unique=True)
    codigo_inventario = db.Column(db.String(100), unique=True)
    estado_operativo = db.Column(db.String(20), default='Operativo') # 'Operativo' o 'Baja'
    area = db.Column(db.String(50))
    ubicacion = db.Column(db.String(100))
    fecha_adquisicion = db.Column(db.Date)
    en_garantia = db.Column(db.Boolean, default=False)

    # Relaciones con cascada para limpieza automática
    perifericos = db.relationship('Periferico', backref='equipo', cascade='all, delete-orphan', lazy=True)
    especificaciones = db.relationship('Especificacion', backref='equipo', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            "id_equipo": self.id_equipo,
            "id_usuario": self.id_usuario,
            "tipo_equipo": self.tipo_equipo,
            "marca": self.marca,
            "modelo": self.modelo,
            "numero_serie": self.numero_serie,
            "codigo_inventario": self.codigo_inventario,
            "estado_operativo": self.estado_operativo,
            "area": self.area,
            "ubicacion": self.ubicacion,
            "fecha_adquisicion": self.fecha_adquisicion.isoformat() if self.fecha_adquisicion else None,
            "en_garantia": self.en_garantia
        }

class Periferico(db.Model):
    __tablename__ = 'Periferico'
    
    id_periferico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_equipo = db.Column(db.Integer, db.ForeignKey('Equipo.id_equipo', ondelete='CASCADE'), nullable=False)
    tipo = db.Column(db.String(30))
    marca = db.Column(db.String(50))
    numero_serie = db.Column(db.String(100))
    id_inventario_interno = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id_periferico": self.id_periferico,
            "id_equipo": self.id_equipo,
            "tipo": self.tipo,
            "marca": self.marca,
            "numero_serie": self.numero_serie,
            "id_inventario_interno": self.id_inventario_interno
        }

class Especificacion(db.Model):
    __tablename__ = 'Especificacion'
    
    id_especificacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_equipo = db.Column(db.Integer, db.ForeignKey('Equipo.id_equipo', ondelete='CASCADE'), nullable=False)
    sistema_operativo = db.Column(db.String(50))
    procesador = db.Column(db.String(100))
    ram = db.Column(db.String(50))
    tipo_ram = db.Column(db.String(50))
    almacenamiento = db.Column(db.String(100))
    almacenamiento_tipo = db.Column(db.String(50))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    es_actual = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id_especificacion": self.id_especificacion,
            "id_equipo": self.id_equipo,
            "sistema_operativo": self.sistema_operativo,
            "procesador": self.procesador,
            "ram": self.ram,
            "tipo_ram": self.tipo_ram,
            "almacenamiento": self.almacenamiento,
            "almacenamiento_tipo": self.almacenamiento_tipo,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "es_actual": self.es_actual
        }
