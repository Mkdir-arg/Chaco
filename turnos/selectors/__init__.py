"""Selectors para la app de turnos."""

from .backoffice import (  # noqa: F401
    build_agenda_context,
    build_bandeja_pendientes_context,
    get_backoffice_home_context,
    get_configuraciones_list,
    get_turno_detalle_queryset,
)
