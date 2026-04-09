
# Decisiones Técnicas

> Registro corto de decisiones arquitectónicas relevantes.

## 2026-03-09 — Programas tienen flujo obligatorio

**Decisión:** Todo programa social tiene un flujo configurable. Sin flujo configurado el programa queda en estado BORRADOR y no puede activarse.

**Motivo:** Unificar el comportamiento de todos los programas bajo un motor de flujos común. Eliminar lógica ad-hoc por tipo de programa.

---

## 2026-03-09 — Jerarquía organizacional fija en dos niveles

**Decisión:** Secretaría → Subsecretaría (exactamente dos niveles). No se puede agregar más niveles.

**Motivo:** Refleja la estructura real del organismo. Evitar complejidad de árbol genérico innecesario.

---

## 2026-03-09 — Naturaleza de programa: un solo acto vs persistente

**Decisión:** Los programas tienen dos naturalezas. "Un solo acto": el caso cierra automáticamente al completar el flujo. "Persistente": el caso permanece abierto hasta baja manual explícita.

**Motivo:** Distintos programas sociales tienen ciclos de vida distintos que no deben forzarse al mismo comportamiento.

---

## 2026-03-09 — Roles como grupos Django independientes sin jerarquía

**Decisión:** Todos los roles son grupos Django. No existe jerarquía entre roles — un usuario puede tener múltiples roles simultáneamente. El administrador (`is_staff`) asigna y revoca roles.

**Motivo:** Flexibilidad operativa. Un operador puede tener simultáneamente `turnoOperar` y `ciudadanoVer` sin que un rol implique al otro.

---

## 2026-03-09 — Motor de flujos basado en sistema NODO

**Decisión:** El motor de flujos del backend se adapta del sistema NODO (Django). El editor visual usa React solo para ese componente, el resto del sistema sigue con Alpine.js.

**Motivo:** El sistema NODO ya tiene un motor de flujos probado en producción. React solo para el editor drag & drop porque Alpine.js no escala para ese caso de uso.

---

## 2026-03-09 — Tareas territoriales como nodo del flujo

**Decisión:** Las tareas territoriales (formularios completados por operadores de campo en app móvil) son un tipo de nodo dentro del flujo de un programa, no una entidad de configuración separada.

**Motivo:** Unifica la lógica de flujos. Evita una entidad paralela que duplique el concepto de "paso del flujo".

---

## 2026-03-11 — Actividades siempre pertenecen a una institución

**Decisión:** Una actividad (`PlanFortalecimiento`) siempre requiere una institución. No existen actividades flotantes sin institución asociada.

**Motivo:** Las actividades son la operativa institucional — representan lo que una institución hace. Sin institución, no hay contexto organizacional para la actividad.

---

## 2026-03-11 — Actividades tienen dos tipos de acceso: libre y por programa

**Decisión:** Una actividad puede ser de acceso **libre** (cualquier ciudadano puede inscribirse directamente) o **requiere programa** (el ciudadano debe estar inscripto en un programa específico primero).

**Campo a agregar:** `tipo_acceso = LIBRE | REQUIERE_PROGRAMA` en `PlanFortalecimiento`. Si es `REQUIERE_PROGRAMA`, FK opcional al `Programa` correspondiente.

**Motivo:** Refleja la realidad operativa: algunas actividades son abiertas a la comunidad, otras son parte del flujo de atención de un programa específico.

---

## 2026-03-11 — Unificación del modelo de Derivación

**Decisión:** Los dos modelos de derivación existentes (`Derivacion` legacy desde `LegajoAtencion`, y `DerivacionInstitucional` desde `Ciudadano`) deben unificarse en un único modelo de derivación.

**Motivo:** Dos modelos paralelos para el mismo concepto generan confusión operativa y duplicación de lógica. Cuando el motor de flujos reemplace `LegajoAtencion`, la `Derivacion` legacy quedaría huérfana de todas formas.

**Plan:** La unificación es parte del diseño del motor de flujos (US-006). El modelo unificado sale desde `Ciudadano`, no desde un legajo específico. La `Derivacion` legacy se depreca cuando `LegajoAtencion` migre al motor de flujos.


## 2026-03-13 — Refactor DX incremental por slices

- Contexto: el repo real `SistemSo` no coincide con el contexto viejo de `AkunCalcu` y además concentra deuda en views/forms/urls monolíticos.
- Decisión: aplicar modernización interna por slices, empezando por `users`, `portal` institucional y `turnos`.
- Regla derivada: en apps existentes se prefieren módulos por dominio (`views_public.py`, `services_turnos.py`, `selectors_usuarios.py`) antes que convertir masivamente `views.py/forms.py/urls.py` en paquetes.
- Consecuencia: el patrón queda validado en un área acotada antes de entrar en `configuracion`, `legajos` y `conversaciones`.

## 2026-03-13 — `configuracion` primero por workflows institucionales

- Contexto: `configuracion` concentra deuda real en las pantallas operativas de instituciones y actividades, no en el CRUD geográfico.
- Decisión: el slice 2 se aplicó solo sobre detalle institucional, actividad, staff, derivaciones e inscriptos, con selectors + services + forms explícitos.
- Regla derivada: cuando una app mezcla tablas maestras simples y workflows complejos, el refactor debe empezar por los workflows que concentran side effects y queries repetidas.
- Consecuencia: se reduce riesgo de regresión y queda una base reusable antes de entrar en `legajos`.

## 2026-03-13 — `legajos` empieza por ciudadanos y admisión

- Contexto: `legajos` mezcla varios dominios y no era realista refactorizarlo completo en un solo corte.
- Decisión: el slice 3 se enfocó en la entrada principal del módulo: listado/detalle de ciudadano, consulta RENAPER y wizard de admisión.
- Regla derivada: en módulos monolíticos, atacar primero el flujo de entrada con más visibilidad y reutilización antes de tocar submódulos laterales.
- Consecuencia: el manejo de sesión y las queries repetidas ya no viven pegadas a las views del flujo base.

