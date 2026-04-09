---
name: Auditoría transversal del sistema
description: Registro trazable de todas las acciones del sistema — quién hizo qué, cuándo y sobre qué entidad — para cumplir requisitos de auditoría estatal.
type: requerimiento
---

# Auditoría transversal
> Estado: ABIERTO
> Fecha: 2026-03-12
> Prioridad: ALTA
> Tipo: FEATURE

## Descripción

Todo el sistema debe ser trazable. Cada acción relevante queda registrada con: usuario que la realizó, timestamp, entidad afectada, acción realizada y datos anteriores/nuevos (cuando aplique).

## Dependencias

- Se implementa en paralelo con o después de US-006 (motor de flujos) para cubrir también inscripciones y derivaciones
- Aplica a todos los módulos: ciudadanos, programas, instituciones, turnos, actividades, derivaciones, configuraciones

## Alcance de la auditoría

### Acciones a registrar

| Módulo | Acciones |
|--------|---------|
| **Ciudadanos** | Alta, edición de campos, cambio de campos sensibles, visualización de campos sensibles |
| **Programas** | Creación, edición, cambio de estado (BORRADOR→ACTIVO→SUSPENDIDO→INACTIVO), publicación de flujo |
| **Inscripciones** | Creación (derivación/inscripción directa), aceptación, rechazo, avance de paso, baja |
| **Derivaciones** | Creación, aceptación, rechazo |
| **Instituciones** | Creación, edición, cambio de estado (aprobación/rechazo/reactivación) |
| **Turnos** | Creación, confirmación, rechazo, cancelación, completado |
| **Actividades** | Inscripción ciudadano, cambio de estado, registro de asistencia por clase |
| **Configuraciones** | Cambios en ConfiguracionTurnos, disponibilidades, parámetros del sistema |
| **Usuarios** | Creación, asignación/revocación de roles |

### Datos del registro

Cada entrada de auditoría contiene:
- `usuario` → quién realizó la acción
- `accion` → qué hizo (CREATE / UPDATE / DELETE / VIEW_SENSITIVE)
- `entidad_tipo` → modelo afectado (ej: "Ciudadano", "InscripcionPrograma")
- `entidad_id` → ID del registro afectado
- `datos_anteriores` → JSON con valores previos (para UPDATE)
- `datos_nuevos` → JSON con valores nuevos (para UPDATE/CREATE)
- `timestamp` → cuándo ocurrió
- `ip` → IP del cliente (best-effort)

## Implementación sugerida

- Modelo `RegistroAuditoria` en app `core/` (transversal a todo el sistema)
- Signal Django o mixin en las views para capturar automáticamente
- Considerar `django-simple-history` o implementación propia
- Los logs de auditoría son **inmutables** — no se editan ni eliminan

## Criterios de éxito

- [ ] Toda acción listada en la tabla queda registrada automáticamente
- [ ] El administrador puede consultar el log de auditoría filtrado por usuario, entidad, acción y rango de fechas
- [ ] Los registros de auditoría son inmutables (no hay vista de edición/borrado)
- [ ] Solo usuarios con `reportesVer` o `is_staff` pueden ver el log
- [ ] El sistema de auditoría no impacta perceptiblemente el tiempo de respuesta de las vistas
