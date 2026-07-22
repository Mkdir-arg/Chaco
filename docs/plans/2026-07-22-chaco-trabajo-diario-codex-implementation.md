# Implementación de la automatización diaria de Chaco

Estado: autorizado para implementación y publicación en PR

Fecha: 2026-07-22

Diseño aprobado: `docs/plans/2026-07-22-chaco-trabajo-diario-codex-design.md`

## Resultado esperado

Entregar una única tarea programada de Codex, inicialmente pausada, que ejecute el
contrato aprobado de forma segura sobre el Project #1. La selección y agrupación
funcional siguen siendo razonamiento de Codex; identidad, elegibilidad, persistencia,
ownership, transiciones y recuperación se delegan a un helper determinista y testeado.

La automatización no se habilita hasta que:

- el código y las reglas estén integrados en `development`;
- `gh` tenga `read:project` y `project`;
- el snapshot real read-only pase;
- un smoke supervisado cubra mutaciones, puente de decisión, reanudación y entorno;
- GitHub, Git, Docker y filesystem funcionen sin pedir permisos durante un run;
- el horario efectivo se confirme en la UI;
- el usuario autorice activar la recurrencia.

## Límite de responsabilidades

| Componente | Decide o ejecuta |
| --- | --- |
| Codex | Comprende el pedido, inspecciona el código, agrupa por concepto, redacta el Brief, implementa, prueba y revisa |
| Helper determinista | Preflight, snapshot, lease, marcadores, fingerprint, comentarios, reacciones, ownership, transiciones, rama/PR y reconciliación |
| GitHub | Fuente durable de planes, decisiones, Project, ramas, PR y checks |
| Docker Compose | Entorno final de aceptación respaldado por una imagen del head SHA |
| Usuario | Autoriza o rechaza cada versión del Plan de grupo y revisa el PR final |

## Archivos previstos

| Archivo | Cambio |
| --- | --- |
| `scripts/codex_daily_work.py` | CLI determinista, sin dependencias nuevas |
| `core/tests/test_codex_daily_work.py` | Tests unitarios con `SimpleTestCase` y mocks de `gh`, Git y reloj |
| `docker-compose.yml` | Hacer que una variable opcional definida vacía permanezca vacía |
| `docker-compose.acceptance.yml` | Stack sin bind mount, puertos seguros e imagen etiquetada por SHA |
| `.dockerignore` | Excluir scratch de la automatización del contexto de imagen |
| `docs/plans/2026-07-22-chaco-trabajo-diario-codex-prompt.md` | Prompt canónico versionado de la tarea programada |
| `docs/plans/2026-07-22-chaco-trabajo-diario-codex-design.md` | Diseño aprobado y auditado |
| `docs/plans/2026-07-22-chaco-trabajo-diario-codex-implementation.md` | Este plan |
| `CONTEXT.md` | Lenguaje compartido |
| `ESTADOS.md` | Gates y excepción automática acotada |
| `AGENTS.md` | Alcance permitido para futuros agentes |

No se agregan paquetes, base de datos de coordinación, Issue coordinador, workflow de
CI adicional ni archivo mutable de estado dentro del repositorio.

## Fase 1 — Aislar y congelar el contrato

1. Crear un worktree aislado desde el último `origin/development` con rama
   `codex/chaco-daily-automation`.
2. Trasladar únicamente los archivos nombrados en este plan; no incorporar cambios de
   la rama o checkout actual del usuario.
3. Confirmar que diseño, glosario, `ESTADOS.md` y `AGENTS.md` dicen lo mismo sobre:
   - reserva previa a autorización;
   - Sello y Evento de decisión;
   - Task y Requerimiento;
   - ownership y compensación;
   - Blocked e In review;
   - prohibiciones de merge, aprobación propia, force-push y datos productivos.
4. Mantener la automatización deshabilitada mientras estos archivos no estén en
   `development`.

Gate: diff documental coherente y sin preguntas abiertas.