## 2026-03-13 — `legajos` clínico conserva compatibilidad con actividades dinámicas

- Contexto: el flujo clínico base tenía lógica de evaluación/planes/seguimientos/derivaciones inline en views y el formulario de plan no representaba correctamente los datos existentes al editar.
- Decisión: el slice 4 movió orquestación a `services_legajos.py`, lecturas a `selectors_legajos.py` y mantuvo compatibilidad con actividades dinámicas adicionales del plan parseando los slots enviados por `POST`.
- Regla derivada: cuando un form legacy convive con inputs dinámicos fuera del schema declarado, el refactor debe preservar ese contrato antes de endurecer validaciones.
- Consecuencia: se corrige una inconsistencia funcional real en edición de planes sin introducir un corte abrupto del flujo histórico.

## 2026-03-13 — los templates deben reflejar el modelo real

- Contexto: varias pantallas de `legajos` venían renderizando campos inexistentes o nombres legacy que ya no pertenecen al schema actual.
- Decisión: el slice 5 corrigió esos templates y movió los hotspots de eventos/reportes/responsable a selectors y services para que el frontend dependa de contratos reales del dominio.
- Regla derivada: cuando un template y un modelo divergen, la prioridad es realinear el template al modelo antes de agregar más lógica de presentación.
- Consecuencia: se reduce deuda silenciosa y baja el riesgo de romper pantallas por atributos fantasma.

## 2026-03-13 — modularizar `views.py` sin romper compatibilidad

- Contexto: `legajos/views.py` seguía siendo el archivo más monolítico del proyecto aun después de extraer services y selectors.
- Decisión: el slice 6 separó ciudadanía/admisión y clínica en `views_ciudadanos.py` y `views_clinico.py`, dejando `views.py` como fachada compatible.
- Regla derivada: cuando la deuda es física/organizacional, primero conviene introducir fachadas compatibles antes de forzar cambios de imports/URLs en cascada.
- Consecuencia: se reduce el tamaño cognitivo del módulo y queda allanado el próximo paso de separar institucional/programas/actividades.

## 2026-03-13 — completar la fachada de `legajos/views.py`

- Contexto: después del slice 6, `legajos/views.py` todavía mezclaba fachada e implementación real del bloque institucional/operativo.
- Decisión: el slice 7 movió ese bloque a `views_operativa.py` y dejó `views.py` como un punto de reexportación sin lógica propia.
- Regla derivada: si una fachada temporal todavía conserva implementación, el siguiente corte debe convertirla en fachada real antes de abrir más submódulos.
- Consecuencia: el contrato de imports se mantiene estable, pero la app ya puede seguir modularizándose por dominios con menos fricción.

## 2026-03-13 — modularizar `conversaciones` preservando endpoints legacy

- Contexto: `conversaciones/views.py` mezclaba chat público, backoffice, métricas y lógica de cola con parsing manual de JSON y queries repetidas.
- Decisión: el slice 8 extrajo selectors, services y forms livianos, separó `views_public.py` y `views_backoffice.py` y dejó `views.py` como fachada compatible.
- Regla derivada: en módulos con transporte AJAX/WebSocket legacy, primero conviene separar responsabilidades y validar payloads sin cambiar rutas ni el contrato del frontend.
- Consecuencia: el módulo ya puede seguir evolucionando con menor riesgo y la deuda específica de CSRF/polling queda aislada para un corte posterior.

## 2026-03-13 — alinear la API auxiliar del chat con la misma capa de dominio

- Contexto: aun con `views.py` modularizado, `api_views.py` y `api_extra.py` seguían resolviendo permisos, previews y marcado de leídos con queries inline.
- Decisión: el slice 9 reusó selectors y services del módulo para alertas, detalle en vivo y marcado de mensajes leídos.
- Regla derivada: cuando una app expone HTML y APIs sobre el mismo dominio, ambas superficies deben consumir la misma capa de lectura/orquestación.
- Consecuencia: baja la duplicación interna y se reduce el riesgo de divergencia entre la UI principal y sus APIs auxiliares.

## 2026-03-13 — `configuracion` adopta fachada compatible de views por dominio

- Contexto: `configuracion` seguía con un `views.py` de más de 500 líneas aun después del slice 2.
- Decisión: el slice 10 separó geografía, institucional y actividades en módulos propios y dejó `views.py` como fachada compatible.
- Regla derivada: cuando una app ya tiene services/selectors pero conserva una view monolítica, el siguiente paso de DX es modularización física, no más abstracción lógica.
- Consecuencia: se reduce el costo de navegación del módulo y se homogeniza el patrón con `legajos` y `conversaciones`.

## 2026-03-13 — introducir namespaces sin romper el código legado

- Contexto: `users`, `core` y `healthcheck` seguían sin `app_name` y eso hacía menos predecible el espacio de rutas del proyecto.
- Decisión: el slice 11 agregó `app_name` y expuso includes namespaced en paralelo a los legacy.
- Regla derivada: cuando un rename global de URLs es riesgoso, primero conviene habilitar compatibilidad dual y migrar el consumo de forma incremental.
- Consecuencia: ya se pueden usar namespaces consistentes en código nuevo sin obligar a una migración agresiva del código existente.

## 2026-03-13 — migrar primero consumidores de names no ambiguos

- Contexto: una vez habilitados los namespaces, todavía había mucho consumo legacy en templates.
- Decisión: el slice 12 migró primero `core:*` y `users:*` en pantallas donde el name no colisiona con `django.contrib.auth.urls`.
- Regla derivada: en migraciones de URLs, empezar por consumidores no ambiguos y dejar autenticación para un corte específico.
- Consecuencia: avanza la estandarización real sin introducir una regresión oculta en login/logout.

