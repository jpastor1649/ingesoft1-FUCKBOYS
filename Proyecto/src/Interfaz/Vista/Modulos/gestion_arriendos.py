from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit,
    QTextEdit, QPushButton, QMessageBox, QFormLayout, QSizePolicy, QGroupBox, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from qtawesome import icon as qta_icon


class ConfiguracionArriendos(QWidget):
    def __init__(self, apartamentos=None, parent=None):
        super().__init__(parent)
        self.apartamentos = apartamentos or ["Apartamento A", "Apartamento B"]
        self.setStyleSheet(self._build_stylesheet())
        self.init_ui()

    def _build_stylesheet(self):
        return """
        QWidget {
            background-color: #F9FAFB;
        }
        QLabel#titulo {
            color: #1F2937;
            font-size: 20px;
            font-weight: bold;
        }
        QGroupBox {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            margin-top: 10px;
            font-size: 15px;
            color: #2563EB;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 4px;
        }
        QLineEdit, QTextEdit, QComboBox {
            border: 1px solid #D1D5DB;
            border-radius: 4px;
            padding: 6px;
            font-size: 14px;
            color: #374151;
        }
        QPushButton {
            background-color: #2563EB;
            color: white;
            border-radius: 6px;
            padding: 8px 20px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #1E40AF;
        }
        QPushButton#limpiar {
            background-color: #6B7280;
        }
        QPushButton#limpiar:hover {
            background-color: #4B5563;
        }
        """

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # — Título —
        titulo = QLabel("Configuración de Arriendos")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        # — Separador —
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(sep)

        # — Grupo de formulario —
        grupo = QGroupBox("Detalles del Arriendo")
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(12)

        # Apartamento
        self.combo_apto = QComboBox()
        self.combo_apto.addItems(self.apartamentos)
        form_layout.addRow("Apartamento:", self.combo_apto)

        # Valor
        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("Ej. 450000")
        form_layout.addRow("Valor ($):", self.input_valor)

        # Estado
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Pagado", "Pendiente", "Vencido"])
        form_layout.addRow("Estado del pago:", self.combo_estado)

        # Observaciones
        self.input_obs = QTextEdit()
        self.input_obs.setPlaceholderText("Comentarios adicionales...")
        self.input_obs.setFixedHeight(80)
        form_layout.addRow("Observaciones:", self.input_obs)

        grupo.setLayout(form_layout)
        main_layout.addWidget(grupo)

        # — Espaciador vertical —
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # — Botones —
        botones = QHBoxLayout()
        botones.setSpacing(12)

        self.btn_guardar = QPushButton("  Guardar")
        self.btn_guardar.setIcon(qta_icon('fa5s.save', color='white'))
        self.btn_guardar.clicked.connect(self.guardar_datos)
        botones.addWidget(self.btn_guardar)

        self.btn_limpiar = QPushButton("  Limpiar")
        self.btn_limpiar.setObjectName("limpiar")
        self.btn_limpiar.setIcon(qta_icon('fa5s.broom', color='white'))
        self.btn_limpiar.clicked.connect(self.limpiar_campos)
        botones.addWidget(self.btn_limpiar)

        main_layout.addLayout(botones)

    def guardar_datos(self):
        apto = self.combo_apto.currentText()
        valor = self.input_valor.text().replace(".", "").strip()
        estado = self.combo_estado.currentText()
        observaciones = self.input_obs.toPlainText()

        if not valor.isdigit():
            QMessageBox.warning(self, "Error", "El valor del arriendo debe ser numérico.")
            return

        QMessageBox.information(
            self,
            "Guardado",
            f"Datos guardados:\n\nApartamento: {apto}\nValor: ${int(valor):,}\nEstado: {estado}"
        )

    def limpiar_campos(self):
        self.combo_apto.setCurrentIndex(0)
        self.input_valor.clear()
        self.combo_estado.setCurrentIndex(0)
        self.input_obs.clear()