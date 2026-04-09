"""
Servicios para gestión de acceso a actividades institucionales.
"""
import secrets
import string

from django.db import transaction


class InscripcionError(Exception):
    pass


def _generar_codigo_inscripcion():
    from ..models import InscriptoActividad

    alphabet = string.ascii_uppercase + string.digits
    for _ in range(10):
        codigo = ''.join(secrets.choice(alphabet) for _ in range(8))
        if not InscriptoActividad.objects.filter(codigo_inscripcion=codigo).exists():
            return codigo
    raise RuntimeError('No se pudo generar un código de inscripción único.')


@transaction.atomic
def inscribir_ciudadano_a_actividad(actividad, ciudadano, usuario, observaciones=''):
    """
    Inscribe un ciudadano a una actividad validando acceso, unicidad y cupo.

    Returns:
        InscriptoActividad: el registro creado.

    Raises:
        InscripcionError: si no se puede realizar la inscripción.
    """
    from ..models import HistorialInscripto, InscriptoActividad, PlanFortalecimiento

    # Lock sobre la actividad para evitar race conditions en cupo
    actividad = PlanFortalecimiento.objects.select_for_update().get(pk=actividad.pk)

    # Validar tipo de acceso
    puede, mensaje = validar_acceso_actividad(actividad, ciudadano)
    if not puede:
        raise InscripcionError(mensaje)

    # Verificar que no tenga inscripción activa
    ya_activo = InscriptoActividad.objects.filter(
        actividad=actividad,
        ciudadano=ciudadano,
        estado__in=[InscriptoActividad.Estado.INSCRITO, InscriptoActividad.Estado.ACTIVO],
    ).exists()
    if ya_activo:
        raise InscripcionError('El ciudadano ya tiene una inscripción activa en esta actividad.')

    # Validar cupo (0 = sin límite)
    if actividad.cupo_ciudadanos > 0:
        inscriptos_activos = InscriptoActividad.objects.filter(
            actividad=actividad,
            estado__in=[InscriptoActividad.Estado.INSCRITO, InscriptoActividad.Estado.ACTIVO],
        ).count()
        if inscriptos_activos >= actividad.cupo_ciudadanos:
            raise InscripcionError(
                'Cupo completo. Esta actividad no acepta nuevas inscripciones.'
            )

    codigo = _generar_codigo_inscripcion()

    inscripto = InscriptoActividad.objects.create(
        actividad=actividad,
        ciudadano=ciudadano,
        estado=InscriptoActividad.Estado.INSCRITO,
        codigo_inscripcion=codigo,
        inscrito_por=usuario,
        observaciones=observaciones,
    )

    HistorialInscripto.objects.create(
        inscripto=inscripto,
        accion=HistorialInscripto.TipoAccion.INSCRIPCION,
        usuario=usuario,
        descripcion=f'Inscripto en la actividad. Código: {codigo}',
        estado_anterior='',
    )

    return inscripto


def get_estado_inscripcion_ciudadano(actividad, ciudadano):
    """
    Retorna el InscriptoActividad activo (INSCRITO o ACTIVO) del ciudadano en la actividad,
    o None si no tiene inscripción activa.
    """
    from ..models import InscriptoActividad

    return InscriptoActividad.objects.filter(
        actividad=actividad,
        ciudadano=ciudadano,
        estado__in=[InscriptoActividad.Estado.INSCRITO, InscriptoActividad.Estado.ACTIVO],
    ).first()


def validar_acceso_actividad(actividad, ciudadano):
    """
    Verifica si un ciudadano puede inscribirse a una actividad según su tipo de acceso.

    Returns:
        tuple[bool, str]: (puede_acceder, mensaje_error)
        - Si puede_acceder es True, mensaje_error es cadena vacía.
        - Si puede_acceder es False, mensaje_error describe el requisito faltante.
    """
    from ..models import PlanFortalecimiento
    from ..models_programas import InscripcionPrograma

    if actividad.tipo_acceso == PlanFortalecimiento.TipoAcceso.LIBRE:
        return True, ''

    # REQUIERE_PROGRAMA
    if not actividad.programa_requerido_id:
        # Mal configurada — no bloqueamos al ciudadano
        return True, ''

    tiene_inscripcion = InscripcionPrograma.objects.filter(
        ciudadano=ciudadano,
        programa_id=actividad.programa_requerido_id,
        estado__in=['ACTIVO', 'EN_SEGUIMIENTO'],
    ).exists()

    if tiene_inscripcion:
        return True, ''

    nombre_programa = actividad.programa_requerido.nombre if actividad.programa_requerido else ''
    return (
        False,
        f'Para acceder a esta actividad debés estar inscripto activo en el programa "{nombre_programa}".',
    )
