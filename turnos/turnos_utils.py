from datetime import date, datetime, timedelta

from .models import ConfiguracionTurnos, DisponibilidadConfiguracion


def get_slots_por_configuracion(configuracion: ConfiguracionTurnos, fecha: date) -> list:
    """
    Retorna lista de slots disponibles para una ConfiguracionTurnos en una fecha dada.
    Cada slot: {'hora_inicio': time, 'hora_fin': time, 'disponible': bool, 'cupo_restante': int}
    """
    from portal.models import TurnoCiudadano

    dia_semana = fecha.weekday()

    disponibilidades = DisponibilidadConfiguracion.objects.filter(
        configuracion=configuracion,
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
                configuracion=configuracion,
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


def get_calendario_por_configuracion(
    configuracion: ConfiguracionTurnos, anio: int, mes: int
) -> dict:
    """
    Retorna un dict {fecha: tiene_disponibilidad} para el mes dado.
    Solo incluye fechas futuras (desde hoy).
    Tiene en cuenta anticipación mínima y máxima de la configuración.
    """
    from calendar import monthrange

    hoy = date.today()
    fecha_minima = hoy + timedelta(hours=configuracion.anticipacion_minima_hs / 24)
    fecha_maxima = hoy + timedelta(days=configuracion.anticipacion_maxima_dias)

    _, dias_en_mes = monthrange(anio, mes)

    dias_activos = set(
        DisponibilidadConfiguracion.objects.filter(configuracion=configuracion, activo=True)
        .values_list('dia_semana', flat=True)
    )

    resultado = {}
    for dia in range(1, dias_en_mes + 1):
        fecha = date(anio, mes, dia)
        if fecha < fecha_minima.date() if hasattr(fecha_minima, 'date') else fecha < hoy:
            continue
        if fecha > fecha_maxima:
            continue
        resultado[fecha] = fecha.weekday() in dias_activos

    return resultado
