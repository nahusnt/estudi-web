import os
import re

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from pymongo import MongoClient

from modelos import CATEGORIAS, RepositorioTareas, Tarea

# Carga la configuracion local sin exponer credenciales en el codigo.
load_dotenv()
URI_ATLAS = os.getenv("MONGO_URI")

# Inicializa una conexion reutilizable con MongoDB.
cliente = MongoClient(URI_ATLAS)
db = cliente["lista_tareas_db"]
repo = RepositorioTareas(db)
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY") or os.urandom(32)

ESTADOS = {"pendientes": False, "terminadas": True}
ORDENES = {"recientes", "antiguas", "titulo"}


def etiqueta_valida(etiqueta):
    return re.fullmatch(r"[\w-]{1,20}", etiqueta) is not None


def obtener_filtros(origen):
    estado = origen.get("estado", "")
    categoria = origen.get("categoria", "")
    etiqueta = origen.get("etiqueta", "").strip().lstrip("#").casefold()
    orden = origen.get("orden", "recientes")
    return {
        "estado": estado if estado in {"", *ESTADOS} else "",
        "categoria": categoria if categoria in CATEGORIAS else "",
        "etiqueta": etiqueta if etiqueta_valida(etiqueta) else "",
        "orden": orden if orden in ORDENES else "recientes",
    }


def validar_id_tarea(id_tarea):
    if not ObjectId.is_valid(id_tarea):
        abort(404)


# Muestra las tareas almacenadas.
@app.route('/')
def index():
    filtros = obtener_filtros(request.args)
    tareas = repo.cargar_todas(
        estado=ESTADOS.get(filtros["estado"]),
        categoria=filtros["categoria"],
        etiqueta=filtros["etiqueta"],
        orden=filtros["orden"],
    )
    return render_template(
        "index.html",
        tareas=tareas,
        categorias=CATEGORIAS,
        etiquetas_disponibles=repo.listar_etiquetas(),
        filtros=filtros,
    )


# Crea una tarea a partir del formulario.
@app.route('/agregar', methods=['POST'])
def agregar():
    titulo = request.form.get('titulo', '').strip()
    categoria = request.form.get("categoria", "")
    etiquetas_texto = request.form.get("etiquetas", "")
    etiquetas = [
        etiqueta.lstrip("#").casefold()
        for etiqueta in etiquetas_texto.replace(",", " ").split()
    ]
    etiquetas = list(dict.fromkeys(etiquetas))

    if not titulo or len(titulo) > 120:
        flash("El título es obligatorio y debe tener 120 caracteres como máximo.", "error")
    elif categoria not in CATEGORIAS:
        flash("Selecciona una categoría válida.", "error")
    elif len(etiquetas) > 5 or any(
        not etiqueta_valida(etiqueta) for etiqueta in etiquetas
    ):
        flash("Usa hasta 5 etiquetas de 20 caracteres; puedes escribirlas como #trabajo.", "error")
    else:
        repo.guardar(Tarea(titulo=titulo, categoria=categoria, etiquetas=etiquetas))
    return redirect(url_for("index", **obtener_filtros(request.form)))


# Actualiza el estado de una tarea.
@app.route('/toggle/<id_tarea>', methods=['POST'])
def toggle_tarea(id_tarea):
    validar_id_tarea(id_tarea)
    repo.cambiar_estado(id_tarea)
    return redirect(url_for("index", **obtener_filtros(request.form)))


# Elimina una tarea existente.
@app.route('/eliminar/<id_tarea>', methods=['POST'])
def eliminar_tarea(id_tarea):
    validar_id_tarea(id_tarea)
    repo.eliminar(id_tarea)
    return redirect(url_for("index", **obtener_filtros(request.form)))

if __name__ == '__main__':
    app.run(debug=True)