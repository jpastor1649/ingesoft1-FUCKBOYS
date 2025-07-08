"""
Enumeraciones utilizadas en el sistema de gestión de apartamentos.
Author: ahbordam
Versión: 1.0.0
Date: 2025-07-08
"""

from enum import Enum


class TipoServicio(Enum):
    """Tipos de servicios públicos"""
    ACUEDUCTO_Y_ASEO = "ACUEDUCTO Y ASEO"
    ENERGIA = "ENERGIA"
    GAS_NATURAL = "GAS NATURAL"

    def __str__(self):
        return self.value


class EstadoPago(Enum):
    """3 Estados"""
    CANCELADO = "CANCELADO"
    PENDIENTE = "PENDIENTE" 
    CERRADO = "CERRADO"

    def __str__(self):
        return self.value


class TipoLectura(Enum):
    """Lectura"""
    FACTURA = "FACTURA"
    LECTURA_CONTADOR_INTERNO = "LECTURA CONTADOR INTERNO"

    def __str__(self):
        return self.value