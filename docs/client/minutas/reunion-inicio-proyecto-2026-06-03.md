# :material-note-text-outline: Minuta de Reunión — Inicio de proyecto

!!! abstract "Reunión 1 — Inicio de proyecto"
    Reunión de arranque del proyecto entre el equipo ICORE y el Ministerio de Desarrollo de Chaco para definir el alcance inicial, la forma de trabajo y los próximos pasos.

---

## :material-information-outline: Metadatos

| Campo | Valor |
|---|---|
| :material-folder-outline: **Proyecto** | Chaco — Digitalización de procesos provinciales |
| :material-calendar-outline: **Fecha** | 2026-06-03 |
| :material-clock-outline: **Horario** | 15:00 a 16:00 hs |
| :material-video-outline: **Modalidad** | A confirmar |
| :material-account-edit-outline: **Redactada por** | Equipo ICORE |
| :material-package-variant-closed: **Versión** | [Versión 001](../versiones/version-001.md) |

---

## :material-account-group-outline: Participantes

| Nombre | Rol | Organización |
|---|---|---|
| Agostina Coppola | Analista Funcional y QA | ICORE |
| Matías Fariña | Project Manager (PM) | ICORE |
| Guido Cortiglia | Coordinador operativo | Ministerio de Desarrollo de Chaco |
| Walter Giordano | Referente de Tecnología y Sistemas | Ministerio de Desarrollo de Chaco |
| Claudia Miserachs | Consultora externa | Ministerio de Desarrollo de Chaco |

---

## :material-bullseye-arrow: Objetivo de la reunión

!!! quote ""
    Definir el alcance de la app para el relevamiento y aprobación de becas y programas asistenciales del Ministerio de Desarrollo Humano.

---

## :material-forum-outline: Temas tratados

### Objetivo funcional de la app

La app será utilizada por personal de campo para registrar personas interesadas en programas de becas y ayudas. Funcionará como herramienta de **captura de datos en territorio, validación y derivación**.

### Circuito acordado

1. Un operador releva los datos en territorio a través de la app.
2. Un responsable o administrador local o zonal revisa la carga, distribuye los equipos territoriales y asigna a cada operador una zona o actividad concreta, determinando la validación o el rechazo del registro.
3. Si se aprueba, la información se envía al sistema existente del Ministerio (SIS) para continuar el proceso e impactar el dato final.

### Alcance de la primera etapa

El objetivo inicial es capturar información y resolver la primera etapa del circuito. El seguimiento más avanzado de los beneficiarios queda para una segunda etapa.

### Alcance del proceso de becas e integración

- El proyecto abarca entre 6 y 7 programas asistenciales, cada uno con sus propias condiciones y reglas.
- El cupo no se consume al cargar la solicitud, sino cuando la persona es efectivamente aceptada.
- Se contempla una lista de espera o registro amplio de interesados.
- Algunos programas pueden exigir documentación adicional, como certificado de estudio, certificado de domicilio, fotos u otros comprobantes.
- Esa documentación deberá parametrizarse por programa.

### Lógica de integración entre sistemas

- El sistema de I-Core (NODO) actuará únicamente como capa de captura y validación previa.
- Luego enviará la información mediante un POST hacia el sistema existente del Ministerio (SIS).
- El SIS será el encargado de devolver el OK o el rechazo con su respectivo motivo.
- El SIS ejecutará los controles de elegibilidad, incluyendo validación de becas habilitadas, restricciones del programa, rechazos automáticos por beneficios incompatibles y derivaciones a asistentes sociales.
- La app deberá devolver esa respuesta de aprobación o rechazo con motivo para que el operador pueda informar al ciudadano.

### Arquitectura tecnológica y despliegue

- La app deberá poder trabajar sin conexión a internet en territorio.
- Se implementará un esquema con carga local o caché en el celular y sincronización posterior cuando vuelva la conexión.
- Para la autenticación se evaluaron dos opciones: TGD (Gobierno Digital) o una cuenta de Gmail.
- Para la salida inicial se priorizará la alternativa más rápida y simple.
- Se utilizará la integración existente con RENAPER, que funciona solo con conexión a internet.
- Si no hay conexión o cae el servicio, la app permitirá capturar datos mínimos en modo local: DNI, sexo, estado civil, fecha de nacimiento, domicilio completo, foto frente y dorso del DNI, y otros datos del servicio.
- La infraestructura será la provista por el cliente.
- Se recomendó AWS como alternativa práctica para salir rápido, utilizando S3 para archivos y Aurora para la base de datos.
- Se mantiene la posibilidad de migrar luego la infraestructura a entornos propios del Ministerio.
- En esta primera etapa se entregará un link directo para descargar el archivo APK.

---

## :material-handshake-outline: Acuerdos y decisiones tomadas

| # | Acuerdo | Responsable | Fecha límite |
|:-:|---|---|---|
| 1 | Enviar documentación formal de requerimientos para revisión | Ministerio | A definir |
| 2 | Enviar organigrama, decreto, flujo preliminar e información de contexto | Ministerio | A definir |
| 3 | Revisar la documentación y preparar una propuesta técnica y funcional | I-Core | A definir |
| 4 | Afinar autenticación, reglas de negocio, integración con SIS, documentación obligatoria por programa y modalidad de despliegue | Ambos equipos | A definir |

---

## :material-arrow-right-bold: Próximos pasos

- El Ministerio enviará la documentación formal y los documentos necesarios para la revisión.
- I-Core revisará la documentación recibida y preparará una propuesta técnica y funcional.
- Ambos equipos continuarán afinando autenticación, reglas de negocio, integración con sistemas existentes, documentación obligatoria por programa y modalidad de despliegue.

---

## :material-calendar-plus-outline: Próxima reunión

| Campo | Valor |
|---|---|
| :material-calendar-outline: **Fecha propuesta** | A coordinar |
| :material-bullseye-arrow: **Objetivo** | A definir |

---

!!! note "Minuta cerrada"
    Documento consolidado con los acuerdos confirmados en reunión. Los elementos que no quedaron definidos se mantienen como pendientes de confirmación.
