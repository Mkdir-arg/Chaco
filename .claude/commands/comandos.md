# Comando /comandos

Muestra la lista completa de comandos disponibles con descripcion y ejemplo de uso.

## Instrucciones para el agente

Cuando el usuario ejecuta `/comandos`, mostrar exactamente esto:

---

## Comandos disponibles

### /feature
Implementa una nueva funcionalidad siguiendo el flujo completo: Product Owner → Arquitecto → Desarrollador → Reviewer → Documentador.
Los agentes se activan automaticamente. Solo se te consulta para aprobar cada fase.

**Cuando usarlo:** nueva funcionalidad, mejora o expansion de algo existente.

**Ejemplo:**
```
/feature agregar exportacion de legajos a PDF con filtro por fecha
```

---

### /definir
Sesion de definicion con el equipo funcional. **Sin codigo. Sin implementacion.**
Clarifica reglas de negocio, debate decisiones, documenta antes de comprometerse a construir.
Carga el contexto existente automaticamente y conduce la conversacion con preguntas dirigidas.

**Cuando usarlo:** antes de pedir una feature, cuando hay dudas sobre como debe funcionar algo, cuando hay preguntas de negocio sin resolver.

**Ejemplo:**
```
/definir como manejar feriados en el sistema de turnos
/definir que pasa cuando un ciudadano falta a un turno
/definir quien puede ver los legajos de un ciudadano
```

---

### /planificar
Ejecuta solo las Fases 1 y 2 del workflow de feature: user story + diseño técnico completo. Se detiene antes del código.
Ideal cuando ya sabés qué querés construir pero no querés arrancar la implementación todavía.

**Cuando usarlo:** después de un `/definir`, cuando querés dejar el diseño aprobado listo para el sprint.

**Ejemplo:**
```
/planificar ABM de Secretaría y Subsecretaría con FK en Programa
/planificar wizard de configuración de programa
```

---

### /roadmap
Genera el mapa de dependencias del backlog: qué bloquea qué, camino crítico, items listos para arrancar y dominios que necesitan `/definir`.

**Cuando usarlo:** antes de planificar un sprint, cuando el backlog creció y querés entender el orden lógico.

**Ejemplo:**
```
/roadmap
```

---

### /fix
Corrige un bug encontrado en desarrollo o staging. Flujo corto: Diagnostico → Fix → Revision → Documentacion.
Sin user story, directo al problema.

**Cuando usarlo:** algo no funciona como deberia, pero no es urgente ni esta en produccion.

**Ejemplo:**
```
/fix el formulario de derivaciones no guarda cuando el campo observaciones esta vacio
```

---

### /hotfix
Correccion urgente para un problema critico en produccion. Flujo minimo con un solo checkpoint.
Genera automaticamente el checklist de deploy.

**Cuando usarlo:** produccion caida, error que afecta a usuarios reales, urgencia alta.

**Ejemplo:**
```
/hotfix error 500 en el listado de ciudadanos desde las 14hs, afecta a todos los usuarios
```

---

### /sprint-plan
Planifica el sprint de la semana. Lee el backlog, propone que items incluir segun prioridad y complejidad, y genera el `current-sprint.md`.

**Cuando usarlo:** inicio de semana o inicio de nuevo sprint.

**Ejemplo:**
```
/sprint-plan
```

---

### /sprint-review
Cierra el sprint actual. Revisa que se completo, que quedo pendiente, y genera el resumen de la semana.

**Cuando usarlo:** fin de sprint, antes de planificar el siguiente.

**Ejemplo:**
```
/sprint-review
```

---

### /status
Muestra el estado actual del proyecto: sprint activo, items en progreso, ultimo cambio por modulo, y deuda tecnica pendiente.

**Cuando usarlo:** para tener un panorama rapido antes de arrancar a trabajar.

**Ejemplo:**
```
/status
```

---

### /tomarcafe
Lee toda la documentacion del proyecto (contexto funcional, arquitectura, backlog, sprint, errores, requerimientos, changelog) y presenta un panorama completo de donde estamos. Propone con que arrancar la sesion con una tabla de opciones ordenada por prioridad.

**Cuando usarlo:** al inicio de una conversacion nueva, cuando retomas el trabajo despues de un tiempo, cuando no sabes por donde empezar.

**Ejemplo:**
```
/tomarcafe
```

---

### /comandos
Muestra esta lista.

**Ejemplo:**
```
/comandos
```

---

## Flujo tipico de una semana

```
Lunes    → /tomarcafe      (ponerse al dia, ver panorama completo)
           /sprint-plan    (formalizar el sprint)
Martes   → /definir [si hay algo por clarificar antes de arrancar]
           /planificar [diseño técnico sin código, si querés revisarlo primero]
           /feature [nueva funcionalidad, cuando el diseño ya está aprobado]
Miercoles→ /fix [bug encontrado durante desarrollo]
Viernes  → /sprint-review
```

Si hay una urgencia en produccion en cualquier momento:
```
           /hotfix [descripcion del problema]
```

## Flujo de diseño antes de codear

```
/definir [tema]    → cierra reglas de negocio, genera requerimiento
/planificar [idea] → genera user story + diseño técnico, espera aprobación
/feature [idea]    → arranca desde Fase 3 (código) con el diseño ya aprobado
```
