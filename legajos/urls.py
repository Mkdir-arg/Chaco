from django.urls import include, path

from .views import acompanamiento as views_acompanamiento
from .views import alertas as views_alertas
from .views import api_derivaciones as views_api_derivaciones
from .views import ciudadanos as views_ciudadanos
from .views import clinico as views_clinico
from .views import contactos_api as views_contactos_api
from .views import contactos_panel as views_contactos_panel
from .views import cursos as views_cursos
from .views.dashboard_contactos import (  # importar directamente del módulo, no del __init__
    dashboard_contactos as view_dashboard_contactos_completo,
    exportar_reporte_contactos as view_exportar_reporte_contactos,
    metricas_contactos_api as view_metricas_contactos_api,
    metricas_red_contactos_api as view_metricas_red_contactos_api,
)
from .views import dashboard_simple as views_simple
from .views import derivacion as views_derivacion
from .views import derivacion_programa as views_derivacion_programa
from .views import institucional as views_institucional
from .views import operativa as views_operativa
from .views import programas as views_programas

app_name = "legajos"

urlpatterns = [
    path("", views_clinico.LegajoListView.as_view(), name="lista"),
    path("nuevo/", views_ciudadanos.LegajoCreateView.as_view(), name="nuevo"),
    path("ciudadanos/", views_ciudadanos.CiudadanoListView.as_view(), name="ciudadanos"),
    path("ciudadanos/nuevo/", views_ciudadanos.CiudadanoCreateView.as_view(), name="ciudadano_nuevo"),
    path("ciudadanos/confirmar/", views_ciudadanos.CiudadanoConfirmarView.as_view(), name="ciudadano_confirmar"),
    path("ciudadanos/manual/", views_ciudadanos.CiudadanoManualView.as_view(), name="ciudadano_manual"),
    path("ciudadanos/<int:pk>/", views_ciudadanos.CiudadanoDetailView.as_view(), name="ciudadano_detalle"),
    path("ciudadanos/<int:pk>/editar/", views_ciudadanos.CiudadanoUpdateView.as_view(), name="ciudadano_editar"),
    path("programas/", views_programas.ProgramaListView.as_view(), name="programas"),
    path("programas/<int:pk>/", views_programas.ProgramaDetailView.as_view(), name="programa_detalle"),
    path(
        "acompanamiento/<int:inscripcion_id>/crear-legajo/",
        views_acompanamiento.crear_legajo_acompanamiento,
        name="crear_legajo_acompanamiento",
    ),
    path("nachec/", include("legajos.urls_nachec")),
    path(
        "instituciones/<int:pk>/detalle-programatico/",
        views_institucional.institucion_detalle_programatico,
        name="institucion_detalle_programatico",
    ),
    path(
        "programa/<int:institucion_programa_id>/derivaciones/",
        views_institucional.programa_derivaciones,
        name="programa_derivaciones",
    ),
    path(
        "derivacion/<int:derivacion_id>/aceptar/",
        views_derivacion_programa.aceptar_derivacion_programa,
        name="derivacion_aceptar",
    ),
    path(
        "derivacion/<int:derivacion_id>/rechazar/",
        views_derivacion_programa.rechazar_derivacion_programa,
        name="derivacion_rechazar",
    ),
    path(
        "programa/<int:institucion_programa_id>/casos/",
        views_institucional.programa_casos,
        name="programa_casos",
    ),
    path("caso/<int:caso_id>/", views_institucional.caso_detalle, name="caso_detalle"),
    path(
        "caso/<int:caso_id>/cambiar-estado/",
        views_institucional.cambiar_estado_caso_view,
        name="caso_cambiar_estado",
    ),
    path(
        "programa/<int:institucion_programa_id>/indicadores/",
        views_institucional.api_programa_indicadores,
        name="api_programa_indicadores",
    ),
    path(
        "ciudadanos/<int:ciudadano_id>/derivar-programa/",
        views_derivacion.derivar_programa_view,
        name="derivar_programa",
    ),
    path(
        "ciudadanos/<int:ciudadano_id>/derivaciones-programa/<int:programa_id>/",
        views_api_derivaciones.derivaciones_programa_api,
        name="derivaciones_programa_api",
    ),
    path("admision/paso1/", views_ciudadanos.AdmisionPaso1View.as_view(), name="admision_paso1"),
    path("admision/paso2/", views_ciudadanos.AdmisionPaso2View.as_view(), name="admision_paso2"),
    path("admision/paso3/", views_ciudadanos.AdmisionPaso3View.as_view(), name="admision_paso3"),
    path("<uuid:legajo_id>/evaluaciones/", views_clinico.EvaluacionListView.as_view(), name="evaluaciones"),
    path("<uuid:legajo_id>/evaluacion/", views_clinico.EvaluacionInicialView.as_view(), name="evaluacion"),
    path("<uuid:legajo_id>/planes/", views_clinico.PlanListView.as_view(), name="planes"),
    path("<uuid:legajo_id>/plan/", views_clinico.PlanIntervencionView.as_view(), name="plan"),
    path("plan/<int:pk>/editar/", views_clinico.PlanUpdateView.as_view(), name="plan_editar"),
    path("plan/<int:pk>/marcar-etapa/", views_operativa.marcar_etapa_plan, name="marcar_etapa_plan"),
    path("<uuid:legajo_id>/seguimientos/", views_clinico.SeguimientoListView.as_view(), name="seguimientos"),
    path("<uuid:legajo_id>/seguimiento/", views_clinico.SeguimientoCreateView.as_view(), name="seguimiento_nuevo"),
    path("seguimiento/<int:pk>/editar/", views_clinico.SeguimientoUpdateView.as_view(), name="seguimiento_editar"),
    path("<uuid:legajo_id>/derivaciones/", views_clinico.DerivacionListView.as_view(), name="derivaciones"),
    path("<uuid:legajo_id>/derivacion/", views_clinico.DerivacionCreateView.as_view(), name="derivacion_nueva"),
    path("derivacion/<int:pk>/editar/", views_clinico.DerivacionUpdateView.as_view(), name="derivacion_editar"),
    path(
        "actividades-por-institucion/<int:institucion_id>/",
        views_operativa.actividades_por_institucion,
        name="actividades_por_institucion",
    ),
    path("<uuid:legajo_id>/eventos/", views_clinico.EventoListView.as_view(), name="eventos"),
    path("<uuid:legajo_id>/evento/", views_clinico.EventoCriticoCreateView.as_view(), name="evento_nuevo"),
    path("evento/<int:pk>/editar/", views_clinico.EventoUpdateView.as_view(), name="evento_editar"),
    path(
        "<uuid:legajo_id>/inscribir-actividad/",
        views_operativa.InscribirActividadView.as_view(),
        name="inscribir_actividad",
    ),
    path(
        "<uuid:legajo_id>/actividades-inscrito/",
        views_operativa.ActividadesInscritoListView.as_view(),
        name="actividades_inscrito",
    ),
    path("<uuid:pk>/", views_clinico.LegajoDetailView.as_view(), name="detalle"),
    path("<uuid:pk>/cerrar/", views_clinico.LegajoCerrarView.as_view(), name="cerrar"),
    path("<uuid:pk>/reabrir/", views_clinico.LegajoReabrirView.as_view(), name="reabrir"),
    path(
        "<uuid:pk>/cambiar-responsable/",
        views_clinico.CambiarResponsableView.as_view(),
        name="cambiar_responsable",
    ),
    path("reportes/", views_clinico.ReportesView.as_view(), name="reportes"),
    path("exportar-csv/", views_clinico.ExportarCSVView.as_view(), name="exportar_csv"),
    path(
        "dispositivo/<int:dispositivo_id>/derivaciones/",
        views_clinico.DispositivoDerivacionesView.as_view(),
        name="dispositivo_derivaciones",
    ),
    path("cerrar-alerta/", views_clinico.CerrarAlertaEventoView.as_view(), name="cerrar_alerta_evento"),
    path("dashboard-contactos/", views_contactos_panel.dashboard_contactos_simple, name="dashboard_contactos"),
    path("dashboard-contactos/completo/", view_dashboard_contactos_completo, name="dashboard_contactos_completo"),
    path("dashboard-contactos/api/metricas/", view_metricas_contactos_api, name="metricas_contactos_api"),
    path("dashboard-contactos/api/metricas-red/", view_metricas_red_contactos_api, name="metricas_red_contactos_api"),
    path("dashboard-contactos/exportar/", view_exportar_reporte_contactos, name="exportar_reporte_contactos"),
    path("derivaciones-ciudadano/<int:derivacion_id>/aceptar/", views_derivacion_programa.aceptar_derivacion_ciudadano, name="derivacion_ciudadano_aceptar"),
    path("derivaciones-ciudadano/<int:derivacion_id>/rechazar/", views_derivacion_programa.rechazar_derivacion_ciudadano, name="derivacion_ciudadano_rechazar"),
    path("test-contactos/", views_simple.dashboard_contactos_simple, name="test_contactos"),
    path("test-api/", views_simple.test_api, name="test_api"),
    path(
        "<uuid:legajo_id>/historial-contactos/",
        views_contactos_panel.historial_contactos_simple,
        name="historial_contactos",
    ),
    path("<uuid:legajo_id>/red-contactos/", views_contactos_panel.red_contactos_simple, name="red_contactos"),
    path(
        "ciudadanos/<int:ciudadano_id>/actividades/",
        views_contactos_api.actividades_ciudadano_api,
        name="actividades_ciudadano",
    ),
    path("<uuid:legajo_id>/subir-archivos/", views_contactos_api.subir_archivos_legajo, name="subir_archivos"),
    path("<uuid:legajo_id>/archivos/", views_contactos_api.archivos_legajo_api, name="archivos_legajo"),
    path(
        "ciudadanos/<int:ciudadano_id>/archivos/",
        views_contactos_api.archivos_ciudadano_api,
        name="archivos_ciudadano",
    ),
    path(
        "ciudadanos/<int:ciudadano_id>/subir-archivos/",
        views_contactos_api.subir_archivos_ciudadano,
        name="subir_archivos_ciudadano",
    ),
    path("archivos/<int:archivo_id>/eliminar/", views_contactos_api.eliminar_archivo, name="eliminar_archivo"),
    path(
        "ciudadanos/<int:ciudadano_id>/alertas/",
        views_contactos_api.alertas_ciudadano_api,
        name="alertas_ciudadano",
    ),
    path("alertas/<int:alerta_id>/cerrar/", views_contactos_api.cerrar_alerta_api, name="cerrar_alerta_ciudadano"),
    path(
        "ciudadanos/<int:pk>/cursos-actividades/",
        views_cursos.cursos_actividades_ciudadano,
        name="cursos_actividades_ciudadano",
    ),
    path(
        "ciudadanos/<int:ciudadano_id>/timeline/",
        views_contactos_api.timeline_ciudadano_api,
        name="timeline_ciudadano",
    ),
    path(
        "ciudadanos/<int:ciudadano_id>/prediccion-riesgo/",
        views_contactos_api.prediccion_riesgo_api,
        name="prediccion_riesgo",
    ),
    path("<uuid:legajo_id>/evolucion/", views_contactos_api.evolucion_legajo_api, name="evolucion_legajo"),
    path("alertas/", views_alertas.alertas_dashboard, name="alertas_dashboard"),
    path("alertas/<int:alerta_id>/cerrar-ajax/", views_alertas.cerrar_alerta_ajax, name="cerrar_alerta_ajax"),
    path("alertas/count/", views_alertas.alertas_count_ajax, name="alertas_count_ajax"),
    path("alertas/preview/", views_alertas.alertas_preview_ajax, name="alertas_preview_ajax"),
    path("alertas/debug/", views_alertas.debug_alertas, name="debug_alertas"),
    path("alertas/test/", views_alertas.test_alertas_page, name="test_alertas"),
    path("instituciones/", views_operativa.InstitucionListView.as_view(), name="instituciones"),
    path("instituciones/crear/", views_operativa.InstitucionCreateView.as_view(), name="institucion_crear"),
    path("instituciones/<int:pk>/editar/", views_operativa.InstitucionUpdateView.as_view(), name="institucion_editar"),
    path("instituciones/<int:pk>/eliminar/", views_operativa.InstitucionDeleteView.as_view(), name="institucion_eliminar"),
    path(
        "legajos-institucionales/",
        views_operativa.LegajoInstitucionalListView.as_view(),
        name="legajos_institucionales",
    ),
    path(
        "legajos-institucionales/crear/",
        views_operativa.LegajoInstitucionalCreateView.as_view(),
        name="legajo_institucional_crear",
    ),
    path(
        "legajos-institucionales/<int:pk>/",
        views_operativa.LegajoInstitucionalDetailView.as_view(),
        name="legajo_institucional_detalle",
    ),
    path(
        "legajos-institucionales/<int:pk>/editar/",
        views_operativa.LegajoInstitucionalUpdateView.as_view(),
        name="legajo_institucional_editar",
    ),
]
