# Comando /definir

Sesión de análisis funcional. Clarifica un requerimiento y produce el documento de análisis funcional completo.

## Qué hace

1. Lee `CLAUDE.md`
2. Lee la conversación actual
3. Inspecciona el código relacionado (modelos, views, templates, urls)
4. Lee `docs/internal/analisis/README.md` para determinar el número siguiente
5. Hace las preguntas necesarias para cerrar el alcance
6. Produce el análisis funcional completo siguiendo la plantilla

## Reglas

- No implementa código
- No escribe en `docs/client/` ni en `docs/internal/decisions/`
- Siempre produce un archivo en `docs/internal/analisis/NNN-nombre.md`
- Siempre actualiza `docs/internal/analisis/README.md`
- Si hay un sprint activo, agrega el requerimiento al documento de sprint
- Si quedan preguntas sin respuesta, el estado del análisis es "En análisis", no "Definido"
- No cierra el análisis hasta que todos los criterios de aceptación sean verificables

## Plantilla a usar

`docs/internal/analisis/_plantilla-analisis.md`

## Output esperado

- Archivo `docs/internal/analisis/NNN-nombre-funcionalidad.md` creado
- `docs/internal/analisis/README.md` actualizado
- Resumen en la conversación: estado, requerimientos definidos, preguntas abiertas si las hay
