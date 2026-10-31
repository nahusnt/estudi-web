<div align="center">
  <img src="./static/images/logo.png" alt="Logo de Estudi Web" width="112">
  <h1>Estudi Web</h1>
  <p><strong>🌊 Tu día, más claro. Tus pendientes, en orden. ✨</strong></p>
  <p>Una app web ligera para organizar tareas personales con categorías, etiquetas y filtros.<br>
  <em>Menos ruido, más foco y todo en su lugar.</em></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10 o posterior">
    <img src="https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask 3">
    <img src="https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB Atlas">
  </p>

   <p><a href="#-un-vistazo">👀 Ver la app</a> · <a href="#android">📱 Android</a> · <a href="#-lo-que-puedes-hacer">✨ Funciones</a> · <a href="#-cuenta-y-perfil">👤 Cuenta y perfil</a> · <a href="#-estructura-del-proyecto">📁 Estructura</a> · <a href="#-empezar">🚀 Instalación</a> · <a href="#-contribuir">🤝 Contribuir</a></p>
</div>

---

## 👀 Un vistazo

> **Tu espacio, tus prioridades.** Estudi Web mantiene lo importante a mano y deja que cada persona organice su lista a su manera.

<p align="center">
  <a href="./images/vista-clara.svg">
    <img src="./images/vista-clara.svg" alt="Vista demostrativa de Estudi Web en modo claro, con barra lateral y perfil abajo" width="49%">
  </a>
  <a href="./images/vista-oscura.svg">
    <img src="./images/vista-oscura.svg" alt="Vista demostrativa de Estudi Web en modo oscuro, con barra lateral y perfil abajo" width="49%">
  </a>
</p>

<p align="center"><sub>☀️ Tema claro · 🌙 Tema oscuro · Barra lateral con una sola tarjeta de perfil · Resumen de tareas</sub></p>

<a id="android"></a>

## 📱 También en Android

¿Prefieres organizarte desde el móvil? Explora la versión de Estudi disponible para Android:

<p align="center">
  <a href="https://github.com/nahusnt/estudi-app"><strong>🤖 Visitar Estudi para Android en GitHub →</strong></a>
</p>

## ✨ Lo que puedes hacer

- ✅ Crear tareas y marcarlas como completadas.
- 📝 Añadir una descripción y una fecha límite opcionales a cada tarea.
- 🗂️ Clasificar cada pendiente como Trabajo, Personal, Estudio u Otro.
- 🏷️ Añadir hasta cinco etiquetas por tarea.
- 🔎 Filtrar por estado, categoría o etiqueta, y ordenar por fecha o título.
- 📊 Consultar un resumen con progreso, categorías, tareas vencidas y próximas fechas límite.
- 🧭 Alternar entre la interfaz anterior con navegación superior y la nueva barra lateral; la preferencia queda guardada en el navegador.
- ⚙️ Personalizar el diseño, tema, paleta, idioma, tamaño del texto, densidad, contraste y animaciones; las preferencias quedan guardadas en el navegador.
- 🔐 Crear una cuenta con correo y nombre de usuario único; iniciar sesión con cualquiera de los dos identificadores.
- 👤 Personalizar el perfil con foto, nombre visible, descripción y etiquetas.
- 👁️ Mostrar u ocultar la contraseña desde el formulario de inicio de sesión.
- 🖼️ Ver la foto de perfil junto al nombre de la cuenta en la barra lateral; si no hay foto, se muestra una inicial.
- ☁️ Guardar tus tareas en la base `lista_tareas_db` de MongoDB, en el clúster indicado por `MONGO_URI`.

## 👤 Cuenta y perfil

Al abrir la aplicación por primera vez, crea una cuenta desde **Crear una cuenta**. El nombre de usuario debe tener entre 3 y 24 caracteres y solo puede contener letras, números, guiones y guiones bajos. Es único y no distingue entre mayúsculas y minúsculas.

En el inicio de sesión puedes escribir tu correo o tu nombre de usuario. Usa el botón con el icono del ojo para alternar la visibilidad de la contraseña. Las cuentas creadas antes de incorporar el nombre de usuario pueden seguir iniciando sesión con su correo y elegir uno desde la sección **Perfil**.

Desde **Perfil** puedes editar estos datos:

- **Foto:** PNG, JPG o WebP de hasta 1 MB. Se guarda como dato de imagen en el documento de usuario de MongoDB.
- **Nombre visible:** hasta 60 caracteres.
- **Descripción:** hasta 280 caracteres.
- **Etiquetas:** hasta 8, con un máximo de 24 caracteres cada una; sepáralas con comas.

