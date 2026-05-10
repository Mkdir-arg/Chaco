# Análisis funcional 001 — Registro de ciudadano

**Estado:** Completado
**Fecha de análisis:** 2026-05-12
**Analista:** functional-analyst
**Sprint asociado:** [Sprint 001](../sprints/2026-05-12-sprint-001.md)
**Módulo/App:** `legajos`

---

## 1. Contexto y motivación

El sistema necesita registrar ciudadanos que se acercan a una institución para recibir asistencia social. Actualmente el operador no tiene una forma unificada de hacerlo: en algunos casos busca primero por DNI para evitar duplicados, en otros carga manualmente sin verificar. Esto genera legajos duplicados y datos inconsistentes que afectan los reportes y las derivaciones posteriores. El requerimiento surge de la necesidad de estandarizar el punto de entrada de cualquier ciudadano al sistema, garantizando unicidad y trazabilidad desde el primer contacto.

---

## 2. Actores involucrados

| Actor | Rol en el sistema | Qué puede hacer en esta funcionalidad |
|---|---|---|
| Operador institucional | Staff del backoffice con permiso de legajos | Buscar, registrar y confirmar datos de un ciudadano |
| Administrador institucional | Staff con permisos ampliados | Todo lo anterior + editar registros ya confirmados |
| Ciudadano | Usuario externo | No interactúa directamente con este flujo |

---

## 3. Descripción funcional

### Flujo principal — registro con consulta a RENAPER

1. El operador ingresa al módulo **Legajos** y hace clic en **Nuevo ciudadano**.
2. El sistema muestra el formulario de búsqueda por DNI.
3. El operador ingresa el DNI y el sistema consulta RENAPER.
4. RENAPER devuelve los datos: nombre, apellido, fecha de nacimiento, domicilio.
5. El sistema muestra los datos para confirmación.
6. El operador revisa, completa los campos faltantes (teléfono, correo, observaciones) y confirma.
7. El sistema crea el legajo y redirige al detalle del ciudadano recién registrado.

### Flujos alternativos

**Ciudadano ya registrado**
- Condición: el DNI ingresado ya existe en el sistema.
- Comportamiento: el sistema muestra el legajo existente con un aviso. El operador puede continuar editando ese legajo o cancelar.

**RENAPER no disponible o sin respuesta**
- Condición: la integración con RENAPER falla o no devuelve datos.
- Comportamiento: el sistema muestra un aviso y habilita el formulario de registro manual completo.

**Registro manual sin DNI**
- Condición: el ciudadano no tiene DNI o no lo tiene disponible.
- Comportamiento: el operador puede registrar con datos mínimos (nombre y apellido). El sistema marca el legajo como "pendiente de verificación".

---

## 4. Requerimientos

### Requerimientos funcionales

| ID | Requerimiento | Prioridad | Notas |
|---|---|---|---|
| RF-001-01 | El sistema debe verificar si el DNI ya existe antes de crear un legajo nuevo | Alta | Evita duplicados |
| RF-001-02 | El sistema debe consultar RENAPER con el DNI ingresado y autocompletar los datos disponibles | Alta | La consulta es opcional si RENAPER no está disponible |
| RF-001-03 | El operador debe poder registrar un ciudadano manualmente sin consultar RENAPER | Alta | Flujo de fallback obligatorio |
| RF-001-04 | El sistema debe permitir registrar un ciudadano sin DNI, marcando el legajo como pendiente de verificación | Media | Casos de personas en situación de calle o extranjeros |
| RF-001-05 | El formulario debe validar formato de DNI (solo números, 7 u 8 dígitos) antes de consultar | Alta | — |
| RF-001-06 | El sistema debe registrar quién creó el legajo y en qué fecha | Alta | Trazabilidad |
| RF-001-07 | El operador debe poder adjuntar una foto del ciudadano al momento del registro | Baja | Opcional en el primer registro |

### Requerimientos no funcionales

| ID | Requerimiento | Categoría |
|---|---|---|
| RNF-001-01 | La consulta a RENAPER debe resolverse en menos de 5 segundos o mostrar indicador de carga | Performance |
| RNF-001-02 | Solo usuarios con permiso `legajos.add_ciudadano` pueden crear legajos | Seguridad |
| RNF-001-03 | El formulario debe funcionar correctamente en dispositivos móviles | Usabilidad |

---

## 5. Reglas de negocio

| ID | Regla | Consecuencia si no se cumple |
|---|---|---|
| RN-001-01 | Un ciudadano no puede tener dos legajos con el mismo DNI en la misma institución | El sistema debe bloquear la creación y mostrar el legajo existente |
| RN-001-02 | Un legajo sin DNI debe quedar en estado "pendiente de verificación" y no puede ser derivado a programas hasta que se complete | El sistema debe impedir la derivación y mostrar el motivo |
| RN-001-03 | Los datos que vienen de RENAPER no pueden ser editados por el operador en el momento del registro, solo los campos complementarios | Integridad de datos oficiales |

---

## 6. Criterios de aceptación

- [x] Dado un operador con permisos, cuando ingresa un DNI existente, entonces el sistema muestra el legajo existente y no crea uno nuevo.
- [x] Dado un operador con permisos, cuando ingresa un DNI nuevo y RENAPER responde, entonces el sistema autocompleta nombre, apellido y fecha de nacimiento.
- [x] Dado un operador con permisos, cuando RENAPER no responde, entonces el sistema habilita el formulario manual sin bloquear el flujo.
- [x] Dado un operador con permisos, cuando registra un ciudadano sin DNI, entonces el legajo queda en estado "pendiente de verificación".
- [x] Dado cualquier usuario sin permiso `legajos.add_ciudadano`, cuando intenta acceder al formulario, entonces recibe un error 403.

---

## 7. Casos límite y excepciones

| Caso | Comportamiento esperado |
|---|---|
| DNI con letras o caracteres especiales | El formulario rechaza el input antes de enviar, con mensaje de validación |
| RENAPER devuelve datos de una persona fallecida | El sistema muestra los datos con una advertencia visible; el operador decide si continuar |
| El operador cierra el navegador a mitad del formulario | No se crea ningún registro parcial |
| Dos operadores intentan registrar el mismo DNI al mismo tiempo | El segundo recibe el aviso de legajo existente |

---

## 8. Dependencias

- Requiere que la integración con RENAPER esté configurada en variables de entorno (`RENAPER_API_URL`, `RENAPER_API_KEY`)
- Requiere que exista al menos una institución activa en el sistema para asociar el legajo
- El permiso `legajos.add_ciudadano` debe estar asignado al grupo correspondiente

---

## 9. Fuera de alcance

- No incluye la edición de datos del ciudadano después del registro inicial (eso es un requerimiento separado)
- No incluye la carga masiva de ciudadanos por CSV
- No incluye la fusión de legajos duplicados existentes
- No modifica el flujo de derivaciones

---

## 10. Preguntas abiertas

| # | Pregunta | Responsable de responder | Estado |
|---|---|---|---|
| 1 | ¿Los datos de RENAPER se sincronizan automáticamente si cambian, o solo en el momento del registro? | Product Owner | Cerrada — solo en el momento del registro |
| 2 | ¿Un ciudadano puede tener legajos en múltiples instituciones con el mismo DNI? | Product Owner | Cerrada — sí, cada institución tiene su propio legajo |

---

## 11. Historial de cambios del análisis

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-05-12 | Versión inicial | — |
| 2026-05-12 | Agregado RN-001-03 sobre datos de RENAPER | Surgió durante la revisión con el equipo |
