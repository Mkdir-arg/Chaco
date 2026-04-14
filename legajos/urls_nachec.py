"""
URLs para transiciones de estado Ñachec
"""

from django.urls import path

from .views import (
    activar_plan,
    adjuntar_evidencias,
    asignar_territorial,
    autosave_relevamiento,
    cancelar_prestacion,
    cerrar_caso,
    cerrar_caso_nachec,
    completar_tarea,
    completar_validacion,
    confirmar_entrega_prestacion,
    dashboard_nachec,
    enviar_a_asignacion,
    evaluar_caso,
    finalizar_relevamiento,
    formulario_relevamiento,
    iniciar_prestacion,
    iniciar_relevamiento,
    pasar_a_seguimiento,
    reasignar_territorial,
    reabrir_caso_nachec,
    reprogramar_prestacion,
    ver_tarea_validacion,
)

urlpatterns = [
    path("dashboard/", dashboard_nachec, name="nachec_dashboard"),
    path("tarea/<int:tarea_id>/completar/", completar_tarea, name="nachec_completar_tarea"),
    path("caso/<int:caso_id>/tarea-validacion/", ver_tarea_validacion, name="nachec_ver_tarea_validacion"),
    path("caso/<int:caso_id>/completar-validacion/", completar_validacion, name="nachec_completar_validacion"),
    path("caso/<int:caso_id>/enviar-asignacion/", enviar_a_asignacion, name="nachec_enviar_asignacion"),
    path("caso/<int:caso_id>/asignar-territorial/", asignar_territorial, name="nachec_asignar_territorial"),
    path("caso/<int:caso_id>/reasignar-territorial/", reasignar_territorial, name="nachec_reasignar_territorial"),
    path("caso/<int:caso_id>/iniciar-relevamiento/", iniciar_relevamiento, name="nachec_iniciar_relevamiento"),
    path("caso/<int:caso_id>/relevamiento/", formulario_relevamiento, name="nachec_formulario_relevamiento"),
    path("caso/<int:caso_id>/relevamiento/autosave/", autosave_relevamiento, name="nachec_autosave_relevamiento"),
    path("caso/<int:caso_id>/adjuntar-evidencias/", adjuntar_evidencias, name="nachec_adjuntar_evidencias"),
    path("caso/<int:caso_id>/finalizar-relevamiento/", finalizar_relevamiento, name="nachec_finalizar_relevamiento"),
    path("caso/<int:caso_id>/evaluar/", evaluar_caso, name="nachec_evaluar_caso"),
    path("caso/<int:caso_id>/activar-plan/", activar_plan, name="nachec_activar_plan"),
    path("caso/<int:caso_id>/pasar-seguimiento/", pasar_a_seguimiento, name="nachec_pasar_seguimiento"),
    path("caso/<int:caso_id>/cerrar/", cerrar_caso, name="nachec_cerrar_caso_legajo"),
    path("prestacion/<int:prestacion_id>/iniciar/", iniciar_prestacion, name="nachec_iniciar_prestacion"),
    path(
        "prestacion/<int:prestacion_id>/confirmar-entrega/",
        confirmar_entrega_prestacion,
        name="nachec_confirmar_entrega",
    ),
    path("prestacion/<int:prestacion_id>/reprogramar/", reprogramar_prestacion, name="nachec_reprogramar_prestacion"),
    path("prestacion/<int:prestacion_id>/cancelar/", cancelar_prestacion, name="nachec_cancelar_prestacion"),
    path("caso/<int:caso_id>/cerrar-caso/", cerrar_caso_nachec, name="nachec_cerrar_caso"),
    path("caso/<int:caso_id>/reabrir-caso/", reabrir_caso_nachec, name="nachec_reabrir_caso"),
]
