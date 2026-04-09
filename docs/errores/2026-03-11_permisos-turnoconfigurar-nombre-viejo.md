---
name: Permisos turnoConfigurar usan nombre de grupo desactualizado
description: Las vistas de configuración de turnos verifican el grupo 'Administradores de Turnos' (nombre viejo) en lugar de 'turnoConfigurar' (nombre acordado)
type: error
---

# Permisos turnoConfigurar usan nombre de grupo desactualizado
> Estado: CERRADO (resuelto en US-011 — 2026-03-15)
> Fecha: 2026-03-11
> Severidad: ALTO

## Descripción

Las vistas de configuración de turnos en el backoffice usan un decorator interno `_admin_turnos_required` que verifica el grupo `'Administradores de Turnos'` — el nombre viejo previo a la sesión 4 donde se acordaron los nombres definitivos de roles.

Cuando se ejecute **US-011** (data migration que renombra los grupos Django), estas vistas dejarán de protegerse correctamente porque el grupo nuevo se llamará `turnoConfigurar`.

## Archivos afectados

- `turnos/views_backoffice.py` línea 43-47:
  ```python
  def _admin_turnos_required(view_func):
      return login_required(
          group_required(['Administradores de Turnos'])(view_func)  # ← nombre viejo
      )
  ```

## Vistas afectadas

- `configuracion_crear`
- `configuracion_editar`
- `disponibilidad_grilla`
- `disponibilidad_agregar`
- `disponibilidad_editar`
- `disponibilidad_eliminar`

## Comportamiento esperado vs actual

- **Esperado:** verificar grupo `turnoConfigurar`
- **Actual:** verifica grupo `Administradores de Turnos`

## Fix requerido

Cambiar en `_admin_turnos_required`:
```python
group_required(['turnoConfigurar'])(view_func)
```

> **Nota:** hacer este fix junto con o después de US-011 para que el grupo exista en la base con el nuevo nombre.
