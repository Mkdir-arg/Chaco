# Contexto Funcional del Proyecto

> **Regla:** El Analista Funcional lee este documento ANTES de escribir cualquier user story.
> **Regla:** El Documentador actualiza este documento al cierre de cada Fase 5.

> Última actualización: 2026-04-03 (sesión 9 — DX-059 stack local docker)


---

## Qué es el sistema

SistemSo es un sistema de gestión estatal. Permite a organismos de gobierno gestionar ciudadanos, programas sociales e instituciones. Tiene dos superficies: el **backoffice** (para operadores y profesionales del estado) y el **portal ciudadano** (acceso público para el ciudadano).

Los tres dominios centrales son:
- **Ciudadanos** — toda la información del ciudadano trazada: programas, ayudas, grupo familiar, domicilio, historial
- **Programas** — procesos configurables con flujos, capacidades activables y ciclo de vida propio
- **Instituciones** — entidades que brindan servicios al estado, puntos donde se dan las actividades de los programas

---

## Actores del sistema

| Actor | Quién es | Qué hace |
|-------|----------|---------|
| **Operador backoffice** | Empleado del organismo | Gestiona legajos, conversaciones, turnos, derivaciones |
| **Profesional** | Psicólogo, trabajador social, etc. | Lleva legajos de atención, planes de intervención, seguimientos |
| **Administrador** | Rol técnico/supervisor | Configura el sistema, aprueba instituciones, gestiona usuarios |
| **Ciudadano** | Persona en situación de vulnerabilidad | Accede al portal para turnos, ver sus programas, hacer consultas |
| **Encargado de Institución** | Representante de una ONG/organismo | Registra su institución, ve el estado del trámite |

---

## Reglas de negocio confirmadas

> Estas decisiones fueron tomadas y NO deben cuestionarse sin revisión explícita del usuario.

### Actividades institucionales — inscripción
- Un ciudadano **puede reinscribirse** a una actividad si su inscripción anterior tiene estado ABANDONADO o FINALIZADO
- Solo puede haber **una inscripción activa** (INSCRITO o ACTIVO) por (ciudadano, actividad) al mismo tiempo — garantizado por service con `select_for_update`
- `cupo_ciudadanos = 0` en `PlanFortalecimiento` significa **sin límite de cupo**; un cupo real es siempre >= 1
- El **código de inscripción** es de 8 caracteres alfanuméricos en mayúsculas, único globalmente, permanente
- Los operadores del backoffice inscriben por DNI; los ciudadanos se inscriben desde el portal (solo actividades LIBRE)

### Búsqueda de ciudadanos
- Los operadores pueden buscar ciudadanos por **nombre** (parcial) o por **DNI**
- La búsqueda debe ser suficientemente rápida para ser usada durante una atención telefónica

### Ciudadanos
- Se identifican por **DNI** (campo único en el sistema) — no puede haber dos registros del mismo ciudadano
- La identidad se verifica contra **RENAPER** (DNI + sexo) en el registro desde el portal ciudadano
- Alta también disponible de forma manual cuando RENAPER no está disponible
- Un ciudadano puede estar inscripto en múltiples programas simultáneamente
- Un ciudadano puede estar en múltiples instituciones

#### Información registrada en la ficha del ciudadano
- **Datos básicos:** DNI, nombre, apellido, fecha nacimiento, género, teléfono, email, domicilio, provincia, municipio, foto
- **Grupo familiar** (ya implementado)
- **Situación habitacional:** tipo de vivienda, tenencia, condiciones
- **Situación laboral / económica:** situación laboral, ingreso estimado, obra social
- **Nivel educativo**
- **Cobertura médica / medicación habitual** *(campo sensible — requiere `ciudadanoSensible`)*
- **Documentación:** DNI físico, estado RENAPER, estado migratorio *(campo sensible)*
- **Observaciones / notas libres**

#### Hub del ciudadano `/legajos/ciudadanos/<id>/`
El perfil del ciudadano es el centro de toda su información. Tiene solapas estáticas y dinámicas con badge behavior:

| Solapa | Tipo | Qué muestra |
|--------|------|-------------|
| Resumen | Estática | Vista general del ciudadano |
| Cursos y Actividades | Estática | Historial de actividades en instituciones |
| Red Familiar | Estática | Grupo familiar |
| Archivos | Estática | Documentos adjuntos |
| Programas | Dinámica | Programas en los que está inscripto |
| Turnos | Dinámica | Turnos asignados |
| Instituciones | Dinámica | Instituciones donde fue atendido |
| Conversaciones | Dinámica | Consultas y chat con operadores |
| Derivaciones | Dinámica | Historial de derivaciones |
| Alertas | Dinámica | Alertas activas |
| Línea de tiempo | Dinámica | Todo lo que pasó cronológicamente |

**Comportamiento de solapas:** contador numérico en cada tab · las dinámicas se ocultan si no tienen datos · indicador visual si hay algo que requiere atención

#### Roles del ciudadano
| Rol | Qué permite |
|-----|------------|
| `ciudadanoVer` | Ver la ficha completa (sin campos sensibles) |
| `ciudadanoCrear` | Crear y editar ciudadanos |
| `ciudadanoSensible` | Acceder a campos de salud, documentación migratoria y campos marcados como sensibles |

#### Acceso por ámbito
- Operador de **institución** → ve solo ciudadanos que pasaron por esa institución
- Operador de **programa / backoffice** → ve todos los ciudadanos, gestiona solo los de su ámbito

#### Confidencialidad en dos capas
- Campos de salud y documentación migratoria → sensibles por defecto (requieren `ciudadanoSensible`)
- El operador puede marcar campos adicionales como sensibles al cargar el ciudadano

#### Implementación del control de acceso a campos sensibles (confirmado US-008)
- **Campos sensibles definidos:** `cobertura_medica`, `medicacion_habitual`, `estado_migratorio`
- **Flag de acceso:** `puede_ver_sensible = user.is_superuser or user.groups.filter(name='ciudadanoSensible').exists()`
- **Protección en tres capas independientes:**
  1. **Form layer** — los fields sensibles no se inyectan en el form si el flag es `False`; `save()` tampoco los persiste sin el flag
  2. **View layer** — la view calcula el flag y lo pasa como kwarg al form y como variable de contexto
  3. **Template layer** — la sección sensible está envuelta en `{% if puede_ver_sensible %}`
- **La foto del ciudadano NO es sensible** — la puede ver cualquier operador con acceso a la ficha (sin requerir `ciudadanoSensible`)
- Este patrón de tres capas es el estándar a seguir para cualquier futuro campo sensible en el sistema

### Instituciones
- Pasan por un flujo de aprobación: BORRADOR → ENVIADO → REVISION → APROBADO/RECHAZADO
- Solo instituciones APROBADAS pueden ofrecer servicios activos
- Tipos: DTC, CAAC, CCC, CAI, IC, CT (según clasificación SEDRONAR)
- Una institución puede tener múltiples encargados (ManyToMany con User)
- Una institución puede tener su propia `ConfiguracionTurnos` (OneToOne)
- Cada institución tiene un **legajo institucional** con: personal, evaluaciones periódicas, planes de fortalecimiento (actividades) e indicadores de monitoreo
- Una institución puede estar habilitada para ejecutar múltiples programas (`InstitucionPrograma`)

