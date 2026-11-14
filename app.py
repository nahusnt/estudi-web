"""Configura la aplicación Flask y conecta sus rutas con los modelos y repositorios."""

import base64
import os
from datetime import date, timedelta

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from modelos import CATEGORIAS, Categoria, RepositorioTareas, Tarea
from usuarios import RepositorioUsuarios, Usuario
# [Parte 3] Controles de seguridad reutilizables: sanitización XSS y mensajes de error.
from security_utils import MENSAJE_ERROR_DB, registrar_error_db

# Carga la configuracion local sin exponer credenciales en el codigo.
load_dotenv()
URI_ATLAS = os.getenv("MONGO_URI")

# Inicializa una conexion reutilizable con MongoDB.
cliente = MongoClient(URI_ATLAS)
db = cliente["lista_tareas_db"]
repo = RepositorioTareas(db)

# Las cuentas viven en otra base del mismo cluster. Si se define USUARIOS_URI
# se usa un cluster distinto solo para las cuentas.
URI_USUARIOS = os.getenv("USUARIOS_URI") or URI_ATLAS
cliente_usuarios = cliente if URI_USUARIOS == URI_ATLAS else MongoClient(URI_USUARIOS)
BASE_USUARIOS = os.getenv("USUARIOS_DB", "estudi_usuarios_db")
repo_usuarios = RepositorioUsuarios(cliente_usuarios[BASE_USUARIOS])

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY") or os.urandom(32)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024


# [EXCEPCIONES] Handler global de seguridad (red de seguridad / defense in depth):
# captura cualquier PyMongoError que no haya sido atrapado por los try/except de las
# rutas. Registra el detalle interno y devuelve un mensaje genérico al navegador.
@app.errorhandler(PyMongoError)
def manejar_error_mongodb(error):
    registrar_error_db(error, app.logger)
    return (MENSAJE_ERROR_DB, 500)


# [EXCEPCIONES] Handler 404 personalizado: no revela stack traces ni rutas internas.
# Se invoca cuando abort(404) descarta un ID inválido o cuando la ruta no existe.
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return ("La página que buscás no existe o no está disponible.", 404)


# [EXCEPCIONES] Handler 500 personalizado: mensaje genérico para cualquier error no
# capturado por las rutas, sin exponer el stack trace al usuario final.
@app.errorhandler(500)
def error_interno(error):
    registrar_error_db(error, app.logger)
    return (MENSAJE_ERROR_DB, 500)


ESTADOS = {"pendientes": False, "terminadas": True}
ORDENES = {"recientes", "antiguas", "titulo"}
SECCIONES = {"crear", "resumen", "ajustes", "perfil"}
MAX_FOTO_PERFIL_BYTES = 1024 * 1024

# Rutas accesibles sin sesion iniciada.
RUTAS_PUBLICAS = {"login", "registro", "static"}


@app.before_request
def exigir_sesion_iniciada():
    """Permite las rutas públicas y redirige al acceso si falta la sesión."""
    # Cualquier otra ruta exige una sesion activa; si no, redirige al login.
    if request.endpoint in RUTAS_PUBLICAS or request.endpoint is None:
        return None
    if not session.get("usuario_id"):
        return redirect(url_for("login"))
    return None


# Registra una cuenta nueva e inicia la sesion.
@app.route("/registro", methods=["GET", "POST"])
def registro():
    """Valida una cuenta nueva, la guarda y crea su sesión."""
    if request.method == "POST":
        correo = request.form.get("correo", "")
        nombre_usuario = request.form.get("nombre_usuario", "")
        # [XSS] La contraseña NO se sanitiza: se hashea tal cual (ver usuarios.py).
        # Escaparla alteraría su valor y rompería la verificación en el login.
        contrasena = request.form.get("contrasena", "")
        confirmacion = request.form.get("confirmacion", "")
        if not nombre_usuario.strip():
            flash("El nombre de usuario es obligatorio.", "error")
        elif contrasena != confirmacion:
            flash("Las contraseñas no coinciden.", "error")
        else:
            try:
                # Usuario() valida correo/nombre y [HASHING] hashea la contraseña.
                usuario = Usuario(
                    correo=correo,
                    contrasena=contrasena,
                    nombre_usuario=nombre_usuario,
                )
            except ValueError as error:
                flash(str(error), "error")
            else:
                try:
                    # [EXCEPCIONES] Consultas + inserción en MongoDB envueltas en try/except.
                    if repo_usuarios.buscar_por_correo(usuario.correo):
                        flash("Ese correo ya está registrado. Inicia sesión.", "error")
                    elif repo_usuarios.buscar_por_nombre_usuario(usuario.nombre_usuario):
                        flash("Ese nombre de usuario ya está en uso. Elige otro.", "error")
                    else:
                        guardado = repo_usuarios.guardar(usuario)
                        session["usuario_id"] = str(guardado.id)
                        session["usuario_correo"] = guardado.correo
                        session["usuario_nombre"] = guardado.nombre
                        session["usuario_nombre_usuario"] = guardado.nombre_usuario or ""
                        flash("¡Cuenta creada! Bienvenido/a a Estudi Web.", "ok")
                        return redirect(url_for("index"))
                except DuplicateKeyError:
                    # DuplicateKeyError es subclase de PyMongoError: va antes para dar
                    # un mensaje específico al usuario (correo/usuario duplicado).
                    flash("Ese correo o nombre de usuario ya está registrado.", "error")
                except PyMongoError as error:
                    # [EXCEPCIONES] Log interno + mensaje genérico al usuario (500).
                    registrar_error_db(error, app.logger)
                    return (MENSAJE_ERROR_DB, 500)
    return render_template("registro.html")


