from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QHBoxLayout, QPushButton, QDateEdit, QComboBox, QMessageBox,
    QSizePolicy, QFrame, QSpacerItem
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

class ConfiguracionArriendoUsuario(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F3F4F6;
            }
            QLabel#titulo {
                color: #1F2937;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel[data="label"] {
                color: #374151;
                font-size: 14px;
            }
            QLineEdit, QTextEdit, QDateEdit, QComboBox {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
                color: #111827;
                background-color: white;
            }
            QTextEdit {
                min-height: 80px;
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
            QFrame#alertaFrame {
                background-color: #FEF3C7;
                border: 1px solid #FBBF24;
                border-radius: 6px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        titulo = QLabel("💼 Configuración del Arriendo")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)

        def label(text):
            lbl = QLabel(text)
            lbl.setProperty("data", "label")
            return lbl

        self.input_valor = QLineEdit("850000")
        self.input_valor.setReadOnly(True)
        form_layout.addRow(label("Valor mensual de arriendo:"), self.input_valor)

        self.fecha_inicio = QDateEdit(QDate.currentDate())
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setReadOnly(True)
        form_layout.addRow(label("Inicio de contrato:"), self.fecha_inicio)

        self.fecha_vencimiento = QDateEdit(QDate.currentDate().addMonths(12))
        self.fecha_vencimiento.setCalendarPopup(True)
        self.fecha_vencimiento.setReadOnly(True)
        form_layout.addRow(label("Vencimiento del contrato:"), self.fecha_vencimiento)

        self.fecha_pago_reciente = QDateEdit(QDate.currentDate().addDays(-15))
        self.fecha_pago_reciente.setCalendarPopup(True)
        self.fecha_pago_reciente.setReadOnly(True)
        form_layout.addRow(label("Último pago realizado:"), self.fecha_pago_reciente)

        self.combo_estado_pago = QComboBox()
        self.combo_estado_pago.addItems(["Pagado", "En trámite", "Moroso"])
        self.combo_estado_pago.setEnabled(False)
        form_layout.addRow(label("Estado del pago:"), self.combo_estado_pago)

        self.input_observaciones = QTextEdit()
        self.input_observaciones.setPlaceholderText("Observaciones o mensajes del administrador…")
        self.input_observaciones.setReadOnly(True)
        form_layout.addRow(label("Observaciones:"), self.input_observaciones)

        layout.addLayout(form_layout)

        # Alerta visual
        self.alerta_frame = QFrame()
        self.alerta_frame.setObjectName("alertaFrame")
        self.alerta_frame.setVisible(False)

        alerta_layout = QVBoxLayout(self.alerta_frame)
        self.alerta_label = QLabel("⚠️ Su contrato vence en menos de 30 días.")
        self.alerta_label.setWordWrap(True)
        alerta_layout.addWidget(self.alerta_label)
        layout.addWidget(self.alerta_frame)

        # Botón de acción
        botones = QHBoxLayout()
        botones.addStretch()
        self.btn_descargar = QPushButton("Descargar Contrato PDF")
        botones.addWidget(self.btn_descargar)
        layout.addLayout(botones)

        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.check_alerta()

    def check_alerta(self):
        dias_para_vencimiento = QDate.currentDate().daysTo(self.fecha_vencimiento.date())
        estado = self.combo_estado_pago.currentText()

        if estado == "Moroso":
            msg = "❗ Su pago está en estado de mora. Realice el abono cuanto antes."
        elif dias_para_vencimiento <= 30:
            msg = f"⚠️ Su contrato vence en {dias_para_vencimiento} días. Contacte al administrador."
        else:
            self.alerta_frame.setVisible(False)
            return

        self.alerta_label.setText(msg)
        self.alerta_frame.setVisible(True)