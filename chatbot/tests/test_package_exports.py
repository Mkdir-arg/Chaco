from django.test import SimpleTestCase


class ChatbotPackageExportsTests(SimpleTestCase):
    def test_views_package_exports_public_symbols(self):
        from chatbot.views import admin_panel, chat_interface, send_message

        self.assertTrue(callable(admin_panel))
        self.assertTrue(callable(chat_interface))
        self.assertTrue(callable(send_message))

    def test_forms_services_and_selectors_packages_export_public_symbols(self):
        from chatbot.api_views import ChatbotKnowledgeViewSet, ConversationViewSet
        from chatbot.forms import ApiKeyForm, SendMessageForm
        from chatbot.selectors import build_admin_dashboard_payload, get_user_conversations
        from chatbot.services import send_message_to_chatbot, validate_api_key_format

        self.assertIsNotNone(ConversationViewSet)
        self.assertIsNotNone(ChatbotKnowledgeViewSet)
        self.assertIsNotNone(SendMessageForm)
        self.assertIsNotNone(ApiKeyForm)
        self.assertTrue(callable(send_message_to_chatbot))
        self.assertTrue(callable(validate_api_key_format))
        self.assertTrue(callable(build_admin_dashboard_payload))
        self.assertTrue(callable(get_user_conversations))
