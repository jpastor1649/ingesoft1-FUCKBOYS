from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QSizePolicy, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt


class MiHogar(QWidget):
    def __init__(self, datos_apartamento=None, parent=None):
        super().__init__(parent)

        # Datos simulados si no se pasan desde backend
        self.datos = datos_apartamento or {
            "apartamento": "302",
            "piso": "3",
            "personas": 3,
            "estado_arriendo": "Activo",
            "observaciones": "Revisar fuga en el grifo del baño.",
            "servicios": ["Agua", "Luz", "Internet"]
        }

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        titulo = QLabel("🏡 Mi Hogar")
        titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)

        def crear_linea(texto, valor):
            fila = QHBoxLayout()
            label = QLabel(f"{texto}:")
            label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            label.setFixedWidth(250)
            valor_lbl = QLabel(str(valor))
            valor_lbl.setFont(QFont("Segoe UI", 12))
            fila.addWidget(label)
            fila.addWidget(valor_lbl)
            return fila

        info_layout.addLayout(crear_linea("Número de apartamento", self.datos["apartamento"]))
        info_layout.addLayout(crear_linea("Piso", self.datos["piso"]))
        info_layout.addLayout(crear_linea("Personas registradas", self.datos["personas"]))
        info_layout.addLayout(crear_linea("Estado del arriendo", self.datos["estado_arriendo"]))

        obs_lbl = QLabel("Observaciones del inmueble:")
        obs_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(obs_lbl)

        obs_text = QLabel(self.datos["observaciones"])
        obs_text.setWordWrap(True)
        obs_text.setFont(QFont("Segoe UI", 11))
        obs_text.setStyleSheet("background: #F9FAFB; border: 1px solid #E5E7EB; padding: 8px; border-radius: 6px;")
        layout.addWidget(obs_text)

        servicios_lbl = QLabel("Servicios activos:")
        servicios_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(servicios_lbl)

        lista_servicios = QListWidget()
        lista_servicios.setStyleSheet("background-color: white; border: 1px solid #D1D5DB;")
        for servicio in self.datos["servicios"]:
            item = QListWidgetItem(f"✅ {servicio}")
            item.setFont(QFont("Segoe UI", 11))
            lista_servicios.addItem(item)

        layout.addLayout(info_layout)
        layout.addWidget(lista_servicios)
        layout.addStretch()
