import smtplib
from email.mime.text import MIMEText
from flask import current_app

def enviar_correo_generico(destinatario, asunto, cuerpo):
    """Función base para enviar correos usando la configuración de la app"""
    smtp_server = current_app.config['SMTP_SERVER']
    smtp_port = current_app.config['SMTP_PORT']
    smtp_user = current_app.config['SMTP_USER']
    smtp_password = current_app.config['SMTP_PASSWORD']

    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = smtp_user
    msg['To'] = destinatario

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

def enviar_correo_recuperacion(destinatario, enlace):
    asunto = 'Recuperación de Contraseña - ExperTrack'
    cuerpo = f"Haz clic en el siguiente enlace para recuperar tu contraseña:\n\n{enlace}"
    return enviar_correo_generico(destinatario, asunto, cuerpo)
