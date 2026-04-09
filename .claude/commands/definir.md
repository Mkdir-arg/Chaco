# Comando /definir

Sesión de definición con el equipo funcional. **Sin código. Sin implementación.**
El objetivo es clarificar, debatir y documentar antes de comprometerse a construir.

---

## Cuándo usar este comando

- Cuando hay dudas sobre cómo debe funcionar algo
- Cuando querés pensar con el equipo antes de pedir una feature
- Cuando hay preguntas de negocio sin resolver
- Cuando algo del sistema no está claro y querés alinearte

---

## Comportamiento del orquestador

Cuando el usuario ejecuta `/definir [tema]`:

### PASO 1 — Cargar contexto

Leer obligatoriamente y en este orden:
1. `docs/team/contexto-funcional.md` — reglas de negocio, actores, preguntas abiertas, historial
2. `docs/team/arquitectura.md` — estado técnico actual, principios, deudas
3. `docs/team/backlog.md` — qué user stories ya existen, cuáles están pendientes de definir, dependencias entre items
4. `docs/funcionalidades/_index.md` — qué funcionalidades existen relacionadas al tema
5. Si existe carpeta en `docs/funcionalidades/[slug-relacionado]/` → leer el documento más reciente
6. Buscar en `docs/requerimientos/` si ya existe un archivo relacionado al tema → leerlo si existe

Con esta información, antes de presentar el punto de partida:
- Identificar si el tema ya tiene user story en el backlog
- Identificar si ya existe un requerimiento documentado
- Identificar qué user stories del backlog se verían afectadas por lo que se defina en esta sesión

### PASO 2 — Presentar punto de partida

Mostrar al usuario:

```
## Lo que ya sabemos sobre [tema]

**Reglas de negocio confirmadas:**
- [reglas existentes en contexto-funcional.md relacionadas al tema]

**Decisiones técnicas tomadas:**
- [decisiones de arquitectura.md relacionadas al tema]

**Preguntas abiertas relacionadas:**
- [ ] [preguntas de contexto-funcional.md que aplican]

**Lo que NO está definido todavía:**
- [gaps identificados al leer la documentación]
```

Luego preguntar: **"¿Esto es lo que querés explorar, o hay algo más específico?"**

**ESPERAR RESPUESTA antes de continuar.**

### PASO 3 — Sesión de preguntas y definición

El analista funcional conduce la conversación haciendo preguntas específicas.

**Reglas de la sesión:**
- Preguntar de a una o dos preguntas por vez, no bombardear
- Si el usuario da una respuesta ambigua → pedir clarificación antes de avanzar
- Si hay una decisión de impacto técnico → mencionar la implicancia ("eso significa que...")
- Si hay conflicto con algo ya definido → señalarlo explícitamente ("eso contradice la regla X, ¿querés cambiarla?")
- No proponer soluciones técnicas — solo clarificar el QUÉ, nunca el CÓMO

**Formato de cada pregunta:**
```
❓ [Pregunta concreta]
   Contexto: [Por qué importa esta pregunta]
   Opciones posibles: [A] ... / [B] ... / [C] Otro
```

### PASO 4 — Consolidar y documentar

Al terminar el diálogo, presentar el resumen consolidado:

```
## Resumen de la sesión — [tema]

### Definiciones acordadas
- [lista de decisiones tomadas durante la sesión]

### Reglas de negocio nuevas
- [reglas que surgieron de la conversación]

### Preguntas que quedaron abiertas
- [ ] [si quedó algo sin resolver]

### Implicancias técnicas identificadas
- [si surgió algo que el arquitecto necesita considerar]

### Próximo paso sugerido
- [ ] Registrar en requerimientos → /feature [descripción]
- [ ] Más definición necesaria antes de implementar
- [ ] No requiere implementación — solo documentación
```

Luego preguntar: **"¿Aprobás este resumen? Lo documento y queda como base para el próximo /feature."**

**ESPERAR RESPUESTA.**

### PASO 5 — Guardar resultados

Si el usuario aprueba el resumen:

1. **Actualizar `docs/team/contexto-funcional.md`:**
   - Agregar nuevas reglas de negocio a la sección correspondiente
   - Tachar preguntas abiertas que se respondieron (marcar como `~~pregunta~~`)
   - Agregar nuevas preguntas que surgieron
   - Actualizar el historial de sesiones con la fecha y un resumen de 2-3 líneas

2. **Si quedaron requerimientos concretos → crear archivo en `docs/requerimientos/`:**
   ```
   docs/requerimientos/YYYY-MM-DD_[slug-del-tema].md
   ```
   Con estado `ABIERTO` y los criterios de éxito definidos en la sesión.

3. **Actualizar `docs/team/backlog.md`:**
   - Si surgieron user stories nuevas → agregarlas como items pendientes con ID correlativo
   - Si el tema ya tenía user story en el backlog → actualizar las notas con referencia al requerimiento creado
   - Si había un item en "Pendiente de /definir" → moverlo a "Features pendientes" o marcarlo como resuelto

4. **Si hubo decisión técnica → actualizar `docs/team/arquitectura.md`**

Terminar con:
> "Sesión documentada. Cuando quieras implementar algo de lo que definimos, usá `/feature [descripción]` o `/planificar [descripción]` si querés ver el diseño antes de codear."

---

## Lo que NUNCA hace este comando

- ❌ No escribe código
- ❌ No crea migraciones
- ❌ No modifica templates ni modelos
- ❌ No activa el arquitecto para diseñar (solo para informar implicancias)
- ❌ No avanza a implementación sin que el usuario lo pida explícitamente

---

## Ejemplo de uso

```
/definir cómo manejar feriados en el sistema de turnos
/definir qué pasa cuando un ciudadano falta a un turno
/definir el flujo de derivación automática entre programas
/definir quién puede ver los legajos de un ciudadano
```
