---
name: Estado del análisis del sistema de turnos
description: Hallazgos del análisis de la turnera en sesión 2026-03-11 — permisos, vinculación programas, flujo ciudadano
type: project
---

# Estado del análisis del sistema de turnos (2026-03-11)

## Lo que funciona
- Backoffice de turnos completo: configuraciones, disponibilidades, agenda, bandeja, aprobar/rechazar/cancelar/completar
- Flujo del portal ciudadano completo: mis turnos, solicitar, calendario, slots, confirmar, cancelar
- Modelo `TurnoCiudadano` bien armado con doble vínculo legacy/nuevo y contexto genérico

## Bugs documentados
- `docs/errores/2026-03-11_permisos-turnoconfigurar-nombre-viejo.md` — el decorator usa `'Administradores de Turnos'` en lugar de `'turnoConfigurar'`
- `docs/errores/2026-03-11_permisos-turnooperar-no-aplicado.md` — las vistas operativas no verifican `turnoOperar`, cualquier operador puede aprobar turnos

## Requerimiento documentado
- `docs/requerimientos/2026-03-11_portal-turnos-migrar-a-configuracionturnos.md` — el portal usa `RecursoTurnos` (legacy), necesita migrar a `ConfiguracionTurnos` cuando US-004/005 estén implementadas

## Dependencias clave
- Los fixes de permisos deben hacerse junto con o después de US-011 (data migration de grupos)
- La migración del portal depende de US-004 (ABM Secretarías) y US-005 (wizard programa)

## Modelo Programa actual vs diseñado
- El modelo `Programa` en `legajos/models_programas.py` no tiene: `naturaleza`, FK a `Subsecretaria`, `estado` (BORRADOR/ACTIVO/...), `tiene_lista_espera`, `cupo_maximo`
- La FK `configuracion_turnos` sí existe ✅
- Todo lo faltante es parte de US-004 y US-005
