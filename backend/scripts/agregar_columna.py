"""
Script para agregar columna tipo_documento a la tabla afiliados
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def agregar_columna():
    from app import app
    from models import db
    
    with app.app_context():
        try:
            # Verificar si la columna ya existe
            result = db.session.execute(db.text("SHOW COLUMNS FROM afiliados LIKE 'tipo_documento'"))
            if result.fetchone():
                print("[EPS] La columna tipo_documento ya existe")
                return
            
            # Agregar la columna
            db.session.execute(db.text("ALTER TABLE afiliados ADD COLUMN tipo_documento VARCHAR(20) AFTER id_usuario"))
            db.session.commit()
            print("[EPS] Columna tipo_documento agregada correctamente")
            
        except Exception as e:
            db.session.rollback()
            print(f"[EPS] Error: {e}")

if __name__ == '__main__':
    agregar_columna()