#### Roles de institución — backoffice
| Rol | Qué permite |
|-----|------------|
| `institucionVer` | Ver el catálogo de instituciones y sus datos |
| `institucionAdministrar` | Crear, editar, aprobar/rechazar instituciones |

#### Roles internos del panel institución
| Rol | Qué permite |
|-----|------------|
| `EncargadoInstitucion` | Acceso total al panel + gestionar usuarios internos (crear/eliminar administrativos y profesores) + único que puede solicitar revisión o reactivación |
| `AdministrativoInstitucion` | Configura actividades, asigna profesores, ve turnos — no puede gestionar usuarios |
| `ProfesorInstitucion` | Toma asistencia en actividades, se asigna a actividades — ve nombre, foto y contacto básico del ciudadano (sin ficha completa ni campos sensibles) |

#### Panel institución — tercera superficie del sistema
- URL: `/institucion/` — superficie propia con middleware y base template separados
- Mismo sistema de login Django — el sistema detecta el rol y redirige automáticamente al panel institución
- Patrón arquitectónico idéntico al portal ciudadano (`portal/`)
- Los tres roles (`EncargadoInstitucion`, `AdministrativoInstitucion`, `ProfesorInstitucion`) acceden exclusivamente a esta superficie

#### Reactivación de institución RECHAZADA
- Una institución RECHAZADA puede solicitar reactivación
- La puede iniciar la propia institución desde su panel (botón "Solicitar reactivación") **o** el backoffice la inicia y notifica a la institución
- El proceso se guarda como `REACTIVACION` — historial diferenciado de la aprobación original
- La institución recibe notificación informando que es un proceso de reactivación, no una aprobación nueva

#### Evaluaciones periódicas a instituciones
- Son **tareas territoriales aplicadas a instituciones** — mismo mecanismo que las tareas del motor de flujos
- Las crean los administradores del programa desde el backoffice
- Se asignan a un operador territorial que las completa desde la **app de campo (móvil)**
- El resultado queda vinculado al legajo de la institución evaluada
- **Prerequisitos:** motor de flujos (US-006) + app móvil definida y operativa

#### Indicadores de monitoreo
- Métricas internas de la institución: alumnos activos, profesores, actividades en curso, turnos agendados

### Actividades institucionales

- Una actividad **siempre pertenece a una institución** — no existen actividades sin institución
- Las actividades viven en el legajo institucional como `PlanFortalecimiento`
- Tipos: `PREVENCION`, `TRATAMIENTO`, `REDUCCION_RIESGO`, `REINSERCION`, `CAPACITACION`
- Una actividad puede tener su propia `ConfiguracionTurnos` para ofrecer turnos propios
- Un ciudadano puede estar inscripto en **múltiples actividades simultáneamente**

#### Tipos de acceso a una actividad

| Tipo | Descripción | Quién puede inscribir |
|------|-------------|----------------------|
| **LIBRE** | Actividad abierta | El ciudadano desde el portal, o cualquier operador/encargado |
| **REQUIERE_PROGRAMA** | Solo para inscriptos en un programa específico | Solo operadores que gestionen ese programa o encargados de la institución |

**Campo en `PlanFortalecimiento`:** `tipo_acceso = LIBRE | REQUIERE_PROGRAMA`. Si es `REQUIERE_PROGRAMA`, FK al `Programa` asociado.

#### Cupo y lista de espera

- El cupo máximo es **opcional** — se configura al crear la actividad
- La lista de espera es **opcional** — se configura junto con el cupo
- Cuando se libera un cupo con lista de espera activa, hay dos modos (configurable):
  - **Automático**: se asigna al siguiente en la lista sin intervención
  - **Manual**: el operador elige quién de la lista ocupa el lugar

#### Fechas de la actividad

- Fecha de inicio y fecha de fin son **opcionales**
- Si se configura fecha de fin y se llega a ella → todos los ciudadanos `ACTIVO` pasan automáticamente a `FINALIZADO`

#### Clases (entidad dentro de la actividad)

- Una actividad se organiza en **clases** — entidades con: fecha, hora de inicio, duración y título opcional
- Las clases son creadas con anticipación por el staff o el encargado de la institución
- La asistencia se registra **por clase** — valores: `PRESENTE / AUSENTE / JUSTIFICADO / TARDANZA`
- Pueden registrar asistencia: el **staff asignado a la actividad** + el **encargado de la institución**

#### Inscripción a una actividad

El ciudadano queda en `InscriptoActividad` con estados:

| Estado | Cómo se llega |
|--------|--------------|
| `INSCRITO` | Al inscribirse, antes de la primera clase |
| `ACTIVO` | Al comenzar a participar |
| `FINALIZADO` | Automático al llegar la fecha fin de la actividad, o manual si el staff lo marca como completado satisfactoriamente |
| `ABANDONADO` | Manual por operador/staff, o auto-desinscripción del ciudadano desde el portal |

**Al inscribirse:** el ciudadano recibe un **código de inscripción** como confirmación y lo ve en su perfil del portal.

**Al abandonar:** los turnos pendientes de la actividad se cancelan y los slots vuelven a estar disponibles.

#### Staff de la actividad

- Se crea y gestiona desde la solapa de gestión dentro de la institución
- Se asigna a una actividad específica desde dentro de la actividad misma
- Solo el staff asignado + el encargado de la institución pueden registrar asistencia

#### Vista del ciudadano — solapa "Cursos y Actividades"

La tarjeta de cada actividad muestra: **nombre, institución, estado, próxima clase, asistencia acumulada**.
Incluye tanto actividades activas como historial completo.
El ciudadano también puede ver su **porcentaje de asistencia** desde el portal.

### Derivaciones

Actualmente existen dos modelos de derivación en el sistema que **se unificarán** (US-021):

| Modelo | Estado | Origen | Destino |
|--------|--------|--------|---------|
| `Derivacion` | Legacy — deprecar | `LegajoAtencion` SEDRONAR | Institución + Actividad opcional |
| `DerivacionInstitucional` | Nuevo | `Ciudadano` | `InstitucionPrograma` (institución + programa) |

**Decisión tomada:** unificar en un solo modelo que sale desde `Ciudadano`. La `Derivacion` legacy se depreca cuando `LegajoAtencion` migre al motor de flujos (US-006).

El modelo unificado tendrá:
- Origen: `Ciudadano`
- Destino: puede ser `InstitucionPrograma` (ciudadano va a programa en institución) o `PlanFortalecimiento` (ciudadano va a actividad específica)
- `tipo_inicio`: `DERIVACION` (cualquier operador) | `INSCRIPCION_DIRECTA` (solo gestores del programa destino)
- Estados: `PENDIENTE` → `ACEPTADA` / `RECHAZADA`
- Urgencia: `BAJA` / `MEDIA` / `ALTA`
- Campos: motivo, respuesta, quién deriva, quién responde, fecha respuesta
- Sin vencimiento: las derivaciones PENDIENTE quedan indefinidamente hasta que el operador destino actúe

