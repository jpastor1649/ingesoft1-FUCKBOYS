# widgets.py

from PyQt5.QtWidgets import QWidget, QCheckBox, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal

class RoleSwitch(QWidget):
    toggled = pyqtSignal(str)  # Señal emitida con el rol actual

    def __init__(self, parent=None):
        super().__init__(parent)

        # Texto que indica el estado actual del rol
        self.label = QLabel("Soy arrendatario")
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet("color: #444;")

        # Switch basado en QCheckBox
        self.switch = QCheckBox()
        self.switch.setChecked(False)
        self.switch.setStyleSheet(self.estilo_switch())
        self.switch.stateChanged.connect(self.actualizar_rol)

        # Layout horizontal que contiene texto + switch
        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.switch)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

    def actualizar_rol(self, state):
        if state == Qt.Checked:
            self.label.setText("Soy arrendador")
            self.toggled.emit("arrendador")
        else:
            self.label.setText("Soy arrendatario")
            self.toggled.emit("arrendatario")

    def estilo_switch(self):
        return """
        QCheckBox::indicator {
            width: 50px;
            height: 25px;
            border-radius: 12px;
            background-color: #ccc;
            position: relative;
        }
        QCheckBox::indicator:checked {
            background-color: #4A90E2;
        }
        QCheckBox::indicator:unchecked::before,
        QCheckBox::indicator:checked::before {
            content: "";
            position: absolute;
            top: 2px;
            left: 2px;
            width: 21px;
            height: 21px;
            background-color: white;
            border-radius: 10px;
            transition: left 0.2s ease;
        }
        QCheckBox::indicator:checked::before {
            left: 27px;
        }
        """