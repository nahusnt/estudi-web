# Modelo de datos

La aplicación usa MongoDB. Las tareas y las cuentas se guardan en colecciones separadas. Los nombres de base de datos se definen en `app.py` y pueden configurarse para cuentas con variables de entorno.

Las preferencias de apariencia no forman parte de estas colecciones: se conservan en `localStorage` del navegador. Consulta [Arquitectura](./ARQUITECTURA.md) para el flujo de acceso y [README.md](../README.md) para configurar la conexión.

## Tareas

**Base:** `lista_tareas_db`
**Colección:** `tareas`

| Campo | Tipo | Descripción |
|---|---|---|
| `_id` | `ObjectId` | Identificador que genera MongoDB. |
| `usuario_id` | `string` | ID de la cuenta propietaria. Las nuevas tareas lo reciben desde la sesión activa. Los documentos antiguos pueden no tenerlo. |
| `titulo` | `string` | Obligatorio, hasta 120 caracteres. |
| `completada` | `boolean` | Estado de la tarea; por defecto `false`. |
| `categoria` | `string` | `Trabajo`, `Personal`, `Estudio` u `Otro`; el valor inicial del modelo es `Personal`. |
| `etiquetas` | `array[string]` | Hasta cinco etiquetas únicas, normalizadas a minúsculas y sin `#`; cada una admite hasta 20 caracteres alfanuméricos, guion o guion bajo. |
| `descripcion` | `string` | Campo opcional, hasta 500 caracteres. |
| `fecha_vencimiento` | `string` o `null` | Fecha opcional en formato ISO `YYYY-MM-DD`. |

Para compatibilidad, al leer documentos anteriores se usan valores por defecto si faltan `completada`, `categoria`, `etiquetas`, `descripcion` o `fecha_vencimiento`. Las tareas antiguas sin `usuario_id` no pertenecen a ninguna cuenta y no aparecen en las vistas de tareas autenticadas.

## Cuentas

**Base por defecto:** `estudi_usuarios_db`
**Colección:** `usuarios`

La base se puede cambiar con `USUARIOS_DB`; el clúster es el definido por `MONGO_URI`, salvo que se configure un `USUARIOS_URI` distinto.

| Campo | Tipo | Descripción |
|---|---|---|
| `_id` | `ObjectId` | Identificador de la cuenta. Su representación como texto se guarda en `usuario_id` de las tareas. |
| `correo` | `string` | Obligatorio, normalizado a minúsculas. |
| `contrasena_hash` | `string` | Hash generado por Werkzeug; nunca se persiste la contraseña en texto plano. |
| `nombre_usuario` | `string` | Nombre público de 3 a 24 caracteres: letras, números, guion o guion bajo. |
| `usuario_normalizado` | `string` | Nombre de usuario normalizado para búsquedas e inicio de sesión sin distinguir mayúsculas. |
| `nombre` | `string` | Nombre visible obligatorio, hasta 60 caracteres. |
| `descripcion` | `string` | Descripción opcional, hasta 280 caracteres. |
| `foto_perfil` | `string` o `null` | Imagen PNG, JPG o WebP representada como data URL; máximo 1 MB. |
| `etiquetas` | `array[string]` | Hasta ocho etiquetas únicas, de hasta 24 caracteres. |

## Índices

- `tareas.titulo`: índice creado por `RepositorioTareas` para el ordenamiento por título.
- `usuarios.correo`: índice único.
- `usuarios.usuario_normalizado`: índice único parcial, aplicado a cuentas que tienen nombre de usuario normalizado.
- MongoDB también crea automáticamente un índice único para `_id` en cada colección.

La unicidad de correo y nombre de usuario también se respalda en la aplicación, pero los índices permiten que MongoDB rechace duplicados incluso ante solicitudes concurrentes.
