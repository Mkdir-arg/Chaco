---
name: Instituciones — panel institución y gestión interna
description: Define la tercera superficie del sistema (panel institución en /institucion/), roles internos, gestión de usuarios, reactivación y evaluaciones periódicas.
type: requerimiento
---

# Instituciones — panel institución y gestión interna
> Estado: ABIERTO
> Fecha: 2026-03-12
> Prioridad: MEDIA
> Tipo: FEATURE

## Descripción

Las instituciones tienen flujo de aprobación implementado pero carecen de una superficie propia para su gestión interna. Esta definición cubre el panel institución como tercera superficie del sistema, los roles internos, la gestión de usuarios, el flujo de reactivación y las evaluaciones periódicas.

## Tercera superficie: Panel Institución

- **URL:** `/institucion/`
- **Arquitectura:** app Django nueva `institucion/` con middleware propio, base template propio y routing separado del backoffice y del portal ciudadano
- **Auth:** mismo sistema de login Django — el sistema detecta el rol y redirige automáticamente a `/institucion/`
- **Patrón:** idéntico al portal ciudadano (`portal/`) — misma estrategia de separación

## Roles internos

| Rol | Grupo Django | Qué puede hacer |
|-----|-------------|----------------|
| `EncargadoInstitucion` | Existente | Todo + gestionar usuarios internos + solicitar revisión/reactivación |
| `AdministrativoInstitucion` | Nuevo | Configurar actividades, asignar profesores, ver turnos — sin gestión de usuarios |
| `ProfesorInstitucion` | Nuevo | Tomar asistencia, asignarse a actividades — visibilidad limitada del ciudadano |

**Visibilidad del Profesor sobre el ciudadano:** nombre, foto, teléfono/email únicamente. Sin acceso a ficha completa ni campos sensibles.

## Gestión de usuarios internos (US-025)

- El encargado crea usuarios con rol `AdministrativoInstitucion` o `ProfesorInstitucion` desde su panel
- El encargado puede eliminar estos usuarios
- Solo el encargado puede gestionar usuarios — administrativos y profesores no pueden

## Reactivación de institución RECHAZADA (US-026)

- Una institución RECHAZADA puede volver a postularse
- **Quién inicia:**
  - La institución desde su panel (botón "Solicitar reactivación")
  - El backoffice desde el admin, notificando a la institución
- **Historial:** se guarda como `REACTIVACION` — diferenciado de la aprobación original
- **Notificación:** la institución recibe aviso explícito de que es un proceso de reactivación

## Evaluaciones periódicas (US-027)

- Son **tareas territoriales aplicadas a instituciones** — mismo mecanismo que tareas del motor de flujos
- **Quién las crea:** administradores de programa desde el backoffice
- **Quién las ejecuta:** operadores territoriales desde la app de campo (móvil)
- **Qué hacen:** completan un formulario de auditoría en la app
- **Resultado:** queda vinculado al legajo de la institución evaluada
- **Prerequisitos:** motor de flujos (US-006) + app móvil definida

## Indicadores de monitoreo

Panel con métricas internas de la institución:
- Alumnos/ciudadanos activos
- Profesores asignados
- Actividades en curso
- Turnos agendados

## Criterios de éxito

### Panel institución (US-019)
- [ ] El encargado accede a `/institucion/` con su usuario Django y ve su panel
- [ ] El administrativo y el profesor también acceden a `/institucion/` con sus roles respectivos
- [ ] Un usuario sin rol de institución no puede acceder a `/institucion/`
- [ ] El panel muestra indicadores de monitoreo (alumnos, profesores, actividades, turnos)

### Gestión de usuarios (US-025)
- [ ] El encargado puede crear un usuario con rol AdministrativoInstitucion
- [ ] El encargado puede crear un usuario con rol ProfesorInstitucion
- [ ] El encargado puede eliminar usuarios internos
- [ ] El administrativo no puede gestionar usuarios

### Reactivación (US-026)
- [ ] Institución RECHAZADA ve botón "Solicitar reactivación" en su panel
- [ ] Al solicitarla, el backoffice recibe la solicitud para revisión
- [ ] El backoffice puede iniciar reactivación desde su lado y notificar a la institución
- [ ] El proceso queda registrado como REACTIVACION en el historial, no como aprobación nueva

### Evaluaciones periódicas (US-027)
- [ ] Un admin de programa puede crear una evaluación asignada a un territorial
- [ ] El territorial la ve y completa desde la app móvil
- [ ] El formulario completado queda vinculado al legajo de la institución
