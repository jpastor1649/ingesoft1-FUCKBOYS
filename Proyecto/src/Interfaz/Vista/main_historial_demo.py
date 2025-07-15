from PyQt5.QtWidgets import QApplication
from Modulos.Historial import HistorialReportesDialog
import sys

if __name__ == "__main__":
    aptos = [f"Apto {i}" for i in range(101, 106)]
    app = QApplication(sys.argv)
    dlg = HistorialReportesDialog(aptos)
    dlg.exec_()
