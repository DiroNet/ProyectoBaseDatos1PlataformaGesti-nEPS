"""
Pruebas de Integración - Sistema de Citas Médicas
Punto 2 del Proyecto Final
Flujo completo: Registro -> Login -> Solicitar cita -> Confirmar
"""
import requests
import time

BASE_URL = "http://localhost:5000"
RESULTADOS = []

def test_01_registro_paciente():
    """PI-01: Registro de nuevo paciente en el sistema"""
    print("\n" + "="*50)
    print("PI-01: REGISTRO DE PACIENTE")
    print("---")
    
    # Datos de entrada específicos para el sistema
    timestamp = int(time.time())
    datos = {
        "email": f"juan_perez_{timestamp}@gmail.com",
        "password": "password123",
        "nombre": "Juan",
        "apellido": "Pérez",
        "telefono": "3001234567",
        "rol": "paciente",
        "cedula": f"100000{timestamp}",
        "fecha_nacimiento": "1990-05-15",
        "direccion": "Carrera 10 #20-30, Bogotá"
    }
    
    print("Datos de entrada:")
    print(f"  - Email: {datos['email']}")
    print(f"  - Nombre: {datos['nombre']} {datos['apellido']}")
    print(f"  - Cédula: {datos['cedula']}")
    print(f"  - Teléfono: {datos['telefono']}")
    print(f"  - Fecha nacimiento: {datos['fecha_nacimiento']}")
    print(f"  - Dirección: {datos['direccion']}")
    print("\nResultado esperado: Usuario creado exitosamente (status 201)")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=datos, timeout=10)
        print(f"Resultado real: Status {response.status_code}")
        
        if response.status_code == 201:
            resultado = response.json()
            print(f"  - Usuario ID: {resultado.get('usuario_id')}")
            print(f"  - Mensaje: {resultado.get('message')}")
            print("[OK] PASS - PI-01")
            RESULTADOS.append({"id": "PI-01", "nombre": "Registro paciente", "estado": "PASS"})
            return datos['email'], datos['password']
        else:
            resultado = response.json()
            print(f"  - Error: {resultado.get('error')}")
            print("[X] FAIL - PI-01")
            RESULTADOS.append({"id": "PI-01", "nombre": "Registro paciente", "estado": "FAIL"})
            return None, None
    except Exception as e:
        print(f"Error de conexión: {e}")
        print("[X] FAIL - PI-01")
        RESULTADOS.append({"id": "PI-01", "nombre": "Registro paciente", "estado": "FAIL"})
        return None, None

