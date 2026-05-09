import smtplib
from email.mime.text import MIMEText
from flask import current_app
from datetime import datetime, timedelta
from ..models import db, Alerta, Usuario, Equipo
from ..config import Config

def verificar_alertas_programadas(app):
    """Lógica central para procesar alertas con contexto de APP real"""
    import os, fcntl
    
    # Usamos un candado de archivo para que solo un worker de Gunicorn trabaje
    lock_file = open(".scheduler_main.lock", "wb")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print(">>> [SCHEDULER] Candado obtenido. Verificando alertas...", flush=True)
    except (IOError, BlockingIOError):
        # Si otro worker ya tiene el candado, este proceso no hace nada
        lock_file.close()
        return 0

    try:
        with app.app_context():
            # Cargamos configuración para SMTP
            SMTP_SERVER = Config.SMTP_SERVER
            SMTP_PORT = Config.SMTP_PORT
            SMTP_USER = Config.SMTP_USER
            SMTP_PASSWORD = Config.SMTP_PASSWORD

            hoy = (datetime.utcnow() + timedelta(hours=-6)).date()
            #obtenemos alertas pendientes junto con los datos del usuario y equipo
            # Consulta simplificada
            alertas_pendientes = Alerta.query.filter_by(estatus='Pendiente').all()
            print(f">>> [SCHEDULER] Alertas pendientes (bruto): {len(alertas_pendientes)}", flush=True)
            
            count = 0
            if not alertas_pendientes:
                return 0

            #iniciamos conexión SMTP
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            
            for al in alertas_pendientes:
                # Obtenemos usuario y equipo individualmente
                user = Usuario.query.get(al.id_usuario)
                eq = Equipo.query.get(al.id_equipo)
                
                if not user or not eq:
                    print(f">>> [DEBUG] Alerta {al.id} ignorada (falta usuario id:{al.id_usuario} o equipo id:{al.id_equipo})", flush=True)
                    continue

                fecha_disparo = al.fecha_programada - timedelta(days=2)
                print(f">>> [DEBUG] Procesando alerta '{al.titulo}'. Fecha Prog: {al.fecha_programada}, Hoy: {hoy}", flush=True)
                
                if hoy >= fecha_disparo:
                    print(f">>> [DEBUG] ¡Es hora de enviar! Conectando a SMTP...", flush=True)
                    #iniciamos conexión SMTP dentro del if para no abrirla si no hay nada que enviar
                    try:
                        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                        server.starttls()
                        server.login(SMTP_USER, SMTP_PASSWORD)
                        
                        cuerpo = (f"Hola {user.nombre},\n\n"
                                 f"Esta es una notificacion automatica de ExperTrack.\n"
                                 f"Tienes una actividad programada para el equipo: {eq.codigo_inventario} ({eq.marca} {eq.modelo}).\n\n"
                                 f"Detalles de la alerta:\n"
                                 f"- Titulo: {al.titulo}\n"
                                 f"- Descripcion: {al.descripcion}\n"
                                 f"- Fecha Programada: {al.fecha_programada}\n\n"
                                 f"Por favor, toma las medidas necesarias.\n\n"
                                 f"Atentamente,\nSistema ExperTrack")
                        
                        msg = MIMEText(cuerpo)
                        msg['Subject'] = f"ALERTA PREVENTIVA: {al.titulo}"
                        msg['From'] = SMTP_USER
                        msg['To'] = user.correo
                        
                        server.sendmail(SMTP_USER, user.correo, msg.as_string())
                        server.quit()
                        
                        al.estatus = 'Enviada'
                        count += 1
                        print(f">>> [OK] Alerta enviada con éxito a {user.correo}", flush=True)
                    except Exception as smtp_e:
                        print(f">>> [ERROR SMTP] No se pudo enviar el correo: {smtp_e}", flush=True)
                else:
                    print(f">>> [DEBUG] Aún no es tiempo para la alerta '{al.titulo}'", flush=True)

            # El cierre de conexión ahora se maneja dentro del loop
            
            #si se envio al menos una alerta, confirmamos la transaccion
            if count > 0:
                db.session.commit()
            return count
            
    except Exception as e:
        print(f"Error en verificacion de alertas: {e}")
        return 0
    finally:
        lock_file.close()
