from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.contrib import messages
import csv
import json

from ..models_auditoria import LogAccion, LogDescargaArchivo, SesionUsuario, AlertaAuditoria
from ..models_auditoria_extendida import (
    AuditoriaCiudadano, AuditoriaLegajo, AuditoriaEvaluacion,
    AuditoriaEventoCritico, AuditoriaConsentimiento, AuditoriaAccesoSensible,
    AuditoriaDerivacion, AuditoriaPlanIntervencion, AuditoriaInstitucion
)


def es_administrador(user):
    """Verificar si el usuario es administrador"""
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Administrador').exists())


@login_required
@user_passes_test(es_administrador)
def dashboard_auditoria(request):
    """Dashboard principal de auditoría"""
    # Estadísticas generales
    hoy = timezone.now().date()
    hace_7_dias = hoy - timedelta(days=7)
    hace_30_dias = hoy - timedelta(days=30)
    
    stats = {
        'acciones_hoy': LogAccion.objects.filter(timestamp__date=hoy).count(),
        'acciones_semana': LogAccion.objects.filter(timestamp__date__gte=hace_7_dias).count(),
        'acciones_mes': LogAccion.objects.filter(timestamp__date__gte=hace_30_dias).count(),
        'descargas_hoy': LogDescargaArchivo.objects.filter(timestamp__date=hoy).count(),
        'sesiones_activas': SesionUsuario.objects.filter(activa=True).count(),
        'alertas_pendientes': AlertaAuditoria.objects.filter(revisada=False).count(),
        # Nuevas estadísticas
        'auditorias_ciudadano': AuditoriaCiudadano.objects.filter(timestamp__date__gte=hace_30_dias).count(),
        'auditorias_legajo': AuditoriaLegajo.objects.filter(timestamp__date__gte=hace_30_dias).count(),
        'eventos_criticos': AuditoriaEventoCritico.objects.filter(timestamp__date__gte=hace_30_dias).count(),
        'accesos_sensibles': AuditoriaAccesoSensible.objects.filter(timestamp__date__gte=hace_30_dias).count(),
        'accesos_fuera_horario': AuditoriaAccesoSensible.objects.filter(
            timestamp__date__gte=hace_30_dias,
            fuera_horario=True
        ).count(),
    }
    
    # Actividad por día (últimos 7 días)
    actividad_diaria = []
    for i in range(7):
        fecha = hoy - timedelta(days=i)
        count = LogAccion.objects.filter(timestamp__date=fecha).count()
        actividad_diaria.append({
            'fecha': fecha.strftime('%d/%m'),
            'count': count
        })
    actividad_diaria.reverse()
    
    # Top usuarios más activos
    usuarios_activos = LogAccion.objects.filter(
        timestamp__date__gte=hace_7_dias,
        usuario__isnull=False
    ).select_related('usuario').values(
        'usuario__username', 'usuario__first_name', 'usuario__last_name'
    ).annotate(
        total_acciones=Count('id')
    ).order_by('-total_acciones')[:10]
    
    # Alertas recientes
    alertas_recientes = AlertaAuditoria.objects.filter(
        revisada=False
    ).order_by('-timestamp')[:5]
    
    context = {
        'stats': stats,
        'actividad_diaria': json.dumps(actividad_diaria),
        'usuarios_activos': usuarios_activos,
        'alertas_recientes': alertas_recientes,
    }
    
    return render(request, 'core/auditoria/dashboard.html', context)


