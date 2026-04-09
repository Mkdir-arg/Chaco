# Requerimiento: Mapa completo de roles y permisos del sistema

**Estado:** ABIERTO
**Fecha:** 2026-03-09
**Origen:** Sesión /definir — Roles y permisos, mapa completo del sistema

---

## Contexto

El sistema tenía roles definidos de forma parcial y dispersa por módulo, con nombres inconsistentes (mezcla de español/inglés, mayúsculas sin criterio). Esta sesión cerró el mapa completo de roles y acordó los nombres definitivos.

---

## Definiciones acordadas

### Principios generales

- Todos los roles son **grupos Django** — sin jerarquía entre ellos
- Un usuario puede tener **múltiples roles simultáneamente**
- Un usuario sin roles en el backoffice **no puede acceder a ninguna sección**
- El **portal ciudadano** es completamente separado del backoffice
- Los roles son **independientes del dominio técnico** — se asignan por función del usuario

### Mapa de roles operativos

| Módulo | Rol | Qué permite |
|--------|-----|------------|
| **Ciudadanos** | `ciudadanoVer` | Ver ficha del ciudadano (sin campos sensibles) |
| | `ciudadanoCrear` | Crear y editar ciudadanos |
| | `ciudadanoSensible` | Ver campos de salud, documentación migratoria y campos marcados como sensibles |
| **Instituciones** | `institucionVer` | Ver el catálogo de instituciones y sus datos |
| | `institucionAdministrar` | Crear, editar, aprobar/rechazar instituciones |
| **Programas — configuración** | `secretariaConfigurar` | Crear y editar Secretarías y Subsecretarías |
| | `programaConfigurar` | Crear y configurar programas (wizard, flujo, capacidades) |
| **Programas — operativa** | `programaOperar` | Gestionar inscripciones, derivaciones, seguimiento de ciudadanos en programas |
| **Turnos — configuración** | `turnoConfigurar` | Crear y configurar `ConfiguracionTurnos` (horarios, modos, disponibilidades) |
| **Turnos — operativa** | `turnoOperar` | Gestionar agenda: confirmar, rechazar, cancelar turnos |
| **Conversaciones** | `conversacionOperar` | Acceder a la bandeja de conversaciones y responder ciudadanos |
| **Dashboard** | `dashboardVer` | Ver métricas e indicadores del panel de control |
| **Configuración sistema** | `sistemaConfigurar` | Gestionar parámetros globales del sistema |
| **Usuarios y roles** | `usuarioAdministrar` | Crear usuarios, asignar y revocar roles |
| **Reportes** | `reportesVer` | Ver y exportar reportes |

### Roles especiales

| Rol especial | Naturaleza | Qué permite |
|-------------|-----------|------------|
| `is_superuser` | Flag Django | Acceso total — solo para DevOps/soporte técnico, nunca operativo |
| `Ciudadanos` | Grupo Django | Usuarios del portal ciudadano — no acceden al backoffice |
| `EncargadoInstitucion` | Grupo Django | Representante externo de ONG — acceso limitado a su institución |

### Nombres a migrar (código existente → nombre acordado)

| Nombre en código | Nombre acordado | Estado |
|-----------------|----------------|--------|
| `configurarSecretaria` | `secretariaConfigurar` | Pendiente de migrar en US-011 |
| `ConfiguracionPrograma` | `programaConfigurar` | Pendiente de migrar en US-011 |
| `Administradores de Turnos` | `turnoConfigurar` | Pendiente de migrar en US-011 |

---

## Criterios de aceptación

### Fase 1 — Creación de grupos Django (US-011)
- [ ] Todos los roles listados existen como grupos Django en la base de datos
- [ ] Los nombres viejos (`configurarSecretaria`, `ConfiguracionPrograma`, `Administradores de Turnos`) son migrados a los nombres nuevos
- [ ] Los usuarios existentes con esos roles mantienen sus permisos tras la migración
- [ ] La migración se ejecuta como data migration o management command (no manual)

### Fase 2 — Protección de vistas por rol
- [ ] Cada vista del backoffice tiene el decorador/mixin correspondiente al rol requerido
- [ ] Un usuario sin el rol correcto recibe redirección con mensaje explicativo, no error 403
- [ ] Las vistas que requieren múltiples roles (ej: ver ciudadano = `ciudadanoVer` O `ciudadanoCrear`) tienen la lógica combinada correctamente
- [ ] El portal ciudadano rechaza a usuarios del backoffice y viceversa

### Fase 3 — Interfaz de gestión de usuarios
- [ ] `usuarioAdministrar` puede crear usuarios y asignar grupos desde el backoffice
- [ ] La interfaz muestra los roles como checkboxes con el nombre legible (no el técnico)
- [ ] No es necesario entrar al `/admin/` de Django para asignar roles

---

## Orden de implementación sugerido

1. `/feature` — Data migration: crear todos los grupos + migrar nombres existentes (US-011)
2. Aplicar roles en vistas a medida que se implementan las features de cada módulo (inline con cada US)
3. `/feature` — Interfaz de gestión de usuarios con asignación de roles (depende de US-011)

---

## Preguntas que quedaron abiertas

- [ ] ¿El `EncargadoInstitucion` puede ver ciudadanos que pasaron por su institución? (afecta `ciudadanoVer`)
- [ ] ¿Hay roles dentro de un programa específico (no a nivel sistema)? — relevante para US-012 (inscripción/derivación)
- [ ] ¿`dashboardVer` es un rol que se asigna manualmente o lo tiene todo usuario del backoffice por defecto?
- [ ] ¿`reportesVer` puede filtrar solo sus datos o ve reportes globales?
