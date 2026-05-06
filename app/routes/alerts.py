from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Alerta, Usuario, Equipo
from ..services.alert_logic import verificar_alertas_programadas
from datetime import datetime

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/alertas', methods=['POST'])
@jwt_required()
def create_alerta():
    data = request.json
    try:
        nueva_alerta = Alerta(
            id_usuario=data.get('id_usuario'),
            id_equipo=data.get('id_equipo'),
            titulo=data.get('titulo'),
            descripcion=data.get('descripcion'),
            fecha_programada=datetime.strptime(data.get('fecha_programada'), '%Y-%m-%d').date()
        )
        db.session.add(nueva_alerta)
        db.session.commit()
        return jsonify({"status": "success", "message": "Alerta creada", "alerta": nueva_alerta.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@alerts_bp.route('/alertas', methods=['GET'])
@jwt_required()
def get_alertas():
    usuario_id = get_jwt_identity()
    usuario_auth = Usuario.query.get(usuario_id)
    
    if not usuario_auth or usuario_auth.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403

    estatus = request.args.get('estatus')
    try:
        query = db.session.query(Alerta, Equipo, Usuario)\
            .join(Equipo, Alerta.id_equipo == Equipo.id_equipo)\
            .join(Usuario, Alerta.id_usuario == Usuario.id_usuario)
        
        # Si no se pide un estatus específico, mostramos solo las Pendientes
        if estatus:
            query = query.filter(Alerta.estatus == estatus)
        else:
            query = query.filter(Alerta.estatus == 'Pendiente')
            
        alertas = query.all()
        resultado = []
        for al, eq, us in alertas:
            al_dict = al.to_dict()
            al_dict['codigo_equipo'] = eq.codigo_inventario
            al_dict['nombre_responsable'] = f"{us.nombre} {us.apellido_paterno}"
            resultado.append(al_dict)
            
        return jsonify({"status": "success", "alertas": resultado}), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc()) # Esto saldrá en la terminal de la EC2
        return jsonify({
            "status": "error", 
            "message": "Error interno en el servidor",
            "error_detail": str(e)
        }), 500

@alerts_bp.route('/alertas/verificar_manual', methods=['POST'])
@jwt_required()
def verificar_manual():
    count = verificar_alertas_programadas()
    return jsonify({"status": "success", "message": f"Se procesaron {count} alertas"}), 200

@alerts_bp.route('/alertas/<int:id>', methods=['PUT'])
@jwt_required()
def update_alerta(id):
    alerta = Alerta.query.get(id)
    if not alerta:
        return jsonify({"status": "error", "message": "Alerta no encontrada"}), 404
        
    data = request.json
    try:
        if 'titulo' in data: alerta.titulo = data['titulo']
        if 'descripcion' in data: alerta.descripcion = data['descripcion']
        if 'fecha_programada' in data:
            alerta.fecha_programada = datetime.strptime(data['fecha_programada'], '%Y-%m-%d').date()
        if 'estatus' in data: alerta.estatus = data['estatus']
            
        db.session.commit()
        return jsonify({"status": "success", "message": "Alerta actualizada", "alerta": alerta.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@alerts_bp.route('/alertas/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_alerta(id):
    alerta = Alerta.query.get(id)
    if not alerta:
        return jsonify({"status": "error", "message": "Alerta no encontrada"}), 404
        
    try:
        db.session.delete(alerta)
        db.session.commit()
        return jsonify({"status": "success", "message": "Alerta eliminada"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
