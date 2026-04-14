# Arquitectura del Sistema

> **Regla:** El Arquitecto lee este documento ANTES de proponer cualquier diseño técnico.
> **Regla:** El Arquitecto actualiza este documento cuando toma una decisión técnica relevante.

> Última actualización: 2026-04-03


---

## Stack tecnológico

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Backend | Python / Django | 3.12 / 4.2 |
| Base de datos | MySQL | 8.0 |
| Frontend | Tailwind CSS + Alpine.js | CDN |
| WebSocket | Django Channels + Redis | — |
| Cache | Redis | 7 |
| Servidor | Daphne ASGI (local) / Nginx + Daphne (producción actual) | — |
| Contenedores | Docker Compose | — |
| Admin UI | Django Admin | — |

---

## Estructura de apps Django

```
SistemSo/
├── config/           → settings, urls, wsgi, asgi, middlewares
├── core/             → Institucion, modelos geográficos, utilidades base
├── legajos/          → Ciudadanos, legajos, programas, ÑACHEC, contactos, institucional
├── portal/           → Portal ciudadano (auth, registro instituciones)
├── conversaciones/   → Chat ciudadano-operador, WebSocket
├── users/            → Usuarios del backoffice, permisos, SolicitudCambioEmail
├── configuracion/    → UI de configuración (sin modelos propios)
├── dashboard/        → Panel principal
├── tramites/         → Módulo de trámites (stub, sin desarrollar)
└── healthcheck/      → Health checks del sistema
```

---

## Principios de arquitectura establecidos

> Estas decisiones NO deben revertirse sin una razón técnica fuerte y aprobación del usuario.

### Separación de apps
- **Nueva funcionalidad → nueva app Django.** No agregar más modelos a `legajos/`. Ya tiene 4 dominios mezclados y es deuda técnica.
- Cuando una funcionalidad involucra múltiples apps existentes, vive en la app más neutral o en una nueva.
- El backoffice y el portal ciudadano viven en apps separadas. No mezclar vistas de operador con vistas de ciudadano.

### Modelos
- Todos los modelos usan `verbose_name` y `__str__` obligatoriamente.
- Los modelos abstractos base viven en `core/models.py` (`TimeStamped`, `LegajoBase`).
- Las FKs entre apps se referencian como strings: `'legajos.Ciudadano'`, `'core.Subsecretaria'`.
- Los campos nuevos en modelos existentes son siempre `null=True` o tienen `default` para no romper datos.

### Migraciones
- Se crean inmediatamente después de modificar un modelo. Nunca se acumulan.
- Las migraciones con dependencias cruzadas (una app depende de otra) van en la app que agrega el campo, con `dependencies` explícitas.
- No se hacen `squashmigrations` sin coordinación explícita.

### Seguridad
- Todas las vistas del backoffice: `@login_required` mínimo.
- Vistas del portal ciudadano: `@ciudadano_required` (decorator propio en `core/decorators.py`).
- CSRF en todos los forms POST sin excepción. Las vistas con `@csrf_exempt` son deuda técnica.

### Modularización interna
- En apps existentes, preferir modularización incremental por dominio: `views_<dominio>.py`, `forms_<dominio>.py`, `services_<dominio>.py`, `selectors_<dominio>.py`.
- No convertir masivamente `views.py/forms.py/urls.py` en paquetes si eso obliga a un package-flip con alto churn de imports.
- Las views deben quedar delgadas: permisos, parseo HTTP, invocación de service/selector y render/redirect.
- Los selectors son solo lectura y no tienen side effects.
- Los services orquestan reglas, transacciones, invalidación de cache y notificaciones.

### Frontend
- Tailwind CSS via CDN (configurado en `includes/base.html`).
- Alpine.js para interactividad sin build step.
- SweetAlert2 para confirmaciones de eliminación.
- Select2 activado globalmente desde `base.html` — no duplicar.
- Los templates del backoffice extienden `includes/base.html`.
- Los templates del portal ciudadano extienden `portal/base.html`.

---

## Decisiones técnicas tomadas

