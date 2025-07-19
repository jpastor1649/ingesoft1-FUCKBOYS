import subprocess
import os
import mysql.connector

class DataBaseManager:
    def __init__(self):
        """
        Clase para gestionar la creación y verificación de la base de datos.
        """
        self.DB_NAME = "apartamentos"
        self.DB_USER = "root"
        self.DB_PASSWORD = "proyecto123"
        self.SCRIPT_DIR = "src/db/SQL"
        self.SCRIPTS = [
            "script CREATE DATABASE.sql",
            "script STACK_PROCEDURES.sql",
            "script TRIGGERS.sql",
            "script DATA INSERTION.sql"
        ]
        self.MYSQL_CMD = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" 

    def verificar_db_existe(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user=self.DB_USER,
                password=self.DB_PASSWORD
            )
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES LIKE %s", (self.DB_NAME,))
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            return resultado is not None
        except mysql.connector.Error as err:
            print(f"❌ Error de conexión: {err}")
            return False

    def crear_base_de_datos(self):
        print("🛠 Creando base de datos...")
        try:
            subprocess.run([
                self.MYSQL_CMD,
                f"-u{self.DB_USER}",
                f"-p{self.DB_PASSWORD}",
                "-e", f"CREATE DATABASE IF NOT EXISTS {self.DB_NAME};"
            ], check=True)
            print(f"✅ Base de datos '{self.DB_NAME}' lista.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creando base: {e}")

    def ejecutar_scripts(self):
        for script_name in self.SCRIPTS:
            script_path = os.path.join(self.SCRIPT_DIR, script_name)
            print(f"📄 Ejecutando: {script_path}")
            try:
                subprocess.run([
                    self.MYSQL_CMD,
                    f"-u{self.DB_USER}",
                    f"-p{self.DB_PASSWORD}",
                    self.DB_NAME,
                    "-e", f"source {script_path}"
                ], check=True)
                print(f"✅ Ejecutado: {script_name}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error en {script_name}: {e}")

    def check(self):
        """        Verifica si la base de datos existe, si no, la crea y ejecuta los scripts necesarios.
        """
        db_manager = DataBaseManager()
        if not db_manager.verificar_db_existe():
            db_manager.crear_base_de_datos()
            db_manager.ejecutar_scripts()
        else:
            print("✅ La base de datos ya existe.")
