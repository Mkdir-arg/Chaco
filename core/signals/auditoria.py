"""
Signals para Auditoría Automática
Sistema SEDRONAR - Captura automática de cambios en modelos críticos
"""

from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.serializers import serialize
import json
import hashlib
from datetime import datetime, time

# Thread local para almacenar información de la request
import threading
_thread_locals = threading.local()


def get_current_request():
    """Obtiene la request actual del thread local"""
    return getattr(_thread_locals, 'request', None)


def set_current_request(request):
    """Guarda la request en el thread local"""
    _thread_locals.request = request


def get_request_info():
    """Extrae información de la request actual"""
    request = get_current_request()
    if request:
        return {
            'usuario': request.user if request.user.is_authenticated else None,
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'url': request.path,
            'metodo': request.method,
        }
    return {
        'usuario': None,
        'ip_address': None,
        'user_agent': '',
        'url': '',
        'metodo': '',
    }


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def es_fuera_horario():
    """Verifica si es fuera del horario laboral (22:00-06:00)"""
    hora_actual = datetime.now().time()
    return hora_actual >= time(22, 0) or hora_actual < time(6, 0)


def calcular_hash_archivo(archivo):
    """Calcula el hash SHA256 de un archivo"""
    if not archivo:
        return ''
    try:
        archivo.seek(0)
        return hashlib.sha256(archivo.read()).hexdigest()
    except:
        return ''


def modelo_a_dict(instance):
    """Convierte un modelo a diccionario para auditoría"""
    data = {}
    for field in instance._meta.fields:
        field_name = field.name
        field_value = getattr(instance, field_name)
        
        # Convertir valores especiales
        if hasattr(field_value, 'pk'):
            data[field_name] = str(field_value.pk)
        elif isinstance(field_value, datetime):
            data[field_name] = field_value.isoformat()
        else:
            data[field_name] = str(field_value) if field_value is not None else None
    
    return data


def detectar_campos_modificados(instance, datos_anteriores):
    """Detecta qué campos fueron modificados"""
    datos_nuevos = modelo_a_dict(instance)
    campos_modificados = {}
    
    for campo, valor_nuevo in datos_nuevos.items():
        valor_anterior = datos_anteriores.get(campo)
        if valor_anterior != valor_nuevo:
            campos_modificados[campo] = {
                'anterior': valor_anterior,
                'nuevo': valor_nuevo
            }
    
    return campos_modificados


# ============================================================================
# SIGNALS PARA CIUDADANO
# ============================================================================

@receiver(pre_save, sender='legajos.Ciudadano')
def ciudadano_pre_save(sender, instance, **kwargs):
    """Captura el estado anterior del ciudadano antes de guardar"""
    if instance.pk:
        try:
            instance._estado_anterior = modelo_a_dict(
                sender.objects.get(pk=instance.pk)
            )
        except sender.DoesNotExist:
            instance._estado_anterior = None
    else:
        instance._estado_anterior = None


