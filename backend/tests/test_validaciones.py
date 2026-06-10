import pytest
import sys
import os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import validate_email, validate_time, validate_documento, validate_telefono_co, validate_fecha_nacimiento

print("="*60)
print("PRUEBAS UNITARIAS - VALIDACIONES")
print("="*60)

class TestValidacionesEmail:
    def test_email_formato_valido(self):
        print("\n[UT-01] Email formato válido")
        print("  Input: 'paciente@test.com'")
        print("  Esperado: True")
        result = validate_email("paciente@test.com")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")
    
    def test_email_valido_con_punto(self):
        print("\n[UT-02] Email válido con punto")
        print("  Input: 'juan.perez@hospital.co'")
        print("  Esperado: True")
        result = validate_email("juan.perez@hospital.co")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")
    
    def test_email_valido_gmail(self):
        print("\n[UT-03] Email válido Gmail")
        print("  Input: 'usuario@gmail.com'")
        print("  Esperado: True")
        result = validate_email("usuario@gmail.com")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")
    
    def test_email_invalido_sin_arrobma(self):
        print("\n[UT-04] Email inválido sin @")
        print("  Input: 'pacientetest.com'")
        print("  Esperado: False")
        result = validate_email("pacientetest.com")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")
    
    def test_email_invalido_sin_dominio(self):
        print("\n[UT-05] Email inválido sin dominio")
        print("  Input: 'paciente@'")
        print("  Esperado: False")
        result = validate_email("paciente@")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")
    
    def test_email_invalido_vacio(self):
        print("\n[UT-06] Email inválido vacío")
        print("  Input: '' (vacío)")
        print("  Esperado: False")
        result = validate_email("")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")
    
    def test_email_invalido_sin_extension(self):
        print("\n[UT-07] Email inválido sin extensión")
        print("  Input: 'test@dominio'")
        print("  Esperado: False")
        result = validate_email("test@dominio")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

class TestValidacionesHora:
    def test_hora_valida_inicio_6am(self):
        print("\n[UT-08] Hora válida inicio 6am")
        print("  Input: '06:00'")
        print("  Esperado: True")
        result = validate_time("06:00")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")
    
    def test_hora_valida_fin_8pm(self):
        print("\n[UT-09] Hora válida fin 8pm")
        print("  Input: '20:00'")
        print("  Esperado: True")
        result = validate_time("20:00")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")
    
    def test_hora_valida_media_jornada(self):
        print("\n[UT-10] Hora válida media jornada")
        print("  Input: '14:30'")
        print("  Esperado: True")
        result = validate_time("14:30")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")
    
    def test_hora_valida_12pm(self):
        print("\n[UT-11] Hora válida 12pm")
        print("  Input: '12:00'")
        print("  Esperado: True")
        result = validate_time("12:00")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")
    
    def test_hora_invalida_antes_6am(self):
        print("\n[UT-12] Hora inválida antes 6am")
        print("  Input: '05:30'")
        print("  Esperado: False")
        result = validate_time("05:30")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")
    
    def test_hora_invalida_despues_8pm(self):
        print("\n[UT-13] Hora inválida después 8pm")
        print("  Input: '20:30'")
        print("  Esperado: False")
        result = validate_time("20:30")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")
    
    def test_hora_invalida_5am(self):
        print("\n[UT-14] Hora inválida 5am")
        print("  Input: '05:00'")
        print("  Esperado: False")
        result = validate_time("05:00")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")
    
    def test_hora_invalida_9pm(self):
        print("\n[UT-15] Hora inválida 9pm")
        print("  Input: '21:00'")
        print("  Esperado: False")
        result = validate_time("21:00")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")
    
    def test_hora_formato_invalido(self):
        print("\n[UT-16] Hora formato inválido")
        print("  Input: '8am'")
        print("  Esperado: False")
        result = validate_time("8am")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")
    
    def test_hora_formato_invalido_letras(self):
        print("\n[UT-17] Hora formato letras")
        print("  Input: 'abc'")
        print("  Esperado: False")
        result = validate_time("abc")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

class TestValidacionesCedula:
    def test_cedula_valida_8_digitos(self):
        print("\n[UT-C01] Cédula válida 8 dígitos")
        print("  Input: '12345678'")
        print("  Esperado: True")
        result = validate_documento("12345678")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_cedula_valida_6_digitos_minimo(self):
        print("\n[UT-C02] Cédula válida 6 dígitos (mínimo)")
        print("  Input: '123456'")
        print("  Esperado: True")
        result = validate_documento("123456")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_cedula_valida_10_digitos_maximo(self):
        print("\n[UT-C03] Cédula válida 10 dígitos (máximo)")
        print("  Input: '1234567890'")
        print("  Esperado: True")
        result = validate_documento("1234567890")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_cedula_invalida_con_letras(self):
        print("\n[UT-C04] Cédula inválida con letras")
        print("  Input: 'ABC12345'")
        print("  Esperado: False")
        result = validate_documento("ABC12345")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

    def test_cedula_invalida_muy_corta(self):
        print("\n[UT-C05] Cédula inválida muy corta (< 6 dígitos)")
        print("  Input: '12345'")
        print("  Esperado: False")
        result = validate_documento("12345")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

    def test_cedula_invalida_muy_larga(self):
        print("\n[UT-C06] Cédula inválida muy larga (> 10 dígitos)")
        print("  Input: '12345678901'")
        print("  Esperado: False")
        result = validate_documento("12345678901")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

    def test_cedula_invalida_vacia(self):
        print("\n[UT-C07] Cédula inválida vacía")
        print("  Input: ''")
        print("  Esperado: False")
        result = validate_documento("")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

    def test_cedula_invalida_con_espacios(self):
        print("\n[UT-C08] Cédula inválida con espacios")
        print("  Input: '1234 5678'")
        print("  Esperado: False")
        result = validate_documento("1234 5678")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")


