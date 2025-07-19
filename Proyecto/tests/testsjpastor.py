import unittest
from unittest.mock import MagicMock, patch
import sys

sys.path.append("src")
from models.classes.usuarios import Usuario
from models.classes.lectura import Lectura
from models.classes.recibo import Recibo
from models.classes.pago import Pago


class TestUsuario(unittest.TestCase):

    def setUp(self):
        # Simula un conector con el método set_table
        self.db_mock = MagicMock()
        self.db_mock.set_table = MagicMock()

        # Crea un usuario con base de datos mockeada
        self.usuario = Usuario(self.db_mock)

        # Simula que no es admin y que tiene 2 apartamentos
        self.usuario.es_admin = MagicMock(return_value=False)
        self.usuario.obtener_apartamentos = MagicMock(
            return_value=[{"apar_id": 1}, {"apar_id": 202}]
        )

    @patch("models.classes.usuarios.Lectura")
    def test_obtener_lecturas_filtradas_por_mes(self, MockLectura):
        # Simular datos de lectura
        lectura_instance = MockLectura.return_value
        lectura_instance.obtener_por_apartamento.side_effect = lambda aid: [
            {"lec_mes": "ENERO", "valor": 10, "apar_id": aid}
        ]

        lecturas = self.usuario.obtener_lecturas(mes="ENERO")
        self.assertEqual(len(lecturas), 2)
        for lec in lecturas:
            self.assertEqual(lec["lec_mes"], "ENERO")

    @patch("models.classes.usuarios.Recibo")
    def test_obtener_recibos_admin_sin_filtro(self, MockRecibo):
        # Convertir usuario a admin
        self.usuario.es_admin = MagicMock(return_value=True)

        # Simular resultados
        recibo_instance = MockRecibo.return_value
        recibo_instance.obtener_todos.return_value = [
            {"reci_mes": "MARZO", "apar_id": 1},
            {"reci_mes": "ABRIL", "apar_id": 2},
        ]

        recibos = self.usuario.obtener_recibos()
        self.assertEqual(len(recibos), 2)

    @patch("models.classes.usuarios.Pago")
    def test_obtener_pagos_filtrados_por_apartamento_y_mes(self, MockPago):
        pago_instance = MockPago.return_value
        pago_instance.obtener_por_apartamento.side_effect = lambda aid: [
            {"pago_mes": "MAYO", "apar_id": aid}
        ]

        pagos = self.usuario.obtener_pagos(mes="MAYO", apar_id=1)
        self.assertEqual(len(pagos), 1)
        self.assertEqual(pagos[0]["apar_id"], 1)
        self.assertEqual(pagos[0]["pago_mes"], "MAYO")

    @patch("models.classes.usuarios.Lectura")
    def test_obtener_lecturas_sin_apartamentos(self, MockLectura):
        # Simula que el usuario no tiene apartamentos
        self.usuario.obtener_apartamentos = MagicMock(return_value=[])

        lectura_instance = MockLectura.return_value
        lectura_instance.obtener_por_apartamento.return_value = []

        lecturas = self.usuario.obtener_lecturas()
        self.assertEqual(lecturas, [])

    @patch("models.classes.usuarios.Recibo")
    def test_obtener_recibos_admin_filtrado_por_mes_y_apartamento(self, MockRecibo):
        # Simula que el usuario es admin
        self.usuario.es_admin = MagicMock(return_value=True)

        recibo_instance = MockRecibo.return_value
        recibo_instance.obtener_por_apartamento.return_value = [
            {"reci_mes": "ABRIL", "apar_id": 2}
        ]

        recibos = self.usuario.obtener_recibos(mes="ABRIL", apar_id=2)
        self.assertEqual(len(recibos), 1)
        self.assertEqual(recibos[0]["reci_mes"], "ABRIL")
        self.assertEqual(recibos[0]["apar_id"], 2)

    @patch("models.classes.usuarios.Pago")
    @patch("builtins.print")
    def test_obtener_pagos_sin_resultados(self, mock_print, MockPago):
        pago_instance = MockPago.return_value
        pago_instance.obtener_por_apartamento.return_value = []

        pagos = self.usuario.obtener_pagos(mes="JUNIO")

        self.assertEqual(pagos, [])
        mock_print.assert_called_once_with("No hay pagos registrados")

if __name__ == "__main__":
    unittest.main()
