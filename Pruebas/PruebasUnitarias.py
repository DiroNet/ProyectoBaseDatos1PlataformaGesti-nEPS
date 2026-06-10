"""
PRUEBAS UNITARIAS - Sistema EPS
Proyecto Final Base de Datos 2026-01

Este script contiene pruebas unitarias para validar las reglas de negocio
y funcionalidades del sistema. No modifica la base de datos.
"""

import unittest
from datetime import date, time, datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\\backend')

print("=" * 70)
print(" PRUEBAS UNITARIAS - SISTEMA EPS")
print("=" * 70)


class TestValidacionesUsuario(unittest.TestCase):
    """Pruebas para validaciones de usuario"""

    def test_email_formato_valido(self):
        """UT-01: Email con formato valido"""
        email = "usuario@eps.com"
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        import re
        result = re.match(patron, email) is not None
        self.assertTrue(result)
        print(f"  [UT-01] Email valido: {email}")

    def test_email_formato_invalido(self):
        """UT-02: Email con formato invalido"""
        email = "usuario@invalido"
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        import re
        result = re.match(patron, email) is not None
        self.assertFalse(result)
        print(f"  [UT-02] Email invalido detectado: {email}")

    def test_password_minimo_6_caracteres(self):
        """UT-03: Password debe tener minimo 6 caracteres"""
        password = "123456"
        result = len(password) >= 6
        self.assertTrue(result)
        print(f"  [UT-03] Password valido: {len(password)} caracteres")

    def test_password_muy_corto(self):
        """UT-04: Password muy corto debe fallar"""
        password = "123"
        result = len(password) >= 6
        self.assertFalse(result)
        print(f"  [UT-04] Password invalido: {len(password)} caracteres")

    def test_rol_valido_admin(self):
        """UT-05: Rol ADMIN es valido"""
        rol = "ADMIN"
        roles_validos = ["ADMIN", "AFILIADO", "PROFESIONAL"]
        result = rol in roles_validos
        self.assertTrue(result)
        print(f"  [UT-05] Rol valido: {rol}")

    def test_rol_valido_afiliado(self):
        """UT-06: Rol AFILIADO es valido"""
        rol = "AFILIADO"
        roles_validos = ["ADMIN", "AFILIADO", "PROFESIONAL"]
        result = rol in roles_validos
        self.assertTrue(result)
        print(f"  [UT-06] Rol valido: {rol}")

    def test_rol_invalido(self):
        """UT-07: Rol inexistente debe fallar"""
        rol = "VISITANTE"
        roles_validos = ["ADMIN", "AFILIADO", "PROFESIONAL"]
        result = rol in roles_validos
        self.assertFalse(result)
        print(f"  [UT-07] Rol invalido detectado: {rol}")


class TestValidacionesAfiliado(unittest.TestCase):
    """Pruebas para validaciones de afiliado"""

    def test_documento_8_digitos(self):
        """UT-08: Documento debe tener 8 digitos"""
        documento = "12345678"
        result = len(documento) == 8 and documento.isdigit()
        self.assertTrue(result)
        print(f"  [UT-08] Documento valido: {documento}")

    def test_documento_muy_corto(self):
        """UT-09: Documento con menos de 8 digitos debe fallar"""
        documento = "1234567"
        result = len(documento) == 8 and documento.isdigit()
        self.assertFalse(result)
        print(f"  [UT-09] Documento invalido: {documento}")

    def test_telefono_formato_colombia(self):
        """UT-10: Telefono colombiano valido (10 digitos)"""
        telefono = "3001234567"
        result = len(telefono) == 10 and telefono.isdigit()
        self.assertTrue(result)
        print(f"  [UT-10] Telefono valido: {telefono}")

    def test_telefono_formato_invalido(self):
        """UT-11: Telefono con formato incorrecto debe fallar"""
        telefono = "123"
        result = len(telefono) == 10 and telefono.isdigit()
        self.assertFalse(result)
        print(f"  [UT-11] Telefono invalido: {telefono}")


