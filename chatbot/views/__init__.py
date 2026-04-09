"""Paquete de vistas para la app de chatbot."""

from .admin import (  # noqa: F401
    add_knowledge,
    admin_data,
    admin_panel,
    chat_logs,
    delete_knowledge,
    test_api_key,
    update_api_key,
)
from .public import (  # noqa: F401
    chat_interface,
    load_conversation,
    new_conversation,
    send_message,
    submit_feedback,
)