## 2026-03-13 — dividir `chatbot` por superficie funcional

- Contexto: `chatbot/views.py` seguía mezclando chat del usuario, panel admin y parsing manual de payloads.
- Decisión: el slice 13 separó vistas públicas y administrativas y movió lectura/orquestación a selectors/services con forms livianos para JSON.
- Regla derivada: cuando una app combina superficie de usuario y de administración, separar primero por superficie antes de rediseñar endpoints.
- Consecuencia: la app queda consistente con el patrón del refactor DX y con mejor base para hardening posterior.

## 2026-03-13 — endurecer `chatbot` después de alinear contrato real con frontend

- Contexto: tras la modularización apareció una inconsistencia funcional entre `chat.js` y `chatbot/urls.py`/`views_public.py`.
- Decisión: el slice 14 corrigió primero el contrato real de rutas y respuesta JSON y, sobre esa base, quitó `@csrf_exempt` en los endpoints principales del módulo.
- Regla derivada: no endurecer seguridad sobre una integración rota; primero alinear contrato, después activar la protección.
- Consecuencia: `chatbot` queda funcionalmente más coherente y con mejor postura de seguridad sin tocar su UX.

## 2026-03-13 — endurecer `conversaciones` solo después de corregir su contrato público

- Contexto: el chat ciudadano usaba rutas hardcodeadas, no enviaba cabecera CSRF y evaluaba contra una URL que en realidad estaba protegida como backoffice.
- Decisión: el slice 15 corrigió primero el contrato real renderizando URLs desde Django y devolviendo la evaluación al dominio público; después retiró `@csrf_exempt` de los POST JSON principales.
- Regla derivada: en integraciones AJAX legacy, primero se corrige el contrato observable por el frontend y recién después se endurecen controles de seguridad.
- Consecuencia: `conversaciones` conserva la UX actual, pero elimina una incoherencia funcional real y mejora su postura CSRF.

## 2026-03-13 — los runtimes en vivo deben ser idempotentes y configurables

- Contexto: `conversaciones_lista_ws.js` se cargaba tanto desde `base.html` como desde `lista.html`, y además seguía dependiendo de URLs hardcodeadas para detalle, cierre y API.
- Decisión: el slice 16 eliminó la carga duplicada local, agregó un guard de inicialización global y movió las URLs operativas al DOM renderizado por Django.
- Regla derivada: si un runtime JS se inyecta globalmente desde `base.html`, debe tolerar inclusiones repetidas y tomar configuración específica de pantalla desde atributos de datos o un objeto global.
- Consecuencia: la lista en vivo de conversaciones queda más estable y más preparada para cambios futuros de rutas/namespaces.

## 2026-03-13 — la configuración de dominio compartido debe salir de archivos estáticos

- Contexto: tras los slices 15 y 16 todavía quedaban scripts globales y consumidores cross-app de `conversaciones` pegados a `/conversaciones/...`, incluso fuera de la app misma.
- Decisión: el slice 17 introdujo `window.conversacionesConfig` en `base.html` y movió a esa configuración los scripts globales de estadísticas/alertas, además de parametrizar el detalle operador y el portal ciudadano.
- Regla derivada: cuando un dominio cruza varias pantallas y apps, la fuente de verdad de sus rutas debe renderizarse desde Django y no replicarse en múltiples archivos estáticos.
- Consecuencia: baja el acoplamiento transversal del módulo y se simplifica la futura migración de namespaces/rutas.

## 2026-03-13 — extraer primero subdominios cerrados de `portal/views_ciudadano.py`

- Contexto: `portal/views_ciudadano.py` seguía siendo un hotspot grande y mezclaba auth, perfil, consultas y turnos.
- Decisión: el slice 18 atacó primero el subdominio de consultas ciudadanas, porque tiene ownership claro, integra con `conversaciones` y podía migrarse a forms/selectors/services sin tocar turnos ni autenticación.
- Regla derivada: cuando una view monolítica mezcla varios subdominios, conviene extraer primero el flujo con fronteras más claras y menor dependencia de UI compleja.
- Consecuencia: el portal ciudadano gana una estructura más testeable y el archivo principal baja de tamaño sin introducir una migración masiva.

## 2026-03-13 — los turnos ciudadanos deben validar con forms aunque el flujo nazca en GET

- Contexto: la confirmación de turnos del portal ciudadano armaba fecha y horarios desde query params y luego persistía con `POST` raw dentro de `portal/views_ciudadano.py`.
- Decisión: el slice 19 extrajo turnos a un módulo propio y usó un form explícito para la confirmación, manteniendo el flujo multi-paso pero validando `fecha`, `hora_inicio`, `hora_fin` y `motivo` con Django Forms.
- Regla derivada: en flujos multi-paso del portal ciudadano, los pasos intermedios pueden hidratarse desde GET, pero el paso que confirma o persiste datos debe cerrarse con un form explícito y un service transaccional.
- Consecuencia: baja el acoplamiento del portal, se elimina parsing manual repetido y la reserva/cancelación de turnos queda reusable y testeable.

## 2026-03-13 — separar `auth/registro` antes de tocar perfil ciudadano

- Contexto: después de extraer consultas y turnos, `portal/views_ciudadano.py` seguía mezclando autenticación, throttling por IP, sesión de registro y creación/vinculación de cuentas.
- Decisión: el slice 20 movió login/logout, registro por pasos y password reset a `views_ciudadano_auth.py` y concentró la orquestación del alta en `services_ciudadano_auth.py`.
- Regla derivada: cuando un módulo ciudadano mezcla subdominios funcionales y auth, conviene extraer primero la autenticación/alta si concentra estado de sesión, efectos de seguridad o creación de cuentas.
- Consecuencia: el archivo principal del portal ciudadano baja fuerte de tamaño y queda mejor preparado para extraer luego perfil/datos sin mezclar preocupaciones.

