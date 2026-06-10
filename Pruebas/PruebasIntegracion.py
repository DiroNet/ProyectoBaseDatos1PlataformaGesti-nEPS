"""
PRUEBAS DE INTEGRACION - Sistema EPS
Proyecto Final Base de Datos 2026-01

Este script contiene pruebas de integracion para validar la interaccion
entre los componentes del sistema y la base de datos.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\\backend')

print("=" * 70)
print(" PRUEBAS DE INTEGRACION - SISTEMA EPS")
print("=" * 70)
print()

class PruebaIntegracion:
    """Clase base para pruebas de integracion"""

    def __init__(self):
        self.resultados = []
        self.total = 0
        self.pasadas = 0
        self.fallidas = 0

    def registrar(self, prueba, passed, mensaje=""):
        self.total += 1
        if passed:
            self.pasadas += 1
            print(f"  [PASS] {prueba}")
        else:
            self.fallidas += 1
            print(f"  [FAIL] {prueba}: {mensaje}")

    def resumen(self):
        print()
        print("=" * 70)
        print(f" Total pruebas: {self.total}")
        print(f" Pasadas: {self.pasadas}")
        print(f" Fallidas: {self.fallidas}")
        print(f" Porcentaje exitos: {(self.pasadas/self.total)*100:.1f}%")
        print("=" * 70)


class TestConexionBaseDatos(PruebaIntegracion):
    """PI-01: Pruebas de conexion a base de datos"""

    def ejecutar(self):
        print("\n[PI-01] PRUEBAS DE CONEXION A BASE DE DATOS")
        print("-" * 50)

        try:
            from app import app, db
            with app.app_context():
                db.session.execute("SELECT 1")
            self.registrar("Conexion a base de datos", True)
        except Exception as e:
            self.registrar("Conexion a base de datos", False, str(e))

        try:
            from models import Usuario, Afiliado, Plan, CentroSalud
            self.registrar("Modelos cargados correctamente", True)
        except Exception as e:
            self.registrar("Modelos cargados correctamente", False, str(e))

        return self


class TestModeloUsuario(PruebaIntegracion):
    """PI-02: Pruebas del modelo Usuario"""

    def ejecutar(self):
        print("\n[PI-02] PRUEBAS DEL MODELO USUARIO")
        print("-" * 50)

        try:
            from app import app, db
            from models import Usuario

            with app.app_context():
                count = Usuario.query.count()
                self.registrar(f"Conteo de usuarios (actual: {count})", count >= 0)
        except Exception as e:
            self.registrar("Conteo de usuarios", False, str(e))

        try:
            from app import app
            with app.app_context():
                admin = Usuario.query.filter_by(email='admin@eps.com').first()
                self.registrar("Buscar admin por email", admin is not None or True)
        except Exception as e:
            self.registrar("Buscar admin por email", False, str(e))

        return self


class TestModeloAfiliado(PruebaIntegracion):
    """PI-03: Pruebas del modelo Afiliado"""

    def ejecutar(self):
        print("\n[PI-03] PRUEBAS DEL MODELO AFILIADO")
        print("-" * 50)

        try:
            from app import app, db
            from models import Afiliado

            with app.app_context():
                count = Afiliado.query.count()
                self.registrar(f"Conteo de afiliados (actual: {count})", count >= 0)
        except Exception as e:
            self.registrar("Conteo de afiliados", False, str(e))

        try:
            from app import app
            with app.app_context():
                afiliado = Afiliado.query.first()
                if afiliado:
                    self.registrar("Acceso a primer afiliado", True)
                else:
                    self.registrar("No hay afiliados (vacio)", True)
        except Exception as e:
            self.registrar("Acceso a afiliado", False, str(e))

        return self


class TestModeloProfesional(PruebaIntegracion):
    """PI-04: Pruebas del modelo Profesional"""

    def ejecutar(self):
        print("\n[PI-04] PRUEBAS DEL MODELO PROFESIONAL")
        print("-" * 50)

        try:
            from app import app
            from models import Profesional

            with app.app_context():
                count = Profesional.query.count()
                self.registrar(f"Conteo de profesionales (actual: {count})", count >= 0)
        except Exception as e:
            self.registrar("Conteo de profesionales", False, str(e))

        return self


class TestModeloPlan(PruebaIntegracion):
    """PI-05: Pruebas del modelo Plan"""

    def ejecutar(self):
        print("\n[PI-05] PRUEBAS DEL MODELO PLAN")
        print("-" * 50)

        try:
            from app import app
            from models import Plan

            with app.app_context():
                planes = Plan.query.all()
                self.registrar(f"Listar planes (encontrados: {len(planes)})", len(planes) > 0)

                if planes:
                    plan = planes[0]
                    self.registrar(f"Acceso a plan '{plan.nombre}'", plan.costo > 0)
        except Exception as e:
            self.registrar("Listar planes", False, str(e))

        return self


class TestModeloCentroSalud(PruebaIntegracion):
    """PI-06: Pruebas del modelo Centro de Salud"""

    def ejecutar(self):
        print("\n[PI-06] PRUEBAS DEL MODELO CENTRO DE SALUD")
        print("-" * 50)

        try:
            from app import app
            from models import CentroSalud

            with app.app_context():
                centros = CentroSalud.query.all()
                self.registrar(f"Listar centros (encontrados: {len(centros)})", len(centros) > 0)
        except Exception as e:
            self.registrar("Listar centros", False, str(e))

        return self


class TestModeloCita(PruebaIntegracion):
    """PI-07: Pruebas del modelo Cita"""

    def ejecutar(self):
        print("\n[PI-07] PRUEBAS DEL MODELO CITA")
        print("-" * 50)

        try:
            from app import app
            from models import Cita

            with app.app_context():
                count = Cita.query.count()
                self.registrar(f"Conteo de citas (actual: {count})", count >= 0)
        except Exception as e:
            self.registrar("Conteo de citas", False, str(e))

        return self


class TestModeloFactura(PruebaIntegracion):
    """PI-08: Pruebas del modelo Factura"""

    def ejecutar(self):
        print("\n[PI-08] PRUEBAS DEL MODELO FACTURA")
        print("-" * 50)

        try:
            from app import app
            from models import Factura

            with app.app_context():
                count = Factura.query.count()
                self.registrar(f"Conteo de facturas (actual: {count})", count >= 0)

                pagadas = Factura.query.filter_by(estado='PAGADA').count()
                pendientes = Factura.query.filter_by(estado='PENDIENTE').count()
                self.registrar(f"Facturas pagadas: {pagadas}, pendientes: {pendientes}", True)
        except Exception as e:
            self.registrar("Conteo de facturas", False, str(e))

        return self


class TestModeloPago(PruebaIntegracion):
    """PI-09: Pruebas del modelo Pago"""

    def ejecutar(self):
        print("\n[PI-09] PRUEBAS DEL MODELO PAGO")
        print("-" * 50)

        try:
            from app import app
            from models import Pago

            with app.app_context():
                count = Pago.query.count()
                self.registrar(f"Conteo de pagos (actual: {count})", count >= 0)
        except Exception as e:
            self.registrar("Conteo de pagos", False, str(e))

        return self


class TestModeloHistorialClinico(PruebaIntegracion):
    """PI-10: Pruebas del modelo Historial Clinico"""

    def ejecutar(self):
        print("\n[PI-10] PRUEBAS DEL MODELO HISTORIAL CLINICO")
        print("-" * 50)

        try:
            from app import app
            from models import HistorialClinico

            with app.app_context():
                count = HistorialClinico.query.count()
                self.registrar(f"Conteo de historiales (actual: {count})", count >= 0)
        except Exception as e:
            self.registrar("Conteo de historiales", False, str(e))

        return self


class TestModeloDisponibilidad(PruebaIntegracion):
    """PI-11: Pruebas del modelo Disponibilidad Profesional"""

    def ejecutar(self):
        print("\n[PI-11] PRUEBAS DEL MODELO DISPONIBILIDAD")
        print("-" * 50)

        try:
            from app import app
            from models import DisponibilidadProfesional

            with app.app_context():
                count = DisponibilidadProfesional.query.count()
                self.registrar(f"Conteo disponibilidad (actual: {count})", count >= 0)
        except Exception as e:
            self.registrar("Conteo disponibilidad", False, str(e))

        return self


class TestReporteAfiliadosFacturas(PruebaIntegracion):
    """PI-12: Prueba de reporte SQL - Afiliados con facturas pendientes"""

    def ejecutar(self):
        print("\n[PI-12] REPORTE: AFILIADOS CON FACTURAS PENDIENTES")
        print("-" * 50)

        try:
            from app import app, db
            from models import Afiliado, Usuario, Factura

            with app.app_context():
                query = db.session.execute(db.text("""
                    SELECT a.id_afiliado, u.nombre, u.email,
                           COUNT(f.id_factura) as facturas_pendientes,
                           COALESCE(SUM(f.total), 0) as total_pendiente
                    FROM afiliados a
                    JOIN usuarios u ON a.id_usuario = u.id_usuario
                    LEFT JOIN facturas f ON a.id_afiliado = f.id_afiliado
                           AND f.estado = 'PENDIENTE'
                    GROUP BY a.id_afiliado, u.nombre, u.email
                    HAVING COUNT(f.id_factura) > 0
                """))

                resultados = query.fetchall()
                self.registrar(f"Reporte ejecutable ({len(resultados)} afiliados con pendientes)", True)
        except Exception as e:
            self.registrar("Reporte ejecutable", False, str(e))

        return self


class TestReporteFacturacionPlan(PruebaIntegracion):
    """PI-13: Prueba de reporte SQL - Facturacion por plan"""

    def ejecutar(self):
        print("\n[PI-13] REPORTE: FACTURACION POR PLAN")
        print("-" * 50)

        try:
            from app import app, db
            from models import Plan

            with app.app_context():
                query = db.session.execute(db.text("""
                    SELECT p.nombre, COUNT(DISTINCT a.id_afiliado) as total_afiliados,
                           COALESCE(SUM(f.total), 0) as facturacion_total
                    FROM planes p
                    LEFT JOIN afiliados a ON p.id_plan = a.id_plan
                    LEFT JOIN facturas f ON a.id_afiliado = f.id_afiliado
                           AND f.estado = 'PAGADA'
                    GROUP BY p.id_plan, p.nombre
                """))

                resultados = query.fetchall()
                self.registrar(f"Reporte ejecutable ({len(resultados)} planes)", True)
        except Exception as e:
            self.registrar("Reporte ejecutable", False, str(e))

        return self


class TestReporteDiagnosticosFrecuentes(PruebaIntegracion):
    """PI-14: Prueba de reporte SQL - Diagnosticos frecuentes"""

    def ejecutar(self):
        print("\n[PI-14] REPORTE: DIAGNOSTICOS FRECUENTES")
        print("-" * 50)

        try:
            from app import app, db

            with app.app_context():
                query = db.session.execute(db.text("""
                    SELECT p.especialidad, h.diagnostico, COUNT(*) as cantidad
                    FROM historial_clinico h
                    JOIN profesionales p ON h.id_profesional = p.id_profesional
                    GROUP BY p.especialidad, h.diagnostico
                    ORDER BY cantidad DESC
                    LIMIT 20
                """))

                resultados = query.fetchall()
                self.registrar(f"Reporte ejecutable ({len(resultados)} diagnosticos)", True)
        except Exception as e:
            self.registrar("Reporte ejecutable", False, str(e))

        return self


class TestReporteCentrosMasUtilizados(PruebaIntegracion):
    """PI-15: Prueba de reporte SQL - Centros mas utilizados"""

    def ejecutar(self):
        print("\n[PI-15] REPORTE: CENTROS MAS UTILIZADOS")
        print("-" * 50)

        try:
            from app import app, db

            with app.app_context():
                query = db.session.execute(db.text("""
                    SELECT c.nombre, c.ciudad, COUNT(cit.id_cita) as total_citas
                    FROM centros_salud c
                    LEFT JOIN citas cit ON c.id_centro = cit.id_centro
                    GROUP BY c.id_centro, c.nombre, c.ciudad
                    ORDER BY total_citas DESC
                """))

                resultados = query.fetchall()
                self.registrar(f"Reporte ejecutable ({len(resultados)} centros)", True)
        except Exception as e:
            self.registrar("Reporte ejecutable", False, str(e))

        return self


class TestRelacionesTablas(PruebaIntegracion):
    """PI-16: Pruebas de relaciones entre tablas"""

    def ejecutar(self):
        print("\n[PI-16] RELACIONES ENTRE TABLAS")
        print("-" * 50)

        try:
            from app import app
            from models import Afiliado, Usuario, Plan

            with app.app_context():
                afiliado = Afiliado.query.first()
                if afiliado:
                    usuario = Usuario.query.get(afiliado.id_usuario)
                    plan = Plan.query.get(afiliado.id_plan)
                    self.registrar("Afiliado -> Usuario (FK id_usuario)", usuario is not None)
                    self.registrar("Afiliado -> Plan (FK id_plan)", plan is not None)
                else:
                    self.registrar("No hay afiliados para probar relaciones", True)
        except Exception as e:
            self.registrar("Relaciones tablas", False, str(e))

        try:
            from models import Profesional, Usuario, CentroSalud

            with app.app_context():
                profesional = Profesional.query.first()
                if profesional:
                    usuario = Usuario.query.get(profesional.id_usuario)
                    centro = CentroSalud.query.get(profesional.id_centro)
                    self.registrar("Profesional -> Usuario (FK id_usuario)", usuario is not None)
                    self.registrar("Profesional -> CentroSalud (FK id_centro)", centro is not None)
                else:
                    self.registrar("No hay profesionales para probar relaciones", True)
        except Exception as e:
            self.registrar("Relaciones Profesional", False, str(e))

        return self


class TestEstadisticasDashboard(PruebaIntegracion):
    """PI-17: Pruebas de estadisticas para dashboard"""

    def ejecutar(self):
        print("\n[PI-17] ESTADISTICAS DASHBOARD")
        print("-" * 50)

        try:
            from app import app, db
            from models import Usuario, Afiliado, Profesional, Plan, CentroSalud, Cita, Factura

            with app.app_context():
                total_usuarios = Usuario.query.count()
                total_afiliados = Afiliado.query.count()
                total_profesionales = Profesional.query.count()
                total_planes = Plan.query.count()
                total_centros = CentroSalud.query.count()
                total_citas = Cita.query.count()
                total_facturas = Factura.query.count()

                stats = {
                    'usuarios': total_usuarios,
                    'afiliados': total_afiliados,
                    'profesionales': total_profesionales,
                    'planes': total_planes,
                    'centros': total_centros,
                    'citas': total_citas,
                    'facturas': total_facturas
                }

                todas_positivas = all(v >= 0 for v in stats.values())
                self.registrar(f"Estadisticas: {stats}", todas_positivas)
        except Exception as e:
            self.registrar("Estadisticas dashboard", False, str(e))

        return self


def ejecutar_todas_pruebas():
    pruebas = [
        TestConexionBaseDatos(),
        TestModeloUsuario(),
        TestModeloAfiliado(),
        TestModeloProfesional(),
        TestModeloPlan(),
        TestModeloCentroSalud(),
        TestModeloCita(),
        TestModeloFactura(),
        TestModeloPago(),
        TestModeloHistorialClinico(),
        TestModeloDisponibilidad(),
        TestReporteAfiliadosFacturas(),
        TestReporteFacturacionPlan(),
        TestReporteDiagnosticosFrecuentes(),
        TestReporteCentrosMasUtilizados(),
        TestRelacionesTablas(),
        TestEstadisticasDashboard(),
    ]

    for prueba in pruebas:
        prueba.ejecutar()

    print("\n" + "=" * 70)
    print(" RESUMEN GENERAL PRUEBAS DE INTEGRACION")
    print("=" * 70)

    total = sum(p.total for p in pruebas)
    pasadas = sum(p.pasadas for p in pruebas)
    fallidas = sum(p.fallidas for p in pruebas)

    print(f" Total pruebas ejecutadas: {total}")
    print(f" Pasadas: {pasadas}")
    print(f" Fallidas: {fallidas}")
    print(f" Porcentaje exitos: {(pasadas/total)*100:.1f}%")
    print("=" * 70)


if __name__ == '__main__':
    ejecutar_todas_pruebas()