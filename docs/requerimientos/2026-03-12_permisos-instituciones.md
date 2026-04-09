---
name: Permisos de acceso al módulo de instituciones
description: Proteger todas las vistas del módulo de instituciones con los roles institucionVer e institucionAdministrar. Hoy usan solo LoginRequiredMixin.
type: requerimiento
---

# Permisos módulo instituciones
> Estado: ABIERTO
> Fecha: 2026-03-12
> Prioridad: ALTA
> Tipo: MEJORA

## Descripción

Todas las vistas del módulo de instituciones actualmente solo verifican que el usuario esté autenticado (`LoginRequiredMixin`). Deben verificar además el rol correspondiente.

## Dependencias

- **US-011** — los grupos `institucionVer` e `institucionAdministrar` deben existir en la base

## Reglas de acceso

| Vista | Rol requerido |
|-------|--------------|
| Lista de instituciones | `institucionVer` |
| Detalle de institución | `institucionVer` |
| Crear institución | `institucionAdministrar` |
| Editar institución | `institucionAdministrar` |
| Aprobar / Rechazar institución | `institucionAdministrar` |
| Legajo institucional (ver) | `institucionVer` |
| Legajo institucional (editar) | `institucionAdministrar` |

## Criterios de éxito

- [ ] Un usuario sin `institucionVer` ni `institucionAdministrar` no puede acceder a ninguna vista de instituciones
- [ ] Un usuario con `institucionVer` puede ver pero no crear/editar/aprobar
- [ ] Un usuario con `institucionAdministrar` puede hacer todo
- [ ] El acceso denegado redirige con mensaje claro (no 403 genérico)
- [ ] Ejecutar junto con US-011 para que los grupos existan antes de aplicar los decoradores
