from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_apscheduler import APScheduler
import pymysql
from .config import Config
from .models import db

# Inicializamos extensiones fuera de la factory para poder importarlas
jwt = JWTManager()
scheduler = APScheduler()

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../static')
    app.config.from_object(config_class)
    
    # Driver MySQL
    pymysql.install_as_MySQLdb()
    
    # Inicializar extensiones con la app
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, supports_credentials=True, origins=["http://localhost:5173", "https://exper-track.vercel.app"])
    scheduler.init_app(app)
    
    # Registrar módulos (Blueprints)
    from .routes.auth import auth_bp
    from .routes.inventory import inventory_bp
    from .routes.alerts import alerts_bp
    from .routes.expert import expert_bp
    from .routes.dashboard import dashboard_bp
    from .routes.technical_record import technical_record_bp
    from .routes.system import system_bp
    
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(inventory_bp, url_prefix='')
    app.register_blueprint(alerts_bp, url_prefix='')
    app.register_blueprint(expert_bp, url_prefix='')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(technical_record_bp, url_prefix='')
    app.register_blueprint(system_bp, url_prefix='')
    
    # Inicialización de servicios con el contexto de la app
    with app.app_context():
        try:
            from .services.prolog_service import inicializar_prolog, sincronizar_hechos_prolog
            from .services.alert_logic import verificar_alertas_programadas
            
            # 1. Cargar motor de Prolog y sincronizar
            inicializar_prolog()
            sincronizar_hechos_prolog()
            
            # 2. Configurar tarea recurrente de alertas
            if not scheduler.running:
                scheduler.start() # <--- ¡ESTO FALTABA!
                scheduler.add_job(
                    id='job_alertas_30min', 
                    func=verificar_alertas_programadas, 
                    trigger='interval', 
                    minutes=15,
                    args=[app]  # <--- Pasamos la instancia de la app
                )
                print(">>> Scheduler Job registrado e INICIADO: Alertas cada 30 minutos.")
        except Exception as e:
            print(f">>> Error en inicialización de fábrica: {e}")
            
    return app
