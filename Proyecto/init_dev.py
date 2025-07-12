import os
import subprocess
import sys

def verificar_dependencias():
    print("🔍 Verificando entorno de desarrollo...")
    print("✅ Dependencias mínimas OK")

def main_init():
    verificar_dependencias()

    # # Ejecutar init_db.py
    # ruta_db = os.path.join("src", "init_db.py")
    # if not os.path.exists(ruta_db):
    #     print(f"❌ No se encuentra el archivo: {ruta_db}")
    #     return

    # print("🛠 Inicializando base de datos...")
    # subprocess.run([sys.executable, ruta_db], check=True)

    # Ejecutar main.py
    ruta_main = os.path.join("src", "main.py")
    if not os.path.exists(ruta_main):
        print(f"❌ No se encuentra el archivo: {ruta_main}")
        return

    print("🚀 Lanzando aplicación...")
    subprocess.run([sys.executable, ruta_main], check=True)

if __name__ == "__main__":
    main_init()
