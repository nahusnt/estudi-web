import unittest
from unittest.mock import MagicMock, Mock, patch
from datetime import date, timedelta

from bson import ObjectId

with patch("pymongo.MongoClient"):
    import app as app_module

from modelos import RepositorioTareas, Tarea
# test_app.py verifica las rutas principales de la aplicación y las validaciones del modelo de tareas.
# Usa un repositorio simulado, por lo que las pruebas no necesitan conectarse a MongoDB ni modificar datos reales.
# python -m unittest discover -s tests -v
class RutasTareasTest(unittest.TestCase):
    def setUp(self):
        self.repo = Mock(spec=RepositorioTareas)
        self.repo.cargar_todas.return_value = []
        self.repo.listar_etiquetas.return_value = []
        self.repo.guardar.side_effect = lambda tarea: tarea
        self.repo.cambiar_estado.return_value = None
        self.repo.eliminar.return_value = None
        self.repo_patch = patch.object(app_module, "repo", self.repo)
        self.repo_patch.start()
        self.addCleanup(self.repo_patch.stop)
        self.client = app_module.app.test_client()

    def test_inicio_muestra_tareas_y_carga_filtros(self):
        self.repo.cargar_todas.return_value = [
            Tarea(
                "Preparar entrega",
                categoria="Trabajo",
                etiquetas=["cliente"],
                id_tarea="507f1f77bcf86cd799439011",
                descripcion="Revisar el diseño",
                fecha_vencimiento="2026-10-30",
            )
        ]
        self.repo.listar_etiquetas.return_value = ["cliente"]

        respuesta = self.client.get("/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b"Preparar entrega", respuesta.data)
        self.assertIn(b"Revisar el dise\xc3\xb1o", respuesta.data)
        self.assertIn(b"Vence 30/10/2026", respuesta.data)
        self.repo.cargar_todas.assert_called_once_with(
            estado=None,
            categoria="",
            etiqueta="",
            orden="recientes",
        )
        self.repo.listar_etiquetas.assert_called_once_with()

    def test_filtros_validos_se_envian_al_repositorio(self):
        respuesta = self.client.get(
            "/?estado=pendientes&categoria=Trabajo&etiqueta=%23Urgente&orden=titulo"
        )

        self.assertEqual(respuesta.status_code, 200)
        self.repo.cargar_todas.assert_called_once_with(
            estado=False,
            categoria="Trabajo",
            etiqueta="urgente",
            orden="titulo",
        )

    def test_filtros_invalidos_se_reemplazan_por_valores_seguros(self):
        respuesta = self.client.get(
            "/?estado=desconocido&categoria=Inventada&etiqueta=mal%20etiquetada&orden=azar"
        )

        self.assertEqual(respuesta.status_code, 200)
        self.repo.cargar_todas.assert_called_once_with(
            estado=None,
            categoria="",
            etiqueta="",
            orden="recientes",
        )

    def test_agregar_guarda_tarea_valida(self):
        respuesta = self.client.post(
            "/agregar",
            data={
                "titulo": "Preparar entrega",
                "categoria": "Trabajo",
                "etiquetas": "#cliente urgente",
                "descripcion": "  Revisar el dise\xc3\xb1o  ",
                "fecha_vencimiento": "2026-10-30",
                "seccion": "crear",
            },
        )

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(
            respuesta.location,
            "/?estado=&categoria=Trabajo&etiqueta=&orden=recientes&seccion=crear",
        )
        tarea_guardada = self.repo.guardar.call_args.args[0]
        self.assertEqual(tarea_guardada.titulo, "Preparar entrega")
        self.assertEqual(tarea_guardada.categoria, "Trabajo")
        self.assertEqual(tarea_guardada.etiquetas, ["cliente", "urgente"])
        self.assertEqual(tarea_guardada.descripcion, "Revisar el dise\xc3\xb1o")
        self.assertEqual(tarea_guardada.fecha_vencimiento, date(2026, 10, 30))

    def test_agregar_sin_descripcion_ni_fecha_sigue_funcionando(self):
        respuesta = self.client.post(
            "/agregar",
            data={"titulo": "Tarea simple", "categoria": "Personal"},
        )

        self.assertEqual(respuesta.status_code, 302)
        tarea_guardada = self.repo.guardar.call_args.args[0]
        self.assertEqual(tarea_guardada.descripcion, "")
        self.assertIsNone(tarea_guardada.fecha_vencimiento)

    def test_agregar_fecha_invalida_muestra_error_y_no_guarda(self):
        respuesta = self.client.post(
            "/agregar",
            data={
                "titulo": "Preparar entrega",
                "categoria": "Trabajo",
                "fecha_vencimiento": "30/10/2026",
            },
            follow_redirects=True,
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b"La fecha l\xc3\xadmite debe ser v\xc3\xa1lida", respuesta.data)
        self.repo.guardar.assert_not_called()

    def test_agregar_titulo_invalido_muestra_error_y_no_guarda(self):
        respuesta = self.client.post(
            "/agregar",
            data={"titulo": "   ", "categoria": "Personal", "seccion": "crear"},
            follow_redirects=True,
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b"El t\xc3\xadtulo es obligatorio", respuesta.data)
        self.repo.guardar.assert_not_called()

    def test_resumen_calcula_totales_y_porcentaje(self):
        self.repo.cargar_todas.return_value = [
            Tarea("Pendiente uno", categoria="Trabajo"),
            Tarea("Pendiente dos", categoria="Trabajo"),
            Tarea("Terminada", completada=True, categoria="Personal"),
        ]

        respuesta = self.client.get("/?seccion=resumen")

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b"<strong>3</strong>", respuesta.data)
        self.assertIn(b"<strong>2</strong>", respuesta.data)
        self.assertIn(b"<strong>1</strong>", respuesta.data)
        self.assertIn(b"67%", respuesta.data)
        self.assertIn(b"Progreso completado", respuesta.data)
        self.repo.cargar_todas.assert_called_once_with()
        self.repo.listar_etiquetas.assert_not_called()

    def test_resumen_separa_tareas_vencidas_proximas_y_completadas(self):
        hoy = date.today()
        self.repo.cargar_todas.return_value = [
            Tarea("Atrasada", fecha_vencimiento=hoy - timedelta(days=1)),
            Tarea("Próxima", fecha_vencimiento=hoy + timedelta(days=2)),
            Tarea(
                "Completada futura",
                completada=True,
                fecha_vencimiento=hoy + timedelta(days=1),
            ),
        ]

        respuesta = self.client.get("/?seccion=resumen")

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b"Pr\xc3\xb3ximas \xc2\xb7 7 d\xc3\xadas</span><strong>1", respuesta.data)
        self.assertIn(b"Vencidas</span><strong>1", respuesta.data)
        self.assertIn(b"Atrasada", respuesta.data)
        self.assertIn(b"Pr\xc3\xb3xima", respuesta.data)
        self.assertNotIn(b"Completada futura", respuesta.data)

    def test_navegacion_y_alternativa_de_interfaz_estan_disponibles(self):
        respuesta = self.client.get("/?seccion=ajustes")

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b'aria-label="Secciones principales"', respuesta.data)
        self.assertIn(b'aria-label="Dise\xc3\xb1o de interfaz"', respuesta.data)
        self.assertIn(b'value="compact">Anterior', respuesta.data)
        self.assertIn(b'value="extended">Nueva', respuesta.data)

    def test_toggle_cambia_estado_de_tarea(self):
        id_tarea = "507f1f77bcf86cd799439011"

        respuesta = self.client.post(
            f"/toggle/{id_tarea}",
            data={"seccion": "crear", "estado": "pendientes"},
        )

        self.assertEqual(respuesta.status_code, 302)
        self.repo.cambiar_estado.assert_called_once_with(id_tarea)
        self.assertIn("estado=pendientes", respuesta.location)

    def test_eliminar_borra_tarea(self):
        id_tarea = "507f1f77bcf86cd799439011"

        respuesta = self.client.post(
            f"/eliminar/{id_tarea}",
            data={"seccion": "crear"},
        )

        self.assertEqual(respuesta.status_code, 302)
        self.repo.eliminar.assert_called_once_with(id_tarea)

    def test_id_invalido_responde_404_sin_modificar_datos(self):
        respuesta = self.client.post("/toggle/no-es-un-id")

        self.assertEqual(respuesta.status_code, 404)
        self.repo.cambiar_estado.assert_not_called()
        self.repo.eliminar.assert_not_called()