## Fase 2 — Construir primero el modelo puro y sus tests

Crear tests fallando antes de la integración con GitHub para:

1. Preflight:
   - identidad exacta `juanikitro` y database ID estable esperado;
   - scopes requeridos;
   - Project único y editable;
   - campos/opciones resueltos por nombre;
   - paginación completa y `count == totalCount`;
   - una sola iteración vigente, inicio inclusivo y fin exclusivo en Buenos Aires.
2. Elegibilidad:
   - Issue abierto, Tipo Task, Ready, único assignee correcto, Iteration vigente;
   - Prioridad, Modulo, EstimacionHoras, QA, épica y análisis válidos;
   - exclusión explicada para cada item que no cumpla.
3. Dependencias y orden:
   - integrada en `development` o incluida en la misma unidad;
   - In QA exige comprobar el commit y registrar riesgo;
   - las demás dependencias sin integrar excluyen al dependiente.
   - ranking estable por prerrequisitos, prioridad, trabajo desbloqueado y antigüedad.
4. Task → Requerimiento:
   - cero Requerimientos para el mismo repo y épica es válido;
   - uno para la épica es el vínculo canónico;
   - si ese Requerimiento no enumera el análisis de la Task, queda desactualizado y
     bloquea para reconciliación;
   - más de uno para la épica o un formato ambiguo bloquea antes de escribir;
   - el rollback inspecciona todas las Tasks del alcance, no solo las asignadas.
5. Planes y decisiones:
   - marcador HTML versionado y fingerprint estable;
   - secuencia de plan y colisiones;
   - Evento de decisión monotónico;
   - reacción aislada inválida;
   - solo el último evento válido puede concordar con el sello vigente;
   - autorización completa persiste, crea/recupera PR y activa o encola;
   - rechazo antes de código libera y después de código pausa;
   - observación produce cero mutaciones;
   - caída entre reacción, evento, PR y compensación se reanuda idempotentemente.
6. Lease y ownership:
   - creación atómica en el Git common dir;
   - rechazo de token ajeno o vencido;
   - heartbeat y recuperación solo tras expiración y reconciliación;
   - compensación parcial que no desarma una reserva vencedora;
   - un Requerimiento previamente In progress nunca se reclama ni se revierte.
7. Allowlist de transiciones:
   - aceptar solo las transiciones documentadas;
   - fallar cerrado ante estado inesperado;
   - no mover Requerimientos a In QA o Done;
   - Blocked exige dos intentos con la misma huella externa, evidencia saneada y causa
     fuera de la unidad; un error de código/test/revisión se rechaza;
   - resume exige una comprobación vigente de que desapareció la causa externa;
   - deliver exige checkpoints de validación, Standards y Spec para el head actual,
     checks aplicables válidos, base actual y mergeability; cualquier evidencia
     ausente, vieja o discordante se rechaza.
8. Política de siguiente acción:
   - una Unidad activa o la Cola autorizada impiden proponer trabajo nuevo;
   - un Plan pendiente sin autorizar no impide una única propuesta adicional;
   - jamás se producen dos propuestas nuevas en el mismo Ciclo programado;
   - una unidad interrumpida por runtime se reanuda antes de seleccionar otra.

Los fixtures son pequeños y sintéticos dentro del test. No contienen cuerpos reales
completos, credenciales ni tokens.

Gate:

```powershell
$env:PY_VENV = "C:\Users\Juanito\Desktop\Repositorios\I-CORE\Chaco\.venv\Scripts\python.exe"
$env:DJANGO_SECRET_KEY = "test-key"
& $env:PY_VENV manage.py test core.tests.test_codex_daily_work --verbosity=2
```

El worktree aislado no contiene `.venv`. El preflight verifica esta ruta compartida,
Python 3.12 y las herramientas necesarias; no instala paquetes durante un run
desatendido.

## Fase 3 — Implementar el helper determinista

`scripts/codex_daily_work.py` seguirá el patrón de los scripts existentes: stdlib,
`argparse`, `main(argv=None)`, salida JSON opcional y `subprocess.run` con listas de
argumentos y `shell=False`.

