import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QMovie, QFont
from PyQt5.QtCore import Qt, QSize

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienvenido")
        self.setMinimumSize(400, 300)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        # Gif animado
        gif_label = QLabel(self)
        movie = QMovie("Assets\ciudad gif.gif")  # ← Ajusta la ruta
        movie.setScaledSize(QSize(800, 800))
        gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(gif_label, alignment=Qt.AlignCenter)

        # Texto de bienvenida
        text = QLabel("👋 Bienvenido a la interfaz de Administrador 🎉", self)
        text.setFont(QFont("Segoe UI", 16, QFont.Bold))
        text.setAlignment(Qt.AlignCenter)
        layout.addWidget(text)

