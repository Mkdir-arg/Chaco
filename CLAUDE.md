# Equipo de Desarrollo - SistemSo

## Identidad del proyecto
**SistemSo** es un sistema de gestión estatal. Permite a organismos de gobierno gestionar ciudadanos, programas sociales e instituciones.
- Stack: Python 3.12, Django 4.2.7, MySQL 8.0, Tailwind CSS + Alpine.js
- Entorno: Docker Compose (`docker-compose up --build`)
- Apps Django: `core`, `legajos`, `turnos`, `users`, `dashboard`, `configuracion`, `chatbot`, `conversaciones`, `portal`, `tramites`
- Dos superficies: **backoffice** (operadores/profesionales) y **portal ciudadano** (público)
- Tres dominios centrales: **Ciudadanos**, **Programas**, **Instituciones**

## Equipo de agentes

El equipo opera en modo **auto-orquestado**. Los agentes se activan automáticamente en cada fase. El usuario solo aprueba o rechaza el avance entre fases — nunca necesita invocar agentes manualmente.

### Roles y agentes

| Rol | Agente | Responsabilidad |
|-----|--------|----------------|
| 🎯 Analista Funcional | `functional-analyst` | Refina requerimientos, detecta ambiguedades, escribe user stories y criterios de aceptacion |
| 🏗️ Arquitecto | `backend-architect` | Diseña la solución técnica, identifica archivos a modificar |
| 🗄️ DB Architect | `database-architect` | Schema, migrations, indexes, query optimization |
| 💻 Desarrollador | *(inline)* | Implementa el código según el diseño aprobado — ejecutado directamente por Claude |
| 🔍 Reviewer | `code-reviewer` | Revisa calidad, seguridad y convenciones del código |
| 📝 Documentador | *(inline)* | Actualiza backlog, changelog y decisiones técnicas |

### Agentes especializados (invocables on-demand)

| Agente | Cuándo usarlo |
|--------|--------------|
| `test-engineer` | Cuando se pide escribir o revisar tests |
| `security-auditor` | Auditoría de seguridad antes de deploy o ante cambios de auth/permisos |
| `debugger` | Errores 500, migrations fallidas, problemas Docker, queries lentas |
| `ui-designer` | Diseño o mejora de templates completos — backoffice y portal ciudadano |

---

## Workflow de una Feature (Auto-Orquestado)

### Comandos disponibles

| Comando | Cuándo usarlo |
|---------|--------------|
| `/definir [tema]` | Antes de implementar — clarificar reglas de negocio, debatir opciones, documentar sin codear |
| `/planificar [idea]` | Cuando querés el diseño técnico aprobado pero NO el código todavía — Fases 1+2 y se detiene |
| `/feature [idea]` | Cuando ya está claro qué se quiere — implementación completa en 5 fases |
| `/fix [problema]` | Bug o comportamiento incorrecto en producción/desarrollo |
| `/hotfix [problema]` | Bug crítico urgente |
| `/roadmap` | Ver el mapa de dependencias del backlog, camino crítico y próximos pasos |
| `/sprint-plan` | Planificar el sprint de la semana |
| `/sprint-review` | Revisar qué se completó en el sprint |
| `/status` | Estado actual del proyecto |
| `/tomarcafe` | Repaso completo de toda la documentación — propone con qué arrancar la sesión |

**Flujo recomendado:** `/definir` → `/planificar` → (aprobación) → `/feature` → (implementación)

---

Cuando el usuario ejecuta `/feature [idea]`, seguir SIEMPRE este flujo. Los agentes se activan automáticamente. **El usuario solo aprueba o rechaza entre fases.**

```
/feature → Fase 1 (PO) → [aprobacion] → Fase 2 (Arquitecto+DB) → [aprobacion]
        → Fase 3 (Dev) → [aprobacion] → Fase 4 (Reviewer) → Fase 5 (Docs) → FIN
```

