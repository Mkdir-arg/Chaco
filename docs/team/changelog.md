# Changelog — SistemSo

> Registro cronológico de todos los cambios implementados por el equipo.

## Formato de entrada

```
### [FECHA] Título del cambio
**Sprint**: Sprint N
**User Story**: Como [usuario]...
**Archivos modificados**: lista de archivos
**Descripción**: qué se hizo y por qué.
```

---

## 2026-04-14 — Retiro funcional de legajos clínicos e institucionales

**User Story:** Como equipo de desarrollo quiero retirar del flujo activo los legajos de atención e institucionales para concentrar la operación en la ficha del ciudadano y en programas, sin perder compatibilidad con datos históricos.

**Archivos modificados:**
- `legajos/urls.py`, `legajos/views/deprecated.py` — rutas legacy redirigidas fuera de los legajos clínicos e institucionales
- `legajos/selectors/ciudadanos.py`, `legajos/services/solapas.py`, `legajos/templates/legajos/ciudadano_detail.html` — hub del ciudadano sin tab de legajos y con resumen basado en programas
- `dashboard/views/home.py`, `dashboard/api_views/__init__.py`, `dashboard/utils.py` — métricas reemplazadas por inscripciones y derivaciones activas
- `legajos/api_urls.py`, `legajos/admin.py` — sin exposición directa de `LegajoAtencion` en API REST ni admin principal
- `legajos/views/institucional.py`, `configuracion/templates/configuracion/institucion_detail.html` — detalle institucional sin alta automática de `LegajoInstitucional`
- `legajos/tests/test_ciudadanos_admision.py`, `legajos/tests/test_legajo_workflow.py` — pruebas adaptadas al retiro funcional

**Descripción:** Se retiró el acceso activo a `LegajoAtencion` y `LegajoInstitucional` sin borrar tablas históricas. Las rutas legacy ahora redirigen a la ficha del ciudadano o al detalle programático de institución, el dashboard y el hub del ciudadano trabajan con programas e inscripciones activas, y se eliminó la exposición directa de estos legajos en la API REST y en el admin principal.

---

## 2026-04-03 — DX-059 Stack local Docker simplificado

**User Story:** Como equipo de desarrollo quiero levantar el entorno local con `docker compose up` y con el menor bootstrap posible para reducir el tiempo hasta entorno usable.

**Archivos modificados:**
- `docker-compose.yml` — nuevo stack local por defecto con `app`, `mysql`, `redis`
- `docker-compose.hybrid.yml` — alineado al mismo contrato local simple
- `docker-entrypoint.sh` — espera DB, corre migraciones y bootstrap idempotente mínimo antes de levantar Daphne
- `Dockerfile` — instala un entrypoint estable fuera del bind mount local
- `legajos/management/commands/crear_programas.py` — reemplaza campo legacy `activo` por `estado` + `naturaleza`
- `config/settings.py` — agrega `app` a hosts internos permitidos
- `.env.local.example`, `docs/team/entorno-local.md`, `docs/funcionalidades/refactor-dx/v1.58_slice-59-stack-local-docker.md`

**Descripción:** El entorno local deja de depender de `nginx` y de la separación artificial HTTP/WebSocket. El arranque diario ya no ejecuta `pip install`, `sleep`, `collectstatic`, `load_initial_data` ni `setup_system`. El backend local levanta con un solo proceso ASGI sobre un solo puerto y conserva solo un bootstrap mínimo e idempotente.

---

## 2026-03-19 — US-009 Hub del Ciudadano — Solapas dinámicas y badge behavior

**User Story:** Como operador/profesional del backoffice quiero ver en el hub del ciudadano todas las solapas de información con badges que indican ítems de atención para priorizar la acción sin navegar entre módulos.

**Archivos modificados:**
- `legajos/services/solapas.py` — SOLAPAS_ESTATICAS expandida a 11 entradas; `obtener_solapas_ciudadano` refactorizado (copia dicts, inyecta badges); nuevo método `obtener_badges_ciudadano` con 5 tipos de badge
- `legajos/selectors/ciudadanos.py` — `build_ciudadano_detail_context` genera alertas on-the-fly y construye querysets para 7 tabs nuevos + `linea_tiempo`
- `legajos/templates/legajos/ciudadano_detail.html` — badges inline-style en botones de tab; 7 nuevos paneles de tab con empty states; loop de programa usa `solapas` (ID normalizado); `confirm()` migrado a SweetAlert2

**Descripción:** Expande el hub con 7 solapas estáticas nuevas (Turnos, Instituciones, Conversaciones, Derivaciones, Alertas, Línea de tiempo, Red Familiar) y un sistema de badges que muestra conteos de atención urgente. El tab de ACOMPANAMIENTO_SEDRONAR usa ahora `solapa.id` (normalizado) para garantizar consistencia con el botón. Se corrigieron dos usos de `confirm()` nativo que violan la convención del design system.

---

## 2026-03-19 — US-008 Perfil social ampliado del ciudadano

**User Story:** Como operador quiero que la ficha del ciudadano incluya situación habitacional, laboral, educativa, médica, documentación migratoria, notas y foto para tener toda la información social centralizada.

**Archivos modificados:**
- `legajos/models.py` — 14 nuevos campos en `Ciudadano`: `foto` (ImageField), `tipo_vivienda`, `tenencia_vivienda`, `condiciones_vivienda`, `situacion_laboral`, `ingreso_estimado`, `obra_social`, `nivel_educativo`, `cobertura_medica` (sensible), `medicacion_habitual` (sensible), `dni_fisico`, `estado_renaper`, `estado_migratorio` (sensible), `observaciones`. `TextChoices` para todos los campos enum. 4 nuevos índices.
- `legajos/migrations/0034_ciudadano_campos_perfil_ampliado.py` — migración creada y aplicada
- `legajos/forms/ciudadanos.py` — `CiudadanoUpdateForm` extendido con campos no-sensibles en `Meta.fields/widgets`; campos sensibles inyectados en `__init__` solo con `puede_ver_sensible=True`; `clean_foto` valida 5 MB máximo; `save()` persiste campos sensibles condicionalmente
- `legajos/views/ciudadanos.py` — `CiudadanoUpdateView` pasa `puede_ver_sensible` al form y al contexto; `form_valid` invalida caché. `CiudadanoDetailView` pasa `user` al selector
- `legajos/selectors/ciudadanos.py` — `build_ciudadano_detail_context` acepta `user` y retorna `puede_ver_sensible`; `buscar_ciudadanos_rapido` retorna `foto_url`
- `legajos/templates/legajos/ciudadano_edit_form.html` — `enctype="multipart/form-data"`, fieldsets de foto/habitacional/laboral/educativo/documentación/sensibles/observaciones
- `legajos/templates/legajos/ciudadano_detail.html` — foto en avatar, sección social con `{% if tiene_social %}`, sección sensible con `{% if puede_ver_sensible %}`

**Descripción:** Amplía la ficha del ciudadano con toda la información de su perfil social. Los campos de salud (`cobertura_medica`, `medicacion_habitual`) y documentación migratoria (`estado_migratorio`) son sensibles y están protegidos en tres capas independientes: form (no se inyectan sin el flag), view (calcula el flag por grupo Django) y template (sección condicional). La foto tiene validación de peso en el form (5 MB máximo). Se agregaron 4 índices para preparar los filtros del hub ciudadano (US-009).

---

## 2026-03-19 — Fix: Imports rotos post-refactor DX

**Tipo:** fix
**Severidad:** Alto — servidor no levantaba

**Archivos corregidos:**
- `legajos/views/__init__.py` — eliminado import stale `views_ciudadanos`; renombrado `contactos_api` a `historial_contactos_api` para evitar shadowing del módulo
- `legajos/selectors/__init__.py` — agregados 9 exports faltantes de `legajos.py` usados por `clinico.py`
- `portal/selectors/turnos_ciudadano.py`, `portal/services/turnos_ciudadano.py` — `from .models` → `from portal.models`
- `conversaciones/selectors/conversaciones.py` — 3 lazy imports `from .models` → `from conversaciones.models`
- `legajos/selectors/contactos.py` — lazy import `from .models` → `from legajos.models`
- `legajos/admin_programas.py` — campo `activo` → `estado` en `ProgramaAdmin` (campo no existe en el modelo)
- `flujos/models.py` — índice renombrado para cumplir límite de 30 chars
- `flujos/migrations/0002_rename_long_index.py` — migración de rename creada

**Descripción:** Consecuencia del refactor DX (slices 37–47). Los `__init__.py` de los nuevos paquetes no exportaban todos los símbolos necesarios y varios archivos usaban `from .models import` (punto simple) dentro de sub-paquetes. También se levantó el contenedor `nginx` (puerto 9000) que no había sido incluido en el startup inicial.

---

## 2026-03-19 — US-023 Clases y registro de asistencia en actividades institucionales

**User Story:** Como operador institucional quiero registrar clases dentro de una actividad y marcar asistencia por clase. Como ciudadano quiero ver mi historial de asistencia desde el portal.

**Archivos nuevos:**
- `legajos/models.py` — modelos `ClaseActividad` y `AsistenciaClase`
- `legajos/migrations/0033_claseactividad_asistenciaclase.py`
- `configuracion/selectors/clases.py`, `configuracion/services/clases.py`, `configuracion/forms/clases.py`, `configuracion/views/clases.py`
- `configuracion/templates/configuracion/clase_lista.html`, `clase_form.html`, `clase_asistencia.html`
- `portal/selectors/actividades_ciudadano.py` (función `get_asistencia_ciudadano_en_actividad`)
- `portal/views/ciudadano_actividades.py` (vista `ciudadano_detalle_actividad`)
- `portal/templates/portal/ciudadano/detalle_actividad.html`

**Archivos modificados:** `configuracion/urls.py`, `portal/urls.py`, `portal/templates/.../mis_actividades.html`, `configuracion/templates/.../actividad_detail.html`, `__init__.py` de selectors/services/views

**Descripción:** Capa de clases (sesiones) sobre las actividades institucionales. Gestión CRUD desde el backoffice con bloqueo de edición en clases futuras. Asistencia registrable con estados PRESENTE/AUSENTE/JUSTIFICADO/TARDANZA. Portal ciudadano muestra historial con porcentaje de asistencia.

---

## 2026-03-19 — US-022 Inscripción de ciudadanos a actividades institucionales

**User Story:** Como operador backoffice o ciudadano autenticado en el portal quiero inscribir un ciudadano a una actividad institucional para registrar su participación con código de confirmación, respetando tipo de acceso y cupo.