class ModeloTareaTest(unittest.TestCase):
    def test_rechaza_categoria_invalida(self):
        with self.assertRaisesRegex(ValueError, "categoría válida"):
            Tarea("Tarea", categoria="Inventada")

    def test_rechaza_mas_de_cinco_etiquetas(self):
        with self.assertRaisesRegex(ValueError, "hasta 5 etiquetas"):
            Tarea("Tarea", etiquetas=["uno", "dos", "tres", "cuatro", "cinco", "seis"])

    def test_rechaza_descripcion_mayor_a_quinientos_caracteres(self):
        with self.assertRaisesRegex(ValueError, "500 caracteres"):
            Tarea("Tarea", descripcion="x" * 501)

    def test_rechaza_fecha_invalida(self):
        with self.assertRaisesRegex(ValueError, "fecha límite"):
            Tarea("Tarea", fecha_vencimiento="2026-02-30")

    def test_serializa_fecha_limite_en_formato_iso(self):
        tarea = Tarea(
            "Tarea",
            descripcion="  Detalles  ",
            fecha_vencimiento="2026-10-30",
        )

        self.assertEqual(tarea.descripcion, "Detalles")
        self.assertEqual(tarea.fecha_vencimiento, date(2026, 10, 30))
        self.assertEqual(
            tarea.a_diccionario()["fecha_vencimiento"],
            "2026-10-30",
        )


