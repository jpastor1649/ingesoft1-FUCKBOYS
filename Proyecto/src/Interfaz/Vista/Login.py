# Importación de clases necesarias de PyQt5
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QFont, QMovie
from PyQt5.QtCore import Qt

from design.uiQT import estilo_input, button_style, estilo_card, AnimatedToggle


# Definición de la clase LoginWindow que hereda de QWidget
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        # CONFIGURACIÓN DE LA VENTANA PRINCIPAL
        self.setWindowTitle("Login")              
        self.setMinimumSize(960, 600)             
        self.setStyleSheet("background-color: #F8F9FA;")  

        # LAYOUT PRINCIPAL HORIZONTAL
        self.main_layout = QHBoxLayout(self)   

        # SECCIÓN: BANNER ANIMADO (GIF)
        self.banner = QLabel()                    
        self.banner.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        self.banner.setScaledContents(True)       
        self.movie = QMovie("Assets/persona jugando.gif")  
        self.banner.setMovie(self.movie)          
        self.movie.start()                      

        # SECCIÓN: CONTENEDOR DEL FORMULARIO
        self.form_frame = QFrame()                
        self.form_frame.setFixedWidth(400)        
        self.form_frame.setStyleSheet(estilo_card())  

        # Layout vertical para organizar los elementos del formulario
        form_layout = QVBoxLayout(self.form_frame)
        form_layout.setContentsMargins(30, 40, 30, 30)  
        form_layout.setSpacing(20)                   

        # LOGO O TÍTULO SUPERIOR
        self.logo = QLabel("LOGO")                      
        self.logo.setAlignment(Qt.AlignCenter)         
        self.logo.setFont(QFont("Segoe UI", 18, QFont.Bold))  

        # CAMPO DE TEXTO: USUARIO
        user = QLineEdit()
        user.setPlaceholderText("Correo o Usuario")     

        # CAMPO DE TEXTO: CONTRASEÑA
        password = QLineEdit()
        password.setPlaceholderText("Contraseña")      
        password.setEchoMode(QLineEdit.Password)        

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

        # BOTÓN DE INGRESO
        login_btn = QPushButton("Ingresar")             #
        login_btn.clicked.connect(self.iniciar_sesion)

        # BOTÓN PARA REGISTRARSE
        go_register = QPushButton("¿No tienes cuenta? Regístrate")
        go_register.setFlat(True)
        go_register.setStyleSheet("color: #4A90E2; text-decoration: underline; background-color: transparent;")
        go_register.clicked.connect(self.mostrar_register)

        # APLICACIÓN DE FUENTE A TODOS LOS ELEMENTOS DEL FORMULARIO
        for widget in [user, password, login_btn, go_register]:
            widget.setFont(QFont("Segoe UI", 11))

        # APLICACIÓN DE ESTILOS PERSONALIZADOS
        user.setStyleSheet(estilo_input())              
        password.setStyleSheet(estilo_input())         
        login_btn.setStyleSheet(button_style("#4A90E2", "#3A78C2"))  # Estilo del botón de login

        # AGREGADO DE WIDGETS AL FORMULARIO
        form_layout.addWidget(self.logo)             
        form_layout.addWidget(user)                    
        form_layout.addWidget(password)                 
        form_layout.addLayout(role_switch_layout)       
        form_layout.addStretch()                       
        form_layout.addWidget(login_btn)                
        form_layout.addWidget(go_register)              

        # AGREGADO DE LOS ELEMENTOS AL LAYOUT PRINCIPAL DE LA VENTANA
        self.main_layout.addWidget(self.banner)         
        self.main_layout.addWidget(self.form_frame)     

    def mostrar_register(self):
        from Vista.Register import RegisterWindow 
        self.registro = RegisterWindow()
        self.registro.show()
        self.close()


    def actualizar_rol_texto(self):
        if self.role_switch.isChecked():
            self.role_label.setText("Soy arrendador")
        else:
            self.role_label.setText("Soy arrendatario")

    def iniciar_sesion(self):
        if self.role_switch.isChecked():
            # Si es arrendador, ir a Admin
            from Vista.Inquilino import PanelInquilino
            self.admin = PanelInquilino()
            self.admin.showMaximized()
            self.close()
        else:
            from Vista.Admin import PanelAdmin
            self.admin = PanelAdmin()
            self.admin.showMaximized()
            self.close()