def test_02_login_paciente():
    """PI-02: Login de paciente existente"""
    print("\n" + "="*50)
    print("PI-02: LOGIN DE PACIENTE")
    print("---")
    
    # Usar paciente de prueba ya registrado
    datos = {
        "email": "paciente@test.com",
        "password": "paciente123"
    }
    
    print("Datos de entrada:")
    print(f"  - Email: {datos['email']}")
    print(f"  - Password: {datos['password']}")
    print("\nResultado esperado: Token JWT recibido (status 200)")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=datos, timeout=10)
        print(f"Resultado real: Status {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            token = resultado.get('token')
            usuario = resultado.get('usuario', {})
            print(f"  - Token recibido: {token[:20]}...")
            print(f"  - Usuario: {usuario.get('nombre')} {usuario.get('apellido')}")
            print(f"  - Rol: {usuario.get('rol_nombre')}")
            print("[OK] PASS - PI-02")
            RESULTADOS.append({"id": "PI-02", "nombre": "Login paciente", "estado": "PASS"})
            return token
        else:
            resultado = response.json()
            print(f"  - Error: {resultado.get('error')}")
            print("[X] FAIL - PI-02")
            RESULTADOS.append({"id": "PI-02", "nombre": "Login paciente", "estado": "FAIL"})
            return None
    except Exception as e:
        print(f"Error: {e}")
        RESULTADOS.append({"id": "PI-02", "nombre": "Login paciente", "estado": "FAIL"})
        return None

def test_03_solicitar_cita(token):
    """PI-03: Paciente solicita cita médica"""
    print("\n" + "="*50)
    print("PI-03: SOLICITAR CITA MÉDICA")
    print("---")
    
    from datetime import date, timedelta
    
    # Fecha válida: 5 días en el futuro para evitar conflictos
    fecha_futura = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
    
    # Usar médico 1 que tiene disponibilidad
    # Obtener día de mañana (asegurarse que sea laborable)
    from datetime import date, timedelta
    manana = date.today() + timedelta(days=2)  # 2 días en el futuro
    
    datos = {
        "medico_id": 1,
        "fecha": manana.isoformat(),
        "hora": "11:00",  # Hora 11am (no usada)
        "tipo_consulta": "Medicina General"
    }
    
    print("Datos de entrada:")
    print(f"  - Médico ID: {datos['medico_id']}")
    print(f"  - Fecha: {fecha_futura} (fecha futura)")
    print(f"  - Hora: {datos['hora']} (dentro de horario 6am-8pm)")
    print(f"  - Tipo consulta: {datos['tipo_consulta']}")
    print("\nResultado esperado: Cita creada con estado 'pendiente' (status 201)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/citas", json=datos, headers=headers, timeout=10)
        print(f"Resultado real: Status {response.status_code}")
        
        if response.status_code == 201:
            resultado = response.json()
            print(f"  - Cita ID: {resultado.get('id')}")
            print(f"  - Estado: {resultado.get('estado')}")
            print(f"  - Fecha: {resultado.get('fecha')}")
            print(f"  - Hora: {resultado.get('hora')}")
            print("[OK] PASS - PI-03")
            RESULTADOS.append({"id": "PI-03", "nombre": "Solicitar cita", "estado": "PASS"})
            return resultado.get('id')
        else:
            resultado = response.json()
            print(f"  - Error: {resultado.get('error')}")
            print("[X] FAIL - PI-03")
            RESULTADOS.append({"id": "PI-03", "nombre": "Solicitar cita", "estado": "FAIL"})
            return None
    except Exception as e:
        print(f"Error: {e}")
        RESULTADOS.append({"id": "PI-03", "nombre": "Solicitar cita", "estado": "FAIL"})
        return None

def test_04_ver_citas(token):
    """PI-04: Paciente visualiza sus citas"""
    print("\n" + "="*50)
    print("PI-04: VER CITAS DEL PACIENTE")
    print("---")
    
    print("Datos de entrada:")
    print("  - Token JWT del paciente autenticado")
    print("\nResultado esperado: Lista de citas (status 200)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/citas", headers=headers, timeout=10)
        print(f"Resultado real: Status {response.status_code}")
        
        if response.status_code == 200:
            citas = response.json()
            print(f"  - Total citas: {len(citas)}")
            for cita in citas[:3]:
                print(f"    * Cita ID {cita.get('id')}: {cita.get('fecha')} {cita.get('hora')} - {cita.get('estado')}")
            print("[OK] PASS - PI-04")
            RESULTADOS.append({"id": "PI-04", "nombre": "Ver citas paciente", "estado": "PASS"})
            return True
        else:
            resultado = response.json()
            print(f"  - Error: {resultado.get('error')}")
            print("[X] FAIL - PI-04")
            RESULTADOS.append({"id": "PI-04", "nombre": "Ver citas paciente", "estado": "FAIL"})
            return False
    except Exception as e:
        print(f"Error: {e}")
        RESULTADOS.append({"id": "PI-04", "nombre": "Ver citas paciente", "estado": "FAIL"})
        return False

def test_05_login_medico():
    """PI-05: Login de médico"""
    print("\n" + "="*50)
    print("PI-05: LOGIN DE MÉDICO")
    print("---")
    
    datos = {
        "email": "medico@test.com",
        "password": "medico123"
    }
    
    print("Datos de entrada:")
    print(f"  - Email: {datos['email']}")
    print(f"  - Password: {datos['password']}")
    print("\nResultado esperado: Token JWT recibido (status 200)")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=datos, timeout=10)
        print(f"Resultado real: Status {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            token = resultado.get('token')
            usuario = resultado.get('usuario', {})
            print(f"  - Token recibido: {token[:20]}...")
            print(f"  - Médico: {usuario.get('nombre')} {usuario.get('apellido')}")
            print(f"  - Especialidad: {usuario.get('especialidad')}")
            print("[OK] PASS - PI-05")
            RESULTADOS.append({"id": "PI-05", "nombre": "Login médico", "estado": "PASS"})
            return token
        else:
            resultado = response.json()
            print(f"  - Error: {resultado.get('error')}")
            print("[X] FAIL - PI-05")
            RESULTADOS.append({"id": "PI-05", "nombre": "Login médico", "estado": "FAIL"})
            return None
    except Exception as e:
        print(f"Error: {e}")
        RESULTADOS.append({"id": "PI-05", "nombre": "Login médico", "estado": "FAIL"})
        return None

def test_06_confirmar_cita(token, cita_id):
    """PI-06: Médico confirma cita"""
    print("\n" + "="*50)
    print("PI-06: CONFIRMAR CITA POR MÉDICO")
    print("---")
    
    datos = {"estado": "confirmada"}
    
    print("Datos de entrada:")
    print(f"  - Cita ID: {cita_id}")
    print(f"  - Nuevo estado: 'confirmada'")
    print("\nResultado esperado: Cita confirmada (status 200)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.put(f"{BASE_URL}/api/citas/{cita_id}", json=datos, headers=headers, timeout=10)
        print(f"Resultado real: Status {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"  - Cita ID: {resultado.get('id')}")
            print(f"  - Estado actualizado: {resultado.get('estado')}")
            print("[OK] PASS - PI-06")
            RESULTADOS.append({"id": "PI-06", "nombre": "Confirmar cita", "estado": "PASS"})
            return True
        else:
            resultado = response.json()
            print(f"  - Error: {resultado.get('error')}")
            print("[X] FAIL - PI-06")
            RESULTADOS.append({"id": "PI-06", "nombre": "Confirmar cita", "estado": "FAIL"})
            return False
    except Exception as e:
        print(f"Error: {e}")
        RESULTADOS.append({"id": "PI-06", "nombre": "Confirmar cita", "estado": "FAIL"})
        return False

def test_07_cancelar_cita(token, cita_id):
    """PI-07: Paciente Cancela cita"""
    print("\n" + "="*50)
    print("PI-07: CANCELAR CITA POR PACIENTE")
    print("---")
    
    datos = {"estado": "cancelada"}
    
    print("Datos de entrada:")
    print(f"  - Cita ID: {cita_id}")
    print(f"  - Nuevo estado: 'cancelada'")
    print("\nResultado esperado: Cita cancelada (status 200)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.put(f"{BASE_URL}/api/citas/{cita_id}", json=datos, headers=headers, timeout=10)
        print(f"Resultado real: Status {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"  - Cita ID: {resultado.get('id')}")
            print(f"  - Estado actualizado: {resultado.get('estado')}")
            print("[OK] PASS - PI-07")
            RESULTADOS.append({"id": "PI-07", "nombre": "Cancelar cita", "estado": "PASS"})
            return True
        else:
            resultado = response.json()
            print(f"  - Error: {resultado.get('error')}")
            print("[X] FAIL - PI-07")
            RESULTADOS.append({"id": "PI-07", "nombre": "Cancelar cita", "estado": "FAIL"})
            return False
    except Exception as e:
        print(f"Error: {e}")
        RESULTADOS.append({"id": "PI-07", "nombre": "Cancelar cita", "estado": "FAIL"})
        return False

def verificar_backend():
    """Verificar conexión con backend"""
    print("\nVerificando conexión con backend...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Conexión exitosa: {data.get('message')}")
            return True
    except Exception as e:
        print(f"ERROR: No se puede conectar al backend")
        print(f"Detalles: {e}")
        print("\nAsegúrate que el backend esté corriendo en puerto 5000")
        print("Ejecuta: python app.py")
    return False

def mostrar_resumen():
    """Mostrar resumen de resultados"""
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS DE INTEGRACIÓN")
    print("="*60)
    
    for r in RESULTADOS:
        estado = r['estado']
        print(f"  [{estado}] {r['id']}: {r['nombre']}")
    
    passed = sum(1 for r in RESULTADOS if r['estado'] == 'PASS')
    total = len(RESULTADOS)
    print(f"\nTotal: {passed}/{total} pruebas pasaron")

if __name__ == "__main__":
    print("="*60)
    print("PRUEBAS DE INTEGRACIÓN")
    print("Sistema de Citas Médicas - Proyecto Final")
    print("="*60)
    
    if not verificar_backend():
        exit(1)
    
    print("\n" + "="*60)
    print("EJECUTANDO FLUJO DE INTEGRACIÓN")
    print("="*60)
    
    # PI-01: Registro de nuevo paciente (crea datos únicos)
    test_01_registro_paciente()
    
    # PI-02: Login con paciente existente (datos prueba)
    token_paciente = test_02_login_paciente()
    
    if token_paciente:
        # PI-03: Solicitar cita
        cita_id = test_03_solicitar_cita(token_paciente)
        
        # PI-04: Ver citas
        test_04_ver_citas(token_paciente)
        
        if cita_id:
            # PI-05: Login médico
            token_medico = test_05_login_medico()
            
            if token_medico:
                # PI-06: Confirmar cita
                test_06_confirmar_cita(token_medico, cita_id)
                
                # PI-07: Cancelar cita con paciente
                test_07_cancelar_cita(token_paciente, cita_id)
    
    # PI-07: Cancelar cita con paciente (si hay cita disponible)
    mostrar_resumen()