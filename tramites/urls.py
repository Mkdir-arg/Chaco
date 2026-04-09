from django.urls import path
from .views import aprobar_tramite, detalle_tramite, lista_tramites, rechazar_tramite

app_name = 'tramites'

urlpatterns = [
    path('', lista_tramites, name='lista_tramites'),
    path('<int:tramite_id>/', detalle_tramite, name='detalle_tramite'),
    path('<int:tramite_id>/aprobar/', aprobar_tramite, name='aprobar_tramite'),
    path('<int:tramite_id>/rechazar/', rechazar_tramite, name='rechazar_tramite'),
]
