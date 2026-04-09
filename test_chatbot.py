#!/usr/bin/env python
"""
Script de prueba para el chatbot NODO
Verifica que el servicio de IA funcione correctamente
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chatbot.ai_service import ChatbotAIService

def test_chatbot():
    """Prueba el chatbot con diferentes preguntas"""
    
    print("=" * 60)
    print("PRUEBA DEL CHATBOT ASISTENTE NODO")
    print("=" * 60)
    
    ai_service = ChatbotAIService()
    
    # Preguntas de prueba
    preguntas = [
        "¿Cuántos ciudadanos tenemos registrados?",
        "¿Cuántas instituciones hay?",
        "¿Cuántas actividades por institución tenemos?",
        "¿Cuántos legajos hay en el sistema?",
    ]
    
    for i, pregunta in enumerate(preguntas, 1):
        print(f"\n{i}. Pregunta: {pregunta}")
        print("-" * 60)
        
        try:
            response = ai_service.generate_response(pregunta, [])
            print(f"Respuesta: {response['content']}")
            print(f"Tokens usados: {response.get('tokens_used', 0)}")
        except Exception as e:
            print(f"ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    test_chatbot()
