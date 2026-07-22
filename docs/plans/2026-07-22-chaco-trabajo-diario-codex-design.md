# Automatización diaria de trabajo asignado en Chaco

Estado: aprobado

Fecha: 2026-07-22

Project: https://github.com/users/Mkdir-arg/projects/1/views/17

Usuario asignado y autorizador: juanikitro

## Objetivo

Crear una tarea programada de Codex que avance de forma sostenida sobre las tareas
asignadas al usuario en el Project de Chaco, sin perder contexto funcional ni
convertir todo el backlog en un único lote.

La automatización debe:

- reconstruir el contexto desde GitHub y el código en cada ejecución;
- seleccionar y agrupar tareas por una Unidad de entrega coherente;
- explicar el pedido en lenguaje simple antes del detalle técnico;
- reservar el grupo en In progress antes de solicitar autorización;
- comenzar código únicamente después de una autorización manual en Codex;
- ejecutar secuencialmente todas las unidades que el usuario apruebe;
- abrir, validar y revisar un PR por unidad;
- dejar un entorno local con datos reproducibles para la aceptación.

## Fuera de alcance

- Implementar automáticamente todas las tareas Ready en un mismo grupo.
- Seleccionar elementos de Backlog, In review, In QA, Done o Roadmap como trabajo nuevo.
- Aprobar o fusionar PRs.
- Mover tareas a In QA o Done.
- Mover un `[REQUERIMIENTO]` a In QA o Done.
- Utilizar datos de producción sin una autorización separada.
- Mantener varias implementaciones o varios entornos locales activos en paralelo.
- Crear un Issue coordinador adicional.

## Hechos y restricciones actuales

- La vista 17 se llama Mis issues y filtra por assignee:@me; no excluye QA.
- Los estados documentados son Backlog, Ready, In progress, In review, In QA,
  Done, Roadmap y Blocked.
- El repositorio canónico redirige hoy de Mkdir-arg/Chaco a Mkdir-arg/Chaco-Back.
- La rama de integración y rama por defecto es development.
- Los PR contra development ejecutan CI también cuando son draft.
- GitHub no impone required checks ni protección de development; el gate debe ser
  una política explícita de la automatización.
- La autenticación gh actual tiene repo pero necesita read:project y project para
  consultar y modificar Project v2.
- Docker Compose usa puertos fijos, por lo que solo puede quedar un stack de
  aceptación activo a la vez sin introducir overrides adicionales.

## Arquitectura elegida

El estado se distribuye en los Issues existentes. No se agrega una bitácora central.

| Fuente | Responsabilidad |
| --- | --- |
| GitHub Project | Estado operativo de las tareas |
| Comentario canónico | Plan completo, inmutable y versionado |
| Reacciones 👍 y 👎 | Sello operativo vigente de la decisión tomada en Codex |
| Comentarios de evento | Historial inmutable de decisiones, cambios de estado y recuperación |
| Referencias de grupo | Enlaces desde las tareas secundarias al comentario canónico |
| PR draft | Estado real de rama, implementación, validaciones y revisión |
| origin/development | Base técnica y fixed point de revisión |

Cada ejecución standalone reconstruye el estado desde esas fuentes. No presupone
que conserva la conversación ni el worktree de una ejecución anterior. La rama
remota, el PR y GitHub son la continuidad durable; el estado local solo sirve durante
la ejecución actual.

## Programación

- Frecuencia: lunes a viernes.
- Hora: 09:30.
- Zona horaria deseada: America/Buenos_Aires; debe verificarse el horario efectivo
  que muestre la UI antes de habilitar.
- Destino de ejecución: worktree aislado del proyecto local de Chaco.
- Notificaciones: política normal, no silenciada, e historial de todas las
  ejecuciones. Una notificación del sistema operativo en cada éxito no se considera
  garantizada hasta verificar el comportamiento de la app.
- Máximo de propuestas nuevas: un Plan de grupo por ejecución.

Una autorización manual puede activar implementación cualquier día y a cualquier
hora; la frecuencia laboral limita las ejecuciones automáticas, no las respuestas
interactivas.

## Ciclo de cada ejecución