**Archivos modificados:**
- `legajos/models.py` — `InscriptoActividad`: `codigo_inscripcion`, `inscrito_por`, elimina `unique_together`, agrega `__str__`
- `legajos/services/actividades.py` — `inscribir_ciudadano_a_actividad`, `get_estado_inscripcion_ciudadano`, `InscripcionError`
- `legajos/services/__init__.py` — exports actualizados
- `configuracion/forms/institucional.py` — `InscripcionDirectaForm`
- `configuracion/selectors/instituciones.py` — `cupo_disponible` y `cupos_restantes` en `build_actividad_detail_context`
- `configuracion/services/actividades.py` — `aceptar_derivacion` refactorizado (reemplaza `get_or_create` por service)
- `configuracion/views/actividades.py` — `InscripcionDirectaView` + context `inscripcion_form`
- `configuracion/views/__init__.py`, `configuracion/urls.py` — export y URL nueva
- `portal/selectors/actividades_ciudadano.py` — `get_inscripciones_ciudadano`
- `portal/selectors/__init__.py`, `portal/views/ciudadano.py`, `portal/urls.py` — exports y URLs nuevas
- `configuracion/templates/configuracion/actividad_detail.html` — form inscripción, código en nómina, badge cupo corregido

**Archivos creados:**
- `legajos/migrations/0032_inscriptoactividad_codigo_inscripto_por.py`
- `portal/views/ciudadano_actividades.py`
- `portal/templates/portal/ciudadano/mis_actividades.html`

**Descripción:** Implementa el flujo completo de inscripción. Service central con `@transaction.atomic + select_for_update` para evitar race conditions en cupo. `unique_together` eliminado para permitir reinscripciones históricas. `aceptar_derivacion` corregido (ya no usa `get_or_create` que ignoraba estado). Bug de cupo=0 corregido en template.

---

## 2026-03-15 — US-020 Tipo de acceso en actividades institucionales

**User Story:** Como administrador quiero configurar el tipo de acceso de una actividad (LIBRE o REQUIERE_PROGRAMA) para controlar qué ciudadanos pueden inscribirse.

**Archivos modificados:**
- `legajos/models.py` — `TipoAcceso` y campos `tipo_acceso`/`programa_requerido` en `PlanFortalecimiento`
- `legajos/services/actividades.py` (nuevo) — `validar_acceso_actividad(actividad, ciudadano)`
- `legajos/services/__init__.py` — export
- `configuracion/forms/institucional.py` — campos nuevos en ambos forms con `clean()`
- `configuracion/templates/configuracion/plan_form.html`, `actividad_editar_form.html` — sección Alpine.js
- `portal/selectors/actividades_ciudadano.py` (nuevo) — `get_actividades_accesibles(ciudadano)`
- `portal/selectors/__init__.py` — export

**Migraciones:** `0031_planfortalecimiento_tipo_acceso_programa_requerido`

**Descripción:** Prerequisito para US-022. Agrega control de acceso por programa en actividades institucionales. La función `validar_acceso_actividad` será consumida por el flujo de inscripción a actividades.

---

## 2026-03-15 — US-017 Baja de ciudadano de un programa persistente

**User Story:** Como operador quiero dar de baja a un ciudadano de un programa persistente registrando motivo y fecha para cerrar su caso formalmente.

**Archivos modificados:**
- `legajos/models_programas.py` — agrega `DADO_DE_BAJA` al enum `InscripcionPrograma.Estado`
- `legajos/services/programas.py` — nuevo `BajaProgramaService` con transacción atómica (baja + cancelar turnos + cancelar flujo)
- `legajos/services/__init__.py` — export del nuevo service
- `legajos/views/programas.py` — nueva FBV `dar_de_baja_inscripcion`
- `legajos/urls.py` — nueva URL `acompanamiento/<int:inscripcion_id>/dar-de-baja/`
- `legajos/templates/legajos/programas/programa_detail.html` — botón baja + modal SweetAlert2 + badge `DADO_DE_BAJA`

**Migraciones:** `0030_inscripcionprograma_estado_dado_de_baja`

**Descripción:** Operación formal de baja desde el tab Acompañamientos del panel de programa. Cancela turnos PENDIENTE/CONFIRMADO del ciudadano vinculados al programa y cierra el flujo activo con log de motivo.

---

## 2026-03-15 — US-012 Derivación e inscripción de ciudadanos a programas

**User Story:** Como operador del backoffice quiero derivar o inscribir directamente a un ciudadano en un programa para iniciar su proceso de admisión formal a través del flujo configurado del programa.

**Archivos modificados:**
- `legajos/models_institucional.py` — `inscripcion_creada` en `DerivacionCiudadano`
- `legajos/permissions_institucional.py` — corrección de `puede_operar_programa` y compañeras
- `legajos/services/institucional.py` — `aceptar_derivacion_programa`, `rechazar_derivacion_programa`
- `legajos/forms/derivacion.py` — `DerivarProgramaForm` sobre `DerivacionCiudadano`
- `legajos/views/derivacion.py`, `legajos/views/derivacion_programa.py`, `legajos/views/programas.py`, `legajos/views/api_derivaciones.py`
- `legajos/urls.py` — nuevas URLs `derivacion_ciudadano_aceptar/rechazar`
- `legajos/templates/legajos/programas/programa_detail.html`, `derivar_programa.html`, `derivar_rechazar_ciudadano.html` (nuevo)

**Migraciones:** `0029_derivacionciudadano_inscripcion_creada`

**Descripción:** Implementa el flujo completo de derivación e inscripción de ciudadanos a programas usando `DerivacionCiudadano`. Reemplaza el flujo previo basado en `DerivacionPrograma` (que queda legacy para Ñachec). Al aceptar una derivación se crea `InscripcionPrograma` y el FlowRuntime inicia el flujo via signal automático. Se corrigen los permisos `puede_operar_programa` que bloqueaban a todos los no-superusuarios.

---

## 2026-03-15 — US-021 Unificación modelo de derivación

**User Story:** Como desarrollador quiero reemplazar `DerivacionInstitucional` por el nuevo modelo unificado `DerivacionCiudadano` para eliminar la duplicación de lógica y habilitar US-012.

**Archivos modificados:**
- `legajos/models_institucional.py` — nuevo modelo `DerivacionCiudadano`; `CasoInstitucional.derivacion_origen`; related_names legacy renombrados
- `legajos/forms/institucional.py` — `DerivacionCiudadanoForm`
- `legajos/services/institucional.py` — `DerivacionCiudadanoService`; fix bugs `responsable_caso` y `caso.notas`
- `legajos/services/__init__.py` — exporta `DerivacionCiudadanoService`
- `legajos/views/institucional.py` — queries y service al nuevo modelo; fix `select_related` inválidos; POST-only en `aceptar_derivacion`
- `legajos/views/programas.py` — anotaciones y queries al nuevo modelo
- `configuracion/selectors/instituciones.py` — badge derivaciones pendientes al nuevo modelo
- `legajos/admin.py` — `DerivacionCiudadanoAdmin`

**Migraciones:** `0026` (schema), `0027` (data), `0028` (AddField CasoInstitucional)

**Descripción:** Se unificaron los dos modelos de derivación existentes. `DerivacionCiudadano` reemplaza `DerivacionInstitucional` en toda la capa activa. La tabla legacy se conserva con `related_name=*_legacy`. Datos históricos migrados sin pérdida. Se corrigieron 3 bugs preexistentes detectados durante el review.

---

## 2026-03-15 — Fix: turnoOperar no aplicado en vistas operativas

**Tipo:** fix
**Error:** `docs/errores/2026-03-11_permisos-turnooperar-no-aplicado.md`
**Archivos modificados:**
- `turnos/mixins.py` — agregado `turno_operar_required` decorator y `TurnoOperarRequiredMixin`
- `turnos/views/turnos.py` — vistas operativas (agenda, bandeja, detalle, aprobar, rechazar, cancelar, completar) usan el nuevo guard de `turnoOperar`

**Descripción:** Las vistas operativas de turnos usaban un guard permisivo que solo verificaba "no ciudadano". Se corrigió para exigir el grupo `turnoOperar`, alineando el comportamiento con lo definido en US-011.

---

## 2026-03-15 — US-007 Editor Visual de Flujos

**User Story:** Como usuario con rol `programaConfigurar` quiero un editor visual drag & drop para diseñar el flujo de un programa para poder configurar visualmente la secuencia de pasos sin editar JSON manualmente.

**Archivos creados:**
- `flujos/views_urls.py` — URL HTML del editor
- `flujos/templates/flujos/editor.html` — template con mount point React
- `frontend/flow-editor/` — proyecto React + Vite completo (14 archivos)

**Archivos modificados:**
- `flujos/views.py` — view `editor_flujo` + imports
- `config/urls.py` — include `flujos_editor`
- `configuracion/templates/configuracion/programa_list.html` — enlace al editor

**Descripción:** Editor visual con React Flow embebido en el backoffice Django. Panel izquierdo con 5 tipos de nodo arrastrables (inicio, fin, accion_humana, espera, decision). Panel derecho de propiedades con editor de condiciones para nodos decision. Validación en tiempo real del grafo. Guardar borrador y publicar via API REST. Bundle compilado con Vite hacia `static/flujos/dist/`. CSRF via cookie. URLs inyectadas desde Django (no hardcodeadas).

---

## 2026-03-15 — US-006 Motor de Flujos Backend

**User Story:** Como desarrollador quiero un motor de flujos backend (app `flujos/`) con modelos, runtime y tipos de nodo para que los programas puedan tener flujos configurables que guíen la atención de un ciudadano desde su inscripción hasta el cierre del caso.

**Archivos creados:**
- `flujos/` (app nueva) — `models.py`, `runtime.py`, `forms.py`, `views.py`, `urls.py`, `admin.py`
- `flujos/migrations/0001_initial.py` — DDL completo con 4 tablas, UniqueConstraint y 5 índices

**Archivos modificados:**
- `config/settings.py` — `'flujos'` en INSTALLED_APPS
- `config/urls.py` — `path("api/", include("flujos.urls"))`
- `legajos/models_programas.py` — property `flujo_activo`
- `configuracion/views/programas.py` — validación flujo publicado en BORRADOR→ACTIVO
- `legajos/signals/programas.py` — signal `iniciar_flujo_inscripcion`

**Descripción:** App `flujos/` con 4 modelos (Flujo, VersionFlujo, InstanciaFlujo, InstanciaLog) y `FlowRuntime` para iniciar y avanzar instancias de ejecución. Evaluador de condiciones simple (`==`, `!=`, `>`, `>=`, `<`, `<=`, `in`). API REST JSON en 3 endpoints bajo `/api/flujos/`. La transición BORRADOR→ACTIVO en programas ahora requiere flujo publicado. Al crear una InscripcionPrograma se inicia el flujo automáticamente si el programa tiene flujo activo.

---

## 2026-03-15 — US-005 Wizard de configuración de programa

**User Story:** Como usuario con rol `programaConfigurar` quiero crear y editar un programa social mediante un wizard de configuración por pasos para dar de alta programas correctamente tipificados y listos para operar.

**Archivos modificados:**
- `legajos/models_programas.py` — campos nuevos: `naturaleza`, `estado` (reemplaza `activo`), `tiene_turnos`, `cupo_maximo`, `tiene_lista_espera`; `tipo` pasa a CharField libre; `verbose_name` en `icono`, `color`, `orden`; property `esta_activo`
- `legajos/views/programas.py` — filtros `activo=True` → `estado=ACTIVO`
- `legajos/forms/derivacion.py` — queryset actualizado
- `legajos/templatetags/programas_tags.py` — queryset actualizado
- `legajos/services/solapas.py` — queryset actualizado
- `portal/selectors/public.py` — 2 querysets actualizados
- `configuracion/urls.py` — 10 rutas del wizard
- `configuracion/views/__init__.py` — exports nuevos
- `core/views/public.py` — endpoint AJAX `load_subsecretarias`
- `core/urls.py` — ruta `ajax_load_subsecretarias`

