import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargamos las variables del archivo .env
load_dotenv()

class Config:
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-default-secret')
    
    # Base de Datos Principal
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')
    DB_HOST = os.environ.get('DB_HOST')
    DB_NAME = os.environ.get('DB_NAME')
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
    
    # Base de Datos de Hechos (Prolog Sync)
    DB_HECHOS_NAME = os.environ.get('DB_HECHOS_NAME')
    SQLALCHEMY_BINDS = {
        'hechos': f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_HECHOS_NAME}'
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuración
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_COOKIE_SAMESITE = 'None'
    
    # Correo
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    
    # Scheduler
    SCHEDULER_API_ENABLED = True