@receiver(post_save, sender='legajos.Ciudadano')
def ciudadano_post_save(sender, instance, created, **kwargs):
    """Audita cambios en ciudadanos"""
    from core.models_auditoria_extendida import AuditoriaCiudadano
    from core.models_auditoria import LogAccion
    
    request_info = get_request_info()
    datos_nuevos = modelo_a_dict(instance)
    accion = 'CREATE' if created else 'UPDATE'
    
    # Crear LogAccion para vista general
    LogAccion.objects.create(
        usuario=request_info['usuario'],
        accion=accion,
        modelo='Ciudadano',
        objeto_id=str(instance.pk),
        objeto_repr=str(instance),
        detalles=datos_nuevos,
        ip_address=request_info['ip_address'],
        user_agent=request_info['user_agent']
    )
    
    if created:
        # Creación
        AuditoriaCiudadano.objects.create(
            ciudadano=instance,
            accion='CREATE',
            usuario=request_info['usuario'],
            datos_nuevos=datos_nuevos,
            ip_address=request_info['ip_address'],
            user_agent=request_info['user_agent'],
            motivo='Creación de nuevo ciudadano'
        )
    else:
        # Actualización
        datos_anteriores = getattr(instance, '_estado_anterior', {})
        campos_modificados = detectar_campos_modificados(instance, datos_anteriores)
        
        if campos_modificados:
            # Detectar si se modificaron datos personales sensibles
            campos_sensibles = {'dni', 'nombre', 'apellido', 'fecha_nacimiento'}
            modifico_datos_personales = bool(campos_sensibles & set(campos_modificados.keys()))
            
            AuditoriaCiudadano.objects.create(
                ciudadano=instance,
                accion='UPDATE',
                usuario=request_info['usuario'],
                campos_modificados=campos_modificados,
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                ip_address=request_info['ip_address'],
                user_agent=request_info['user_agent'],
                modifico_datos_personales=modifico_datos_personales,
                motivo=getattr(instance, '_motivo_cambio', '')
            )


@receiver(post_delete, sender='legajos.Ciudadano')
def ciudadano_post_delete(sender, instance, **kwargs):
    """Audita eliminación de ciudadanos"""
    from core.models_auditoria_extendida import AuditoriaCiudadano
    
    request_info = get_request_info()
    
    # No usar ForeignKey para DELETE, guardar solo el ID
    AuditoriaCiudadano.objects.create(
        ciudadano=None,  # No podemos referenciar un objeto eliminado
        accion='DELETE',
        usuario=request_info['usuario'],
        datos_anteriores=modelo_a_dict(instance),
        ip_address=request_info['ip_address'],
        user_agent=request_info['user_agent'],
        motivo=getattr(instance, '_motivo_eliminacion', f'Eliminación de ciudadano DNI: {instance.dni}')
    )


# ============================================================================
# SIGNALS PARA LEGAJO
# ============================================================================

@receiver(pre_save, sender='legajos.LegajoAtencion')
def legajo_pre_save(sender, instance, **kwargs):
    """Captura el estado anterior del legajo"""
    if instance.pk:
        try:
            anterior = sender.objects.get(pk=instance.pk)
            instance._estado_anterior = modelo_a_dict(anterior)
            instance._responsable_anterior = anterior.responsable
            instance._estado_anterior_valor = anterior.estado
            instance._nivel_riesgo_anterior = anterior.nivel_riesgo
        except sender.DoesNotExist:
            instance._estado_anterior = None


@receiver(post_save, sender='legajos.LegajoAtencion')
def legajo_post_save(sender, instance, created, **kwargs):
    """Audita cambios en legajos"""
    from core.models_auditoria_extendida import AuditoriaLegajo
    from core.models_auditoria import AlertaAuditoria, LogAccion
    
    request_info = get_request_info()
    datos_nuevos = modelo_a_dict(instance)
    
    # Crear LogAccion
    LogAccion.objects.create(
        usuario=request_info['usuario'],
        accion='CREATE' if created else 'UPDATE',
        modelo='LegajoAtencion',
        objeto_id=str(instance.pk),
        objeto_repr=f'Legajo {instance.codigo}',
        detalles=datos_nuevos,
        ip_address=request_info['ip_address'],
        user_agent=request_info['user_agent']
    )
    
    if created:
        AuditoriaLegajo.objects.create(
            legajo=instance,
            accion='CREATE',
            usuario=request_info['usuario'],
            datos_completos_nuevos=datos_nuevos,
            ip_address=request_info['ip_address'],
            motivo='Creación de nuevo legajo'
        )
    else:
        datos_anteriores = getattr(instance, '_estado_anterior', {})
        
        # Detectar cambios importantes
        cambio_estado = (
            hasattr(instance, '_estado_anterior_valor') and
            instance._estado_anterior_valor != instance.estado
        )
        cambio_responsable = (
            hasattr(instance, '_responsable_anterior') and
            instance._responsable_anterior != instance.responsable
        )
        cambio_nivel_riesgo = (
            hasattr(instance, '_nivel_riesgo_anterior') and
            instance._nivel_riesgo_anterior != instance.nivel_riesgo
        )
        
        if datos_anteriores:
            AuditoriaLegajo.objects.create(
                legajo=instance,
                accion='UPDATE',
                usuario=request_info['usuario'],
                datos_completos_anteriores=datos_anteriores,
                datos_completos_nuevos=datos_nuevos,
                ip_address=request_info['ip_address'],
                cambio_estado=cambio_estado,
                cambio_responsable=cambio_responsable,
                cambio_nivel_riesgo=cambio_nivel_riesgo,
                motivo=getattr(instance, '_motivo_cambio', '')
            )
            
            # Generar alertas para cambios críticos
            if cambio_responsable and request_info['usuario']:
                AlertaAuditoria.objects.create(
                    tipo='CAMBIOS_CRITICOS',
                    severidad='MEDIA',
                    usuario_afectado=instance.responsable,
                    descripcion=f'Cambio de responsable en legajo {instance.codigo}',
                    detalles={
                        'legajo': str(instance.pk),
                        'responsable_anterior': str(instance._responsable_anterior),
                        'responsable_nuevo': str(instance.responsable),
                    }
                )


