"""
🧪 PRUEBAS UNITARIAS - GESTORES ARRENDOS
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


class TestGeneradorReportes:
    """Pruebas para GeneradorReportes 📊"""
    
    def test_generar_reporte_mes(self):
        """Reporte mensual"""
        mock_connector = Mock()
        mock_connector.get_filtered.return_value = [
            {"arre_valor": 500000},
            {"arre_valor": 600000}
        ]
        
        generador = GeneradorReportes(mock_connector)
        
        # Act
        reporte = generador.generar_reporte_mes("JULIO")
        
        # Assert
        assert reporte["mes"] == "JULIO"
        assert reporte["total_arrendos"] == 1100000
        assert "total_general" in reporte


class TestGestorApartamentos:
    """Pruebas para GestorApartamentos 🏢"""
    
    def test_obtener_apartamentos(self):
        """Prueba obtener lista de apartamentos"""

        mock_connector = Mock()
        mock_connector.get_all.return_value = [
            {"apar_id": 101, "apar_cantidadPersonas": 2},
            {"apar_id": 102, "apar_cantidadPersonas": 3}
        ]
        
        gestor = GestorApartamentos(mock_connector)
        
        # Act
        apartamentos = gestor.obtener_apartamentos()
        
        # Assert
        assert len(apartamentos) == 2
        assert apartamentos[0]["apar_id"] == 101
        assert apartamentos[1]["apar_cantidadPersonas"] == 3


class TestGestorPagos:
    """Pruebas para GestorPagos 💳"""
    
    def test_obtener_pagos_pendientes(self):
        """Prueba obtener pagos pendientes"""

        mock_connector = Mock()
        mock_connector.get_filtered.return_value = [
            {"pago_id": 1, "pago_estado": "PENDIENTE", "pago_valorTotal": 75000},
            {"pago_id": 2, "pago_estado": "PENDIENTE", "pago_valorTotal": 45000}
        ]
        
        gestor = GestorPagos(mock_connector)
        
        # Act
        pagos = gestor.obtener_pagos_pendientes()
        
        # Assert
        assert len(pagos) == 2
        assert all(p["pago_estado"] == "PENDIENTE" for p in pagos)
        assert pagos[0]["pago_valorTotal"] == 75000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])