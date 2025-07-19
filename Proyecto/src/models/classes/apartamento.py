from typing import Optional, List, Dict, Any
from connector.connector import Connector


class Apartamento:
    """
    Clase para gestionar operaciones CRUD de apartamentos
    """
    
    def __init__(self, connector: Connector):
        """
        Constructor de la clase Apartamento
        """
        self.connector = connector
        self.connector.set_table('apartamentos')
    
    def crear(self, apar_id: int, cantidad_personas: int, observaciones: str = "") -> bool:
        """
        Crear un nuevo apartamento
        
        Args:
            apar_id (int): ID del apartamento
            cantidad_personas (int): Cantidad de personas en el apartamento
            observaciones (str): Observaciones adicionales (opcional)
        """
        # Preparar campos y valores
        fields = ['apar_id', 'apar_cantidadPersonas']
        values = [apar_id, cantidad_personas]
        
        # Agregar observaciones si existen
        if observaciones.strip():
            fields.append('apar_observaciones')
            values.append(observaciones.strip())
        
        # Insertar en la base de datos
        affected = self.connector.insert(fields, tuple(values))
        return affected > 0
    
    def obtener_por_id(self, apar_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener un apartamento por su ID
        
        Args:
            apar_id (int): ID del apartamento a buscar
        """
        where = f"apar_id = {apar_id}"
        results = self.connector.get_filtered(where)
        return results[0] if results else None
    
    def obtener_todos(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los apartamentos
        """
        return self.connector.get_all()
    
    def obtener_por_inquilino(self, inq_id: int) -> List[Dict[str, Any]]:
        """
        Obtener apartamentos por ID de inquilino
        
        Args:
            inq_id (int): ID del inquilino
        """
        where = f"apar_id IN (SELECT arre_apar_id FROM arrendos WHERE arre_inq_id = {inq_id})"
        return self.connector.get_filtered(where)
    
    def actualizar(self, apar_id: int, cantidad_personas: int, observaciones: str = "") -> bool:
        """
        Actualizar datos de un apartamento existente
        
        Args:
            apar_id (int): ID del apartamento a actualizar
            cantidad_personas (int): Nueva cantidad de personas
            observaciones (str): Nuevas observaciones (opcional)
        """
        # Preparar campos y valores
        fields = ['apar_cantidadPersonas', 'apar_observaciones']
        values = (cantidad_personas, observaciones.strip() if observaciones else None)
        
        # Actualizar
        affected = self.connector.update(fields, values, 'apar_id', apar_id)
        return affected > 0
    
    def eliminar(self, apar_id: int) -> bool:
        """
        Eliminar un apartamento
        
        Args:
            apar_id (int): ID del apartamento a eliminar
        """
        sql = f"DELETE FROM apartamentos WHERE apar_id = {apar_id}"
        affected = self.connector._execute(sql)
        return affected > 0