# ============================================================================
# SIGNALS PARA EVALUACION INICIAL
# ============================================================================

@receiver(pre_save, sender='legajos.EvaluacionInicial')
def evaluacion_pre_save(sender, instance, **kwargs):
    """Captura el estado anterior de la evaluación"""
    if instance.pk:
        try:
            anterior = sender.objects.get(pk=instance.pk)
            instance._estado_anterior = modelo_a_dict(anterior)
            instance._riesgo_suicida_anterior = anterior.riesgo_suicida
            instance._violencia_anterior = anterior.violencia
        except sender.DoesNotExist:
            instance._estado_anterior = None


@receiver(post_save, sender='legajos.EvaluacionInicial')
def evaluacion_post_save(sender, instance, created, **kwargs):
    """Audita cambios en evaluaciones - GENERA ALERTAS AUTOMÁTICAS"""
    from core.models_auditoria_extendida import AuditoriaEvaluacion
    from core.models_auditoria import AlertaAuditoria
    
    request_info = get_request_info()
    datos_nuevos = modelo_a_dict(instance)
    
    if created:
        AuditoriaEvaluacion.objects.create(
            evaluacion=instance,
            accion='CREATE',
            usuario=request_info['usuario'],
            datos_nuevos=datos_nuevos,
            ip_address=request_info['ip_address'],
            riesgo_suicida_nuevo=instance.riesgo_suicida,
            violencia_nuevo=instance.violencia
        )
        
        # Alertas para evaluación inicial con riesgos
        if instance.riesgo_suicida or instance.violencia:
            AlertaAuditoria.objects.create(
                tipo='CAMBIOS_CRITICOS',
                severidad='CRITICA',
                usuario_afectado=instance.legajo.responsable,
                descripcion=f'Evaluación inicial con riesgos detectados - Legajo {instance.legajo.codigo}',
                detalles={
                    'legajo': str(instance.legajo.pk),
                    'riesgo_suicida': instance.riesgo_suicida,
                    'violencia': instance.violencia,
                }
            )
    else:
        datos_anteriores = getattr(instance, '_estado_anterior', {})
        campos_modificados = detectar_campos_modificados(instance, datos_anteriores)
        
        # Detectar cambios en campos críticos
        cambio_riesgo_suicida = (
            hasattr(instance, '_riesgo_suicida_anterior') and
            instance._riesgo_suicida_anterior != instance.riesgo_suicida
        )
        cambio_violencia = (
            hasattr(instance, '_violencia_anterior') and
            instance._violencia_anterior != instance.violencia
        )
        
        genera_alerta = cambio_riesgo_suicida or cambio_violencia
        
        if campos_modificados:
            AuditoriaEvaluacion.objects.create(
                evaluacion=instance,
                accion='UPDATE',
                usuario=request_info['usuario'],
                campos_modificados=campos_modificados,
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                ip_address=request_info['ip_address'],
                genera_alerta=genera_alerta,
                cambio_riesgo_suicida=cambio_riesgo_suicida,
                cambio_violencia=cambio_violencia,
                riesgo_suicida_anterior=getattr(instance, '_riesgo_suicida_anterior', None),
                riesgo_suicida_nuevo=instance.riesgo_suicida,
                violencia_anterior=getattr(instance, '_violencia_anterior', None),
                violencia_nuevo=instance.violencia
            )
            
            # Generar alertas críticas
            if genera_alerta:
                severidad = 'CRITICA' if (instance.riesgo_suicida or instance.violencia) else 'ALTA'
                AlertaAuditoria.objects.create(
                    tipo='CAMBIOS_CRITICOS',
                    severidad=severidad,
                    usuario_afectado=instance.legajo.responsable,
                    descripcion=f'Cambio en evaluación de riesgos - Legajo {instance.legajo.codigo}',
                    detalles={
                        'legajo': str(instance.legajo.pk),
                        'cambio_riesgo_suicida': cambio_riesgo_suicida,
                        'cambio_violencia': cambio_violencia,
                        'riesgo_suicida_actual': instance.riesgo_suicida,
                        'violencia_actual': instance.violencia,
                    }
                )


