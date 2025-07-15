from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QGridLayout, QComboBox, QDateEdit, QSpinBox, QFileDialog, QMessageBox, QFrame, QTabWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon

class ConfiguracionServiciosDialog(QDialog):
    """⚙️ Configuración de Servicios"""
    def __init__(self, servicios, apartamentos):
        super().__init__()
        self.setWindowTitle("Configuración de Servicios")
        self.setMinimumSize(700, 500)
        self.servicios = servicios
        self.apartamentos = apartamentos

        layout = QVBoxLayout(self)
        # Buscador servicio
        top = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("🔍 Buscar servicio...")
        self.search.setMinimumWidth(400)
        self.search.setFixedHeight(38)
        self.search.setStyleSheet("font-size: 17px; padding: 8px 16px; border-radius: 8px; border: 1.5px solid #CBD5E1;")
        self.search.textChanged.connect(self.filtrar)
        top.addWidget(self.search)
        layout.addLayout(top)

        # Scroll servicios
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        cont = QWidget()
        grid = QGridLayout(cont)
        grid.setSpacing(15)
        grid.setContentsMargins(20,20,20,20)

        # Cabecera
        grid.addWidget(QLabel("<b>Servicio</b>"), 0,0)
        grid.addWidget(QLabel("<b>Compartido</b>"),0,1)
        grid.addWidget(QLabel("<b>Apartamentos vinculados</b>"),0,2)


        # Servicios con líneas separadoras y verticales
        row_count = 1
        for idx, (srv, shared) in enumerate(self.servicios.items()):
            lbl = QLabel(srv); lbl.setFont(QFont("Segoe UI",11))
            chk = QPushButton("Compartido" if shared else "Individual")
            chk.setCheckable(True); chk.setChecked(shared)
            chk.clicked.connect(lambda c, s=srv: self.toggle_shared(s))
            aptos = QLabel(", ".join(self.apartamentos)); aptos.setWordWrap(True)
            grid.addWidget(lbl, row_count, 0)
            grid.addWidget(chk, row_count, 1)
            grid.addWidget(aptos, row_count, 2)
            # Líneas verticales
            for col in range(1, 3):
                vline = QFrame()
                vline.setFrameShape(QFrame.VLine)
                vline.setFrameShadow(QFrame.Sunken)
                vline.setStyleSheet("color: #CBD5E1; background: #CBD5E1; min-width: 1px;")
                grid.addWidget(vline, row_count, col)
            # Línea separadora
            if idx < len(self.servicios) - 1:
                row_count += 1
                for col in range(3):
                    line = QFrame()
                    line.setFrameShape(QFrame.HLine)
                    line.setFrameShadow(QFrame.Sunken)
                    line.setStyleSheet("color: #CBD5E1; background: #CBD5E1; min-height: 1px;")
                    grid.addWidget(line, row_count, col)
            row_count += 1

        scroll.setWidget(cont)
        layout.addWidget(scroll)
        from qtawesome import icon as qta_icon
        btn = QPushButton("  Guardar configuración")
        btn.setIcon(qta_icon('fa5s.save', color='#2563EB'))
        btn.setStyleSheet("QPushButton { background: #2563EB; color: white; border-radius: 8px; padding: 10px 24px; font-size: 15px; } QPushButton:hover { background: #1E40AF; }")
        btn.setMinimumWidth(220)
        btn.clicked.connect(self.guardar)
        layout.addWidget(btn, alignment=Qt.AlignRight)

    def toggle_shared(self, servicio):
        self.servicios[servicio] = not self.servicios[servicio]

    def filtrar(self, text):
        # simple filtering (could be improved)
        for i in range(1, self.layout().itemAt(1).widget().widget().layout().rowCount()):
            lbl = self.layout().itemAt(1).widget().widget().layout().itemAtPosition(i,0).widget()
            visible = text.lower() in lbl.text().lower()
            for col in range(3):
                w = self.layout().itemAt(1).widget().widget().layout().itemAtPosition(i,col).widget()
                w.setVisible(visible)

    def guardar(self):
        QMessageBox.information(self, "Guardado", "Configuración de servicios guardada correctamente.")
        self.accept()

