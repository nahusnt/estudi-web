import os

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, url_for
from pymongo import MongoClient

from modelos import RepositorioTareas, Tarea

# Carga la configuracion local sin exponer credenciales en el codigo.
load_dotenv()
URI_ATLAS = os.getenv("MONGO_URI")

# Inicializa una conexion reutilizable con MongoDB.
cliente = MongoClient(URI_ATLAS)
db = cliente["lista_tareas_db"]
repo = RepositorioTareas(db)
app = Flask(__name__)


def validar_id_tarea(id_tarea):
    if not ObjectId.is_valid(id_tarea):
        abort(404)


# Muestra las tareas almacenadas.
@app.route('/')
def index():
    tareas = repo.cargar_todas()
    return render_template('index.html', tareas=tareas)


# Crea una tarea a partir del formulario.
@app.route('/agregar', methods=['POST'])
def agregar():
    titulo = request.form.get('titulo', '').strip()
    if titulo:
        nueva_tarea = Tarea(titulo=titulo)
        repo.guardar(nueva_tarea)
    return redirect(url_for('index'))


# Actualiza el estado de una tarea.
@app.route('/toggle/<id_tarea>', methods=['POST'])
def toggle_tarea(id_tarea):
    validar_id_tarea(id_tarea)
    repo.cambiar_estado(id_tarea)
    return redirect(url_for('index'))


# Elimina una tarea existente.
@app.route('/eliminar/<id_tarea>', methods=['POST'])
def eliminar_tarea(id_tarea):
    validar_id_tarea(id_tarea)
    repo.eliminar(id_tarea)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)