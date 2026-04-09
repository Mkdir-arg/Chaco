---
name: Búsqueda rápida de ciudadano por nombre o DNI
description: Funcionalidad de búsqueda rápida accesible desde el backoffice para encontrar ciudadanos por nombre parcial o DNI exacto durante atenciones telefónicas.
type: requerimiento
---

# Búsqueda rápida de ciudadano
> Estado: ABIERTO
> Fecha: 2026-03-12
> Prioridad: MEDIA
> Tipo: FEATURE

## Descripción

Los operadores necesitan encontrar ciudadanos rápidamente durante atenciones telefónicas. La búsqueda debe ser lo suficientemente ágil para no interrumpir la atención.

## Reglas de negocio

- Búsqueda por **nombre parcial** (nombre y/o apellido, case-insensitive)
- Búsqueda por **DNI exacto**
- Accesible desde cualquier pantalla del backoffice (header o atajo de teclado)
- Solo usuarios con `ciudadanoVer` pueden buscar
- Resultados muestran: foto, nombre completo, DNI, edad — suficiente para identificar sin abrir el legajo
- Click en resultado → navega al perfil del ciudadano

## Criterios de éxito

- [ ] El operador puede buscar un ciudadano por nombre parcial desde cualquier pantalla del backoffice
- [ ] El operador puede buscar por DNI exacto
- [ ] Los resultados aparecen sin recargar la página (AJAX)
- [ ] Cada resultado muestra foto, nombre completo, DNI y edad
- [ ] Click en un resultado navega al hub del ciudadano
- [ ] Solo usuarios con `ciudadanoVer` pueden usar la búsqueda
- [ ] La búsqueda responde en menos de 500ms para bases de hasta 10.000 ciudadanos
