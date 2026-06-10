"""
Script para verificar login y crear usuarios de prueba
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def verificar_login():
    from app import app
    from models import db, Usuario
    from flask_bcrypt import Bcrypt
    
    with app.app_context():
        bcrypt = Bcrypt(app)
        
        print("=== VERIFICACION DE USUARIOS ===")
        
        usuarios = Usuario.query.all()
        print(f"Total usuarios: {len(usuarios)}")
        
        for u in usuarios:
            print(f"\nUsuario: {u.email}")
            print(f"  Nombre: {u.nombre}")
            print(f"  Rol: {u.rol}")
            print(f"  Password hash (primeros 30 chars): {u.password[:30]}...")
            
            # Verificar si el hash es válido
            test = bcrypt.check_password_hash(u.password, 'admin123')
            print(f"  admin123 es valido: {test}")
        
        print("\n=== CREAR USUARIO DE PRUEBA ===")
        
        # Crear usuario de prueba si no existe
        test_user = Usuario.query.filter_by(email='test@test.com').first()
        if not test_user:
            hashed = bcrypt.generate_password_hash('test123').decode('utf-8')
            test_user = Usuario(
                nombre='Test User',
                email='test@test.com',
                password=hashed,
                rol='ADMIN'
            )
            db.session.add(test_user)
            db.session.commit()
            print("Usuario test@test.com / test123 creado")
        else:
            print("Usuario test@test.com ya existe")
        
        print("\n=== VERIFICAR LOGIN ===")
        
        # Probar login
        user = Usuario.query.filter_by(email='test@test.com').first()
        if user:
            valid = bcrypt.check_password_hash(user.password, 'test123')
            print(f"Login test@test.com / test123: {'EXITOSO' if valid else 'FALLO'}")

if __name__ == '__main__':
    verificar_login()