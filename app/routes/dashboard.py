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
    
    if not usuario_auth:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    try:
        # 1. Administrador: gráficas y proactividad
        if usuario_auth.rol == 'Administrador':
            stats_equipos = db.session.query(
                Equipo.estado_operativo, func.count(Equipo.id_equipo)
            ).group_by(Equipo.estado_operativo).all()
            
            total_eventos = Evento.query.count()
            eventos_validados = Evento.query.filter_by(validado=True).count()
            
            total_alertas = Alerta.query.count()
            alertas_enviadas = Alerta.query.filter_by(estatus='Enviada').count()
            
            return jsonify({
                "status": "success",
                "rol": "Administrador",
                "data": {
                    "distribucion_estados": dict(stats_equipos),
                    "frecuencia_fallas": {
                        "total": total_eventos,
                        "validados": eventos_validados,
                        "pendientes": total_eventos - eventos_validados
                    },
                    "indice_proactividad": {
                        "total_alertas": total_alertas,
                        "enviadas": alertas_enviadas,
                        "pendientes": total_alertas - alertas_enviadas
                    },
                    "resumen_general": {
                        "total_usuarios": Usuario.query.count(),
                        "total_equipos": Equipo.query.count()
                    }
                }
            }), 200

        # 2. Técnico: diagnósticos y sugerencias
        elif usuario_auth.rol == 'Técnico':
            pendientes = db.session.query(Evento, Equipo).join(
                Equipo, Evento.id_equipo == Equipo.id_equipo
            ).filter(Evento.validado == False).order_by(Evento.fecha_creacion.desc()).limit(10).all()
            
            recientes = Alerta.query.order_by(Alerta.id_alerta.desc()).limit(5).all()
            
            return jsonify({
                "status": "success",
                "rol": "Técnico",
                "data": {
                    "diagnosticos_pendientes": [
                        {
                            "id_evento": ev.id_evento,
                            "falla": ev.falla_reportada,
                            "equipo": eq.codigo_inventario,
                            "fecha": ev.fecha_creacion.isoformat()
                        } for ev, eq in pendientes
                    ],
                    "sugerencias_recientes": [a.to_dict() for a in recientes]
                }
            }), 200

        # 3. Usuario Solicitante: sus reportes y alertas vinculadas
        else:
            mis_reportes = Evento.query.filter_by(id_usuario=usuario_id_auth).order_by(Evento.fecha_creacion.desc()).all()
            mis_equipos_ids = [e.id_equipo for e in usuario_auth.equipos]
            mis_alertas = Alerta.query.filter(Alerta.id_equipo.in_(mis_equipos_ids)).order_by(Alerta.fecha_programada.asc()).all()
            
            return jsonify({
                "status": "success",
                "rol": "Solicitante",
                "data": {
                    "mis_reportes": [r.to_dict() for r in mis_reportes],
                    "notificaciones_preventivas": [a.to_dict() for a in mis_alertas]
                }
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
