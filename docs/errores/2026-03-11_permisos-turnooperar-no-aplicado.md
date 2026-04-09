---
name: Rol turnoOperar no está aplicado en vistas operativas de turnos
description: Las vistas de gestión de turnos (aprobar, rechazar, cancelar, agenda, bandeja) solo verifican que el usuario sea "no ciudadano", sin exigir el rol turnoOperar
type: error
---

# Rol turnoOperar no está aplicado en vistas operativas de turnos
> Estado: CERRADO (resuelto 2026-03-15)
> Fecha: 2026-03-11
> Severidad: MEDIO

## Descripción

Las vistas operativas de turnos (agenda, bandeja de pendientes, aprobar, rechazar, cancelar, completar) usan el decorator `_operador_required`, que verifica únicamente que el usuario esté autenticado y **no pertenezca al grupo `Ciudadanos`**.

Esto significa que cualquier usuario del backoffice —independientemente de su rol— puede aprobar o rechazar turnos. Un usuario con solo `ciudadanoVer` podría hacerlo.

## Archivos afectados

- `turnos/views_backoffice.py` líneas 25-40:
  ```python
  def _es_operador(user):
      return user.is_authenticated and (
          user.is_staff or user.is_superuser or
          not user.groups.filter(name='Ciudadanos').exists()  # ← demasiado permisivo
      )
  ```

## Vistas afectadas

| Vista | Acción | Debería requerir |
|-------|--------|-----------------|
| `backoffice_home` | Dashboard | cualquier operador (OK) |
| `configuracion_lista` | Ver configs | cualquier operador (OK) |
| `agenda` | Ver agenda | `turnoOperar` |
| `bandeja_pendientes` | Ver pendientes | `turnoOperar` |
| `turno_detalle` | Ver detalle | `turnoOperar` |
| `turno_aprobar` | Aprobar turno | `turnoOperar` |
| `turno_rechazar` | Rechazar turno | `turnoOperar` |
| `turno_cancelar` | Cancelar turno | `turnoOperar` |
| `turno_completar` | Completar turno | `turnoOperar` |

## Comportamiento esperado vs actual

- **Esperado:** solo usuarios con `turnoOperar` pueden gestionar turnos
- **Actual:** cualquier usuario del backoffice puede hacerlo

## Fix requerido

Reemplazar `_operador_required` por `group_required(['turnoOperar'])` en las vistas operativas, o crear un decorator `_turno_operar_required` equivalente a `_admin_turnos_required`.

```python
def _turno_operar_required(view_func):
    return login_required(
        group_required(['turnoOperar'])(view_func)
    )
```

> **Nota:** hacer este fix junto con o después de US-011 para que el grupo exista en la base.
