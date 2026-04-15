# Comando /roadmap

Genera un mapa simple de prioridades basado en el repo real.

## Qué hace

1. Lee `CLAUDE.md`
2. Inspecciona la estructura del repo y los módulos activos
3. Detecta áreas críticas, deuda visible y dependencias técnicas
4. Devuelve un orden recomendado de trabajo

## Reglas

- No escribe código
- No modifica archivos
- No depende de `docs/` ni `documentos/`

## Salida esperada

- Estado actual del repo
- Áreas con mayor impacto
- Posibles bloqueos
- Próximos pasos recomendados