1. Ejecutar el preflight de identidad, permisos, Project, repositorio y exclusión mutua.
2. Actualizar referencias remotas y resolver el repositorio canónico.
3. Reconciliar reservas fallidas, decisiones incompletas y estados parciales.
4. Leer tareas In progress, Blocked, planes, reacciones, eventos, PRs y checks.
5. Si existe una Unidad activa, reconstruir su rama remota y continuarla.
6. Si existe una Cola de unidades autorizadas, drenarla secuencialmente.
7. Si solo existen planes sin autorizar, permitir una propuesta nueva.
8. Si puede seleccionarse trabajo nuevo, formar como máximo un grupo.
9. Si no hay trabajo elegible, emitir un Resumen de espera sin mutaciones.

La existencia de planes todavía no autorizados no bloquea una nueva propuesta.
La existencia de trabajo activo o autorizado sí bloquea la creación de planes nuevos.
No hay un tope diario de unidades aprobadas. Si el runtime disponible termina, la
unidad conserva un checkpoint durable en GitHub y se reanuda en el próximo turno
interactivo o Ciclo programado antes de seleccionar trabajo nuevo.

## Elegibilidad y prioridad

Una tarea nueva solo es elegible cuando cumple simultáneamente:

- Tipo igual a Task.
- Status igual a Ready.
- Exactamente un assignee: juanikitro.
- Iteration igual a la iteración vigente.
- Gates de Ready completos según ESTADOS.md.

Antes de evaluar la allowlist, el preflight debe:

- validar la sesión GitHub y el ID estable de `juanikitro`;
- exigir scopes `repo`, `read:project` y `project`;
- paginar exhaustivamente todos los items del Project, sin depender de la porción
  visible de la vista;
- resolver por nombre los IDs vigentes de campos y opciones requeridos;
- determinar la Iteration vigente por sus fechas o configuración, no por posición;
- abortar sin escrituras ante identidad, scope, campos, opciones o iteración ambiguos.

Un prerrequisito se considera disponible cuando su código está integrado y verificado
en `origin/development`, o cuando forma parte de la misma Unidad de entrega y su orden
interno es explícito. Un prerrequisito en `In QA` puede contarse como integrado solo
después de verificar el commit en `development`, dejando registrado el riesgo de QA.
Si está en Backlog, Ready, In progress, Blocked o In review sin integración, la tarea
dependiente no se reserva como trabajo nuevo.

La tarea ancla se elige en este orden:

1. Prerrequisitos del grafo funcional y técnico.
2. Prioridad Alta, luego Media y luego Baja.
3. Cantidad de trabajo que desbloquea.
4. Antigüedad.

## Regla de agrupación

Una Unidad de entrega contiene una o más tareas y debe producir un único resultado
funcional revisable en un PR coherente.

Se pueden agrupar tareas cuando existe dependencia real, superficie de código
compartida o una validación funcional que naturalmente se entrega junta. Compartir
épica, análisis, módulo, prioridad o iteración no alcanza por sí solo.

No existe un máximo numérico de tareas. El límite es conceptual: el grupo debe poder
explicarse, revisarse, probarse y revertirse como una sola entrega. Codex nunca
agrupa todo el backlog por conveniencia.

## Identidad y formato del plan

El formato es:

    PG-<tarea-ancla>-<AAAAMMDD>-<secuencia>:v<versión>

Ejemplo:

    PG-173-20260723-01:v1

El identificador visible se usa en Codex, comentarios, PR y commits. Para nombres de
rama se usa una variante válida para Git, reemplazando los dos puntos:

    codex/pg-173-20260723-01-v1-<slug>

El comentario canónico incluye metadata HTML invisible con:

- ID y versión;
- tarea ancla y tareas incluidas;
- huella del alcance y criterios;
- identidad GitHub autorizadora por ID estable;
- fecha de creación.
- clave idempotente del intento de reserva.

La metadata no contiene secretos. Los eventos posteriores se escriben como comentarios
breves separados; el comentario canónico no se edita. El `comment_id` se obtiene de la
respuesta de GitHub, se guarda en referencias y eventos posteriores, y también puede
redescubrirse por el Identificador de plan. Nunca se intenta incluir el ID del comentario
dentro del propio comentario antes de crearlo.

