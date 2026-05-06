from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Equipo, Periferico, Especificacion, Usuario
from ..services.pdf_service import PDF_Inventario
import io
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/equipos', methods=['POST'])
@jwt_required()
def create_equipo():
    data = request.json
    try:
        nuevo_equipo = Equipo(
            id_usuario=data.get('id_usuario'),
            tipo_equipo=data.get('tipo_equipo'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            numero_serie=data.get('numero_serie'),
            codigo_inventario=data.get('codigo_inventario'),
            area=data.get('area'),
            ubicacion=data.get('ubicacion'),
            fecha_adquisicion=datetime.strptime(data.get('fecha_adquisicion'), '%Y-%m-%d').date() if data.get('fecha_adquisicion') else None,
            en_garantia=data.get('en_garantia', False)
        )
        db.session.add(nuevo_equipo)
        db.session.flush()

        if 'especificaciones' in data:
            specs = data['especificaciones']
            nueva_spec = Especificacion(
                id_equipo=nuevo_equipo.id_equipo,
                sistema_operativo=specs.get('sistema_operativo'),
                procesador=specs.get('procesador'),
                ram=specs.get('ram'),
                tipo_ram=specs.get('tipo_ram'),
                almacenamiento=specs.get('almacenamiento'),
                almacenamiento_tipo=specs.get('almacenamiento_tipo')
            )
            db.session.add(nueva_spec)

        db.session.commit()
        return jsonify({"status": "success", "message": "Equipo registrado", "equipo": nuevo_equipo.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@inventory_bp.route('/equipos', methods=['GET'])
@jwt_required()
def get_equipos():
    equipos = Equipo.query.all()
    return jsonify({"status": "success", "equipos": [e.to_dict() for e in equipos]}), 200

@inventory_bp.route('/reporte_inventario_pdf', methods=['GET'])
@jwt_required()
def export_inventario_pdf():
    try:
        usuario_id = get_jwt_identity()
        usuario_gen = Usuario.query.get(usuario_id)
        if usuario_gen.rol not in ['Administrador', 'Técnico']:
            return jsonify({"status": "error", "message": "No tienes permisos"}), 403

        equipos = Equipo.query.order_by(Equipo.codigo_inventario).all()
        from ..services.pdf_service import generar_inventario_pdf
        pdf_bytes = generar_inventario_pdf(equipos, usuario_gen)
        
        buffer = io.BytesIO(pdf_bytes)
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Inventario_ExperTrack_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@inventory_bp.route('/equipos/<int:id>', methods=['GET'])
@jwt_required()
def get_equipo(id):
    equipo = Equipo.query.get(id)
    if not equipo:
        return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
    
    spec = Especificacion.query.filter_by(id_equipo=id, es_actual=True).first()
    perifericos = Periferico.query.filter_by(id_equipo=id).all()
    
    data = equipo.to_dict()
    data['especificaciones'] = spec.to_dict() if spec else None
    data['perifericos'] = [p.to_dict() for p in perifericos]
    
    return jsonify({"status": "success", "equipo": data}), 200

@inventory_bp.route('/equipos/<int:id>/expediente_pdf', methods=['GET'])
@jwt_required()
def export_expediente_pdf(id):
    try:
        equipo = Equipo.query.get(id)
        if not equipo:
            return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
            
        spec = Especificacion.query.filter_by(id_equipo=id, es_actual=True).first()
        historial = db.session.query(Evento, Usuario, Mantenimiento)\
            .join(Usuario, Evento.id_usuario == Usuario.id_usuario)\
            .outerjoin(Mantenimiento, Evento.id_evento == Mantenimiento.id_evento)\
            .filter(Evento.id_equipo == id)\
            .order_by(Evento.fecha_creacion.desc())\
            .all()

        from ..services.pdf_service import generar_expediente_pdf
        pdf_bytes = generar_expediente_pdf(equipo, spec, historial)
        
        buffer = io.BytesIO(pdf_bytes)
        buffer.seek(0)
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f'Expediente_ID_{id}.pdf')
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
