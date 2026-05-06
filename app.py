# app.py - ARCHIVO PUENTE
# Este archivo redirige a la nueva arquitectura modular.
# Útil para no romper el despliegue automático (CI/CD) mientras se actualiza el servidor.

from run import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)