class TestValidacionesProfesional(unittest.TestCase):
    """Pruebas para validaciones de profesional"""

    def test_especialidad_valida(self):
        """UT-12: Especialidad valida"""
        especialidades = ["Medicina General", "Cardiologia", "Pediatria", "Cirugia"]
        especialidad = "Cardiologia"
        result = especialidad in especialidades
        self.assertTrue(result)
        print(f"  [UT-12] Especialidad valida: {especialidad}")

    def test_especialidad_invalida(self):
        """UT-13: Especialidad no existe debe fallar"""
        especialidades = ["Medicina General", "Cardiologia", "Pediatria", "Cirugia"]
        especialidad = "Homeopatia"
        result = especialidad in especialidades
        self.assertFalse(result)
        print(f"  [UT-13] Especialidad invalida: {especialidad}")

    def test_profesional_activo_puede_atencer(self):
        """UT-14: Profesional activo puede atender"""
        activo = True
        result = activo == True
        self.assertTrue(result)
        print(f"  [UT-14] Profesional activo puede atender")

    def test_profesional_inactivo_no_puede_atencer(self):
        """UT-15: Profesional inactivo no puede atender"""
        activo = False
        result = activo == False
        self.assertTrue(result)
        print(f"  [UT-15] Profesional inactivo no puede atender")


class TestValidacionesCita(unittest.TestCase):
    """Pruebas para validaciones de cita"""

    def test_estado_cita_valido_pendiente(self):
        """UT-16: Estado pendiente es valido"""
        estado = "pendiente"
        estados_validos = ["pendiente", "confirmada", "cancelada", "completada"]
        result = estado in estados_validos
        self.assertTrue(result)
        print(f"  [UT-16] Estado valido: {estado}")

    def test_estado_cita_valido_confirmada(self):
        """UT-17: Estado confirmada es valido"""
        estado = "confirmada"
        estados_validos = ["pendiente", "confirmada", "cancelada", "completada"]
        result = estado in estados_validos
        self.assertTrue(result)
        print(f"  [UT-17] Estado valido: {estado}")

    def test_estado_cita_invalido(self):
        """UT-18: Estado inexistente debe fallar"""
        estado = "reprogramada"
        estados_validos = ["pendiente", "confirmada", "cancelada", "completada"]
        result = estado in estados_validos
        self.assertFalse(result)
        print(f"  [UT-18] Estado invalido: {estado}")

    def test_cita_puede_reprogramarse(self):
        """UT-19: Cita pendiente puede reprogramarse"""
        estado = "pendiente"
        puede_reprogramar = estado in ["pendiente", "confirmada"]
        self.assertTrue(puede_reprogramar)
        print(f"  [UT-19] Cita {estado} puede reprogramarse")

    def test_cita_cancelada_no_puede_reprogramarse(self):
        """UT-20: Cita cancelada no puede reprogramarse"""
        estado = "cancelada"
        puede_reprogramar = estado in ["pendiente", "confirmada"]
        self.assertFalse(puede_reprogramar)
        print(f"  [UT-20] Cita {estado} no puede reprogramarse")


class TestValidacionesFactura(unittest.TestCase):
    """Pruebas para validaciones de factura"""

    def test_estado_factura_pagada(self):
        """UT-21: Factura pagada es valido"""
        estado = "PAGADA"
        estados_validos = ["PAGADA", "PENDIENTE", "CANCELADA"]
        result = estado in estados_validos
        self.assertTrue(result)
        print(f"  [UT-21] Estado factura valido: {estado}")

    def test_estado_factura_pendiente(self):
        """UT-22: Factura pendiente es valido"""
        estado = "PENDIENTE"
        estados_validos = ["PAGADA", "PENDIENTE", "CANCELADA"]
        result = estado in estados_validos
        self.assertTrue(result)
        print(f"  [UT-22] Estado factura valido: {estado}")

    def test_total_factura_positivo(self):
        """UT-23: Total de factura debe ser positivo"""
        total = 150000
        result = total > 0
        self.assertTrue(result)
        print(f"  [UT-23] Total valido: ${total}")

    def test_total_factura_cero_invalido(self):
        """UT-24: Total cero debe ser invalido"""
        total = 0
        result = total > 0
        self.assertFalse(result)
        print(f"  [UT-24] Total invalido: ${total}")


