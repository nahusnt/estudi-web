# Lista de Tareas Personal

Proyecto Final Integrador de Programacion II + Bases de Datos II.

## Descripcion

Aplicacion web para administrar tareas personales.

El usuario podrá:

- Agregar tareas.
- Marcar tareas como completadas.
- Eliminar tareas.
- Mantener las tareas guardadas.
- Filtrar por estado, categoría y etiqueta, y ordenar por fecha o título.
- Clasificar tareas en Trabajo, Personal, Estudio u Otro y agregar hasta cinco etiquetas.
- Alternar entre modo claro y oscuro; la preferencia se guarda en el navegador.

## Vista previa

El README de GitHub no admite carruseles interactivos; puedes abrir cada imagen para verla en grande.

<p align="center">
  <a href="./images/vista-clara.svg">
    <img src="./images/vista-clara.svg" alt="Vista previa de la aplicación en modo claro" width="49%">
  </a>
  <a href="./images/vista-oscura.svg">
    <img src="./images/vista-oscura.svg" alt="Vista previa de la aplicación en modo oscuro" width="49%">
  </a>
</p>

## Tecnologias

- Python
- Flask
- MongoDB
- HTML
- CSS
- JavaScript

## Requisitos

- Python 3.10 o posterior.
- Una cuenta de MongoDB Atlas con un usuario de base de datos y acceso de red configurados.

## Instalacion

1. Clona el repositorio y abre una terminal en la carpeta del proyecto.
2. Crea y activa un entorno virtual.

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instala las dependencias:

```bash
python -m pip install -r requirements.txt
```

4. Copia la plantilla a `.env`.

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

En macOS o Linux:

```bash
cp .env.example .env
```

Abre `.env` y completa `MONGO_URI` con la URI de tu cluster de Atlas.
5. Inicia la aplicación:

```bash
python app.py
```

Abre `http://127.0.0.1:5000` en el navegador.

## Configurar MongoDB Atlas

En Atlas, crea un usuario de base de datos con permisos de lectura y escritura, y agrega la IP de tu computadora en **Network Access**. El usuario de base de datos es distinto de tu usuario para iniciar sesión en Atlas.

La plantilla de `.env.example` tiene este formato:

```dotenv
MONGO_URI=mongodb+srv://USUARIO:CONTRASENA_CODIFICADA@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=lista-tareas-personal
```

Reemplaza los valores de ejemplo por los de **Connect > Drivers** en Atlas. Si la contraseña contiene caracteres especiales como `@`, `:`, `/` o `#`, codifícala para URL antes de colocarla en la URI. No compartas ni subas tu `.env`; cada computadora debe configurar sus propias credenciales.

Si aparece `bad auth : authentication failed`, revisa el usuario y la contraseña del usuario de base de datos y actualiza la URI. Si aparece un error de conexión o timeout, revisa **Network Access** y la conexión a Internet.

## Integrantes

- Santiago Nahuel Thomas
- Luciana Centurion
- Santiago Sebastian Ojeda

## Clonar y preparar el repositorio con Git

1. Abre una terminal en la carpeta donde quieras guardar el proyecto.
2. Clona el repositorio y entra en la carpeta creada:

```powershell
git clone https://github.com/nahusnt/lista-tareas-personal.git
cd lista-tareas-personal
```

3. Comprueba que Git reconoce el repositorio:

```powershell
git status
```

4. Sigue los pasos de [Instalacion](#instalacion) para crear el entorno virtual, instalar las dependencias y configurar `.env`.

## Subir tus cambios con Git

1. Desde la carpeta del proyecto, revisa los archivos modificados:

```powershell
git status
```

2. Prepara los cambios y verifica lo que vas a incluir:

```powershell
git add .
git diff --cached
```

No agregues `.env`: contiene credenciales locales y esta excluido por `.gitignore`.

3. Crea un commit con un mensaje descriptivo:

```powershell
git commit -m "Describe brevemente los cambios"
```

4. Sube el commit a la rama principal:

```powershell
git push origin main
```
