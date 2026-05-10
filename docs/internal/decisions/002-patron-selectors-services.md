# ADR 002 — Patrón selectors/services en apps Django

**Estado:** Aceptado
**Fecha:** 2026

## Contexto

Las views de Django tienden a acumular lógica de negocio y consultas mezcladas, dificultando el testing y la reutilización.

## Decisión

Adoptar separación explícita en cada app:

- `selectors/` — solo consultas de lectura, sin efectos secundarios
- `services/` — lógica de negocio y operaciones de escritura
- `views/` — orquestación HTTP: recibe request, llama selectors/services, retorna response

## Consecuencias positivas

- Views testeables sin base de datos (mockeando selectors/services)
- Lógica de negocio reutilizable desde management commands, signals y API
- Separación clara de responsabilidades

## Consecuencias negativas

- Más archivos por app
- Requiere disciplina del equipo para no poner lógica en views

## Notas de implementación

Los archivos legacy con sufijo `_views.py`, `_selectors.py`, `_services.py` en la raíz de cada app son la versión anterior al refactor. Las versiones nuevas viven en subcarpetas `views/`, `selectors/`, `services/`.
