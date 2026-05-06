import os
from pyswip import Prolog
from flask import current_app
from datetime import datetime, timedelta
from ..models import db, FallaHecho
from pathlib import Path

# Inicializamos el motor de Prolog de forma global
prolog = Prolog()

def get_prolog_paths():
    """Obtiene las rutas absolutas de reglas y hechos de forma robusta"""
    # current_app.root_path es proyecto/app/
    # Queremos subir un nivel para llegar a la raíz donde está motor_prolog
    root_path = Path(current_app.root_path).parent
    path_reglas = (root_path / "motor_prolog" / "reglas.pl").as_posix()
    path_hechos = (root_path / "motor_prolog" / "hechos.pl").as_posix()
    return path_reglas, path_hechos

def inicializar_prolog():
    """Carga las reglas iniciales en el motor"""
    path_reglas, _ = get_prolog_paths()
    try:
        # Importante: Algunos entornos requieren recargar el motor
        prolog.consult(path_reglas)
        print(f">>> Motor Prolog cargado desde: {path_reglas}")
        return True
    except Exception as e:
        print(f">>> Error crítico al inicializar Prolog: {e}")
        return False

def sincronizar_hechos_prolog():
    """Consulta la base de datos y regenera el archivo hechos.pl"""
    path_reglas, path_hechos = get_prolog_paths()
    try:
        fallas = FallaHecho.query.all()
        
        lines = [
            "% --- hechos.pl: GENERADO AUTOMATICAMENTE ---",
            "% No editar este archivo manualmente.",
            f"% Ultima actualizacion: {datetime.utcnow() - timedelta(hours=6)}", 
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
        return True
    except Exception as e:
        print(f">>> Error sincronizando con Prolog: {str(e)}")
        return False
