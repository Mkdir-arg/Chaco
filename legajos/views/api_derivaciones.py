"""
Vistas API para derivaciones de programas
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import Ciudadano
from ..models_institucional import DerivacionCiudadano
from ..models_programas import Programa


@login_required
def derivaciones_programa_api(request, ciudadano_id, programa_id):
    """API para obtener derivaciones de un ciudadano a un programa específico."""
    ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)
    programa = get_object_or_404(Programa, id=programa_id)

    derivaciones = DerivacionCiudadano.objects.filter(
        ciudadano=ciudadano,
        programa=programa,
    ).select_related(
        'programa_origen',
        'derivado_por',
        'quien_responde',
    ).order_by('-creado')

    derivaciones_data = []
    for d in derivaciones:
        derivaciones_data.append({
            'id': d.id,
            'creado': d.creado.isoformat(),
            'programa_origen': d.programa_origen.nombre if d.programa_origen else None,
            'motivo': d.motivo,
            'urgencia': d.urgencia,
            'urgencia_display': d.get_urgencia_display(),
            'estado': d.estado,
            'estado_display': d.get_estado_display(),
            'tipo_inicio': d.tipo_inicio,
            'tipo_inicio_display': d.get_tipo_inicio_display(),
            'derivado_por': d.derivado_por.get_full_name() if d.derivado_por else None,
            'fecha_respuesta': d.fecha_respuesta.isoformat() if d.fecha_respuesta else None,
            'quien_responde': d.quien_responde.get_full_name() if d.quien_responde else None,
            'respuesta': d.respuesta,
        })

    return JsonResponse({
        'success': True,
        'derivaciones': derivaciones_data,
        'total': len(derivaciones_data),
    })
