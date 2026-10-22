from bson import ObjectId

CATEGORIAS = ("Trabajo", "Personal", "Estudio", "Otro")


# Representa una tarea y su formato de almacenamiento.
class Tarea:
    def __init__(
        self,
        titulo,
        completada=False,
        id_tarea=None,
        categoria="Personal",
        etiquetas=None,
    ):
        self.id = id_tarea
        self.titulo = titulo
        self.completada = completada
        self.categoria = categoria
        self.etiquetas = etiquetas or []

    def a_diccionario(self):
        """Convierte el objeto a un diccionario compatible con MongoDB"""
        return {
            "titulo": self.titulo,
            "completada": self.completada,
            "categoria": self.categoria,
            "etiquetas": self.etiquetas,
        }


# Centraliza las consultas y modificaciones de tareas en MongoDB.
class RepositorioTareas:
    def __init__(self, db):
        self.coleccion = db["tareas"]

    def guardar(self, tarea):
        resultado = self.coleccion.insert_one(tarea.a_diccionario())
        tarea.id = str(resultado.inserted_id)
        return tarea

    def cargar_todas(self, estado=None, categoria=None, etiqueta=None, orden="recientes"):
        # Recupera solo los campos usados por la vista y evita una lista intermedia.
        filtros = {}
        if estado is not None:
            filtros["completada"] = estado
        if categoria:
            if categoria == "Personal":
                filtros["$or"] = [
                    {"categoria": categoria},
                    {"categoria": {"$exists": False}},
                ]
            else:
                filtros["categoria"] = categoria
        if etiqueta:
            filtros["etiquetas"] = etiqueta

        ordenes = {
            "recientes": [("_id", -1)],
            "antiguas": [("_id", 1)],
            "titulo": [("titulo", 1), ("_id", -1)],
        }
        documentos = self.coleccion.find(
            filtros,
            {"titulo": 1, "completada": 1, "categoria": 1, "etiquetas": 1},
        ).sort(ordenes[orden])
        return [
            Tarea(
                titulo=doc["titulo"],
                completada=doc.get("completada", False),
                id_tarea=str(doc["_id"]),
                categoria=doc.get("categoria", "Personal"),
                etiquetas=doc.get("etiquetas", []),
            )
            for doc in documentos
        ]

    def listar_etiquetas(self):
        return sorted(self.coleccion.distinct("etiquetas"), key=str.casefold)

    def cambiar_estado(self, id_tarea):
        # Invierte el estado de forma atomica en una sola operacion de MongoDB.
        self.coleccion.update_one(
            {"_id": ObjectId(id_tarea)},
            [
                {
                    "$set": {
                        "completada": {
                            "$not": [{"$ifNull": ["$completada", False]}]
                        }
                    }
                }
            ],
        )

    def eliminar(self, id_tarea):
        self.coleccion.delete_one({"_id": ObjectId(id_tarea)})