**Archivos creados:**
- `legajos/migrations/0025_wizard_configuracion_programa.py` — RunPython para convertir `activo→estado`, luego RemoveField
- `configuracion/forms_programas.py` — 4 forms (uno por paso del wizard)
- `configuracion/views/programas.py` — wizard en FBVs con estado en sesión (creación + edición + cambio de estado)
- `configuracion/templates/configuracion/programa_list.html`
- `configuracion/templates/configuracion/programa_wizard_paso[1-4].html`

**Descripción:** Wizard de 4 pasos para crear y editar programas sociales. Paso 1: identidad y jerarquía organizacional (Secretaría→Subsecretaría, filtrado dinámico vía AJAX). Paso 2: naturaleza (UN_SOLO_ACTO/PERSISTENTE). Paso 3: capacidades (turnos, cupo, lista de espera). Paso 4: visual + confirmación. Los programas se crean en estado BORRADOR y se activan manualmente desde el listado. Migración `0025` convierte el campo `activo` (BooleanField) a `estado` (CharField con 4 valores) conservando datos existentes.

---

## 2026-03-15 — US-013 + US-018 + US-004 Búsqueda rápida, permisos instituciones y ABM Secretarías

**User Stories:**
- US-013: Como operador quiero buscar un ciudadano por nombre o DNI de forma rápida para atender consultas sin demoras
- US-018: Como administrador quiero que las vistas de instituciones estén protegidas por roles `institucionVer` e `institucionAdministrar`
- US-004: Como usuario con rol `secretariaConfigurar` quiero gestionar Secretarías y Subsecretarías y vincular Programas a una Subsecretaría

**Archivos creados:**
- `legajos/selectors/ciudadanos.py` — `buscar_ciudadanos_rapido(q)` con búsqueda por DNI o nombre (max 10 resultados)
- `legajos/views_ciudadanos_api.py` — endpoint AJAX `ciudadano_buscar_api` con `@login_required` + `@group_required`
- `core/models_secretaria.py` — models `Secretaria` y `Subsecretaria` con `puede_eliminarse()`
- `core/migrations/0008_secretaria_subsecretaria.py` — migración de ambas tablas
- `legajos/migrations/0024_programa_subsecretaria.py` — FK `subsecretaria` en `Programa`
- `configuracion/forms_secretaria.py` — `SecretariaForm` y `SubsecretariaForm`
- `configuracion/views/secretaria.py` — 8 CBVs con `GroupRequiredMixin` + manejo de `ProtectedError`
- `configuracion/templates/configuracion/secretaria_list.html` — lista con SweetAlert2
- `configuracion/templates/configuracion/secretaria_form.html`
- `configuracion/templates/configuracion/secretaria_confirm_delete.html`
- `configuracion/templates/configuracion/subsecretaria_list.html` — lista con SweetAlert2
- `configuracion/templates/configuracion/subsecretaria_form.html`
- `configuracion/templates/configuracion/subsecretaria_confirm_delete.html`

**Archivos modificados:**
- `core/mixins.py` — `GroupRequiredMixin` ahora redirige a login para usuarios no autenticados
- `core/decorators.py` — `group_required` extendido con `redirect_to` opcional (retrocompatible)
- `core/models.py` — re-exporta `Secretaria` y `Subsecretaria`
- `configuracion/views/institucional.py` — reemplazado control ad-hoc por `LoginRequiredMixin + GroupRequiredMixin` en todas las CBVs; fix de `success_url`
- `configuracion/views/__init__.py` — exporta las 8 vistas nuevas
- `configuracion/urls.py` — 8 rutas nuevas para secretarías/subsecretarías
- `legajos/views/institucional.py` — `@require_ver_institucion` reemplazado por `@group_required` con `redirect_to`
- `legajos/models_programas.py` — FK `subsecretaria` nullable en `Programa`
- `legajos/urls.py` — ruta `ciudadano_buscar_api` (antes de `<int:pk>` para evitar colisión)
- `templates/includes/navbar.html` — componente Alpine.js de búsqueda con debounce 300ms

**Descripción:** Tres features implementadas simultáneamente. La búsqueda rápida (US-013) agrega un widget en la navbar con resultados en tiempo real. Los permisos de instituciones (US-018) reemplaza el control de acceso ad-hoc por el patrón `GroupRequiredMixin` consistente con el resto del sistema. El ABM de secretarías (US-004) agrega la jerarquía organizacional Secretaría→Subsecretaría→Programa con CRUD completo protegido por `secretariaConfigurar`.

---

## 2026-03-15 — US-011 Data migration de roles y permisos

**User Story:** Como administrador del sistema quiero que todos los roles del backoffice existan como grupos Django con sus nombres definitivos acordados, y que los grupos con nombres viejos sean migrados automáticamente.

**Archivos modificados:**
- `turnos/mixins.py` — reemplazado `'Administradores de Turnos'` por `'turnoConfigurar'` en `admin_turnos_required` y `AdminTurnosRequiredMixin`

**Archivos verificados (sin cambios necesarios):**
- `users/management/commands/setup_grupos.py` — ya estaba completo con 15 roles operativos, 5 grupos especiales y 4 renombres legacy

**Descripción:** Se unificaron los nombres de grupos Django con los acordados en la sesión de /definir roles. El management command `setup_grupos` crea idempotentemente todos los grupos del sistema y migra los 4 nombres legacy. El fix en mixins.py cierra los errores `2026-03-11_permisos-turnoconfigurar-nombre-viejo.md` y `2026-03-11_permisos-turnooperar-no-aplicado.md` (este último parcialmente — las vistas operativas de turnos quedan pendientes inline con US correspondientes).

**Orden de deploy:** ejecutar `python manage.py setup_grupos` antes de deployar el código para evitar ventana de inconsistencia.

---

## 2026-03-13 — Refactor DX Slice 47: packaging de la familia `views_nachec_*` en `legajos`

**Archivos modificados:**
- `legajos/views/__init__.py`
- `legajos/views/nachec_cierre.py`
- `legajos/views/nachec_dashboard.py`
- `legajos/views/nachec_decisiones.py`
- `legajos/views/nachec_operacion.py`
- `legajos/views/nachec_prestaciones.py`
- `legajos/views_nachec_cierre.py`
- `legajos/views_nachec_dashboard.py`
- `legajos/views_nachec_decisiones.py`
- `legajos/views_nachec_operacion.py`
- `legajos/views_nachec_prestaciones.py`
- `legajos/tests/test_nachec_package.py`

**Descripción:** Se movió al paquete `legajos/views/` la familia completa `views_nachec_*`, manteniendo wrappers legacy y sin tocar las transiciones internas del programa. Con este corte, el packaging estructural de `legajos` quedó prácticamente completo en views, forms, services y selectors.

## 2026-03-13 — Refactor DX Slice 46: packaging de `views_clinico` en `legajos`

**Archivos modificados:**
- `legajos/views/__init__.py`
- `legajos/views/clinico.py`
- `legajos/views_clinico.py`
- `legajos/tests/test_clinico_package.py`

**Descripción:** Se movió `views_clinico.py` al paquete `legajos/views/` manteniendo wrapper legacy compatible y smoke test de exports. Con este corte, la mayor parte del dominio clínico ya quedó alineada con la estructura nueva sin alterar comportamiento funcional.

## 2026-03-13 — Refactor DX Slice 45: packaging de `views_institucional` en `legajos`

**Archivos modificados:**
- `legajos/views/__init__.py`
- `legajos/views/institucional.py`
- `legajos/views_institucional.py`
- `legajos/tests/test_institucional_package.py`

**Descripción:** Se movió `views_institucional.py` al paquete `legajos/views/` manteniendo wrapper legacy compatible y smoke test de exports. El cambio no reordena reglas del dominio institucional, pero deja esa superficie alineada con la estructura nueva del módulo.

## 2026-03-13 — Refactor DX Slice 44: packaging de `views_derivacion_programa` en `legajos`

**Archivos modificados:**
- `legajos/views/__init__.py`
- `legajos/views/derivacion_programa.py`
- `legajos/views_derivacion_programa.py`
- `legajos/tests/test_derivacion_programa_package.py`

**Descripción:** Luego de extraer el workflow a service, `views_derivacion_programa.py` se movió al paquete `legajos/views/` con wrapper legacy compatible y smoke test de exports. El borde programas/`ÑACHEC` ya quedó alineado con el packaging nuevo sin arrastrar lógica pesada en la capa HTTP.

## 2026-03-13 — Refactor DX Slice 43: service layer para derivaciones de programa

**Archivos modificados:**
- `legajos/services/__init__.py`
- `legajos/services/derivaciones_programa.py`
- `legajos/services_derivaciones_programa.py`
- `legajos/views_derivacion_programa.py`
- `legajos/tests/test_derivaciones_programa_service.py`

**Descripción:** Se extrajo de `views_derivacion_programa.py` la orquestación de aceptación, rechazo y flujo especial de `ÑACHEC` hacia un service dedicado. El cambio fija el borde entre programas y `ÑACHEC`, reduce lógica sensible en la view y agrega tests del workflow crítico antes de una futura modularización física.

## 2026-03-13 — Refactor DX Slice 42: packaging de `views_programas` y `views_solapas` en `legajos`

**Archivos modificados:**
- `legajos/views/__init__.py`
- `legajos/views/programas.py`
- `legajos/views/solapas.py`
- `legajos/views_programas.py`
- `legajos/views_solapas.py`
- `legajos/tests/test_programas_package.py`
- `legajos/tests/test_solapas_package.py`

**Descripción:** Se movieron `views_programas.py` y `views_solapas.py` al paquete `legajos/views/`, manteniendo compatibilidad con los módulos históricos y agregando smoke tests de exports. Con este corte, el packaging de `views` en `legajos` ya cubre casi toda la superficie no crítica.

## 2026-03-13 — Refactor DX Slice 41: packaging de `views_operativa` en `legajos`

**Archivos modificados:**
- `legajos/views/__init__.py`
- `legajos/views/operativa.py`
- `legajos/views_operativa.py`
- `legajos/tests/test_operativa_package.py`

**Descripción:** Se movió `views_operativa.py` a `legajos/views/operativa.py`, manteniendo compatibilidad con el módulo histórico y agregando un smoke test de exports. Con esto, el packaging de `legajos` ya agotó prácticamente la superficie de bajo riesgo dentro de `views`.

## 2026-03-13 — Refactor DX Slice 40: packaging de views de soporte en `legajos`

**Archivos modificados:**
- `legajos/views/__init__.py`
- `legajos/views/acompanamiento.py`
- `legajos/views/alertas.py`
- `legajos/views/api_derivaciones.py`
- `legajos/views/cursos.py`
- `legajos/views/derivacion.py`
- `legajos/views_acompanamiento.py`
- `legajos/views_alertas.py`
- `legajos/views_api_derivaciones.py`
- `legajos/views_cursos.py`
- `legajos/views_derivacion.py`
- `legajos/tests/test_support_views_package.py`

