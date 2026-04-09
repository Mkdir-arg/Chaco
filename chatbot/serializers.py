from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message, ChatbotKnowledge, ChatbotFeedback


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para User"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer para Message"""
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'role', 'content', 'timestamp', 'tokens_used'
        ]
        read_only_fields = ['id', 'timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer para Conversation"""
    user = UserSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.IntegerField(read_only=True)  # Viene del annotate
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'user', 'title', 'created_at', 'updated_at', 
            'is_active', 'messages', 'message_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatbotKnowledgeSerializer(serializers.ModelSerializer):
    """Serializer para ChatbotKnowledge"""
    
    class Meta:
        model = ChatbotKnowledge
        fields = [
            'id', 'title', 'content', 'category', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatbotFeedbackSerializer(serializers.ModelSerializer):
    """Serializer para ChatbotFeedback"""
    user = UserSerializer(read_only=True)
    message = MessageSerializer(read_only=True)
    rating_display = serializers.CharField(source='get_rating_display', read_only=True)
    
    class Meta:
        model = ChatbotFeedback
        fields = [
            'id', 'message', 'user', 'rating', 'rating_display',
            'comment', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SendMessageSerializer(serializers.Serializer):
    """Serializer para enviar mensajes al chatbot"""
    message = serializers.CharField(max_length=2000)
    conversation_id = serializers.IntegerField(required=False)