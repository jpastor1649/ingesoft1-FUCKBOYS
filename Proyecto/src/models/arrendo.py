"""
Tabla: 'arrendos'.
Author: ahbordam
Versión: 1.0.0
Date: 2025-07-08
"""

from datetime import date
from typing import Optional
from .enums import EstadoPago


class Arrendo:
    """
    Clase que representa un contrato de arrendamiento.
    
    Attributes:
        inquilino_id (int): ID del inquilino que arrienda
        apartamento_id (int): ID del apartamento arrendado
        fecha_inicio (date): Fecha de inicio del contrato
        fecha_fin (date): Fecha de fin del contrato
        mes (str): Mes al que corresponde el pago
        valor (int): Valor mensual del arriendo
        fecha_pago (date): Fecha en que se realizó el pago
        estado (EstadoPago): Estado del pago del arriendo
        observaciones (str): Observaciones adicionales
    """

    def __init__(self, inquilino_id: int = 0, apartamento_id: int = 0, 
                 fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None,
                 mes: str = "", valor: int = 0, fecha_pago: Optional[date] = None,
                 estado: EstadoPago = EstadoPago.PENDIENTE, observaciones: str = ""):

        self._inquilino_id = inquilino_id
        self._apartamento_id = apartamento_id
        self._fecha_inicio = fecha_inicio
        self._fecha_fin = fecha_fin
        self._mes = mes
        self._valor = valor
        self._fecha_pago = fecha_pago
        self._estado = estado
        self._observaciones = observaciones

    # Properties para inquilino_id
    @property
    def inquilino_id(self) -> int:
        return self._inquilino_id

    @inquilino_id.setter
    def inquilino_id(self, value: int):
        if value <= 0:
            raise ValueError("El ID del inquilino debe ser positivo")
        self._inquilino_id = value

    # Properties para apartamento_id
    @property
    def apartamento_id(self) -> int:
        return self._apartamento_id

    @apartamento_id.setter
    def apartamento_id(self, value: int):
        if value <= 0:
            raise ValueError("El ID del apartamento debe ser positivo")
        self._apartamento_id = value

    # Properties para fecha_inicio
    @property
    def fecha_inicio(self) -> Optional[date]:
        return self._fecha_inicio

    @fecha_inicio.setter
    def fecha_inicio(self, value: Optional[date]):
        self._fecha_inicio = value

    # Properties para fecha_fin
    @property
    def fecha_fin(self) -> Optional[date]:
        return self._fecha_fin

    @fecha_fin.setter
    def fecha_fin(self, value: Optional[date]):
        if value and self._fecha_inicio and value < self._fecha_inicio:
            raise ValueError("La fecha fin debe ser posterior o igual a la fecha inicio")
        self._fecha_fin = value

    # Properties para mes
    @property
    def mes(self) -> str:
        return self._mes

    @mes.setter
    def mes(self, value: str):
        if not value or not value.strip():
            raise ValueError("El mes no puede estar vacío")
        if len(value) > 50:
            raise ValueError("El mes no puede exceder 50 caracteres")
        self._mes = value.strip()

    # Properties para valor
    @property
    def valor(self) -> int:
        return self._valor

    @valor.setter
    def valor(self, value: int):
        if value < 0:
            raise ValueError("El valor del arriendo no puede ser negativo")
        self._valor = value

    @property
    def fecha_pago(self) -> Optional[date]:
        return self._fecha_pago

    @fecha_pago.setter
    def fecha_pago(self, value: Optional[date]):
        self._fecha_pago = value
        #Actualizar estado automáticamente según la lógica del trigger
        self._actualizar_estado()

    @property
    def estado(self) -> EstadoPago:
        return self._estado

    @estado.setter
    def estado(self, value: EstadoPago):
        self._estado = value

    @property
    def observaciones(self) -> str:
        return self._observaciones

    @observaciones.setter
    def observaciones(self, value: str):
        self._observaciones = value if value else ""

    def _actualizar_estado(self):
        """
        Actualiza el estado según la fecha de pago (lógica del trigger).
        """
        if self._fecha_pago is not None:
            self._estado = EstadoPago.CANCELADO
        else:
            self._estado = EstadoPago.PENDIENTE

    def esta_pagado(self) -> bool:
      
        return self.estado == EstadoPago.CANCELADO and self.fecha_pago is not None

    def esta_vencido(self) -> bool:
        
        if self.esta_pagado():
            return False
        
        #Lógica para determinar vencimiento con respecto a fecha_fin
        if self.fecha_fin:
            return date.today() > self.fecha_fin
        return False

    def to_dict(self) -> dict:
        """
        Obj to dicc
        """
        return {
            'arre_inq_id': self.inquilino_id,
            'arre_apar_id': self.apartamento_id,
            'arre_fechaInicio': self.fecha_inicio,
            'arre_fechaFin': self.fecha_fin,
            'arre_mes': self.mes,
            'arre_valor': self.valor,
            'arre_fechaPago': self.fecha_pago,
            'arre_estado': self.estado.value,
            'arre_observaciones': self.observaciones
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Arrendo':
        """
        dicc to obj
        """
        estado = EstadoPago.PENDIENTE
        if data.get('arre_estado'):
            estado = EstadoPago(data['arre_estado'])

        return cls(
            inquilino_id=data.get('arre_inq_id', 0),
            apartamento_id=data.get('arre_apar_id', 0),
            fecha_inicio=data.get('arre_fechaInicio'),
            fecha_fin=data.get('arre_fechaFin'),
            mes=data.get('arre_mes', ''),
            valor=data.get('arre_valor', 0),
            fecha_pago=data.get('arre_fechaPago'),
            estado=estado,
            observaciones=data.get('arre_observaciones', '')
        )

    def es_valido(self) -> bool:
        """
        Validación de datos
        """
        try:
            return (self.inquilino_id > 0 and 
                   self.apartamento_id > 0 and
                   len(self.mes.strip()) > 0 and
                   self.valor >= 0 and
                   self.fecha_inicio is not None and
                   self.fecha_fin is not None and
                   self.fecha_fin >= self.fecha_inicio)
        except:
            return False

    def __str__(self) -> str:
        return f"Arrendo Apt-{self.apartamento_id} {self.mes} - ${self.valor:,} ({self.estado.value})"

    def __repr__(self) -> str:
        return f"Arrendo({self.inquilino_id}, {self.apartamento_id}, '{self.mes}', {self.valor})"