# Análisis funcional 002 — Derivación de ciudadano a programa

**Estado:** En desarrollo
**Fecha de análisis:** 2026-05-12
**Analista:** functional-analyst
**Sprint asociado:** [Sprint 001](../sprints/2026-05-12-sprint-001.md)
**Módulo/App:** `legajos`

---

## 1. Contexto y motivación

Una vez que un ciudadano tiene legajo en el sistema, el operador necesita inscribirlo en uno o más programas sociales y, en muchos casos, derivarlo a un dispositivo específico dentro de la institución para que reciba atención. Hoy este proceso se hace de forma manual fuera del sistema, lo que genera pérdida de información sobre quién derivó, cuándo y con qué criterio. El requerimiento busca digitalizar el flujo completo de derivación: desde que el operador decide derivar hasta que el dispositivo receptor acepta o rechaza, dejando trazabilidad en el legajo del ciudadano.

---

## 2. Actores involucrados

| Actor | Rol en el sistema | Qué puede hacer en esta funcionalidad |
|---|---|---|
| Operador institucional | Staff del backoffice | Iniciar una derivación desde el legajo del ciudadano |
| Operador receptor | Staff del dispositivo destino | Aceptar o rechazar la derivación recibida |
| Administrador institucional | Staff con permisos ampliados | Ver todas las derivaciones, anular derivaciones |
| Coordinador de programa | Staff con rol de coordinación | Ver derivaciones hacia su programa |

---

## 3. Descripción funcional

### Flujo principal — derivación entre dispositivos

1. El operador abre el legajo del ciudadano y va a la pestaña **Programas**.
2. Hace clic en **Derivar**.
3. El sistema muestra un formulario con: programa destino, dispositivo destino, motivo de derivación y observaciones.
4. El operador completa el formulario y confirma.
5. El sistema registra la derivación con estado "Pendiente" y notifica al dispositivo receptor.
6. El operador receptor ve la derivación en su bandeja de entrada.
7. El operador receptor acepta o rechaza con un motivo.
8. El sistema actualiza el estado de la derivación en el legajo del ciudadano y notifica al operador que derivó.

### Flujos alternativos

**Derivación rechazada**
- Condición: el operador receptor rechaza la derivación.
- Comportamiento: el sistema actualiza el estado a "Rechazada", registra el motivo y notifica al operador original. El ciudadano no queda inscripto en el programa.

**Derivación sin respuesta**
- Condición: el dispositivo receptor no responde en X días (configurable).
- Comportamiento: el sistema marca la derivación como "Vencida" y notifica al administrador.

**Ciudadano ya inscripto en el programa**
- Condición: el ciudadano ya tiene una inscripción activa en el programa destino.
- Comportamiento: el sistema muestra un aviso y no permite crear una derivación duplicada.

---

## 4. Requerimientos

### Requerimientos funcionales

| ID | Requerimiento | Prioridad | Notas |
|---|---|---|---|
| RF-002-01 | El operador debe poder iniciar una derivación desde el legajo del ciudadano | Alta | — |
| RF-002-02 | El formulario de derivación debe incluir: programa destino, dispositivo destino, motivo y observaciones | Alta | Programa y dispositivo son obligatorios |
| RF-002-03 | El sistema debe notificar al dispositivo receptor cuando recibe una derivación nueva | Alta | Notificación interna en el sistema |
| RF-002-04 | El operador receptor debe poder aceptar o rechazar la derivación con un motivo | Alta | El motivo es obligatorio al rechazar |
| RF-002-05 | El sistema debe impedir derivar a un ciudadano que ya tiene inscripción activa en el mismo programa | Alta | — |
| RF-002-06 | El legajo del ciudadano debe mostrar el historial completo de derivaciones con estado, fecha y operadores involucrados | Alta | — |
| RF-002-07 | El administrador debe poder anular una derivación pendiente | Media | Solo mientras está en estado "Pendiente" |
| RF-002-08 | El sistema debe marcar como "Vencida" una derivación sin respuesta después del plazo configurado | Media | Plazo configurable por institución |

### Requerimientos no funcionales

| ID | Requerimiento | Categoría |
|---|---|---|
| RNF-002-01 | Solo usuarios con permiso `legajos.add_derivacion` pueden iniciar derivaciones | Seguridad |
| RNF-002-02 | El operador receptor solo puede ver derivaciones dirigidas a su dispositivo | Seguridad |
| RNF-002-03 | La notificación al receptor debe aparecer en menos de 10 segundos de confirmada la derivación | Performance |

---

## 5. Reglas de negocio

| ID | Regla | Consecuencia si no se cumple |
|---|---|---|
| RN-002-01 | Un ciudadano no puede tener dos derivaciones activas al mismo programa simultáneamente | El sistema bloquea la derivación y muestra la derivación existente |
| RN-002-02 | Solo se puede derivar a programas activos y dispositivos activos | El selector solo muestra opciones activas |
| RN-002-03 | El motivo de rechazo es obligatorio | El formulario de rechazo no puede enviarse sin motivo |
| RN-002-04 | Una derivación aceptada no puede anularse, solo puede cerrarse mediante el flujo de egreso del programa | Integridad del historial |

---

## 6. Criterios de aceptación

- [ ] Dado un operador con permisos, cuando inicia una derivación, entonces el sistema registra la derivación con estado "Pendiente" y notifica al receptor.
- [ ] Dado un operador receptor, cuando acepta una derivación, entonces el ciudadano queda inscripto en el programa y el estado cambia a "Aceptada".
- [ ] Dado un operador receptor, cuando rechaza una derivación sin ingresar motivo, entonces el sistema no permite enviar el formulario.
- [ ] Dado un ciudadano con inscripción activa en un programa, cuando un operador intenta derivarlo al mismo programa, entonces el sistema muestra un aviso y bloquea la acción.
- [ ] Dado un administrador, cuando anula una derivación en estado "Pendiente", entonces el estado cambia a "Anulada" y se notifica a ambos operadores.

---

## 7. Casos límite y excepciones

| Caso | Comportamiento esperado |
|---|---|
| El dispositivo destino se desactiva mientras hay una derivación pendiente | La derivación queda en estado "Pendiente" pero se notifica al administrador |
| El operador que derivó es dado de baja del sistema | La derivación permanece en el historial con el nombre del operador original |
| Se intenta derivar a un ciudadano con legajo en estado "pendiente de verificación" | El sistema bloquea la derivación y muestra el motivo |

---

## 8. Dependencias

- Requiere que el análisis 001 (Registro de ciudadano) esté completado: el ciudadano debe tener legajo activo
- Requiere que existan programas y dispositivos configurados en el módulo de Configuración
- Requiere el sistema de notificaciones internas del módulo `conversaciones`

---

## 9. Fuera de alcance

- No incluye derivaciones entre instituciones distintas (inter-institucional)
- No incluye el flujo de egreso del programa una vez aceptada la derivación
- No incluye reportes de derivaciones (eso es un requerimiento separado)
- No modifica la configuración de programas ni dispositivos

---

## 10. Preguntas abiertas

| # | Pregunta | Responsable de responder | Estado |
|---|---|---|---|
| 1 | ¿El plazo de vencimiento de derivaciones es global o configurable por institución? | Product Owner | Cerrada — configurable por institución |
| 2 | ¿Las notificaciones son solo internas o también por correo? | Product Owner | Abierta |

---

## 11. Historial de cambios del análisis

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-05-12 | Versión inicial | — |
