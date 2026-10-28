# Modelado de Amenazas - Grupo 1
## Proyecto: Estudi Web

La aplicación permite crear, listar, completar y eliminar tareas almacenadas en MongoDB. Los riesgos y las medidas de hardening se describen según el código actual y las mejoras recomendadas.

### 1. Amenaza: Acceso y modificación de tareas sin control de propietario
- **Descripción del Riesgo:** La aplicación no implementa autenticación ni asocia las tareas a un usuario. Las rutas permiten listar y modificar tareas mediante su identificador, por lo que cualquier visitante puede acceder a las tareas compartidas o cambiar su identificador para intentar modificar o eliminar otra tarea (Broken Access Control / IDOR).
- **Impacto:** Exposición de títulos, descripciones, fechas y etiquetas; además de modificación o eliminación no autorizada de tareas.
- **Mitigación / Hardening:** Incorporar autenticación y guardar el identificador del propietario en cada tarea. En cada consulta, actualización y eliminación, filtrar por el identificador de la tarea y el usuario de la sesión activa. No confiar únicamente en que el identificador recibido sea válido.

### 2. Amenaza: Falsificación de solicitudes entre sitios (CSRF)
- **Descripción del Riesgo:** Las rutas `/agregar`, `/toggle/<id_tarea>` y `/eliminar/<id_tarea>` realizan cambios mediante solicitudes POST, pero no se observa validación de tokens CSRF. Un sitio externo podría inducir al navegador de una víctima a enviar una solicitud no deseada.
- **Impacto:** Creación, finalización o eliminación de tareas sin intención del usuario. El riesgo aumenta al incorporar autenticación basada en cookies.
- **Mitigación / Hardening:** Proteger los formularios y las rutas POST con tokens CSRF, por ejemplo mediante Flask-WTF. Al añadir sesiones autenticadas, configurar cookies `SameSite` y `Secure` en producción y validar el origen de las solicitudes como defensa adicional.

### 3. Amenaza: Exposición de la aplicación por configuración de depuración o secretos débiles
- **Descripción del Riesgo:** Al ejecutar directamente `app.py`, Flask se inicia con `debug=True`. Además, la aplicación acepta una clave secreta desde `FLASK_SECRET_KEY` pero genera una clave aleatoria si no está configurada, lo que puede invalidar sesiones entre reinicios y no garantiza una configuración adecuada en producción.
- **Impacto:** El modo de depuración puede exponer información interna y, si el servidor de desarrollo queda accesible, aumentar el riesgo de ejecución de código. Una clave mal gestionada puede comprometer la integridad de las sesiones y la protección de formularios.
- **Mitigación / Hardening:** Desactivar el modo debug fuera del entorno local y desplegar mediante un servidor WSGI de producción. Configurar una `FLASK_SECRET_KEY` larga, aleatoria y protegida como variable de entorno; no almacenarla en el repositorio. Mantener `MONGO_URI` fuera del código, restringir el acceso de red a MongoDB y usar un usuario de base de datos con permisos mínimos.
