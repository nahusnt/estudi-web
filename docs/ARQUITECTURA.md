# Arquitectura

Estudi Web es una aplicación web Flask con plantillas Jinja, CSS y JavaScript en el navegador, y MongoDB como persistencia. El acceso a las páginas de trabajo requiere una sesión iniciada.

## Componentes

- **`app.py`** configura Flask, carga `.env`, crea las conexiones MongoDB y los repositorios, protege las rutas con una comprobación de sesión y define los flujos de registro, inicio/cierre de sesión, perfil y tareas. También calcula las métricas y fechas que se muestran en el resumen.
- **`modelos.py`** define `Categoria`, `Tarea` y `RepositorioTareas`. Valida las tareas y concentra las consultas y modificaciones de la colección `tareas`, incluyendo filtros por propietario.
- **`usuarios.py`** define `Usuario` y `RepositorioUsuarios`. Valida las cuentas y perfiles, verifica hashes de contraseña y administra la colección `usuarios` con índices únicos de correo y nombre de usuario normalizado.
- **`templates/`** contiene las vistas Jinja: `login.html`, `registro.html` e `index.html`. La vista principal presenta las secciones de tareas, resumen, ajustes y perfil; la tarjeta de cuenta aparece una sola vez al final de la barra lateral.
- **`static/css/styles.css`** define temas, paletas, componentes, las disposiciones compacta y extendida, y los ajustes responsive.
- **`static/js/app.js`** aplica las preferencias del navegador, cambia tema, idioma, disposición, contraste, tamaño y densidad del texto/listado, y gestiona interacciones como confirmaciones y visibilidad de contraseñas.
- **`static/images/`** contiene recursos de interfaz, como el logotipo. **`images/`** contiene las ilustraciones de demostración y el diagrama de red de la documentación.
- **`tests/test_app.py`** contiene las pruebas automatizadas; los repositorios se simulan para no depender de una base real durante la suite.

## Persistencia

- Las tareas se guardan en la base `lista_tareas_db`, colección `tareas`, del clúster definido por `MONGO_URI`.
- Las cuentas se guardan por defecto en la base `estudi_usuarios_db`, colección `usuarios`, del mismo clúster. `USUARIOS_DB` permite cambiar el nombre de esa base y `USUARIOS_URI` permite usar otro clúster.
- Cada tarea creada por la aplicación incluye `usuario_id`. Las rutas de listado, cambio de estado y eliminación pasan el ID de la sesión al repositorio para limitar las operaciones a las tareas de esa cuenta.
- Los documentos antiguos de tareas pueden no incluir `descripcion`, `fecha_vencimiento` o `categoria`; el repositorio asigna valores compatibles al leerlos. Las tareas antiguas sin `usuario_id` no aparecen en las listas de una cuenta.

## Flujo de una petición

1. El navegador solicita una ruta Flask. `/login`, `/registro` y los recursos estáticos son públicos; el resto requiere `usuario_id` en la sesión.
2. La ruta valida los datos recibidos y consulta el repositorio correspondiente. Las modificaciones de tareas se limitan al propietario de la sesión.
3. Flask pasa los datos a una plantilla Jinja, que genera HTML con los recursos de `static/`.
4. JavaScript aplica las preferencias locales guardadas en `localStorage` y habilita interacciones del lado del cliente.

## Rutas principales

| Ruta | Método | Función |
|---|---|---|
| `/login` | GET, POST | Muestra el acceso e inicia sesión por correo o nombre de usuario. |
| `/registro` | GET, POST | Muestra el alta de cuenta y crea una cuenta nueva. |
| `/` | GET | Renderiza la sección solicitada mediante `?seccion=crear`, `resumen`, `ajustes` o `perfil`. |
| `/perfil` | POST | Actualiza los datos y la foto del perfil de la sesión. |
| `/agregar` | POST | Valida y guarda una tarea para la cuenta activa. |
| `/toggle/<id_tarea>` | POST | Cambia el estado de una tarea propia. |
| `/eliminar/<id_tarea>` | POST | Elimina una tarea propia. |
| `/logout` | POST | Cierra la sesión. |
