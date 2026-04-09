---
name: Derivación e inscripción de ciudadanos a programas
description: Flujo completo para ingresar un ciudadano a un programa via derivación o inscripción directa, con aceptación manual por el operador destino e inicio del flujo.
type: requerimiento
---

# Derivación e inscripción de ciudadanos a programas
> Estado: CERRADO (implementado 2026-03-15)
> Fecha: 2026-03-12
> Prioridad: ALTA
> Tipo: FEATURE

## Descripción

Un ciudadano puede ingresar a un programa por dos caminos: **derivación** (cualquier operador) o **inscripción directa** (solo gestores del programa destino). Ambos usan el mismo modelo y flujo — la diferencia es el permiso y el punto de entrada.

El operador del programa destino acepta o rechaza manualmente. Al aceptar, se crea `InscripcionPrograma` y se inicia el flujo configurado del programa.

## Dependencias

- **US-021** — modelo unificado de derivación debe existir primero
- **US-006** — motor de flujos backend (el flujo que se inicia al aceptar)
- **US-011** — grupos Django con nombres definitivos (para el permiso `programaOperar`)

## Modelo de datos (definido)

**Derivacion (modelo unificado):**
- `ciudadano` → FK a Ciudadano
- `programa_destino` → FK a Programa (o institución/actividad según destino)
- `tipo_inicio` → `DERIVACION` | `INSCRIPCION_DIRECTA`
- `estado` → `PENDIENTE` | `ACEPTADA` | `RECHAZADA`
- `urgencia` → `BAJA` | `MEDIA` | `ALTA`
- `motivo` → texto
- `respuesta` → texto (opcional)
- `quien_deriva` → FK a User
- `quien_responde` → FK a User (opcional)
- `fecha_respuesta` → datetime (opcional)
- `programa_origen` → FK a Programa (opcional — se registra cuando se deriva desde el dashboard de un programa)

## Reglas de negocio

### Validaciones al crear
- ❌ Si ya existe Derivacion con `estado=PENDIENTE` al mismo programa → error con aviso
- ❌ Si el ciudadano ya tiene `InscripcionPrograma` con `estado=ACTIVO` en ese programa → error con aviso
- ✅ Si la derivación anterior fue RECHAZADA → puede derivarse de nuevo
- ✅ Un ciudadano puede tener derivaciones PENDIENTE a distintos programas simultáneamente

### Quién puede crear
- Derivación (`tipo_inicio=DERIVACION`): cualquier operador del backoffice
- Inscripción directa (`tipo_inicio=INSCRIPCION_DIRECTA`): solo gestores del programa destino (`programaOperar`)

### Quién acepta/rechaza
- El operador del **programa destino** (con rol `programaOperar` en ese programa)
- No hay aceptación automática

### Al aceptar
- `Derivacion.estado` → `ACEPTADA`
- `InscripcionPrograma` se crea con `estado=PENDIENTE`
- `InstanciaFlujo` se crea y el flujo inicia

### Al rechazar (desde bandeja de derivaciones)
- `Derivacion.estado` → `RECHAZADA`
- `InscripcionPrograma` NO se crea

### Cancelación dentro del flujo
- No existe "cancelar derivación" como acción directa
- El flujo puede tener un paso de "rechazar" si se configura
- Si el flujo rechaza → `InstanciaFlujo` queda en estado `RECHAZADO`, `InscripcionPrograma` pasa a `INACTIVO`
- La `Derivacion` queda en estado `ACEPTADA` (el rechazo ocurre en el flujo, no en la derivación)

## Puntos de entrada UI

| Desde | Quién | Comportamiento |
|-------|-------|----------------|
| Perfil del ciudadano `/legajos/ciudadanos/<id>/` | Cualquier operador | Elige destino libremente |
| Dashboard del programa | Gestor del programa | Busca ciudadano; `programa_origen` queda registrado automáticamente |

## Notificaciones

- **Operador destino:** badge + alerta en bandeja al recibir derivación nueva
- **Ciudadano:** sin notificación activa — lo ve en su portal, sección Programas

## Criterios de éxito

- [ ] Un operador puede crear una derivación desde el perfil del ciudadano eligiendo programa destino
- [ ] Un gestor puede crear inscripción directa desde el dashboard del programa
- [ ] Se valida correctamente y se muestra aviso si hay PENDIENTE o ya está ACTIVO
- [ ] El operador destino ve la derivación en su bandeja con badge
- [ ] El operador destino puede aceptar o rechazar con motivo
- [ ] Al aceptar se crea `InscripcionPrograma` (estado PENDIENTE) y se inicia el flujo
- [ ] Al rechazar no se crea inscripción
- [ ] El ciudadano ve sus derivaciones pendientes en el portal sección Programas
- [ ] El flujo puede rechazar en cualquier paso si está configurado para eso
