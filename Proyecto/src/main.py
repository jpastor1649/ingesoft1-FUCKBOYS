import sys

sys.path.append("src")
from connector.connector import Connector
from init_db import DataBaseManager
from usuarios import Usuario
from managers.gestor_apartamentos import GestorApartamentos
from managers.gestor_pagos import GestorPagos
from managers.generador_reportes import GeneradorReportes


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

def pedir_filtros():
    mes = input("¿Filtrar por mes? (deje vacío para no filtrar): ").strip().upper()
    mes = mes if mes else None
    apar_id = input("¿Filtrar por apartamento? (deje vacío para no filtrar): ").strip()
    apar_id = int(apar_id) if apar_id else None
    return mes, apar_id

def main():
    db = Connector()
    db.connect()

    usuario = Usuario.seleccionar_usuario(db)
    if not usuario:
        return
    print(f"\n👤 Usuario cargado: {usuario.name} (Rol: {usuario.rol})")

    while True:
        print("\n=== Menú de Consultas ===")
        print("1. Ver arriendos")
        print("2. Ver apartamentos")
        print("3. Ver lecturas")
        print("4. Ver recibos")
        print("5. Ver pagos")
        print("6. Ver inquilinos")
        print("7. Ver servicios (recibo de servicios)")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            mes, apar_id = pedir_filtros()
            print("\n📦 Arriendos:")
            for a in usuario.obtener_arriendos(mes=mes, apar_id=apar_id):
                print(a)
        elif opcion == "2":
            print("\n🏢 Apartamentos:")
            apar_id = input("¿Filtrar por apartamento? (deje vacío para no filtrar): ").strip()
            if apar_id:
                for ap in usuario.obtener_apartamentos():
                    if ap["apar_id"] == int(apar_id):
                        print(ap)
            else:
                for ap in usuario.obtener_apartamentos():
                    print(ap)
        elif opcion == "3":
            mes, apar_id = pedir_filtros()
            print("\n🧾 Lecturas:")
            for l in usuario.obtener_lecturas(mes=mes, apar_id=apar_id):
                print(l)
        elif opcion == "4":
            mes, apar_id = pedir_filtros()
            print("\n📨 Recibos:")
            for r in usuario.obtener_recibos(mes=mes, apar_id=apar_id):
                print(r)
        elif opcion == "5":
            mes, apar_id = pedir_filtros()
            print("\n💳 Pagos:")
            for p in usuario.obtener_pagos(mes=mes, apar_id=apar_id):
                print(p)
        elif opcion == "6":
            print("\n👥 Inquilino:")
            for i in usuario.obtener_inquilinos():
                print(i)
        elif opcion == "7":
            print("\n=== SERVICIOS ===")
            print("1. Servicios por apartamento")
            print("2. Servicios de todos los apartamentos")
            subop = input("Seleccione una opción: ").strip()
            if subop == "1":
                print("👥 Servicios por apartamento")
                try:
                    apar_id = int(input("Ingrese el ID del apartamento: "))
                    mes = input("Ingrese el mes (ejemplo: JULIO): ").strip().upper()
                    recibo = usuario.calcular_recibo_apartamento_mes(apar_id, mes)
                    print(recibo)
                except Exception as e:
                    print(f"Error: {e}")
            elif subop == "2":
                print("\nSERVICIOS de todos los apartamentos")
                try:
                    mes = input("Ingrese el mes para todos los apartamentos (ejemplo: JULIO): ").strip().upper()
                    recibos_mes = usuario.calcular_recibos_mes_usuario(mes)
                    print(recibos_mes)
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Opción no válida.")
        elif opcion == "0":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")
    
    # --- Pruebas de managers y servicios ---
    print("=== Prueba de reportes ===")

    # Reporte general del mes
    print("\n📊 Reporte general del mes MAYO:")
    try:
        reporte_mes = usuario.generar_reporte_mes("MAYO")
        print(usuario.exportar_reporte_texto(reporte_mes))
    except Exception as e:
        print(f"Error al generar reporte del mes: {e}")

    # Reporte de cada apartamento del usuario para MAYO
    print("\n📊 Reporte de apartamentos para MAYO:")
    try:
        apartamentos = usuario.obtener_apartamentos()
        for ap in apartamentos:
            apar_id = ap["apar_id"]
            print(f"\n- Apartamento {apar_id}:")
            try:
                reporte_apto = usuario.generar_reporte_apartamento(apar_id, "MAYO")
                print(usuario.exportar_reporte_texto(reporte_apto))
            except Exception as e:
                print(f"  Error: {e}")
    except Exception as e:
        print(f"Error al obtener apartamentos: {e}")

    # Reporte de recaudación
    print("\n📊 Reporte de recaudación MAYO:")
    try:
        reporte_recaudacion = usuario.generar_reporte_recaudacion("MAYO")
        print(usuario.exportar_reporte_texto(reporte_recaudacion))
    except Exception as e:
        print(f"Error al generar reporte de recaudación: {e}")

    # Resumen general (solo admin)
    if usuario.rol == "admin":
        print("\n📊 Resumen general del sistema:")
        try:
            resumen = usuario.obtener_resumen_general()
            print(resumen)
        except Exception as e:
            print(f"Error al obtener resumen general: {e}")

    db.close()


if __name__ == "__main__":
    main()
