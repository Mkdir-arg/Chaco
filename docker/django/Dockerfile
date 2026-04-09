FROM python:3.11.9-bullseye

WORKDIR /sisoc

# Variables de entorno generales para Python y el sistema
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=es_AR.UTF-8
ENV LC_ALL=es_AR.UTF-8

# Instalación de dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      default-libmysqlclient-dev \
      gcc \
      libc-dev \
      bash \
      mariadb-client \
      locales \
      curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configuración de locales
RUN echo "es_AR.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen && \
    echo "LANG=es_AR.UTF-8" > /etc/default/locale && \
    echo "LC_ALL=es_AR.UTF-8" >> /etc/default/locale

# Copiar archivos del proyecto
COPY . .

# Instalación de dependencias de la aplicación
RUN pip install --upgrade pip && pip install -r requirements.txt && \
    pip install pymysql django-redis==5.4.0 redis==5.0.1 django-health-check==3.17.0

# Hacer ejecutable el entrypoint y startup script
RUN chmod +x ./docker/django/entrypoint_final.py
RUN chmod +x ./scripts/startup.sh

# Comando de inicio con optimizaciones automáticas
CMD ["./scripts/startup.sh", "python", "./docker/django/entrypoint_final.py"]
