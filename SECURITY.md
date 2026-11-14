# Seguridad — Estudi Web

Modelado de amenazas del Proyecto Integrador Final "EXPOTÉCNICA 2026" (Seguridad
Informática, E.P.E.T. N°1 UNESCO). Estudi Web es una aplicación de **lista de tareas**
(Grupo 1 / Opción D de la consigna): los usuarios crean una cuenta, inician sesión y
gestionan sus propias tareas, categorías, etiquetas y perfil.

Este documento identifica las **3 amenazas** principales del proyecto, su **Impacto** y la
**Mitigación / Hardening** aplicada en el código (Parte 3 - Desarrollo Seguro). Al final
se incluye un anexo con los controles implementados y los riesgos adicionales que quedan
como trabajo futuro. La configuración de red de MongoDB Atlas también debe limitarse desde
el panel del proveedor.

---

## 1. Amenaza 1: Acceso o modificación de tareas ajenas (IDOR / Broken Access Control)

- **Descripción del Riesgo:** un usuario autenticado manipula el identificador de una
  tarea en las rutas HTTP (`/toggle/<id_tarea>` y `/eliminar/<id_tarea>`) para marcar,
  eliminar o (vía listado) ver tareas que pertenecen a otro usuario. Es la vulnerabilidad
  típica IDOR (Insecure Direct Object Reference) / Broken Access Control, que corresponde
  al ejemplo de la Opción D (Grupo 1 - Lista de Tareas) de la consigna.

- **Impacto:** manipulación, eliminación o visualización de información privada de otros
  usuarios. Se viola la confidencialidad e integridad de los datos de cada cuenta y se
  pierde el aislamiento entre usuarios.

- **Mitigación / Hardening (aplicada en código):**
  - **Verificación de propiedad en el backend (Flask):** todas las operaciones de tareas
    (`cambiar_estado`, `eliminar`, `cargar_todas`) filtran la consulta de MongoDB por
    `usuario_id` tomado **de la sesión activa**, nunca de la petición del cliente. Ver
    `modelos.py` (métodos de `RepositorioTareas`) y `app.py` (pasaje de
    `session["usuario_id"]`).
  - **Validación estricta del identificador:** `validar_id_tarea` (`app.py`) descarta con
    un `404` cualquier ID que no sea un `ObjectId` válido, antes de tocar la base de datos.
  - **Sesión obligatoria:** `@app.before_request` exige una sesión iniciada para toda
    ruta que no sea `/login`, `/registro` o recursos estáticos.
  - *Prueba:* ver `tests/test_app.py` → `test_id_invalido_responde_404_sin_modificar_datos`
    y `test_toggle_cambia_estado_de_tarea` (que confirma el pasaje del `usuario_id`).

---

## 2. Amenaza 2: Cross-Site Scripting (XSS) en campos de texto libre

- **Descripción del Riesgo:** un usuario ingresa etiquetas HTML o código JavaScript
  malicioso (por ejemplo `<script>alert('Hackeado')</script>`) en un campo de texto libre
  —título o descripción de una tarea, o nombre/descripción de perfil— y la aplicación lo
  guarda y muestra tal cual en la vista. El navegador de quien vea esa tarea o perfil
  ejecutaría el script.

- **Impacto:** ejecución de scripts no deseados en el navegador de otros usuarios que
  naveguen las tareas o el perfil afectado, permitiendo robo de sesión, defacement o
  acciones en nombre de la víctima.

- **Mitigación / Hardening (aplicada en código):**
  - **Sanitización en la entrada con la librería nativa `html`:** los validadores de
    `Tarea` (título, descripción) y de `Usuario` (nombre, descripción) aplican
    `html.escape()` **antes de guardar en MongoDB**, vía el helper `sanitizar()` de
    `security_utils.py`. No se confía solo en el autoescape de Jinja2.
  - **Helper idempotente:** `sanitizar(texto) = html.escape(html.unescape(texto.strip()))`
    des-escapa primero y escapa después, para que re-editar un perfil ya sanitizado no
    produzca doble escape (`&amp;lt;`) ni degrade el valor.
  - **Renderizado coherente:** como el texto se guarda ya escapado, las plantillas lo
    muestran con `|safe` (porque ya es seguro), evitando el doble escape en la vista.
  - **La contraseña NUNCA se sanitiza:** se hashea tal cual (ver Amenaza 3 / anexo);
    escaparla alteraría su valor y rompería el login.
  - **Campos no-libres protegidos por regex/whitelist:** `nombre_usuario`, `correo`,
    `etiquetas`, `categoría`, `estado`, `orden` y `fecha_vencimiento` se validan con
    expresiones regulares estrictas o conjuntos cerrados, por lo que no pueden contener
    HTML y no requieren escape.
  - *Prueba:* ver `tests/test_app.py` → `test_texto_de_tarea_se_sanitiza_en_la_entrada` y
    `test_sanitizar_es_idempotente_y_seguro`.

---

## 3. Amenaza 3: Exposición de Stack Trace y errores de MongoDB

- **Descripción del Riesgo:** si ocurre un error en la conexión con MongoDB o falla una
  consulta, Flask por defecto puede mostrar una pantalla de depuración (stack trace) con
  rutas internas del servidor, versiones de librerías, nombres de colecciones y estructura
  de la base de datos. Esto entrega información valiosa a un atacante.

- **Impacto:** fuga de información técnica (estructura de la BD, rutas del servidor,
  versiones) que facilita ataques posteriores dirigidos. También degrada la experiencia
  del usuario final con mensajes incomprensibles.

