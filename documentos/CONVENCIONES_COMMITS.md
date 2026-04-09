# Guía de Convenciones de Commits

Este proyecto utiliza [Conventional Commits](https://www.conventionalcommits.org/) para mantener un historial de cambios claro y generar documentación automática.

## Formato

```
<tipo>(<alcance>): <descripción>

[cuerpo opcional]

[nota de pie opcional]
```

## Tipos

### feat
Nueva funcionalidad para el usuario.

**Incrementa**: Versión MINOR (0.X.0)

**Ejemplos**:
```
feat(conversaciones): agregar notificaciones en tiempo real
feat(legajos): implementar búsqueda avanzada
feat(dashboard): nuevo widget de estadísticas
```

### fix
Corrección de un bug.

**Incrementa**: Versión PATCH (0.0.X)

**Ejemplos**:
```
fix(conversaciones): corregir error en paginación
fix(legajos): resolver problema de validación de DNI
fix(dashboard): arreglar cálculo de métricas
```

### refactor
Cambio en el código que no añade funcionalidad ni corrige bugs.

**Incrementa**: Ninguna (no genera release)

**Ejemplos**:
```
refactor(core): simplificar lógica de cache
refactor(conversaciones): extraer servicio de mensajería
```

### perf
Mejora de performance.

**Incrementa**: Versión PATCH (0.0.X)

**Ejemplos**:
```
perf(legajos): optimizar consultas de búsqueda
perf(dashboard): reducir tiempo de carga de gráficos
```

### docs
Cambios en documentación.

**Incrementa**: Ninguna (no genera release)

**Ejemplos**:
```
docs(arquitectura): actualizar diagrama de componentes
docs(readme): agregar instrucciones de deployment
```

### style
Cambios de formato (espacios, punto y coma, etc).

**Incrementa**: Ninguna (no genera release)

### test
Agregar o modificar tests.

**Incrementa**: Ninguna (no genera release)

### chore
Cambios en el proceso de build o herramientas auxiliares.

**Incrementa**: Ninguna (no genera release)

**Ejemplos**:
```
chore(deps): actualizar dependencias
chore(docker): optimizar Dockerfile
```

## Breaking Changes

Para cambios incompatibles con versiones anteriores:

**Incrementa**: Versión MAJOR (X.0.0)

### Opción 1: Usar `!` después del tipo
```
feat(api)!: cambiar estructura de respuesta de endpoints
```

### Opción 2: Agregar `BREAKING CHANGE` en el pie
```
feat(api): cambiar estructura de respuesta

BREAKING CHANGE: Los endpoints ahora retornan {data: ..., meta: ...}
en lugar de retornar directamente el array de datos.
```

## Alcance (Scope)

El alcance indica qué parte del código se modifica:

- `conversaciones`: Sistema de mensajería
- `legajos`: Gestión de legajos
- `dashboard`: Panel de control
- `core`: Funcionalidad central
- `users`: Sistema de usuarios
- `chatbot`: Bot de conversación
- `tramites`: Gestión de trámites
- `portal`: Portal público
- `configuracion`: Configuración del sistema
- `api`: APIs REST
- `deps`: Dependencias
- `docker`: Configuración de Docker

## Ejemplos Completos

### Nueva funcionalidad
```
feat(conversaciones): agregar sistema de archivos adjuntos

Permite a los operadores enviar y recibir archivos en las conversaciones.
Soporta imágenes, PDFs y documentos de Office.

- Validación de tipo de archivo
- Límite de 10MB por archivo
- Almacenamiento en media/conversaciones/
```

### Corrección de bug
```
fix(legajos): resolver error al guardar ciudadano sin DNI

El sistema fallaba cuando se intentaba guardar un ciudadano
sin número de DNI. Ahora el DNI es opcional y se valida
solo si está presente.

Closes #123
```

### Breaking change
```
feat(api)!: cambiar autenticación a JWT

BREAKING CHANGE: La autenticación por sesión ya no está soportada.
Todos los clientes deben migrar a JWT tokens.

Migración:
1. Obtener token en /api/auth/login/
2. Incluir header: Authorization: Bearer <token>
```

## Beneficios

✅ **Versionado automático**: El sistema calcula la versión según los commits
✅ **CHANGELOG automático**: Se genera sin intervención manual
✅ **Documentación de PRs**: Cada PR se documenta automáticamente
✅ **Trazabilidad**: Fácil identificar qué cambió y por qué
✅ **Comunicación clara**: El equipo entiende el impacto de cada cambio

## Herramientas

### Validación local
```bash
# Instalar commitlint (opcional)
npm install -g @commitlint/cli @commitlint/config-conventional

# Validar mensaje
echo "feat(core): nueva funcionalidad" | commitlint
```

### Git hooks (opcional)
```bash
# Instalar husky para validar commits
npm install -D husky @commitlint/cli @commitlint/config-conventional
npx husky install
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
```

## Referencias

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
