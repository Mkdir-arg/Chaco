# Requerimiento: Estructura de programas con flujos configurables

**Estado:** ABIERTO
**Fecha:** 2026-03-09
**Origen:** Sesión /definir — estructura general del sistema

---

## Contexto

Los programas sociales hoy son un catálogo plano sin estructura de flujo ni distinción de naturaleza. Esta sesión definió el modelo conceptual completo que debe implementarse.

---

## Definiciones acordadas

### Naturaleza de un programa
- **Un solo acto**: el ciudadano atraviesa el flujo, se resuelve (aprobado/rechazado), y el caso cierra automáticamente
- **Persistente**: el ciudadano entra, traversa el flujo, y permanece activo hasta baja manual. El flujo puede seguir alimentando información durante toda la vida del caso

### Jerarquía organizacional
- Todo programa pertenece a: **Secretaría → Subsecretaría** (exactamente dos niveles, no más)
- Los modelos `Secretaria` y `Subsecretaria` deben crearse en `core/`

### Flujos
- Todo programa tiene un flujo obligatorio
- Sin flujo = estado BORRADOR (el programa existe pero no puede activarse)
- El flujo define: pasos, formularios, evaluaciones, tareas territoriales, derivaciones, etc.
- Las tareas territoriales son un **tipo de nodo dentro del flujo** (formulario que se completa en app móvil)

### Permisos
- Solo el rol `ConfiguracionPrograma` puede crear y configurar programas

---

## Criterios de aceptación

### Fase 1 — Jerarquía organizacional
- [ ] Existe modelo `Secretaria` con nombre, descripción, activo
- [ ] Existe modelo `Subsecretaria` con FK a `Secretaria`, nombre, descripción, activo
- [ ] ABM completo en backoffice para ambos (solo Admin o `ConfiguracionPrograma`)
- [ ] El modelo `Programa` tiene FK obligatoria a `Subsecretaria`

### Fase 2 — Panel de configuración de programa (wizard)
- [ ] Paso 1: datos básicos (nombre, descripción, Secretaría → Subsecretaría)
- [ ] Paso 2: naturaleza del programa (un solo acto / persistente)
- [ ] Paso 3: capacidades activables (turnos sí/no) — aplica a AMBOS tipos de programa
- [ ] El programa se crea en estado BORRADOR si no tiene flujo configurado
- [ ] Solo usuarios con rol `ConfiguracionPrograma` acceden a la creación
- [ ] El detalle del programa también es un wizard (misma estructura)

### Fase 3 — Motor de flujos (backend)
- [ ] Nueva app `flujos/` con modelos: `Flujo`, `Step`, `Transition`, `InstanciaFlujo`, `InstanceLog`
- [ ] `FlowRuntime` capaz de ejecutar instancias paso a paso
- [ ] Tipos de nodo mínimos: start, form, evaluation, condition, email, delay, tarea territorial
- [ ] Un programa puede tener un `Flujo` asociado
- [ ] Una `InscripcionPrograma` puede tener una `InstanciaFlujo` activa
- [ ] Cierre automático de la inscripción al completar el flujo (solo programas de un solo acto)

### Fase 4 — Editor visual de flujos (frontend)
- [ ] Decisión de stack tomada (React solo para el editor, resto Alpine.js — pendiente)
- [ ] Editor drag & drop basado en el sistema NODO como referencia
- [ ] Integrado en el wizard del programa como paso final de configuración

---

## Orden de implementación sugerido

1. `/feature` — ABM Secretaría / Subsecretaría + FK en Programa
2. `/feature` — Panel de configuración de programa (wizard, sin flujo por ahora)
3. `/feature` — Motor de flujos backend (app `flujos/`)
4. `/feature` — Editor visual de flujos (requiere decisión de stack primero)

---

## Implicancias técnicas

- Modelo `Programa` en `legajos/models_programas.py` necesita: campo `naturaleza`, FK a `Subsecretaria`, campo `tiene_turnos`, campo `cupo_maximo` (null=True), campo `tiene_lista_espera`, estado `BORRADOR/ACTIVO/SUSPENDIDO/INACTIVO`
- `InscripcionPrograma` necesita lógica de cierre automático (un solo acto) vs. baja manual (persistente)
- Motor de flujos: adaptar backend del sistema NODO. Ver `docs/requerimientos/referencia-motor-flujos-nodo.md` (pendiente de crear)
- Editor visual: requiere React — decisión arquitectónica pendiente antes de implementar Fase 4
