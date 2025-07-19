from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
sys.path.append('src')  # Ajusta el path según tu estructura de carpetas
from connector.connector import Connector


class Recibo:
    SERVICIOS_VALIDOS = ['ACUEDUCTO Y ASEO', 'ENERGIA', 'GAS NATURAL']
    
    def __init__(self, connector: Connector):
        self.connector = connector
        self.connector.set_table('recibos')
    
    def crear(self, fecha: str, servicio: str, mes: str, 
              consumo_inicial: float, consumo_final: float) -> Optional[int]:
        """
        Crear un nuevo recibo
        
        Args:
            fecha: Fecha del recibo (YYYY-MM-DD)
            servicio: Tipo de servicio
            mes: Mes del recibo
            consumo_inicial: Lectura inicial total
            consumo_final: Lectura final total
        """
        if not self._validar_datos(fecha, servicio, mes, consumo_inicial, consumo_final):
            return None
            
        fields = ['reci_fecha', 'reci_servicio', 'reci_mes', 
                 'reci_consumoInicial', 'reci_consumoFinal']
        values = (fecha, servicio, mes.upper(), consumo_inicial, consumo_final)
        
        affected = self.connector.insert(fields, values)
        if affected > 0:
            # Obtener el ID del recibo recién creado
            ultimo_recibo = self.obtener_ultimo_recibo()
            return ultimo_recibo['reci_id'] if ultimo_recibo else None
        return None
    
    def obtener_por_id(self, reci_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener un recibo por su ID
        """
        where = f"reci_id = {reci_id}"
        results = self.connector.get_filtered(where)
        return results[0] if results else None
    
    def obtener_todos(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los recibos
        """
        where = "1=1 ORDER BY reci_fecha DESC"
        return self.connector.get_filtered(where)
    
    def obtener_por_mes(self, mes: str) -> List[Dict[str, Any]]:
        """
        Obtener recibos de un mes específico
        """
        where = f"reci_mes = '{mes.upper()}' ORDER BY reci_servicio"
        return self.connector.get_filtered(where)
    
    # def obtener_por_apartamento(self, apar_id: int) -> List[Dict[str, Any]]:
    #     """
    #     Obtener recibos asociados a un apartamento específico usando correspondencia
    #     """
    #     # Guardar la tabla original
    #     tabla_original = self.connector.table
    #     # Buscar correspondencias para el apartamento
    #     self.connector.set_table('correspondencia')
    #     correspondencias = self.connector.get_filtered(f"corre_apar_id = {apar_id}")
    #     self.connector.set_table(tabla_original)

    #     reci_ids = [c['corre_reci_id'] for c in correspondencias]
    #     if not reci_ids:
    #         return []

    #     # Buscar los recibos asociados a esos IDs
    #     self.connector.set_table('recibos')
    #     where = f"reci_id IN ({','.join(str(rid) for rid in reci_ids)}) ORDER BY reci_fecha DESC, reci_servicio"
    #     return self.connector.get_filtered(where)

    def obtener_por_apartamento(self, apar_id: int) -> List[Dict[str, Any]]:
        """
        Obtener recibos asociados a un apartamento específico usando correspondencia
        """
        tabla_original = self.connector.table
        self.connector.set_table('correspondencia')
        correspondencias = self.connector.get_filtered(f"corre_apar_id = {apar_id}")
        self.connector.set_table(tabla_original)

        reci_ids = [c['corre_reci_id'] for c in correspondencias]
        print(f"[DEBUG] Recibos asociados al apartamento {apar_id}: {reci_ids}")  # <-- Debug

        if not reci_ids:
            return []

        self.connector.set_table('recibos')
        where = f"reci_id IN ({','.join(str(rid) for rid in reci_ids)}) ORDER BY reci_fecha DESC, reci_servicio"
        resultados = self.connector.get_filtered(where)
        print(f"[DEBUG] Resultados de recibos: {resultados}")  # <-- Debug
        return resultados

    def obtener_por_servicio(self, servicio: str) -> List[Dict[str, Any]]:
        """
        Obtener recibos de un servicio específico
        """
        where = f"reci_servicio = '{servicio}' ORDER BY reci_fecha DESC"
        return self.connector.get_filtered(where)
    
    def obtener_por_mes_y_servicio(self, mes: str, servicio: str) -> Optional[Dict[str, Any]]:
        """
        Obtener recibo específico por mes y servicio
        """
        where = f"reci_mes = '{mes.upper()}' AND reci_servicio = '{servicio}'"
        results = self.connector.get_filtered(where)
        return results[0] if results else None
    
    def obtener_ultimo_recibo(self) -> Optional[Dict[str, Any]]:
        """
        Obtener el último recibo creado
        """
        where = "1=1 ORDER BY reci_id DESC LIMIT 1"
        results = self.connector.get_filtered(where)
        return results[0] if results else None
    
    def actualizar(self, reci_id: int, fecha: str, servicio: str, mes: str,
                   consumo_inicial: float, consumo_final: float) -> bool:
        """
        Actualizar un recibo existente
        """
        if not self._validar_datos(fecha, servicio, mes, consumo_inicial, consumo_final):
            return False
            
        if not self.obtener_por_id(reci_id):
            print(f"❌ No existe recibo con ID {reci_id}")
            return False
            
        fields = ['reci_fecha', 'reci_servicio', 'reci_mes', 
                 'reci_consumoInicial', 'reci_consumoFinal']
        values = (fecha, servicio, mes.upper(), consumo_inicial, consumo_final)
        
        affected = self.connector.update(fields, values, 'reci_id', reci_id)
        return affected > 0
    
    def eliminar(self, reci_id: int) -> bool:
        """
        Eliminar un recibo (solo si no tiene correspondencia o detalles)
        """
        if not self.obtener_por_id(reci_id):
            print(f"❌ No existe recibo con ID {reci_id}")
            return False
            
        # Verificar dependencias
        if self._tiene_dependencias(reci_id):
            print(f"❌ No se puede eliminar: el recibo {reci_id} tiene registros asociados")
            return False
            
        where = f"reci_id = {reci_id}"
        sql = f"DELETE FROM recibos WHERE {where}"
        affected = self.connector._execute(sql)
        return affected > 0
    
    def calcular_consumo_total(self, reci_id: int) -> float:
        """
        Calcular el consumo total de un recibo
        """
        recibo = self.obtener_por_id(reci_id)
        if not recibo:
            return 0.0
            
        return float(recibo['reci_consumoFinal']) - float(recibo['reci_consumoInicial'])
    
    def obtener_apartamentos_asociados(self, reci_id: int) -> List[Dict[str, Any]]:
        """
        Obtener apartamentos asociados a un recibo através de correspondencia
        """
        sql = """
        SELECT a.*, c.corre_reci_id 
        FROM apartamentos a
        INNER JOIN correspondencia c ON a.apar_id = c.corre_apar_id
        WHERE c.corre_reci_id = %s
        """
        return self.connector._fetch(sql.replace('%s', str(reci_id)))
    
    def asociar_apartamento(self, reci_id: int, apar_id: int) -> bool:
        """
        Asociar un apartamento a un recibo através de correspondencia
        """
        if not self.obtener_por_id(reci_id):
            print(f"❌ No existe recibo con ID {reci_id}")
            return False
            
        if not self._existe_apartamento(apar_id):
            print(f"❌ No existe apartamento con ID {apar_id}")
            return False
            
        # Verificar si ya existe la asociación
        if self._existe_correspondencia(reci_id, apar_id):
            print(f"❌ Ya existe asociación entre recibo {reci_id} y apartamento {apar_id}")
            return False
            
        tabla_original = self.connector.table
        self.connector.set_table('correspondencia')
        
        fields = ['corre_reci_id', 'corre_apar_id']
        values = (reci_id, apar_id)
        
        affected = self.connector.insert(fields, values)
        self.connector.set_table(tabla_original)
        return affected > 0
    
    def desasociar_apartamento(self, reci_id: int, apar_id: int) -> bool:
        """
        Desasociar un apartamento de un recibo
        """
        if not self._existe_correspondencia(reci_id, apar_id):
            print(f"❌ No existe asociación entre recibo {reci_id} y apartamento {apar_id}")
            return False
            
        tabla_original = self.connector.table
        self.connector.set_table('correspondencia')
        
        where = f"corre_reci_id = {reci_id} AND corre_apar_id = {apar_id}"
        sql = f"DELETE FROM correspondencia WHERE {where}"
        affected = self.connector._execute(sql)
        
        self.connector.set_table(tabla_original)
        return affected > 0
    
    def obtener_detalles_servicio(self, reci_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener detalles específicos del servicio (acueducto, energía, gas)
        """
        recibo = self.obtener_por_id(reci_id)
        if not recibo:
            return None
            
        servicio = recibo['reci_servicio']
        tabla_original = self.connector.table
        
        if servicio == 'ACUEDUCTO Y ASEO':
            self.connector.set_table('acueducto')
            where = f"acue_reci_id = {reci_id}"
        elif servicio == 'ENERGIA':
            self.connector.set_table('energia')
            where = f"ener_reci_id = {reci_id}"
        elif servicio == 'GAS NATURAL':
            self.connector.set_table('gas')
            where = f"gas_reci_id = {reci_id}"
        else:
            self.connector.set_table(tabla_original)
            return None
            
        detalles = self.connector.get_filtered(where)
        self.connector.set_table(tabla_original)
        
        return detalles[0] if detalles else None
    
    def obtener_recibos_mes_completo(self, mes: str) -> Dict[str, Any]:
        """
        Obtener todos los recibos de un mes con sus detalles
        """
        recibos_mes = self.obtener_por_mes(mes)
        
        resultado = {
            'mes': mes,
            'recibos': {},
            'total_servicios': len(recibos_mes),
            'servicios_completos': []
        }
        
        for recibo in recibos_mes:
            servicio = recibo['reci_servicio']
            reci_id = recibo['reci_id']
            
            # Obtener detalles del servicio
            detalles = self.obtener_detalles_servicio(reci_id)
            
            # Obtener apartamentos asociados
            apartamentos = self.obtener_apartamentos_asociados(reci_id)
            
            resultado['recibos'][servicio] = {
                'recibo_base': recibo,
                'detalles_servicio': detalles,
                'apartamentos_asociados': apartamentos,
                'consumo_total': self.calcular_consumo_total(reci_id)
            }
            
            if detalles and apartamentos:
                resultado['servicios_completos'].append(servicio)
        
        return resultado
    
    def validar_recibo_completo(self, reci_id: int) -> Dict[str, bool]:
        """
        Validar si un recibo tiene toda la información necesaria
        """
        recibo = self.obtener_por_id(reci_id)
        if not recibo:
            return {'valido': False, 'errores': ['Recibo no existe']}
            
        errores = []
        
        # Verificar detalles del servicio
        detalles = self.obtener_detalles_servicio(reci_id)
        if not detalles:
            errores.append('Faltan detalles del servicio')
        
        # Verificar apartamentos asociados
        apartamentos = self.obtener_apartamentos_asociados(reci_id)
        if not apartamentos:
            errores.append('No hay apartamentos asociados')
        
        # Verificar consumo válido
        consumo = self.calcular_consumo_total(reci_id)
        if consumo <= 0:
            errores.append('Consumo inválido o cero')
        
        return {
            'valido': len(errores) == 0,
            'errores': errores,
            'tiene_detalles': detalles is not None,
            'tiene_apartamentos': len(apartamentos) > 0,
            'consumo_valido': consumo > 0
        }
    
    def _validar_datos(self, fecha: str, servicio: str, mes: str,
                      consumo_inicial: float, consumo_final: float) -> bool:
        """
        Validar datos del recibo
        """
        # Validar fecha
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            print("❌ Formato de fecha inválido. Use YYYY-MM-DD")
            return False
            
        # Validar servicio
        if servicio not in self.SERVICIOS_VALIDOS:
            print(f"❌ Servicio inválido. Debe ser uno de: {', '.join(self.SERVICIOS_VALIDOS)}")
            return False
            
        # Validar mes
        if not mes or len(mes.strip()) == 0:
            print("❌ El mes es obligatorio")
            return False
            
        # Validar consumos
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
        self.connector.set_table('apartamentos')
        
        where = f"apar_id = {apar_id}"
        result = self.connector.get_filtered(where)
        
        self.connector.set_table(tabla_original)
        return len(result) > 0
    
    def _existe_correspondencia(self, reci_id: int, apar_id: int) -> bool:
        """
        Verificar si existe correspondencia entre recibo y apartamento
        """
        tabla_original = self.connector.table
        self.connector.set_table('correspondencia')
        
        where = f"corre_reci_id = {reci_id} AND corre_apar_id = {apar_id}"
        result = self.connector.get_filtered(where)
        
        self.connector.set_table(tabla_original)
        return len(result) > 0
    
    def _tiene_dependencias(self, reci_id: int) -> bool:
        """
        Verificar si un recibo tiene registros dependientes
        """
        tablas_dependientes = [
            ('correspondencia', 'corre_reci_id'),
            ('acueducto', 'acue_reci_id'),
            ('energia', 'ener_reci_id'),
            ('gas', 'gas_reci_id')
        ]
        
        tabla_original = self.connector.table
        
        for tabla, campo in tablas_dependientes:
            self.connector.set_table(tabla)
            where = f"{campo} = {reci_id}"
            registros = self.connector.get_filtered(where)
            
            if registros:
                self.connector.set_table(tabla_original)
                return True
                
        self.connector.set_table(tabla_original)
        return False
    
    def obtener_estadisticas_mes(self, mes: str) -> Dict[str, Any]:
        """
        Obtener estadísticas de recibos de un mes
        """
        recibos = self.obtener_por_mes(mes)
        
        servicios_disponibles = set(r['reci_servicio'] for r in recibos)
        servicios_completos = []
        consumo_total = 0.0
        
        for recibo in recibos:
            reci_id = recibo['reci_id']
            validacion = self.validar_recibo_completo(reci_id)
            
            if validacion['valido']:
                servicios_completos.append(recibo['reci_servicio'])
                
            consumo_total += self.calcular_consumo_total(reci_id)
        
        return {
            'mes': mes,
            'total_recibos': len(recibos),
            'servicios_disponibles': list(servicios_disponibles),
            'servicios_completos': servicios_completos,
            'servicios_faltantes': list(set(self.SERVICIOS_VALIDOS) - servicios_disponibles),
            'consumo_total_mes': round(consumo_total, 3),
            'porcentaje_completitud': round((len(servicios_completos) / len(recibos)) * 100, 2) if recibos else 0
        }