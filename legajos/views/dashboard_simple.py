import csv
from datetime import timedelta

from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from core.decorators import group_required
from ..models import LegajoAtencion

@login_required
def dashboard_contactos_simple(request):
    """Dashboard simple para probar"""
    return render(request, 'legajos/dashboard_simple.html', {
        'titulo': 'Dashboard de Contactos - Funcionando!'
    })

@login_required  
def test_api(request):
    """API de prueba"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Las APIs funcionan correctamente'
    })


@login_required
@group_required(['Ciudadanos'])
def reportes_view(request):
    """Vista liviana de reportes para mantener operativa la navegación del backoffice."""
    hace_7_dias = timezone.now().date() - timedelta(days=7)

    legajos = LegajoAtencion.objects.select_related('dispositivo')
    stats = {
        'total_legajos': legajos.count(),
        'legajos_activos': legajos.exclude(estado='CERRADO').count(),
        'riesgo_alto': legajos.filter(nivel_riesgo='ALTO').count(),
        'nuevos_semana': legajos.filter(fecha_admision__gte=hace_7_dias).count(),
        'por_estado': [
            {'codigo': item['estado'], 'label': item['estado'].replace('_', ' ').title(), 'total': item['total']}
            for item in legajos.values('estado').order_by('estado').annotate(total=models.Count('id'))
        ],
        'por_riesgo': [
            {'codigo': item['nivel_riesgo'], 'label': item['nivel_riesgo'].title(), 'total': item['total']}
            for item in legajos.values('nivel_riesgo').order_by('nivel_riesgo').annotate(total=models.Count('id'))
        ],
        'por_dispositivo': [
            {
                'nombre': item['dispositivo__nombre'] or 'Sin institución',
                'tipo_label': 'Institución',
                'total': item['total'],
            }
            for item in legajos.values('dispositivo__nombre').order_by('dispositivo__nombre').annotate(total=models.Count('id'))[:10]
        ],
        'por_mes': [
            {'mes': item['mes'], 'total': item['total']}
            for item in legajos.annotate(mes=models.functions.TruncMonth('fecha_admision')).values('mes').order_by('-mes').annotate(total=models.Count('id'))[:6]
        ],
        'metricas_calidad': {
            'ttr_promedio': 0,
            'adherencia_adecuada': 0,
            'tasa_derivacion': 0,
            'eventos_por_100': 0,
            'cobertura_seguimiento': 0,
        },
    }
    return render(request, 'legajos/reportes.html', {'stats': stats})


@login_required
@group_required(['Ciudadanos'])
def exportar_reportes_csv(request):
    """Exportación CSV básica de legajos para no romper la acción principal de reportes."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reportes_legajos.csv"'

    writer = csv.writer(response)
    writer.writerow(['codigo', 'apellido', 'nombre', 'dni', 'estado', 'nivel_riesgo', 'fecha_admision'])

    legajos = LegajoAtencion.objects.select_related('ciudadano').order_by('-fecha_admision')[:1000]
    for legajo in legajos:
        writer.writerow([
            legajo.codigo,
            legajo.ciudadano.apellido,
            legajo.ciudadano.nombre,
            legajo.ciudadano.dni,
            legajo.estado,
            legajo.nivel_riesgo,
            legajo.fecha_admision,
        ])

    return response