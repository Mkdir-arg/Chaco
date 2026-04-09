# Arquitectura del Sistema SistemSo

## 1. Stack Tecnológico

### Backend
- **Framework**: Django 4.2.20 (Python)
- **API REST**: Django REST Framework 3.15.2
- **WebSockets**: Django Channels 4.0.0 + Daphne 4.0.0
- **ASGI/WSGI**: Daphne (WebSockets) + Gunicorn (HTTP)

### Base de Datos
- **Motor**: MySQL 8.0
- **ORM**: Django ORM
- **Pool de Conexiones**: mysqlclient 2.1.1
- **Configuración**: 
  - Connection pooling (CONN_MAX_AGE: 60s)
  - Health checks habilitados
  - Isolation level: read committed

### Cache & Mensajería
- **Redis 7**: 
  - DB 1: Cache general (django-redis)
  - DB 2: Sesiones
  - DB 0: Channel Layer (WebSockets)
- **Compresión**: zlib en cache
- **Pool**: 200 conexiones max (cache), 100 (sesiones)

### Servidor Web
- **Producción**: Nginx (proxy reverso)
- **HTTP Workers**: Gunicorn + gevent (async I/O)
- **WebSocket Server**: Daphne
- **Workers**: (CPU * 2) + 1
- **Worker Connections**: 1000 por worker

### Contenedores
- **Docker Compose**: Arquitectura híbrida
- **Servicios**:
  - sedronar-mysql (MySQL 8.0)
  - sedronar-redis (Redis 7)
  - sedronar-http (Gunicorn)
  - sedronar-ws (Daphne)
  - nginx (Proxy)

---

## 2. Arquitectura de Aplicación

### Patrón: Monolito Modular con Microservicios Internos

```
┌─────────────────────────────────────────────────────────┐
│                    NGINX (Puerto 9000)                   │
│  - Proxy reverso                                         │
│  - Balanceo de carga                                     │
│  - Archivos estáticos                                    │
└────────────┬────────────────────────────┬────────────────┘
             │                            │
    ┌────────▼────────┐          ┌───────▼────────┐
    │  Gunicorn:8000  │          │  Daphne:8001   │
    │  (HTTP/REST)    │          │  (WebSockets)  │
    │  - gevent       │          │  - ASGI        │
    │  - workers      │          │  - Channels    │
    └────────┬────────┘          └───────┬────────┘
             │                            │
             └────────────┬───────────────┘
                          │
         ┌────────────────▼────────────────┐
         │      Django Application         │
         │  ┌──────────────────────────┐   │
         │  │   Apps Modulares         │   │
         │  │  - users                 │   │
         │  │  - core                  │   │
         │  │  - legajos               │   │
         │  │  - conversaciones        │   │
         │  │  - dashboard             │   │
         │  │  - chatbot               │   │
         │  │  - tramites              │   │
         │  │  - portal                │   │
         │  │  - configuracion         │   │
         │  └──────────────────────────┘   │
         └─────────────┬───────────────────┘
                       │
         ┌─────────────┴───────────────┐
         │                             │
    ┌────▼─────┐              ┌───────▼────┐
    │  MySQL   │              │   Redis    │
    │  :3306   │              │   :6379    │
    └──────────┘              └────────────┘
```

---

## 3. Patrones de Diseño Implementados

### 3.1 Arquitectura General
- **Monolito Modular**: Apps Django independientes con responsabilidades claras
- **Service Layer**: Lógica de negocio separada de vistas (ej: `AlertasService`)
- **Repository Pattern**: Managers personalizados en modelos

### 3.2 Comunicación
- **Pub/Sub**: Channel Layers para WebSockets
- **Event-Driven**: Signals de Django para eventos del sistema
- **Observer**: Consumers de Channels escuchan eventos

### 3.3 Middleware Chain
```python
SecurityMiddleware
  → ConcurrencyLimitMiddleware
  → SilkyMiddleware (profiling)
  → GZipMiddleware
  → RequestMetricsMiddleware
  → MonitoringMiddleware
  → PerformanceMiddleware
  → SessionMiddleware
  → AuthenticationMiddleware
  → AuditoriaMiddleware
  → AccesoSensibleMiddleware
  → DescargaArchivoMiddleware
  → SesionUsuarioMiddleware
  → QueryCountMiddleware
  → InstitucionRedirectMiddleware
```

### 3.4 Cache Strategy
- **Cache-Aside**: Datos consultados frecuentemente
- **Write-Through**: Sesiones en Redis
- **TTL**: 300s (5 min) por defecto
- **Compresión**: zlib para reducir memoria

