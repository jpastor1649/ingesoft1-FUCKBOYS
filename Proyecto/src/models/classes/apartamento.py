from typing import Optional, List, Dict, Any
from connector.connector import Connector


class Apartamento:
    def __init__(self, connector: Connector):
        self.connector = connector
        self.connector.set_table('apartamentos')
    
    def crear(self, apar_id: int, cantidad_personas: int, observaciones: str = "") -> bool:
        """
        Crear un nuevo apartamento
        """
        if not self._validar_datos(apar_id, cantidad_personas):
            return False
            
        if self.obtener_por_id(apar_id):
            print(f"❌ Ya existe un apartamento con ID {apar_id}")
            return False
            
        fields = ['apar_id', 'apar_cantidadPersonas', 'apar_observaciones']
        values = (apar_id, cantidad_personas, observaciones.strip() if observaciones else None)
        
        affected = self.connector.insert(fields, values)
        return affected > 0
    
    def obtener_por_id(self, apar_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener un apartamento por su ID
        """
        where = f"apar_id = {apar_id}"
        results = self.connector.get_filtered(where)
        return results[0] if results else None
    
    def obtener_todos(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los apartamentos
        """
        return self.connector.get_all()
    
    def actualizar(self, apar_id: int, cantidad_personas: int, observaciones: str = "") -> bool:
        """
        Actualizar datos de un apartamento
        """
        if not self._validar_datos(apar_id, cantidad_personas):
            return False
            
        if not self.obtener_por_id(apar_id):
            print(f"❌ No existe apartamento con ID {apar_id}")
            return False
            
        fields = ['apar_cantidadPersonas', 'apar_observaciones']
        values = (cantidad_personas, observaciones.strip() if observaciones else None)
        
        affected = self.connector.update(fields, values, 'apar_id', apar_id)
        return affected > 0
    
    def eliminar(self, apar_id: int) -> bool:
        """
        Eliminar un apartamento (solo si no tiene arrendos o lecturas)
        """
        if not self.obtener_por_id(apar_id):
            print(f"❌ No existe apartamento con ID {apar_id}")
            return False
            
        # Verificar dependencias
        if self._tiene_dependencias(apar_id):
            print(f"❌ No se puede eliminar: el apartamento {apar_id} tiene registros asociados")
            return False
            
        where = f"apar_id = {apar_id}"
        sql = f"DELETE FROM apartamentos WHERE {where}"
        affected = self.connector._execute(sql)
        return affected > 0
    
    def obtener_apartamentos_disponibles(self) -> List[Dict[str, Any]]:
        """
        Obtener apartamentos sin arrendos activos
        """
        sql = """
        SELECT a.* FROM apartamentos a 
        WHERE a.apar_id NOT IN (
            SELECT DISTINCT arre_apar_id 
            FROM arrendos 
            WHERE arre_estado IN ('PENDIENTE', 'CANCELADO')
        )
        """
        return self.connector._fetch(sql)
    
    def obtener_apartamentos_ocupados(self) -> List[Dict[str, Any]]:
        """
        Obtener apartamentos con arrendos activos
        """
        sql = """
        SELECT a.*, ar.arre_inq_id, ar.arre_fechaInicio, ar.arre_estado
        FROM apartamentos a 
        INNER JOIN arrendos ar ON a.apar_id = ar.arre_apar_id
        WHERE ar.arre_estado IN ('PENDIENTE', 'CANCELADO')
        """
        return self.connector._fetch(sql)
    
    def obtener_consumos_apartamento(self, apar_id: int, mes: str = None) -> List[Dict[str, Any]]:
        """
        Obtener consumos de un apartamento por mes
        """
        tabla_original = self.connector.table
        self.connector.set_table('lecturas')
        
        where = f"lec_apar_id = {apar_id}"
        if mes:
            where += f" AND lec_mes = '{mes}'"
            
        lecturas = self.connector.get_filtered(where)
        self.connector.set_table(tabla_original)
        return lecturas
    
    def obtener_pagos_apartamento(self, apar_id: int, mes: str = None) -> List[Dict[str, Any]]:
        """
        Obtener pagos de un apartamento
        """
        tabla_original = self.connector.table
        self.connector.set_table('pagos')
        
        where = f"pago_lec_apar_id = {apar_id}"
        if mes:
            where += f" AND pago_mes = '{mes}'"
            
        pagos = self.connector.get_filtered(where)
        self.connector.set_table(tabla_original)
        return pagos
    
    def obtener_historial_arrendos(self, apar_id: int) -> List[Dict[str, Any]]:
        """
        Obtener historial de arrendos de un apartamento
        """
        tabla_original = self.connector.table
        self.connector.set_table('arrendos')
        
        where = f"arre_apar_id = {apar_id} ORDER BY arre_fechaInicio DESC"
        arrendos = self.connector.get_filtered(where)
        
        self.connector.set_table(tabla_original)
        return arrendos
    
    def calcular_factor_personas(self, apar_id: int) -> float:
        """
        Calcular factor de distribución basado en cantidad de personas
        """
        apartamento = self.obtener_por_id(apar_id)
        if not apartamento:
            return 0.0
            
        # Obtener total de personas en todos los apartamentos ocupados
        ocupados = self.obtener_apartamentos_ocupados()
        total_personas = sum(apt.get('apar_cantidadPersonas', 0) for apt in ocupados)
        
        if total_personas == 0:
            return 0.0
            
        personas_apartamento = apartamento['apar_cantidadPersonas']
        return personas_apartamento / total_personas
    
    def _validar_datos(self, apar_id: int, cantidad_personas: int) -> bool:
        """
        Validar datos del apartamento
        """
        if apar_id <= 0:
            print("❌ El ID debe ser un número positivo")
            return False
            
        if cantidad_personas <= 0 or cantidad_personas > 10:
            print("❌ La cantidad de personas debe estar entre 1 y 10")
            return False
            
        return True
    
    def _tiene_dependencias(self, apar_id: int) -> bool:
        """
        Verificar si un apartamento tiene registros dependientes
        """
        tablas_dependientes = [
            ('arrendos', 'arre_apar_id'),
            ('lecturas', 'lec_apar_id'),
            ('correspondencia', 'corre_apar_id')
        ]
        
        tabla_original = self.connector.table
        
        for tabla, campo in tablas_dependientes:
            self.connector.set_table(tabla)
            where = f"{campo} = {apar_id}"
            registros = self.connector.get_filtered(where)
            
            if registros:
                self.connector.set_table(tabla_original)
                return True
                
        self.connector.set_table(tabla_original)
        return False
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas generales de apartamentos
        """
        apartamentos = self.obtener_todos()
        disponibles = self.obtener_apartamentos_disponibles()
        ocupados = self.obtener_apartamentos_ocupados()
        
        total_personas = sum(apt.get('apar_cantidadPersonas', 0) for apt in apartamentos)
        
        return {
            'total_apartamentos': len(apartamentos),
            'apartamentos_disponibles': len(disponibles),
            'apartamentos_ocupados': len(ocupados),
            'total_personas': total_personas,
            'promedio_personas_por_apto': round(total_personas / len(apartamentos), 2) if apartamentos else 0,
            'tasa_ocupacion': round((len(ocupados) / len(apartamentos)) * 100, 2) if apartamentos else 0
        }