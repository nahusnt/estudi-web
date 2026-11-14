"""Migración de contraseñas legacy a hashes (Parte 3 - Hardening de credenciales).

ESTE SCRIPT ES UNA RED DE SEGURIDAD / EVIDENCIA DE HARDENING.
-------------------------------------------------------------
El código actual de Estudi Web (``usuarios.py``) SIEMPRE hashea las contraseñas con
``werkzeug.security.generate_password_hash`` antes de guardarlas, y nunca almacena
texto plano. Por lo tanto, si todas las cuentas se crearon desde la aplicación, **no
existen contraseñas en texto plano** y este script no encontrará nada que migrar.

Se entrega igual como evidencia de la práctica de hardening para la defensa oral: detecta
y repara el caso en el que existan documentos legacy con un campo ``contrasena`` en texto
plano (por ejemplo, insertados a mano en MongoDB Compass o provenientes de una versión
anterior del código).

Uso:
    python migrar_contrasenas.py

Lee las variables de entorno desde ``.env`` (MONGO_URI y, opcionalmente, USUARIOS_DB /
USUARIOS_URI), igual que ``app.py``.

Qué hace, documento por documento de la colección ``usuarios``:
  - Si tiene ``contrasena_hash`` y NO tiene ``contrasena``: ya está OK, se omite.
  - Si tiene ``contrasena`` (texto plano) y NO tiene ``contrasena_hash``: se genera el
    hash con generate_password_hash, se guarda en ``contrasena_hash`` y se elimina el
    campo ``contrasena`` (``$unset``).
  - Si tiene ambos (caso raro): se regenera el hash desde el texto plano y se elimina
    ``contrasena``.
  - Si no tiene ninguno: se reporta como anomalía (no se puede recuperar la contraseña).

El script es idempotente: se puede ejecutar varias veces sin riesgo.
"""

import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from werkzeug.security import generate_password_hash

# [HASHING] Importamos el mensaje genérico de error para mantener la coherencia con app.py.
from security_utils import MENSAJE_ERROR_DB, registrar_error_db


def main():
    # Carga la configuración local (igual que app.py).
    load_dotenv()
    uri = os.getenv("MONGO_URI")
    if not uri:
        print("[migración] Falta definir MONGO_URI en el archivo .env.")
        print("            Copia .env.example a .env y completa tus credenciales de MongoDB Atlas.")
        return

    uri_usuarios = os.getenv("USUARIOS_URI") or uri
    base_usuarios = os.getenv("USUARIOS_DB", "estudi_usuarios_db")

    cliente = MongoClient(uri_usuarios)
    coleccion = cliente[base_usuarios]["usuarios"]

    # Contadores para el reporte final.
    ya_hasheadas = 0
    migradas = 0
    anomalas = 0

    print(f"[migración] Conectado a '{base_usuarios}.usuarios'.")
    print("[migración] Buscando cuentas con contraseña en texto plano (campo 'contrasena')...")

    try:
        # [EXCEPCIONES] La operación de MongoDB va envuelta en try/except PyMongoError.
        documentos = list(coleccion.find({}, {"contrasena": 1, "contrasena_hash": 1}))
    except PyMongoError as error:
        # El detalle real se loguea en consola del servidor; al usuario le llega el mensaje genérico.
        registrar_error_db(error)
        print(f"[migración] {MENSAJE_ERROR_DB}")
        return

    for doc in documentos:
        _id = doc["_id"]
        tiene_plana = "contrasena" in doc
        tiene_hash = "contrasena_hash" in doc

        if not tiene_plana and not tiene_hash:
            # No hay forma de recuperar la contraseña: se reporta y se omite.
            anomalas += 1
            print(f"[migración] ANOMALÍA: el documento {_id} no tiene contraseña ni hash.")
            continue

        if tiene_plana:
            # Hay texto plano: se (re)genera el hash y se elimina el campo inseguro.
            plana = doc["contrasena"]
            if not isinstance(plana, str) or len(plana) < 8:
                anomalas += 1
                print(f"[migración] ANOMALÍA: el documento {_id} tiene una 'contrasena' inválida o muy corta; se omite.")
                continue
            nuevo_hash = generate_password_hash(plana)
            try:
                # [EXCEPCIONES] update_one envuelto en try/except PyMongoError.
                coleccion.update_one(
                    {"_id": _id},
                    {"$set": {"contrasena_hash": nuevo_hash}, "$unset": {"contrasena": ""}},
                )
            except PyMongoError as error:
                registrar_error_db(error)
                print(f"[migración] No se pudo migrar el documento {_id}: {MENSAJE_ERROR_DB}")
                anomalas += 1
                continue
            migradas += 1
            print(f"[migración] Migrado: {_id} -> contraseña hasheada (campo 'contrasena' eliminado).")
        else:
            # Ya tiene hash y no tiene texto plano: nada que hacer.
            ya_hasheadas += 1

    print("\n[migración] Resumen:")
    print(f"  - Cuentas ya hasheadas (sin cambios): {ya_hasheadas}")
    print(f"  - Cuentas migradas de texto plano a hash: {migradas}")
    print(f"  - Cuentas con anomalías (requieren revisión manual): {anomalas}")
    if migradas == 0 and anomalas == 0:
        print("  - No se encontraron contraseñas en texto plano: todas las cuentas ya usan hash. ✔")
    print("[migración] Listo.")


if __name__ == "__main__":
    main()
