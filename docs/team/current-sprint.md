# Sprint Actual — SistemSo

> Estado: Sin sprint activo
> Inicio: —
> Fin: —

## Objetivo del sprint

_Se define en el sprint planning._

## Items del sprint

| ID | User Story | Estado | Notas |
|----|-----------|--------|-------|
| RM-002 | Como equipo de desarrollo quiero retirar el sistema de turnos del proyecto para simplificar el dominio activo y eliminar dependencias cruzadas obsoletas | ✅ Completado | Ejecutado el 2026-04-14 con limpieza de app, portal, modelos y migraciones históricas |
| DX-001 | Como equipo de desarrollo quiero estandarizar `users`, `portal` institucional y `turnos` con services/selectors/views delgadas para mejorar DX y testabilidad | ✅ Completado | Trabajo técnico ejecutado fuera de sprint formal el 2026-03-13 |
| DX-002 | Como equipo de desarrollo quiero refactorizar `configuracion` institucional y de actividades con selectors/services/forms explícitos para bajar acoplamiento y facilitar testing | ✅ Completado | Slice 2 ejecutado el 2026-03-13 sin cambios de modelo |
| DX-003 | Como equipo de desarrollo quiero refactorizar `legajos` en ciudadanos y admisión para ordenar RENAPER, sesión y consultas reutilizables | ✅ Completado | Slice 3 ejecutado el 2026-03-13 sin cambios de modelo |
| DX-004 | Como equipo de desarrollo quiero refactorizar el flujo clínico base de `legajos` para separar evaluación, planes, seguimientos y derivaciones en selectors/services/forms consistentes | ✅ Completado | Slice 4 ejecutado el 2026-03-13 sin cambios de modelo |
| DX-005 | Como equipo de desarrollo quiero cerrar el hotspot restante del legajo clínico en eventos, reportes, exportación y responsable para eliminar lógica y templates inconsistentes | ✅ Completado | Slice 5 ejecutado el 2026-03-13 sin cambios de modelo |
| DX-006 | Como equipo de desarrollo quiero separar físicamente `legajos/views.py` por dominios para que el módulo sea más navegable y mantenible sin romper compatibilidad | ✅ Completado | Slice 6 ejecutado el 2026-03-13 sin cambios de modelo ni URLs |
| DX-007 | Como equipo de desarrollo quiero completar la modularización de `legajos/views.py` dejando una fachada pura y moviendo la operativa institucional a un módulo propio | ✅ Completado | Slice 7 ejecutado el 2026-03-13 sin cambios de modelo, URLs ni templates |
| DX-008 | Como equipo de desarrollo quiero modularizar `conversaciones` con selectors, services y views separadas para bajar el acoplamiento del chat sin romper sus endpoints | ✅ Completado | Slice 8 ejecutado el 2026-03-13 manteniendo URLs y contrato AJAX/WebSocket |
| DX-009 | Como equipo de desarrollo quiero alinear la API auxiliar de `conversaciones` al patrón de selectors/services para eliminar queries y permisos inline duplicados | ✅ Completado | Slice 9 ejecutado el 2026-03-13 sin cambios de rutas ni modelos |
| DX-010 | Como equipo de desarrollo quiero separar físicamente `configuracion/views.py` por dominios para que la app siga el mismo patrón modular del resto del refactor | ✅ Completado | Slice 10 ejecutado el 2026-03-13 sin cambios de URLs, modelos ni templates |
| DX-011 | Como equipo de desarrollo quiero habilitar namespaces consistentes en `users`, `core` y `healthcheck` sin romper los names legacy mientras se migra el proyecto | ✅ Completado | Slice 11 ejecutado el 2026-03-13 con compatibilidad dual namespaced/legacy |
| DX-012 | Como equipo de desarrollo quiero migrar consumidores claros a `core:*` y `users:*` para empezar a retirar dependencia de names legacy | ✅ Completado | Slice 12 ejecutado el 2026-03-13 solo sobre templates con names no ambiguos |
| DX-013 | Como equipo de desarrollo quiero modularizar `chatbot` y validar payloads JSON para bajar acoplamiento entre chat público y administración | ✅ Completado | Slice 13 ejecutado el 2026-03-13 sin cambios de rutas ni modelos |
| DX-014 | Como equipo de desarrollo quiero corregir el contrato real frontend/backend de `chatbot` y endurecer CSRF en sus endpoints principales | ✅ Completado | Slice 14 ejecutado el 2026-03-13 alineando rutas, shape JSON y protección CSRF |
| DX-015 | Como equipo de desarrollo quiero corregir el contrato real de `conversaciones` y endurecer CSRF en sus endpoints JSON sin romper la UX actual | ✅ Completado | Slice 15 ejecutado el 2026-03-13 alineando evaluación pública, URLs renderizadas y protección CSRF |
| DX-016 | Como equipo de desarrollo quiero estabilizar el runtime de la lista en vivo de `conversaciones` para evitar doble suscripción y paths hardcodeados | ✅ Completado | Slice 16 ejecutado el 2026-03-13 alineando `conversaciones_lista_ws.js` con URLs renderizadas y guard de inicialización |
| DX-017 | Como equipo de desarrollo quiero cerrar los consumidores residuales de `conversaciones` fuera de su lista principal para reducir hardcodes cross-app | ✅ Completado | Slice 17 ejecutado el 2026-03-13 moviendo config de URLs a `base.html`, detalle operador y portal ciudadano |
| DX-018 | Como equipo de desarrollo quiero extraer consultas ciudadanas de `portal/views_ciudadano.py` a capas más claras para bajar acoplamiento y mejorar testabilidad | ✅ Completado | Slice 18 ejecutado el 2026-03-13 con forms, selectors y services dedicados |
| DX-019 | Como equipo de desarrollo quiero extraer turnos ciudadanos de `portal/views_ciudadano.py` a capas claras para aislar reservas, disponibilidad y validación | ✅ Completado | Slice 19 ejecutado el 2026-03-13 con forms, selectors, services y tests del flujo ciudadano de turnos |
| DX-020 | Como equipo de desarrollo quiero extraer auth y registro ciudadano de `portal/views_ciudadano.py` para separar sesión, throttling y alta por pasos | ✅ Completado | Slice 20 ejecutado el 2026-03-13 con service de auth/registro y tests de flujo |
| DX-021 | Como equipo de desarrollo quiero extraer perfil, programas y mis datos de `portal/views_ciudadano.py` para dejar el módulo como fachada compatible | ✅ Completado | Slice 21 ejecutado el 2026-03-13 con selectors/services de perfil y tests de ownership/cambio de email |
| DX-022 | Como equipo de desarrollo quiero reducir el hotspot principal de `ÑACHEC` separando prestaciones, cierre y dashboard en módulos propios | ✅ Completado | Slice 22 ejecutado el 2026-03-13 con fachada compatible en `views_nachec.py` y smoke test de exports |
| DX-023 | Como equipo de desarrollo quiero seguir partiendo `ÑACHEC` separando evaluación y activación de plan antes de tocar asignación y relevamiento | ✅ Completado | Slice 23 ejecutado el 2026-03-13 con `views_nachec_decisiones.py` y ampliación del smoke test |
| DX-024 | Como equipo de desarrollo quiero cerrar la modularización física de `ÑACHEC` separando la operación territorial restante en un módulo dedicado | ✅ Completado | Slice 24 ejecutado el 2026-03-13 con `views_nachec_operacion.py` y `views_nachec.py` como fachada pura |
| DX-025 | Como equipo de desarrollo quiero limpiar `legajos/forms.py` separándolo por dominio para alinear forms con las views ya modularizadas | ✅ Completado | Slice 25 ejecutado el 2026-03-13 con fachadas compatibles y smoke test de forms |
| DX-026 | Como equipo de desarrollo quiero modularizar el backoffice de `turnos` y usar CBVs donde el CRUD repetible ya está claro | ✅ Completado | Slice 26 ejecutado el 2026-03-13 con `views_backoffice.py` como fachada, mixins reutilizables y CRUD en CBVs |
| DX-027 | Como equipo de desarrollo quiero refactorizar el módulo legacy de contactos separando queries, archivos y panel para bajar acoplamiento y corregir inconsistencias con el modelo real | ✅ Completado | Slice 27 ejecutado el 2026-03-13 con selectors/services dedicados y fachada compatible |
| DX-028 | Como equipo de desarrollo quiero retirar hardcodes residuales y migrar consumidores transversales a namespaces estables | ✅ Completado | Slice 28 ejecutado el 2026-03-13 sobre logout, chatbot bubble, alertas y tests de namespaces |
| DX-029 | Como equipo de desarrollo quiero eliminar names duplicados en `legajos/urls.py` para que el routing sea predecible y más seguro de refactorizar | ✅ Completado | Slice 29 ejecutado el 2026-03-13 desambiguando `cerrar_alerta_evento` y `cerrar_alerta_ciudadano` |
| DX-030 | Como equipo de desarrollo quiero que los services de `users` publiquen URLs namespaced consistentes para evitar contrato legacy en tablas y acciones | ✅ Completado | Slice 30 ejecutado el 2026-03-13 corrigiendo reverses legacy y `usuario_borrar` |
| DX-031 | Como equipo de desarrollo quiero agrupar `turnos` y `users` en paquetes de views/services/selectors/signals para ordenar imports y preparar la siguiente etapa del refactor | ✅ Completado | Slice 31 ejecutado el 2026-03-13 con fachadas compatibles y smoke tests de exports |
| DX-032 | Como equipo de desarrollo quiero agrupar `chatbot` en paquetes reales para alinear la app con el packaging nuevo sin romper su contrato HTTP ni sus tests | ✅ Completado | Slice 32 ejecutado el 2026-03-13 con wrappers compatibles y smoke tests de exports |
| DX-033 | Como equipo de desarrollo quiero agrupar `configuracion` en paquetes reales para ordenar views/forms/services/selectors sin tocar su contrato funcional | ✅ Completado | Slice 33 ejecutado el 2026-03-13 con wrappers compatibles y smoke tests de exports |
| DX-034 | Como equipo de desarrollo quiero agrupar `portal` en paquetes reales sin romper sus flujos ciudadanos ni el registro institucional | ✅ Completado | Slice 34 ejecutado el 2026-03-13 con wrappers compatibles y tests de patch actualizados a paths reales |
| DX-035 | Como equipo de desarrollo quiero agrupar `conversaciones` en paquetes reales sin romper chat, runtime y registro de señales | ✅ Completado | Slice 35 ejecutado el 2026-03-13 con wrappers compatibles, tests ajustados y `ready()` unificado |
| DX-036 | Como equipo de desarrollo quiero agrupar `core` en paquetes reales donde el riesgo sea bajo para ordenar la base compartida del proyecto | ✅ Completado | Slice 36 ejecutado el 2026-03-13 sobre views/forms/selectors del flujo principal |
| DX-037 | Como equipo de desarrollo quiero agrupar `legajos` en paquetes reales de services/selectors antes de tocar wiring sensible de views y signals | ✅ Completado | Slice 37 ejecutado el 2026-03-13 con wrappers compatibles y smoke test de exports |
| DX-038 | Como equipo de desarrollo quiero agrupar `legajos` en un paquete real de forms para cerrar la capa de formularios antes de tocar views o signals | ✅ Completado | Slice 38 ejecutado el 2026-03-13 con wrappers compatibles y tests de fachada ampliados |
| DX-039 | Como equipo de desarrollo quiero agrupar en `legajos/views/` las views auxiliares de contactos y dashboards simples antes de mover bloques más sensibles | ✅ Completado | Slice 39 ejecutado el 2026-03-13 con wrappers compatibles y tests de fachada ampliados |
| DX-040 | Como equipo de desarrollo quiero seguir agrupando en `legajos/views/` las views de soporte de bajo riesgo antes de entrar en subdominios más sensibles | ✅ Completado | Slice 40 ejecutado el 2026-03-13 con wrappers compatibles y smoke test de exports |
| DX-041 | Como equipo de desarrollo quiero mover `views_operativa.py` al paquete nuevo de views antes de tocar módulos más sensibles de `legajos` | ✅ Completado | Slice 41 ejecutado el 2026-03-13 con wrapper compatible y smoke test de exports |
| DX-042 | Como equipo de desarrollo quiero mover `views_programas.py` y `views_solapas.py` al paquete nuevo antes de entrar en el núcleo más sensible de `legajos` | ✅ Completado | Slice 42 ejecutado el 2026-03-13 con wrappers compatibles y smoke tests de exports |
| DX-043 | Como equipo de desarrollo quiero sacar la lógica sensible de `views_derivacion_programa.py` a un service antes de modularizar físicamente ese borde con `ÑACHEC` | ✅ Completado | Slice 43 ejecutado el 2026-03-13 con service dedicado y tests del workflow |
| DX-044 | Como equipo de desarrollo quiero mover `views_derivacion_programa.py` al paquete nuevo de views una vez extraído su workflow sensible | ✅ Completado | Slice 44 ejecutado el 2026-03-13 con wrapper compatible y smoke test de exports |
| DX-045 | Como equipo de desarrollo quiero mover `views_institucional.py` al paquete nuevo sin cambiar su dominio interno todavía | ✅ Completado | Slice 45 ejecutado el 2026-03-13 con wrapper compatible y smoke test de exports |
| DX-046 | Como equipo de desarrollo quiero mover `views_clinico.py` al paquete nuevo manteniendo intacto su comportamiento actual | ✅ Completado | Slice 46 ejecutado el 2026-03-13 con wrapper compatible y smoke test de exports |
| DX-047 | Como equipo de desarrollo quiero cerrar el packaging de `ÑACHEC` moviendo su familia `views_nachec_*` al paquete nuevo sin tocar sus transiciones internas | ✅ Completado | Slice 47 ejecutado el 2026-03-13 con wrappers compatibles y smoke test de exports |
| DX-048 | Como equipo de desarrollo quiero cerrar el packaging restante de `services` en `legajos` antes de evaluar el wiring sensible de `signals` | ✅ Completado | Slice 48 ejecutado el 2026-03-13 con wrappers compatibles y migración de consumidores internos |
| DX-049 | Como equipo de desarrollo quiero agrupar `signals` de `legajos` en un paquete real manteniendo el wiring explícito desde `AppConfig` | ✅ Completado | Slice 49 ejecutado el 2026-03-13 con `ready()` explícito y smoke test de exports |
| DX-050 | Como equipo de desarrollo quiero alinear `dashboard`, `tramites` y `healthcheck` a la convención de packaging para cerrar las apps chicas que quedaban legacy | ✅ Completado | Slice 50 ejecutado el 2026-03-13 con views empaquetadas y smoke tests básicos |
| DX-051 | Como equipo de desarrollo quiero cerrar la deuda estructural pendiente de `core` agrupando auditoría, performance y señales en paquetes reales | ✅ Completado | Slice 51 ejecutado el 2026-03-13 con wrappers compatibles, `ready()` explícito y smoke tests ampliados |
| DX-052 | Como equipo de desarrollo quiero mover `api_views` de las apps chicas al mismo patrón de package para no dejar excepciones entre HTML y API | ✅ Completado | Slice 52 ejecutado el 2026-03-13 sobre `dashboard`, `users` y `chatbot` |
| DX-053 | Como equipo de desarrollo quiero mover `api_views` de `core` y `conversaciones` al mismo patrón de package sin tocar contratos HTTP | ✅ Completado | Slice 53 ejecutado el 2026-03-13 con compatibilidad desde `api_urls.py` y smoke tests ampliados |
| DX-054 | Como equipo de desarrollo quiero cerrar también `api_views` de `legajos` para agotar la deuda estructural repo-wide más obvia | ✅ Completado | Slice 54 ejecutado el 2026-03-13 con compatibilidad de routing DRF y smoke test ampliado |
| DX-055 | Como equipo de desarrollo quiero sacar a service layer el subflujo inicial de `nachec_operacion` para reducir lógica de negocio en views y corregir inconsistencias de tareas | ✅ Completado | Slice 55 ejecutado el 2026-03-14 con tests de service para validación, envío y asignación |
| DX-056 | Como equipo de desarrollo quiero extraer la reasignación territorial y el inicio de relevamiento de `nachec_operacion` para seguir adelgazando el flujo operativo más sensible | ✅ Completado | Slice 56 ejecutado el 2026-03-16 con service layer y tests de reasignación/inicio |
| DX-057 | Como equipo de desarrollo quiero cerrar las excepciones físicas más visibles de `forms` y `services` para dejar la cartografía repo-wide casi totalmente alineada a carpetas | ✅ Completado | Slice 57 ejecutado el 2026-03-16 con `users/forms`, `turnos/forms` y `core/services/auditoria` movidos a paquetes reales |
| DX-058 | Como equipo de desarrollo quiero retirar la capa legacy de compatibilidad de `legajos` para que la app dependa solo de sus paquetes reales | ✅ Completado | Slice 58 ejecutado el 2026-03-17 con imports, URLs y tests alineados al layout definitivo |

