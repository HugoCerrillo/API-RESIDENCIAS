import smtplib
from email.mime.text import MIMEText
from flask import current_app
from datetime import datetime, timedelta
from ..models import db, Alerta, Usuario, Equipo
from ..config import Config

def verificar_alertas_programadas():
    """Lógica central para procesar alertas (2 días antes)"""
    with current_app.app_context():
        try:
            # Cargamos configuración para SMTP
            SMTP_SERVER = Config.SMTP_SERVER
            SMTP_PORT = Config.SMTP_PORT
            SMTP_USER = Config.SMTP_USER
            SMTP_PASSWORD = Config.SMTP_PASSWORD

            hoy = (datetime.utcnow() + timedelta(hours=-6)).date()
            #obtenemos alertas pendientes junto con los datos del usuario y equipo
            query = db.session.query(Alerta, Usuario, Equipo)\
                .join(Usuario, Alerta.id_usuario == Usuario.id_usuario)\
                .join(Equipo, Alerta.id_equipo == Equipo.id_equipo)\
                .filter(Alerta.estatus == 'Pendiente')
            
            alertas = query.all()
            count = 0
            
            if not alertas:
                return 0

            #iniciamos conexión SMTP
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            
            for al, user, eq in alertas:
                fecha_disparo = al.fecha_programada - timedelta(days=2)
                
                if hoy >= fecha_disparo:
                    #redactamos el correo con MIMEText
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
                    
                    #enviamos
                    server.sendmail(SMTP_USER, user.correo, msg.as_string())
                    
                    #marcamos como enviada
                    al.estatus = 'Enviada'
                    count += 1
                    print(f">>> Alerta enviada a {user.correo}")

            server.quit() #cerramos la conexion
            
            #si se envio al menos una alerta, confirmamos la transaccion
            if count > 0:
                db.session.commit()
            return count
            
        except Exception as e:
            print(f"Error en verificacion de alertas: {e}")
            return 0