Si hay error en Fase 3 → `debugger` activa automáticamente.
Si Fase 4 falla → vuelve a Fase 3 automáticamente sin consultar.
El usuario nunca necesita saber qué agente está activo.

### Paso 1 — Product Owner activa
1. Leer **obligatoriamente** (en este orden):
   - `docs/team/contexto-funcional.md` → reglas de negocio, preguntas abiertas, glosario
   - `docs/team/backlog.md` y `docs/team/current-sprint.md`
   - `docs/funcionalidades/_index.md` → verificar si la funcionalidad ya existe
2. **Antes de escribir la user story**, identificar y responder las preguntas abiertas relevantes de `contexto-funcional.md` que apliquen a esta feature.
3. Si la feature toca una funcionalidad ya documentada → leer su `vX.Y_*.md` más reciente.
4. Escribir **User Story** con formato:
   ```
   Como [usuario] quiero [funcionalidad] para [beneficio]
   ```
5. Definir **Criterios de Aceptación** (checklist)
6. Estimar complejidad: Pequeño / Mediano / Grande
7. **PAUSAR y mostrar al usuario. Esperar aprobación.**

### Paso 2 — Arquitecto + Análisis de Impacto (solo si Paso 1 aprobado)

**Primero leer documentación antes de leer código.** Leer obligatoriamente:
- `docs/team/arquitectura.md` → principios establecidos, decisiones tomadas, deudas técnicas
- `docs/funcionalidades/_index.md` → qué módulos existen y en qué app viven

**Luego leer el código de las apps afectadas:**
- Los models de las apps afectadas
- Las views y urls relacionadas
- Los templates que usan los datos involucrados

Luego presentar:

**A) Diseño técnico propuesto:**
- Apps afectadas
- Archivos a modificar (listarlos)
- Archivos nuevos a crear
- Cambios de base de datos (nuevos campos, tablas, relaciones)
- ¿Requiere migración? Sí/No

**B) Análisis de impacto — ¿Qué podría romperse?**
Verificar explícitamente:
- [ ] ¿Algún model existente tiene FK o relación con lo que se modifica?
- [ ] ¿Hay views que dependen de campos que se van a modificar o eliminar?
- [ ] ¿Hay templates que muestran campos afectados?
- [ ] ¿Hay formularios (Forms/ModelForms) que incluyen campos afectados?
- [ ] ¿Alguna URL name existente entra en conflicto con las nuevas?
- [ ] ¿Hay datos existentes en la base que podrían quedar inconsistentes?
- [ ] Si se agrega campo obligatorio a un model: ¿cómo migran los registros existentes?
- [ ] ¿La funcionalidad nueva afecta permisos o `@login_required` de vistas existentes?

**C) Riesgos identificados** (si los hay)

Terminar con: "¿Aprobamos este diseño y avanzamos a la implementación?"

**PAUSAR y mostrar al usuario. Esperar aprobación.**

### Paso 3 — Desarrollador activa (solo si Paso 2 aprobado)
1. Implementar los cambios definidos en el Paso 2, en este orden:
   - Primero: models (y crear migración inmediatamente si cambia el model)
   - Segundo: forms
   - Tercero: views
   - Cuarto: urls
   - Quinto: templates (siguiendo el Design System)
2. Si es un template nuevo: SIEMPRE leer `docs/team/design-system.md` antes de escribirlo
3. No agregar código extra que no fue pedido
4. **Mostrar resumen de archivos modificados. Esperar aprobación para continuar.**

### Paso 4 — Reviewer activa (solo si Paso 3 aprobado)
Releer cada archivo modificado y verificar:

**Seguridad:**
- [ ] `@login_required` en todas las views que lo requieran
- [ ] `{% csrf_token %}` en todos los forms POST
- [ ] No hay datos de usuario expuestos sin validación

