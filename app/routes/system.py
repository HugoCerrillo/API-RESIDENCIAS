from flask import Blueprint, jsonify
from ..models import db
import os

system_bp = Blueprint('system', __name__)

@system_bp.route('/check-connection-bd')
def check_connection():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            "status": "success",
            "message": "¡Conexión establecida con AWS RDS!"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "No se pudo conectar a la base de datos",
            "error_detail": str(e)
        }), 500

@system_bp.route('/estado-scheduler', methods=['GET'])
def check_scheduler():
    # Importamos dinámicamente para evitar circulares
    from .. import scheduler
    return jsonify({
        "status": "success",
        "scheduler_running": scheduler.running,
        "jobs": [str(job) for job in scheduler.get_jobs()]
    }), 200
