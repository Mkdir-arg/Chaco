# Workflow del equipo

## Estrategia de branches

```
main          → producción, siempre estable
develop       → integración, base para features
feature/xxx   → nueva funcionalidad
fix/xxx       → corrección de bug
hotfix/xxx    → corrección urgente directo a main
```

## Flujo estándar

```bash
# 1. Partir siempre desde develop actualizado
git checkout develop
git pull origin develop

# 2. Crear branch con nombre descriptivo
git checkout -b feature/nachec-cierre-automatico

# 3. Trabajar en commits pequeños y descriptivos
git commit -m "feat(nachec): agregar lógica de cierre automático por inactividad"

# 4. Push y abrir PR hacia develop
git push origin feature/nachec-cierre-automatico
```

## Convención de commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(app): descripción corta
fix(app): descripción corta
refactor(app): descripción corta
docs: descripción corta
test(app): descripción corta
chore: descripción corta
```

Ejemplos reales:
```
feat(legajos): agregar filtro por programa en lista de ciudadanos
fix(portal): corregir redirect después de login con sesión expirada
refactor(conversaciones): extraer lógica de cola a service dedicado
```

## Proceso de PR

1. El PR debe tener título descriptivo siguiendo la convención de commits
2. Completar el template de PR (`.github/PULL_REQUEST_TEMPLATE.md`)
3. Al menos 1 aprobación requerida antes de mergear
4. El autor del PR es responsable de resolver conflictos
5. Mergear con **Squash and merge** hacia develop

## Merge a main

Solo el tech lead o responsable hace merge de develop → main.
Siempre acompañado de un tag de versión:

```bash
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

## Qué NO hacer

- No pushear directo a `main` ni a `develop`
- No dejar branches sin PR por más de 1 semana
- No mergear sin aprobación
- No incluir credenciales ni `.env` en commits
