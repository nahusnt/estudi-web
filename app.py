import os
from datetime import date, timedelta

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from pymongo import MongoClient

from modelos import CATEGORIAS, Categoria, RepositorioTareas, Tarea

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
SECCIONES = {"crear", "resumen", "ajustes"}


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
    if seccion == "crear":
        tareas = repo.cargar_todas(
            estado=ESTADOS.get(filtros["estado"]),
            categoria=filtros["categoria"],
            etiqueta=filtros["etiqueta"],
            orden=filtros["orden"],
        )
        etiquetas_disponibles = repo.listar_etiquetas()
    elif seccion == "resumen":
        todas_las_tareas = repo.cargar_todas()

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
        repo.guardar(tarea)
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
    repo.cambiar_estado(id_tarea)
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
    repo.eliminar(id_tarea)
    return redirect(
        url_for(
            "index",
            **obtener_filtros(request.form),
            seccion=obtener_seccion(request.form),
        )
    )

if __name__ == '__main__':
    app.run(debug=True)