## 2026-03-13 — cerrar `portal/views_ciudadano.py` como fachada antes de salir del módulo

- Contexto: tras slices 18, 19 y 20, el archivo residual del portal ciudadano todavía concentraba perfil, programas, mis datos y cambio de email/password.
- Decisión: el slice 21 movió ese resto a `views_ciudadano_perfil.py`, apoyado en `selectors_ciudadano_perfil.py` y `services_ciudadano_perfil.py`.
- Regla derivada: si un archivo histórico ya fue partido en varios submódulos, conviene terminar el trabajo y dejarlo como fachada pura antes de saltar a otro hotspot.
- Consecuencia: `portal/views_ciudadano.py` deja de ser un monolito y el dominio ciudadano del portal queda físicamente separado por subdominios claros.

## 2026-03-13 — en `ÑACHEC` modularizar primero bloques grandes de bajo riesgo

- Contexto: `legajos/views_nachec.py` seguía siendo el mayor hotspot del repo con más de 2700 líneas y cobertura automática baja para sus workflows críticos.
- Decisión: el slice 22 atacó primero prestaciones, cierre/reapertura y dashboard, porque son bloques grandes, bien delimitados y con contrato de URLs estable.
- Regla derivada: en monolitos de alto riesgo, empezar por separar físicamente los bloques más aislables antes de mover validaciones y transiciones de estado más delicadas.
- Consecuencia: el archivo principal de `ÑACHEC` baja fuerte de tamaño y queda mejor preparado para continuar con evaluación, relevamiento y asignación.

## 2026-03-13 — en `ÑACHEC` separar evaluación/plan antes de asignación/relevamiento

- Contexto: tras el slice 22, el hotspot restante seguía mezclando dos zonas distintas de riesgo: decisiones profesionales y operación territorial.
- Decisión: el slice 23 aisló primero evaluación, ampliación/rechazo y activación de plan en `views_nachec_decisiones.py`.
- Regla derivada: dentro de workflows largos, conviene separar antes las decisiones de escritorio y recién después las transiciones territoriales que dependen más de permisos, SLA y evidencias.
- Consecuencia: `views_nachec.py` queda por debajo de 1000 líneas y el bloque más sensible restante queda mejor delimitado para el próximo corte.

## 2026-03-13 — cerrar `ÑACHEC` con una fachada pura cuando la modularización física ya terminó

- Contexto: después de separar prestaciones, cierre, dashboard, evaluación y plan, `views_nachec.py` todavía retenía el bloque operativo restante y seguía siendo el punto de implementación real del módulo.
- Decisión: el slice 24 movió validación, asignación, reasignación, relevamiento y evidencias a `views_nachec_operacion.py`, dejando `views_nachec.py` como una fachada pura de compatibilidad.
- Regla derivada: cuando un hotspot histórico ya fue fragmentado por subdominios estables, el archivo original debe terminar como fachada mínima antes de pasar al siguiente hotspot.
- Consecuencia: baja el costo de navegación, se explicita la nueva cartografía del módulo y se preserva compatibilidad con imports y URLs existentes.

## 2026-03-13 — alinear primero los forms con las views ya modularizadas

- Contexto: tras modularizar casi todas las views de `legajos`, el archivo `forms.py` seguía mezclando ciudadanía, clínica y operativa en más de 500 líneas.
- Decisión: el slice 25 dividió `legajos/forms.py` en `forms_ciudadanos.py`, `forms_clinico.py` y `forms_operativa.py`, dejando `forms.py` como fachada compatible.
- Regla derivada: cuando el corte por dominio ya existe en views, conviene reflejarlo también en forms antes de abrir otro hotspot de la app.
- Consecuencia: mejora la navegabilidad del módulo y se preserva el contrato público de imports mientras baja el costo de mantenimiento.

## 2026-03-13 — usar CBVs solo donde el CRUD repetible ya está maduro

- Contexto: `turnos` ya tenía services y selectors claros, pero el backoffice seguía concentrando dashboard, configuraciones, disponibilidades, agenda y acciones en un único archivo de views.
- Decisión: el slice 26 separó el backoffice en módulos y llevó a CBVs el CRUD repetible de configuraciones y disponibilidades, manteniendo como FBVs las acciones POST atómicas sobre turnos.
- Regla derivada: en refactors incrementales, las CBVs aportan valor cuando encapsulan formularios/listas/detalles repetibles; no conviene forzarlas en endpoints de acción simples.
- Consecuencia: mejora la coherencia de la app sin introducir abstracciones innecesarias ni cambiar contratos de URL.

## 2026-03-13 — en módulos legacy de APIs, extraer primero lectura y adjuntos repetidos

- Contexto: `legajos/views_simple_contactos.py` mezclaba vistas HTML, múltiples APIs JSON, queries compuestas y validación/upload de adjuntos en un solo archivo grande.
- Decisión: el slice 27 separó panel y API, extrajo la lectura a `selectors_contactos.py` y encapsuló el manejo repetido de archivos en `services_contactos.py`, dejando `views_simple_contactos.py` como fachada.
- Regla derivada: cuando un módulo legacy mezcla APIs heterogéneas con side effects repetidos, conviene aislar primero lectura y archivos antes de revisar permisos o rediseñar el contrato completo.
- Consecuencia: baja el costo cognitivo del módulo y permite corregir inconsistencias con el modelo real desde un solo lugar.

## 2026-03-13 — cerrar hardcodes transversales antes de tocar la capa de URLs

