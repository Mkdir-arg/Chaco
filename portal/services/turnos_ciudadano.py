from django.db import transaction

from ..models import DisponibilidadTurnos, TurnoCiudadano


class TurnoNoDisponibleError(Exception):
    pass


@transaction.atomic
def reservar_turno_ciudadano(*, ciudadano, recurso, fecha, hora_inicio, hora_fin, motivo):
    ocupados = TurnoCiudadano.objects.select_for_update().filter(
        recurso=recurso,
        fecha=fecha,
        hora_inicio=hora_inicio,
        estado__in=[TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
    ).count()

    disponibilidad = DisponibilidadTurnos.objects.filter(
        recurso=recurso,
        dia_semana=fecha.weekday(),
        hora_inicio__lte=hora_inicio,
        hora_fin__gte=hora_fin,
        activo=True,
    ).first()

    if not disponibilidad or ocupados >= disponibilidad.cupo_maximo:
        raise TurnoNoDisponibleError('Este turno ya no está disponible. Por favor elegí otro horario.')

    estado_inicial = (
        TurnoCiudadano.Estado.PENDIENTE
        if recurso.requiere_aprobacion
        else TurnoCiudadano.Estado.CONFIRMADO
    )

    return TurnoCiudadano.objects.create(
        ciudadano=ciudadano,
        recurso=recurso,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        estado=estado_inicial,
        motivo_consulta=motivo,
    )


def cancelar_turno_ciudadano(turno):
    if turno.estado in [TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO]:
        turno.estado = TurnoCiudadano.Estado.CANCELADO_CIUDADANO
        turno.save(update_fields=['estado', 'modificado'])
        return True
    return False