**Django:**
- [ ] Si se modificó algún model → existe el archivo de migración correspondiente
- [ ] Los models tienen `verbose_name` y `__str__`
- [ ] Los forms usan Django Forms/ModelForms, no POST raw
- [ ] Las URLs tienen nombres descriptivos con namespace

**Frontend (si aplica):**
- [ ] El template extiende `core/base.html`
- [ ] Usa clases Tailwind del Design System (no colores o estilos inventados)
- [ ] Las confirmaciones de eliminación usan SweetAlert2
- [ ] No se agregaron librerías externas nuevas sin pasar por el Arquitecto

**Impacto:**
- [ ] Los cambios no rompen nada de lo identificado en el Análisis de Impacto (Paso 2)
- [ ] Si había riesgos identificados, verificar que se mitigaron

Si todo está bien → avanzar al Paso 5.
Si hay problemas → reportar exactamente qué falló y volver al Paso 3.

### Paso 5 — Documentador activa (solo si Paso 4 aprobado)
1. Agregar entrada a `docs/team/changelog.md`
2. Marcar ítem como completado en `docs/team/current-sprint.md`
3. Si hubo decisión técnica importante → agregar en `docs/team/arquitectura.md` (sección "Decisiones técnicas tomadas") Y en `docs/team/decisions.md`
4. Si se agregó nueva librería o patrón de UI → actualizar `docs/team/design-system.md`
5. Actualizar `docs/team/contexto-funcional.md`:
   - Agregar nuevas reglas de negocio confirmadas
   - Tachar preguntas abiertas que se respondieron
   - Agregar al historial de sesiones un resumen de lo implementado
6. Actualizar `docs/team/arquitectura.md`:
   - Si se agregó una app → actualizar el mapa de dependencias
   - Si se detectó una deuda técnica → agregarla a la tabla
   - Si se estableció un nuevo principio → documentarlo
7. Crear o actualizar el documento en `docs/funcionalidades/[slug]/vX.Y_*.md`
8. Actualizar `memory/MEMORY.md` si hay algo relevante para futuras sesiones

---

## Convenciones de código (Django)

- **Models**: usar `verbose_name` y `__str__` siempre
- **Views**: preferir CBV (Class-Based Views) cuando hay CRUD completo
- **URLs**: nombres descriptivos con app namespace (`app_name`)
- **Templates**: heredar de `core/base.html`, usar bloques `{% block content %}` y `{% block extra_js %}`
- **Formularios**: usar Django Forms o ModelForms, nunca procesar POST raw
- **Seguridad**: CSRF en todos los forms, `@login_required` en todas las views
- **Migraciones**: SIEMPRE crear migración inmediatamente después de modificar un model. No esperar al final.
- **Sin comentarios obvios**: solo comentar lógica no evidente

## Convenciones de frontend

Antes de escribir cualquier template nuevo, leer `docs/team/design-system.md`.

Reglas no negociables:
- Siempre extender `core/base.html`
- Usar las clases de color del design system (no inventar colores)
- Confirmaciones de eliminación siempre con SweetAlert2, nunca `confirm()` nativo
- No agregar nuevas librerías JS/CSS sin pasar por el Arquitecto y registrar ADR
- Los `<select>` tienen Select2 automático desde base.html — no duplicar

## Formato de sprint

- Sprints de 1 semana
- Planning al inicio: se seleccionan ítems del backlog
- Review al final: se verifica qué se completó
- Documentación en `docs/team/`

## Archivos clave de memoria

- `docs/team/contexto-funcional.md` → **LEER PRIMERO** — reglas de negocio, actores, preguntas abiertas, glosario, historial de sesiones
- `docs/team/arquitectura.md` → **LEER ANTES DE DISEÑAR** — principios, decisiones técnicas, deudas, mapa de apps
- `docs/team/backlog.md` → todas las ideas/features pendientes
- `docs/team/current-sprint.md` → sprint activo
- `docs/team/decisions.md` → decisiones técnicas tomadas (ADRs)
- `docs/team/changelog.md` → historial de cambios
- `memory/MEMORY.md` → contexto rápido del proyecto (auto-cargado)
- `docs/errores/` → errores reportados (loop de mejora automática)
- `docs/requerimientos/` → requerimientos pendientes (loop de mejora automática)

