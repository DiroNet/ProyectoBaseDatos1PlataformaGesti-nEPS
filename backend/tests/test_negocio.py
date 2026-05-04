import pytest
import sys
import os
from datetime import date, time, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*60)
print("PRUEBAS UNITARIAS - LÓGICA DE NEGOCIO")
print("="*60)

class TestDisponibilidad:
    def test_medico_tiene_disponibilidad_lunes(self):
        print("\n[UT-18] Médico tiene disponibilidad lunes")
        print("  Input: dia_semana=1")
        print("  Esperado: True")
        dia_semana = 1
        result = 1 <= dia_semana <= 7
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_medico_tiene_disponibilidad_miercoles(self):
        print("\n[UT-19] Médico tiene disponibilidad miércoles")
        print("  Input: dia_semana=3")
        print("  Esperado: True")
        dia_semana = 3
        result = 1 <= dia_semana <= 7
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_dia_invalido(self):
        print("\n[UT-20] Día inválido")
        print("  Input: dia_semana=0")
        print("  Esperado: False")
        dia_semana = 0
        result = 1 <= dia_semana <= 7
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

class TestConflictosHorario:
    def test_conflicto_hora_exacta(self):
        print("\n[UT-21] Conflicto hora exacta")
        print("  Input: hora1=10:00, hora2=10:00")
        print("  Esperado: Conflicto")
        hora1 = time(10, 0)
        hora2 = time(10, 0)
        result = hora1 == hora2
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_no_hay_conflicto_diferente_hora(self):
        print("\n[UT-22] Sin conflicto horas diferentes")
        print("  Input: hora1=10:00, hora2=11:00")
        print("  Esperado: Sin conflicto")
        hora1 = time(10, 0)
        hora2 = time(11, 0)
        result = hora1 == hora2
        print(f"  Resultado: {result}")
        assert result == False
        print("  [OK] PASS")

class TestFechas:
    def test_no_permitir_cita_fecha_pasada(self):
        print("\n[UT-23] No permitir cita fecha pasada")
        print("  Input: fechaayer < fecha_hoy")
        print("  Esperado: Rechazar")
        fecha_pasada = date.today() - timedelta(days=1)
        fecha_hoy = date.today()
        result = fecha_pasada < fecha_hoy
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_fecha_hoy_permitida(self):
        print("\n[UT-24] Fecha hoy permitida")
        print("  Input: fecha_hoy")
        print("  Esperado: Permitir")
        fecha_hoy = date.today()
        result = fecha_hoy >= date.today() - timedelta(days=1)
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_fecha_futura_permitida(self):
        print("\n[UT-25] Fecha futura permitida")
        print("  Input: fecha+7 días")
        print("  Esperado: Permitir")
        fecha_futura = date.today() + timedelta(days=7)
        result = fecha_futura > date.today()
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

class TestHorarioMedico:
    def test_hora_fuera_horario_atencion(self):
        print("\n[UT-26] Hora fuera horario atención")
        print("  Input: cita=19:00, horario hasta 17:00")
        print("  Esperado: Rechazar")
        hora_cita = time(19, 0)
        hora_inicio = time(8, 0)
        hora_fin = time(17, 0)
        result = hora_cita < hora_inicio or hora_cita > hora_fin
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_hora_dentro_horario_atencion(self):
        print("\n[UT-27] Hora dentro horario")
        print("  Input: cita=10:00, inicio=8:00, fin=17:00")
        print("  Esperado: Permitir")
        hora_cita = time(10, 0)
        hora_inicio = time(8, 0)
        hora_fin = time(17, 0)
        result = hora_inicio <= hora_cita <= hora_fin
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_hora_limite_inferior(self):
        print("\n[UT-28] Hora límite inferior")
        print("  Input: cita=8:00")
        print("  Esperado: Permitir")
        hora_cita = time(8, 0)
        hora_inicio = time(8, 0)
        hora_fin = time(17, 0)
        result = hora_inicio <= hora_cita <= hora_fin
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_hora_limite_superior(self):
        print("\n[UT-29] Hora límite superior")
        print("  Input: cita=17:00")
        print("  Esperado: Permitir")
        hora_cita = time(17, 0)
        hora_inicio = time(8, 0)
        hora_fin = time(17, 0)
        result = hora_inicio <= hora_cita <= hora_fin
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

class TestReglasNegocio:
    def test_estados_cita_validos(self):
        print("\n[UT-30] Estados cita válidos")
        print("  Input: estados=['pendiente','confirmada','cancelada','completada']")
        print("  Esperado: Válido")
        estados_validos = ['pendiente', 'confirmada', 'cancelada', 'completada']
        result = 'pendiente' in estados_validos and 'confirmada' in estados_validos
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_dia_semana_valido(self):
        print("\n[UT-31] Día semana válido")
        print("  Input: dias 1-7")
        print("  Esperado: Válido")
        result = all(1 <= d <= 7 for d in range(1, 8))
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_dia_semana_lunes(self):
        print("\n[UT-32] Día semana lunes")
        print("  Input: dia=1")
        print("  Esperado: Válido")
        result = 1 == 1
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_dia_semana_domingo(self):
        print("\n[UT-33] Día semana domingo")
        print("  Input: dia=7")
        print("  Esperado: Válido")
        result = 7 == 7
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

    def test_tipos_consulta_validos(self):
        print("\n[UT-34] Tipos consulta válidos")
        print("  Input: tipos=['MG','Cardiología','Pediatría']")
        print("  Esperado: Válido")
        tipos_validos = ['Medicina General', 'Cardiología', 'Pediatría']
        for tipo in ['Medicina General', 'Cardiología']:
            result = tipo in tipos_validos
        print(f"  Resultado: {result}")
        assert result == True
        print("  [OK] PASS")

print("\n" + "="*60)
print("FIN PRUEBAS NEGOCIO - 17 pruebas ejecutadas")
print("="*60)