## Contenido del Brief operativo

El Plan de grupo comienza con un Resumen funcional del grupo: pocas líneas en
lenguaje llano que expliquen qué pide el conjunto y qué resultado observable tendrá.
Debe entenderse sin abrir Issues ni leer código.

Luego incluye:

1. Identificador y estado.
2. Objetivo y razón del agrupamiento.
3. Tareas incluidas y orden interno.
4. Épica, análisis de origen y `[REQUERIMIENTO]` vinculado, si existe.
5. Evidencia relevante encontrada en el código.
6. Alcance y fuera de alcance.
7. Pasos de implementación.
8. Criterios de aceptación y casos QA.
9. Riesgos, dependencias y posibles bloqueos.
10. Estrategia de validación proporcional.
11. Datos y entorno local necesarios.
12. Rama y PR previstos.
13. Frases exactas para autorizar o rechazar.

La tarea principal recibe el plan completo. Las demás tareas reciben una referencia
breve con el ID y el enlace al comentario canónico.

## Reserva antes de la autorización

La reserva es una operación compensable y se ejecuta bajo la lease exclusiva de la
automatización:

1. Prevalidar que todas las tareas siguen siendo elegibles y resolver de forma
   inequívoca sus `[REQUERIMIENTO]` vinculados, si existen.
2. Publicar el comentario canónico y las referencias.
3. Mover todas las tareas Ready → In progress.
4. Mover cada `[REQUERIMIENTO]` vinculado Backlog → In progress cuando corresponda.
5. Confirmar que todos los movimientos terminaron.
6. Publicar el Evento de reserva completada con sus transiciones y ownership.
7. Presentar el plan en la tarea de Codex.

No se crea un `[REQUERIMIENTO]` faltante. La búsqueda se hace primero por repositorio y
épica: cero Requerimientos para esa épica significa que no existe; más de uno es
ambiguo. Si existe exactamente uno pero no enumera el análisis de la Task, se considera
desactualizado y requiere reconciliación antes de reservar. Ambigüedad, formato inválido
o inconsistencia detienen la reserva antes de escribir. Si ya estaba en `In progress`,
la automatización no reclama ownership de ese movimiento ni podrá revertirlo. Un grupo
que abarque más de un Requerimiento sincroniza cada uno de forma independiente.

Antes de publicar se busca el marcador único del Identificador de plan y la huella del
grupo. Si dos intentos solapados alcanzaran a crear planes para alguna misma tarea, una
relectura posterior elige como única reserva vigente el comentario canónico con menor
`comment_id`; los demás intentos se marcan como duplicados fallidos y compensan sus
movimientos de forma consciente de ownership. Nunca se devuelve un item a `Ready` si
la reserva vencedora válida también lo incluye; cada transición queda ligada a la
clave idempotente de la reserva que la originó. Una colisión de secuencia se resuelve
del mismo modo antes de exponer el plan al usuario.

Si un movimiento falla a mitad:

- intentar devolver a Ready las tareas ya movidas y revertir únicamente los
  Requerimientos cuyo movimiento pertenece a esta reserva;
- marcar la versión como Reserva fallida;
- no considerar válido el grupo parcial;
- detener la ejecución;
- reconciliar cualquier residuo antes de seleccionar más trabajo.

Una reserva pendiente no vence. Cada ejecución revalida tareas, alcance, criterios y
contratos relevantes. Cambios no relacionados no invalidan el plan.

## Autorización, observaciones y rechazo

La decisión se expresa en la misma tarea de Codex que presentó el plan. Esa respuesta
dispara un turno interactivo: Codex valida la frase exacta y persiste el resultado en
GitHub. Un Ciclo programado standalone nunca lee otro chat ni infiere una aprobación;
solo consume una decisión que ya quedó persistida.

| Respuesta | Reacción persistida por Codex | Efecto |
| --- | --- | --- |
| Autorizo PG-...:vN | 👍 | Autoriza esa versión exacta |
| Rechazo PG-...:vN o No autorizo PG-...:vN | 👎 | Rechaza esa versión |
| Pregunta, comentario o pedido de cambio | Ninguna | Mantiene la reserva |

