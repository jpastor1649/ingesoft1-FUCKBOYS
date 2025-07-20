"""
🎶 PRUEBAS UNITARIAS
"""

import pytest
from unittest.mock import Mock
import sys
import os

#Path
sys.path.append("src/managers")
sys.path.append("src")

#Classes
from managers.generador_reportes import GeneradorReportes
from managers.gestor_apartamentos import GestorApartamentos  
from managers.gestor_pagos import GestorPagos

class TestManagers:
    """Pruebas para managers 🕵️"""

    def test_apartamentos_validos(self):
        """Prueba obtener lista de apartamentos"""

        mock_connector = Mock()
        mock_connector.get_all.return_value = [
            {"apar_id": 1},
            {"apar_id": 101},
            {"apar_id": 201},
            {"apar_id": 202},
            {"apar_id": 301},
            {"apar_id": 302},
            {"apar_id": 401}
        ]
        
        gestor = GestorApartamentos(mock_connector)
        
        # Act
        apartamentos = gestor.obtener_apartamentos()
        
        # Assert
        assert len(apartamentos) != 0
        assert apartamentos[0]["apar_id"] != 0
    

    
    def test_generar_reporte_mes_enero(self):
        """Reporte mensual enero"""
        mock_connector = Mock()
        mock_connector.get_filtered.return_value = [
            {"arre_valor": 500000},
            {"arre_valor": 600000}
        ]
        
        generador = GeneradorReportes(mock_connector)
        
        # Act
        reporte = generador.generar_reporte_mes("ENERO")
        
        # Assert
        assert reporte["mes"] == "ENERO"
        assert reporte["total_arrendos"] != 0
        assert "total_general" in reporte

    

    def test_obtener_pagos_cancelados(self):
        """Prueba obtener pagos cancelados"""

        mock_connector = Mock()
        mock_connector.get_filtered.return_value = [
            {"pago_id": 1, "pago_estado": "CANCELADO", "pago_valorTotal": 75000},
            {"pago_id": 2, "pago_estado": "CANCELADO", "pago_valorTotal": 45000}
        ]
        
        gestor = GestorPagos(mock_connector)
        
        # Act
        pagos = gestor.obtener_pagos_pendientes()
        
        # Assert
        assert len(pagos) == 2
        assert all(p["pago_estado"] == "CANCELADO" for p in pagos)
        assert pagos[0]["pago_valorTotal"] == 45000





if __name__ == "__main__":
    pytest.main([__file__, "-v"])