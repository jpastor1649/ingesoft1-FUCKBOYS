from datetime import datetime  
from typing import Dict, List, Any, Optional  

from connector.connector import Connector  
from services.servicio_acueducto import ServicioAcueducto
from services.servicio_energia import ServicioEnergia
from services.servicio_gas import ServicioGas



class CalculadoraRecibos:
    def __init__(self, connector: Connector):
        self.connector = connector
        self.servicio_acueducto = ServicioAcueducto(connector)
        self.servicio_energia = ServicioEnergia(connector)
        self.servicio_gas = ServicioGas(connector)

    def calcular_recibo_apartamento_mes(self, apar_id: int, mes: str) -> Dict[str, Any]:
        """
        Calcular recibo total de un apartamento para un mes específico
        """
        # Obtener arriendo del mes
        arriendo = self._obtener_arriendo_mes(apar_id, mes)

        # Calcular servicios
        servicios = {}
        total_servicios = 0

        # Procesar cada servicio
        for servicio_nombre in ["ACUEDUCTO Y ASEO", "ENERGIA", "GAS NATURAL"]:
            valor = self._calcular_servicio_apartamento(apar_id, mes, servicio_nombre)
            if valor > 0:
                servicios[servicio_nombre] = valor
                total_servicios += valor

        # Calcular totales
        total_arriendo = arriendo.get("valor", 0) if arriendo else 0
        total_general = total_arriendo + total_servicios

        return {
            "apartamento_id": apar_id,
            "mes": mes,
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d"),
            "arriendo": {
                "valor": total_arriendo,
                "estado": (
                    arriendo.get("estado", "SIN_DATOS") if arriendo else "SIN_DATOS"
                ),
            },
            "servicios": servicios,
            "total_servicios": total_servicios,
            "total_arriendo": total_arriendo,
            "total_general": total_general,
        }

    def calcular_distribucion_mes_completo(self, mes: str) -> Dict[str, Any]:
        """
        Calcular distribución de servicios para todos los apartamentos en un mes
        """
        # Obtener apartamentos ocupados
        apartamentos = self._obtener_apartamentos_ocupados_mes(mes)
        if not apartamentos:
            return {"error": f"No hay apartamentos ocupados en {mes}"}

        distribucion = {}

        # Calcular para cada apartamento
        for apartamento in apartamentos:
            apar_id = apartamento["apar_id"]
            recibo = self.calcular_recibo_apartamento_mes(apar_id, mes)
            distribucion[apar_id] = recibo

        # Calcular totales generales
        total_arrendos = sum(r.get("total_arriendo", 0) for r in distribucion.values())
        total_servicios = sum(
            r.get("total_servicios", 0) for r in distribucion.values()
        )

        return {
            "mes": mes,
            "apartamentos": distribucion,
            "totales": {
                "total_apartamentos": len(apartamentos),
                "total_arrendos": total_arrendos,
                "total_servicios": total_servicios,
                "total_general": total_arrendos + total_servicios,
            },
        }

    def _calcular_factor_consumo_apartamento(
        self, apar_id: int, mes: str, servicio: str
    ) -> float:
        """
        Calcular factor de distribución de un apartamento basado en su consumo
        """
        # Obtener consumo del apartamento
        consumo_apartamento = self._obtener_consumo_apartamento(apar_id, mes, servicio)

        # Obtener consumo total de todos los apartamentos ocupados
        apartamentos = self._obtener_apartamentos_ocupados_mes(mes)
        consumo_total = 0

        for apt in apartamentos:
            consumo_total += self._obtener_consumo_apartamento(
                apt["apar_id"], mes, servicio
            )

        # Calcular factor
        if consumo_total > 0:
            return consumo_apartamento / consumo_total
        else:
            # Si no hay consumo registrado, distribuir equitativamente
            return 1.0 / len(apartamentos) if apartamentos else 0.0

    def _calcular_servicio_apartamento(
        self, apar_id: int, mes: str, servicio: str
    ) -> float:
        """
        Calcular valor de un servicio específico para un apartamento
        """
        # Obtener recibo del servicio
        recibo = self._obtener_recibo_servicio_mes(mes, servicio)
        if not recibo:
            return 0.0

        reci_id = recibo["reci_id"]

        # Calcular valor total del servicio
        if servicio == "ACUEDUCTO Y ASEO":
            detalle = self.servicio_acueducto.obtener_por_recibo(reci_id)
            if not detalle:
                return 0.0
            calculo = self.servicio_acueducto.calcular_valor_total(reci_id)
        elif servicio == "ENERGIA":
            detalle = self.servicio_energia.obtener_por_recibo(reci_id)
            if not detalle:
                return 0.0
            calculo = self.servicio_energia.calcular_valor_total(reci_id)
        elif servicio == "GAS NATURAL":
            detalle = self.servicio_gas.obtener_por_recibo(reci_id)
            if not detalle:
                return 0.0
            calculo = self.servicio_gas.calcular_valor_total(reci_id)
        else:
            return 0.0

        # Calcular factor de distribución para este apartamento
        factor = self._calcular_factor_consumo_apartamento(apar_id, mes, servicio)

        # Calcular valor proporcional
        valor_total = calculo.get("valor_total", 0)
        return round(valor_total * factor, 2)

    def _obtener_arriendo_mes(self, apar_id: int, mes: str) -> Optional[Dict[str, Any]]:
        """Obtener arriendo de un apartamento en un mes"""
        tabla_original = self.connector.table
        self.connector.set_table("arrendos")

        where = f"arre_apar_id = {apar_id} AND arre_mes = '{mes.upper()}'"
        result = self.connector.get_filtered(where)

        self.connector.set_table(tabla_original)

        if result:
            arriendo = result[0]
            return {
                "valor": arriendo["arre_valor"],
                "estado": arriendo["arre_estado"],
                "fecha_pago": arriendo["arre_fechaPago"],
            }
        return None

    def _obtener_apartamentos_ocupados_mes(self, mes: str) -> List[Dict[str, Any]]:
        """Obtener apartamentos ocupados en un mes"""
        sql = """
        SELECT DISTINCT a.*
        FROM apartamentos a
        INNER JOIN arrendos ar ON a.apar_id = ar.arre_apar_id
        WHERE ar.arre_mes = %s AND ar.arre_estado IN ('PENDIENTE', 'CANCELADO')
        """
        return self.connector._fetch(sql.replace("%s", f"'{mes.upper()}'"))

    def _obtener_recibo_servicio_mes(
        self, mes: str, servicio: str
    ) -> Optional[Dict[str, Any]]:
        """Obtener recibo de un servicio en un mes"""
        tabla_original = self.connector.table
        self.connector.set_table("recibos")

        where = f"reci_mes = '{mes.upper()}' AND reci_servicio = '{servicio}'"
        result = self.connector.get_filtered(where)

        self.connector.set_table(tabla_original)
        return result[0] if result else None

    def _obtener_consumo_apartamento(
        self, apar_id: int, mes: str, servicio: str
    ) -> float:
        """Obtener consumo de un apartamento para un servicio en un mes"""
        tabla_original = self.connector.table
        self.connector.set_table("lecturas")

        where = f"lec_apar_id = {apar_id} AND lec_mes = '{mes.upper()}' AND lec_servicio = '{servicio}'"
        lecturas = self.connector.get_filtered(where)

        self.connector.set_table(tabla_original)

        consumo_total = 0.0
        for lectura in lecturas:
            consumo = float(lectura["lec_consumoFinal"]) - float(
                lectura["lec_consumoInicial"]
            )
            consumo_total += consumo

        return consumo_total
