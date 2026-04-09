from django.urls import path

from . import views

urlpatterns = [
    path('programas/<int:programa_id>/flujo/editar/', views.editor_flujo, name='editor_flujo'),
]
