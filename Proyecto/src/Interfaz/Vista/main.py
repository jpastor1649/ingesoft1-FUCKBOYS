# vista/main.py
from PyQt5.QtWidgets import QApplication
from .Login import LoginWindow
import sys

def main():
    app = QApplication(sys.argv)
    ventana = LoginWindow()
    ventana.show()  # Cambia por showMaximized() si quieres pantalla completa
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()