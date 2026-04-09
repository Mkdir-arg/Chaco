import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from ..forms import ApiKeyForm, KnowledgeForm
from ..selectors import build_admin_dashboard_payload, get_chat_logs_payload
from ..services import (
    add_knowledge_entry,
    delete_knowledge_entry,
    test_api_connection,
    validate_api_key_format,
)


def _json_payload(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "JSON inválido"}, status=400)


def staff_required(view_func):
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.path.startswith("/chatbot/api/"):
                return JsonResponse({"error": "Sin permisos"}, status=403)
            messages.error(request, "No tienes permisos para acceder a esta sección.")
            return redirect("chatbot:chat_interface")
        return view_func(request, *args, **kwargs)

    return wrapped


@login_required
@staff_required
def admin_panel(request):
    return render(
        request,
        "chatbot/admin_dashboard.html",
        {
            "chatbot_admin_urls": {
                "admin_data": reverse("chatbot:admin_data"),
                "chat_logs": reverse("chatbot:chat_logs"),
                "update_api_key": reverse("chatbot:update_api_key"),
                "test_api_key": reverse("chatbot:test_api_key"),
                "add_knowledge": reverse("chatbot:add_knowledge"),
                "delete_knowledge_template": reverse(
                    "chatbot:delete_knowledge", kwargs={"knowledge_id": 0}
                ).replace("/0/", "/__ID__/"),
            },
        },
    )


@login_required
@staff_required
def admin_data(request):
    return JsonResponse(build_admin_dashboard_payload())


@login_required
@staff_required
def chat_logs(request):
    return JsonResponse({"logs": get_chat_logs_payload()})


@login_required
@staff_required
def update_api_key(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    payload, error_response = _json_payload(request)
    if error_response:
        return error_response

    form = ApiKeyForm(payload)
    if not form.is_valid() or not form.cleaned_data["api_key"]:
        return JsonResponse({"error": "API Key requerida"}, status=400)

    if not validate_api_key_format(form.cleaned_data["api_key"]):
        return JsonResponse({"error": "Formato de API Key inválido"}, status=400)

    return JsonResponse({"success": True, "message": "API Key actualizada"})


@login_required
@staff_required
def test_api_key(request):
    try:
        response = test_api_connection()
        if "error" in response:
            return JsonResponse(
                {
                    "success": False,
                    "message": f"Error: {response['error'][:100]}",
                },
                status=400,
            )
        return JsonResponse(
            {"success": True, "message": "API Key funcionando correctamente"}
        )
    except Exception as exc:
        return JsonResponse(
            {
                "success": False,
                "message": f"Error de conexión: {str(exc)[:100]}",
            },
            status=500,
        )


@login_required
@staff_required
def add_knowledge(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    payload, error_response = _json_payload(request)
    if error_response:
        return error_response

    form = KnowledgeForm(payload)
    if not form.is_valid():
        return JsonResponse({"error": "Datos inválidos"}, status=400)

    knowledge = add_knowledge_entry(form.cleaned_data)
    return JsonResponse({"success": True, "id": knowledge.id})


@login_required
@staff_required
def delete_knowledge(request, knowledge_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        delete_knowledge_entry(knowledge_id)
        return JsonResponse({"success": True})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
