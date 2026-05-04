from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, time, date
import re
from config import config
from models import db, Rol, Usuario, Paciente, Medico, Disponibilidad, Cita, HistorialMedico, Especialidad, Estado

app = Flask(__name__)
app.config.from_object(config['development'])

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_time(time_str):
    try:
        t = datetime.strptime(time_str, '%H:%M').time()
        return time(6, 0) <= t <= time(20, 0)
    except:
        return False

@app.route('/')
def index():
    return jsonify({'message': 'API Sistema de Citas Médicas', 'version': '1.0'})

# ============ AUTENTICACIÓN ============

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required = ['email', 'password', 'nombre', 'apellido', 'rol']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Campo {field} requerido'}), 400
    
    # Validar cédula para pacientes
    if data['rol'] == 'paciente' and not data.get('cedula'):
        return jsonify({'error': 'Cédula requerida para pacientes'}), 400
    
    # Validar que la cédula no esté duplicada
    if data['rol'] == 'paciente' and data.get('cedula'):
        cedula_existente = Paciente.query.filter_by(cedula=data['cedula']).first()
        if cedula_existente:
            return jsonify({'error': 'La cédula ya está registrada en el sistema'}), 400
    
    # Validar cédula profesional para médicos
    if data['rol'] == 'medico' and not data.get('cedula_profesional'):
        return jsonify({'error': 'Cédula profesional requerida para médicos'}), 400
    
    # Validar que la cédula profesional no esté duplicada
    if data['rol'] == 'medico' and data.get('cedula_profesional'):
        medico_existente = Medico.query.filter_by(cedula_profesional=data['cedula_profesional']).first()
        if medico_existente:
            return jsonify({'error': 'La cédula profesional ya está registrada en el sistema'}), 400
    
    if not validate_email(data['email']):
        return jsonify({'error': 'Email inválido'}), 400
    
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email ya registrado'}), 400
    
    rol = Rol.query.filter_by(nombre=data['rol']).first()
    if not rol:
        return jsonify({'error': 'Rol inválido'}), 400
    
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    usuario = Usuario(
        email=data['email'],
        password=hashed,
        nombre=data['nombre'],
        apellido=data['apellido'],
        telefono=data.get('telefono', ''),
        rol_id=rol.id
    )
    db.session.add(usuario)
    db.session.flush()
    
    if data['rol'] == 'paciente':
        paciente = Paciente(
            usuario_id=usuario.id,
            cedula=data.get('cedula', ''),
            fecha_nacimiento=datetime.strptime(data.get('fecha_nacimiento', '2000-01-01'), '%Y-%m-%d').date() if data.get('fecha_nacimiento') else None,
            direccion=data.get('direccion', '')
        )
        db.session.add(paciente)
    elif data['rol'] == 'medico':
        medico = Medico(
            usuario_id=usuario.id,
            especialidad=data.get('especialidad', 'Medicina General'),
            cedula_profesional=data.get('cedula_profesional', '')
        )
        db.session.add(medico)
        
        for day in range(1, 8):
            disp = Disponibilidad(
                medico_id=None,
                dia_semana=day,
                hora_inicio=time(8, 0),
                hora_fin=time(17, 0)
            )
        db.session.flush()
        disp.medico_id = medico.id
    
    db.session.commit()
    return jsonify({'message': 'Usuario registrado exitosamente', 'usuario_id': usuario.id}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email y password requeridos'}), 400
    
    usuario = Usuario.query.filter_by(email=data['email']).first()
    
    if not usuario or not bcrypt.check_password_hash(usuario.password, data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    if not usuario.activo:
        return jsonify({'error': 'Usuario inactivo'}), 403
    
    token = create_access_token(identity=str(usuario.id))
    
    return jsonify({
        'token': token,
        'usuario': usuario.to_dict()
    }), 200

# ============ USUARIOS ============

@app.route('/api/usuarios', methods=['GET'])
@jwt_required()
def get_usuarios():
    current_id = int(get_jwt_identity())
    current_user = Usuario.query.get(current_id)
    
    # Administradores ven todos los usuarios, otros solo activos
    if current_user.rol.nombre == 'administrador':
        usuarios = Usuario.query.all()
    else:
        usuarios = Usuario.query.filter_by(activo=True).all()
    
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
    current_user = Usuario.query.get(current_id)
    usuario = Usuario.query.get_or_404(user_id)
    
    # Solo el propio usuario o un administrador puede modificar
    if usuario.id != current_id and current_user.rol.nombre != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if 'nombre' in data:
        usuario.nombre = data['nombre']
    if 'apellido' in data:
        usuario.apellido = data['apellido']
    if 'telefono' in data:
        usuario.telefono = data['telefono']
    if 'activo' in data:
        if current_user.rol.nombre == 'administrador' or usuario.id == current_id:
            usuario.activo = data['activo']
    
    db.session.commit()
    return jsonify(usuario.to_dict()), 200

@app.route('/api/usuarios/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(user_id):
    current_id = int(get_jwt_identity())
    current_user = Usuario.query.get(current_id)
    
    # Solo administradores pueden eliminar usuarios
    if current_user.rol.nombre != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    usuario = Usuario.query.get_or_404(user_id)
    
    # No permitir eliminarse a sí mismo
    if usuario.id == current_id:
        return jsonify({'error': 'No puedes eliminar tu propia cuenta'}), 400
    
    from models import Cita, Disponibilidad, HistorialMedico
    
    # Buscar y eliminar paciente asociado
    paciente = Paciente.query.filter_by(usuario_id=user_id).first()
    if paciente:
        # Eliminar citas del paciente
        Cita.query.filter_by(paciente_id=paciente.id).delete()
        # Eliminar historial del paciente
        HistorialMedico.query.filter_by(paciente_id=paciente.id).delete()
        db.session.delete(paciente)
    
    # Buscar y eliminar médico asociado
    medico = Medico.query.filter_by(usuario_id=user_id).first()
    if medico:
        # Eliminar disponibilidad del médico
        Disponibilidad.query.filter_by(medico_id=medico.id).delete()
        # Eliminar citas del médico
        Cita.query.filter_by(medico_id=medico.id).delete()
        # Eliminar historial del médico
        HistorialMedico.query.filter_by(medico_id=medico.id).delete()
        db.session.delete(medico)
    
    db.session.delete(usuario)
    db.session.commit()
    
    return jsonify({'message': 'Usuario eliminado correctamente'}), 200

# ============ PACIENTES ============

@app.route('/api/pacientes', methods=['GET'])
@jwt_required()
def get_pacientes():
    pacientes = Paciente.query.all()
    return jsonify([p.to_dict() for p in pacientes]), 200

@app.route('/api/pacientes/<int:paciente_id>', methods=['GET'])
@jwt_required()
def get_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    return jsonify(paciente.to_dict()), 200

# ============ MÉDICOS ============

@app.route('/api/medicos', methods=['GET'])
@jwt_required()
def get_medicos():
    current_id = int(get_jwt_identity())
    current_user = Usuario.query.get(current_id)
    
    # Administradores ven todos los médicos, otros solo activos
    if current_user.rol.nombre == 'administrador':
        medicos = Medico.query.all()
    else:
        medicos = Medico.query.filter_by(activo=True).all()
    
    return jsonify([m.to_dict() for m in medicos]), 200

@app.route('/api/medicos/<int:medico_id>', methods=['GET'])
@jwt_required()
def get_medico(medico_id):
    medico = Medico.query.get_or_404(medico_id)
    return jsonify(medico.to_dict()), 200

@app.route('/api/medicos/<int:medico_id>', methods=['PUT'])
@jwt_required()
def update_medico(medico_id):
    current_id = int(get_jwt_identity())
    current_user = Usuario.query.get(current_id)
    medico = Medico.query.get_or_404(medico_id)
    
    # Solo el propio médico o un administrador puede modificar
    if medico.usuario.id != current_id and current_user.rol.nombre != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if 'especialidad' in data:
        # Buscar la especialidad por nombre para obtener el nombre correcto
        if 'especialidad_id' in data and data['especialidad_id']:
            esp = Especialidad.query.get(data['especialidad_id'])
            if esp:
                medico.especialidad = esp.nombre
            else:
                medico.especialidad = data['especialidad']
        else:
            # Solo guardar el nombre
            esp = Especialidad.query.filter_by(nombre=data['especialidad']).first()
            if esp:
                medico.especialidad = esp.nombre
            else:
                medico.especialidad = data['especialidad']
    if 'cedula_profesional' in data:
        medico.cedula_profesional = data['cedula_profesional']
    if 'activo' in data:
        # Solo administradores pueden cambiar el estado activo
        if current_user.rol.nombre == 'administrador':
            medico.activo = data['activo']
    
    db.session.commit()
    return jsonify(medico.to_dict()), 200

@app.route('/api/medicos', methods=['POST'])
@jwt_required()
def create_medico():
    data = request.get_json()
    
    # Verificar que sea administrador
    current_id = int(get_jwt_identity())
    current_user = Usuario.query.get(current_id)
    if current_user.rol.nombre != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    # Buscar o crear el rol de médico
    rol_medico = Rol.query.filter_by(nombre='medico').first()
    if not rol_medico:
        return jsonify({'error': 'Rol de médico no encontrado'}), 400
    
    # Buscar el nombre de la especialidad
    nombre_especialidad = ''
    if 'especialidad_id' in data and data['especialidad_id']:
        esp = Especialidad.query.get(data['especialidad_id'])
        if esp:
            nombre_especialidad = esp.nombre
    elif 'especialidad' in data:
        esp = Especialidad.query.filter_by(nombre=data['especialidad']).first()
        if esp:
            nombre_especialidad = esp.nombre
        else:
            nombre_especialidad = data['especialidad']
    
    # Crear el usuario del médico
    nuevo_usuario = Usuario(
        email=data['email'],
        nombre=data['nombre'],
        apellido=data['apellido'],
        telefono=data.get('telefono', ''),
        rol_id=rol_medico.id,
        activo=True
    )
    nuevo_usuario.set_password(data['password'])
    db.session.add(nuevo_usuario)
    db.session.flush()
    
    # Crear el registro de médico
    nuevo_medico = Medico(
        usuario_id=nuevo_usuario.id,
        especialidad=nombre_especialidad,
        cedula_profesional=data.get('cedula_profesional', ''),
        activo=True
    )
    db.session.add(nuevo_medico)
    db.session.commit()
    
    return jsonify(nuevo_medico.to_dict()), 201

@app.route('/api/medicos/<int:medico_id>', methods=['DELETE'])
@jwt_required()
def delete_medico(medico_id):
    current_id = int(get_jwt_identity())
    current_user = Usuario.query.get(current_id)
    
    if current_user.rol.nombre != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    medico = Medico.query.get_or_404(medico_id)
    usuario_id = medico.usuario_id
    
    from models import Cita, Disponibilidad, HistorialMedico
    
    # Eliminar disponibilidad
    Disponibilidad.query.filter_by(medico_id=medico_id).delete()
    # Eliminar citas
    Cita.query.filter_by(medico_id=medico_id).delete()
    # Eliminar historial
    HistorialMedico.query.filter_by(medico_id=medico_id).delete()
    
    db.session.delete(medico)
    
    # Eliminar también el usuario del médico
    usuario = Usuario.query.get(usuario_id)
    if usuario:
        db.session.delete(usuario)
    
    db.session.commit()
    
    return jsonify({'message': 'Médico eliminado correctamente'}), 200

# ============ DISPONIBILIDAD ============

@app.route('/api/disponibilidad/medico/<int:medico_id>', methods=['GET'])
@jwt_required()
def get_disponibilidad_medico(medico_id):
    disponibilidad = Disponibilidad.query.filter_by(medico_id=medico_id, activo=True).all()
    return jsonify([d.to_dict() for d in disponibilidad]), 200

@app.route('/api/disponibilidad/medico/<int:medico_id>', methods=['POST'])
@jwt_required()
def create_disponibilidad(medico_id):
    current_id = int(get_jwt_identity())
    medico = Medico.query.get_or_404(medico_id)
    
    if medico.usuario_id != current_id:
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if 'dia_semana' not in data or 'hora_inicio' not in data or 'hora_fin' not in data:
        return jsonify({'error': 'Campos requeridos: dia_semana, hora_inicio, hora_fin'}), 400
    
    if not validate_time(data['hora_inicio']) or not validate_time(data['hora_fin']):
        return jsonify({'error': 'Horario debe estar entre 6:00 y 20:00'}), 400
    
    dia = int(data['dia_semana'])
    if dia < 1 or dia > 7:
        return jsonify({'error': 'Día debe ser 1-7 (Lunes-Domingo)'}), 400
    
    disp = Disponibilidad(
        medico_id=medico_id,
        dia_semana=dia,
        hora_inicio=datetime.strptime(data['hora_inicio'], '%H:%M').time(),
        hora_fin=datetime.strptime(data['hora_fin'], '%H:%M').time()
    )
    db.session.add(disp)
    db.session.commit()
    
    return jsonify(disp.to_dict()), 201

@app.route('/api/disponibilidad/<int:disp_id>', methods=['PUT'])
@jwt_required()
def update_disponibilidad(disp_id):
    disponibilidad = Disponibilidad.query.get_or_404(disp_id)
    data = request.get_json()
    
    if 'hora_inicio' in data:
        disponibilidad.hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
    if 'hora_fin' in data:
        disponibilidad.hora_fin = datetime.strptime(data['hora_fin'], '%H:%M').time()
    if 'activo' in data:
        disponibilidad.activo = data['activo']
    
    db.session.commit()
    return jsonify(disponibilidad.to_dict()), 200

# ============ CITAS ============

@app.route('/api/citas', methods=['GET'])
@jwt_required()
def get_citas():
    paciente_id = request.args.get('paciente_id')
    medico_id = request.args.get('medico_id')
    fecha = request.args.get('fecha')
    estado = request.args.get('estado')
    
    query = Cita.query
    
    if paciente_id:
        query = query.filter_by(paciente_id=paciente_id)
    if medico_id:
        query = query.filter_by(medico_id=medico_id)
    if fecha:
        query = query.filter_by(fecha=datetime.strptime(fecha, '%Y-%m-%d').date())
    if estado:
        query = query.filter_by(estado=estado)
    
    citas = query.order_by(Cita.fecha, Cita.hora).all()
    return jsonify([c.to_dict() for c in citas]), 200

@app.route('/api/citas', methods=['POST'])
@jwt_required()
def create_cita():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol.nombre != 'paciente':
        return jsonify({'error': 'Solo pacientes pueden crear citas'}), 403
    
    paciente = Paciente.query.filter_by(usuario_id=current_id).first()
    if not paciente:
        return jsonify({'error': 'Paciente no encontrado'}), 404
    
    data = request.get_json()
    
    required = ['medico_id', 'fecha', 'hora', 'tipo_consulta']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Campo {field} requerido'}), 400
    
    try:
        fecha_cita = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        hora_cita = datetime.strptime(data['hora'], '%H:%M').time()
    except:
        return jsonify({'error': 'Formato de fecha u hora inválido'}), 400
    
    if fecha_cita < date.today():
        return jsonify({'error': 'No se pueden agendar citas en fechas pasadas'}), 400
    
    dia_semana = fecha_cita.isoweekday()
    if dia_semana > 7:
        return jsonify({'error': 'Solo se pueden agendar citas de lunes a domingo'}), 400
    
    disponibilidad = Disponibilidad.query.filter_by(
        medico_id=data['medico_id'],
        dia_semana=dia_semana,
        activo=True
    ).first()
    
    if not disponibilidad:
        return jsonify({'error': 'El médico no tiene disponibilidad para este día. Por favor seleccione otro día.'}), 400
    
    if hora_cita < disponibilidad.hora_inicio or hora_cita > disponibilidad.hora_fin:
        return jsonify({'error': 'El médico no atiende en este horario. Horario disponible: ' + str(disponibilidad.hora_inicio) + ' a ' + str(disponibilidad.hora_fin)}), 400
    
    # Verificar citas existentes (pendiente o confirmada)
    cita_existente = Cita.query.filter(
        Cita.medico_id == data['medico_id'],
        Cita.fecha == fecha_cita,
        Cita.hora == hora_cita,
        Cita.estado.in_(['pendiente', 'confirmada'])
    ).first()
    
    if cita_existente:
        return jsonify({'error': 'Ya existe una cita agendada en este horario. Por favor seleccione otra hora.'}), 400
    
    cita = Cita(
        paciente_id=paciente.id,
        medico_id=data['medico_id'],
        fecha=fecha_cita,
        hora=hora_cita,
        tipo_consulta=data['tipo_consulta'],
        estado='pendiente'
    )
    db.session.add(cita)
    db.session.commit()
    
    return jsonify(cita.to_dict()), 201

@app.route('/api/citas/<int:cita_id>', methods=['GET'])
@jwt_required()
def get_cita(cita_id):
    cita = Cita.query.get_or_404(cita_id)
    return jsonify(cita.to_dict()), 200

@app.route('/api/citas/<int:cita_id>', methods=['PUT'])
@jwt_required()
def update_cita(cita_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    cita = Cita.query.get_or_404(cita_id)
    
    data = request.get_json()
    
    # Administrador puede modificar cualquier campo
    if usuario.rol.nombre == 'administrador':
        if 'estado' in data:
            cita.estado = data['estado']
        if 'observaciones' in data:
            cita.observaciones = data['observaciones']
        if 'fecha' in data:
            cita.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        if 'hora' in data:
            cita.hora = datetime.strptime(data['hora'], '%H:%M').time()
    elif usuario.rol.nombre == 'paciente':
        paciente = Paciente.query.filter_by(usuario_id=current_id).first()
        if cita.paciente_id != paciente.id:
            return jsonify({'error': 'No autorizado'}), 403
        
        if 'estado' in data and data['estado'] in ['cancelada']:
            cita.estado = data['estado']
    elif usuario.rol.nombre == 'medico':
        medico = Medico.query.filter_by(usuario_id=current_id).first()
        if cita.medico_id != medico.id:
            return jsonify({'error': 'No autorizado'}), 403
        
        if 'estado' in data:
            cita.estado = data['estado']
        if 'observaciones' in data:
            cita.observaciones = data['observaciones']
    
    db.session.commit()
    return jsonify(cita.to_dict()), 200

@app.route('/api/citas/<int:cita_id>', methods=['DELETE'])
@jwt_required()
def delete_cita(cita_id):
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    cita = Cita.query.get_or_404(cita_id)
    
    paciente = Paciente.query.filter_by(usuario_id=current_id).first()
    
    if usuario.rol.nombre == 'paciente':
        if cita.paciente_id != paciente.id:
            return jsonify({'error': 'No autorizado'}), 403
    elif usuario.rol.nombre != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    cita.estado = 'cancelada'
    db.session.commit()
    
    return jsonify({'message': 'Cita cancelada'}), 200

# ============ HISTORIAL MÉDICO ============

@app.route('/api/historial/paciente/<int:paciente_id>', methods=['GET'])
@jwt_required()
def get_historial_paciente(paciente_id):
    historial = HistorialMedico.query.filter_by(paciente_id=paciente_id).order_by(HistorialMedico.fecha_registro.desc()).all()
    return jsonify([h.to_dict() for h in historial]), 200

@app.route('/api/historial', methods=['POST'])
@jwt_required()
def create_historial():
    current_id = int(get_jwt_identity())
    usuario = Usuario.query.get(current_id)
    
    if usuario.rol.nombre != 'medico':
        return jsonify({'error': 'Solo médicos pueden registrar historial'}), 403
    
    data = request.get_json()
    
    required = ['paciente_id', 'diagnostico']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Campo {field} requerido'}), 400
    
    # Obtener el médico actual
    medico = Medico.query.filter_by(usuario_id=current_id).first()
    if not medico:
        return jsonify({'error': 'Médico no encontrado'}), 404
    
    historial = HistorialMedico(
        paciente_id=data['paciente_id'],
        medico_id=medico.id,
        cita_id=data.get('cita_id'),
        diagnostico=data['diagnostico'],
        tratamiento=data.get('tratamiento', ''),
        observaciones=data.get('observaciones', '')
    )
    db.session.add(historial)
    
    # Si se proporciona cita_id, marcar la cita como completada
    if data.get('cita_id'):
        cita = Cita.query.get(data['cita_id'])
        if cita:
            cita.estado = 'completada'
    
    db.session.commit()
    
    return jsonify(historial.to_dict()), 201

# ============ INICIALIZAR BASE DE DATOS ============

@app.route('/api/init', methods=['POST'])
def init_db():
    try:
        db.create_all()
        
        # Migración: agregar columna cedula si no existe (solo si la tabla ya existe)
        try:
            db.session.execute(db.text("ALTER TABLE pacientes ADD COLUMN cedula VARCHAR(20)"))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        
        # Crear tablas si no existen
        db.create_all()
        
        rol_paciente = Rol.query.filter_by(nombre='paciente').first()
        rol_medico = Rol.query.filter_by(nombre='medico').first()
        rol_admin = Rol.query.filter_by(nombre='administrador').first()
        
        if not rol_paciente:
            rol_paciente = Rol(nombre='paciente', descripcion='Usuario que solicita citas médicas')
            db.session.add(rol_paciente)
        
        if not rol_medico:
            rol_medico = Rol(nombre='medico', descripcion='Profesional de la salud que atiende citas')
            db.session.add(rol_medico)
        
        if not rol_admin:
            rol_admin = Rol(nombre='administrador', descripcion='Usuario que gestiona el sistema')
            db.session.add(rol_admin)
        
        db.session.commit()
        
        admin_exists = Usuario.query.filter_by(email='admin@hospital.com').first()
        if not admin_exists:
            hashed = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = Usuario(
                email='admin@hospital.com',
                password=hashed,
                nombre='Admin',
                apellido='Sistema',
                telefono='3000000000',
                rol_id=rol_admin.id
            )
            db.session.add(admin)
        
        # Crear paciente de prueba
        paciente_exists = Usuario.query.filter_by(email='paciente@test.com').first()
        if not paciente_exists:
            hashed_paciente = bcrypt.generate_password_hash('paciente123').decode('utf-8')
            usuario_paciente = Usuario(
                email='paciente@test.com',
                password=hashed_paciente,
                nombre='Juan',
                apellido='Pérez',
                telefono='3001234567',
                rol_id=rol_paciente.id
            )
            db.session.add(usuario_paciente)
            db.session.flush()
            
            paciente = Paciente(
                usuario_id=usuario_paciente.id,
                fecha_nacimiento=date(1990, 5, 15),
                direccion='Calle 123, Ciudad'
            )
            db.session.add(paciente)
        
        # Crear médico de prueba
        medico_exists = Usuario.query.filter_by(email='medico@test.com').first()
        if not medico_exists:
            hashed_medico = bcrypt.generate_password_hash('medico123').decode('utf-8')
            usuario_medico = Usuario(
                email='medico@test.com',
                password=hashed_medico,
                nombre='María',
                apellido='García',
                telefono='3009876543',
                rol_id=rol_medico.id
            )
            db.session.add(usuario_medico)
            db.session.flush()
            
            medico = Medico(
                usuario_id=usuario_medico.id,
                especialidad='Medicina General',
                cedula_profesional='MD-12345'
            )
            db.session.add(medico)
            db.session.flush()
            
            # Disponibilidad del médico (Lun-Dom 8am-5pm)
            for dia in range(1, 8):
                disp = Disponibilidad(
                    medico_id=medico.id,
                    dia_semana=dia,
                    hora_inicio=time(8, 0),
                    hora_fin=time(17, 0)
                )
                db.session.add(disp)
        
        # Crear segundo médico
        medico2_exists = Usuario.query.filter_by(email='medico2@test.com').first()
        if not medico2_exists:
            hashed_medico2 = bcrypt.generate_password_hash('medico123').decode('utf-8')
            usuario_medico2 = Usuario(
                email='medico2@test.com',
                password=hashed_medico2,
                nombre='Carlos',
                apellido='López',
                telefono='3008765432',
                rol_id=rol_medico.id
)
            db.session.add(usuario_medico2)
            db.session.flush()
            
            medico2 = Medico(
                usuario_id=usuario_medico2.id,
                especialidad='Cardiología',
                cedula_profesional='MD-67890'
            )
            db.session.add(medico2)
            db.session.flush()
        
        # Crear estados por defecto
        estados_default = [
            {'nombre': 'activo', 'descripcion': 'Usuario activo en el sistema', 'color': '#10B981'},
            {'nombre': 'inactivo', 'descripcion': 'Usuario inactivo en el sistema', 'color': '#EF4444'},
            {'nombre': 'pendiente', 'descripcion': 'Cita awaiting confirmation', 'color': '#F59E0B'},
            {'nombre': 'confirmada', 'descripcion': 'Cita confirmada por el médico', 'color': '#10B981'},
            {'nombre': 'cancelada', 'descripcion': 'Cita cancelada por el paciente o médico', 'color': '#EF4444'},
            {'nombre': 'completada', 'descripcion': 'Cita atendidos exitosamente', 'color': '#3B82F6'},
        ]
        
        for e in estados_default:
            est_existe = Estado.query.filter_by(nombre=e['nombre']).first()
            if not est_existe:
                nuevo_est = Estado(nombre=e['nombre'], descripcion=e['descripcion'], color=e['color'])
                db.session.add(nuevo_est)
        
        # Crear especialidades con descripcion
        especialidades_default = [
            {'nombre': 'Medicina General', 'descripcion': 'Atención primaria de salud, consulta general'},
            {'nombre': 'Medicina Interna', 'descripcion': 'Enfermedades adultas no quirúrgicas'},
            {'nombre': 'Pediatría', 'descripcion': 'Atención médica para niños y adolescentes'},
            {'nombre': 'Ginecología', 'descripcion': 'Salud de la mujer y sistema reproductor'},
            {'nombre': 'Cardiología', 'descripcion': 'Enfermedades del corazón y sistema circulatorio'},
            {'nombre': 'Dermatología', 'descripcion': 'Enfermedades de la piel'},
            {'nombre': 'Oftalmología', 'descripcion': 'Enfermedades de los ojos'},
            {'nombre': 'Ortopedia', 'descripcion': 'Enfermedades de los huesos y músculos'},
            {'nombre': 'Neurología', 'descripcion': 'Enfermedades del sistema nervioso'},
            {'nombre': 'Psicología', 'descripcion': 'Salud mental y comportamiento'},
        ]
        
        for esp in especialidades_default:
            esp_existe = Especialidad.query.filter_by(nombre=esp['nombre']).first()
            if not esp_existe:
                nueva_esp = Especialidad(nombre=esp['nombre'], descripcion=esp['descripcion'], activo=True)
                db.session.add(nueva_esp)
        
        # Crear citas de ejemplo
        from datetime import datetime, timedelta
        paciente = Paciente.query.first()
        medico = Medico.query.first()
        medico2 = Medico.query.filter(Medico.especialidad == 'Cardiología').first()
        
        if paciente and medico:
            # Citas para hoy
            fecha_hoy = date.today()
            citas_ejemplo = [
                {'paciente': paciente.id, 'medico': medico.id, 'fecha': fecha_hoy, 'hora': time(9, 0), 'tipo': 'Medicina General', 'estado': 'confirmada'},
                {'paciente': paciente.id, 'medico': medico.id, 'fecha': fecha_hoy, 'hora': time(10, 30), 'tipo': 'Medicina General', 'estado': 'pendiente'},
                {'paciente': paciente.id, 'medico': medico.id, 'fecha': fecha_hoy, 'hora': time(14, 0), 'tipo': 'Medicina General', 'estado': 'pendiente'},
            ]
            if medico2:
                citas_ejemplo.append({'paciente': paciente.id, 'medico': medico2.id, 'fecha': fecha_hoy, 'hora': time(11, 0), 'tipo': 'Cardiología', 'estado': 'confirmada'})
            
            for c in citas_ejemplo:
                cita_existe = Cita.query.filter_by(paciente_id=c['paciente'], medico_id=c['medico'], fecha=c['fecha'], hora=c['hora']).first()
                if not cita_existe:
                    nueva_cita = Cita(
                        paciente_id=c['paciente'],
                        medico_id=c['medico'],
                        fecha=c['fecha'],
                        hora=c['hora'],
                        tipo_consulta=c['tipo'],
                        estado=c['estado']
                    )
                    db.session.add(nueva_cita)
        
        db.session.commit()
        
        return jsonify({'message': 'Base de datos inicializada correctamente con usuarios de prueba'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ ESTADOS ============

@app.route('/api/estados', methods=['GET'])
@jwt_required()
def get_estados():
    estados = Estado.query.all()
    return jsonify([e.to_dict() for e in estados]), 200

@app.route('/api/estados', methods=['POST'])
@jwt_required()
def create_estado():
    current_id = int(get_jwt_identity())
    current_user = Usuario.query.get(current_id)
    
    if current_user.rol.nombre != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if 'nombre' not in data:
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    nuevo = Estado(
        nombre=data['nombre'],
        descripcion=data.get('descripcion', ''),
        color=data.get('color', '#64748B')
    )
    db.session.add(nuevo)
    db.session.commit()
    
    return jsonify(nuevo.to_dict()), 201

# ============ ESPECIALIDADES ============

@app.route('/api/especialidades', methods=['GET'])
@jwt_required()
def get_especialidades():
    especialidades = Especialidad.query.filter_by(activo=True).all()
    return jsonify([e.to_dict() for e in especialidades]), 200

@app.route('/api/especialidades', methods=['POST'])
@jwt_required()
def create_especialidad():
    current_id = int(get_jwt_identity())
    current_user = Usuario.query.get(current_id)
    
    if current_user.rol.nombre != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if 'nombre' not in data:
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    # Verificar que no exista
    existente = Especialidad.query.filter_by(nombre=data['nombre']).first()
    if existente:
        return jsonify({'error': 'La especialidad ya existe'}), 400
    
    nueva = Especialidad(
        nombre=data['nombre'],
        descripcion=data.get('descripcion', '')
    )
    db.session.add(nueva)
    db.session.commit()
    
    return jsonify(nueva.to_dict()), 201

@app.route('/api/especialidades/<int:esp_id>', methods=['PUT'])
@jwt_required()
def update_especialidad(esp_id):
    current_id = int(get_jwt_identity())
    current_user = Usuario.query.get(current_id)
    
    if current_user.rol.nombre != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    especialidad = Especialidad.query.get_or_404(esp_id)
    data = request.get_json()
    
    if 'nombre' in data:
        especialidad.nombre = data['nombre']
    if 'descripcion' in data:
        especialidad.descripcion = data['descripcion']
    if 'activo' in data:
        especialidad.activo = data['activo']
    
    db.session.commit()
    return jsonify(especialidad.to_dict()), 200

@app.route('/api/especialidades/<int:esp_id>', methods=['DELETE'])
@jwt_required()
def delete_especialidad(esp_id):
    current_id = int(get_jwt_identity())
    current_user = Usuario.query.get(current_id)
    
    if current_user.rol.nombre != 'administrador':
        return jsonify({'error': 'No autorizado'}), 403
    
    especialidad = Especialidad.query.get_or_404(esp_id)
    especialidad.activo = False
    db.session.commit()
    
    return jsonify({'message': 'Especialidad eliminada'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)