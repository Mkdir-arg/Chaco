# Fix: Rol `turnoOperar` no aplicado en vistas operativas de turnos

> Tipo: fix
> Fecha: 2026-03-15
> Módulo: `turnos`
> Severidad original: MEDIO

## Problema

Las vistas operativas de turnos (agenda, bandeja de pendientes, detalle, aprobar, rechazar, cancelar, completar) usaban `OperadorRequiredMixin` / `operador_required`, que solo verificaba que el usuario no perteneciera al grupo `Ciudadanos`. Cualquier usuario del backoffice podía aprobar o rechazar turnos sin necesitar el grupo `turnoOperar`.

## Causa raíz

Al hacer el refactor DX (slice 26/31), se modularizaron los mixins de permisos pero no se creó el equivalente para `turnoOperar`. Las vistas quedaron con el guard permisivo heredado.

## Solución aplicada

**`turnos/mixins.py`** — agregados:
- `turno_operar_required(view_func)`: decorator que verifica `is_superuser OR turnoOperar`
- `TurnoOperarRequiredMixin`: equivalente CBV con el mismo criterio

**`turnos/views/turnos.py`** — reemplazados:
- `AgendaView`, `BandejaPendientesView`, `TurnoDetailView`: `OperadorRequiredMixin` → `TurnoOperarRequiredMixin`
- `turno_aprobar`, `turno_rechazar`, `turno_cancelar`, `turno_completar`: `@operador_required` → `@turno_operar_required`

`BackofficeHomeView` y `configuracion_lista` conservan `OperadorRequiredMixin` (cualquier operador puede verlos).

## Archivos modificados

- `turnos/mixins.py`
- `turnos/views/turnos.py`

## Requirió migración

No.
