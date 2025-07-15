from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QSizePolicy, QGraphicsOpacityEffect,
    QDialog, QLineEdit, QScrollArea, QGridLayout, QMessageBox, QMenu, QAction, QComboBox, QFileDialog
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSlot, QSize, QDate
from PyQt5.QtGui import QFont, QIcon, QPixmap
import sys


class TarjetaInquilino(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setFixedSize(340, 500)
        self.setStyleSheet("""
            background-color: white;
            border-radius: 16px;
        """)

        # Sin sombra para evitar errores de QPainter

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        pixmap = QPixmap(data.get("imagen", "Assets/Defaultperson.jpg"))
        if pixmap.isNull():
            pixmap = QPixmap("Assets/Defaultperson.jpg")
        # Formato más vertical: ancho 120, alto 180
        pixmap = pixmap.scaled(120, 180, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        imagen_label = QLabel()
        imagen_label.setPixmap(pixmap)
        imagen_label.setFixedSize(120, 180)
        imagen_label.setStyleSheet("border-radius: 8px; margin-bottom: 8px;")
        layout.addWidget(imagen_label, alignment=Qt.AlignHCenter)

        nombre = QLabel(f"{data['nombre']} ({data['edad']} años)")
        nombre.setFont(QFont("Segoe UI", 12, QFont.Bold))
        cedula = QLabel(f"🪪 {data['cedula']}")
        celular = QLabel(f"📞 {data['celular']}")
        integrantes = QLabel(f"👥 {data['integrantes']} integrantes")
        arriendo = QLabel(f"💲{data['valor_arriendo']} / mes")
        apto = QLabel(f"🏠 {data['apartamento']}")

        for w in [nombre, cedula, celular, integrantes, arriendo, apto]:
            w.setStyleSheet("color: #1F2937; font-size: 15px;")
            layout.addWidget(w)

        self.opciones_btn = QPushButton()
        self.opciones_btn.setIcon(QIcon("Assets/Iconos/exportarpdf.png"))  # Usa un ícono de menú vertical llamativo
        self.opciones_btn.setIconSize(QSize(32, 32))
        self.opciones_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #E0E7EF;
                border-radius: 8px;
            }
        """)
        self.opciones_btn.setFixedSize(40, 40)
        self.opciones_btn.setCursor(Qt.PointingHandCursor)
        self.opciones_btn.clicked.connect(self.mostrar_menu)
        layout.addWidget(self.opciones_btn, alignment=Qt.AlignRight)

    def mostrar_menu(self, pos=None):
        # Quitar temporalmente el efecto de sombra para evitar errores de QPainter
        efecto = self.graphicsEffect()
        if efecto:
            self.setGraphicsEffect(None)

        menu = QMenu()
        mostrar = QAction("Mostrar información", self)
        editar = QAction("Editar", self)
        eliminar = QAction("Eliminar", self)

        mostrar.triggered.connect(self.mostrar_info)
        editar.triggered.connect(self.editar_info)
        eliminar.triggered.connect(self.eliminar)

        menu.addAction(mostrar)
        menu.addAction(editar)
        menu.addAction(eliminar)

        from PyQt5.QtCore import QPoint
        if isinstance(pos, QPoint):
            menu.exec_(self.opciones_btn.mapToGlobal(pos))
        else:
            menu.exec_(self.opciones_btn.mapToGlobal(self.opciones_btn.rect().bottomRight()))

        # Restaurar el efecto de sombra después de mostrar el menú
        if efecto:
            self.setGraphicsEffect(efecto)

    def editar_info(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Inquilino")
        dialog.setMinimumWidth(540)
        dialog.setMinimumHeight(600)

        from PyQt5.QtWidgets import QScrollArea
        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        dialog.setStyleSheet("""
            QDialog {
                background: #F8FAFC;
                border-radius: 18px;
            }
            QLabel[title='true'] {
                font-size: 20px;
                font-weight: bold;
                color: #1F2937;
                margin-bottom: 12px;
            }
            QLineEdit {
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
                padding: 8px 0;
                font-size: 15px;
                min-width: 100px;
            }
            QPushButton#cancelar {
                background: #E5E7EB;
                color: #1F2937;
            }
            QPushButton#imagen {
                background: #F1F5F9;
                color: #2563EB;
                border: 1px solid #2563EB;
                font-size: 14px;
                min-width: 120px;
            }
        """)
        scroll.setWidget(content)
        main_layout = QVBoxLayout(dialog)
        main_layout.addWidget(scroll)

        titulo = QLabel("Editar inquilino")
        titulo.setProperty('title', True)
        layout.addWidget(titulo, alignment=Qt.AlignHCenter)

        nombre = QLineEdit(self.data["nombre"]); nombre.setPlaceholderText("Nombre")
        edad = QLineEdit(str(self.data["edad"])); edad.setPlaceholderText("Edad")
        cedula = QLineEdit(self.data["cedula"]); cedula.setPlaceholderText("Cédula")
        celular = QLineEdit(self.data["celular"]); celular.setPlaceholderText("Celular")
        apartamento = QLineEdit(self.data["apartamento"]); apartamento.setPlaceholderText("Apartamento")
        integrantes = QLineEdit(str(self.data["integrantes"])); integrantes.setPlaceholderText("Integrantes")
        arriendo = QLineEdit(str(self.data["valor_arriendo"])); arriendo.setPlaceholderText("Valor del arriendo")
        direccion = QLineEdit(self.data.get("direccion", "")); direccion.setPlaceholderText("Dirección")

        # Servicios compartidos con QCheckBox
        from PyQt5.QtWidgets import QGroupBox, QGridLayout, QCheckBox
        servicios = ["Agua", "Luz", "Gas", "Internet", "TV", "Teléfono"]
        recibos_existentes = [s.strip() for s in self.data.get("recibos", "").split(",") if s.strip()]
        group_serv = QGroupBox("Servicios compartidos:")
        group_serv.setStyleSheet("""
            QGroupBox {
                font-size:15px;
                color:#2563EB;
                margin:14px 0 14px 0;
                padding: 12px 10px 10px 10px;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
            }
        """)
        serv_layout = QGridLayout(group_serv)
        checkboxes = []
        for idx, s in enumerate(servicios):
            cb = QCheckBox(s)
            cb.setChecked(s in recibos_existentes)
            row = idx // 3
            col = idx % 3
            serv_layout.addWidget(cb, row, col)
            checkboxes.append(cb)

        imagen_input = QLineEdit(self.data.get("imagen", "")); imagen_input.setPlaceholderText("Ruta imagen")
        boton_imagen = QPushButton("Seleccionar imagen"); boton_imagen.setObjectName("imagen")
        def seleccionar_imagen():
            ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Imagenes (*.png *.jpg *.jpeg)")
            if ruta:
                imagen_input.setText(ruta)
        boton_imagen.clicked.connect(seleccionar_imagen)

        for campo in [nombre, edad, cedula, celular, apartamento, integrantes, arriendo, direccion, imagen_input]:
            layout.addWidget(campo)
        layout.addWidget(boton_imagen, alignment=Qt.AlignLeft)
        layout.addWidget(group_serv)

        botones = QHBoxLayout()
        guardar = QPushButton("Guardar")
        cancelar = QPushButton("Cancelar"); cancelar.setObjectName("cancelar")
        botones.addWidget(guardar)
        botones.addWidget(cancelar)
        layout.addLayout(botones)

        cancelar.clicked.connect(dialog.reject)
        def guardar_cambios():
            try:
                servicios_seleccionados = [cb.text() for cb in checkboxes if cb.isChecked()]
                self.data.update({
                    "nombre": nombre.text(),
                    "edad": int(edad.text()),
                    "cedula": cedula.text(),
                    "celular": celular.text(),
                    "apartamento": apartamento.text(),
                    "integrantes": int(integrantes.text()),
                    "valor_arriendo": int(arriendo.text()),
                    "direccion": direccion.text(),
                    "recibos": ", ".join(servicios_seleccionados),
                    "imagen": imagen_input.text() or "Assets/Defaultperson.jpg"
                })
                parent = self.parent()
                while parent is not None and not hasattr(parent, 'cargar_tarjetas'):
                    parent = parent.parent()
                if parent is not None:
                    parent.cargar_tarjetas()
                dialog.accept()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Datos inválidos: {e}")
        guardar.clicked.connect(guardar_cambios)

        dialog.exec_()

    def mostrar_info(self):
        info = f"""
        <div style='background:#F8FAFC; border-radius:14px; padding:12px 6px; font-size:16px;'>
            <div style='font-size:22px; font-weight:bold; color:#2563EB; margin-bottom:8px;'>👤 {self.data['nombre']}</div>
            <div>🎂 <b>Edad:</b> {self.data['edad']} años</div>
            <div>🪪 <b>Cédula:</b> {self.data['cedula']}</div>
            <div>📞 <b>Celular:</b> {self.data['celular']}</div>
            <div>🏠 <b>Apartamento:</b> {self.data['apartamento']}</div>
            <div>👥 <b>Integrantes:</b> {self.data['integrantes']}</div>
            <div>💲 <b>Arriendo:</b> ${self.data['valor_arriendo']:,} / mes</div>
            <div>📍 <b>Dirección:</b> {self.data.get('direccion', 'No especificada')}</div>
            <div>🧾 <b>Recibos compartidos:</b> {self.data.get('recibos', 'Ninguno')}</div>
        </div>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Información del inquilino")
        msg.setTextFormat(Qt.RichText)
        msg.setText(info)
        msg.setStyleSheet("QLabel{min-width:340px;}")
        msg.exec_()

        def editar_info(self):
            dialog = QDialog(self)
            dialog.setWindowTitle("Editar Inquilino")
            layout = QVBoxLayout(dialog)

            nombre = QLineEdit(self.data["nombre"])
            edad = QLineEdit(str(self.data["edad"]))
            cedula = QLineEdit(self.data["cedula"])
            celular = QLineEdit(self.data["celular"])
            apartamento = QLineEdit(self.data["apartamento"])
            integrantes = QLineEdit(str(self.data["integrantes"]))
            arriendo = QLineEdit(str(self.data["valor_arriendo"]))
            direccion = QLineEdit(self.data.get("direccion", ""))
            recibos = QLineEdit(self.data.get("recibos", ""))

            imagen_input = QLineEdit(self.data.get("imagen", ""))
            boton_imagen = QPushButton("Seleccionar imagen")
            def seleccionar_imagen():
                ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Imagenes (*.png *.jpg *.jpeg)")
                if ruta:
                    imagen_input.setText(ruta)
            boton_imagen.clicked.connect(seleccionar_imagen)

            for campo in [nombre, edad, cedula, celular, apartamento, integrantes, arriendo, direccion, recibos, imagen_input, boton_imagen]:
                layout.addWidget(campo)

            botones = QHBoxLayout()
            guardar = QPushButton("Guardar")
            cancelar = QPushButton("Cancelar")
            botones.addWidget(guardar)
            botones.addWidget(cancelar)
            layout.addLayout(botones)

            cancelar.clicked.connect(dialog.reject)
            def guardar_cambios():
                try:
                    self.data.update({
                        "nombre": nombre.text(),
                        "edad": int(edad.text()),
                        "cedula": cedula.text(),
                        "celular": celular.text(),
                        "apartamento": apartamento.text(),
                        "integrantes": int(integrantes.text()),
                        "valor_arriendo": int(arriendo.text()),
                        "direccion": direccion.text(),
                        "recibos": recibos.text(),
                        "imagen": imagen_input.text() or "Assets/Defaultperson.jpg"
                    })
                    self.parent().parent().parent().cargar_tarjetas()  # refrescar desde GestionInquilinos
                    dialog.accept()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Datos inválidos: {e}")
            guardar.clicked.connect(guardar_cambios)

            dialog.exec_()

    
    def eliminar(self):
        self.hide()