# Inicia la sesion de una cuenta existente.
@app.route("/login", methods=["GET", "POST"])
def login():
    """Autentica con correo o nombre de usuario y establece la sesión."""
    if request.method == "POST":
        identificador = request.form.get("identificador", request.form.get("correo", ""))
        contrasena = request.form.get("contrasena", "")
        try:
            # [EXCEPCIONES] La autenticación consulta MongoDB: se envuelve en try/except.
            usuario = repo_usuarios.autenticar(identificador, contrasena)
        except PyMongoError as error:
            registrar_error_db(error, app.logger)
            return (MENSAJE_ERROR_DB, 500)
        if usuario:
            session["usuario_id"] = str(usuario.id)
            session["usuario_correo"] = usuario.correo
            session["usuario_nombre"] = usuario.nombre
            session["usuario_nombre_usuario"] = usuario.nombre_usuario or ""
            return redirect(url_for("index"))
        flash("Correo, nombre de usuario o contraseña incorrectos.", "error")
    return render_template("login.html")


def convertir_foto_perfil_a_data_url(archivo):
    """Valida el tamaño y la firma de imagen antes de codificarla como data URL."""
    contenido = archivo.stream.read(MAX_FOTO_PERFIL_BYTES + 1)
    if len(contenido) > MAX_FOTO_PERFIL_BYTES:
        raise ValueError("La foto debe pesar 1 MB o menos.")
    if contenido.startswith(b"\x89PNG\r\n\x1a\n"):
        tipo = "image/png"
    elif contenido.startswith(b"\xff\xd8\xff"):
        tipo = "image/jpeg"
    elif contenido[:4] == b"RIFF" and contenido[8:12] == b"WEBP":
        tipo = "image/webp"
    else:
        raise ValueError("Usa una imagen PNG, JPG o WebP válida.")
    return f"data:{tipo};base64,{base64.b64encode(contenido).decode('ascii')}"


@app.route("/perfil", methods=["POST"])
def actualizar_perfil():
    """Valida y persiste los campos del perfil de la cuenta activa."""
    id_usuario = session["usuario_id"]
    try:
        # [EXCEPCIONES] La carga inicial del perfil consulta MongoDB.
        usuario = repo_usuarios.buscar_por_id(id_usuario)
    except PyMongoError as error:
        registrar_error_db(error, app.logger)
        return (MENSAJE_ERROR_DB, 500)
    if not usuario:
        session.clear()
        return redirect(url_for("login"))

    foto_perfil = usuario.foto_perfil
    archivo = request.files.get("foto_perfil")
    try:
        if request.form.get("eliminar_foto") == "1":
            foto_perfil = None
        if archivo and archivo.filename:
            foto_perfil = convertir_foto_perfil_a_data_url(archivo)
        # actualizar_perfil vuelve a aplicar [XSS] sanitizar en nombre y descripción.
        usuario.actualizar_perfil(
            nombre_usuario=request.form.get("nombre_usuario", ""),
            nombre=request.form.get("nombre", ""),
            descripcion=request.form.get("descripcion", ""),
            etiquetas=request.form.get("etiquetas", "").replace(",", " ").split(),
            foto_perfil=foto_perfil,
        )
        propietario = repo_usuarios.buscar_por_nombre_usuario(usuario.nombre_usuario)
        if propietario and str(propietario.id) != str(usuario.id):
            flash("Ese nombre de usuario ya está en uso. Elige otro.", "error")
            return redirect(url_for("index", seccion="perfil"))
        if not repo_usuarios.actualizar_perfil(id_usuario, usuario):
            session.clear()
            return redirect(url_for("login"))
    except DuplicateKeyError:
        # DuplicateKeyError (subclase de PyMongoError) va antes: mensaje específico.
        flash("Ese nombre de usuario ya está en uso. Elige otro.", "error")
    except ValueError as error:
        flash(str(error), "error")
    except PyMongoError as error:
        # [EXCEPCIONES] Log interno + mensaje genérico al usuario (500).
        registrar_error_db(error, app.logger)
        return (MENSAJE_ERROR_DB, 500)
    else:
        session["usuario_nombre"] = usuario.nombre
        session["usuario_nombre_usuario"] = usuario.nombre_usuario or ""
        flash("Perfil actualizado.", "ok")
    return redirect(url_for("index", seccion="perfil"))


