from typing import Optional, List, Dict, Any
from connector.connector import Connector


class Inquilino:
    def __init__(self, connector: Connector):
        self.connector = connector
        self.connector.set_table('inquilinos')
    
    def crear(self, inq_id: int, nombre: str, edad: int) -> bool:
        """       
        Args:
            inq_id: ID único del inquilino
            nombre: Nombre completo del inquilino
            edad: Edad del inquilino
        """
        if not self._validar_datos(inq_id, nombre, edad):
            return False
            
        if self.obtener_por_id(inq_id):
            print(f"❌ Ya existe un inquilino con ID {inq_id}")
            return False
            
        fields = ['inq_id', 'inq_nombre', 'inq_edad']
        values = (inq_id, nombre.strip().upper(), edad)
        
        affected = self.connector.insert(fields, values)
        return affected > 0
    
    def obtener_por_id(self, inq_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener un inquilino por su ID
        """
        where = f"inq_id = {inq_id}"
        results = self.connector.get_filtered(where)
        return results[0] if results else None
    
    def obtener_todos(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los inquilinos
        
        Returns:
            Lista de inquilinos
        """
        return self.connector.get_all()
    
    def obtener_por_inquilino(self, inq_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener un inquilino por su ID
        
        Args:
            inq_id (int): ID del inquilino a buscar
        """
        where = f"inq_id = {inq_id}"
        results = self.connector.get_filtered(where)
        return results[0] if results else None
    
    def actualizar(self, inq_id: int, nombre: str, edad: int) -> bool:
        """
        Actualizar datos de un inquilino
        """
        if not self._validar_datos(inq_id, nombre, edad):
            return False
            
        if not self.obtener_por_id(inq_id):
            print(f"❌ No existe inquilino con ID {inq_id}")
            return False
            
        fields = ['inq_nombre', 'inq_edad']
        values = (nombre.strip().upper(), edad)
        
        affected = self.connector.update(fields, values, 'inq_id', inq_id)
        return affected > 0
    
    def eliminar(self, inq_id: int) -> bool:
        """
        Eliminar un inquilino (solo si no tiene arrendos activos)
        """
        if not self.obtener_por_id(inq_id):
            print(f"❌ No existe inquilino con ID {inq_id}")
            return False
            
        # Verificar si tiene arrendos activos
        if self._tiene_arrendos_activos(inq_id):
            print(f"❌ No se puede eliminar: el inquilino {inq_id} tiene arrendos activos")
            return False
            
        # Eliminar inquilino
        where = f"inq_id = {inq_id}"
        sql = f"DELETE FROM inquilinos WHERE {where}"
        affected = self.connector._execute(sql)
        return affected > 0
    
    def buscar_por_nombre(self, nombre: str) -> List[Dict[str, Any]]:
        """
        Buscar inquilinos por nombre (búsqueda parcial)
        """
        where = f"inq_nombre LIKE '%{nombre.upper()}%'"
        return self.connector.get_filtered(where)
    
    def obtener_arrendos_inquilino(self, inq_id: int) -> List[Dict[str, Any]]:
        """
        Obtener todos los arrendos de un inquilino
        """
        # Cambiar temporalmente a tabla arrendos
        tabla_original = self.connector.table
        self.connector.set_table('arrendos')
        
        where = f"arre_inq_id = {inq_id}"
        arrendos = self.connector.get_filtered(where)
        
        # Restaurar tabla original
        self.connector.set_table(tabla_original)
        return arrendos
    
    def _validar_datos(self, inq_id: int, nombre: str, edad: int) -> bool:
        """
        Validar datos del inquilino
        """
        if inq_id <= 0:
            print("❌ El ID debe ser un número positivo")
            return False
            
        if not nombre or len(nombre.strip()) < 2:
            print("❌ El nombre debe tener al menos 2 caracteres")
            return False
            
        if len(nombre.strip()) > 50:
            print("❌ El nombre no puede exceder 50 caracteres")
            return False
            
        if edad < 18 or edad > 120:
            print("❌ La edad debe estar entre 18 y 120 años")
            return False
            
        return True
    
    def _tiene_arrendos_activos(self, inq_id: int) -> bool:
        """
        Verificar si un inquilino tiene arrendos activos
        """
        tabla_original = self.connector.table
        self.connector.set_table('arrendos')
        
        # Buscar arrendos no cerrados
        where = f"arre_inq_id = {inq_id} AND arre_estado != 'CERRADO'"
        arrendos = self.connector.get_filtered(where)
        
        self.connector.set_table(tabla_original)
        return len(arrendos) > 0
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas generales de inquilinos
        """
        inquilinos = self.obtener_todos()
        
        if not inquilinos:
            return {
                'total_inquilinos': 0,
                'edad_promedio': 0,
                'edad_minima': 0,
                'edad_maxima': 0
            }
        
        edades = [inq['inq_edad'] for inq in inquilinos]
        
        return {
            'total_inquilinos': len(inquilinos),
            'edad_promedio': round(sum(edades) / len(edades), 2),
            'edad_minima': min(edades),
            'edad_maxima': max(edades)
        }