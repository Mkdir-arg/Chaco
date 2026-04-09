from django.urls import path
from .views import (
    alertas_auditoria,
    dashboard_auditoria,
    exportar_logs,
    historial_cambios,
    logs_acciones,
    logs_descargas,
    marcar_alerta_revisada,
    sesiones_usuario,
)

app_name = 'auditoria'

urlpatterns = [
    # Dashboard principal
    path('', dashboard_auditoria, name='dashboard'),
    
    # Logs
    path('logs/acciones/', logs_acciones, name='logs_acciones'),
    path('logs/descargas/', logs_descargas, name='logs_descargas'),
    path('logs/exportar/', exportar_logs, name='exportar_logs'),
    
    # Sesiones
    path('sesiones/', sesiones_usuario, name='sesiones'),
    
    # Alertas
    path('alertas/', alertas_auditoria, name='alertas'),
    path('alertas/<int:alerta_id>/revisar/', marcar_alerta_revisada, name='marcar_alerta_revisada'),
    
    # Historial de cambios
    path('historial/', historial_cambios, name='historial_cambios'),
]