Codex agrega, consulta o elimina la reacción del comentario canónico. Solo cuenta la
reacción creada con la identidad GitHub configurada para `juanikitro` y validada por
su ID estable. Las reacciones de otros usuarios se ignoran.

La decisión válida requiere dos piezas concordantes: el Sello de decisión vigente y
un comentario de Evento de decisión. El evento registra ID y versión del plan,
secuencia monotónica de decisión, clave idempotente, decisión normalizada, frase
exacta recibida, fecha, identificador de la tarea de Codex cuando esté disponible y
`reaction_id`. La reacción es un gate operativo persistido por Codex, no prueba
criptográfica de que el usuario actuó directamente en GitHub. Una reacción manual
aislada, sin evento concordante, no autoriza ni rechaza.

Solo cuenta el Evento de decisión válido con mayor secuencia para esa versión del
plan, y el Sello vigente debe concordar con él. Dos eventos distintos con la misma
secuencia son un conflicto salvo que compartan la misma clave idempotente y contenido.
Un evento histórico concordante con una reacción vieja nunca desplaza al evento más
reciente.

Las reacciones son excluyentes. Para una nueva decisión, Codex crea o redescubre el
nuevo sello, obtiene su `reaction_id`, publica el Evento de decisión concordante y
recién entonces retira el sello anterior, borrando únicamente la reacción de la
identidad autorizadora cuyo ID fue registrado. Si falla antes de completar el evento,
compensa el sello nuevo y conserva el anterior. Si quedan ambas por un fallo, o si
reacción y evento no concuerdan, el estado es conflictivo y no se ejecuta.

Si reacción y evento no pueden persistirse de forma concordante, la decisión no
produce efectos. Codex intenta compensar la pieza parcial, informa el fallo y permite
reintentar. Los eventos conservan el historial; las reacciones solo representan el
estado vigente.

## Versionado e invalidación

El comentario canónico es inmutable. Un cambio material en tareas, alcance, criterios
de aceptación o contratos relevantes:

1. invalida la versión anterior mediante un comentario de evento;
2. conserva sus Eventos de decisión como evidencia histórica y retira o ignora el
   Sello de decisión anterior;
3. crea un comentario canónico nuevo para vN+1;
4. exige otra autorización.

Una reacción de una versión anterior nunca autoriza alcance nuevo.

## Activación y control de concurrencia

Tras persistir 👍 y su Evento de decisión, Codex crea inmediatamente la rama y el PR
draft. Si no existe otra Unidad activa, la implementación comienza en esa misma tarea;
si existe, queda en la Cola de unidades autorizadas.

El turno interactivo aplica la decisión como una sola operación orquestada. Una
autorización persiste decisión, crea o recupera rama y PR, y activa o encola. Un rechazo
antes de código persiste 👎, libera Task/Requerimiento y cierra únicamente un PR vacío;
si ya hay código, pausa sin descartar. Una observación no invoca esta operación.

Solo una unidad puede recibir cambios funcionales a la vez. La cola usa el plan más
antiguo, salvo prioridad explícita del usuario, y se drena sin un límite de política
diario, reanudándose en otro run cuando el runtime actual no alcance.

Toda ruta mutante —reserva, decisión, activación, movimientos, push y PR— adquiere una
lease exclusiva creada atómicamente en el directorio Git común, fuera del worktree
efímero. La lease contiene un token de dueño y se renueva antes de cada fase mutante;
cada comando rechaza un token ajeno o vencido. Solo se configura una tarea programada.
Si otra ejecución conserva la lease, el segundo intento no escribe y termina informando
que la operación quedó para el próximo turno. Una lease huérfana solo se recupera tras
su vencimiento y después de reconciliar GitHub; GitHub sigue siendo la fuente de verdad.

Como defensa adicional ante una carrera o recuperación defectuosa:

