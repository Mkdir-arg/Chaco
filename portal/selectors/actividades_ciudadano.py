"""
Selector de actividades accesibles para un ciudadano en el portal.
"""
from django.db.models import Q


def get_actividades_accesibles(ciudadano, institucion=None):
    """
    Retorna las actividades que un ciudadano puede ver/solicitar inscripción.

    - Actividades LIBRE: siempre accesibles.
    - Actividades REQUIERE_PROGRAMA: solo si el ciudadano tiene InscripcionPrograma
      con estado ACTIVO o EN_SEGUIMIENTO en el programa requerido.

    Si se pasa 'institucion', filtra además por legajo_institucional__institucion.

    Usa 2 queries independientemente de la cantidad de actividades (anti N+1).
    """
    from legajos.models import PlanFortalecimiento
    from legajos.models_programas import InscripcionPrograma

    # IDs de programas en los que el ciudadano está activo
    programas_activos = set(
        InscripcionPrograma.objects.filter(
            ciudadano=ciudadano,
            estado__in=['ACTIVO', 'EN_SEGUIMIENTO'],
        ).values_list('programa_id', flat=True)
    )

    qs = PlanFortalecimiento.objects.filter(
        estado=PlanFortalecimiento.Estado.ACTIVO,
    ).select_related('programa_requerido', 'legajo_institucional__institucion')

    if institucion is not None:
        qs = qs.filter(legajo_institucional__institucion=institucion)

    qs = qs.filter(
        Q(tipo_acceso=PlanFortalecimiento.TipoAcceso.LIBRE)
        | Q(
            tipo_acceso=PlanFortalecimiento.TipoAcceso.REQUIERE_PROGRAMA,
            programa_requerido_id__in=programas_activos,
        )
    )

    return qs.order_by('nombre')


def get_inscripciones_ciudadano(ciudadano):
    """
    Retorna todas las inscripciones del ciudadano (historial completo, cualquier estado),
    ordenadas por fecha descendente.
    """
    from legajos.models import InscriptoActividad

    return InscriptoActividad.objects.filter(
        ciudadano=ciudadano,
    ).select_related(
        'actividad',
        'actividad__legajo_institucional__institucion',
    ).order_by('-fecha_inscripcion')


def get_asistencia_ciudadano_en_actividad(ciudadano, actividad_pk):
    """
    Retorna el contexto de asistencia de un ciudadano en una actividad específica.

    Returns:
        dict con 'inscripcion', 'clases_con_asistencia', 'total_clases',
        'total_presentes', 'porcentaje' — o None si el ciudadano no está inscripto.
    """
    from django.utils import timezone
    from legajos.models import AsistenciaClase, ClaseActividad, InscriptoActividad

    try:
        inscripcion = InscriptoActividad.objects.select_related(
            'actividad__legajo_institucional__institucion',
        ).get(ciudadano=ciudadano, actividad_id=actividad_pk)
    except InscriptoActividad.DoesNotExist:
        return None

    hoy = timezone.localdate()
    clases = ClaseActividad.objects.filter(
        actividad_id=actividad_pk,
        fecha__lte=hoy,
    ).order_by('fecha', 'hora_inicio')

    # Un solo query para todas las asistencias de esta inscripcion
    asistencias_dict = {
        a.clase_id: a
        for a in AsistenciaClase.objects.filter(
            inscripcion=inscripcion,
            clase__in=clases,
        )
    }

    clases_con_asistencia = [
        (clase, asistencias_dict.get(clase.pk))
        for clase in clases
    ]

    total_clases = len(clases_con_asistencia)
    total_presentes = sum(
        1 for _, a in clases_con_asistencia
        if a and a.estado in (AsistenciaClase.Estado.PRESENTE, AsistenciaClase.Estado.TARDANZA)
    )
    porcentaje = round(total_presentes / total_clases * 100) if total_clases else None

    return {
        'inscripcion': inscripcion,
        'clases_con_asistencia': clases_con_asistencia,
        'total_clases': total_clases,
        'total_presentes': total_presentes,
        'porcentaje': porcentaje,
    }
