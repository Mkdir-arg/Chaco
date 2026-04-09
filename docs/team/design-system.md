# Design System — SistemSo / NODO

> **Regla:** Leer este documento ANTES de escribir cualquier template nuevo.
> **Regla:** No inventar colores, tipografías ni componentes fuera de este sistema.
> Fuente: Manual de Marca NODO 2026
> Última actualización: 2026-03-12

---

## Stack de UI

| Tecnología | Versión | Cómo se usa |
|-----------|---------|-------------|
| Tailwind CSS | CDN | Clases utilitarias. Config extendida en `includes/base.html` |
| Alpine.js | 3.x | Interactividad declarativa (modales, toggles, dropdowns) |
| Font Awesome | 6.4 | Íconos: `fas fa-*`, `far fa-*`, `fab fa-*` |
| Inter | Google Fonts | **Fuente base en toda la plataforma** (ver Tipografía) |

**No usar:** Bootstrap directamente, jQuery para DOM, librerías de componentes externas.
**Excepción:** Select2 — ya está activado globalmente desde `base.html`, no duplicar.

---

## Grilla

La grilla de los legajos se estructura en 7 columnas:

| Elemento | Ancho |
|----------|-------|
| Barra de menú lateral | 290px |
| Gap lateral (izquierda y derecha) | 33px |
| Columna de contenido | 243px (× 6) |
| Gap entre columnas | 20px |

**En Tailwind:**
```html
<!-- Sidebar (ya manejado por base.html) -->
<!-- Contenido principal -->
<div class="px-8">  <!-- 33px aprox padding lateral -->
    <div class="grid grid-cols-6 gap-5">  <!-- gap-5 = 20px -->
        <!-- columnas -->
    </div>
</div>
```

---

## Paleta de colores

### Colores de marca (brand)

| Color | Hex | Uso |
|-------|-----|-----|
| Magenta | `#FF0080` | CTA principal, líneas, detalles, gradiente |
| Purple | `#7928CA` | Gradiente, gráficos, ilustraciones |
| Violet | `#8908CC` | Gradiente, ilustraciones |
| Cyan | `#08B8CC` | Gráficos, ilustraciones secundarias |
| Rose | `#CC0884` | Gráficos, ilustraciones secundarias |

**Gradiente principal:** `linear-gradient(45deg, #7928CA 0%, #FF0080 100%)`

### Colores de UI (texto, fondos, bordes)

| Color | Hex | Uso exacto |
|-------|-----|-----------|
| `#141414` | Negro casi puro | Nombre del legajo / ciudadano |
| `#101828` | Títulos tarjetas | Títulos de tarjetas, dropdowns, badges |
| `#252F40` | Título módulo | Encabezados de módulo (Inter Bold 16) |
| `#4A5565` | Texto general | Párrafos, menú lateral |
| `#8C8C8C` | Subtítulo muted | Subtítulos, textos secundarios del legajo |
| `#56606A` | Iconos | Color de íconos en UI |
| `#E5E7EB` | Borde tarjetas | Stroke de tarjetas, separadores |
| `#FFFFFF` | Fondo módulos | Background de cards y módulos |
| `#F9FAFB` | Fondo alternativo | Fondo de inputs, botones secondary |
| `#F3F4F6` | Fondo hover | Fondo en hover de botones secondary |

### CSS Variables (disponibles vía branding)

```css
var(--color-primario)        /* #7928CA */
var(--color-primario-claro)  /* #FF0080 */
var(--color-acento)          /* #08B8CC */
var(--nodo-gradient)         /* linear-gradient(45deg, #7928CA, #FF0080) */
var(--nodo-text-primary)     /* #141414 */
var(--nodo-text-secondary)   /* #252F40 */
var(--nodo-text-tertiary)    /* #4A5565 */
var(--nodo-text-muted)       /* #8C8C8C */
var(--nodo-border)           /* #E5E7EB */
var(--fondo-principal)       /* #F8FAFC */
```

---

## Tipografía

**Familia:** `Inter` — fuente base en toda la plataforma.

> ⚠️ El `base.html` actual carga Lora + Montserrat (legacy). Inter es la fuente definitiva del manual de marca. Para nuevos templates usar `font-['Inter']` o la clase `font-sans` si Inter está configurada.

