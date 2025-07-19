from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta

from connector.connector import Connector


class Pago:
    """    Clase para manejar los pagos de servicios de los apartamentos
    """
    SERVICIOS_VALIDOS = ["ACUEDUCTO Y ASEO", "ENERGIA", "GAS NATURAL"]
    TIPOS_LECTURA_VALIDOS = ["FACTURA", "LECTURA CONTADOR INTERNO"]
    ESTADOS_VALIDOS = ["CANCELADO", "PENDIENTE", "CERRADO"]

    def __init__(self, connector: Connector):
        self.connector = connector
        self.connector.set_table("pagos")

    def crear(
        self,
        lec_apar_id: int,
        lec_fecha: str,
        lec_servicio: str,
        mes: str,
        tipo_lectura: str,
        consumo: int,
        valor_total: int,
        estado: str = "PENDIENTE",
        fecha_pago: str = None,
        observacion: str = "",
    ) -> bool:
        """
        Crear un nuevo pago

        Args:
            lec_apar_id: ID del apartamento de la lectura
            lec_fecha: Fecha de la lectura asociada
            lec_servicio: Servicio de la lectura asociada
            mes: Mes del pago
            tipo_lectura: Tipo de lectura (FACTURA o LECTURA CONTADOR INTERNO)
            consumo: Consumo registrado
            valor_total: Valor total a pagar
            estado: Estado del pago
            fecha_pago: Fecha del pago (opcional)
            observacion: Observaciones adicionales
        """
        if not self._validar_datos(
            lec_apar_id,
            lec_fecha,
            lec_servicio,
            mes,
            tipo_lectura,
            consumo,
            valor_total,
            estado,
        ):
            return False

        # Verificar que no exista ya el pago
        if self.obtener_por_clave(lec_apar_id, lec_fecha, lec_servicio):
            print(
                f"❌ Ya existe pago para apartamento {lec_apar_id}, fecha {lec_fecha}, servicio {lec_servicio}"
            )
            return False

        # Verificar que existe la lectura asociada
        if not self._existe_lectura(lec_apar_id, lec_fecha, lec_servicio):
            print(f"❌ No existe lectura asociada para este pago")
            return False

        fields = [
            "pago_lec_apar_id",
            "pago_lec_fecha",
            "pago_lec_servicio",
            "pago_mes",
            "pago_fechaPago",
            "pago_tipoLectura",
            "pago_consumo",
            "pago_valorTotal",
            "pago_estado",
            "pago_observacion",
        ]
        values = (
            lec_apar_id,
            lec_fecha,
            lec_servicio,
            mes.upper(),
            fecha_pago,
            tipo_lectura,
            consumo,
            valor_total,
            estado,
            observacion.strip() if observacion else None,
        )

        affected = self.connector.insert(fields, values)
        return affected > 0

    def obtener_por_clave(
        self, lec_apar_id: int, lec_fecha: str, lec_servicio: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtener un pago por su clave primaria compuesta
        """
        where = f"pago_lec_apar_id = {lec_apar_id} AND pago_lec_fecha = '{lec_fecha}' AND pago_lec_servicio = '{lec_servicio}'"
        results = self.connector.get_filtered(where)
        return results[0] if results else None

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los pagos
        """
        where = "1=1 ORDER BY pago_lec_fecha DESC, pago_lec_apar_id"
        return self.connector.get_filtered(where)

    def obtener_por_apartamento(self, apar_id: int) -> List[Dict[str, Any]]:
        """
        Obtener pagos de un apartamento específico
        """
        self.connector.set_table("pagos")
        where = f"pago_lec_apar_id = {apar_id} ORDER BY pago_lec_fecha DESC"
        return self.connector.get_filtered(where)

    def obtener_por_mes(self, mes: str) -> List[Dict[str, Any]]:
        """
        Obtener pagos de un mes específico
        """
        where = (
            f"pago_mes = '{mes.upper()}' ORDER BY pago_lec_apar_id, pago_lec_servicio"
        )
        return self.connector.get_filtered(where)

    def obtener_por_servicio(self, servicio: str) -> List[Dict[str, Any]]:
        """
        Obtener pagos de un servicio específico
        """
        where = f"pago_lec_servicio = '{servicio}' ORDER BY pago_lec_fecha DESC"
        return self.connector.get_filtered(where)

    def obtener_por_estado(self, estado: str) -> List[Dict[str, Any]]:
        """
        Obtener pagos por estado
        """
        where = f"pago_estado = '{estado}' ORDER BY pago_lec_fecha DESC"
        return self.connector.get_filtered(where)

    def obtener_pendientes(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los pagos pendientes
        """
        return self.obtener_por_estado("PENDIENTE")

    def obtener_pagados(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los pagos cancelados/pagados
        """
        return self.obtener_por_estado("CANCELADO")

    def obtener_apartamento_mes_servicio(
        self, apar_id: int, mes: str, servicio: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtener pago específico por apartamento, mes y servicio
        """
        where = f"pago_lec_apar_id = {apar_id} AND pago_mes = '{mes.upper()}' AND pago_lec_servicio = '{servicio}'"
        results = self.connector.get_filtered(where)
        return results[0] if results else None

    def actualizar_estado(
        self,
        lec_apar_id: int,
        lec_fecha: str,
        lec_servicio: str,
        nuevo_estado: str,
        fecha_pago: str = None,
    ) -> bool:
        """
        Actualizar estado de un pago
        """
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            print(f"❌ Estado inválido: {nuevo_estado}")
            return False

        pago = self.obtener_por_clave(lec_apar_id, lec_fecha, lec_servicio)
        if not pago:
            print("❌ Pago no encontrado")
            return False

        fields = ["pago_estado"]
        values = [nuevo_estado]

        if fecha_pago:
            fields.append("pago_fechaPago")
            values.append(fecha_pago)

        where_fields = ["pago_lec_apar_id", "pago_lec_fecha", "pago_lec_servicio"]
        where_values = [lec_apar_id, lec_fecha, lec_servicio]

        where_clause = " AND ".join([f"{field} = %s" for field in where_fields])
        sql = f"UPDATE pagos SET {', '.join([f'{field} = %s' for field in fields])} WHERE {where_clause}"

        affected = self.connector._execute(sql, tuple(values + where_values))
        return affected > 0

    def registrar_pago(
        self, lec_apar_id: int, lec_fecha: str, lec_servicio: str, fecha_pago: str
    ) -> bool:
        """
        Registrar pago de un servicio
        """
        return self.actualizar_estado(
            lec_apar_id, lec_fecha, lec_servicio, "CANCELADO", fecha_pago
        )

    def cerrar_pago(self, lec_apar_id: int, lec_fecha: str, lec_servicio: str) -> bool:
        """
        Cerrar un pago definitivamente
        """
        return self.actualizar_estado(lec_apar_id, lec_fecha, lec_servicio, "CERRADO")

    def actualizar_valor(
        self, lec_apar_id: int, lec_fecha: str, lec_servicio: str, nuevo_valor: int
    ) -> bool:
        """
        Actualizar valor de un pago
        """
        if nuevo_valor <= 0:
            print("❌ El valor debe ser positivo")
            return False

        pago = self.obtener_por_clave(lec_apar_id, lec_fecha, lec_servicio)
        if not pago:
            print("❌ Pago no encontrado")
            return False

        where_fields = ["pago_lec_apar_id", "pago_lec_fecha", "pago_lec_servicio"]
        where_values = [lec_apar_id, lec_fecha, lec_servicio]
        where_clause = " AND ".join([f"{field} = %s" for field in where_fields])

        sql = f"UPDATE pagos SET pago_valorTotal = %s WHERE {where_clause}"
        affected = self.connector._execute(sql, tuple([nuevo_valor] + where_values))
        return affected > 0

    def calcular_total_apartamento_mes(self, apar_id: int, mes: str) -> Dict[str, Any]:
        """
        Calcular total a pagar por apartamento en un mes
        """
        where = f"pago_lec_apar_id = {apar_id} AND pago_mes = '{mes.upper()}'"
        pagos = self.connector.get_filtered(where)

        total = 0
        desglose = {}
        pendientes = 0
        cancelados = 0

        for pago in pagos:
            servicio = pago["pago_lec_servicio"]
            valor = pago["pago_valorTotal"]
            estado = pago["pago_estado"]

            desglose[servicio] = {
                "valor": valor,
                "estado": estado,
                "consumo": pago["pago_consumo"],
                "tipo_lectura": pago["pago_tipoLectura"],
                "fecha_pago": pago["pago_fechaPago"],
            }

            total += valor

            if estado == "PENDIENTE":
                pendientes += 1
            elif estado == "CANCELADO":
                cancelados += 1

        return {
            "apartamento_id": apar_id,
            "mes": mes,
            "total_pagar": total,
            "desglose_servicios": desglose,
            "total_servicios": len(pagos),
            "servicios_pendientes": pendientes,
            "servicios_pagados": cancelados,
            "estado_general": (
                "PENDIENTE"
                if pendientes > 0
                else "CANCELADO" if cancelados > 0 else "SIN_PAGOS"
            ),
        }

    def obtener_resumen_mes(self, mes: str) -> Dict[str, Any]:
        """
        Obtener resumen de todos los pagos de un mes
        """
        pagos_mes = self.obtener_por_mes(mes)

        total_esperado = sum(p["pago_valorTotal"] for p in pagos_mes)
        pagos_pendientes = [p for p in pagos_mes if p["pago_estado"] == "PENDIENTE"]
        pagos_cancelados = [p for p in pagos_mes if p["pago_estado"] == "CANCELADO"]

        total_pendiente = sum(p["pago_valorTotal"] for p in pagos_pendientes)
        total_pagado = sum(p["pago_valorTotal"] for p in pagos_cancelados)

        # Agrupar por apartamento
        apartamentos = {}
        for pago in pagos_mes:
            apar_id = pago["pago_lec_apar_id"]
            if apar_id not in apartamentos:
                apartamentos[apar_id] = []
            apartamentos[apar_id].append(pago)

        return {
            "mes": mes,
            "total_pagos": len(pagos_mes),
            "total_esperado": total_esperado,
            "total_pendiente": total_pendiente,
            "total_pagado": total_pagado,
            "pagos_pendientes": len(pagos_pendientes),
            "pagos_cancelados": len(pagos_cancelados),
            "apartamentos_con_pagos": len(apartamentos),
            "porcentaje_recaudo": (
                round((total_pagado / total_esperado) * 100, 2)
                if total_esperado > 0
                else 0
            ),
            "servicios_por_apartamento": {
                apar_id: len(pagos) for apar_id, pagos in apartamentos.items()
            },
        }

    def obtener_morosos(self, dias_mora: int = 30) -> List[Dict[str, Any]]:
        """
        Obtener pagos en mora
        """

        fecha_limite = (datetime.now() - timedelta(days=dias_mora)).strftime("%Y-%m-%d")
        where = f"pago_estado = 'PENDIENTE' AND pago_lec_fecha < '{fecha_limite}'"
        return self.connector.get_filtered(where)

    def obtener_historial_pagos_apartamento(
        self, apar_id: int, limit: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Obtener historial de pagos de un apartamento
        """
        where = (
            f"pago_lec_apar_id = {apar_id} ORDER BY pago_lec_fecha DESC LIMIT {limit}"
        )
        return self.connector.get_filtered(where)

    def generar_recibo_apartamento_mes(self, apar_id: int, mes: str) -> Dict[str, Any]:
        """
        Generar recibo consolidado de un apartamento para un mes
        """
        # Obtener pagos del apartamento en el mes
        pagos_servicios = self.calcular_total_apartamento_mes(apar_id, mes)

        # Obtener información del arriendo
        arriendo_mes = self._obtener_arriendo_mes(apar_id, mes)

        # Calcular total general
        total_servicios = pagos_servicios["total_pagar"]
        total_arriendo = arriendo_mes["valor"] if arriendo_mes else 0
        total_general = total_servicios + total_arriendo

        return {
            "apartamento_id": apar_id,
            "mes": mes,
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d"),
            "arriendo": arriendo_mes,
            "servicios": pagos_servicios,
            "total_servicios": total_servicios,
            "total_arriendo": total_arriendo,
            "total_general": total_general,
            "estado_general": self._determinar_estado_recibo(
                pagos_servicios, arriendo_mes
            ),
        }

    def _validar_datos(
        self,
        lec_apar_id: int,
        lec_fecha: str,
        lec_servicio: str,
        mes: str,
        tipo_lectura: str,
        consumo: int,
        valor_total: int,
        estado: str,
    ) -> bool:
        """
        Validar datos del pago

        Args:
            lec_apar_id: ID del apartamento
            lec_fecha: Fecha de la lectura
            lec_servicio: Servicio de la lectura
            mes: Mes del pago
            tipo_lectura: Tipo de lectura
            consumo: Consumo registrado
            valor_total: Valor total
            estado: Estado del pago
        """
        # Validar ID del apartamento
        if lec_apar_id <= 0:
            print("❌ El ID del apartamento debe ser positivo")
            return False

        # Validar fecha
        try:
            datetime.strptime(lec_fecha, "%Y-%m-%d")
        except ValueError:
            print("❌ Formato de fecha inválido. Use YYYY-MM-DD")
            return False

        # Validar servicio
        if lec_servicio not in self.SERVICIOS_VALIDOS:
            print(
                f"❌ Servicio inválido. Debe ser uno de: {', '.join(self.SERVICIOS_VALIDOS)}"
            )
            return False

        # Validar mes
        if not mes or len(mes.strip()) == 0:
            print("❌ El mes es obligatorio")
            return False

        # Validar tipo de lectura
        if tipo_lectura not in self.TIPOS_LECTURA_VALIDOS:
            print(
                f"❌ Tipo de lectura inválido. Debe ser uno de: {', '.join(self.TIPOS_LECTURA_VALIDOS)}"
            )
            return False

        # Validar consumo
        if consumo < 0:
            print("❌ El consumo no puede ser negativo")
            return False

        # Validar valor
        if valor_total <= 0:
            print("❌ El valor total debe ser positivo")
            return False

        # Validar estado
        if estado not in self.ESTADOS_VALIDOS:
            print(
                f"❌ Estado inválido. Debe ser uno de: {', '.join(self.ESTADOS_VALIDOS)}"
            )
            return False

        return True

    def _existe_lectura(self, apar_id: int, fecha: str, servicio: str) -> bool:
        """
        Verificar si existe una lectura asociada
        """
        tabla_original = self.connector.table
        self.connector.set_table("lecturas")

        where = f"lec_apar_id = {apar_id} AND lec_fecha = '{fecha}' AND lec_servicio = '{servicio}'"
        result = self.connector.get_filtered(where)

        self.connector.set_table(tabla_original)
        return len(result) > 0

    def _obtener_arriendo_mes(self, apar_id: int, mes: str) -> Optional[Dict[str, Any]]:
        """
        Obtener arriendo de un apartamento en un mes específico
        """
        tabla_original = self.connector.table
        self.connector.set_table("arrendos")

        where = f"arre_apar_id = {apar_id} AND arre_mes = '{mes.upper()}'"
        arrendos = self.connector.get_filtered(where)

        self.connector.set_table(tabla_original)
        return arrendos[0] if arrendos else None

    def _determinar_estado_recibo(
        self, pagos_servicios: Dict[str, Any], arriendo: Optional[Dict[str, Any]]
    ) -> str:
        """
        Determinar estado general del recibo
        """
        servicios_pendientes = pagos_servicios["servicios_pendientes"]
        arriendo_pendiente = (
            arriendo and arriendo["arre_estado"] == "PENDIENTE" if arriendo else False
        )

        if servicios_pendientes > 0 or arriendo_pendiente:
            return "PENDIENTE"
        elif pagos_servicios["servicios_pagados"] > 0 or (
            arriendo and arriendo["arre_estado"] == "CANCELADO"
        ):
            return "CANCELADO"
        else:
            return "CERRADO"

    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """
        Obtener estadísticas generales de pagos
        """
        todos_pagos = self.obtener_todos()
        pendientes = self.obtener_pendientes()
        pagados = self.obtener_pagados()

        if not todos_pagos:
            return {
                "total_pagos": 0,
                "total_pendiente": 0,
                "total_pagado": 0,
                "valor_promedio": 0,
                "apartamentos_con_pagos": 0,
            }

        valores = [p["pago_valorTotal"] for p in todos_pagos]
        total_pendiente = sum(p["pago_valorTotal"] for p in pendientes)
        total_pagado = sum(p["pago_valorTotal"] for p in pagados)

        apartamentos = set(p["pago_lec_apar_id"] for p in todos_pagos)

        return {
            "total_pagos": len(todos_pagos),
            "pagos_pendientes": len(pendientes),
            "pagos_cancelados": len(pagados),
            "total_pendiente": total_pendiente,
            "total_pagado": total_pagado,
            "valor_promedio": round(sum(valores) / len(valores), 2),
            "valor_minimo": min(valores),
            "valor_maximo": max(valores),
            "apartamentos_con_pagos": len(apartamentos),
            "porcentaje_recaudo": (
                round((total_pagado / (total_pendiente + total_pagado)) * 100, 2)
                if (total_pendiente + total_pagado) > 0
                else 0
            ),
        }