- cada tarea publica un evento de activación antes del primer cambio funcional;
- vuelve a leer todos los eventos y PRs activos;
- el evento válido más antiguo, con comment_id como desempate, conserva el turno;
- cualquier otra tarea se detiene antes de editar y queda en cola;
- una Unidad activa nunca se desaloja por una aprobación posterior.

Este protocolo evita concurrencia en la máquina configurada y detecta conflictos,
pero no pretende ser un lock distribuido entre varias máquinas. Ejecutar otra copia
de la automatización en otro host queda fuera de alcance.

## Git, worktree y PR

- Worktree aislado, sin modificar el checkout actual del usuario.
- Base inicial: último origin/development.
- Rama: codex/pg-<id-sin-dos-puntos>-<slug>.
- Commit inicial: chore(plan): iniciar PG-...
- PR draft inmediatamente después de la autorización.
- Si un commit vacío no permite abrir el PR, usar una referencia temporal al plan y
  eliminarla con el primer cambio funcional.
- Cada PR enlaza todas las tareas con referencias, sin cerrarlas automáticamente.
- Nunca hacer force-push, borrar la rama, aprobar o fusionar automáticamente.

Cada Unidad de entrega posee rama remota y PR propios. No se presupone que su worktree
local sobreviva entre runs: al reanudar, Codex hace `fetch`, localiza el PR por su head
y usa un `detached HEAD` desde `origin/<rama-del-plan>` en el worktree aislado. Cada
push especifica de forma explícita `HEAD:refs/heads/<rama-del-plan>`, exige avance
fast-forward y nunca usa force. Así no intenta hacer checkout de una rama local que
pueda seguir asociada a otro worktree administrado por Codex. Dentro de un mismo run
puede reutilizarse secuencialmente el worktree de ejecución solo después de cerrar el
checkpoint de la unidad anterior y comprobar que no quedan cambios locales. La
automatización no elimina worktrees administrados por Codex como mecanismo de limpieza.

Cada paso lógico completo termina con commit, push fast-forward y checkpoint en el PR.
La automatización no cruza una pausa deliberada o una operación larga dejando como
única copia cambios funcionales sin commit en un worktree efímero.

Antes de comenzar código se vuelve a validar la base. Un cambio material invalida el
plan; una deriva no material se incorpora de forma segura sin ampliar el alcance.

## Rechazo, pausa y dependencias

Un rechazo antes de código funcional:

- conserva el plan como historial;
- devuelve las tareas In progress → Ready;
- devuelve un `[REQUERIMIENTO]` In progress → Backlog solo cuando la automatización
  fue propietaria de esa transición, no queda otra reserva o unidad activa de su
  alcance y ninguna Task vinculada está en In progress, Blocked, In review, In QA o
  Done;
- cierra un PR draft vacío si ya fue creado;
- conserva la rama como evidencia recuperable.

Si ya existe código funcional, una instrucción de cancelación pausa la unidad:

- no se agregan más cambios;
- las tareas permanecen In progress;
- rama y PR draft se conservan;
- no se cierra ni descarta nada sin una segunda instrucción explícita.

Si una unidad aprobada depende de un PR todavía no integrado:

- abre o conserva su PR draft;
- no apila la rama sobre el PR prerequisito;
- no duplica el código;
- permanece In progress como Espera de integración;
- cede el turno a unidades independientes;
- se actualiza desde development y se retoma al integrarse el prerrequisito.

Esta espera cubre dependencias descubiertas o modificadas después de reservar. Antes
de una reserva nueva rige la regla más estricta de Elegibilidad y prioridad: no se
reserva un dependiente cuyo prerrequisito aún no está integrado ni incluido en el grupo.

## Implementación y límites de alcance

La implementación se limita al Plan autorizado. Se permiten decisiones internas
necesarias para cumplirlo, pero no agregar tareas, comportamiento o criterios nuevos.

Los commits usan Conventional Commits y mantienen trazabilidad con el ID del plan.
La automatización conserva un resumen operativo actualizado en el PR: decisiones,
archivos, riesgos, validación, bloqueos y próximo paso.

## Validación proporcional

Siempre se validan los comportamientos afectados. Se agregan controles transversales
cuando la unidad toca:

- modelos o migraciones;
- permisos, roles o seguridad;
- datos compartidos;
- infraestructura;
- contratos consumidos por otros módulos.

Las tareas relacionadas pueden preparar datos y ejecutar sus pruebas en una misma
pasada cuando eso reduzca duplicación sin ocultar fallos.

Los fallos propios de implementación, tests o revisión nunca son Blocked: la unidad
permanece In progress y Codex los corrige.

## Revisión independiente

El fixed point es el merge-base contra origin/development. Antes de revisión humana
se ejecutan dos revisiones en contextos frescos y paralelos:

- Standards: reglas documentadas del repositorio y baseline de olores de código.
- Spec: Plan autorizado, Issues y criterios de aceptación.

La revisión exige cero hallazgos dentro del diff y los contratos directamente
afectados. La deuda preexistente no relacionada se informa, pero no amplía la unidad.
Cada corrección obliga a repetir ambos ejes hasta quedar limpios.

## Gate de CI y entrega a revisión humana

La evidencia válida pertenece al último commit del PR draft y a una base conocida de
`origin/development`.

Checks bloqueantes actuales:

- Django System Check.
- Migration Check.
- Tests & Coverage.
- Query Budgets & Smoke Time.
- Pip Audit.

Checks informativos que igualmente deben inspeccionarse:

- Ruff Lint.
- Ruff Format.
- Bandit Security Scan.
- Dependency Review.

Un hallazgo causado por el diff bloquea aunque el workflow use continue-on-error.
Checks aplicables ausentes, pendientes, cancelados o fallidos mantienen el PR draft y
las tareas en In progress.

Antes de marcar el PR listo, Codex vuelve a hacer `fetch`, registra head SHA y base SHA,
y comprueba mergeability. Si `origin/development` avanzó, actualiza la rama de forma no
destructiva, sin force-push; si la deriva es material, invalida el plan, y si no lo es,
repite Validación proporcional, ambas revisiones y CI sobre el nuevo head. Un check
omitido legítimamente por filtros de paths no se trata como ausente; los workflows
informativos se inspeccionan por sus pasos y logs, aunque el job global aparezca verde.

Solo con Validación proporcional aprobada, Revisión limpia y CI válida Codex:

1. actualiza el PR con la evidencia final;
2. lo convierte de draft a listo;
3. mueve todas las tareas In progress → In review;
4. inicia la siguiente unidad aprobada.

Codex nunca aprueba ni fusiona el PR.

## Entorno local de aceptación

Al finalizar una unidad, Codex levanta un entorno reproducible desde el worktree de
esa unidad, usando una ruta absoluta estable y externa a los worktrees para el archivo
de entorno, más un override de aceptación:

    docker compose --project-directory <worktree-unidad> --env-file <ruta-absoluta>\.env.local -p chaco-<grupo> -f docker-compose.yml -f docker-compose.acceptance.yml up -d --build --wait

Reglas:

- usar .env.local explícito;
- no imprimir secretos ni credenciales;
- publicar servicios solo en loopback; MySQL y Redis no se exponen al host salvo que
  una prueba focalizada lo requiera;
- RENAPER_TEST_MODE=True;
- antes de habilitar, cambiar la interpolación de
  `LOCAL_OPTIONAL_BOOTSTRAP_COMMANDS` de `${VAR:-default}` a `${VAR-default}` y fijar
  `LOCAL_OPTIONAL_BOOTSTRAP_COMMANDS=`; el entrypoint ya omite correctamente un valor
  vacío, mientras una variable ausente conserva el comportamiento histórico;
- datos sintéticos mediante fixtures o seeds versionados;
- agregar un seed focalizado e idempotente si faltan escenarios;
- fijar en cada Brief los comandos de bootstrap/seed, su orden y postcondiciones, y
  verificar los datos esperados después de ejecutarlos;
- esperar healthchecks y validar `/health/`; si `--wait` no está disponible, usar
  polling acotado y fallar si el servicio no queda listo;
- no usar datos productivos sin autorización separada;
- no ejecutar down -v.

