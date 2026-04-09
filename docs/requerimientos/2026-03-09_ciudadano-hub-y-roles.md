# Requerimiento: Expansión de ficha ciudadano, hub con solapas y roles de acceso

**Estado:** ABIERTO
**Fecha:** 2026-03-09
**Origen:** Sesión /definir — ciudadano y legajo ciudadano

---

## Contexto

La ficha del ciudadano hoy tiene datos básicos y grupo familiar. Se definió que debe expandirse con más información social, y que el hub `/legajos/ciudadanos/<id>/` debe tener solapas estáticas y dinámicas con badge behavior. También se definió el mapa de roles de acceso.

---

## Definiciones acordadas

### Información a registrar
- Datos básicos existentes: DNI, nombre, apellido, fecha nacimiento, género, teléfono, email, domicilio, provincia, municipio
- **Nuevos campos:** foto, situación habitacional (tipo vivienda, tenencia, condiciones), situación laboral/económica, nivel educativo, cobertura médica/medicación *(sensible)*, documentación migratoria *(sensible)*, observaciones/notas libres

### Hub del ciudadano — solapas
**Estáticas** (siempre presentes): Resumen · Cursos y Actividades · Red Familiar · Archivos

**Dinámicas** (solo si hay datos): Programas · Turnos · Instituciones · Conversaciones · Derivaciones · Alertas · Línea de tiempo

**Badge behavior:** contador numérico en cada tab · dinámicas ocultas si sin datos · indicador visual si requiere atención

### Roles
| Rol | Permiso |
|-----|---------|
| `ciudadanoVer` | Ver ficha (sin campos sensibles) |
| `ciudadanoCrear` | Crear y editar ciudadanos |
| `ciudadanoSensible` | Acceder a campos de salud, documentación migratoria y campos marcados como sensibles |

### Acceso por ámbito
- Operador de institución → solo ciudadanos de su institución
- Operador de programa/backoffice → todos los ciudadanos, gestiona los de su ámbito

---

## Criterios de aceptación

### Feature A — Expansión de ficha ciudadano
- [ ] El modelo `Ciudadano` tiene los nuevos campos: foto, situación habitacional, laboral, educativa, médica, documentación, notas
- [ ] Los campos de salud y documentación migratoria tienen flag `sensible=True`
- [ ] El formulario de alta/edición del ciudadano incluye todos los campos nuevos
- [ ] Los campos sensibles no se renderizan si el usuario no tiene `ciudadanoSensible`
- [ ] El operador puede marcar campos adicionales como sensibles al cargar el ciudadano

### Feature B — Hub ciudadano con solapas dinámicas
- [ ] Las solapas estáticas (Resumen, Cursos y Actividades, Red Familiar, Archivos) siempre se muestran
- [ ] Las solapas dinámicas solo aparecen si hay datos relacionados
- [ ] Cada solapa muestra contador numérico
- [ ] Las solapas con alertas activas o atención requerida tienen indicador visual diferenciado
- [ ] El diseño sigue el mismo patrón visual de badges estáticos y dinámicos existente

### Feature C — Roles y acceso
- [ ] Los grupos `ciudadanoVer`, `ciudadanoCrear`, `ciudadanoSensible` existen en la base de datos
- [ ] Las vistas del hub y listado de ciudadanos respetan los permisos
- [ ] El listado filtra por ámbito según el tipo de operador (institución vs. backoffice)
- [ ] Un usuario sin rol recibe redirección al intentar acceder directamente

---

## Deuda técnica planificada (no bloquea esta feature)
- `LegajoAtencion` se mantiene SEDRONAR-específico hoy
- En el futuro: sus acciones (evaluación, plan, seguimientos) pasan a ser nodos de acción del motor de flujos
- Cuando suceda: modelos SEDRONAR/ÑACHEC se eliminan y la data migra

---

## Orden de implementación sugerido

1. `/feature` — Expansión de campos en modelo `Ciudadano` + formulario actualizado
2. `/feature` — Hub ciudadano: solapas dinámicas con badge behavior
3. `/feature` — Roles `ciudadanoVer`, `ciudadanoCrear`, `ciudadanoSensible` + filtro por ámbito
