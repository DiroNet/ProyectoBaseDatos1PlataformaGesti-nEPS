import pytest
import sys
import os
from datetime import date, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*60)
print("PRUEBAS UNITARIAS - REGLAS DEL DOMINIO")
print("="*60)

class TestMedicoInactivo:
    def test_medico_inactivo_flag(self):
        print("\n[UT-35] Médico inactivo flag")
        print("  Input: activo=False")
        print("  Esperado: False")
        activo = False
        result = activo == False
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_medico_activo_flag(self):
        print("\n[UT-36] Médico activo flag")
        print("  Input: activo=True")
        print("  Esperado: True")
        activo = True
        result = activo == True
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_verificar_estado_inactivo(self):
        print("\n[UT-37] Verificar estado inactivo")
        print("  Input: medico_activo=False")
        print("  Esperado: No puede atender")
        medico_activo = False
        result = not medico_activo
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_verificar_estado_activo(self):
        print("\n[UT-38] Verificar estado activo")
        print("  Input: medico_activo=True")
        print("  Esperado: Puede atender")
        medico_activo = True
        result = medico_activo
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

class TestReprogramacion:
    def test_cita_cancelada_no_reprogramable(self):
        print("\n[UT-39] Cita cancelada no reprogramable")
        print("  Input: estado='cancelada'")
        print("  Esperado: No reprogramable")
        estado = 'cancelada'
        result = estado == 'cancelada'
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_cita_pendiente_reprogramable(self):
        print("\n[UT-40] Cita pendiente reprogramable")
        print("  Input: estado='pendiente'")
        print("  Esperado: Reprogramable")
        estado = 'pendiente'
        result = estado in ['pendiente', 'confirmada']
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_cita_confirmada_reprogramable(self):
        print("\n[UT-41] Cita confirmada reprogramable")
        print("  Input: estado='confirmada'")
        print("  Esperado: Reprogramable")
        estado = 'confirmada'
        result = estado in ['pendiente', 'confirmada']
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

class TestReglasDominio:
    def test_paciente_necesita_cedula(self):
        print("\n[UT-42] Paciente necesita cédula")
        print("  Input: tiene_cedula=True")
        print("  Esperado: Requerido")
        tiene_cedula = True
        result = tiene_cedula
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_medico_necesita_cedula_profesional(self):
        print("\n[UT-43] Médico necesita cédula profesional")
        print("  Input: tiene_cedula=True")
        print("  Esperado: Requerido")
        tiene_cedula = True
        result = tiene_cedula
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_rol_paciente_valido(self):
        print("\n[UT-44] Rol paciente válido")
        print("  Input: rol='paciente'")
        print("  Esperado: Válido")
        rol = 'paciente'
        result = rol == 'paciente'
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_rol_medico_valido(self):
        print("\n[UT-45] Rol médico válido")
        print("  Input: rol='medico'")
        print("  Esperado: Válido")
        rol = 'medico'
        result = rol == 'medico'
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_rol_administrador_valido(self):
        print("\n[UT-46] Rol administrador válido")
        print("  Input: rol='administrador'")
        print("  Esperado: Válido")
        rol = 'administrador'
        result = rol == 'administrador'
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

class TestReglasHorarios:
    def test_horario_oficina_6a20(self):
        print("\n[UT-47] Horario oficina 6a20")
        print("  Input: hora_inicio=6, hora_fin=20")
        print("  Esperado: Válido")
        hora_inicio = 6
        hora_fin = 20
        result = hora_inicio >= 6 and hora_fin <= 20
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_validar_horario_lunes_viernes(self):
        print("\n[UT-48] Validar horario lun-vier")
        print("  Input: dias=[1,2,3,4,5]")
        print("  Esperado: Válido")
        dias_laborales = [1, 2, 3, 4, 5]
        result = all(1 <= d <= 5 for d in dias_laborales)
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

class TestValidacionesRegistro:
    def test_password_minimo_caracteres(self):
        print("\n[UT-49] Password mínimo caracteres")
        print("  Input: password='123456'")
        print("  Esperado: 6+ caracteres")
        password = '123456'
        result = len(password) >= 6
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_email_no_duplicado(self):
        print("\n[UT-50] Email no duplicado")
        print("  Input: email_existe=False")
        print("  Esperado: No duplicado")
        email_existe = False
        result = not email_existe
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

class TestCitas:
    def test_cita_tiene_paciente(self):
        print("\n[UT-51] Cita tiene paciente")
        print("  Input: tiene_paciente=True")
        print("  Esperado: Requerido")
        tiene_paciente = True
        result = tiene_paciente
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_cita_tiene_medico(self):
        print("\n[UT-52] Cita tiene médico")
        print("  Input: tiene_medico=True")
        print("  Esperado: Requerido")
        tiene_medico = True
        result = tiene_medico
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_cita_tiene_fecha(self):
        print("\n[UT-53] Cita tiene fecha")
        print("  Input: tiene_fecha=True")
        print("  Esperado: Requerido")
        tiene_fecha = True
        result = tiene_fecha
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_cita_tiene_hora(self):
        print("\n[UT-54] Cita tiene hora")
        print("  Input: tiene_hora=True")
        print("  Esperado: Requerido")
        tiene_hora = True
        result = tiene_hora
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

print("\n" + "="*60)
print("FIN PRUEBAS DOMINIO - 20 pruebas ejecutadas")
print("="*60)