La foto y el nombre también se muestran en la barra lateral junto al botón para cerrar sesión.

## 🧪 Pruebas

Ejecuta las pruebas automatizadas desde la raíz del proyecto:

```bash
python -m unittest discover -s tests -v
```

Las 45 pruebas automatizadas validan las rutas principales, la autenticación, el perfil y las reglas de los modelos sin necesitar una conexión a MongoDB.


## 🧰 Tecnologías

| Aplicación | Datos |
| --- | --- |
| Python y Flask | MongoDB Atlas y PyMongo |
| HTML, CSS y JavaScript | Variables de entorno con `python-dotenv` |

## 📁 Estructura del proyecto

Este es el mapa de las carpetas y archivos principales del repositorio. La carpeta raíz es la que se abre en VS Code; en la rama principal se llama `main`.

```text
estudi-web/
├── app.py
├── modelos.py
├── usuarios.py
├── requirements.txt
├── README.md
├── CAMBIOS.md
├── REDES.md
├── SECURITY.md
├── docs/
├── images/
├── static/
│   ├── css/
│   ├── images/
│   └── js/
├── templates/
└── tests/
```

### Archivos de la raíz

| Archivo | Para qué sirve |
|---|---|
| `app.py` | Punto de entrada del sitio. Configura Flask y MongoDB, define las rutas, controla las sesiones y conecta los formularios con los modelos y las vistas. |
| `modelos.py` | Define las categorías y tareas, sus validaciones y `RepositorioTareas`, que lee y escribe tareas en MongoDB. |
| `usuarios.py` | Define el modelo `Usuario` y `RepositorioUsuarios`, que registran y autentican cuentas y guardan sus datos de perfil. |
| `requirements.txt` | Lista las dependencias de Python que se instalan con `pip`. |
| `README.md` | Documentación principal: funciones, instalación, configuración, pruebas y estructura del proyecto. |
| `CAMBIOS.md` | Resumen de cambios y notas de trabajo sobre las cuentas y perfiles. |
| `REDES.md` | Documenta el diagrama y la propuesta de topología de red del proyecto. |
| `SECURITY.md` | Describe amenazas de seguridad identificadas y recomendaciones de mitigación. |
| `.gitignore` | Indica qué archivos locales o generados Git debe ignorar, como `.env`, los entornos virtuales y `__pycache__`. |

### Carpetas

| Carpeta | Contenido |
|---|---|
| `docs/` | Documentación de arquitectura (`ARQUITECTURA.md`), modelo de datos (`MODELO_DATOS.md`) y diario de trabajo (`DIARIO.md`). |
| `images/` | Recursos para documentación y presentación: capturas de la interfaz en temas claro y oscuro, y el diagrama de red usado en `REDES.md`. |
| `static/css/` | Hojas de estilo del navegador. `styles.css` contiene los temas, componentes y reglas responsive. |
| `static/images/` | Imágenes que usa la interfaz, como el logotipo (`logo.png` y `logo-waves.svg`). |
| `static/js/` | JavaScript del navegador (`app.js`) y su documentación (`DOCUMENTACION_FRONTEND.md`); gestiona preferencias e interacciones de la interfaz. |
| `templates/` | Vistas HTML renderizadas por Flask/Jinja: `index.html` para la aplicación, `login.html` para iniciar sesión y `registro.html` para crear una cuenta. |
| `tests/` | Pruebas automatizadas de las rutas, autenticación, modelos y repositorios. `test_app.py` las reúne. |

Los directorios `__pycache__/` y los archivos `.pyc` los genera Python al ejecutar la aplicación o las pruebas; no son código fuente. El entorno virtual (`.venv/`) y el archivo local `.env` tampoco forman parte del repositorio.

Las imágenes `images/vista-clara.svg` y `images/vista-oscura.svg` son ilustraciones de demostración del resumen; usan datos de ejemplo y no son capturas de una sesión real.

## 🧩 Organización del backend

- `Tarea` mantiene privados sus datos y valida el título y las etiquetas al crear cada tarea.
- `Categoria` centraliza las categorías permitidas.
- `RepositorioTareas` encapsula las operaciones de lectura y escritura en MongoDB.
- `Usuario` valida el correo, el nombre de usuario y los datos del perfil; las contraseñas se almacenan únicamente como hash.
- `RepositorioUsuarios` gestiona el registro, la autenticación por correo o nombre de usuario y la persistencia del perfil en la colección `usuarios`.

