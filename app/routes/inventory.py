from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Equipo, Periferico, Especificacion, Usuario, Evento, Mantenimiento
from ..services.pdf_service import PDF_Inventario
import io
from datetime import datetime
from ..utils.helpers import admin_required

inventory_bp = Blueprint('inventory', __name__)


#-------------------------------------------------------------------------------------------------------------
#endpoint para crear un equipo
@inventory_bp.route('/equipos', methods=['POST'])
@jwt_required()
def create_equipo():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    
    data = request.json #obtenemos los datos del equipo
    
    #Usuario Solicitante solo puede crear su propio equipo ("Alta Básica")
    #Administrador/Técnico pueden asignar a cualquier usuario
    id_propietario = usuario.id_usuario
    if usuario.rol in ['Administrador', 'Técnico'] and 'id_usuario' in data:
        id_propietario = data['id_usuario']

    try:
        #crear el Equipo 
        nuevo_equipo = Equipo(
            id_usuario=id_propietario,
            tipo_equipo=data.get('tipo_equipo'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            numero_serie=data.get('numero_serie'),
            codigo_inventario=data.get('codigo_inventario'),
            area=data.get('area'),
            ubicacion=data.get('ubicacion'),
            fecha_adquisicion=data.get('fecha_adquisicion'),
            en_garantia=data.get('en_garantia', False)
        )
        db.session.add(nuevo_equipo) #agregamos el equipo
        db.session.flush() #obtenemos el id_equipo antes del commit

        #agregar Periféricos (si los técnicos/admins los mandan)
        if usuario.rol != 'Usuario Solicitante' and 'perifericos' in data:
            for p in data['perifericos']: #recorremos los perifericos
                nuevo_p = Periferico(
                    id_equipo=nuevo_equipo.id_equipo,
                    tipo=p.get('tipo'),
                    marca=p.get('marca'),
                    numero_serie=p.get('numero_serie'),
                    id_inventario_interno=p.get('id_inventario_interno')
                )
                db.session.add(nuevo_p) #agregamos el periferico

        #agregar Especificación (Solo si no es Usuario Solicitante)
        if usuario.rol != 'Usuario Solicitante' and 'especificaciones' in data:
            specs = data['especificaciones'] #obtenemos las especificaciones
            nueva_spec = Especificacion(
                id_equipo=nuevo_equipo.id_equipo,
                sistema_operativo=specs.get('sistema_operativo'),
                procesador=specs.get('procesador'),
                ram=specs.get('ram'),
                tipo_ram=specs.get('tipo_ram'),
                almacenamiento=specs.get('almacenamiento'),
                almacenamiento_tipo=specs.get('almacenamiento_tipo'),
                es_actual=True
            )
            db.session.add(nueva_spec) #agregamos la especificación

        db.session.commit() #guardamos los cambios
        return jsonify({
            "status": "success",
            "message": "Equipo registrado correctamente",
            "id_equipo": nuevo_equipo.id_equipo
        }), 201

    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay un error
        return jsonify({"status": "error", "message": str(e)}), 500
#-------------------------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------------------------
#endpoint para obtener los equipos registrados
@inventory_bp.route('/equipos', methods=['GET'])
@jwt_required()
def get_equipos():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #filtrado por rol
    query = db.session.query(Equipo, Usuario.nombre.label('dueño')).join(Usuario, Equipo.id_usuario == Usuario.id_usuario)
    
    if usuario.rol == 'Usuario Solicitante': #si el usuario es solicitante
        query = query.filter(Equipo.id_usuario == usuario.id_usuario) #solo muestra sus equipos
    
    resultados = query.all() #obtenemos todos los equipos
     
    lista_equipos = [] #creamos una lista para guardar los equipos
    for eq, dueño in resultados: #recorremos los equipos
        d = eq.to_dict() #convertimos el equipo a diccionario
        d['dueño'] = dueño #agregamos el dueño
        lista_equipos.append(d) #agregamos el equipo a la lista
        
    return jsonify({
        "status": "success",
        "equipos": lista_equipos
    }), 200
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para obtener los detalles de un equipo
@inventory_bp.route('/equipos/<int:id>', methods=['GET'])
@jwt_required()
def get_equipo_detalle(id):
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    equipo = Equipo.query.get(id) #obtenemos el equipo
    if not equipo:
        return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
        
    #Usuario Solicitante solo ve sus propios equipos
    if usuario.rol == 'Usuario Solicitante' and equipo.id_usuario != usuario.id_usuario:
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
    
    #obtenemos la especificación actual
    spec_actual = Especificacion.query.filter_by(id_equipo=id, es_actual=True).first()
    
    return jsonify({
        "status": "success",
        "equipo": equipo.to_dict(), #convertimos el equipo a diccionario
        "perifericos": [p.to_dict() for p in equipo.perifericos], #convertimos los perifericos a diccionario    
        "especificacion": spec_actual.to_dict() if spec_actual else None, #convertimos la especificación a diccionario
        "dueño": equipo.propietario.nombre if hasattr(equipo, 'propietario') else "Desconocido" #obtenemos el dueño
    }), 200
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para actualizar un equipo
@inventory_bp.route('/equipos/<int:id>', methods=['PUT'])
@jwt_required()
def update_equipo(id):
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    if usuario.rol not in ['Administrador', 'Técnico']: #si el usuario no es administrador o técnico
        return jsonify({"status": "error", "message": "No tienes permisos para editar equipos"}), 403
        
    equipo = Equipo.query.get(id) #obtenemos el equipo
    if not equipo: #si el equipo no existe
        return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
        
    data = request.json #obtenemos los datos del equipo
    
    try:
        # 1. Actualizar datos basicos
        if 'id_usuario' in data: equipo.id_usuario = data['id_usuario']        
        if 'marca' in data: equipo.marca = data['marca']
        if 'modelo' in data: equipo.modelo = data['modelo']
        if 'tipo_equipo' in data: equipo.tipo_equipo = data['tipo_equipo']
        if 'numero_serie' in data: equipo.numero_serie = data['numero_serie']
        if 'codigo_inventario' in data: equipo.codigo_inventario = data['codigo_inventario']
        if 'area' in data: equipo.area = data['area']
        if 'ubicacion' in data: equipo.ubicacion = data['ubicacion']
        if 'estado_operativo' in data: equipo.estado_operativo = data['estado_operativo']
        if 'en_garantia' in data: equipo.en_garantia = data['en_garantia']

        # 2. Logica de Versionado de Especificaciones
        if 'especificaciones' in data: #si hay especificaciones
            new_specs_data = data['especificaciones'] #obtenemos las especificaciones
            
            #buscar la especificacion actual
            current_spec = Especificacion.query.filter_by(id_equipo=id, es_actual=True).first()
            
            #solo crear nueva version si el registro actual es diferente o si no existe
            should_create_new = False #variable para verificar si se debe crear una nueva version
            if not current_spec: #si no existe la especificacion actual
                should_create_new = True #se crea una nueva version
            else:
                #verificar si algo cambio (omitiendo id y metadatos)
                fields_to_check = ['sistema_operativo', 'procesador', 'ram', 'tipo_ram', 'almacenamiento', 'almacenamiento_tipo']
                for field in fields_to_check: #recorremos los campos
                    if new_specs_data.get(field) != getattr(current_spec, field): #si algo cambio
                        should_create_new = True #se crea una nueva version
                        break
            
            if should_create_new: #si se debe crear una nueva version
                if current_spec: #si existe la especificacion actual
                    current_spec.es_actual = False # Versionamos la anterior
                
                #creamos el nuevo registro
                nueva_version = Especificacion(
                    id_equipo=id,
                    sistema_operativo=new_specs_data.get('sistema_operativo'),
                    procesador=new_specs_data.get('procesador'),
                    ram=new_specs_data.get('ram'),
                    tipo_ram=new_specs_data.get('tipo_ram'),
                    almacenamiento=new_specs_data.get('almacenamiento'),
                    almacenamiento_tipo=new_specs_data.get('almacenamiento_tipo'),
                    es_actual=True
                )
                db.session.add(nueva_version) #agregamos la nueva version

        if 'perifericos' in data: #si hay perifericos
            #borramos los perifericos actuales para reemplazarlos con la nueva lista
            Periferico.query.filter_by(id_equipo=id).delete() #borramos los perifericos actuales
            
            for p in data['perifericos']: #recorremos los perifericos
                nuevo_p = Periferico(
                    id_equipo=id,
                    tipo=p.get('tipo'),
                    marca=p.get('marca'),
                    numero_serie=p.get('numero_serie'),
                    id_inventario_interno=p.get('id_inventario_interno')
                )
                db.session.add(nuevo_p) #agregamos el nuevo periferico

        db.session.commit() #guardamos los cambios
        return jsonify({"status": "success", "message": "Equipo y especificaciones actualizados"}), 200

    except Exception as e:
        db.session.rollback() #deshacemos los cambios con un rollback si hay un error
        return jsonify({"status": "error", "message": str(e)}), 500    


#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para eliminar un equipo
@inventory_bp.route('/equipos/<int:id>', methods=['DELETE'])
@jwt_required() #solo usuarios autenticados
@admin_required #solo administradores
def delete_equipo(id):
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    if usuario.rol != 'Administrador': #si el usuario no es administrador
        return jsonify({"status": "error", "message": "Solo el administrador puede eliminar equipos"}), 403
        
    equipo = Equipo.query.get(id) #obtenemos el equipo
    if not equipo: #si el equipo no existe
        return jsonify({"status": "error", "message": "Equipo no encontrado"}), 404
        
    try:
        #el cascade configurado en models.py se encargará de Perifericos y Especificaciones
        db.session.delete(equipo) #eliminamos el equipo
        db.session.commit() #guardamos los cambios
        return jsonify({"status": "success", "message": "Equipo y todo su historial eliminados correctamente"}), 200
    except Exception as e:
        db.session.rollback() #deshacemos los cambios con un rollback si hay un error
        return jsonify({"status": "error", "message": str(e)}), 500

#-------------------------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------------------------
#endpoint para generar el inventario en pdf
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
#-------------------------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------------------------
#endpoint para generar el expediente de un equipo en pdf
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
