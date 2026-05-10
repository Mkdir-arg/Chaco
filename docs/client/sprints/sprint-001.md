# Sprint 001 — Gestión base de ciudadanos

**Estado:** 🟡 En progreso
**Período:** 12 de mayo → 23 de mayo de 2026
**Objetivo:** Implementar el flujo completo de ingreso y derivación de ciudadanos: desde el registro inicial hasta la derivación a un programa con trazabilidad en el legajo.

---

## Alcance del sprint

Este sprint cubre dos funcionalidades centrales del módulo de Legajos:

| # | Funcionalidad | Prioridad | Estado | Horas est. | Horas reales |
|---|---|---|---|---|---|
| 1 | [Registro de ciudadano](#registro-de-ciudadano) | Alta | ✅ Completado | 16 hs | 14 hs |
| 2 | [Derivación a programa](#derivacion-a-programa) | Alta | 🔄 En progreso | 20 hs | — |

**Total estimado:** 36 hs
**Avance:** 1 de 2 funcionalidades completadas

---

## Registro de ciudadano

Permite al operador registrar un ciudadano nuevo en el sistema, con verificación de duplicados y consulta automática a RENAPER para autocompletar datos.

### Tareas

| Tarea | Estado | Horas est. | Horas reales |
|---|---|---|---|
| Validación de DNI duplicado en el formulario | ✅ Completado | 3 hs | 2 hs |
| Integración con RENAPER y autocompletado | ✅ Completado | 5 hs | 5 hs |
| Formulario de registro manual (fallback) | ✅ Completado | 3 hs | 3 hs |
| Estado "pendiente de verificación" para legajos sin DNI | ✅ Completado | 2 hs | 2 hs |
| Auditoría de creación (quién y cuándo) | ✅ Completado | 1 hs | 1 hs |
| Tests y validación | ✅ Completado | 2 hs | 1 hs |

**Subtotal:** 16 hs estimadas / 14 hs reales

### Requerimientos

| ID | Descripción | Prioridad | Estado |
|---|---|---|---|
| RF-001-01 | El sistema verifica si el DNI ya existe antes de crear un legajo nuevo | Alta | ✅ |
| RF-001-02 | El sistema consulta RENAPER y autocompleta nombre, apellido y fecha de nacimiento | Alta | ✅ |
| RF-001-03 | Si RENAPER no responde, el sistema habilita el formulario manual sin bloquear el flujo | Alta | ✅ |
| RF-001-04 | El sistema permite registrar un ciudadano sin DNI, marcando el legajo como pendiente de verificación | Media | ✅ |
| RF-001-05 | El formulario valida el formato del DNI antes de consultar | Alta | ✅ |
| RF-001-06 | El sistema registra quién creó el legajo y en qué fecha | Alta | ✅ |
| RF-001-07 | El operador puede adjuntar una foto al momento del registro | Baja | ⏸ Postergado |

### Criterios de aceptación

- [x] Dado un operador con permisos, cuando ingresa un DNI existente, entonces el sistema muestra el legajo existente y no crea uno nuevo.
- [x] Dado un operador con permisos, cuando ingresa un DNI nuevo y RENAPER responde, entonces el sistema autocompleta los datos.
- [x] Dado un operador con permisos, cuando RENAPER no responde, entonces el sistema habilita el formulario manual.
- [x] Dado un operador con permisos, cuando registra sin DNI, entonces el legajo queda en estado "pendiente de verificación".
- [x] Dado un usuario sin permisos, cuando intenta acceder al formulario, entonces recibe un error 403.

---

## Derivación a programa {#derivacion-a-programa}

Permite al operador derivar un ciudadano a un programa social con flujo de aceptación/rechazo por parte del dispositivo receptor y trazabilidad completa en el legajo.

### Tareas

| Tarea | Estado | Horas est. | Horas reales |
|---|---|---|---|
| Formulario de derivación (programa, dispositivo, motivo) | 🔄 En progreso | 4 hs | — |
| Flujo de aceptación y rechazo por el receptor | ⏳ Pendiente | 6 hs | — |
| Notificación interna al receptor | ⏳ Pendiente | 3 hs | — |
| Bloqueo de derivación duplicada al mismo programa | ⏳ Pendiente | 2 hs | — |
| Historial de derivaciones en el legajo | ⏳ Pendiente | 3 hs | — |
| Anulación de derivación pendiente (admin) | ⏳ Pendiente | 1 hs | — |
| Vencimiento automático por plazo configurable | ⏳ Pendiente | 1 hs | — |

**Subtotal:** 20 hs estimadas / en curso

### Requerimientos

| ID | Descripción | Prioridad | Estado |
|---|---|---|---|
| RF-002-01 | El operador puede iniciar una derivación desde el legajo del ciudadano | Alta | 🔄 |
| RF-002-02 | El formulario incluye programa destino, dispositivo, motivo y observaciones | Alta | 🔄 |
| RF-002-03 | El sistema notifica al dispositivo receptor al crear la derivación | Alta | ⏳ |
| RF-002-04 | El receptor puede aceptar o rechazar con motivo obligatorio al rechazar | Alta | ⏳ |
| RF-002-05 | El sistema bloquea derivar a un ciudadano ya inscripto en el mismo programa | Alta | ⏳ |
| RF-002-06 | El legajo muestra el historial completo de derivaciones | Alta | ⏳ |
| RF-002-07 | El administrador puede anular una derivación en estado pendiente | Media | ⏳ |
| RF-002-08 | El sistema marca como vencida una derivación sin respuesta tras el plazo configurado | Media | ⏳ |

### Criterios de aceptación

- [ ] Dado un operador con permisos, cuando inicia una derivación, entonces el sistema la registra como "Pendiente" y notifica al receptor.
- [ ] Dado un operador receptor, cuando acepta, entonces el ciudadano queda inscripto y el estado cambia a "Aceptada".
- [ ] Dado un operador receptor, cuando rechaza sin motivo, entonces el sistema no permite enviar el formulario.
- [ ] Dado un ciudadano ya inscripto en un programa, cuando se intenta derivarlo al mismo programa, entonces el sistema bloquea la acción.
- [ ] Dado un administrador, cuando anula una derivación pendiente, entonces el estado cambia a "Anulada" y se notifica a ambos operadores.

---

## Qué quedó fuera de este sprint

| Funcionalidad | Motivo | ¿Próximo sprint? |
|---|---|---|
| Adjuntar foto al registro (RF-001-07) | Baja prioridad, no bloquea el flujo principal | Sí |
| Derivaciones entre instituciones | Requiere análisis funcional propio | A definir |
| Reportes de derivaciones | Requiere análisis funcional propio | A definir |