### Pesos y usos

| Peso | Tailwind | Uso |
|------|----------|-----|
| Normal (400) | `font-normal` | Párrafos, ayuda, texto general |
| Medium (500) | `font-medium` | Botones, etiquetas, CTAs, algunos títulos |
| Semibold (600) | `font-semibold` | Títulos de secciones y tarjetas |
| Bold (700) | `font-bold` | Títulos principales |
| Extrabold (800) | `font-extrabold` | H1 en secciones hero |

### Tamaños y tracking

| Tailwind | Uso |
|----------|-----|
| `text-xs` / `text-sm` | Párrafo pequeño, botones, etiquetas |
| `text-base` / `text-lg` / `text-xl` | Texto estándar |
| `text-2xl` / `text-3xl` | Encabezados de bloques |
| `text-4xl` / `text-5xl` / `text-6xl` | Encabezados estilo H1 |

**Tracking:**
- `tracking-tighter` → H1 grandes (mejora legibilidad en tamaños grandes)
- `tracking-tight` → Títulos de secciones y tarjetas

### Jerarquía en un módulo (spec exacto del manual)

| Elemento | Spec |
|----------|------|
| Título Módulo | Inter Bold 16px, color `#252F40` |
| Título Tarjeta | Inter Semibold 32px, line-height 32px, color `#101828` |
| Párrafo | Inter Normal 16px, line-height 24px, color `#4A5565` |

---

## Módulos (Cards)

Todos los módulos del sistema siguen esta especificación:

```
Fill:   #FFFFFF
Stroke: ninguno
Shadow: Shadow-MD (ver sección Sombras)
Radio módulo (contenedor): 15px
Radio tarjeta (interna):   12px
Stroke tarjeta interna:    #E5E7EB
```

**Espaciado interno:**

```
Padding externo del módulo:     15px en todos los lados
Gap entre título y tarjeta:     15px
Padding interno de la tarjeta:  28px lados, 28px top
Gap entre tarjeta y botón:      24px
Padding bottom variable:        15px mínimo
```

**Template HTML:**

```html
<!-- Módulo -->
<div class="bg-white rounded-[15px] p-[15px]" style="box-shadow: var(--shadow-md)">
    <!-- Título módulo -->
    <h3 class="text-base font-bold mb-[15px]" style="color: #252F40">Título Módulo</h3>

    <!-- Tarjeta interna -->
    <div class="rounded-xl border p-7" style="border-color: #E5E7EB">
        <h4 class="text-3xl font-semibold leading-8 mb-1" style="color: #101828">Título Tarjeta</h4>
        <p class="text-base leading-6" style="color: #4A5565">Párrafo del módulo...</p>
        <div class="mt-6">
            <button class="btn-nodo btn-tertiary btn-xs">Botón →</button>
        </div>
    </div>
</div>
```

---

## Sombras

### Shadow-MD (única sombra del sistema)

Usada en todos los módulos y cards.

```css
box-shadow:
    0 1px 3px 0 rgba(0, 0, 0, 0.10),
    0 1px 2px -1px rgba(0, 0, 0, 0.10);
```

Equivale a `shadow-sm` de Tailwind. Usar `shadow-sm` en clases Tailwind.

---

## Botones

### Tamaños

| Tamaño | Font | Alto | Padding H | Padding V | Radio |
|--------|------|------|-----------|-----------|-------|
| XS | Inter Medium 12px | 32px | 12px | 6px | 12px |
| SM | Inter Medium 14px | 36px | 12px | 8px | 12px |
| Base | Inter Medium 14px | 40px | 16px | 10px | 12px |
| L | Inter Medium 16px | 48px | 20px | 12px | 12px |
| XL | Inter Medium 16px | 52px | 24px | 14px | 12px |

Gap entre ícono y texto: 6px. Ambos íconos (izquierdo y derecho) son opcionales.

### Variantes y estados

#### Brand (acción principal)

