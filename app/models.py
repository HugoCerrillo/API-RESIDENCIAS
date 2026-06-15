from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy() #inicializamos la base de datos

#--------------------------------------------------
#modelo de la tabla Usuario
class Usuario(db.Model):
    __tablename__ = 'Usuario' #nombre de la tabla
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido_paterno = db.Column(db.String(50), nullable=False)
    apellido_materno = db.Column(db.String(50))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    rol = db.Column(db.String(50), nullable=False) 
    estatus = db.Column(db.Boolean, default=True)
    telefono = db.Column(db.String(15))
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)
 
    #relacion con equipo como dueño del equipo
    equipos = db.relationship('Equipo', backref='propietario', cascade='all, delete-orphan', lazy=True)
    
    #relacion con Evento (como técnico asignado)
    eventos_asignados = db.relationship('Evento', backref='tecnico', cascade='all, delete-orphan', lazy=True)
    
    #relacion con Alerta (como cliente a notificar)
    alertas = db.relationship('Alerta', backref='cliente', cascade='all, delete-orphan', lazy=True)

    #clase para convertir el objeto a diccionario
    def to_dict(self):
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
#--------------------------------------------------

#--------------------------------------------------
#modelo de la tabla Equipo
class Equipo(db.Model):
    __tablename__ = 'Equipo' #nombre de la tabla
    
    id_equipo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario', ondelete='CASCADE'), nullable=False)
    tipo_equipo = db.Column(db.String(30), nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    numero_serie = db.Column(db.String(100), unique=True)
    codigo_inventario = db.Column(db.String(100), unique=True)
    estado_operativo = db.Column(db.String(20), default='Operativo') 
    area = db.Column(db.String(50))
    ubicacion = db.Column(db.String(100))
    fecha_adquisicion = db.Column(db.Date)
    en_garantia = db.Column(db.Boolean, default=False)

    #relaciones con cascada para limpieza automatica
    perifericos = db.relationship('Periferico', backref='equipo', cascade='all, delete-orphan', lazy=True)
    especificaciones = db.relationship('Especificacion', backref='equipo', cascade='all, delete-orphan', lazy=True)
    eventos = db.relationship('Evento', backref='equipo', cascade='all, delete-orphan', lazy=True)
    alertas = db.relationship('Alerta', backref='equipo', cascade='all, delete-orphan', lazy=True)

    #clase para convertir el objeto a diccionario
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
#--------------------------------------------------

#--------------------------------------------------
#modelo de la tabla Periferico
class Periferico(db.Model):
    __tablename__ = 'Periferico' #nombre de la tabla
    
    id_periferico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_equipo = db.Column(db.Integer, db.ForeignKey('Equipo.id_equipo', ondelete='CASCADE'), nullable=False)
    tipo = db.Column(db.String(30))
    marca = db.Column(db.String(50))
    numero_serie = db.Column(db.String(100))
    id_inventario_interno = db.Column(db.String(100))

    #clase para convertir el objeto a diccionario
    def to_dict(self):
        return {
            "id_periferico": self.id_periferico,
            "id_equipo": self.id_equipo,
            "tipo": self.tipo,
            "marca": self.marca,
            "numero_serie": self.numero_serie,
            "id_inventario_interno": self.id_inventario_interno
        }
#--------------------------------------------------

#--------------------------------------------------
#modelo de la tabla Especificacion
class Especificacion(db.Model):
    __tablename__ = 'Especificacion' #nombre de la tabla
    
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

    #clase para convertir el objeto a diccionario
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
#--------------------------------------------------

#--------------------------------------------------
#modelo de la tabla Evento
class Evento(db.Model):
    __tablename__ = 'Evento' #nombre de la tabla
    
    id_evento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_equipo = db.Column(db.Integer, db.ForeignKey('Equipo.id_equipo', ondelete='CASCADE'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario', ondelete='CASCADE'), nullable=False)
    falla_reportada = db.Column(db.Text)
    estado_fisico = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    validado = db.Column(db.Boolean, default=False)

    #clase para convertir el objeto a diccionario
    def to_dict(self):
        return {
            "id_evento": self.id_evento,
            "id_equipo": self.id_equipo,
            "id_usuario": self.id_usuario,
            "falla_reportada": self.falla_reportada or "",
            "estado_fisico": self.estado_fisico or "",
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "validado": self.validado
        }
#--------------------------------------------------

#--------------------------------------------------
#modelo de la tabla Diagnostico
class Diagnostico(db.Model):
    __tablename__ = 'Diagnostico' #nombre de la tabla
    
    id_evento = db.Column(db.Integer, db.ForeignKey('Evento.id_evento', ondelete='CASCADE'), primary_key=True)
    fecha_diagnostico = db.Column(db.DateTime, default=datetime.utcnow)
    log_chatbot = db.Column(db.JSON)
    resultado_preeliminar = db.Column(db.Text)
    validacion_tecnico = db.Column(db.Text)

    #relacion uno a uno con Evento
    evento = db.relationship('Evento', backref=db.backref('diagnostico', uselist=False, cascade='all, delete-orphan'))

    #clase para convertir el objeto a diccionario
    def to_dict(self):
        return {
            "id_evento": self.id_evento,
            "fecha_diagnostico": self.fecha_diagnostico.isoformat() if self.fecha_diagnostico else None,
            "log_chatbot": self.log_chatbot,
            "resultado_preeliminar": self.resultado_preeliminar or "",
            "validacion_tecnico": self.validacion_tecnico or ""
        }
#--------------------------------------------------

#--------------------------------------------------
#modelo de la tabla Mantenimiento
class Mantenimiento(db.Model):
    __tablename__ = 'Mantenimiento' #nombre de la tabla
    
    id_evento = db.Column(db.Integer, db.ForeignKey('Evento.id_evento', ondelete='CASCADE'), primary_key=True)
    tipo = db.Column(db.Enum('Preventivo', 'Correctivo'), nullable=False)
    fecha_entrega = db.Column(db.DateTime)
    descripcion_trabajo = db.Column(db.Text)
    piezas_reemplazadas = db.Column(db.Text)

    #relacion uno a uno con Evento
    evento = db.relationship('Evento', backref=db.backref('mantenimiento', uselist=False, cascade='all, delete-orphan'))

    #clase para convertir el objeto a diccionario
    def to_dict(self):
        return {
            "id_evento": self.id_evento,
            "tipo": str(self.tipo) if self.tipo is not None else None,
            "fecha_entrega": self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            "descripcion_trabajo": self.descripcion_trabajo or "",
            "piezas_reemplazadas": self.piezas_reemplazadas or ""
        }
#--------------------------------------------------

#--------------------------------------------------
#modelo de la tabla Alerta
class Alerta(db.Model):
    __tablename__ = 'Alerta' #nombre de la tabla
    
    id_alerta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario', ondelete='CASCADE'), nullable=False)
    id_equipo = db.Column(db.Integer, db.ForeignKey('Equipo.id_equipo', ondelete='CASCADE'), nullable=False)
    estatus = db.Column(db.Enum('Pendiente', 'Enviada'), default='Pendiente')
    titulo = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_programada = db.Column(db.Date)

    #clase para convertir el objeto a diccionario
    def to_dict(self):
        return {
            "id_alerta": self.id_alerta,
            "id_usuario": self.id_usuario,
            "id_equipo": self.id_equipo,
            "estatus": self.estatus.value if hasattr(self.estatus, 'value') else (self.estatus.name if hasattr(self.estatus, 'name') else str(self.estatus)) if self.estatus else None,
            "titulo": self.titulo or "",
            "descripcion": self.descripcion or "",
            "fecha_programada": self.fecha_programada.isoformat() if self.fecha_programada else None
        }
#---------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------
#MODELOS PARA LA BASE DE DATOS DE HECHOS (SISTEMA EXPERTO)
#---------------------------------------------------------------------------------------------------------------------------

#--------------------------------------------------
#modelo de la tabla CategoriaHecho
class CategoriaHecho(db.Model):
    __bind_key__ = 'hechos' #especificamos la base de datos
    __tablename__ = 'categorias' #nombre de la tabla
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

    #clase para convertir el objeto a diccionario
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre
        }
#--------------------------------------------------

#--------------------------------------------------
#modelo de la tabla SintomaHecho
class SintomaHecho(db.Model):
    __bind_key__ = 'hechos' #especificamos la base de datos
    __tablename__ = 'sintomas_iniciales' #nombre de la tabla
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)


    def to_dict(self):
        return {
            "id": self.id,
            "clave": self.clave,
            "descripcion": self.descripcion
        }
#--------------------------------------------------

#--------------------------------------------------
#modelo de la tabla FallaHecho
class FallaHecho(db.Model):
    __bind_key__ = 'hechos' #especificamos la base de datos
    __tablename__ = 'fallas' #nombre de la tabla
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_equipo = db.Column(db.Enum('PC', 'Laptop'), nullable=False)
    sintoma_id = db.Column(db.Integer, db.ForeignKey('sintomas_iniciales.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    pregunta_pista = db.Column(db.Text, nullable=False)
    diagnostico = db.Column(db.Text, nullable=False)
    recomendacion = db.Column(db.Text, nullable=False)

    #relaciones para facilitar consultas
    sintoma = db.relationship('SintomaHecho', backref='fallas', lazy=True)
    categoria = db.relationship('CategoriaHecho', backref='fallas', lazy=True)

    #clase para convertir el objeto a diccionario
    def to_dict(self):
        return {
            "id": self.id,
            "tipo_equipo": self.tipo_equipo.value if hasattr(self.tipo_equipo, 'value') else (self.tipo_equipo.name if hasattr(self.tipo_equipo, 'name') else str(self.tipo_equipo)) if self.tipo_equipo else None,
            "sintoma_id": self.sintoma_id,
            "categoria_id": self.categoria_id,
            "pregunta_pista": self.pregunta_pista,
            "diagnostico": self.diagnostico,
            "recomendacion": self.recomendacion,
            "sintoma": self.sintoma.descripcion if self.sintoma else "",
            "categoria": self.categoria.nombre if self.categoria else ""
        }
#--------------------------------------------------