class RegistroLecturasDialog(QDialog):
    """📊 Registro de Lecturas Internas"""
    def __init__(self, apartamentos):
        super().__init__()
        self.setWindowTitle("Registro de Lecturas Internas")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        # Buscador
        top = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("🔍 Buscar apto...")
        top.addWidget(self.search)
        layout.addLayout(top)

        # Tabla scroll
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        cont = QWidget(); grid = QGridLayout(cont)
        grid.setContentsMargins(20,20,20,20); grid.setSpacing(10)
        headers = ["Apartamento","Servicio","Fecha","Lectura Inicial","Lectura Final"]
        for c,h in enumerate(headers): grid.addWidget(QLabel(f"<b>{h}</b>"),0,c)
        from PyQt5.QtWidgets import QCalendarWidget
        row_count = 1
        for idx, apto in enumerate(apartamentos):
            grid.addWidget(QLabel(apto), row_count, 0)
            serv = QComboBox(); serv.addItems(["Agua","Luz","Gas","Internet"])
            grid.addWidget(serv, row_count, 1)
            # Usar QCalendarWidget para seleccionar fecha
            date_btn = QPushButton("Seleccionar fecha")
            date_lbl = QLabel(QDate.currentDate().toString("yyyy-MM-dd"))
            def show_calendar(row=row_count, label=date_lbl):
                cal = QCalendarWidget()
                cal.setGridVisible(True)
                cal.setWindowModality(Qt.ApplicationModal)
                cal.setWindowTitle("Seleccionar fecha")
                cal.setMinimumSize(400,300)
                def set_date():
                    label.setText(cal.selectedDate().toString("yyyy-MM-dd"))
                    cal.close()
                cal.clicked.connect(set_date)
                cal.show()
            date_btn.clicked.connect(show_calendar)
            date_layout = QHBoxLayout()
            date_layout.addWidget(date_lbl)
            date_layout.addWidget(date_btn)
            date_widget = QWidget(); date_widget.setLayout(date_layout)
            grid.addWidget(date_widget, row_count, 2)
            ini = QSpinBox(); ini.setMaximum(100000); grid.addWidget(ini, row_count, 3)
            fin = QSpinBox(); fin.setMaximum(100000); grid.addWidget(fin, row_count, 4)
            # Línea separadora
            if idx < len(apartamentos) - 1:
                row_count += 1
                for col in range(5):
                    line = QFrame()
                    line.setFrameShape(QFrame.HLine)
                    line.setFrameShadow(QFrame.Sunken)
                    line.setStyleSheet("color: #CBD5E1; background: #CBD5E1; min-height: 1px;")
                    grid.addWidget(line, row_count, col)
            row_count += 1
        scroll.setWidget(cont); layout.addWidget(scroll)
        from qtawesome import icon as qta_icon
        btn = QPushButton("  Guardar Lecturas")
        btn.setIcon(qta_icon('fa5s.save', color='#2563EB'))
        btn.setStyleSheet("QPushButton { background: #2563EB; color: white; border-radius: 8px; padding: 10px 24px; font-size: 15px; } QPushButton:hover { background: #1E40AF; }")
        btn.setMinimumWidth(220)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)

class IngresoRecibosDialog(QDialog):
    """📥 Ingreso de Recibos"""
    def __init__(self, apartamentos):
        super().__init__()
        self.setWindowTitle("Ingreso de Recibos")
        self.setMinimumSize(600,400)
        layout=QVBoxLayout(self)
        form = QVBoxLayout()
        cb = QComboBox(); cb.addItems(apartamentos); form.addWidget(QLabel("Apartamento:")); form.addWidget(cb)
        cs = QComboBox(); cs.addItems(["Agua","Luz","Gas","Internet"]); form.addWidget(QLabel("Servicio:")); form.addWidget(cs)
        # Usar QCalendarWidget para seleccionar fecha
        date_btn = QPushButton("Seleccionar fecha")
        date_lbl = QLabel(QDate.currentDate().toString("yyyy-MM-dd"))
        def show_calendar():
            from PyQt5.QtWidgets import QCalendarWidget
            cal = QCalendarWidget()
            cal.setGridVisible(True)
            cal.setWindowModality(Qt.ApplicationModal)
            cal.setWindowTitle("Seleccionar fecha")
            cal.setMinimumSize(400,300)
            def set_date():
                date_lbl.setText(cal.selectedDate().toString("yyyy-MM-dd"))
                cal.close()
            cal.clicked.connect(set_date)
            cal.show()
        date_btn.clicked.connect(show_calendar)
        date_layout = QHBoxLayout()
        date_layout.addWidget(date_lbl)
        date_layout.addWidget(date_btn)
        date_widget = QWidget(); date_widget.setLayout(date_layout)
        form.addWidget(QLabel("Fecha:")); form.addWidget(date_widget)
        sp = QSpinBox(); sp.setMaximum(100000); form.addWidget(QLabel("Consumo:")); form.addWidget(sp)
        tr = QLineEdit(); tr.setPlaceholderText("Tarifa por unidad"); form.addWidget(QLabel("Tarifa:")); form.addWidget(tr)
        layout.addLayout(form)
        from qtawesome import icon as qta_icon
        btn = QPushButton("  Ingresar Recibo")
        btn.setIcon(qta_icon('fa5s.save', color='#2563EB'))
        btn.setStyleSheet("QPushButton { background: #2563EB; color: white; border-radius: 8px; padding: 10px 24px; font-size: 15px; } QPushButton:hover { background: #1E40AF; }")
        btn.setMinimumWidth(220)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)

