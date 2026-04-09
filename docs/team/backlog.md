# Product Backlog — SistemSo

> Actualizado: 2026-03-12 (sesión 6 — /definir derivacion-e-inscripcion)

## Leyenda
- 🟡 Pendiente
- 🔵 En sprint
- ✅ Completado
- ❌ Descartado

## Features pendientes

| ID | User Story | Complejidad | Notas |
|----|-----------|-------------|-------|
| US-005 | Como usuario con rol `programaConfigurar` quiero configurar un programa mediante un wizard (datos básicos, jerarquía, naturaleza, capacidades activables) para poder dar de alta programas correctamente tipificados | Grande ✅ | Implementado 2026-03-15. Ver `docs/funcionalidades/programas-sociales/v1.1_wizard-configuracion-programa.md` |
| US-006 | Como desarrollador quiero un motor de flujos backend (app `flujos/`) con modelos, runtime y tipos de nodo para que los programas puedan tener flujos configurables | Grande ✅ | Implementado 2026-03-15. Ver `docs/funcionalidades/motor-flujos/v1.0_motor-flujos-backend.md` |
| US-007 | Como usuario con rol `programaConfigurar` quiero un editor visual de flujos para diseñar el flujo de un programa mediante drag & drop | Grande ✅ | Implementado 2026-03-15. Ver `docs/funcionalidades/editor-visual-flujos/v1.0_editor-visual-flujos.md` |
| US-008 | Como operador quiero que la ficha del ciudadano incluya situación habitacional, laboral, educativa, médica, documentación migratoria, notas y foto para tener toda la información social centralizada | Mediano ✅ | Implementado 2026-03-19. Ver `docs/funcionalidades/ficha-ciudadano/v1.0_perfil-social-ciudadano.md` |
| US-009 | Como operador quiero ver el hub del ciudadano con solapas estáticas y dinámicas con badge behavior para acceder a toda su información desde un solo lugar | Mediano 🟡 | Requiere US-008. Solapas dinámicas: Programas, Turnos, Instituciones, Conversaciones, Derivaciones, Alertas, Línea de tiempo |
| US-010 | Como administrador quiero gestionar los roles `ciudadanoVer`, `ciudadanoCrear` y `ciudadanoSensible` para controlar quién accede a qué información del ciudadano | Pequeño 🟡 | Incluye filtro por ámbito (institución vs. backoffice) |
| US-012 | Como operador quiero ingresar un ciudadano a un programa (via derivación o inscripción directa) e iniciar su flujo obligatorio para gestionar su proceso de admisión hasta el cierre | Grande ✅ | Implementado 2026-03-15. Ver `docs/funcionalidades/derivacion-inscripcion-programas/v1.0_derivacion-inscripcion-programas.md` |
| US-014 | Como usuario con rol `ConfiguracionPrograma` quiero configurar cupo máximo y lista de espera en un programa para controlar la capacidad de inscripciones simultáneas | Pequeño 🟡 | Campo `cupo_maximo` (opcional) y `tiene_lista_espera` en la config del programa. Incluir en US-005 (wizard) |
| US-015 | Como ciudadano quiero ver mis programas, inscribirme, solicitar turnos y chatear con un operador desde el portal | Grande 🟡 | Ver `docs/requerimientos/2026-03-12_portal-ciudadano-iteraciones-2-6.md`. Requiere US-009 + US-012 + R-001. |
| US-016 | Como organismo quiero que todas las acciones del sistema queden trazadas (quién hizo qué, cuándo y sobre qué entidad) para cumplir con los requisitos de auditoría estatal | Grande 🟡 | Ver `docs/requerimientos/2026-03-12_auditoria-transversal.md` |
| US-017 | Como operador quiero dar de baja a un ciudadano de un programa persistente registrando motivo y fecha para cerrar su caso formalmente | Pequeño ✅ | Implementado 2026-03-15. Ver `docs/funcionalidades/programas-sociales/v1.2_baja-ciudadano-programa.md` |
| US-019 | Como encargado de institución quiero tener un panel propio donde ver mi institución, su legajo, actividades y agenda de turnos | Mediano 🟡 | `EncargadoInstitucion` no tiene panel — solo ve el portal. Requiere diseño de superficie separada o sección en backoffice con acceso restringido. |
| US-020 | Como administrador quiero configurar el tipo de acceso de una actividad (libre o requiere programa) para controlar quién puede inscribirse | Pequeño ✅ | Implementado 2026-03-15. Ver `docs/funcionalidades/actividades-institucionales/v1.0_tipo-acceso-actividades.md` |
| US-025 | Como encargado de institución quiero crear y gestionar usuarios internos (administrativos y profesores) para delegar la operación diaria de la institución | Mediano 🟡 | Requiere US-019 (panel institución). AdministrativoInstitucion y ProfesorInstitucion como grupos Django nuevos. |
| US-026 | Como institución quiero solicitar la reactivación de mi institución rechazada para volver a operar, y como backoffice quiero poder iniciarla también | Pequeño 🟡 | Requiere US-019. Historial diferenciado como REACTIVACION. Notificación a la institución. |
| US-027 | Como administrador de programa quiero crear evaluaciones periódicas a instituciones asignadas a operadores territoriales para auditar su funcionamiento desde la app de campo | Grande 🟡 | Tarea territorial aplicada a institución → legajo. Requiere US-006 (motor de flujos) + /definir app-movil. |
| US-021 | Como desarrollador quiero unificar los dos modelos de derivación en uno solo que salga desde Ciudadano para eliminar la duplicación de lógica | Grande ✅ | Implementado 2026-03-15. Ver `docs/funcionalidades/instituciones/v1.2_unificacion-modelo-derivacion.md` |
| US-022 | Como operador quiero inscribir ciudadanos a actividades con validación de tipo de acceso, cupo y código de inscripción para gestionar el ingreso a cada actividad institucional | Mediano ✅ | Implementado 2026-03-19. Ver `docs/funcionalidades/actividades-institucionales/v1.1_inscripcion-ciudadanos.md` |
| US-023 | Como staff de una actividad quiero crear clases y registrar asistencia por clase para llevar el seguimiento de participación de cada ciudadano | Mediano ✅ | Implementado 2026-03-19. Ver `docs/funcionalidades/actividades-institucionales/v1.2_clases-y-asistencia.md` |
| US-024 | Como encargado quiero configurar lista de espera en una actividad con modo automático o manual para gestionar los cupos disponibles cuando se liberan | Pequeño 🟡 | Dos modos: auto (asigna al siguiente) y manual (operador elige). Requiere US-022. |

