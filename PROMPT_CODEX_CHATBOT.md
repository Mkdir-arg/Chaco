# PROMPT PARA CODEX - SOLUCIÓN CHATBOT

## CONTEXTO

Tengo un chatbot en Django que está dando "Error interno del servidor" cuando el usuario escribe "hola".

**Rama actual:** Retoque
**Rama que funciona:** IA

## PROBLEMA

Cuando el usuario escribe "hola" en el chatbot, recibe:
```
Error interno del servidor
```

## ARCHIVOS INVOLUCRADOS

1. `chatbot/views.py` - Vista que recibe el mensaje
2. `chatbot/ai_service_enhanced.py` - Servicio de IA
3. `templates/components/chatbot_bubble.html` - Interfaz del chatbot
4. `chatbot/urls.py` - URLs del chatbot

## ENDPOINT

```
POST /chatbot/api/send-message/
Body: {"message": "hola"}
Headers: 
  - Content-Type: application/json
  - X-CSRFToken: <token>
```

## TAREA

1. **Compara** los archivos entre la rama `Retoque` y la rama `IA`:
   - `chatbot/views.py`
   - `chatbot/ai_service_enhanced.py`
   - `chatbot/urls.py`

2. **Identifica** qué está causando el error interno del servidor

3. **Copia** EXACTAMENTE la implementación de la rama `IA` que funciona

4. **Verifica** que:
   - El servicio `EnhancedChatbotService` se inicialice correctamente
   - El método `generate_response()` maneje errores
   - La vista `send_message()` devuelva siempre JSON válido
   - No haya imports faltantes

## COMANDOS ÚTILES

```bash
# Ver diferencias entre ramas
git diff Retoque..IA -- chatbot/views.py
git diff Retoque..IA -- chatbot/ai_service_enhanced.py

# Ver archivo completo de rama IA
git show IA:chatbot/views.py
git show IA:chatbot/ai_service_enhanced.py

# Ver logs del servidor
docker-compose logs web --tail=100
```

## REQUISITOS DE LA SOLUCIÓN

1. **Debe funcionar sin OpenAI** para saludos básicos
2. **Debe responder "hola"** con un mensaje de bienvenida
3. **Debe consultar la BD** para preguntas como "¿cuántos ciudadanos?"
4. **Debe manejar errores** sin romper el servidor
5. **Debe devolver** siempre `{"success": true/false, "response": "..."}`

## ESTRUCTURA ESPERADA

### ai_service_enhanced.py
```python
class EnhancedChatbotService:
    def __init__(self):
        # Inicializar cliente OpenAI
        # Manejar si no está disponible
        pass
    
    def generate_response(self, message, conversation_history=None):
        # 1. Detectar saludos → respuesta directa
        # 2. Detectar consultas BD → consultar y responder
        # 3. Otras preguntas → usar OpenAI si disponible
        # 4. Siempre devolver dict con 'content' y 'tokens_used'
        pass
```

### views.py
```python
@login_required
@csrf_exempt
def send_message(request):
    try:
        # 1. Parsear JSON
        # 2. Crear conversación
        # 3. Guardar mensaje usuario
        # 4. Llamar ai_service.generate_response()
        # 5. Guardar respuesta
        # 6. Retornar {"success": True, "response": "..."}
    except Exception as e:
        return JsonResponse({"success": False, "error": "..."}, status=500)
```

## VALIDACIÓN

Después de implementar, probar:

```bash
# Test 1: Saludo
curl -X POST http://localhost:9000/chatbot/api/send-message/ \
  -H "Content-Type: application/json" \
  -d '{"message": "hola"}'

# Esperado: {"success": true, "response": "¡Hola! Soy el Asistente NODO..."}

# Test 2: Consulta BD
curl -X POST http://localhost:9000/chatbot/api/send-message/ \
  -H "Content-Type: application/json" \
  -d '{"message": "¿cuántos ciudadanos hay?"}'

# Esperado: {"success": true, "response": "Total: X ciudadanos..."}
```

## ARCHIVOS A REVISAR EN RAMA IA

```bash
git show IA:chatbot/views.py
git show IA:chatbot/ai_service_enhanced.py
git show IA:chatbot/urls.py
git show IA:templates/components/chatbot_bubble.html
```

## CHECKLIST DE SOLUCIÓN

- [ ] `EnhancedChatbotService` se importa correctamente
- [ ] `__init__()` no lanza excepciones
- [ ] `generate_response()` siempre retorna dict con 'content'
- [ ] Vista `send_message()` maneja todas las excepciones
- [ ] URL `/chatbot/api/send-message/` está registrada
- [ ] CSRF está deshabilitado con `@csrf_exempt`
- [ ] Usuario está autenticado con `@login_required`
- [ ] Respuesta JSON siempre tiene `success` y `response`/`error`

## RESULTADO ESPERADO

Cuando el usuario escribe "hola", debe recibir:
```json
{
  "success": true,
  "response": "¡Hola! Soy el Asistente NODO. Pregúntame sobre ciudadanos, usuarios o estadísticas del sistema."
}
```

Sin errores 500, sin excepciones, sin problemas de imports.
