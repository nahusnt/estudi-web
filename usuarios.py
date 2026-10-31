import re

from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash

# Formato esperado: nombre@dominio.ext (sin espacios).
CORREO_VALIDO = re.compile(r"^[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")
NOMBRE_USUARIO_VALIDO = re.compile(r"^[A-Za-z0-9_-]{3,24}$")
ETIQUETA_PERFIL_VALIDA = re.compile(r"[\w-]{1,24}")


# Representa una cuenta de usuario y su formato de almacenamiento.
class Usuario:
    def __init__(
        self,
        correo,
        contrasena=None,
        contrasena_hash=None,
        id_usuario=None,
        nombre_usuario=None,
        nombre=None,
        descripcion="",
        foto_perfil=None,
        etiquetas=None,
    ):
        correo = correo.strip().lower() if isinstance(correo, str) else ""
        if not CORREO_VALIDO.fullmatch(correo):
            raise ValueError("Ingresa un correo válido, por ejemplo nombre@dominio.com.")

        if contrasena_hash is None:
            # La contraseña en texto plano nunca se almacena: solo su hash irreversible.
            if not isinstance(contrasena, str) or len(contrasena) < 8:
                raise ValueError("La contraseña debe tener al menos 8 caracteres.")
            self.__hash = generate_password_hash(contrasena)
        else:
            self.__hash = contrasena_hash

        self.__correo = correo
        self.__id = id_usuario
        self.__nombre_usuario = self._validar_nombre_usuario(nombre_usuario) if nombre_usuario else None
        nombre_inicial = nombre if nombre is not None else self.__nombre_usuario or correo.split("@", 1)[0]
        self.__nombre = self._validar_nombre(nombre_inicial)
        self.__descripcion = self._validar_descripcion(descripcion)
        self.__foto_perfil = foto_perfil
        self.__etiquetas = self._validar_etiquetas(etiquetas)

    @staticmethod
    def _validar_nombre_usuario(nombre_usuario):
        if not isinstance(nombre_usuario, str):
            raise ValueError("El nombre de usuario debe tener entre 3 y 24 caracteres: letras, números, guion o guion bajo.")
        nombre_usuario = nombre_usuario.strip()
        if not NOMBRE_USUARIO_VALIDO.fullmatch(nombre_usuario):
            raise ValueError("El nombre de usuario debe tener entre 3 y 24 caracteres: letras, números, guion o guion bajo.")
        return nombre_usuario

    @staticmethod
    def normalizar_nombre_usuario(nombre_usuario):
        return nombre_usuario.strip().casefold() if isinstance(nombre_usuario, str) else ""

    @staticmethod
    def _validar_nombre(nombre):
        if not isinstance(nombre, str):
            raise ValueError("El nombre visible es obligatorio y debe tener 60 caracteres como máximo.")
        nombre = nombre.strip()
        if not nombre or len(nombre) > 60:
            raise ValueError("El nombre visible es obligatorio y debe tener 60 caracteres como máximo.")
        return nombre

    @staticmethod
    def _validar_descripcion(descripcion):
        if not isinstance(descripcion, str):
            raise ValueError("La descripción debe ser texto.")
        descripcion = descripcion.strip()
        if len(descripcion) > 280:
            raise ValueError("La descripción debe tener 280 caracteres como máximo.")
        return descripcion

    @staticmethod
    def _validar_etiquetas(etiquetas):
        etiquetas_normalizadas = []
        for etiqueta in etiquetas or []:
            if not isinstance(etiqueta, str):
                raise ValueError("Usa hasta 8 etiquetas de 24 caracteres, separadas por comas.")
            etiqueta = etiqueta.strip().lstrip("#").casefold()
            if etiqueta and etiqueta not in etiquetas_normalizadas:
                etiquetas_normalizadas.append(etiqueta)
        if len(etiquetas_normalizadas) > 8 or any(
            not ETIQUETA_PERFIL_VALIDA.fullmatch(etiqueta)
            for etiqueta in etiquetas_normalizadas
        ):
            raise ValueError("Usa hasta 8 etiquetas de 24 caracteres, separadas por comas.")
        return etiquetas_normalizadas

    @property
    def id(self):
        return self.__id

    @property
    def correo(self):
        return self.__correo

    @property
    def nombre_usuario(self):
        return self.__nombre_usuario

    @property
    def nombre_usuario_normalizado(self):
        return self.normalizar_nombre_usuario(self.__nombre_usuario)

    @property
    def nombre(self):
        return self.__nombre

    @property
    def descripcion(self):
        return self.__descripcion

    @property
    def foto_perfil(self):
        return self.__foto_perfil

    @property
    def etiquetas(self):
        return self.__etiquetas.copy()

    def verificar_contrasena(self, contrasena):
        return check_password_hash(self.__hash, contrasena or "")

    def asignar_id(self, id_usuario):
        self.__id = id_usuario

    def actualizar_perfil(self, nombre_usuario, nombre, descripcion, etiquetas, foto_perfil):
        self.__nombre_usuario = self._validar_nombre_usuario(nombre_usuario)
        self.__nombre = self._validar_nombre(nombre)
        self.__descripcion = self._validar_descripcion(descripcion)
        self.__etiquetas = self._validar_etiquetas(etiquetas)
        self.__foto_perfil = foto_perfil

    def a_diccionario(self):
        """Convierte el objeto a un diccionario compatible con MongoDB."""
        datos = {
            "correo": self.__correo,
            "contrasena_hash": self.__hash,
            "nombre": self.__nombre,
            "descripcion": self.__descripcion,
            "foto_perfil": self.__foto_perfil,
            "etiquetas": self.__etiquetas.copy(),
        }
        if self.__nombre_usuario:
            datos["nombre_usuario"] = self.__nombre_usuario
            datos["usuario_normalizado"] = self.nombre_usuario_normalizado
        return datos


