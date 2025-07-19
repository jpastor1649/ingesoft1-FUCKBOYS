# pylint: disable=broad-exception-caught
# pylint: disable=line-too-long

"""Main application entry point for managing apartments and rentals."""

import sys

sys.path.append("src")

from connector.connector import Connector
from models.classes.usuarios import Usuario


def pedir_filtros():
    """Solicita al usuario filtros para las consultas de arriendos, lecturas, recibos y pagos."""
    mes = input("¿Filtrar por mes? (deje vacío para no filtrar): ").strip().upper()
    mes = mes if mes else None
    apar_id = input("¿Filtrar por apartamento? (deje vacío para no filtrar): ").strip()
    apar_id = int(apar_id) if apar_id else None
    return mes, apar_id


def menu_apartamentos(usuario):
    """Muestra el menú de opciones para gestionar apartamentos."""

    if usuario:
        while True:
            print("\n=== Menú de Apartamentos ===")
            print("1. Ver apartamentos")
            print("2. Crear apartamento")
            print("3. Actualizar apartamento")
            print("4. Eliminar apartamento")
            print("0. Volver al menú principal")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                print("\n🏢 Apartamentos:")
                apar_id = input(
                    "¿Filtrar por apartamento? (deje vacío para no filtrar): "
                ).strip()
                if apar_id:
                    for ap in usuario.obtener_apartamentos():
                        if ap["apar_id"] == int(apar_id):
                            print(ap)
                else:
                    for ap in usuario.obtener_apartamentos():
                        print(ap)

            elif opcion == "2":
                if usuario.rol != "admin":
                    print("Solo los administradores pueden crear apartamentos.")
                    break
                try:
                    apar_id = int(input("Ingrese el ID del apartamento: "))
                    cantidad_personas = int(input("Ingrese la cantidad de personas: "))
                    observaciones = input("Ingrese observaciones (opcional): ")
                    if usuario.crear_apartamento(
                        apar_id, cantidad_personas, observaciones
                    ):
                        print("Apartamento creado exitosamente.")
                    else:
                        print("Error al crear el apartamento.")
                except ValueError as e:
                    print(f"Error: {e}")
            elif opcion == "3":
                if usuario.rol != "admin":
                    print("Solo los administradores pueden actualizar apartamentos.")
                    break
                try:
                    apar_id = int(input("Ingrese el ID del apartamento a actualizar: "))
                    cantidad_personas = int(
                        input("Ingrese la nueva cantidad de personas: ")
                    )
                    observaciones = input("Ingrese nuevas observaciones (opcional): ")
                    if usuario.actualizar_apartamento(
                        apar_id, cantidad_personas, observaciones
                    ):
                        print("Apartamento actualizado exitosamente.")
                    else:
                        print("Error al actualizar el apartamento.")
                except ValueError as e:
                    print(f"Error: {e}")
            elif opcion == "4":
                if usuario.rol != "admin":
                    print("Solo los administradores pueden eliminar apartamentos.")
                    break
                try:
                    apar_id = int(input("Ingrese el ID del apartamento a eliminar: "))
                    if usuario.eliminar_apartamento(apar_id):
                        print("Apartamento eliminado exitosamente.")
                    else:
                        print("Error al eliminar el apartamento.")
                except ValueError as e:
                    print(f"Error: {e}")
            elif opcion == "0":
                break


