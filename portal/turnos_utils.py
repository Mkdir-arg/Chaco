from datetime import datetime, timedelta, date

from .models import DisponibilidadTurnos, TurnoCiudadano


def get_slots_disponibles(recurso, fecha: date) -> list:
    """
    Retorna lista de slots disponibles para un recurso en una fecha dada.
    Cada slot: {'hora_inicio': time, 'hora_fin': time, 'disponible': bool, 'cupo_restante': int}
    """
    dia_semana = fecha.weekday()  # 0=Lunes

    disponibilidades = DisponibilidadTurnos.objects.filter(
        recurso=recurso,
        dia_semana=dia_semana,
        activo=True,
    )

    slots = []
    for disp in disponibilidades:
        hora_actual = datetime.combine(fecha, disp.hora_inicio)
        hora_fin_disp = datetime.combine(fecha, disp.hora_fin)
        duracion = timedelta(minutes=disp.duracion_turno_min)

        while hora_actual + duracion <= hora_fin_disp:
            hora_slot_inicio = hora_actual.time()
            hora_slot_fin = (hora_actual + duracion).time()

            ocupados = TurnoCiudadano.objects.filter(
                recurso=recurso,
                fecha=fecha,
                hora_inicio=hora_slot_inicio,
                estado__in=[TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
            ).count()

            cupo_restante = disp.cupo_maximo - ocupados

            slots.append({
                'hora_inicio': hora_slot_inicio,
                'hora_fin': hora_slot_fin,
                'disponible': cupo_restante > 0,
                'cupo_restante': max(0, cupo_restante),
            })

            hora_actual += duracion

    return slots


def get_calendario_mensual(recurso, anio: int, mes: int) -> dict:
    """
    Retorna un dict {fecha: tiene_disponibilidad} para el mes dado.
    Solo incluye fechas futuras (desde hoy).
    """
    from calendar import monthrange
    from datetime import date as date_type

    hoy = date_type.today()
    _, dias_en_mes = monthrange(anio, mes)
    dias_con_disponibilidad = {}

    dias_activos = set(
        DisponibilidadTurnos.objects.filter(recurso=recurso, activo=True)
        .values_list('dia_semana', flat=True)
    )

    for dia in range(1, dias_en_mes + 1):
        fecha = date_type(anio, mes, dia)
        if fecha < hoy:
            continue
        dias_con_disponibilidad[fecha] = fecha.weekday() in dias_activos

    return dias_con_disponibilidad
