# Usa una imagen de Python ligera
FROM python:3.11-slim

# Instala SWI-Prolog (para cuando metas tu motor)
RUN apt-get update && apt-get install -y swi-prolog && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos tu código (app.py, models.py, etc.)
COPY . .

# Exponemos el puerto interno
EXPOSE 5000

CMD ["python", "app.py"]