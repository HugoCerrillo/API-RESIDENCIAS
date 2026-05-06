from flask import current_app
from datetime import datetime, timedelta
from ..models import db, Alerta, Usuario, Equipo
from .email_service import enviar_correo_generico

def verificar_alertas_programadas():
    """Lógica central para procesar alertas (2 días antes)"""
    # Necesitamos el context si se llama desde el scheduler
    with current_app.app_context():
        try:
            hoy = (datetime.utcnow() + timedelta(hours=-6)).date()
            alertas = db.session.query(Alerta, Usuario, Equipo)\
                .join(Usuario, Alerta.id_usuario == Usuario.id_usuario)\
                .join(Equipo, Alerta.id_equipo == Equipo.id_equipo)\
                .filter(Alerta.estatus == 'Pendiente').all()
            
            if not alertas:
                return 0

            count = 0
            for al, user, eq in alertas:
                fecha_disparo = al.fecha_programada - timedelta(days=2)
                if hoy >= fecha_disparo:
                    cuerpo = (f"Hola {user.nombre},\n\n"
                             f"Esta es una notificacion automatica de ExperTrack.\n"
                             f"Tienes una actividad programada para el equipo: {eq.codigo_inventario} ({eq.marca} {eq.modelo}).\n\n"
                             f"Detalles de la alerta:\n"
                             f"- Titulo: {al.titulo}\n"
                             f"- Descripcion: {al.descripcion}\n"
                             f"- Fecha Programada: {al.fecha_programada}\n\n"
                             f"Por favor, toma las medidas necesarias.\n\n"
                             f"Atentamente,\nSistema ExperTrack")
                    
                    if enviar_correo_generico(user.correo, f"ALERTA PREVENTIVA: {al.titulo}", cuerpo):
                        al.estatus = 'Enviada'
                        count += 1
                        print(f">>> Alerta enviada a {user.correo}")

            db.session.commit()
            return count
        except Exception as e:
            print(f">>> Error en verificación de alertas: {e}")
            return 0
