import sys
sys.path.append("src")
from connector.connector import Connector
from init_db import DataBaseManager

class Usuario:
    def __init__(self, id_usuario: int, rol: str):
        self.id_usuario = id_usuario
        self.rol = rol  

    def es_admin(self):
        return self.rol == 'admin'

def seleccionar_usuario():
    print("=== Login ===")
    rol = input("Rol (admin o inquilino): ").strip().lower()
    if rol not in ("admin", "inquilino"):
        print("❌ Rol inválido.")
        return None

    if rol == "inquilino":
        try:
            id_usuario = int(input("Ingrese su ID de inquilino: "))
        except ValueError:
            print("❌ ID inválido.")
            return None
    else:
        id_usuario = 0

    return Usuario(id_usuario=id_usuario, rol=rol)

def mostrar_menu():
    print("\n--- Menú ---")
    print("1. Inquilinos")
    print("2. Arrendos")
    print("3. Apartamentos")
    print("4. Lecturas")
    print("5. Pagos")
    print("6. Recibos")
    print("7. Correspondencia")
    print("8. Acueducto")
    print("9. Gas")
    print("10. Energía")
    print("0. Salir")


def obtener_y_mostrar_tabla(nombre_tabla: str, connector: Connector, usuario: Usuario):
    connector.set_table(nombre_tabla)

    if usuario.es_admin():
        data = connector.get_all()
    else:
        if nombre_tabla == "inquilinos":
            where = f"inq_id = {usuario.id_usuario}"
        elif nombre_tabla == "arrendos":
            where = f"arre_inq_id = {usuario.id_usuario}"
        elif nombre_tabla == "apartamentos":
            where = f"apar_id IN (SELECT arre_apar_id FROM arrendos WHERE arre_inq_id = {usuario.id_usuario})"
        elif nombre_tabla == "lecturas":
            where = f"lec_apar_id IN (SELECT arre_apar_id FROM arrendos WHERE arre_inq_id = {usuario.id_usuario})"
        elif nombre_tabla == "pagos":
            where = f"pago_lec_apar_id IN (SELECT arre_apar_id FROM arrendos WHERE arre_inq_id = {usuario.id_usuario})"
        elif nombre_tabla == "recibos":
            where = f"reci_id IN (SELECT corre_reci_id FROM correspondencia WHERE corre_apar_id IN (SELECT arre_apar_id FROM arrendos WHERE arre_inq_id = {usuario.id_usuario}))"
        elif nombre_tabla == "correspondencia":
            where = f"corre_apar_id IN (SELECT arre_apar_id FROM arrendos WHERE arre_inq_id = {usuario.id_usuario})"
        elif nombre_tabla in ("acueducto", "gas", "energia"):
            where = f"{nombre_tabla[:4]}_reci_id IN (SELECT reci_id FROM recibos WHERE reci_id IN (SELECT corre_reci_id FROM correspondencia WHERE corre_apar_id IN (SELECT arre_apar_id FROM arrendos WHERE arre_inq_id = {usuario.id_usuario})))"
        else:
            where = "1=0"  # no permitido

        data = connector.get_filtered(where)

    print(f"\n--- Datos de {nombre_tabla.upper()} ---")
    if data:
        for row in data:
            print(row)
    else:
        print("No hay datos disponibles.")


def main():

    usuario = seleccionar_usuario()
    if not usuario:
        return

    db = Connector()
    db.connect()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            obtener_y_mostrar_tabla("inquilinos", db, usuario)
        elif opcion == "2":
            obtener_y_mostrar_tabla("arrendos", db, usuario)
        elif opcion == "3":
            obtener_y_mostrar_tabla("apartamentos", db, usuario)
        elif opcion == "4":
            obtener_y_mostrar_tabla("lecturas", db, usuario)
        elif opcion == "5":
            obtener_y_mostrar_tabla("pagos", db, usuario)
        elif opcion == "6":
            obtener_y_mostrar_tabla("recibos", db, usuario)
        elif opcion == "7":
            obtener_y_mostrar_tabla("correspondencia", db, usuario)
        elif opcion == "8":
            obtener_y_mostrar_tabla("acueducto", db, usuario)
        elif opcion == "9":
            obtener_y_mostrar_tabla("gas", db, usuario)
        elif opcion == "10":
            obtener_y_mostrar_tabla("energia", db, usuario)
        elif opcion == "0":
            print("👋 Saliendo...")
            break
        else:
            print("❌ Opción inválida.")

    db.close()

if __name__ == "__main__":
    main()
