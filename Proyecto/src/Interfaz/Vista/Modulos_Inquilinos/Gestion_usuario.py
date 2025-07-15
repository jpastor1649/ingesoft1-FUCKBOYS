from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QFrame, QMessageBox, QSizePolicy, QSpacerItem
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class GestionUsuario(QWidget):
    def __init__(self, datos_usuario=None, parent=None):
        super().__init__(parent)

        self.datos_usuario = datos_usuario or {
            "nombre": "Juan Pérez",
            "edad": "30",
            "contacto": "juan.perez@email.com",
            "rol": "Inquilino",
            "permisos": "Lectura/Actualización",
            "inicio_arriendo": "01/01/2024",
            "valor_mensual": "$1.000.000",
            "estado_pago": "Pagado"
        }

        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F9FAFB;
            }
            QLabel#titulo {
                color: #1F2937;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel#subtitulo {
                color: #4B5563;
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 14px;
            }
            QLabel[data="label"] {
                color: #374151;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2563EB;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
            QPushButton#eliminar {
                background-color: #DC2626;
            }
            QPushButton#eliminar:hover {
                background-color: #991B1B;
            }
            QFrame#linea {
                background-color: #D1D5DB;
                height: 1px;
            }
        """)

        # Layout principal centrado
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignTop)

        # Título
        titulo = QLabel("👤 Gestión de Usuario")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        # Subtítulo (opcional)
        subtitulo = QLabel("Edita tu perfil y visualiza tu estado actual")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitulo)

        # Formulario
        form_box = QWidget()
        form_layout = QFormLayout(form_box)
        form_layout.setSpacing(12)

        def build_label(text):
            lbl = QLabel(text)
            lbl.setProperty("data", "label")
            return lbl

        self.input_nombre = QLineEdit(self.datos_usuario["nombre"])
        self.input_edad = QLineEdit(self.datos_usuario["edad"])
        self.input_contacto = QLineEdit(self.datos_usuario["contacto"])
        form_layout.addRow(build_label("Nombre:"), self.input_nombre)
        form_layout.addRow(build_label("Edad:"), self.input_edad)
        form_layout.addRow(build_label("Contacto:"), self.input_contacto)

        # Rol y permisos
        self.rol_lbl = build_label(self.datos_usuario["rol"])
        self.permisos_lbl = build_label(self.datos_usuario["permisos"])
        self.rol_lbl.setStyleSheet("font-weight: bold;")
        form_layout.addRow(build_label("Rol:"), self.rol_lbl)
        form_layout.addRow(build_label("Permisos:"), self.permisos_lbl)

        main_layout.addWidget(form_box)

        # Línea divisoria
        linea = QFrame()
        linea.setObjectName("linea")
        linea.setFrameShape(QFrame.HLine)
        linea.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(linea)

        # Sección de arriendo
        arriendo_label = QLabel("📄 Información del Arriendo")
        arriendo_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        arriendo_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(arriendo_label)

        self.inicio_lbl = build_label(f"Fecha de inicio: {self.datos_usuario['inicio_arriendo']}")
        self.valor_lbl = build_label(f"Valor mensual: {self.datos_usuario['valor_mensual']}")
        self.estado_lbl = build_label(f"Estado de pago: {self.datos_usuario['estado_pago']}")
        for lbl in [self.inicio_lbl, self.valor_lbl, self.estado_lbl]:
            main_layout.addWidget(lbl)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_guardar = QPushButton("Actualizar perfil")
        self.btn_guardar.clicked.connect(self.actualizar_perfil)

        self.btn_cambiar_pass = QPushButton("Cambiar contraseña")

        self.btn_cerrar_sesion = QPushButton("Eliminar cuenta")
        self.btn_cerrar_sesion.setObjectName("eliminar")

        btn_row.addWidget(self.btn_guardar)
        btn_row.addWidget(self.btn_cambiar_pass)
        btn_row.addWidget(self.btn_cerrar_sesion)

        main_layout.addLayout(btn_row)

        # Espaciador inferior
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def actualizar_perfil(self):
        nombre = self.input_nombre.text().strip()
        edad = self.input_edad.text().strip()
        contacto = self.input_contacto.text().strip()

        if not nombre or not edad or not contacto:
            QMessageBox.warning(self, "Error", "Todos los campos deben estar llenos.")
            return

        QMessageBox.information(self, "Éxito", "Perfil actualizado correctamente.")