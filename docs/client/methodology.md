# Metodología de trabajo

El proyecto se organiza con entregas incrementales, prioridades visibles y validación continua. La idea es avanzar en bloques acotados, mostrar resultados temprano y ajustar sobre evidencia en lugar de acumular cambios grandes al final.

## Principios de trabajo

- Alcance pequeño y entendible por cada sprint.
- Prioridad sobre valor operativo real, no sobre volumen de cambios.
- Validación temprana con referentes del negocio.
- Trazabilidad documental de lo que se definió, lo que se desarrolló y lo que quedó pendiente.

## Ciclo de trabajo

### 1. Relevamiento y priorización

Se ordenan necesidades, problemas y oportunidades según impacto operativo, urgencia y dependencias.

### 2. Análisis funcional

Cada funcionalidad se baja a reglas de negocio, criterios de aceptación, actores involucrados y casos fuera de alcance.

### 3. Planificación del sprint

Se define qué entra en la iteración, con objetivo, alcance, prioridad y estado esperado para cada funcionalidad.

### 4. Implementación y seguimiento

El equipo desarrolla por bloques pequeños, con seguimiento periódico, resolución temprana de dudas y visibilidad de riesgos.

### 5. Validación

Antes del cierre, se revisan los flujos implementados con foco en comportamiento real, permisos, datos y criterios de aceptación.

### 6. Cierre y siguiente paso

Se consolida el estado del sprint, se registra qué quedó pendiente y se usa ese resultado como base para la siguiente iteración.

## Artefactos que ordenan el trabajo

| Documento | Para qué sirve |
|---|---|
| [Kick Off](kickoff.md) | Alinear objetivo, alcance inicial, responsables y riesgos |
| [Equipo](team.md) | Dejar claro quién decide, quién valida y cómo se escala |
| [Arquitectura](architecture.md) | Mostrar la base técnica del sistema |
| [Sprints](sprints/index.md) | Seguir el avance real de cada iteración |

## Estados de avance

| Estado | Significado |
|---|---|
| ⏳ Pendiente | Todavía no comenzó |
| 🔄 En progreso | Está en desarrollo o validación |
| ✅ Completado | Ya quedó implementado y verificado |
| ⏸ Postergado | Se decidió moverlo a una iteración posterior |

## Qué permite esta metodología

- Detectar bloqueos antes de que frenen todo el proyecto.
- Ajustar prioridades sin perder trazabilidad.
- Mostrar avances reales en plazos cortos.
- Tomar decisiones con evidencia funcional y no solo con intuición.