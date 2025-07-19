from typing import Optional, List, Dict, Any
from connector.connector import Connector


class ServicioAcueducto:
    def __init__(self, connector: Connector):
        self.connector = connector
        self.connector.set_table('acueducto')
    
    def crear_detalle(self, reci_id: int, piso: int, consumo: float,
                     cargo_fijo_acueducto: float, tarifa_acueducto: float,
                     cargo_fijo_alcantarillado: float, tarifa_alcantarillado: float,
                     descuento: int) -> bool:
        """
        Crear detalle de factura de acueducto
        
        Args:
            reci_id: ID del recibo asociado
            piso: Piso del apartamento
            consumo: Consumo en m3
            cargo_fijo_acueducto: Cargo fijo por acueducto
            tarifa_acueducto: Tarifa por m3 de acueducto
            cargo_fijo_alcantarillado: Cargo fijo por alcantarillado
            tarifa_alcantarillado: Tarifa por m3 de alcantarillado
            descuento: Porcentaje de descuento
        """
        if not self._validar_datos(piso, consumo, cargo_fijo_acueducto, tarifa_acueducto,
                                  cargo_fijo_alcantarillado, tarifa_alcantarillado, descuento):
            return False
            
        if not self._existe_recibo(reci_id):
            print(f"❌ No existe recibo con ID {reci_id}")
            return False
            
        if self.obtener_por_recibo(reci_id):
            print(f"❌ Ya existe detalle de acueducto para el recibo {reci_id}")
            return False
            
        fields = ['acue_reci_id', 'acue_piso', 'acue_consumo', 'acue_cargoFijoAcueducto',
                 'acue_tarifaAcueducto', 'acue_cargoFijoAlcantarillado', 
                 'acue_tarifaAlacantarillado', 'acue_descuento']
        values = (reci_id, piso, consumo, cargo_fijo_acueducto, tarifa_acueducto,
                 cargo_fijo_alcantarillado, tarifa_alcantarillado, descuento)
        
        affected = self.connector.insert(fields, values)
        return affected > 0
    
    def obtener_por_recibo(self, reci_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener detalle de acueducto por ID de recibo
        """
        self.connector.set_table('acueducto')
        where = f"acue_reci_id = {reci_id}"
        results = self.connector.get_filtered(where)
        return results[0] if results else None
    
    def obtener_todos(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los detalles de acueducto
        """
        self.connector.set_table('acueducto')
        return self.connector.get_all()
    
    def actualizar(self, reci_id: int, piso: int, consumo: float,
                   cargo_fijo_acueducto: float, tarifa_acueducto: float,
                   cargo_fijo_alcantarillado: float, tarifa_alcantarillado: float,
                   descuento: int) -> bool:
        """
        Actualizar detalle de acueducto
        """
        if not self._validar_datos(piso, consumo, cargo_fijo_acueducto, tarifa_acueducto,
                                  cargo_fijo_alcantarillado, tarifa_alcantarillado, descuento):
            return False
            
        if not self.obtener_por_recibo(reci_id):
            print(f"❌ No existe detalle de acueducto para el recibo {reci_id}")
            return False
            
        fields = ['acue_piso', 'acue_consumo', 'acue_cargoFijoAcueducto',
                 'acue_tarifaAcueducto', 'acue_cargoFijoAlcantarillado',
                 'acue_tarifaAlacantarillado', 'acue_descuento']
        values = (piso, consumo, cargo_fijo_acueducto, tarifa_acueducto,
                 cargo_fijo_alcantarillado, tarifa_alcantarillado, descuento)
        
        affected = self.connector.update(fields, values, 'acue_reci_id', reci_id)
        return affected > 0
    
    def eliminar(self, reci_id: int) -> bool:
        """
        Eliminar detalle de acueducto
        """
        if not self.obtener_por_recibo(reci_id):
            print(f"❌ No existe detalle de acueducto para el recibo {reci_id}")
            return False
            
        where = f"acue_reci_id = {reci_id}"
        sql = f"DELETE FROM acueducto WHERE {where}"
        affected = self.connector._execute(sql)
        return affected > 0
    
    def calcular_valor_acueducto(self, reci_id: int) -> float:
        """
        Calcular valor total de acueducto
        """
        detalle = self.obtener_por_recibo(reci_id)
        if not detalle:
            return 0.0
            
        consumo = float(detalle['acue_consumo'])
        cargo_fijo = float(detalle['acue_cargoFijoAcueducto'])
        tarifa = float(detalle['acue_tarifaAcueducto'])
        
        valor_acueducto = cargo_fijo + (consumo * tarifa)
        return round(valor_acueducto, 2)
    
    def calcular_valor_alcantarillado(self, reci_id: int) -> float:
        """
        Calcular valor total de alcantarillado
        """
        detalle = self.obtener_por_recibo(reci_id)
        if not detalle:
            return 0.0
            
        consumo = float(detalle['acue_consumo'])
        cargo_fijo = float(detalle['acue_cargoFijoAlcantarillado'])
        tarifa = float(detalle['acue_tarifaAlacantarillado'])
        
        valor_alcantarillado = cargo_fijo + (consumo * tarifa)
        return round(valor_alcantarillado, 2)
    
    def calcular_valor_total(self, reci_id: int) -> Dict[str, float]:
        """
        Calcular valor total del servicio de acueducto y aseo
        """
        detalle = self.obtener_por_recibo(reci_id)
        if not detalle:
            return {
                'valor_acueducto': 0.0,
                'valor_alcantarillado': 0.0,
                'subtotal': 0.0,
                'descuento_porcentaje': 0,
                'descuento_valor': 0.0,
                'valor_total': 0.0
            }
            
        valor_acueducto = self.calcular_valor_acueducto(reci_id)
        valor_alcantarillado = self.calcular_valor_alcantarillado(reci_id)
        subtotal = valor_acueducto + valor_alcantarillado
        
        descuento_porcentaje = int(detalle['acue_descuento'])
        descuento_valor = subtotal * (descuento_porcentaje / 100.0)
        valor_total = subtotal - descuento_valor
        
        return {
            'valor_acueducto': round(valor_acueducto, 2),
            'valor_alcantarillado': round(valor_alcantarillado, 2),
            'subtotal': round(subtotal, 2),
            'descuento_porcentaje': descuento_porcentaje,
            'descuento_valor': round(descuento_valor, 2),
            'valor_total': round(valor_total, 2)
        }
    
    def calcular_distribucion_apartamentos(self, reci_id: int, factores_distribucion: Dict[int, float]) -> Dict[int, Dict[str, float]]:
        """
        Calcular distribución del costo entre apartamentos
        """
        calculo_total = self.calcular_valor_total(reci_id)
        valor_total = calculo_total['valor_total']
        
        distribucion = {}
        
        for apar_id, factor in factores_distribucion.items():
            valor_apartamento = valor_total * factor
            
            distribucion[apar_id] = {
                'factor_distribucion': factor,
                'valor_acueducto': round(calculo_total['valor_acueducto'] * factor, 2),
                'valor_alcantarillado': round(calculo_total['valor_alcantarillado'] * factor, 2),
                'descuento_aplicado': round(calculo_total['descuento_valor'] * factor, 2),
                'valor_total': round(valor_apartamento, 2)
            }
            
        return distribucion
    
    def obtener_historial_consumos(self, limit: int = 12) -> List[Dict[str, Any]]:
        """
        Obtener historial de consumos de acueducto
        """
        sql = """
        SELECT a.*, r.reci_fecha, r.reci_mes 
        FROM acueducto a
        INNER JOIN recibos r ON a.acue_reci_id = r.reci_id
        ORDER BY r.reci_fecha DESC
        LIMIT %s
        """
        return self.connector._fetch(sql.replace('%s', str(limit)))
    
    def obtener_promedio_consumo_mensual(self) -> float:
        """
        Obtener promedio de consumo mensual
        """
        sql = """
        SELECT AVG(acue_consumo) as promedio
        FROM acueducto
        """
        result = self.connector._fetch(sql)
        return float(result[0]['promedio']) if result and result[0]['promedio'] else 0.0
    
    def obtener_estadisticas_tarifas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de tarifas de acueducto
        """
        detalles = self.obtener_todos()
        
        if not detalles:
            return {
                'total_registros': 0,
                'tarifa_acueducto_promedio': 0.0,
                'tarifa_alcantarillado_promedio': 0.0,
                'cargo_fijo_acueducto_promedio': 0.0,
                'cargo_fijo_alcantarillado_promedio': 0.0,
                'descuento_promedio': 0.0
            }
        
        tarifas_acueducto = [float(d['acue_tarifaAcueducto']) for d in detalles]
        tarifas_alcantarillado = [float(d['acue_tarifaAlacantarillado']) for d in detalles]
        cargos_fijos_acueducto = [float(d['acue_cargoFijoAcueducto']) for d in detalles]
        cargos_fijos_alcantarillado = [float(d['acue_cargoFijoAlcantarillado']) for d in detalles]
        descuentos = [int(d['acue_descuento']) for d in detalles]
        
        return {
            'total_registros': len(detalles),
            'tarifa_acueducto_promedio': round(sum(tarifas_acueducto) / len(tarifas_acueducto), 4),
            'tarifa_alcantarillado_promedio': round(sum(tarifas_alcantarillado) / len(tarifas_alcantarillado), 4),
            'cargo_fijo_acueducto_promedio': round(sum(cargos_fijos_acueducto) / len(cargos_fijos_acueducto), 2),
            'cargo_fijo_alcantarillado_promedio': round(sum(cargos_fijos_alcantarillado) / len(cargos_fijos_alcantarillado), 2),
            'descuento_promedio': round(sum(descuentos) / len(descuentos), 2),
            'tarifa_acueducto_maxima': max(tarifas_acueducto),
            'tarifa_acueducto_minima': min(tarifas_acueducto),
            'consumo_promedio': self.obtener_promedio_consumo_mensual()
        }
    
    def _validar_datos(self, piso: int, consumo: float, cargo_fijo_acueducto: float,
                      tarifa_acueducto: float, cargo_fijo_alcantarillado: float,
                      tarifa_alcantarillado: float, descuento: int) -> bool:
        """
        Validar datos del servicio de acueducto
        """
        if piso < 1 or piso > 9:
            print("❌ El piso debe estar entre 1 y 9")
            return False
            
        if consumo < 0:
            print("❌ El consumo no puede ser negativo")
            return False
            
        if cargo_fijo_acueducto < 0 or tarifa_acueducto < 0:
            print("❌ Los valores de acueducto no pueden ser negativos")
            return False
            
        if cargo_fijo_alcantarillado < 0 or tarifa_alcantarillado < 0:
            print("❌ Los valores de alcantarillado no pueden ser negativos")
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
        self.connector.set_table('recibos')
        
        where = f"reci_id = {reci_id}"
        result = self.connector.get_filtered(where)
        
        self.connector.set_table(tabla_original)
        return len(result) > 0