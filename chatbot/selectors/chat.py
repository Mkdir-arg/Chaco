from datetime import datetime

from django.conf import settings
from django.db import models

from ..models import ChatbotKnowledge, Conversation, Message


def get_user_conversations(user, limit=10):
    return Conversation.objects.filter(user=user)[:limit]


def get_user_conversation(conversation_id, user):
    return Conversation.objects.prefetch_related("messages").filter(
        id=conversation_id, user=user
    ).first()


def get_user_conversation_queryset(user):
    return Conversation.objects.prefetch_related("messages").filter(user=user)


def build_admin_dashboard_payload():
    today = datetime.now().date()
    stats = {
        "conversations_today": Conversation.objects.filter(created_at__date=today).count(),
        "messages_today": Message.objects.filter(timestamp__date=today).count(),
        "tokens_used": Message.objects.filter(timestamp__date=today).aggregate(
            total=models.Sum("tokens_used")
        )["total"]
        or 0,
    }

    api_key = getattr(settings, "OPENAI_API_KEY", None)
    system_status = {
        "api_status": bool(api_key and len(api_key) > 20),
        "api_message": "Configurada" if api_key else "No configurada",
    }

    recent_conversations = [
        {
            "id": conv.id,
            "user": conv.user.username,
            "timestamp": conv.created_at.strftime("%d/%m/%Y %H:%M"),
            "messages_count": conv.messages.count(),
            "last_message": last_message.content[:100] if last_message else "Sin mensajes",
        }
        for conv in Conversation.objects.select_related("user").order_by("-created_at")[
            :5
        ]
        for last_message in [conv.messages.order_by("-timestamp").first()]
    ]

    knowledge = [
        {
            "id": item.id,
            "title": item.title,
            "content": item.content,
            "category": item.category,
            "is_active": item.is_active,
        }
        for item in ChatbotKnowledge.objects.order_by("-created_at")[:10]
    ]

    return {
        "system_status": system_status,
        "stats": stats,
        "recent_conversations": recent_conversations,
        "knowledge": knowledge,
    }


def get_chat_logs_payload():
    now = datetime.now().strftime("%H:%M:%S")
    return [
        {
            "id": 1,
            "timestamp": now,
            "level": "INFO",
            "message": "Usuario conectado al chat",
        },
        {
            "id": 2,
            "timestamp": now,
            "level": "DEBUG",
            "message": "Procesando mensaje de usuario",
        },
    ]
