from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Alerta, Usuario, Equipo
from ..services.alert_logic import verificar_alertas_programadas
from datetime import datetime

alerts_bp = Blueprint('alerts', __name__)

#-------------------------------------------------------------------------------------------------------------
#endpoint para crear una nueva alerta
@alerts_bp.route('/alertas', methods=['POST'])
@jwt_required()
def create_alerta():
    usuario_id_auth = get_jwt_identity() #obtenemos el id del usuario
    usuario_auth = Usuario.query.get(usuario_id_auth) #obtenemos el usuario
    
    #solo los administradores y técnicos pueden crear alertas
    if usuario_auth.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No tienes permisos para crear alertas"}), 403

    data = request.json
    id_equipo = data.get('id_equipo') # id del equipo al que se le enviara la alerta
    id_usuario = data.get('id_usuario') # id del usuario al que se le enviara la alerta
    titulo = data.get('titulo') # titulo de la alerta
    descripcion = data.get('descripcion') # descripcion de la alerta
    fecha_programada = data.get('fecha_programada') # fecha en la que se enviara la alerta

    if not all([id_equipo, id_usuario, titulo, fecha_programada]):
        return jsonify({"status": "error", "message": "Faltan campos obligatorios"}), 400

    try:
        #verificamos existencia
        if not Equipo.query.get(id_equipo):
            return jsonify({"status": "error", "message": "El equipo no existe"}), 404
        if not Usuario.query.get(id_usuario):
            return jsonify({"status": "error", "message": "El usuario responsable no existe"}), 404

        #creamos la alerta
        nueva_alerta = Alerta(
            id_equipo=id_equipo,
            id_usuario=id_usuario,
            titulo=titulo,
            descripcion=descripcion,
            fecha_programada=datetime.strptime(fecha_programada, '%Y-%m-%d').date()
        ) 
        
        db.session.add(nueva_alerta) #agregamos la alerta a la base de datos
        db.session.commit() #confirmamos la transaccion
        return jsonify({"status": "success", "message": "Alerta creada correctamente", "alerta": nueva_alerta.to_dict()}), 201
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para visualizar todas las alertas
@alerts_bp.route('/alertas', methods=['GET'])
@jwt_required()
def get_alertas():
    usuario_auth = Usuario.query.get(get_jwt_identity()) #obtenemos el id del usuario
    
    #solo los administradores y técnicos pueden ver las alertas
    if usuario_auth.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403

    try:
        #filtro por estatus
        estatus = request.args.get('estatus')
        query = db.session.query(Alerta, Equipo, Usuario).join(Equipo, Alerta.id_equipo == Equipo.id_equipo).join(Usuario, Alerta.id_usuario == Usuario.id_usuario)
        
        #aplicamos el filtro si se proporciona
        if estatus:
            query = query.filter(Alerta.estatus == estatus)
            
        #ejecutamos la consulta
        alertas = query.all()
        resultado = []
        for al, eq, us in alertas:
            al_dict = al.to_dict()
            al_dict['codigo_equipo'] = eq.codigo_inventario
            al_dict['nombre_responsable'] = f"{us.nombre} {us.apellido_paterno}"
            resultado.append(al_dict)
            
        return jsonify({"status": "success", "alertas": resultado}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para editar una alerta existente
@alerts_bp.route('/alertas/<int:id>', methods=['PUT'])
@jwt_required() #solo usuarios autenticados
def update_alerta(id):
    usuario_auth = Usuario.query.get(get_jwt_identity()) #obtenemos el id del usuario
    
    #solo los administradores y técnicos pueden editar las alertas
    if usuario_auth.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No tienes permisos"}), 403

    alerta = Alerta.query.get(id) #obtenemos la alerta
    
    #verificamos que la alerta exista
    if not alerta:
        return jsonify({"status": "error", "message": "Alerta no encontrada"}), 404

    data = request.json #obtenemos los datos de la alerta
    try:
        if 'titulo' in data: alerta.titulo = data['titulo']
        if 'descripcion' in data: alerta.descripcion = data['descripcion']
        if 'estatus' in data: alerta.estatus = data['estatus']
        if 'id_usuario' in data: alerta.id_usuario = data['id_usuario']
        if 'fecha_programada' in data: 
            alerta.fecha_programada = datetime.strptime(data['fecha_programada'], '%Y-%m-%d').date()
            
        db.session.commit() #confirmamos la transaccion
        return jsonify({"status": "success", "message": "Alerta actualizada", "alerta": alerta.to_dict()}), 200
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para eliminar una alerta (exclusivo para admin)
@alerts_bp.route('/alertas/<int:id>', methods=['DELETE'])
@jwt_required() #solo usuarios autenticados
def delete_alerta(id):
    usuario_auth = Usuario.query.get(get_jwt_identity()) #obtenemos el id del usuario
    
    #solo los administradores pueden eliminar las alertas
    if usuario_auth.rol != 'Administrador':
        return jsonify({"status": "error", "message": "Solo el administrador puede eliminar alertas"}), 403

    alerta = Alerta.query.get(id) #obtenemos la alerta
    
    #verificamos que la alerta exista
    if not alerta:
        return jsonify({"status": "error", "message": "Alerta no encontrada"}), 404

    try:
        db.session.delete(alerta) #eliminamos la alerta
        db.session.commit()
        return jsonify({"status": "success", "message": "Alerta eliminada correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
#-------------------------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------------------------
#función para verificar las alertas pendientes y enviar correos 
@alerts_bp.route('/alertas/verificar_manual', methods=['POST'])
@jwt_required()
def verificar_manual():
    #solo permitimos a técnicos o admins disparar esto
    usuario = Usuario.query.get(get_jwt_identity())
    if usuario.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    procesadas = verificar_alertas_programadas()
    return jsonify({
        "status": "success", 
        "message": f"Verificación completada. Se enviaron {procesadas} alertas.",
        "enviadas": procesadas
    }), 200
#-------------------------------------------------------------------------------------------------------------