# Comando /roadmap

Genera el mapa de dependencias del backlog: qué bloquea qué, el camino crítico hacia los objetivos principales, y los próximos pasos recomendados.

---

## Cuándo usar este comando

- Cuando querés ver el panorama completo antes de planificar un sprint
- Cuando querés saber qué tenés que hacer antes de poder trabajar en algo
- Cuando querés identificar qué dominio o feature está bloqueando más cosas
- Cuando el backlog creció y querés entender el orden lógico de implementación

---

## Comportamiento del orquestador

Cuando el usuario ejecuta `/roadmap`:

### PASO 1 — Cargar todo el contexto de planificación

Leer obligatoriamente:
1. `docs/team/backlog.md` — todos los items, sus dependencias, estado, complejidad
2. `docs/team/contexto-funcional.md` — sección "Pendiente de /definir" y preguntas abiertas
3. `docs/requerimientos/` — leer todos los archivos con estado ABIERTO para entender alcance
4. `docs/team/current-sprint.md` — qué está en progreso ahora

### PASO 2 — Construir el mapa de dependencias

Analizar cada item del backlog y:
- Identificar sus prerequisitos explícitos (declarados en las notas del backlog)
- Identificar prerequisitos implícitos (por lógica de negocio o técnica)
- Identificar qué items están bloqueados por dominios sin definir

### PASO 3 — Presentar el roadmap

Mostrar en este formato:

---

## Roadmap — SistemSo

### Estado actual
- **En sprint:** [items activos]
- **Completados:** [count] items
- **Pendientes:** [count] items
- **Bloqueados por /definir:** [count] items

---

### Camino crítico — orden mínimo para llegar a operativo

```
[US-011] Grupos Django — prerequisito de TODO
    ↓
[US-004] Secretaría/Subsecretaría
    ↓
[US-005] Wizard configuración programa
    ↓
[US-006] Motor de flujos backend
    ↓
[US-007] Editor visual de flujos ← REQUIERE DECISIÓN: stack React
    ↓
[US-012] Inscripción y derivación de ciudadanos ← REQUIERE /definir primero
```

---

### Por dominio

#### Ciudadanos
| Item | Bloquea | Bloqueado por | Listo para arrancar |
|------|---------|--------------|-------------------|
| US-008 | US-009 | nada | ✅ Sí |
| US-009 | US-015 | US-008 | ❌ Espera US-008 |
| US-010 | US-012 | US-011 | ❌ Espera US-011 |
| US-013 | nada | nada | ✅ Sí |

#### Programas
[...misma estructura...]

#### Infraestructura
[...misma estructura...]

---

### Items listos para arrancar HOY
> No tienen prerequisitos pendientes ni dominios sin definir.

- [US-XXX] — descripción
- [US-XXX] — descripción

---

### Items bloqueados por /definir
> No se pueden estimar ni implementar hasta que se haga la sesión correspondiente.

| Dominio | Bloquea | Urgencia |
|---------|---------|---------|
| Actividades | US-009 (solapa Cursos y Actividades) | Alta |
| Derivación e inscripción | US-012 | Alta |
| Instituciones | US-009 (solapa Instituciones) | Media |

---

### Recomendación de orden para el próximo sprint

1. [primero esto] — por qué
2. [luego esto] — por qué
3. [luego esto] — por qué

---

Terminar con:
> "¿Querés arrancar con alguno de los items listos, o primero hacemos una sesión `/definir` para desbloquear algo?"

**ESPERAR RESPUESTA.**

---

## Lo que NUNCA hace este comando

- ❌ No escribe código
- ❌ No modifica el backlog
- ❌ No inicia ninguna implementación

---

## Ejemplo de uso

```
/roadmap
```