# ============================================================================
# SIGNALS PARA EVENTO CRÍTICO
# ============================================================================

@receiver(post_save, sender='legajos.EventoCritico')
def evento_critico_post_save(sender, instance, created, **kwargs):
    """Audita eventos críticos - SIEMPRE GENERA ALERTA"""
    from core.models_auditoria_extendida import AuditoriaEventoCritico
    from core.models_auditoria import AlertaAuditoria
    
    request_info = get_request_info()
    datos_nuevos = modelo_a_dict(instance)
    
    if created:
        AuditoriaEventoCritico.objects.create(
            evento=instance,
            accion='CREATE',
            usuario=request_info['usuario'],
            datos_nuevos=datos_nuevos,
            ip_address=request_info['ip_address'],
            tipo_evento=instance.tipo
        )
        
        # SIEMPRE generar alerta para eventos críticos nuevos
        AlertaAuditoria.objects.create(
            tipo='CAMBIOS_CRITICOS',
            severidad='CRITICA',
            usuario_afectado=instance.legajo.responsable,
            descripcion=f'Nuevo evento crítico: {instance.get_tipo_display()} - Legajo {instance.legajo.codigo}',
            detalles={
                'legajo': str(instance.legajo.pk),
                'tipo_evento': instance.tipo,
                'detalle': instance.detalle,
            }
        )


# ============================================================================
# SIGNALS PARA CONSENTIMIENTO
# ============================================================================

@receiver(pre_save, sender='legajos.Consentimiento')
def consentimiento_pre_save(sender, instance, **kwargs):
    """Captura el estado anterior del consentimiento"""
    if instance.pk:
        try:
            instance._estado_anterior = modelo_a_dict(
                sender.objects.get(pk=instance.pk)
            )
        except sender.DoesNotExist:
            instance._estado_anterior = None


@receiver(post_save, sender='legajos.Consentimiento')
def consentimiento_post_save(sender, instance, created, **kwargs):
    """Audita consentimientos - REQUISITO LEGAL"""
    from core.models_auditoria_extendida import AuditoriaConsentimiento
    
    request_info = get_request_info()
    datos_completos = modelo_a_dict(instance)
    
    # Calcular hash del archivo
    archivo_hash = ''
    archivo_nombre = ''
    if instance.archivo:
        archivo_hash = calcular_hash_archivo(instance.archivo)
        archivo_nombre = instance.archivo.name
    
    accion = 'CREATE' if created else 'UPDATE'
    
    AuditoriaConsentimiento.objects.create(
        consentimiento=instance,
        accion=accion,
        usuario=request_info['usuario'],
        datos_completos=datos_completos,
        ip_address=request_info['ip_address'],
        archivo_hash=archivo_hash,
        archivo_nombre=archivo_nombre,
        motivo=getattr(instance, '_motivo_cambio', f'{accion} de consentimiento')
    )


