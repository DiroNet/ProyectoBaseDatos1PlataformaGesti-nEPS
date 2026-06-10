import os
from sqlalchemy import text
from config import config

def ejecutar_seed():
    """Ejecuta el script seed.sql en la base de datos"""
    from models import db
    
    seed_path = os.path.join(os.path.dirname(__file__), 'seed.sql')
    
    if not os.path.exists(seed_path):
        print("[EPS] No se encontró seed.sql")
        return False
    
    try:
        with open(seed_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for statement in statements:
            if statement:
                try:
                    db.session.execute(text(statement))
                except Exception as e:
                    print(f"[EPS] Error en statement: {str(e)[:100]}")
        
        db.session.commit()
        print("[EPS] Seed data cargado correctamente")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"[EPS] Error ejecutando seed: {e}")
        return False

if __name__ == '__main__':
    from app import app
    with app.app_context():
        ejecutar_seed()