#### Quién acepta una derivación
El **operador del programa destino** acepta o rechaza manualmente. No hay aceptación automática.

#### Notificaciones
- **Operador destino:** recibe badge + alerta en bandeja cuando llega una derivación nueva
- **Ciudadano:** no recibe notificación activa. Lo puede ver en su portal, sección Programas

#### Reglas de validación (se verifican antes de crear la derivación)
- ✅ Se puede derivar si la derivación anterior al mismo programa fue RECHAZADA (o el flujo fue rechazado)
- ❌ No se puede derivar si ya existe una derivación PENDIENTE al mismo programa → aviso al operador
- ❌ No se puede derivar si el ciudadano ya está ACTIVO en ese programa → aviso al operador
- ✅ Un ciudadano puede tener derivaciones PENDIENTE a **distintos programas** simultáneamente

#### Ciclo de vida completo
```
[Operador crea derivación — desde perfil ciudadano o desde dashboard de programa]
        ↓
  Derivacion → PENDIENTE
  Operador del programa destino recibe badge + alerta en bandeja
        ↓
  [RECHAZA] → Derivacion = RECHAZADA
              InscripcionPrograma NO se crea
  [ACEPTA]  → Derivacion = ACEPTADA
              InscripcionPrograma creado (estado PENDIENTE)
                    ↓
              Flujo inicia (InstanciaFlujo creada)
                    ↓
              [Si el flujo tiene paso "rechazar" configurado y se rechaza]
              → InstanciaFlujo = RECHAZADO
              → InscripcionPrograma = INACTIVO
              [Si el flujo completa sin rechazo]
              → InscripcionPrograma = ACTIVO
                    ↓
              Cierre automático (un solo acto) | Baja manual (persistente)
```

#### Puntos de entrada en la UI
| Desde | Quién | Comportamiento |
|-------|-------|----------------|
| Perfil del ciudadano `/legajos/ciudadanos/<id>/` | Cualquier operador | Elige destino (programa/institución/actividad) libremente |
| Dashboard del programa | Gestor del programa | Busca ciudadano; origen queda registrado automáticamente como el programa actual |

### Programas sociales
- Catálogo unificado: sirve tanto para ciudadanos como para instituciones
- Todo programa pertenece a una jerarquía organizacional: **Secretaría → Subsecretaría → Programa** (exactamente dos niveles)
- Todo programa tiene un flujo configurable — sin excepción
- Solo usuarios con el rol **`ConfiguracionPrograma`** pueden crear y configurar programas

#### Estados del modelo Programa

```
BORRADOR → ACTIVO → SUSPENDIDO → INACTIVO
```

| Estado | Acepta nuevos ingresos | Inscripciones en curso | Descripción |
|--------|----------------------|----------------------|-------------|
| `BORRADOR` | ❌ | ❌ | Sin flujo configurado |
| `ACTIVO` | ✅ | ✅ | Operativo |
| `SUSPENDIDO` | ❌ | ✅ continúan | Cerrado a nuevos ingresos, los existentes siguen su flujo |
| `INACTIVO` | ❌ | ❌ | Programa cerrado completamente |

#### Naturaleza de un programa
Los programas tienen dos naturalezas con distinto ciclo de vida post-flujo:

| | Un solo acto | Persistente |
|--|--|--|
| Tiene flujo | ✅ | ✅ |
| Post-flujo | Cerrado automáticamente | Sigue abierto hasta baja manual |
| Alimentación continua | ❌ | ✅ según lo que configure el flujo |
| Puede tener turnos | ✅ (activable) | ✅ (activable) |

- **Un solo acto**: el ciudadano atraviesa el flujo completo, se aprueba o no, y el caso cierra automáticamente
- **Persistente**: el ciudadano entra al programa, traversa el flujo, y **permanece activo** hasta que un operador registra la baja. Durante ese tiempo el flujo puede seguir alimentando información

#### Turnos en programas
- **Ambos tipos** de programa pueden tener turnos configurados — la distinción un solo acto / persistente no afecta esta capacidad
- La activación de turnos depende exclusivamente de si el programa tiene `tiene_turnos = True` en su configuración

#### Cupos y lista de espera en programas
- Un programa puede tener **cupo máximo** configurado (cantidad de inscripciones activas simultáneas)
- Si el programa tiene cupo y está lleno, los nuevos ingresos entran a una **lista de espera**
- La lista de espera es opcional — se configura junto con el cupo en la configuración del programa
- Si no tiene cupo configurado, el programa acepta ingresos sin límite

#### Puntos de entrada de un ciudadano a un programa
Hay dos caminos para que un ciudadano ingrese a un programa. Son la **misma acción** con la misma estructura de datos — la diferencia es solo de permiso y punto de origen:

| Camino | Quién lo hace | `tipo_inicio` |
|--------|--------------|-----------|
| **Derivación** | Cualquier operador del backoffice | `DERIVACION` |
| **Inscripción directa** | Solo gestores del programa destino | `INSCRIPCION_DIRECTA` |

**Regla absoluta:** en ambos casos el ciudadano SIEMPRE debe completar el flujo completo. No existe aprobación automática ni salto de pasos.

#### Momento de creación de InscripcionPrograma
`InscripcionPrograma` se crea **al momento de ACEPTAR la derivación** (no al completar el flujo). El flujo corre sobre una inscripción ya existente en estado PENDIENTE.

#### Estados de un ciudadano en un programa — dos capas
1. **Estado general** (de la inscripción): `ACTIVO` / `INACTIVO` / `DADO_DE_BAJA`
2. **Estado del paso actual** (de la instancia de flujo): nombre configurable por el administrador del flujo al definir cada paso — ejemplo: "En evaluación", "En seguimiento", "Pendiente de documentación"

#### Roles dentro de un programa
- Cada paso del flujo tiene un **rol asignado** — solo operadores con ese rol pueden ejecutar ese paso
- Los roles son específicos del programa — cada programa define qué roles existen y qué pasos gestionan
- Ejemplo: paso 1 "Aceptar derivación" → rol `mda` del programa; paso 2 → mismo u otro rol

#### Flujos de programas
- El flujo define completamente el comportamiento del programa: pasos, formularios, evaluaciones, tareas territoriales, roles por paso
- Las **tareas territoriales** son un tipo de nodo dentro del flujo (formulario que se completa en app móvil y vuelve vinculado al ciudadano/caso)
- El motor de flujos se adapta del sistema NODO (backend Django, editor visual React — pendiente de implementación)

### Roles y permisos del sistema

Todos los roles son grupos Django independientes — no existe jerarquía entre ellos. Un usuario puede tener múltiples roles simultáneamente. El Administrador (`is_staff`) puede asignar y quitar roles en cualquier momento.

#### Mapa completo de roles