@receiver(pre_delete, sender='legajos.Consentimiento')
def consentimiento_pre_delete(sender, instance, **kwargs):
    """Audita eliminación de consentimientos - CRÍTICO"""
    from core.models_auditoria_extendida import AuditoriaConsentimiento
    from core.models_auditoria import AlertaAuditoria
    
    request_info = get_request_info()
    
    # OBLIGATORIO: Debe tener motivo de eliminación
    motivo = getattr(instance, '_motivo_eliminacion', '')
    if not motivo:
        raise ValueError('Debe proporcionar un motivo para eliminar un consentimiento')
    
    # Calcular hash del archivo antes de eliminar
    archivo_hash = ''
    if instance.archivo:
        archivo_hash = calcular_hash_archivo(instance.archivo)
    
    AuditoriaConsentimiento.objects.create(
        consentimiento_id=instance.pk,
        accion='DELETE',
        usuario=request_info['usuario'],
        datos_completos=modelo_a_dict(instance),
        ip_address=request_info['ip_address'],
        archivo_hash=archivo_hash,
        archivo_nombre=instance.archivo.name if instance.archivo else '',
        motivo=motivo
    )
    
    # Generar alerta crítica
    AlertaAuditoria.objects.create(
        tipo='CAMBIOS_CRITICOS',
        severidad='CRITICA',
        usuario_afectado=request_info['usuario'] or User.objects.first(),
        descripcion=f'Eliminación de consentimiento - Ciudadano {instance.ciudadano}',
        detalles={
            'ciudadano': str(instance.ciudadano.pk),
            'motivo': motivo,
        }
    )


# ============================================================================
# SIGNALS PARA DERIVACIÓN
# ============================================================================

@receiver(pre_save, sender='legajos.Derivacion')
def derivacion_pre_save(sender, instance, **kwargs):
    """Captura el estado anterior de la derivación"""
    if instance.pk:
        try:
            anterior = sender.objects.get(pk=instance.pk)
            instance._estado_anterior = modelo_a_dict(anterior)
            instance._estado_anterior_valor = anterior.estado
            instance._urgencia_anterior = anterior.urgencia
        except sender.DoesNotExist:
            instance._estado_anterior = None


@receiver(post_save, sender='legajos.Derivacion')
def derivacion_post_save(sender, instance, created, **kwargs):
    """Audita derivaciones"""
    from core.models_auditoria_extendida import AuditoriaDerivacion
    
    request_info = get_request_info()
    datos_completos = modelo_a_dict(instance)
    
    cambio_estado = (
        hasattr(instance, '_estado_anterior_valor') and
        instance._estado_anterior_valor != instance.estado
    )
    cambio_urgencia = (
        hasattr(instance, '_urgencia_anterior') and
        instance._urgencia_anterior != instance.urgencia
    )
    
    AuditoriaDerivacion.objects.create(
        derivacion=instance,
        accion='CREATE' if created else 'UPDATE',
        usuario=request_info['usuario'],
        estado_anterior=getattr(instance, '_estado_anterior_valor', ''),
        estado_nuevo=instance.estado,
        datos_completos=datos_completos,
        ip_address=request_info['ip_address'],
        institucion_origen=instance.legajo.dispositivo,
        institucion_destino=instance.destino,
        cambio_estado=cambio_estado,
        cambio_urgencia=cambio_urgencia
    )