def menu_arriendos(usuario):
    """Muestra el menú de opciones para gestionar arriendos."""
    if usuario:
        while True:
            print("\n=== Menú de Arriendos ===")
            print("1. Ver arriendos")
            print("2. Crear arriendo")
            print("3. Actualizar arriendo")
            print("4. Cerrar o Registrar arriendo")
            print("0. Volver al menú principal")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                mes, apar_id = pedir_filtros()
                print("\n📦 Arriendos:")
                for a in usuario.obtener_arriendos(mes=mes, apar_id=apar_id):
                    print(a)

            elif opcion == "2":
                if usuario.rol != "admin":
                    print("Solo los administradores pueden crear arriendos.")
                    break
                try:
                    inq_id = int(input("Ingrese el ID del inquilino: "))
                    apar_id = int(input("Ingrese el ID del apartamento: "))
                    mes = input("Ingrese el mes (Ej. ENERO): ").strip().upper()
                    valor = float(input("Ingrese el valor del arriendo: "))
                    fecha_inicio = input(
                        "Ingrese la fecha de inicio (YYYY-MM-DD): "
                    ).strip()
                    fecha_fin = input("Ingrese la fecha de fin (YYYY-MM-DD): ").strip()
                    estado = (
                        input("Estado del arriendo (Ej. PENDIENTE): ").strip()
                        or "PENDIENTE"
                    ).upper()
                    fecha_pago = (
                        input("Fecha de pago (opcional, YYYY-MM-DD): ").strip() or None
                    )
                    observaciones = input("Observaciones (opcional): ").strip()

                    creado = usuario.crear_arriendo(
                        inq_id=inq_id,
                        apar_id=apar_id,
                        mes=mes,
                        valor=valor,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin,
                        estado=estado,
                        fecha_pago=fecha_pago,
                        observaciones=observaciones,
                    )

                    if creado:
                        print("✅ Arriendo creado exitosamente.")
                    else:
                        print(
                            "❌ Error al crear el arriendo. Verifica los datos o conflictos de fechas."
                        )
                except ValueError as e:
                    print(f"Error de entrada: {e}")

            elif opcion == "3":
                if usuario.rol != "admin":
                    print("Solo los administradores pueden actualizar arriendos.")
                    break

                try:
                    print("\n¿Qué desea actualizar?")
                    print("1. Estado del arriendo")
                    print("2. Valor del arriendo")
                    sub_opcion = input("Seleccione una opción: ").strip()

                    apar_id = int(input("Ingrese el ID del apartamento: "))
                    inq_id = int(input("Ingrese el ID del inquilino: "))
                    fecha_inicio = input(
                        "Ingrese la fecha de inicio del arriendo (YYYY-MM-DD): "
                    ).strip()

                    if sub_opcion == "1":
                        nuevo_estado = (
                            input("Nuevo estado del arriendo (Ej. PENDIENTE): ")
                            .strip()
                            .upper()
                        )
                        fecha_pago = (
                            input("Fecha de pago (opcional, YYYY-MM-DD): ").strip()
                            or None
                        )

                        actualizado = usuario.actualizar_estado_arriendo(
                            fecha_inicio=fecha_inicio,
                            apar_id=apar_id,
                            inq_id=inq_id,
                            nuevo_estado=nuevo_estado,
                            fecha_pago=fecha_pago,
                        )
                        if actualizado:
                            print("✅ Estado del arriendo actualizado correctamente.")
                        else:
                            print(
                                "❌ No se pudo actualizar el estado. Verifique los datos."
                            )

                    elif sub_opcion == "2":
                        nuevo_valor = int(input("Nuevo valor del arriendo: "))
                        actualizado = usuario.actualizar_valor_arriendo(
                            fecha_inicio=fecha_inicio,
                            apar_id=apar_id,
                            inq_id=inq_id,
                            nuevo_valor=nuevo_valor,
                        )
                        if actualizado:
                            print("✅ Valor del arriendo actualizado correctamente.")
                        else:
                            print(
                                "❌ No se pudo actualizar el valor. Verifique los datos o que el arriendo exista."
                            )

                    else:
                        print("❌ Opción inválida.")

                except ValueError as e:
                    print(f"Error de entrada: {e}")

            elif opcion == "4":
                if usuario.rol != "admin":
                    print(
                        "Solo los administradores pueden cerrar o registrar arriendos."
                    )
                    break
                try:
                    print("\n💳 ¿Acción de estado?")
                    print("1. Registrar pago")
                    print("2. Cerrar arriendo")
                    sub_op = input("Seleccione una opción: ").strip()

                    apar_id = int(input("ID del apartamento: "))
                    inq_id = int(input("ID del inquilino: "))
                    fecha_inicio = input(
                        "Fecha de inicio del arriendo (YYYY-MM-DD): "
                    ).strip()

                    if sub_op == "1":
                        fecha_pago = input("Fecha de pago (YYYY-MM-DD): ").strip()
                        ok = usuario.registrar_pago_arriendo(
                            fecha_inicio, apar_id, inq_id, fecha_pago
                        )
                    elif sub_op == "2":
                        ok = usuario.cerrar_arriendo(fecha_inicio, apar_id, inq_id)
                    else:
                        print("❌ Opción inválida.")
                        continue

                    print(
                        "✅ Estado actualizado."
                        if ok
                        else "❌ No se pudo cambiar el estado."
                    )
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == "0":
                break

            else:
                print("Opción no válida. Intente de nuevo.")


