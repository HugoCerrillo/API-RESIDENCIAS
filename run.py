from app import create_app, scheduler

app = create_app()

if __name__ == '__main__':
    # Iniciamos el scheduler si no está corriendo
    if not scheduler.running:
        scheduler.start()
        
    app.run(debug=True, port=5000)
