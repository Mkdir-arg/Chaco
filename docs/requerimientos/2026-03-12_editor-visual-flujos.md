---
name: Editor visual de flujos de programa (US-007)
description: Define el editor drag & drop en React para configurar visualmente el flujo paso a paso de cada programa social. Incluye decisiones de stack, tipos de nodo, persistencia y versionado.
type: requerimiento
---

# Editor visual de flujos de programa
> Estado: ABIERTO
> Fecha: 2026-03-12
> Prioridad: ALTA
> Tipo: FEATURE

## Dependencias
- **US-006** — Motor de flujos backend (app `flujos/`) debe existir primero
- **US-005** — Wizard de programa (el editor se accede desde el paso final del wizard)

## Concepto central

El flujo de un programa es un **grafo dirigido** de nodos conectados por transiciones. Cada nodo representa una acción o decisión que ocurre cuando un ciudadano avanza en el programa. El editor permite al configurador armar ese grafo visualmente con drag & drop. Al guardar, el grafo se persiste como JSON. El motor de flujos (US-006) lo interpreta en tiempo de ejecución.

---

## Decisiones de stack (cerradas)

| Decisión | Elección | Razón |
|----------|---------|-------|
| Librería de canvas | **React Flow** | Estándar de industria para grafos en React. Nodos custom, JSON nativo, MIT. |
| Compilación | **Vite** | Más rápido que CRA, mejor DX, output limpio para integrar en Django staticfiles |
| Integración Django | Assets compilados en `static/flujos/dist/` cargados desde template Django | Sin SSR — 100% client-side |
| Comunicación backend | API REST Django — `GET/POST /api/flujos/<programa_id>/` | Simple, desacoplado |
| Propiedades de nodo | Panel lateral derecho dentro del mismo editor | Sin navegación fuera del canvas |

**Estructura de archivos:**
```
frontend/
└── flow-editor/          ← app React (Vite)
    ├── src/
    │   ├── nodes/        ← un componente por tipo de nodo
    │   ├── panels/       ← panel de propiedades por tipo
    │   └── App.tsx
    └── dist/             ← output compilado → static/flujos/dist/
```

---

## Tipos de nodo

| Nodo | Qué hace |
|------|---------|
| **Inicio** | Punto de entrada del flujo. Único por flujo. |
| **Formulario** | El operador (o ciudadano) completa un formulario con campos configurables |
| **Evaluación** | Un profesional evalúa al ciudadano y emite un resultado |
| **Condición** | Bifurcación lógica — el flujo sigue por una rama u otra según un criterio |
| **Aprobación** | Paso de aceptar/rechazar — si rechaza, el flujo cierra la inscripción |
| **Tarea territorial** | Formulario enviado a operador de campo para completar en app móvil |
| **Email** | Envío de email automático (ciudadano / operador / ambos) |
| **Espera** | Pausa configurable en días antes de avanzar al siguiente paso |
| **Asignación** | Asigna el caso a un operador o rol específico |
| **Fin** | Cierre del flujo — resultado: Aprobado / Rechazado / Completado |

---

## Propiedades configurables por nodo

### Todos los nodos
- Nombre del paso (ej: "Entrevista inicial")
- Rol asignado — solo operadores con ese rol pueden ejecutar este paso
- Descripción/instrucciones para el operador

### Formulario
- Campos configurables: texto corto, texto largo, número, fecha, selección simple, selección múltiple, archivo adjunto, booleano (sí/no)
- Cada campo: obligatorio / opcional
- ¿Visible para el ciudadano desde el portal?

### Condición
- Variable a evaluar (resultado de formulario, campo del ciudadano, resultado de evaluación)
- Operador: igual a / mayor que / contiene / es verdadero
- Valor de comparación
- Dos salidas: rama VERDADERO y rama FALSO

### Aprobación
- Texto del motivo de rechazo (obligatorio al rechazar)
- ¿El rechazo cierra la inscripción automáticamente?

### Tarea territorial
- Formulario a enviar a app móvil
- Plazo en días para completar
- Comportamiento al vencer el plazo

### Email
- Destinatario: ciudadano / operador / ambos
- Asunto y cuerpo con variables dinámicas (nombre ciudadano, programa, estado)

### Espera
- Cantidad de días
- ¿El operador puede saltear la espera manualmente?

### Fin
- Resultado: APROBADO / RECHAZADO / COMPLETADO
- Programas de un solo acto: cierra la inscripción automáticamente al llegar aquí

---

## Comportamiento del editor (UX)

- **Canvas** central con drag & drop (React Flow)
- **Panel izquierdo** con los tipos de nodo disponibles para arrastrar
- **Panel derecho** con propiedades del nodo seleccionado (incluye el form builder para nodo Formulario)
- **Conectores** entre nodos dibujados clickeando en los puertos de salida/entrada
- **Validación en tiempo real:**
  - Nodos sin conectar → aviso
  - Flujo sin nodo Inicio o sin nodo Fin → no se puede publicar
  - Nodo sin rol asignado → aviso
- **Botón "Publicar flujo"** — solo activo cuando el flujo pasa todas las validaciones

---

## Persistencia y versionado

- El flujo se guarda como **JSON** en el modelo `Flujo` del motor de flujos (US-006)
- Cada publicación crea una nueva **versión** del flujo (`version: N`)
- Las instancias en curso siguen corriendo sobre la versión con la que fueron creadas — no se migran
- El configurador puede ver qué versión está activa y cuántas instancias corren sobre versiones anteriores

---

## Permisos

- Solo `programaConfigurar` puede abrir y guardar el editor
- Se accede desde `/programas/<id>/flujo/editar/` dentro del backoffice
- Un programa con instancias activas puede editarse — al publicar genera versión nueva sin romper instancias existentes

---

## Integración con el resto del sistema

| Conexión | Cómo |
|----------|------|
| Motor de flujos (US-006) | Lee el JSON del `Flujo` para ejecutar instancias |
| Wizard del programa (US-005) | El editor es el paso final de configuración |
| App móvil | Los nodos "Tarea territorial" generan tareas que recibe la app |
| Portal ciudadano | Los nodos "Formulario" marcados como visibles al ciudadano aparecen en su portal |

---

## Criterios de éxito

- [ ] El editor carga el flujo existente (si hay) desde la API al abrirse
- [ ] El configurador puede arrastrar nodos al canvas y conectarlos
- [ ] Cada tipo de nodo tiene su panel de propiedades con sus campos específicos
- [ ] El nodo Formulario permite agregar/quitar/ordenar campos desde el panel lateral
- [ ] La validación en tiempo real bloquea la publicación si hay errores
- [ ] Al publicar, se crea una nueva versión del flujo en el backend
- [ ] Las instancias en curso no se ven afectadas por la nueva versión
- [ ] Solo usuarios con `programaConfigurar` pueden acceder al editor
- [ ] El editor funciona correctamente en los navegadores modernos (Chrome, Firefox, Edge)
