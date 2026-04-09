from django.db import transaction
from django.utils import timezone

from legajos.models import AsistenciaClase, ClaseActividad


class ClaseError(Exception):
    pass


@transaction.atomic
def crear_clase(actividad, fecha, hora_inicio, duracion_minutos, titulo, usuario):
    """Crea una nueva clase para una actividad."""
    clase = ClaseActividad.objects.create(
        actividad=actividad,
        fecha=fecha,
        hora_inicio=hora_inicio,
        duracion_minutos=duracion_minutos or None,
        titulo=titulo or '',
        creado_por=usuario,
    )
    return clase


@transaction.atomic
def editar_clase(clase, fecha, hora_inicio, duracion_minutos, titulo, usuario):
    """Edita una clase existente."""
    clase.fecha = fecha
    clase.hora_inicio = hora_inicio
    clase.duracion_minutos = duracion_minutos or None
    clase.titulo = titulo or ''
    clase.save()
    return clase


@transaction.atomic
def eliminar_clase(clase):
    """
    Elimina una clase. Falla si ya tiene asistencias registradas.
    """
    if clase.asistencias.exists():
        raise ClaseError(
            'No se puede eliminar una clase que ya tiene registros de asistencia.'
        )
    clase.delete()


@transaction.atomic
def guardar_asistencia_clase(clase, registros, usuario):
    """
    Guarda el listado de asistencia para una clase.
    registros: dict {inscripcion_id: estado}
    Bloquea si la clase es futura.
    """
    if clase.fecha > timezone.localdate():
        raise ClaseError('No se puede registrar asistencia en una clase con fecha futura.')

    procesados = 0
    for inscripcion_id, estado in registros.items():
        if estado not in [c[0] for c in AsistenciaClase.Estado.choices]:
            continue
        AsistenciaClase.objects.update_or_create(
            clase=clase,
            inscripcion_id=inscripcion_id,
            defaults={
                'estado': estado,
                'registrado_por': usuario,
            },
        )
        procesados += 1

    return procesados
