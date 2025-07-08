"""
Tabla: 'lecturas'.
Author: ahbordam
Versión: 1.0.0
Date: 2025-07-08
"""

from datetime import date
from typing import Optional
from decimal import Decimal
from .enums import TipoServicio


class Lectura:
    """    
    Attributes:
        id (int): ID único de la lectura (auto-generado)
        apartamento_id (int): ID del apartamento
        fecha (date): Fecha de la lectura
        servicio (TipoServicio): Tipo de servicio medido
        mes (str): Mes al que corresponde la lectura
        consumo_inicial (Decimal): Lectura inicial del contador
        consumo_final (Decimal): Lectura final del contador
    """

    def __init__(self, id: int = 0, apartamento_id: int = 0, fecha: Optional[date] = None,
                 servicio: TipoServicio = TipoServicio.ACUEDUCTO_Y_ASEO, mes: str = "",
                 consumo_inicial: float = 0.0, consumo_final: float = 0.0):
    
        self._id = id
        self._apartamento_id = apartamento_id
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
    def apartamento_id(self) -> int:
        return self._apartamento_id

    @apartamento_id.setter
    def apartamento_id(self, value: int):
        if value <= 0:
            raise ValueError("El ID del apartamento debe ser positivo")
        self._apartamento_id = value

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
        Validaciones
        Consumo final sea mayor o igual al inicial.
        Asociado al trigger de la BD.
        """
        if self._consumo_final < self._consumo_inicial:
            raise ValueError("El consumo final no puede ser menor al inicial")

    def calcular_consumo(self) -> Decimal:
        """
        Calcula el consumo total (final - inicial).
        Returns:
            Decimal: Consumo calculado
        """
        return self._consumo_final - self._consumo_inicial

    def obtener_consumo_float(self) -> float:
        """
        Obtiene el consumo como float para cálculos.
        Returns:
            float: Consumo como número flotante
        """
        return float(self.calcular_consumo())

    def es_consumo_cero(self) -> bool:
        """
        Verifica si el consumo es cero.
        
        Returns:
            bool: True si el consumo es cero
        """
        return self.calcular_consumo() == 0

    def es_consumo_valido(self) -> bool:
        """
        Validación
        """
        consumo = self.obtener_consumo_float()
        
        # Rangos razonables por tipo de servicio (pueden ajustarse)
        if self.servicio == TipoServicio.ACUEDUCTO_Y_ASEO:
            return 0 <= consumo <= 1000  # m³
        elif self.servicio == TipoServicio.ENERGIA:
            return 0 <= consumo <= 5000  # kWh
        elif self.servicio == TipoServicio.GAS_NATURAL:
            return 0 <= consumo <= 500   # m³
        
        return False

    def to_dict(self) -> dict:
        """
        Obj to dicc
        """
        return {
            'lec_id': self.id,
            'lec_apar_id': self.apartamento_id,
            'lec_fecha': self.fecha,
            'lec_servicio': self.servicio.value,
            'lec_mes': self.mes,
            'lec_consumoInicial': float(self.consumo_inicial),
            'lec_consumoFinal': float(self.consumo_final)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Lectura':
        """
        Dicc to obj
        """
        servicio = TipoServicio.ACUEDUCTO_Y_ASEO
        if data.get('lec_servicio'):
            servicio = TipoServicio(data['lec_servicio'])

        return cls(
            id=data.get('lec_id', 0),
            apartamento_id=data.get('lec_apar_id', 0),
            fecha=data.get('lec_fecha'),
            servicio=servicio,
            mes=data.get('lec_mes', ''),
            consumo_inicial=float(data.get('lec_consumoInicial', 0)),
            consumo_final=float(data.get('lec_consumoFinal', 0))
        )

    def es_valido(self) -> bool:
        """
        Validación de datos.
        """
        try:
            return (self.apartamento_id > 0 and
                   self.fecha is not None and
                   len(self.mes.strip()) > 0 and
                   self.consumo_inicial >= 0 and
                   self.consumo_final >= self.consumo_inicial and
                   self.es_consumo_valido())
        except:
            return False

    def __str__(self) -> str:
        consumo = self.calcular_consumo()
        return f"Lectura Apt-{self.apartamento_id} {self.servicio.value} {self.mes}: {consumo}"

    def __repr__(self) -> str:
        return f"Lectura({self.id}, {self.apartamento_id}, '{self.servicio.value}', {self.consumo_inicial}, {self.consumo_final})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Lectura):
            return False
        return (self.apartamento_id == other.apartamento_id and
                self.fecha == other.fecha and
                self.servicio == other.servicio)