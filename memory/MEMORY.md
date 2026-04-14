
# MEMORY

## Identidad real del repo

- El repositorio activo es `SistemSo`, no `akuna_calc`.
- Apps principales: `core`, `legajos`, `portal`, `turnos`, `conversaciones`, `configuracion`, `users`, `dashboard`, `tramites`, `healthcheck`.

## Estado relevante 2026-03-13

- Se completó el primer slice del refactor DX interno.
- Slice implementado: `users`, `portal` institucional, `turnos`, con soporte en `core`.
- Patrón validado: selectors para lectura, services para orquestación, views más delgadas, formularios sin persistencia pesada.
- Se completó también el segundo slice sobre `configuracion`, enfocado en instituciones y actividades.
- `configuracion` ahora tiene `selectors_instituciones.py`, `services_actividades.py` y forms explícitos para editar inscriptos, actividades y staff.
- Se completó el tercer slice sobre `legajos`, enfocado en ciudadanos y admisión.
- `legajos` ahora tiene `selectors_ciudadanos.py`, `services_ciudadanos.py` y `services_admision.py` para RENAPER, detalle de ciudadano y wizard de admisión.
- Se completó el cuarto slice sobre `legajos`, enfocado en flujo clínico base.
- `legajos` ahora suma `selectors_legajos.py` y `services_legajos.py` para evaluación, planes, seguimientos, derivaciones y cierre/reapertura.
- Se completó el quinto slice sobre `legajos`, enfocado en eventos críticos, reportes, exportación y cambio de responsable.
- Se corrigieron templates clínicos que todavía dependían de campos inexistentes del modelo actual.
- Se completó el sexto slice sobre `legajos`, enfocado en modularización física de views.
- `legajos/views.py` ahora funciona como fachada compatible y el código de ciudadanía/admisión y clínica vive en módulos separados.
- Se completó el séptimo slice sobre `legajos`, enfocado en terminar la modularización física de views.
- `legajos/views.py` quedó como fachada pura y la operativa institucional/actividades vive en `legajos/views_operativa.py`.
- Se completó el octavo slice sobre `conversaciones`, enfocado en modularización del chat.
- `conversaciones/views.py` quedó como fachada compatible y el módulo ahora usa `views_public.py`, `views_backoffice.py`, `selectors_conversaciones.py`, `services_chat.py` y `forms_chat.py`.
- Se completó el noveno slice sobre `conversaciones`, enfocado en la API auxiliar.
- `conversaciones/api_views.py` y `api_extra.py` ya reutilizan selectors/services en lugar de repetir lógica inline.
- Se completó el décimo slice sobre `configuracion`, enfocado en modularización física.
- `configuracion/views.py` quedó como fachada compatible y la app ahora reparte geografía, institucional y actividades en módulos separados.
- Se completó el undécimo slice sobre namespaces.
- `users`, `core` y `healthcheck` ya tienen `app_name` y `config/urls.py` expone includes namespaced en paralelo a los legacy.
- Se completó el duodécimo slice sobre migración inicial de consumidores.
- Templates internos ya usan `core:*` y `users:*` en varios puntos no ambiguos; autenticación quedó pendiente aparte.
- Se completó el decimotercer slice sobre `chatbot`.
- `chatbot/views.py` quedó como fachada compatible y el módulo ahora usa forms/selectors/services y vistas separadas para superficie pública y admin.
- Se completó el decimocuarto slice sobre `chatbot`.
- El módulo ya alinea rutas/rendered URLs, shape JSON del chat y CSRF en sus endpoints principales.
- Se completó el decimoquinto slice sobre `conversaciones`.
- El chat ciudadano y el detalle de operador ya consumen URLs renderizadas por Django, la evaluación volvió a la superficie pública real y los POST JSON principales del módulo ya no usan `@csrf_exempt`.
- Se completó el decimosexto slice sobre `conversaciones`.
- La lista en vivo ya no carga dos veces `conversaciones_lista_ws.js`, el runtime WebSocket es idempotente y toma URLs operativas desde el DOM renderizado.
- Se completó el decimoséptimo slice sobre `conversaciones`.
- Los scripts globales y consumidores cross-app del dominio ya usan configuración renderizada por Django en lugar de rutas hardcodeadas.
- Se completó el decimoctavo slice sobre `portal`.
- Las consultas ciudadanas ahora viven en `views_ciudadano_consultas.py`, `selectors_ciudadano.py` y `services_consultas.py`, con forms explícitos para nueva consulta y envío de mensaje.
- Se completó el decimonoveno slice sobre `portal`.
- Los turnos ciudadanos ahora viven en `views_ciudadano_turnos.py`, `selectors_turnos_ciudadano.py` y `services_turnos_ciudadano.py`, con form explícito para confirmar el turno.
- Se completó el vigésimo slice sobre `portal`.
- La autenticación y el registro ciudadano ahora viven en `views_ciudadano_auth.py` y `services_ciudadano_auth.py`, con tests de flujo de alta y vinculación.
- Se completó el vigésimo primer slice sobre `portal`.
- Perfil, programas y mis datos ahora viven en `views_ciudadano_perfil.py`, `selectors_ciudadano_perfil.py` y `services_ciudadano_perfil.py`.
- Se completó el vigésimo segundo slice sobre `ÑACHEC`.
- Prestaciones, cierre/reapertura y dashboard ya viven en módulos propios y `views_nachec.py` quedó parcialmente como fachada compatible.
- Se completó el vigésimo tercer slice sobre `ÑACHEC`.
- Evaluación profesional y activación de plan ahora viven en `views_nachec_decisiones.py`.
- Se completó el vigésimo cuarto slice sobre `ÑACHEC`.
- La operación territorial restante ahora vive en `views_nachec_operacion.py` y `views_nachec.py` quedó como fachada pura.
- Se completó el vigésimo quinto slice sobre `legajos`.
- `legajos/forms.py` quedó como fachada y el módulo ahora separa ciudadanía, clínica y operativa en archivos distintos.
- Se completó el vigésimo sexto slice sobre `turnos`.
- El backoffice ahora se reparte en módulos dedicados, con mixins de permisos reutilizables y CBVs para el CRUD repetible.
- Se completó el vigésimo séptimo slice sobre `contactos`.
- El módulo legacy ahora usa selectors para lectura compuesta, un service de adjuntos y una fachada compatible para no romper URLs/imports.
- Se completó el vigésimo octavo slice sobre consumers transversales de rutas.
- `users:logout`, `chatbot:send_message` y `conversaciones:detalle` ya están consumidos desde namespaces/config renderizada en los puntos más visibles.
- Se completó el vigésimo noveno slice sobre `legajos/urls.py`.
- El conflicto nominal de `cerrar_alerta` quedó resuelto con names explícitos por dominio.
- Se completó el trigésimo slice sobre `users`.
- El service del listado de usuarios ya expone reverses y `url_name` namespaced.
- Se completó el trigésimo primer slice sobre `turnos` y `users`.
- Ambas apps ahora agrupan implementación en paquetes reales de `views`, `services` y `selectors`; `users` también separa `signals` en paquete propio.
- La compatibilidad se preserva con wrappers en los módulos legacy, lo que deja preparada la misma estrategia para futuras apps.
- Se completó el trigésimo segundo slice sobre `chatbot`.
- `chatbot` ahora también agrupa `views`, `forms`, `services` y `selectors` en paquetes reales, con wrappers legacy y preservando exports usados por tests.
- Se completó el trigésimo tercer slice sobre `configuracion`.
- `configuracion` ahora agrupa `views`, `forms`, `services` y `selectors` en paquetes reales, reutilizando la modularización por dominio ya existente.
- Se completó el trigésimo cuarto slice sobre `portal`.
- `portal` ahora agrupa `views`, `forms`, `services` y `selectors` en paquetes reales y sus tests dejaron de parchear wrappers legacy.
- Se completó el trigésimo quinto slice sobre `conversaciones`.
- `conversaciones` ahora agrupa `views`, `forms`, `services`, `selectors` y `signals` en paquetes reales, y `apps.py` ya no tiene el bug estructural de doble `ready()`.
- Se completó el trigésimo sexto slice sobre `core`.
- `core` ahora agrupa `views`, `forms` y `selectors` del flujo principal en paquetes reales; la auditoría pesada y los signals quedaron deliberadamente fuera de este corte.
- Se completó el trigésimo séptimo slice sobre `legajos`.
- `legajos` ahora agrupa `services` y `selectors` reales para ciudadanía, admisión, legajos, contactos y solapas, preservando wrappers legacy compatibles.
- El siguiente paso razonable dentro de `legajos` ya no es packaging masivo: conviene seguir por subdominio sobre `views` o `signals`, empezando por la superficie con menor wiring sensible.
- Se completó el trigésimo octavo slice sobre `legajos`.
- `legajos` ahora también agrupa `forms` reales por dominio, con wrappers legacy compatibles.
- El siguiente corte seguro dentro de la app pasa a ser selectivo sobre `views`, empezando por la superficie menos sensible y evitando todavía una migración masiva de signals.
- Se completó el trigésimo noveno slice sobre `legajos`.
- El bloque auxiliar de contactos y dashboards simples ahora vive en `legajos/views/`, con wrappers legacy compatibles.
- El siguiente corte seguro sigue siendo selectivo sobre `views`, pero ya más cerca de zonas sensibles como `programas`, `operativa` o `institucional`.
- Se completó el cuadragésimo slice sobre `legajos`.
- Alertas, cursos, derivación simple, API de derivaciones y acompañamiento ahora viven también en `legajos/views/`, con wrappers legacy compatibles.
- El siguiente corte ya deja de ser tan barato: lo pendiente entra en `programas`, `operativa`, `institucional`, clínica y `ÑACHEC`.
- Se completó el cuadragésimo primer slice sobre `legajos`.
- `views_operativa.py` ahora vive dentro de `legajos/views/`, con wrapper legacy compatible.
- A partir de acá, lo pendiente en `legajos` ya es la superficie más sensible del dominio; seguir en automático sin mejor validación funcional deja de ser razonable.
- Se completó el cuadragésimo segundo slice sobre `legajos`.
- `views_programas.py` y `views_solapas.py` ahora viven dentro de `legajos/views/`, con wrappers legacy compatibles.
- Lo pendiente en `legajos` quedó concentrado en `views_derivacion_programa.py`, `views_institucional.py`, `views_clinico.py` y `views_nachec_*`, que ya son bloques de dominio sensible.
- Se completó el cuadragésimo tercer slice sobre `legajos`.
- `views_derivacion_programa.py` ya no concentra el workflow sensible: aceptación, rechazo y branch `ÑACHEC` ahora viven en `services/derivaciones_programa.py`.
- El siguiente paso razonable es mover físicamente esa view al paquete `legajos/views/`; después de eso, el bloqueo fuerte vuelve a estar en `institucional`, clínica y `ÑACHEC`.
- Se completó el cuadragésimo cuarto slice sobre `legajos`.
- `views_derivacion_programa.py` ahora vive dentro de `legajos/views/`, con wrapper legacy compatible.
- El siguiente bloqueo fuerte ya quedó claramente en `views_institucional.py`, `views_clinico.py` y `views_nachec_*`.
- Se completó el cuadragésimo quinto slice sobre `legajos`.
- `views_institucional.py` ahora vive dentro de `legajos/views/`, con wrapper legacy compatible.
- El siguiente frente razonable pasó a ser `views_clinico.py`; después de eso, casi todo lo que queda será la familia `views_nachec_*`.
- Se completó el cuadragésimo sexto slice sobre `legajos`.
- `views_clinico.py` ahora vive dentro de `legajos/views/`, con wrapper legacy compatible.
- Lo pendiente en `legajos` ya quedó esencialmente concentrado en la familia `views_nachec_*`.
- Se completó el cuadragésimo séptimo slice sobre `legajos`.
- La familia `views_nachec_*` ahora vive dentro de `legajos/views/`, con wrappers legacy compatibles.
- El packaging estructural de `legajos` quedó prácticamente completo; lo siguiente ya no es cartografía sino deuda funcional y de wiring más fina.
- Se completó el cuadragésimo octavo slice sobre `legajos`.
- La familia restante de servicios ahora vive dentro de `legajos/services/`, con wrappers legacy compatibles y consumidores internos alineados al paquete nuevo.
- El siguiente frente estructural natural pasó a ser `signals`, ya con una API de servicios más estable debajo.
- Se completó el cuadragésimo noveno slice sobre `legajos`.
- La familia de señales ahora vive dentro de `legajos/signals/`, con `ready()` explícito hacia el paquete nuevo y smoke tests de exports.
- El packaging estructural de `legajos` quedó prácticamente agotado; lo siguiente ya es deuda funcional o de contrato.
- Se completó el quincuagésimo slice sobre apps chicas.
- `dashboard`, `tramites` y `healthcheck` ahora también usan paquetes reales de `views`, y `dashboard` dejó explícito su paquete de `signals`.
- El packaging repo-wide quedó casi agotado; los siguientes pasos con valor real pasan a ser funcionales o de contrato.
- Se completó el quincuagésimo primer slice sobre `core`.
- Auditoría, performance y señales de `core` ahora viven dentro de `core/views/` y `core/signals/`, con `ready()` explícito y wrappers legacy.
- El packaging repo-wide quedó prácticamente agotado; lo siguiente ya no es estructural barato.
- Se completó el quincuagésimo segundo slice sobre `api_views` chicas.
- `dashboard`, `users` y `chatbot` ahora también exponen sus APIs desde paquetes reales.
- Lo pendiente ya quedó mayormente en APIs más acopladas (`core`, `conversaciones`, `legajos`) o en deuda funcional, no en packaging trivial.
- Se completó el quincuagésimo tercer slice sobre `api_views` compartidas.
- `core` y `conversaciones` ahora también exponen sus APIs desde paquetes reales sin tocar `api_urls.py`.
- Lo pendiente ya quedó esencialmente en `legajos/api_views*` o en deuda funcional, no en packaging barato.
- Se completó el quincuagésimo cuarto slice sobre `legajos`.
- `legajos` ahora también expone sus APIs desde `legajos/api_views/`, incluyendo la API de contactos.
- El packaging estructural repo-wide quedó prácticamente agotado; lo siguiente ya no es un refactor físico barato.
- Se completó el quincuagésimo quinto slice sobre `ÑACHEC`.
- `ServicioOperacionNachec` ahora concentra validación inicial, envío a asignación y asignación territorial.
- El siguiente frente ya no es estructural: queda el bloque de relevamiento, scoring y evidencias en `nachec_operacion`.
- Se completó el quincuagésimo sexto slice sobre `ÑACHEC`.
- `ServicioOperacionNachec` ahora también concentra reasignación territorial e inicio de relevamiento.
- El siguiente frente sigue estando en el cierre de relevamiento, scoring y evidencias, que ya no es un corte barato ni de bajo riesgo.
- Se completó el quincuagésimo séptimo slice sobre packaging residual.
- `users/forms.py`, `turnos/forms.py` y `core/services_auditoria.py` ya quedaron absorbidos por carpetas reales.
- La deuda estructural repo-wide quedó prácticamente cerrada; lo pendiente es mayormente funcional, de wrappers legacy o de validación runtime.
- Se completó el quincuagésimo octavo slice sobre `legajos`.
- `legajos` dejó de depender de wrappers legacy internos y ahora consume solo sus paquetes reales de `views`, `forms`, `services`, `selectors` y `signals`.
- La cartografía física final del repositorio quedó alineada casi por completo; el riesgo pendiente ya es más de runtime/contrato que de estructura.