### DT-015 — Retiro del sistema de turnos (2026-04-14)
**Contexto:** El proyecto dejó de ofrecer agenda ciudadana y backoffice de turnos. Mantener la app `turnos`, sus modelos legacy del portal y sus referencias cruzadas en `core` y `legajos` agregaba complejidad sin valor operativo.

**Decisión:** Retirar el sistema de turnos del arranque del proyecto, del portal ciudadano, de los permisos bootstrap y de las relaciones de modelos. Las migraciones históricas de `core`, `portal` y `legajos` se limpiaron para que instalaciones nuevas no dependan de una app eliminada.

**Consecuencia:** El código activo ya no expone turnos ni agenda. La documentación histórica puede seguir existiendo como referencia, pero no describe funcionalidad vigente.

---

### DT-001 — Coexistencia de RecursoTurnos y ConfiguracionTurnos (2026-03-09)
**Contexto:** El portal ciudadano usaba `RecursoTurnos` como única forma de configurar turnos. Se necesitaba extender el sistema para que cualquier entidad (Programa, Institución, Actividad) pudiera tener turnos configurables.

**Decisión:** Crear `ConfiguracionTurnos` en nueva app `turnos/`. `RecursoTurnos` se mantiene como legacy con un `OneToOneField` a `ConfiguracionTurnos`. `TurnoCiudadano` tiene FK a ambos, con propiedad `config_efectiva` que hace fallback.

**Por qué no se migró directo:** Los turnos históricos tienen `recurso` asignado. La migración directa hubiera roto los datos existentes.

**Consecuencia:** El código nuevo usa `configuracion`. El portal ciudadano existente sigue usando `recurso`. En v2 se migrará completamente.

---

### DT-002 — App `turnos/` separada de `portal/` (2026-03-09)
**Decisión:** El backoffice de turnos vive en `turnos/`, no en `portal/`. Razón: `ConfiguracionTurnos` es referenciada por `core`, `legajos` y `portal`. Si viviera en `portal/`, las otras apps dependerían del portal, invirtiendo la dependencia.

---

### DT-004 — Editor visual de flujos: React Flow + Vite (2026-03-12)
**Contexto:** El editor de flujos de programas requiere un canvas drag & drop con nodos conectables — funcionalidad imposible de implementar bien con Alpine.js.

**Decisión:** React (con React Flow) solo para el editor visual. El resto del sistema sigue con Alpine.js. Compilación con Vite. Los assets compilados se sirven desde `static/flujos/dist/` via Django staticfiles. La comunicación con el backend es via API REST (`GET/POST /api/flujos/<programa_id>/`).

**Por qué React Flow:** estándar de industria para grafos en React, maneja el modelo de nodos y conexiones nativamente, JSON listo para persistir, nodos completamente custom, MIT.

**Por qué no todo React:** el resto del sistema no necesita SPA. Introducir React globalmente agregaría complejidad de build sin beneficio. El editor es el único componente que lo justifica.

**Consecuencia:** se agrega `frontend/flow-editor/` a la raíz del proyecto. El pipeline de CI debe compilar el editor antes del deploy. El template `flujos/editor.html` carga los assets compilados.

---

### DT-005 — Tercera superficie: Panel Institución en `/institucion/` (2026-03-12)
**Contexto:** Las instituciones necesitan una superficie propia para sus usuarios (EncargadoInstitucion, AdministrativoInstitucion, ProfesorInstitucion) que no es el backoffice ni el portal ciudadano.

**Decisión:** Nueva app Django `institucion/` con middleware propio, base template propio y routing separado. Mismo sistema de login Django — el middleware detecta el rol y redirige a `/institucion/`. Patrón idéntico al de `portal/`.

**Por qué no usar el portal ciudadano:** el portal está diseñado para ciudadanos en situación de vulnerabilidad. Compartirlo con representantes institucionales genera disonancia de UX y complica el middleware.

---

### DT-003 — Emails de notificación de turnos como best-effort (2026-03-09)
**Decisión:** `enviar_email_confirmacion()` y `enviar_email_cancelacion()` nunca lanzan excepciones al caller. Si el envío falla, se loguea y continúa. La acción del operador (aprobar/rechazar) no depende del email.

**Razón:** El email es una notificación secundaria. Bloquear la aprobación de un turno porque el servidor SMTP falló sería un error de prioridades.

