# Comando /sprint-review

Cierra el sprint actual revisando qué se completó.

## Instrucciones para el agente

1. Leer `docs/team/current-sprint.md` y `docs/team/changelog.md`

2. Presentar al usuario:
   - Ítems completados ✅ en este sprint
   - Ítems no completados (si los hay) y por qué
   - Velocidad del sprint (cuántos ítems de qué complejidad)

3. Preguntar al usuario: "¿Hay algo que mejorar para el próximo sprint? ¿Algún impedimento o aprendizaje?"

4. Cuando el usuario responda:
   - Mover ítems no completados de vuelta al backlog como 🟡
   - Archivar el sprint cerrado en `docs/team/changelog.md` con una sección de "Sprint N — Retrospectiva"
   - Limpiar `docs/team/current-sprint.md` para el próximo sprint

5. Confirmar: "Sprint cerrado. Cuando quieras arrancar el próximo, usá /sprint-plan."
