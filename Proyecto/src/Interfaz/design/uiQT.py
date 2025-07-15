from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import QPropertyAnimation, pyqtProperty, QEasingCurve
from PyQt5.QtGui import QColor, QPainter, QBrush

class AnimatedToggle(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._circle_position = 2.0
        self.setFixedSize(60, 28)

        self._animation = QPropertyAnimation(self, b"circle_position", self)
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self.stateChanged.connect(self._start_animation)

    def _start_animation(self):
        start = self._circle_position
        end = self.width() - 26 if self.isChecked() else 2
        self._animation.stop()
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fondo del switch
        bg_color = QColor("#4A90E2") if self.isChecked() else QColor("#ccc")
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 14, 14)

        # Círculo deslizante
        painter.setBrush(QBrush(QColor("#fff")))
        painter.drawEllipse(int(self._circle_position), 2, 24, 24)

    @pyqtProperty(float)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos
        self.update()



def estilo_input():
    return """
        QLineEdit {
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
        }
        QLineEdit:focus {
            border: 1px solid #4A90E2;
        }
    """

def button_style(base_color, hover_color):
    return f"""
        QPushButton {{
            background-color: {base_color};
            color: white;
            padding: 10px;
            border: none;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
    """

def estilo_card():
    return """
        QFrame {
            background-color: #ffffff;
            border-radius: 12px;
        }
    """
def estilo_switch():
    return """
        QCheckBox {
            spacing: 10px;
        }
        QCheckBox::indicator {
            width: 40px;
            height: 20px;
            border-radius: 10px;
            background-color: #ccc;
        }
        QCheckBox::indicator:checked {
            background-color: #4A90E2;
        }
    """


def estilo_boton_icono():
    return "border: true;"

def estilo_etiqueta_icono():
    return """
        QLabel {
            color: white;
            font-weight: bold;
            font-size: 12pt;
            border: 2px solid black;
            border-radius: 6px;
            padding: 4px 8px;
            background-color: rgba(0, 0, 0, 0.3); /* Fondo sutil para contraste */
        }
    """

def estilo_barra_inferior():
    return "background-color: #2C3E50;"

def estilo_titulo():
    return """
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
    """
def menuTexStyle():
    return (
        "QPushButton { color: white; background: transparent; text-align: left; padding: 14px; }"
        "QPushButton:hover { background-color: #374151; }"
    )