# ============================================================================
# SIGNALS PARA PLAN DE INTERVENCIÓN
# ============================================================================

@receiver(pre_save, sender='legajos.PlanIntervencion')
def plan_pre_save(sender, instance, **kwargs):
    """Captura el estado anterior del plan"""
    if instance.pk:
        try:
            anterior = sender.objects.get(pk=instance.pk)
            instance._estado_anterior = modelo_a_dict(anterior)
            instance._vigente_anterior = anterior.vigente
        except sender.DoesNotExist:
            instance._estado_anterior = None


@receiver(post_save, sender='legajos.PlanIntervencion')
def plan_post_save(sender, instance, created, **kwargs):
    """Audita planes de intervención"""
    from core.models_auditoria_extendida import AuditoriaPlanIntervencion
    
    request_info = get_request_info()
    datos_nuevos = modelo_a_dict(instance)
    
    cambio_vigencia = (
        hasattr(instance, '_vigente_anterior') and
        instance._vigente_anterior != instance.vigente
    )
    
    if created:
        AuditoriaPlanIntervencion.objects.create(
            plan=instance,
            accion='CREATE',
            usuario=request_info['usuario'],
            datos_nuevos=datos_nuevos,
            ip_address=request_info['ip_address'],
            vigente_nuevo=instance.vigente
        )
    else:
        datos_anteriores = getattr(instance, '_estado_anterior', {})
        campos_modificados = detectar_campos_modificados(instance, datos_anteriores)
        
        if campos_modificados:
            AuditoriaPlanIntervencion.objects.create(
                plan=instance,
                accion='UPDATE',
                usuario=request_info['usuario'],
                campos_modificados=campos_modificados,
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                ip_address=request_info['ip_address'],
                cambio_vigencia=cambio_vigencia,
                vigente_anterior=getattr(instance, '_vigente_anterior', None),
                vigente_nuevo=instance.vigente
            )


# ============================================================================
# SIGNALS PARA INSTITUCIÓN
# ============================================================================

@receiver(pre_save, sender='core.Institucion')
def institucion_pre_save(sender, instance, **kwargs):
    """Captura el estado anterior de la institución"""
    if instance.pk:
        try:
            anterior = sender.objects.get(pk=instance.pk)
            instance._estado_anterior = modelo_a_dict(anterior)
            instance._estado_registro_anterior = anterior.estado_registro
            instance._activo_anterior = anterior.activo
        except sender.DoesNotExist:
            instance._estado_anterior = None


@receiver(post_save, sender='core.Institucion')
def institucion_post_save(sender, instance, created, **kwargs):
    """Audita instituciones"""
    from core.models_auditoria_extendida import AuditoriaInstitucion
    
    request_info = get_request_info()
    datos_nuevos = modelo_a_dict(instance)
    
    if created:
        AuditoriaInstitucion.objects.create(
            institucion=instance,
            accion='CREATE',
            usuario=request_info['usuario'],
            datos_nuevos=datos_nuevos,
            ip_address=request_info['ip_address']
        )
    else:
        datos_anteriores = getattr(instance, '_estado_anterior', {})
        campos_modificados = detectar_campos_modificados(instance, datos_anteriores)
        
        cambio_estado_registro = (
            hasattr(instance, '_estado_registro_anterior') and
            instance._estado_registro_anterior != instance.estado_registro
        )
        cambio_activo = (
            hasattr(instance, '_activo_anterior') and
            instance._activo_anterior != instance.activo
        )
        
        if campos_modificados:
            AuditoriaInstitucion.objects.create(
                institucion=instance,
                accion='UPDATE',
                usuario=request_info['usuario'],
                campos_modificados=campos_modificados,
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                ip_address=request_info['ip_address'],
                cambio_estado_registro=cambio_estado_registro,
                estado_registro_anterior=getattr(instance, '_estado_registro_anterior', ''),
                estado_registro_nuevo=instance.estado_registro,
                cambio_activo=cambio_activo
            )
