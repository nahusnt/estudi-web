from flask import Flask, abort, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from modelos import Tarea, RepositorioTareas

app = Flask(__name__)


import os
from dotenv import load_dotenv

load_dotenv()  
URI_ATLAS = os.getenv("MONGO_URI")

cliente = MongoClient(URI_ATLAS)
db = cliente['lista_tareas_db']
repo = RepositorioTareas(db)


def validar_id_tarea(id_tarea):
    if not ObjectId.is_valid(id_tarea):
        abort(404)

@app.route('/')
def index():
    tareas = repo.cargar_todas()
    return render_template('index.html', tareas=tareas)

@app.route('/agregar', methods=['POST'])
def agregar():
    titulo = request.form.get('titulo', '').strip()
    if titulo:
        nueva_tarea = Tarea(titulo=titulo)
        repo.guardar(nueva_tarea)
    return redirect(url_for('index'))


@app.route('/toggle/<id_tarea>', methods=['POST'])
def toggle_tarea(id_tarea):
    validar_id_tarea(id_tarea)
    repo.cambiar_estado(id_tarea)
    return redirect(url_for('index'))

@app.route('/eliminar/<id_tarea>', methods=['POST'])
def eliminar_tarea(id_tarea):
    validar_id_tarea(id_tarea)
    repo.eliminar(id_tarea)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)