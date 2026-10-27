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

  <p><a href="#-un-vistazo">👀 Ver la app</a> · <a href="#android">📱 Android</a> · <a href="#-lo-que-puedes-hacer">✨ Funciones</a> · <a href="#-empezar">🚀 Instalación</a> · <a href="#-contribuir">🤝 Contribuir</a></p>
</div>

---

## 👀 Un vistazo

> **Tu espacio, tus prioridades.** Estudi Web mantiene lo importante a mano y deja que cada persona organice su lista a su manera.

<p align="center">
  <a href="./images/vista-clara.svg">
    <img src="./images/vista-clara.svg" alt="Resumen de tareas de Estudi Web en modo claro" width="49%">
  </a>
  <a href="./images/vista-oscura.svg">
    <img src="./images/vista-oscura.svg" alt="Resumen de tareas de Estudi Web en modo oscuro" width="49%">
  </a>
</p>

<p align="center"><sub>☀️ Tema claro · 🌙 Tema oscuro · Crear, consultar tu resumen y personalizar tus ajustes</sub></p>

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
- ⚙️ Personalizar el tema claro/oscuro y el espacio de la lista; las preferencias quedan guardadas en el navegador.
- ☁️ Guardar tus tareas en MongoDB, ya sea tu propia base de datos u otra externa.

## 🧪 Pruebas

Ejecuta las pruebas automatizadas desde la raíz del proyecto:

```bash
python -m unittest discover -s tests -v
```

Las pruebas validan las rutas principales y reglas del modelo sin necesitar una conexión a MongoDB.


## 🧰 Tecnologías

| Aplicación | Datos |
| --- | --- |
| Python y Flask | MongoDB Atlas y PyMongo |
| HTML, CSS y JavaScript | Variables de entorno con `python-dotenv` |

## 🧩 Organización del backend

- `Tarea` mantiene privados sus datos y valida el título y las etiquetas al crear cada tarea.
- `Categoria` centraliza las categorías permitidas.
- `RepositorioTareas` encapsula las operaciones de lectura y escritura en MongoDB.

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
   Copy-Item .env.example .env
   ```

   **macOS o Linux**

   ```bash
   cp .env.example .env
   ```

   Abre `.env` y configura `MONGO_URI` con la URI de tu clúster de Atlas.

5. Inicia la aplicación:

   ```bash
   python app.py
   ```

6. Visita [http://127.0.0.1:5000](http://127.0.0.1:5000).

## 🍃 Configurar MongoDB Atlas

En Atlas, crea un usuario de base de datos con permisos de lectura y escritura y agrega la IP de tu computadora en **Network Access**. Este usuario es distinto de tu usuario para iniciar sesión en Atlas.

La plantilla `.env.example` muestra el formato esperado:

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
