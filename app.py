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


@app.errorhandler(PyMongoError)
def manejar_error_mongodb(error):
    app.logger.exception("Error interno al procesar una operación de MongoDB.")
    return (
        "Ocurrió un error interno al procesar su solicitud. "
        "Intente nuevamente más tarde.",
        500,
    )


ESTADOS = {"pendientes": False, "terminadas": True}
ORDENES = {"recientes", "antiguas", "titulo"}
SECCIONES = {"crear", "resumen", "ajustes", "perfil"}
MAX_FOTO_PERFIL_BYTES = 1024 * 1024

# Rutas accesibles sin sesion iniciada.
RUTAS_PUBLICAS = {"login", "registro", "static"}


@app.before_request
def exigir_sesion_iniciada():
    # Cualquier otra ruta exige una sesion activa; si no, redirige al login.
    if request.endpoint in RUTAS_PUBLICAS or request.endpoint is None:
        return None
    if not session.get("usuario_id"):
        return redirect(url_for("login"))
    return None


# Registra una cuenta nueva e inicia la sesion.
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        correo = request.form.get("correo", "")
        nombre_usuario = request.form.get("nombre_usuario", "")
        contrasena = request.form.get("contrasena", "")
        confirmacion = request.form.get("confirmacion", "")
        if not nombre_usuario.strip():
            flash("El nombre de usuario es obligatorio.", "error")
        elif contrasena != confirmacion:
            flash("Las contraseñas no coinciden.", "error")
        else:
            try:
                usuario = Usuario(
                    correo=correo,
                    contrasena=contrasena,
                    nombre_usuario=nombre_usuario,
                )
            except ValueError as error:
                flash(str(error), "error")
            else:
                if repo_usuarios.buscar_por_correo(usuario.correo):
                    flash("Ese correo ya está registrado. Inicia sesión.", "error")
                elif repo_usuarios.buscar_por_nombre_usuario(usuario.nombre_usuario):
                    flash("Ese nombre de usuario ya está en uso. Elige otro.", "error")
                else:
                    try:
                        guardado = repo_usuarios.guardar(usuario)
                    except DuplicateKeyError:
                        flash("Ese correo o nombre de usuario ya está registrado.", "error")
                    else:
                        session["usuario_id"] = str(guardado.id)
                        session["usuario_correo"] = guardado.correo
                        session["usuario_nombre"] = guardado.nombre
                        session["usuario_nombre_usuario"] = guardado.nombre_usuario or ""
                        flash("¡Cuenta creada! Bienvenido/a a Estudi Web.", "ok")
                        return redirect(url_for("index"))
    return render_template("registro.html")


# Inicia la sesion de una cuenta existente.
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = repo_usuarios.autenticar(
            request.form.get("identificador", request.form.get("correo", "")),
            request.form.get("contrasena", ""),
        )
        if usuario:
            session["usuario_id"] = str(usuario.id)
            session["usuario_correo"] = usuario.correo
            session["usuario_nombre"] = usuario.nombre
            session["usuario_nombre_usuario"] = usuario.nombre_usuario or ""
            return redirect(url_for("index"))
        flash("Correo, nombre de usuario o contraseña incorrectos.", "error")
    return render_template("login.html")


def convertir_foto_perfil_a_data_url(archivo):
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
    id_usuario = session["usuario_id"]
    usuario = repo_usuarios.buscar_por_id(id_usuario)
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
        flash("Ese nombre de usuario ya está en uso. Elige otro.", "error")
    except ValueError as error:
        flash(str(error), "error")
    else:
        session["usuario_nombre"] = usuario.nombre
        session["usuario_nombre_usuario"] = usuario.nombre_usuario or ""
        flash("Perfil actualizado.", "ok")
    return redirect(url_for("index", seccion="perfil"))


# Cierra la sesion actual.
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


def obtener_filtros(origen):
    estado = origen.get("estado", "")
    categoria = origen.get("categoria", "")
    etiqueta = origen.get("etiqueta", "").strip().lstrip("#").casefold()
    orden = origen.get("orden", "recientes")
    return {
        "estado": estado if estado in {"", *ESTADOS} else "",
        "categoria": categoria if Categoria.es_valida(categoria) else "",
        "etiqueta": etiqueta if Tarea.etiqueta_valida(etiqueta) else "",
        "orden": orden if orden in ORDENES else "recientes",
    }


def obtener_seccion(origen):
    seccion = origen.get("seccion", "crear")
    return seccion if seccion in SECCIONES else "crear"


def validar_id_tarea(id_tarea):
    if not ObjectId.is_valid(id_tarea):
        abort(404)


# Muestra las tareas almacenadas.
@app.route('/')
def index():
    filtros = obtener_filtros(request.args)
    seccion = obtener_seccion(request.args)
    tareas = []
    todas_las_tareas = []
    etiquetas_disponibles = []
    usuario_id = session.get("usuario_id")
    perfil = repo_usuarios.buscar_por_id(usuario_id) if seccion == "perfil" else None
    usuario_foto_perfil = (
        perfil.foto_perfil
        if perfil
        else repo_usuarios.obtener_foto_perfil(usuario_id)
    )
    if seccion == "crear":
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
    titulo = request.form.get('titulo', '')
    categoria = request.form.get("categoria", "")
    etiquetas_texto = request.form.get("etiquetas", "")
    etiquetas = etiquetas_texto.replace(",", " ").split()
    descripcion = request.form.get("descripcion", "")
    fecha_vencimiento = request.form.get("fecha_vencimiento", "")

    try:
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
        repo.guardar(tarea, session["usuario_id"])
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
    validar_id_tarea(id_tarea)
    repo.cambiar_estado(id_tarea, session["usuario_id"])
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
    validar_id_tarea(id_tarea)
    repo.eliminar(id_tarea, session["usuario_id"])
    return redirect(
        url_for(
            "index",
            **obtener_filtros(request.form),
            seccion=obtener_seccion(request.form),
        )
    )

if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG", "").casefold() in {"1", "true"})
