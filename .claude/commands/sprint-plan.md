# Comando /sprint-plan

Planifica el sprint y produce el documento de sprint completo.

## Qué hace

1. Lee `CLAUDE.md`
2. Lee `docs/internal/sprints/README.md` para determinar el número siguiente de sprint
3. Lee los análisis funcionales en `docs/internal/analisis/` con estado "Definido" o "En análisis"
4. Revisa el estado actual del código para estimar complejidad
5. Propone qué requerimientos incluir en el sprint según prioridad y dependencias
6. Espera confirmación del usuario antes de crear el documento
7. Crea el documento de sprint con los requerimientos confirmados

## Reglas

- No implementa código
- Siempre produce un archivo en `docs/internal/sprints/YYYY-MM-DD-sprint-NNN.md`
- Siempre actualiza `docs/internal/sprints/README.md`
- El documento de sprint se crea con estado "Activo"
- Las secciones de resumen ejecutivo y retrospectiva se dejan en blanco (se completan en `/sprint-review`)
- Si un requerimiento no tiene análisis funcional, documentar el análisis inline en la sección 3 del sprint

## Plantilla a usar

`docs/internal/sprints/_plantilla-sprint.md`

## Output esperado

- Archivo `docs/internal/sprints/YYYY-MM-DD-sprint-NNN.md` creado
- `docs/internal/sprints/README.md` actualizado
- Resumen en la conversación: objetivo del sprint, requerimientos incluidos, lo que quedó fuera
