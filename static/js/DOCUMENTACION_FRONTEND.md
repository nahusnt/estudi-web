# Documentación del frontend — Estudi Web

## Estructura

- `templates/index.html` contiene la interfaz autenticada: barra lateral, tareas, resumen, perfil y ajustes.
- `templates/login.html` y `templates/registro.html` contienen los formularios de acceso y alta de cuentas.
- `static/css/styles.css` define el sistema visual, los temas y las adaptaciones a distintos tamaños.
- `static/js/app.js` conecta controles de la interfaz, preferencias guardadas en el navegador, confirmaciones y traducciones.
- `static/images/` contiene imágenes de uso directo en la interfaz.
- `images/vista-clara.svg` y `images/vista-oscura.svg` son ilustraciones de demostración con datos ficticios; no son capturas reales.

## Interfaz principal

La disposición extendida muestra una barra lateral fija/sticky con marca y navegación para **Resumen**, **Tareas**, **Ajustes** y **Perfil**. En la parte inferior se presenta una sola tarjeta con avatar (o inicial), nombre, identificador y botón de cierre de sesión. El texto promocional y el estado inferior que existían antes ya no forman parte del diseño.

En pantallas estrechas la navegación se adapta; en móvil se ocultan el rótulo de la sección y la tarjeta lateral de cuenta para conservar espacio. La disposición compacta mantiene el estilo anterior con navegación superior y oculta la tarjeta lateral.

## Preferencias

JavaScript valida los valores antes de aplicarlos y usa `localStorage` para guardar las preferencias del navegador:

| Preferencia | Clave | Opciones |
|---|---|---|
| Tema | `tema-lista-tareas` | oscuro, claro, AMOLED |
| Paleta | `paleta-lista-tareas` | violeta, océano, atardecer, menta, cítrico, frambuesa, coral, bosque, zafiro y rosa |
| Idioma | `idioma-lista-tareas` | español, inglés, portugués, chino simplificado, japonés y coreano |
| Disposición | `disposicion-lista-tareas` | compacta o extendida |
| Densidad de tareas | `lista-tareas-compacta` | cómoda o compacta |
| Tamaño del texto | `tamano-texto-lista-tareas` | normal, grande o muy grande |
| Contraste | `contraste-lista-tareas` | normal o reforzado |
| Animaciones | `animaciones-lista-tareas` | activadas o desactivadas |

Si una preferencia no existe o no es válida, se aplica el valor inicial definido en `app.js`. Si el navegador bloquea `localStorage`, las funciones afectadas usan sus valores iniciales.

## Interacciones

- El botón de cabecera recorre los temas y el selector de ajustes permite elegir uno directamente.
- Los selectores y controles de ajustes actualizan los atributos `data-*` de `<html>` y guardan la preferencia correspondiente.
- El cambio de idioma reemplaza textos de interfaz con traducciones definidas en `TRADUCCIONES`; los valores escritos por la persona usuaria no se traducen.
- Las casillas de tarea envían su formulario para cambiar el estado. Antes de eliminar, se solicita confirmación.
- En login y registro, el control de contraseña alterna entre texto visible y oculto.
- Se respetan los estados de foco y `prefers-reduced-motion` en CSS.

## Clases y atributos visuales

| Selector | Función |
|---|---|
| `[data-theme]`, `[data-palette]` | Variables de color del tema y paleta activa. |
| `[data-layout]` | Cambia entre barra lateral extendida y navegación compacta. |
| `[data-density]`, `[data-text-size]`, `[data-contrast]`, `[data-motion]` | Ajustes de densidad, tamaño, contraste y animación. |
| `.sidebar`, `.section-nav`, `.sidebar-user` | Navegación lateral y única tarjeta de la cuenta. |
| `.panel`, `.glass` | Paneles visuales de tareas, resumen, ajustes y perfil. |
| `.task-form`, `.filters`, `.task-list`, `.task-item` | Formulario, filtros y elementos de tareas. |
| `.summary-cards`, `.completion-panel`, `.summary-details` | Métricas y progreso del resumen. |
| `.profile-panel`, `.profile-avatar`, `.profile-fields` | Presentación y formulario del perfil. |
| `.button` y sus modificadores | Botones comunes, primarios, secundarios, discretos y de eliminación. |
