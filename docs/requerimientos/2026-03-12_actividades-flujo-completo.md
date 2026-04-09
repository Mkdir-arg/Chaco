---
name: Actividades — flujo completo (inscripción, clases, asistencia, staff, lista de espera)
description: Define el modelo completo de actividades institucionales incluyendo inscripción desde portal y backoffice, entidad Clase, registro de asistencia, gestión de staff, cupo y lista de espera.
type: requerimiento
---

# Actividades — flujo completo
> Estado: ABIERTO
> Fecha: 2026-03-12
> Prioridad: MEDIA
> Tipo: FEATURE

## Descripción

Las actividades (`PlanFortalecimiento`) ya existen en el sistema pero sin flujo operativo completo. Esta definición cubre el ciclo de vida completo: inscripción de ciudadanos, clases, registro de asistencia, estados, staff y lista de espera.

## Reglas de negocio

### Inscripción

| Tipo de acceso | Quién puede inscribir |
|---------------|----------------------|
| `LIBRE` | El ciudadano desde el portal, operadores del programa, encargados de la institución |
| `REQUIERE_PROGRAMA` | Solo operadores que gestionen ese programa o encargados de la institución |

- Un ciudadano puede estar inscripto en múltiples actividades simultáneamente
- Al inscribirse, el ciudadano recibe un **código de inscripción** como confirmación
- El código y el estado de inscripción son visibles en el perfil del portal del ciudadano

### Cupo y lista de espera

- Cupo máximo: opcional, configurable al crear la actividad
- Lista de espera: opcional, configurable junto con el cupo
- Cuando se libera un cupo con lista de espera activa, dos modos (configurable por actividad):
  - **Automático**: se asigna al siguiente en la lista automáticamente
  - **Manual**: el operador recibe aviso y elige quién de la lista ocupa el lugar

### Fechas

- Fecha de inicio y fecha de fin: ambas opcionales
- Si hay fecha de fin configurada y se llega a ella → todos los ciudadanos `ACTIVO` pasan automáticamente a `FINALIZADO`

### Entidad Clase

- Una actividad se organiza en **clases**
- Campos de una clase: fecha, hora de inicio, duración, título (opcional)
- Las crea con anticipación el staff asignado o el encargado de la institución
- La asistencia se registra **por clase**, no por día

### Registro de asistencia

- Valores: `PRESENTE / AUSENTE / JUSTIFICADO / TARDANZA`
- Pueden registrar: staff asignado a la actividad + encargado de la institución

### Estados del ciudadano en la actividad

| Estado | Cómo se llega |
|--------|--------------|
| `INSCRITO` | Al inscribirse, antes de la primera clase |
| `ACTIVO` | Al comenzar a participar |
| `FINALIZADO` | Automático al llegar la fecha fin, o manual por staff al marcar como completado |
| `ABANDONADO` | Manual por operador/staff, o auto-desinscripción del ciudadano desde el portal |

- Al pasar a `ABANDONADO`: los turnos pendientes de la actividad se cancelan y sus slots se liberan

### Staff de la actividad

- Se crea y gestiona desde la solapa de gestión de la institución
- Se asigna a una actividad específica desde dentro de la actividad

### Vista del ciudadano

**Solapa "Cursos y Actividades" en el hub del ciudadano:**
- Muestra actividades activas + historial completo
- Tarjeta de cada actividad: nombre, institución, estado, próxima clase, asistencia acumulada

**Portal ciudadano:**
- El ciudadano ve su porcentaje de asistencia
- Ve su código de inscripción y estado

## User stories derivadas

- **US-020** — Agregar campo `tipo_acceso` a `PlanFortalecimiento` (ya en backlog)
- **US-022** — Inscripción de ciudadanos a actividades: validación tipo_acceso, cupo, código de inscripción, notificación
- **US-023** — Entidad Clase y registro de asistencia por clase
- **US-024** — Lista de espera en actividades (modos auto/manual)

## Criterios de éxito

- [ ] Un operador puede inscribir un ciudadano a una actividad LIBRE o REQUIERE_PROGRAMA
- [ ] Un ciudadano puede inscribirse desde el portal a una actividad LIBRE
- [ ] Al inscribirse se genera un código de inscripción visible en el portal del ciudadano
- [ ] Se valida el tipo de acceso — si REQUIERE_PROGRAMA, verifica inscripción activa en ese programa
- [ ] Se valida el cupo — si lleno y hay lista de espera, el ciudadano entra a la lista
- [ ] La lista de espera opera en modo auto o manual según configuración
- [ ] El staff/encargado puede crear clases con anticipación (fecha + hora + duración + título)
- [ ] El staff/encargado puede registrar asistencia por clase para cada ciudadano inscripto
- [ ] Si la actividad tiene fecha de fin y se llega a ella, los ciudadanos ACTIVO pasan a FINALIZADO automáticamente
- [ ] Un operador puede marcar manualmente a un ciudadano como FINALIZADO o ABANDONADO
- [ ] El ciudadano puede auto-desinscribirse desde el portal (pasa a ABANDONADO)
- [ ] Al abandonar, los turnos pendientes se cancelan y los slots se liberan
- [ ] La solapa "Cursos y Actividades" muestra activas + historial con tarjeta: nombre, institución, estado, próxima clase, asistencia acumulada
- [ ] El portal muestra porcentaje de asistencia al ciudadano