### Interfaz prevista

- `state --json`: preflight, snapshot, reconciliación read-only y siguiente acción
  permitida (`continue_active`, `activate_authorized`, `plan_new`, `wait`, `conflict`).
- `lease acquire|renew|release`: crea atómicamente la lease en el Git common dir,
  devuelve un token opaco y exige ese mismo token para renovar o liberar. La
  recuperación de una lease vencida requiere `reconcile` sin conflictos.
- `reserve --input <plan.json>`: dry-run por defecto; con `--apply`, renderiza el
  comentario canónico y referencias, resuelve ganador, mueve Tasks y sincroniza
  Requerimientos.
- `apply-decision --plan <PG> --decision <authorize|reject>`: lee la frase original
  por stdin y orquesta una decisión completa. Autorizar persiste 👍 + evento, crea o
  recupera branch/commit/PR y activa o encola; rechazar persiste 👎 + evento y, si no
  hay código, libera Task/Requerimiento y cierra solo un PR vacío. Si ya hay código,
  pausa sin descartar. Una observación no llama este comando.
- `activate --plan <PG>`: recuperación idempotente de una autorización ya persistida;
  rechaza cualquier versión sin Sello + Evento vigentes.
- `checkpoint --plan <PG> --phase <fase>`: persiste progreso reanudable y evidencias.
- `transition --plan <PG> --event <block|resume|deliver>`: aplica exclusivamente las
  transiciones permitidas después de validar sus gates.
- `reconcile --json`: informa conflictos; con `--apply`, repara únicamente operaciones
  propias y compensables.

Toda mutación exige simultáneamente `--apply`, token de lease vigente, plan/version,
estado esperado e idempotency key. Un comando sin `--apply` no llama endpoints de
escritura, no hace commits y no modifica el Project.

Los JSON transitorios se crean en el directorio temporal del sistema, nunca dentro del
contexto Docker ni como archivos versionables del worktree.

El flujo normal adquiere la lease al comienzo del turno, la renueva antes de cada fase
mutante y la libera en un bloque final. Una caída deja expirar la lease; ningún otro
run la recupera sin reconciliar primero GitHub. Los tests cubren acquire → renew →
mutaciones → release, token ajeno, expiración y caída entre decisión y activación.

### Lectura de GitHub

1. Usar GraphQL para Project v2 y paginar hasta `hasNextPage=false`.
2. Resolver en vivo `Status`, `Tipo`, `Prioridad`, `Modulo`, `EstimacionHoras` e
   `Iteration`; las constantes locales solo sirven como control de drift.
3. Usar `content.repository.nameWithOwner` para tolerar el redirect del repo.
4. Usar REST para comentarios y reacciones, conservando los IDs devueltos.
5. Parsear de forma estricta `Épica padre` y `Análisis de origen`.
6. Redactar motivos de inclusión/exclusión sin volcar cuerpos completos ni secretos.

### Evidencia exigida por `transition`

- `block`: dos resultados con la misma huella de causa, incluido un único reintento,
  categoría externa permitida, timestamps, URL de run/check cuando exista y extracto
  saneado. El helper rechaza categorías de implementación, test o revisión propia.
- `resume`: prueba focalizada actual que demuestre que desapareció la misma huella de
  bloqueo; no basta el paso del tiempo.
- `deliver`: head SHA y base SHA actuales, PR mergeable, checkpoint de Validación
  proporcional, Eventos Standards y Spec en limpio para ese head, checks aplicables
  terminados y ausencia de una base más nueva. El helper consulta GitHub y no acepta
  evidencia declarativa desactualizada aportada solo por Codex.

Los tests incluyen casos negativos por evidencia ausente, intento único, huella
distinta, review de otro SHA, check omitido que sí era aplicable y base avanzada.

### Reserva y compensación

