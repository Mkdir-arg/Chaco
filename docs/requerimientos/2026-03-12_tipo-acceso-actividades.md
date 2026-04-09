---
name: Tipo de acceso en actividades (LIBRE / REQUIERE_PROGRAMA)
description: Agregar campo tipo_acceso y FK opcional a Programa en el modelo PlanFortalecimiento para controlar quién puede inscribirse a cada actividad.
type: requerimiento
---

# Tipo de acceso en actividades
> Estado: CERRADO (implementado 2026-03-15)
> Fecha: 2026-03-12
> Prioridad: MEDIA
> Tipo: MEJORA

## Descripción

El modelo `PlanFortalecimiento` (actividades institucionales) necesita un campo `tipo_acceso` para determinar si la actividad es abierta a cualquier ciudadano o si requiere estar inscripto en un programa específico.

## Cambios de modelo

**En `PlanFortalecimiento`:**
- `tipo_acceso` → CharField con choices `LIBRE` / `REQUIERE_PROGRAMA`, default `LIBRE`
- `programa_requerido` → FK a `Programa`, null=True, blank=True — solo aplica cuando `tipo_acceso = REQUIERE_PROGRAMA`

**Regla de integridad:** si `tipo_acceso = REQUIERE_PROGRAMA`, entonces `programa_requerido` es obligatorio.

## Impacto en lógica de inscripción

- Al intentar inscribir un ciudadano a una actividad `REQUIERE_PROGRAMA`:
  - Verificar que el ciudadano tiene `InscripcionPrograma` con `estado=ACTIVO` en `programa_requerido`
  - Si no → bloquear inscripción con mensaje claro
- Actividades `LIBRE` → sin validación adicional

## Criterios de éxito

- [ ] El campo `tipo_acceso` existe en `PlanFortalecimiento` con default `LIBRE`
- [ ] Si `tipo_acceso = REQUIERE_PROGRAMA`, se puede seleccionar el programa requerido
- [ ] La migración se aplica sin romper actividades existentes (default `LIBRE`)
- [ ] Al inscribir a una actividad `REQUIERE_PROGRAMA`, se valida la inscripción activa en el programa
- [ ] El formulario de creación/edición de actividad incluye este campo
- [ ] En el portal, las actividades `REQUIERE_PROGRAMA` solo aparecen si el ciudadano cumple la condición
