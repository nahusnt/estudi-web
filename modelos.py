from bson import ObjectId


# Representa una tarea y su formato de almacenamiento.
class Tarea:
    def __init__(self, titulo, completada=False, id_tarea=None):
        self.id = id_tarea
        self.titulo = titulo
        self.completada = completada

    def a_diccionario(self):
        """Convierte el objeto a un diccionario compatible con MongoDB"""
        return {
            "titulo": self.titulo,
            "completada": self.completada
        }


# Centraliza las consultas y modificaciones de tareas en MongoDB.
class RepositorioTareas:
    def __init__(self, db):
        self.coleccion = db["tareas"]

    def guardar(self, tarea):
        resultado = self.coleccion.insert_one(tarea.a_diccionario())
        tarea.id = str(resultado.inserted_id)
        return tarea

    def cargar_todas(self):
        # Recupera solo los campos usados por la vista y evita una lista intermedia.
        documentos = self.coleccion.find({}, {"titulo": 1, "completada": 1})
        return [
            Tarea(
                titulo=doc["titulo"],
                completada=doc.get("completada", False),
                id_tarea=str(doc["_id"]),
            )
            for doc in documentos
        ]

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
