from typing import Dict, Any, List
from connector.connector import Connector


class GeneradorReportes:
    
    def __init__(self, connector: Connector):
        """
        Constructor del generador
        """
        self.connector = connector
    
    def generar_reporte_mes(self, mes: str) -> Dict[str, Any]:
        """
        Generar reporte básico de un mes
        """
        # Obtener arrendos del mes
        self.connector.set_table('arrendos')
        arrendos = self.connector.get_filtered(f"arre_mes = '{mes.upper()}'")
        
        # Obtener pagos del mes
        self.connector.set_table('pagos')
        pagos = self.connector.get_filtered(f"pago_mes = '{mes.upper()}'")
        
        # Calcular totales
        total_arrendos = sum(a['arre_valor'] for a in arrendos)
        total_servicios = sum(p['pago_valorTotal'] for p in pagos)
        
        return {
            'mes': mes.upper(),
            'total_arrendos': total_arrendos,
            'total_servicios': total_servicios,
            'total_general': total_arrendos + total_servicios,
            'cantidad_arrendos': len(arrendos),
            'cantidad_pagos': len(pagos)
        }
    
    def generar_reporte_apartamento(self, apar_id: int, mes: str) -> Dict[str, Any]:
        """
        Generar reporte de un apartamento específico
        """
        # Obtener arriendo del mes
        self.connector.set_table('arrendos')
        arrendos = self.connector.get_filtered(
            f"arre_apar_id = {apar_id} AND arre_mes = '{mes.upper()}'"
        )
        
        # Obtener pagos del mes
        self.connector.set_table('pagos')
        pagos = self.connector.get_filtered(
            f"pago_lec_apar_id = {apar_id} AND pago_mes = '{mes.upper()}'"
        )
        
        # Calcular totales
        total_arriendo = arrendos[0]['arre_valor'] if arrendos else 0
        total_servicios = sum(p['pago_valorTotal'] for p in pagos)
        
        return {
            'apartamento_id': apar_id,
            'mes': mes.upper(),
            'arriendo': total_arriendo,
            'servicios': {p['pago_lec_servicio']: p['pago_valorTotal'] for p in pagos},
            'total_servicios': total_servicios,
            'total_general': total_arriendo + total_servicios
        }
    
    def generar_reporte_recaudacion(self, mes: str) -> Dict[str, Any]:
        """
        Generar reporte de recaudación del mes
        """
        # Obtener arrendos
        self.connector.set_table('arrendos')
        arrendos = self.connector.get_filtered(f"arre_mes = '{mes.upper()}'")
        
        # Obtener pagos
        self.connector.set_table('pagos')
        pagos = self.connector.get_filtered(f"pago_mes = '{mes.upper()}'")
        
        # Calcular arrendos
        total_arrendos = sum(a['arre_valor'] for a in arrendos)
        arrendos_pagados = sum(a['arre_valor'] for a in arrendos if a['arre_estado'] == 'CANCELADO')
        
        # Calcular servicios
        total_servicios = sum(p['pago_valorTotal'] for p in pagos)
        servicios_pagados = sum(p['pago_valorTotal'] for p in pagos if p['pago_estado'] == 'CANCELADO')
        
        return {
            'mes': mes.upper(),
            'arrendos': {
                'total': total_arrendos,
                'pagado': arrendos_pagados,
                'pendiente': total_arrendos - arrendos_pagados
            },
            'servicios': {
                'total': total_servicios,
                'pagado': servicios_pagados,
                'pendiente': total_servicios - servicios_pagados
            },
            'total_esperado': total_arrendos + total_servicios,
            'total_recaudado': arrendos_pagados + servicios_pagados,
            'total_pendiente': (total_arrendos - arrendos_pagados) + (total_servicios - servicios_pagados)
        }
    
    def exportar_reporte_texto(self, reporte: Dict[str, Any]) -> str:
        """
        Exportar reporte en formato texto
        """
        lineas = []
        lineas.append("=" * 40)
        lineas.append(f"REPORTE MES: {reporte.get('mes', 'N/A')}")
        lineas.append("=" * 40)
        
        # Si es reporte general del mes
        if 'total_arrendos' in reporte:
            lineas.append(f"Total Arrendos: ${reporte['total_arrendos']:,}")
            lineas.append(f"Total Servicios: ${reporte['total_servicios']:,}")
            lineas.append(f"Total General: ${reporte['total_general']:,}")
        
        # Si es reporte de apartamento
        if 'apartamento_id' in reporte:
            lineas.append(f"Apartamento: {reporte['apartamento_id']}")
            lineas.append(f"Arriendo: ${reporte['arriendo']:,}")
            lineas.append("Servicios:")
            for servicio, valor in reporte.get('servicios', {}).items():
                lineas.append(f"  {servicio}: ${valor:,}")
            lineas.append(f"Total: ${reporte['total_general']:,}")
        
        # Si es reporte de recaudación
        if 'total_esperado' in reporte:
            lineas.append("ARRENDOS:")
            lineas.append(f"  Total: ${reporte['arrendos']['total']:,}")
            lineas.append(f"  Pagado: ${reporte['arrendos']['pagado']:,}")
            lineas.append(f"  Pendiente: ${reporte['arrendos']['pendiente']:,}")
            lineas.append("SERVICIOS:")
            lineas.append(f"  Total: ${reporte['servicios']['total']:,}")
            lineas.append(f"  Pagado: ${reporte['servicios']['pagado']:,}")
            lineas.append(f"  Pendiente: ${reporte['servicios']['pendiente']:,}")
            lineas.append("-" * 40)
            lineas.append(f"TOTAL ESPERADO: ${reporte['total_esperado']:,}")
            lineas.append(f"TOTAL RECAUDADO: ${reporte['total_recaudado']:,}")
            lineas.append(f"TOTAL PENDIENTE: ${reporte['total_pendiente']:,}")
        
        return "\n".join(lineas)
    
    def obtener_resumen_general(self) -> Dict[str, Any]:
        """
        Obtener resumen general del sistema
        """
        # Total apartamentos
        self.connector.set_table('apartamentos')
        total_apartamentos = len(self.connector.get_all())
        
        # Total inquilinos
        self.connector.set_table('inquilinos')
        total_inquilinos = len(self.connector.get_all())
        
        # Arrendos activos
        self.connector.set_table('arrendos')
        arrendos = self.connector.get_all()
        arrendos_activos = len([a for a in arrendos if a['arre_estado'] in ['PENDIENTE', 'CANCELADO']])
        
        # Pagos pendientes
        self.connector.set_table('pagos')
        pagos = self.connector.get_all()
        pagos_pendientes = len([p for p in pagos if p['pago_estado'] == 'PENDIENTE'])
        
        return {
            'total_apartamentos': total_apartamentos,
            'total_inquilinos': total_inquilinos,
            'arrendos_activos': arrendos_activos,
            'pagos_pendientes': pagos_pendientes
        }
