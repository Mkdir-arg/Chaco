# Análisis funcional NNN — [Nombre de la funcionalidad]

**Estado:** En análisis | Definido | En desarrollo | Completado | Descartado
**Fecha de análisis:** YYYY-MM-DD
**Analista:** functional-analyst
**Sprint asociado:** [link al sprint] o "Sin asignar"
**Módulo/App:** [nombre del módulo Django afectado]

---

## 1. Contexto y motivación

> Por qué existe este requerimiento. Qué problema resuelve. Quién lo pidió y en qué situación.
> Incluir el contexto del dominio necesario para entender la funcionalidad sin conocer el sistema de antemano.

[Descripción en prosa, mínimo 3 oraciones. No usar bullets acá.]

---

## 2. Actores involucrados

> Quiénes interactúan con esta funcionalidad, con qué rol y qué pueden hacer.

| Actor | Rol en el sistema | Qué puede hacer en esta funcionalidad |
|---|---|---|
| [Ej: Operador institucional] | [Ej: Staff del backoffice] | [Ej: Registrar, editar y derivar ciudadanos] |

---

## 3. Descripción funcional

> Qué hace la funcionalidad, paso a paso, desde la perspectiva del usuario.
> Describir el flujo principal y los flujos alternativos.

### Flujo principal

1. [Paso 1]
2. [Paso 2]
3. [Paso N]

### Flujos alternativos

**[Nombre del flujo alternativo]**
- Condición: [cuándo ocurre]
- Comportamiento: [qué pasa]

---

## 4. Requerimientos

> Lista completa de requerimientos derivados del análisis.
> Cada requerimiento debe ser verificable: se puede decir "cumple" o "no cumple".

### Requerimientos funcionales

| ID | Requerimiento | Prioridad | Notas |
|---|---|---|---|
| RF-NNN-01 | [Descripción clara y verificable] | Alta / Media / Baja | [Aclaraciones si hacen falta] |
| RF-NNN-02 | ... | ... | ... |

### Requerimientos no funcionales

| ID | Requerimiento | Categoría |
|---|---|---|
| RNF-NNN-01 | [Ej: La búsqueda debe responder en menos de 2 segundos] | Performance |
| RNF-NNN-02 | [Ej: Solo usuarios con permiso X pueden acceder] | Seguridad |

---

## 5. Reglas de negocio

> Restricciones, validaciones y condiciones que el sistema debe respetar.
> Son las reglas que no son obvias y que el desarrollador necesita conocer.

| ID | Regla | Consecuencia si no se cumple |
|---|---|---|
| RN-NNN-01 | [Descripción de la regla] | [Qué error o comportamiento ocurre] |

---

## 6. Criterios de aceptación

> Condiciones concretas que deben cumplirse para considerar la funcionalidad completa.
> Formato: "Dado [contexto], cuando [acción], entonces [resultado esperado]."

- [ ] Dado [contexto], cuando [acción], entonces [resultado].
- [ ] Dado [contexto], cuando [acción], entonces [resultado].

---

## 7. Casos límite y excepciones

> Situaciones borde que el sistema debe manejar explícitamente.
> Si no se documenta acá, el desarrollador puede ignorarlos.

| Caso | Comportamiento esperado |
|---|---|
| [Ej: El ciudadano no tiene DNI cargado] | [Ej: Mostrar advertencia, permitir continuar con registro manual] |

---

## 8. Dependencias

> Qué otras funcionalidades, módulos o datos externos son necesarios para que esto funcione.

- [Ej: Requiere que el módulo de Programas esté configurado con al menos un programa activo]
- [Ej: Depende de la integración con RENAPER para autocompletar datos]

---

## 9. Fuera de alcance

> Qué NO incluye este análisis. Explícito para evitar malentendidos.

- [Ej: No incluye exportación a PDF, eso es un requerimiento separado]
- [Ej: No modifica el flujo de derivaciones existente]

---

## 10. Preguntas abiertas

> Dudas que quedaron sin resolver durante el análisis. Deben cerrarse antes de que el estado pase a "Definido".

| # | Pregunta | Responsable de responder | Estado |
|---|---|---|---|
| 1 | [Pregunta] | [Quién debe responder] | Abierta / Cerrada |

---

## 11. Historial de cambios del análisis

| Fecha | Cambio | Motivo |
|---|---|---|
| YYYY-MM-DD | Versión inicial | — |
