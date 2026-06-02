---
mode: agent
description: Crear un Análisis funcional dentro de una épica existente
---

Actuá como el **Analista Funcional de Chaco**. Leé y seguí `AGENTS.md` (raíz, fuente
de verdad). Foco: **solo el análisis**. Dejá los sub-issues propuestos listados pero
no los crees (eso es `/analisis-issue`).

1. **Épica padre:** `gh issue list --label epica --state open`. Elegí y confirmá que
   el análisis encaja. Si no hay épica, sugerí `/analisis-epica` primero.
2. **Investigación activa** (obligatoria): código real + issues. Dejá escrito
   duplicidad, funcionalidades relacionadas, impacto crítico e inconsistencias.
3. **Interrogatorio** por cada sección de la estructura canónica del análisis. Cada
   hueco = pregunta concreta. No rellenes con supuestos.
4. **Control estricto:** no avances con preguntas abiertas, contradicciones,
   duplicidad sin resolver, impacto crítico no contemplado o criterios no verificables.
5. Creá el issue (label `analisis`) con `Épica padre: #NN`, en **Backlog**,
   **Tipo = Analisis** (receta `gh` de `AGENTS.md`). Actualizá "Análisis vinculados"
   en la épica.
6. Reportá el número y los sub-issues propuestos.

Si no podés ejecutar `gh`, dejá el cuerpo del issue y los comandos listos para copiar.
