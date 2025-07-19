from typing import Optional, List, Dict, Any
from datetime import datetime
from connector.connector import Connector


class Lectura:
    """Clase para manejar las lecturas de servicios de los apartamentos"""

    SERVICIOS_VALIDOS = ["ACUEDUCTO Y ASEO", "ENERGIA", "GAS NATURAL"]

    def __init__(self, connector: Connector):
        self.connector = connector
        self.connector.set_table("lecturas")

    def crear(
        self,
        apar_id: int,
        fecha: str,
        servicio: str,
        mes: str,
        consumo_inicial: float,
        consumo_final: float,
    ) -> bool:
        """
        Crear una nueva lectura

        Args:
            apar_id: ID del apartamento
            fecha: Fecha de la lectura (YYYY-MM-DD)
            servicio: Tipo de servicio
            mes: Mes de la lectura
            consumo_inicial: Lectura inicial
            consumo_final: Lectura final
        """
        if not self._validar_datos(
            apar_id, fecha, servicio, mes, consumo_inicial, consumo_final
        ):
            return False

        # Verificar unicidad
        if self.obtener_por_clave(apar_id, fecha, servicio):
            print(
                f"❌ Ya existe lectura para apartamento {apar_id}, fecha {fecha}, servicio {servicio}"
            )
            return False

        fields = [
            "lec_apar_id",
            "lec_fecha",
            "lec_servicio",
            "lec_mes",
            "lec_consumoInicial",
            "lec_consumoFinal",
        ]
        values = (apar_id, fecha, servicio, mes.upper(), consumo_inicial, consumo_final)

        affected = self.connector.insert(fields, values)
        return affected > 0

    def obtener_por_id(self, lec_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener una lectura por su ID
        """
        where = f"lec_id = {lec_id}"
        results = self.connector.get_filtered(where)
        return results[0] if results else None

    def obtener_por_clave(
        self, apar_id: int, fecha: str, servicio: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtener una lectura por su clave única (apartamento, fecha, servicio)
        """
        where = f"lec_apar_id = {apar_id} AND lec_fecha = '{fecha}' AND lec_servicio = '{servicio}'"
        results = self.connector.get_filtered(where)
        return results[0] if results else None

    def obtener_todas(self) -> List[Dict[str, Any]]:
        """
        Obtener todas las lecturas
        """
        self.connector.set_table("lecturas")
        where = "1=1 ORDER BY lec_fecha DESC, lec_apar_id, lec_servicio"
        return self.connector.get_filtered(where)

    def obtener_por_apartamento(self, apar_id: int) -> List[Dict[str, Any]]:
        """
        Obtener lecturas de un apartamento específico
        """
        self.connector.set_table("lecturas")
        where = f"lec_apar_id = {apar_id} ORDER BY lec_fecha DESC, lec_servicio"
        return self.connector.get_filtered(where)

    def obtener_por_mes(self, mes: str) -> List[Dict[str, Any]]:
        """
        Obtener lecturas de un mes específico
        """
        where = f"lec_mes = '{mes.upper()}' ORDER BY lec_apar_id, lec_servicio"
        return self.connector.get_filtered(where)

    def obtener_por_servicio(self, servicio: str) -> List[Dict[str, Any]]:
        """
        Obtener lecturas de un servicio específico
        """
        where = f"lec_servicio = '{servicio}' ORDER BY lec_fecha DESC, lec_apar_id"
        return self.connector.get_filtered(where)

    def obtener_por_apartamento_mes_servicio(
        self, apar_id: int, mes: str, servicio: str
    ) -> List[Dict[str, Any]]:
        """
        Obtener lecturas específicas por apartamento, mes y servicio
        """
        where = f"lec_apar_id = {apar_id} AND lec_mes = '{mes.upper()}' AND lec_servicio = '{servicio}'"
        return self.connector.get_filtered(where)

    def actualizar(
        self, lec_id: int, consumo_inicial: float, consumo_final: float
    ) -> bool:
        """
        Actualizar consumos de una lectura
        """
        if not self._validar_consumos(consumo_inicial, consumo_final):
            return False

        lectura = self.obtener_por_id(lec_id)
        if not lectura:
            print(f"❌ No existe lectura con ID {lec_id}")
            return False

        fields = ["lec_consumoInicial", "lec_consumoFinal"]
        values = (consumo_inicial, consumo_final)

        affected = self.connector.update(fields, values, "lec_id", lec_id)
        return affected > 0

    def eliminar(self, lec_id: int) -> bool:
        """
        Eliminar una lectura (solo si no tiene pagos asociados)
        """
        lectura = self.obtener_por_id(lec_id)
        if not lectura:
            print(f"❌ No existe lectura con ID {lec_id}")
            return False

        # Verificar si tiene pagos asociados
        if self._tiene_pagos_asociados(lectura):
            print(f"❌ No se puede eliminar: la lectura {lec_id} tiene pagos asociados")
            return False

        where = f"lec_id = {lec_id}"
        sql = f"DELETE FROM lecturas WHERE {where}"
        affected = self.connector._execute(sql)
        return affected > 0

    def calcular_consumo(self, lec_id: int) -> float:
        """
        Calcular el consumo de una lectura (final - inicial)
        """
        lectura = self.obtener_por_id(lec_id)
        if not lectura:
            return 0.0

        return float(lectura["lec_consumoFinal"]) - float(lectura["lec_consumoInicial"])

    def obtener_consumo_total_mes_servicio(self, mes: str, servicio: str) -> float:
        """
        Obtener consumo total de un servicio en un mes específico
        """
        lecturas = self.obtener_por_mes(mes)
        lecturas_servicio = [l for l in lecturas if l["lec_servicio"] == servicio]

        total = 0.0
        for lectura in lecturas_servicio:
            consumo = float(lectura["lec_consumoFinal"]) - float(
                lectura["lec_consumoInicial"]
            )
            total += consumo

        return total

    def obtener_consumos_apartamento_mes(
        self, apar_id: int, mes: str
    ) -> Dict[str, float]:
        """
        Obtener todos los consumos de un apartamento en un mes
        """
        lecturas = self.obtener_por_apartamento_mes_servicio(apar_id, mes, "")
        # Filtrar sin servicio específico
        where = f"lec_apar_id = {apar_id} AND lec_mes = '{mes.upper()}'"
        lecturas = self.connector.get_filtered(where)

        consumos = {}
        for lectura in lecturas:
            servicio = lectura["lec_servicio"]
            consumo = float(lectura["lec_consumoFinal"]) - float(
                lectura["lec_consumoInicial"]
            )
            consumos[servicio] = consumo

        return consumos

    def calcular_factor_consumo_apartamento(
        self, apar_id: int, mes: str, servicio: str
    ) -> float:
        """
        Calcular factor de distribución basado en consumo proporcional
        """
        # Obtener consumo del apartamento específico
        lecturas_apartamento = self.obtener_por_apartamento_mes_servicio(
            apar_id, mes, servicio
        )
        if not lecturas_apartamento:
            return 0.0

        consumo_apartamento = 0.0
        for lectura in lecturas_apartamento:
            consumo_apartamento += float(lectura["lec_consumoFinal"]) - float(
                lectura["lec_consumoInicial"]
            )

        # Obtener consumo total del servicio en el mes
        consumo_total = self.obtener_consumo_total_mes_servicio(mes, servicio)

        if consumo_total == 0:
            return 0.0

        return consumo_apartamento / consumo_total

    def obtener_historial_consumos_apartamento(
        self, apar_id: int, limit: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Obtener historial de consumos de un apartamento
        """
        where = f"lec_apar_id = {apar_id} ORDER BY lec_fecha DESC LIMIT {limit}"
        lecturas = self.connector.get_filtered(where)

        historial = []
        for lectura in lecturas:
            consumo = float(lectura["lec_consumoFinal"]) - float(
                lectura["lec_consumoInicial"]
            )
            historial.append(
                {
                    "fecha": lectura["lec_fecha"],
                    "mes": lectura["lec_mes"],
                    "servicio": lectura["lec_servicio"],
                    "consumo_inicial": lectura["lec_consumoInicial"],
                    "consumo_final": lectura["lec_consumoFinal"],
                    "consumo_calculado": consumo,
                }
            )

        return historial

    def _validar_datos(
        self,
        apar_id: int,
        fecha: str,
        servicio: str,
        mes: str,
        consumo_inicial: float,
        consumo_final: float,
    ) -> bool:
        """
        Validar datos de la lectura
        """
        # Validar ID del apartamento
        if apar_id <= 0:
            print("❌ El ID del apartamento debe ser positivo")
            return False

        # Validar fecha
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            print("❌ Formato de fecha inválido. Use YYYY-MM-DD")
            return False

        # Validar servicio
        if servicio not in self.SERVICIOS_VALIDOS:
            print(
                f"❌ Servicio inválido. Debe ser uno de: {', '.join(self.SERVICIOS_VALIDOS)}"
            )
            return False

        # Validar mes
        if not mes or len(mes.strip()) == 0:
            print("❌ El mes es obligatorio")
            return False

        # Validar consumos
        if not self._validar_consumos(consumo_inicial, consumo_final):
            return False

        # Verificar que existe el apartamento
        if not self._existe_apartamento(apar_id):
            print(f"❌ No existe apartamento con ID {apar_id}")
            return False

        return True

    def _validar_consumos(self, consumo_inicial: float, consumo_final: float) -> bool:
        """
        Validar valores de consumo
        """
        if consumo_inicial < 0 or consumo_final < 0:
            print("❌ Los consumos no pueden ser negativos")
            return False

        if consumo_final < consumo_inicial:
            print("❌ El consumo final debe ser mayor o igual al inicial")
            return False

        return True

    def _existe_apartamento(self, apar_id: int) -> bool:
        """
        Verificar si existe un apartamento
        """
        tabla_original = self.connector.table
        self.connector.set_table("apartamentos")

        where = f"apar_id = {apar_id}"
        result = self.connector.get_filtered(where)

        self.connector.set_table(tabla_original)
        return len(result) > 0

    def _tiene_pagos_asociados(self, lectura: Dict[str, Any]) -> bool:
        """
        Verificar si una lectura tiene pagos asociados
        """
        tabla_original = self.connector.table
        self.connector.set_table("pagos")

        where = f"""
        pago_lec_apar_id = '{lectura['lec_apar_id']}'
        AND pago_lec_fecha = '{lectura['lec_fecha']}'
        AND pago_lec_servicio = '{lectura['lec_servicio']}'
        """
        pagos = self.connector.get_filtered(where)

        self.connector.set_table(tabla_original)
        return len(pagos) > 0

    def obtener_estadisticas_servicio(self, servicio: str) -> Dict[str, Any]:
        """
        Obtener estadísticas de un servicio específico
        """
        lecturas = self.obtener_por_servicio(servicio)

        if not lecturas:
            return {
                "servicio": servicio,
                "total_lecturas": 0,
                "consumo_promedio": 0,
                "consumo_total": 0,
                "apartamentos_con_lecturas": 0,
            }

        consumos = []
        apartamentos = set()

        for lectura in lecturas:
            consumo = float(lectura["lec_consumoFinal"]) - float(
                lectura["lec_consumoInicial"]
            )
            consumos.append(consumo)
            apartamentos.add(lectura["lec_apar_id"])

        return {
            "servicio": servicio,
            "total_lecturas": len(lecturas),
            "consumo_promedio": round(sum(consumos) / len(consumos), 3),
            "consumo_total": round(sum(consumos), 3),
            "consumo_minimo": round(min(consumos), 3),
            "consumo_maximo": round(max(consumos), 3),
            "apartamentos_con_lecturas": len(apartamentos),
        }
