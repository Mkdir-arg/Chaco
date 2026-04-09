# Sistema de Documentación Automática

Sistema completo de documentación, versionado y gestión de Pull Requests para SistemSo.

## Características

✅ **Documentación automática de PRs**: Cada PR genera su propia documentación
✅ **Versionado semántico automático**: Basado en Conventional Commits
✅ **CHANGELOG automático**: Se actualiza con cada release
✅ **Documentación por versión**: Historial completo de cambios
✅ **Sitio web de documentación**: MkDocs con Material theme
✅ **Trazabilidad completa**: De código a documentación

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Repository                     │
└────────────┬────────────────────────────────────────────┘
             │
             ├─► Pull Request abierto/actualizado
             │   └─► Workflow: pr-documentation.yml
             │       └─► Genera: documentos/prs/PR-XXX.md
             │
             ├─► Push a main/Dev
             │   ├─► Workflow: release.yml
             │   │   ├─► Analiza commits (Conventional Commits)
             │   │   ├─► Calcula nueva versión (SemVer)
             │   │   ├─► Actualiza CHANGELOG.md
             │   │   ├─► Genera documentos/versiones/vX.X.X.md
             │   │   └─► Crea tag y release en GitHub
             │   │
             │   └─► Workflow: deploy-docs.yml
             │       ├─► Build con MkDocs
             │       └─► Deploy a GitHub Pages
             │
             └─► Resultado: Documentación siempre actualizada
```

## Workflows de GitHub Actions

### 1. PR Documentation (`pr-documentation.yml`)

**Trigger**: Cuando se abre o actualiza un PR

**Acciones**:
- Analiza archivos modificados
- Detecta módulos afectados
- Identifica tipo de cambio (feat/fix/breaking)
- Genera documento completo del PR
- Commit automático a la rama del PR

**Resultado**: `documentos/prs/PR-{numero}.md`

### 2. Release & Changelog (`release.yml`)

**Trigger**: Push a `main` o `Dev`

**Acciones**:
- Analiza commits desde última versión
- Calcula nueva versión según SemVer
- Genera/actualiza CHANGELOG.md
- Crea documentación de versión
- Crea tag y release en GitHub

**Resultado**: 
- Tag: `vX.X.X`
- `CHANGELOG.md` actualizado
- `documentos/versiones/vX.X.X.md`

### 3. Deploy Documentation (`deploy-docs.yml`)

**Trigger**: Push a `main` o `Dev` (cambios en `documentos/`)

**Acciones**:
- Build del sitio con MkDocs
- Deploy a GitHub Pages

**Resultado**: Sitio web en `https://{usuario}.github.io/{repo}/`

## Convenciones de Commits

El sistema usa [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<alcance>): <descripción>
```

### Tipos principales:

- `feat`: Nueva funcionalidad → Incrementa MINOR
- `fix`: Corrección de bug → Incrementa PATCH
- `perf`: Mejora de performance → Incrementa PATCH
- Breaking change → Incrementa MAJOR

Ver [CONVENCIONES_COMMITS.md](CONVENCIONES_COMMITS.md) para detalles completos.

## Estructura de Documentación

```
documentos/
├── index.md                          # Página principal
├── arquitectura/
│   └── ARQUITECTURA_v1.0_2025-02-06.md
├── prs/
│   ├── index.md
│   ├── PR-1.md
│   ├── PR-2.md
│   └── ...
├── versiones/
│   ├── index.md
│   ├── v1.0.0.md
│   ├── v1.1.0.md
│   └── ...
└── CONVENCIONES_COMMITS.md

CHANGELOG.md                          # Raíz del proyecto
mkdocs.yml                            # Configuración MkDocs
```

## Configuración Inicial

### 1. Habilitar GitHub Pages

1. Ir a Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages` / `root`
4. Save

### 2. Configurar Permisos de Workflows

1. Ir a Settings → Actions → General
2. Workflow permissions: **Read and write permissions**
3. Allow GitHub Actions to create and approve pull requests: ✅

### 3. Variables de Entorno (opcional)

Si necesitas tokens adicionales:

```bash
Settings → Secrets and variables → Actions → New repository secret
```

## Uso

### Para Desarrolladores

1. **Crear rama**:
   ```bash
   git checkout -b feat/nueva-funcionalidad
   ```

2. **Hacer commits siguiendo convenciones**:
   ```bash
   git commit -m "feat(conversaciones): agregar notificaciones push"
   ```

3. **Crear Pull Request**:
   - El sistema genera automáticamente la documentación del PR
   - Revisar `documentos/prs/PR-XXX.md`

4. **Merge a Dev/main**:
   - El sistema calcula la nueva versión
   - Actualiza CHANGELOG
   - Genera documentación de versión
   - Publica en GitHub Pages

### Comandos Útiles

```bash
# Ver documentación localmente
pip install mkdocs mkdocs-material
mkdocs serve
# Abrir http://localhost:8000

# Build manual
mkdocs build

# Validar commits (opcional)
npm install -g @commitlint/cli @commitlint/config-conventional
echo "feat(core): test" | commitlint
```

## Sitio de Documentación

Una vez configurado, la documentación estará disponible en:

```
https://mkdir-arg.github.io/SistemSo/
```

### Secciones:

- **Inicio**: Visión general del proyecto
- **Arquitectura**: Documentación técnica completa
- **Pull Requests**: Historial de PRs con detalles
- **Versiones**: Documentación por versión
- **CHANGELOG**: Registro de cambios

## Mantenimiento

### Actualizar Documentación Manual

Si necesitas actualizar documentación manualmente:

```bash
# Editar archivos en documentos/
vim documentos/arquitectura/nueva-doc.md

# Commit
git add documentos/
git commit -m "docs(arquitectura): actualizar diagrama de componentes"
git push

# El workflow deploy-docs.yml se ejecuta automáticamente
```

### Forzar Nueva Versión

```bash
# Commit con breaking change
git commit -m "feat(api)!: cambiar estructura de respuesta

BREAKING CHANGE: Los endpoints ahora retornan formato diferente"

# Push a main
git push origin main

# Se genera versión MAJOR automáticamente
```

## Troubleshooting

### El workflow no se ejecuta

- Verificar permisos en Settings → Actions
- Verificar que los workflows estén en `.github/workflows/`
- Revisar Actions tab para ver errores

### La documentación no se publica

- Verificar que GitHub Pages esté habilitado
- Verificar rama `gh-pages` existe
- Revisar logs del workflow `deploy-docs`

### La versión no se incrementa

- Verificar que los commits sigan Conventional Commits
- Revisar logs del workflow `release`
- Verificar que haya cambios desde última versión

## Beneficios

✅ **Cero mantenimiento manual**: Todo se genera automáticamente
✅ **Siempre actualizada**: La documentación refleja el código real
✅ **Trazabilidad completa**: De commit a versión a documentación
✅ **Onboarding rápido**: Nuevos desarrolladores tienen toda la info
✅ **Auditoría**: Historial completo de cambios
✅ **Profesional**: Sitio web navegable y visualmente atractivo

## Referencias

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [MkDocs](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [semantic-release](https://semantic-release.gitbook.io/)
