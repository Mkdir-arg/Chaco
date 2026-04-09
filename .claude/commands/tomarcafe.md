# Comando /tomarcafe

Hace un repaso profundo de toda la documentación del sistema y propone con qué arrancar la sesión.
Ideal para ejecutar al inicio de una conversación nueva o cuando querés retomar el trabajo sin saber por dónde.

## Instrucciones para el agente

### Paso 1 — Leer toda la documentación (en paralelo donde sea posible)

Leer obligatoriamente los siguientes archivos:

**Contexto del sistema:**
- `docs/team/contexto-funcional.md` — reglas de negocio, actores, glosario, historial de sesiones
- `docs/team/arquitectura.md` — principios, decisiones técnicas, mapa de apps, deudas técnicas

**Estado del trabajo:**
- `docs/team/backlog.md` — todas las user stories pendientes y completadas
- `docs/team/current-sprint.md` — sprint activo si existe
- `docs/team/changelog.md` — últimas entradas para entender qué se hizo recientemente

**Pendientes y problemas:**
- Todos los archivos en `docs/errores/` — bugs con su estado actual
- Todos los archivos en `docs/requerimientos/` — requerimientos formales con su estado

**Funcionalidades documentadas:**
- `docs/funcionalidades/_index.md` — índice de funcionalidades implementadas

**Memoria persistente:**
- `memory/MEMORY.md` — contexto rápido del proyecto

---

### Paso 2 — Procesar lo leído

Con toda esa información, identificar:

**A) Errores abiertos**
- Listar los que tienen `Estado: ABIERTO` (sin bloqueo)
- Listar los que tienen `Estado: ABIERTO (bloqueado por ...)` — indicar el prerequisito

**B) Requerimientos abiertos**
- Listar los que tienen `Estado: ABIERTO` ordenados por prioridad

**C) User stories listas para arrancar**
- Del backlog, identificar las que NO tienen prerequisitos pendientes (o cuyos prerequisitos ya están ✅ completados)
- Considerar también las que están 🔵 En sprint si hay sprint activo

**D) Temas sin definir**
- De `contexto-funcional.md` sección "Preguntas abiertas sin resolver"
- De `backlog.md` sección "Pendiente de /definir antes de poder estimar"

**E) Deudas técnicas accionables**
- De `arquitectura.md` sección "Deudas técnicas documentadas" — las de severidad Alta o que desbloqueen algo

---

### Paso 3 — Presentar el panorama

Presentar una sección de contexto rápido:

```
## Estado del sistema al [fecha de hoy]
[2-3 líneas que resumen en qué punto está el proyecto: qué se construyó, qué falta, cuál es el próximo gran hito]
```

Luego presentar la tabla de opciones para arrancar:

```
## ¿Con qué arrancamos?
```

| # | Tipo | Qué es | Comando | Prioridad sugerida |
|---|------|--------|---------|-------------------|
| 1 | 🔴 Fix | [descripción del error] | `/fix ...` | Alta / Bloqueado por X |
| 2 | 📐 Definir | [tema a definir] | `/definir ...` | Alta / Media |
| 3 | 🚀 Desarrollo | [US-XXX descripción] | `/feature ...` | Alta / Media |
| 4 | 🚀 Desarrollo | [US-XXX descripción] | `/feature ...` | Media |
| ... | ... | ... | ... | ... |

**Reglas de la tabla:**
- Máximo 6-8 filas — solo lo más relevante, no listar todo el backlog
- Ordenar: errores desbloqueados primero → prerequisitos críticos → features con mayor valor → definiciones que desbloquean desarrollo
- Si hay sprint activo con ítems 🔵, ponerlos al tope con indicador de "en sprint"
- Errores bloqueados por prerequisito → mostrar el prerequisito como opción, no el error en sí
- No incluir items que dependan de features aún no iniciadas (a menos que sean el siguiente paso lógico)

Terminar con:

```
¿Arrancamos con alguno de estos o tenés algo específico en mente?
```

---

### Notas de ejecución

- No modificar ningún archivo durante este comando — es solo lectura y análisis
- Si algún archivo no existe todavía, ignorarlo sin error
- Si hay sprint activo, priorizarlo sobre el backlog general
- El tono es de conversación de equipo — como cuando llegás al trabajo y te ponés al día con un colega
