# Instrucciones para GitHub Copilot — Chaco

`Chaco` es un monorepo Django (Python 3.12, Django 4.2, MySQL 8, Tailwind, Alpine.js,
Docker). Apps frecuentes: `core`, `legajos`, `configuracion`, `conversaciones`,
`dashboard`, `portal`, `users`, `tramites`, `healthcheck`. Trabajá **code-first**:
leé el código real antes de asumir comportamiento.

## Análisis funcional

El método de trabajo del analista funcional es **`AGENTS.md`** (raíz del repo):
fuente de verdad única, compartida con todas las herramientas. **Para cualquier
tarea de análisis funcional, leé y seguí `AGENTS.md`.** En resumen:

- Modelo **Épica → Análisis → Sub-issues**, todo en GitHub Issues.
- Investigación activa obligatoria (duplicidad, relacionadas, impacto crítico,
  inconsistencias) y **control estricto**: no se generan issues con dudas.
- Issues nuevos van a **Backlog**. **Solo el PM mueve** las tareas.
- Documentación pública en `docs/client/` (ver reglas de publicación en `AGENTS.md`).

Los prompts `/analisis-*` (en `.github/prompts/`) disparan cada paso del flujo.

## Gestión

- El trabajo se organiza en GitHub Issues/Projects (Project #1 "Proyect Chaco").
- Ningún asistente cambia el estado de una tarea en el Project: como mucho crea
  issues en Backlog.
