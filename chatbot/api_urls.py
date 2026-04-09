from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ConversationViewSet, MessageViewSet, ChatbotKnowledgeViewSet, ChatbotFeedbackViewSet
)

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'knowledge', ChatbotKnowledgeViewSet)
router.register(r'feedback', ChatbotFeedbackViewSet, basename='feedback')

urlpatterns = [
    path('', include(router.urls)),
]