"""Paquete de vistas para la app de configuracion."""

from .clases import (  # noqa: F401
    ClaseAsistenciaView,
    ClaseCreateView,
    ClaseEditarView,
    ClaseEliminarView,
    ClaseListView,
)
from .actividades import (
    ActividadDetailView,
    ActividadEditarView,
    DerivacionAceptarView,
    DerivacionRechazarView,
    InscripcionDirectaView,
    InscriptoEditarView,
    StaffActividadCreateView,
    buscar_personal_ajax,
)
from .extra import (
    AsistenciaView,
    StaffDesasignarView,
    StaffEditarView,
    TomarAsistenciaView,
)
from .geografia import (
    LocalidadCreateView,
    LocalidadDeleteView,
    LocalidadListView,
    LocalidadUpdateView,
    MunicipioCreateView,
    MunicipioDeleteView,
    MunicipioListView,
    MunicipioUpdateView,
    ProvinciaCreateView,
    ProvinciaDeleteView,
    ProvinciaListView,
    ProvinciaUpdateView,
)
from .secretaria import (
    SecretariaListView,
    SecretariaCreateView,
    SecretariaUpdateView,
    SecretariaDeleteView,
    SubsecretariaListView,
    SubsecretariaCreateView,
    SubsecretariaUpdateView,
    SubsecretariaDeleteView,
)
from .programas import (
    programa_list,
    programa_wizard_paso1,
    programa_wizard_paso2,
    programa_wizard_paso3,
    programa_wizard_paso4,
    programa_editar_paso1,
    programa_editar_paso2,
    programa_editar_paso3,
    programa_editar_paso4,
    programa_cambiar_estado,
)
from .institucional import (
    DispositivoCreateView,
    DispositivoForm,
    DispositivoListView,
    DispositivoRed,
    DispositivoUpdateView,
    InstitucionCreateView,
    InstitucionDeleteView,
    InstitucionDetailView,
    InstitucionListView,
    InstitucionUpdateView,
)
