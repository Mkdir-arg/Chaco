# Módulo Chatbot SEDRONAR

Asistente virtual inteligente integrado con OpenAI para el sistema SEDRONAR.

## Características

- **Chat en tiempo real** con interfaz moderna
- **Integración con OpenAI** GPT-3.5-turbo
- **Conocimiento contextual** del sistema SEDRONAR
- **Historial de conversaciones** por usuario
- **Panel de administración** para gestionar conocimiento
- **Sistema de feedback** para mejorar respuestas
- **Interfaz responsive** con Tailwind CSS

## Configuración

### 1. Variables de Entorno

Agregar a tu archivo `.env`:

```bash
OPENAI_API_KEY=tu-api-key-aqui
```

### 2. Instalación de Dependencias

```bash
pip install openai==0.28.1
```

### 3. Migraciones

```bash
python manage.py makemigrations chatbot
python manage.py migrate
```

### 4. Datos Iniciales

```bash
python manage.py loaddata chatbot/fixtures/initial_knowledge.json
```

## Uso

### Acceso al Chat

- **URL**: `/chatbot/`
- **Menú**: Sidebar → Chatbot
- **Permisos**: Todos los usuarios autenticados

### Panel de Administración

- **URL**: `/chatbot/admin/`
- **Permisos**: Solo staff/administradores
- **Funciones**: Gestionar base de conocimiento, ver estadísticas

## Estructura de Archivos

```
chatbot/
├── models.py          # Modelos de datos
├── views.py           # Vistas y lógica
├── urls.py            # URLs del módulo
├── ai_service.py      # Servicio de OpenAI
├── admin.py           # Configuración admin
├── templates/         # Plantillas HTML
├── static/           # CSS y JavaScript
└── fixtures/         # Datos iniciales
```

## Modelos de Datos

- **Conversation**: Conversaciones por usuario
- **Message**: Mensajes individuales
- **ChatbotKnowledge**: Base de conocimiento
- **ChatbotFeedback**: Feedback de usuarios

## API Endpoints

- `POST /chatbot/send/` - Enviar mensaje
- `GET /chatbot/conversation/<id>/` - Cargar conversación
- `POST /chatbot/new/` - Nueva conversación
- `POST /chatbot/feedback/` - Enviar feedback

## Costos Estimados

Con suscripción OpenAI de $20/mes:
- ~10,000 consultas mensuales
- Costo por consulta: ~$0.002
- Ideal para sistemas gubernamentales

## Personalización

### Agregar Conocimiento

1. Acceder al panel admin
2. Crear nuevos elementos en "Base de Conocimiento"
3. Categorizar por tipo de información
4. Activar/desactivar según necesidad

### Modificar Prompts

Editar `ai_service.py` → `get_system_context()` para personalizar el comportamiento del asistente.

## Troubleshooting

### Error de API Key
- Verificar que `OPENAI_API_KEY` esté configurada
- Confirmar que la key sea válida

### Respuestas lentas
- Verificar conexión a internet
- Considerar reducir `max_tokens` en `ai_service.py`

### Error de permisos
- Verificar que el usuario esté autenticado
- Para admin panel, verificar `is_staff=True`