class GestionInquilinos(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Inquilinos")
        self.setMinimumSize(1000, 700)

        self.lista_inquilinos = [
            {
                "nombre": "Laura Gómez", "edad": 32, "cedula": "123456789",
                "celular": "3004567890", "integrantes": 3, "valor_arriendo": 850000,
                "apartamento": "Torre 1 - 304", "direccion": "Cra 15 #45-21", "recibos": "Agua, Luz",
                "imagen": "Assets/Defaultperson.jpg"
            },
            {
                "nombre": "Mario Rodríguez", "edad": 45, "cedula": "987654321",
                "celular": "3109876543", "integrantes": 2, "valor_arriendo": 790000,
                "apartamento": "Torre 2 - 101", "direccion": "Cll 12 #34-56", "recibos": "Gas, Internet"
            }
        ]

        layout = QVBoxLayout(self)
        # Fondo claro sin borde
        self.setStyleSheet("background: #F3F6FA;")

        # Barra superior
        top_bar = QHBoxLayout()
        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText("Buscar inquilino...")
        self.busqueda.textChanged.connect(self.filtrar_inquilinos)
        btn_agregar = QPushButton("+ Agregar inquilino")
        btn_agregar.clicked.connect(self.abrir_formulario)
        top_bar.addWidget(self.busqueda)
        top_bar.addWidget(btn_agregar)
        layout.addLayout(top_bar)

        # Área scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.widget = QWidget()
        self.grid = QGridLayout(self.widget)
        self.scroll.setWidget(self.widget)
        layout.addWidget(self.scroll)

        self.cargar_tarjetas()

    def cargar_tarjetas(self):
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        self.tarjetas = []
        for i, data in enumerate(self.lista_inquilinos):
            tarjeta = TarjetaInquilino(data)
            self.grid.addWidget(tarjeta, i // 3, i % 3)
            self.tarjetas.append(tarjeta)

    def filtrar_inquilinos(self):
        texto = self.busqueda.text().lower()
        for tarjeta in self.tarjetas:
            nombre = tarjeta.data["nombre"].lower()
            tarjeta.setVisible(texto in nombre)

    def abrir_formulario(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuevo Inquilino")
        dialog.setMinimumWidth(540)
        dialog.setMinimumHeight(600)

        from PyQt5.QtWidgets import QScrollArea
        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        dialog.setStyleSheet("""
            QDialog {
                background: #F8FAFC;
                border-radius: 18px;
            }
            QLabel[title='true'] {
                font-size: 20px;
                font-weight: bold;
                color: #1F2937;
                margin-bottom: 12px;
            }
            QLineEdit {
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
                padding: 8px 0;
                font-size: 15px;
                min-width: 100px;
            }
            QPushButton#cancelar {
                background: #E5E7EB;
                color: #1F2937;
            }
            QPushButton#imagen {
                background: #F1F5F9;
                color: #2563EB;
                border: 1px solid #2563EB;
                font-size: 14px;
                min-width: 120px;
            }
        """)
        scroll.setWidget(content)
        main_layout = QVBoxLayout(dialog)
        main_layout.addWidget(scroll)

        titulo = QLabel("Nuevo inquilino")
        titulo.setProperty('title', True)
        layout.addWidget(titulo, alignment=Qt.AlignHCenter)

        nombre = QLineEdit(); nombre.setPlaceholderText("Nombre")
        edad = QLineEdit(); edad.setPlaceholderText("Edad")
        cedula = QLineEdit(); cedula.setPlaceholderText("Cédula")
        celular = QLineEdit(); celular.setPlaceholderText("Celular")
        integrantes = QLineEdit(); integrantes.setPlaceholderText("Integrantes")
        arriendo = QLineEdit(); arriendo.setPlaceholderText("Valor del arriendo")
        apto = QLineEdit(); apto.setPlaceholderText("Apartamento")
        direccion = QLineEdit(); direccion.setPlaceholderText("Dirección")

        from PyQt5.QtWidgets import QGroupBox, QGridLayout, QCheckBox
        servicios = ["Agua", "Luz", "Gas", "Internet", "TV", "Teléfono"]
        group_serv = QGroupBox("Servicios compartidos:")
        group_serv.setStyleSheet("""
            QGroupBox {
                font-size:15px;
                color:#2563EB;
                margin:14px 0 14px 0;
                padding: 12px 10px 10px 10px;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
            }
        """)
        serv_layout = QGridLayout(group_serv)
        checkboxes = []
        for idx, s in enumerate(servicios):
            cb = QCheckBox(s)
            row = idx // 3
            col = idx % 3
            serv_layout.addWidget(cb, row, col)
            checkboxes.append(cb)

        imagen = QLineEdit(); imagen.setPlaceholderText("Ruta imagen")
        buscar_img = QPushButton("Seleccionar imagen"); buscar_img.setObjectName("imagen")
        buscar_img.clicked.connect(lambda: self.seleccionar_imagen(imagen))

        for w in [nombre, edad, cedula, celular, integrantes, arriendo, apto, direccion, imagen]:
            layout.addWidget(w)
        layout.addWidget(buscar_img, alignment=Qt.AlignLeft)
        layout.addWidget(group_serv)

        btns = QHBoxLayout()
        guardar = QPushButton("Guardar")
        cancelar = QPushButton("Cancelar"); cancelar.setObjectName("cancelar")
        guardar.clicked.connect(lambda: self.guardar_inquilino(dialog, nombre, edad, cedula, celular, integrantes, arriendo, apto, direccion, checkboxes, imagen))
        cancelar.clicked.connect(dialog.reject)
        btns.addWidget(guardar)
        btns.addWidget(cancelar)
        layout.addLayout(btns)
        dialog.exec_()

    def seleccionar_imagen(self, campo):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg)")
        if ruta:
            campo.setText(ruta)

    def guardar_inquilino(self, dialog, nombre, edad, cedula, celular, integrantes, arriendo, apto, direccion, checkboxes, imagen):
        try:
            servicios_seleccionados = [cb.text() for cb in checkboxes if cb.isChecked()]
            nuevo = {
                "nombre": nombre.text(), "edad": int(edad.text()), "cedula": cedula.text(),
                "celular": celular.text(), "integrantes": int(integrantes.text()),
                "valor_arriendo": int(arriendo.text()), "apartamento": apto.text(),
                "direccion": direccion.text(), "recibos": ", ".join(servicios_seleccionados),
                "imagen": imagen.text() or "Assets/Defaultperson.jpg"
            }
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Datos inválidos: {e}")
            return
        self.lista_inquilinos.append(nuevo)
        self.cargar_tarjetas()
        dialog.accept()

