# Modelo de datos

## Colección

La aplicación usa la base de datos `lista_tareas_db` y la colección `tareas`.

## Documentos de tareas

| Campo | Tipo | Descripción |
|---|---|---|
| `_id` | `ObjectId` | Identificador generado automáticamente por MongoDB. |
| `titulo` | `string` | Título obligatorio de la tarea, de hasta 120 caracteres. |
| `completada` | `boolean` | Indica si la tarea está terminada. Su valor inicial es `false`. |
| `categoria` | `string` | Categoría de la tarea: `Trabajo`, `Personal`, `Estudio` u `Otro`. |
| `etiquetas` | `array[string]` | Lista de hasta cinco etiquetas normalizadas, sin el signo `#`. |

## Índice

Al crear `RepositorioTareas` se ejecuta `create_index("titulo")` sobre la colección `tareas`. MongoDB crea un índice ascendente para `titulo`.

Este índice permite localizar y ordenar las tareas por título con menos trabajo cuando la aplicación usa el orden `titulo`. MongoDB ya crea automáticamente el índice de `_id`; el índice de `titulo` es el índice adicional definido por la aplicación.
