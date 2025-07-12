import sys

sys.path.append("src")
from connector.connector import Connector

sys.path.append("src/models")
from models.arrendo import Arrendo
from models.apartamento import Apartamento
from models.inquilino import Inquilino
from models.lectura import Lectura
from models.recibo import Recibo
from models.pago import Pago


class Usuario:
    def __init__(self, id_usuario: int, rol: str, connector: Connector):
        self.id_usuario = id_usuario
        self.rol = rol
        self.db = connector
        self.nombre =  self._cargar_nombre_desde_db()


    def es_admin(self) -> bool:
        return self.rol == "admin"

    def obtener_arrendos(self):
        return (
            Arrendo.fetch_all(self.db)
            if self.es_admin()
            else Arrendo.fetch_by_inquilino(self.db, self.id_usuario)
        )

    def obtener_apartamentos(self):
        return (
            Apartamento.fetch_all(self.db)
            if self.es_admin()
            else Apartamento.fetch_by_inquilino(self.db, self.id_usuario)
        )

    def obtener_inquilinos(self):
        return (
            Inquilino.fetch_all(self.db)
            if self.es_admin()
            else [Inquilino.fetch_by_inquilino(self.db, self.id_usuario)]
        )

    def obtener_lecturas(self):
        return (
            Lectura.fetch_all(self.db)
            if self.es_admin()
            else Lectura.fetch_by_inquilino(self.db, self.id_usuario)
        )

    def obtener_recibos(self):
        return (
            Recibo.fetch_all(self.db)
            if self.es_admin()
            else Recibo.fetch_by_inquilino(self.db, self.id_usuario)
        )

    def obtener_pagos(self):
        return (
            Pago.fetch_all(self.db)
            if self.es_admin()
            else Pago.fetch_by_inquilino(self.db, self.id_usuario)
        )

    def _cargar_nombre_desde_db(self):
        try:
            self.db.set_table("inquilinos")
            datos = self.db.get_filtered(f"inq_id = {self.id_usuario}")
            if datos:
                self.nombre = datos[0].get("inq_nombre", "")
            else:
                self.nombre = "Desconocido"
        except Exception as e:
            print(f"⚠️ Error cargando nombre del inquilino: {e}")
            self.nombre = "Desconocido"

    def __str__(self) -> str:
        if self.es_admin():
            return "👤 Usuario Administrador (acceso completo)"
        return f"🏠 Inquilino ID: {self.id_usuario} - Nombre: {self.nombre or 'Desconocido'}"