| Estado | Fill | Texto | Stroke |
|--------|------|-------|--------|
| Inicial | Gradient 45° `#7928CA → #FF0080` | `#FFFFFF` | — |
| Hover | Gradient + `#000000` 20% overlay | `#FFFFFF` | — |
| Focus | Gradient + stroke `#7928CA` 2px + shadow `#E5E7EB` | `#FFFFFF` | `#7928CA` 2px |
| Disabled | `#F3F4F6` | `#99A1AF` | `#E5E7E8` 1px |

```html
<button class="btn-nodo btn-primary btn-base">Acción principal</button>
<button class="btn-nodo btn-primary btn-sm">Pequeño</button>
<button class="btn-nodo btn-primary btn-xs">Extra pequeño</button>
```

#### Secondary (acción secundaria)

| Estado | Fill | Texto | Stroke |
|--------|------|-------|--------|
| Inicial | `#F9FAFB` | `#4A5565` | `#E5E7EB` 1px |
| Hover | `#F3F4F6` | `#101828` | `#E5E7EB` 1px |
| Focus | `#F3F4F6` | `#101828` | `#E5E7EB` 1px + shadow `#F3F4F6` |
| Disabled | `#F3F4F6` | `#99A1AF` | `#E5E7E8` 1px |

```html
<button class="btn-nodo btn-secondary btn-base">Cancelar</button>
```

#### Tertiary (acción de apoyo / link-style)

| Estado | Fill | Texto | Stroke |
|--------|------|-------|--------|
| Inicial | `#FFFFFF` | `#FF0080` | `#FF0080` 1px |
| Hover | `#FF0080` 10% | `#D4006A` | `#D4006A` 1px |
| Focus | `#D4006A` 10% | `#D4006A` | `#D4006A` 1px + shadow `#F3F4F6` |
| Disabled | `#C7A0B4` 20% | `#D4006A` | `#C7A0B4` 1px |

```html
<button class="btn-nodo btn-tertiary btn-xs">Ver más →</button>
```

Las clases `btn-nodo` están definidas en `custom/css/nodo-buttons.css`. **No reinventar con inline styles.**

---

## Badges

### Tamaños

| Tamaño | Font | Alto | Radio | Padding |
|--------|------|------|-------|---------|
| SM | Inter Medium 12px | 20px | 6px | 2px V / 4px-6px H |
| LG | Inter Medium 14px | 24px | 6px | 4px V / 6px H |

Ambos íconos (izquierdo y derecho) son opcionales.

### Variantes — tokens oficiales del manual de marca

Los colores exactos pueden variar por perfil de branding.

| Variante | Texto | Fill | Stroke | Uso |
|----------|-------|------|--------|-----|
| **Gray** | `#101828` | `#F9FAFB` | `#101828` 1px | Neutro, borrador, sin estado |
| **White** | `#101828` | `#FFFFFF` | `#E5E7EB` 1px | Secundario, alternativo |
| **Brand** | `#A11F60` | `#FFB9DC` | `#101828` 1px | Especial, destacado de marca |
| **Danger** | `#8B0836` | `#FEF0F2` | `#FFCCD3` 1px | Rechazado, cancelado, crítico |
| **Warning** | `#771D1D` | `#FFF8F1` | `#FCD9BD` 1px | Pendiente, advertencia |
| **Success** | `#006045` | `#ECFDF5` | `#A4F4CF` 1px | Activo, aprobado, completado |

### CSS de badges

```css
.badge-nodo {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    border-style: solid;
    border-width: 1px;
    border-radius: 6px;
}
/* SM */
.badge-sm { font-size: 12px; height: 20px; padding: 2px 6px; }
/* LG */
.badge-lg { font-size: 14px; height: 24px; padding: 4px 6px; }

.badge-gray    { color: #101828; background: #F9FAFB; border-color: #101828; }
.badge-white   { color: #101828; background: #FFFFFF; border-color: #E5E7EB; }
.badge-brand   { color: #A11F60; background: #FFB9DC; border-color: #101828; }
.badge-danger  { color: #8B0836; background: #FEF0F2; border-color: #FFCCD3; }
.badge-warning { color: #771D1D; background: #FFF8F1; border-color: #FCD9BD; }
.badge-success { color: #006045; background: #ECFDF5; border-color: #A4F4CF; }
```

### Uso en templates