---

### DT-008 — Refactor DX incremental por slices y módulos por dominio (2026-03-13)
**Contexto:** El proyecto tiene views y forms monolíticos en varias apps. Un refactor big-bang para introducir service layer, selectors y convenciones homogéneas tiene demasiado riesgo por falta de cobertura automática y por el volumen de imports cruzados.

**Decisión:** Aplicar el refactor en slices incrementales. En apps existentes se estandariza primero con módulos por dominio (`views_public.py`, `views_backoffice.py`, `services_turnos.py`, `selectors_public.py`, etc.) y no con package-flip masivo de `views/` o `forms/`.

**Consecuencia:** El primer slice se implementó en `users`, `portal` institucional y `turnos`, dejando `legajos`, `configuracion` y `conversaciones` para etapas posteriores con el patrón ya validado.

### DT-009 — `configuracion` se refactoriza por workflows, no por CRUD completo (2026-03-13)
**Contexto:** La mayor deuda de `configuracion` no estaba en geografía sino en los workflows institucionales y de actividades: detalle institucional, detalle de actividad, staff, derivaciones e inscriptos concentraban queries y side effects en las views.

**Decisión:** El slice 2 se enfocó solo en ese núcleo operativo. Se extrajeron selectors para contextos de detalle y services para flujos de staff/derivaciones/inscriptos/actividad, manteniendo geografía fuera del corte para minimizar riesgo.

**Consecuencia:** `configuracion` sigue sin package-flip masivo, pero ya adopta el patrón del refactor DX en la parte con mayor retorno de mantenimiento. La próxima etapa recomendada queda en `legajos` y `conversaciones`.

### DT-010 — `legajos` se refactoriza por slices de dominio, empezando por ciudadanos y admisión (2026-03-13)
**Contexto:** `legajos` sigue siendo la app con mayor deuda estructural del proyecto. Un refactor global del módulo completo tiene demasiado riesgo por el tamaño de `views.py`, la mezcla de dominios y la baja cobertura automática.

**Decisión:** El slice 3 se concentró en `Ciudadano*` y en el wizard de admisión. Se extrajeron selectors para lista/detalle y services para RENAPER + manejo de sesión del wizard, sin entrar todavía en seguimientos, planes, derivaciones clínicas ni institucional.

**Consecuencia:** El hub principal de `legajos` ya adopta el patrón del refactor DX y queda una base más segura para avanzar luego sobre el legajo de atención propiamente dicho.

### DT-011 — `legajos` clínico se refactoriza con compatibilidad para actividades dinámicas del plan (2026-03-13)
**Contexto:** El flujo clínico base de `legajos` seguía mezclando queries, asignación de profesionales, cierre/reapertura y parseo de actividades dinámicas dentro de las views. Además, `plan_form.html` ignoraba los valores del form al editar y podía perder información existente.

**Decisión:** El slice 4 extrajo selectors para listados y detalle del legajo, creó `services_legajos.py` para evaluación, planes, seguimientos, derivaciones y acciones de estado, y movió el mapeo de tamizajes/actividades al form sin perder compatibilidad con slots dinámicos adicionales enviados por `POST`.

**Consecuencia:** El flujo clínico base queda más testeable y predecible sin cortar el comportamiento histórico de planes con más de tres actividades. La deuda restante en `legajos` queda concentrada en eventos, reportes, responsable y módulos laterales.

### DT-012 — los templates clínicos deben seguir el contrato real del modelo, no campos legacy fantasma (2026-03-13)
**Contexto:** Varias pantallas de `legajos` renderizaban atributos que no existen en los modelos actuales (`evento.descripcion`, `evento.gravedad`, `evaluacion.motivo_consulta`, `evaluacion.diagnostico`, `plan.activo`, `derivacion.origen`). Eso hacía que el frontend quedara visualmente “implementado” pero arquitectónicamente roto.

**Decisión:** El slice 5 corrigió esos templates para alinearlos con los campos reales y extrajo a selectors/services la lógica de eventos, reportes, exportación y cambio de responsable.

**Consecuencia:** Se reduce deuda invisible pero peligrosa: ahora el template expresa el dominio real y el backend queda mejor preparado para tests de integración y cambios futuros.