## Estado funcional 2026-03-19

- US-022 completado: inscripción de ciudadanos a actividades desde backoffice (por DNI) y portal ciudadano.
- `InscriptoActividad` ya tiene `codigo_inscripcion` y `inscrito_por`; sin `unique_together` (reinscripciones históricas permitidas).
- `inscribir_ciudadano_a_actividad` es el service central — usar siempre este, nunca crear `InscriptoActividad` directo.
- Bug de cupo=0 corregido en `actividad_detail.html` y en `aceptar_derivacion` (ya no usa `get_or_create`).
- Próximo candidato: US-023 (clases y asistencia) o US-008 (ficha ciudadana completa).

## Estado funcional 2026-03-15

- US-012 completado: flujo de derivación e inscripción de ciudadanos a programas usando `DerivacionCiudadano`.
- `DerivacionPrograma` queda como tabla legacy (sin UI activa), solo usada por el flujo Ñachec.
- `puede_operar_programa` corregido: ahora verifica grupo `programaOperar`, responsable local y `CoordinadorPrograma`. Antes siempre retornaba False para no-superusuarios.
- El signal `iniciar_flujo_inscripcion` en `legajos/signals/programas.py` inicia el FlowRuntime automáticamente al crear `InscripcionPrograma`. El service no lo llama directamente.
- Siguiente US candidata: US-008/009 (hub ciudadano), US-020 (tipo acceso actividades), US-022 (inscripción a actividades).

