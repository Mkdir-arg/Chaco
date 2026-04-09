from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from chatbot.forms_chatbot import ApiKeyForm, SendMessageForm
from chatbot.models import Conversation, Message
from chatbot.services_chatbot import (
    get_or_create_bubble_conversation,
    send_message_to_chatbot,
    validate_api_key_format,
)


class ChatbotFormsTests(TestCase):
    def test_send_message_form_normaliza_espacios(self):
        form = SendMessageForm({'message': '  hola chatbot  '})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['message'], 'hola chatbot')

    def test_api_key_form_trim(self):
        form = ApiKeyForm({'api_key': '  sk-test  '})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['api_key'], 'sk-test')


class ChatbotServicesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='chatbot-user', password='secret')

    def test_get_or_create_bubble_conversation_reutiliza_sesion(self):
        conversation = Conversation.objects.create(user=self.user, title='Chat previo', is_active=True)
        session = {'chatbot_bubble_conversation_id': conversation.id}

        reused = get_or_create_bubble_conversation(session, self.user, 'hola')

        self.assertEqual(reused.id, conversation.id)

    @patch('chatbot.services_chatbot.EnhancedChatbotService.generate_response')
    def test_send_message_to_chatbot_persiste_historial(self, mock_generate_response):
        mock_generate_response.return_value = {'content': 'respuesta', 'tokens_used': 12}
        session = {}

        response = send_message_to_chatbot(session, self.user, 'hola')

        self.assertEqual(response['content'], 'respuesta')
        conversation = Conversation.objects.get(id=session['chatbot_bubble_conversation_id'])
        self.assertEqual(Message.objects.filter(conversation=conversation).count(), 2)

    def test_validate_api_key_format(self):
        self.assertTrue(validate_api_key_format('sk-test'))
        self.assertFalse(validate_api_key_format('test'))


class ChatbotViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='chatbot-view-user', password='secret')
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.user)

    @patch('chatbot.services_chatbot.EnhancedChatbotService.generate_response')
    def test_send_message_returns_frontend_contract(self, mock_generate_response):
        mock_generate_response.return_value = {'content': 'respuesta', 'tokens_used': 7}
        self.client.get(reverse('chatbot:chat_interface'))
        csrftoken = self.client.cookies['csrftoken'].value

        response = self.client.post(
            reverse('chatbot:send_message'),
            data='{"message":"hola"}',
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrftoken,
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertIn('conversation_id', payload)
        self.assertEqual(payload['user_message']['content'], 'hola')
        self.assertEqual(payload['assistant_message']['content'], 'respuesta')

    @patch('chatbot.services_chatbot.EnhancedChatbotService.generate_response')
    def test_send_message_rechaza_post_sin_csrf(self, mock_generate_response):
        mock_generate_response.return_value = {'content': 'respuesta', 'tokens_used': 7}

        response = self.client.post(
            reverse('chatbot:send_message'),
            data='{"message":"hola"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)
