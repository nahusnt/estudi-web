"""Funciones reutilizables de seguridad para la Parte 3 (Secure Coding y Sanitización).

Agrupa los controles defensivos que se aplican de forma transversal en la app:

- ``sanitizar``: limpia texto libre del usuario contra XSS ANTES de guardarlo en MongoDB.
- ``MENSAJE_ERROR_DB``: mensaje genérico que se devuelve al usuario ante cualquier fallo
  de MongoDB (nunca revela detalles técnicos, consultas ni stack traces).
- ``registrar_error_db``: imprime el detalle real del error SOLO en la consola del servidor,
  usando el formato que pide la consigna de Parte 3.

Estos helpers se usan desde ``app.py``, ``modelos.py`` y ``usuarios.py`` para mantener una
sola fuente de verdad para los controles de seguridad.
"""

import html  # [XSS] Librería nativa de Python para escapar caracteres especiales.

# [EXCEPCIONES] Mensaje genérico que ve el usuario ante cualquier fallo de MongoDB.
# No contiene información de conexión, nombres de colecciones, consultas ni stack trace.
MENSAJE_ERROR_DB = (
    "Ocurrió un error interno al procesar su solicitud. "
    "Intente nuevamente más tarde."
)


def sanitizar(texto):
    """Sanitiza texto libre del usuario contra XSS antes de guardarlo en MongoDB.

    [XSS] Control de Cross-Site Scripting (Parte 3, punto 1):

    1. ``html.unescape`` normaliza entidades HTML preexistentes en el texto. Esto sirve
       cuando un perfil o tarea se re-edita y el valor ya viene escapado de un guardado
       anterior: al des-escapar primero se parte de texto plano y se evita el doble
       escape (que mostraría ``&amp;lt;`` en pantalla).
    2. ``html.escape`` convierte los caracteres especiales (``<``, ``>``, ``&``,
       ``"`` y ``'``) en entidades HTML seguras (``&lt;``, ``&gt;``, ``&amp;`` ...),
       de modo que el navegador los muestre como texto y no ejecute etiquetas ni
       scripts. Es la librería nativa que pide la consigna.

    El resultado es **idempotente**: ``sanitizar(sanitizar(x)) == sanitizar(x)``, por lo
    que re-editar un campo ya escapado no lo degrada.

    Devuelve una cadena vacía si el valor no es texto (``None``, números, listas) para
    no romper las validaciones de los modelos.
    """
    if not isinstance(texto, str):
        return ""
    # 1) Des-escapar para partir de texto plano y evitar doble escape en reediciones.
    plano = html.unescape(texto)
    # 2) Escapar a entidades HTML seguras antes de persistir en MongoDB.
    #    quote=True (por defecto) también escapa comillas, protegiendo los atributos HTML.
    return html.escape(plano, quote=True)


def registrar_error_db(error, logger=None):
    """Loguea el detalle real de un error de MongoDB SOLO en la consola del servidor.

    [EXCEPCIONES] Manejo seguro de excepciones (Parte 3, punto 3):

    El usuario final nunca ve este mensaje: se imprime acá (y opcionalmente en el
    ``logger`` de Flask) para que el equipo de desarrollo pueda diagnosticar el problema.
    Usa el formato solicitado por la consigna de Parte 3.

    - ``error``: la excepción capturada (``PyMongoError``).
    - ``logger``: logger de Flask (``app.logger``) para integrar con los tests y los
      logs del servidor. Es opcional: si no se pasa, solo se usa ``print``.
    """
    detalle = f"[LOG DE SEGURIDAD - ERROR DB]: {error}"
    # Consigna Parte 3: el error real se loguea en la consola del servidor.
    print(detalle)
    # logging adicional (lo usan los tests y el servidor WSGI en producción).
    if logger is not None:
        logger.error(detalle)
