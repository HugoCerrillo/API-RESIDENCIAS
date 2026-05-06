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
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    evento = Evento.query.get(id)
    
    if not evento:
        return jsonify({"status": "error", "message": "Evento no encontrado"}), 404
        
    data = request.json
    try:
        # 1. Lógica para Administrador (Edición total)
        if usuario.rol == 'Administrador':
            if 'falla_reportada' in data: evento.falla_reportada = data['falla_reportada']
            if 'estado_fisico' in data: evento.estado_fisico = data['estado_fisico']
            if 'validado' in data:
                evento.validado = data['validado']
                # Si el admin lo valida, el equipo vuelve a estar Operativo
                if data['validado'] == True and evento.equipo:
                    evento.equipo.estado_operativo = 'Operativo'
                elif data['validado'] == False and evento.equipo:
                    evento.equipo.estado_operativo = 'En Mantenimiento'

        # 2. Lógica para Técnico (Validación)
        elif usuario.rol == 'Técnico':
            if 'validado' in data:
                # Solo puede validar (pasar de False a True)
                if evento.validado == False and data['validado'] == True:
                    evento.validado = True
                    if evento.equipo:
                        evento.equipo.estado_operativo = 'Operativo'
                else:
                    return jsonify({"status": "error", "message": "Un técnico solo puede validar un evento"}), 403
            else:
                return jsonify({"status": "error", "message": "No se enviaron cambios permitidos"}), 400
        else:
            return jsonify({"status": "error", "message": "Sin permisos"}), 403

        db.session.commit()
        return jsonify({"status": "success", "message": "Evento actualizado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

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
    usuario = Usuario.query.get(get_jwt_identity())
    if usuario.rol == 'Usuario Solicitante':
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
        
    try:
        mantenimientos = Mantenimiento.query.all()
        return jsonify({"status": "success", "mantenimientos": [m.to_dict() for m in mantenimientos]}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@technical_record_bp.route('/diagnosticos', methods=['GET'])
@jwt_required()
def get_diagnosticos():
    usuario = Usuario.query.get(get_jwt_identity())
    if usuario.rol == 'Usuario Solicitante':
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
        
    try:
        diagnosticos = Diagnostico.query.all()
        return jsonify({"status": "success", "diagnosticos": [d.to_dict() for d in diagnosticos]}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@technical_record_bp.route('/diagnosticos/<int:id_evento>', methods=['PUT'])
@jwt_required()
def update_diagnostico(id_evento):
    usuario = Usuario.query.get(get_jwt_identity())
    if usuario.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No tienes permisos"}), 403

    diag = Diagnostico.query.get(id_evento)
    if not diag:
        return jsonify({"status": "error", "message": "Diagnóstico no encontrado"}), 404
        
    data = request.json
    try:
        if 'log_chatbot' in data: diag.log_chatbot = data['log_chatbot']
        if 'resultado_preeliminar' in data: diag.resultado_preeliminar = data['resultado_preeliminar']
        if 'validacion_tecnico' in data: diag.validacion_tecnico = data['validacion_tecnico']
        
        db.session.commit()
        return jsonify({"status": "success", "message": "Diagnóstico actualizado", "diagnostico": diag.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@technical_record_bp.route('/mantenimientos/<int:id_evento>', methods=['PUT'])
@jwt_required()
def update_mantenimiento(id_evento):
    usuario = Usuario.query.get(get_jwt_identity())
    if usuario.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No tienes permisos"}), 403

    mant = Mantenimiento.query.get(id_evento)
    if not mant:
        return jsonify({"status": "error", "message": "Mantenimiento no encontrado"}), 404
        
    data = request.json
    try:
        if 'tipo' in data: mant.tipo = data['tipo']
        if 'fecha_entrega' in data:
            # Si viene como string, convertir a datetime
            if isinstance(data['fecha_entrega'], str):
                mant.fecha_entrega = datetime.strptime(data['fecha_entrega'], '%Y-%m-%d %H:%M:%S')
        if 'descripcion_trabajo' in data: mant.descripcion_trabajo = data['descripcion_trabajo']
        if 'piezas_reemplazadas' in data: mant.piezas_reemplazadas = data['piezas_reemplazadas']
        
        db.session.commit()
        return jsonify({"status": "success", "message": "Mantenimiento actualizado", "mantenimiento": mant.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
