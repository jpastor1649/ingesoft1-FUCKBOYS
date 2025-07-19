import subprocess
import os
import mysql.connector


class DataBaseManager:
    """Clase para gestionar la creación y verificación de la base de datos."""

    def __init__(self):
        """
        Clase para gestionar la creación y verificación de la base de datos.
        """
        self.db_name = "apartamentos"
        self.db_user = "root"
        self.db_password = "proyecto123"
        self.script_dir = "src/db/SQL"
        self.scripts = [
            "script CREATE DATABASE.sql",
            "script STACK_PROCEDURES.sql",
            "script TRIGGERS.sql",
            "script DATA INSERTION.sql",
        ]
        self.mysql_cmd = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

    def verificar_db_existe(self):
        """Verifica si la base de datos ya existe"""
        try:
            conn = mysql.connector.connect(
                host="localhost", user=self.db_user, password=self.db_password
            )
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES LIKE %s", (self.db_name,))
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            return resultado is not None
        except mysql.connector.Error as err:
            print(f"❌ Error de conexión: {err}")
            return False

    def crear_base_de_datos(self):
        """Crea la base de datos y ejecuta los scripts necesarios."""
        print("🛠 Creando base de datos...")
        try:
            subprocess.run(
                [
                    self.mysql_cmd,
                    f"-u{self.db_user}",
                    f"-p{self.db_password}",
                    "-e",
                    f"CREATE DATABASE IF NOT EXISTS {self.db_name};",
                ],
                check=True,
            )
            print(f"✅ Base de datos '{self.db_name}' lista.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creando base: {e}")

    def ejecutar_scripts(self):
        """Ejecuta los scripts SQL necesarios para inicializar la base de datos."""
        for script_name in self.scripts:
            script_path = os.path.join(self.script_dir, script_name)
            print(f"📄 Ejecutando: {script_path}")
            try:
                subprocess.run(
                    [
                        self.mysql_cmd,
                        f"-u{self.db_user}",
                        f"-p{self.db_password}",
                        self.db_name,
                        "-e",
                        f"source {script_path}",
                    ],
                    check=True,
                )
                print(f"✅ Ejecutado: {script_name}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error en {script_name}: {e}")

    def check(self):
        """Verifica si la base de datos existe, si no, la crea y ejecuta los scripts necesarios."""
        db_manager = DataBaseManager()
        if not db_manager.verificar_db_existe():
            db_manager.crear_base_de_datos()
            db_manager.ejecutar_scripts()
        else:
            print("✅ La base de datos ya existe.")
