# Fix: Compose no podía crear la red del proyecto por agotamiento del pool de subredes

> Tipo: fix
> Fecha: 2026-04-14
> Módulo: `docker`
> Severidad original: ALTO

## Problema

Al levantar el proyecto con Docker Compose, la creación de `chaco_default` fallaba con:

`failed to create network chaco_default: Error response from daemon: all predefined address pools have been fully subnetted`

## Causa raíz

Compose intentaba crear la red por defecto del proyecto usando el pool global de Docker. En este host, ese pool ya estaba agotado por redes previas, así que Docker no podía asignar una subred nueva.

## Solución aplicada

Se definió un subnet explícito para la red por defecto del stack de desarrollo y otro para la red de producción:

- `docker-compose.yml` → `networks.default.ipam.config[0].subnet`
- `docker-compose.prod.yml` → `networks.nodo-network.ipam.config[0].subnet`

Los subnets quedan parametrizados por variables de entorno para permitir override si hubiera conflicto local:

- `CHACO_DOCKER_SUBNET`
- `CHACO_PROD_DOCKER_SUBNET`

## Archivos modificados

- `docker-compose.yml`
- `docker-compose.prod.yml`

## Requirió migración

No.
