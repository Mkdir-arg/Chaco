---
name: Portal ciudadano — migrar flujo de turnos a ConfiguracionTurnos
description: El flujo de solicitud de turno del portal ciudadano usa RecursoTurnos (legacy). Debe migrarse para soportar ConfiguracionTurnos (nuevo sistema).
type: requerimiento
---

# Portal ciudadano — migrar flujo de turnos a ConfiguracionTurnos
> Estado: ABIERTO
> Fecha: 2026-03-11
> Prioridad: MEDIA
> Tipo: MEJORA

## Descripción

El flujo completo de solicitud de turno del portal ciudadano ya está implementado y funciona. Sin embargo, está construido **exclusivamente sobre el modelo legacy `RecursoTurnos`** y su `DisponibilidadTurnos`.

El nuevo sistema de turnos usa `ConfiguracionTurnos` + `DisponibilidadConfiguracion`, que es el que se vincula a Programas e Instituciones. El ciudadano hoy no puede pedir turno de un Programa o una Institución que use el nuevo sistema.

## Estado actual

- ✅ `ciudadano_mis_turnos` — funciona (muestra `TurnoCiudadano` independiente del origen)
- ✅ `ciudadano_solicitar_turno` — lista `RecursoTurnos` activos (legacy)
- ✅ `ciudadano_turno_calendario` — usa `get_calendario_mensual(recurso, ...)` (legacy)
- ✅ `ciudadano_turno_slots` — usa `get_slots_disponibles(recurso, ...)` (legacy)
- ✅ `ciudadano_confirmar_turno` — verifica `DisponibilidadTurnos` y crea turno con `recurso=recurso` (legacy)
- ❌ No soporta `ConfiguracionTurnos` como origen del turno

## Lo que hay que hacer

1. Unificar el punto de entrada: el ciudadano debe poder pedir turno de un **Programa**, una **Institución** o un **RecursoTurnos** genérico — todos usando su `ConfiguracionTurnos` asociada.
2. Adaptar `ciudadano_turno_calendario` y `ciudadano_turno_slots` para recibir una `ConfiguracionTurnos` en lugar de un `RecursoTurnos`.
3. Adaptar `ciudadano_confirmar_turno` para crear `TurnoCiudadano` con `configuracion=config` (en lugar de `recurso=recurso`) y setear correctamente `contexto_tipo` + `contexto_id`.
4. `ciudadano_mis_turnos` ya muestra `TurnoCiudadano` genéricamente — revisar que `nombre_entidad` funcione para ambos orígenes (property `nombre_entidad` ya existe en el modelo ✅).

## Dependencias

- Requiere que US-004 (ABM Secretarías/Subsecretarías) y US-005 (wizard programa) estén implementadas para que haya Programas con `ConfiguracionTurnos` asignada.
- El `RecursoTurnos` legacy puede coexistir durante la transición.

## Criterios de éxito

- [ ] El ciudadano puede solicitar turno de un Programa con `tiene_turnos=True`
- [ ] El ciudadano puede solicitar turno de una Institución con `ConfiguracionTurnos` asignada
- [ ] Los turnos solicitados quedan con `contexto_tipo` correcto (PROGRAMA / INSTITUCION)
- [ ] El flujo legacy de `RecursoTurnos` sigue funcionando sin romper