| DX-059 | Como equipo de desarrollo quiero simplificar el stack local Docker a `app + mysql + redis` con un solo comando y bootstrap idempotente | ✅ Completado | Slice 59 ejecutado el 2026-04-03 con `docker compose up` como flujo recomendado |
| US-012 | Derivación e inscripción de ciudadanos a programas — flujo completo con bandeja, aceptar/rechazar y creación de InscripcionPrograma | ✅ Completado | Implementado 2026-03-15 |
| US-017 | Baja de ciudadano de un programa persistente — registra motivo, cancela turnos y flujo activo | ✅ Completado | Implementado 2026-03-15 |
| US-020 | Tipo de acceso en actividades institucionales — LIBRE o REQUIERE_PROGRAMA con validación y selector anti-N+1 | ✅ Completado | Implementado 2026-03-15 |
| US-023 | Clases y registro de asistencia en actividades institucionales | ✅ Completado | Implementado 2026-03-19 |
| US-008 | Perfil social ampliado del ciudadano (foto, habitacional, laboral, educativo, médico, documentación migratoria) | ✅ Completado | Implementado 2026-03-19 |
| US-009 | Hub del Ciudadano — 11 solapas estáticas + solapas dinámicas por programa + badge behavior (alertas, derivaciones, turnos, conversaciones, legajos) | ✅ Completado | Implementado 2026-03-19 |

## Impedimentos

_Ninguno._

---

## Historial de sprints anteriores

Ver `docs/team/changelog.md` para el detalle de cada sprint.
