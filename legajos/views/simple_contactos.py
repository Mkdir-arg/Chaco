"""Fachada compatible para vistas simples de contactos."""

from .contactos_api import (
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
from .contactos_panel import (
    dashboard_contactos_simple,
    historial_contactos_simple,
    red_contactos_simple,
)
