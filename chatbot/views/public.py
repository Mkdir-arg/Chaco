import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from ..forms import FeedbackForm, SendMessageForm
from ..selectors import get_user_conversation_queryset, get_user_conversations
from ..services import send_message_to_chatbot, submit_feedback_for_message


def _json_payload(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "JSON inválido"}, status=400)


def _first_form_error(form, default_message):
    if form.errors:
        return next(iter(form.errors.values()))[0]
    return default_message


@login_required
def chat_interface(request):
    conversations = get_user_conversations(request.user)
    active_conversation = conversations.first() if conversations.exists() else None
    return render(
        request,
        "chatbot/chat_interface.html",
        {
            "conversations": conversations,
            "active_conversation": active_conversation,
            "chatbot_urls": {
                "send_message": reverse("chatbot:send_message"),
                "submit_feedback": reverse("chatbot:submit_feedback"),
                "new_conversation": reverse("chatbot:new_conversation"),
                "conversation_detail_template": reverse(
                    "chatbot:load_conversation", kwargs={"conversation_id": 0}
                ).replace("/0/", "/__ID__/"),
            },
        },
    )


@login_required
def send_message(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    payload, error_response = _json_payload(request)
    if error_response:
        return error_response

    form = SendMessageForm(payload)
    if not form.is_valid() or not form.cleaned_data["message"]:
        return JsonResponse(
            {"error": _first_form_error(form, "Mensaje vacío")},
            status=400,
        )

    try:
        response_data = send_message_to_chatbot(
            request.session,
            request.user,
            form.cleaned_data["message"],
        )
        conversation_id = request.session.get("chatbot_bubble_conversation_id")
        return JsonResponse(
            {
                "success": True,
                "response": response_data["content"],
                "conversation_id": conversation_id,
                "user_message": {
                    "id": response_data.get("user_message_id"),
                    "content": form.cleaned_data["message"],
                    "timestamp": response_data.get("user_message_timestamp"),
                },
                "assistant_message": {
                    "id": response_data.get("assistant_message_id"),
                    "content": response_data["content"],
                    "timestamp": response_data.get("assistant_message_timestamp"),
                },
            }
        )
    except Exception:
        return JsonResponse(
            {
                "success": False,
                "error": "Error interno del servidor",
            },
            status=500,
        )


@login_required
def load_conversation(request, conversation_id):
    conversation = get_object_or_404(
        get_user_conversation_queryset(request.user), id=conversation_id
    )
    return JsonResponse(
        {
            "conversation_id": conversation.id,
            "title": conversation.title,
            "messages": [
                {
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat(),
                }
                for message in conversation.messages.all()
            ],
        }
    )


@login_required
def new_conversation(request):
    from ..models import Conversation

    conversation = Conversation.objects.create(
        user=request.user,
        title="Nueva conversación",
    )
    return JsonResponse(
        {
            "conversation_id": conversation.id,
            "title": conversation.title,
        }
    )


@login_required
def submit_feedback(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    payload, error_response = _json_payload(request)
    if error_response:
        return error_response

    form = FeedbackForm(payload)
    if not form.is_valid():
        return JsonResponse(
            {"error": _first_form_error(form, "Feedback inválido")},
            status=400,
        )

    try:
        submit_feedback_for_message(request.user, form.cleaned_data)
        return JsonResponse({"success": True})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