class RepositorioTareasTest(unittest.TestCase):
    def setUp(self):
        self.coleccion = MagicMock()
        self.db = MagicMock()
        self.db.__getitem__.return_value = self.coleccion
        self.repo = RepositorioTareas(self.db)

    def test_documentos_anteriores_se_cargan_sin_descripcion_ni_fecha(self):
        id_tarea = ObjectId()
        self.coleccion.find.return_value.sort.return_value = [
            {"_id": id_tarea, "titulo": "Tarea existente"}
        ]

        tareas = self.repo.cargar_todas()

        self.assertEqual(len(tareas), 1)
        self.assertEqual(tareas[0].descripcion, "")
        self.assertIsNone(tareas[0].fecha_vencimiento)
        self.coleccion.find.assert_called_once_with(
            {},
            {
                "titulo": 1,
                "completada": 1,
                "categoria": 1,
                "etiquetas": 1,
                "descripcion": 1,
                "fecha_vencimiento": 1,
            },
        )

    def test_guarda_descripcion_y_fecha_limite(self):
        id_tarea = ObjectId()
        self.coleccion.insert_one.return_value.inserted_id = id_tarea
        tarea = Tarea(
            "Tarea nueva",
            descripcion="Detalles",
            fecha_vencimiento="2026-10-30",
        )

        tarea_guardada = self.repo.guardar(tarea)

        self.assertIs(tarea_guardada, tarea)
        self.assertEqual(tarea.id, str(id_tarea))
        self.coleccion.insert_one.assert_called_once_with(
            {
                "titulo": "Tarea nueva",
                "completada": False,
                "categoria": "Personal",
                "etiquetas": [],
                "descripcion": "Detalles",
                "fecha_vencimiento": "2026-10-30",
            }
        )


if __name__ == "__main__":
    unittest.main()
