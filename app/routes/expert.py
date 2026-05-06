from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Usuario, Evento, Diagnostico, CategoriaHecho, SintomaHecho, FallaHecho
from ..services.prolog_service import prolog, sincronizar_hechos_prolog

expert_bp = Blueprint('expert', __name__)

@expert_bp.route('/diagnosticar', methods=['POST'])
@jwt_required()
def diagnosticar():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "mensaje": "No se recibieron datos"}), 400

        tipo = data.get('tipo')
        sintoma = data.get('sintoma')
        historial = data.get('historial', [])

        # 1. Limpiamos memoria
        list(prolog.query("limpiar_memoria"))

        # 2. Inyectamos historial
        for paso in historial:
            pregunta = paso['p']
            respuesta = paso['r']
            prolog.assertz(f"respuesta('{pregunta}', {respuesta})")

        # 3. Consulta principal
        query_str = f"siguiente_paso('{tipo}', '{sintoma}', Accion, Valor)"
        results = list(prolog.query(query_str))

        if results:
            res = results[0]
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

@expert_bp.route('/sintomas', methods=['GET'])
@jwt_required()
def get_sintomas():
    try:
        sintomas = SintomaHecho.query.all()
        return jsonify({"status": "success", "sintomas": [s.to_dict() for s in sintomas]}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@expert_bp.route('/categorias_hechos', methods=['POST'])
@jwt_required()
def create_categoria_hecho():
    usuario = Usuario.query.get(get_jwt_identity())
    if usuario.rol != 'Técnico':
        return jsonify({"status": "error", "message": "Acceso denegado"}), 403
    data = request.json
    try:
        nueva_cat = CategoriaHecho(nombre=data.get('nombre'))
        db.session.add(nueva_cat)
        db.session.commit()
        return jsonify({"status": "success", "categoria": nueva_cat.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@expert_bp.route('/categorias_hechos', methods=['GET'])
@jwt_required()
def get_categorias_hechos():
    categorias = CategoriaHecho.query.all()
    return jsonify({"status": "success", "categorias": [c.to_dict() for c in categorias]}), 200

@expert_bp.route('/sintomas_hechos', methods=['POST'])
@jwt_required()
def create_sintoma_hecho():
    data = request.json
    try:
        nuevo_sint = SintomaHecho(clave=data.get('clave'), descripcion=data.get('descripcion'))
        db.session.add(nuevo_sint)
        db.session.commit()
        return jsonify({"status": "success", "sintoma": nuevo_sint.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@expert_bp.route('/fallas_hechos', methods=['POST'])
@jwt_required()
def create_falla_hecho():
    data = request.json
    try:
        nueva_falla = FallaHecho(
            tipo_equipo=data.get('tipo_equipo'),
            sintoma_id=data.get('sintoma_id'),
            categoria_id=data.get('categoria_id'),
            pregunta_pista=data.get('pregunta_pista'),
            diagnostico=data.get('diagnostico'),
            recomendacion=data.get('recomendacion')
        )
        db.session.add(nueva_falla)
        db.session.commit()
        sincronizar_hechos_prolog()
        return jsonify({"status": "success", "falla": nueva_falla.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@expert_bp.route('/fallas_hechos', methods=['GET'])
@jwt_required()
def get_fallas_hechos():
    fallas = FallaHecho.query.all()
    return jsonify({"status": "success", "fallas": [f.to_dict() for f in fallas]}), 200

@expert_bp.route('/exportar_hechos', methods=['GET'])
@jwt_required()
def exportar_hechos():
    if sincronizar_hechos_prolog():
        return jsonify({"status": "success", "message": "Archivo hechos.pl actualizado"}), 200
    return jsonify({"status": "error", "message": "Fallo en la sincronización"}), 500
