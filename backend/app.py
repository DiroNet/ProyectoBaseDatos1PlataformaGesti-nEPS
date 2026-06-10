from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import re
from config import config
from models import db, Usuario, Afiliado, Plan, CentroSalud, Profesional, Factura, Pago, Cita, HistorialClinico, DisponibilidadProfesional

app = Flask(__name__)
app.config.from_object(config['development'])

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)

def init_default_data():
    """Inicializa datos por defecto si no existen"""
    try:
        existing_admin = Usuario.query.filter_by(email='admin@eps.com').first()
        if not existing_admin:
            hashed = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = Usuario(nombre='Administrador', email='admin@eps.com', password=hashed, rol='ADMIN')
            db.session.add(admin)
            db.session.flush()
            print("[EPS] Admin creado: admin@eps.com / admin123")

        planes_default = [
            {'nombre': 'Plan Basico', 'descripcion': 'Cobertura basica essential', 'costo': 50000},
            {'nombre': 'Plan Estandar', 'descripcion': 'Cobertura estandar con especialidades', 'costo': 100000},
            {'nombre': 'Plan Premium', 'descripcion': 'Cobertura completa con todos los beneficios', 'costo': 200000},
        ]
        for p in planes_default:
            if not Plan.query.filter_by(nombre=p['nombre']).first():
                db.session.add(Plan(**p))
                print(f"[EPS] Plan creado: {p['nombre']}")

        centros_default = [
            {'nombre': 'Centro Medico Central', 'direccion': 'Calle 1 #1-1', 'ciudad': 'Bogota'},
            {'nombre': 'Clinica Norte', 'direccion': 'Calle 100 #50-20', 'ciudad': 'Bogota'},
            {'nombre': 'Hospital del Sur', 'direccion': 'Av. Caracas #30-15', 'ciudad': 'Bogota'},
        ]
        for c in centros_default:
            if not CentroSalud.query.filter_by(nombre=c['nombre']).first():
                db.session.add(CentroSalud(**c))
                print(f"[EPS] Centro creado: {c['nombre']}")

        db.session.commit()
        print("[EPS] Datos inicializados correctamente")
    except Exception as e:
        db.session.rollback()
        print(f"[EPS] Error inicializando datos: {e}")

