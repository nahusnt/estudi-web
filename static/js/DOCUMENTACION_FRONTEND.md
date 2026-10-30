# Documentación del rediseño Frontend – Estudi Web

## 1. Decisiones de diseño
- **Referencia:** la imagen "Y2K Aesthetic" de Pinterest: fondo oscuro, tipografía cromada, degradados holográficos, vidrio translúcido, burbujas de luz y detalles pixelados.
- **Tipografías (Google Fonts):** *Orbitron* para títulos (aspecto futurista/cromado), *Space Grotesk* para el texto (legible) y *VT323* para etiquetas y detalles pixelados.
- **Paleta:** base violeta-noche (`#0b0a1a`) con acentos cian, lila, rosa y durazno que se combinan en el degradado `--holo`.
- **Glassmorphism:** los paneles usan fondo translúcido, `backdrop-filter: blur`, borde con degradado y bordes redondeados grandes (26px).
- **Forma redonda como identidad:** botones tipo píldora, casillas circulares y badges redondeados (la "forma burbuja" de la referencia).
- **Brillos:** dos burbujas de luz difuminadas en el fondo y una estrella de 4 puntas (lens flare) hecha con CSS.
- **Responsivo:** mobile-first en la práctica; 3 puntos de corte (760px y 480px) que reacomodan las grillas.
- **Accesibilidad:** foco visible, `prefers-reduced-motion` respetado, contraste alto en ambos temas.
- **Archivos:** se mantienen los nombres `styles.css` y `app.js` porque así los referencia `url_for` en el HTML.

## 2. Clases CSS
| Clase | Para qué sirve |
|---|---|
| `:root` / `[data-theme="light"]` / `[data-theme="amoled"]` | Variables de color para los temas oscuro, claro y AMOLED negro puro. |
| `.bg-orb`, `.bg-orb-one/two` | Burbujas de luz difuminadas del fondo (decorativas). |
| `.app-shell` | Contenedor central con ancho máximo. |
| `.page-header`, `.brand-lockup`, `.brand-logo` | Cabecera, grupo logo + títulos, logo con borde holográfico. |
| `.eyebrow`, `.sparkle`, `.sparkle-lg` | Texto pixelado superior y estrella de 4 puntas (con `clip-path`). |
| `.chrome-title` | Título con efecto cromado (degradado recortado al texto). |
| `.panel`, `.glass` | Tarjeta de vidrio con borde degradado y desenfoque. |
| `.task-form`, `.filters` | Grillas de los formularios de alta y de filtros. |
| `.field`, `.field-title`, `.field-tags` | Etiqueta + campo; las dos últimas ocupan todo el ancho en móvil. |
| `.button`, `.button-primary`, `.button-secondary`, `.button-quiet`, `.button-delete` | Botón base y variantes: holográfico, de vidrio, discreto (tema) y de peligro. |
| `.add-button`, `.filter-button` | Botones de agregar y de aplicar filtros. |
| `.task-list`, `.task-item`, `.is-complete` | Lista, cada tarea, y estado de tarea terminada (tachada). |
| `.toggle-form`, `.delete-form`, `.checkbox-label` | Formularios de marcar/eliminar y contenedor de la casilla circular. |
| `.task-content`, `.task-title`, `.task-meta` | Texto de la tarea y fila de insignias. |
| `.category-badge`, `.tag-badge` | Insignias de categoría (contorno) y de etiqueta (pixelada). |
| `.empty-state` | Mensaje cuando no hay tareas. |
| `.messages`, `.notice`, `.notice-error` | Mensajes flash de Flask. |

## 3. Cómo se adaptó el JavaScript
- Se conservaron los `id` `#theme-toggle` y `#theme-label` y la clase `.delete-form`, así que el JS sigue encontrando los elementos.
- El HTML conserva el `onchange="this.form.submit()"` de las casillas y el atributo `data-confirm` de eliminar, por lo que marcar y borrar tareas funcionan igual.
- Se agregó `aplicarTema(tema)`, que centraliza el cambio de `data-theme`, el texto del botón y su `aria-label`.
- `localStorage` ahora va dentro de `try/catch` por si el navegador lo bloquea.
- **No se tocó nada** de Python ni de las variables Jinja (`{{ tarea.titulo }}`, `url_for`, `filtros`, etc.).

## 4. Temas, paletas e idioma
- El diseño es **oscuro por defecto**. Se puede elegir entre `dark`, `light` y `amoled`; AMOLED usa `#000000` como fondo y oculta los orbes decorativos.
- El selector de color ofrece diez paletas de acento y se combina con cualquiera de los tres temas.
- El botón de cabecera recorre los tres temas. La opción y la paleta se guardan en `localStorage` con las claves `tema-lista-tareas` y `paleta-lista-tareas`.
- El selector de idioma ofrece español, inglés, portugués, chino simplificado, japonés y coreano; su preferencia se guarda con `idioma-lista-tareas`. Los datos introducidos por la persona usuaria se mantienen sin traducir.
- Al volver a cargar la página, JavaScript restaura las preferencias. Los componentes usan variables CSS (`var(--text)`, `var(--surface)`…), sin duplicar reglas por tema.