### DT-013 — `legajos/views.py` queda como fachada compatible durante la modularización (2026-03-13)
**Contexto:** Después de los slices clínicos, `legajos/views.py` seguía siendo el archivo más costoso de navegar del repo. Sin embargo, cambiar `urls.py` y todos los imports externos a la vez agregaba churn innecesario.

**Decisión:** El slice 6 separó el contenido en `views_ciudadanos.py` y `views_clinico.py`, manteniendo `views.py` como fachada que reexporta las vistas ya movidas y conserva solo el contenido todavía no migrado.

**Consecuencia:** Se gana modularidad real sin romper la API interna del módulo. Los siguientes cortes pueden seguir moviendo dominios fuera de `views.py` sin tocar rutas ni imports consumidores.

### DT-014 — `legajos/views.py` pasa a ser fachada pura y la operativa vive en su propio módulo (2026-03-13)
**Contexto:** Tras el slice 6, `legajos/views.py` todavía conservaba institucional, actividades y acciones operativas, por lo que la fachada compatible seguía cargando lógica real y no solo reexportaciones.

**Decisión:** El slice 7 movió ese bloque a `views_operativa.py` y dejó `views.py` como un módulo de compatibilidad que solo reexporta vistas y endpoints divididos por dominio.

**Consecuencia:** El costo de navegación baja de forma material y el próximo refactor puede atacar subdominios concretos sin volver a abrir un archivo monolítico ni tocar las URLs existentes.

### DT-015 — `conversaciones` se modulariza sin romper el contrato AJAX/WebSocket actual (2026-03-13)
**Contexto:** `conversaciones/views.py` concentraba más de 700 líneas con endpoints públicos, backoffice, métricas, queries repetidas y parsing manual de JSON. Quitar de golpe los `@csrf_exempt` o rediseñar el transporte del chat implicaba tocar frontend y comportamiento en tiempo real.

**Decisión:** El slice 8 separó `views_public.py` y `views_backoffice.py`, movió las lecturas a `selectors_conversaciones.py`, encapsuló la orquestación del chat en `services_chat.py` y agregó forms livianos para validar payloads sin cambiar URLs ni el contrato AJAX/WebSocket existente.

**Consecuencia:** El módulo queda mucho más mantenible y testeable sin asumir un rediseño del chat. La deuda restante sobre CSRF y polling/WebSocket queda documentada y aislada.

### DT-016 — la API auxiliar de `conversaciones` debe reutilizar la misma capa de lectura y workflow (2026-03-13)
**Contexto:** Después del slice 8, `api_views.py` y `api_extra.py` seguían resolviendo permisos, consultas y marcado de mensajes por fuera del patrón nuevo, manteniendo duplicación dentro del mismo módulo.

**Decisión:** El slice 9 alineó esas APIs con `selectors_conversaciones.py` y `services_chat.py`, reutilizando permisos, queries y el marcado de mensajes leídos en lugar de repetir implementación.

**Consecuencia:** `conversaciones` queda mucho más coherente internamente y el próximo corte puede enfocarse en deuda funcional real del chat en lugar de seguir ordenando plumbing repetido.

### DT-017 — `configuracion/views.py` se modulariza por dominios y mantiene una fachada compatible (2026-03-13)
**Contexto:** Aunque `configuracion` ya tenía services/selectors para sus workflows principales, `views.py` seguía concentrando geografía, institucional y actividades en más de 500 líneas.

**Decisión:** El slice 10 dividió físicamente el módulo en `views_geografia.py`, `views_institucional.py` y `views_actividades.py`, manteniendo `views.py` como fachada de compatibilidad y reutilizando `TimestampedSuccessUrlMixin` donde la app ya usaba redirects con query timestamp.

**Consecuencia:** La app queda alineada con el patrón modular del resto del refactor DX y el próximo trabajo en `configuracion` puede hacerse por subdominio en lugar de reabrir un archivo monolítico.

### DT-018 — los namespaces nuevos se exponen en paralelo a los names legacy (2026-03-13)
**Contexto:** `users`, `core` y `healthcheck` carecían de `app_name`, pero renombrar de golpe todos los `reverse()` y `{% url %}` del proyecto agregaba un riesgo transversal innecesario.

