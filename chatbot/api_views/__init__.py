from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Count
from ..models import Conversation, Message, ChatbotKnowledge, ChatbotFeedback
from ..serializers import (
    ConversationSerializer, MessageSerializer, ChatbotKnowledgeSerializer,
    ChatbotFeedbackSerializer, SendMessageSerializer
)


@extend_schema_view(
    list=extend_schema(description="Lista todas las conversaciones del usuario"),
    create=extend_schema(description="Crea una nueva conversación"),
    retrieve=extend_schema(description="Obtiene una conversación específica"),
    update=extend_schema(description="Actualiza una conversación"),
    partial_update=extend_schema(description="Actualiza parcialmente una conversación"),
    destroy=extend_schema(description="Elimina una conversación")
)
class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar conversaciones del chatbot.
    
    Permite realizar operaciones CRUD sobre las conversaciones del usuario.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    ordering = ['-updated_at']

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).select_related('user').prefetch_related('messages').annotate(
            message_count=Count('messages')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(description="Obtiene los mensajes de una conversación")
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Obtiene los mensajes de una conversación específica"""
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Envía un mensaje al chatbot",
        request=SendMessageSerializer
    )
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Envía un mensaje al chatbot en esta conversación"""
        conversation = self.get_object()
        serializer = SendMessageSerializer(data=request.data)
        
        if serializer.is_valid():
            message_content = serializer.validated_data['message']
            
            # Crear mensaje del usuario
            user_message = Message.objects.create(
                conversation=conversation,
                role='user',
                content=message_content
            )
            
            # Aquí iría la lógica del chatbot para generar respuesta
            # Por ahora retornamos una respuesta simple
            bot_response = "Esta es una respuesta automática del chatbot."
            
            bot_message = Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=bot_response
            )
            
            # Actualizar timestamp de la conversación
            conversation.save()
            
            return Response({
                'user_message': MessageSerializer(user_message).data,
                'bot_message': MessageSerializer(bot_message).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(description="Lista todos los mensajes"),
    retrieve=extend_schema(description="Obtiene un mensaje específico")
)
class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para mensajes.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'conversation']
    ordering = ['timestamp']

    def get_queryset(self):
        return Message.objects.filter(conversation__user=self.request.user)


@extend_schema_view(
    list=extend_schema(description="Lista toda la base de conocimiento"),
    create=extend_schema(description="Crea un nuevo elemento de conocimiento"),
    retrieve=extend_schema(description="Obtiene un elemento específico"),
    update=extend_schema(description="Actualiza un elemento de conocimiento"),
    partial_update=extend_schema(description="Actualiza parcialmente un elemento"),
    destroy=extend_schema(description="Elimina un elemento de conocimiento")
)
class ChatbotKnowledgeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar la base de conocimiento del chatbot.
    """
    queryset = ChatbotKnowledge.objects.all()
    serializer_class = ChatbotKnowledgeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']
    search_fields = ['title', 'content']
    ordering = ['-updated_at']


@extend_schema_view(
    list=extend_schema(description="Lista todos los feedbacks"),
    create=extend_schema(description="Crea un nuevo feedback"),
    retrieve=extend_schema(description="Obtiene un feedback específico"),
    update=extend_schema(description="Actualiza un feedback"),
    partial_update=extend_schema(description="Actualiza parcialmente un feedback"),
    destroy=extend_schema(description="Elimina un feedback")
)
class ChatbotFeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar feedback del chatbot.
    """
    serializer_class = ChatbotFeedbackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['rating']
    ordering = ['-created_at']

    def get_queryset(self):
        return ChatbotFeedback.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