- Contexto: aun con namespaces compatibles disponibles, seguían quedando templates y scripts globales consumiendo `logout`, `chatbot` o `conversaciones` mediante paths hardcodeados o names legacy.
- Decisión: el slice 28 migró esos consumidores a namespaces estables o a configuración renderizada por Django, y amplió los smoke tests de rutas críticas.
- Regla derivada: antes de endurecer o renombrar URLs, conviene barrer los consumidores transversales más visibles y fijar con tests los namespaces que ya deben considerarse públicos.
- Consecuencia: baja el riesgo de la futura etapa de limpieza de URLs y se reducen los puntos de rotura silenciosa ante cambios de routing.

## 2026-03-13 — desambiguar names duplicados antes de reordenar URLs legacy

- Contexto: `legajos/urls.py` todavía retenía un conflicto nominal concreto: dos rutas distintas compartían el name `cerrar_alerta`.
- Decisión: el slice 29 renombró esos endpoints a `cerrar_alerta_evento` y `cerrar_alerta_ciudadano`, actualizando el único consumidor explícito y agregando smoke tests.
- Regla derivada: cuando una app mantiene URLs legacy extensas, el primer saneamiento debe ser eliminar `name=` duplicados antes de intentar reorganizaciones más ambiciosas.
- Consecuencia: el routing queda más predecible y se reduce el riesgo de `reverse()` ambiguos en etapas posteriores.

## 2026-03-13 — los services de UI deben publicar solo rutas namespaced

- Contexto: `users/services.py` todavía emitía reverses legacy y un `url_name` inconsistente para la tabla/listado de usuarios.
- Decisión: el slice 30 migró ese contrato interno a `users:*` y corrigió la acción de eliminación a `users:usuario_eliminar`.
- Regla derivada: cuando un service arma configuración consumida por componentes de UI, debe exponer nombres de ruta canónicos y no aliases legacy.
- Consecuencia: se reduce el acoplamiento oculto entre routing y componentes genéricos de tabla del backoffice.

## 2026-03-13 — migrar a paquetes reales solo por apps y con fachadas compatibles

- Contexto: después de modularizar muchos monolitos, varias apps seguían teniendo archivos raíz como `views.py` o `services.py`, pero mover todo el repo a paquetes reales en una sola pasada implicaba demasiado riesgo de imports rotos y side effects no cubiertos.
- Decisión: el slice 31 inició la migración de packaging real solo en `turnos` y `users`, creando `views/`, `services/`, `selectors/` y `signals/` donde correspondía y dejando wrappers compatibles en los módulos legacy.
- Regla derivada: las migraciones físicas de packaging deben hacerse app por app, con tests de exports públicos, antes de retirar los entrypoints históricos.
- Consecuencia: el proyecto gana estructura más consistente sin obligar a un big bang de imports en todo el árbol.

## 2026-03-13 — preservar exports implícitos al empaquetar apps con tests legacy

- Contexto: en `chatbot`, los tests existentes parcheaban `EnhancedChatbotService` desde `chatbot.services_chatbot`, aunque el verdadero contrato funcional del módulo eran sus funciones helper.
- Decisión: el slice 32 mantuvo ese export en el wrapper legacy al mover la implementación real a `chatbot/services/chat.py`.
- Regla derivada: antes de reemplazar un módulo histórico por un wrapper, hay que conservar también los símbolos usados por tests, monkeypatches o integraciones internas, no solo las funciones “principales”.
- Consecuencia: baja el riesgo de roturas sutiles durante la migración a paquetes y se respeta mejor el contrato efectivo del código existente.

## 2026-03-13 — cuando una app ya está modularizada por dominio, empaquetarla sin rediseñarla

- Contexto: `configuracion` ya había separado geografía, institucional y actividades en módulos distintos, pero todavía convivía con entrypoints raíz y sin paquetes reales por responsabilidad.
- Decisión: el slice 33 convirtió esa cartografía existente en paquetes reales de `views`, `forms`, `services` y `selectors`, sin mezclar el corte de packaging con un nuevo rediseño funcional.
- Regla derivada: si una app ya tiene un corte por dominio suficientemente claro, el packaging debe limitarse a reflejar esa estructura física y dejar wrappers mínimos en los módulos históricos.
- Consecuencia: se baja riesgo, se gana orden interno y se evita introducir dos tipos de cambio a la vez.

## 2026-03-13 — al empaquetar una app, los tests deben migrar a los paths reales

- Contexto: en `portal`, varios tests parcheaban helpers internos sobre módulos legacy (`services_*.py`) que pasaron a ser wrappers durante el packaging.
- Decisión: el slice 34 actualizó esos tests para parchear los módulos reales bajo `portal.services.*`, en vez de seguir confiando en wrappers históricos.
- Regla derivada: cuando una migración física convierte módulos legacy en fachadas, los tests que hacen monkeypatch de internals deben moverse al path real del paquete y no seguir fijando paths transitorios.
- Consecuencia: se evita una falsa sensación de compatibilidad y se mantiene la testabilidad del dominio sobre su cartografía nueva.

## 2026-03-13 — no migrar packaging de señales sin corregir antes `ready()`

- Contexto: `conversaciones` tenía dos definiciones de `ready()` en su `AppConfig`, por lo que solo se registraba la segunda familia de señales.
- Decisión: el slice 35 unificó el registro en un único `ready()` antes de cerrar el packaging de `signals`.
- Regla derivada: si una app registra señales desde `AppConfig`, la migración a paquetes debe empezar verificando que `ready()` no tenga inconsistencias estructurales que oculten parte del wiring.
- Consecuencia: se evita “preservar” accidentalmente un bug de inicialización al reordenar archivos.

## 2026-03-13 — en la app base `core`, empaquetar solo la superficie de bajo riesgo primero