def ejecutar_seed_sql():
    """Ejecuta el script seed.sql si existe"""
    import os
    seed_path = os.path.join(os.path.dirname(__file__), 'scripts', 'seed.sql')
    
    if not os.path.exists(seed_path):
        print("[EPS] seed.sql no encontrado, usando init_default_data")
        return
    
    try:
        with open(seed_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        from sqlalchemy import text
        statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for statement in statements:
            if statement:
                try:
                    db.session.execute(text(statement))
                except Exception as e:
                    pass
        
        db.session.commit()
        print("[EPS] Seed SQL ejecutado correctamente")
    except Exception as e:
        db.session.rollback()
        print(f"[EPS] Seed SQL no ejecutado: {e}")

with app.app_context():
    db.create_all()
    init_default_data()
    ejecutar_seed_sql()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_documento(doc):
    """Cédula colombiana: solo dígitos, entre 6 y 10 caracteres."""
    if not doc or not isinstance(doc, str):
        return False
    return doc.isdigit() and 6 <= len(doc) <= 10

def validate_telefono_co(tel):
    """Celular colombiano: 10 dígitos, empieza con 3."""
    if not tel or not isinstance(tel, str):
        return False
    return bool(re.match(r'^3\d{9}$', tel))

def validate_fecha_nacimiento(fecha_str):
    """Fecha de nacimiento no puede ser futura ni posterior a hoy."""
    if not fecha_str:
        return False
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        return fecha <= datetime.now().date()
    except ValueError:
        return False

def validate_time(t):
    """Hora válida: formato HH:MM, entre 06:00 y 20:00 inclusive."""
    if not t or not isinstance(t, str):
        return False
    try:
        h, m = t.split(':')
        hora = int(h)
        minuto = int(m)
        if len(h) != 2 or len(m) != 2:
            return False
        return 6 <= hora <= 20 and 0 <= minuto <= 59 and not (hora == 20 and minuto > 0)
    except (ValueError, AttributeError):
        return False

@app.route('/')
def index():
    return jsonify({'message': 'API Sistema EPS', 'version': '1.0'})

@app.route('/api/init', methods=['POST'])
def init_db():
    try:
        init_default_data()
        return jsonify({'message': 'Base de datos EPS inicializada correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required = ['email', 'password', 'nombre', 'rol']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Campo {field} requerido'}), 400
    
    if not validate_email(data['email']):
        return jsonify({'error': 'Email inválido'}), 400
    
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email ya registrado'}), 400
    
    documento = data.get('documento', '')
    telefono = data.get('telefono', '')
    fecha_nacimiento = data.get('fecha_nacimiento', '')

    if documento:
        if not validate_documento(documento):
            return jsonify({'error': 'La cédula debe tener entre 6 y 10 dígitos numéricos'}), 400
        if Afiliado.query.filter_by(documento=documento).first():
            return jsonify({'error': 'Este número de cédula ya está registrado'}), 400

    if telefono:
        if not validate_telefono_co(telefono):
            return jsonify({'error': 'El teléfono debe ser un número móvil colombiano (10 dígitos, empieza con 3)'}), 400
        if Afiliado.query.filter_by(telefono=telefono).first():
            return jsonify({'error': 'Este número de teléfono ya está registrado'}), 400

    if fecha_nacimiento:
        if not validate_fecha_nacimiento(fecha_nacimiento):
            return jsonify({'error': 'La fecha de nacimiento no puede ser una fecha futura'}), 400

    if data['rol'] not in ['AFILIADO', 'ADMIN', 'PROFESIONAL']:
        return jsonify({'error': 'Rol inválido'}), 400
    
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    usuario = Usuario(
        nombre=data['nombre'],
        email=data['email'],
        password=hashed,
        rol=data['rol']
    )
    db.session.add(usuario)
    db.session.flush()
    
    if data['rol'] == 'AFILIADO':
        afiliado = Afiliado(
            id_usuario=usuario.id_usuario,
            documento=data.get('documento', ''),
            telefono=data.get('telefono', ''),
            direccion=data.get('direccion', ''),
            id_plan=data.get('id_plan')
        )
        db.session.add(afiliado)
    
    db.session.commit()
    return jsonify({'message': 'Usuario registrado exitosamente', 'id': usuario.id_usuario}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email y password requeridos'}), 400
    
    usuario = Usuario.query.filter_by(email=data['email']).first()
    
    if not usuario:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    try:
        password_valido = bcrypt.check_password_hash(usuario.password, data['password'])
    except:
        password_valido = (usuario.password == data['password'])
    
    if not password_valido:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    token = create_access_token(identity=str(usuario.id_usuario))
    
    return jsonify({
        'token': token,
        'usuario': usuario.to_dict()
    }), 200

@app.route('/api/usuarios', methods=['GET'])
@jwt_required()
def get_usuarios():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    usuarios = Usuario.query.all()
    return jsonify([u.to_dict() for u in usuarios]), 200

@app.route('/api/usuarios/<int:user_id>', methods=['GET'])
@jwt_required()
def get_usuario(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    return jsonify(usuario.to_dict()), 200

@app.route('/api/usuarios/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_usuario(user_id):
    current_id = int(get_jwt_identity())
    usuario_actual = Usuario.query.get(current_id)
    usuario = Usuario.query.get_or_404(user_id)
    
    if usuario.id_usuario != current_id and usuario_actual.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if 'nombre' in data:
        usuario.nombre = data['nombre']
    if 'telefono' in data:
        afiliado = Afiliado.query.filter_by(id_usuario=user_id).first()
        if afiliado:
            afiliado.telefono = data['telefono']
    
    db.session.commit()
    return jsonify(usuario.to_dict()), 200

@app.route('/api/usuarios/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(user_id):
    current_id = int(get_jwt_identity())
    usuario_actual = Usuario.query.get(current_id)
    
    if usuario_actual.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    if usuario_actual.id_usuario == user_id:
        return jsonify({'error': 'No puedes eliminar tu propia cuenta'}), 400
    
    usuario = Usuario.query.get_or_404(user_id)
    
    afiliado = Afiliado.query.filter_by(id_usuario=user_id).first()
    if afiliado:
        Cita.query.filter_by(id_afiliado=afiliado.id_afiliado).delete()
        Factura.query.filter_by(id_afiliado=afiliado.id_afiliado).delete()
        HistorialClinico.query.filter_by(id_afiliado=afiliado.id_afiliado).delete()
        db.session.delete(afiliado)
    
    profesional = Profesional.query.filter_by(id_usuario=user_id).first()
    if profesional:
        Cita.query.filter_by(id_profesional=profesional.id_profesional).delete()
        HistorialClinico.query.filter_by(id_profesional=profesional.id_profesional).delete()
        db.session.delete(profesional)
    
    db.session.delete(usuario)
    db.session.commit()
    
    return jsonify({'message': 'Usuario eliminado correctamente'}), 200

@app.route('/api/afiliados', methods=['GET'])
@jwt_required()
def get_afiliados():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol == 'AFILIADO':
        afiliado = Afiliado.query.filter_by(id_usuario=current_id).first()
        if afiliado:
            return jsonify([afiliado.to_dict()]), 200
    
    afiliados = Afiliado.query.all()
    return jsonify([a.to_dict() for a in afiliados]), 200

@app.route('/api/afiliados/<int:afiliado_id>', methods=['GET'])
@jwt_required()
def get_afiliado(afiliado_id):
    afiliado = Afiliado.query.get_or_404(afiliado_id)
    return jsonify(afiliado.to_dict()), 200

@app.route('/api/afiliados', methods=['POST'])
@jwt_required()
def create_afiliado():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    required = ['email', 'password', 'nombre', 'documento']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} requerido'}), 400
    
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email ya registrado'}), 400
    
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    nuevo_usuario = Usuario(
        nombre=data['nombre'],
        email=data['email'],
        password=hashed,
        rol='AFILIADO'
    )
    db.session.add(nuevo_usuario)
    db.session.flush()
    
    afiliado = Afiliado(
        id_usuario=nuevo_usuario.id_usuario,
        documento=data['documento'],
        fecha_nacimiento=datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date() if data.get('fecha_nacimiento') else None,
        telefono=data.get('telefono', ''),
        direccion=data.get('direccion', ''),
        id_plan=data.get('id_plan')
    )
    db.session.add(afiliado)
    db.session.commit()
    
    return jsonify(afiliado.to_dict()), 201

@app.route('/api/afiliados/<int:afiliado_id>', methods=['PUT'])
@jwt_required()
def update_afiliado(afiliado_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    afiliado = Afiliado.query.get_or_404(afiliado_id)
    
    if afiliado.id_usuario != current_id and usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if 'documento' in data:
        afiliado.documento = data['documento']
    if 'fecha_nacimiento' in data:
        afiliado.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
    if 'telefono' in data:
        afiliado.telefono = data['telefono']
    if 'direccion' in data:
        afiliado.direccion = data['direccion']
    if 'id_plan' in data:
        afiliado.id_plan = data['id_plan']
    
    db.session.commit()
    return jsonify(afiliado.to_dict()), 200

@app.route('/api/profesionales', methods=['GET'])
@jwt_required()
def get_profesionales():
    profesionales = Profesional.query.all()
    return jsonify([p.to_dict() for p in profesionales]), 200

@app.route('/api/profesionales/<int:profesional_id>', methods=['GET'])
@jwt_required()
def get_profesional(profesional_id):
    profesional = Profesional.query.get_or_404(profesional_id)
    return jsonify(profesional.to_dict()), 200

@app.route('/api/profesionales', methods=['POST'])
@jwt_required()
def create_profesional():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    required = ['email', 'password', 'nombre', 'especialidad']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} requerido'}), 400
    
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email ya registrado'}), 400
    
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    nuevo_usuario = Usuario(
        nombre=data['nombre'],
        email=data['email'],
        password=hashed,
        rol='PROFESIONAL'
    )
    db.session.add(nuevo_usuario)
    db.session.flush()
    
    profesional = Profesional(
        id_usuario=nuevo_usuario.id_usuario,
        especialidad=data['especialidad'],
        id_centro=data.get('id_centro')
    )
    db.session.add(profesional)
    db.session.commit()
    
    return jsonify(profesional.to_dict()), 201

@app.route('/api/profesionales/<int:profesional_id>', methods=['PUT'])
@jwt_required()
def update_profesional(profesional_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    profesional = Profesional.query.get_or_404(profesional_id)
    
    if profesional.id_usuario != current_id and usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if 'especialidad' in data:
        profesional.especialidad = data['especialidad']
    if 'id_centro' in data:
        profesional.id_centro = data['id_centro']
    
    db.session.commit()
    return jsonify(profesional.to_dict()), 200

@app.route('/api/disponibilidad/<int:profesional_id>', methods=['GET'])
@jwt_required()
def get_disponibilidad_profesional(profesional_id):
    disponibilidad = DisponibilidadProfesional.query.filter_by(
        id_profesional=profesional_id,
        activo=True
    ).all()
    return jsonify([d.to_dict() for d in disponibilidad]), 200

@app.route('/api/disponibilidad', methods=['POST'])
@jwt_required()
def create_disponibilidad():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)

    if usuario.rol != 'ADMIN' and usuario.rol != 'PROFESIONAL':
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()

    if not data.get('id_profesional') or not data.get('dia_semana') or not data.get('hora_inicio') or not data.get('hora_fin'):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    disp = DisponibilidadProfesional(
        id_profesional=data['id_profesional'],
        dia_semana=data['dia_semana'],
        hora_inicio=data['hora_inicio'],
        hora_fin=data['hora_fin'],
        activo=True
    )
    db.session.add(disp)
    db.session.commit()

    return jsonify(disp.to_dict()), 201

@app.route('/api/disponibilidad/<int:disp_id>', methods=['DELETE'])
@jwt_required()
def delete_disponibilidad(disp_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)

    if usuario.rol != 'ADMIN' and usuario.rol != 'PROFESIONAL':
        return jsonify({'error': 'No autorizado'}), 403

    disp = DisponibilidadProfesional.query.get_or_404(disp_id)
    disp.activo = False
    db.session.commit()

    return jsonify({'message': 'Disponibilidad eliminada'}), 200

@app.route('/api/centros', methods=['GET'])
@jwt_required()
def get_centros():
    centros = CentroSalud.query.all()
    return jsonify([c.to_dict() for c in centros]), 200

@app.route('/api/centros/<int:centro_id>', methods=['GET'])
@jwt_required()
def get_centro(centro_id):
    centro = CentroSalud.query.get_or_404(centro_id)
    return jsonify(centro.to_dict()), 200

@app.route('/api/centros', methods=['POST'])
@jwt_required()
def create_centro():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if not data.get('nombre'):
        return jsonify({'error': 'Nombre requerido'}), 400
    
    centro = CentroSalud(
        nombre=data['nombre'],
        direccion=data.get('direccion', ''),
        ciudad=data.get('ciudad', '')
    )
    db.session.add(centro)
    db.session.commit()
    
    return jsonify(centro.to_dict()), 201

@app.route('/api/centros/<int:centro_id>', methods=['PUT'])
@jwt_required()
def update_centro(centro_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    centro = CentroSalud.query.get_or_404(centro_id)
    data = request.get_json()
    
    if 'nombre' in data:
        centro.nombre = data['nombre']
    if 'direccion' in data:
        centro.direccion = data['direccion']
    if 'ciudad' in data:
        centro.ciudad = data['ciudad']
    
    db.session.commit()
    return jsonify(centro.to_dict()), 200

@app.route('/api/centros/<int:centro_id>', methods=['DELETE'])
@jwt_required()
def delete_centro(centro_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    centro = CentroSalud.query.get_or_404(centro_id)
    db.session.delete(centro)
    db.session.commit()
    return jsonify({'message': 'Centro eliminado'}), 200

@app.route('/api/planes', methods=['GET'])
@jwt_required()
def get_planes():
    planes = Plan.query.all()
    return jsonify([p.to_dict() for p in planes]), 200

@app.route('/api/planes/<int:plan_id>', methods=['GET'])
@jwt_required()
def get_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    return jsonify(plan.to_dict()), 200

@app.route('/api/planes', methods=['POST'])
@jwt_required()
def create_plan():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if not data.get('nombre'):
        return jsonify({'error': 'Nombre requerido'}), 400
    
    plan = Plan(
        nombre=data['nombre'],
        descripcion=data.get('descripcion', ''),
        costo=data.get('costo', 0)
    )
    db.session.add(plan)
    db.session.commit()
    
    return jsonify(plan.to_dict()), 201

@app.route('/api/planes/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_plan(plan_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    plan = Plan.query.get_or_404(plan_id)
    data = request.get_json()
    
    if data.get('nombre'):
        plan.nombre = data['nombre']
    if 'descripcion' in data:
        plan.descripcion = data['descripcion']
    if data.get('costo') is not None:
        plan.costo = data['costo']
    
    db.session.commit()
    return jsonify(plan.to_dict()), 200

@app.route('/api/planes/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_plan(plan_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    plan = Plan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    return jsonify({'message': 'Plan eliminado'}), 200

@app.route('/api/citas', methods=['GET'])
@jwt_required()
def get_citas():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    query = Cita.query
    
    if usuario.rol == 'AFILIADO':
        afiliado = Afiliado.query.filter_by(id_usuario=current_id).first()
        if afiliado:
            query = query.filter_by(id_afiliado=afiliado.id_afiliado)
    elif usuario.rol == 'PROFESIONAL':
        profesional = Profesional.query.filter_by(id_usuario=current_id).first()
        if profesional:
            query = query.filter_by(id_profesional=profesional.id_profesional)
    
    estado = request.args.get('estado')
    if estado:
        query = query.filter_by(estado=estado)
    
    citas = query.order_by(Cita.fecha.desc()).all()
    return jsonify([c.to_dict() for c in citas]), 200

@app.route('/api/citas/<int:cita_id>', methods=['GET'])
@jwt_required()
def get_cita(cita_id):
    cita = Cita.query.get_or_404(cita_id)
    return jsonify(cita.to_dict()), 200

@app.route('/api/citas', methods=['POST'])
@jwt_required()
def create_cita():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'AFILIADO':
        return jsonify({'error': 'Solo afiliados pueden agendar citas'}), 403
    
    afiliado = Afiliado.query.filter_by(id_usuario=current_id).first()
    if not afiliado:
        return jsonify({'error': 'Afiliado no encontrado'}), 404
    
    data = request.get_json()
    
    required = ['id_profesional', 'id_centro', 'fecha']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Campo {field} requerido'}), 400
    
    try:
        fecha_cita = datetime.strptime(data['fecha'], '%Y-%m-%d %H:%M')
    except:
        return jsonify({'error': 'Formato de fecha inválido'}), 400
    
    if fecha_cita < datetime.now():
        return jsonify({'error': 'No se pueden agendar citas en fechas pasadas'}), 400
    
    cita = Cita(
        id_afiliado=afiliado.id_afiliado,
        id_profesional=data['id_profesional'],
        id_centro=data['id_centro'],
        fecha=fecha_cita,
        estado='PENDIENTE'
    )
    db.session.add(cita)
    db.session.commit()
    
    return jsonify(cita.to_dict()), 201

@app.route('/api/citas/<int:cita_id>', methods=['PUT'])
@jwt_required()
def update_cita(cita_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    cita = Cita.query.get_or_404(cita_id)
    
    data = request.get_json()
    
    if usuario.rol == 'ADMIN':
        if 'estado' in data:
            cita.estado = data['estado']
        if 'fecha' in data:
            cita.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d %H:%M')
    elif usuario.rol == 'AFILIADO':
        afiliado = Afiliado.query.filter_by(id_usuario=current_id).first()
        if cita.id_afiliado != afiliado.id_afiliado:
            return jsonify({'error': 'No autorizado'}), 403
        if 'estado' in data and data['estado'] in ['CANCELADA']:
            cita.estado = data['estado']
    elif usuario.rol == 'PROFESIONAL':
        profesional = Profesional.query.filter_by(id_usuario=current_id).first()
        if cita.id_profesional != profesional.id_profesional:
            return jsonify({'error': 'No autorizado'}), 403
        if 'estado' in data:
            cita.estado = data['estado']
    
    db.session.commit()
    return jsonify(cita.to_dict()), 200

@app.route('/api/citas/<int:cita_id>', methods=['DELETE'])
@jwt_required()
def delete_cita(cita_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    cita = Cita.query.get_or_404(cita_id)
    
    if usuario.rol == 'AFILIADO':
        afiliado = Afiliado.query.filter_by(id_usuario=current_id).first()
        if cita.id_afiliado != afiliado.id_afiliado:
            return jsonify({'error': 'No autorizado'}), 403
    elif usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    cita.estado = 'CANCELADA'
    db.session.commit()
    
    return jsonify({'message': 'Cita cancelada'}), 200

@app.route('/api/facturas', methods=['GET'])
@jwt_required()
def get_facturas():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    query = Factura.query
    
    if usuario.rol == 'AFILIADO':
        afiliado = Afiliado.query.filter_by(id_usuario=current_id).first()
        if afiliado:
            query = query.filter_by(id_afiliado=afiliado.id_afiliado)
    
    estado = request.args.get('estado')
    if estado:
        query = query.filter_by(estado=estado)
    
    facturas = query.order_by(Factura.fecha.desc()).all()
    return jsonify([f.to_dict() for f in facturas]), 200

@app.route('/api/facturas/<int:factura_id>', methods=['GET'])
@jwt_required()
def get_factura(factura_id):
    factura = Factura.query.get_or_404(factura_id)
    return jsonify(factura.to_dict()), 200

@app.route('/api/facturas', methods=['POST'])
@jwt_required()
def create_factura():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if not data.get('id_afiliado') or not data.get('total'):
        return jsonify({'error': 'Campos requeridos'}), 400
    
    factura = Factura(
        id_afiliado=data['id_afiliado'],
        fecha=datetime.now().date(),
        total=data['total'],
        estado='PENDIENTE'
    )
    db.session.add(factura)
    db.session.commit()
    
    return jsonify(factura.to_dict()), 201

@app.route('/api/facturas/<int:factura_id>', methods=['DELETE'])
@jwt_required()
def delete_factura(factura_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    factura = Factura.query.get_or_404(factura_id)
    db.session.delete(factura)
    db.session.commit()
    
    return jsonify({'message': 'Factura eliminada'}), 200

@app.route('/api/facturas/<int:factura_id>/pagar', methods=['POST'])
@jwt_required()
def pagar_factura(factura_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    factura = Factura.query.get_or_404(factura_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    pago = Pago(
        id_factura=factura_id,
        fecha=datetime.now().date(),
        monto=factura.total,
        metodo_pago=data.get('metodo_pago', 'Efectivo')
    )
    db.session.add(pago)
    factura.estado = 'PAGADA'
    db.session.commit()
    
    return jsonify(factura.to_dict()), 200

@app.route('/api/pagos', methods=['GET'])
@jwt_required()
def get_pagos():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    pagos = Pago.query.all()
    return jsonify([p.to_dict() for p in pagos]), 200

@app.route('/api/historial', methods=['GET'])
@jwt_required()
def get_historial():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    query = HistorialClinico.query
    
    if usuario.rol == 'AFILIADO':
        afiliado = Afiliado.query.filter_by(id_usuario=current_id).first()
        if afiliado:
            query = query.filter_by(id_afiliado=afiliado.id_afiliado)
    elif usuario.rol == 'PROFESIONAL':
        profesional = Profesional.query.filter_by(id_usuario=current_id).first()
        if profesional:
            query = query.filter_by(id_profesional=profesional.id_profesional)
    
    historiales = query.order_by(HistorialClinico.fecha.desc()).all()
    return jsonify([h.to_dict() for h in historiales]), 200

@app.route('/api/historial', methods=['POST'])
@jwt_required()
def create_historial():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'PROFESIONAL':
        return jsonify({'error': 'Solo profesionales pueden registrar historial'}), 403
    
    profesional = Profesional.query.filter_by(id_usuario=current_id).first()
    if not profesional:
        return jsonify({'error': 'Profesional no encontrado'}), 404
    
    data = request.get_json()
    
    if not data.get('id_afiliado') or not data.get('diagnostico'):
        return jsonify({'error': 'Campos requeridos'}), 400
    
    historial = HistorialClinico(
        id_afiliado=data['id_afiliado'],
        id_profesional=profesional.id_profesional,
        fecha=datetime.now().date(),
        diagnostico=data['diagnostico'],
        tratamiento=data.get('tratamiento', '')
    )
    db.session.add(historial)
    
    if data.get('id_cita'):
        cita = Cita.query.get(data['id_cita'])
        if cita:
            cita.estado = 'FINALIZADA'
    
    db.session.commit()
    
    return jsonify(historial.to_dict()), 201

@app.route('/api/consultas/afiliados-facturas-pendientes', methods=['GET'])
@jwt_required()
def get_afiliados_facturas_pendientes():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    resultados = db.session.execute(
        db.text('''
            SELECT a.id_afiliado, u.nombre, u.email, COUNT(f.id_factura) as facturas_pendientes, SUM(f.total) as total_pendiente
            FROM afiliados a
            JOIN usuarios u ON a.id_usuario = u.id_usuario
            LEFT JOIN facturas f ON a.id_afiliado = f.id_afiliado AND f.estado = 'PENDIENTE'
            GROUP BY a.id_afiliado, u.nombre, u.email
            HAVING COUNT(f.id_factura) > 0
        ''')
    ).fetchall()
    
    return jsonify([{
        'id_afiliado': r[0],
        'nombre': r[1],
        'email': r[2],
        'facturas_pendientes': r[3],
        'total_pendiente': float(r[4]) if r[4] else 0
    } for r in resultados]), 200

@app.route('/api/consultas/facturacion-por-plan', methods=['GET'])
@jwt_required()
def get_facturacion_por_plan():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    resultados = db.session.execute(
        db.text('''
            SELECT p.nombre, COUNT(DISTINCT a.id_afiliado) as total_afiliados, COALESCE(SUM(f.total), 0) as facturacion_total
            FROM planes p
            LEFT JOIN afiliados a ON p.id_plan = a.id_plan
            LEFT JOIN facturas f ON a.id_afiliado = f.id_afiliado AND f.estado = 'PAGADA'
            GROUP BY p.id_plan, p.nombre
        ''')
    ).fetchall()
    
    return jsonify([{
        'plan': r[0],
        'total_afiliados': r[1],
        'facturacion_total': float(r[2])
    } for r in resultados]), 200

@app.route('/api/consultas/diagnosticos-frecuentes', methods=['GET'])
@jwt_required()
def get_diagnosticos_frecuentes():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    resultados = db.session.execute(
        db.text('''
            SELECT p.especialidad, h.diagnostico, COUNT(*) as cantidad
            FROM historial_clinico h
            JOIN profesionales p ON h.id_profesional = p.id_profesional
            GROUP BY p.especialidad, h.diagnostico
            ORDER BY cantidad DESC
            LIMIT 20
        ''')
    ).fetchall()
    
    return jsonify([{
        'especialidad': r[0],
        'diagnostico': r[1],
        'cantidad': r[2]
    } for r in resultados]), 200

@app.route('/api/consultas/centros-mas-utilizados', methods=['GET'])
@jwt_required()
def get_centros_mas_utilizados():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol != 'ADMIN':
        return jsonify({'error': 'No autorizado'}), 403
    
    resultados = db.session.execute(
        db.text('''
            SELECT c.nombre, c.ciudad, COUNT(cit.id_cita) as total_citas
            FROM centros_salud c
            LEFT JOIN citas cit ON c.id_centro = cit.id_centro
            GROUP BY c.id_centro, c.nombre, c.ciudad
            ORDER BY total_citas DESC
        ''')
    ).fetchall()
    
    return jsonify([{
        'centro': r[0],
        'ciudad': r[1],
        'total_citas': r[2]
    } for r in resultados]), 200

@app.route('/api/consultas/citas-proximas-afiliado', methods=['GET'])
@jwt_required()
def get_citas_proximas_afiliado():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    afiliado = Afiliado.query.filter_by(id_usuario=current_id).first()
    if not afiliado:
        return jsonify({'error': 'Afiliado no encontrado'}), 404
    
    ahora = datetime.now()
    citas = Cita.query.filter(
        Cita.id_afiliado == afiliado.id_afiliado,
        Cita.fecha >= ahora,
        Cita.estado.in_(['PENDIENTE', 'CONFIRMADA'])
    ).order_by(Cita.fecha).limit(10).all()
    
    return jsonify([c.to_dict() for c in citas]), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)