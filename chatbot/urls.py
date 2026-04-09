from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_interface, name='chat_interface'),
    path('api/send-message/', views.send_message, name='send_message'),
    path('conversation/<int:conversation_id>/', views.load_conversation, name='load_conversation'),
    path('new/', views.new_conversation, name='new_conversation'),
    path('admin/', views.admin_panel, name='admin_panel'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    # APIs para el dashboard admin
    path('api/admin-data/', views.admin_data, name='admin_data'),
    path('api/logs/', views.chat_logs, name='chat_logs'),
    path('api/update-api-key/', views.update_api_key, name='update_api_key'),
    path('api/test-api/', views.test_api_key, name='test_api_key'),
    path('api/add-knowledge/', views.add_knowledge, name='add_knowledge'),
    path('api/delete-knowledge/<int:knowledge_id>/', views.delete_knowledge, name='delete_knowledge'),
]