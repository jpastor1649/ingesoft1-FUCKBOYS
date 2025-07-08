"""
Tabla: 'recibos'.
Author: ahbordam
Versión: 1.0.0
Date: 2025-07-08
"""

from datetime import date
from typing import Optional
from decimal import Decimal
from .enums import TipoServicio


class Recibo:
    """    
    Attributes:
        id (int): ID único del recibo (auto-generado)
        fecha (date): Fecha del recibo
        servicio (TipoServicio): Tipo de servicio del recibo
        mes (str): Mes al que corresponde el recibo
        consumo_inicial (Decimal): Lectura inicial en el recibo
        consumo_final (Decimal): Lectura final en el recibo
    """

    def __init__(self, id: int = 0, fecha: Optional[date] = None,
                 servicio: TipoServicio = TipoServicio.ACUEDUCTO_Y_ASEO, mes: str = "",
                 consumo_inicial: float = 0.0, consumo_final: float = 0.0):
        
        self._id = id
        self._fecha = fecha
        self._servicio = servicio
        self._mes = mes
        self._consumo_inicial = Decimal(str(consumo_inicial))
        self._consumo_final = Decimal(str(consumo_final))

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int):
        if value < 0:
            raise ValueError("El ID no puede ser negativo")
        self._id = value

    @property
    def fecha(self) -> Optional[date]:
        return self._fecha

    @fecha.setter
    def fecha(self, value: Optional[date]):
        self._fecha = value

    @property
    def servicio(self) -> TipoServicio:
        return self._servicio

    @servicio.setter
    def servicio(self, value: TipoServicio):
        if not isinstance(value, TipoServicio):
            raise ValueError("El servicio debe ser del tipo TipoServicio")
        self._servicio = value

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

    @property
    def consumo_inicial(self) -> Decimal:
        return self._consumo_inicial

    @consumo_inicial.setter
    def consumo_inicial(self, value: float):
        if value < 0:
            raise ValueError("El consumo inicial no puede ser negativo")
        self._consumo_inicial = Decimal(str(value))
        self._validar_consumos()

    @property
    def consumo_final(self) -> Decimal:
        return self._consumo_final

    @consumo_final.setter
    def consumo_final(self, value: float):
        if value < 0:
            raise ValueError("El consumo final no puede ser negativo")
        self._consumo_final = Decimal(str(value))
        self._validar_consumos()

    def _validar_consumos(self):
        """
        Valida que el consumo final sea mayor o igual al inicial.
        """
        if self._consumo_final < self._consumo_inicial:
            raise ValueError("El consumo final no puede ser menor al inicial")

    def calcular_consumo_total(self) -> Decimal:

        return self._consumo_final - self._consumo_inicial

    def obtener_consumo_float(self) -> float:

        return float(self.calcular_consumo_total())

    def to_dict(self) -> dict:
        """
        Obj to dicc
        """
        return {
            'reci_id': self.id,
            'reci_fecha': self.fecha,
            'reci_servicio': self.servicio.value,
            'reci_mes': self.mes,
            'reci_consumoInicial': float(self.consumo_inicial),
            'reci_consumoFinal': float(self.consumo_final)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Recibo':
        """
        Dicc to obj
        """
        servicio = TipoServicio.ACUEDUCTO_Y_ASEO
        if data.get('reci_servicio'):
            servicio = TipoServicio(data['reci_servicio'])

        return cls(
            id=data.get('reci_id', 0),
            fecha=data.get('reci_fecha'),
            servicio=servicio,
            mes=data.get('reci_mes', ''),
            consumo_inicial=float(data.get('reci_consumoInicial', 0)),
            consumo_final=float(data.get('reci_consumoFinal', 0))
        )

    def es_valido(self) -> bool:
        """
        Validación de datos.
        """
        try:
            return (self.fecha is not None and
                   len(self.mes.strip()) > 0 and
                   self.consumo_inicial >= 0 and
                   self.consumo_final >= self.consumo_inicial)
        except:
            return False

    def __str__(self) -> str:
        consumo = self.calcular_consumo_total()
        return f"Recibo {self.servicio.value} {self.mes}: {consumo} unidades"

    def __repr__(self) -> str:
        return f"Recibo({self.id}, '{self.servicio.value}', '{self.mes}', {self.consumo_inicial}, {self.consumo_final})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Recibo):
            return False
        return self.id == other.id