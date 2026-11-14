"""Define el modelo de cuenta y las operaciones de autenticación en MongoDB."""

import re

from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash

from security_utils import sanitizar  # [XSS] helper de sanitización de entrada.

# Formato esperado: nombre@dominio.ext (sin espacios).
CORREO_VALIDO = re.compile(r"^[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")
NOMBRE_USUARIO_VALIDO = re.compile(r"^[A-Za-z0-9_-]{3,24}$")
ETIQUETA_PERFIL_VALIDA = re.compile(r"[\w-]{1,24}")


# Representa una cuenta de usuario y su formato de almacenamiento.
class Usuario:
    """Valida la identidad y el perfil, y conserva la contraseña únicamente como hash."""

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
        """Normaliza el correo y construye una cuenta con campos de perfil válidos."""
        correo = correo.strip().lower() if isinstance(correo, str) else ""
        # El correo se valida con una expresión regular estricta que no permite
        # caracteres HTML, por lo que no requiere sanitización adicional.
        if not CORREO_VALIDO.fullmatch(correo):
            raise ValueError("Ingresa un correo válido, por ejemplo nombre@dominio.com.")

        if contrasena_hash is None:
            # [HASHING] La contraseña en texto plano nunca se almacena: solo su hash
            # irreversible generado con werkzeug.security.generate_password_hash.
            # IMPORTANTE: la contraseña NO se sanitiza con html.escape, porque eso
            # alteraría su valor y rompería la verificación en el login. Se hashea tal
            # cual la ingresa el usuario.
            if not isinstance(contrasena, str) or len(contrasena) < 8:
                raise ValueError("La contraseña debe tener al menos 8 caracteres.")
            self.__hash = generate_password_hash(contrasena)
        else:
            self.__hash = contrasena_hash

        self.__correo = correo
        self.__id = id_usuario
        # El nombre de usuario se valida con regex ([A-Za-z0-9_-]): sin HTML posible.
        self.__nombre_usuario = self._validar_nombre_usuario(nombre_usuario) if nombre_usuario else None
        nombre_inicial = nombre if nombre is not None else self.__nombre_usuario or correo.split("@", 1)[0]
        self.__nombre = self._validar_nombre(nombre_inicial)
        self.__descripcion = self._validar_descripcion(descripcion)
        self.__foto_perfil = foto_perfil
        self.__etiquetas = self._validar_etiquetas(etiquetas)

    @staticmethod
    def _validar_nombre_usuario(nombre_usuario):
        """Valida el identificador público de 3 a 24 caracteres."""
        if not isinstance(nombre_usuario, str):
            raise ValueError("El nombre de usuario debe tener entre 3 y 24 caracteres: letras, números, guion o guion bajo.")
        nombre_usuario = nombre_usuario.strip()
        if not NOMBRE_USUARIO_VALIDO.fullmatch(nombre_usuario):
            raise ValueError("El nombre de usuario debe tener entre 3 y 24 caracteres: letras, números, guion o guion bajo.")
        return nombre_usuario

    @staticmethod
    def normalizar_nombre_usuario(nombre_usuario):
        """Normaliza el identificador para búsquedas que ignoran mayúsculas."""
        return nombre_usuario.strip().casefold() if isinstance(nombre_usuario, str) else ""

    @staticmethod
    def _validar_nombre(nombre):
        """Recorta, valida y sanitiza el nombre visible obligatorio."""
        if not isinstance(nombre, str):
            raise ValueError("El nombre visible es obligatorio y debe tener 60 caracteres como máximo.")
        nombre = nombre.strip()
        if not nombre or len(nombre) > 60:
            raise ValueError("El nombre visible es obligatorio y debe tener 60 caracteres como máximo.")
        # [XSS] El nombre visible es texto libre: se escapa antes de persistirlo.
        return sanitizar(nombre)

    @staticmethod
    def _validar_descripcion(descripcion):
        """Valida el texto de descripción, aplica el máximo y sanitiza."""
        if not isinstance(descripcion, str):
            raise ValueError("La descripción debe ser texto.")
        descripcion = descripcion.strip()
        if len(descripcion) > 280:
            raise ValueError("La descripción debe tener 280 caracteres como máximo.")
        # [XSS] La descripción del perfil es texto libre: se escapa antes de persistirla.
        return sanitizar(descripcion)

    @staticmethod
    def _validar_etiquetas(etiquetas):
        """Normaliza y valida hasta ocho etiquetas únicas del perfil."""
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
        # Las etiquetas se validan con regex ([\w-]): sin caracteres HTML posibles.
        return etiquetas_normalizadas

    @property
    def id(self):
        """Devuelve el ID de MongoDB como texto o None antes de guardar."""
        return self.__id

    @property
    def correo(self):
        """Devuelve el correo normalizado de la cuenta."""
        return self.__correo

    @property
    def nombre_usuario(self):
        """Devuelve el nombre de usuario o None para cuentas antiguas."""
        return self.__nombre_usuario

    @property
    def nombre_usuario_normalizado(self):
        """Devuelve la versión normalizada usada por búsquedas e índices."""
        return self.normalizar_nombre_usuario(self.__nombre_usuario)

    @property
    def nombre(self):
        """Devuelve el nombre visible del perfil (sanitizado)."""
        return self.__nombre

    @property
    def descripcion(self):
        """Devuelve la descripción del perfil (sanitizada)."""
        return self.__descripcion

    @property
    def foto_perfil(self):
        """Devuelve la imagen de perfil almacenada como data URL, si existe."""
        return self.__foto_perfil

    @property
    def etiquetas(self):
        """Devuelve una copia de las etiquetas para proteger la lista interna."""
        return self.__etiquetas.copy()

    def verificar_contrasena(self, contrasena):
        """Compara la contraseña proporcionada con el hash guardado."""
        # [HASHING] check_password_hash verifica la contraseña sin almacenarla nunca.
        return check_password_hash(self.__hash, contrasena or "")

    def asignar_id(self, id_usuario):
        """Asocia a la cuenta el ID que MongoDB generó al insertarla."""
        self.__id = id_usuario

    def actualizar_perfil(self, nombre_usuario, nombre, descripcion, etiquetas, foto_perfil):
        """Valida y reemplaza los campos editables del perfil."""
        self.__nombre_usuario = self._validar_nombre_usuario(nombre_usuario)
        # [XSS] Al re-validar nombre y descripcion se vuelve a aplicar sanitizar, que
        # es idempotente: no degrada valores ya escapados en una edición anterior.
        self.__nombre = self._validar_nombre(nombre)
        self.__descripcion = self._validar_descripcion(descripcion)
        self.__etiquetas = self._validar_etiquetas(etiquetas)
        self.__foto_perfil = foto_perfil

    def a_diccionario(self):
        """Serializa la cuenta sin incluir nunca la contraseña en texto plano."""
        datos = {
            "correo": self.__correo,
            # [HASHING] Se persiste el hash, nunca la contraseña original.
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
    """Agrupa consultas de cuentas, autenticación e índices de unicidad."""

    def __init__(self, db):
        """Selecciona la colección y establece índices únicos para correo y usuario."""
        self.__coleccion = db["usuarios"]
        # El correo es unico: la base rechaza dos cuentas con el mismo correo.
        self.__coleccion.create_index("correo", unique=True)
        self.__coleccion.create_index(
            "usuario_normalizado",
            unique=True,
            partialFilterExpression={"usuario_normalizado": {"$type": "string"}},
        )

    def guardar(self, usuario):
        """Inserta la cuenta y asigna al objeto el ID generado por MongoDB."""
        resultado = self.__coleccion.insert_one(usuario.a_diccionario())
        usuario.asignar_id(str(resultado.inserted_id))
        return usuario

    def buscar_por_correo(self, correo):
        """Busca una cuenta por correo sin distinguir mayúsculas."""
        documento = self.__coleccion.find_one(
            {"correo": (correo or "").strip().lower()}
        )
        return self._usuario_desde_documento(documento)

    def buscar_por_nombre_usuario(self, nombre_usuario):
        """Busca por el identificador normalizado; devuelve None si está vacío."""
        normalizado = Usuario.normalizar_nombre_usuario(nombre_usuario)
        if not normalizado:
            return None
        documento = self.__coleccion.find_one({"usuario_normalizado": normalizado})
        return self._usuario_desde_documento(documento)

    def buscar_por_identificador(self, identificador):
        """Interpreta el valor como correo o nombre de usuario y busca la cuenta."""
        identificador = (identificador or "").strip()
        if "@" in identificador:
            return self.buscar_por_correo(identificador)
        if not NOMBRE_USUARIO_VALIDO.fullmatch(identificador):
            return None
        return self.buscar_por_nombre_usuario(identificador)

    def buscar_por_id(self, id_usuario):
        """Busca por ObjectId y descarta identificadores con formato inválido."""
        # [IDOR] La validación de ObjectId evita consultas con IDs manipulados.
        if not ObjectId.is_valid(id_usuario):
            return None
        documento = self.__coleccion.find_one({"_id": ObjectId(id_usuario)})
        return self._usuario_desde_documento(documento)

    def obtener_foto_perfil(self, id_usuario):
        """Lee únicamente la foto de una cuenta válida para reducir datos consultados."""
        if not ObjectId.is_valid(id_usuario):
            return None
        documento = self.__coleccion.find_one(
            {"_id": ObjectId(id_usuario)}, {"foto_perfil": 1}
        )
        return documento.get("foto_perfil") if documento else None

    @staticmethod
    def _usuario_desde_documento(documento):
        """Reconstruye un Usuario o devuelve None si MongoDB no encontró el documento."""
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
        """Devuelve la cuenta solo cuando el identificador y el hash coinciden."""
        usuario = self.buscar_por_identificador(identificador)
        # [HASHING] Verifica la contraseña contra el hash almacenado (check_password_hash).
        if usuario and usuario.verificar_contrasena(contrasena):
            return usuario
        return None

    def actualizar_perfil(self, id_usuario, usuario):
        """Actualiza los campos de perfil de una cuenta identificada por ObjectId."""
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
        """Devuelve el número de cuentas almacenadas."""
        return self.__coleccion.count_documents({})
