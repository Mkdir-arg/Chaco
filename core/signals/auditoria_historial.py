"""
Signals adicionales para auditar tablas de historial y alertas
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .auditoria import get_request_info, modelo_a_dict


# ============================================================================
# SIGNALS PARA HISTORIAL DE DERIVACIONES
# ============================================================================

@receiver(post_save, sender='legajos.HistorialDerivacion')
def historial_derivacion_post_save(sender, instance, created, **kwargs):
    """Audita cambios en historial de derivaciones"""
    from core.models_auditoria import LogAccion
    
    request_info = get_request_info()
    
    LogAccion.objects.create(
        usuario=request_info['usuario'],
        accion='CREATE' if created else 'UPDATE',
        modelo='HistorialDerivacion',
        objeto_id=str(instance.pk),
        objeto_repr=str(instance),
        detalles=modelo_a_dict(instance),
        ip_address=request_info['ip_address'],
        user_agent=request_info['user_agent']
    )


# ============================================================================
# SIGNALS PARA HISTORIAL DE ASIGNACIONES
# ============================================================================

@receiver(post_save, sender='conversaciones.HistorialAsignacion')
def historial_asignacion_post_save(sender, instance, created, **kwargs):
    """Audita cambios en historial de asignaciones"""
    from core.models_auditoria import LogAccion
    
    request_info = get_request_info()
    
    LogAccion.objects.create(
        usuario=request_info['usuario'],
        accion='CREATE' if created else 'UPDATE',
        modelo='HistorialAsignacion',
        objeto_id=str(instance.pk),
        objeto_repr=str(instance),
        detalles=modelo_a_dict(instance),
        ip_address=request_info['ip_address'],
        user_agent=request_info['user_agent']
    )


# ============================================================================
# SIGNALS PARA ALERTAS DE CIUDADANOS
# ============================================================================

@receiver(post_save, sender='legajos.AlertaCiudadano')
def alerta_ciudadano_post_save(sender, instance, created, **kwargs):
    """Audita alertas de ciudadanos"""
    from core.models_auditoria import LogAccion
    
    request_info = get_request_info()
    
    LogAccion.objects.create(
        usuario=request_info['usuario'],
        accion='CREATE' if created else 'UPDATE',
        modelo='AlertaCiudadano',
        objeto_id=str(instance.pk),
        objeto_repr=f"Alerta {instance.tipo} - {instance.ciudadano}",
        detalles=modelo_a_dict(instance),
        ip_address=request_info['ip_address'],
        user_agent=request_info['user_agent']
    )


# ============================================================================
# SIGNALS PARA ALERTAS DE EVENTOS CRÍTICOS
# ============================================================================

@receiver(post_save, sender='legajos.AlertaEventoCritico')
def alerta_evento_post_save(sender, instance, created, **kwargs):
    """Audita alertas de eventos críticos"""
    from core.models_auditoria import LogAccion
    
    request_info = get_request_info()
    
    LogAccion.objects.create(
        usuario=request_info['usuario'],
        accion='CREATE' if created else 'UPDATE',
        modelo='AlertaEventoCritico',
        objeto_id=str(instance.pk),
        objeto_repr=str(instance),
        detalles=modelo_a_dict(instance),
        ip_address=request_info['ip_address'],
        user_agent=request_info['user_agent']
    )


# ============================================================================
# SIGNALS PARA ALERTAS DE CONVERSACIONES
# ============================================================================

@receiver(post_save, sender='conversaciones.HistorialAlertaConversacion')
def alerta_conversacion_post_save(sender, instance, created, **kwargs):
    """Audita alertas de conversaciones"""
    from core.models_auditoria import LogAccion
    
    request_info = get_request_info()
    
    LogAccion.objects.create(
        usuario=request_info['usuario'],
        accion='CREATE' if created else 'UPDATE',
        modelo='HistorialAlertaConversacion',
        objeto_id=str(instance.pk),
        objeto_repr=str(instance),
        detalles=modelo_a_dict(instance),
        ip_address=request_info['ip_address'],
        user_agent=request_info['user_agent']
    )


# ============================================================================
# SIGNALS PARA HISTORIAL DE CONTACTOS
# ============================================================================

@receiver(post_save, sender='legajos.HistorialContacto')
def historial_contacto_post_save(sender, instance, created, **kwargs):
    """Audita historial de contactos"""
    from core.models_auditoria import LogAccion
    
    request_info = get_request_info()
    
    LogAccion.objects.create(
        usuario=request_info['usuario'],
        accion='CREATE' if created else 'UPDATE',
        modelo='HistorialContacto',
        objeto_id=str(instance.pk),
        objeto_repr=str(instance),
        detalles=modelo_a_dict(instance),
        ip_address=request_info['ip_address'],
        user_agent=request_info['user_agent']
    )
