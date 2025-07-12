from typing import List, Dict, Any
from connector.connector import Connector


class GestorApartamentos:
    """
    Gestor simplificado para operaciones de apartamentos
    """
    
    def __init__(self, connector: Connector):
        """
        Constructor del gestor
        """
        self.connector = connector
    
    def obtener_apartamentos(self) -> List[Dict[str, Any]]:
        """
        Obtener lista de todos los apartamentos
        """
        self.connector.set_table('apartamentos')
        return self.connector.get_all()
    
    def obtener_apartamento_con_inquilino(self, apar_id: int) -> Dict[str, Any]:
        """
        Obtener información de un apartamento y su inquilino actual
        """
        # Obtener apartamento
        self.connector.set_table('apartamentos')
        apartamentos = self.connector.get_filtered(f"apar_id = {apar_id}")
        
        if not apartamentos:
            return {}
        
        apartamento = apartamentos[0]
        
        # Buscar arriendo activo
        self.connector.set_table('arrendos')
        arrendos = self.connector.get_filtered(
            f"arre_apar_id = {apar_id} AND arre_estado IN ('PENDIENTE', 'CANCELADO')"
        )
        
        inquilino = None
        if arrendos:
            # Obtener inquilino del arriendo activo
            self.connector.set_table('inquilinos')
            inquilinos = self.connector.get_filtered(f"inq_id = {arrendos[0]['arre_inq_id']}")
            if inquilinos:
                inquilino = inquilinos[0]
        
        return {
            'apartamento': apartamento,
            'inquilino': inquilino,
            'arriendo': arrendos[0] if arrendos else None
        }
    
    def listar_apartamentos_estado(self) -> List[Dict[str, Any]]:
        """
        Listar apartamentos con su estado de ocupación
        """
        # Obtener todos los apartamentos
        self.connector.set_table('apartamentos')
        apartamentos = self.connector.get_all()
        
        resultado = []
        
        for apt in apartamentos:
            # Verificar si tiene arriendo activo
            self.connector.set_table('arrendos')
            arrendos = self.connector.get_filtered(
                f"arre_apar_id = {apt['apar_id']} AND arre_estado IN ('PENDIENTE', 'CANCELADO')"
            )
            
            estado = 'OCUPADO' if arrendos else 'DISPONIBLE'
            
            resultado.append({
                'apar_id': apt['apar_id'],
                'cantidad_personas': apt['apar_cantidadPersonas'],
                'estado': estado
            })
        
        return resultado
    
    def obtener_arrendos_inquilino(self, inq_id: int) -> List[Dict[str, Any]]:
        """
        Obtener todos los arrendos de un inquilino
        """
        self.connector.set_table('arrendos')
        return self.connector.get_filtered(f"arre_inq_id = {inq_id}")
    
    def obtener_resumen_ocupacion(self) -> Dict[str, int]:
        """
        Obtener resumen de ocupación
        """
        # Total apartamentos
        self.connector.set_table('apartamentos')
        total_apartamentos = len(self.connector.get_all())
        
        # Apartamentos ocupados
        self.connector.set_table('arrendos')
        sql = """
        SELECT COUNT(DISTINCT arre_apar_id) as ocupados 
        FROM arrendos 
        WHERE arre_estado IN ('PENDIENTE', 'CANCELADO')
        """
        result = self.connector._fetch(sql)
        ocupados = result[0]['ocupados'] if result else 0
        
        return {
            'total': total_apartamentos,
            'ocupados': ocupados,
            'disponibles': total_apartamentos - ocupados
        }
