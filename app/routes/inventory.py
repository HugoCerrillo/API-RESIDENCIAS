from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Equipo, Periferico, Especificacion, Usuario, Evento, Mantenimiento
from ..services.pdf_service import PDF_Inventario
import io
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/equipos', methods=['POST'])
@jwt_required()
def create_equipo():
    usuario_creador = Usuario.query.get(get_jwt_identity())
    data = request.json
    
    # Lógica de propietario original
    id_propietario = usuario_creador.id_usuario
    if usuario_creador.rol in ['Administrador', 'Técnico'] and 'id_usuario' in data:
        id_propietario = data['id_usuario']

    try:
        nuevo_equipo = Equipo(
            id_usuario=id_propietario,
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
        db.session.flush() # Para obtener el id_equipo antes del commit

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
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    
    # Consulta base con join al dueño
    query = db.session.query(Equipo, Usuario.nombre.label('dueño'))\
              .join(Usuario, Equipo.id_usuario == Usuario.id_usuario)
    
    if usuario.rol == 'Usuario Solicitante':
        query = query.filter(Equipo.id_usuario == usuario.id_usuario)
    
    resultados = query.all()
    lista_equipos = []
    
    for eq, dueño in resultados:
        d = eq.to_dict()
        d['dueño'] = dueño
        
        # Agregamos la especificación actual
        spec = Especificacion.query.filter_by(id_equipo=eq.id_equipo, es_actual=True).first()
        d['especificacion'] = spec.to_dict() if spec else None
        
        # Agregamos los periféricos (importante para la matriz)
        d['perifericos'] = [p.to_dict() for p in eq.perifericos]
        
        lista_equipos.append(d)
        
    return jsonify({
        "status": "success",
        "equipos": lista_equipos
    }), 200

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
    
    return jsonify({
        "status": "success", 
        "equipo": equipo.to_dict(),
        "especificacion": spec.to_dict() if spec else None,
        "perifericos": [p.to_dict() for p in perifericos],
        "dueño": equipo.propietario.nombre if equipo.propietario else "Desconocido"
    }), 200

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

@inventory_bp.route('/equipos/<int:id>', methods=['PUT'])
@jwt_required()
def update_equipo(id):
    usuario = Usuario.query.get(get_jwt_identity())
    if usuario.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No tienes permisos"}), 403
        
    equipo = Equipo.query.get(id)
    if not equipo:
        return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
        
    data = request.json
    try:
        # 1. Datos básicos
        campos = ['id_usuario', 'marca', 'modelo', 'tipo_equipo', 'numero_serie', 'codigo_inventario', 'area', 'ubicacion', 'estado_operativo', 'en_garantia']
        for campo in campos:
            if campo in data: setattr(equipo, campo, data[campo])

        # 2. Lógica de Versionado de Especificaciones
        if 'especificaciones' in data:
            new_specs = data['especificaciones']
            current_spec = Especificacion.query.filter_by(id_equipo=id, es_actual=True).first()
            
            should_create = not current_spec
            if current_spec:
                for f in ['sistema_operativo', 'procesador', 'ram', 'tipo_ram', 'almacenamiento', 'almacenamiento_tipo']:
                    if new_specs.get(f) != getattr(current_spec, f):
                        should_create = True
                        break
            
            if should_create:
                if current_spec: current_spec.es_actual = False
                nueva_version = Especificacion(
                    id_equipo=id,
                    sistema_operativo=new_specs.get('sistema_operativo'),
                    procesador=new_specs.get('procesador'),
                    ram=new_specs.get('ram'),
                    tipo_ram=new_specs.get('tipo_ram'),
                    almacenamiento=new_specs.get('almacenamiento'),
                    almacenamiento_tipo=new_specs.get('almacenamiento_tipo'),
                    es_actual=True
                )
                db.session.add(nueva_version)

        if 'perifericos' in data:
            Periferico.query.filter_by(id_equipo=id).delete()
            for p in data['perifericos']:
                db.session.add(Periferico(
                    id_equipo=id, tipo=p.get('tipo'), marca=p.get('marca'),
                    numero_serie=p.get('numero_serie'), id_inventario_interno=p.get('id_inventario_interno')
                ))

        db.session.commit()
        return jsonify({"status": "success", "message": "Equipo actualizado"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@inventory_bp.route('/equipos/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_equipo(id):
    usuario = Usuario.query.get(get_jwt_identity())
    if usuario.rol != 'Administrador':
        return jsonify({"status": "error", "message": "Solo el administrador puede eliminar"}), 403
        
    equipo = Equipo.query.get(id)
    if not equipo:
        return jsonify({"status": "error", "message": "No encontrado"}), 404
        
    try:
        db.session.delete(equipo)
        db.session.commit()
        return jsonify({"status": "success", "message": "Equipo eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
