# Reglas de documentación — Chaco

Estas reglas aplican a todos los agentes y a cualquier tarea que involucre documentación.

---

## Estructura de documentación

```
docs/internal/   → equipo de desarrollo, NUNCA se publica
docs/client/     → clientes/instituciones, se publica en GitHub Pages via MkDocs
```

**Regla absoluta:** ningún contenido de `docs/internal/` debe aparecer en `docs/client/` ni en `mkdocs.yml`.

---

## Qué va en cada lugar

### `docs/internal/` — documentación del equipo

| Archivo | Cuándo actualizarlo |
|---|---|
| `architecture.md` | Al cambiar el stack, agregar apps o modificar el patrón de capas |
| `setup.md` | Al cambiar dependencias, variables de entorno o pasos de instalación |
| `onboarding.md` | Al cambiar convenciones, accesos o contexto del dominio |
| `workflow.md` | Al cambiar branching strategy, convención de commits o proceso de PR |
| `roadmap.md` | Al cerrar un trimestre o redefinir objetivos estratégicos |
| `processes.md` | Al cambiar el proceso de deploy, rollback o gestión de incidentes |
| `decisions/NNN-titulo.md` | Cada vez que se toma una decisión técnica relevante e irreversible |
| `analisis/NNN-nombre.md` | Cada vez que el functional-analyst cierra el alcance de un requerimiento |
| `sprints/YYYY-MM-DD-sprint-NNN.md` | Al iniciar un sprint (`/sprint-plan`) y al cerrarlo (`/sprint-review`) |

### `docs/client/` — documentación pública

| Archivo | Cuándo actualizarlo |
|---|---|
| `getting-started.md` | Al cambiar el flujo de acceso o configuración inicial |
| `modules/*.md` | Al agregar, modificar o eliminar funcionalidades visibles al usuario |
| `faq.md` | Al identificar preguntas recurrentes de usuarios reales |
| `changelog.md` | En cada release con cambios visibles para el cliente |
| `support.md` | Al cambiar canales de contacto o SLA |

### GitHub Issues / Projects — NO va en docs

- Tareas puntuales, bugs, features en progreso
- Discusiones de implementación específica
- Seguimiento de trabajo (quién, cuándo)
- Cualquier cosa que cambie en menos de 2 semanas

---

## Cuándo documentar

- **Siempre** al tomar una decisión técnica que afecte arquitectura → ADR en `docs/internal/decisions/`
- **Siempre** al cambiar el proceso de setup o deploy → `docs/internal/setup.md` o `processes.md`
- **Siempre** al lanzar una funcionalidad nueva visible al cliente → entrada en `docs/client/changelog.md` + módulo correspondiente
- **Siempre** al usar `/definir` → análisis funcional en `docs/internal/analisis/NNN-nombre.md`
- **Siempre** al usar `/sprint-plan` → documento de sprint en `docs/internal/sprints/YYYY-MM-DD-sprint-NNN.md`
- **Siempre** al usar `/sprint-review` → completar y cerrar el documento de sprint activo
- **Nunca** documentar algo que ya está claro en el código mismo

---

## Formato de ADR

Nombre: `docs/internal/decisions/NNN-titulo-en-kebab-case.md`

```markdown
# ADR NNN — Título

**Estado:** Propuesto | Aceptado | Deprecado | Rechazado
**Fecha:** YYYY-MM

## Contexto
## Decisión
## Opciones evaluadas
## Consecuencias
```

---

## Convención de nombres

- Carpetas: `kebab-case` en minúsculas
- Archivos: `kebab-case.md`
- ADRs: `NNN-titulo.md` con número secuencial de 3 dígitos
- Sin espacios, sin mayúsculas, sin caracteres especiales

---

## Responsabilidad por rol

| Agente | Documenta en |
|---|---|
| `backend-architect` | `docs/internal/architecture.md`, `docs/internal/decisions/` |
| `database-architect` | `docs/internal/decisions/` (decisiones de schema) |
| `django-developer` | `docs/internal/setup.md` si cambia el entorno; `docs/client/modules/` si cambia funcionalidad visible |
| `functional-analyst` | `docs/internal/analisis/`, `docs/internal/sprints/`, `docs/client/modules/` y `docs/client/faq.md` cuando la funcionalidad está completada |
| `ui-designer` | `docs/client/modules/` si cambia flujo de usuario |
| `code-reviewer` | No documenta, pero verifica que la documentación esté actualizada |
| `test-engineer` | No documenta en `docs/`, los tests son su documentación |
| `debugger` | `docs/internal/processes.md` si el bug revela un proceso roto |
| `security-auditor` | `docs/internal/decisions/` si la auditoría genera una decisión de arquitectura |
