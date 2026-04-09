#!/usr/bin/env python
"""
Script de diagnóstico para verificar el consumo de la API key de OpenAI
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from chatbot.ai_service import ChatbotAIService

print("=" * 70)
print("DIAGNÓSTICO DEL CHATBOT - CONSUMO DE API KEY")
print("=" * 70)

# 1. Verificar que la API key esté en settings
print("\n1. VERIFICANDO API KEY EN SETTINGS")
print("-" * 70)
api_key = getattr(settings, 'OPENAI_API_KEY', None)
if api_key:
    print(f"✅ API Key encontrada: {api_key[:20]}...{api_key[-10:]}")
    print(f"   Longitud: {len(api_key)} caracteres")
else:
    print("❌ API Key NO encontrada en settings")

# 2. Verificar inicialización del servicio
print("\n2. VERIFICANDO INICIALIZACIÓN DEL SERVICIO")
print("-" * 70)
try:
    ai_service = ChatbotAIService()
    print(f"✅ Servicio inicializado correctamente")
    print(f"   OpenAI disponible: {ai_service.openai_available}")
    print(f"   Modelo: {ai_service.model if ai_service.openai_available else 'N/A'}")
    print(f"   Max tokens: {ai_service.max_tokens if ai_service.openai_available else 'N/A'}")
except Exception as e:
    print(f"❌ Error al inicializar servicio: {str(e)}")
    ai_service = None

# 3. Probar consulta a base de datos (sin OpenAI)
print("\n3. PROBANDO CONSULTA A BASE DE DATOS (SIN OPENAI)")
print("-" * 70)
if ai_service:
    try:
        response = ai_service.generate_response("hola", [])
        print(f"✅ Respuesta generada:")
        print(f"   Contenido: {response['content'][:100]}...")
        print(f"   Tokens usados: {response.get('tokens_used', 0)}")
        print(f"   Error: {response.get('error', 'Ninguno')}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# 4. Probar consulta que requiere OpenAI
print("\n4. PROBANDO CONSULTA QUE REQUIERE OPENAI")
print("-" * 70)
if ai_service and ai_service.openai_available:
    try:
        response = ai_service.generate_response("¿Qué es SEDRONAR?", [])
        print(f"✅ Respuesta generada con OpenAI:")
        print(f"   Contenido: {response['content'][:150]}...")
        print(f"   Tokens usados: {response.get('tokens_used', 0)}")
        if 'error' in response:
            print(f"   ⚠️ Error: {response['error']}")
    except Exception as e:
        print(f"❌ Error al usar OpenAI: {str(e)}")
        import traceback
        print(traceback.format_exc())
else:
    print("⚠️ OpenAI no disponible, saltando prueba")

# 5. Verificar flujo completo
print("\n5. ANÁLISIS DEL FLUJO")
print("-" * 70)
print("Flujo de ejecución:")
print("1. Usuario envía mensaje → /chatbot/api/send-message/")
print("2. Vista send_message() recibe el mensaje")
print("3. Crea/obtiene conversación")
print("4. Llama a ChatbotAIService.generate_response()")
print("5. El servicio:")
print("   a) Primero intenta query_database() → Respuesta directa (0 tokens)")
print("   b) Si no puede, usa OpenAI → Respuesta con IA (consume tokens)")
print("   c) Si falla, devuelve mensaje de fallback")

# 6. Resumen
print("\n6. RESUMEN")
print("=" * 70)
if api_key and ai_service and ai_service.openai_available:
    print("✅ CONFIGURACIÓN CORRECTA")
    print("   - API Key configurada")
    print("   - Servicio inicializado")
    print("   - OpenAI disponible")
    print("\n   El chatbot PUEDE consumir la API de OpenAI")
elif api_key and ai_service:
    print("⚠️ CONFIGURACIÓN PARCIAL")
    print("   - API Key configurada")
    print("   - Servicio inicializado")
    print("   - OpenAI NO disponible (posible error de conexión)")
    print("\n   El chatbot funciona SOLO con consultas a BD")
else:
    print("❌ CONFIGURACIÓN INCORRECTA")
    print("   - Revisar API Key en .env")
    print("   - Reiniciar contenedor")

print("\n" + "=" * 70)