```html
<span class="badge-nodo badge-sm badge-success">Activo</span>
<span class="badge-nodo badge-sm badge-warning">Pendiente</span>
<span class="badge-nodo badge-sm badge-danger">Rechazado</span>
<span class="badge-nodo badge-sm badge-gray">Borrador</span>
<span class="badge-nodo badge-lg badge-brand">Destacado</span>
```

### Mapeo de estados del sistema

| Estado de negocio | Variante |
|-------------------|---------|
| Activo / Confirmado / Aprobado / Completado | `badge-success` |
| Pendiente / En espera / En revisión | `badge-warning` |
| Rechazado / Cancelado / Dado de baja / Inactivo | `badge-danger` |
| Borrador / Sin estado | `badge-gray` |
| Suspendido (programa) | `badge-warning` |
| Destacado / especial | `badge-brand` |

---

## Componentes disponibles

Usar `{% include 'components/X.html' %}` antes de escribir HTML a mano.

| Componente | Archivo | Cuándo usar |
|-----------|---------|-------------|
| Tabla responsive | `components/responsive_table.html` | Listados con paginación |
| Card de estadística | `components/stats_card.html` | Métricas en dashboard |
| Card de form | `components/form_card.html` | Formularios con crispy |
| Tabs | `components/tabs.html` | Hub del ciudadano, secciones con solapas |
| Modal | `components/modal.html` | Confirmaciones, detalle rápido |
| Estado vacío | `components/empty_state.html` | Cuando no hay resultados |
| Breadcrumb | `components/breadcrumb.html` | Navegación contextual |
| Paginación | `components/pagination.html` | Listados paginados |
| Timeline | `components/timeline.html` | Historial cronológico |
| Spinner | `components/loading_spinner.html` | Carga asíncrona |
| Barra de búsqueda | `components/search_bar.html` | Filtro rápido |
| Botones de acción | `components/action_buttons.html` | Ver / Editar / Eliminar |
| Botones de form | `components/form_buttons.html` | Guardar / Cancelar |
| Info card | `components/info_card.html` | Datos de detalle con ícono |
| Stepper / Wizard | `components/ciudadano_stepper.html` | Flujos multi-paso |

---

## Layout base

### Estructura de página backoffice

```html
{% extends 'includes/base.html' %}
{% block title %}Título de página{% endblock %}
{% block titulo-pagina-content %}Título visible{% endblock %}
{% block breadcrumb %}
    <li class="breadcrumb-item"><a href="{% url 'home' %}">Inicio</a></li>
    <li class="breadcrumb-item active">Sección</li>
{% endblock %}
{% block content %}
    <!-- contenido aquí -->
{% endblock %}
{% block extra_js %}
    <!-- JS específico aquí -->
{% endblock %}
```

Portal ciudadano: extiende `portal/base.html`.

### Patrones de grilla de contenido

```html
<!-- Página con sidebar de filtros -->
<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
    <div class="lg:col-span-1"><!-- filtros --></div>
    <div class="lg:col-span-3"><!-- contenido --></div>
</div>

<!-- Dashboard con métricas (4 columnas) -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    <!-- cards -->
</div>

<!-- Detalle full-width -->
<div class="space-y-6"><!-- módulos apilados --></div>
```

---

## Módulo tabla (patrón del manual)

Basado en el ejemplo "Módulo tabla" del manual de marca:

```html
<!-- Módulo tabla -->
<div class="bg-white rounded-[15px] shadow-sm p-[15px]">
    <!-- Toolbar -->
    <div class="flex items-center justify-between mb-4">
        <!-- Búsqueda -->
        <div class="relative">
            <input type="text" placeholder="Buscar..."
                   class="pl-9 pr-3 py-2 text-sm border rounded-xl border-gray-200
                          focus:outline-none focus:ring-2 focus:ring-primario/30"
                   style="color: #4A5565">
            <i class="fas fa-search absolute left-3 top-2.5 text-xs" style="color: #56606A"></i>
        </div>
        <!-- Acciones -->
        <div class="flex gap-2">
            <button class="btn-nodo btn-primary btn-sm">+ Agregar</button>
            <button class="btn-nodo btn-secondary btn-sm">
                <i class="fas fa-filter mr-1"></i>Filtrar
            </button>
            <button class="btn-nodo btn-secondary btn-sm">Acciones ▾</button>
        </div>
    </div>

    <!-- Tabla -->
    <table class="w-full text-sm">
        <thead>
            <tr class="border-b" style="border-color: #E5E7EB">
                <th class="text-left pb-3 font-medium" style="color: #4A5565">Columna</th>
            </tr>
        </thead>
        <tbody>
            {% for item in object_list %}
            <tr class="border-b hover:bg-gray-50 transition-colors"
                style="border-color: #E5E7EB">
                <td class="py-3" style="color: #141414">{{ item }}</td>
                <td>
                    <span class="badge-nodo badge-sm badge-success">Estado</span>
                </td>
                <td class="text-right">
                    <button class="btn-nodo btn-secondary btn-xs">Acciones ▾</button>
                    <button class="btn-nodo btn-tertiary btn-xs ml-1">
                        <i class="fas fa-trash"></i> Borrar
                    </button>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <!-- Paginación -->
    <div class="flex items-center justify-between mt-4 text-sm" style="color: #4A5565">
        <span>Mostrando 1-5 of 16</span>
        {% include 'components/pagination.html' %}
    </div>
</div>
```

---

## Módulo con stepper (patrón del manual)

Para historial de ejecución / flujos / timelines:

```html
<div class="bg-white rounded-[15px] shadow-sm p-[15px]">
    <h3 class="text-base font-bold mb-4" style="color: #252F40">Historial de Ejecución</h3>

    <div class="flex gap-4">
        <!-- Stepper vertical -->
        <div class="flex flex-col gap-1 min-w-[140px]">
            {% for paso in pasos %}
            <div class="flex items-start gap-2">
                <div class="flex flex-col items-center">
                    <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs
                                {% if paso.completado %}text-white{% else %}text-gray-400 bg-gray-100{% endif %}"
                         style="{% if paso.completado %}background: var(--nodo-gradient){% endif %}">
                        {% if paso.completado %}<i class="fas fa-check text-xs"></i>
                        {% else %}<i class="fas fa-{{ paso.icono }} text-xs"></i>{% endif %}
                    </div>
                    {% if not forloop.last %}
                    <div class="w-px h-6 bg-gray-200 my-1"></div>
                    {% endif %}
                </div>
                <div>
                    <p class="text-sm font-medium" style="color: {% if paso.activo %}var(--color-primario-claro){% else %}#4A5565{% endif %}">
                        {{ paso.nombre }}
                    </p>
                    <p class="text-xs" style="color: #8C8C8C">{{ paso.fecha }}</p>
                </div>
            </div>
            {% endfor %}
        </div>

        <!-- Detalle del paso activo -->
        <div class="flex-1 rounded-xl border p-5" style="border-color: #E5E7EB">
            <h4 class="text-2xl font-semibold mb-1" style="color: #101828">{{ paso_activo.titulo }}</h4>
            <p class="text-sm mb-1" style="color: #8C8C8C">{{ paso_activo.fecha }}</p>
            <p class="text-base leading-6" style="color: #4A5565">{{ paso_activo.descripcion }}</p>
            <div class="mt-5">
                <button class="btn-nodo btn-tertiary btn-xs">Ver más →</button>
            </div>
        </div>
    </div>
</div>
```

---

## Reglas no negociables

- [ ] **Tipografía: Inter** — no usar Lora/Montserrat en nuevos templates
- [ ] **No inventar colores** — usar CSS variables, clases del sistema o valores exactos del manual
- [ ] **No agregar librerías externas** sin aprobación del Arquitecto + ADR
- [ ] **Select2 ya está activado** desde `base.html` — no duplicar
- [ ] **Eliminaciones siempre con SweetAlert2** — nunca `confirm()` nativo
- [ ] **Backoffice** extiende `includes/base.html`
- [ ] **Portal ciudadano** extiende `portal/base.html`
- [ ] **`{% csrf_token %}`** en todos los forms POST
- [ ] **Badges** usan `badge-nodo badge-[variante]` — no Tailwind genérico
- [ ] **Shadow en módulos:** `shadow-sm` (= Shadow-MD del manual)
- [ ] **Border-radius módulo:** `rounded-[15px]`, tarjeta interna: `rounded-xl` (12px)