### 3.5 Concurrencia
- **Gevent**: Workers asíncronos para I/O
- **Connection Pooling**: Reutilización de conexiones DB
- **Channel Layers**: Comunicación entre workers

---

## 4. Sistema de Mensajería en Tiempo Real

### 4.1 Arquitectura WebSocket

```
Cliente (Browser)
    │
    │ WebSocket Connection
    │
    ▼
Nginx (:9000)
    │
    │ Proxy Pass /ws/
    │
    ▼
Daphne (:8001)
    │
    │ ASGI Protocol
    │
    ▼
Django Channels
    │
    ├─► ConversacionConsumer
    ├─► ConversacionesListConsumer
    ├─► AlertasConsumer
    └─► AlertasConversacionesConsumer
    │
    ▼
Redis Channel Layer
    │
    └─► Broadcast a todos los workers
```

### 4.2 Consumers Implementados

#### ConversacionConsumer
- **Ruta**: `/ws/conversaciones/<id>/`
- **Función**: Chat 1:1 entre operador y ciudadano
- **Grupos**: `conversacion_{id}`
- **Permisos**: Grupos 'Conversaciones', 'OperadorCharla'
- **Features**:
  - Asignación automática de operador
  - Persistencia de mensajes en BD
  - Alertas de respuesta rápida

#### ConversacionesListConsumer
- **Ruta**: `/ws/conversaciones/`
- **Función**: Notificaciones de nuevas conversaciones
- **Grupos**: `conversaciones_list`
- **Eventos**:
  - `nueva_conversacion`
  - `nuevo_mensaje`
  - `actualizar_lista`

#### AlertasConsumer
- **Ruta**: `/ws/alertas/`
- **Función**: Sistema de alertas del sistema
- **Grupos**: `alertas_sistema`
- **Permisos**: Grupos 'Legajos', 'Supervisores', 'Coordinadores'
- **Eventos**:
  - `nueva_alerta`
  - `alerta_critica`
  - `alerta_cerrada`

#### AlertasConversacionesConsumer
- **Ruta**: `/ws/alertas-conversaciones/`
- **Función**: Alertas específicas por operador
- **Grupos**: `conversaciones_operador_{user_id}`
- **Eventos**: `nueva_alerta_conversacion`

### 4.3 Flujo de Mensaje

```
1. Usuario envía mensaje
   ↓
2. Consumer.receive() recibe JSON
   ↓
3. @database_sync_to_async guarda en MySQL
   ↓
4. channel_layer.group_send() publica a Redis
   ↓
5. Redis broadcast a todos los workers
   ↓
6. Todos los consumers del grupo reciben
   ↓
7. Consumer.chat_message() envía a WebSocket
   ↓
8. Cliente recibe mensaje en tiempo real
```

---

## 5. Optimizaciones de Performance

### 5.1 Base de Datos
- **Connection Pooling**: 60s de reutilización
- **Health Checks**: Verificación antes de reusar
- **Timeouts**: 10s (connect, read, write)
- **Charset**: utf8mb4 (emojis y caracteres especiales)

### 5.2 Cache
- **Redis**: 3 bases de datos separadas
- **Compresión**: zlib en cache general
- **Pool**: 200 conexiones simultáneas
- **TTL**: 300s por defecto

### 5.3 Workers
- **Gunicorn**: gevent workers (async I/O)
- **Fórmula**: (CPU * 2) + 1 workers
- **Connections**: 1000 por worker
- **Max Requests**: 1000 (reciclar workers)
- **Preload**: True (mejor performance)

### 5.4 Middleware
- **GZip**: Compresión de respuestas
- **ConcurrencyLimit**: Limitar requests concurrentes
- **RequestMetrics**: Monitoreo en tiempo real
- **QueryCount**: Detectar N+1 queries

### 5.5 Profiling
- **Silk**: Performance profiling
- **Intercept**: 100% en dev, 10% en prod
- **Python Profiler**: Habilitado

---

## 6. Seguridad

### 6.1 Middleware de Seguridad
- **SecurityMiddleware**: Headers de seguridad
- **XSSProtectionMiddleware**: Protección XSS
- **CSRF**: Tokens en formularios
- **Clickjacking**: X-Frame-Options

### 6.2 Auditoría
- **AuditoriaMiddleware**: Log de acciones
- **AccesoSensibleMiddleware**: Log de datos sensibles
- **DescargaArchivoMiddleware**: Log de descargas
- **SesionUsuarioMiddleware**: Tracking de sesiones

### 6.3 Autenticación
- **Django Auth**: Sistema nativo
- **Grupos**: Control de permisos granular
- **Sesiones**: Redis (seguras y rápidas)