# Cierra la sesion actual.
@app.route("/logout", methods=["POST"])
def logout():
    """Elimina todos los datos de sesión y vuelve al formulario de acceso."""
    session.clear()
    return redirect(url_for("login"))


def obtener_filtros(origen):
    """Normaliza los filtros recibidos y descarta valores fuera de las opciones válidas."""
    # [NoSQL] Defensa en profundidad: se fuerza cada valor a str() antes de usarlo en
    # las consultas de MongoDB, para descartar operadores inyectados ($ne, $gt, ...).
    # Además cada valor se valida contra un conjunto/regex cerrado.
    estado = str(origen.get("estado", ""))
    categoria = str(origen.get("categoria", ""))
    etiqueta = str(origen.get("etiqueta", "")).strip().lstrip("#").casefold()
    orden = str(origen.get("orden", "recientes"))
    return {
        "estado": estado if estado in {"", *ESTADOS} else "",
        "categoria": categoria if Categoria.es_valida(categoria) else "",
        "etiqueta": etiqueta if Tarea.etiqueta_valida(etiqueta) else "",
        "orden": orden if orden in ORDENES else "recientes",
    }


def obtener_seccion(origen):
    """Devuelve una sección permitida o la sección inicial de tareas."""
    seccion = str(origen.get("seccion", "crear"))
    return seccion if seccion in SECCIONES else "crear"


def validar_id_tarea(id_tarea):
    """Responde 404 antes de consultar MongoDB si el identificador no es válido."""
    # [IDOR] Validación estricta del ObjectId: un ID manipulado se descarta con 404
    # antes de tocar la base de datos.
    if not ObjectId.is_valid(id_tarea):
        abort(404)


# Muestra las tareas almacenadas.
@app.route('/')
def index():
    """Renderiza la sección solicitada y calcula los datos del resumen cuando hacen falta."""
    filtros = obtener_filtros(request.args)
    seccion = obtener_seccion(request.args)
    usuario_id = session.get("usuario_id")
    try:
        # [EXCEPCIONES] Todas las operaciones de MongoDB del listado van en un solo
        # bloque try/except: si cualquiera falla, se loguea y se devuelve 500 genérico.
        perfil = repo_usuarios.buscar_por_id(usuario_id) if seccion == "perfil" else None
        usuario_foto_perfil = (
            perfil.foto_perfil
            if perfil
            else repo_usuarios.obtener_foto_perfil(usuario_id)
        )
        tareas = []
        todas_las_tareas = []
        etiquetas_disponibles = []
        if seccion == "crear":
            # [IDOR] cargar_todas filtra por usuario_id: solo tareas del usuario activo.
            tareas = repo.cargar_todas(
                estado=ESTADOS.get(filtros["estado"]),
                categoria=filtros["categoria"],
                etiqueta=filtros["etiqueta"],
                orden=filtros["orden"],
                usuario_id=usuario_id,
            )
            etiquetas_disponibles = repo.listar_etiquetas()
        elif seccion == "resumen":
            todas_las_tareas = repo.cargar_todas(usuario_id=usuario_id)

        # Las métricas se calculan sobre las tareas del usuario obtenidas para el resumen.
        tareas_pendientes = sum(not tarea.completada for tarea in todas_las_tareas)
        tareas_terminadas = len(todas_las_tareas) - tareas_pendientes
        fecha_hoy = date.today()
        limite_proximas_tareas = fecha_hoy + timedelta(days=7)
        tareas_vencidas_lista = [
            tarea
            for tarea in todas_las_tareas
            if not tarea.completada
            and tarea.fecha_vencimiento is not None
            and tarea.fecha_vencimiento < fecha_hoy
        ]
        tareas_vencidas_lista.sort(
            key=lambda tarea: (tarea.fecha_vencimiento, tarea.titulo.casefold())
        )
        tareas_vencidas = len(tareas_vencidas_lista)
        tareas_por_vencer = [
            tarea
            for tarea in todas_las_tareas
            if not tarea.completada
            and tarea.fecha_vencimiento is not None
            and fecha_hoy <= tarea.fecha_vencimiento <= limite_proximas_tareas
        ]
        tareas_por_vencer.sort(
            key=lambda tarea: (tarea.fecha_vencimiento, tarea.titulo.casefold())
        )
        porcentaje_pendientes = round(
            tareas_pendientes / len(todas_las_tareas) * 100
        ) if todas_las_tareas else 0
        porcentaje_completadas = 100 - porcentaje_pendientes if todas_las_tareas else 0
        categorias_resumen = [
            {
                "nombre": categoria,
                "total": sum(tarea.categoria == categoria for tarea in todas_las_tareas),
            }
            for categoria in CATEGORIAS
        ]
    except PyMongoError as error:
        # [EXCEPCIONES] Error de MongoDB: log interno + mensaje genérico al usuario.
        registrar_error_db(error, app.logger)
        return (MENSAJE_ERROR_DB, 500)
    return render_template(
        "index.html",
        tareas=tareas,
        seccion=seccion,
        categorias=CATEGORIAS,
        etiquetas_disponibles=etiquetas_disponibles,
        filtros=filtros,
        total_tareas=len(todas_las_tareas),
        tareas_pendientes=tareas_pendientes,
        tareas_terminadas=tareas_terminadas,
        porcentaje_pendientes=porcentaje_pendientes,
        porcentaje_completadas=porcentaje_completadas,
        tareas_vencidas=tareas_vencidas,
        tareas_vencidas_lista=tareas_vencidas_lista[:5],
        tareas_por_vencer=tareas_por_vencer[:5],
        total_tareas_por_vencer=len(tareas_por_vencer),
        categorias_resumen=categorias_resumen,
        usuario_correo=session.get("usuario_correo", ""),
        usuario_nombre=session.get("usuario_nombre", ""),
        usuario_nombre_usuario=session.get("usuario_nombre_usuario", ""),
        usuario_foto_perfil=usuario_foto_perfil,
        perfil=perfil,
    )