**Decisión:** El slice 11 agregó `app_name` a esos módulos y expuso includes namespaced en `config/urls.py` sin retirar los includes legacy, habilitando una migración progresiva a `users:*`, `core:*` y `healthcheck:*`.

**Consecuencia:** El proyecto gana previsibilidad de URLs y namespaces sin pagar el costo de un big-bang en templates y llamadas a `reverse()`.

### DT-019 — la migración a namespaces se hace primero en consumidores no ambiguos (2026-03-13)
**Contexto:** Tras habilitar namespaces compatibles, seguía pendiente mover consumidores reales. Sin embargo, nombres como `login/logout` siguen conviviendo con `django.contrib.auth.urls` y no conviene tocarlos sin una decisión explícita.

**Decisión:** El slice 12 migró primero consumidores claros de `core:*` y `users:*` en templates y dejó fuera los names ambiguos.

**Consecuencia:** La migración empieza a generar valor real y reduce dependencia de names legacy, pero sin entrar todavía en las rutas sensibles de autenticación.

### DT-020 — `chatbot` se divide entre vistas públicas y administrativas sin cambiar su superficie HTTP (2026-03-13)
**Contexto:** `chatbot/views.py` mezclaba chat público, panel admin, validación manual de JSON y lecturas del dashboard en un mismo archivo.

**Decisión:** El slice 13 separó `views_public.py` y `views_admin.py`, agregó forms para payloads JSON, selectors para lecturas del dashboard y services para el workflow del chat y las acciones administrativas, manteniendo `views.py` como fachada compatible.

**Consecuencia:** El módulo queda más testeable y navegable sin asumir todavía un hardening de CSRF o un rediseño de sus endpoints.

### DT-021 — el hardening de `chatbot` se apoya en URLs renderizadas y contrato explícito de respuesta (2026-03-13)
**Contexto:** Tras modularizar `chatbot`, apareció una inconsistencia funcional real: el JS del chat consumía un endpoint hardcodeado inexistente y esperaba un shape de JSON distinto al devuelto por la view.

**Decisión:** El slice 14 pasó URLs al frontend desde templates, alineó la respuesta de `send_message` con lo que el JS necesita y retiró `@csrf_exempt` donde el frontend ya enviaba token CSRF.

**Consecuencia:** Se elimina una fuente concreta de bugs silenciosos y el módulo gana una base más segura para seguir endureciendo endpoints JSON.

### DT-022 — el entorno local usa un solo servicio ASGI con bootstrap mínimo (2026-04-03)
**Contexto:** el stack local anterior mezclaba `nginx`, `gunicorn`, `daphne`, reinstalación de dependencias y seeds pesados en cada restart, lo que degradaba mucho el tiempo hasta entorno usable.

**Decisión:** el entorno local recomendado pasa a ser `docker compose up` sobre `app`, `mysql` y `redis`. `app` sirve HTTP y WebSocket con un solo proceso ASGI (`daphne`) y ejecuta solo `migrate`, `crear_superadmin`, `setup_grupos` y `crear_programas` como bootstrap automático.

**Consecuencia:** mejora la DX local, baja la fragilidad del startup y deja el seed pesado/demo fuera del camino crítico diario.

---

## Deudas técnicas documentadas

