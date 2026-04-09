from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from ..models_contactos import (
    HistorialContacto, VinculoFamiliar, ProfesionalTratante,
    DispositivoVinculado, ContactoEmergencia
)
from ..models import LegajoAtencion


@login_required
def dashboard_contactos(request):
    """Dashboard principal del sistema de contactos"""
    return render(request, 'legajos/dashboard_contactos.html')


@login_required
def metricas_contactos_api(request):
    """API para métricas del dashboard"""
    # Fechas para filtros
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    hace_7_dias = hoy - timedelta(days=7)
    
    # Métricas generales
    total_contactos = HistorialContacto.objects.count()
    contactos_mes = HistorialContacto.objects.filter(
        fecha_contacto__date__gte=hace_30_dias
    ).count()
    contactos_semana = HistorialContacto.objects.filter(
        fecha_contacto__date__gte=hace_7_dias
    ).count()
    
    # Contactos por tipo
    contactos_por_tipo = dict(
        HistorialContacto.objects.values('tipo_contacto')
        .annotate(total=Count('id'))
        .values_list('tipo_contacto', 'total')
    )
    
    # Contactos por estado
    contactos_por_estado = dict(
        HistorialContacto.objects.values('estado')
        .annotate(total=Count('id'))
        .values_list('estado', 'total')
    )
    
    # Profesionales más activos
    profesionales_activos = list(
        HistorialContacto.objects.filter(fecha_contacto__date__gte=hace_30_dias)
        .select_related('profesional')
        .values('profesional__first_name', 'profesional__last_name')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    
    # Vínculos familiares
    total_vinculos = VinculoFamiliar.objects.filter(activo=True).count()
    contactos_emergencia = VinculoFamiliar.objects.filter(
        es_contacto_emergencia=True, activo=True
    ).count()
    
    # Dispositivos más vinculados
    dispositivos_activos = list(
        DispositivoVinculado.objects.filter(estado='ACTIVO')
        .values('dispositivo__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    
    # Tendencia semanal (últimos 7 días)
    tendencia_semanal = []
    for i in range(7):
        fecha = hoy - timedelta(days=i)
        contactos_dia = HistorialContacto.objects.filter(
            fecha_contacto__date=fecha
        ).count()
        tendencia_semanal.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'contactos': contactos_dia
        })
    
    return JsonResponse({
        'metricas_generales': {
            'total_contactos': total_contactos,
            'contactos_mes': contactos_mes,
            'contactos_semana': contactos_semana,
            'total_vinculos': total_vinculos,
            'contactos_emergencia': contactos_emergencia
        },
        'contactos_por_tipo': contactos_por_tipo,
        'contactos_por_estado': contactos_por_estado,
        'profesionales_activos': profesionales_activos,
        'dispositivos_activos': dispositivos_activos,
        'tendencia_semanal': list(reversed(tendencia_semanal))
    })


@login_required
def metricas_red_contactos_api(request):
    """API para métricas de red de contactos"""
    # Distribución de vínculos por tipo
    vinculos_por_tipo = dict(
        VinculoFamiliar.objects.filter(activo=True)
        .values('tipo_vinculo')
        .annotate(total=Count('id'))
        .values_list('tipo_vinculo', 'total')
    )
    
    # Profesionales por rol
    profesionales_por_rol = dict(
        ProfesionalTratante.objects.filter(activo=True)
        .values('rol')
        .annotate(total=Count('id'))
        .values_list('rol', 'total')
    )
    
    # Ciudadanos con más vínculos
    ciudadanos_conectados = list(
        VinculoFamiliar.objects.filter(activo=True)
        .select_related('ciudadano_principal')
        .values('ciudadano_principal__nombre', 'ciudadano_principal__apellido')
        .annotate(total_vinculos=Count('id'))
        .order_by('-total_vinculos')[:10]
    )
    
    return JsonResponse({
        'vinculos_por_tipo': vinculos_por_tipo,
        'profesionales_por_rol': profesionales_por_rol,
        'ciudadanos_conectados': ciudadanos_conectados
    })


@login_required
def exportar_reporte_contactos(request):
    """Exportar reporte de contactos en CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_contactos.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Fecha', 'Tipo', 'Estado', 'Ciudadano', 'Profesional', 
        'Duración', 'Motivo'
    ])
    
    contactos = HistorialContacto.objects.select_related(
        'legajo__ciudadano', 'legajo__dispositivo', 'profesional'
    ).order_by('-fecha_contacto')
    
    for contacto in contactos:
        writer.writerow([
            contacto.fecha_contacto.strftime('%Y-%m-%d %H:%M'),
            contacto.get_tipo_contacto_display(),
            contacto.get_estado_display(),
            str(contacto.legajo.ciudadano),
            contacto.profesional.get_full_name(),
            contacto.duracion_formateada,
            contacto.motivo
        ])
    
    return response
