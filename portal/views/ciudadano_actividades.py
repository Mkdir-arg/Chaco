from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from core.decorators import ciudadano_required
from legajos.models import PlanFortalecimiento
from legajos.services.actividades import InscripcionError, inscribir_ciudadano_a_actividad

from ..selectors import (
    get_actividades_accesibles,
    get_asistencia_ciudadano_en_actividad,
    get_inscripciones_ciudadano,
)


@ciudadano_required
def ciudadano_mis_actividades(request):
    ciudadano = request.user.ciudadano_perfil
    todas_inscripciones = list(get_inscripciones_ciudadano(ciudadano))
    inscripciones_activas_dict = {
        i.actividad_id: i for i in todas_inscripciones
        if i.estado in ['INSCRITO', 'ACTIVO']
    }
    actividades = get_actividades_accesibles(ciudadano)
    # Lista de (actividad, inscripcion_activa_o_None) para el template
    actividades_con_estado = [
        (actividad, inscripciones_activas_dict.get(actividad.pk))
        for actividad in actividades
    ]
    context = {
        'ciudadano': ciudadano,
        'actividades_con_estado': actividades_con_estado,
        'mis_inscripciones': todas_inscripciones,
    }
    return render(request, 'portal/ciudadano/mis_actividades.html', context)


@ciudadano_required
def ciudadano_inscribirse_actividad(request, actividad_pk):
    if request.method != 'POST':
        return redirect('portal:ciudadano_mis_actividades')

    ciudadano = request.user.ciudadano_perfil
    actividad = get_object_or_404(PlanFortalecimiento, pk=actividad_pk)

    try:
        inscripto = inscribir_ciudadano_a_actividad(
            actividad=actividad,
            ciudadano=ciudadano,
            usuario=request.user,
        )
    except InscripcionError as exc:
        messages.error(request, str(exc))
        return redirect('portal:ciudadano_mis_actividades')

    messages.success(
        request,
        f'Te inscribiste correctamente en "{actividad.nombre}". '
        f'Tu código de inscripción es: {inscripto.codigo_inscripcion}',
    )
    return redirect('portal:ciudadano_mis_actividades')


@ciudadano_required
def ciudadano_detalle_actividad(request, actividad_pk):
    ciudadano = request.user.ciudadano_perfil
    contexto = get_asistencia_ciudadano_en_actividad(ciudadano, actividad_pk)
    if contexto is None:
        messages.error(request, 'No estás inscripto en esta actividad.')
        return redirect('portal:ciudadano_mis_actividades')
    return render(request, 'portal/ciudadano/detalle_actividad.html', contexto)
