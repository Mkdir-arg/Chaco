"""Servicios para la app de legajos."""

from .actividades import (  # noqa: F401
    InscripcionError,
    get_estado_inscripcion_ciudadano,
    inscribir_ciudadano_a_actividad,
    validar_acceso_actividad,
)
from .admision import AdmisionSessionService  # noqa: F401
from .alertas import AlertasService  # noqa: F401
from .ciudadanos import CiudadanosService, RenaperLookupError  # noqa: F401
from .contactos import (  # noqa: F401
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    ContactosFilesError,
    eliminar_archivo_por_id,
    subir_archivos_para_objeto,
)
from .derivaciones_programa import DerivacionProgramaResult, DerivacionProgramaService  # noqa: F401
from .filtros_usuario import FiltrosUsuarioService  # noqa: F401
from .institucional import CasoService, DerivacionCiudadanoService, DerivacionService  # noqa: F401
from .legajos import LegajoWorkflowService  # noqa: F401
from .nachec import (  # noqa: F401
    ServicioDeteccionDuplicados,
    ServicioOperacionNachec,
    ServicioSLA,
    ServicioTransicionNachec,
)
from .programas import BajaProgramaService  # noqa: F401
from .solapas import SolapasService  # noqa: F401
