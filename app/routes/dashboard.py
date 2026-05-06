from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from ..models import db, Usuario, Equipo, Evento, Alerta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    usuario_id_auth = get_jwt_identity()
    usuario_auth = Usuario.query.get(usuario_id_auth)
    
    try:
        if usuario_auth.rol == 'Administrador':
            # Lógica de admin
            estados = db.session.query(Equipo.estado_operativo, func.count(Equipo.id_equipo))\
                .group_by(Equipo.estado_operativo).all()
            return jsonify({"status": "success", "rol": "Administrador", "data": {"distribucion_estados": dict(estados)}}), 200
            
        elif usuario_auth.rol == 'Técnico':
            # Lógica de técnico
            pendientes = db.session.query(Evento, Equipo).join(Equipo).filter(Evento.validado == False).all()
            return jsonify({"status": "success", "rol": "Técnico", "data": {"pendientes": len(pendientes)}}), 200
            
        else:
            # Solicitante
            mis_reportes = Evento.query.filter_by(id_usuario=usuario_id_auth).all()
            return jsonify({"status": "success", "rol": "Solicitante", "data": {"mis_reportes": len(mis_reportes)}}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
