from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QComboBox, QPushButton, QFrame,
    QSizePolicy, QFileDialog, QSpacerItem
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize


class ReportesYRecibos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F3F4F6;
            }
            QLabel#titulo {
                font-size: 20px;
                font-weight: bold;
                color: #1F2937;
            }
            QLabel#subtitulo {
                font-size: 14px;
                color: #4B5563;
            }
            QComboBox, QPushButton {
                font-size: 14px;
                padding: 6px;
                border-radius: 6px;
            }
            QComboBox {
                border: 1px solid #D1D5DB;
                background-color: white;
            }
            QPushButton {
                background-color: #2563EB;
                color: white;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
            QPushButton#descargar {
                background-color: #10B981;
            }
            QPushButton#descargar:hover {
                background-color: #059669;
            }
            QFrame#filtroFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # — Título y subtítulo —
        titulo = QLabel("📄 Reportes y Recibos")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Consulta tu historial de pagos y descarga tus recibos.")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitulo)

        # — Filtros —
        filtro_frame = QFrame()
        filtro_frame.setObjectName("filtroFrame")
        filtro_layout = QHBoxLayout(filtro_frame)
        filtro_layout.setContentsMargins(12, 12, 12, 12)
        filtro_layout.setSpacing(12)

        filtro_layout.addWidget(QLabel("Mes:"))
        self.combo_mes = QComboBox()
        self.combo_mes.addItems([
            "Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ])
        filtro_layout.addWidget(self.combo_mes)

        filtro_layout.addWidget(QLabel("Servicio:"))
        self.combo_servicio = QComboBox()
        self.combo_servicio.addItems(["Todos", "Arriendo", "Agua", "Luz", "Gas", "Internet"])
        filtro_layout.addWidget(self.combo_servicio)

        self.btn_filtrar = QPushButton("Filtrar")
        filtro_layout.addWidget(self.btn_filtrar)
        filtro_layout.addStretch()

        self.btn_descargar = QPushButton("Descargar PDF")
        self.btn_descargar.setObjectName("descargar")
        filtro_layout.addWidget(self.btn_descargar)

        layout.addWidget(filtro_frame)

        # — Tabla de reportes —
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Mes", "Detalle", "Monto Total", "Estado", "Descargar"
        ])
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.tabla)

        # — Datos de ejemplo —
        datos = [
            ("Junio", "Arriendo + Agua + Luz", "$850.000", "Pagado"),
            ("Mayo", "Arriendo + Agua + Gas", "$820.000", "Pendiente"),
            ("Abril", "Arriendo + Internet", "$780.000", "Vencido"),
        ]

        self.tabla.setRowCount(len(datos))
        for fila, (mes, detalle, monto, estado) in enumerate(datos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(mes))
            self.tabla.setItem(fila, 1, QTableWidgetItem(detalle))
            self.tabla.setItem(fila, 2, QTableWidgetItem(monto))
            self.tabla.setItem(fila, 3, QTableWidgetItem(estado))

            btn_pdf = QPushButton()
            btn_pdf.setIcon(QIcon("Assets/Iconos/pdf.png"))  # Asegúrate que exista
            btn_pdf.setIconSize(QSize(24, 24))
            btn_pdf.setToolTip("Descargar recibo PDF")
            btn_pdf.setCursor(Qt.PointingHandCursor)
            btn_pdf.setStyleSheet("border: none; padding: 4px;")
            self.tabla.setCellWidget(fila, 4, btn_pdf)

        # Espaciador final
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))