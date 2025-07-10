class Usuario:
    def __init__(self, id_usuario: int, rol: str):
        self.id_usuario = id_usuario
        self.rol = rol  # "admin" o "inquilino"

    def es_admin(self):
        return self.rol == "admin"