| Módulo | Rol | Qué permite |
|--------|-----|------------|
| **Ciudadanos** | `ciudadanoVer` | Ver ficha del ciudadano (sin campos sensibles) |
| | `ciudadanoCrear` | Crear y editar ciudadanos |
| | `ciudadanoSensible` | Ver campos de salud, documentación migratoria y campos marcados como sensibles |
| **Instituciones** | `institucionVer` | Ver el catálogo de instituciones y sus datos |
| | `institucionAdministrar` | Crear, editar, aprobar/rechazar instituciones |
| **Programas — configuración** | `secretariaConfigurar` | Crear y editar Secretarías y Subsecretarías |
| | `programaConfigurar` | Crear y configurar programas (wizard, flujo, capacidades) |
| **Programas — operativa** | `programaOperar` | Gestionar inscripciones, derivaciones, seguimiento de ciudadanos en programas |
| **Turnos — configuración** | `turnoConfigurar` | Crear y configurar `ConfiguracionTurnos` (horarios, modos, disponibilidades) |
| **Turnos — operativa** | `turnoOperar` | Gestionar agenda: confirmar, rechazar, cancelar turnos de ciudadanos |
| **Conversaciones** | `conversacionOperar` | Acceder a la bandeja de conversaciones, responder ciudadanos via chat |
| **Dashboard** | `dashboardVer` | Ver el panel de control con métricas e indicadores |
| **Configuración sistema** | `sistemaConfigurar` | Gestionar parámetros globales (email, integraciones, etc.) |
| **Usuarios y roles** | `usuarioAdministrar` | Crear usuarios, asignar y revocar roles |
| **Reportes** | `reportesVer` | Ver y exportar reportes del sistema |

#### Roles especiales (no son grupos Django)

| Rol especial | Naturaleza | Qué permite |
|-------------|-----------|------------|
| `is_superuser` | Flag Django | Acceso total sin restricciones — solo para DevOps/soporte técnico |
| `Ciudadanos` (grupo portal) | Grupo Django | Identifica a los usuarios del portal ciudadano — no acceden al backoffice |
| `EncargadoInstitucion` | Grupo Django | Usuario externo representante de una ONG/organismo — acceso limitado a su institución |

#### Roles renombrados respecto al código existente

| Nombre viejo (en código) | Nombre nuevo (acordado) | Módulo |
|--------------------------|------------------------|--------|
| `configurarSecretaria` | `secretariaConfigurar` | Programas — configuración |
| `ConfiguracionPrograma` | `programaConfigurar` | Programas — configuración |
| `Administradores de Turnos` | `turnoConfigurar` | Turnos — configuración |

> **Nota técnica:** los nombres viejos están en el código actualmente. La migración de nombres se hace como parte de US-011 (data migration de grupos Django).

#### Reglas de acceso

- Un usuario sin ningún rol en el backoffice no puede acceder a ninguna sección
- El portal ciudadano es completamente separado — los usuarios del portal pertenecen al grupo `Ciudadanos`
- `EncargadoInstitucion` accede solo a la vista de su institución — no al backoffice general
- `is_superuser` no es un rol operativo, solo para mantenimiento técnico

---

### Turnos
- Los turnos son configurables por entidad (Programa, Institución, Actividad)
- `ConfiguracionTurnos` es el modelo nuevo (v2). `RecursoTurnos` es legacy (v1) — coexisten
- Modos: AUTO (ciudadano elige), MANUAL (operador asigna), AMBOS
- Cuando `requiere_aprobacion=True` el turno nace en estado PENDIENTE
- Cuando `requiere_aprobacion=False` el turno nace directamente en CONFIRMADO
- Un turno cancelado por el sistema notifica al ciudadano por email (best-effort)

### Portal ciudadano
El portal es la superficie pública para el ciudadano. Está completamente separado del backoffice via middleware. Lo que el ciudadano puede hacer:

| Funcionalidad | Estado |
|--------------|--------|
| Registro y login con email/password | ✅ Implementado (iteración 1) |
| Ver su perfil y datos del legajo | ✅ Implementado (iteración 1) |
| Ver sus programas y estado en cada uno | 🟡 Pendiente (iteración 2) |
| Inscribirse a un programa | 🟡 Pendiente (iteración 2) |
| Solicitar turno online | 🟡 Pendiente (iteración 6) |
| Iniciar chat con un operador | 🟡 Pendiente (iteración 3) |
| Ver sus documentos | 🟡 Pendiente (iteración 4) |
| Recibir notificaciones | 🟡 Pendiente (iteración 5) |

### Conversaciones
- Un ciudadano puede iniciar una conversación desde el portal
- El sistema intenta asignación automática a un operador
- Las conversaciones tienen WebSocket en tiempo real
- Estados: activa → cerrada

### Trazabilidad y auditoría
- **Todo el sistema es trazable** — cada acción queda registrada: quién configuró, quién cambió estado, quién aceptó una derivación, quién dio de baja, qué hizo el ciudadano en el portal
- La auditoría clínica (`AuditoriaEvaluacion`, `AuditoriaCiudadano`) existe y funciona para el módulo SEDRONAR
- La trazabilidad general del sistema (inscripciones, cambios de estado de programas, turnos, derivaciones) debe extenderse al resto de los módulos como parte del diseño de cada feature

#### Baja manual de un ciudadano en un programa persistente
- Se ejecuta mediante un botón explícito desde la vista del ciudadano en el programa
- Registra: quién dio la baja, fecha y hora, motivo (campo obligatorio)
- Al dar la baja: la inscripción pasa a `DADO_DE_BAJA`, el flujo activo se suspende, los turnos pendientes se cancelan
- Solo pueden dar de baja operadores con el rol correspondiente al programa

### ÑACHEC
- Es un programa específico con su propio modelo de legajo (`CasoNachec`)
- Tiene lógica de evaluación de vulnerabilidad propia
- Se gestiona separado del legajo de atención estándar

---

## Preguntas abiertas sin resolver

> El Analista Funcional debe responder estas preguntas ANTES de diseñar features relacionadas.

- [ ] ¿Un turno puede reprogramarse o solo cancelarse y crear uno nuevo?
- [ ] ¿Qué pasa con los turnos si se desactiva una institución? ¿Se cancelan en cascada?
- ~~¿El ciudadano recibe notificación cuando es derivado a otro programa?~~ → Resuelto: no recibe notificación activa, lo ve en su portal sección Programas
- ~~¿Los operadores pueden ver legajos de cualquier ciudadano o solo los asignados a su institución?~~ → Resuelto: depende del ámbito (institución vs. programa)
- [ ] ¿Existe un concepto de "guardia" o atención urgente fuera del sistema de turnos?
- [ ] ¿El operador que marca un campo de ciudadano como "sensible" puede también desmarcarlo, o requiere un rol especial?
- [ ] ¿La foto del ciudadano requiere `ciudadanoSensible` o la ve cualquiera con `ciudadanoVer`?
- [ ] ¿Qué muestra exactamente la solapa "Resumen" del hub ciudadano?
- [ ] ¿El toggle "requiere turno" en un programa persistente — lo activa solo `ConfiguracionPrograma` o también el Operador?
- ~~¿Las actividades son parte de un programa o son entidades independientes?~~ → Resuelto: siempre pertenecen a una institución. Tienen tipo de acceso LIBRE o REQUIERE_PROGRAMA.
- ~~¿La asignación de profesionales a actividades — es uno por muchos?~~ → Resuelto: muchos (StaffActividad con rol_en_actividad)

