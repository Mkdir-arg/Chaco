from django.db.models import Count, Q
from django.utils import timezone

from legajos.models import AsistenciaClase, ClaseActividad, InscriptoActividad


def get_clases_de_actividad(actividad):
    """Retorna las clases de una actividad anotadas con estadísticas de asistencia."""
    return (
        ClaseActividad.objects.filter(actividad=actividad)
        .annotate(
            total_presentes=Count(
                'asistencias',
                filter=Q(asistencias__estado__in=['PRESENTE', 'TARDANZA']),
            ),
            total_nomina=Count('asistencias'),
        )
        .order_by('fecha', 'hora_inicio')
    )


def build_clase_asistencia_context(clase):
    """
    Construye el contexto para el formulario de asistencia de una clase.
    La nómina incluye solo inscriptos cuya fecha de inscripción es <= fecha de la clase.
    """
    hoy = timezone.localdate()

    nomina_base = InscriptoActividad.objects.filter(
        actividad=clase.actividad,
        estado__in=['INSCRITO', 'ACTIVO'],
        creado__date__lte=clase.fecha,
    ).select_related('ciudadano')

    # Para cada inscripto, obtener su registro de asistencia existente (si hay)
    asistencias_existentes = {
        a.inscripcion_id: a
        for a in AsistenciaClase.objects.filter(
            clase=clase,
            inscripcion__in=nomina_base,
        )
    }

    nomina_con_asistencia = []
    for inscripto in nomina_base:
        asistencia = asistencias_existentes.get(inscripto.pk)
        nomina_con_asistencia.append({
            'inscripto': inscripto,
            'asistencia': asistencia,
            'estado_actual': asistencia.estado if asistencia else AsistenciaClase.Estado.AUSENTE,
        })

    return {
        'clase': clase,
        'nomina': nomina_con_asistencia,
        'bloqueado': clase.fecha > hoy,
        'estados': AsistenciaClase.Estado.choices,
    }


def calcular_porcentaje_asistencia(inscripto):
    """
    Calcula el porcentaje de asistencia de un inscripto.
    Cuenta solo clases pasadas o de hoy en las que el inscripto estaba en nómina.
    TARDANZA cuenta como presencia.
    Retorna float con 1 decimal, o None si no hay clases elegibles.
    """
    hoy = timezone.localdate()
    clases_elegibles = ClaseActividad.objects.filter(
        actividad=inscripto.actividad,
        fecha__lte=hoy,
        fecha__gte=inscripto.creado.date(),
    ).count()

    if clases_elegibles == 0:
        return None

    presencias = AsistenciaClase.objects.filter(
        inscripcion=inscripto,
        estado__in=[AsistenciaClase.Estado.PRESENTE, AsistenciaClase.Estado.TARDANZA],
    ).count()

    return round(presencias / clases_elegibles * 100, 1)
