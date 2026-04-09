# Fix: Imports rotos post-refactor DX (paquetes de views/selectors/services)

> Estado: CERRADO
> Fecha: 2026-03-19
> Severidad: ALTO
> Tipo: fix

## Descripción

El refactor DX (slices 37–47, sesión anterior) migró módulos planos a paquetes con sub-archivos. Quedaron múltiples imports stale que impedían el inicio del servidor. El servicio `sedronar-ws` crasheaba en el startup con distintos `ImportError` / `AttributeError`.

El servidor no levantaba. Además, el contenedor `nginx` (puerto 9000) no estaba incluido en el `up -d` inicial y tampoco levantaba.

## Archivos corregidos

| Archivo | Problema | Fix |
|---------|---------|-----|
| `legajos/views/__init__.py` | `from ..views_ciudadanos import (...)` — módulo eliminado en refactor | Eliminado el bloque stale (los símbolos ya estaban re-exportados desde `.ciudadanos`) |
| `legajos/views/__init__.py` | `from .historial_contactos import contactos_api` shadoweaba el módulo `contactos_api.py` | Renombrado a `historial_contactos_api` |
| `legajos/selectors/__init__.py` | 9 funciones usadas por `clinico.py` no exportadas desde `legajos.py` | Agregados: `get_derivaciones_queryset`, `get_dispositivo_derivaciones_queryset`, `get_eventos_dashboard_metrics`, `get_eventos_queryset`, `get_export_legajos_queryset`, `get_plan_vigente`, `get_planes_queryset`, `get_responsable_candidates`, `get_seguimientos_queryset` |
| `portal/selectors/turnos_ciudadano.py` | `from .models import RecursoTurnos, TurnoCiudadano` — no existe `models.py` en selectors | → `from portal.models import ...` |
| `portal/services/turnos_ciudadano.py` | `from .models import DisponibilidadTurnos, TurnoCiudadano` — idem | → `from portal.models import ...` |
| `conversaciones/selectors/conversaciones.py` | 3 lazy imports `from .models import` dentro de funciones | → `from conversaciones.models import ...` |
| `legajos/selectors/contactos.py` | Lazy import `from .models import AlertaCiudadano` dentro de función | → `from legajos.models import AlertaCiudadano` |
| `legajos/admin_programas.py` | `list_display` y `list_filter` referenciaban campo `activo` inexistente en `Programa` (usa `estado`) | Reemplazado por `estado` en `list_display`, `list_filter` y `fieldsets` |
| `flujos/models.py` | Índice `ix_instanciaflujo_version_estado` (34 chars) supera límite Django de 30 | Renombrado a `ix_instflujo_version_estado` |
| `flujos/migrations/0002_rename_long_index.py` | — | Creada migración con `RenameIndex` para renombrar el índice en la DB |

## Causa raíz

Todos los errores son consecuencia del refactor DX que reorganizó módulos planos en paquetes. Los `__init__.py` de los nuevos paquetes (`views/`, `selectors/`, `services/`) no exportaban todos los símbolos necesarios, y algunos archivos internos usaban `from .models import` (punto simple) en lugar de `from app.models import` o `from ..models import`.

El error del admin y el índice largo son bugs independientes que no habían sido detectados porque el servidor nunca había levantado con la nueva estructura.

## Verificación

- `curl http://localhost:9000/` → 200
- Todos los contenedores `Up` y `healthy`
- Sin errores en logs recientes
