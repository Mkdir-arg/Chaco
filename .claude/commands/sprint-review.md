# Comando /sprint-review

Cierra el sprint activo y completa el documento de sprint con la retrospectiva y el resumen ejecutivo.

## Qué hace

1. Lee `CLAUDE.md`
2. Lee `docs/internal/sprints/README.md` para identificar el sprint activo
3. Lee el documento del sprint activo
4. Revisa el estado real del código para contrastar con lo planificado
5. Completa las secciones pendientes del documento de sprint
6. Actualiza el estado de cada requerimiento (Completado / Pendiente / Descartado)
7. Actualiza los análisis funcionales asociados con su nuevo estado
8. Cierra el sprint

## Reglas

- No implementa código
- Actualiza el documento de sprint existente, no crea uno nuevo
- Actualiza el estado del sprint a "Cerrado" en el documento y en el índice
- Actualiza el estado de los análisis funcionales asociados en `docs/internal/analisis/README.md`
- Si hay requerimientos que pasan al siguiente sprint, mencionarlos explícitamente

## Secciones que completa

- Sección 1 — Resumen ejecutivo
- Sección 2 — Estado final de cada requerimiento
- Sección 7 — Retrospectiva
- Sección 8 — Historial (agregar entrada de cierre)

## Output esperado

- Documento de sprint actualizado con estado "Cerrado"
- `docs/internal/sprints/README.md` actualizado
- `docs/internal/analisis/README.md` actualizado con los nuevos estados
- Resumen en la conversación: qué se completó, qué quedó pendiente, acciones para el próximo sprint
