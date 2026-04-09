"""Formularios para la app de legajos."""

from .ciudadanos import (  # noqa: F401
    AdmisionLegajoForm,
    BuscarCiudadanoForm,
    CiudadanoConfirmarForm,
    CiudadanoForm,
    CiudadanoManualForm,
    CiudadanoUpdateForm,
    ConsentimientoForm,
    ConsultaRenaperForm,
)
from .clinico import (  # noqa: F401
    DerivacionForm,
    EvaluacionInicialForm,
    EventoCriticoForm,
    LegajoCerrarForm,
    LegajoReabrirForm,
    PlanIntervencionForm,
    SeguimientoForm,
)
from .contactos import HistorialContactoForm  # noqa: F401
from .derivacion import DerivarProgramaForm  # noqa: F401
from .institucional import (  # noqa: F401
    CambiarEstadoCasoForm,
    DerivacionInstitucionalForm,
    RechazarDerivacionForm,
)
from .operativa import InscribirActividadForm  # noqa: F401