1. Releer Tasks y Requerimientos inmediatamente antes de escribir.
2. Crear comentario canónico y referencias.
3. Resolver carreras por menor `comment_id`.
4. Mover Tasks una por una, verificando después de cada mutación.
5. Sincronizar Requerimientos solo después de reservar sus Tasks.
6. Ante fallo, revertir únicamente transiciones propias que no necesite una reserva
   vencedora.
7. Hacer snapshot final antes de presentar el plan en Codex.

### Activación Git y PR

1. Rechazar un worktree sucio.
2. Hacer `fetch` y partir de `origin/development` o de la rama remota del plan.
3. Trabajar en detached HEAD para no competir con branches locales de otros worktrees.
4. Crear el commit vacío `chore(plan): iniciar <PG>` cuando la rama aún no exista.
5. Empujar explícitamente HEAD a la branch remota esperada, solo fast-forward.
6. Crear o recuperar un único PR draft por head; nunca aprobar, mergear, borrar branch
   ni usar force-push.

Gate: todos los tests de la Fase 2 verdes y errores de `gh` clasificados sin exponer
tokens ni stdout sensible.

## Fase 4 — Entorno de aceptación seguro

1. Cambiar en `docker-compose.yml` la interpolación de
   `LOCAL_OPTIONAL_BOOTSTRAP_COMMANDS` para que una variable definida vacía no reciba
   el default; el comportamiento histórico se conserva si la variable está ausente.
2. Crear `docker-compose.acceptance.yml` y comprobar con la versión instalada de
   Compose que:
   - elimina el bind mount `.:/app`;
   - construye una imagen etiquetada con el head SHA;
   - publica la app solo en `127.0.0.1`;
   - no publica MySQL ni Redis al host;
   - fuerza `RENAPER_TEST_MODE=True`;
   - deja vacíos los comandos opcionales;
   - conserva volúmenes sin permitir `down -v`.
3. Guardar la configuración local en una ruta estable externa a los worktrees,
   `C:\Users\Juanito\.config\chaco-automation\.env.local`, con permisos restringidos.
   Se crea a partir del ejemplo con valores solo locales, nunca productivos, y no se
   imprime ni se copia al repo.
4. Justo antes del build, exigir worktree limpio, obtener el SHA completo, añadir
   label OCI `org.opencontainers.image.revision` y etiquetar la imagen con ese SHA.
   Comprobar también que no haya scratch ignorado inesperado dentro del contexto y
   excluir `.tmp_*` en `.dockerignore`. Después del build registrar y verificar image
   ID o digest.
5. El Brief de cada unidad declara comandos de seed, orden y postcondiciones.
6. `up --wait` o polling acotado debe terminar con `/health/` válido y datos esperados
   comprobados.
7. Registrar Project de Compose, labels, imagen, head SHA, puertos y volúmenes en el
   checkpoint del plan. La rotación localiza por labels y detiene solo el stack propio.

Validación estática, sin usar secretos reales:

```powershell
docker compose --env-file .env.local.example `
  -f docker-compose.yml `
  -f docker-compose.acceptance.yml `
  config --quiet