- Contexto: `core` comparte piezas de bajo acoplamiento como geografía y vistas generales, pero también concentra auditoría, middleware y signals sensibles.
- Decisión: el slice 36 empaquetó solo `views`, `forms` y `selectors` del flujo principal, dejando fuera la parte de auditoría/signals.
- Regla derivada: en apps transversales y de infraestructura, conviene aislar primero el packaging de la superficie estable antes de tocar wiring sensible o código de observabilidad.
- Consecuencia: mejora la consistencia estructural sin comprometer la trazabilidad y auditoría del sistema.

## 2026-03-13 — en `legajos`, empaquetar primero la capa reusable antes del wiring sensible

- Contexto: `legajos` es la app más grande del proyecto y todavía conserva `views` y `signals` con mucho acoplamiento de dominio, pero ya tenía una capa reusable estabilizada de ciudadanía, admisión, contactos, legajos y solapas.
- Decisión: el slice 37 creó paquetes reales de `services` y `selectors` para esa capa, manteniendo wrappers legacy y sin tocar todavía `views` ni `signals`.
- Regla derivada: en apps grandes con mucho wiring implícito, conviene empaquetar primero la capa reusable ya estabilizada antes de mover la superficie operativa más sensible.
- Consecuencia: baja la deuda estructural y mejora la navegabilidad sin introducir todavía riesgo alto en el runtime del dominio.

## 2026-03-13 — en `legajos`, cerrar primero el packaging de forms antes de pasar a views o signals

- Contexto: `legajos` ya había separado `forms_ciudadanos.py`, `forms_clinico.py`, `forms_operativa.py` y otros submódulos, pero seguía exponiéndolos solo como archivos planos legacy.
- Decisión: el slice 38 creó `legajos/forms/` como paquete real y dejó wrappers mínimos en los módulos históricos de forms.
- Regla derivada: si la capa de formularios ya está partida por dominio y no tiene side effects de runtime, conviene empaquetarla antes de seguir con superficies más riesgosas como views o signals.
- Consecuencia: la cartografía de la app gana consistencia y se reduce otro bloque de deuda estructural sin cambiar comportamiento funcional.

## 2026-03-13 — en `legajos`, mover views auxiliares antes que las views sensibles

- Contexto: después de empaquetar `services`, `selectors` y `forms`, la siguiente deuda natural estaba en `views`, pero la app todavía conserva bloques muy sensibles en clínica, institucional y `ÑACHEC`.
- Decisión: el slice 39 empezó la migración de views por el bloque de contactos y dashboards simples, que ya estaba separado en módulos pequeños y con menor riesgo operativo.
- Regla derivada: cuando una app grande entra en la etapa de packaging de views, conviene empezar por subdominios auxiliares con poco wiring implícito antes de tocar superficies críticas del negocio.
- Consecuencia: el proyecto gana consistencia estructural y tests de export sin abrir todavía un frente de regresión alto en las rutas principales de `legajos`.

## 2026-03-13 — en `legajos`, extender el packaging de views por bloques de soporte antes de entrar en dominio pesado

- Contexto: después del bloque de contactos, todavía quedaban en archivos planos varias views pequeñas pero estables de soporte, como alertas, cursos, derivación simple y acompañamiento.
- Decisión: el slice 40 movió esas views a `legajos/views/` y dejó intactos los bloques más delicados de programas, operativa, institucional, clínica y `ÑACHEC`.
- Regla derivada: cuando ya existe un paquete de views parcial en una app grande, conviene ampliarlo primero con bloques chicos y estables antes de tocar módulos largos con reglas de negocio más densas.
- Consecuencia: el packaging avanza con riesgo controlado y deja más explícito cuál es la superficie verdaderamente sensible que queda pendiente.

## 2026-03-13 — en `legajos`, detener la migración física cuando ya solo quedan views de dominio pesado

- Contexto: después de mover contactos, dashboards simples, alertas, cursos, derivación simple, acompañamiento y operativa, lo que sigue en `legajos` son módulos como `programas`, `institucional`, clínica y `ÑACHEC`, con reglas más densas y más side effects.
- Decisión: el slice 41 deja documentado que, a partir de este punto, la estrategia de packaging barato pierde seguridad y ya no conviene seguir en automático sin mejor validación funcional.
- Regla derivada: en apps grandes, la modularización física puede avanzar en bucle solo mientras el siguiente bloque no concentre demasiada lógica sensible; cuando eso ocurre, conviene frenar y reevaluar.
- Consecuencia: se evita convertir un refactor incremental de DX en una fuente de regresiones sobre el corazón operativo del sistema.

## 2026-03-13 — cerrar `programas` y `solapas` antes de declarar agotada la superficie barata

- Contexto: tras mover contactos, soporte y operativa, todavía quedaban `views_programas.py` y `views_solapas.py` como bloques medianos pero físicamente movibles sin rediseñar reglas internas.
- Decisión: el slice 42 los migró a `legajos/views/` y dejó wrappers compatibles, pero consideró ese corte como el último paso barato antes del dominio más sensible.
- Regla derivada: si un módulo todavía puede moverse físicamente sin reabrir reglas de negocio complejas, conviene cerrarlo antes de declarar agotada la estrategia incremental.
- Consecuencia: se maximiza el avance del packaging sin entrar todavía en el terreno de mayor riesgo.

## 2026-03-13 — antes de mover un borde sensible, extraer su workflow a services

- Contexto: `views_derivacion_programa.py` ya no era un simple candidato a packaging; mezclaba aceptación normal, branch especial de `ÑACHEC`, validación de duplicados, creación de tareas con SLA e historial.
- Decisión: el slice 43 extrajo ese workflow a `services/derivaciones_programa.py` y dejó la view como coordinadora delgada.
- Regla derivada: cuando un módulo pendiente concentra transiciones de estado y side effects reales, conviene extraer primero la lógica a services y recién después considerar un movimiento físico del archivo.
- Consecuencia: se baja riesgo, se gana testabilidad y se prepara una futura modularización sin arrastrar lógica de negocio pegada a la capa HTTP.