---

## Lo que el usuario NO pidió pero podría necesitar

> El Analista debe tener esto en mente para proponer mejoras en el momento oportuno.

- Recordatorios automáticos 24hs antes de un turno (Celery/cron — deuda pendiente)
- Notificaciones push / WhatsApp (no solo email)
- Vista mensual de agenda de turnos (hoy solo hay vista diaria)
- Exportación a PDF del legajo de atención
- Estadísticas de asistencia a turnos (ausentismo)
- Integración con sistema de expedientes municipales

## Tareas técnicas futuras documentadas

> Existen como componentes del sistema pero requieren /definir y documentación formal antes de implementar.

- **App móvil** — existe y recibe tareas territoriales completadas por operadores de campo. Devuelve formularios al sistema. Requiere documentar: cómo se conecta (API REST), autenticación, gestión de usuarios propios. Pendiente de `/definir app-movil`.
- **Sistema de alertas** — `AlertaEventoCritico` existe en `LegajoAtencion` pero el sistema de alertas general no está definido. Qué las genera (turno faltado, inscripción vencida, derivación sin respuesta, evento clínico), quién las recibe, cómo se marcan como leídas. Pendiente de `/definir alertas`.

---

## Contexto de sesiones anteriores

> El Analista actualiza esta sección al final de cada sesión importante.

### 2026-03-09 (sesión 1)
- Se diseñó e implementó el sistema de turnos configurables (backoffice completo)
- Se definió que los turnos pueden originarse desde: portal genérico, programa, institución, actividad, derivación, legajo de atención, backoffice por teléfono
- Se aprobó la coexistencia de `RecursoTurnos` (legacy) y `ConfiguracionTurnos` (nuevo)
- Se creó la app `turnos/` separada de `portal/` por razones de separación de responsabilidades
- Se documentaron 17 funcionalidades del sistema en `docs/funcionalidades/`
- Se agregó la burbuja de mejora automática al CLAUDE.md

