from typing import Dict, Any, List
from connector.connector import Connector
from services.calculadora_recibos import CalculadoraRecibos


class GeneradorReportes:
    def __init__(self, connector: Connector):
        self.connector = connector
        self.calculadora = CalculadoraRecibos(connector)
    
    def generar_reporte_mes(self, mes: str) -> Dict[str, Any]:
        """
        Generar reporte completo de un mes
        """
        # Obtener distribución del mes
        distribucion = self.calculadora.calcular_distribucion_mes_completo(mes)
        
        if 'error' in distribucion:
            return distribucion
        
        # Preparar reporte
        reporte = {
            'mes': mes,
            'fecha_generacion': self._obtener_fecha_actual(),
            'resumen_ejecutivo': self._generar_resumen_ejecutivo(distribucion),
            'apartamentos': [],
            'servicios': self._generar_resumen_servicios(mes),
            'totales': distribucion.get('totales', {})
        }
        
        # Detalles por apartamento
        for apar_id, datos in distribucion.get('apartamentos', {}).items():
            apartamento_reporte = {
                'apartamento_id': apar_id,
                'arriendo': datos.get('total_arriendo', 0),
                'servicios': datos.get('servicios', {}),
                'total_servicios': datos.get('total_servicios', 0),
                'total_general': datos.get('total_general', 0)
            }
            reporte['apartamentos'].append(apartamento_reporte)
        
        return reporte
    
    def generar_reporte_apartamento(self, apar_id: int, mes: str) -> Dict[str, Any]:
        """
        Generar reporte específico de un apartamento
        """
        recibo = self.calculadora.calcular_recibo_apartamento_mes(apar_id, mes)
        
        # Obtener información adicional del apartamento
        info_apartamento = self._obtener_info_apartamento(apar_id)
        
        return {
            'apartamento_id': apar_id,
            'mes': mes,
            'fecha_generacion': self._obtener_fecha_actual(),
            'info_apartamento': info_apartamento,
            'recibo': recibo,
            'desglose_servicios': self._generar_desglose_servicios(apar_id, mes)
        }
    
    def generar_reporte_recaudacion(self, mes: str) -> Dict[str, Any]:
        """
        Generar reporte de recaudación del mes
        """
        # Obtener pagos del mes
        pagos_mes = self._obtener_pagos_mes(mes)
        arrendos_mes = self._obtener_arrendos_mes(mes)
        
        # Calcular totales
        total_esperado_servicios = sum(p.get('pago_valorTotal', 0) for p in pagos_mes)
        total_pagado_servicios = sum(p.get('pago_valorTotal', 0) for p in pagos_mes if p.get('pago_estado') == 'CANCELADO')
        
        total_esperado_arrendos = sum(a.get('arre_valor', 0) for a in arrendos_mes)
        total_pagado_arrendos = sum(a.get('arre_valor', 0) for a in arrendos_mes if a.get('arre_estado') == 'CANCELADO')
        
        total_esperado = total_esperado_servicios + total_esperado_arrendos
        total_recaudado = total_pagado_servicios + total_pagado_arrendos
        
        return {
            'mes': mes,
            'fecha_generacion': self._obtener_fecha_actual(),
            'servicios': {
                'total_esperado': total_esperado_servicios,
                'total_recaudado': total_pagado_servicios,
                'pendiente': total_esperado_servicios - total_pagado_servicios,
                'porcentaje_recaudo': round((total_pagado_servicios / total_esperado_servicios) * 100, 2) if total_esperado_servicios > 0 else 0
            },
            'arrendos': {
                'total_esperado': total_esperado_arrendos,
                'total_recaudado': total_pagado_arrendos,
                'pendiente': total_esperado_arrendos - total_pagado_arrendos,
                'porcentaje_recaudo': round((total_pagado_arrendos / total_esperado_arrendos) * 100, 2) if total_esperado_arrendos > 0 else 0
            },
            'totales': {
                'total_esperado': total_esperado,
                'total_recaudado': total_recaudado,
                'pendiente': total_esperado - total_recaudado,
                'porcentaje_recaudo_general': round((total_recaudado / total_esperado) * 100, 2) if total_esperado > 0 else 0
            }
        }
    
    def exportar_reporte_simple(self, reporte: Dict[str, Any]) -> str:
        """
        Exportar reporte en formato texto simple
        """
        lineas = []
        lineas.append("=" * 50)
        lineas.append(f"REPORTE - {reporte.get('mes', 'N/A')}")
        lineas.append(f"Fecha: {reporte.get('fecha_generacion', 'N/A')}")
        lineas.append("=" * 50)
        
        # Totales
        if 'totales' in reporte:
            totales = reporte['totales']
            lineas.append("\nTOTALES GENERALES:")
            lineas.append(f"Total Arrendos: ${totales.get('total_arrendos', 0):,}")
            lineas.append(f"Total Servicios: ${totales.get('total_servicios', 0):,}")
            lineas.append(f"Total General: ${totales.get('total_general', 0):,}")
        
        # Apartamentos
        if 'apartamentos' in reporte:
            lineas.append("\nDETALLE POR APARTAMENTO:")
            for apt in reporte['apartamentos']:
                lineas.append(f"\nApartamento {apt['apartamento_id']}:")
                lineas.append(f"  Arriendo: ${apt.get('arriendo', 0):,}")
                lineas.append(f"  Servicios: ${apt.get('total_servicios', 0):,}")
                lineas.append(f"  Total: ${apt.get('total_general', 0):,}")
        
        return "\n".join(lineas)
    
    def _generar_resumen_ejecutivo(self, distribucion: Dict[str, Any]) -> Dict[str, Any]:
        """Generar resumen ejecutivo del mes"""
        totales = distribucion.get('totales', {})
        apartamentos = distribucion.get('apartamentos', {})
        
        return {
            'total_apartamentos': totales.get('total_apartamentos', 0),
            'total_ingresos': totales.get('total_general', 0),
            'promedio_por_apartamento': round(totales.get('total_general', 0) / max(totales.get('total_apartamentos', 1), 1), 2),
            'apartamento_mayor_valor': max(apartamentos.keys(), key=lambda x: apartamentos[x].get('total_general', 0)) if apartamentos else None
        }
    
    def _generar_resumen_servicios(self, mes: str) -> Dict[str, Any]:
        """Generar resumen de servicios del mes"""
        servicios = ['ACUEDUCTO Y ASEO', 'ENERGIA', 'GAS NATURAL']
        resumen = {}
        
        for servicio in servicios:
            recibo = self._obtener_recibo_servicio_mes(mes, servicio)
            if recibo:
                resumen[servicio] = {
                    'disponible': True,
                    'consumo_total': recibo.get('reci_consumoFinal', 0) - recibo.get('reci_consumoInicial', 0)
                }
            else:
                resumen[servicio] = {'disponible': False}
        
        return resumen
    
    def _generar_desglose_servicios(self, apar_id: int, mes: str) -> Dict[str, Any]:
        """Generar desglose detallado de servicios para un apartamento"""
        desglose = {}
        servicios = ['ACUEDUCTO Y ASEO', 'ENERGIA', 'GAS NATURAL']
        
        for servicio in servicios:
            valor = self.calculadora._calcular_servicio_apartamento(apar_id, mes, servicio)
            factor = self.calculadora.calcular_factor_consumo_apartamento(apar_id, mes, servicio)
            
            desglose[servicio] = {
                'valor': valor,
                'factor_distribucion': round(factor * 100, 2)  # En porcentaje
            }
        
        return desglose
    
    def _obtener_fecha_actual(self) -> str:
        """Obtener fecha actual formateada"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _obtener_info_apartamento(self, apar_id: int) -> Dict[str, Any]:
        """Obtener información básica del apartamento"""
        tabla_original = self.connector.table
        self.connector.set_table('apartamentos')
        
        where = f"apar_id = {apar_id}"
        result = self.connector.get_filtered(where)
        
        self.connector.set_table(tabla_original)
        return result[0] if result else {}
    
    def _obtener_recibo_servicio_mes(self, mes: str, servicio: str) -> Dict[str, Any]:
        """Obtener recibo de un servicio en un mes"""
        tabla_original = self.connector.table
        self.connector.set_table('recibos')
        
        where = f"reci_mes = '{mes.upper()}' AND reci_servicio = '{servicio}'"
        result = self.connector.get_filtered(where)
        
        self.connector.set_table(tabla_original)
        return result[0] if result else {}
    
    def _obtener_pagos_mes(self, mes: str) -> List[Dict[str, Any]]:
        """Obtener pagos de un mes"""
        tabla_original = self.connector.table
        self.connector.set_table('pagos')
        
        where = f"pago_mes = '{mes.upper()}'"
        result = self.connector.get_filtered(where)
        
        self.connector.set_table(tabla_original)
        return result
    
    def _obtener_arrendos_mes(self, mes: str) -> List[Dict[str, Any]]:
        """Obtener arrendos de un mes"""
        tabla_original = self.connector.table
        self.connector.set_table('arrendos')
        
        where = f"arre_mes = '{mes.upper()}'"
        result = self.connector.get_filtered(where)
        
        self.connector.set_table(tabla_original)
        return result