---

## Completadas

| US-022 | Inscripción de ciudadanos a actividades institucionales (backoffice + portal) | Mediano ✅ |



| ID | User Story | Complejidad |
|----|-----------|-------------|
| US-001 | Como operador quiero registrar y gestionar ciudadanos (alta via RENAPER o manual, edición, búsqueda) para poder abrirles legajos e inscribirlos en programas | Mediano ✅ |
| US-002 | Como profesional quiero gestionar el legajo de atención SEDRONAR de un ciudadano (evaluación inicial, plan de intervención, seguimientos, derivaciones, eventos críticos) | Grande ✅ |
| US-003 | Como operador quiero gestionar el sistema de turnos configurable (ConfiguracionTurnos, disponibilidades, agenda, bandeja de pendientes, aprobación/rechazo) | Grande ✅ |
| US-004-PREV | Como ciudadano quiero acceder al portal para ver mis programas, solicitar turnos y contactar un operador via chat | Grande ✅ |
| US-005-PREV | Como operador quiero gestionar conversaciones con ciudadanos en tiempo real via WebSocket | Mediano ✅ |
| US-011 | Como administrador quiero que todos los roles del sistema existan como grupos Django con nombres definitivos y los grupos legacy migrados | Pequeño ✅ |
| US-013 | Como operador quiero poder buscar un ciudadano por nombre o DNI de forma rápida para atender consultas telefónicas sin demoras | Pequeño ✅ |
| US-018 | Como administrador quiero que las vistas de instituciones estén protegidas por los roles `institucionVer` e `institucionAdministrar` para controlar el acceso al módulo | Pequeño ✅ |
| US-004 | Como usuario con rol `secretariaConfigurar` quiero gestionar el catálogo de Secretarías y Subsecretarías y vincular Programas a una Subsecretaría para organizar los programas dentro de la jerarquía organizacional | Mediano ✅ |
| US-005 | Como usuario con rol `programaConfigurar` quiero configurar un programa mediante un wizard (datos básicos, jerarquía, naturaleza, capacidades activables) para poder dar de alta programas correctamente tipificados | Grande ✅ |

---

## Pendiente de /definir antes de poder estimar

| Dominio | Por qué no tiene US todavía |
|---------|----------------------------|
| ~~Instituciones~~ | ~~Solo definidas a nivel flujo de aprobación~~ → **Resuelto 2026-03-12** — ver US-019, US-025, US-026, US-027 |
| ~~Actividades~~ | ~~Completamente indefinidas~~ → **Resuelto 2026-03-12** — ver US-022, US-023, US-024 |
| ~~Roles y permisos~~ | ~~Mapa completo del sistema sin cerrar~~ → **Resuelto 2026-03-09** — ver `docs/requerimientos/2026-03-09_roles-y-permisos.md` |
| ~~Derivación e inscripción~~ | ~~Flujo completo definido conceptualmente pero sin criterios de aceptación~~ → **Resuelto 2026-03-12** — ver US-012 |
| App móvil | Existe pero sin documentar — cómo se conecta, auth, usuarios propios |
| Alertas | Sistema general sin definir — qué las genera, quién las recibe, cómo se resuelven |

---

## Ideas sin refinar

_Acá van las ideas crudas antes de convertirlas en user stories._
