import re

from bson import ObjectId


class Categoria:
    NOMBRES_VALIDOS = ("Trabajo", "Personal", "Estudio", "Otro")

    def __init__(self, nombre):
        if not self.es_valida(nombre):
            raise ValueError("Selecciona una categoría válida.")
        self.__nombre = nombre

    @property
    def nombre(self):
        return self.__nombre

    @classmethod
    def es_valida(cls, nombre):
        return nombre in cls.NOMBRES_VALIDOS


CATEGORIAS = Categoria.NOMBRES_VALIDOS


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
        titulo = titulo.strip() if isinstance(titulo, str) else ""
        if not titulo or len(titulo) > 120:
            raise ValueError(
                "El título es obligatorio y debe tener 120 caracteres como máximo."
            )

        self.__id = id_tarea
        self.__titulo = titulo
        self.__completada = completada
        self.__categoria = (
            categoria if isinstance(categoria, Categoria) else Categoria(categoria)
        )
        self.__etiquetas = self._validar_etiquetas(etiquetas)

    @staticmethod
    def etiqueta_valida(etiqueta):
        return re.fullmatch(r"[\w-]{1,20}", etiqueta) is not None

    @classmethod
    def _validar_etiquetas(cls, etiquetas):
        etiquetas_normalizadas = []
        for etiqueta in etiquetas or []:
            if not isinstance(etiqueta, str):
                raise ValueError(
                    "Usa hasta 5 etiquetas de 20 caracteres; puedes escribirlas como #trabajo."
                )
            normalizada = etiqueta.lstrip("#").casefold()
            if normalizada not in etiquetas_normalizadas:
                etiquetas_normalizadas.append(normalizada)

        if len(etiquetas_normalizadas) > 5 or any(
            not cls.etiqueta_valida(etiqueta) for etiqueta in etiquetas_normalizadas
        ):
            raise ValueError(
                "Usa hasta 5 etiquetas de 20 caracteres; puedes escribirlas como #trabajo."
            )
        return etiquetas_normalizadas

    @property
    def id(self):
        return self.__id

    @property
    def titulo(self):
        return self.__titulo

    @property
    def completada(self):
        return self.__completada

    @property
    def categoria(self):
        return self.__categoria.nombre

    @property
    def etiquetas(self):
        return self.__etiquetas.copy()

    def asignar_id(self, id_tarea):
        self.__id = id_tarea

    def a_diccionario(self):
        """Convierte el objeto a un diccionario compatible con MongoDB"""
        return {
            "titulo": self.titulo,
            "completada": self.completada,
            "categoria": self.categoria,
            "etiquetas": self.__etiquetas.copy(),
        }


# Centraliza las consultas y modificaciones de tareas en MongoDB.
class RepositorioTareas:
    def __init__(self, db):
        self.__coleccion = db["tareas"]
        self.__coleccion.create_index("titulo")

    def guardar(self, tarea):
        resultado = self.__coleccion.insert_one(tarea.a_diccionario())
        tarea.asignar_id(str(resultado.inserted_id))
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
        documentos = self.__coleccion.find(
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
        return sorted(self.__coleccion.distinct("etiquetas"), key=str.casefold)

    def cambiar_estado(self, id_tarea):
        # Invierte el estado de forma atomica en una sola operacion de MongoDB.
        self.__coleccion.update_one(
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
        self.__coleccion.delete_one({"_id": ObjectId(id_tarea)})
