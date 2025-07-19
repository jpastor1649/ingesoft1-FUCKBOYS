from typing import List, Dict, Any
from connector.connector import Connector


class GestorPagos:
    """
    Gestor para operaciones de pagos
    """

    def __init__(self, connector: Connector):
        """
        Constructor del gestor
        """
        self.connector = connector

    def obtener_pagos_mes(self, mes: str) -> List[Dict[str, Any]]:
        """
        Obtener todos los pagos de un mes específico
        """
        self.connector.set_table("pagos")
        return self.connector.get_filtered(f"pago_mes = '{mes.upper()}'")

    def obtener_pagos_apartamento(self, apar_id: int) -> List[Dict[str, Any]]:
        """
        Obtener todos los pagos de un apartamento
        """
        self.connector.set_table("pagos")
        return self.connector.get_filtered(f"pago_lec_apar_id = {apar_id}")

    def obtener_pagos_pendientes(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los pagos pendientes
        """
        self.connector.set_table("pagos")
        return self.connector.get_filtered("pago_estado = 'PENDIENTE'")

    def registrar_pago(
        self, apar_id: int, fecha_lectura: str, servicio: str, fecha_pago: str
    ) -> bool:
        """
        Actualizar un pago como cancelado
        """
        self.connector.set_table("pagos")

        # Actualizar estado y fecha de pago
        values = ("CANCELADO", fecha_pago)

        # Actualizar usando WHERE con múltiples condiciones
        sql = f"""
        UPDATE pagos 
        SET pago_estado = %s, pago_fechaPago = %s 
        WHERE pago_lec_apar_id = '{apar_id}' 
        AND pago_lec_fecha = '{fecha_lectura}' 
        AND pago_lec_servicio = '{servicio}'
        """

        affected = self.connector._execute(sql, values)
        return affected > 0

    def obtener_resumen_pagos(self) -> Dict[str, Any]:
        """
        Obtener resumen general de pagos
        """
        self.connector.set_table("pagos")

        # Total de pagos
        todos = self.connector.get_all()
        total = len(todos)

        # Pagos por estado
        pendientes = len([p for p in todos if p["pago_estado"] == "PENDIENTE"])
        cancelados = len([p for p in todos if p["pago_estado"] == "CANCELADO"])
        cerrados = len([p for p in todos if p["pago_estado"] == "CERRADO"])

        # Valor total
        valor_total = sum(p["pago_valorTotal"] for p in todos)
        valor_pendiente = sum(
            p["pago_valorTotal"] for p in todos if p["pago_estado"] == "PENDIENTE"
        )
        valor_cancelado = sum(
            p["pago_valorTotal"] for p in todos if p["pago_estado"] == "CANCELADO"
        )

        return {
            "total_pagos": total,
            "pendientes": pendientes,
            "cancelados": cancelados,
            "cerrados": cerrados,
            "valor_total": valor_total,
            "valor_pendiente": valor_pendiente,
            "valor_cancelado": valor_cancelado,
        }

    def obtener_pagos_servicio(self, servicio: str) -> List[Dict[str, Any]]:
        """
        Obtener todos los pagos de un servicio específicoo
        """
        self.connector.set_table("pagos")
        return self.connector.get_filtered(f"pago_lec_servicio = '{servicio}'")
