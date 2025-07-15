# Importación de clases necesarias de PyQt5
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QFont, QMovie
from PyQt5.QtCore import Qt

# Importación de estilos personalizados desde el módulo 'Diseño.uiQT'
from design.uiQT import estilo_input, button_style, estilo_card, AnimatedToggle


# Definición de la clase RegisterWindow que hereda de QWidget
class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Registro")
        self.setMinimumSize(960, 600)
        self.setStyleSheet("background-color: #F8F9FA;")

        self.main_layout = QHBoxLayout(self)

        self.banner = QLabel()
        self.banner.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.banner.setScaledContents(True)
        self.movie = QMovie("Assets/persona jugando.gif")
        self.banner.setMovie(self.movie)
        self.movie.start()

        self.form_frame = QFrame()
        self.form_frame.setFixedWidth(400)
        self.form_frame.setStyleSheet(estilo_card())

        form_layout = QVBoxLayout(self.form_frame)
        form_layout.setContentsMargins(30, 40, 30, 30)
        form_layout.setSpacing(20)

        self.logo = QLabel("LOGO")
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setFont(QFont("Segoe UI", 18, QFont.Bold))

        name = QLineEdit()
        name.setPlaceholderText("Nombre completo")

        email = QLineEdit()
        email.setPlaceholderText("Correo electrónico")

        password = QLineEdit()
        password.setPlaceholderText("Contraseña")
        password.setEchoMode(QLineEdit.Password)

        confirm = QLineEdit()
        confirm.setPlaceholderText("Confirmar contraseña")
        confirm.setEchoMode(QLineEdit.Password)

        # SWITCH ANIMADO PARA ROL DE USUARIO
        role_switch_layout = QHBoxLayout()
        self.role_switch = AnimatedToggle()
        self.role_label = QLabel("Soy arrendatario")
        self.role_label.setFont(QFont("Segoe UI", 11))
        self.role_label.setStyleSheet("color: #333;")
        self.role_switch.stateChanged.connect(self.actualizar_rol_texto)
        role_switch_layout.addWidget(self.role_switch)
        role_switch_layout.addWidget(self.role_label)
        role_switch_layout.addStretch()

        register_btn = QPushButton("Registrarse")

        go_login = QPushButton("¿Ya tienes cuenta? Inicia sesión")
        go_login.setFlat(True)
        go_login.setStyleSheet("color: #4A90E2; text-decoration: underline; background-color: transparent;")
        go_login.clicked.connect(self.mostrar_login)

        for widget in [name, email, password, confirm, register_btn, go_login]:
            widget.setFont(QFont("Segoe UI", 11))

        name.setStyleSheet(estilo_input())
        email.setStyleSheet(estilo_input())
        password.setStyleSheet(estilo_input())
        confirm.setStyleSheet(estilo_input())
        register_btn.setStyleSheet(button_style("#4A90E2", "#3A78C2"))

        form_layout.addWidget(self.logo)
        form_layout.addWidget(name)
        form_layout.addWidget(email)
        form_layout.addWidget(password)
        form_layout.addWidget(confirm)
        form_layout.addLayout(role_switch_layout)
        form_layout.addStretch()
        form_layout.addWidget(register_btn)
        form_layout.addWidget(go_login)

        self.main_layout.addWidget(self.banner)
        self.main_layout.addWidget(self.form_frame)

    def mostrar_login(self):
        from Vista.Login import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()


    def actualizar_rol_texto(self):
        if self.role_switch.isChecked():
            self.role_label.setText("Soy arrendador")
        else:
            self.role_label.setText("Soy arrendatario")
