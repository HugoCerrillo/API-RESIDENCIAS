from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Evento, Diagnostico, Mantenimiento, Usuario, Equipo
from datetime import datetime
from sqlalchemy import func

technical_record_bp = Blueprint('technical_record', __name__)


#------------------------------------------------------------------------------------------------------------
#endpoint para crear eventos
@technical_record_bp.route('/eventos', methods=['POST'])
@jwt_required()
def create_evento():
    usuario_id_creador = get_jwt_identity() #id del usuario que crea el evento
    usuario_creador = Usuario.query.get(usuario_id_creador) #obtenemos el usuario
    
    data = request.json #obtenemos los datos en json
    id_equipo = data.get('id_equipo')
    
    #id final del técnico que se asignará al evento
    id_tecnico_asignado = None
    
    try:
        #1. determinamos el tecnico asignado
        if usuario_creador.rol == 'Técnico':
            #si el creador es tecnico, se lo asigna a sí mismo
            id_tecnico_asignado = usuario_id_creador
        
        elif usuario_creador.rol == 'Usuario Solicitante':
            #si es solicitante, buscamos al técnico con menos eventos abiertos (validado=False)
            tecnico_menos_ocupado = db.session.query(
                Usuario
            ).outerjoin(Evento, (Usuario.id_usuario == Evento.id_usuario) & (Evento.validado == False))\
             .filter(Usuario.rol == 'Técnico')\
             .group_by(Usuario.id_usuario)\
             .order_by(func.count(Evento.id_evento).asc(), Usuario.id_usuario.asc())\
             .first()
            
            if not tecnico_menos_ocupado:
                return jsonify({"status": "error", "message": "No hay técnicos registrados en el sistema para asignar el evento"}), 500
            
            id_tecnico_asignado = tecnico_menos_ocupado.id_usuario #obtenemos el id del técnico
        
        else:
            #Administradores u otros roles no generan eventos
            return jsonify({"status": "error", "message": "Tu rol no tiene permisos para generar eventos"}), 403

        #2. buscar el equipo para cambiar su estado
        equipo = Equipo.query.get(id_equipo)
        if not equipo:
            return jsonify({"status": "error", "message": "El equipo especificado no existe"}), 404
            
        #3. creamos el nuevo evento
        nuevo_evento = Evento(
            id_equipo=id_equipo, #equipo que se reporta
            id_usuario=id_tecnico_asignado, #técnico asignado automáticamente
            falla_reportada=data.get('falla_reportada'), #falla reportada
            estado_fisico=data.get('estado_fisico'), #estado fisico del equipo
            validado=False #por defecto inicia en False
        )
        
        #4. automatizacion: cambiamos el estado del equipo a 'En Mantenimiento'
        equipo.estado_operativo = 'En Mantenimiento'
        
        db.session.add(nuevo_evento) #agregamos el nuevo evento a la base de datos
        db.session.commit() #guardamos los cambios
        
        return jsonify({
            "status": "success",
            "message": f"Evento registrado y asignado al técnico ID: {id_tecnico_asignado}",
            "evento": nuevo_evento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500
#------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------
#endpoint para visualizar todos los eventos registrados
@technical_record_bp.route('/eventos', methods=['GET'])
@jwt_required()
def get_eventos():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    
    #RESTRICCIÓN: El usuario solicitante no puede ver el listado de eventos
    if usuario.rol == 'Usuario Solicitante':
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
        
    try:
        eventos = Evento.query.all() #traemos todos los eventos
        return jsonify({
            "status": "success",
            "eventos": [e.to_dict() for e in eventos] #convertimos los eventos a diccionario
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
#------------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------------
#endpoint para actualizar un evento (con restricciones de rol)
@technical_record_bp.route('/eventos/<int:id>', methods=['PUT'])
@jwt_required()
def update_evento(id):
    usuario_id = get_jwt_identity() #id del usuario en sesion
    usuario = Usuario.query.get(usuario_id) #datos del usuario
    
    evento = Evento.query.get(id) #buscamos el evento
    if not evento:
        return jsonify({"status": "error", "message": "Evento no encontrado"}), 404
        
    data = request.json #datos a actualizar
    
    try:
        #LOGICA PARA ADMINISTRADOR: puede modificar todo
        if usuario.rol == 'Administrador':
            if 'id_equipo' in data: evento.id_equipo = data['id_equipo']
            if 'id_usuario' in data: evento.id_usuario = data['id_usuario']
            if 'falla_reportada' in data: evento.falla_reportada = data['falla_reportada']
            if 'estado_fisico' in data: evento.estado_fisico = data['estado_fisico']
            
            #Automatización al validar 
            if 'validado' in data:
                #Si se quiere validar (pasar a True)
                if data['validado'] == True and evento.validado == False: #si el evento no está validado y se quiere validar
                    evento.validado = True #se valida el evento
                    
                    #CONSULTA DE SEGURIDAD: hay otros eventos sin validar para este equipo?
                    pendientes = Evento.query.filter(
                        Evento.id_equipo == evento.id_equipo, 
                        Evento.validado == False,
                        Evento.id_evento != evento.id_evento #Excluimos el actual por seguridad
                    ).count() #contamos los eventos sin validar
                    
                    if pendientes == 0: #si no hay eventos sin validar
                        if evento.equipo: #si el evento tiene equipo
                            evento.equipo.estado_operativo = 'Operativo' #el equipo se pone como operativo
                    else:
                        if evento.equipo: #si el evento tiene equipo
                            evento.equipo.estado_operativo = 'En Mantenimiento' #el equipo se pone como en mantenimiento
                else:
                    evento.validado = data['validado'] #se actualiza el validado
            
        #LOGICA PARA TÉCNICO: solo puede validar
        elif usuario.rol == 'Técnico':
            #verificamos que NO intente cambiar otros atributos
            campos_prohibidos = ['id_equipo', 'id_usuario', 'falla_reportada', 'estado_fisico']
            for campo in campos_prohibidos: #recorremos los campos prohibidos
                if campo in data: #si el campo está en los datos
                    return jsonify({
                        "status": "error", 
                        "message": "Como técnico, no tienes permisos para modificar otros atributos del evento"
                    }), 403
            
            #verificamos la condicion de validado (de False a True)
            if 'validado' in data:
                if evento.validado == False and data['validado'] == True: #si el evento no está validado y se quiere validar
                    evento.validado = True #se valida el evento
                    
                    #CONSULTA DE SEGURIDAD: ¿Hay otros eventos sin validar para este equipo?
                    pendientes = Evento.query.filter(
                        Evento.id_equipo == evento.id_equipo, 
                        Evento.validado == False,
                        Evento.id_evento != evento.id_evento #excluimos el actual por seguridad
                    ).count() #contamos los eventos sin validar
                    
                    if pendientes == 0: #si no hay eventos sin validar
                        if evento.equipo: #si el evento tiene equipo
                            evento.equipo.estado_operativo = 'Operativo' #el equipo se pone como operativo
                    else:
                        if evento.equipo: #si el evento tiene equipo
                            evento.equipo.estado_operativo = 'En Mantenimiento' #el equipo se pone como en mantenimiento
                else:
                    return jsonify({"status": "error", "message": "Un técnico solo puede validar un evento (pasar de False a True)"}), 403
            else:
                return jsonify({"status": "error", "message": "No se enviaron cambios permitidos para el técnico"}), 400
        
        else:
            return jsonify({"status": "error", "message": "No tienes permisos para actualizar eventos"}), 403

        db.session.commit() #confirmamos la transaccion
        return jsonify({
            "status": "success",
            "message": "Evento actualizado correctamente",
            "evento": evento.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
#------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------
#endpoint para crear un diagnóstico nuevo
@technical_record_bp.route('/diagnosticos', methods=['POST'])
@jwt_required()
def create_diagnostico():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
        
    data = request.json #obtenemos los datos en json
    id_evento = data.get('id_evento') #obtenemos el id del evento
    
    if not id_evento:
        return jsonify({"status": "error", "message": "id_evento es requerido"}), 400
        
    try:
        #1. Verificar que el evento exista
        evento = Evento.query.get(id_evento) #obtenemos el evento
        if not evento:
            return jsonify({"status": "error", "message": "El evento no existe"}), 404
            
        #2. Verificar que no exista ya un diagnóstico para este evento (Relación 1:1)
        existe = Diagnostico.query.get(id_evento) #verificamos si ya existe un diagnóstico para este evento
        if existe:
            return jsonify({
                "status": "error", 
                "message": "Ya existe un diagnóstico registrado para este evento. Usa PUT para editarlo."
            }), 400
            
        #3. Crear el diagnóstico
        nuevo_diagnostico = Diagnostico(
            id_evento=id_evento,
            log_chatbot=data.get('log_chatbot'),
            resultado_preeliminar=data.get('resultado_preeliminar'),
            validacion_tecnico=data.get('validacion_tecnico')
        )
        
        db.session.add(nuevo_diagnostico) #agregamos el nuevo diagnostico a la base de datos
        db.session.commit() #confirmamos la transaccion
        
        return jsonify({
            "status": "success",
            "message": "Diagnóstico registrado correctamente",
            "diagnostico": nuevo_diagnostico.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500
#------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------
#endpoint para visualizar los diagnosticos registrados
@technical_record_bp.route('/diagnosticos', methods=['GET'])
@jwt_required()
def get_diagnosticos():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    
    #RESTRICCIÓN: El usuario solicitante no puede ver el listado de diagnosticos
    if usuario.rol == 'Usuario Solicitante':
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
        
    try:
        diagnosticos = Diagnostico.query.all() #traemos todos los diagnosticos
        return jsonify({
            "status": "success",
            "diagnosticos": [d.to_dict() for d in diagnosticos] #convertimos los diagnosticos a diccionario
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
#------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------
#endpoint para editar un diagnostico (solo técnicos y administradores)
@technical_record_bp.route('/diagnosticos/<int:id_evento>', methods=['PUT'])
@jwt_required()
def update_diagnostico(id_evento):
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #RESTRICCIÓN: Solo Admins o Técnicos pueden editar el diagnóstico
    if usuario.rol not in ['Administrador', 'Técnico']:
        return jsonify({
            "status": "error", 
            "message": "No tienes permisos para editar diagnósticos técnicos"
        }), 403
    
    #1. Verificar que el evento asociado exista y su estado de validación
    evento = Evento.query.get(id_evento)
    if not evento:
        return jsonify({"status": "error", "message": "El evento asociado no existe"}), 404
        
    #2. Si el evento ya está VALIDADO (True), solo el Admin puede seguir editando
    if evento.validado == True and usuario.rol != 'Administrador':
        return jsonify({
            "status": "error", 
            "message": "Este evento ya ha sido validado. Solo un administrador puede realizar cambios en el diagnóstico."
        }), 403
        
    diagnostico = Diagnostico.query.get(id_evento)
    if not diagnostico:
        return jsonify({"status": "error", "message": "Diagnóstico no encontrado"}), 404
        
    data = request.json #obtenemos los datos en json
    
    try:
        if 'log_chatbot' in data: diagnostico.log_chatbot = data['log_chatbot'] #actualizamos el log del chatbot
        if 'resultado_preeliminar' in data: diagnostico.resultado_preeliminar = data['resultado_preeliminar'] #actualizamos el resultado preliminar
        if 'validacion_tecnico' in data: diagnostico.validacion_tecnico = data['validacion_tecnico'] #actualizamos la validacion tecnica
        
        db.session.commit() #confirmamos la transaccion
        return jsonify({
            "status": "success",
            "message": "Diagnóstico actualizado correctamente",
            "diagnostico": diagnostico.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500
#------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------
#endpoint para crear un mantenimiento (Admin y Técnico)
@technical_record_bp.route('/mantenimientos', methods=['POST'])
@jwt_required()
def create_mantenimiento():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #RESTRICCIÓN: Solo Técnico o Administrador pueden registrar el mantenimiento
    if usuario.rol not in ['Técnico', 'Administrador']:
        return jsonify({
            "status": "error", 
            "message": "Solo el técnico asignado o el administrador pueden registrar el mantenimiento final"
        }), 403
        
    data = request.json #obtenemos los datos en json
    id_evento = data.get('id_evento') #obtenemos el id del evento
    
    if not id_evento:
        return jsonify({"status": "error", "message": "id_evento es requerido"}), 400
        
    try:
        #1. Verificar existencia del evento
        evento = Evento.query.get(id_evento)
        if not evento:
            return jsonify({"status": "error", "message": "El evento no existe"}), 404
            
        #2. Verificar duplicados
        existe = Mantenimiento.query.get(id_evento) #verificamos si ya existe un mantenimiento para este evento
        if existe:
            return jsonify({
                "status": "error", 
                "message": "Ya existe un registro de mantenimiento para este evento"
            }), 400
            
        #3. Parsear fecha de entrega de forma segura
        fecha_raw = data.get('fecha_entrega')
        fecha_parsed = None
        if fecha_raw:
            try:
                fecha_raw_clean = fecha_raw.split('.')[0].replace('Z', '')
                if 'T' in fecha_raw_clean:
                    fecha_parsed = datetime.fromisoformat(fecha_raw_clean)
                else:
                    fecha_parsed = datetime.strptime(fecha_raw_clean, '%Y-%m-%d')
            except ValueError:
                fecha_parsed = None

        #4. Crear mantenimiento
        nuevo_mantenimiento = Mantenimiento(
            id_evento=id_evento,
            tipo=data.get('tipo'), # 'Preventivo' o 'Correctivo'
            fecha_entrega=fecha_parsed,
            descripcion_trabajo=data.get('descripcion_trabajo'),
            piezas_reemplazadas=data.get('piezas_reemplazadas')
        )
        
        db.session.add(nuevo_mantenimiento) #agregamos el nuevo mantenimiento a la base de datos
        db.session.commit() #confirmamos la transaccion
        
        return jsonify({
            "status": "success",
            "message": "Mantenimiento registrado con éxito",
            "mantenimiento": nuevo_mantenimiento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500
#------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------
#endpoint para visualizar mantenimientos (Admin y Técnico)
@technical_record_bp.route('/mantenimientos', methods=['GET'])
@jwt_required()
def get_mantenimientos():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #RESTRICCIÓN: Usuario Solicitante no puede ver esta lista
    if usuario.rol == 'Usuario Solicitante':
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
        
    try:
        mantenimientos = Mantenimiento.query.all() #traemos todos los mantenimientos
        return jsonify({
            "status": "success",
            "mantenimientos": [m.to_dict() for m in mantenimientos] #convertimos los mantenimientos a diccionario
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
#------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------
#endpoint para editar mantenimientos (Administrador y Técnico bajo condición)
@technical_record_bp.route('/mantenimientos/<int:id_evento>', methods=['PUT'])
@jwt_required()
def update_mantenimiento(id_evento):
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #1. Verificar permisos basicos de rol
    if usuario.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No tienes permisos para editar mantenimientos"}), 403
        
    #2. Verificar que el evento asociado exista y su estado de validacion
    evento = Evento.query.get(id_evento) #verificamos si el evento existe
    if not evento:
        return jsonify({"status": "error", "message": "El evento asociado no existe"}), 404
        
    #3. Restriccion dinamica: Si esta VALIDADO, solo Admin puede editar
    if evento.validado == True and usuario.rol != 'Administrador':
        return jsonify({
            "status": "error", 
            "message": "Este evento ya ha sido validado. Solo un administrador puede realizar cambios en el mantenimiento."
        }), 403
        
    mantenimiento = Mantenimiento.query.get(id_evento) #obtenemos el mantenimiento
    if not mantenimiento:
        return jsonify({"status": "error", "message": "Mantenimiento no encontrado"}), 404
        
    data = request.json #obtenemos los datos en json
    
    try:
        if 'tipo' in data: mantenimiento.tipo = data['tipo']
        if 'fecha_entrega' in data:
            fecha_raw = data['fecha_entrega']
            fecha_parsed = None
            if fecha_raw:
                try:
                    fecha_raw_clean = fecha_raw.split('.')[0].replace('Z', '')
                    if 'T' in fecha_raw_clean:
                        fecha_parsed = datetime.fromisoformat(fecha_raw_clean)
                    else:
                        fecha_parsed = datetime.strptime(fecha_raw_clean, '%Y-%m-%d')
                except ValueError:
                    fecha_parsed = None
            mantenimiento.fecha_entrega = fecha_parsed
        if 'descripcion_trabajo' in data: mantenimiento.descripcion_trabajo = data['descripcion_trabajo']
        if 'piezas_reemplazadas' in data: mantenimiento.piezas_reemplazadas = data['piezas_reemplazadas']
        
        db.session.commit() #confirmamos la transaccion
        return jsonify({
            "status": "success",
            "message": "Mantenimiento actualizado por el administrador",
            "mantenimiento": mantenimiento.to_dict() #convertimos el mantenimiento a diccionario
        }), 200
        
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500
#------------------------------------------------------------------------------------------------------------
