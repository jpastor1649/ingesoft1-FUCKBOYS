from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QScrollArea, QWidget, QGridLayout, QMessageBox, QCalendarWidget
)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont
from qtawesome import icon as qta_icon

class HistorialReportesDialog(QDialog):
    def __init__(self, apartamentos):
        super().__init__()
        self.setWindowTitle("Historial y Reportes")
        self.setMinimumSize(900, 600)
        self.setWindowFlags(Qt.Widget)

        layout = QVBoxLayout(self)

        filtros = QHBoxLayout()
        filtros.addWidget(QLabel("Mes/Año:"))
        self.filter_date_lbl = QLabel(QDate.currentDate().toString("yyyy-MM"))
        self.filter_date_btn = QPushButton("Seleccionar fecha")
        self.filter_date_btn.setStyleSheet("padding: 6px 16px; border-radius: 6px; background: #E5E7EB; color: #1F2937; font-size: 14px;")
        self.filter_date_btn.clicked.connect(self.show_calendar)
        filtros.addWidget(self.filter_date_lbl)
        filtros.addWidget(self.filter_date_btn)

        filtros.addWidget(QLabel("Rol:"))
        self.filter_role = QComboBox()
        self.filter_role.addItems(["Todos", "Arrendador", "Arrendatario"])
        filtros.addWidget(self.filter_role)

        filtros.addWidget(QLabel("Servicio:"))
        self.filter_service = QComboBox()
        self.filter_service.addItems(["Todos", "Agua", "Luz", "Gas", "Internet"])
        filtros.addWidget(self.filter_service)

        filtros.addStretch()

        self.btn_generate = QPushButton("  Generar Reporte")
        self.btn_generate.setIcon(qta_icon('fa5s.chart-bar', color='#2563EB'))
        self.btn_generate.setStyleSheet("QPushButton { background: #2563EB; color: white; border-radius: 8px; padding: 10px 24px; font-size: 15px; } QPushButton:hover { background: #1E40AF; }")
        self.btn_generate.clicked.connect(self.generar_reporte)
        filtros.addWidget(self.btn_generate)

        layout.addLayout(filtros)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_container = QWidget()
        self.grid = QGridLayout(self.table_container)
        self.grid.setSpacing(12)
        self.grid.setContentsMargins(20, 20, 20, 20)
        self.scroll.setWidget(self.table_container)
        layout.addWidget(self.scroll)

        footer = QHBoxLayout()
        footer.addStretch()
        self.btn_export_pdf = QPushButton("  Exportar PDF")
        self.btn_export_pdf.setIcon(qta_icon('fa5s.file-pdf', color='#DC2626'))
        self.btn_export_pdf.setStyleSheet("QPushButton { background: #DC2626; color: white; border-radius: 8px; padding: 8px 20px; font-size: 14px; } QPushButton:hover { background: #991B1B; }")
        self.btn_export_pdf.clicked.connect(lambda: QMessageBox.information(self, "Exportar", "Función PDF próximamente"))
        footer.addWidget(self.btn_export_pdf)

        self.btn_export_csv = QPushButton("  Exportar CSV")
        self.btn_export_csv.setIcon(qta_icon('fa5s.file-csv', color='#2563EB'))
        self.btn_export_csv.setStyleSheet("QPushButton { background: #2563EB; color: white; border-radius: 8px; padding: 8px 20px; font-size: 14px; } QPushButton:hover { background: #1E40AF; }")
        self.btn_export_csv.clicked.connect(lambda: QMessageBox.information(self, "Exportar", "Función CSV próximamente"))
        footer.addWidget(self.btn_export_csv)

        layout.addLayout(footer)

        self.apartamentos = apartamentos

        # Ejecutar automáticamente después de insertarse en el layout
        QTimer.singleShot(0, self.generar_tabla)

    def show_calendar(self):
        cal = QCalendarWidget()
        cal.setGridVisible(True)
        cal.setWindowModality(Qt.ApplicationModal)
        cal.setWindowTitle("Seleccionar fecha")
        cal.setMinimumSize(400, 300)
        def set_date():
            self.filter_date_lbl.setText(cal.selectedDate().toString("yyyy-MM"))
            cal.close()
        cal.clicked.connect(set_date)
        cal.show()

    def generar_tabla(self, mes=None, rol=None, servicio=None):
        if mes is None:
            mes = self.filter_date_lbl.text()
        if rol is None:
            rol = self.filter_role.currentText()
        if servicio is None:
            servicio = self.filter_service.currentText()

        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        headers = ["Apartamento", "Servicio", "Mes/Año", "Consumo", "Valor Pagado"]
        for col, h in enumerate(headers):
            lbl = QLabel(f"<b>{h}</b>")
            lbl.setTextFormat(Qt.RichText)
            lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            lbl.setStyleSheet("color: #2563EB; padding: 6px 0;")
            self.grid.addWidget(lbl, 0, col)

        sample = [
            {"apto": "Apto 101", "srv": "Agua", "mes": "2025-06", "rol": "Arrendatario", "cons": 120.5, "valor": 30000},
            {"apto": "Apto 202", "srv": "Luz", "mes": "2025-06", "rol": "Arrendador", "cons": 85.2, "valor": 45000},
            {"apto": "Apto 303", "srv": "Internet", "mes": "2025-06", "rol": "Arrendatario", "cons": 50, "valor": 60000},
        ]

        filtered = [rec for rec in sample if (not mes or rec["mes"] == mes)
                    and (rol == "Todos" or rec["rol"] == rol)
                    and (servicio == "Todos" or rec["srv"] == servicio)]

        for row, rec in enumerate(filtered, start=1):
            self.grid.addWidget(QLabel(rec["apto"]), row, 0)
            self.grid.addWidget(QLabel(rec["srv"]), row, 1)
            self.grid.addWidget(QLabel(rec["mes"]), row, 2)
            self.grid.addWidget(QLabel(str(rec["cons"])), row, 3)
            self.grid.addWidget(QLabel(f"${rec['valor']:.0f}"), row, 4)

        self.table_container.adjustSize()
        self.scroll.ensureVisible(0, 0)
        self.scroll.repaint()

    def generar_reporte(self):
        self.generar_tabla()
        QMessageBox.information(self, "Reporte", "Reporte generado correctamente.")