**Descripción:** Se movió a `legajos/views/` otro bloque de views de bajo riesgo: alertas, cursos, derivación simple, API de derivaciones y acompañamiento. Los wrappers legacy se mantienen, y las zonas más sensibles de la app quedaron explícitamente fuera de este corte.

## 2026-03-13 — Refactor DX Slice 39: packaging de views auxiliares de contactos en `legajos`

**Archivos modificados:**
- `legajos/views/__init__.py`
- `legajos/views/contactos_api.py`
- `legajos/views/contactos_panel.py`
- `legajos/views/dashboard_contactos.py`
- `legajos/views/dashboard_simple.py`
- `legajos/views/historial_contactos.py`
- `legajos/views/red_contactos.py`
- `legajos/views/simple_contactos.py`
- `legajos/views_contactos_api.py`
- `legajos/views_contactos_panel.py`
- `legajos/views_dashboard_contactos.py`
- `legajos/views_dashboard_simple.py`
- `legajos/views_historial_contactos.py`
- `legajos/views_red_contactos.py`
- `legajos/views_simple_contactos.py`
- `legajos/tests/test_contactos_fachada.py`

**Descripción:** Se empaquetó en `legajos/views/` el bloque auxiliar de contactos y dashboards simples, manteniendo wrappers compatibles para los módulos legacy. El corte deja fuera por ahora las views más sensibles de clínica e institucional, pero reduce otra porción grande de deuda estructural en la app.

## 2026-03-13 — Refactor DX Slice 38: packaging de forms en `legajos`

**Archivos modificados:**
- `legajos/forms.py`
- `legajos/forms_ciudadanos.py`
- `legajos/forms_clinico.py`
- `legajos/forms_contactos.py`
- `legajos/forms_derivacion.py`
- `legajos/forms_institucional.py`
- `legajos/forms_operativa.py`
- `legajos/forms/__init__.py`
- `legajos/forms/ciudadanos.py`
- `legajos/forms/clinico.py`
- `legajos/forms/contactos.py`
- `legajos/forms/derivacion.py`
- `legajos/forms/institucional.py`
- `legajos/forms/operativa.py`
- `legajos/tests/test_forms_fachada.py`

**Descripción:** Se convirtió la familia de formularios de `legajos` en un paquete real, reaprovechando el corte por dominio ya existente y manteniendo wrappers compatibles para imports históricos. El cambio no modifica formularios visibles ni flujos, pero completa el packaging de la capa de forms de la app más grande del proyecto.

## 2026-03-13 — Refactor DX Slice 37: packaging de services y selectors en `legajos`

**Archivos modificados:**
- `legajos/services/__init__.py`
- `legajos/services/admision.py`
- `legajos/services/ciudadanos.py`
- `legajos/services/contactos.py`
- `legajos/services/legajos.py`
- `legajos/services/solapas.py`
- `legajos/services_admision.py`
- `legajos/services_ciudadanos.py`
- `legajos/services_contactos.py`
- `legajos/services_legajos.py`
- `legajos/services_solapas.py`
- `legajos/selectors/__init__.py`
- `legajos/selectors/ciudadanos.py`
- `legajos/selectors/contactos.py`
- `legajos/selectors/legajos.py`
- `legajos/selectors_ciudadanos.py`
- `legajos/selectors_contactos.py`
- `legajos/selectors_legajos.py`
- `legajos/tests/test_package_exports.py`

**Descripción:** Se agrupó en `legajos` la capa reutilizable ya estabilizada de `services` y `selectors`, manteniendo wrappers compatibles para los módulos legacy. El objetivo fue seguir bajando deuda estructural en la app más grande del proyecto sin tocar todavía el wiring sensible de `views` y `signals`.

## 2026-03-13 — Refactor DX slice 14: `chatbot` contrato frontend/backend y CSRF

**User Story:** Como equipo de desarrollo quiero alinear el contrato entre frontend y backend del módulo `chatbot` y retirar `@csrf_exempt` en sus endpoints principales para evitar deuda funcional y mejorar seguridad.

**Archivos modificados:**
- `chatbot/views_public.py`
- `chatbot/views_admin.py`
- `chatbot/services_chatbot.py`
- `chatbot/templates/chatbot/chat_interface.html`
- `chatbot/templates/chatbot/admin_dashboard.html`
- `chatbot/static/chatbot/js/chat.js`
- `chatbot/tests/test_chatbot_services.py`

**Descripcion:** Se implementó el slice 14 del refactor DX sobre `chatbot`, corrigiendo una inconsistencia real: el JS del chat consumía rutas y shape de respuesta distintos a los expuestos por Django. Se pasaron URLs al frontend desde templates, se alineó la respuesta de `send_message` con lo que consume el JS, se agregaron tests de contrato/CSRF y se retiró `@csrf_exempt` de los endpoints principales del módulo. El cambio mantiene la misma superficie funcional visible pero elimina una fuente concreta de rotura silenciosa.

## 2026-03-13 — Refactor DX slice 13: `chatbot` modularización y validación de payloads

**User Story:** Como equipo de desarrollo quiero separar la superficie pública y administrativa de `chatbot`, extraer lecturas reutilizables y validar payloads JSON para reducir lógica en `views.py` sin cambiar las rutas del módulo.

**Archivos creados:**
- `chatbot/forms_chatbot.py`
- `chatbot/selectors_chatbot.py`
- `chatbot/services_chatbot.py`
- `chatbot/views_public.py`
- `chatbot/views_admin.py`
- `chatbot/tests/__init__.py`
- `chatbot/tests/test_chatbot_services.py`

**Archivos modificados:**
- `chatbot/views.py`

**Descripcion:** Se implementó el slice 13 del refactor DX sobre `chatbot`. El módulo ahora separa chat público y administración, valida payloads con forms livianos, encapsula el workflow principal y las operaciones administrativas en services, y usa selectors para lecturas del dashboard y conversaciones. `views.py` quedó como fachada compatible y no hubo cambios de URLs, modelos ni templates.

## 2026-03-13 — Refactor DX slice 12: migración inicial de consumidores a namespaces

**User Story:** Como equipo de desarrollo quiero empezar a consumir namespaces explícitos en templates y pantallas internas para reducir dependencia de names legacy y preparar el retiro gradual de la compatibilidad dual.

**Archivos modificados:**
- `core/templates/core/relevamientos.html`
- `core/templates/core/relevamiento_detail.html`
- `core/templates/relevamientos.html`
- `core/templates/relevamiento_detail.html`
- `users/templates/user/user_list.html`
- `users/templates/user/user_form.html`
- `users/templates/user/user_confirm_delete.html`
- `templates/includes/sidebar/opciones.html`
- `templates/includes/header.html`
- `templates/403.html`
- `templates/500.html`
- `templates/relevamientos.html`
- `templates/relevamiento_detail.html`

**Descripcion:** Se implementó el slice 12 del refactor DX, migrando consumidores claros y no ambiguos desde names legacy a `core:*` y `users:*`. Se dejaron fuera `login/logout` porque todavía conviven con `django.contrib.auth.urls` y requieren una decisión más cuidadosa. El objetivo de este corte fue empezar a consumir los namespaces nuevos ya habilitados en el slice 11 sin introducir riesgo innecesario.

## 2026-03-13 — Refactor DX slice 11: namespaces compatibles en `users`, `core` y `healthcheck`

**User Story:** Como equipo de desarrollo quiero estandarizar namespaces en módulos raíz del proyecto sin romper los nombres legacy que todavía usa el código existente.

**Archivos creados:**
- `core/tests/test_url_namespaces.py`

**Archivos modificados:**
- `config/urls.py`
- `users/urls.py`
- `core/urls.py`
- `healthcheck/urls.py`

**Descripcion:** Se implementó el slice 11 del refactor DX sobre URLs. Se agregaron `app_name` faltantes en `users`, `core` y `healthcheck`, y `config/urls.py` ahora expone también includes namespaced sin quitar los includes legacy. Esto habilita usar `users:*`, `core:*` y `healthcheck:*` de forma incremental, preservando compatibilidad con los names antiguos mientras el proyecto termina de migrar.

## 2026-03-13 — Refactor DX slice 10: `configuracion` modularización física de views

**User Story:** Como equipo de desarrollo quiero separar físicamente `configuracion/views.py` por dominios para reducir fricción de navegación y edición sin cambiar URLs ni comportamiento del módulo.

**Archivos creados:**
- `configuracion/views_geografia.py`
- `configuracion/views_institucional.py`
- `configuracion/views_actividades.py`

**Archivos modificados:**
- `configuracion/views.py`

**Descripcion:** Se implementó el décimo slice del refactor DX, enfocado en modularización física de `configuracion`. El archivo monolítico se dividió en geografía, institucional y actividades, reutilizando además `TimestampedSuccessUrlMixin` donde ya existía el patrón de redirect con query timestamp. `views.py` quedó como fachada compatible y no hubo cambios de rutas, modelos ni templates.

## 2026-03-13 — Refactor DX slice 9: `conversaciones` API auxiliar alineada

**User Story:** Como equipo de desarrollo quiero alinear las APIs auxiliares de `conversaciones` con el patrón de selectors y services para que el módulo no mantenga dos estilos arquitectónicos distintos.

**Archivos modificados:**
- `conversaciones/api_views.py`
- `conversaciones/api_extra.py`
- `conversaciones/selectors_conversaciones.py`
- `conversaciones/services_chat.py`
- `conversaciones/tests/test_chat_services.py`

**Descripcion:** Se implementó el noveno slice del refactor DX, cerrando la capa API auxiliar del chat. Las alertas, previews, marcado de leídos y el detalle mínimo en vivo ahora reutilizan selectors y services ya introducidos en el slice 8, en lugar de repetir queries y permisos inline. No hubo cambios de rutas, modelos ni migraciones.

## 2026-03-13 — Refactor DX slice 8: `conversaciones` modularización y selectors

**User Story:** Como equipo de desarrollo quiero desacoplar el módulo `conversaciones` separando vistas públicas y de backoffice, extrayendo queries reutilizables y validación de payloads para reducir lógica en `views.py` sin cambiar las URLs.

**Archivos creados:**
- `conversaciones/forms_chat.py`
- `conversaciones/selectors_conversaciones.py`
- `conversaciones/services_chat.py`
- `conversaciones/views_public.py`
- `conversaciones/views_backoffice.py`
- `conversaciones/tests/__init__.py`
- `conversaciones/tests/test_chat_services.py`

**Archivos modificados:**
- `conversaciones/views.py`

**Descripcion:** Se implementó el octavo slice del refactor DX, focalizado en `conversaciones`. La bandeja, métricas y detalle pasaron a depender de selectors explícitos; la orquestación de inicio de conversación, mensajes, cierre, cola y asignación automática quedó encapsulada en `services_chat.py`; y `views.py` pasó a ser una fachada compatible que reexporta `views_public.py` y `views_backoffice.py`. Se mantuvieron las URLs y el contrato AJAX/WebSocket actual, incluyendo los `@csrf_exempt` legacy donde removerlos sería riesgoso sin tocar frontend.