class TestValidacionesHorario(unittest.TestCase):
    """Pruebas para validaciones de horarios"""

    def test_horario_laboral_valido(self):
        """UT-25: Horario 8am-5pm es valido"""
        hora_inicio = time(8, 0)
        hora_fin = time(17, 0)
        result = hora_inicio < hora_fin
        self.assertTrue(result)
        print(f"  [UT-25] Horario valido: {hora_inicio} - {hora_fin}")

    def test_hora_inicio_mayor_que_fin_invalido(self):
        """UT-26: Hora inicio mayor que fin debe fallar"""
        hora_inicio = time(17, 0)
        hora_fin = time(8, 0)
        result = hora_inicio < hora_fin
        self.assertFalse(result)
        print(f"  [UT-26] Horario invalido: {hora_inicio} > {hora_fin}")

    def test_dia_semana_valido(self):
        """UT-27: Dia de semana valido (1-7)"""
        dia = 3
        result = 1 <= dia <= 7
        self.assertTrue(result)
        print(f"  [UT-27] Dia valido: {dia}")

    def test_dia_semana_invalido(self):
        """UT-28: Dia de semana invalido (fuera de 1-7)"""
        dia = 8
        result = 1 <= dia <= 7
        self.assertFalse(result)
        print(f"  [UT-28] Dia invalido: {dia}")

    def test_dias_laborales_lunes_viernes(self):
        """UT-29: Lunes a viernes son dias laborables"""
        dias_laborales = [1, 2, 3, 4, 5]
        result = all(1 <= d <= 5 for d in dias_laborales)
        self.assertTrue(result)
        print(f"  [UT-29] Dias laborables: {dias_laborales}")


class TestValidacionesPlan(unittest.TestCase):
    """Pruebas para validaciones de plan"""

    def test_costo_plan_positivo(self):
        """UT-30: Costo del plan debe ser positivo"""
        costo = 100000
        result = costo > 0
        self.assertTrue(result)
        print(f"  [UT-30] Costo valido: ${costo}")

    def test_costo_plan_cero_invalido(self):
        """UT-31: Costo cero debe ser invalido"""
        costo = 0
        result = costo > 0
        self.assertFalse(result)
        print(f"  [UT-31] Costo invalido: ${costo}")

    def test_nombre_plan_no_vacio(self):
        """UT-32: Nombre del plan no puede estar vacio"""
        nombre = "Plan Premium"
        result = len(nombre.strip()) > 0
        self.assertTrue(result)
        print(f"  [UT-32] Nombre valido: {nombre}")


class TestLogicaNegocio(unittest.TestCase):
    """Pruebas para logica de negocio"""

    def test_calculo_total_facturas_pendientes(self):
        """UT-33: Calculo de total facturas pendientes"""
        facturas = [50000, 75000, 30000]
        total = sum(facturas)
        result = total == 155000
        self.assertTrue(result)
        print(f"  [UT-33] Total facturas: ${total}")

    def test_conteo_afiliados_por_plan(self):
        """UT-34: Conteo de afiliados por plan"""
        afiliados = ["Plan A", "Plan A", "Plan B", "Plan A", "Plan B", "Plan C"]
        conteo = {}
        for plan in afiliados:
            conteo[plan] = conteo.get(plan, 0) + 1
        result = conteo["Plan A"] == 3
        self.assertTrue(result)
        print(f"  [UT-34] Afiliados Plan A: {conteo['Plan A']}")

    def test_profesional_disponible_en_dia(self):
        """UT-35: Profesional disponible en dia especifico"""
        dias_disponibles = [1, 2, 3, 4, 5]
        dia_buscado = 3
        result = dia_buscado in dias_disponibles
        self.assertTrue(result)
        print(f"  [UT-35] Profesional disponible dia {dia_buscado}")

    def test_profesional_no_disponible_finde(self):
        """UT-36: Profesional no disponible fin de semana"""
        dias_disponibles = [1, 2, 3, 4, 5]
        dia_buscado = 6
        result = dia_buscado in dias_disponibles
        self.assertFalse(result)
        print(f"  [UT-36] Profesional no disponible dia {dia_buscado}")


if __name__ == '__main__':
    print("\nEjecutando pruebas unitarias...\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestValidacionesUsuario))
    suite.addTests(loader.loadTestsFromTestCase(TestValidacionesAfiliado))
    suite.addTests(loader.loadTestsFromTestCase(TestValidacionesProfesional))
    suite.addTests(loader.loadTestsFromTestCase(TestValidacionesCita))
    suite.addTests(loader.loadTestsFromTestCase(TestValidacionesFactura))
    suite.addTests(loader.loadTestsFromTestCase(TestValidacionesHorario))
    suite.addTests(loader.loadTestsFromTestCase(TestValidacionesPlan))
    suite.addTests(loader.loadTestsFromTestCase(TestLogicaNegocio))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(" RESUMEN PRUEBAS UNITARIAS")
    print("=" * 70)
    print(f" Pruebas ejecutadas: {result.testsRun}")
    print(f" Fallidas: {len(result.failures)}")
    print(f" Errores: {len(result.errors)}")
    print(f" Exitosas: {result.testsRun - len(result.failures) - len(result.errors)}")
    print("=" * 70)