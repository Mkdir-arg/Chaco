"""Fachada compatible para vistas de backoffice de turnos."""

from .configuracion import (
    configuracion_crear,
    configuracion_editar,
    configuracion_lista,
    disponibilidad_agregar,
    disponibilidad_editar,
    disponibilidad_eliminar,
    disponibilidad_grilla,
)
from .turnos import (
    agenda,
    api_slots_configuracion,
    backoffice_home,
    bandeja_pendientes,
    turno_aprobar,
    turno_cancelar,
    turno_completar,
    turno_detalle,
    turno_rechazar,
)