def main():
    """Punto de entrada principal para la aplicación de gestión de apartamentos y arriendos."""
    print("Bienvenido al sistema de gestión de apartamentos y arriendos.")
    db = Connector()
    db.connect()

    usuario = Usuario.seleccionar_usuario(db)
    if not usuario:
        return
    print(f"\n👤 Usuario cargado: {usuario.name} (Rol: {usuario.rol})")

    while True:
        print("\n=== Menú de Consultas ===")
        print("1. Arriendos")
        print("2. Apartamentos")
        print("3. Ver lecturas")
        print("4. Ver recibos")
        print("5. Ver pagos")
        print("6. Ver inquilinos")
        print("7. Ver servicios (recibo de servicios)")
        print("8. Reportes")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            menu_arriendos(usuario)
        elif opcion == "2":
            menu_apartamentos(usuario)
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
                    mes = input("Ingrese el mes: ").strip().upper()
                    recibo = usuario.calcular_recibo_apartamento_mes(apar_id, mes)
                    print(recibo)
                except Exception as e:
                    print(f"Error: {e}")
            elif subop == "2":
                print("\nSERVICIOS de todos los apartamentos")
                try:
                    mes = (
                        input("Ingrese el mes para todos los apartamentos: ")
                        .strip()
                        .upper()
                    )
                    recibos_mes = usuario.calcular_recibos_mes_usuario(mes)
                    print(recibos_mes)
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Opción no válida.")
        elif opcion == "8":
            print("1. Reporte general de un mes")
            print("2. Reporte de cada apartamento del usuario para un mes")
            print("3. Reporte de recaudación para un mes")
            if usuario.rol == "admin":
                print("4. Resumen general del sistema")

            subop = input("Seleccione una opción: ").strip()
            if subop == "1":
                mes = input("Ingrese el mes para un reporte general: ").strip().upper()
                print(f"\n📊 Reporte general del mes {mes}:")
                try:
                    reporte_mes = usuario.generar_reporte_mes(mes)
                    print(usuario.exportar_reporte_texto(reporte_mes))
                except Exception as e:
                    print(f"Error al generar reporte del mes: {e}")
            elif subop == "2":
                mes = (
                    input("Ingrese el mes para reporte de apartamentos a su nombre: ")
                    .strip()
                    .upper()
                )
                print(f"\n📊 Reporte de apartamentos para {mes}:")
                try:
                    apartamentos = usuario.obtener_apartamentos()
                    for ap in apartamentos:
                        apar_id = ap["apar_id"]
                        try:
                            reporte_apto = usuario.generar_reporte_apartamento(
                                apar_id, mes
                            )
                            print(usuario.exportar_reporte_texto(reporte_apto))
                        except Exception as e:
                            print(f"  Error: {e}")
                except Exception as e:
                    print(f"Error al obtener apartamentos: {e}")
            elif subop == "3":
                mes = (
                    input("Ingrese el mes para el reporte de recaudación: ")
                    .strip()
                    .upper()
                )
                print(f"\n📊 Reporte de recaudación {mes}:")
                try:
                    reporte_recaudacion = usuario.generar_reporte_recaudacion(mes)
                    print(usuario.exportar_reporte_texto(reporte_recaudacion))
                except Exception as e:
                    print(f"Error al generar reporte de recaudación: {e}")
            elif subop == "4" and usuario.rol == "admin":
                print("\n📊 Resumen general del sistema:")
                try:
                    resumen = usuario.obtener_resumen_general()
                    print(resumen)
                except Exception as e:
                    print(f"Error al obtener resumen general: {e}")
        elif opcion == "0":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

    db.close()


if __name__ == "__main__":
    main()