class GenerarRecibosDialog(QDialog):
    """📤 Generar y Exportar Recibos"""
    def __init__(self, apartamentos):
        super().__init__()
        self.setWindowTitle("Generar y Exportar Recibos")
        self.setMinimumSize(800,600)
        layout=QVBoxLayout(self)
        top=QHBoxLayout(); dm=QDateEdit(QDate.currentDate()); dm.setDisplayFormat("yyyy-MM")
        top.addWidget(QLabel("Mes/Año:")); top.addWidget(dm)
        from qtawesome import icon as qta_icon
        bg = QPushButton("  Generar Recibos")
        bg.setIcon(qta_icon('fa5s.save', color='#2563EB'))
        bg.setStyleSheet("QPushButton { background: #2563EB; color: white; border-radius: 8px; padding: 10px 24px; font-size: 15px; } QPushButton:hover { background: #1E40AF; }")
        bg.setMinimumWidth(220)
        top.addWidget(bg)
        layout.addLayout(top)
        scroll=QScrollArea(); scroll.setWidgetResizable(True)
        cont=QWidget(); grid=QGridLayout(cont); grid.setContentsMargins(20,20,20,20); grid.setSpacing(10)
        row_count = 0
        for idx, apto in enumerate(apartamentos):
            grid.addWidget(QLabel(apto), row_count, 0)
            grid.addWidget(QLabel("Monto:"), row_count, 1)
            grid.addWidget(QLabel("$0.00"), row_count, 2)
            pdf = QPushButton("📥 PDF"); grid.addWidget(pdf, row_count, 3)
            # Línea separadora
            if idx < len(apartamentos) - 1:
                row_count += 1
                for col in range(4):
                    line = QFrame()
                    line.setFrameShape(QFrame.HLine)
                    line.setFrameShadow(QFrame.Sunken)
                    line.setStyleSheet("color: #CBD5E1; background: #CBD5E1; min-height: 1px;")
                    grid.addWidget(line, row_count, col)
            row_count += 1
        scroll.setWidget(cont); layout.addWidget(scroll)

class GestionServicios(QWidget):
    def __init__(self, servicios, apartamentos):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background: #F8FAFC;
                border-radius: 18px;
            }
            QTabWidget::pane {
                border: 1.5px solid #CBD5E1;
                border-radius: 12px;
                background: #F8FAFC;
            }
            QTabBar::tab {
                background: #E5E7EB;
                color: #1F2937;
                border-radius: 8px 8px 0 0;
                padding: 12px 48px;
                font-size: 18px;
                margin-right: 8px;
                min-width: 180px;
                min-height: 40px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabBar::tab:selected {
                background: #2563EB;
                color: white;
            }
        """)
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        # Instanciar los widgets de cada sección
        self.tab_config = ConfiguracionServiciosDialog(servicios, apartamentos)
        self.tab_lecturas = RegistroLecturasDialog(apartamentos)
        self.tab_ingreso = IngresoRecibosDialog(apartamentos)
        self.tab_generar = GenerarRecibosDialog(apartamentos)
        # Agregar como widgets a las pestañas
        self.tabs.addTab(self.tab_config, "⚙️ Configuración")
        self.tabs.addTab(self.tab_lecturas, "📊 Lectura")
        self.tabs.addTab(self.tab_ingreso, "📥 Ingreso Recibo")
        self.tabs.addTab(self.tab_generar, "📤 Generar Recibo")
        layout.addWidget(self.tabs)

# Ejemplo de uso
if __name__=='__main__':
    import sys; from PyQt5.QtWidgets import QApplication
    aptos=[f"Apto {i}" for i in range(101,106)]
    servicios={"Agua":True,"Luz":True,"Gas":False}
    app=QApplication(sys.argv)
    ConfiguracionServiciosDialog(servicios,aptos).exec_()
    RegistroLecturasDialog(aptos).exec_()
    IngresoRecibosDialog(aptos).exec_()
    GenerarRecibosDialog(aptos).exec_()
