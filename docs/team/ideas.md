# Ideas y Visión del Producto — SistemSo

> Este documento captura ideas, mejoras futuras y visión de producto que no son requerimientos formales aún.
> No tienen estimación ni compromiso de implementación. Son insumo para sprint planning y roadmap.
> Actualizado: 2026-03-11

---

## Cómo usar este documento

- **Idea nueva** → agregar en la sección correspondiente con fecha y breve descripción
- **Idea que madura** → moverla al backlog como User Story con `/feature` o `/planificar`
- **Idea descartada** → tacharla con ~~texto~~ y agregar motivo entre paréntesis

---

## 🔔 Notificaciones y comunicación

| Idea | Origen | Fecha |
|------|--------|-------|
| Recordatorios automáticos 24hs antes de un turno (Celery task) | Análisis turnera | 2026-03-11 |
| Notificaciones push / WhatsApp además de email | Análisis turnera | 2026-03-11 |
| Notificación al ciudadano cuando es derivado a un programa | Preguntas abiertas | 2026-03-09 |
| Alertas internas al operador cuando un turno vence sin respuesta | Análisis sistema | 2026-03-11 |
| Alerta cuando una inscripción lleva X días sin avanzar en el flujo | Análisis sistema | 2026-03-11 |

---

## 📅 Turnos

| Idea | Origen | Fecha |
|------|--------|-------|
| Vista mensual de agenda (hoy solo hay vista diaria) | Análisis turnera | 2026-03-11 |
| Estadísticas de asistencia / ausentismo por configuración | Análisis turnera | 2026-03-11 |
| Reprogramación de turno (¿o solo cancelar + crear nuevo?) | Pregunta abierta | 2026-03-09 |
| Cancelación en cascada de turnos al desactivar una institución | Pregunta abierta | 2026-03-09 |
| ¿Existe un concepto de "guardia" o atención urgente fuera del sistema de turnos? | Pregunta abierta | 2026-03-09 |
| Bloqueo de agenda (feriados, días sin atención) por configuración | Análisis turnera | 2026-03-11 |
| Límite de turnos simultáneos por ciudadano en un mismo programa | Análisis turnera | 2026-03-11 |

---

## 👤 Ciudadanos y legajo

| Idea | Origen | Fecha |
|------|--------|-------|
| Exportación a PDF del legajo de atención | Análisis sistema | 2026-03-09 |
| Deduplicación de ciudadanos (en caso de registros duplicados históricos) | Análisis sistema | 2026-03-09 |
| ¿La foto del ciudadano requiere `ciudadanoSensible` o la ve cualquiera con `ciudadanoVer`? | Pregunta abierta | 2026-03-09 |
| ¿Qué muestra exactamente la solapa "Resumen" del hub ciudadano? | Pregunta abierta | 2026-03-09 |
| ¿El operador que marcó un campo como sensible puede también desmarcarlo? | Pregunta abierta | 2026-03-09 |
| Búsqueda rápida global con shortcut de teclado (estilo command palette) | Mejora UX | 2026-03-11 |

---

## 🏛️ Instituciones

| Idea | Origen | Fecha |
|------|--------|-------|
| ¿Qué gestiona internamente una institución? (pendiente /definir) | Análisis sistema | 2026-03-09 |
| Panel del encargado de institución: ver su agenda, ciudadanos atendidos, actividades | Análisis sistema | 2026-03-11 |
| Historial de cambios de estado de una institución (BORRADOR → ENVIADO → REVISION → APROBADO) | Análisis sistema | 2026-03-11 |

---

## 📋 Programas y flujos

| Idea | Origen | Fecha |
|------|--------|-------|
| Editor visual de flujos drag & drop (React — US-007) | Diseño sistema | 2026-03-09 |
| ¿Las actividades son parte de un programa o entidades independientes? | Pregunta abierta | 2026-03-09 |
| ¿La asignación de profesionales a actividades es uno o muchos? | Pregunta abierta | 2026-03-09 |
| ¿El toggle "requiere turno" lo activa solo `programaConfigurar` o también el operador? | Pregunta abierta | 2026-03-09 |
| Templates de flujo reutilizables (definir un flujo una vez y reusarlo en varios programas) | Visión producto | 2026-03-11 |
| Dashboard de inscripciones por programa: cuántos en cada paso del flujo | Visión producto | 2026-03-11 |

