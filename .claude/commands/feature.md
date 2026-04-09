# Comando /feature

Orquesta el equipo completo para implementar una feature. Los agentes se activan automáticamente en cada fase. El usuario solo aprueba o rechaza el avance entre fases.

---

## Comportamiento del orquestador

Cuando el usuario ejecuta `/feature [descripción]`:

1. Ejecuta cada fase usando el agente correspondiente (via Agent tool)
2. Presenta el resultado consolidado al usuario
3. PAUSA y espera aprobación antes de pasar a la siguiente fase
4. Si el usuario rechaza o pide cambios, repite la fase con los ajustes antes de continuar
5. Si durante la implementación aparece un error inesperado, activa `debugger` automáticamente sin consultar

---

## FASE 1 — Analisis Funcional

Activar el agente `functional-analyst` con la descripcion recibida.

El analista:
1. Lee `docs/features/_index.md` y el backlog para detectar conflictos con lo existente
2. Identifica ambiguedades y casos de uso secundarios
3. Si hay preguntas criticas sin respuesta → las presenta al usuario ANTES de escribir la user story
4. Escribe la user story con criterios de aceptacion verificables

Presentar el resultado consolidado al usuario:

**User Story:**
```
Como [rol especifico] quiero [accion concreta] para [beneficio medible]
```

**Criterios de aceptacion:**
- [ ] Dado [contexto], cuando [accion], entonces [resultado]
- [ ] Si [error], entonces [comportamiento]
- [ ] ...

**Complejidad:** Pequeno / Mediano / Grande
**Relacionada con:** [funcionalidad existente o "ninguna"]
**Fuera de alcance:** [que NO entra en esta user story]

Si el analista identifico preguntas criticas → presentarlas primero y esperar respuesta antes de mostrar la user story.

Terminar SIEMPRE con:
> "Fase 1 completada. ¿Aprobamos esta user story y arrancamos el diseño tecnico?"

**ESPERAR RESPUESTA. No continuar hasta recibir aprobacion.**

---

## FASE 2 — Arquitecto + Base de Datos

Activar el agente `backend-architect` para el diseño técnico general.
Activar el agente `database-architect` para el schema y migrations.

Consolidar ambas salidas y presentar al usuario en formato unificado:

**Diseño tecnico:**
- Apps afectadas: ...
- Archivos a modificar: (lista completa)
- Archivos nuevos a crear: (lista completa)
- Cambios de base de datos: (campos, tablas, relaciones)
- Requiere migracion: Si/No
- Estrategia de migracion si hay datos existentes: ...

**Analisis de impacto:**
- [ ] FKs o relaciones en otros models afectados
- [ ] Views que usan campos que se modifican
- [ ] Templates que muestran esos campos
- [ ] Formularios con esos campos
- [ ] Conflictos de nombres en URLs
- [ ] Registros existentes que quedan inconsistentes
- [ ] Campos obligatorios nuevos: como migran los datos existentes

**Riesgos identificados:** (si los hay, con propuesta de mitigacion)

Terminar SIEMPRE con:
> "Fase 2 completada. ¿Aprobamos este diseño y arrancamos la implementacion?"

**ESPERAR RESPUESTA. No continuar hasta recibir aprobacion.**

---

## FASE 3 — Implementacion

Activar el agente `django-developer` con el diseño aprobado en Fase 2.

El agente implementa en este orden obligatorio:
1. Models → makemigrations inmediatamente despues de cada cambio
2. Forms
3. Views
4. URLs
5. Templates (leer `docs/team/design-system.md` antes de escribir cualquier template)

Al terminar, presentar al usuario:

**Archivos modificados:**
- `ruta/archivo.py` — descripcion del cambio
- ...

**Archivos creados:**
- `ruta/archivo.py` — descripcion
- ...

**Migraciones generadas:** (si aplica)
- `app/migrations/XXXX_nombre.py`

Terminar SIEMPRE con:
> "Fase 3 completada. ¿Procedemos con la revision de calidad?"

**ESPERAR RESPUESTA. No continuar hasta recibir aprobacion.**

---

## FASE 4 — Revision

Activar el agente `code-reviewer` sobre todos los archivos modificados/creados en Fase 3.

Si el proyecto tiene componentes de autenticacion, permisos o manejo de datos sensibles involucrados en esta feature, activar tambien `security-auditor` y consolidar ambas salidas.

Presentar resultado consolidado:

**Revision de calidad:**
- [PASS/FAIL] Seguridad: @login_required, csrf_token, datos expuestos
- [PASS/FAIL] Django: migraciones, verbose_name, __str__, forms
- [PASS/FAIL] Frontend: base.html, Tailwind design system, SweetAlert2
- [PASS/FAIL] Impacto: nada roto de lo identificado en Fase 2

Si todo PASS:
> "Fase 4 completada. Todo correcto. ¿Procedemos con la documentacion?"

Si hay FAILs:
> "Fase 4: se encontraron problemas. Volviendo a Fase 3 para corregir."
Activar `django-developer` para corregir los puntos fallidos, luego repetir Fase 4 automaticamente.

**ESPERAR RESPUESTA DEL USUARIO solo cuando todo sea PASS.**

---

## FASE 5 — Documentacion (inline, sin agente dedicado)

Ejecutar automaticamente sin necesidad de aprobacion previa (Fase 4 ya fue aprobada):

### 5A — Documentacion de funcionalidad

Determinar el slug de la funcionalidad (minusculas-con-guiones, ej: `exportacion-pdf`, `registro-ciudadanos`).

**Crear el archivo de version en `docs/funcionalidades/[slug]/`:**

- Si la carpeta no existe → crearla
- Determinar la version: si no hay versiones previas → `v1.0`, si ya existe → incrementar el menor (`v1.1`, `v1.2`, etc.)
- Usar `docs/funcionalidades/_template.md` como base
- Nombre del archivo: `v[X.Y]_[titulo-breve].md`
- Completar todos los campos del template con lo implementado

**Actualizar el indice `docs/funcionalidades/_index.md`:**
- Si la funcionalidad es nueva → agregar fila a la tabla
- Si ya existe → actualizar version actual y fecha

### 5B — Documentacion del equipo

1. Agregar user story como completada en `docs/team/backlog.md`
2. Actualizar `docs/team/current-sprint.md`
3. Agregar entrada en `docs/team/changelog.md`
4. Si hubo decision tecnica importante → agregar ADR en `docs/team/decisions.md`
5. Si se uso patron de UI nuevo → actualizar `docs/team/design-system.md`
6. Si hay algo util para futuras sesiones → actualizar `memory/MEMORY.md`

Terminar SIEMPRE con:
> "Feature completada. Documentacion en docs/funcionalidades/[slug]/v[X.Y]_[titulo].md"

---

## Manejo de errores durante la implementacion

Si durante la Fase 3 aparece un error inesperado (excepcion, fallo de migracion, error de importacion):
- Activar `debugger` automaticamente
- Mostrar diagnostico al usuario
- Proponer fix y continuar sin interrumpir el flujo
- Si el fix requiere cambios de diseño, volver a Fase 2

---

## Regla de oro

El usuario NUNCA deberia tener que saber que agente esta activo.
Solo ve: resultado consolidado + una pregunta clara de aprobacion.
