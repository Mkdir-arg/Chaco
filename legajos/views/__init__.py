"""Views agrupadas de la app de legajos."""

from .alertas import (  # noqa: F401
    alertas_count_ajax,
    alertas_dashboard,
    alertas_preview_ajax,
    cerrar_alerta_ajax,
    debug_alertas,
    test_alertas_page,
)
from .ciudadanos import (  # noqa: F401
    CiudadanoConfirmarView,
    CiudadanoCreateView,
    CiudadanoDetailView,
    CiudadanoListView,
    CiudadanoManualView,
    CiudadanoUpdateView,
)
from .contactos_api import (  # noqa: F401
    actividades_ciudadano_api,
    alertas_ciudadano_api,
    archivos_ciudadano_api,
    archivos_legajo_api,
    cerrar_alerta_api,
    eliminar_archivo,
    evolucion_legajo_api,
    prediccion_riesgo_api,
    subir_archivos_ciudadano,
    subir_archivos_legajo,
    timeline_ciudadano_api,
)
from .contactos_panel import (  # noqa: F401
    dashboard_contactos_simple,
    historial_contactos_simple,
    red_contactos_simple,
)
from .cursos import cursos_actividades_ciudadano  # noqa: F401
from .dashboard_simple import dashboard_contactos_simple as dashboard_contactos_simple_debug  # noqa: F401
from .dashboard_simple import test_api  # noqa: F401
from .derivacion import derivar_programa_view  # noqa: F401
from .derivacion_programa import (  # noqa: F401
    aceptar_derivacion_programa,
    rechazar_derivacion_programa,
)
from .historial_contactos import (  # noqa: F401
    crear_contacto,
    detalle_contacto,
    editar_contacto,
    eliminar_contacto,
    historial_contactos_view,
)
from .institucional import (  # noqa: F401
    aceptar_derivacion,
    api_programa_indicadores,
    cambiar_estado_caso_view,
    caso_detalle,
    institucion_detalle_programatico,
    programa_casos,
    programa_derivaciones,
    rechazar_derivacion_view,
)
from .nachec_cierre import cerrar_caso_nachec, reabrir_caso_nachec  # noqa: F401
from .nachec_dashboard import dashboard_nachec  # noqa: F401
from .nachec_decisiones import activar_plan, cerrar_caso, evaluar_caso, pasar_a_seguimiento  # noqa: F401
from .nachec_operacion import (  # noqa: F401
    adjuntar_evidencias,
    asignar_territorial,
    autosave_relevamiento,
    completar_tarea,
    completar_validacion,
    enviar_a_asignacion,
    finalizar_relevamiento,
    formulario_relevamiento,
    iniciar_relevamiento,
    reasignar_territorial,
    ver_tarea_validacion,
)
from .nachec_prestaciones import (  # noqa: F401
    cancelar_prestacion,
    confirmar_entrega_prestacion,
    iniciar_prestacion,
    reprogramar_prestacion,
)
from .operativa import (  # noqa: F401
    ActividadesInscritoListView,
    InscribirActividadView,
    InstitucionCreateView,
    InstitucionDeleteView,
    InstitucionListView,
    InstitucionUpdateView,
    actividades_por_institucion,
    marcar_etapa_plan,
)
from .programas import ProgramaDetailView, ProgramaListView  # noqa: F401
from .solapas import (  # noqa: F401
    CiudadanoDetalleConSolapasView,
    aceptar_derivacion_programa,
    cerrar_inscripcion_programa,
    ciudadano_detalle_con_solapas,
    derivar_a_programa,
    inscribir_a_programa,
    rechazar_derivacion_programa,
)
