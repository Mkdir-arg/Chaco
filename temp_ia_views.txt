from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
import json
from datetime import datetime
from .models import Conversation, Message, ChatbotKnowledge, ChatbotFeedback
from .ai_service_enhanced import EnhancedChatbotService


@login_required
def chat_interface(request):
    """Interfaz principal del chat"""
    conversations = Conversation.objects.filter(user=request.user)[:10]
    active_conversation = conversations.first() if conversations.exists() else None
    
    context = {
        'conversations': conversations,
        'active_conversation': active_conversation,
    }
    return render(request, 'chatbot/chat_interface.html', context)


@login_required
@csrf_exempt
def send_message(request):
    """API para enviar mensaje al chatbot desde la burbuja"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)
        
        # Crear conversación temporal para la burbuja
        conversation = Conversation.objects.create(
            user=request.user,
            title=f"Chat {message_content[:30]}..."
        )
        
        # Guardar mensaje del usuario
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=message_content
        )
        
        # Generar respuesta con IA
        ai_service = EnhancedChatbotService()
        response_data = ai_service.generate_response(message_content, [])
        
        # Guardar respuesta del asistente
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=response_data['content'],
            tokens_used=response_data.get('tokens_used', 0)
        )
        
        return JsonResponse({
            'success': True,
            'response': response_data['content']
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)


@login_required
def load_conversation(request, conversation_id):
    """Carga una conversación específica"""
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    messages = conversation.messages.all()
    
    messages_data = []
    for message in messages:
        messages_data.append({
            'id': message.id,
            'role': message.role,
            'content': message.content,
            'timestamp': message.timestamp.isoformat()
        })
    
    return JsonResponse({
        'conversation_id': conversation.id,
        'title': conversation.title,
        'messages': messages_data
    })


@login_required
def new_conversation(request):
    """Crea una nueva conversación"""
    conversation = Conversation.objects.create(
        user=request.user,
        title="Nueva conversación"
    )
    return JsonResponse({
        'conversation_id': conversation.id,
        'title': conversation.title
    })


@login_required
def admin_panel(request):
    """Panel de administración del chatbot"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('chatbot:chat_interface')
    
    return render(request, 'chatbot/admin_dashboard.html')


@login_required
@csrf_exempt
def submit_feedback(request):
    """Envía feedback sobre una respuesta"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        message = get_object_or_404(Message, id=message_id)
        
        feedback, created = ChatbotFeedback.objects.get_or_create(
            message=message,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        
        if not created:
            feedback.rating = rating
            feedback.comment = comment
            feedback.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def admin_data(request):
    """API para datos del dashboard admin"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    from datetime import datetime, timedelta
    from django.conf import settings
    
    today = datetime.now().date()
    
    # Estadísticas
    stats = {
        'conversations_today': Conversation.objects.filter(created_at__date=today).count(),
        'messages_today': Message.objects.filter(timestamp__date=today).count(),
        'tokens_used': Message.objects.filter(timestamp__date=today).aggregate(
            total=models.Sum('tokens_used')
        )['total'] or 0
    }
    
    # Estado del sistema
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    system_status = {
        'api_status': bool(api_key and len(api_key) > 20),
        'api_message': 'Configurada' if api_key else 'No configurada'
    }
    
    # Conversaciones recientes
    recent_conversations = []
    for conv in Conversation.objects.select_related('user').order_by('-created_at')[:5]:
        last_message = conv.messages.order_by('-timestamp').first()
        recent_conversations.append({
            'id': conv.id,
            'user': conv.user.username,
            'timestamp': conv.created_at.strftime('%d/%m/%Y %H:%M'),
            'messages_count': conv.messages.count(),
            'last_message': last_message.content[:100] if last_message else 'Sin mensajes'
        })
    
    # Base de conocimiento
    knowledge = []
    for item in ChatbotKnowledge.objects.order_by('-created_at')[:10]:
        knowledge.append({
            'id': item.id,
            'title': item.title,
            'content': item.content,
            'category': item.category,
            'is_active': item.is_active
        })
    
    return JsonResponse({
        'system_status': system_status,
        'stats': stats,
        'recent_conversations': recent_conversations,
        'knowledge': knowledge
    })


@login_required
def chat_logs(request):
    """API para logs del chat"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    # Simular logs (en producción usar logging real)
    logs = [
        {
            'id': 1,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'INFO',
            'message': 'Usuario conectado al chat'
        },
        {
            'id': 2,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'DEBUG',
            'message': 'Procesando mensaje de usuario'
        }
    ]
    
    return JsonResponse({'logs': logs})


@login_required
@csrf_exempt
def update_api_key(request):
    """Actualizar API Key de OpenAI"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return JsonResponse({'error': 'API Key requerida'}, status=400)
        
        # En producción, guardar en base de datos o archivo de configuración
        # Por ahora solo validamos el formato
        if not api_key.startswith('sk-'):
            return JsonResponse({'error': 'Formato de API Key inválido'}, status=400)
        
        return JsonResponse({'success': True, 'message': 'API Key actualizada'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def test_api_key(request):
    """Probar conexión con OpenAI"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        ai_service = EnhancedChatbotService()
        response = ai_service.generate_response('test', [])
        
        if 'error' in response:
            return JsonResponse({'success': False, 'message': f'Error: {response["error"][:100]}'}, status=400)
        
        return JsonResponse({'success': True, 'message': 'API Key funcionando correctamente'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error de conexión: {str(e)[:100]}'}, status=500)


@login_required
@csrf_exempt
def add_knowledge(request):
    """Agregar conocimiento"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        knowledge = ChatbotKnowledge.objects.create(
            title=data['title'],
            content=data['content'],
            category=data['category'],
            is_active=True
        )
        
        return JsonResponse({'success': True, 'id': knowledge.id})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def delete_knowledge(request, knowledge_id):
    """Eliminar conocimiento"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        knowledge = get_object_or_404(ChatbotKnowledge, id=knowledge_id)
        knowledge.delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)