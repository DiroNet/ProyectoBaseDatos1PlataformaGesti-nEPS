"""
Pruebas E2E Manual - Sistema de Citas Médicas
Sin Selenium - Usa el navegador manualmente
Punto 4 del Proyecto Final
"""

print("="*60)
print("PRUEBAS E2E MANUAL")
print("Sistema de Citas Médicas")
print("="*60)
print("""
INSTRUCCIONES:
1. Asegúrate que el frontend esté corriendo en http://localhost:4200
2. Asegúrate que el backend esté corriendo en http://localhost:5000
3. Sigue los pasos manualmente y marca OK o FAIL

""")

# ========================================
# CASOS DE PRUEBA E2E
# ========================================

casos = [
    {
        "id": "E2E-01",
        "nombre": "Página principal carga",
        "pasos": [
            "1. Abrir navegador Firefox",
            "2. Ir a http://localhost:4200",
            "3. Verificar que aparece la página de login"
        ],
        "esperado": "Página de login visible"
    },
    {
        "id": "E2E-02", 
        "nombre": "Login como paciente",
        "pasos": [
            "1. En campo email: paciente@test.com",
            "2. En campo password: paciente123",
            "3. Click en 'Iniciar sesión'"
        ],
        "esperado": "Redirige al dashboard del paciente"
    },
    {
        "id": "E2E-03",
        "nombre": "Ver mis citas",
        "pasos": [
            "1. Estar en dashboard paciente",
            "2. Buscar sección 'Mis Citas'",
            "3. Verificar que muestra las citas"
        ],
        "esperado": "Lista de citas del paciente"
    },
    {
        "id": "E2E-04",
        "nombre": "Agendar nueva cita",
        "pasos": [
            "1. Click en 'Agendar Cita'",
            "2. Seleccionar médico",
            "3. Seleccionar fecha y hora",
            "4. Click en 'Guardar'"
        ],
        "esperado": "Cita creada exitosamente"
    },
    {
        "id": "E2E-05",
        "nombre": "Cancelar cita",
        "pasos": [
            "1. En Mis Citas, buscar una cita",
            "2. Click en 'Cancelar'",
            "3. Confirmar cancelación"
        ],
        "esperado": "Cita cambia a estado cancelada"
    },
    {
        "id": "E2E-06",
        "nombre": "Logout paciente",
        "pasos": [
            "1. Click en botón de logout/salir",
            "2. Confirmar salida"
        ],
        "esperado": "Regresa a página de login"
    },
    {
        "id": "E2E-07",
        "nombre": "Login como médico",
        "pasos": [
            "1. Ir a http://localhost:4200",
            "2. Email: medico@test.com",
            "3. Password: medico123",
            "4. Click en 'Iniciar sesión'"
        ],
        "esperado": "Dashboard del médico"
    },
    {
        "id": "E2E-08",
        "nombre": "Ver agenda médica",
        "pasos": [
            "1. Estar en dashboard médico",
            "2. Buscar sección 'Citas' o 'Agenda'"
        ],
        "esperado": "Lista de citas de pacientes"
    },
    {
        "id": "E2E-09",
        "nombre": "Confirmar cita médica",
        "pasos": [
            "1. En agenda, buscar cita pendiente",
            "2. Click en 'Confirmar'"
        ],
        "esperado": "Cita cambia a confirmada"
    },
    {
        "id": "E2E-10",
        "nombre": "Registrar historial médico",
        "pasos": [
            "1. Seleccionar paciente",
            "2. Llenar diagnóstico",
            "3. Llenar tratamiento",
            "4. Click en 'Guardar'"
        ],
        "esperado": "Historial guardado"
    },
    {
        "id": "E2E-11",
        "nombre": "Logout médico",
        "pasos": [
            "1. Click en logout"
        ],
        "esperado": "Regresa a login"
    },
    {
        "id": "E2E-12",
        "nombre": "Login como administrador",
        "pasos": [
            "1. Ir a http://localhost:4200",
            "2. Email: admin@hospital.com",
            "3. Password: admin123"
        ],
        "esperado": "Dashboard administrador"
    },
    {
        "id": "E2E-13",
        "nombre": "Gestión de usuarios",
        "pasos": [
            "1. En admin, ir a 'Usuarios'",
            "2. Ver lista de usuarios"
        ],
        "esperado": "Lista de usuarios"
    },
    {
        "id": "E2E-14",
        "nombre": "Crear nuevo médico",
        "pasos": [
            "1. Click en 'Agregar Médico'",
            "2. Llenar todos los campos",
            "3. Click en 'Guardar'"
        ],
        "esperado": "Médico creado"
    },
    {
        "id": "E2E-15",
        "nombre": "Eliminar usuario",
        "pasos": [
            "1. Buscar usuario",
            "2. Click en eliminar",
            "3. Confirmar"
        ],
        "esperado": "Usuario eliminado"
    }
]

# Mostrar casos
for caso in casos:
    print(f"\n{'='*50}")
    print(f"ID: {caso['id']}")
    print(f"Prueba: {caso['nombre']}")
    print(f"Pasos:")
    for paso in caso['pasos']:
        print(f"  - {paso}")
    print(f"Resultado esperado: {caso['esperado']}")
    print(f"\n[ ] OK    [ ] FAIL")
    print("-"*50)

print(f"\n{'='*60}")
print("TOTAL: 15 CASOS DE PRUEBA E2E")
print("="*60)
print("""
Para documentar:
1. Ejecuta cada caso manualmente
2. Marca OK o FAIL
3. Captura pantalla de cada prueba
4. Registra en tu documento Word
""")