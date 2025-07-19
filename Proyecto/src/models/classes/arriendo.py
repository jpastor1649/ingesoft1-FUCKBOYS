from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import sys

sys.path.append("src")
from connector.connector import Connector


class Arriendo:
    """Clase para manejar los arrendos del sistema de arrendamiento"""

    ESTADOS_VALIDOS = ["CANCELADO", "PENDIENTE", "CERRADO"]

    def __init__(self, connector: Connector):
        self.connector = connector
        self.connector.set_table("arrendos")

    def crear(
        self,
        inq_id: int,
        apar_id: int,
        fecha_inicio: str,
        fecha_fin: str,
        mes: str,
        valor: int,
        estado: str = "PENDIENTE",
        fecha_pago: str = None,
        observaciones: str = "",
    ) -> bool:
        """Crear un nuevo arriendo"""
        if not self._validar_datos(
            inq_id, apar_id, fecha_inicio, fecha_fin, mes, valor, estado
        ):
            return False

        if self._existe_conflicto_fechas(apar_id, fecha_inicio, fecha_fin):
            print(
                f"❌ Conflicto de fechas: el apartamento {apar_id} ya tiene arriendo en ese período"
            )
            return False

        fields = [
            "arre_inq_id",
            "arre_apar_id",
            "arre_fechaInicio",
            "arre_fechaFin",
            "arre_mes",
            "arre_valor",
            "arre_fechaPago",
            "arre_estado",
            "arre_observaciones",
        ]
        values = (
            inq_id,
            apar_id,
            fecha_inicio,
            fecha_fin,
            mes.upper(),
            valor,
            fecha_pago,
            estado,
            observaciones.strip() if observaciones else None,
        )

        affected = self.connector.insert(fields, values)
        return affected > 0

    def obtener_por_id(
        self, fecha_inicio: str, apar_id: int, inq_id: int
    ) -> Optional[Dict[str, Any]]:
        """Obtener un arriendo por su ID"""
        where = f"arre_fechaInicio = '{fecha_inicio}' AND arre_apar_id = {apar_id} AND arre_inq_id = {inq_id}"
        results = self.connector.get_filtered(where)
        return results[0] if results else None

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtener todos los arrendos"""
        return self.connector.get_all()

    def obtener_por_inquilino(self, inq_id: int) -> List[Dict[str, Any]]:
        """Obtener arrendos de un inquilino específico"""
        where = f"arre_inq_id = {inq_id} ORDER BY arre_fechaInicio DESC"
        return self.connector.get_filtered(where)

    def obtener_por_apartamento(self, apar_id: int) -> List[Dict[str, Any]]:
        """Obtener arrendos de un apartamento específico"""
        where = f"arre_apar_id = {apar_id} ORDER BY arre_fechaInicio DESC"
        return self.connector.get_filtered(where)

    def obtener_activos(self) -> List[Dict[str, Any]]:
        """Obtener arrendos activos (no cerrados ni cancelados)"""
        where = (
            "arre_estado IN ('PENDIENTE', 'CANCELADO') ORDER BY arre_fechaInicio DESC"
        )
        return self.connector.get_filtered(where)

    def obtener_por_mes(self, mes: str) -> List[Dict[str, Any]]:
        """Obtener arrendos de un mes específico"""
        where = f"arre_mes = '{mes.upper()}'"
        return self.connector.get_filtered(where)

    def obtener_pendientes_pago(self) -> List[Dict[str, Any]]:
        """Obtener arrendos pendientes de pago"""
        where = "arre_estado = 'PENDIENTE' AND arre_fechaPago IS NULL"
        return self.connector.get_filtered(where)

    def actualizar_estado(
        self,
        fecha_inicio: str,
        apar_id: int,
        inq_id: int,
        nuevo_estado: str,
        fecha_pago: str = None,
    ) -> bool:
        """Actualizar el estado de un arriendo"""
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            print(f"❌ Estado inválido: {nuevo_estado}")
            return False

        arriendo = self.obtener_por_id(fecha_inicio, apar_id, inq_id)
        if not arriendo:
            print("❌ Arriendo no encontrado")
            return False

        fields = ["arre_estado"]
        values = [nuevo_estado]

        if fecha_pago:
            fields.append("arre_fechaPago")
            values.append(fecha_pago)

        where_fields = ["arre_fechaInicio", "arre_apar_id", "arre_inq_id"]
        where_values = [fecha_inicio, apar_id, inq_id]
        where_clause = " AND ".join([f"{field} = %s" for field in where_fields])

        sql = f"UPDATE arrendos SET {', '.join([f'{field} = %s' for field in fields])} WHERE {where_clause}"
        affected = self.connector._execute(sql, tuple(values + where_values))
        return affected > 0

    def registrar_pago(
        self, fecha_inicio: str, apar_id: int, inq_id: int, fecha_pago: str
    ) -> bool:
        """Registrar el pago de un arriendo"""
        return self.actualizar_estado(
            fecha_inicio, apar_id, inq_id, "CANCELADO", fecha_pago
        )

    def cerrar_arriendo(self, fecha_inicio: str, apar_id: int, inq_id: int) -> bool:
        """Cerrar un arriendo"""
        return self.actualizar_estado(fecha_inicio, apar_id, inq_id, "CERRADO")

    def actualizar_valor(
        self, fecha_inicio: str, apar_id: int, inq_id: int, nuevo_valor: int
    ) -> bool:
        """Actualizar el valor de un arriendo"""
        if nuevo_valor <= 0:
            print("❌ El valor debe ser positivo")
            return False

        arriendo = self.obtener_por_id(fecha_inicio, apar_id, inq_id)
        if not arriendo:
            print("❌ Arriendo no encontrado")
            return False

        where_fields = ["arre_fechaInicio", "arre_apar_id", "arre_inq_id"]
        where_values = [fecha_inicio, apar_id, inq_id]
        where_clause = " AND ".join([f"{field} = %s" for field in where_fields])

        sql = f"UPDATE arrendos SET arre_valor = %s WHERE {where_clause}"
        affected = self.connector._execute(sql, tuple([nuevo_valor] + where_values))
        return affected > 0

    def obtener_ingresos_mes(self, mes: str) -> Dict[str, Any]:
        """Obtener ingresos de arrendos para un mes específico"""
        arrendos_mes = self.obtener_por_mes(mes)

        total_esperado = sum(arr["arre_valor"] for arr in arrendos_mes)
        pagados = [arr for arr in arrendos_mes if arr["arre_estado"] == "CANCELADO"]
        total_pagado = sum(arr["arre_valor"] for arr in pagados)
        pendientes = [arr for arr in arrendos_mes if arr["arre_estado"] == "PENDIENTE"]
        total_pendiente = sum(arr["arre_valor"] for arr in pendientes)

        return {
            "mes": mes,
            "total_arrendos": len(arrendos_mes),
            "total_esperado": total_esperado,
            "total_pagado": total_pagado,
            "total_pendiente": total_pendiente,
            "arrendos_pagados": len(pagados),
            "arrendos_pendientes": len(pendientes),
            "porcentaje_recaudo": (
                round((total_pagado / total_esperado) * 100, 2)
                if total_esperado > 0
                else 0
            ),
        }

    def obtener_morosos(self) -> List[Dict[str, Any]]:
        """Obtener arrendos con pagos pendientes por más de 30 días"""
        fecha_limite = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        where = f"arre_estado = 'PENDIENTE' AND arre_fechaFin < '{fecha_limite}'"
        return self.connector.get_filtered(where)

    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """Obtener estadísticas generales de arrendos"""
        todos = self.obtener_todos()
        activos = self.obtener_activos()
        pendientes = self.obtener_pendientes_pago()

        if not todos:
            return {
                "total_arrendos": 0,
                "arrendos_activos": 0,
                "arrendos_pendientes": 0,
                "valor_promedio": 0,
                "ingresos_totales": 0,
            }

        valores = [arr["arre_valor"] for arr in todos]
        pagados = [arr for arr in todos if arr["arre_estado"] == "CANCELADO"]

        return {
            "total_arrendos": len(todos),
            "arrendos_activos": len(activos),
            "arrendos_pendientes": len(pendientes),
            "arrendos_cerrados": len(
                [arr for arr in todos if arr["arre_estado"] == "CERRADO"]
            ),
            "valor_promedio": round(sum(valores) / len(valores), 2),
            "valor_minimo": min(valores),
            "valor_maximo": max(valores),
            "ingresos_totales": sum(arr["arre_valor"] for arr in pagados),
        }

    def _validar_datos(
        self,
        inq_id: int,
        apar_id: int,
        fecha_inicio: str,
        fecha_fin: str,
        mes: str,
        valor: int,
        estado: str,
    ) -> bool:
        if inq_id <= 0 or apar_id <= 0:
            print("❌ Los IDs deben ser números positivos")
            return False

        try:
            fecha_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

            if fecha_ini >= fecha_fin:
                print("❌ La fecha de inicio debe ser anterior a la fecha de fin")
                return False

        except ValueError:
            print("❌ Formato de fecha inválido. Use YYYY-MM-DD")
            return False

        if not mes or len(mes.strip()) == 0:
            print("❌ El mes es obligatorio")
            return False

        if valor <= 0:
            print("❌ El valor debe ser positivo")
            return False

        if estado not in self.ESTADOS_VALIDOS:
            print(
                f"❌ Estado inválido. Debe ser uno de: {', '.join(self.ESTADOS_VALIDOS)}"
            )
            return False

        if not self._existe_inquilino(inq_id):
            print(f"❌ No existe inquilino con ID {inq_id}")
            return False

        if not self._existe_apartamento(apar_id):
            print(f"❌ No existe apartamento con ID {apar_id}")
            return False

        return True

    def _existe_conflicto_fechas(
        self, apar_id: int, fecha_inicio: str, fecha_fin: str
    ) -> bool:
        where = f"""
        arre_apar_id = {apar_id} 
        AND arre_estado != 'CERRADO'
        AND (
            (arre_fechaInicio <= '{fecha_inicio}' AND arre_fechaFin >= '{fecha_inicio}')
            OR (arre_fechaInicio <= '{fecha_fin}' AND arre_fechaFin >= '{fecha_fin}')
            OR (arre_fechaInicio >= '{fecha_inicio}' AND arre_fechaFin <= '{fecha_fin}')
        )
        """
        conflictos = self.connector.get_filtered(where)
        return len(conflictos) > 0

    def _existe_inquilino(self, inq_id: int) -> bool:
        tabla_original = self.connector.table
        self.connector.set_table("inquilinos")
        where = f"inq_id = {inq_id}"
        result = self.connector.get_filtered(where)
        self.connector.set_table(tabla_original)
        return len(result) > 0

    def _existe_apartamento(self, apar_id: int) -> bool:
        tabla_original = self.connector.table
        self.connector.set_table("apartamentos")
        where = f"apar_id = {apar_id}"
        result = self.connector.get_filtered(where)
        self.connector.set_table(tabla_original)
        return len(result) > 0
