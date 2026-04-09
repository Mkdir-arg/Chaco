from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from ..models import Ciudadano, InscriptoActividad


@login_required
@require_http_methods(["GET"])
def cursos_actividades_ciudadano(request, pk):
    """API endpoint para obtener cursos y actividades activas del ciudadano"""
    ciudadano = get_object_or_404(Ciudadano, pk=pk)
    
    inscripciones = InscriptoActividad.objects.filter(
        ciudadano=ciudadano,
        estado__in=['INSCRITO', 'ACTIVO']
    ).select_related(
        'actividad__legajo_institucional__institucion'
    ).order_by('-fecha_inscripcion')
    
    results = []
    for inscripcion in inscripciones:
        actividad = inscripcion.actividad
        institucion = actividad.legajo_institucional.institucion
        
        results.append({
            'id': inscripcion.id,
            'estado': inscripcion.estado,
            'estado_display': inscripcion.get_estado_display(),
            'fecha_inscripcion': inscripcion.fecha_inscripcion.isoformat(),
            'observaciones': inscripcion.observaciones,
            'actividad': {
                'id': actividad.id,
                'nombre': actividad.nombre,
                'tipo': actividad.tipo,
                'tipo_display': actividad.get_tipo_display(),
                'cupo_ciudadanos': actividad.cupo_ciudadanos,
                'inscritos_count': InscriptoActividad.objects.filter(
                    actividad=actividad,
                    estado__in=['INSCRITO', 'ACTIVO']
                ).count(),
                'institucion': {
                    'id': institucion.id,
                    'nombre': institucion.nombre
                }
            }
        })
    
    return JsonResponse({'results': results})
