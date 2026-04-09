---
name: Unificación de modelos de derivación (US-021)
description: Reemplazar DerivacionInstitucional con el nuevo modelo unificado DerivacionCiudadano que soporta tipo_inicio, programa_origen y destino a programa o actividad.
type: requerimiento
---

# Unificación modelos de derivación
> Estado: CERRADO (implementado 2026-03-15)
> Fecha: 2026-03-12
> Prioridad: ALTA
> Tipo: FEATURE

## Descripción

Existen dos modelos de derivación en el sistema. `Derivacion` (legacy, desde `LegajoAtencion`) se mantiene intacto. `DerivacionInstitucional` se reemplaza con `DerivacionCiudadano`, un modelo más completo que soporta todos los casos de uso definidos en US-012.

## Diseño técnico aprobado

Ver `docs/requerimientos/2026-03-12_derivacion-e-inscripcion.md` para el flujo de negocio completo.

### Nuevo modelo: `DerivacionCiudadano`

**Ubicación:** `legajos/models_institucional.py`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `ciudadano` | FK(Ciudadano, CASCADE) | Origen |
| `tipo_inicio` | CharField — DERIVACION / INSCRIPCION_DIRECTA | Quién inició |
| `institucion_programa` | FK(InstitucionPrograma, PROTECT, null=True) | Destino programa |
| `actividad_destino` | FK(PlanFortalecimiento, PROTECT, null=True) | Destino actividad |
| `programa_origen` | FK(Programa, SET_NULL, null=True) | Desde qué programa se originó |
| `institucion` | FK(Institucion, null=True) | Redundancia BI — auto en save() |
| `programa` | FK(Programa, null=True) | Redundancia BI — auto en save() |
| `estado` | CharField — PENDIENTE / ACEPTADA / RECHAZADA | — |
| `urgencia` | CharField — BAJA / MEDIA / ALTA | — |
| `motivo` | TextField | Obligatorio |
| `observaciones` | TextField(blank=True) | — |
| `derivado_por` | FK(User, SET_NULL) | — |
| `respuesta` | TextField(blank=True) | — |
| `fecha_respuesta` | DateTimeField(null=True) | — |
| `quien_responde` | FK(User, SET_NULL, null=True) | — |
| `caso_creado` | FK(CasoInstitucional, SET_NULL, null=True) | — |

### Estrategia de migración

1. **Migración A** — Crear `DerivacionCiudadano` + renombrar `related_name` de `DerivacionInstitucional` a `*_legacy`
2. **Migración B** — Data migration: copiar registros de `DerivacionInstitucional` → `DerivacionCiudadano` (mapear `ACEPTADA_UNIFICADA` → `ACEPTADA`)
3. **Migración C** — `AlterField` en `CasoInstitucional.caso_creado` para apuntar a la nueva tabla
4. `DerivacionInstitucional` queda como tabla legacy sin eliminar (se elimina junto con la migración de `LegajoAtencion` a flujos)

### Archivos a modificar

- `legajos/models_institucional.py` — nuevo modelo + renombrar related_names legacy
- `legajos/forms_institucional.py` — nuevos forms
- `legajos/services_institucional.py` — nuevo service
- `legajos/views_institucional.py` — actualizar queries
- `legajos/views_programas.py` — actualizar anotaciones
- `configuracion/views.py` — actualizar query de conteo
- `legajos/admin.py` — actualizar admin

### Riesgos identificados

- Conflicto de `related_name` entre modelo viejo y nuevo → mitigar renombrando a `*_legacy` en Migración A
- Registros con `ACEPTADA_UNIFICADA` → mapear explícitamente en Migración B
- `views_programas.py` anotación `derivaciones_programa` → actualizar `related_name`
- Existe `DerivacionPrograma` (tercer modelo, distinto flujo) → no tocar

## Criterios de éxito

- [ ] El modelo `DerivacionCiudadano` existe con todos los campos especificados
- [ ] Los datos de `DerivacionInstitucional` se migraron correctamente (sin pérdida)
- [ ] `CasoInstitucional.caso_creado` apunta al nuevo modelo
- [ ] Las views y forms usan el nuevo modelo
- [ ] `DerivacionInstitucional` sigue existiendo con sus datos históricos (no se elimina)
- [ ] No hay conflictos de `related_name` en startup
- [ ] El dashboard de `configuracion/views.py` sigue mostrando derivaciones pendientes correctamente
