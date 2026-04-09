"""Selectors para la app de configuracion."""

from .clases import (  # noqa: F401
    build_clase_asistencia_context,
    calcular_porcentaje_asistencia,
    get_clases_de_actividad,
)
from .instituciones import (  # noqa: F401
    build_actividad_detail_context,
    build_institucion_detail_context,
    get_instituciones_queryset_for_user,
    search_personal_for_actividad,
)
