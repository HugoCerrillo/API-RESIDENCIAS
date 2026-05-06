import os
from pyswip import Prolog
from flask import current_app
from datetime import datetime, timedelta
from ..models import db, FallaHecho

# Inicializamos el motor de Prolog
prolog = Prolog()

def get_prolog_paths():
    """Obtiene las rutas absolutas de reglas y hechos"""
    # La carpeta motor_prolog está en la raíz del proyecto
    # current_app.root_path es proyecto/app/
    base_path = os.path.abspath(os.path.join(current_app.root_path, '..'))
    path_reglas = os.path.join(base_path, "motor_prolog", "reglas.pl").replace("\\", "/")
    path_hechos = os.path.join(base_path, "motor_prolog", "hechos.pl").replace("\\", "/")
    return path_reglas, path_hechos

def inicializar_prolog():
    """Carga las reglas iniciales en el motor"""
    path_reglas, _ = get_prolog_paths()
    try:
        prolog.consult(path_reglas)
        print(">>> Motor Prolog inicializado correctamente.")
        return True
    except Exception as e:
        print(f">>> Error al inicializar Prolog: {e}")
        return False

def sincronizar_hechos_prolog():
    """Consulta la base de datos y regenera el archivo hechos.pl para Prolog"""
    path_reglas, path_hechos = get_prolog_paths()
    try:
        fallas = FallaHecho.query.all()
        
        lines = [
            "% --- hechos.pl: GENERADO AUTOMATICAMENTE DESDE LA BASE DE DATOS ---",
            "% No editar este archivo manualmente.",
            f"% Ultima actualizacion: {datetime.utcnow() + timedelta(hours=-6)}", 
            "\n"
        ]
        
        for f in fallas:
            diag = f.diagnostico.replace("'", "''")
            rec = f.recomendacion.replace("'", "''")
            pregunta = f.pregunta_pista.replace("'", "''")
            
            lines.append(f"falla_info({f.id}, '{f.tipo_equipo}', '{diag}', '{rec}').")
            sintoma_clave = f.sintoma.clave if f.sintoma else "sintoma_desconocido"
            lines.append(f"condicion({f.id}, {sintoma_clave}, '{pregunta}').")
        
        with open(path_hechos, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))
            
        prolog.consult(path_reglas)
        print(">>> Sincronización con Prolog exitosa.")
        return True
    except Exception as e:
        print(f">>> Error sincronizando con Prolog: {str(e)}")
        return False
