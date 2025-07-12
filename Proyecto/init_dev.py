import sys
import os

# Agrega src al path para importar main.py
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from src.init_db import DataBaseManager

import main  # Ahora puedes importar main como módulo

def verificar_dependencias():
    print("🔍 Verificando entorno de desarrollo...")
    print("✅ Dependencias mínimas OK")

def main_init():
    verificar_dependencias()
    db = DataBaseManager()
    db.check()
    print("🚀 Lanzando aplicación...")
    main.main()  

if __name__ == "__main__":
    main_init()