## Próxima etapa sugerida

- El siguiente hotspot real pasó a ser el bloque territorial restante de `ÑACHEC`: validación, asignación, relevamiento y evidencias.
- El siguiente hotspot real pasó a ser decidir entre profundizar `ÑACHEC` con services/selectors propios o atacar la deuda transversal restante de auth namespaces y `turnos` legacy.
- El siguiente hotspot real pasó a ser `turnos/views_backoffice.py` o `legajos/views_simple_contactos.py`, porque ya no queda retorno alto inmediato en seguir partiendo `ÑACHEC`.
- El siguiente hotspot real pasó a ser `legajos/views_simple_contactos.py` o la deuda transversal remanente de namespaces/auth.
- El siguiente hotspot real pasó a ser la deuda transversal remanente de namespaces/auth y algunos hardcodes legacy de rutas, porque los grandes monolitos internos ya bajaron mucho.
- El siguiente hotspot real pasó a ser la limpieza de `legajos/urls.py`, pero ahí ya hay riesgo alto por names duplicados y consumidores legacy sin cobertura suficiente.
- El siguiente hotspot real ya no es tan claro: queda sobre todo deuda de reordenamiento profundo de `legajos/urls.py` y algunos consumidores legacy con cobertura insuficiente.
- El siguiente hotspot real ya entra en rendimientos decrecientes: quedan aliases legacy y reordenamientos más profundos de URLs que exigen mejor cobertura funcional para no romper contrato.
- En paralelo, sigue pendiente definir una política única de responsables de legajo y evaluar si conviene separar `legajos` por apps en una etapa posterior.

