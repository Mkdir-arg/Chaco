# Arquitectura y tecnologías

Descripción técnica del sistema: cómo está construido, qué tecnologías usa y cómo se organizan sus componentes.

---

## Stack tecnológico

### Backend

| Tecnología | Versión | Rol |
|---|---|---|
| Python | 3.12 | Lenguaje principal |
| Django | 4.2 | Framework web |
| Django REST Framework | 3.15 | API REST |
| Django Channels | 4.0 | WebSockets y tiempo real |
| Daphne | 4.0 | Servidor ASGI para WebSockets |
| Gunicorn + Gevent | 23.0 | Servidor WSGI para producción |

### Base de datos y caché

| Tecnología | Versión | Rol |
|---|---|---|
| MySQL | 8.0 | Base de datos principal |
| Redis | 7 | Caché, sesiones y colas de WebSocket |
| Supabase | — | Almacenamiento externo para relevamientos móviles |

### Frontend

| Tecnología | Rol |
|---|---|
| Tailwind CSS | Estilos y diseño responsivo |
| Alpine.js | Interactividad declarativa sin SPA |
| HTML + Django Templates | Renderizado server-side |

### Infraestructura

| Tecnología | Rol |
|---|---|
| Docker | Contenedores de aplicación |
| Docker Compose | Orquestación local y de producción |
| GitHub Actions | CI/CD y deploy automático de documentación |
| GitHub Pages | Publicación de esta documentación |

### Librerías destacadas

| Librería | Rol |
|---|---|
| django-simple-history | Auditoría automática de cambios en modelos |
| django-filter | Filtros avanzados en listados |
| django-health-check | Endpoint de salud del sistema |
| drf-spectacular | Documentación automática de la API REST |
| structlog | Logging estructurado |
| Pillow | Procesamiento de imágenes |
| OpenAI SDK | Integración con modelos de IA |

---

## Superficies del sistema

El sistema tiene tres superficies de acceso diferenciadas:

```
┌─────────────────────────────────────────────────────┐
│                    Usuarios                         │
│                                                     │
│  Backoffice (staff)  │  Portal ciudadano  │  App    │
│  Operadores e        │  Ciudadanos que    │  móvil  │
│  administradores     │  acceden a sus     │  Campo  │
│  institucionales     │  datos y trámites  │         │
└──────────┬───────────────────┬────────────────┬─────┘
           │                   │                │
           └───────────────────┴────────────────┘
                               │
              ┌────────────────▼────────────────┐
              │         Django + Daphne         │
              │   HTTP (Gunicorn) + WS (ASGI)   │
              │   Middlewares: auth, institución │
              └────────────────┬────────────────┘
                               │
              ┌────────────────▼────────────────┐
              │         Apps de dominio         │
              │                                 │
              │  legajos · configuracion        │
              │  conversaciones · portal        │
              │  users · dashboard · tramites   │
              └────────────────┬────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
  ┌────────▼───────┐  ┌────────▼───────┐  ┌───────▼────────┐
  │   MySQL 8      │  │   Redis 7      │  │   Supabase     │
  │  Datos         │  │  Caché         │  │  Relevamientos │
  │  principales   │  │  Sesiones      │  │  móviles       │
  │                │  │  WebSockets    │  │                │
  └────────────────┘  └────────────────┘  └────────────────┘
```

---

## Módulos del sistema

Cada módulo es una app Django independiente con responsabilidad acotada:

| Módulo | Responsabilidad |
|---|---|
| `legajos` | Gestión de ciudadanos, programas sociales, derivaciones y módulo NACHEC |
| `configuracion` | Instituciones, secretarías, dispositivos, programas, geografía y clases |
| `conversaciones` | Chat en tiempo real, colas de atención y métricas de atención |
| `portal` | Portal ciudadano: autenticación, perfil, consultas y trámites self-service |
| `users` | Usuarios del backoffice, grupos, permisos y roles |
| `dashboard` | Métricas, indicadores y vistas de inicio por rol |
| `tramites` | Seguimiento de trámites institucionales |
| `core` | Modelos base, utilidades, caché, performance y relevamientos |
| `security` | Autenticación avanzada, autorización y auditoría |
| `healthcheck` | Endpoint de salud para monitoreo de infraestructura |

---

## Patrón de capas interno

Cada módulo sigue el mismo patrón de organización interna:

```
<modulo>/
├── models.py        → definición de datos y relaciones
├── selectors/       → consultas de lectura, sin efectos secundarios
├── services/        → lógica de negocio y operaciones de escritura
├── views/           → orquestación HTTP: recibe, delega, responde
├── forms/           → validación de entrada del usuario
└── templates/       → presentación HTML
```

Este patrón garantiza que la lógica de negocio vive en `services/`, es reutilizable desde cualquier punto del sistema (vistas, comandos, señales, API) y es testeable de forma aislada.

---

## Tiempo real

El sistema usa **WebSockets** para funcionalidades que requieren actualización inmediata sin recargar la página:

- Chat entre operadores y ciudadanos (módulo `conversaciones`)
- Notificaciones de alertas y derivaciones
- Actualizaciones de estado en tiempo real

La infraestructura de tiempo real usa **Django Channels** con **Redis** como capa de mensajería (channel layer). El servidor **Daphne** maneja las conexiones ASGI en producción.

---

## Auditoría

Todos los cambios en modelos críticos quedan registrados automáticamente usando **django-simple-history**. Cada modificación guarda: qué cambió, quién lo cambió y cuándo. Esto permite reconstruir el historial completo de cualquier registro.

---

## App móvil

La app móvil está construida con **Expo / React Native** y se conecta directamente a **Supabase** para el almacenamiento de relevamientos de campo. Está pensada para trabajo offline-first: los operadores de campo pueden cargar datos sin conexión y sincronizar cuando tienen red.