## 2026-03-13 — después de extraer un workflow sensible, cerrar enseguida el packaging de la view

- Contexto: tras el slice 43, `views_derivacion_programa.py` ya no concentraba la lógica crítica y quedaba como coordinadora HTTP bastante delgada.
- Decisión: el slice 44 movió esa view a `legajos/views/` inmediatamente, antes de abrir otro frente más complejo.
- Regla derivada: si un slice de service layer deja una view suficientemente delgada, conviene aprovechar el mismo impulso y cerrar enseguida su packaging físico.
- Consecuencia: la arquitectura gana consistencia sin acumular deuda de “views finas pero todavía legacy”.

## 2026-03-13 — mover físicamente una view pesada sigue siendo razonable si ya descansa en capas separadas

- Contexto: `views_institucional.py` seguía siendo grande, pero buena parte de su dominio ya descansaba sobre `services_institucional`, forms y permisos dedicados.
- Decisión: el slice 45 la movió a `legajos/views/` sin rediseñar lógica interna en el mismo cambio.
- Regla derivada: una view grande puede moverse físicamente de forma segura si el riesgo principal está en su comportamiento, no en su cartografía de imports.
- Consecuencia: se sigue reduciendo deuda estructural sin mezclar de golpe packaging y reescritura funcional.

## 2026-03-13 — en clínica, preferir packaging físico antes que reescritura oportunista

- Contexto: `views_clinico.py` seguía siendo grande, pero ya consumía selectors, forms y services del dominio clínico.
- Decisión: el slice 46 la movió al paquete `legajos/views/` sin tocar reglas clínicas ni contratos de templates/URLs.
- Regla derivada: cuando un dominio ya tiene capas separadas, el packaging físico puede hacerse aunque el archivo siga siendo grande; no hace falta mezclarlo con otra reescritura.
- Consecuencia: mejora la coherencia interna del módulo sin abrir una regresión funcional innecesaria.

## 2026-03-13 — en familias ya separadas por archivos, cerrar el packaging en bloque

- Contexto: `ÑACHEC` ya estaba dividido en `views_nachec_cierre.py`, `views_nachec_dashboard.py`, `views_nachec_decisiones.py`, `views_nachec_operacion.py` y `views_nachec_prestaciones.py`, con `views_nachec.py` como fachada.
- Decisión: el slice 47 movió toda esa familia al paquete `legajos/views/` en un solo corte puramente estructural.
- Regla derivada: cuando un subdominio ya está partido por archivos y el cambio no reabre lógica, conviene cerrarlo de una sola vez para evitar arrastrar wrappers mixtos por muchas etapas.
- Consecuencia: se completa antes la cartografía nueva y se reduce la deuda residual de packaging.

## 2026-03-13 — cerrar primero el packaging de `services` antes de entrar en `signals`

- Contexto: tras el slice 47, `legajos` ya tenía `views`, `forms` y parte de `services` empaquetados, pero seguían existiendo servicios planos residuales (`alertas`, `filtros_usuario`, `institucional`, `nachec`) consumidos desde views, consumers y señales.
- Decisión: el slice 48 movió esas familias a `legajos/services/` y dejó wrappers legacy, de modo que la futura migración de señales dependa de una API de paquete estable.
- Regla derivada: cuando queda pendiente empaquetar tanto servicios como señales en una app grande, conviene cerrar primero toda la capa service antes de tocar el wiring de side effects.
- Consecuencia: el siguiente corte sobre `signals` queda más contenido y con menos imports cruzados a módulos legacy.

## 2026-03-13 — al empaquetar señales, hacer explícito el wiring desde `AppConfig`

- Contexto: después del slice 48, `legajos` ya tenía una API de servicios estable, pero la capa de señales seguía repartida entre módulos legacy y side effects disparados por imports planos.
- Decisión: el slice 49 creó `legajos/signals/` como paquete real y actualizó `LegajosConfig.ready()` para importar de forma explícita los submódulos `core`, `alerts`, `historial`, `programas` y `nachec`.
- Regla derivada: en packaging de señales, la compatibilidad de wrappers no alcanza; el registro efectivo debe quedar visible y explícito en `AppConfig.ready()`.
- Consecuencia: se reduce ambigüedad en el wiring y el siguiente trabajo deja de ser estructural para pasar a deuda funcional o de contrato.

## 2026-03-13 — cerrar las excepciones pequeñas después de las apps grandes

- Contexto: tras los slices 48 y 49, la mayor parte del proyecto ya seguía la convención de paquetes, pero `dashboard`, `tramites` y `healthcheck` seguían como excepciones pequeñas con `views.py` planos.
- Decisión: el slice 50 alineó esas apps chicas al mismo patrón y dejó `dashboard/signals/` explícito aunque hoy no registre señales activas.
- Regla derivada: cuando el proyecto ya consolidó una convención estructural, conviene cerrar también las apps chicas restantes para que la cartografía no quede llena de excepciones.
- Consecuencia: el siguiente trabajo deja de ser packaging repo-wide y pasa a centrarse en hotspots funcionales, deuda de contrato o cleanup puntual.

## 2026-03-13 — en `core`, cerrar auditoría y señales como último frente estructural

