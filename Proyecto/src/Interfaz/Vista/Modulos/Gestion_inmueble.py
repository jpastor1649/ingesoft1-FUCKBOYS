from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QLineEdit, QMessageBox, QFileDialog, QDialog, QGridLayout, QFrame, QCheckBox, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QSize

class GestionInmueble(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #F9FAFB;")

        layout = QVBoxLayout(self)

        # Buscador y botón agregar
        top_layout = QHBoxLayout()
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("🔍 Buscar por nombre...")
        self.buscador.setFixedHeight(32)
        self.buscador.textChanged.connect(self.filtrar_apartamentos)

        self.boton_agregar = QPushButton("➕ Agregar Apartamento")
        self.boton_agregar.setFixedHeight(32)
        self.boton_agregar.clicked.connect(self.abrir_formulario_apartamento)

        top_layout.addWidget(self.buscador)
        top_layout.addStretch()
        top_layout.addWidget(self.boton_agregar)
        layout.addLayout(top_layout)

        # Área scroll para apartamentos
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(30)
        self.grid.setContentsMargins(30, 30, 30, 30)
        self.scroll_area.setWidget(self.scroll_content)

        layout.addWidget(self.scroll_area)

        # Datos ficticios para testeo
        self.apartamentos = [
            {"nombre": "Apto 101", "direccion": "Calle 123", "estado": "Ocupado", "inquilinos": 2, "imagen": "Assets/departamento.jpg"},
            {"nombre": "Apto 202", "direccion": "Cra 45", "estado": "Vacío", "inquilinos": 0, "imagen": "Assets/departamento2.jpg"},
        ]

        self.mostrar_apartamentos()

    def filtrar_apartamentos(self):
        texto = self.buscador.text().lower()
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        for apto in self.apartamentos:
            if texto in apto["nombre"].lower():
                self.grid.addWidget(self.crear_tarjeta_apartamento(apto), self.grid.count() // 3, self.grid.count() % 3)

    def mostrar_apartamentos(self):
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        # Responsivo: 3 columnas si ancho >1200, 2 si >800, 1 si menos
        ancho = self.scroll_area.width() if self.scroll_area.width() > 0 else 1200
        if ancho > 1200:
            cols = 3
        elif ancho > 800:
            cols = 2
        else:
            cols = 1
        for idx, apto in enumerate(self.apartamentos):
            self.grid.addWidget(self.crear_tarjeta_apartamento(apto), idx // cols, idx % cols)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.mostrar_apartamentos()

    def crear_tarjeta_apartamento(self, apto):
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border: 1px solid #E5E7EB; border-radius: 12px;")
        frame.setMinimumWidth(350)
        frame.setMaximumWidth(700)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setFixedHeight(400)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)

        pixmap = QPixmap(apto["imagen"]).scaled(600, 250, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        img = QLabel()
        img.setPixmap(pixmap)
        img.setFixedHeight(250)
        img.setStyleSheet("border-radius: 10px;")

        estado = QLabel("🟢 Ocupado" if apto["estado"] == "Ocupado" else "🔴 Vacío")
        estado.setStyleSheet("font-weight: bold; color: #10B981;" if apto["estado"] == "Ocupado" else "color: #EF4444;")
        estado.setFont(QFont("Segoe UI", 12, QFont.Bold))

        nombre = QLabel(f"🏷️ {apto['nombre']}")
        direccion = QLabel(f"📍 {apto['direccion']}")
        inquilinos = QLabel(f"👤 {apto['inquilinos']} inquilino(s)")

        for lbl in [nombre, direccion, inquilinos]:
            lbl.setFont(QFont("Segoe UI", 12))

        boton_menu = QPushButton("⋮")
        boton_menu.setStyleSheet("font-size: 22px; background: transparent;")
        boton_menu.setFixedWidth(36)
        boton_menu.clicked.connect(lambda: self.abrir_menu_apto(apto))

        header = QHBoxLayout()
        header.addWidget(estado)
        header.addStretch()
        header.addWidget(boton_menu)

        layout.addWidget(img)
        layout.addLayout(header)
        layout.addWidget(nombre)
        layout.addWidget(direccion)
        layout.addWidget(inquilinos)

        return frame

    def abrir_menu_apto(self, apto):
        msg = QMessageBox()
        msg.setWindowTitle(apto['nombre'])
        msg.setText("Selecciona una acción:")
        msg.addButton("Mostrar info", QMessageBox.AcceptRole)
        msg.addButton("Editar", QMessageBox.ActionRole)
        msg.addButton("Eliminar", QMessageBox.DestructiveRole)
        res = msg.exec_()

        if res == 0:
            self.mostrar_info_apto(apto)
        elif res == 1:
            self.editar_apartamento(apto)
        elif res == 2:
            self.eliminar_apartamento(apto)

    def eliminar_apartamento(self, apto):
        self.apartamentos.remove(apto)
        self.mostrar_apartamentos()

        confirm = QMessageBox()
        confirm.setWindowTitle("Éxito")
        confirm.setText("🏠 El apartamento se ha eliminado con éxito")
        confirm.addButton("Continuar", QMessageBox.AcceptRole)
        confirm.exec_()

    def mostrar_info_apto(self, apto):
        info = f"""
        <div style='background:#F8FAFC; border-radius:14px; padding:12px 6px; font-size:16px;'>
            <div style='font-size:22px; font-weight:bold; color:#2563EB; margin-bottom:8px;'>🏷️ {apto['nombre']}</div>
            <div>📍 <b>Dirección:</b> {apto['direccion']}</div>
            <div>👤 <b>Inquilinos:</b> {apto['inquilinos']}</div>
            <div>📶 <b>Estado:</b> {'🟢 Ocupado' if apto['estado']=='Ocupado' else '🔴 Vacío'}</div>
        </div>
        """
        msg = QMessageBox()
        msg.setWindowTitle("Información del Apartamento")
        msg.setTextFormat(Qt.RichText)
        msg.setText(info)
        msg.setStyleSheet("QLabel{min-width:340px;}")
        msg.exec_()

    def editar_apartamento(self, apto):
        self.formulario_apartamento(apto, editar=True)

    def abrir_formulario_apartamento(self):
        self.formulario_apartamento()

    def formulario_apartamento(self, apto=None, editar=False):
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Apartamento" if editar else "Nuevo Apartamento")
        dialog.setMinimumWidth(540)
        dialog.setMinimumHeight(520)
        dialog.setStyleSheet("""
            QDialog {
                background: #F8FAFC;
                border-radius: 18px;
            }
            QLabel[title='true'] {
                font-size: 22px;
                font-weight: bold;
                color: #1F2937;
                margin-bottom: 12px;
            }
            QLineEdit, QComboBox {
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 15px;
                background: #fff;
                margin-bottom: 8px;
            }
            QPushButton {
                background: #2563EB;
                color: white;
                border-radius: 8px;
                padding: 10px 0;
                font-size: 16px;
                min-width: 160px;
            }
            QPushButton#cancelar {
                background: #E5E7EB;
                color: #1F2937;
            }
        """)
        from PyQt5.QtWidgets import QScrollArea
        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        scroll.setWidget(content)
        main_layout = QVBoxLayout(dialog)
        main_layout.addWidget(scroll)

        titulo = QLabel("Editar Apartamento" if editar else "Nuevo Apartamento")
        titulo.setProperty('title', True)
        layout.addWidget(titulo, alignment=Qt.AlignHCenter)

        nombre = QLineEdit(apto["nombre"] if apto else "")
        direccion = QLineEdit(apto["direccion"] if apto else "")
        inquilinos = QLineEdit(str(apto["inquilinos"]) if apto else "")
        from PyQt5.QtWidgets import QComboBox
        estado = QComboBox()
        estado.addItems(["Ocupado", "Vacío"])
        if apto and apto["estado"] == "Vacío":
            estado.setCurrentText("Vacío")
        else:
            estado.setCurrentText("Ocupado")

        def actualizar_estado():
            try:
                cant = int(inquilinos.text())
            except ValueError:
                cant = 0
            if cant == 0:
                estado.setCurrentText("Vacío")
            elif cant > 0:
                estado.setCurrentText("Ocupado")

        inquilinos.textChanged.connect(actualizar_estado)

        # Servicios
        group_serv = QFrame()
        group_serv.setStyleSheet("""
            QFrame {
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                margin: 14px 0 14px 0;
                padding: 12px 10px 10px 10px;
            }
        """)
        serv_layout = QHBoxLayout(group_serv)
        serv_layout.setSpacing(18)
        servicios = {}
        for srv in ["Luz", "Agua", "Gas", "Internet"]:
            cb = QCheckBox(srv)
            cb.setChecked(True)
            servicios[srv] = cb
            serv_layout.addWidget(cb)
        layout.addWidget(QLabel("🔌 Servicios incluidos:"))
        layout.addWidget(group_serv)

        telefono = QLineEdit()
        telefono.setPlaceholderText("📞 Teléfono del inquilino")
        foto_btn = QPushButton("📷 Cambiar Imagen")

        # Variable local para la imagen seleccionada
        imagen_seleccionada = [apto["imagen"] if apto and "imagen" in apto else "Assets/departamento.jpg"]

        def seleccionar_imagen():
            ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Images (*.png *.jpg *.jpeg)")
            if ruta:
                imagen_seleccionada[0] = ruta

        foto_btn.clicked.connect(seleccionar_imagen)

        for widget in [QLabel("🏷️ Nombre"), nombre, QLabel("📍 Dirección"), direccion,
                       QLabel("👤 Cant. Inquilinos"), inquilinos, QLabel("📶 Estado"), estado,
                       telefono, foto_btn]:
            layout.addWidget(widget)

        guardar_btn = QPushButton("💾 Guardar")
        guardar_btn.clicked.connect(lambda: dialog.accept())
        layout.addWidget(guardar_btn)

        if dialog.exec_() == QDialog.Accepted:
            nuevo = {
                "nombre": nombre.text(),
                "direccion": direccion.text(),
                "estado": estado.currentText(),
                "inquilinos": int(inquilinos.text()),
                "imagen": imagen_seleccionada[0]
            }
            if editar:
                self.apartamentos[self.apartamentos.index(apto)] = nuevo
            else:
                self.apartamentos.append(nuevo)
            self.mostrar_apartamentos()
