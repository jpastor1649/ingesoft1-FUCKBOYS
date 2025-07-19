import sys

sys.path.append("src")
from connector.connector import Connector

sys.path.append("src/models")
from classes.arriendo import Arriendo
from classes.apartamento import Apartamento
from classes.inquilino import Inquilino
from classes.lectura import Lectura
from classes.recibo import Recibo
from classes.pago import Pago

sys.path.append("src")
from managers.gestor_apartamentos import GestorApartamentos
from managers.gestor_pagos import GestorPagos
from managers.generador_reportes import GeneradorReportes
from models.services.servicio_acueducto import ServicioAcueducto
from models.services.servicio_energia import ServicioEnergia
from models.services.calculadora_servicios import CalculadoraRecibos


class Usuario:
    def __init__(
        self,
        id_usuario: int,
        rol: str = "",
        name: str = "",
        connector: Connector | None = None,
    ):
        self.id_usuario = id_usuario
        self.rol = rol
        self.name = name
        self.db = connector
        self.edad = None  # Inicializar edad como None

        if self.db is not None:
            self.cargar_datos(self.db)

    def es_admin(self) -> bool:
        return self.rol.lower() == "admin"

    def cargar_datos(self, db: Connector) -> None:
        """Carga el nombre y rol del usuario desde la base de datos."""
        try:
            db.set_table("inquilinos")
            resultados = db.get_filtered(f"inq_id = {self.id_usuario}")
            if resultados:
                usuario_db = resultados[0]
                self.name = usuario_db.get("inq_nombre", self.name)
                if not self.rol:
                    self.rol = usuario_db.get("rol", self.rol)
                self.edad = usuario_db.get("inq_edad", self.edad)
        except Exception as e:
            print(f"⚠️ Error al cargar datos del usuario: {e}")

    def obtener_arriendos(self, mes: str = None, apar_id: int = None) -> list[dict]:
        arriendos = Arriendo(self.db)
        resultados = []

        if self.es_admin():
            if apar_id:
                resultados = arriendos.obtener_por_apartamento(apar_id)
            else:
                resultados = arriendos.obtener_todos()
        else:
            resultados = arriendos.obtener_por_inquilino(self.id_usuario)
            if apar_id:
                resultados = [a for a in resultados if a.get("arre_apar_id") == apar_id]

        # Filtrar por mes si es necesario
        if mes:
            resultados = [
                a for a in resultados if a.get("arre_mes", "").upper() == mes.upper()
            ]

        return resultados

    def obtener_apartamentos(self) -> list[dict]:
        apartamentos = Apartamento(self.db)
        return (
            apartamentos.obtener_todos()
            if self.es_admin()
            else apartamentos.obtener_por_inquilino(self.id_usuario)
        )

    def obtener_inquilinos(self) -> list[dict]:
        inquilino = Inquilino(self.db)
        return (
            inquilino.obtener_todos()
            if self.es_admin()
            else [inquilino.obtener_por_inquilino(self.id_usuario)]
        )

    def obtener_lecturas(self, mes: str = None, apar_id: int = None) -> list[dict]:
        lecturas = Lectura(self.db)

        if self.es_admin():
            if apar_id:
                resultados = lecturas.obtener_por_apartamento(apar_id)
            else:
                resultados = lecturas.obtener_todas()
        else:
            apartamentos = self.obtener_apartamentos()
            ids_apartamentos = [apto["apar_id"] for apto in apartamentos]
            resultados = []
            for aid in ids_apartamentos:
                if apar_id and aid != apar_id:
                    continue
                resultados.extend(lecturas.obtener_por_apartamento(aid))

        # Filtrar por mes si es necesario
        if mes:
            resultados = [
                lec
                for lec in resultados
                if lec.get("lec_mes", "").upper() == mes.upper()
            ]

        return resultados

    def obtener_recibos(self, mes: str = None, apar_id: int = None) -> list[dict]:
        recibos = Recibo(self.db)
        resultados = []

        if self.es_admin():
            if apar_id:
                resultados = recibos.obtener_por_apartamento(apar_id)
            else:
                resultados = recibos.obtener_todos()
        else:
            apartamentos = self.obtener_apartamentos()
            ids_apartamentos = [apto["apar_id"] for apto in apartamentos]
            for aid in ids_apartamentos:
                if apar_id and aid != apar_id:
                    continue
                resultados.extend(recibos.obtener_por_apartamento(aid))

        # Filtrar por mes si es necesario
        if mes:
            resultados = [
                r for r in resultados if r.get("reci_mes", "").upper() == mes.upper()
            ]

        return resultados

    def obtener_pagos(self, mes: str = None, apar_id: int = None) -> list[dict]:
        pagos = Pago(self.db)
        resultados = []

        if self.es_admin():
            if apar_id:
                resultados = pagos.obtener_por_apartamento(apar_id)
            else:
                resultados = pagos.obtener_todos()
        else:
            apartamentos = self.obtener_apartamentos()
            ids_apartamentos = [apto["apar_id"] for apto in apartamentos]
            for aid in ids_apartamentos:
                if apar_id and aid != apar_id:
                    continue
                resultados.extend(pagos.obtener_por_apartamento(aid))

        # Filtrar por mes si es necesario
        if mes:
            resultados = [
                p for p in resultados if p.get("pago_mes", "").upper() == mes.upper()
            ]

        if len(resultados) == 0:
            print("No hay pagos registrados")
        return resultados

    # SERVICIOS
    def calcular_recibo_apartamento_mes(self, apar_id: int, mes: str) -> dict:
        """
        Calcula el recibo total de un apartamento para un mes específico.
        Admin: cualquier apartamento.
        Inquilino: solo sus apartamentos.
        """
        if not self.es_admin():
            ids_apartamentos = [apto["apar_id"] for apto in self.obtener_apartamentos()]
            if apar_id not in ids_apartamentos:
                raise PermissionError(
                    "No puedes ver recibos de apartamentos que no te pertenecen."
                )
        calculadora = CalculadoraRecibos(self.db)
        return calculadora.calcular_recibo_apartamento_mes(apar_id, mes)

    def calcular_recibos_mes_usuario(self, mes: str) -> dict:
        """
        Calcula los recibos de todos los apartamentos del usuario para un mes.
        Admin: todos los apartamentos.
        Inquilino: solo sus apartamentos.
        """
        calculadora = CalculadoraRecibos(self.db)
        if self.es_admin():
            return calculadora.calcular_distribucion_mes_completo(mes)
        else:
            apartamentos = self.obtener_apartamentos()
            distribucion = {}
            for apto in apartamentos:
                apar_id = apto["apar_id"]
                recibo = calculadora.calcular_recibo_apartamento_mes(apar_id, mes)
                distribucion[apar_id] = recibo
            # Calcular totales generales para el usuario
            total_arrendos = sum(
                r.get("total_arriendo", 0) for r in distribucion.values()
            )
            total_servicios = sum(
                r.get("total_servicios", 0) for r in distribucion.values()
            )
            return {
                "mes": mes,
                "apartamentos": distribucion,
                "totales": {
                    "total_apartamentos": len(apartamentos),
                    "total_arrendos": total_arrendos,
                    "total_servicios": total_servicios,
                    "total_general": total_arrendos + total_servicios,
                },
            }

    # GESTORES
    def generar_reporte_mes(self, mes: str) -> dict:
        """
        Genera un reporte básico de un mes.
        Admin: reporte global.
        Inquilino: suma de sus apartamentos.
        """
        generador = GeneradorReportes(self.db)
        if self.es_admin():
            return generador.generar_reporte_mes(mes)
        else:
            apartamentos = self.obtener_apartamentos()
            ids_apartamentos = [apto["apar_id"] for apto in apartamentos]
            total_arrendos = 0
            total_servicios = 0
            cantidad_arrendos = 0
            cantidad_pagos = 0
            for apar_id in ids_apartamentos:
                rep = generador.generar_reporte_apartamento(apar_id, mes)
                total_arrendos += rep.get("arriendo", 0)
                total_servicios += rep.get("total_servicios", 0)
                cantidad_arrendos += 1 if rep.get("arriendo", 0) > 0 else 0
                cantidad_pagos += len(rep.get("servicios", {}))
            return {
                "mes": mes.upper(),
                "total_arrendos": total_arrendos,
                "total_servicios": total_servicios,
                "total_general": total_arrendos + total_servicios,
                "cantidad_arrendos": cantidad_arrendos,
                "cantidad_pagos": cantidad_pagos,
            }

    def generar_reporte_apartamento(self, apar_id: int, mes: str) -> dict:
        """
        Genera un reporte de un apartamento específico para un mes.
        Admin: cualquier apartamento.
        Inquilino: solo sus apartamentos.
        """
        generador = GeneradorReportes(self.db)
        if self.es_admin():
            return generador.generar_reporte_apartamento(apar_id, mes)
        else:
            ids_apartamentos = [apto["apar_id"] for apto in self.obtener_apartamentos()]
            if apar_id not in ids_apartamentos:
                raise PermissionError(
                    "No puedes ver reportes de apartamentos que no te pertenecen."
                )
            return generador.generar_reporte_apartamento(apar_id, mes)

    def generar_reporte_recaudacion(self, mes: str) -> dict:
        """
        Genera un reporte de recaudación del mes.
        Admin: reporte global.
        Inquilino: solo sus apartamentos.
        """
        generador = GeneradorReportes(self.db)
        if self.es_admin():
            return generador.generar_reporte_recaudacion(mes)
        else:
            apartamentos = self.obtener_apartamentos()
            ids_apartamentos = [apto["apar_id"] for apto in apartamentos]
            total_arriendos = 0
            arrendos_pagados = 0
            total_servicios = 0
            servicios_pagados = 0
            for apar_id in ids_apartamentos:
                rep = generador.generar_reporte_apartamento(apar_id, mes)
                arriendo = rep.get("arriendo", 0)
                total_arriendos += arriendo
                # Verifica si el arriendo está pagado
                self.db.set_table("arrendos")
                arr = self.db.get_filtered(
                    f"arre_apar_id = {apar_id} AND arre_mes = '{mes.upper()}'"
                )
                if arr and arr[0].get("arre_estado") == "CANCELADO":
                    arrendos_pagados += arriendo
                servicios = rep.get("servicios", {})
                total_servicios += rep.get("total_servicios", 0)
                # Suma solo los servicios pagados
                self.db.set_table("pagos")
                for servicio, valor in servicios.items():
                    # Asegúrate de que el nombre del servicio coincida con el de la base de datos
                    pago = self.db.get_filtered(
                        f"pago_lec_apar_id = {apar_id} AND pago_mes = '{mes.upper()}' AND pago_lec_servicio = '{servicio}'"
                    )
                    if pago and pago[0].get("pago_estado") == "CANCELADO":
                        servicios_pagados += valor
            return {
                "mes": mes.upper(),
                "arrendos": {
                    "total": total_arriendos,
                    "pagado": arrendos_pagados,
                    "pendiente": total_arriendos - arrendos_pagados,
                },
                "servicios": {
                    "total": total_servicios,
                    "pagado": servicios_pagados,
                    "pendiente": total_servicios - servicios_pagados,
                },
                "total_esperado": total_arriendos + total_servicios,
                "total_recaudado": arrendos_pagados + servicios_pagados,
                "total_pendiente": (total_arriendos - arrendos_pagados)
                + (total_servicios - servicios_pagados),
            }

    def exportar_reporte_texto(self, reporte: dict) -> str:
        """Exporta un reporte en formato texto."""
        generador = GeneradorReportes(self.db)
        return generador.exportar_reporte_texto(reporte)

    def obtener_resumen_general(self) -> dict:
        """Obtiene el resumen general del sistema (solo admin)."""
        if not self.es_admin():
            raise PermissionError("Solo el administrador puede ver el resumen general.")
        generador = GeneradorReportes(self.db)
        return generador.obtener_resumen_general()

    def seleccionar_usuario(connector: Connector) -> "Usuario | None":
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

        return Usuario(id_usuario=id_usuario, rol=rol, connector=connector)