# MEMORY.md — Contexto rápido del proyecto SistemSo

> Índice de memorias persistentes. Cargado automáticamente en cada conversación.
> No escribir contenido aquí — solo punteros a archivos de memoria.

## Memorias activas

- [feedback_respuestas_cortas.md](feedback_respuestas_cortas.md) — El usuario prefiere respuestas directas y concisas, sin preamble
- [project_estado_turnera.md](project_estado_turnera.md) — Estado del análisis del sistema de turnos (sesión 2026-03-11)
- [project_errores_documentados.md](project_errores_documentados.md) — Errores abiertos documentados en docs/errores/

## Documentos clave del proyecto

| Archivo | Para qué sirve |
|---------|---------------|
| `docs/team/contexto-funcional.md` | Reglas de negocio, actores, preguntas abiertas, glosario |
| `docs/team/backlog.md` | User Stories pendientes con orden de dependencia |
| `docs/team/ideas.md` | Ideas sin refinar, preguntas abiertas, deudas técnicas |
| `docs/team/arquitectura.md` | Principios, decisiones técnicas, mapa de apps |
| `docs/team/decisions.md` | ADRs — decisiones técnicas tomadas |
| `docs/errores/` | Bugs abiertos detectados en análisis |
| `docs/requerimientos/` | Requerimientos formales pendientes de implementar |
| `docs/funcionalidades/_index.md` | Índice de todas las funcionalidades documentadas |
