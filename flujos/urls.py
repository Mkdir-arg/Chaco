from django.urls import path

from . import views

app_name = 'flujos'

urlpatterns = [
    path('flujos/<int:programa_id>/definicion/', views.api_definicion, name='api_definicion'),
    path('flujos/<int:programa_id>/publicar/', views.api_publicar, name='api_publicar'),
    path('flujos/instancia/<int:instancia_id>/', views.api_instancia, name='api_instancia'),
]