| ID | Descripción | Severidad | Cuándo surgió |
|----|-------------|-----------|--------------|
| DT-001 | `legajos/` mezcla 4 dominios (ciudadanos, programas, ÑACHEC, institucional) | Alta | Desde el inicio |
| DT-002 | `simple_history` comentado en `legajos/models.py` — sin historial de cambios | Media | Desde el inicio |
| DT-003 | `TipoPrograma` tiene entrada duplicada `NACHEC`/`ÑACHEC` | Baja | Detectada 2026-03-09 |
| DT-004 | Deuda mitigada parcialmente: el flujo institucional público dejó de usar `@csrf_exempt`; quedan flujos públicos/AJAX legacy por revisar | Media | Actualizada 2026-03-13 |
| DT-005 | `RecursoTurnos` es legacy — migrar a `ConfiguracionTurnos` en v2 | Media | 2026-03-09 |
| DT-006 | Recordatorios automáticos de turnos requieren Celery (no implementado) | Media | 2026-03-09 |
| DT-007 | `configuracion/` no tiene modelos propios — es solo una capa de UI sobre `core` y `legajos` | Baja | Detectada 2026-03-09 |
| DT-008 | Ya se habilitaron namespaces en `users`, `core` y `healthcheck`, pero todavía falta migrar gradualmente `reverse()` y templates al esquema namespaced y luego retirar la compatibilidad dual | Media | Actualizada 2026-03-13 |
| DT-009 | `legajos/views.py` ya quedó como fachada pura, pero la app `legajos` sigue mezclando dominios ciudadanos, clínicos, institucionales y de contactos en una misma app | Media | Actualizada 2026-03-13 |
| DT-010 | Falta una política única y explícita para quién puede ser `responsable` de un legajo; hoy conviven criterios de modelo, form y views históricas | Media | Actualizada 2026-03-13 |
| DT-011 | `conversaciones` ya no concentra toda la lógica en `views.py`, pero mantiene endpoints legacy con `@csrf_exempt` y mezcla polling HTTP con notificaciones realtime parciales | Media | Actualizada 2026-03-13 |
| DT-012 | La migración a paquetes reales (`views/`, `services/`, `selectors/`, `signals/`) ya alcanzó `turnos`, `users`, `chatbot`, `configuracion`, `portal`, `conversaciones` y parte de `core`; sigue incompleta en `legajos` y en la capa de auditoría/signals de `core` | Media | Actualizada 2026-03-13 |
| DT-013 | El entorno local con Docker ya fue simplificado, pero el runtime de desarrollo usa Daphne sin autoreload y todavía conserva comandos de bootstrap opcional separados del arranque diario | Baja | 2026-04-03 |

---

## Mapa de dependencias entre apps

```
                ┌─────────┐
                │  core   │  ← modelos base, Institucion, geografía
                └────┬────┘
                     │ FK
          ┌──────────┴──────────┐
          │                     │
     ┌────▼────┐          ┌─────▼────┐
     │ legajos │          │  turnos  │ ← ConfiguracionTurnos
     └────┬────┘          └─────┬────┘
          │ FK                  │ FK
     ┌────▼────┐          ┌─────▼────┐
     │  portal │──────────▶  portal  │ ← TurnoCiudadano (tiene FK a ambos)
     └────┬────┘          └──────────┘
          │
     ┌────▼──────────┐
     │ conversaciones │
     └───────────────┘
```

---

## Grupos de Django y permisos

| Grupo | Quiénes | Qué pueden hacer |
|-------|---------|-----------------|
| `Ciudadanos` | Usuarios del portal ciudadano | Solo su propio perfil, turnos y consultas |
| `EncargadoInstitucion` | Representantes de ONG | Ver y gestionar su institución |
| `Responsable` | Profesionales con legajos asignados | Gestionar legajos asignados |
| `Administradores de Turnos` | Operadores con permisos de config | Crear/editar ConfiguracionTurnos y disponibilidades |
| Staff Django (`is_staff=True`) | Operadores backoffice | Acceso general al backoffice |
| Superusuario (`is_superuser=True`) | Administrador del sistema | Acceso total |

---

## Patrones a seguir en código nuevo

### Vista de backoffice estándar
```python
@login_required
@group_required(['NombreGrupo'])  # si requiere grupo específico
def mi_vista(request):
    ...
```

### Template de backoffice
```html
{% extends 'includes/base.html' %}
{% block content %}
  <!-- contenido -->
{% endblock %}
{% block extra_js %}
  <!-- JS específico de esta vista -->
{% endblock %}
```

### Modelo nuevo
```python
class MiModelo(TimeStamped):  # TimeStamped de core.models
    nombre = models.CharField(max_length=200, verbose_name='Nombre')

    class Meta:
        verbose_name = 'Mi modelo'
        verbose_name_plural = 'Mis modelos'

    def __str__(self):
        return self.nombre
```

### FK cross-app
```python
# Siempre como string para evitar importación circular
ciudadano = models.ForeignKey('legajos.Ciudadano', on_delete=models.PROTECT)
```

---

