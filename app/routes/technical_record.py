from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Evento, Diagnostico, Mantenimiento, Usuario, Equipo
from datetime import datetime

technical_record_bp = Blueprint('technical_record', __name__)

from sqlalchemy import func

# --- EVENTOS ---
@technical_record_bp.route('/eventos', methods=['POST'])
@jwt_required()
def create_evento():
    usuario_id_creador = get_jwt_identity()
    usuario_creador = Usuario.query.get(usuario_id_creador)
    
    data = request.json
    id_equipo = data.get('id_equipo')
    id_tecnico_asignado = None
    
    try:
        # 1. Determinamos el técnico asignado
        if usuario_creador.rol == 'Técnico':
            id_tecnico_asignado = usuario_id_creador
        elif usuario_creador.rol == 'Usuario Solicitante':
            tecnico_menos_ocupado = db.session.query(Usuario)\
                .outerjoin(Evento, (Usuario.id_usuario == Evento.id_usuario) & (Evento.validado == False))\
                .filter(Usuario.rol == 'Técnico')\
                .group_by(Usuario.id_usuario)\
                .order_by(func.count(Evento.id_evento).asc(), Usuario.id_usuario.asc())\
                .first()
            
            if not tecnico_menos_ocupado:
                return jsonify({"status": "error", "message": "No hay técnicos disponibles"}), 500
            id_tecnico_asignado = tecnico_menos_ocupado.id_usuario
        else:
            return jsonify({"status": "error", "message": "Tu rol no permite generar eventos"}), 403

        # 2. Actualizar estado del equipo
        equipo = Equipo.query.get(id_equipo)
        if not equipo:
            return jsonify({"status": "error", "message": "Equipo no existe"}), 404
        equipo.estado_operativo = 'En Mantenimiento'

        # 3. Crear evento
        nuevo_evento = Evento(
            id_equipo=id_equipo,
            id_usuario=id_tecnico_asignado,
            falla_reportada=data.get('falla_reportada'),
            estado_fisico=data.get('estado_fisico'),
            validado=False
        )
        db.session.add(nuevo_evento)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": f"Evento asignado al técnico ID: {id_tecnico_asignado}",
            "evento": nuevo_evento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@technical_record_bp.route('/eventos', methods=['GET'])
@jwt_required()
def get_eventos():
    eventos = Evento.query.order_by(Evento.fecha_creacion.desc()).all()
    return jsonify({"status": "success", "eventos": [e.to_dict() for e in eventos]}), 200

@technical_record_bp.route('/eventos/<int:id>', methods=['PUT'])
@jwt_required()
def update_evento(id):
    evento = Evento.query.get(id)
    if not evento: return jsonify({"status": "error", "message": "No encontrado"}), 404
    data = request.json
    if 'validado' in data: evento.validado = data['validado']
    db.session.commit()
    return jsonify({"status": "success", "evento": evento.to_dict()}), 200

# --- DIAGNÓSTICOS ---
@technical_record_bp.route('/diagnosticos', methods=['POST'])
@jwt_required()
def create_diagnostico():
    data = request.json
    try:
        nuevo_diag = Diagnostico(
            id_evento=data.get('id_evento'),
            log_chatbot=data.get('log_chatbot'),
            resultado_preeliminar=data.get('resultado_preeliminar'),
            validacion_tecnico=data.get('validacion_tecnico')
        )
        db.session.add(nuevo_diag)
        db.session.commit()
        return jsonify({"status": "success", "diagnostico": nuevo_diag.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- MANTENIMIENTOS ---
@technical_record_bp.route('/mantenimientos', methods=['POST'])
@jwt_required()
def create_mantenimiento():
    data = request.json
    try:
        nuevo_mant = Mantenimiento(
            id_evento=data.get('id_evento'),
            tipo=data.get('tipo'),
            fecha_entrega=datetime.utcnow(),
            descripcion_trabajo=data.get('descripcion_trabajo'),
            piezas_reemplazadas=data.get('piezas_reemplazadas')
        )
        db.session.add(nuevo_mant)
        db.session.commit()
        return jsonify({"status": "success", "mantenimiento": nuevo_mant.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@technical_record_bp.route('/mantenimientos', methods=['GET'])
@jwt_required()
def get_mantenimientos():
    mantenimientos = Mantenimiento.query.all()
    return jsonify({"status": "success", "mantenimientos": [m.to_dict() for m in mantenimientos]}), 200

@technical_record_bp.route('/diagnosticos', methods=['GET'])
@jwt_required()
def get_diagnosticos():
    diagnosticos = Diagnostico.query.all()
    return jsonify({"status": "success", "diagnosticos": [d.to_dict() for d in diagnosticos]}), 200

@technical_record_bp.route('/diagnosticos/<int:id_evento>', methods=['PUT'])
@jwt_required()
def update_diagnostico(id_evento):
    diag = Diagnostico.query.get(id_evento)
    if not diag: return jsonify({"status": "error", "message": "No encontrado"}), 404
    data = request.json
    if 'validacion_tecnico' in data: diag.validacion_tecnico = data['validacion_tecnico']
    db.session.commit()
    return jsonify({"status": "success", "diagnostico": diag.to_dict()}), 200

@technical_record_bp.route('/mantenimientos/<int:id_evento>', methods=['PUT'])
@jwt_required()
def update_mantenimiento(id_evento):
    mant = Mantenimiento.query.get(id_evento)
    if not mant: return jsonify({"status": "error", "message": "No encontrado"}), 404
    data = request.json
    if 'descripcion_trabajo' in data: mant.descripcion_trabajo = data['descripcion_trabajo']
    if 'piezas_reemplazadas' in data: mant.piezas_reemplazadas = data['piezas_reemplazadas']
    db.session.commit()
    return jsonify({"status": "success", "mantenimiento": mant.to_dict()}), 200