# Crea una tarea a partir del formulario.
@app.route('/agregar', methods=['POST'])
def agregar():
    """Construye una tarea validada, la guarda para el usuario y conserva filtros al volver."""
    titulo = request.form.get('titulo', '')
    categoria = request.form.get("categoria", "")
    etiquetas_texto = request.form.get("etiquetas", "")
    etiquetas = etiquetas_texto.replace(",", " ").split()
    descripcion = request.form.get("descripcion", "")
    fecha_vencimiento = request.form.get("fecha_vencimiento", "")

    try:
        # Tarea() valida los campos y aplica [XSS] sanitizar en título y descripción.
        tarea = Tarea(
            titulo=titulo,
            categoria=categoria,
            etiquetas=etiquetas,
            descripcion=descripcion,
            fecha_vencimiento=fecha_vencimiento,
        )
    except ValueError as error:
        flash(str(error), "error")
    else:
        try:
            # [EXCEPCIONES + IDOR] La inserción se vincula al usuario de la sesión.
            repo.guardar(tarea, session["usuario_id"])
        except PyMongoError as error:
            registrar_error_db(error, app.logger)
            return (MENSAJE_ERROR_DB, 500)
    return redirect(
        url_for(
            "index",
            **obtener_filtros(request.form),
            seccion=obtener_seccion(request.form),
        )
    )


# Actualiza el estado de una tarea.
@app.route('/toggle/<id_tarea>', methods=['POST'])
def toggle_tarea(id_tarea):
    """Cambia el estado de una tarea propia después de validar su identificador."""
    validar_id_tarea(id_tarea)
    try:
        # [EXCEPCIONES + IDOR] La operación se restringe al usuario de la sesión.
        repo.cambiar_estado(id_tarea, session["usuario_id"])
    except PyMongoError as error:
        registrar_error_db(error, app.logger)
        return (MENSAJE_ERROR_DB, 500)
    return redirect(
        url_for(
            "index",
            **obtener_filtros(request.form),
            seccion=obtener_seccion(request.form),
        )
    )


# Elimina una tarea existente.
@app.route('/eliminar/<id_tarea>', methods=['POST'])
def eliminar_tarea(id_tarea):
    """Borra una tarea propia y vuelve a la lista con los filtros recibidos."""
    validar_id_tarea(id_tarea)
    try:
        # [EXCEPCIONES + IDOR] La operación se restringe al usuario de la sesión.
        repo.eliminar(id_tarea, session["usuario_id"])
    except PyMongoError as error:
        registrar_error_db(error, app.logger)
        return (MENSAJE_ERROR_DB, 500)
    return redirect(
        url_for(
            "index",
            **obtener_filtros(request.form),
            seccion=obtener_seccion(request.form),
        )
    )

# Permite iniciar el servidor integrado solo al ejecutar este archivo directamente.
if __name__ == '__main__':
    # [EXCEPCIONES] debug=False para la demo final: NUNCA exponer stack traces en
    # producción. El modo debug queda desactivado de forma permanente (se quitó el
    # override de FLASK_DEBUG) para cumplir la consigna de Parte 3.
    app.run(debug=False)