## Decisiones técnicas tomadas

- 2026-03-13: los templates que consumen endpoints JSON en `chatbot` y `conversaciones` deben recibir las URLs efectivas desde Django, evitando rutas hardcodeadas en JS para preservar compatibilidad ante modularización y namespaces.
- 2026-03-13: en módulos de chat, el endurecimiento CSRF solo se aplica después de alinear el contrato frontend/backend y garantizar emisión de cookie CSRF en la superficie pública.
- 2026-03-13: los runtimes WebSocket cargados globalmente desde `base.html` deben ser idempotentes y leer su configuración desde el DOM de la pantalla cuando exista, para evitar doble inicialización y paths embebidos.
- 2026-03-13: los scripts globales de un dominio compartido deben consumir una configuración explícita (`window.<dominio>Config`) renderizada por Django, en lugar de embutir rutas del proyecto en archivos estáticos.
- 2026-03-13: en el portal ciudadano, los subdominios con ownership sensible sobre recursos del ciudadano deben encapsular ese control en selectors y services propios, no repetirlo inline en views monolíticas.
- 2026-03-13: en el portal ciudadano, la reserva y cancelación de turnos deben vivir en services transaccionales y las pantallas deben validarse con forms explícitos, incluso cuando el flujo sea multi-paso y arranque desde parámetros GET.
- 2026-03-13: los flujos de autenticación y registro del portal ciudadano deben separar la orquestación de sesión, throttling y alta de usuario en un service propio antes de seguir partiendo la view monolítica.
- 2026-03-13: cuando una view monolítica del portal ya fue desarmada por subdominios, el archivo original debe quedar como fachada de compatibilidad y no retener lógica propia residual.
- 2026-03-13: en monolitos críticos de dominio como `ÑACHEC`, conviene atacar primero la modularización física de bloques grandes y bien delimitados antes de extraer lógica interna más sensible.
- 2026-03-13: al modularizar workflows largos de `ÑACHEC`, conviene seguir el orden `dashboard/prestaciones/cierre` → `evaluación/plan` → `asignación/relevamiento`, porque cada paso reduce riesgo para el siguiente.
- 2026-03-13: cuando un hotspot de dominio ya fue partido por bloques y conserva URLs estables, el archivo histórico debe cerrarse como fachada pura para evitar regresión de imports y dejar explícita la nueva cartografía modular.
- 2026-03-13: cuando las views de una app ya están modularizadas, el siguiente paso barato y seguro es alinear los forms al mismo corte por dominio y dejar el archivo histórico como fachada compatible.
- 2026-03-13: en apps donde la capa service/selectors ya existe y el patrón CRUD es repetible, conviene introducir CBVs solo en esos flujos y dejar las acciones POST atómicas como FBVs delgadas.
- 2026-03-13: en módulos legacy con APIs JSON heterogéneas, conviene extraer primero selectors de lectura y un service pequeño para side effects repetidos antes de intentar rediseñar contratos o permisos.
- 2026-03-13: cuando una ruta ya tiene namespace estable, los templates y scripts deben consumirla desde Django o desde configuración renderizada, no embutir paths del proyecto en HTML/JS.
- 2026-03-13: cuando una app conserva routes legacy, los `name=` deben ser únicos y explícitos por dominio antes de intentar una limpieza más profunda del archivo de URLs.
- 2026-03-13: los services que publican configuración de tablas o acciones para el frontend deben emitir `url_name` y `reverse()` ya namespaced, no depender de aliases legacy.
- 2026-03-13: la migración de módulos planos a paquetes reales debe hacerse app por app, dejando wrappers compatibles en los entrypoints legacy hasta que exista cobertura suficiente para retirar esos aliases.
- 2026-03-13: al mover una app a paquetes reales, los módulos legacy deben seguir exportando también símbolos usados implícitamente por tests o monkeypatches, aunque no formen parte de la API funcional principal.
- 2026-03-13: cuando una app de Django tenga múltiples familias de señales, `AppConfig.ready()` debe consolidarlas en un único método explícito antes o durante la migración de packaging; mantener varios `ready()` en la clase es una inconsistencia funcional.
- 2026-03-13: en apps grandes como `legajos`, el packaging físico debe empezar por `services` y `selectors` ya estabilizados, dejando `views` y `signals` para una etapa posterior con mejor cobertura.
- 2026-03-13: cuando una app ya tiene `forms_*` divididos por dominio y wrappers compatibles, el siguiente paso seguro es convertirlos en paquete real antes de tocar `views` o `signals`.
- 2026-03-13: en `legajos`, el packaging de `views` debe empezar por subdominios auxiliares ya separados, como contactos y dashboards simples, antes de tocar clínica, institucional o `ÑACHEC`.
- 2026-03-13: una vez cerradas las views auxiliares en `legajos`, todavía conviene seguir por bloques de soporte pequeños antes de pasar a `programas`, `operativa` o `institucional`.
- 2026-03-13: cuando en `legajos` ya solo quedan módulos de `views` con reglas densas o side effects fuertes, la estrategia incremental pierde seguridad y conviene frenar hasta tener mejor validación funcional.
- 2026-03-13: `programas` y `solapas` siguen siendo movibles físicamente mientras no se toquen sus reglas internas; a partir de ahí, el siguiente nivel pendiente ya cruza dominio pesado de verdad.
- 2026-03-13: cuando una view restante mezcla transiciones, SLA y creación de tareas, el siguiente corte ya no debe ser packaging físico sino extracción previa a service layer con tests de workflow.
- 2026-03-13: una vez extraída la lógica sensible de una view a services, el movimiento físico al paquete `views/` vuelve a ser un corte barato y seguro.
- 2026-03-13: si una view ya apoya en `services`, `forms` y `permissions` separados, puede moverse físicamente al paquete `views/` sin necesidad de rediseño funcional en el mismo slice.
- 2026-03-13: en dominios grandes como clínica, el packaging físico sigue siendo válido mientras el slice no reabra reglas ni contratos; el valor está en mejorar navegación y consistencia sin mezclarlo con reescrituras.
- 2026-03-13: en subdominios ya partidos por archivos como `ÑACHEC`, el cierre del packaging puede hacerse en bloque si el slice se limita a imports, wrappers y exports, sin tocar transiciones internas.
- 2026-03-13: cuando una app grande aún conserva servicios planos residuales, conviene cerrarlos dentro del paquete `services/` antes de tocar `signals`, para que el wiring de side effects ya dependa de una API estable.
- 2026-03-13: al migrar señales a un paquete real, `AppConfig.ready()` debe importar explícitamente los submódulos del paquete nuevo; no conviene depender de imports implícitos o side effects escondidos en wrappers.
- 2026-03-13: una vez cerradas las apps grandes, conviene alinear también las apps chicas al mismo patrón de packaging para evitar excepciones innecesarias en la cartografía del proyecto.
- 2026-03-13: en apps transversales como `core`, primero conviene empaquetar la superficie estable (`views`, `forms`, `selectors`) y recién después cerrar auditoría/performance y `signals` con wiring explícito.
- 2026-03-13: una vez estabilizado el packaging de views HTML, todavía vale la pena alinear `api_views` en apps chicas si el contrato HTTP no cambia y el import path desde `urls.py` puede conservarse.
- 2026-03-13: las `api_views` de apps compartidas también pueden moverse a paquetes reales siempre que `api_urls.py` siga apuntando al mismo import lógico y no se toque el contrato DRF.
- 2026-03-13: si una API grande todavía está acotada a routers propios y no reabre permisos/serializers, también puede cerrarse como último paso estructural antes de dar por agotado el packaging repo-wide.
- 2026-03-14: una vez agotado el packaging repo-wide, el siguiente paso correcto en hotspots grandes es extraer a services los subflujos más acotados y testeables antes de tocar formularios, scoring o adjuntos.
- 2026-03-16: dentro de `ÑACHEC`, los subflujos operativos con cambios de asignación o estado pero sin scoring/adjuntos deben migrarse primero a `ServicioOperacionNachec`, dejando en la view solo permisos HTTP, parseo y mensajes.
- 2026-03-16: cuando el repo ya está mayormente empaquetado, las excepciones residuales de `forms.py` o `services_*.py` deben absorberse dentro del paquete existente de la app antes de considerar cerrado el frente estructural.