- Contexto: tras los slices 36, 50 y el avance repo-wide, `core` todavía retenía una excepción relevante: `views_auditoria.py`, `performance_dashboard.py` y varias señales de auditoría/cache seguían fuera de los paquetes reales.
- Decisión: el slice 51 movió esos bloques a `core/views/` y `core/signals/`, manteniendo wrappers legacy y dejando `CoreConfig.ready()` con imports explícitos.
- Regla derivada: en una app transversal, la deuda estructural más sensible conviene atacarla al final, cuando el resto del proyecto ya estabilizó la convención y reduce el riesgo de imports cruzados impredecibles.
- Consecuencia: la deuda estructural repo-wide queda casi totalmente consumida y el siguiente trabajo ya pasa a hotspots funcionales o de contrato.

## 2026-03-13 — después de las views HTML, alinear también `api_views` de bajo riesgo

- Contexto: tras el slice 51, el proyecto ya tenía casi todas sus views HTML empaquetadas, pero algunas apps chicas seguían exponiendo `api_views.py` planos.
- Decisión: el slice 52 movió `api_views` de `dashboard`, `users` y `chatbot` a paquetes reales sin cambiar contratos HTTP ni rutas.
- Regla derivada: si una API es pequeña y sus imports están acotados a `urls.py` o `api_urls.py`, todavía conviene alinearla al patrón repo-wide antes de declarar agotado el refactor estructural.
- Consecuencia: lo que queda pendiente deja de ser packaging barato y pasa a APIs más acopladas o a deuda funcional directa.

## 2026-03-13 — las APIs compartidas también pueden seguir el mismo patrón si el routing queda estable

- Contexto: después del slice 52, seguían fuera del patrón `api_views` de `core` y `conversaciones`, aunque sus routers/imports seguían bastante acotados a `api_urls.py`.
- Decisión: el slice 53 movió esas APIs a paquetes reales y dejó `api_urls.py` importando el mismo símbolo lógico.
- Regla derivada: incluso en apps compartidas, una API puede moverse a paquete si el routing se mantiene estable y el refactor no toca serializers, permisos ni contratos HTTP.
- Consecuencia: la deuda estructural repo-wide queda casi agotada y el siguiente trabajo ya entra en APIs más grandes o deuda funcional.

## 2026-03-13 — cerrar la última API grande solo si sigue siendo cartografía pura

- Contexto: tras el slice 53, el único bloque estructural obvio que seguía fuera de convención era `legajos/api_views*`, pero ya era una API más grande que las anteriores.
- Decisión: el slice 54 la movió al paquete real porque seguía consumida solo por sus routers y no exigió tocar serializers, permisos ni contratos DRF.
- Regla derivada: la última API grande de una app puede cerrarse estructuralmente si el cambio sigue siendo cartografía pura y el routing permanece estable.
- Consecuencia: a partir de este punto, el refactor repo-wide deja de tener slices estructurales baratos y lo que queda es funcional, de contrato o de cleanup fino.

## 2026-03-14 — después del packaging, empezar por subflujos operativos acotados

- Contexto: tras el slice 54, el packaging repo-wide quedó prácticamente agotado y el siguiente hotspot real pasó a ser `legajos/views/nachec_operacion.py`, que todavía retenía mucha lógica de negocio.
- Decisión: el slice 55 atacó primero el subflujo más acotado y reusable (`validación` → `envío a asignación` → `asignación territorial`) y lo movió a `ServicioOperacionNachec`.
- Regla derivada: cuando ya no queda deuda estructural barata, conviene seguir por subflujos operativos con transiciones claras y poco acoplamiento a scoring/adjuntos, para maximizar impacto y mantener riesgo controlado.
- Consecuencia: la view baja bastante de responsabilidad y el siguiente corte ya queda concentrado en relevamiento, scoring y evidencias.

## 2026-03-16 — seguir `ÑACHEC` por operaciones sin scoring ni adjuntos

- Contexto: tras el slice 55, el siguiente bloque todavía relativamente acotado dentro de `nachec_operacion` era `reasignar_territorial` e `iniciar_relevamiento`, mientras `finalizar_relevamiento` y `adjuntar_evidencias` ya cruzan scoring, `ContentType`, archivos y contratos más frágiles.
- Decisión: el slice 56 movió esos dos subflujos a `ServicioOperacionNachec` y dejó para un corte posterior el bloque de cierre/evidencias.
- Regla derivada: en workflows largos de dominio, conviene separar primero transiciones operativas puras y dejar para el final los pasos que combinan persistencia, scoring y adjuntos.
- Consecuencia: la view de operación queda más fina y el riesgo del siguiente corte queda mejor acotado al bloque de relevamiento final.

## 2026-03-16 — cerrar el frente estructural absorbiendo excepciones residuales

- Contexto: tras más de cincuenta slices, el repo ya estaba casi completamente organizado por carpetas, pero seguían destacando tres excepciones visibles y transversales: `users/forms.py`, `turnos/forms.py` y `core/services_auditoria.py`.
- Decisión: el slice 57 movió esos módulos a `users/forms/`, `turnos/forms/` y `core/services/auditoria.py`, actualizando exports y consumidores directos.
- Regla derivada: al final de un refactor estructural largo, conviene cerrar primero las excepciones físicas más evidentes aunque no sean hotspots funcionales, para que la cartografía del proyecto quede coherente de punta a punta.
- Consecuencia: lo que permanece plano en las apps pasa a ser principalmente fachada de compatibilidad o apps mínimas, no deuda estructural de primer orden.

## 2026-04-03 — stack local Docker de un solo comando

- Contexto: el arranque local estaba sobredimensionado con `nginx`, dos procesos de app y bootstrap pesado/no idempotente en cada restart.
- Decisión: el entorno local recomendado pasa a usar `docker compose up` con `app`, `mysql` y `redis`, un solo proceso ASGI y un bootstrap automático mínimo.
- Regla derivada: en desarrollo local, los seeds demo o tareas de mantenimiento pesadas no deben formar parte del camino crítico de startup.
- Consecuencia: el entorno queda más simple de levantar, más estable y más rápido para el uso diario.
