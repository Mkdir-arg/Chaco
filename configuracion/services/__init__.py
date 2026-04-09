"""Servicios para la app de configuracion."""

from .clases import (  # noqa: F401
    ClaseError,
    crear_clase,
    editar_clase,
    eliminar_clase,
    guardar_asistencia_clase,
)
from .actividades import (  # noqa: F401
    ConfiguracionInstitucionalService,
    ConfiguracionWorkflowError,
)
