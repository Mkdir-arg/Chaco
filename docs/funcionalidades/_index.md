# Indice de Funcionalidades

> Leer antes de iniciar cualquier tarea. Actualizado por el Documentador en cada Fase 5.
> Cada funcionalidad tiene su propia carpeta con documentos versionados.

## Indice

| Funcionalidad | Carpeta | Version actual | Ultima actualizacion |
|--------------|---------|---------------|---------------------|
| Confirmar Ciudadano RENAPER | `confirmar-ciudadano-renaper/` | v1.0 | 2026-03-04 |
| Mejora de Logging | `mejora-logging/` | v1.0 | 2026-03-05 |
| Portal Ciudadano — Autenticacion y Registro | `portal-ciudadano/` | v1.0 | 2026-03-08 |
| Gestión de Ciudadanos | `gestion-ciudadanos/` | v1.0 | 2026-03-09 |
| Legajo de Atención | `legajo-atencion/` | v1.0 | 2026-03-09 |
| Programas Sociales | `programas-sociales/` | v1.2 | 2026-03-15 |
| ÑACHEC | `nachec/` | v1.0 | 2026-03-09 |
| Instituciones | `instituciones/` | v1.2 | 2026-03-15 |
| Alertas | `alertas/` | v1.0 | 2026-03-09 |
| Conversaciones — Chat Interno | `conversaciones-chat/` | v1.0 | 2026-03-09 |
| Contactos y Red de Vínculos | `contactos-red/` | v1.0 | 2026-03-09 |
| Usuarios y Permisos | `usuarios-permisos/` | v1.1 | 2026-03-15 |
| Dashboard | `dashboard/` | v1.0 | 2026-03-09 |
| Auditoría | `auditoria/` | v1.0 | 2026-03-09 |
| Configuración del Sistema | `configuracion-sistema/` | v1.1 | 2026-03-15 |
| Búsqueda Rápida Ciudadano | `busqueda-rapida-ciudadano/` | v1.0 | 2026-03-15 |
| Refactor DX Interno | `refactor-dx/` | v1.58 | 2026-04-03 |
| Derivación e Inscripción a Programas | `derivacion-inscripcion-programas/` | v1.0 | 2026-03-15 |
| Actividades Institucionales | `actividades-institucionales/` | v1.2 | 2026-03-19 |
| Ficha del Ciudadano — Perfil Social | `ficha-ciudadano/` | v1.0 | 2026-03-19 |
| Hub del Ciudadano | `hub-ciudadano/` | v1.1 | 2026-03-19 |

---

## Convencion de nombres

- Carpeta: `[slug-funcionalidad]/` — minusculas con guiones
- Documento: `v[X.Y]_[titulo-breve].md`
  - X = version mayor (cambio de arquitectura o modelo)
  - Y = version menor (mejora o ajuste dentro de la funcionalidad)
  - Ejemplo: `v1.0_alta-ciudadano-renaper.md`, `v1.1_agregar-foto-perfil.md`

Cuando se agrega una version nueva → crear un archivo nuevo (no editar el anterior).
El archivo mas reciente es el estado actual.

---

## Aplicaciones del proyecto

| App | Descripcion |
|-----|------------|
| `legajos` | Ciudadanos, legajos de atencion, programas, NACHEC, contactos, institucional |
| `core` | Modelos base, institucion, auditoria, configuracion geografica |
| `portal` | Portal ciudadano, registro instituciones |
| `conversaciones` | Sistema de chat ciudadano-operador |
| `configuracion` | Vistas de configuracion del sistema (geografía, instituciones) |
| `users` | Usuarios del backoffice y permisos |
| `dashboard` | Panel principal |
| `refactor-dx` | Documentación de slices internos de arquitectura y DX |
