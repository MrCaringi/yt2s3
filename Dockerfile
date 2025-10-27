# Usamos una imagen base que ya contiene Python (para yt-dlp)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema (ffmpeg y herramientas básicas)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        ca-certificates \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip y instalar dependencias Python
RUN python -m pip install --upgrade pip setuptools
RUN pip install yt-dlp flask requests minio

# Copiar la aplicación
WORKDIR /app
COPY . /app

# Exponer puerto (si usas flask)
EXPOSE 5000

# Comando por defecto
CMD ["python", "app.py"]
