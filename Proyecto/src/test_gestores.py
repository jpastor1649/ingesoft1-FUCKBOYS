from connector.connector import Connector
from managers.gestor_apartamentos import GestorApartamentos
from managers.gestor_pagos import GestorPagos
from managers.generador_reportes import GeneradorReportes


def test_gestor_apartamentos(db):
    """Probar GestorApartamentos"""
    print("\n" + "=" * 50)
    print("PROBANDO GESTOR DE APARTAMENTOS")
    print("=" * 50)

    gestor = GestorApartamentos(db)

    # Obtener todos los apartamentos
    print("\n1. Lista de apartamentos:")
    apartamentos = gestor.obtener_apartamentos()
    for apt in apartamentos:
        print(
            f"   Apartamento {apt['apar_id']}: {apt['apar_cantidadPersonas']} personas"
        )

    # Ver estado de ocupación
    print("\n2. Estado de ocupación:")
    estados = gestor.listar_apartamentos_estado()
    for estado in estados:
        print(f"   Apto {estado['apar_id']}: {estado['estado']}")

    # Resumen de ocupación
    print("\n3. Resumen general:")
    resumen = gestor.obtener_resumen_ocupacion()
    print(f"   Total: {resumen['total']}")
    print(f"   Ocupados: {resumen['ocupados']}")
    print(f"   Disponibles: {resumen['disponibles']}")

    # Probar con un apartamento específico
    if apartamentos:
        apar_id = apartamentos[0]["apar_id"]
        print(f"\n4. Detalle del apartamento {apar_id}:")
        detalle = gestor.obtener_apartamento_con_inquilino(apar_id)
        if detalle:
            print(f"   Personas: {detalle['apartamento']['apar_cantidadPersonas']}")
            if detalle["inquilino"]:
                print(f"   Inquilino: {detalle['inquilino']['inq_nombre']}")
            else:
                print("   Sin inquilino")


def test_gestor_pagos(db):
    """Probar GestorPagos"""
    print("\n" + "=" * 50)
    print("PROBANDO GESTOR DE PAGOS")
    print("=" * 50)

    gestor = GestorPagos(db)

    # Obtener pagos pendientes
    print("\n1. Pagos pendientes:")
    pendientes = gestor.obtener_pagos_pendientes()
    print(f"   Total pendientes: {len(pendientes)}")

    # Resumen de pagos
    print("\n2. Resumen general de pagos:")
    resumen = gestor.obtener_resumen_pagos()
    print(f"   Total pagos: {resumen['total_pagos']}")
    print(f"   Pendientes: {resumen['pendientes']}")
    print(f"   Cancelados: {resumen['cancelados']}")
    print(f"   Valor total: ${resumen['valor_total']:,}")
    print(f"   Valor pendiente: ${resumen['valor_pendiente']:,}")

    # Pagos por servicio
    print("\n3. Pagos por servicio:")
    servicios = ["ACUEDUCTO Y ASEO", "ENERGIA", "GAS NATURAL"]
    for servicio in servicios:
        pagos = gestor.obtener_pagos_servicio(servicio)
        print(f"   {servicio}: {len(pagos)} pagos")

    # Probar con un mes específico
    mes = "ENERO"  # Cambiar según tus datos
    print(f"\n4. Pagos del mes {mes}:")
    pagos_mes = gestor.obtener_pagos_mes(mes)
    print(f"   Total pagos en {mes}: {len(pagos_mes)}")


def test_generador_reportes(db):
    """Probar GeneradorReportes"""
    print("\n" + "=" * 50)
    print("PROBANDO GENERADOR DE REPORTES")
    print("=" * 50)

    generador = GeneradorReportes(db)

    # Resumen general del sistema
    print("\n1. Resumen general del sistema:")
    resumen = generador.obtener_resumen_general()
    print(f"   Total apartamentos: {resumen['total_apartamentos']}")
    print(f"   Total inquilinos: {resumen['total_inquilinos']}")
    print(f"   Arrendos activos: {resumen['arrendos_activos']}")
    print(f"   Pagos pendientes: {resumen['pagos_pendientes']}")

    # Reporte de un mes
    mes = "ENERO"  # Cambiar según tus datos
    print(f"\n2. Reporte del mes {mes}:")
    reporte_mes = generador.generar_reporte_mes(mes)
    print(generador.exportar_reporte_texto(reporte_mes))

    # Reporte de recaudación
    print(f"\n3. Reporte de recaudación {mes}:")
    reporte_recaudacion = generador.generar_reporte_recaudacion(mes)
    print(generador.exportar_reporte_texto(reporte_recaudacion))

    # Reporte de apartamento específico
    # Primero obtener un apartamento
    gestor_apts = GestorApartamentos(db)
    apartamentos = gestor_apts.obtener_apartamentos()
    if apartamentos:
        apar_id = apartamentos[0]["apar_id"]
        print(f"\n4. Reporte del apartamento {apar_id} en {mes}:")
        reporte_apto = generador.generar_reporte_apartamento(apar_id, mes)
        print(generador.exportar_reporte_texto(reporte_apto))


def main():
    """Función principal"""
    # Crear conexión
    db = Connector()
    db.connect()

    if not db.connection:
        print("❌ No se pudo conectar a la base de datos")
        return

    try:
        # Menú de pruebas
        while True:
            print("\n" + "=" * 50)
            print("MENÚ DE PRUEBAS DE GESTORES")
            print("=" * 50)
            print("1. Probar Gestor de Apartamentos")
            print("2. Probar Gestor de Pagos")
            print("3. Probar Generador de Reportes")
            print("4. Probar todos")
            print("0. Salir")

            opcion = input("\nSeleccione opción: ").strip()

            if opcion == "1":
                test_gestor_apartamentos(db)
            elif opcion == "2":
                test_gestor_pagos(db)
            elif opcion == "3":
                test_generador_reportes(db)
            elif opcion == "4":
                test_gestor_apartamentos(db)
                test_gestor_pagos(db)
                test_generador_reportes(db)
            elif opcion == "0":
                break
            else:
                print("❌ Opción inválida")

            input("\nPresione ENTER para continuar...")

    finally:
        #   Cerrar conexión
        db.close()


if __name__ == "__main__":
    main()
