# ✨ Funcionalidades

Catálogo completo de funcionalidades del sistema SistemSo.

## 📋 Cómo Funciona

Cada vez que se hace merge de un Pull Request con commits tipo `feat` a la rama Main, el sistema automáticamente:

1. Detecta las nuevas funcionalidades
2. Genera documentación detallada
3. Asocia la funcionalidad a la versión correspondiente
4. Actualiza este catálogo

## 📊 Estado Actual

Actualmente no hay funcionalidades documentadas automáticamente. Las funcionalidades se generarán cuando:

- Se haga merge de PRs con commits `feat(modulo): descripción`
- El workflow `merge-main.yml` se ejecute correctamente
- Se cree una nueva versión del sistema

## 🎯 Estructura de Documentación

Cada funcionalidad incluirá:

- **Nombre**: Descripción clara de la funcionalidad
- **Módulo**: Componente del sistema afectado
- **Versión**: En qué versión se introdujo
- **Descripción Funcional**: Qué hace la funcionalidad
- **Descripción Técnica**: Cómo está implementada
- **Impacto**: Qué cambia en el sistema
- **Referencias**: PR y commits relacionados

## 📦 Módulos del Sistema

Las funcionalidades se organizan por módulo:

### 🗂️ Core
Funcionalidad central del sistema

### 👥 Users
Sistema de usuarios y autenticación

### 📋 Legajos
Gestión de legajos y ciudadanos

### 💬 Conversaciones
Sistema de mensajería en tiempo real

### 📊 Dashboard
Panel de control y métricas

### 📄 Tramites
Gestión de trámites

### 🌐 Portal
Portal público

### ⚙️ Configuración
Configuración del sistema

## 🚀 Próximas Funcionalidades

Las funcionalidades se documentarán automáticamente conforme se desarrollen y se haga merge a Main.

---

*Esta página se actualiza automáticamente con cada nueva funcionalidad*
