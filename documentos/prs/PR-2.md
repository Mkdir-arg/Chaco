# Pull Request #${PR_NUMBER}

## Información General
- **Título**: ${PR_TITLE}
- **Autor**: ${PR_AUTHOR}
- **Fecha**: ${PR_DATE}
- **Tipo**: ${CHANGE_TYPE}
- **Estado**: En revisión

## Módulos Afectados
${MODULES}

## Descripción


## Archivos Modificados
```
$(git diff --name-only origin/Main...HEAD)
```

## Estadísticas
- **Commits**: $(git rev-list --count origin/Main...HEAD)
- **Archivos**: $(git diff --name-only origin/Main...HEAD | wc -l)

## Impacto Funcional
- [ ] Nueva funcionalidad
- [ ] Corrección de bug
- [ ] Refactorización
- [ ] Cambio incompatible
- [ ] Actualización de documentación

## Checklist de Revisión
- [ ] Código revisado
- [ ] Tests ejecutados
- [ ] Documentación actualizada
- [ ] Sin conflictos
- [ ] Aprobado por revisor

---
*Generado automáticamente el ${PR_DATE}*
