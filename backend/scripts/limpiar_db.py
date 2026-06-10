"""
Script para LIMPIAR toda la base de datos
ADVERTENCIA: Elimina todos los datos de todas las tablas
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def limpiar_base_datos():
    """Elimina todos los datos de todas las tablas"""
    from app import app
    from models import db
    
    with app.app_context():
        try:
            print("[EPS] Iniciando limpieza de base de datos...")
            
            # Desactivar foreign keys temporalmente
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0'))
            
            # Obtener todas las tablas
            tablas = [
                'disponibilidad_profesional',
                'historial_clinico', 
                'pagos',
                'facturas',
                'citas',
                'profesionales',
                'afiliados',
                'usuarios',
                'centros_salud',
                'planes'
            ]
            
            for tabla in tablas:
                try:
                    db.session.execute(db.text(f'TRUNCATE TABLE {tabla}'))
                    print(f"[EPS] Tabla {tabla} limpiada")
                except Exception as e:
                    print(f"[EPS] Error truncando {tabla}: {str(e)[:50]}")
            
            # Reactivar foreign keys
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
            db.session.commit()
            
            print("[EPS] Base de datos limpiada correctamente")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"[EPS] Error durante limpieza: {e}")
            return False

if __name__ == '__main__':
    confirmar = input("ADVERTENCIA: Se eliminarán TODOS los datos. Continuar? (si/no): ")
    if confirmar.lower() == 'si':
        limpiar_base_datos()
    else:
        print("[EPS] Operacion cancelada")