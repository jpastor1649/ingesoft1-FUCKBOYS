from typing import Optional, List, Dict, Any
from connector.connector import Connector


class ServicioGas:
    def __init__(self, connector: Connector):
        self.connector = connector
        self.connector.set_table("gas")

    def crear_detalle(
        self, reci_id: int, consumo: float, tarifa_fija: float, tarifa_m3: float
    ) -> bool:
        """
        Crear detalle de factura de gas natural

        Args:
            reci_id: ID del recibo asociado
            consumo: Consumo en m3
            tarifa_fija: Tarifa fija mensual
            tarifa_m3: Tarifa por m3
        """
        if not self._validar_datos(consumo, tarifa_fija, tarifa_m3):
            return False

        if not self._existe_recibo(reci_id):
            print(f"❌ No existe recibo con ID {reci_id}")
            return False

        if self.obtener_por_recibo(reci_id):
            print(f"❌ Ya existe detalle de gas para el recibo {reci_id}")
            return False

        fields = ["gas_reci_id", "gas_consumo", "gas_tarifaFija", "gas_tarifaM3"]
        values = (reci_id, consumo, tarifa_fija, tarifa_m3)

        affected = self.connector.insert(fields, values)
        return affected > 0

    def obtener_por_recibo(self, reci_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener detalle de gas por ID de recibo
        """
        self.connector.set_table("gas")
        where = f"gas_reci_id = {reci_id}"
        results = self.connector.get_filtered(where)
        return results[0] if results else None

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los detalles de gas
        """
        self.connector.set_table("gas")
        return self.connector.get_all()

    def actualizar(
        self, reci_id: int, consumo: float, tarifa_fija: float, tarifa_m3: float
    ) -> bool:
        """
        Actualizar detalle de gas
        """
        if not self._validar_datos(consumo, tarifa_fija, tarifa_m3):
            return False

        if not self.obtener_por_recibo(reci_id):
            print(f"❌ No existe detalle de gas para el recibo {reci_id}")
            return False

        fields = ["gas_consumo", "gas_tarifaFija", "gas_tarifaM3"]
        values = (consumo, tarifa_fija, tarifa_m3)

        affected = self.connector.update(fields, values, "gas_reci_id", reci_id)
        return affected > 0

    def eliminar(self, reci_id: int) -> bool:
        """
        Eliminar detalle de gas
        """
        if not self.obtener_por_recibo(reci_id):
            print(f"❌ No existe detalle de gas para el recibo {reci_id}")
            return False

        where = f"gas_reci_id = {reci_id}"
        sql = f"DELETE FROM gas WHERE {where}"
        affected = self.connector._execute(sql)
        return affected > 0

    def calcular_valor_fijo(self, reci_id: int) -> float:
        """
        Calcular valor de la tarifa fija
        """
        detalle = self.obtener_por_recibo(reci_id)
        if not detalle:
            return 0.0

        return float(detalle["gas_tarifaFija"])

    def calcular_valor_consumo(self, reci_id: int) -> float:
        """
        Calcular valor por consumo de gas
        """
        detalle = self.obtener_por_recibo(reci_id)
        if not detalle:
            return 0.0

        consumo = float(detalle["gas_consumo"])
        tarifa_m3 = float(detalle["gas_tarifaM3"])

        valor_consumo = consumo * tarifa_m3
        return round(valor_consumo, 2)

    def calcular_valor_total(self, reci_id: int) -> Dict[str, float]:
        """
        Calcular valor total del servicio de gas natural
        """
        detalle = self.obtener_por_recibo(reci_id)
        if not detalle:
            return {
                "consumo_m3": 0.0,
                "tarifa_fija": 0.0,
                "tarifa_m3": 0.0,
                "valor_fijo": 0.0,
                "valor_consumo": 0.0,
                "valor_total": 0.0,
            }

        consumo = float(detalle["gas_consumo"])
        tarifa_fija = float(detalle["gas_tarifaFija"])
        tarifa_m3 = float(detalle["gas_tarifaM3"])

        valor_fijo = tarifa_fija
        valor_consumo = self.calcular_valor_consumo(reci_id)
        valor_total = valor_fijo + valor_consumo

        return {
            "consumo_m3": round(consumo, 3),
            "tarifa_fija": round(tarifa_fija, 2),
            "tarifa_m3": round(tarifa_m3, 4),
            "valor_fijo": round(valor_fijo, 2),
            "valor_consumo": round(valor_consumo, 2),
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
            consumo_apartamento = calculo_total["consumo_m3"] * factor

            distribucion[apar_id] = {
                "factor_distribucion": factor,
                "consumo_m3": round(consumo_apartamento, 3),
                "valor_fijo": round(calculo_total["valor_fijo"] * factor, 2),
                "valor_consumo": round(calculo_total["valor_consumo"] * factor, 2),
                "valor_total": round(valor_apartamento, 2),
            }

        return distribucion

    def calcular_costo_promedio_m3(self, reci_id: int) -> float:
        """
        Calcular costo promedio por m3 incluyendo tarifa fija
        """
        calculo = self.calcular_valor_total(reci_id)

        if calculo["consumo_m3"] == 0:
            return calculo["tarifa_m3"]  # Solo tarifa variable si no hay consumo

        return round(calculo["valor_total"] / calculo["consumo_m3"], 4)

    def analizar_eficiencia_consumo(self, reci_id: int) -> Dict[str, Any]:
        """
        Analizar eficiencia del consumo de gas
        """
        calculo = self.calcular_valor_total(reci_id)
        consumo = calculo["consumo_m3"]
        valor_total = calculo["valor_total"]

        # Rangos de consumo eficiente (aproximados para Colombia)
        rangos = {
            "muy_eficiente": (0, 15),
            "eficiente": (15, 25),
            "moderado": (25, 40),
            "alto": (40, float("inf")),
        }

        categoria = "muy_eficiente"
        for cat, (min_val, max_val) in rangos.items():
            if min_val <= consumo < max_val:
                categoria = cat
                break

        recomendaciones = self._generar_recomendaciones_gas(categoria, consumo)

        return {
            "consumo_m3": round(consumo, 3),
            "valor_total": round(valor_total, 2),
            "categoria_eficiencia": categoria,
            "costo_promedio_m3": self.calcular_costo_promedio_m3(reci_id),
            "recomendaciones": recomendaciones,
            "porcentaje_tarifa_fija": (
                round((calculo["valor_fijo"] / valor_total) * 100, 2)
                if valor_total > 0
                else 0
            ),
        }

    def obtener_historial_consumos(self, limit: int = 12) -> List[Dict[str, Any]]:
        """
        Obtener historial de consumos de gas
        """
        sql = """
        SELECT g.*, r.reci_fecha, r.reci_mes 
        FROM gas g
        INNER JOIN recibos r ON g.gas_reci_id = r.reci_id
        ORDER BY r.reci_fecha DESC
        LIMIT %s
        """
        return self.connector._fetch(sql.replace("%s", str(limit)))

    def obtener_promedio_consumo_mensual(self) -> float:
        """
        Obtener promedio de consumo mensual en m3
        """
        sql = """
        SELECT AVG(gas_consumo) as promedio
        FROM gas
        """
        result = self.connector._fetch(sql)
        return float(result[0]["promedio"]) if result and result[0]["promedio"] else 0.0

    def proyectar_consumo_anual(self, reci_id: int) -> Dict[str, float]:
        """
        Proyectar consumo y costo anual basado en el recibo actual

        Args:
            reci_id: ID del recibo

        Returns:
            Dict con proyección anual
        """
        calculo = self.calcular_valor_total(reci_id)

        consumo_mensual = calculo["consumo_m3"]
        costo_mensual = calculo["valor_total"]

        return {
            "consumo_mensual": round(consumo_mensual, 3),
            "costo_mensual": round(costo_mensual, 2),
            "consumo_anual_proyectado": round(consumo_mensual * 12, 3),
            "costo_anual_proyectado": round(costo_mensual * 12, 2),
            "tarifa_fija_anual": round(calculo["valor_fijo"] * 12, 2),
            "costo_variable_anual": round(calculo["valor_consumo"] * 12, 2),
        }

    def obtener_estadisticas_tarifas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de tarifas de gas
        """
        detalles = self.obtener_todos()

        if not detalles:
            return {
                "total_registros": 0,
                "tarifa_fija_promedio": 0.0,
                "tarifa_m3_promedio": 0.0,
                "consumo_promedio": 0.0,
            }

        tarifas_fijas = [float(d["gas_tarifaFija"]) for d in detalles]
        tarifas_m3 = [float(d["gas_tarifaM3"]) for d in detalles]

        return {
            "total_registros": len(detalles),
            "tarifa_fija_promedio": round(sum(tarifas_fijas) / len(tarifas_fijas), 2),
            "tarifa_fija_maxima": max(tarifas_fijas),
            "tarifa_fija_minima": min(tarifas_fijas),
            "tarifa_m3_promedio": round(sum(tarifas_m3) / len(tarifas_m3), 4),
            "tarifa_m3_maxima": max(tarifas_m3),
            "tarifa_m3_minima": min(tarifas_m3),
            "consumo_promedio": self.obtener_promedio_consumo_mensual(),
        }

    def _validar_datos(
        self, consumo: float, tarifa_fija: float, tarifa_m3: float
    ) -> bool:
        """
        Validar datos del servicio de gas

        Args:
            consumo: Consumo en m3
            tarifa_fija: Tarifa fija mensual
            tarifa_m3: Tarifa por m3

        Returns:
            bool: True si los datos son válidos
        """
        if consumo < 0:
            print("❌ El consumo no puede ser negativo")
            return False

        if tarifa_fija < 0:
            print("❌ La tarifa fija no puede ser negativa")
            return False

        if tarifa_m3 < 0:
            print("❌ La tarifa por m3 no puede ser negativa")
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