## ⚙️ Variables de entorno

Guarda la configuración privada en `.env` en la raíz del proyecto. `.gitignore` excluye ese archivo del repositorio.

| Variable | Obligatoria | Uso |
|---|---|---|
| `MONGO_URI` | Sí | URI del clúster MongoDB. La aplicación usa la base `lista_tareas_db` para las tareas. |
| `USUARIOS_URI` | No | URI de un clúster distinto para las cuentas. Si se omite, usa `MONGO_URI`. |
| `USUARIOS_DB` | No | Base de datos de cuentas; por defecto `estudi_usuarios_db`. |
| `FLASK_SECRET_KEY` | Recomendable | Clave persistente y privada para firmar las sesiones Flask. Si se omite, se genera una clave aleatoria al iniciar y las sesiones no sobreviven a un reinicio. |

## 🚀 Empezar

### Requisitos

- 🐍 Python 3.10 o posterior.
- 🍃 Una cuenta de MongoDB Atlas con un usuario de base de datos y acceso de red configurados.

### Instalación

1. Clona el repositorio y entra en la carpeta:

   ```bash
   git clone https://github.com/nahusnt/estudi-web.git
   cd estudi-web
   ```

2. Crea y activa un entorno virtual:

   **Windows PowerShell**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS o Linux**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Crea tu archivo local de configuración:

   **Windows PowerShell**

   ```powershell
   New-Item -Path .env -ItemType File
   ```

   **macOS o Linux**

   ```bash
   touch .env
   ```

   Abre `.env` y agrega `MONGO_URI` con la URI de tu clúster de Atlas.

   Si quieres separar las cuentas en otro clúster, también puedes definir `USUARIOS_URI`. Para producción, define además una `FLASK_SECRET_KEY` persistente y secreta.

5. Inicia la aplicación:

   ```bash
   python app.py
   ```

6. Visita [http://127.0.0.1:5000](http://127.0.0.1:5000).

## 🍃 Configurar MongoDB Atlas

En Atlas, crea un usuario de base de datos con permisos de lectura y escritura y agrega la IP de tu computadora en **Network Access**. Este usuario es distinto de tu usuario para iniciar sesión en Atlas.

Agrega esta variable a tu archivo local `.env`, reemplazando los valores de ejemplo:

```dotenv
MONGO_URI=mongodb+srv://usuario:contraseña@cluster0.xxxxx.mongodb.net/
```

Reemplaza los valores de ejemplo por los de **Connect > Drivers** en Atlas. Si la contraseña contiene caracteres especiales como `@`, `:`, `/` o `#`, codifícala para URL antes de colocarla en la URI. No compartas ni subas tu `.env`: contiene credenciales locales.

Si aparece `bad auth : authentication failed`, revisa el usuario y la contraseña de la base de datos y actualiza la URI. Si aparece un error de conexión o timeout, revisa **Network Access** y tu conexión a Internet.

## 👥 Equipo

- Santiago Nahuel Thomas - **Encargado del Backend**
- Luciana Centurion - **Encargada de la Documentación**
- Santiago Sebastian Ojeda - **Encargado del Frontend**

## 🔄 Mantener tu copia al día

Antes de empezar a trabajar, actualiza tu copia local para incluir los cambios más recientes del repositorio. Si ya tienes cambios propios, guárdalos con un commit o con `git stash` antes de cambiar de rama.

```bash
git switch main
git pull --ff-only origin main
```

Si trabajas en otra rama, vuelve a ella y mézclale la versión más reciente de `main` antes de subir tus cambios:

```bash
git switch nombre-de-tu-rama
git fetch origin
git merge origin/main
```

Resuelve cualquier conflicto y prueba tus cambios antes de hacer `git push`. Así trabajamos todos sobre una base actualizada. ✨

## 🤝 Contribuir

1. Revisa los archivos modificados:

   ```bash
   git status
   ```

2. Prepara los cambios y comprueba lo que vas a incluir:

   ```bash
   git add .
   git diff --cached
   ```

   No agregues `.env`: contiene credenciales locales y está excluido por `.gitignore`.

3. Crea un commit con un mensaje descriptivo y sube los cambios:

   ```bash
   git commit -m "Describe brevemente los cambios"
   git push origin main
   ```

---

<div align="center">
  <strong>🌊 Hecho con cariño para que organizarse se sienta un poco más fácil. 💜</strong><br>
  <sub>Gracias por visitar Estudi Web y ayudar a que siga creciendo.</sub>
</div>