class TestValidacionesTelefonoColombia:
    def test_telefono_valido_empieza_3(self):
        print("\n[UT-T01] Teléfono válido empieza con 3")
        print("  Input: '3001234567'")
        print("  Esperado: True")
        result = validate_telefono_co("3001234567")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_telefono_valido_operador_claro(self):
        print("\n[UT-T02] Teléfono válido Claro (310)")
        print("  Input: '3101234567'")
        print("  Esperado: True")
        result = validate_telefono_co("3101234567")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_telefono_valido_operador_movistar(self):
        print("\n[UT-T03] Teléfono válido Movistar (320)")
        print("  Input: '3201234567'")
        print("  Esperado: True")
        result = validate_telefono_co("3201234567")
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_telefono_invalido_empieza_con_1(self):
        print("\n[UT-T04] Teléfono inválido no empieza con 3")
        print("  Input: '1001234567'")
        print("  Esperado: False")
        result = validate_telefono_co("1001234567")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

    def test_telefono_invalido_menos_digitos(self):
        print("\n[UT-T05] Teléfono inválido menos de 10 dígitos")
        print("  Input: '300123456'")
        print("  Esperado: False")
        result = validate_telefono_co("300123456")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

    def test_telefono_invalido_mas_digitos(self):
        print("\n[UT-T06] Teléfono inválido más de 10 dígitos")
        print("  Input: '30012345678'")
        print("  Esperado: False")
        result = validate_telefono_co("30012345678")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

    def test_telefono_invalido_con_letras(self):
        print("\n[UT-T07] Teléfono inválido con letras")
        print("  Input: '300ABC4567'")
        print("  Esperado: False")
        result = validate_telefono_co("300ABC4567")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

    def test_telefono_invalido_vacio(self):
        print("\n[UT-T08] Teléfono inválido vacío")
        print("  Input: ''")
        print("  Esperado: False")
        result = validate_telefono_co("")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")


class TestValidacionesFechaNacimiento:
    def test_fecha_nacimiento_valida_pasado(self):
        print("\n[UT-F01] Fecha de nacimiento válida (pasado)")
        fecha = (date.today() - timedelta(days=365 * 25)).strftime('%Y-%m-%d')
        print(f"  Input: '{fecha}' (hace 25 años)")
        print("  Esperado: True")
        result = validate_fecha_nacimiento(fecha)
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_fecha_nacimiento_valida_hoy(self):
        print("\n[UT-F02] Fecha de nacimiento válida (hoy)")
        fecha = date.today().strftime('%Y-%m-%d')
        print(f"  Input: '{fecha}' (hoy)")
        print("  Esperado: True")
        result = validate_fecha_nacimiento(fecha)
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_fecha_nacimiento_invalida_futuro(self):
        print("\n[UT-F03] Fecha de nacimiento inválida (futuro)")
        fecha = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"  Input: '{fecha}' (mañana)")
        print("  Esperado: False")
        result = validate_fecha_nacimiento(fecha)
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

    def test_fecha_nacimiento_invalida_futuro_lejano(self):
        print("\n[UT-F04] Fecha de nacimiento inválida (futuro lejano)")
        fecha = (date.today() + timedelta(days=365 * 5)).strftime('%Y-%m-%d')
        print(f"  Input: '{fecha}' (5 años futuro)")
        print("  Esperado: False")
        result = validate_fecha_nacimiento(fecha)
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

    def test_fecha_nacimiento_invalida_vacia(self):
        print("\n[UT-F05] Fecha de nacimiento inválida (vacía)")
        print("  Input: ''")
        print("  Esperado: False")
        result = validate_fecha_nacimiento("")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

    def test_fecha_nacimiento_invalida_formato_incorrecto(self):
        print("\n[UT-F06] Fecha de nacimiento inválida (formato incorrecto)")
        print("  Input: '31/12/1990'")
        print("  Esperado: False")
        result = validate_fecha_nacimiento("31/12/1990")
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

    def test_fecha_nacimiento_valida_adulto_mayor(self):
        print("\n[UT-F07] Fecha de nacimiento válida (adulto mayor)")
        fecha = "1940-06-15"
        print(f"  Input: '{fecha}'")
        print("  Esperado: True")
        result = validate_fecha_nacimiento(fecha)
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")


print("\n" + "="*60)
print("FIN PRUEBAS VALIDACIONES - 17 + 8 cedula + 8 telefono + 7 fecha = 40 pruebas")
print("="*60)