- **Mitigación / Hardening (aplicada en código):**
  - **`try/except` por operación:** cada operación de MongoDB en las rutas
    (`buscar_por_id`, `cargar_todas`, `guardar`, `cambiar_estado`, `eliminar`,
    `actualizar_perfil`, `autenticar`, `buscar_por_correo`, etc.) está envuelta en
    `try/except PyMongoError`. Ver `app.py`.
  - **Mensaje genérico al usuario:** ante cualquier error de BD se devuelve
    `"Ocurrió un error interno al procesar su solicitud. Intente nuevamente más tarde."`
    con código `500`, sin detalles técnicos.
  - **Log interno con formato de seguridad:** el error real se registra SOLO en la consola
    del servidor con `print(f"[LOG DE SEGURIDAD - ERROR DB]: {error}")` (y en el `logger`
    de Flask), vía `registrar_error_db()` de `security_utils.py`.
  - **Handlers personalizados 404 y 500:** `@app.errorhandler(404)` y
    `@app.errorhandler(500)` devuelven mensajes personalizados que **no revelan stack
    traces**. El handler global `@app.errorhandler(PyMongoError)` actúa como red de
    seguridad (defense in depth) para cualquier excepción no atrapada.
  - **`debug=False` hardcoded:** `app.run(debug=False)` para la demo final; se eliminó el
    override de `FLASK_DEBUG` para cumplir la consigna de Parte 3.
  - *Prueba:* ver `tests/test_app.py` → `test_error_de_mongodb_devuelve_mensaje_generico_y_registra_detalle`,
    `test_404_no_revela_stack_trace` y `test_app_run_debug_false_en_fuente`.

---

## Anexo A — Controles implementados (transversales)

- **Hashing de contraseñas (Parte 3, punto 2):** las contraseñas se guardan como hashes
  irreversibles generados con `werkzeug.security.generate_password_hash` y se verifican
  con `check_password_hash`. Nunca se almacenan en texto plano (campo `contrasena_hash`).
  Se entrega además `migrar_contrasenas.py` como red de seguridad para detectar y reparar
  cuentas legacy con contraseña plana.
- **Defensa en profundidad anti-inyección NoSQL:** los parámetros de filtro
  (`estado`, `categoría`, `etiqueta`, `orden`, `sección`) se fuerzan a `str()` y se
  validan contra conjuntos/regex cerrados antes de usarse en consultas, descartando
  operadores inyectados (`$ne`, `$gt`, ...). Ninguna consulta recibe un dict crudo del
  cliente.
- **Índices únicos de MongoDB** sobre `correo` y `usuario_normalizado` (unicidad de
  cuenta).
- **Sesión obligatoria** para todas las rutas de trabajo; solo `/login`, `/registro` y
  `/static` son públicas.
- **Carga de imágenes de perfil** limitada a 1 MB y validada por firma binaria (PNG, JPEG,
  WebP); `MAX_CONTENT_LENGTH` limita las solicitudes a 2 MB.
- **`.env` excluido de Git** por `.gitignore`; `.env.example` contiene solo marcadores.
- **Pruebas automatizadas** (51 tests) que cubren validación, XSS, hashing, manejo de
  errores, 404 y `debug=False`, sin conectarse a MongoDB (repositorios simulados).

## Anexo B — Riesgos adicionales / trabajo futuro

Estos puntos no son objeto de la Parte 3 pero deben atenderse antes de desplegar en
producción:

- **Protección CSRF:** los formularios usan POST pero no tokens CSRF. Recomendación:
  añadir Flask-WTF para todos los formularios POST; configurar cookies `Secure`,
  `HttpOnly` y `SameSite`; servir solo por HTTPS.
- **Limitación de intentos de login:** no hay rate limiting. Recomendación: limitar la
  frecuencia del endpoint `/login` y monitorizar intentos fallidos sin registrar secretos.
- **Clave de sesión persistente:** definir `FLASK_SECRET_KEY` larga y aleatoria en el
  entorno de despliegue; no guardar datos sensibles en la cookie de sesión; rotar la clave
  si se sospecha exposición.
- **Tareas anteriores a las cuentas:** los documentos sin `usuario_id` requieren una
  migración controlada para asociarlos a una cuenta.
- **Configuración de MongoDB Atlas:** restringir acceso de red, credenciales con permisos
  mínimos, mantener secretos fuera de Git y rotarlos si se exponen.
- **Carga de imágenes pública:** si se habilita, sumar un servicio de análisis de
  archivos y una política de retención (la validación actual por firma no reemplaza eso).

## Controles de la simulación de red

La red de Cisco Packet Tracer se documenta por separado en [REDES.md](./REDES.md). Sus
ACL y segmentación representan controles complementarios contra el acceso no autorizado a
servidores y a la red de base de datos simulada. No constituyen una configuración de red
de producción ni reemplazan la lista de acceso de red de MongoDB Atlas: la aplicación real
debe protegerse con reglas de red y credenciales configuradas en el proveedor de MongoDB.

La ACL de invitados bloquea el acceso a las subredes de servidores y base de datos; la ACL
de base de datos permite TCP/27017 únicamente desde el host de aplicación simulado y
deniega otros orígenes hacia el host de datos. Estas reglas se relacionan con el riesgo de
acceso de red no autorizado a los datos. El acceso SSH v2 y el banner del router reducen
la exposición de la administración del dispositivo de laboratorio; no se confirma en la
evidencia el cifrado de las contraseñas de configuración.

Los resultados y límites de estas pruebas están en la sección **Integración Redes +
Seguridad** de [REDES.md](./REDES.md). Packet Tracer no ejecuta Flask ni MongoDB real.

## Uso local

El servidor de desarrollo es para desarrollo local únicamente. No exponer ese servidor
directamente a Internet ni activar `debug` en producción (la demo corre con
`app.run(debug=False)`).
