# Roadmap

> Este archivo describe objetivos y dirección estratégica.
> El seguimiento de tareas puntuales vive en GitHub Projects, no acá.

## Estado actual del sistema

El sistema está en producción con las siguientes superficies activas:
- Backoffice para staff institucional
- Portal ciudadano
- App móvil (Expo/React Native) para relevamientos de campo

## Objetivos por trimestre

### Q2 2026 — Estabilización
- [ ] Completar cobertura de tests en apps críticas (`legajos`, `portal`, `conversaciones`)
- [ ] Documentar todos los flujos de NACHEC
- [ ] Resolver deuda técnica en `core/` (archivos duplicados de performance)

### Q3 2026 — Crecimiento
- [ ] Módulo de reportes exportables (PDF/Excel)
- [ ] Mejoras de performance en listados con alto volumen
- [ ] Integración completa con RENAPER

### Q4 2026 — Escala
- [ ] Soporte multi-institución mejorado
- [ ] Panel de métricas en tiempo real para coordinadores
- [ ] Revisión de arquitectura de permisos

## Decisiones estratégicas pendientes

- Evaluar migración de MySQL a PostgreSQL (ver ADR cuando se decida)
- Definir estrategia de versionado de API REST

## Historial de hitos completados

| Fecha | Hito |
|---|---|
| 2026-02 | Lanzamiento de app móvil de relevamientos |
| 2026-04 | Módulo NACHEC en producción |