### 2026-03-13
- Se ejecutó el primer slice del refactor interno de DX sobre `users`, `portal` institucional y `turnos`
- El registro institucional público dejó de depender de FBVs con POST raw y se migró a `FormView` + services/selectors
- La administración de usuarios movió persistencia de grupos y `Profile` fuera de los forms
- El backoffice de turnos separó lecturas reutilizables (`selectors_turnos`) y acciones de negocio (`services_turnos`)
- No se modificaron reglas de negocio ni modelos; el objetivo fue reducir acoplamiento y preparar una base más testeable para siguientes features
- Se ejecutó el segundo slice del refactor DX sobre `configuracion`, focalizado en detalle institucional, detalle de actividad, staff, derivaciones e inscriptos
- Los flujos operativos del módulo dejaron de depender de `POST` raw en las pantallas principales y pasaron a forms explícitos más services transaccionales
- No se alteraron reglas de negocio institucionales ni estados funcionales; el cambio fue estructural para mejorar mantenibilidad y testabilidad
- Se ejecutó el tercer slice del refactor DX sobre `legajos`, acotado a ciudadanos y admisión
- El flujo de RENAPER y el wizard de admisión dejaron de repartir manejo de sesión y orquestación en múltiples views
- La carga manual del ciudadano quedó separada del formulario de confirmación RENAPER, corrigiendo una inconsistencia de UI con el campo DNI
- Se ejecutó el cuarto slice del refactor DX sobre `legajos`, enfocado en legajo de atención, evaluación, planes, seguimientos, derivaciones y cierre/reapertura
- La edición del plan de intervención dejó de depender de inputs hardcodeados que ignoraban los datos existentes
- Las acciones clínicas base del legajo ahora comparten services/selectors reutilizables y forms más acotados a validación/mapeo
- Se ejecutó el quinto slice del refactor DX sobre `legajos`, enfocado en eventos críticos, reportes, exportación y cambio de responsable
- Los templates clínicos dejaron de referenciar campos inexistentes del dominio y ahora reflejan la estructura real de los modelos
- Reportes y acciones AJAX del módulo ya no concentran orquestación inline en `views.py`
- Se ejecutó el sexto slice del refactor DX sobre `legajos`, enfocado en separar físicamente las views por dominios
- `legajos/views.py` quedó como fachada compatible y el código se repartió entre `views_ciudadanos.py` y `views_clinico.py`
- El cambio no altera rutas ni comportamiento funcional, pero reduce fricción para futuros refactors y tests del módulo
- Se ejecutó el séptimo slice del refactor DX sobre `legajos`, enfocado en completar la modularización física de las views
- La operativa institucional y de actividades pasó a `views_operativa.py` y `legajos/views.py` quedó como fachada pura de compatibilidad
- El cambio tampoco altera reglas funcionales ni rutas, pero deja el módulo listo para seguir atacando deuda por subdominio en lugar de por archivo monolítico
- Se ejecutó el octavo slice del refactor DX sobre `conversaciones`, enfocado en separar chat público, backoffice, métricas y orquestación
- El módulo dejó de concentrar parsing manual de payloads y queries repetidas en un solo `views.py`; ahora usa selectors, services y forms livianos sin cambiar las URLs
- Se mantuvo explícitamente el contrato actual del chat y los endpoints AJAX/WebSocket legacy para no introducir regresiones funcionales en el frontend
- Se ejecutó el noveno slice del refactor DX sobre `conversaciones`, enfocado en alinear la API auxiliar de alertas y detalle en vivo
- Las APIs internas del chat ya no repiten permisos, queries ni marcado de mensajes leídos por fuera de la nueva capa del módulo
- El comportamiento visible no cambió; el beneficio fue coherencia interna y menor costo de mantenimiento
- Se ejecutó el décimo slice del refactor DX sobre `configuracion`, enfocado en modularización física de las views
- La app dejó de concentrar geografía, institucional y actividades en un solo `views.py`; ahora usa módulos por dominio con una fachada compatible
- Tampoco hubo cambios funcionales visibles; el valor del corte fue bajar el costo cognitivo y alinear la estructura interna con el resto del refactor
- Se ejecutó el undécimo slice del refactor DX sobre URLs y namespaces raíz del proyecto
- `users`, `core` y `healthcheck` ya exponen namespaces consistentes sin retirar todavía los names legacy
- El cambio fue deliberadamente incremental para evitar una rotura transversal en templates y `reverse()`
- Se ejecutó el duodécimo slice del refactor DX sobre consumidores de URLs
- Varias pantallas internas ya consumen `core:*` y `users:*` en lugar de names legacy sin namespace
- Se dejó autenticación fuera de este corte porque `login/logout` requieren una decisión más cuidadosa por convivencia con Django auth
- Se ejecutó el decimotercer slice del refactor DX sobre `chatbot`
- El módulo ya no mezcla chat de usuario y panel administrativo en un solo `views.py`, y valida payloads JSON con forms livianos
- El comportamiento visible no cambió; el objetivo fue bajar acoplamiento y preparar mejor base para futuras mejoras del bot
- Se ejecutó el decimocuarto slice del refactor DX sobre `chatbot`, enfocado en alinear el contrato real entre frontend y backend
- El chat del bot ya no depende de rutas hardcodeadas inconsistentes ni de `@csrf_exempt` en sus endpoints principales
- Además se agregaron tests para cubrir el shape de respuesta esperado por el frontend y el enforcement de CSRF
- Se ejecutó el decimoquinto slice del refactor DX sobre `conversaciones`, enfocado en el contrato real del chat ciudadano y operador
- La evaluación del ciudadano volvió al dominio público real de la funcionalidad y dejó de chocar con una vista protegida de backoffice
- Los POST JSON del chat ya no dependen de `@csrf_exempt`; ahora usan URLs renderizadas por Django y cabecera CSRF explícita
- Se ejecutó el decimosexto slice del refactor DX sobre `conversaciones`, enfocado en la lista en vivo del backoffice
- La pantalla dejó de cargar dos veces el runtime WebSocket de lista y ya no depende de URLs hardcodeadas para refrescar detalle/cierre
- El comportamiento visible no cambió, pero baja el riesgo de conexiones duplicadas y facilita la migración de rutas
- Se ejecutó el decimoséptimo slice del refactor DX sobre `conversaciones`, enfocado en consumidores residuales del módulo fuera de su lista principal
- Los scripts globales de alertas/estadísticas y algunos consumidores en portal/backoffice ya no embeben rutas de `conversaciones` en archivos estáticos
- El comportamiento visible tampoco cambió, pero el módulo quedó más coherente transversalmente y con menos acoplamiento a paths fijos
- Se ejecutó el decimoctavo slice del refactor DX sobre `portal`, enfocado en consultas ciudadanas
- La parte de consultas salió de `portal/views_ciudadano.py` y ahora usa forms, selectors y services dedicados
- El flujo visible no cambió, pero ahora valida mejor los POST, fija ownership de conversaciones en un único lugar y suma tests del dominio
- Se ejecutó el decimonoveno slice del refactor DX sobre `portal`, enfocado en turnos ciudadanos
- La parte de turnos salió de `portal/views_ciudadano.py` y ahora usa forms, selectors y services dedicados
- El flujo visible no cambió, pero ahora valida la confirmación con formularios Django y encapsula disponibilidad, reserva y cancelación en una capa reutilizable
- Se ejecutó el vigésimo slice del refactor DX sobre `portal`, enfocado en autenticación y registro ciudadano
- El login y el alta por pasos ya no viven dentro de `portal/views_ciudadano.py`; ahora usan un módulo de vistas propio y un service de auth/registro
- El comportamiento visible no cambió, pero quedó aislada la lógica de throttling por IP, sesión de registro y creación/vinculación de cuentas ciudadanas
- Se ejecutó el vigésimo primer slice del refactor DX sobre `portal`, enfocado en perfil, programas y mis datos
- El resto del perfil ciudadano salió de `portal/views_ciudadano.py` y ahora vive en `views_ciudadano_perfil.py`, con selectors y services propios
- El comportamiento visible no cambió, pero el archivo histórico del portal ciudadano quedó reducido a una fachada de compatibilidad
- Se ejecutó el vigésimo segundo slice del refactor DX sobre `ÑACHEC`, enfocado en prestaciones, cierre/reapertura y dashboard
- `legajos/views_nachec.py` dejó de concentrar esos bloques y ahora funciona parcialmente como fachada compatible
- El comportamiento visible no cambió, pero el hotspot principal del módulo bajó de tamaño antes de entrar en validación, relevamiento y evaluación
- Se ejecutó el vigésimo tercer slice del refactor DX sobre `ÑACHEC`, enfocado en evaluación y activación de plan
- La evaluación profesional, la ampliación/rechazo y la activación del plan ahora viven en `views_nachec_decisiones.py`
- El comportamiento visible no cambió, pero `legajos/views_nachec.py` quedó por debajo de las 1000 líneas antes de atacar asignación y relevamiento
- Se ejecutó el vigésimo cuarto slice del refactor DX sobre `ÑACHEC`, enfocado en la operación territorial restante
- Validación, asignación, reasignación, relevamiento y evidencias ahora viven en `views_nachec_operacion.py`
- El comportamiento visible no cambió, pero `legajos/views_nachec.py` quedó finalmente como fachada pura y el hotspot principal de `ÑACHEC` dejó de concentrar la implementación real
- Se ejecutó el vigésimo quinto slice del refactor DX sobre `legajos`, enfocado en cleanup de formularios
- `legajos/forms.py` dejó de concentrar ciudadanía, clínica y operativa en un solo archivo; ahora funciona como fachada compatible hacia módulos por dominio
- El comportamiento visible no cambió, pero se alineó la estructura de forms con las views ya modularizadas y bajó el costo cognitivo del módulo
- Se ejecutó el vigésimo sexto slice del refactor DX sobre `turnos`, enfocado en el backoffice
- El backoffice dejó de concentrar dashboard, configuración, disponibilidad, agenda y acciones en un solo `views_backoffice.py`; ahora usa módulos dedicados y CBVs en el CRUD repetible
- El comportamiento visible no cambió, pero la app ganó mixins de permisos reutilizables y una estructura más coherente con el resto del refactor
- Se ejecutó el vigésimo séptimo slice del refactor DX sobre `contactos`
- El módulo legacy de contactos dejó de mezclar panel, APIs, queries pesadas y uploads en un solo archivo; ahora usa selectors, un service de adjuntos y una fachada compatible
- El comportamiento visible no cambió salvo correcciones necesarias para alinearlo con el modelo real, eliminando referencias a campos inexistentes dentro de ese módulo
- Se ejecutó el vigésimo octavo slice del refactor DX sobre consumidores transversales de rutas
- El logout del backoffice, el bubble de chatbot y el dashboard de alertas ya consumen namespaces/rutas renderizadas por Django en lugar de paths hardcodeados
- El comportamiento visible no cambió, pero la base quedó más preparada para cerrar la migración de URLs y namespaces sin roturas silenciosas
- Se ejecutó el vigésimo noveno slice del refactor DX sobre `legajos/urls.py`
- Las rutas de cierre de alertas dejaron de compartir el mismo `name=` y ahora distinguen explícitamente entre evento crítico y alerta de ciudadano
- El comportamiento visible no cambió, pero el routing de `legajos` quedó menos ambiguo y más seguro para futuros refactors
- Se ejecutó el trigésimo slice del refactor DX sobre `users`
- El service que alimenta la tabla/listado de usuarios dejó de publicar URLs legacy y ahora expone acciones y reverses con namespace explícito
- El comportamiento visible no cambió, pero el contrato interno del módulo quedó más coherente con la estandarización de rutas del proyecto
- Se ejecutó el trigésimo primer slice del refactor DX sobre `turnos` y `users`
- Ambas apps dejaron de depender de módulos raíz únicos para views/services/selectors y ahora exponen paquetes reales con fachadas compatibles
- El comportamiento visible no cambió, pero la cartografía interna del proyecto quedó más predecible para futuros slices de modularización física
- Se ejecutó el trigésimo segundo slice del refactor DX sobre `chatbot`
- La app ahora agrupa views, forms, services y selectors en paquetes reales, manteniendo compatibilidad con los módulos legacy y con los tests existentes
- El comportamiento visible no cambió, pero el módulo quedó listo para seguir la misma estrategia de packaging en otras apps ya modularizadas
- Se ejecutó el trigésimo tercer slice del refactor DX sobre `configuracion`
- La app ahora agrupa views, forms, services y selectors en paquetes reales, manteniendo wrappers de compatibilidad para las entradas legacy por dominio
- El comportamiento visible no cambió, pero el módulo quedó alineado con el patrón de packaging ya aplicado en `turnos`, `users` y `chatbot`
- Se ejecutó el trigésimo cuarto slice del refactor DX sobre `portal`
- La app ahora agrupa views, forms, services y selectors en paquetes reales tanto para registro institucional como para los subdominios ciudadanos
- El comportamiento visible no cambió, pero los tests del portal ya apuntan a los paths reales del paquete y no a wrappers históricos
- Se ejecutó el trigésimo quinto slice del refactor DX sobre `conversaciones`
- La app ahora agrupa views, forms, services, selectors y signals en paquetes reales, manteniendo compatibilidad con rutas e imports legacy del módulo
- Además se corrigió una inconsistencia real de inicialización: `ConversacionesConfig` tenía dos `ready()` y solo uno se ejecutaba
- Se ejecutó el trigésimo sexto slice del refactor DX sobre `core`
- La app ahora agrupa views, forms y selectors del flujo principal en paquetes reales, sin tocar todavía la auditoría pesada ni sus signals
- El comportamiento visible no cambió, pero la capa compartida del proyecto quedó más consistente con el packaging del resto de apps
- Se ejecutó el trigésimo séptimo slice del refactor DX sobre `legajos`
- La app ahora agrupa `services` y `selectors` reales para ciudadanía, admisión, legajos, contactos y solapas, manteniendo wrappers de compatibilidad para imports legacy
- El comportamiento visible no cambió, pero el núcleo reutilizable del dominio quedó alineado con el packaging ya aplicado en el resto del proyecto
- Se ejecutó el trigésimo octavo slice del refactor DX sobre `legajos`
- La app ahora agrupa también `forms` reales por dominio, manteniendo wrappers compatibles para los módulos históricos
- El comportamiento visible no cambió, pero la capa de formularios dejó de depender solo de módulos planos y quedó alineada con el packaging de services/selectors
- Se ejecutó el trigésimo noveno slice del refactor DX sobre `legajos`
- El bloque auxiliar de contactos y dashboards simples ahora vive en `legajos/views/`, manteniendo wrappers de compatibilidad para rutas e imports legacy
- El comportamiento visible no cambió, pero la migración de views de la app ya empezó por la superficie menos sensible
- Se ejecutó el cuadragésimo slice del refactor DX sobre `legajos`
- Alertas, cursos, derivación simple, API de derivaciones y acompañamiento ahora viven también en `legajos/views/`, con wrappers de compatibilidad
- El comportamiento visible no cambió, pero otra capa de soporte salió de módulos planos legacy antes de entrar en áreas más sensibles
- Se ejecutó el cuadragésimo primer slice del refactor DX sobre `legajos`
- `views_operativa.py` ahora vive también dentro de `legajos/views/`, con wrapper legacy compatible
- El comportamiento visible no cambió, pero el margen de slices baratos en `legajos` quedó prácticamente agotado
- Se ejecutó el cuadragésimo segundo slice del refactor DX sobre `legajos`
- `views_programas.py` y `views_solapas.py` ahora viven también dentro de `legajos/views/`, con wrappers legacy compatibles
- El comportamiento visible no cambió, pero lo pendiente en `legajos` ya quedó casi exclusivamente en bloques muy sensibles del dominio
- Se ejecutó el cuadragésimo tercer slice del refactor DX sobre `legajos`
- La lógica de aceptación/rechazo de derivaciones de programa y el branch especial de `ÑACHEC` salió de `views_derivacion_programa.py` a un service dedicado
- El comportamiento visible no cambió, pero el borde entre programas y `ÑACHEC` quedó más testeable y listo para un corte físico posterior
- Se ejecutó el cuadragésimo cuarto slice del refactor DX sobre `legajos`
- `views_derivacion_programa.py` ahora vive dentro de `legajos/views/`, con wrapper legacy compatible
- El comportamiento visible no cambió, y ya casi no quedan views movibles sin entrar en dominios bastante más sensibles
- Se ejecutó el cuadragésimo quinto slice del refactor DX sobre `legajos`
- `views_institucional.py` ahora vive dentro de `legajos/views/`, con wrapper legacy compatible
- El comportamiento visible no cambió, pero la superficie institucional ya quedó alineada con el paquete nuevo sin tocar todavía sus reglas internas
- Se ejecutó el cuadragésimo sexto slice del refactor DX sobre `legajos`
- `views_clinico.py` ahora vive dentro de `legajos/views/`, con wrapper legacy compatible
- El comportamiento visible no cambió, y el frente pendiente en `legajos` quedó todavía más concentrado en la familia `ÑACHEC`
- Se ejecutó el cuadragésimo séptimo slice del refactor DX sobre `legajos`
- La familia `views_nachec_*` ahora vive dentro de `legajos/views/`, con wrappers legacy compatibles
- El comportamiento visible no cambió, y el packaging estructural de `legajos` quedó prácticamente completo
- Se ejecutó el cuadragésimo octavo slice del refactor DX sobre `legajos`
- La familia restante de servicios (`alertas`, `filtros_usuario`, `institucional`, `nachec`) ahora vive dentro de `legajos/services/`, con wrappers legacy compatibles
- El comportamiento visible no cambió, y el siguiente frente estructural quedó concentrado en `signals`
- Se ejecutó el cuadragésimo noveno slice del refactor DX sobre `legajos`
- La familia de señales ahora vive dentro de `legajos/signals/`, con `ready()` explícito y wrappers legacy secundarios donde todavía tenían valor
- El comportamiento visible no cambió, y el packaging estructural de `legajos` quedó prácticamente agotado
- Se ejecutó el quincuagésimo slice del refactor DX sobre apps chicas
- `dashboard`, `tramites` y `healthcheck` ahora siguen también la convención de packaging por carpeta
- El comportamiento visible no cambió, y la deuda estructural restante quedó mucho más concentrada en hotspots funcionales
- Se ejecutó el quincuagésimo primer slice del refactor DX sobre `core`
- Auditoría, performance y señales de `core` ahora viven también dentro de paquetes reales, con `ready()` explícito
- El comportamiento visible no cambió, y el refactor estructural repo-wide quedó prácticamente agotado
- Se ejecutó el quincuagésimo segundo slice del refactor DX sobre APIs chicas
- `dashboard`, `users` y `chatbot` ahora también agrupan sus `api_views` en paquetes reales
- El comportamiento visible no cambió, y la deuda estructural restante quedó todavía más concentrada en APIs más sensibles o deuda funcional
- Se ejecutó el quincuagésimo tercer slice del refactor DX sobre APIs compartidas
- `core` y `conversaciones` ahora también agrupan sus `api_views` en paquetes reales
- El comportamiento visible no cambió, y la deuda estructural restante quedó casi totalmente reducida a `legajos` o deuda funcional
- Se ejecutó el quincuagésimo cuarto slice del refactor DX sobre `legajos`
- `legajos` ahora también agrupa sus `api_views` en paquetes reales, incluyendo contactos
- El comportamiento visible no cambió, y la deuda estructural repo-wide quedó prácticamente agotada
- Se ejecutó el quincuagésimo quinto slice del refactor DX sobre `ÑACHEC`
- El subflujo inicial de operación (`validación`, `envío a asignación`, `asignación territorial`) ahora vive en service layer reutilizable
- Se corrigió una inconsistencia real de tareas de coordinación sin cambiar el flujo visible para el usuario final
- Se ejecutó el quincuagésimo sexto slice del refactor DX sobre `ÑACHEC`
- La reasignación territorial y el inicio de relevamiento ahora viven también en service layer reutilizable
- El comportamiento visible no cambió, pero la view dejó de orquestar transacciones e historial en esos subflujos
- Se ejecutó el quincuagésimo séptimo slice del refactor DX sobre organización física repo-wide
- `users/forms.py`, `turnos/forms.py` y `core/services_auditoria.py` ya no viven como archivos sueltos en raíz de app
- El comportamiento visible no cambió y la cartografía física del repo quedó todavía más consistente
- Se ejecutó el quincuagésimo octavo slice del refactor DX sobre `legajos`
- `legajos` ya no depende de wrappers legacy en raíz y consume directamente sus paquetes reales de `views`, `forms`, `services`, `selectors` y `signals`
- El comportamiento visible no cambió y la cartografía final de la app quedó alineada con el resto del repo