El override de aceptación construye y etiqueta una imagen inmutable con el head SHA de
la unidad y elimina el bind mount del código fuente. Antes de dejar el stack activo se
verifica con `docker compose config` que la app se ejecute desde esa imagen. De ese
modo, los contenedores y sus datos no dependen de que el worktree de construcción siga
existiendo. El proyecto Compose y sus contenedores llevan labels con ID de plan, head
SHA y unidad propietaria para poder redescubrirlos y detenerlos de forma exacta.

Si quedan unidades aprobadas, Codex detiene el stack anterior sin borrar volúmenes y
continúa. Al terminar la última, deja el entorno activo, informa URL, proyecto
Compose, datos cargados y comando de apagado, y pregunta si debe conservarlo. Si no
hay respuesta, permanece activo. Una futura unidad aprobada puede detenerlo. La
automatización registra el worktree, proyecto Compose, puertos, volúmenes conservados
y unidad propietaria. Solo detiene el stack exacto que ella creó; nunca uno ajeno por
mera coincidencia de puerto. La limpieza posterior de volúmenes requiere autorización.

## Bloqueos y recuperación

Un Bloqueo externo requiere evidencia de una decisión funcional faltante, acceso,
dependencia de un tercero o infraestructura fuera de la unidad.

Para un check posiblemente inestable:

1. inspeccionar la causa;
2. reintentar una sola vez si parece externa;
3. si reaparece la misma causa externa verificada, comentar evidencia;
4. mover In progress → Blocked;
5. continuar con otra unidad aprobada independiente.

Cada ejecución revalida primero los bloqueos. Cuando desaparece, mueve Blocked →
In progress y reanuda antes de seleccionar trabajo nuevo, salvo que otra Unidad
activa ya tenga el turno.

## Resumen sin selección

Si no quedan tareas elegibles, la ejecución termina exitosamente sin mutaciones y
enumera por separado:

- planes pendientes de autorización;
- unidades autorizadas en cola;
- Esperas de integración;
- unidades pausadas;
- unidades con Bloqueo externo;
- Requerimientos que necesiten reconciliación;
- entorno local que haya quedado activo.

## Excepción automática de gobernanza

ESTADOS.md y AGENTS.md deben documentar una excepción exclusiva para esta
automatización:

- Ready → In progress al reservar.
- In progress → Ready al rechazar o compensar una reserva.
- In progress ↔ Blocked ante un bloqueo externo verificado.
- In progress → In review al superar el Gate de revisión humana.
- Requerimiento Backlog → In progress al reservar su primera tarea vinculada.
- Requerimiento In progress → Backlog al deshacer la última reserva propia, únicamente
  si ninguna Task del alcance avanzó más allá de Ready y no existe trabajo activo.

Todo movimiento restante continúa reservado al PM humano. La excepción no es un
permiso general para otros agentes. En particular, los Requerimientos nunca pasan
automáticamente a In QA ni Done.

## Seguridad e idempotencia

Antes de toda escritura, Codex verifica el estado actual y el recurso exacto.
Comentarios, reacciones, movimientos, ramas y PRs deben poder reintentarse sin
duplicarse.

Reglas concretas de idempotencia:

- buscar el marcador único y la huella antes de crear un plan o referencia;
- volver a consultar el Status esperado inmediatamente antes de cada transición;
- usar una clave de transición por plan, versión, item, origen y destino;
- compensar una transición solo si su reserva todavía es propietaria del item y no
  existe una reserva vencedora válida que requiera el estado actual;
- registrar ownership de cada transición de Requerimiento y no revertir estados
  preexistentes o establecidos por el PM;
- aceptar como éxito idempotente una reacción ya existente del actor y versión
  correctos; al reemplazarla, eliminar solo el `reaction_id` registrado;
- asignar secuencias monotónicas a los Eventos de decisión y aceptar duplicados de una
  secuencia solo cuando su clave idempotente y contenido sean idénticos;
- redescubrir rama y PR por el head esperado antes de crearlos;
- registrar checkpoints reintentables para reserva, decisión, activación, entrega y
  compensación;
- detenerse y reconciliar cuando haya dos sellos, eventos discordantes o más de un PR
  para el mismo head.

