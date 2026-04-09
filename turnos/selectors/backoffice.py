from datetime import date, timedelta

from django.db.models import Count, Q

from portal.models import TurnoCiudadano

from ..models import ConfiguracionTurnos


def get_backoffice_home_context():
    hoy = date.today()
    return {
        "pendientes_count": TurnoCiudadano.objects.filter(
            estado=TurnoCiudadano.Estado.PENDIENTE
        ).count(),
        "hoy_count": TurnoCiudadano.objects.filter(
            fecha=hoy,
            estado__in=[
                TurnoCiudadano.Estado.PENDIENTE,
                TurnoCiudadano.Estado.CONFIRMADO,
            ],
        ).count(),
        "configs_count": ConfiguracionTurnos.objects.filter(activo=True).count(),
        "hoy": hoy,
    }


def get_configuraciones_list():
    return ConfiguracionTurnos.objects.annotate(
        total_disponibilidades=Count(
            "disponibilidades", filter=Q(disponibilidades__activo=True)
        ),
        total_turnos_pendientes=Count(
            "turnos", filter=Q(turnos__estado=TurnoCiudadano.Estado.PENDIENTE)
        ),
    ).order_by("nombre")


def build_agenda_context(fecha, config_id=None, estado_filter=None):
    hoy = date.today()
    fecha_anterior = fecha - timedelta(days=1)
    fecha_siguiente = fecha + timedelta(days=1)

    turnos = TurnoCiudadano.objects.filter(fecha=fecha).select_related(
        "ciudadano", "recurso", "configuracion", "aprobado_por"
    ).order_by("hora_inicio")

    if config_id:
        turnos = turnos.filter(configuracion_id=config_id)

    if estado_filter:
        turnos = turnos.filter(estado=estado_filter)

    contadores = {
        "pendiente": turnos.filter(estado=TurnoCiudadano.Estado.PENDIENTE).count(),
        "confirmado": turnos.filter(estado=TurnoCiudadano.Estado.CONFIRMADO).count(),
        "completado": turnos.filter(estado=TurnoCiudadano.Estado.COMPLETADO).count(),
        "cancelado": turnos.filter(
            estado__in=[
                TurnoCiudadano.Estado.CANCELADO_CIUDADANO,
                TurnoCiudadano.Estado.CANCELADO_SISTEMA,
            ]
        ).count(),
    }

    return {
        "turnos": turnos,
        "fecha": fecha,
        "fecha_anterior": fecha_anterior,
        "fecha_siguiente": fecha_siguiente,
        "contadores": contadores,
        "configs": ConfiguracionTurnos.objects.filter(activo=True).order_by("nombre"),
        "config_id_actual": config_id,
        "estado_filter": estado_filter,
        "estados": TurnoCiudadano.Estado.choices,
        "hoy": hoy,
    }


def build_bandeja_pendientes_context():
    hoy = date.today()
    maniana = hoy + timedelta(days=1)
    pendientes = TurnoCiudadano.objects.filter(
        estado=TurnoCiudadano.Estado.PENDIENTE,
    ).select_related("ciudadano", "recurso", "configuracion").order_by(
        "fecha", "hora_inicio"
    )

    return {
        "urgentes": pendientes.filter(fecha__range=[hoy, maniana]),
        "vencidos": pendientes.filter(fecha__lt=hoy),
        "normales": pendientes.filter(fecha__gt=maniana),
        "total": pendientes.count(),
        "hoy": hoy,
    }


def get_turno_detalle_queryset():
    return TurnoCiudadano.objects.select_related(
        "ciudadano", "recurso", "configuracion", "aprobado_por"
    )
