from typing import Optional, List, Dict, Any
from connector.connector import Connector


class ServicioEnergia:
    """Servicio para gestionar la energía de los apartamentos."""

    def __init__(self, connector: Connector):
        self.connector = connector
        self.connector.set_table("energia")

    def crear_detalle(
        self, reci_id: int, piso: int, consumo: float, tarifa_kwh: float, descuento: int
    ) -> bool:
        """
        Crear detalle de factura de energía

        Args:
            reci_id: ID del recibo asociado
            piso: Piso del apartamento
            consumo: Consumo en kWh
            tarifa_kwh: Tarifa por kWh
            descuento: Porcentaje de descuento
        """
        if not self._validar_datos(piso, consumo, tarifa_kwh, descuento):
            return False

        if not self._existe_recibo(reci_id):
            print(f"❌ No existe recibo con ID {reci_id}")
            return False

        if self.obtener_por_recibo(reci_id):
            print(f"❌ Ya existe detalle de energía para el recibo {reci_id}")
            return False

        fields = [
            "ener_reci_id",
            "ener_piso",
            "ener_consumo",
            "ener_tarifaKWH",
            "ener_descuento",
        ]
        values = (reci_id, piso, consumo, tarifa_kwh, descuento)

        affected = self.connector.insert(fields, values)
        return affected > 0

    def obtener_por_recibo(self, reci_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener detalle de energía por ID de recibo
        """
        self.connector.set_table("energia")
        where = f"ener_reci_id = {reci_id}"
        results = self.connector.get_filtered(where)
        return results[0] if results else None

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """obtener todos los detalles de energía"""
        self.connector.set_table("energia")

        return self.connector.get_all()

    def actualizar(
        self, reci_id: int, piso: int, consumo: float, tarifa_kwh: float, descuento: int
    ) -> bool:
        """
        Actualizar detalle de energía
        """
        if not self._validar_datos(piso, consumo, tarifa_kwh, descuento):
            return False

        if not self.obtener_por_recibo(reci_id):
            print(f"❌ No existe detalle de energía para el recibo {reci_id}")
            return False

        fields = ["ener_piso", "ener_consumo", "ener_tarifaKWH", "ener_descuento"]
        values = (piso, consumo, tarifa_kwh, descuento)

        affected = self.connector.update(fields, values, "ener_reci_id", reci_id)
        return affected > 0

    def eliminar(self, reci_id: int) -> bool:
        """
        Eliminar detalle de energía
        """
        if not self.obtener_por_recibo(reci_id):
            print(f"❌ No existe detalle de energía para el recibo {reci_id}")
            return False

        where = f"ener_reci_id = {reci_id}"
        sql = f"DELETE FROM energia WHERE {where}"
        affected = self.connector._execute(sql)
        return affected > 0

    def calcular_valor_consumo(self, reci_id: int) -> float:
        """
        Calcular valor por consumo de energía
        """
        detalle = self.obtener_por_recibo(reci_id)
        if not detalle:
            return 0.0

        consumo = float(detalle["ener_consumo"])
        tarifa = float(detalle["ener_tarifaKWH"])

        valor_consumo = consumo * tarifa
        return round(valor_consumo, 2)

    def calcular_valor_total(self, reci_id: int) -> Dict[str, float]:
        """
        Calcular valor total del servicio de energía
        """
        detalle = self.obtener_por_recibo(reci_id)
        if not detalle:
            return {
                "consumo_kwh": 0.0,
                "tarifa_kwh": 0.0,
                "valor_consumo": 0.0,
                "descuento_porcentaje": 0,
                "descuento_valor": 0.0,
                "valor_total": 0.0,
            }

        consumo = float(detalle["ener_consumo"])
        tarifa = float(detalle["ener_tarifaKWH"])
        valor_consumo = self.calcular_valor_consumo(reci_id)

        descuento_porcentaje = int(detalle["ener_descuento"])
        descuento_valor = valor_consumo * (descuento_porcentaje / 100.0)
        valor_total = valor_consumo - descuento_valor

        return {
            "consumo_kwh": round(consumo, 3),
            "tarifa_kwh": round(tarifa, 4),
            "valor_consumo": round(valor_consumo, 2),
            "descuento_porcentaje": descuento_porcentaje,
            "descuento_valor": round(descuento_valor, 2),
            "valor_total": round(valor_total, 2),
        }

    def calcular_distribucion_apartamentos(
        self, reci_id: int, factores_distribucion: Dict[int, float]
    ) -> Dict[int, Dict[str, float]]:
        """
        Calcular distribución del costo entre apartamentos
        """
        calculo_total = self.calcular_valor_total(reci_id)
        valor_total = calculo_total["valor_total"]

        distribucion = {}

        for apar_id, factor in factores_distribucion.items():
            valor_apartamento = valor_total * factor
            consumo_apartamento = calculo_total["consumo_kwh"] * factor

            distribucion[apar_id] = {
                "factor_distribucion": factor,
                "consumo_kwh": round(consumo_apartamento, 3),
                "valor_consumo": round(calculo_total["valor_consumo"] * factor, 2),
                "descuento_aplicado": round(
                    calculo_total["descuento_valor"] * factor, 2
                ),
                "valor_total": round(valor_apartamento, 2),
            }

        return distribucion

    def calcular_costo_promedio_kwh(self, reci_id: int) -> float:
        """
        Calcular costo promedio por kWh incluyendo descuentos
        """
        calculo = self.calcular_valor_total(reci_id)

        if calculo["consumo_kwh"] == 0:
            return 0.0

        return round(calculo["valor_total"] / calculo["consumo_kwh"], 4)

    def obtener_historial_consumos(self, limit: int = 12) -> List[Dict[str, Any]]:
        """
        Obtener historial de consumos de energía
        """
        sql = """
        SELECT e.*, r.reci_fecha, r.reci_mes 
        FROM energia e
        INNER JOIN recibos r ON e.ener_reci_id = r.reci_id
        ORDER BY r.reci_fecha DESC
        LIMIT %s
        """
        return self.connector._fetch(sql.replace("%s", str(limit)))

    def obtener_promedio_consumo_mensual(self) -> float:
        """
        Obtener promedio de consumo mensual en kWh
        """
        sql = """
        SELECT AVG(ener_consumo) as promedio
        FROM energia
        """
        result = self.connector._fetch(sql)
        return float(result[0]["promedio"]) if result and result[0]["promedio"] else 0.0

    def obtener_maximo_consumo_historico(self) -> Dict[str, Any]:
        """
        Obtener el máximo consumo histórico registrado
        """
        sql = """
        SELECT e.*, r.reci_fecha, r.reci_mes 
        FROM energia e
        INNER JOIN recibos r ON e.ener_reci_id = r.reci_id
        ORDER BY e.ener_consumo DESC
        LIMIT 1
        """
        result = self.connector._fetch(sql)
        return result[0] if result else {}

    def calcular_eficiencia_energetica(
        self, reci_id: int, personas_edificio: int
    ) -> Dict[str, float]:
        """
        Calcular indicadores de eficiencia energética

        Args:
            reci_id: ID del recibo
            personas_edificio: Total de personas en el edificio

        Returns:
            Dict con indicadores de eficiencia
        """
        calculo = self.calcular_valor_total(reci_id)
        consumo_total = calculo["consumo_kwh"]

        if personas_edificio == 0:
            return {
                "consumo_total_kwh": consumo_total,
                "consumo_per_capita": 0.0,
                "costo_per_capita": 0.0,
                "eficiencia_economica": 0.0,
            }

        consumo_per_capita = consumo_total / personas_edificio
        costo_per_capita = calculo["valor_total"] / personas_edificio
        eficiencia_economica = (
            calculo["valor_total"] / consumo_total if consumo_total > 0 else 0.0
        )

        return {
            "consumo_total_kwh": round(consumo_total, 3),
            "consumo_per_capita": round(consumo_per_capita, 3),
            "costo_per_capita": round(costo_per_capita, 2),
            "eficiencia_economica": round(eficiencia_economica, 4),
            "personas_edificio": personas_edificio,
        }

    def obtener_estadisticas_tarifas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de tarifas de energía
        """
        detalles = self.obtener_todos()

        if not detalles:
            return {
                "total_registros": 0,
                "tarifa_kwh_promedio": 0.0,
                "tarifa_kwh_maxima": 0.0,
                "tarifa_kwh_minima": 0.0,
                "descuento_promedio": 0.0,
                "consumo_promedio": 0.0,
            }

        tarifas = [float(d["ener_tarifaKWH"]) for d in detalles]
        descuentos = [int(d["ener_descuento"]) for d in detalles]

        return {
            "total_registros": len(detalles),
            "tarifa_kwh_promedio": round(sum(tarifas) / len(tarifas), 4),
            "tarifa_kwh_maxima": max(tarifas),
            "tarifa_kwh_minima": min(tarifas),
            "descuento_promedio": round(sum(descuentos) / len(descuentos), 2),
            "consumo_promedio": self.obtener_promedio_consumo_mensual(),
        }

    def proyectar_consumo_anual(self, reci_id: int) -> Dict[str, float]:
        """
        Proyectar consumo y costo anual basado en el recibo actual
        """
        calculo = self.calcular_valor_total(reci_id)

        consumo_mensual = calculo["consumo_kwh"]
        costo_mensual = calculo["valor_total"]

        proyeccion_anual = {
            "consumo_mensual": round(consumo_mensual, 3),
            "costo_mensual": round(costo_mensual, 2),
            "consumo_anual_proyectado": round(consumo_mensual * 12, 3),
            "costo_anual_proyectado": round(costo_mensual * 12, 2),
            "ahorro_potencial_10_porciento": round((costo_mensual * 12) * 0.1, 2),
            "ahorro_potencial_20_porciento": round((costo_mensual * 12) * 0.2, 2),
        }

        return proyeccion_anual

    def _validar_datos(
        self, piso: int, consumo: float, tarifa_kwh: float, descuento: int
    ) -> bool:
        """
        Validar datos del servicio de energía
        """
        if piso < 1 or piso > 9:
            print("❌ El piso debe estar entre 1 y 9")
            return False

        if consumo < 0:
            print("❌ El consumo no puede ser negativo")
            return False

        if tarifa_kwh < 0:
            print("❌ La tarifa por kWh no puede ser negativa")
            return False

        if descuento < 0 or descuento > 100:
            print("❌ El descuento debe estar entre 0 y 100")
            return False

        return True

    def _existe_recibo(self, reci_id: int) -> bool:
        """
        Verificar si existe un recibo
        """
        tabla_original = self.connector.table
        self.connector.set_table("recibos")

        where = f"reci_id = {reci_id}"
        result = self.connector.get_filtered(where)

        self.connector.set_table(tabla_original)
        return len(result) > 0
