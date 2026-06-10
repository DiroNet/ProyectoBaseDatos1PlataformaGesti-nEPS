"""
Script de validacion - Analiza que archivos y codigo usa el backend
Ejecutar: python scripts/validar_codigo.py
"""
import os
import re

BACKEND_PATH = os.path.dirname(os.path.dirname(__file__))

def analizar_codigo():
    """Analiza el codigo del backend"""
    
    archivos_py = []
    for root, dirs, files in os.walk(BACKEND_PATH):
        if '__pycache__' in root or '.git' in root or 'scripts' in root:
            continue
        for f in files:
            if f.endswith('.py'):
                archivos_py.append(os.path.join(root, f))
    
    print("=" * 60)
    print("ANALISIS DEL CODIGO DEL BACKEND")
    print("=" * 60)
    
    print(f"\n[*] Archivos Python encontrados: {len(archivos_py)}")
    for f in sorted(archivos_py):
        rel = os.path.relpath(f, BACKEND_PATH)
        print(f"   - {rel}")
    
    print("\n[*] IMPORTS Y DEPENDENCIAS")
    print("-" * 40)
    
    imports_totales = {}
    funciones_totales = []
    
    for archivo in archivos_py:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            imports_encontrados = re.findall(r'^(?:from|import)\s+(\w+)', contenido, re.MULTILINE)
            for imp in imports_encontrados:
                imports_totales[imp] = imports_totales.get(imp, 0) + 1
            
            funciones = re.findall(r'^def\s+(\w+)', contenido, re.MULTILINE)
            for func in funciones:
                rel_path = os.path.relpath(archivo, BACKEND_PATH)
                funciones_totales.append((func, rel_path))
                
        except:
            pass
    
    print("\n[*] Imports mas usados:")
    for imp, count in sorted(imports_totales.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"   {imp}: {count} veces")
    
    print(f"\n[*] Funciones definidas: {len(funciones_totales)}")
    for func, path in sorted(funciones_totales, key=lambda x: x[0]):
        print(f"   {func}() -> {path}")

def verificar_archivos_sql():
    """Verifica archivos SQL en el proyecto"""
    print("\n" + "=" * 60)
    print("ARCHIVOS SQL EN EL PROYECTO")
    print("=" * 60)
    
    sql_files = []
    for root, dirs, files in os.walk(BACKEND_PATH):
        for f in files:
            if f.endswith('.sql'):
                sql_files.append(os.path.join(root, f))
    
    for f in sql_files:
        rel = os.path.relpath(f, BACKEND_PATH)
        size = os.path.getsize(f)
        print(f"\n[*] {rel} ({size} bytes)")
        
        with open(f, 'r', encoding='utf-8') as file:
            lineas = len(file.readlines())
            print(f"   Lineas: {lineas}")

def verificar_ejecucion_seed():
    """Verifica si el seed se ejecuto"""
    print("\n" + "=" * 60)
    print("ESTADO DEL SEED")
    print("=" * 60)
    
    seed_path = os.path.join(BACKEND_PATH, 'scripts', 'seed.sql')
    if os.path.exists(seed_path):
        print("[OK] seed.sql encontrado en scripts/")
        with open(seed_path, 'r', encoding='utf-8') as f:
            lineas = len(f.readlines())
        print(f"    {lineas} lineas")
    else:
        print("[X] seed.sql NO encontrado")

if __name__ == '__main__':
    analizar_codigo()
    verificar_archivos_sql()
    verificar_ejecucion_seed()
    print("\n" + "=" * 60)
    print("VALIDACION COMPLETA")
    print("=" * 60)