import os
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Usuario, Evento, Diagnostico, CategoriaHecho, SintomaHecho, FallaHecho
from ..services.prolog_service import prolog, sincronizar_hechos_prolog

expert_bp = Blueprint('expert', __name__)

# Configuración de rutas para Prolog (apuntando a la raíz del proyecto)
BASE_DIR = os.getcwd()
path_hechos = os.path.join(BASE_DIR, 'hechos.pl')
path_reglas = os.path.join(BASE_DIR, 'reglas.pl')


#-------------------------------------------------------------------------------------------------------------
#endpoint para diagnosticar con Prolog
@expert_bp.route('/diagnosticar', methods=['POST'])
@jwt_required()
def diagnosticar():
    try:
        data = request.json #recibe los datos del frontend
        if not data:
            return jsonify({"status": "error", "mensaje": "No se recibieron datos"}), 400

        tipo = data.get('tipo') #tipo de equipo
        sintoma = data.get('sintoma') #sintoma (manifestación de falla) principal
        historial = data.get('historial', []) #historial de preguntas y respuestas

        #1. limpiamos la memoria antes de procesar
        #usamos la regla que definimos en reglas.pl
        list(prolog.query("limpiar_memoria"))

        #2. Inyectamos el historial
        for paso in historial:
            pregunta = paso['p'] #pregunta
            respuesta = paso['r'] # 'si' o 'no'
            #envolvemos el valor en comillas simples para Prolog
            prolog.assertz(f"respuesta('{pregunta}', {respuesta})")

        #3. Ejecutamos la consulta principal
        query_str = f"siguiente_paso('{tipo}', '{sintoma}', Accion, Valor)" #consulta principal
        results = list(prolog.query(query_str)) #obtenemos los resultados

        #4. Procesamos la respuesta
        if results:
            res = results[0]
            #procesamos los datos a string
            return jsonify({
                "status": "success",
                "accion": str(res['Accion']),
                "valor": str(res['Valor'])
            })
        else:
            return jsonify({
                "status": "error", 
                "mensaje": "El motor de inferencia no devolvió resultados"
            }), 404

    except Exception as e:
        print(f"Error en el diagnóstico: {e}")
        return jsonify({"status": "error", "mensaje": str(e)}), 500
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para obtener los sintomas de la bd (bd extra)
@expert_bp.route('/sintomas', methods=['GET'])
@jwt_required()
def get_sintomas():
    try:
        #recibimos el tipo desde los parametros de la URL: /api/sintomas?tipo=PC
        tipo = request.args.get('tipo')
        
        query = SintomaHecho.query #consulta a la tabla SintomaHecho
        
        if tipo:
            #hacemos un JOIN con la tabla de fallas (FallaHecho) para filtrar solo los síntomas
            #que tengan al menos una falla registrada para ese tipo de equipo (PC o Laptop)
            query = query.join(FallaHecho).filter(FallaHecho.tipo_equipo == tipo).distinct()
        
        sintomas = query.all() #obtenemos todos los sintomas
        
        return jsonify({
            "status": "success",
            "sintomas": [s.to_dict() for s in sintomas]
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al obtener síntomas: {str(e)}"
        }), 500
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para registrar nuevas categorías (para los hechos)
@expert_bp.route('/categorias_hechos', methods=['POST'])
@jwt_required()
def create_categoria_hecho():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #solo los técnicos pueden agregar hechos
    if usuario.rol != 'Técnico':
        return jsonify({"status": "error", "message": "Solo los técnicos tienen permisos para alimentar la base de conocimientos"}), 403
        
    data = request.json #obtenemos los datos en json
    nombre = data.get('nombre') #obtenemos el nombre de la categoría
    
    if not nombre:
        return jsonify({"status": "error", "message": "El nombre de la categoría es requerido"}), 400
        
    try:
        nueva_cat = CategoriaHecho(nombre=nombre) #creamos la nueva categoría
        db.session.add(nueva_cat) #agregamos la nueva categoría
        db.session.commit() #confirmamos la transaccion
        return jsonify({
            "status": "success",
            "message": "Categoría de diagnóstico registrada correctamente",
            "categoria": nueva_cat.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": "Error al registrar categoría (posible nombre duplicado)"}), 500
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para obtener todas las categorias de diagnostico
@expert_bp.route('/categorias_hechos', methods=['GET'])
@jwt_required()
def get_categorias_hechos():
    try:
        categorias = CategoriaHecho.query.all()
        return jsonify({
            "status": "success",
            "categorias": [c.to_dict() for c in categorias]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al obtener categorías: {str(e)}"}), 500
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para registrar nuevos sintomas iniciales
@expert_bp.route('/sintomas_hechos', methods=['POST'])
@jwt_required()
def create_sintoma_hecho():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #solo los técnicos pueden agregar hechos
    if usuario.rol != 'Técnico':
        return jsonify({"status": "error", "message": "Solo los técnicos tienen permisos para alimentar la base de conocimientos"}), 403
        
    data = request.json #obtenemos los datos en json
    
    #datos del síntoma (manifestacion de falla)
    clave = data.get('clave')
    descripcion = data.get('descripcion')
    
    #datos de la falla obligatoria (para evitar sintomas huerfanitos)
    tipo_equipo = data.get('tipo_equipo')
    categoria_id = data.get('categoria_id')
    pregunta_pista = data.get('pregunta_pista')
    diagnostico = data.get('diagnostico')
    recomendacion = data.get('recomendacion')
    
    #validamos que todos los campos del sintoma y la falla esten presentes
    campos_requeridos = [clave, descripcion, tipo_equipo, categoria_id, pregunta_pista, diagnostico, recomendacion]
    if not all(campos_requeridos):
        return jsonify({
            "status": "error", 
            "message": "Para registrar un sintoma inicial, es obligatorio incluir los datos de su primera falla asociada (tipo_equipo, categoria_id, etc.)"
        }), 400
        
    #verificamos que la categoria exista    
    if tipo_equipo not in ['PC', 'Laptop']:
        return jsonify({"status": "error", "message": "El tipo_equipo de la falla debe ser 'PC' o 'Laptop'"}), 400

    try:
        #iniciamos el guardado, primero el sintoma
        nuevo_sintoma = SintomaHecho(clave=clave, descripcion=descripcion)
        db.session.add(nuevo_sintoma)
        db.session.flush() #obtenemos el ID del sintoma sin confirmar la transaccion aun

        #creamos la falla ligada al nuevo sintoma
        nueva_falla = FallaHecho(
            tipo_equipo=tipo_equipo,
            sintoma_id=nuevo_sintoma.id,
            categoria_id=categoria_id,
            pregunta_pista=pregunta_pista,
            diagnostico=diagnostico,
            recomendacion=recomendacion
        )
        
        db.session.add(nueva_falla)
        db.session.commit() #confirmamos ambos
        
        #sincronizamos con prolog
        sincronizar_hechos_prolog()
        
        return jsonify({
            "status": "success",
            "message": "Síntoma inicial y su falla asociada registrados y sincronizados correctamente",
            "sintoma": nuevo_sintoma.to_dict(),
            "falla_inicial": nueva_falla.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al registrar: {str(e)}"}), 500
#-------------------------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------------------------
#endpoint para obtener todas las categorias de diagnostico
@expert_bp.route('/categorias_hechos', methods=['POST'])
@jwt_required() #solo usuarios autenticados
def get_categorias_hechos():
    try:
        categorias = CategoriaHecho.query.all()
        return jsonify({
            "status": "success",
            "categorias": [c.to_dict() for c in categorias]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al obtener categorías: {str(e)}"}), 500
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para registrar nuevos sintomas iniciales
@expert_bp.route('/sintomas_hechos', methods=['POST'])
@jwt_required() #solo usuarios autenticados
def create_sintoma_hecho():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #solo los técnicos pueden agregar hechos
    if usuario.rol != 'Técnico':
        return jsonify({"status": "error", "message": "Solo los técnicos tienen permisos para alimentar la base de conocimientos"}), 403
        
    data = request.json #obtenemos los datos en json
    
    #datos del síntoma (manifestacion de falla)
    clave = data.get('clave')
    descripcion = data.get('descripcion')
    
    #datos de la falla obligatoria (para evitar sintomas huerfanitos)
    tipo_equipo = data.get('tipo_equipo')
    categoria_id = data.get('categoria_id')
    pregunta_pista = data.get('pregunta_pista')
    diagnostico = data.get('diagnostico')
    recomendacion = data.get('recomendacion')
    
    #validamos que todos los campos del sintoma y la falla esten presentes
    campos_requeridos = [clave, descripcion, tipo_equipo, categoria_id, pregunta_pista, diagnostico, recomendacion]
    if not all(campos_requeridos):
        return jsonify({
            "status": "error", 
            "message": "Para registrar un sintoma inicial, es obligatorio incluir los datos de su primera falla asociada (tipo_equipo, categoria_id, etc.)"
        }), 400
        
    #verificamos que la categoria exista    
    if tipo_equipo not in ['PC', 'Laptop']:
        return jsonify({"status": "error", "message": "El tipo_equipo de la falla debe ser 'PC' o 'Laptop'"}), 400

    try:
        #iniciamos el guardado, primero el sintoma
        nuevo_sintoma = SintomaHecho(clave=clave, descripcion=descripcion)
        db.session.add(nuevo_sintoma)
        db.session.flush() #obtenemos el ID del sintoma sin confirmar la transaccion aun

        #creamos la falla ligada al nuevo sintoma
        nueva_falla = FallaHecho(
            tipo_equipo=tipo_equipo,
            sintoma_id=nuevo_sintoma.id,
            categoria_id=categoria_id,
            pregunta_pista=pregunta_pista,
            diagnostico=diagnostico,
            recomendacion=recomendacion
        )
        
        db.session.add(nueva_falla)
        db.session.commit() #confirmamos ambos
        
        #sincronizamos con prolog
        sincronizar_hechos_prolog()
        
        return jsonify({
            "status": "success",
            "message": "Síntoma inicial y su falla asociada registrados y sincronizados correctamente",
            "sintoma": nuevo_sintoma.to_dict(),
            "falla_inicial": nueva_falla.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al registrar: {str(e)}"}), 500
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para registrar nuevas fallas
@expert_bp.route('/fallas_hechos', methods=['POST'])
@jwt_required()
def create_falla_hecho():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #solo los técnicos pueden agregar hechos
    if usuario.rol != 'Técnico':
        return jsonify({"status": "error", "message": "Solo los técnicos tienen permisos para alimentar la base de conocimientos"}), 403
        
    data = request.json #obtenemos los datos en json
    tipo_equipo = data.get('tipo_equipo') #obtenemos el tipo de equipo
    sintoma_id = data.get('sintoma_id') #obtenemos el id del sintoma
    categoria_id = data.get('categoria_id') #obtenemos el id de la categoria
    pregunta_pista = data.get('pregunta_pista') #obtenemos la pregunta pista
    diagnostico = data.get('diagnostico') #obtenemos el diagnostico
    recomendacion = data.get('recomendacion') #obtenemos la recomendacion
    
    #verificamos que todos los campos sean obligatorios
    if not all([tipo_equipo, sintoma_id, categoria_id, pregunta_pista, diagnostico, recomendacion]):
        return jsonify({"status": "error", "message": "Todos los campos son obligatorios para registrar una falla"}), 400

    #verificamos que el tipo de equipo sea correcto
    if tipo_equipo not in ['PC', 'Laptop']:
        return jsonify({"status": "error", "message": "El tipo_equipo debe ser 'PC' o 'Laptop'"}), 400

    try:
        #verificamos que existan la categoría y el sintoma individualmente para dar un error descriptivo
        if not CategoriaHecho.query.get(categoria_id):
            return jsonify({"status": "error", "message": f"La categoría con ID {categoria_id} no existe"}), 404
            
        #verificamos que el sintoma exista
        if not SintomaHecho.query.get(sintoma_id):
            return jsonify({"status": "error", "message": f"El síntoma inicial con ID {sintoma_id} no existe. Toda falla debe estar ligada a un síntoma existente."}), 404

        nueva_falla = FallaHecho(
            tipo_equipo=tipo_equipo,
            sintoma_id=sintoma_id,
            categoria_id=categoria_id,
            pregunta_pista=pregunta_pista,
            diagnostico=diagnostico,
            recomendacion=recomendacion
        ) #creamos la nueva falla
        
        db.session.add(nueva_falla) #agregamos la nueva falla
        db.session.commit() #confirmamos la transaccion
        
        # sincronizamos con el archivo fisico de Prolog
        sincronizar_hechos_prolog()
        
        return jsonify({
            "status": "success",
            "message": "Nueva falla/regla de diagnóstico registrada correctamente y sincronizada con Prolog",
            "falla": nueva_falla.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback() #deshacemos los cambios si hay error
        return jsonify({"status": "error", "message": str(e)}), 500
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para obtener todas las fallas registradas
@expert_bp.route('/fallas_hechos', methods=['GET'])
@jwt_required()
def get_fallas_hechos():
    try:              
        tipo = request.args.get('tipo')
        sintoma_id = request.args.get('sintoma_id')
        categoria_id = request.args.get('categoria_id')
        
        query = FallaHecho.query #obtenemos todas las fallas
        
        #filtros
        if tipo:
            query = query.filter(FallaHecho.tipo_equipo == tipo)
        if sintoma_id:
            query = query.filter(FallaHecho.sintoma_id == sintoma_id)
        if categoria_id:
            query = query.filter(FallaHecho.categoria_id == categoria_id)
            
        fallas = query.all()
        
        #construimos la respuesta 
        resultado = []
        for f in fallas:
            f_dict = f.to_dict()
            #agregamos nombres descriptivos gracias a las relaciones
            f_dict['sintoma_descripcion'] = f.sintoma.descripcion if f.sintoma else "N/A"
            f_dict['categoria_nombre'] = f.categoria.nombre if f.categoria else "N/A"
            resultado.append(f_dict)
            
        return jsonify({
            "status": "success",
            "total": len(resultado),
            "fallas": resultado
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al obtener fallas: {str(e)}"}), 500
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#endpoint para descargar el archivo hechos.pl (para presentacion/backup)
@expert_bp.route('/exportar_hechos', methods=['GET'])
@jwt_required()
def exportar_hechos():
    usuario_id = get_jwt_identity() #obtenemos el id del usuario
    usuario = Usuario.query.get(usuario_id) #obtenemos el usuario
    
    #solo los administradores y técnicos pueden descargar la base de conocimientos
    if usuario.rol not in ['Administrador', 'Técnico']:
        return jsonify({"status": "error", "message": "No tienes permisos para descargar la base de conocimientos"}), 403
        
    #forzamos una sincronizacion antes de descargar para tener lo ultimo en la bd
    sincronizar_hechos_prolog()
    
    try:
        return send_file(
            path_hechos,
            as_attachment=True,
            download_name='hechos.pl',
            mimetype='text/plain'
        ) #retornamos el archivo hechos.pl
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al descargar: {str(e)}"}), 500

#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
#funcion para sincronizar la base de datos con prolog
def sincronizar_hechos_prolog():
    """Consulta la base de datos y regenera el archivo hechos.pl para Prolog"""
    try:
        fallas = FallaHecho.query.all() #consulta a la tabla de fallas en la bd
        
        lines = [
            "% --- hechos.pl: GENERADO AUTOMATICAMENTE DESDE LA BASE DE DATOS ---",
            "% No editar este archivo manualmente.",
            f"% Ultima actualizacion: {timedelta(hours=-6) + datetime.utcnow()}", 
            "\n"
        ] #lista de lineas que se van a escribir en el archivo hechos.pl
        
        for f in fallas:
            #escapar comillas simples duplicandolas para Prolog
            diag = f.diagnostico.replace("'", "''")
            rec = f.recomendacion.replace("'", "''")
            pregunta = f.pregunta_pista.replace("'", "''")
            
            #generar lineas de hechos
            lines.append(f"falla_info({f.id}, '{f.tipo_equipo}', '{diag}', '{rec}').")
            sintoma_clave = f.sintoma.clave if f.sintoma else "sintoma_desconocido"
            lines.append(f"condicion({f.id}, {sintoma_clave}, '{pregunta}').")
        
        #escribir el archivo
        with open(path_hechos, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))
            
        #recargar el motor de Prolog para que reconozca los nuevos hechos
        prolog.consult(path_reglas)
        print(">>> Sincronización con Prolog exitosa.") #imprimimos en consola que se sincronizo correctamente
        return True
    except Exception as e:
        print(f">>> Error sincronizando con Prolog: {str(e)}")
        return False
#-------------------------------------------------------------------------------------------------------------