# Centraliza las operaciones de cuentas de usuario en MongoDB.
class RepositorioUsuarios:
    def __init__(self, db):
        self.__coleccion = db["usuarios"]
        # El correo es unico: la base rechaza dos cuentas con el mismo correo.
        self.__coleccion.create_index("correo", unique=True)
        self.__coleccion.create_index(
            "usuario_normalizado",
            unique=True,
            partialFilterExpression={"usuario_normalizado": {"$type": "string"}},
        )

    def guardar(self, usuario):
        resultado = self.__coleccion.insert_one(usuario.a_diccionario())
        usuario.asignar_id(str(resultado.inserted_id))
        return usuario

    def buscar_por_correo(self, correo):
        documento = self.__coleccion.find_one(
            {"correo": (correo or "").strip().lower()}
        )
        return self._usuario_desde_documento(documento)

    def buscar_por_nombre_usuario(self, nombre_usuario):
        normalizado = Usuario.normalizar_nombre_usuario(nombre_usuario)
        if not normalizado:
            return None
        documento = self.__coleccion.find_one({"usuario_normalizado": normalizado})
        return self._usuario_desde_documento(documento)

    def buscar_por_identificador(self, identificador):
        identificador = (identificador or "").strip()
        if "@" in identificador:
            return self.buscar_por_correo(identificador)
        if not NOMBRE_USUARIO_VALIDO.fullmatch(identificador):
            return None
        return self.buscar_por_nombre_usuario(identificador)

    def buscar_por_id(self, id_usuario):
        if not ObjectId.is_valid(id_usuario):
            return None
        documento = self.__coleccion.find_one({"_id": ObjectId(id_usuario)})
        return self._usuario_desde_documento(documento)

    def obtener_foto_perfil(self, id_usuario):
        if not ObjectId.is_valid(id_usuario):
            return None
        documento = self.__coleccion.find_one(
            {"_id": ObjectId(id_usuario)}, {"foto_perfil": 1}
        )
        return documento.get("foto_perfil") if documento else None

    @staticmethod
    def _usuario_desde_documento(documento):
        if not documento:
            return None
        return Usuario(
            correo=documento["correo"],
            contrasena_hash=documento["contrasena_hash"],
            id_usuario=str(documento["_id"]),
            nombre_usuario=documento.get("nombre_usuario"),
            nombre=documento.get("nombre"),
            descripcion=documento.get("descripcion", ""),
            foto_perfil=documento.get("foto_perfil"),
            etiquetas=documento.get("etiquetas", []),
        )

    def autenticar(self, identificador, contrasena):
        usuario = self.buscar_por_identificador(identificador)
        if usuario and usuario.verificar_contrasena(contrasena):
            return usuario
        return None

    def actualizar_perfil(self, id_usuario, usuario):
        if not ObjectId.is_valid(id_usuario):
            return False
        datos = usuario.a_diccionario()
        campos_perfil = {
            clave: datos[clave]
            for clave in (
                "nombre_usuario",
                "usuario_normalizado",
                "nombre",
                "descripcion",
                "foto_perfil",
                "etiquetas",
            )
        }
        resultado = self.__coleccion.update_one(
            {"_id": ObjectId(id_usuario)}, {"$set": campos_perfil}
        )
        return resultado.matched_count == 1

    def contar(self):
        return self.__coleccion.count_documents({})