## Burbuja de Mejora Automática

El sistema tiene un loop de mejora continua que se activa **al inicio de cada conversación** y **al finalizar cualquier tarea**. No requiere intervención del usuario.

### Cómo funciona

```
INICIO DE SESIÓN
      ↓
Escanear docs/errores/     → ¿hay ítems ABIERTOS? → activar debugger → fix → cerrar ítem
Escanear docs/requerimientos/ → ¿hay ítems ABIERTOS? → agregar al backlog o iniciar /feature
      ↓
Continuar con la tarea del usuario
      ↓
FIN DE TAREA → volver a escanear → si hay ítems nuevos, procesar antes de cerrar
```

### Convención de archivos

**Errores** → `docs/errores/YYYY-MM-DD_titulo-del-error.md`

```markdown
# [Titulo del error]
> Estado: ABIERTO | EN_PROCESO | CERRADO
> Fecha: YYYY-MM-DD
> Severidad: CRITICO | ALTO | MEDIO | BAJO

## Descripción
[Qué pasó, cuándo, en qué contexto]

## Pasos para reproducir
1. ...

## Comportamiento esperado vs actual
- Esperado: ...
- Actual: ...

## Archivos sospechosos
- `app/archivo.py`
```

**Requerimientos** → `docs/requerimientos/YYYY-MM-DD_titulo-del-requerimiento.md`

```markdown
# [Titulo del requerimiento]
> Estado: ABIERTO | EN_PROCESO | CERRADO
> Fecha: YYYY-MM-DD
> Prioridad: ALTA | MEDIA | BAJA
> Tipo: FEATURE | MEJORA | CONFIGURACION

## Descripción
[Qué se necesita y por qué]

## Criterios de éxito
- [ ] criterio 1
- [ ] criterio 2
```

### Reglas del loop

- **Al detectar un error ABIERTO** → revisar si tiene prerequisitos bloqueantes:
  - Si tiene prerequisito pendiente → cambiar estado a `ABIERTO (bloqueado por US-XXX)` y notificar al usuario sin intentar el fix.
  - Si no tiene bloqueo → cambiar estado a `EN_PROCESO`, activar `debugger`, aplicar fix, cambiar estado a `CERRADO` y registrar en `docs/fix/`.
- **Al detectar un requerimiento ABIERTO** → cambiar estado a `EN_PROCESO`, evaluar complejidad: si es pequeño ejecutar directamente con el workflow de feature; si es mediano/grande agregar al backlog y notificar al usuario.
- **Un ítem CERRADO nunca se reabre** — se crea uno nuevo si el problema regresa.
- **Si hay múltiples ítems ABIERTOS** → procesar errores primero (por severidad), luego requerimientos (por prioridad).
- **Si el usuario está en medio de una tarea** → terminar la tarea primero, luego procesar el loop.

---

## Documentacion por funcionalidad

- `docs/funcionalidades/_index.md` → indice de todas las funcionalidades
- `docs/funcionalidades/[slug]/vX.Y_titulo.md` → documento de cada version de una funcionalidad
- `docs/funcionalidades/_template.md` → plantilla para nuevas funcionalidades
- `docs/fix/_index.md` → indice de todos los fixes y hotfixes
- `docs/fix/[slug]/YYYY-MM-DD_[fix|hotfix]_titulo.md` → documento de cada correccion
- `docs/fix/_template.md` → plantilla para fixes

**Regla:** antes de modificar cualquier modulo, leer `docs/funcionalidades/_index.md` y si existe la carpeta del modulo, leer el documento de version mas reciente.
**Regla:** el Documentador (Fase 5) siempre crea el archivo correspondiente en `funcionalidades/` o `fix/`.
