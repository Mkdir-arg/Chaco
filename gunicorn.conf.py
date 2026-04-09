# Configuración Gunicorn optimizada para recursos limitados
import multiprocessing
import os

# Establecer variable de entorno para detección de gevent
os.environ['GUNICORN_WORKER_CLASS'] = 'gevent'

# Workers optimizados para memoria limitada
workers = 3  # Reducido para optimizar memoria
worker_class = "gevent"  # Async workers para I/O intensivo
worker_connections = 1000  # Conexiones por worker

# Configuración de memoria y timeouts
max_requests = 1000  # Reciclar workers cada 1000 requests
max_requests_jitter = 100  # Variación aleatoria
timeout = 30  # Timeout de requests
keepalive = 5  # Keep-alive connections

# Configuración de bind
bind = "0.0.0.0:8001"
backlog = 2048  # Queue de conexiones pendientes

# Logging
accesslog = "-"  # Stdout
errorlog = "-"   # Stderr
loglevel = "info"

# Preload para mejor performance
preload_app = True

# Configuración de procesos
user = None
group = None
tmp_upload_dir = None

# Hooks para monitoreo
def when_ready(server):
    server.log.info("Servidor listo para 1000+ usuarios concurrentes")

def worker_int(worker):
    worker.log.info("Worker interrumpido")

def pre_fork(server, worker):
    server.log.info("Worker [booting] iniciando")