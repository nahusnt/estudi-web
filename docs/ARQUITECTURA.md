# Arquitectura

Estudi Web es una aplicación web hecha con Flask, MongoDB y una interfaz HTML, CSS y JavaScript.

## Componentes

- **`app.py`**: crea la aplicación Flask, carga las variables de entorno, abre la conexión con MongoDB, inicializa `RepositorioTareas` y define las rutas. También recibe los formularios, valida sus parámetros, calcula el progreso y las fechas límite del resumen, y envía los datos a las plantillas.
- **`modelos.py`**: contiene `Categoria` y `Tarea`, que validan los datos de dominio, incluida la descripción opcional y la fecha límite. `RepositorioTareas` encapsula las operaciones de MongoDB: guardar, consultar, ordenar, cambiar el estado y eliminar tareas. Los campos nuevos se leen con valores predeterminados para mantener la compatibilidad con tareas guardadas antes de incorporarlos. Al inicializarse crea el índice de `titulo`.
- **`templates/index.html`**: es la vista principal renderizada por Jinja. Muestra la navegación lateral, el formulario de alta, los filtros, la lista de tareas, el resumen y los ajustes. Usa `url_for` para construir las rutas de Flask y variables Jinja para mostrar los datos recibidos.
- **`static/css/styles.css`**: define la presentación visual, la interfaz anterior con navegación superior y la nueva barra lateral, los temas claro y oscuro, la distribución responsive, los estados de las tareas y los componentes de la interfaz.
- **`static/js/app.js`**: gestiona el cambio de tema y disposición, la densidad de la lista, las preferencias guardadas en `localStorage` y la confirmación antes de eliminar una tarea.
- **`static/js/DOCUMENTACION_FRONTEND.md`**: documenta las decisiones del rediseño frontend, las clases CSS, el comportamiento de JavaScript, la accesibilidad y los modos de color.

## Flujo principal

1. `app.py` carga la configuración y crea un `MongoClient`.
2. La base `lista_tareas_db` se entrega a `RepositorioTareas`, que trabaja con la colección `tareas` y crea el índice sobre `titulo`.
3. Una ruta de Flask recibe una petición del navegador y llama al repositorio cuando necesita leer o modificar tareas.
4. Flask entrega los resultados a `templates/index.html`, que genera el HTML con Jinja.
5. El navegador carga los recursos de `static/`: CSS para el diseño y JavaScript para las interacciones que no necesitan una nueva petición.