## 2026-03-13 — Refactor DX slice 7: `legajos` fachada pura de views

**User Story:** Como equipo de desarrollo quiero completar la separación física de `legajos/views.py` para que el archivo quede como una fachada pura y el dominio operativo/institucional tenga su propio módulo mantenible.

**Archivos creados:**
- `legajos/views_operativa.py`

**Archivos modificados:**
- `legajos/views.py`

**Descripcion:** Se implementó el séptimo slice del refactor DX sobre `legajos`, completando la modularización física del módulo de views. El bloque operativo e institucional se movió a `views_operativa.py` y `views.py` quedó como fachada de reexportación compatible para ciudadanía/admisión, clínica, contactos y operativa. No hubo cambios funcionales, de modelos, URLs ni migraciones; el objetivo fue reducir el tamaño cognitivo del módulo y dejar una base más predecible para seguir refactorizando.

## 2026-03-13 — Refactor DX Slice 3: legajos ciudadanos y admisión

**User Story:** Como equipo de desarrollo quiero refactorizar el flujo de ciudadanos y admisión en `legajos` para reducir lógica en views, ordenar el manejo de sesión y dejar una base más mantenible para el resto del módulo.

**Archivos creados:**
- `legajos/selectors_ciudadanos.py`
- `legajos/services_ciudadanos.py`
- `legajos/services_admision.py`
- `legajos/tests/__init__.py`
- `legajos/tests/test_ciudadanos_admision.py`

**Archivos modificados:**
- `legajos/forms.py`
- `legajos/views.py`
- `legajos/urls.py`
- `legajos/templates/legajos/ciudadano_renaper_form.html`

**Descripcion:** Se ejecutó el tercer slice del refactor DX sobre `legajos`, acotado a ciudadanos y admisión. Se extrajeron selectors para lista/detalle y métricas, services para RENAPER y para el wizard de admisión con manejo de sesión, se limpiaron formularios por contexto y se corrigió la duplicación real de rutas en `legajos/urls.py`. No hubo cambios de modelo ni migraciones.

## 2026-03-13 — Refactor DX Slice 2: configuracion institucional y actividades

**User Story:** Como equipo de desarrollo quiero seguir estandarizando la capa de configuración institucional con services, selectors y forms explícitos para reducir acoplamiento en views y poder evolucionar el módulo sin romper workflows operativos.

**Archivos creados:**
- `configuracion/selectors_instituciones.py`
- `configuracion/services_actividades.py`
- `configuracion/tests/__init__.py`
- `configuracion/tests/test_services_actividades.py`

**Archivos modificados:**
- `configuracion/forms.py`
- `configuracion/views.py`
- `configuracion/views_extra.py`
- `configuracion/templates/configuracion/inscripto_form.html`
- `configuracion/templates/configuracion/staff_editar_form.html`
- `configuracion/templates/configuracion/actividad_editar_form.html`

**Descripcion:** Se ejecutó el segundo slice del refactor DX sobre `configuracion`, focalizado en instituciones y actividades. Las queries de detalle institucional y de actividad se extrajeron a selectors, los workflows de staff/derivaciones/inscriptos/actividad quedaron en services transaccionales y los formularios dejaron de depender de `POST` raw en los flujos principales. No hubo cambios de modelos ni migraciones.

## 2026-03-13 — Refactor DX Slice 1: users, portal institucional y turnos

**User Story:** Como equipo de desarrollo quiero estandarizar la arquitectura interna con services, selectors, forms y views más delgadas para reducir costo de cambio y mejorar testabilidad sin alterar el comportamiento funcional del sistema.

**Archivos creados:**
- `core/mixins.py`
- `core/selectors_geografia.py`
- `users/selectors_usuarios.py`
- `users/services_admin.py`
- `users/views_admin.py`
- `users/views_auth.py`
- `portal/forms_public.py`
- `portal/selectors_public.py`
- `portal/services_registro.py`
- `portal/views_public.py`
- `turnos/selectors_turnos.py`
- `turnos/services_turnos.py`
- `users/tests/test_user_admin_services.py`
- `portal/tests/test_registro_institucion.py`
- `turnos/tests/test_turno_actions.py`

**Archivos modificados:**
- `core/views.py`
- `users/forms.py`
- `users/services.py`
- `users/views.py`
- `portal/views.py`
- `portal/urls.py`
- `turnos/views_backoffice.py`

**Descripcion:** Se implementó el primer slice del refactor estructural de DX. `users` movió persistencia de grupos/profile a services; `portal` institucional pasó de FBVs con POST raw a `FormView` + services/selectors y dejó de usar `@csrf_exempt` en ese flujo; `turnos` extrajo queries de backoffice a selectors y acciones de estado a services transaccionales. No hubo cambios de modelos ni migraciones.

## 2026-03-13 — Refactor DX slice 4: `legajos` flujo clínico base

**User Story:** Como equipo de desarrollo quiero refactorizar el flujo clínico base de `legajos` para separar queries, orquestación y formularios en evaluación, planes, seguimientos, derivaciones y acciones de cierre/reapertura.

**Archivos creados:**
- `legajos/selectors_legajos.py`
- `legajos/services_legajos.py`
- `legajos/tests/test_legajo_workflow.py`

**Archivos modificados:**
- `legajos/forms.py`
- `legajos/views.py`
- `legajos/templates/legajos/plan_form.html`
- `legajos/templates/legajos/legajo_cerrar.html`
- `legajos/templates/legajos/legajo_reabrir.html`

**Descripcion:** Se implementó el cuarto slice del refactor DX sobre `legajos`, acotado al legajo de atención. Las queries de listados y detalle pasaron a selectors; la orquestación de evaluación, planes, seguimientos, derivaciones y cierre/reapertura pasó a services; los forms dejaron de persistir JSON dinámico en `save()` y el template del plan dejó de ignorar los valores existentes al editar. No hubo cambios de modelos ni migraciones.

## 2026-03-13 — Refactor DX slice 5: `legajos` eventos, reportes y responsable

**User Story:** Como equipo de desarrollo quiero cerrar el hotspot restante del legajo clínico para ordenar eventos críticos, reportes, exportación y cambio de responsable sin depender de views y templates fuera de contrato con los modelos.

**Archivos modificados:**
- `legajos/forms.py`
- `legajos/selectors_legajos.py`
- `legajos/services_legajos.py`
- `legajos/views.py`
- `legajos/templates/legajos/evento_form.html`
- `legajos/templates/legajos/evento_list.html`
- `legajos/templates/legajos/evaluacion_list.html`
- `legajos/templates/legajos/plan_list.html`
- `legajos/templates/legajos/reportes.html`
- `legajos/templates/legajos/dispositivo_derivaciones.html`
- `legajos/tests/test_legajo_workflow.py`

**Descripcion:** Se implementó el quinto slice del refactor DX sobre `legajos`, enfocado en eventos críticos, reportes, exportación CSV, derivaciones por dispositivo y cambio de responsable. Se extrajeron selectors/services para estos flujos, `EventoCriticoForm` dejó de persistir side effects en `save()`, y se corrigieron templates que referenciaban campos inexistentes del modelo (`descripcion`, `gravedad`, `motivo_consulta`, `diagnostico`, `activo`, `origen`). No hubo cambios de modelo ni migraciones.

## 2026-03-13 — Refactor DX slice 6: `legajos` separación física de views por dominio

**User Story:** Como equipo de desarrollo quiero separar físicamente `legajos/views.py` por dominios para reducir el costo de navegación y edición sin tocar las URLs ni romper imports existentes.

**Archivos creados:**
- `legajos/views_ciudadanos.py`
- `legajos/views_clinico.py`

**Archivos modificados:**
- `legajos/views.py`

**Descripcion:** Se implementó el sexto slice del refactor DX sobre `legajos`, enfocado en modularización física. `views.py` quedó como fachada compatible y el contenido se repartió en `views_ciudadanos.py` y `views_clinico.py`. No hubo cambios funcionales deliberados, de modelos ni de rutas; el objetivo fue bajar el tamaño del archivo monolítico y dejar una base más predecible para seguir refactorizando el módulo.

## 2026-03-05 — Mejora de logging detallado

**User Story:** Como desarrollador, quiero logs detallados en tiempo real del backend, requests HTTP y nginx para diagnosticar problemas en producción.

**Archivos creados:**
- `core/middleware.py` — `RequestLoggingMiddleware`

**Archivos modificados:**
- `config/settings.py` — `console` handler en LOGGING, `django.request` a WARNING, middleware registrado
- `nginx.conf` — `log_format detailed` con `$request_time` y `$upstream_response_time`

**Descripcion:** Tres mejoras de observabilidad: (A) console handler para ver logs con `docker logs nodo-web`; (B) middleware que loguea cada request con método, URL, usuario, IP, status y duración; (D) formato de access log en nginx con tiempos de respuesta totales y de upstream.

---

## 2026-03-05 — [HOTFIX] Redis OOM causa WSDISCONNECT en WebSocket

**Archivos modificados:**
- `docker-compose.prod.yml` — Redis mem_limit 200m→400m, agregado maxmemory 350mb + allkeys-lru

**Descripcion:** WebSockets de alertas y conversaciones conectaban y desconectaban en 1-2 segundos. Causa: Redis sin `maxmemory-policy` se quedaba sin memoria y fallaba `channel_layer.group_add()`. Fix: aumentar limite y configurar eviccion LRU.

---

## 2026-03-04 — [HOTFIX] Error 400 al confirmar ciudadano via RENAPER

**Archivos modificados:**
- `config/settings_production.py` — eliminado `CSRF_COOKIE_HTTPONLY = True`
- `config/settings.py` — eliminado `CSRF_COOKIE_HTTPONLY = True` del bloque prd

**Descripcion:** Error 400 en POST `/legajos/ciudadanos/confirmar/`. Causa: `CSRF_COOKIE_HTTPONLY = True` interferia con validacion CSRF detras del proxy nginx+HTTPS. Fix: eliminar esa flag (no aporta seguridad real segun docs de Django y rompe el flujo CSRF en proxies SSL).

---

## 2026-03-04 — Módulo de Pedidos Telegram (Bot de Voz)

**User Story:** Como vendedor de Akuna Aberturas, quiero enviar un audio de voz por Telegram con los ítems de un pedido, para que el sistema lo interprete automáticamente y lo registre como pedido en AkunCalcu.

**Archivos creados:**
- `akuna_calc/pedidos/__init__.py`
- `akuna_calc/pedidos/apps.py`
- `akuna_calc/pedidos/models.py` — modelos `PedidoTelegram` + `ItemPedidoTelegram`
- `akuna_calc/pedidos/views.py` — endpoints API + vista lista
- `akuna_calc/pedidos/urls.py`
- `akuna_calc/pedidos/migrations/0001_initial.py`
- `akuna_calc/pedidos/templates/pedidos/pedidos_list.html`
- `docs/n8n-pedidos-workflow.md` — JSON del workflow n8n listo para importar

**Archivos modificados:**
- `akuna_calc/akuna_calc/settings.py` — agregado `pedidos` a `INSTALLED_APPS`
- `akuna_calc/akuna_calc/urls.py` — agregado `path('pedidos/', ...)`
- `docker-compose.yml` — agregada variable `TELEGRAM_BOT_SECRET`

