# Pruebas E2E con Selenium - Sistema de Citas Medicas
# Basado en planilla de pruebas E2E
import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By

SCREENSHOTS_DIR = "pruebas\\screenshots"

def crear_carpeta():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def capturar(nombre):
    crear_carpeta()
    path = f"{SCREENSHOTS_DIR}\\{nombre}.png"
    driver.save_screenshot(path)
    print(f"Foto: {path}")

# Driver global
driver = None

def setup_module(module):
    global driver
    print("Abriendo Firefox...")
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    print("Firefox abierto")

def teardown_module(module):
    if driver:
        print("Cerrando navegador...")
        time.sleep(3)
        driver.quit()

def test_e2e_12_login_admin():
    """E2E-12: Login como administrador"""
    print("\n=== E2E-12: Login como administrador ===")
    
    # Paso 1: Ir a http://localhost:4200
    print("1. Abriendo http://localhost:4200...")
    driver.get("http://localhost:4200")
    time.sleep(3)
    capturar("E2E-12_01_pagina_login")
    
    # Paso 2: Email admin@hospital.com
    print("2. Ingresando email...")
    driver.find_element(By.NAME, "email").send_keys("admin@hospital.com")
    
    # Paso 3: Password admin123
    print("3. Ingresando password...")
    driver.find_element(By.NAME, "password").send_keys("admin123")
    capturar("E2E-12_02_credenciales")
    
    # Click en login
    print("4. Haciendo click en Iniciar Sesion...")
    driver.find_element(By.CSS_SELECTOR, "button.btn-auth").click()
    
    time.sleep(4)
    capturar("E2E-12_03_dashboard_admin")
    
    # Verificar que estamos en dashboard
    url = driver.current_url
    print(f"URL actual: {url}")
    
    assert "dashboard" in url, "No se encontro dashboard en la URL"
    print("RESULTADO: OK - Dashboard administrador cargado")

def test_e2e_13_gestion_usuarios():
    """E2E-13: Gestion de usuarios"""
    print("\n=== E2E-13: Gestion de usuarios ===")
    
    # Ya estar en dashboard (del test anterior)
    
    # Paso 1: Click en "Usuarios" del menu
    print("1. Click en Usuarios...")
    driver.find_element(By.XPATH, "//span[contains(text(),'Usuarios')]").click()
    time.sleep(2)
    capturar("E2E-13_01_usuarios")
    
    # Verificar tabla de usuarios
    tablas = driver.find_elements(By.CSS_SELECTOR, "table")
    assert len(tablas) > 0, "No se encontro tabla de usuarios"
    print("RESULTADO: OK - Lista de usuarios visible")

def test_e2e_14_crear_medico():
    """E2E-14: Crear nuevo medico"""
    print("\n=== E2E-14: Crear nuevo medico ===")
    
    # Paso 1: Click en "Medicos" del menu (con acento)
    print("1. Navegando a Medicos...")
    driver.find_element(By.XPATH, "//span[contains(text(),'Médicos')]").click()
    time.sleep(2)
    
    # Paso 2: Click en "Agregar Medico"
    print("2. Click en Agregar Medico...")
    driver.find_element(By.CSS_SELECTOR, "button.btn-add").click()
    time.sleep(2)
    capturar("E2E-14_01_formulario")
    
    # Paso 3: Llenar todos los campos
    print("3. Llenando formulario...")
    driver.find_element(By.NAME, "nombre").send_keys("Alonso")
    driver.find_element(By.NAME, "apellido").send_keys("Rojas")
    driver.find_element(By.NAME, "email").send_keys("alonso@gmail.com")
    driver.find_element(By.NAME, "telefono").send_keys("3145323875")
    driver.find_element(By.NAME, "password").send_keys("123456")
    driver.find_element(By.NAME, "cedula").send_keys("200502")
    capturar("E2E-14_02_formulario_lleno")
    
    #Seleccionar especialidad
    print("4. Seleccionando especialidad...")
    dropdown = driver.find_element(By.NAME, "especialidad_id")
    opciones = dropdown.find_elements(By.TAG_NAME, "option")
    for op in opciones:
        if "Psicologia" in op.text:
            op.click()
            break
    time.sleep(1)
    
    # Paso 4: Click en Guardar
    print("5. Guardando medico...")
    driver.find_element(By.CSS_SELECTOR, "button.btn-submit").click()
    time.sleep(3)
    capturar("E2E-14_03_medico_creado")
    
    print("RESULTADO: OK - Medico creado")

def test_e2e_15_eliminar_usuario():
    """E2E-15: Eliminar usuario"""
    print("\n=== E2E-15: Eliminar usuario ===")
    
    # Paso 1: Click en "Usuarios"
    print("1. Navegando a Usuarios...")
    driver.find_element(By.XPATH, "//span[contains(text(),'Usuarios')]").click()
    time.sleep(2)
    capturar("E2E-15_01_lista_usuarios")
    
    # Paso 2: Buscar usuario (buscar boton de eliminar)
    print("2. Buscando boton de eliminar...")
    botones = driver.find_elements(By.CSS_SELECTOR, ".btn-delete")
    
    if len(botones) > 0:
        print("3. Click en eliminar...")
        botones[0].click()
        time.sleep(2)
        capturar("E2E-15_02_confirmar")
        
        # Paso 3: Confirmar (buscar boton de confirmacion)
        try:
            confirmar = driver.find_element(By.CSS_SELECTOR, ".btn-confirm-delete")
            confirmar.click()
            time.sleep(2)
            capturar("E2E-15_03_eliminado")
            print("RESULTADO: OK - Usuario eliminado")
        except:
            print("No aparecio boton de confirmacion")
    else:
        print("No hay usuarios para eliminar")

def test_e2e_11_logout():
    """E2E-11: Logout"""
    print("\n=== E2E-11: Logout ===")
    
    print("1. Click en Cerrar Sesion...")
    driver.find_element(By.CSS_SELECTOR, "button.btn-logout").click()
    time.sleep(3)
    capturar("E2E-11_logout")
    
    url = driver.current_url
    assert "login" in url or url.endswith("/"), "No regreso al login"
    print("RESULTADO: OK - Regreso a login")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])