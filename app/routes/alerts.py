from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Alerta, Usuario
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
    alertas = Alerta.query.all()
    return jsonify({"status": "success", "alertas": [a.to_dict() for a in alertas]}), 200

@alerts_bp.route('/alertas/verificar_manual', methods=['POST'])
@jwt_required()
def verificar_manual():
    count = verificar_alertas_programadas()
    return jsonify({"status": "success", "message": f"Se procesaron {count} alertas"}), 200