@login_required
@user_passes_test(es_administrador)
def logs_acciones(request):
    """Lista de logs de acciones"""
    logs = LogAccion.objects.select_related('usuario').all()
    
    # Filtros
    usuario_id = request.GET.get('usuario')
    accion = request.GET.get('accion')
    modelo = request.GET.get('modelo')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if usuario_id:
        logs = logs.filter(usuario_id=usuario_id)
    if accion:
        logs = logs.filter(accion=accion)
    if modelo:
        logs = logs.filter(modelo__icontains=modelo)
    if fecha_desde:
        logs = logs.filter(timestamp__date__gte=fecha_desde)
    if fecha_hasta:
        logs = logs.filter(timestamp__date__lte=fecha_hasta)
    
    # Paginación
    paginator = Paginator(logs, 50)
    page = request.GET.get('page')
    logs_page = paginator.get_page(page)
    
    # Datos para filtros (optimizados)
    usuarios = User.objects.filter(logaccion__isnull=False).distinct().only('id', 'username', 'first_name', 'last_name')
    acciones = LogAccion.TipoAccion.choices
    modelos = LogAccion.objects.values_list('modelo', flat=True).distinct()
    
    context = {
        'logs': logs_page,
        'usuarios': usuarios,
        'acciones': acciones,
        'modelos': modelos,
        'filtros': {
            'usuario': usuario_id,
            'accion': accion,
            'modelo': modelo,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    
    return render(request, 'core/auditoria/logs_acciones.html', context)


@login_required
@user_passes_test(es_administrador)
def logs_descargas(request):
    """Lista de logs de descargas"""
    logs = LogDescargaArchivo.objects.select_related('usuario').all()
    
    # Filtros
    usuario_id = request.GET.get('usuario')
    archivo = request.GET.get('archivo')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if usuario_id:
        logs = logs.filter(usuario_id=usuario_id)
    if archivo:
        logs = logs.filter(archivo_nombre__icontains=archivo)
    if fecha_desde:
        logs = logs.filter(timestamp__date__gte=fecha_desde)
    if fecha_hasta:
        logs = logs.filter(timestamp__date__lte=fecha_hasta)
    
    # Paginación
    paginator = Paginator(logs, 50)
    page = request.GET.get('page')
    logs_page = paginator.get_page(page)
    
    context = {
        'logs': logs_page,
        'usuarios': User.objects.filter(logdescargaarchivo__isnull=False).distinct().only('id', 'username', 'first_name', 'last_name'),
        'filtros': {
            'usuario': usuario_id,
            'archivo': archivo,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    
    return render(request, 'core/auditoria/logs_descargas.html', context)


@login_required
@user_passes_test(es_administrador)
def sesiones_usuario(request):
    """Lista de sesiones de usuario"""
    sesiones = SesionUsuario.objects.select_related('usuario').all()
    
    # Filtros
    usuario_id = request.GET.get('usuario')
    activa = request.GET.get('activa')
    fecha_desde = request.GET.get('fecha_desde')
    
    if usuario_id:
        sesiones = sesiones.filter(usuario_id=usuario_id)
    if activa == 'true':
        sesiones = sesiones.filter(activa=True)
    elif activa == 'false':
        sesiones = sesiones.filter(activa=False)
    if fecha_desde:
        sesiones = sesiones.filter(inicio_sesion__date__gte=fecha_desde)
    
    # Paginación
    paginator = Paginator(sesiones, 50)
    page = request.GET.get('page')
    sesiones_page = paginator.get_page(page)
    
    context = {
        'sesiones': sesiones_page,
        'usuarios': User.objects.filter(sesionusuario__isnull=False).distinct().only('id', 'username', 'first_name', 'last_name'),
        'filtros': {
            'usuario': usuario_id,
            'activa': activa,
            'fecha_desde': fecha_desde,
        }
    }
    
    return render(request, 'core/auditoria/sesiones.html', context)


@login_required
@user_passes_test(es_administrador)
def alertas_auditoria(request):
    """Lista de alertas de auditoría"""
    alertas = AlertaAuditoria.objects.select_related(
        'usuario_afectado', 'revisada_por'
    ).all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    severidad = request.GET.get('severidad')
    revisada = request.GET.get('revisada')
    
    if tipo:
        alertas = alertas.filter(tipo=tipo)
    if severidad:
        alertas = alertas.filter(severidad=severidad)
    if revisada == 'true':
        alertas = alertas.filter(revisada=True)
    elif revisada == 'false':
        alertas = alertas.filter(revisada=False)
    
    # Paginación
    paginator = Paginator(alertas, 50)
    page = request.GET.get('page')
    alertas_page = paginator.get_page(page)
    
    context = {
        'alertas': alertas_page,
        'tipos': AlertaAuditoria.TipoAlerta.choices,
        'severidades': AlertaAuditoria.Severidad.choices,
        'filtros': {
            'tipo': tipo,
            'severidad': severidad,
            'revisada': revisada,
        }
    }
    
    return render(request, 'core/auditoria/alertas.html', context)


@login_required
@user_passes_test(es_administrador)
def marcar_alerta_revisada(request, alerta_id):
    """Marcar alerta como revisada"""
    if request.method == 'POST':
        alerta = get_object_or_404(AlertaAuditoria, id=alerta_id)
        alerta.marcar_revisada(request.user)
        messages.success(request, 'Alerta marcada como revisada.')
    
    return JsonResponse({'success': True})


@login_required
@user_passes_test(es_administrador)
def historial_cambios(request):
    """Historial de cambios usando los nuevos modelos de auditoría"""
    
    # Modelos auditados
    modelos_auditados = [
        {'nombre': 'Ciudadano', 'modelo': 'ciudadano'},
        {'nombre': 'Legajo de Atención', 'modelo': 'legajo'},
        {'nombre': 'Evaluación Inicial', 'modelo': 'evaluacion'},
        {'nombre': 'Evento Crítico', 'modelo': 'evento'},
        {'nombre': 'Consentimiento', 'modelo': 'consentimiento'},
        {'nombre': 'Derivación', 'modelo': 'derivacion'},
        {'nombre': 'Plan de Intervención', 'modelo': 'plan'},
        {'nombre': 'Institución', 'modelo': 'institucion'},
    ]
    
    # Filtros
    modelo_seleccionado = request.GET.get('modelo')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    usuario_id = request.GET.get('usuario')
    
    historial = None
    if modelo_seleccionado:
        # Mapear modelo a clase de auditoría
        modelo_map = {
            'ciudadano': AuditoriaCiudadano,
            'legajo': AuditoriaLegajo,
            'evaluacion': AuditoriaEvaluacion,
            'evento': AuditoriaEventoCritico,
            'consentimiento': AuditoriaConsentimiento,
            'derivacion': AuditoriaDerivacion,
            'plan': AuditoriaPlanIntervencion,
            'institucion': AuditoriaInstitucion,
        }
        
        modelo_clase = modelo_map.get(modelo_seleccionado)
        if modelo_clase:
            historial = modelo_clase.objects.select_related('usuario').all()
            
            if fecha_desde:
                historial = historial.filter(timestamp__date__gte=fecha_desde)
            if fecha_hasta:
                historial = historial.filter(timestamp__date__lte=fecha_hasta)
            if usuario_id:
                historial = historial.filter(usuario_id=usuario_id)
            
            # Paginación
            paginator = Paginator(historial, 50)
            page = request.GET.get('page')
            historial = paginator.get_page(page)
    
    context = {
        'modelos_auditados': modelos_auditados,
        'historial': historial,
        'usuarios': User.objects.filter(is_active=True).only('id', 'username', 'first_name', 'last_name'),
        'filtros': {
            'modelo': modelo_seleccionado,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'usuario': usuario_id,
        }
    }
    
    return render(request, 'core/auditoria/historial_cambios.html', context)


@login_required
@user_passes_test(es_administrador)
def exportar_logs(request):
    """Exportar logs a CSV"""
    tipo = request.GET.get('tipo', 'acciones')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="logs_{tipo}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    if tipo == 'acciones':
        writer.writerow(['Usuario', 'Acción', 'Modelo', 'Objeto', 'Fecha', 'IP'])
        logs = LogAccion.objects.select_related('usuario').all()[:1000]
        for log in logs:
            writer.writerow([
                log.usuario.username if log.usuario else 'Anónimo',
                log.get_accion_display(),
                log.modelo,
                log.objeto_repr,
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.ip_address
            ])
    
    elif tipo == 'descargas':
        writer.writerow(['Usuario', 'Archivo', 'Fecha', 'IP'])
        logs = LogDescargaArchivo.objects.select_related('usuario').all()[:1000]
        for log in logs:
            writer.writerow([
                log.usuario.username if log.usuario else 'Anónimo',
                log.archivo_nombre,
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.ip_address
            ])
    
    return response
