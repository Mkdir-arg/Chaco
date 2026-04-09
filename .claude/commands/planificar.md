# Comando /planificar

Ejecuta las Fases 1 y 2 del workflow de feature — user story + diseño técnico — y se detiene. No escribe código.

Usar cuando ya se sabe qué se quiere construir pero no se quiere implementar todavía. Deja el diseño aprobado listo para cuando se llame a `/feature`.

---

## Cuándo usar este comando

- Cuando tenés claro el "qué" pero querés revisar el diseño antes de comprometerte al "cómo"
- Cuando querés agregar una feature al sprint sabiendo exactamente el impacto técnico
- Cuando querés hacer planificación técnica sin arrancar el desarrollo
- Cuando el `/definir` terminó y el siguiente paso es dejar el diseño listo

---

## Comportamiento del orquestador

Cuando el usuario ejecuta `/planificar [descripción]`:

### FASE 1 — Análisis Funcional

Activar el agente `functional-analyst` con la descripción recibida.

El analista:
1. Lee `docs/team/contexto-funcional.md`, `docs/team/backlog.md` y `docs/funcionalidades/_index.md`
2. Si el tema tiene un archivo en `docs/requerimientos/` → leerlo y basar la user story en él
3. Detecta conflictos con funcionalidades existentes
4. Escribe la user story con criterios de aceptación verificables

Presentar al usuario:

**User Story:**
```
Como [rol específico] quiero [acción concreta] para [beneficio medible]
```

**Criterios de aceptación:**
- [ ] Dado [contexto], cuando [acción], entonces [resultado]
- [ ] Si [error], entonces [comportamiento]

**Complejidad:** Pequeño / Mediano / Grande
**Relacionada con:** [funcionalidad existente o "ninguna"]
**Fuera de alcance:** [qué NO entra en esta user story]

Terminar con:
> "Fase 1 completada. ¿Aprobamos esta user story y arrancamos el diseño técnico?"

**ESPERAR RESPUESTA. No continuar hasta recibir aprobación.**

---

### FASE 2 — Arquitecto + Base de Datos

Activar el agente `backend-architect` para el diseño técnico general.
Activar el agente `database-architect` para el schema y migrations.

Consolidar ambas salidas y presentar al usuario en formato unificado:

**Diseño técnico:**
- Apps afectadas: ...
- Archivos a modificar: (lista completa con descripción del cambio)
- Archivos nuevos a crear: (lista completa)
- Cambios de base de datos: (campos, tablas, relaciones)
- Requiere migración: Sí/No
- Estrategia de migración si hay datos existentes: ...

**Análisis de impacto:**
- [ ] FKs o relaciones en otros models afectados
- [ ] Views que usan campos que se modifican
- [ ] Templates que muestran esos campos
- [ ] Formularios con esos campos
- [ ] Conflictos de nombres en URLs
- [ ] Registros existentes que quedan inconsistentes
- [ ] Campos obligatorios nuevos: cómo migran los datos existentes

**Riesgos identificados:** (si los hay, con propuesta de mitigación)

Terminar con:
> "Diseño técnico completo. Cuando quieras implementarlo, ejecutá `/feature [descripción]` — arrancará desde Fase 3 con este diseño como base."

**ESPERAR RESPUESTA. El comando termina aquí — no continúa a implementación.**

---

## Lo que NUNCA hace este comando

- ❌ No escribe código
- ❌ No crea migraciones
- ❌ No modifica archivos de la app
- ❌ No activa al desarrollador

---

## Ejemplo de uso

```
/planificar ABM de Secretaría y Subsecretaría con FK en Programa
/planificar wizard de configuración de programa (datos básicos, naturaleza, capacidades)
/planificar expansión de campos en modelo Ciudadano con foto y situación habitacional
```
