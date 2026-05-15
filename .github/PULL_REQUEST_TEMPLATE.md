## Issue relacionado

Closes #<!-- número del issue principal -->

> **Regla:** Un PR debe resolver un único issue principal. Si hay más de uno, abrí PRs separados.

---

## Resumen funcional

<!-- Describí en 2-3 oraciones qué cambio funcional introduce este PR desde la perspectiva del usuario o del sistema -->

---

## Cambios técnicos

<!-- Listá los archivos y módulos modificados con una descripción de cada cambio -->

- `ruta/archivo.py` — descripción del cambio
- `ruta/template.html` — descripción del cambio

---

## Criterios de aceptación cubiertos

<!-- Copiá los criterios del issue y marcá los que este PR cubre -->

- [ ] Criterio 1 del issue
- [ ] Criterio 2 del issue

---

## Evidencia de pruebas

<!-- Describí cómo probaste los cambios. Adjuntá capturas si aplica -->

- Entorno probado: <!-- staging / local / producción -->
- Casos probados:
  - [ ] Flujo principal
  - [ ] Casos borde
  - [ ] Regresión de funcionalidades existentes

---

## Impacto en documentación

- [ ] Este cambio requiere actualización de documentación en GitHub Pages
- [ ] La documentación ya fue actualizada (indicar archivo)
- [ ] No requiere cambios en documentación

---

## Checklist de despliegue

- [ ] ¿Hay migraciones de base de datos? (si es sí, documentar en el issue)
- [ ] ¿Hay cambios en variables de entorno o configuración?
- [ ] ¿Hay cambios en dependencias (requirements.txt)?
- [ ] ¿Se requiere reiniciar servicios post-deploy?
- [ ] ¿Se notificó al equipo de infraestructura?

---

## Validación de seguridad y permisos

- [ ] Los endpoints nuevos tienen decoradores de autenticación/permisos
- [ ] No se exponen datos sensibles en logs ni responses
- [ ] No hay credenciales hardcodeadas en el código

---

## Definition of Done (DoD)

- [ ] El código sigue las convenciones del proyecto (ver CONTRIBUTING.md)
- [ ] Se crearon las migraciones necesarias (si aplica)
- [ ] Los tests existentes siguen pasando (`manage.py check`)
- [ ] El PR apunta a `main` o a la rama correcta
- [ ] El issue fue aprobado por el cliente antes de iniciar este PR
- [ ] El nombre del PR sigue Conventional Commits en español
