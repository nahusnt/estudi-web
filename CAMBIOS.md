# CAMBIOS — Cuentas y perfiles de Estudi Web

Este documento resume **todo lo que se agregó y modificó** sobre el código original del equipo.
Puedes revisar los cambios archivo por archivo desde la pestaña *Source Control* de VS Code (`Ctrl+Shift+G`).

---

## 1. Qué se agregó

| Archivo | Qué es |
|---|---|
| `usuarios.py` | **NUEVO.** Modelo `Usuario` + `RepositorioUsuarios`. Hashea contraseñas con Werkzeug (`scrypt`), valida correo, username y datos de perfil, y permite autenticar por correo o username. Mismo estilo que `modelos.py`. |
| `templates/login.html` | **NUEVO.** Pantalla de inicio de sesión (mismo estilo holográfico del resto de la app, respeta tema claro/oscuro). |
| `templates/registro.html` | **NUEVO.** Pantalla de registro con username único y confirmación de contraseña. |
| `CAMBIOS.md` | **NUEVO.** Este documento. |

## 2. Qué se modificó

| Archivo | Cambio |
|---|---|
| `app.py` | Rutas `/login`, `/registro`, `/logout`. Protección global con `@app.before_request` (si no iniciaste sesión, cualquier ruta te manda a `/login`). Todas las consultas de tareas ahora filtran por `usuario_id` → **cada usuario ve solo sus tareas**. |
| `modelos.py` | `guardar`, `cargar_todas`, `cambiar_estado` y `eliminar` aceptan un `usuario_id` opcional y lo agregan al filtro de Mongo. Sin `usuario_id` funciona igual que antes (retrocompatible). |
| `templates/index.html` | Incluye navegación de perfil, avatar y datos de cuenta en la barra lateral, además de la edición del perfil. |
| `static/css/styles.css` | Estilos del usuario en el sidebar y de las pantallas de login/registro (57 líneas al final del archivo, nada tocado de lo viejo). |
| `tests/test_app.py` | Pruebas de rutas, autenticación, username, perfil y repositorios simulados. Total actual: **44 tests**. |
| `.env.example` | Eliminado del árbol actual; crea `.env` local siguiendo las instrucciones del README. |

## 3. Cómo correrlo en VS Code

```bash
# 1. Abrir la carpeta del proyecto en VS Code y una terminal (Ctrl+ñ)

# 2. Crear el entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows  (en Linux/Mac: source .venv/bin/activate)

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear .env en la raíz y completar
#    MONGO_URI=mongodb+srv://usuario:contrasena@cluster0.xxxx.mongodb.net/
#    (ver detalle en la sección 5)

# 5. Correr la app
python app.py                 # o: flask --app app run --debug
```

Abrir `http://127.0.0.1:5000` → te redirige a `/login`.

> **Primer uso:** entrá a `/registro`, creá tu cuenta, y listo. Las tareas que crees
> quedan atadas a tu cuenta en Mongo.

## 4. Los tests

```bash
python -m unittest discover -s tests -v
```

44 tests en total. No tocan tu Mongo real: simulan el cliente y las operaciones de repositorio.

## 5. Variables de entorno

| Variable | Obligatoria | Para qué |
|---|---|---|
| `MONGO_URI` | sí | URI del cluster Atlas. |
| `MONGO_DB` | no | Base de datos de tareas (default: `lista_tareas_db`). |
| `USUARIOS_DB` | no | Base de datos de usuarios (default: `estudi_usuarios_db`). Por defecto vive **en el mismo cluster**, en otra base. |
| `USUARIOS_URI` | no | Si algún día querés usuarios en **otro cluster distinto**, ponés acá su URI y no hay que tocar código. |
| `FLASK_SECRET_KEY` | no | Clave de las sesiones/cookies. En producción definir una fija y secreta. |

**Sobre el cluster:** no hace falta un cluster nuevo para guardar contraseñas y correos.
Un solo cluster gratis (M0) soporta varias bases de datos. Ya está separado:
`lista_tareas_db` (tareas) y `estudi_usuarios_db` (usuarios). Si el profe pide clusters
separados, se resuelve con `USUARIOS_URI` en el `.env`, sin cambiar una línea de código.

## 6. Sobre el estilo / tipado del código

Se respetó **exactamente** la convención que ya tenía el proyecto:

- Python plano, **sin type hints** (igual que `modelos.py` original: `def guardar(self, tarea):`).
- Nombres en español (`buscar_por_correo`, `verificar_contrasena`).
- Atributos "privados" con doble guion bajo (`self.__coleccion`, como `self.__db` original).
- Mismo patrón repositorio: el constructor recibe la base de Mongo y expone `guardar()`.
- Docstrings y comentarios en español.

## 7. Seguridad — leer antes de subir a GitHub

1. **`.env` NO está en el repo** (`.gitignore` ya lo excluye). Ese archivo tiene tu
   contraseña de Atlas adentro: nunca lo subas ni lo mandes por chat.
2. Si compartiste credenciales de Atlas, cámbialas desde *Database Access → Edit → Edit Password*
   y actualiza tu `.env` local.
3. Las contraseñas de la app **nunca se guardan en texto plano**: se hashean con
   scrypt (Werkzeug). En Mongo se ve `scrypt:32768:8:1:salt:hash`, no la contraseña.

## 8. Pendientes que quedaron

- **3 tareas viejas huérfanas:** las que existían antes del login no tienen `usuario_id`,
  así que logueado no las vas a ver. Si querés, un scriptcito las migra a tu cuenta.
- Elimina las cuentas de prueba de `estudi_usuarios_db.usuarios` antes de publicar.
- `docs/DIARIO.md` puede actualizarse con el sistema de cuentas y perfiles.
