# Guia de Contribución — Proyecto Chaco

Este documento define las convenciones de trabajo en el repositorio.
Leer antes de abrir una rama, hacer un commit o abrir un PR.

---

## 1. Convención de ramas

| Prefijo | Uso | Ejemplo |
|---------|-----|---------|
| `feature/` | Nueva funcionalidad | `feature/consulta-tramites` |
| `bugfix/` | Corrección de un bug | `bugfix/error-guardado-legajo` |
| `hotfix/` | Corrección urgente en producción | `hotfix/login-caido` |
| `docs/` | Cambios solo de documentación | `docs/actualizar-methodology` |
| `chore/` | Mantenimiento, refactor, dependencias | `chore/actualizar-requirements` |

**Reglas:**
- El nombre de la rama debe ser en minúsculas con guiones, sin acentos ni espacios.
- Debe incluir referencia al issue cuando aplique: `feature/12-consulta-tramites`.
- No trabajar directamente sobre `main`.

---

## 2. Convención de commits (Conventional Commits en español)

Formato: `tipo(alcance opcional): descripción en minúsculas`

| Tipo | Cuándo usarlo |
|------|--------------|
| `feat` | Nueva funcionalidad o requerimiento |
| `fix` | Corrección de un bug |
| `docs` | Cambios en documentación |
| `refactor` | Refactor sin cambio funcional |
| `test` | Agregar o mejorar tests |
| `chore` | Mantenimiento, dependencias, configuración |
| `style` | Formato, sangría, sin cambio de lógica |
| `perf` | Mejora de rendimiento |
| `ci` | Cambios en workflows de CI/CD |

**Ejemplos:**
```
feat(tramites): agregar vista de consulta de estado por ciudadano
fix(legajos): corregir error 500 al guardar sin campo obligatorio
docs(methodology): actualizar flujo de aprobación del cliente
refactor(core): extraer lógica de permisos a mixin reutilizable
chore: actualizar dependencias de requirements.txt
```

**Reglas:**
- Descripción en español, minúsculas, sin punto final.
- Longitud máxima del subject: 72 caracteres.
- Para breaking changes, agregar `!` después del tipo: `feat!: cambiar API de tramites`.

---

## 3. Reglas de Pull Request

- **Un PR = un issue principal.** Si hay múltiples issues, abrí PRs separados.
- El PR debe referenciar el issue: `Closes #número`.
- Usar el template en `.github/PULL_REQUEST_TEMPLATE.md`.
- El título del PR sigue la misma convención que los commits.
- **No se puede mergear sin aprobación del cliente registrada en el issue.**
- Al menos **1 revisión aprobada** del equipo antes de mergear.
- Los checks de CI deben pasar (docs build + lint).

---

## 4. Política de merge

- **Squash and merge** como estrategia predeterminada para mantener un historial limpio.
- Excepción: ramas `hotfix/` pueden usar merge directo si la urgencia lo requiere.
- Eliminar la rama después del merge (GitHub lo hace automáticamente si está configurado).
- No hacer force push sobre `main`.

---

## 5. Flujo completo de trabajo

```
1. Verificar que el issue tiene aprobación del cliente (estado: Aprobado)
2. Crear rama desde main: git checkout -b feature/12-nombre-feature
3. Desarrollar con commits frecuentes y descriptivos
4. Abrir PR usando el template
5. Esperar revisión del equipo
6. Mergear con squash una vez aprobado
7. Eliminar rama local y remota
8. Cerrar issue con consumo real de horas
```

---

## 6. Stack y convenciones técnicas

- Python 3.12, Django 4.2, MySQL 8
- Django Forms/ModelForms para formularios del backoffice
- Templates backoffice: extender `includes/base.html`
- Templates portal: extender `portal/base.html`
- Crear migraciones inmediatamente después de cambiar modelos
- Confirmaciones destructivas: SweetAlert2, nunca `confirm()` nativo

---

## 7. Contacto y dudas

Ante dudas sobre alcance o implementación, consultá el issue correspondiente
o el canal oficial del proyecto antes de empezar el desarrollo.
