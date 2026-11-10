# Seguridad — Estudi Web

Este documento describe los controles que existen en el código y los puntos que deben atenderse antes de desplegar la aplicación en producción. La configuración de red de MongoDB Atlas también debe limitarse desde el panel del proveedor.

## Controles implementados

- Las rutas de trabajo requieren una sesión autenticada; solo `/login`, `/registro` y los recursos estáticos son públicos.
- Las rutas de creación, listado, cambio de estado y eliminación de tareas usan el ID de la sesión para restringir las operaciones a las tareas propias. Los identificadores de tarea se validan como `ObjectId`.
- Los modelos validan los campos antes de guardarlos en MongoDB. Las vistas HTML usan el autoescape de Jinja para mostrar el texto del usuario sin ejecutar etiquetas ni scripts; los datos se guardan como texto original, sin doble escape.
- Las contraseñas se guardan como hashes generados y verificados con las funciones de seguridad de Werkzeug, no como texto plano.
- Los errores de MongoDB se registran en el servidor y devuelven un mensaje genérico, sin exponer detalles de conexión o consultas.
- Los índices únicos de MongoDB protegen la unicidad del correo y del nombre de usuario normalizado.
- La foto de perfil se limita a 1 MB y se aceptan firmas binarias de PNG, JPEG o WebP; la aplicación limita las solicitudes a 2 MB.
- `.env` está excluido por `.gitignore`; no se deben incluir credenciales ni claves en el repositorio.
- `.env.example` contiene solo nombres de variables y valores ilustrativos; reemplaza esos marcadores en tu `.env` local y no copies credenciales reales al repositorio.

## Riesgos y medidas recomendadas

### Protección CSRF

Los formularios que cambian datos usan POST, pero el código actual no configura tokens CSRF. Las sesiones de Flask se basan en cookies, por lo que un sitio externo podría intentar inducir una acción autenticada.

**Recomendación:** añadir protección CSRF, por ejemplo con Flask-WTF, para todos los formularios POST; configurar cookies `Secure`, `HttpOnly` y `SameSite` en producción, y servir la aplicación exclusivamente mediante HTTPS.

### Intentos repetidos de inicio de sesión

El código no implementa límites de intentos ni demoras progresivas para el inicio de sesión.

**Recomendación:** añadir limitación de frecuencia en el endpoint de acceso y monitorizar intentos fallidos, evitando registrar contraseñas u otros secretos.

### Clave de sesión y modo de depuración

`FLASK_SECRET_KEY` permite configurar la clave de firma. Si no está definida, `app.py` genera una clave aleatoria al iniciar, lo que invalida las sesiones al reiniciar. La ejecución directa de `app.py` mantiene el modo debug desactivado; solo se activa explícitamente con `FLASK_DEBUG=1` o `FLASK_DEBUG=true`.

**Recomendación:** definir una clave larga, aleatoria y persistente en el entorno de despliegue. No activar debug en producción y ejecutar mediante un servidor WSGI de producción.

### Sesiones y cierre de sesión

La sesión guarda el ID y algunos datos visibles de la cuenta en la cookie firmada de Flask. La firma evita modificaciones no autorizadas, pero no cifra su contenido.

**Recomendación:** no guardar datos sensibles en la sesión, revisar la configuración de cookies para producción y rotar la clave si se sospecha que fue expuesta.

### Tareas anteriores al inicio de sesión

Los documentos creados antes de incorporar cuentas pueden carecer de `usuario_id`. La aplicación autenticada no los muestra ni los modifica al filtrar por el propietario; se necesitaría una migración controlada para asignarlos a una cuenta.

### Configuración de MongoDB

`MONGO_URI` y, opcionalmente, `USUARIOS_URI` deben mantenerse fuera del código. Una URI de MongoDB permite acceder a los datos según los permisos de la cuenta de base de datos.

**Recomendación:** restringir acceso de red en Atlas, usar credenciales únicas con permisos mínimos, mantener los secretos fuera de Git y rotarlos si se exponen.

### Carga de imágenes de perfil

La aplicación limita el tamaño total de las solicitudes y valida el tamaño y la firma binaria de las imágenes aceptadas. Esta comprobación identifica formatos comunes, pero no sustituye un servicio de análisis de archivos ni una política de retención si se habilitan cargas públicas en el futuro.

## Uso local

El servidor de desarrollo es para desarrollo local únicamente. No exponer ese servidor directamente a Internet ni activar debug en producción.
