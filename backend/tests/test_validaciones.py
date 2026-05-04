import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import validate_email, validate_time

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

print("\n" + "="*60)
print("FIN PRUEBAS VALIDACIONES - 17 pruebas ejecutadas")
print("="*60)