### 2026-03-19 (sesión 7)
- Se implementó US-022: inscripción de ciudadanos a actividades institucionales
- `InscriptoActividad` extendido con `codigo_inscripcion` (8 chars único) e `inscrito_por`; se eliminó `unique_together` para soportar reinscripciones históricas
- Service central `inscribir_ciudadano_a_actividad` con `@transaction.atomic + select_for_update` para evitar race conditions
- `aceptar_derivacion` en `configuracion/services` refactorizado para usar el service central en lugar de `get_or_create` directo
- Vista de inscripción directa desde backoffice (búsqueda por DNI) y desde portal ciudadano
- Bug corregido: cupo=0 en `PlanFortalecimiento` ahora se trata correctamente como "sin límite" en el template
- Reglas confirmadas: cupo=0 = ilimitado; reinscripción permitida tras ABANDONADO/FINALIZADO; código = 8 chars alfanuméricos

### 2026-03-19 (sesión 8)
- Se implementó US-008: perfil social ampliado del ciudadano
- 14 nuevos campos en `Ciudadano`: foto, habitacional (tipo, tenencia, condiciones), laboral (situación, ingreso, obra social), educativo (nivel), médico-sensible (cobertura, medicación), documentación (DNI físico, estado RENAPER, estado migratorio-sensible), observaciones
- Se estableció el patrón de tres capas para campos sensibles: form/view/template. La foto no es sensible.
- `CiudadanoUpdateForm` inyecta campos sensibles condicionalmente en `__init__`; `save()` los persiste solo si el flag es verdadero
- `build_ciudadano_detail_context` extendido para recibir `user` y calcular `puede_ver_sensible`
- `buscar_ciudadanos_rapido` ahora retorna `foto_url` para el buscador rápido
- 4 índices nuevos en `Ciudadano` para preparar filtros del hub (US-009)
- Migración `0034_ciudadano_campos_perfil_ampliado` creada y aplicada

