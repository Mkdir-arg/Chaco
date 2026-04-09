# Comando /hotfix

Correccion urgente para un bug critico en PRODUCCION. Flujo minimo y rapido.
El objetivo es restaurar el servicio lo antes posible con el menor cambio posible.

**Uso:** `/hotfix [descripcion del problema en produccion]`

---

## Principio del hotfix

> "Minimo cambio que restaura el servicio. Nada mas."

No es el momento de refactorizar, mejorar, ni resolver deuda tecnica.
Si el fix correcto requiere cambios grandes → aplicar un parche temporal y luego abrir un `/fix` o `/feature`.

---

## FASE 1 — Triaje (sin aprobacion requerida, es urgente)

Activar el agente `debugger` inmediatamente.

Determinar en menos de 2 minutos:
- **Severidad:** ¿El sistema esta caido totalmente? ¿Afecta a todos los usuarios? ¿Solo a algunos?
- **Causa probable:** basado en el mensaje de error o comportamiento reportado
- **Fix inmediato posible:** ¿hay un cambio de 1-5 lineas que lo resuelve?
- **Workaround temporal:** si el fix real lleva mas tiempo, ¿hay algo que alivie el impacto ahora?

Leer `docs/features/_index.md` y el archivo de la funcionalidad afectada para ver si este problema ocurrio antes.

Presentar al usuario:

**Triaje:**
- Severidad: CRITICA / ALTA
- Causa probable: [una oracion]
- Fix propuesto: [descripcion del cambio minimo]
- Archivos a tocar: [lista]
- Tiempo estimado: [minutos]
- Workaround disponible: Si/No — [cual si aplica]

Terminar con:
> "Triaje completado. ¿Aplicamos el hotfix?"

**ESPERAR RESPUESTA. Un solo checkpoint — despues se ejecuta todo sin pausas.**

---

## FASE 2 — Implementacion (sin pausas adicionales)

Una vez aprobado el triaje, ejecutar TODO sin interrupciones:

### 2A — Fix

Activar el agente `django-developer`.

Reglas absolutas:
- Tocar el minimo de archivos posible
- Cero refactoring, cero mejoras, cero limpieza
- Si requiere migracion → evaluar si puede evitarse con un fix en codigo primero
- Si la migracion es inevitable → ejecutarla con precaucion (datos existentes)

### 2B — Revision rapida

Activar el agente `code-reviewer` con checklist reducido:

- [ ] El cambio no introduce un bug nuevo obvio
- [ ] No hay error de sintaxis
- [ ] CSRF y login_required intactos en los archivos tocados
- [ ] Si hay migracion → es reversible

Si hay problema critico → corregir inmediatamente y re-revisar.
Si hay problema menor → documentarlo como deuda tecnica y continuar.

### 2C — Instrucciones de deploy

Generar checklist de deploy para este hotfix especifico:

```
CHECKLIST DE DEPLOY — Hotfix [fecha]
[ ] Hacer backup de DB antes de aplicar (si hay migracion)
[ ] Aplicar en staging primero y verificar
[ ] Comandos a ejecutar en produccion:
    - git pull origin [rama]
    - pip install -r requirements.txt (si hay nueva dependencia)
    - python manage.py migrate (si hay migracion)
    - python manage.py collectstatic --noinput (si hay cambios en static)
    - systemctl restart gunicorn (o equivalente)
[ ] Verificar que el error original ya no ocurre
[ ] Monitorear logs por 10 minutos post-deploy
```

Presentar al usuario el resumen completo con los archivos modificados y el checklist de deploy.

---

## FASE 3 — Documentacion (ejecutar inmediatamente)

1. Determinar el slug de la funcionalidad afectada (minusculas-con-guiones)
2. Crear el archivo en `docs/fix/[slug]/[YYYY-MM-DD]_hotfix_[titulo-breve].md`
   - Si la carpeta no existe → crearla
   - Usar `docs/fix/_template.md` como base
   - Completar todos los campos incluyendo checklist de deploy
3. Actualizar `docs/fix/_index.md` agregando la fila
4. Agregar entrada urgente en `docs/team/changelog.md`
5. Si el hotfix fue un parche temporal → agregar item en `docs/team/backlog.md` para el fix definitivo

Terminar con:
> "Hotfix completado. Documentado en docs/fix/[slug]/[fecha]_hotfix_[titulo].md
> IMPORTANTE: Seguir el checklist de deploy antes de aplicar en produccion."

---

## Post-hotfix obligatorio

Despues de resolver la urgencia, siempre:
- Si fue un parche → abrir `/fix` para la solucion definitiva
- Si revela un problema de arquitectura → abrir `/feature`
- Agregar test que hubiera detectado este bug antes
