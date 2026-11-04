# Estado actual del proyecto

Este documento resume las partes principales de Estudi Web para orientar el trabajo en el repositorio. La guía de instalación y la descripción completa de carpetas están en `README.md`.

## Funcionalidades actuales

- Registro e inicio de sesión mediante correo o nombre de usuario.
- Sesión requerida para acceder a las secciones de tareas, resumen, ajustes y perfil.
- Tareas asociadas al usuario activo, con alta, finalización, eliminación, filtros y orden.
- Resumen con totales, progreso, categorías y fechas vencidas o próximas.
- Perfil editable con nombre de usuario, nombre visible, descripción, etiquetas y foto.
- Preferencias de interfaz guardadas en el navegador: disposición, tema, paleta, idioma, tamaño del texto, densidad, contraste y animaciones.
- Los modelos validan los datos recibidos; Jinja escapa el contenido de usuario al renderizarlo y las contraseñas se almacenan con hashes de Werkzeug.
- Los errores de MongoDB se registran internamente y se responden con un mensaje genérico; debug permanece desactivado por defecto.
- Pruebas automatizadas con repositorios simulados; cubren validación, XSS y manejo de errores sin conectarse a MongoDB.

## Archivos de referencia

| Archivo | Responsabilidad |
|---|---|
| `app.py` | Aplicación Flask, rutas, sesiones, errores genéricos de MongoDB y configuración de conexiones. |
| `modelos.py` | Modelo y repositorio de tareas. |
| `usuarios.py` | Modelo y repositorio de cuentas. |
| `templates/` | Vistas de la aplicación, login y registro. |
| `static/css/styles.css` | Diseño visual, temas y responsive. |
| `static/js/app.js` | Preferencias locales y comportamiento del frontend. |
| `tests/test_app.py` | Pruebas de rutas, modelos, repositorios y controles de seguridad. |
| `docs/` | Arquitectura, modelo de datos y diario. |

## Datos y configuración

- Las tareas se guardan en `lista_tareas_db.tareas` dentro del clúster de `MONGO_URI`.
- Las cuentas se guardan por defecto en `estudi_usuarios_db.usuarios`. `USUARIOS_DB` cambia esa base y `USUARIOS_URI` permite configurar otro clúster.
- `FLASK_SECRET_KEY` debe definirse como secreto persistente en producción.
- El archivo `.env` local está excluido de Git. No guardar credenciales en el repositorio.
- Las tareas antiguas que no tienen `usuario_id` requieren una migración manual/controlada para asociarse con una cuenta.

## Desarrollo y pruebas

Instala las dependencias con `python -m pip install -r requirements.txt`, configura `.env` y ejecuta localmente con `python app.py`. La suite se ejecuta desde la raíz:

```bash
python -m unittest discover -s tests -v
```

Consulta `README.md` para los pasos completos. Antes de desplegar, revisa `SECURITY.md`; en particular, la protección CSRF, la clave de sesión, las cookies y el modo de depuración.
