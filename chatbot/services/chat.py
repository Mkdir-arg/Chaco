from django.shortcuts import get_object_or_404

from ..ai_service_enhanced import EnhancedChatbotService
from ..models import ChatbotFeedback, ChatbotKnowledge, Conversation, Message


def get_or_create_bubble_conversation(session, user, message_content):
    session_key = "chatbot_bubble_conversation_id"
    conversation_id = session.get(session_key)
    conversation = None

    if conversation_id:
        conversation = Conversation.objects.filter(
            id=conversation_id,
            user=user,
            is_active=True,
        ).first()

    if not conversation:
        conversation = Conversation.objects.create(
            user=user,
            title=f"Chat {message_content[:30]}...",
        )
        session[session_key] = conversation.id

    return conversation


def send_message_to_chatbot(session, user, message_content):
    conversation = get_or_create_bubble_conversation(session, user, message_content)
    history = list(
        conversation.messages.only("role", "content").order_by("timestamp")[:20]
    )

    user_message = Message.objects.create(
        conversation=conversation,
        role="user",
        content=message_content,
    )

    ai_service = EnhancedChatbotService()
    response_data = ai_service.generate_response(message_content, history)

    assistant_message = Message.objects.create(
        conversation=conversation,
        role="assistant",
        content=response_data["content"],
        tokens_used=response_data.get("tokens_used", 0),
    )

    response_data["conversation_id"] = conversation.id
    response_data["user_message_id"] = user_message.id
    response_data["assistant_message_id"] = assistant_message.id
    response_data["user_message_timestamp"] = user_message.timestamp.isoformat()
    response_data["assistant_message_timestamp"] = assistant_message.timestamp.isoformat()
    return response_data


def submit_feedback_for_message(user, cleaned_data):
    message = get_object_or_404(Message, id=cleaned_data["message_id"])
    feedback, created = ChatbotFeedback.objects.get_or_create(
        message=message,
        user=user,
        defaults={
            "rating": cleaned_data["rating"],
            "comment": cleaned_data.get("comment", ""),
        },
    )

    if not created:
        feedback.rating = cleaned_data["rating"]
        feedback.comment = cleaned_data.get("comment", "")
        feedback.save(update_fields=["rating", "comment"])

    return feedback


def validate_api_key_format(api_key):
    return api_key.startswith("sk-")


def test_api_connection():
    ai_service = EnhancedChatbotService()
    return ai_service.generate_response("test", [])


def add_knowledge_entry(cleaned_data):
    return ChatbotKnowledge.objects.create(
        title=cleaned_data["title"],
        content=cleaned_data["content"],
        category=cleaned_data["category"],
        is_active=True,
    )


def delete_knowledge_entry(knowledge_id):
    knowledge = get_object_or_404(ChatbotKnowledge, id=knowledge_id)
    knowledge.delete()
    return knowledge_id