**Descripción:** Implementación completa del flujo de pedidos por voz vía Telegram. El bot transcribe el audio (Whisper), extrae ítems con GPT-4o-mini, crea un borrador en Django, pide confirmación al usuario y según la respuesta confirma o cancela el pedido. Ver en `http://localhost:8080/pedidos/`.

---

## 2026-03-04 — Documento V1 del sistema

**User Story:** Como equipo de desarrollo, quiero un documento V1 del sistema.
**Archivos creados:** `docs/V1-sistema.md`
**Descripción:** Análisis completo del sistema. Se documentaron 8 módulos, sus procesos, cálculos internos, arquitectura técnica, flujos de trabajo, integraciones y glosario del negocio.

---

## 2026-03-04 — Setup del equipo de agentes

**Descripción**: Se configuró la estructura del equipo de desarrollo con metodología Scrum guiado.
- Creado `CLAUDE.md` con roles, workflow y convenciones
- Creado `docs/team/` con backlog, sprint, decisions, changelog
- Creados comandos personalizados en `.claude/commands/`
- Inicializada memoria del proyecto en `memory/MEMORY.md`

---

## 2026-03-13 — Refactor DX Slice 15: `conversaciones` contrato real y CSRF

**Archivos modificados:**
- `conversaciones/views_public.py`
- `conversaciones/views_backoffice.py`
- `conversaciones/views.py`
- `conversaciones/templates/conversaciones/chat_ciudadano.html`
- `conversaciones/templates/conversaciones/detalle.html`
- `conversaciones/templates/conversaciones/lista.html`
- `conversaciones/tests/test_chat_services.py`

**Descripción:** Se corrigió una inconsistencia funcional real en `conversaciones`: el chat ciudadano evaluaba contra una URL resuelta por backoffice y los fetches JSON dependían de rutas hardcodeadas sin cabecera CSRF. El slice alinea el contrato renderizado entre templates y URLs namespaced, protege los POST JSON con CSRF y agrega tests de contrato para conversación pública y respuesta de operador.

---

## 2026-03-13 — Refactor DX Slice 16: `conversaciones` runtime de lista en vivo

**Archivos modificados:**
- `conversaciones/templates/conversaciones/lista.html`
- `static/custom/js/conversaciones_lista_ws.js`
- `conversaciones/tests/test_chat_services.py`

**Descripción:** Se eliminó la doble carga de `conversaciones_lista_ws.js` en la pantalla de lista y se movió el contrato de URLs/runtime a atributos renderizados por Django. El WebSocket de lista ahora evita inicialización duplicada, usa URLs configurables para detalle/cierre/API y queda mejor preparado para la migración de namespaces.

---

## 2026-03-13 — Refactor DX Slice 17: `conversaciones` residual cross-app

**Archivos modificados:**
- `templates/includes/base.html`
- `static/custom/js/conversaciones_tiempo_real_global.js`
- `static/custom/js/conversaciones_tiempo_real.js`
- `static/custom/js/alertas_conversaciones_fallback.js`
- `static/custom/js/alertas_conversaciones_simple.js`
- `conversaciones/templates/conversaciones/detalle.html`
- `portal/templates/portal/ciudadano/consulta_detalle.html`
- `conversaciones/tests/test_chat_services.py`

**Descripción:** Se alinearon consumidores residuales de `conversaciones` fuera de la lista principal. Los scripts globales ahora toman URLs desde una configuración renderizada por Django, el detalle de operador deja de hardcodear el path WebSocket y el portal ciudadano deja de construir manualmente la URL de mensajes. El objetivo fue cerrar la deuda cross-app del módulo antes de pasar al siguiente hotspot.

---

## 2026-03-13 — Refactor DX Slice 18: `portal` consultas ciudadanas

**Archivos modificados:**
- `portal/forms.py`
- `portal/views_ciudadano.py`
- `portal/templates/portal/ciudadano/nueva_consulta.html`
- `portal/selectors_ciudadano.py`
- `portal/services_consultas.py`
- `portal/views_ciudadano_consultas.py`
- `portal/tests/test_ciudadano_consultas.py`

**Descripción:** Se extrajo el subdominio de consultas ciudadanas de `portal/views_ciudadano.py` hacia selectors, services y vistas dedicadas. El flujo de nueva consulta y envío de mensaje deja de depender de `POST` raw y pasa a forms explícitos. También se agregan tests para ownership, validación y creación de conversación/mensaje.

---

## 2026-03-13 — Refactor DX Slice 19: `portal` turnos ciudadano

**Archivos modificados:**
- `portal/forms.py`
- `portal/views_ciudadano.py`
- `portal/templates/portal/ciudadano/turno_confirmar.html`
- `portal/selectors_turnos_ciudadano.py`
- `portal/services_turnos_ciudadano.py`
- `portal/views_ciudadano_turnos.py`
- `portal/tests/test_ciudadano_turnos.py`

**Descripción:** Se extrajo el subdominio de turnos del portal ciudadano desde `portal/views_ciudadano.py` hacia selectors, services y vistas dedicadas. La confirmación del turno deja de procesar `POST` raw y pasa a un form explícito con validación de fecha y normalización del motivo. También se encapsuló la reserva/cancelación en services reutilizables y se agregaron tests del flujo ciudadano de turnos.

---

## 2026-03-13 — Refactor DX Slice 20: `portal` auth y registro ciudadano

**Archivos modificados:**
- `portal/views_ciudadano.py`
- `portal/views_ciudadano_auth.py`
- `portal/services_ciudadano_auth.py`
- `portal/tests/test_ciudadano_auth.py`

**Descripción:** Se extrajo la autenticación y el registro ciudadano hacia un módulo dedicado y un service de orquestación. El login conserva el throttling por IP, mientras que el alta por pasos deja de mezclar consulta RENAPER, sesión y creación de usuario/ciudadano dentro de `portal/views_ciudadano.py`. También se agregaron tests de flujo para legajo existente, cuenta ya registrada y alta nueva.

---

## 2026-03-13 — Refactor DX Slice 21: `portal` perfil, programas y mis datos

**Archivos modificados:**
- `portal/views_ciudadano.py`
- `portal/selectors_ciudadano_perfil.py`
- `portal/services_ciudadano_perfil.py`
- `portal/views_ciudadano_perfil.py`
- `portal/tests/test_ciudadano_perfil.py`

**Descripción:** Se extrajo el resto del perfil ciudadano fuera de `portal/views_ciudadano.py`. El dashboard, programas, mis datos y cambio de email/password ahora viven en un módulo dedicado con selectors y services propios. También se encapsuló la solicitud/confirmación de cambio de email y se agregaron tests de ownership e integridad del cambio de email.

---

## 2026-03-13 — Refactor DX Slice 22: `ÑACHEC` prestaciones, cierre y dashboard

**Archivos modificados:**
- `legajos/views_nachec.py`
- `legajos/views_nachec_prestaciones.py`
- `legajos/views_nachec_cierre.py`
- `legajos/views_nachec_dashboard.py`
- `legajos/tests/test_nachec_fachada.py`

**Descripción:** Se extrajeron del monolito `legajos/views_nachec.py` los bloques de prestaciones, cierre/reapertura y dashboard hacia módulos dedicados, manteniendo `urls_nachec.py` intacto y usando `views_nachec.py` como fachada compatible. El objetivo del corte fue bajar drásticamente el tamaño del hotspot antes de entrar en flujos más sensibles de validación, evaluación y relevamiento.

---

## 2026-03-13 — Refactor DX Slice 23: `ÑACHEC` evaluación y activación de plan

**Archivos modificados:**
- `legajos/views_nachec.py`
- `legajos/views_nachec_decisiones.py`
- `legajos/tests/test_nachec_fachada.py`

**Descripción:** Se extrajo de `legajos/views_nachec.py` el bloque de evaluación profesional, solicitudes de ampliación/rechazo, activación de plan y transiciones cortas posteriores. El archivo principal del módulo queda aún más cerca de una fachada, mientras que el smoke test se amplía para fijar esos exports.

---

## 2026-03-13 — Refactor DX Slice 24: `ÑACHEC` operación territorial

**Archivos modificados:**
- `legajos/views_nachec.py`
- `legajos/views_nachec_operacion.py`
- `legajos/tests/test_nachec_fachada.py`

**Descripción:** Se extrajo el bloque operativo restante de `ÑACHEC` hacia `views_nachec_operacion.py`, incluyendo validación, asignación, reasignación, relevamiento y evidencias. `legajos/views_nachec.py` quedó finalmente como una fachada pura de compatibilidad, y el smoke test ahora cubre también esos exports.

---

## 2026-03-13 — Refactor DX Slice 25: `legajos` cleanup de forms

**Archivos modificados:**
- `legajos/forms.py`
- `legajos/forms_ciudadanos.py`
- `legajos/forms_clinico.py`
- `legajos/forms_operativa.py`
- `legajos/tests/test_forms_fachada.py`

**Descripción:** Se dividió `legajos/forms.py` por dominio funcional, separando ciudadanía/admisión, clínica y operativa. El archivo histórico quedó como fachada compatible para no romper imports existentes, y se agregó un smoke test para fijar los exports públicos del módulo.

---

## 2026-03-13 — Refactor DX Slice 26: `turnos` backoffice modular y CBVs

**Archivos modificados:**
- `turnos/mixins.py`
- `turnos/views_backoffice.py`
- `turnos/views_configuracion.py`
- `turnos/views_turnos.py`
- `turnos/tests/test_views_fachada.py`

**Descripción:** Se reorganizó el backoffice de `turnos` en módulos dedicados y se pasó el CRUD repetible de configuraciones/disponibilidades a CBVs, manteniendo `views_backoffice.py` como fachada compatible y sin cambiar URLs. Las acciones POST atómicas se mantuvieron como FBVs porque ahí no agregaban valor real las CBVs.

---

## 2026-03-13 — Refactor DX Slice 27: `contactos` selectors, service y fachada

**Archivos modificados:**
- `legajos/selectors_contactos.py`
- `legajos/services_contactos.py`
- `legajos/views_contactos_panel.py`
- `legajos/views_contactos_api.py`
- `legajos/views_simple_contactos.py`
- `legajos/tests/test_contactos_fachada.py`

**Descripción:** Se refactorizó el módulo legacy de contactos separando panel y APIs, extrayendo queries compuestas a selectors y el manejo de adjuntos a un service dedicado. `views_simple_contactos.py` quedó como fachada compatible. En el mismo corte se corrigieron referencias inconsistentes al modelo real dentro del módulo legacy, usando `EventoCritico.detalle` y `PlanIntervencion.actividades` en lugar de campos inexistentes.

---

## 2026-03-13 — Refactor DX Slice 28: namespaces y hardcodes residuales

**Archivos modificados:**
- `templates/includes/header.html`
- `templates/includes/navbar.html`
- `templates/components/chatbot_bubble.html`
- `templates/legajos/alertas_dashboard.html`
- `core/tests/test_url_namespaces.py`

