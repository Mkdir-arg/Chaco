# Sistema de Conversaciones SEDRONAR

Sistema de chat en tiempo real entre ciudadanos y operadores del backoffice.

## Características

### Para Ciudadanos
- **Chat público**: Acceso sin autenticación en `/conversaciones/chat/`
- **Dos modalidades**:
  - **Anónima**: Sin identificación
  - **Personal**: Requiere DNI
- **Interfaz simple**: Chat en tiempo real con polling automático

### Para Operadores (Backoffice)
- **Gestión de conversaciones**: Lista y detalle de todas las conversaciones
- **Asignación automática**: El primer operador que responde queda asignado
- **Estados**: Conversaciones activas y cerradas
- **Permisos**: Solo usuarios del grupo "Conversaciones"

## Instalación

1. **Ejecutar migraciones**:
```bash
docker compose exec django python manage.py migrate
```

2. **Configurar grupo y permisos**:
```bash
docker compose exec django python manage.py setup_conversaciones
```

3. **Asignar usuarios al grupo**:
   - Ir al admin de Django
   - Asignar usuarios al grupo "Conversaciones"

## URLs

### Ciudadanos (Públicas)
- `/conversaciones/chat/` - Interfaz de chat
- `/conversaciones/iniciar/` - API para iniciar conversación
- `/conversaciones/<id>/enviar/` - API para enviar mensaje
- `/conversaciones/<id>/mensajes/` - API para obtener mensajes

### Backoffice (Requiere autenticación)
- `/conversaciones/` - Lista de conversaciones
- `/conversaciones/<id>/` - Detalle de conversación
- `/conversaciones/<id>/responder/` - API para responder
- `/conversaciones/<id>/cerrar/` - Cerrar conversación

## Modelos

### Conversacion
- `tipo`: 'anonima' o 'personal'
- `estado`: 'activa' o 'cerrada'
- `dni_ciudadano`: Solo para conversaciones personales
- `operador_asignado`: Usuario que atiende la conversación
- `fecha_inicio` / `fecha_cierre`

### Mensaje
- `conversacion`: FK a Conversacion
- `remitente`: 'ciudadano' o 'operador'
- `contenido`: Texto del mensaje
- `fecha_envio`
- `leido`: Para marcar mensajes como leídos

## Funcionalidades Técnicas

- **Polling**: El chat ciudadano actualiza mensajes cada 2 segundos
- **CSRF exempt**: APIs de ciudadanos sin CSRF para simplicidad
- **Responsive**: Interfaz adaptable a móviles
- **Alpine.js**: JavaScript reactivo en el frontend
- **Tailwind CSS**: Estilos utilitarios

## Seguridad

- Las APIs públicas solo permiten operaciones básicas
- Los ciudadanos no pueden ver conversaciones de otros
- Los operadores requieren autenticación y permisos específicos
- Validación de entrada en todos los endpoints