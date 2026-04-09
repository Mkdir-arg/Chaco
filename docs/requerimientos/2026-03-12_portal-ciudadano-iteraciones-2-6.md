---
name: Portal ciudadano — iteraciones 2 a 6
description: Expansión del portal ciudadano para incluir programas, inscripciones, actividades, documentos, notificaciones y turnos via ConfiguracionTurnos.
type: requerimiento
---

# Portal ciudadano — iteraciones 2 a 6
> Estado: ABIERTO
> Fecha: 2026-03-12
> Prioridad: MEDIA
> Tipo: FEATURE

## Descripción

La iteración 1 del portal está implementada (auth, registro, perfil básico). Las iteraciones 2-6 completan la experiencia del ciudadano en el portal.

## Dependencias

- **US-008** Ficha ciudadano expandida
- **US-009** Hub ciudadano
- **US-012** Inscripción y derivación (para que el ciudadano vea sus programas)
- **US-022** Inscripción a actividades (para que el ciudadano vea sus actividades)
- **R-001** Portal turnos → ConfiguracionTurnos (para solicitar turnos del nuevo sistema)

## Iteraciones

### Iteración 2 — Programas e inscripciones
- El ciudadano ve sus programas activos e historial
- Ve el estado actual dentro de cada programa (paso del flujo)
- Ve sus derivaciones pendientes
- Si hay programas con inscripción LIBRE, puede inscribirse desde el portal
- Ve el código de inscripción al inscribirse

### Iteración 3 — Chat con operador
- El ciudadano puede iniciar una conversación desde el portal
- Ve el historial de conversaciones anteriores
- *(WebSocket ya implementado — integrar en el portal)*

### Iteración 4 — Documentos y actividades
- El ciudadano ve sus documentos adjuntos
- Ve sus actividades activas e historial (solapa Cursos y Actividades)
- Ve su porcentaje de asistencia por actividad
- Puede auto-desinscribirse de una actividad (pasa a ABANDONADO)

### Iteración 5 — Notificaciones
- El ciudadano ve notificaciones de eventos: turno confirmado, turno cancelado, derivación recibida, inscripción aceptada
- Las notificaciones quedan marcadas como leídas al verlas

### Iteración 6 — Turnos via ConfiguracionTurnos
- El ciudadano puede solicitar turno de un Programa con `tiene_turnos=True`
- El ciudadano puede solicitar turno de una Institución con `ConfiguracionTurnos` asignada
- El ciudadano puede solicitar turno de una Actividad con `ConfiguracionTurnos` asignada
- Los turnos quedan con `contexto_tipo` correcto (PROGRAMA / INSTITUCION / ACTIVIDAD)
- El flujo legacy de `RecursoTurnos` sigue funcionando sin romper

## Criterios de éxito

- [ ] El ciudadano ve sus programas activos y el estado actual en cada uno
- [ ] El ciudadano ve sus derivaciones pendientes
- [ ] El ciudadano puede inscribirse a programas LIBRES desde el portal
- [ ] El ciudadano puede iniciar y continuar conversaciones con operadores
- [ ] El ciudadano ve sus documentos adjuntos
- [ ] El ciudadano ve sus actividades con % de asistencia
- [ ] El ciudadano puede auto-desinscribirse de una actividad
- [ ] El ciudadano ve notificaciones de eventos relevantes
- [ ] El ciudadano puede solicitar turnos de programas e instituciones con ConfiguracionTurnos
