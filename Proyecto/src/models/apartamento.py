"""
Tabla: 'apartamentos'.
Author: ahbordam
Versión: 1.0.0
Date: 2025-07-08
"""
from typing import Optional


class Apartamento:

    def __init__(self, id: int = 0, cantidad_personas: int = 0, observaciones: str = ""):

        self._id = id
        self._cantidad_personas = cantidad_personas
        self._observaciones = observaciones

    # Properties para ID
    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int):
        if value <= 0:
            raise ValueError("El número de apartamento debe ser positivo")
        self._id = value

    # Properties para cantidad de personas
    @property
    def cantidad_personas(self) -> int:
        return self._cantidad_personas

    @cantidad_personas.setter
    def cantidad_personas(self, value: int):
        if value < 0:
            raise ValueError("La cantidad de personas no puede ser negativa")
        if value > 10:
            raise ValueError("La cantidad de personas excede el límite")
        self._cantidad_personas = value

    # Properties para observaciones
    @property
    def observaciones(self) -> str:
        return self._observaciones

    @observaciones.setter
    def observaciones(self, value: str):
        self._observaciones = value if value else ""

    def to_dict(self) -> dict:
        """
        Objeto a diccionario.
        """
        return {
            'apar_id': self.id,
            'apar_cantidadPersonas': self.cantidad_personas,
            'apar_observaciones': self.observaciones
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Apartamento':
        """
        dict a objeto
        """
        return cls(
            id=data.get('apar_id', 0),
            cantidad_personas=data.get('apar_cantidadPersonas', 0),
            observaciones=data.get('apar_observaciones', '')
        )

    def es_valido(self) -> bool:
        
        try:
            return (self.id > 0 and 
                   self.cantidad_personas >= 0)
        except:
            return False

    def __str__(self) -> str:
        return f"Apartamento {self.id} - {self.cantidad_personas} personas"

    def __repr__(self) -> str:
        return f"Apartamento({self.id}, {self.cantidad_personas}, '{self.observaciones}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Apartamento):
            return False
        return self.id == other.id