from datetime import date

from django.http import Http404
from django.shortcuts import get_object_or_404

from ..models import RecursoTurnos, TurnoCiudadano


def get_turnos_ciudadano_contexto(ciudadano):
    return {
        'turnos_proximos': TurnoCiudadano.objects.filter(
            ciudadano=ciudadano,
            fecha__gte=date.today(),
            estado__in=[TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
        ).select_related('recurso').order_by('fecha', 'hora_inicio'),
        'turnos_historial': TurnoCiudadano.objects.filter(
            ciudadano=ciudadano,
            fecha__lt=date.today(),
        ).select_related('recurso').order_by('-fecha', '-hora_inicio')[:10],
    }


def get_recursos_turnos_activos():
    return RecursoTurnos.objects.filter(activo=True).order_by('tipo', 'nombre')


def get_recurso_turnos_activo_or_404(recurso_id):
    return get_object_or_404(RecursoTurnos, pk=recurso_id, activo=True)


def get_turno_ciudadano_or_404(ciudadano, pk):
    return get_object_or_404(
        TurnoCiudadano.objects.select_related('recurso'),
        pk=pk,
        ciudadano=ciudadano,
    )
