"""Define las categorías, el modelo de tareas y su acceso a MongoDB."""

import re
from datetime import date

from bson import ObjectId


class Categoria:
    """Valida y representa una de las categorías admitidas por la aplicación."""

    NOMBRES_VALIDOS = ("Trabajo", "Personal", "Estudio", "Otro")

    def __init__(self, nombre):
        """Rechaza nombres fuera del conjunto de categorías permitidas."""
        if not self.es_valida(nombre):
            raise ValueError("Selecciona una categoría válida.")
        self.__nombre = nombre

    @property
    def nombre(self):
        """Devuelve el nombre validado de la categoría."""
        return self.__nombre

    @classmethod
    def es_valida(cls, nombre):
        """Indica si el nombre pertenece al conjunto de categorías."""
        return nombre in cls.NOMBRES_VALIDOS


CATEGORIAS = Categoria.NOMBRES_VALIDOS


# Representa una tarea y su formato de almacenamiento.
class Tarea:
    """Guarda los datos de una tarea tras validarlos y normalizarlos."""

    def __init__(
        self,
        titulo,
        completada=False,
        id_tarea=None,
        categoria="Personal",
        etiquetas=None,
        descripcion="",
        fecha_vencimiento=None,
    ):
        """Valida los campos y establece los valores de la tarea."""
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
        self.__descripcion = self._validar_descripcion(descripcion)
        self.__fecha_vencimiento = self._validar_fecha(fecha_vencimiento)

    @staticmethod
    def _validar_descripcion(descripcion):
        """Recorta y limita la descripción opcional."""
        if not isinstance(descripcion, str):
            raise ValueError("La descripción debe ser texto.")
        descripcion = descripcion.strip()
        if len(descripcion) > 500:
            raise ValueError("La descripción debe tener 500 caracteres como máximo.")
        return descripcion

    @staticmethod
    def _validar_fecha(fecha_vencimiento):
        """Convierte una fecha ISO o date; permite que no se indique vencimiento."""
        if fecha_vencimiento in (None, ""):
            return None
        if isinstance(fecha_vencimiento, date):
            return fecha_vencimiento
        if isinstance(fecha_vencimiento, str):
            try:
                fecha = date.fromisoformat(fecha_vencimiento)
            except ValueError as error:
                raise ValueError("La fecha límite debe ser válida.") from error
            if fecha.isoformat() == fecha_vencimiento:
                return fecha
        raise ValueError("La fecha límite debe ser válida.")

    @staticmethod
    def etiqueta_valida(etiqueta):
        """Comprueba que una etiqueta use caracteres y longitud permitidos."""
        return re.fullmatch(r"[\w-]{1,20}", etiqueta) is not None

    @classmethod
    def _validar_etiquetas(cls, etiquetas):
        """Normaliza etiquetas, quita duplicados y aplica el máximo de cinco."""
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
        """Devuelve el identificador asignado por MongoDB, si existe."""
        return self.__id

    @property
    def titulo(self):
        """Devuelve el título validado."""
        return self.__titulo

    @property
    def completada(self):
        """Indica si la tarea está marcada como completada."""
        return self.__completada

    @property
    def categoria(self):
        """Devuelve el nombre de la categoría asociada."""
        return self.__categoria.nombre

    @property
    def etiquetas(self):
        """Devuelve una copia para evitar cambios externos en la lista interna."""
        return self.__etiquetas.copy()

    @property
    def descripcion(self):
        """Devuelve la descripción normalizada."""
        return self.__descripcion

    @property
    def fecha_vencimiento(self):
        """Devuelve la fecha límite o None si no se definió."""
        return self.__fecha_vencimiento

    def asignar_id(self, id_tarea):
        """Asocia al objeto el identificador generado al guardarlo."""
        self.__id = id_tarea

    def a_diccionario(self):
        """Serializa la tarea con nombres de campo y fecha compatibles con MongoDB."""
        return {
            "titulo": self.titulo,
            "completada": self.completada,
            "categoria": self.categoria,
            "etiquetas": self.__etiquetas.copy(),
            "descripcion": self.descripcion,
            "fecha_vencimiento": (
                self.fecha_vencimiento.isoformat()
                if self.fecha_vencimiento
                else None
            ),
        }


# Centraliza las consultas y modificaciones de tareas en MongoDB.
class RepositorioTareas:
    """Encapsula las consultas de tareas y limita las operaciones al propietario."""

    def __init__(self, db):
        """Selecciona la colección y crea el índice usado para ordenar por título."""
        self.__coleccion = db["tareas"]
        self.__coleccion.create_index("titulo")

    def guardar(self, tarea, usuario_id=None):
        """Inserta una tarea, la vincula al usuario y asigna el ID insertado."""
        documento = tarea.a_diccionario()
        if usuario_id:
            documento["usuario_id"] = usuario_id
        resultado = self.__coleccion.insert_one(documento)
        tarea.asignar_id(str(resultado.inserted_id))
        return tarea

    def cargar_todas(self, estado=None, categoria=None, etiqueta=None, orden="recientes", usuario_id=None):
        """Filtra y ordena tareas, aplicando valores compatibles a documentos antiguos."""
        # Recupera solo los campos usados por la vista y evita una lista intermedia.
        filtros = {}
        if usuario_id:
            filtros["usuario_id"] = usuario_id
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
            {
                "titulo": 1,
                "completada": 1,
                "categoria": 1,
                "etiquetas": 1,
                "descripcion": 1,
                "fecha_vencimiento": 1,
            },
        ).sort(ordenes[orden])
        return [
            Tarea(
                titulo=doc["titulo"],
                completada=doc.get("completada", False),
                id_tarea=str(doc["_id"]),
                categoria=doc.get("categoria", "Personal"),
                etiquetas=doc.get("etiquetas", []),
                descripcion=doc.get("descripcion", ""),
                fecha_vencimiento=doc.get("fecha_vencimiento"),
            )
            for doc in documentos
        ]

    def listar_etiquetas(self):
        """Devuelve las etiquetas distintas ordenadas sin distinguir mayúsculas."""
        return sorted(self.__coleccion.distinct("etiquetas"), key=str.casefold)

    def cambiar_estado(self, id_tarea, usuario_id=None):
        """Invierte el estado en MongoDB y opcionalmente restringe por propietario."""
        # Invierte el estado de forma atomica en una sola operacion de MongoDB.
        # El usuario_id limita la operacion a tareas propias.
        consulta = {"_id": ObjectId(id_tarea)}
        if usuario_id:
            consulta["usuario_id"] = usuario_id
        self.__coleccion.update_one(
            consulta,
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

    def eliminar(self, id_tarea, usuario_id=None):
        """Elimina la tarea indicada, restringiendo la consulta al propietario si se recibe."""
        consulta = {"_id": ObjectId(id_tarea)}
        if usuario_id:
            consulta["usuario_id"] = usuario_id
        self.__coleccion.delete_one(consulta)
