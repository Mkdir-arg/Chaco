# Procesos internos

## Deploy a producción

```bash
# 1. Asegurarse de estar en main actualizado
git checkout main
git pull origin main

# 2. Ejecutar script de deploy
./scripts/deploy_prod.sh
```

El script `deploy_prod.sh` realiza:
1. Build de la imagen Docker
2. Push al registry
3. Restart del servicio en el servidor

### Checklist pre-deploy

- [ ] Tests pasando en CI
- [ ] Migraciones revisadas (sin operaciones destructivas sin respaldo)
- [ ] Variables de entorno de producción actualizadas si hubo cambios
- [ ] Notificar al equipo en el canal correspondiente

## Rollback

Si el deploy falla o hay un error crítico en producción:

```bash
# Volver a la imagen anterior
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --no-build
# (ajustar tag de imagen según el caso)
```

Para rollback de migraciones:
```bash
docker compose exec django python manage.py migrate <app> <migration_anterior>
```

## Gestión de incidentes

### Severidades

| Nivel | Descripción | Tiempo de respuesta |
|---|---|---|
| P1 | Sistema caído o datos comprometidos | Inmediato |
| P2 | Funcionalidad crítica degradada | < 2 horas |
| P3 | Bug con workaround disponible | Próximo sprint |

### Pasos ante un incidente P1/P2

1. Notificar en el canal del equipo con descripción del problema
2. Revisar logs: `docker compose logs -f django`
3. Evaluar rollback si el problema es post-deploy
4. Abrir issue en GitHub con label `incident` documentando causa y resolución

## Gestión de migraciones en producción

- Siempre hacer backup de la base antes de migraciones que alteran tablas grandes
- Migraciones con `ALTER TABLE` en tablas > 100k filas deben planificarse en horario de bajo tráfico
- Usar `--fake` solo si se está seguro de que el esquema ya está aplicado manualmente
