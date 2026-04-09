#!/usr/bin/env python3
"""
Script para generar estadísticas y actualizar la Home de documentación
Se ejecuta automáticamente en los workflows
"""
import os
import json
from datetime import datetime
from pathlib import Path

def count_files(directory, pattern="*.md"):
    """Cuenta archivos que coinciden con el patrón"""
    path = Path(directory)
    if not path.exists():
        return 0
    return len(list(path.glob(pattern)))

def get_latest_files(directory, pattern="*.md", limit=5):
    """Obtiene los archivos más recientes"""
    path = Path(directory)
    if not path.exists():
        return []
    files = sorted(path.glob(pattern), key=lambda x: x.stat().st_mtime, reverse=True)
    return [f.stem for f in files[:limit]]

def get_version_info():
    """Obtiene información de la versión actual"""
    try:
        import subprocess
        version = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0'], 
                                         stderr=subprocess.DEVNULL).decode().strip()
        return version
    except:
        return "v0.1.0"

def generate_stats():
    """Genera estadísticas del proyecto"""
    base_path = Path(__file__).parent.parent.parent
    docs_path = base_path / "documentos"
    
    stats = {
        "version": get_version_info(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "prs": count_files(docs_path / "prs", "PR-*.md"),
        "versions": len([d for d in (docs_path / "versiones").iterdir() if d.is_dir()]) if (docs_path / "versiones").exists() else 0,
        "features": count_files(docs_path / "funcionalidades"),
        "latest_features": get_latest_files(docs_path / "funcionalidades", limit=5)
    }
    
    return stats

def generate_home_dashboard(stats):
    """Genera el contenido de la home con dashboard visual"""
    
    features_list = "\n".join([f"- {f.replace('-', ' ').title()}" for f in stats['latest_features']]) if stats['latest_features'] else "- Sistema de documentación automática"
    
    content = f"""# 🏠 SistemSo - Centro de Documentación

Bienvenido al centro de documentación del proyecto SistemSo. Aquí encontrarás toda la información técnica y funcional del sistema, actualizada automáticamente.

---

## 📊 Estado del Proyecto

| Métrica | Valor |
|---------|-------|
| **Versión Actual** | {stats['version']} |
| **Última Actualización** | {stats['date']} |
| **Pull Requests Documentados** | {stats['prs']} |
| **Versiones Liberadas** | {stats['versions']} |
| **Funcionalidades** | {stats['features']} |

---

## 🗂️ Navegación Rápida

### 📐 Documentación Técnica

**[Arquitectura del Sistema](arquitectura/ARQUITECTURA_v1.0_2025-02-06.md)**  
Stack tecnológico, patrones de diseño, arquitectura de deployment y sistema de mensajería en tiempo real.  
*Última actualización: 2025-02-06*

**[Convenciones de Commits](CONVENCIONES_COMMITS.md)**  
Guía completa de Conventional Commits para mantener un historial claro y generar documentación automática.  
*Última actualización: {stats['date']}*

---

### 🔀 Pull Requests

**[Ver todos los PRs →](prs/index.md)**

Documentación detallada de cada Pull Request, incluyendo:
- ✅ Módulos afectados
- 📝 Archivos modificados
- 📊 Estadísticas de cambios
- 🎯 Impacto funcional

📈 **Total documentados**: {stats['prs']} PRs

---

### 🚀 Versiones del Sistema

**[Ver historial de versiones →](versiones/index.md)**

#### Última Versión: {stats['version']}

Liberada el {stats['date']}

**Características principales:**
- Sistema de documentación automática
- Versionado semántico
- Workflows de CI/CD
- Sitio de documentación web

[📖 Ver documentación completa de {stats['version']} →](versiones/{stats['version']}/index.md)

---

### ✨ Funcionalidades Recientes

{features_list}

[🔍 Ver todas las funcionalidades →](funcionalidades/index.md)

---

### 🧾 CHANGELOG

**[Ver CHANGELOG completo →](../CHANGELOG.md)**

Registro cronológico de todos los cambios del proyecto, actualizado automáticamente con cada release.

---

## 🎯 Guías Rápidas

### Para Desarrolladores

1. [Cómo hacer commits](CONVENCIONES_COMMITS.md#formato)
2. [Crear Pull Request](README.md#para-desarrolladores)
3. [Arquitectura](arquitectura/ARQUITECTURA_v1.0_2025-02-06.md)

### Para QA/Negocio

1. [Versiones](versiones/index.md) - Qué cambió
2. [Funcionalidades](funcionalidades/index.md) - Nuevas features
3. [CHANGELOG](../CHANGELOG.md) - Resumen de cambios

---

## 🔄 Actualización Automática

Esta documentación se actualiza automáticamente cuando:

- ✅ Se abre o actualiza un Pull Request
- ✅ Se hace merge a la rama principal
- ✅ Se libera una nueva versión
- ✅ Se agregan nuevas funcionalidades

**No requiere mantenimiento manual.**

---

## 📚 Recursos Adicionales

- [GitHub Repository](https://github.com/Mkdir-arg/SistemSo)
- [Sistema de Documentación](README.md)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

*Documentación generada automáticamente el {stats['date']}*  
*Versión del sistema: {stats['version']}*
"""
    
    return content

if __name__ == "__main__":
    stats = generate_stats()
    content = generate_home_dashboard(stats)
    
    output_path = Path(__file__).parent.parent.parent / "documentos" / "index.md"
    output_path.write_text(content, encoding='utf-8')
    
    print(f"✅ Home actualizada con éxito")
    print(f"📊 Estadísticas: {json.dumps(stats, indent=2)}")
