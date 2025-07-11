from typing import List, Dict, Any, Optional
from connector.connector import Connector
from models.apartamento import Apartamento
from models.inquilino import Inquilino
from models.arriendo import Arriendo


class GestorApartamentos:
    def __init__(self, connector: Connector):
        self.connector = connector
        self.apartamento = Apartamento(connector)
        self.inquilino = Inquilino(connector)
        self.arriendo = Arriendo(connector)
    
    def crear_apartamento_completo(self, apar_id: int, cantidad_personas: int, 
                                   inq_id: int, nombre_inquilino: str, edad_inquilino: int,
                                   valor_arriendo: int, mes: str) -> bool:
        """
        Crear apartamento con inquilino y arriendo en una sola operación
        
        Args:
            apar_id: ID del apartamento
            cantidad_personas: Cantidad de personas
            inq_id: ID del inquilino
            nombre_inquilino: Nombre del inquilino
            edad_inquilino: Edad del inquilino
            valor_arriendo: Valor del arriendo
            mes: Mes del arriendo
        """
        try:
            # Crear inquilino
            if not self.inquilino.crear(inq_id, nombre_inquilino, edad_inquilino):
                return False
            
            # Crear apartamento
            if not self.apartamento.crear(apar_id, cantidad_personas):
                return False
            
            # Crear arriendo
            from datetime import datetime, timedelta
            fecha_inicio = datetime.now().strftime('%Y-%m-%d')
            fecha_fin = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            if not self.arriendo.crear(inq_id, apar_id, fecha_inicio, fecha_fin, 
                                     mes, valor_arriendo):
                return False
            
            print(f"✅ Apartamento {apar_id} creado completamente")
            return True
            
        except Exception as e:
            print(f"❌ Error creando apartamento completo: {e}")
            return False
    
    def obtener_resumen_apartamento(self, apar_id: int) -> Dict[str, Any]:
        """
        Obtener resumen completo de un apartamento
        """
        apartamento = self.apartamento.obtener_por_id(apar_id)
        if not apartamento:
            return {'error': f'Apartamento {apar_id} no encontrado'}
        
        # Obtener arrendos
        arrendos = self.arriendo.obtener_por_apartamento(apar_id)
        
        # Obtener inquilino actual (si existe)
        inquilino_actual = None
        if arrendos:
            arriendo_activo = next((a for a in arrendos if a['arre_estado'] in ['PENDIENTE', 'CANCELADO']), None)
            if arriendo_activo:
                inquilino_actual = self.inquilino.obtener_por_id(arriendo_activo['arre_inq_id'])
        
        return {
            'apartamento': apartamento,
            'inquilino_actual': inquilino_actual,
            'total_arrendos': len(arrendos),
            'arrendos_activos': len([a for a in arrendos if a['arre_estado'] in ['PENDIENTE', 'CANCELADO']]),
            'estado': 'OCUPADO' if inquilino_actual else 'DISPONIBLE'
        }
    
    def listar_apartamentos_con_estado(self) -> List[Dict[str, Any]]:
        """
        Listar todos los apartamentos con su estado actual
        """
        apartamentos = self.apartamento.obtener_todos()
        resultado = []
        
        for apt in apartamentos:
            resumen = self.obtener_resumen_apartamento(apt['apar_id'])
            if 'error' not in resumen:
                resultado.append({
                    'apar_id': apt['apar_id'],
                    'cantidad_personas': apt['apar_cantidadPersonas'],
                    'estado': resumen['estado'],
                    'inquilino_actual': resumen['inquilino_actual']['inq_nombre'] if resumen['inquilino_actual'] else None
                })
        
        return resultado
    
    def cambiar_inquilino(self, apar_id: int, nuevo_inq_id: int, nuevo_valor: int, mes: str) -> bool:
        """
        Cambiar inquilino de un apartamento
        """
        try:
            # Cerrar arrendos activos
            arrendos_activos = [a for a in self.arriendo.obtener_por_apartamento(apar_id) 
                              if a['arre_estado'] in ['PENDIENTE', 'CANCELADO']]
            
            for arriendo in arrendos_activos:
                self.arriendo.cerrar_arriendo(
                    arriendo['arre_fechaInicio'], 
                    arriendo['arre_apar_id'], 
                    arriendo['arre_inq_id']
                )
            
            # Crear nuevo arriendo
            from datetime import datetime, timedelta
            fecha_inicio = datetime.now().strftime('%Y-%m-%d')
            fecha_fin = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            return self.arriendo.crear(nuevo_inq_id, apar_id, fecha_inicio, fecha_fin, 
                                     mes, nuevo_valor)
                                     
        except Exception as e:
            print(f"❌ Error cambiando inquilino: {e}")
            return False