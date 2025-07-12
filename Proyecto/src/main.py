from connector.connector import Connector
from models.usuario import Usuario
from models.arrendo import Arrendo
from models.apartamento import Apartamento  
from models.inquilino import Inquilino
from models.lectura import Lectura
from models.recibo import Recibo
from models.pago import Pago

def seleccionar_usuario() -> Usuario:
    print("=== Login simulado ===")
    while True:
        rol = input("Ingrese su rol ('admin' o 'inquilino'): ").strip().lower()
        if rol not in ("admin", "inquilino"):
            print("❌ Rol inválido. Intente nuevamente.")
        else:
            break

    if rol == "inquilino":
        while True:
            try:
                id_usuario = int(input("Ingrese su ID de inquilino: "))
                break
            except ValueError:
                print("❌ ID inválido. Debe ser un número entero.")
    else:
        id_usuario = 0  # el admin no tiene ID de inquilino

    return Usuario(id_usuario=id_usuario, rol=rol, connector=None)  # conector se asigna después


def mostrar_menu():
    print("\n--- Menú Principal ---")
    print("1. Mostrar arrendos")
    print("2. Mostrar apartamentos")
    print("3. Mostrar inquilinos")
    print("4. Mostrar lecturas")
    print("5. Mostrar pagos")
    print("6. Mostrar recibos")
    print("0. Salir")


def ejecutar_interfaz(usuario: Usuario):
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            print("Arrendos:")
            for x in usuario.obtener_arrendos(): print(x)
        elif opcion == "2":
            print("Apartamentos:")
            for x in usuario.obtener_apartamentos(): print(x)
        elif opcion == "3":
            print("Inquilinos:")
            for x in usuario.obtener_inquilinos(): print(x)
        elif opcion == "4":
            print("Lecturas:")
            for x in usuario.obtener_lecturas(): print(x)
        elif opcion == "5":
            print("Pagos:")
            for x in usuario.obtener_pagos(): print(x)
        elif opcion == "6":
            print("Recibos:") 
            for x in usuario.obtener_recibos(): print(x)
        elif opcion == "0":
            print("👋 Cerrando sesión...")
            break
        else:
            print("❌ Opción inválida")


def main():
    db = Connector()
    db.connect()

    usuario = seleccionar_usuario()
    usuario.db = db  
    print(f"\nBienvenido {usuario}\n")

    ejecutar_interfaz(usuario)
    db.close()


if __name__ == "__main__":
    main()
