"""
Tabla: 'inquilinos'.
Author: ahbordam
Versión: 1.0.0
Date: 2025-07-08
"""

from typing import Optional


class Inquilino:
    def __init__(self, id: int = 0, nombre: str = "", edad: int = 0):
        self._id = id
        self._nombre = nombre
        self._edad = edad

    #Properties para ID
    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int):
        if value < 0:
            raise ValueError("El ID no puede ser negativo ERROR")
        self._id = value

    # Properties para nombre
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, value: str):
        if not value or not value.strip():
            raise ValueError("El nombre no puede estar vacío")
        if len(value) > 50:
            raise ValueError("El nombre no puede exceder 50 caracteres")
        self._nombre = value.strip()

    # Properties para edad
    @property
    def edad(self) -> int:
        return self._edad

    @edad.setter
    def edad(self, value: int):
        if value < 0 or value > 100:
            raise ValueError("La edad debe estar entre 0 y 100 años")
        self._edad = value

    def to_dict(self) -> dict:
        """
        Objeto a diccionario para operabilidad
        """
        return {
            'inq_id': self.id,
            'inq_nombre': self.nombre,
            'inq_edad': self.edad
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Inquilino':
        return cls(
            id=data.get('inq_id', 0),
            nombre=data.get('inq_nombre', ''),
            edad=data.get('inq_edad', 0)
        )

    def es_valido(self) -> bool:
        """
        Valida si el inquilino tiene datos válidos.
        """
        try:
            return (self.id > 0 and 
                   len(self.nombre.strip()) > 0 and 
                   0 <= self.edad <= 100)
        except:
            return False

    def __str__(self) -> str:
        return f"Inquilino(ID: {self.id}, Nombre: {self.nombre}, Edad: {self.edad})"

    def __repr__(self) -> str:
        return f"Inquilino({self.id}, '{self.nombre}', {self.edad})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Inquilino):
            return False
        return self.id == other.id