**Descripción:** Se migraron consumidores residuales a namespaces estables y se retiraron hardcodes de rutas en puntos transversales del proyecto. El logout del backoffice ahora usa `users:logout`, el bubble de chatbot recibe su endpoint desde Django y el dashboard de alertas dejó de embeber rutas fijas de `conversaciones` y de cierre de alertas. Además se ampliaron los smoke tests de namespaces para fijar rutas críticas de `users`, `chatbot` y `conversaciones`.

---

## 2026-03-13 — Refactor DX Slice 29: desambiguación de names en `legajos`

**Archivos modificados:**
- `legajos/urls.py`
- `templates/components/alertas_eventos.html`
- `core/tests/test_url_namespaces.py`

**Descripción:** Se eliminó el conflicto de names duplicados en `legajos/urls.py`, renombrando las dos rutas `cerrar_alerta` a nombres explícitos según su dominio: `cerrar_alerta_evento` y `cerrar_alerta_ciudadano`. También se actualizó el único consumidor explícito del nombre anterior y se fijó el contrato con smoke tests.

---

## 2026-03-13 — Refactor DX Slice 30: `users` servicios con namespaces consistentes

**Archivos modificados:**
- `users/services.py`
- `users/tests/test_service_urls.py`

**Descripción:** Se alineó el contexto de listado de usuarios a namespaces estables, reemplazando reverses legacy y corrigiendo un `url_name` inconsistente (`usuario_borrar`) por `users:usuario_eliminar`. El contrato quedó cubierto con un test simple del service.

---

## 2026-03-13 — Refactor DX Slice 31: packaging de `turnos` y `users`

**Archivos modificados:**
- `turnos/views_backoffice.py`
- `turnos/views_configuracion.py`
- `turnos/views_turnos.py`
- `turnos/services_turnos.py`
- `turnos/selectors_turnos.py`
- `turnos/views/__init__.py`
- `turnos/views/backoffice.py`
- `turnos/views/configuracion.py`
- `turnos/views/turnos.py`
- `turnos/services/__init__.py`
- `turnos/services/notifications.py`
- `turnos/services/workflow.py`
- `turnos/selectors/__init__.py`
- `turnos/selectors/backoffice.py`
- `turnos/tests/test_package_exports.py`
- `users/views.py`
- `users/views_admin.py`
- `users/views_auth.py`
- `users/services.py`
- `users/services_admin.py`
- `users/selectors_usuarios.py`
- `users/signals.py`
- `users/views/__init__.py`
- `users/views/admin.py`
- `users/views/auth.py`
- `users/services/__init__.py`
- `users/services/admin.py`
- `users/services/listing.py`
- `users/selectors/__init__.py`
- `users/selectors/usuarios.py`
- `users/signals/__init__.py`
- `users/signals/profiles.py`
- `users/tests/test_package_exports.py`

**Descripción:** Se agruparon views, services, selectors y signals en paquetes reales dentro de `turnos` y `users`, manteniendo wrappers de compatibilidad en los módulos legacy para no romper imports existentes. En el mismo corte se alinearon los `success_url` de administración de usuarios al namespace `users:*` y se agregaron smoke tests para fijar los exports públicos de los paquetes.

---

## 2026-03-13 — Refactor DX Slice 32: packaging de `chatbot`

**Archivos modificados:**
- `chatbot/views.py`
- `chatbot/views_admin.py`
- `chatbot/views_public.py`
- `chatbot/forms_chatbot.py`
- `chatbot/services_chatbot.py`
- `chatbot/selectors_chatbot.py`
- `chatbot/views/__init__.py`
- `chatbot/views/admin.py`
- `chatbot/views/public.py`
- `chatbot/forms/__init__.py`
- `chatbot/forms/chat.py`
- `chatbot/services/__init__.py`
- `chatbot/services/chat.py`
- `chatbot/selectors/__init__.py`
- `chatbot/selectors/chat.py`
- `chatbot/tests/test_package_exports.py`

**Descripción:** Se agrupó `chatbot` en paquetes reales de views, forms, services y selectors, dejando wrappers compatibles para los módulos legacy y preservando el export histórico de `EnhancedChatbotService` en `services_chatbot.py`. El módulo quedó alineado con el patrón de packaging ya aplicado en `turnos` y `users`.

---

## 2026-03-13 — Refactor DX Slice 33: packaging de `configuracion`

**Archivos modificados:**
- `configuracion/views.py`
- `configuracion/views_actividades.py`
- `configuracion/views_extra.py`
- `configuracion/views_geografia.py`
- `configuracion/views_institucional.py`
- `configuracion/forms.py`
- `configuracion/services_actividades.py`
- `configuracion/selectors_instituciones.py`
- `configuracion/views/__init__.py`
- `configuracion/views/actividades.py`
- `configuracion/views/extra.py`
- `configuracion/views/geografia.py`
- `configuracion/views/institucional.py`
- `configuracion/forms/__init__.py`
- `configuracion/forms/institucional.py`
- `configuracion/services/__init__.py`
- `configuracion/services/actividades.py`
- `configuracion/selectors/__init__.py`
- `configuracion/selectors/instituciones.py`
- `configuracion/tests/test_package_exports.py`

**Descripción:** Se agrupó `configuracion` en paquetes reales de views, forms, services y selectors. Los módulos legacy por dominio quedaron como wrappers compatibles, `configuracion.views` y `configuracion.forms` pasaron a ser paquetes reales y se agregaron smoke tests para fijar el contrato público del packaging.

---

## 2026-03-13 — Refactor DX Slice 34: packaging de `portal`

**Archivos modificados:**
- `portal/views.py`
- `portal/views_public.py`
- `portal/views_ciudadano.py`
- `portal/views_ciudadano_auth.py`
- `portal/views_ciudadano_consultas.py`
- `portal/views_ciudadano_perfil.py`
- `portal/views_ciudadano_turnos.py`
- `portal/forms.py`
- `portal/forms_public.py`
- `portal/services_ciudadano_auth.py`
- `portal/services_ciudadano_perfil.py`
- `portal/services_consultas.py`
- `portal/services_registro.py`
- `portal/services_turnos_ciudadano.py`
- `portal/selectors_ciudadano.py`
- `portal/selectors_ciudadano_perfil.py`
- `portal/selectors_public.py`
- `portal/selectors_turnos_ciudadano.py`
- `portal/views/__init__.py`
- `portal/views/public.py`
- `portal/views/ciudadano.py`
- `portal/views/ciudadano_auth.py`
- `portal/views/ciudadano_consultas.py`
- `portal/views/ciudadano_perfil.py`
- `portal/views/ciudadano_turnos.py`
- `portal/forms/__init__.py`
- `portal/forms/ciudadano.py`
- `portal/forms/public.py`
- `portal/services/__init__.py`
- `portal/services/ciudadano_auth.py`
- `portal/services/ciudadano_perfil.py`
- `portal/services/consultas.py`
- `portal/services/registro.py`
- `portal/services/turnos_ciudadano.py`
- `portal/selectors/__init__.py`
- `portal/selectors/ciudadano.py`
- `portal/selectors/ciudadano_perfil.py`
- `portal/selectors/public.py`
- `portal/selectors/turnos_ciudadano.py`
- `portal/tests/test_package_exports.py`
- `portal/tests/test_ciudadano_auth.py`
- `portal/tests/test_ciudadano_consultas.py`
- `portal/tests/test_ciudadano_perfil.py`

**Descripción:** Se agrupó `portal` en paquetes reales de views, forms, services y selectors, manteniendo wrappers de compatibilidad para los módulos legacy. También se actualizaron los tests del portal para parchear internals sobre los paths reales del paquete y no sobre wrappers históricos.

---

## 2026-03-13 — Refactor DX Slice 35: packaging de `conversaciones`

**Archivos modificados:**
- `conversaciones/apps.py`
- `conversaciones/views.py`
- `conversaciones/views_backoffice.py`
- `conversaciones/views_public.py`
- `conversaciones/forms_chat.py`
- `conversaciones/services.py`
- `conversaciones/services_chat.py`
- `conversaciones/selectors_conversaciones.py`
- `conversaciones/signals.py`
- `conversaciones/signals_alertas.py`
- `conversaciones/views/__init__.py`
- `conversaciones/views/backoffice.py`
- `conversaciones/views/public.py`
- `conversaciones/forms/__init__.py`
- `conversaciones/forms/chat.py`
- `conversaciones/services/__init__.py`
- `conversaciones/services/core.py`
- `conversaciones/services/chat.py`
- `conversaciones/selectors/__init__.py`
- `conversaciones/selectors/conversaciones.py`
- `conversaciones/signals/__init__.py`
- `conversaciones/signals/alerts.py`
- `conversaciones/tests/test_chat_services.py`
- `conversaciones/tests/test_package_exports.py`

**Descripción:** Se agrupó `conversaciones` en paquetes reales de views, forms, services, selectors y signals. En el mismo corte se corrigió una inconsistencia estructural real en `apps.py`: la app tenía dos métodos `ready()` y solo se estaba ejecutando el último; ahora el registro de señales queda explícito y único. También se actualizaron los tests de patching al path real del paquete.

---

## 2026-03-13 — Refactor DX Slice 36: packaging liviano de `core`

**Archivos modificados:**
- `core/views.py`
- `core/forms.py`
- `core/selectors_geografia.py`
- `core/views/__init__.py`
- `core/views/public.py`
- `core/forms/__init__.py`
- `core/forms/general.py`
- `core/selectors/__init__.py`
- `core/selectors/geografia.py`
- `core/tests/test_package_exports.py`

**Descripción:** Se agrupó `core` en paquetes reales para `views`, `forms` y `selectors` del flujo principal, dejando fuera la auditoría pesada y la capa de signals. El objetivo fue alinear la cartografía base del proyecto sin tocar todavía los módulos de mayor riesgo operativo.

---

## 2026-03-13 — Refactor DX Slice 48: packaging restante de `services` en `legajos`

**Archivos modificados:**
- `legajos/services/__init__.py`
- `legajos/services/alertas.py`
- `legajos/services/filtros_usuario.py`
- `legajos/services/institucional.py`
- `legajos/services/nachec.py`
- `legajos/services_alertas.py`
- `legajos/services_filtros_usuario.py`
- `legajos/services_institucional.py`
- `legajos/services_nachec.py`
- `legajos/api_views.py`
- `legajos/signals_alertas.py`
- `legajos/views/alertas.py`
- `legajos/views/contactos_api.py`
- `legajos/views/institucional.py`
- `conversaciones/consumers.py`
- `conversaciones/signals/alerts.py`
- `legajos/tests/test_package_exports.py`

**Descripción:** Se terminó de agrupar en `legajos/services/` la familia de servicios que todavía seguía en módulos planos (`alertas`, `filtros_usuario`, `institucional`, `nachec`), manteniendo wrappers legacy compatibles. También se migraron consumidores internos al paquete nuevo y se amplió el smoke test de exports para fijar la API pública del paquete.

---

## 2026-03-13 — Refactor DX Slice 49: packaging de `signals` en `legajos`

