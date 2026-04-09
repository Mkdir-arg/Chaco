from datetime import date

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render

from core.decorators import ciudadano_required

from ..forms import CiudadanoConfirmarTurnoForm
from ..selectors import (
    get_recurso_turnos_activo_or_404,
    get_recursos_turnos_activos,
    get_turno_ciudadano_or_404,
    get_turnos_ciudadano_contexto,
)
from ..services.turnos_ciudadano import (
    TurnoNoDisponibleError,
    cancelar_turno_ciudadano,
    reservar_turno_ciudadano,
)
from ..turnos_utils import get_calendario_mensual, get_slots_disponibles


@ciudadano_required
def ciudadano_mis_turnos(request):
    ciudadano = request.user.ciudadano_perfil
    context = {'ciudadano': ciudadano}
    context.update(get_turnos_ciudadano_contexto(ciudadano))
    return render(request, 'portal/ciudadano/mis_turnos.html', context)


@ciudadano_required
def ciudadano_solicitar_turno(request):
    ciudadano = request.user.ciudadano_perfil
    return render(
        request,
        'portal/ciudadano/solicitar_turno.html',
        {
            'ciudadano': ciudadano,
            'recursos': get_recursos_turnos_activos(),
        },
    )


@ciudadano_required
def ciudadano_turno_calendario(request, recurso_id):
    ciudadano = request.user.ciudadano_perfil
    recurso = get_recurso_turnos_activo_or_404(recurso_id)

    hoy = date.today()
    anio = int(request.GET.get('anio', hoy.year))
    mes = int(request.GET.get('mes', hoy.month))
    calendario = get_calendario_mensual(recurso, anio, mes)

    mes_anterior = {'anio': anio - 1, 'mes': 12} if mes == 1 else {'anio': anio, 'mes': mes - 1}
    mes_siguiente = {'anio': anio + 1, 'mes': 1} if mes == 12 else {'anio': anio, 'mes': mes + 1}

    context = {
        'ciudadano': ciudadano,
        'recurso': recurso,
        'calendario': calendario,
        'calendario_json': {fecha.isoformat(): disponible for fecha, disponible in calendario.items()},
        'anio': anio,
        'mes': mes,
        'mes_nombre': date(anio, mes, 1).strftime('%B %Y').capitalize(),
        'mes_anterior': mes_anterior,
        'mes_siguiente': mes_siguiente,
        'hoy_iso': hoy.isoformat(),
        'primer_dia_offset': range(date(anio, mes, 1).weekday()),
    }
    return render(request, 'portal/ciudadano/turno_calendario.html', context)


@ciudadano_required
def ciudadano_turno_slots(request, recurso_id):
    recurso = get_recurso_turnos_activo_or_404(recurso_id)
    fecha_str = request.GET.get('fecha')

    try:
        fecha = date.fromisoformat(fecha_str)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Fecha inválida'}, status=400)

    if fecha < date.today():
        return JsonResponse({'error': 'No se pueden solicitar turnos para fechas pasadas'}, status=400)

    slots = get_slots_disponibles(recurso, fecha)
    return JsonResponse(
        {
            'slots': [
                {
                    'hora_inicio': slot['hora_inicio'].strftime('%H:%M'),
                    'hora_fin': slot['hora_fin'].strftime('%H:%M'),
                    'disponible': slot['disponible'],
                }
                for slot in slots
            ]
        }
    )


@ciudadano_required
def ciudadano_confirmar_turno(request, recurso_id):
    ciudadano = request.user.ciudadano_perfil
    recurso = get_recurso_turnos_activo_or_404(recurso_id)
    form = CiudadanoConfirmarTurnoForm(request.POST or None, initial=request.GET or None)

    if request.method == 'POST' and form.is_valid():
        try:
            turno = reservar_turno_ciudadano(
                ciudadano=ciudadano,
                recurso=recurso,
                fecha=form.cleaned_data['fecha'],
                hora_inicio=form.cleaned_data['hora_inicio'],
                hora_fin=form.cleaned_data['hora_fin'],
                motivo=form.cleaned_data['motivo'],
            )
        except TurnoNoDisponibleError as exc:
            messages.error(request, str(exc))
            return redirect('portal:ciudadano_turno_calendario', recurso_id=recurso_id)
        return redirect('portal:ciudadano_turno_confirmado', pk=turno.pk)

    if request.method == 'POST' and not form.is_valid():
        messages.error(request, 'Datos del turno inválidos. Intentá de nuevo.')
        return redirect('portal:ciudadano_turno_calendario', recurso_id=recurso_id)

    return render(
        request,
        'portal/ciudadano/turno_confirmar.html',
        {
            'ciudadano': ciudadano,
            'recurso': recurso,
            'fecha': request.GET.get('fecha'),
            'hora_inicio': request.GET.get('hora_inicio'),
            'hora_fin': request.GET.get('hora_fin'),
            'form': form,
        },
    )


@ciudadano_required
def ciudadano_turno_confirmado(request, pk):
    ciudadano = request.user.ciudadano_perfil
    return render(
        request,
        'portal/ciudadano/turno_confirmado.html',
        {
            'ciudadano': ciudadano,
            'turno': get_turno_ciudadano_or_404(ciudadano, pk),
        },
    )


@ciudadano_required
def ciudadano_cancelar_turno(request, pk):
    ciudadano = request.user.ciudadano_perfil
    turno = get_turno_ciudadano_or_404(ciudadano, pk)

    if request.method == 'POST':
        if cancelar_turno_ciudadano(turno):
            messages.success(
                request,
                f'Tu turno del {turno.fecha.strftime("%d/%m/%Y")} fue cancelado.',
            )
        return redirect('portal:ciudadano_mis_turnos')

    return render(
        request,
        'portal/ciudadano/turno_cancelar.html',
        {
            'ciudadano': ciudadano,
            'turno': turno,
        },
    )
