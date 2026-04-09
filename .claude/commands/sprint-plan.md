# Comando /sprint-plan

Arranca un nuevo sprint. El equipo revisa el backlog y propone qué ítems trabajar.

## Instrucciones para el agente

1. Leer `docs/team/backlog.md` y `docs/team/current-sprint.md`
2. Si hay un sprint activo, alertar al usuario

3. Presentar el backlog de ítems pendientes (🟡) ordenados por prioridad aparente

4. Proponer un objetivo de sprint en una oración

5. Sugerir entre 2 y 4 ítems para el sprint (adaptado a la complejidad estimada)

6. Preguntar: "¿Arrancamos el sprint con estos ítems o querés ajustar?"

7. Cuando el usuario apruebe:
   - Actualizar `docs/team/current-sprint.md` con los ítems seleccionados, fecha de inicio y objetivo
   - Marcar ítems como 🔵 En sprint en `docs/team/backlog.md`
   - Mostrar confirmación

**ESPERAR APROBACIÓN DEL USUARIO en el paso 6 antes de modificar archivos.**