**Archivos modificados:**
- `legajos/apps.py`
- `legajos/signals/__init__.py`
- `legajos/signals/core.py`
- `legajos/signals/alerts.py`
- `legajos/signals/historial.py`
- `legajos/signals/programas.py`
- `legajos/signals/nachec.py`
- `legajos/signals.py`
- `legajos/signals_alertas.py`
- `legajos/signals_historial.py`
- `legajos/signals_programas.py`
- `legajos/signals_nachec.py`
- `legajos/tests/test_signals_package.py`

**Descripción:** Se agrupó la capa de señales de `legajos` dentro de `legajos/signals/`, se dejó `AppConfig.ready()` apuntando al paquete nuevo y se conservaron wrappers compatibles en los módulos legacy secundarios. El slice no cambia reglas de negocio; solo ordena el wiring de side effects y fija exports básicos con smoke tests.

---

## 2026-03-13 — Refactor DX Slice 50: packaging de apps chicas restantes

**Archivos modificados:**
- `dashboard/views.py`
- `dashboard/views/__init__.py`
- `dashboard/views/home.py`
- `dashboard/signals.py`
- `dashboard/signals/__init__.py`
- `dashboard/urls.py`
- `dashboard/tests/__init__.py`
- `dashboard/tests/test_package_exports.py`
- `tramites/views.py`
- `tramites/views/__init__.py`
- `tramites/views/backoffice.py`
- `tramites/urls.py`
- `tramites/tests/__init__.py`
- `tramites/tests/test_package_exports.py`
- `healthcheck/views.py`
- `healthcheck/views/__init__.py`
- `healthcheck/views/basic.py`
- `healthcheck/tests/__init__.py`
- `healthcheck/tests/test_package_exports.py`
- `legajos/signals.py`

**Descripción:** Se alinearon `dashboard`, `tramites` y `healthcheck` al mismo patrón de packaging por responsabilidad, moviendo sus views a paquetes reales y dejando `dashboard/signals/` como paquete explícito aunque todavía no registre hooks propios. En el mismo corte se eliminó el viejo `legajos/signals.py`, ya reemplazado por el paquete real del slice anterior.

---

## 2026-03-13 — Refactor DX Slice 51: packaging de auditoría/performance en `core`

**Archivos modificados:**
- `core/views/__init__.py`
- `core/views/auditoria.py`
- `core/views/performance.py`
- `core/views_auditoria.py`
- `core/performance_dashboard.py`
- `core/signals/__init__.py`
- `core/signals/auditoria.py`
- `core/signals/auditoria_historial.py`
- `core/signals/cache.py`
- `core/signals_auditoria.py`
- `core/signals_auditoria_historial.py`
- `core/signals_cache.py`
- `core/apps.py`
- `core/urls.py`
- `core/urls_auditoria.py`
- `core/tests/test_package_exports.py`

**Descripción:** Se cerró la parte pendiente de `core` moviendo auditoría y performance al paquete real de views y agrupando las señales de auditoría/cache dentro de `core/signals/`. Se mantuvieron wrappers compatibles para los módulos históricos y `CoreConfig.ready()` quedó con imports explícitos del paquete nuevo.

---

## 2026-03-13 — Refactor DX Slice 52: packaging de `api_views` en apps chicas

**Archivos modificados:**
- `dashboard/api_views.py`
- `dashboard/api_views/__init__.py`
- `dashboard/tests/test_package_exports.py`
- `users/api_views.py`
- `users/api_views/__init__.py`
- `users/tests/test_package_exports.py`
- `chatbot/api_views.py`
- `chatbot/api_views/__init__.py`
- `chatbot/tests/test_package_exports.py`

**Descripción:** Se movió la capa de `api_views` de `dashboard`, `users` y `chatbot` a paquetes reales, manteniendo intactos sus imports desde `urls.py` y `api_urls.py`. También se ampliaron los smoke tests de exports para fijar que esos viewsets y endpoints ya viven en el paquete nuevo.

---

## 2026-03-13 — Refactor DX Slice 53: packaging de `api_views` en apps compartidas

**Archivos modificados:**
- `core/api_views.py`
- `core/api_views/__init__.py`
- `core/tests/test_package_exports.py`
- `conversaciones/api_views.py`
- `conversaciones/api_views/__init__.py`
- `conversaciones/api_extra.py`
- `conversaciones/api_views/extra.py`
- `conversaciones/api_urls.py`
- `conversaciones/tests/test_package_exports.py`

**Descripción:** Se movieron las APIs compartidas de `core` y `conversaciones` al mismo patrón de paquetes reales, manteniendo intactos los imports desde `api_urls.py`. También se ampliaron los smoke tests para cubrir exports del paquete nuevo.

---

## 2026-03-13 — Refactor DX Slice 54: packaging de `api_views` en `legajos`

**Archivos modificados:**
- `legajos/api_views.py`
- `legajos/api_views/__init__.py`
- `legajos/api_views_contactos.py`
- `legajos/api_views/contactos.py`
- `legajos/api_urls.py`
- `legajos/api_urls_contactos.py`
- `legajos/tests/test_package_exports.py`

**Descripción:** Se cerró también la capa de `api_views` en `legajos`, moviendo tanto la API principal como la de contactos al paquete real `legajos/api_views/`. El routing de DRF se mantuvo estable desde `api_urls.py` y `api_urls_contactos.py`, y se amplió el smoke test del paquete.

---

## 2026-03-14 — Refactor DX Slice 55: service layer inicial para operación `ÑACHEC`

**Archivos modificados:**
- `legajos/services/nachec.py`
- `legajos/services/__init__.py`
- `legajos/views/nachec_operacion.py`
- `legajos/tests/test_nachec_operacion_services.py`

**Descripción:** Se extrajo a service layer el subflujo inicial de `ÑACHEC` en `nachec_operacion`: completar validación, completar tarea, construir contexto de envío a asignación, enviar a asignación y asignar territorial. En el mismo corte se corrigió una inconsistencia real: la tarea de asignación se creaba como `OTRO`, pero la reasignación/completado buscaba un tipo inexistente; ahora la coordinación vuelve a encontrar y completar la tarea correcta por criterio consistente.

---

## 2026-03-16 — Refactor DX Slice 56: service layer para reasignación e inicio de relevamiento `ÑACHEC`

**Archivos modificados:**
- `legajos/services/nachec.py`
- `legajos/views/nachec_operacion.py`
- `legajos/tests/test_nachec_operacion_services.py`

**Descripción:** Se siguió adelgazando `legajos/views/nachec_operacion.py` moviendo a `ServicioOperacionNachec` la reasignación de territorial, la construcción de contexto para reasignación e inicio de relevamiento, y la transición transaccional `ASIGNADO -> EN_RELEVAMIENTO` con su actualización de tarea e historial. También se agregaron tests de service para fijar ese contrato operativo y se redujo la duplicación de cálculo de carga territorial/SLA en la view.

---

## 2026-03-16 — Refactor DX Slice 57: packaging final de `forms` y `services` residuales

**Archivos modificados:**
- `users/forms/__init__.py`
- `turnos/forms/__init__.py`
- `core/services/auditoria.py`
- `core/services/__init__.py`
- `core/management/commands/verificar_auditoria.py`
- `users/tests/test_package_exports.py`
- `turnos/tests/test_package_exports.py`
- `core/tests/test_package_exports.py`

**Archivos eliminados:**
- `users/forms.py`
- `turnos/forms.py`
- `core/services_auditoria.py`

**Descripción:** Se absorbieron dentro de carpetas reales las excepciones estructurales más relevantes que todavía quedaban fuera del patrón principal: `users/forms.py`, `turnos/forms.py` y `core/services_auditoria.py`. Desde este punto, la organización física del proyecto queda casi completamente alineada a carpetas por responsabilidad, y lo que persiste en raíz es principalmente fachada de compatibilidad o apps mínimas.

---

## 2026-03-17 — Refactor DX Slice 58: retiro de compatibilidad legacy en `legajos`

**Archivos modificados:**
- `legajos/urls.py`
- `legajos/urls_nachec.py`
- `legajos/views/__init__.py`
- `legajos/views/ciudadanos.py`
- `legajos/views/clinico.py`
- `legajos/views/derivacion.py`
- `legajos/views/institucional.py`
- `legajos/tests/test_ciudadanos_admision.py`
- `legajos/tests/test_clinico_package.py`
- `legajos/tests/test_derivacion_programa_package.py`
- `legajos/tests/test_institucional_package.py`
- `legajos/tests/test_legajo_workflow.py`
- `legajos/tests/test_nachec_package.py`
- `legajos/tests/test_operativa_package.py`
- `legajos/tests/test_package_exports.py`
- `legajos/tests/test_programas_package.py`
- `legajos/tests/test_solapas_package.py`
- `legajos/tests/test_support_views_package.py`

**Archivos eliminados:**
- `legajos/forms.py`
- `legajos/forms_ciudadanos.py`
- `legajos/forms_clinico.py`
- `legajos/forms_contactos.py`
- `legajos/forms_derivacion.py`
- `legajos/forms_institucional.py`
- `legajos/forms_operativa.py`
- `legajos/selectors_ciudadanos.py`
- `legajos/selectors_contactos.py`
- `legajos/selectors_legajos.py`
- `legajos/services_admision.py`
- `legajos/services_alertas.py`
- `legajos/services_ciudadanos.py`
- `legajos/services_contactos.py`
- `legajos/services_derivaciones_programa.py`
- `legajos/services_filtros_usuario.py`
- `legajos/services_institucional.py`
- `legajos/services_legajos.py`
- `legajos/services_nachec.py`
- `legajos/services_solapas.py`
- `legajos/signals_alertas.py`
- `legajos/signals_historial.py`
- `legajos/signals_nachec.py`
- `legajos/signals_programas.py`
- `legajos/views.py`
- `legajos/views_acompanamiento.py`
- `legajos/views_alertas.py`
- `legajos/views_api_derivaciones.py`
- `legajos/views_ciudadanos.py`
- `legajos/views_clinico.py`
- `legajos/views_contactos_api.py`
- `legajos/views_contactos_panel.py`
- `legajos/views_cursos.py`
- `legajos/views_dashboard_contactos.py`
- `legajos/views_dashboard_simple.py`
- `legajos/views_derivacion.py`
- `legajos/views_derivacion_programa.py`
- `legajos/views_historial_contactos.py`
- `legajos/views_institucional.py`
- `legajos/views_nachec.py`
- `legajos/views_nachec_cierre.py`
- `legajos/views_nachec_dashboard.py`
- `legajos/views_nachec_decisiones.py`
- `legajos/views_nachec_operacion.py`
- `legajos/views_nachec_prestaciones.py`
- `legajos/views_operativa.py`
- `legajos/views_programas.py`
- `legajos/views_red_contactos.py`
- `legajos/views_simple_contactos.py`
- `legajos/views_solapas.py`

**Descripción:** Se retiró la capa legacy de compatibilidad de `legajos`, dejando la app consumiendo solo los paquetes reales `legajos/views/`, `legajos/forms/`, `legajos/services/`, `legajos/selectors/` y `legajos/signals/`. También se actualizaron imports y tests para apuntar al layout definitivo, con lo que `legajos` deja de mantener dos cartografías internas en paralelo.
