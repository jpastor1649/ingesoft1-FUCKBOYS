"""
Tabla: 'pagos'.
Author: ahbordam
Versión: 1.0.0
Date: 2025-07-08
"""

from datetime import date
from typing import Optional
from .enums import TipoServicio, EstadoPago, TipoLectura


class Pago:
    """  
    Attributes:
        lectura_apartamento_id (int): ID del apartamento de la lectura
        lectura_fecha (date): Fecha de la lectura relacionada
        lectura_servicio (TipoServicio): Tipo de servicio
        mes (str): Mes del pago
        fecha_pago (date): Fecha en que se realizó el pago
        tipo_lectura (TipoLectura): Tipo de lectura (factura o contador interno)
        consumo (int): Consumo registrado
        valor_total (int): Valor total a pagar
        estado (EstadoPago): Estado del pago
        observacion (str): Observaciones adicionales
    """

    def __init__(self, lectura_apartamento_id: int = 0, lectura_fecha: Optional[date] = None,
                 lectura_servicio: TipoServicio = TipoServicio.ACUEDUCTO_Y_ASEO,
                 mes: str = "", fecha_pago: Optional[date] = None,
                 tipo_lectura: TipoLectura = TipoLectura.LECTURA_CONTADOR_INTERNO,
                 consumo: int = 0, valor_total: int = 0,
                 estado: EstadoPago = EstadoPago.PENDIENTE, observacion: str = ""):
        
        self._lectura_apartamento_id = lectura_apartamento_id
        self._lectura_fecha = lectura_fecha
        self._lectura_servicio = lectura_servicio
        self._mes = mes
        self._fecha_pago = fecha_pago
        self._tipo_lectura = tipo_lectura
        self._consumo = consumo
        self._valor_total = valor_total
        self._estado = estado
        self._observacion = observacion

    @property
    def lectura_apartamento_id(self) -> int:
        return self._lectura_apartamento_id

    @lectura_apartamento_id.setter
    def lectura_apartamento_id(self, value: int):
        if value <= 0:
            raise ValueError("El ID del apartamento debe ser positivo")
        self._lectura_apartamento_id = value

    @property
    def lectura_fecha(self) -> Optional[date]:
        return self._lectura_fecha

    @lectura_fecha.setter
    def lectura_fecha(self, value: Optional[date]):
        self._lectura_fecha = value

    @property
    def lectura_servicio(self) -> TipoServicio:
        return self._lectura_servicio

    @lectura_servicio.setter
    def lectura_servicio(self, value: TipoServicio):
        if not isinstance(value, TipoServicio):
            raise ValueError("El servicio debe ser del tipo TipoServicio")
        self._lectura_servicio = value

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
    def fecha_pago(self) -> Optional[date]:
        return self._fecha_pago

    @fecha_pago.setter
    def fecha_pago(self, value: Optional[date]):
        self._fecha_pago = value

    @property
    def tipo_lectura(self) -> TipoLectura:
        return self._tipo_lectura

    @tipo_lectura.setter
    def tipo_lectura(self, value: TipoLectura):
        if not isinstance(value, TipoLectura):
            raise ValueError("El tipo de lectura debe ser del tipo TipoLectura")
        self._tipo_lectura = value

    @property
    def consumo(self) -> int:
        return self._consumo

    @consumo.setter
    def consumo(self, value: int):
        if value < 0:
            raise ValueError("El consumo no puede ser negativo")
        self._consumo = value

    @property
    def valor_total(self) -> int:
        return self._valor_total

    @valor_total.setter
    def valor_total(self, value: int):
        if value < 0:
            raise ValueError("El valor total no puede ser negativo")
        self._valor_total = value

    @property
    def estado(self) -> EstadoPago:
        return self._estado

    @estado.setter
    def estado(self, value: EstadoPago):
        if not isinstance(value, EstadoPago):
            raise ValueError("El estado debe ser del tipo EstadoPago")
        self._estado = value

    @property
    def observacion(self) -> str:
        return self._observacion

    @observacion.setter
    def observacion(self, value: str):
        self._observacion = value if value else ""

    def esta_pagado(self) -> bool:
        """
        Verifica si el pago está completado.
        """
        return self.estado == EstadoPago.CANCELADO and self.fecha_pago is not None

    def esta_pendiente(self) -> bool:
        """
        Verifica si el pago está pendiente.
        """
        return self.estado == EstadoPago.PENDIENTE

    def obtener_clave_primaria(self) -> tuple:
        """
        Obtiene la clave primaria compuesta del pago.
        
        """
        return (self.lectura_apartamento_id, self.lectura_fecha, self.lectura_servicio.value)

    def to_dict(self) -> dict:
        """
        Obj to dicc
        """
        return {
            'pago_lec_apar_id': self.lectura_apartamento_id,
            'pago_lec_fecha': self.lectura_fecha,
            'pago_lec_servicio': self.lectura_servicio.value,
            'pago_mes': self.mes,
            'pago_fechaPago': self.fecha_pago,
            'pago_tipoLectura': self.tipo_lectura.value,
            'pago_consumo': self.consumo,
            'pago_valorTotal': self.valor_total,
            'pago_estado': self.estado.value,
            'pago_observacion': self.observacion
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Pago':
        """
        Dicc to obj
        """
        servicio = TipoServicio.ACUEDUCTO_Y_ASEO
        if data.get('pago_lec_servicio'):
            servicio = TipoServicio(data['pago_lec_servicio'])

        tipo_lectura = TipoLectura.LECTURA_CONTADOR_INTERNO
        if data.get('pago_tipoLectura'):
            tipo_lectura = TipoLectura(data['pago_tipoLectura'])

        estado = EstadoPago.PENDIENTE
        if data.get('pago_estado'):
            estado = EstadoPago(data['pago_estado'])

        return cls(
            lectura_apartamento_id=data.get('pago_lec_apar_id', 0),
            lectura_fecha=data.get('pago_lec_fecha'),
            lectura_servicio=servicio,
            mes=data.get('pago_mes', ''),
            fecha_pago=data.get('pago_fechaPago'),
            tipo_lectura=tipo_lectura,
            consumo=data.get('pago_consumo', 0),
            valor_total=data.get('pago_valorTotal', 0),
            estado=estado,
            observacion=data.get('pago_observacion', '')
        )

    def es_valido(self) -> bool:
        """
        Validación de datos
        """
        try:
            return (self.lectura_apartamento_id > 0 and
                   self.lectura_fecha is not None and
                   len(self.mes.strip()) > 0 and
                   self.consumo >= 0 and
                   self.valor_total >= 0)
        except:
            return False

    def __str__(self) -> str:
        return f"Pago Apt-{self.lectura_apartamento_id} {self.lectura_servicio.value} {self.mes}: ${self.valor_total:,} ({self.estado.value})"

    def __repr__(self) -> str:
        return f"Pago({self.lectura_apartamento_id}, '{self.lectura_servicio.value}', '{self.mes}', {self.valor_total})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Pago):
            return False
        return self.obtener_clave_primaria() == other.obtener_clave_primaria()