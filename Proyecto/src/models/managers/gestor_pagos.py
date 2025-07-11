from typing import List, Dict, Any
from connector.connector import Connector
from models.pago import Pago
from services.calculadora_recibos import CalculadoraRecibos


class GestorPagos:
    def __init__(self, connector: Connector):
        self.connector = connector
        self.pago = Pago(connector)
        self.calculadora = CalculadoraRecibos(connector)
    
    def generar_pagos_mes(self, mes: str) -> Dict[str, Any]:
        """
        Generar todos los pagos de servicios para un mes
        """
        distribucion = self.calculadora.calcular_distribucion_mes_completo(mes)
        
        if 'error' in distribucion:
            return distribucion
        
        pagos_creados = 0
        errores = []
        
        # Crear pagos para cada apartamento y servicio
        for apar_id, datos in distribucion['apartamentos'].items():
            servicios = datos.get('servicios', {})
            
            for servicio, valor in servicios.items():
                if valor > 0:
                    # Buscar lectura asociada
                    lectura = self._obtener_lectura_apartamento_mes(apar_id, mes, servicio)
                    if lectura:
                        # Crear pago
                        if self.pago.crear(
                            lec_apar_id=apar_id,
                            lec_fecha=lectura['lec_fecha'],
                            lec_servicio=servicio,
                            mes=mes,
                            tipo_lectura='LECTURA CONTADOR INTERNO',
                            consumo=int(lectura['lec_consumoFinal'] - lectura['lec_consumoInicial']),
                            valor_total=int(valor),
                            estado='PENDIENTE'
                        ):
                            pagos_creados += 1
                        else:
                            errores.append(f"Error creando pago {servicio} para apartamento {apar_id}")
                    else:
                        errores.append(f"No se encontró lectura de {servicio} para apartamento {apar_id}")
        
        return {
            'mes': mes,
            'pagos_creados': pagos_creados,
            'errores': errores,
            'exitoso': len(errores) == 0
        }
    
    def registrar_pago_servicio(self, apar_id: int, fecha_lectura: str, servicio: str) -> bool:
        """
        Registrar pago de un servicio específico
        """
        from datetime import datetime
        fecha_pago = datetime.now().strftime('%Y-%m-%d')
        
        return self.pago.registrar_pago(apar_id, fecha_lectura, servicio, fecha_pago)
    
    def obtener_resumen_pagos_mes(self, mes: str) -> Dict[str, Any]:
        """
        Obtener resumen de pagos de un mes
        """
        return self.pago.obtener_resumen_mes(mes)
    
    def obtener_pagos_pendientes(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los pagos pendientes
        """
        return self.pago.obtener_pendientes()
    
    def obtener_pagos_apartamento(self, apar_id: int) -> List[Dict[str, Any]]:
        """
        Obtener historial de pagos de un apartamento
        """
        return self.pago.obtener_por_apartamento(apar_id)
    
    def _obtener_lectura_apartamento_mes(self, apar_id: int, mes: str, servicio: str) -> Dict[str, Any]:
        """
        Obtener lectura de un apartamento para un mes y servicio específico
        """
        tabla_original = self.connector.table
        self.connector.set_table('lecturas')
        
        where = f"lec_apar_id = {apar_id} AND lec_mes = '{mes.upper()}' AND lec_servicio = '{servicio}'"
        lecturas = self.connector.get_filtered(where)
        
        self.connector.set_table(tabla_original)
        return lecturas[0] if lecturas else None