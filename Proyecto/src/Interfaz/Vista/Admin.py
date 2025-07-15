from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QSizePolicy, QGraphicsOpacityEffect, QScrollArea
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSlot, QSize

from PyQt5.QtGui import QFont, QIcon, QPixmap
import sys

from Vista.Modulos.Gestion_inmueble import GestionInmueble
from Vista.Modulos.Gestion_Inquilinos import GestionInquilinos
from Vista.Modulos.Gestion_servicios import GestionServicios
from Vista.Modulos.Historial import HistorialReportesDialog
from Vista.Modulos.gestion_arriendos import ConfiguracionArriendos
from Vista.Modulos.Bienvenida import WelcomeWindow



class PanelAdmin(QMainWindow):
    def __init__(self):
        super().__init__()
        # No crear widgets de módulos aquí, solo los fijos (título y label)
        self.setWindowTitle("Panel Arrendatario")
        self.setMinimumSize(800, 600)

        # --- Widget central y layout principal ---
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QHBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Menú lateral ---
        self.menu_frame = QFrame()
        self.menu_frame.setStyleSheet("background-color: #1F2937;")
        self.menu_frame.setFixedWidth(280)
        menu_layout = QVBoxLayout(self.menu_frame)
        menu_layout.setContentsMargins(10, 10, 10, 10)
        menu_layout.setSpacing(15)

        # Logo / Título menú con imagen al lado del texto
        logo = QLabel()
        pixmap = QPixmap("Assets/3891758.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pixmap)
        logo.setStyleSheet("color: white;")
        logo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.logo_text = QLabel("Panel \nArrendatario")
        self.logo_text.setStyleSheet("color: white;")
        self.logo_text.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.logo_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        logo_row = QHBoxLayout()
        logo_row.setSpacing(8)
        logo_row.addWidget(logo)
        logo_row.addWidget(self.logo_text)
        self.logo_row_widget = QWidget()
        self.logo_row_widget.setLayout(logo_row)
        menu_layout.addWidget(self.logo_row_widget)

        self.menu_buttons = []

        # Ítems del menú con íconos
        menu_items = [
            ("Gestión Inmueble", "Assets/Iconos/Gestion_inmuebles.png"),
            ("Gestión de Inquilinos", "Assets/Iconos/Gestion_inquilinos.png"),
            ("Gestión de Servicios", "Assets/Iconos/Gestion_servicios.png"),
            ("Configuración de \n Arriendos", "Assets/Iconos/configuracion_arriendos.png"),
            ("Historial y Reportes", "Assets/Iconos/historial.png"),
        ]

        for texto, icono_path in menu_items:
            btn = QPushButton(f"  {texto}")
            btn.setIcon(QIcon(icono_path))
            btn.setIconSize(QSize(50, 50))
            btn.setMinimumHeight(48)
            btn.setStyleSheet(
                "QPushButton { color: white; background: transparent; text-align: left; padding: 16px 12px; font-size: 16px; border-radius: 8px; }"
                "QPushButton:hover { background-color: #374151; }"
            )
            btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, t=texto: self.cambiar_contenido(t))
            menu_layout.addWidget(btn)
            self.menu_buttons.append((btn, texto))

        # Botón cerrar sesión con icono
        self.cerrar_btn = QPushButton("  Cerrar sesión")
        self.cerrar_btn.setIcon(QIcon("Assets\Iconos\CERRAR.png"))  # Cambia el icono si prefieres otro
        self.cerrar_btn.setIconSize(QSize(32, 32))
        self.cerrar_btn.setFont(QFont("Segoe UI", 12))
        self.cerrar_btn.setStyleSheet(
            "QPushButton { color: #F87171; background: transparent; text-align: left; padding: 8px; }"
            "QPushButton:hover { background-color: #7F1D1D; color: white; }"
        )
        self.cerrar_btn.setCursor(Qt.PointingHandCursor)
        self.cerrar_btn.clicked.connect(self.cerrar_sesion)
        menu_layout.addWidget(self.cerrar_btn)

        # Botón ocultar/mostrar menú SIEMPRE VISIBLE
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setStyleSheet("color: #1F2937; background: #F3F4F6; font-size: 20px; border-radius: 16px; padding: 4px 10px;")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_menu)

        menu_layout.addStretch()

        # --- Área de contenido central (sin scroll) ---
        self.content_frame = QWidget()
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(10)

        # Título de sección (solo se agrega dinámicamente en la pantalla de bienvenida)
        self.section_title = QLabel("Bienvenido")
        self.section_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        # Placeholder de contenido (solo se agrega dinámicamente en la pantalla de bienvenida)
        self.content_label = QLabel("Estamos trabajando...")
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setFont(QFont("Segoe UI", 14))

        # Efecto de opacidad para animar contenido
        self.opacity_effect = QGraphicsOpacityEffect(self.content_frame)
        self.content_frame.setGraphicsEffect(self.opacity_effect)
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)

        # Agregar al layout principal
        # Contenedor vertical para botón toggle y contenido
        content_container = QVBoxLayout()
        content_container.setContentsMargins(0, 0, 0, 0)
        content_container.setSpacing(0)
        # Botón toggle arriba a la izquierda
        content_container.addWidget(self.toggle_btn, alignment=Qt.AlignLeft | Qt.AlignTop)
        content_container.addWidget(self.content_frame)
        self.main_layout.addWidget(self.menu_frame)
        self.main_layout.addLayout(content_container)
        self.cambiar_contenido("Bienvenido")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Mini mode si el ancho de la ventana es menor a 900px
        if self.width() < 900:
            self.menu_mini = True
            self.menu_frame.setFixedWidth(90)
            self.logo_text.hide()
            for btn, texto in self.menu_buttons:
                btn.setText("")
            self.cerrar_btn.setText("")
        else:
            self.menu_mini = False
            self.menu_frame.setFixedWidth(260)
            self.logo_text.show()
            for btn, texto in self.menu_buttons:
                btn.setText(f"  {texto}")
            self.cerrar_btn.setText("  Cerrar sesión")

    @pyqtSlot()
    def toggle_menu(self):
        # Animar minimumWidth y maximumWidth para ocultar/mostrar el menú correctamente
        current_width = self.menu_frame.width()
        # Determinar el ancho a mostrar según el modo mini o normal
        if hasattr(self, 'menu_mini') and self.menu_mini:
            menu_width = 90
        else:
            menu_width = 260
        new_width = 0 if current_width > 0 else menu_width

        for prop in [b"minimumWidth", b"maximumWidth"]:
            anim = QPropertyAnimation(self.menu_frame, prop)
            anim.setDuration(300)
            anim.setStartValue(current_width)
            anim.setEndValue(new_width)
            anim.setEasingCurve(QEasingCurve.InOutCubic)
            anim.start()
            # Guardar referencia para evitar recolección de basura
            if not hasattr(self, 'menu_anims'):
                self.menu_anims = []
            self.menu_anims.append(anim)
    
            
    def cambiar_contenido(self, titulo):
        # Eliminar widgets anteriores excepto section_title y content_label
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            widget = item.widget()
            if widget is not None and widget not in [self.section_title, self.content_label]:
                self.content_layout.removeWidget(widget)
                widget.setParent(None)
                widget.deleteLater()

        # Ocultar por defecto título y contenido base
        self.section_title.hide()
        self.content_label.hide()

        # Mostrar contenido según selección
        if titulo == "Bienvenido":
            widget = WelcomeWindow()
            self.content_layout.addWidget(widget)
            return

        elif titulo.startswith("Gestión Inmueble"):
            widget = GestionInmueble()
            self.content_layout.addWidget(widget)

        elif titulo.startswith("Gestión de Inquilinos"):
            widget = GestionInquilinos()
            self.content_layout.addWidget(widget)

        elif titulo.startswith("Gestión de Servicios"):
            temp_inmueble = GestionInmueble()
            apartamentos = [apto["nombre"] for apto in temp_inmueble.apartamentos]
            servicios = {"Agua": True, "Luz": True, "Gas": False, "Internet": True}
            widget = GestionServicios(servicios, apartamentos)
            self.content_layout.addWidget(widget)

        elif titulo.startswith("Historial y Reportes"):
            temp_inmueble = GestionInmueble()
            apartamentos = [apto["nombre"] for apto in temp_inmueble.apartamentos]
            widget = HistorialReportesDialog(apartamentos)
            widget.setWindowFlags(Qt.Widget)  # Forzar modo embebido en layout
            try:
                mes = widget.filter_date_lbl.text()
                rol = widget.filter_role.currentText()
                servicio = widget.filter_service.currentText()
                widget.generar_tabla(mes=mes, rol=rol, servicio=servicio)
            except Exception:
                pass
            self.content_layout.addWidget(widget)

        elif titulo.startswith("Configuración de"):
            widget = ConfiguracionArriendos()
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 🔧 Añadir esto
            self.content_layout.addWidget(widget)
        
        else:
            self.section_title.setText(titulo)
            self.section_title.show()
            self.content_layout.addWidget(self.section_title)

        # Animar fade in
        self.fade_anim.stop()
        self.fade_anim.start()


    def cerrar_sesion(self):
        from Vista.Login import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()