```

Además de la sintaxis, renderizar `config --format json` y afirmar mecánicamente:

- `app` solo publica `127.0.0.1:8000`;
- `mysql` y `redis` no tienen puertos de host;
- `app` no conserva el bind mount del código;
- imagen y label usan el SHA completo esperado;
- `RENAPER_TEST_MODE` es verdadero y los comandos opcionales están vacíos.

La prueba runtime de Docker requiere una autorización separada al ejecutar esta fase,
porque construye imágenes, inicia contenedores y una base local.

## Fase 5 — Versionar el prompt operativo

Crear `docs/plans/2026-07-22-chaco-trabajo-diario-codex-prompt.md` con dos capas:

1. Contrato innegociable breve, embebido luego en la tarea programada:
   - el run es standalone: no conserva chat, worktree ni estado local anterior;
   - identidad, allowlist y prioridad de continuidad;
   - lease, estado esperado, relectura e idempotency key en toda mutación;
   - cero escrituras ante ambigüedad, scope faltante o conflicto;
   - máximo un plan nuevo por ejecución;
   - código solo con Sello + Evento vigentes;
   - observación no decide; rechazo libera antes de código y pausa después de código;
   - autorización aplica decisión, abre PR y activa o encola inmediatamente;
   - transiciones exactas de Task y Requerimiento;
   - una unidad funcional activa a la vez;
   - bootstrap limpio y detached desde la rama remota correcta;
   - entrega solo con validación, Standards, Spec y CI del head/base actuales;
   - prohibiciones de secretos, producción, force-push, merge y `down -v`.
2. Procedimiento que obliga a leer, en orden:
   - verificar remoto, worktree limpio y capacidades sin pedir aprobación;
   - hacer `fetch` y posicionarse en detached HEAD de `origin/development`;
   - `AGENTS.md` y cualquier instrucción local aplicable;
   - `ESTADOS.md`;
   - diseño, prompt y `CONTEXT.md`;
   - `QA.md` cuando corresponda;
   - estado vivo devuelto por el helper;
   - si hay una Unidad activa, cambiar después a detached HEAD de su branch remota;
   - código focalizado, empezando por modelos según el método del repo.

El prompt ordena usar el helper para todas las escrituras de coordinación. Codex
conserva la responsabilidad semántica de agrupar, implementar, validar y ejecutar las
dos revisiones frescas. Las preferencias de notificación se configuran en Codex y no
se incluyen dentro del prompt.

Cada paso lógico de implementación termina con commit, push fast-forward y checkpoint
en el PR. Antes de una validación larga o de devolver el turno, no puede quedar como
única copia trabajo funcional sin commit dentro del worktree efímero.

Una respuesta exacta del usuario en la misma tarea ejecuta `apply-decision` dentro de
ese turno. Si autoriza y no hay otra Unidad activa, Codex continúa la implementación;
si debe encolar, lo informa. Si rechaza, confirma la compensación o la pausa. Una
ejecución programada posterior solo consume el estado ya persistido en GitHub.

## Fase 6 — Validación local focalizada

Sin Docker ni mutaciones GitHub:

```powershell
$env:PY_VENV = "C:\Users\Juanito\Desktop\Repositorios\I-CORE\Chaco\.venv\Scripts\python.exe"
$env:DJANGO_SECRET_KEY = "test-key"
& $env:PY_VENV manage.py test core.tests.test_codex_daily_work --verbosity=2
& $env:PY_VENV -m compileall -q scripts\codex_daily_work.py
& $env:PY_VENV -m ruff check scripts\codex_daily_work.py core\tests\test_codex_daily_work.py
& $env:PY_VENV -m ruff format --check scripts\codex_daily_work.py core\tests\test_codex_daily_work.py
git diff --check
```

Antes de usarlo se comprueba que el venv compartido exista, sea Python 3.12 y tenga
Ruff disponible. Si falta una herramienta no se instala silenciosamente durante el
run: se detiene la puesta en marcha o se deja esa comprobación explícitamente a CI.

Integración read-only, primero con los scopes actuales y luego de ampliarlos:

1. Confirmar que scopes faltantes producen `preflight_failed` y cero escrituras.
2. Tras `gh auth refresh -s read:project,project`, ejecutar `state --json`.
3. Verificar identidad, Project, campos, opciones, iteración, paginación y motivos de
   elegibilidad.
4. Comprobar vínculos Task → Requerimiento con datos vivos; si los ejemplos observados
   cambiaron, verificar el algoritmo, no congelar números históricos como verdad.
5. Ejecutar un `reserve` dry-run y revisar el ledger sin publicar comentarios ni mover
   items.

No se corre la suite completa localmente; el PR contra `development` ejecutará los
checks existentes. Cualquier validación adicional se decide por el diff real.

## Fase 7 — Publicación y revisión de la implementación

Con autorización explícita para Git:

1. Crear commits Conventional Commits, agrupados por documentación, helper y entorno.
2. Stagear solo los archivos nombrados; no usar `git add -A`.
3. Push de `codex/chaco-daily-automation` y PR draft a `development`.
4. Ejecutar dos revisiones frescas e independientes:
   - Standards: reglas del repo, seguridad, idempotencia y mantenibilidad.
   - Spec: cobertura exacta del diseño aprobado.
5. Corregir y repetir hasta cero hallazgos dentro del diff y contratos afectados.
6. Esperar CI del último head, inspeccionar también Ruff/Bandit informativos y
   verificar base/mergeability.
7. Convertir el PR en listo; no aprobarlo ni fusionarlo.

La automatización no se crea todavía: un worktree standalone debe poder leer el helper
y las reglas desde `development`.

## Fase 8 — Crear la tarea programada después del merge

1. Verificar que el PR anterior fue fusionado y que `origin/development` contiene los
   archivos y tests esperados.
2. Completar manualmente el refresh de scopes de `gh` y repetir `state --json`.
3. Preparar el venv compartido y la ruta externa de `.env.local`; comprobar existencia,
   permisos y valores seguros sin imprimirlos.
4. En una tarea Codex regular con worktree, ejecutar el smoke completo antes del modo
   desatendido:
   - bootstrap detached desde `origin/development`;
   - lease completa y recuperación inyectada;
   - reserva y compensación sobre un item reversible expresamente autorizado;
   - `apply-decision`, PR y reconstrucción desde la rama remota;
   - transición negativa para Blocked/deliver;
   - build, health y parada exacta del stack sin borrar volúmenes.
5. Verificar que `fetch`, escrituras GitHub, push, PR, Python y Docker funcionan con la
   política desatendida sin abrir pedidos de permiso. Confirmar que la computadora, la
   app, el repo, la red y esas capacidades estarán disponibles al horario programado.
6. Consultar el Project local mediante `codex_app__list_projects` y crear mediante
   `codex_app__automation_update` una única automatización:
   - nombre: `Trabajo diario asignado en Chaco`;
   - proyecto local Chaco;
   - ejecución en worktree standalone;
   - lunes a viernes a las 09:30 locales;
   - modelo de alta capacidad y razonamiento alto;
   - notificaciones normales;
   - estado inicial pausado.
7. Verificar en la UI proyecto, prompt, horario efectivo, zona local, worktree y
   política de avisos.
8. No depender de una operación API `run now`. Si la UI instalada ofrece ejecución
   manual puede usarse como comprobación adicional, pero el smoke previo sigue siendo
   obligatorio.
9. Tras confirmación final, cambiar esa misma automatización a activa. Su primera
   ejecución programada puede publicar y reservar como máximo un grupo.
10. Comprobar comentario, referencias, Tasks, Requerimientos y respuesta en Codex. Si
    falla, pausar, reconciliar y no crear una segunda automatización.

## Rollback

- Antes del primer run: pausar o eliminar la automatización; no hay estado GitHub que
  revertir.
- Reserva parcial: usar `reconcile --apply` con ownership; nunca hacer cambios manuales
  masivos.
- Rechazo sin código: Tasks a Ready, Requerimiento propio a Backlog si cumple el gate,
  PR vacío cerrado y branch conservada.
- Problema del helper: pausar la automatización, mantener Project/PR como evidencia y
  corregir mediante un PR normal.
- Entorno local: detener solo el Project Compose identificado, sin `down -v`; borrar
  volúmenes requiere otra autorización.

## Definición de terminado

- Reglas y helper integrados en `development`.
- Tests focalizados y CI del PR verdes.
- Scopes, identidad, Project e iteración verificados en vivo.
- Dry-run sin escrituras revisado.
- Automatización única visible en Codex con horario correcto.
- Primer Plan de grupo reservado de forma completa e idempotente.
- Una autorización o rechazo de prueba persiste reacción y Evento concordantes.
- No existen duplicados, estados parciales ni cambios fuera de la allowlist.