### 2026-04-03 (sesión 9)
- Se simplificó el stack local Docker para que el flujo recomendado sea `docker compose up`
- El entorno local recomendado ahora levanta solo `app`, `mysql` y `redis`
- HTTP y WebSocket comparten un mismo proceso ASGI en el contenedor `app`
- El bootstrap diario queda reducido a migraciones y setup idempotente mínimo; los seeds demo o pesados salen del arranque automático

---

## Glosario del negocio

| Término | Definición |
|---------|-----------|
| **Ficha del ciudadano** | Perfil central del ciudadano con toda su información social — hub en `/legajos/ciudadanos/<id>/` |
| **Legajo de atención** | ⚠️ Entidad SEDRONAR-específica (deuda técnica). Seguimiento clínico-social — migrará al motor de flujos en el futuro |
| **Inscripción a programa** | Relación entre un ciudadano y un programa — el ciudadano "entra" al programa via `InscripcionPrograma` |
| **Derivación** | Transferencia de un ciudadano de un programa/institución a otro |
| **Inscripción** | Alta de un ciudadano en un programa social |
| **Recurso de turnos** | Entidad que ofrece slots de atención (legacy: `RecursoTurnos`) |
| **Configuración de turnos** | Nueva entidad configurable que reemplaza el recurso (v2) |
| **NODO** | Institución de la red SEDRONAR que funciona como punto territorial |
| **ÑACHEC** | Programa específico de la red con lógica de evaluación propia |
| **Backoffice** | Interfaz interna para operadores y profesionales (no pública) |
| **Portal ciudadano** | Interfaz pública para ciudadanos (`/portal/mi-perfil/`) |
| **Programa de un solo acto** | Programa cuyo ciclo de vida cierra automáticamente al completar el flujo |
| **Programa persistente** | Programa que permanece abierto por tiempo indefinido hasta baja manual explícita |
| **Tarea territorial** | Formulario asignado a un operador de campo, completado en app móvil, vinculado al ciudadano/caso |
| **Flujo de programa** | Secuencia de pasos configurables que define el comportamiento completo de un programa |
| **Secretaría / Subsecretaría** | Jerarquía organizacional a la que pertenece un programa (dos niveles fijos) |
| **programaConfigurar** | Rol (antes `ConfiguracionPrograma`) — permite crear y configurar programas |
| **secretariaConfigurar** | Rol (antes `configurarSecretaria`) — permite crear y editar Secretarías y Subsecretarías |
| **turnoConfigurar** | Rol (antes `Administradores de Turnos`) — permite configurar turnos |
| **programaOperar** | Rol — gestiona inscripciones, derivaciones y seguimiento en programas |
| **turnoOperar** | Rol — gestiona la agenda de turnos (confirmar, rechazar, cancelar) |
| **ciudadanoVer** | Rol que permite ver la ficha del ciudadano (sin campos sensibles) |
| **ciudadanoCrear** | Rol que permite crear y editar ciudadanos |
| **ciudadanoSensible** | Rol que permite acceder a campos de salud, documentación migratoria y campos sensibles |
| **Hub del ciudadano** | Perfil central del ciudadano con todas sus solapas — `/legajos/ciudadanos/<id>/` |
| **Campo sensible** | Campo de la ficha del ciudadano que requiere el rol `ciudadanoSensible` para ser visible |
| **LegajoAtencion** | Entidad clínico-social SEDRONAR-específica — deuda técnica planificada para migrar al motor de flujos |