No se permiten:

- secretos en comentarios, logs o commits;
- datos productivos sin autorización;
- force-push;
- eliminación automática de ramas;
- down -v;
- autoaprobación o automerge;
- ampliación silenciosa del alcance.

## Puesta en marcha

1. Actualizar ESTADOS.md y AGENTS.md con la excepción acotada y la semántica de reserva.
2. Versionar en development este diseño, CONTEXT.md y esas reglas de gobernanza, con
   autorización explícita para commit/push; un worktree programado no ve archivos
   untracked del checkout principal.
3. Incluir además las invariantes críticas en el prompt de la tarea para que un fallo
   de lectura documental no amplíe permisos.
4. Ejecutar gh auth refresh con scopes read:project y project.
5. Verificar previamente que la computadora y Codex permanezcan disponibles, que el
   repo exista en la ruta configurada y que red, sandbox y permisos desatendidos estén
   preautorizados para GitHub Project, git push, PR y Docker. El run no puede resolver
   una aprobación de sistema en mitad de la ejecución.
6. Implementar y probar la lease exclusiva, marcadores y reconciliación de estado.
7. Simular en modo read-only elegibilidad, prioridad y agrupación contra todo el Project.
8. Verificar que la simulación no incluya In QA ni otros estados no permitidos.
9. Hacer en una tarea Codex regular con worktree un smoke supervisado de
   reserva/compensación, decisión, reanudación remota y entorno de aceptación antes del
   modo desatendido. Los fallos parciales se prueban con inyección controlada; toda
   mutación sobre items reales requiere autorización puntual y una ruta reversible.
10. Crear o actualizar mediante la herramienta de automations de Codex una única tarea
   programada para el proyecto local
   a03c533e-3faf-48f3-9afe-86962266722f.
11. Crearla pausada; no depender de que exista una acción API de ejecución inmediata.
12. Configurar worktree, lunes a viernes, 09:30 local y notificaciones normales.
13. Confirmar en la UI el horario efectivo y la política de avisos.
14. Activar la recurrencia solo después del smoke y permitir que la primera ejecución
    programada publique y reserve un solo grupo.

## Criterios de aceptación de la automatización

- Nunca selecciona trabajo nuevo fuera de la allowlist.
- Nunca incluye una tarea ya reservada en otro plan.
- Cada plan empieza con un resumen funcional breve y fácil de entender.
- Agrupa por resultado funcional, no por cantidad ni por mera cercanía temática.
- Mueve todo el grupo a In progress antes de solicitar autorización.
- Mantiene sincronizado cada `[REQUERIMIENTO]` vinculado sin crearlo ni llevarlo a
  In QA o Done.
- No modifica código sin 👍 y Evento de decisión concordantes para la versión exacta.
- Una observación no se interpreta como rechazo.
- Toda unidad aprobada se ejecuta secuencialmente, sin límite diario de política, y se
  reanuda desde estado remoto si el runtime actual termina.
- Cada unidad usa rama y PR propios y siempre se ejecuta en un worktree aislado, aunque
  el worktree local pueda recrearse entre runs.
- No apila ramas ante prerrequisitos sin integrar.
- El PR no queda listo ni las tareas pasan a In review sin validación, revisión limpia,
  CI del último commit y comprobación de la base actual de development.
- Un error propio no se etiqueta como Blocked.
- Un fallo externo solo bloquea después de evidencia y un reintento.
- El entorno final contiene datos reproducibles y nunca elimina volúmenes automáticamente.
- Dos runs del host configurado no pueden reservar ni modificar código a la vez; una
  ambigüedad de lease o estado detiene las escrituras y fuerza reconciliación.
- Cuando no hay trabajo nuevo, informa claramente pendientes, esperas y bloqueos.

## Documentación derivada

- CONTEXT.md: vocabulario acordado.
- ESTADOS.md: transiciones automáticas autorizadas.
- AGENTS.md: alcance de la excepción para futuros agentes.
- Este documento: diseño aprobado.

No se crea un ADR: la arquitectura puede cambiarse pausando la automatización y no
cumple el umbral de una decisión difícil de revertir.
