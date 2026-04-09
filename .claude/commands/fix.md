# Comando /fix

Corrige un bug encontrado en desarrollo o staging. Flujo mas corto que /feature: sin user story, directo al diagnostico.

**Uso:** `/fix [descripcion del bug]`

---

## Comportamiento del orquestador

No hay Fase 1 de Product Owner. Se arranca directamente con el diagnostico.
El usuario solo aprueba el avance entre fases.
Si el bug requiere cambios de diseño mayores → escalar a `/feature`.

---

## FASE 1 — Diagnostico

Activar el agente `debugger` con la descripcion del bug.

Presentar al usuario:

**Diagnostico:**
- Causa raiz: [una oracion]
- Ubicacion: `archivo:linea`
- Por que ocurre: [explicacion breve]
- Alcance: ¿afecta otros modulos? Si/No — [cuales]

**Fix propuesto:**
- Cambios necesarios: [lista de archivos y que cambia en cada uno]
- Requiere migracion: Si/No
- Riesgo del fix: Bajo / Medio / Alto — [por que]

Leer `docs/features/_index.md` y el archivo de la funcionalidad afectada si existe, para verificar si este bug tiene antecedentes.

Terminar con:
> "Fase 1 completada. ¿Aprobamos este diagnostico y aplicamos el fix?"

**ESPERAR RESPUESTA. No continuar hasta recibir aprobacion.**

---

## FASE 2 — Implementacion del fix

Activar el agente `django-developer` con el diagnostico aprobado.

Reglas estrictas para un fix:
- Cambiar SOLO lo necesario para corregir el bug — nada mas
- No refactorizar codigo que no sea parte del bug
- No agregar funcionalidad nueva
- Si se modifica un model → generar migracion inmediatamente

Al terminar, presentar:

**Archivos modificados:**
- `ruta/archivo.py` — descripcion del cambio puntual

Terminar con:
> "Fase 2 completada. ¿Procedemos con la revision?"

**ESPERAR RESPUESTA. No continuar hasta recibir aprobacion.**

---

## FASE 3 — Revision

Activar el agente `code-reviewer` sobre los archivos modificados.

Foco especial para un fix:
- [ ] El cambio resuelve el bug sin introducir regresiones
- [ ] No se modifico nada fuera del alcance del fix
- [ ] Si habia test para este modulo → el fix no lo rompe
- [ ] Checklist estandar de seguridad y Django

Si todo PASS:
> "Fase 3 completada. ¿Procedemos con la documentacion?"

Si hay FAILs → volver a Fase 2 automaticamente sin consultar.

**ESPERAR RESPUESTA DEL USUARIO solo cuando todo sea PASS.**

---

## FASE 4 — Documentacion

Sin necesidad de aprobacion previa.

1. Determinar el slug de la funcionalidad afectada (minusculas-con-guiones)
2. Crear el archivo en `docs/fix/[slug]/[YYYY-MM-DD]_fix_[titulo-breve].md`
   - Si la carpeta no existe → crearla
   - Usar `docs/fix/_template.md` como base
   - Completar todos los campos
3. Actualizar `docs/fix/_index.md` agregando la fila
4. Agregar entrada en `docs/team/changelog.md`

Terminar con:
> "Fix completado. Documentado en docs/fix/[slug]/[fecha]_fix_[titulo].md"

---

## Cuando escalar a /feature

Si durante el diagnostico se detecta que el fix requiere:
- Cambio de schema de base de datos no trivial
- Refactor de arquitectura
- Nueva funcionalidad para resolver el problema de raiz

→ Informar al usuario y sugerir abrir un `/feature` en su lugar.
