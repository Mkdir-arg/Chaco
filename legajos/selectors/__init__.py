"""Selectors para la app de legajos."""

from .ciudadanos import (  # noqa: F401
    build_ciudadano_detail_context,
    get_ciudadanos_dashboard_metrics,
    get_ciudadanos_queryset,
)
from .contactos import (  # noqa: F401
    build_ciudadano_actividades_payload,
    build_ciudadano_archivos_payload,
    build_ciudadano_timeline_payload,
    build_legajo_archivos_payload,
    build_legajo_evolucion_payload,
    get_legajo_contactos_context,
)
from .legajos import (  # noqa: F401
    get_derivaciones_queryset,
    get_dispositivo_derivaciones_queryset,
    get_eventos_dashboard_metrics,
    get_eventos_queryset,
    get_export_legajos_queryset,
    get_legajo_detail_queryset,
    get_legajos_queryset,
    get_plan_vigente,
    get_planes_queryset,
    get_legajos_report_stats,
    get_responsable_candidates,
    get_seguimientos_dashboard_metrics,
    get_seguimientos_queryset,
)