### 6.4 Producción
- **HTTPS**: Forzado en producción
- **HSTS**: 1 año
- **Secure Cookies**: Session y CSRF
- **SSL Redirect**: Automático

---

## 7. Logging y Monitoreo

### 7.1 Logs Separados
- `info.log`: Información general
- `error.log`: Errores
- `warning.log`: Advertencias
- `critical.log`: Críticos
- `data.log`: Datos estructurados (JSON)

### 7.2 Formato
- **Verbose**: Timestamp, módulo, nivel, mensaje
- **JSON**: Para data.log (parseable)

### 7.3 Rotación
- **DailyFileHandler**: Rotación diaria automática

### 7.4 Health Checks
- **Endpoint**: `/health/`
- **Checks**: DB, Cache, Disk, Memory
- **Nginx**: Healthcheck cada 10s

---

## 8. Deployment en Ubuntu + Nginx

### 8.1 Arquitectura Recomendada

```
Internet
    │
    ▼
Nginx (Host Ubuntu :80/443)
    │
    ├─► /static/ → Archivos estáticos
    ├─► /media/ → Archivos subidos
    ├─► /ws/ → Docker Daphne :8001
    └─► / → Docker Gunicorn :8000
    │
    ▼
Docker Compose
    ├─► sedronar-http (Gunicorn)
    ├─► sedronar-ws (Daphne)
    ├─► sedronar-mysql (MySQL)
    └─► sedronar-redis (Redis)
```

### 8.2 Configuración Nginx Host

```nginx
upstream docker_http {
    server localhost:8000;
}

upstream docker_ws {
    server localhost:8001;
}

server {
    listen 80;
    server_name tu-dominio.com;
    
    # Redirigir a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;
    
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;
    
    client_max_body_size 100M;
    
    # WebSockets
    location /ws/ {
        proxy_pass http://docker_ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # Static files
    location /static/ {
        alias /ruta/al/proyecto/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /ruta/al/proyecto/media/;
        expires 30d;
    }
    
    # HTTP
    location / {
        proxy_pass http://docker_http;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 8.3 Variables de Entorno (.env)

```bash
# Django
DJANGO_SECRET_KEY=tu-secret-key-segura
DJANGO_DEBUG=False
ENVIRONMENT=prd
DJANGO_ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Database
DATABASE_NAME=sedronar
DATABASE_USER=sedronar
DATABASE_PASSWORD=password-seguro
DATABASE_HOST=sedronar-mysql
DATABASE_PORT=3306

# Redis (interno Docker)
REDIS_HOST=sedronar-redis
REDIS_PORT=6379

# Dominio
DOMINIO=tu-dominio.com
```

---

## 9. Mejoras Recomendadas

### 9.1 Escalabilidad
- [ ] Separar Redis en 3 instancias (cache, sessions, channels)
- [ ] Implementar Celery para tareas asíncronas
- [ ] Considerar PostgreSQL (mejor concurrencia que MySQL)
- [ ] Load balancer para múltiples instancias de Gunicorn

### 9.2 Monitoreo
- [ ] Prometheus + Grafana para métricas
- [ ] Sentry para tracking de errores
- [ ] ELK Stack para logs centralizados
- [ ] APM (New Relic, DataDog)

### 9.3 Seguridad
- [ ] Rate limiting por IP
- [ ] WAF (Web Application Firewall)
- [ ] Backup automático de BD
- [ ] Secrets management (Vault, AWS Secrets Manager)

### 9.4 Performance
- [ ] CDN para archivos estáticos
- [ ] Database read replicas
- [ ] Query optimization (índices, explain)
- [ ] Lazy loading de relaciones

---

## 10. Comandos Útiles

### Desarrollo
```bash
# Levantar servicios
docker-compose -f docker-compose.hybrid.yml up -d

# Ver logs
docker-compose logs -f sedronar-http
docker-compose logs -f sedronar-ws

# Ejecutar migraciones
docker-compose exec sedronar-ws python manage.py migrate

# Crear superusuario
docker-compose exec sedronar-ws python manage.py createsuperuser

# Collectstatic
docker-compose exec sedronar-http python manage.py collectstatic --noinput
```

### Producción
```bash
# Build y deploy
docker-compose -f docker-compose.hybrid.yml build
docker-compose -f docker-compose.hybrid.yml up -d

# Backup BD
docker-compose exec sedronar-mysql mysqldump -u sedronar -p sedronar > backup.sql

# Restore BD
docker-compose exec -T sedronar-mysql mysql -u sedronar -p sedronar < backup.sql

# Ver métricas
docker stats

# Limpiar
docker system prune -a
```