---

## 📱 App móvil (tareas territoriales)

| Idea | Origen | Fecha |
|------|--------|-------|
| Documentar API REST + autenticación de la app móvil (`/definir app-movil`) | Análisis sistema | 2026-03-09 |
| Gestión de usuarios propios de la app móvil (operadores de campo) | Análisis sistema | 2026-03-09 |
| Sincronización offline de formularios cuando no hay conexión | Visión producto | 2026-03-11 |

---

## 🔐 Seguridad y auditoría

| Idea | Origen | Fecha |
|------|--------|-------|
| Auditoría transversal: registrar cada acción del sistema (US-016) | Diseño sistema | 2026-03-09 |
| Log de acceso a campos sensibles del ciudadano | Análisis sistema | 2026-03-11 |
| 2FA para usuarios con roles sensibles (`ciudadanoSensible`, `usuarioAdministrar`) | Visión producto | 2026-03-11 |

---

## 📊 Reportes y métricas

| Idea | Origen | Fecha |
|------|--------|-------|
| Exportación a PDF / Excel de reportes | Análisis sistema | 2026-03-09 |
| Integración con sistema de expedientes municipales | Visión producto | 2026-03-09 |
| Dashboard de métricas por secretaría / subsecretaría | Visión producto | 2026-03-11 |
| Indicador de capacidad de cupo en tiempo real por programa | Análisis sistema | 2026-03-11 |

---

## 🛠️ Deudas técnicas conocidas

| Deuda | Descripción | Fecha detectada |
|-------|-------------|----------------|
| `RecursoTurnos` legacy | Modelo viejo que coexiste con `ConfiguracionTurnos`. El portal ciudadano usa solo el legacy. Migrar cuando US-004/005 estén listos. | 2026-03-11 |
| `LegajoAtencion` SEDRONAR-específico | Deuda planificada: migrar al motor de flujos en el futuro. Hoy es un modelo propio. | 2026-03-09 |
| Nombres de grupos Django desactualizados | `Administradores de Turnos`, `configurarSecretaria`, `ConfiguracionPrograma` — renombrar con US-011. | 2026-03-11 |
| `turnoOperar` sin aplicar en vistas | Las vistas operativas de turnos no verifican el rol correcto. Fix junto con US-011. | 2026-03-11 |
| `RecursoTurnos.tipo` NODO hardcodeado | `NODO` es un concepto SEDRONAR-específico mezclado en el modelo genérico. | 2026-03-11 |

---

## ❓ Preguntas abiertas sin responder

> Copadas desde `contexto-funcional.md` para tenerlas en un solo lugar visible.

- [ ] ¿Un turno puede reprogramarse o solo cancelarse y crear uno nuevo?
- [ ] ¿Qué pasa con los turnos si se desactiva una institución? ¿Se cancelan en cascada?
- [ ] ¿El ciudadano recibe notificación cuando es derivado a otro programa?
- [ ] ¿Existe un concepto de "guardia" o atención urgente fuera del sistema de turnos?
- [ ] ¿El operador que marca un campo de ciudadano como "sensible" puede también desmarcarlo?
- [ ] ¿La foto del ciudadano requiere `ciudadanoSensible` o la ve cualquiera con `ciudadanoVer`?
- [ ] ¿Qué muestra exactamente la solapa "Resumen" del hub ciudadano?
- [ ] ¿El toggle "requiere turno" en un programa persistente — lo activa solo `programaConfigurar` o también el operador?
- [x] ~~¿Las actividades son parte de un programa o son entidades independientes?~~ → Siempre de una institución. Tipo de acceso LIBRE o REQUIERE_PROGRAMA.
- [x] ~~¿La asignación de profesionales a actividades — es uno por actividad o muchos?~~ → Muchos (StaffActividad con rol_en_actividad)
