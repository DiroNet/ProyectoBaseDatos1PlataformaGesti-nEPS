from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Rol(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    
    def to_dict(self):
        return {'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion}

class Estado(db.Model):
    __tablename__ = 'estados'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    color = db.Column(db.String(20))
    
    def to_dict(self):
        return {'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion, 'color': self.color}

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    rol = db.relationship('Rol', backref='usuarios')
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self, include_paciente=False, include_medico=False):
        data = {
            'id': self.id,
            'email': self.email,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'telefono': self.telefono,
            'rol_id': self.rol_id,
            'rol_nombre': self.rol.nombre if self.rol else None,
            'activo': self.activo,
            'estado': 'activo' if self.activo else 'inactivo'
        }
        # Buscar paciente directamente por usuario_id
        paciente = Paciente.query.filter_by(usuario_id=self.id).first()
        if paciente:
            data['paciente_id'] = paciente.id
        # Buscar médico directamente por usuario_id
        medico = Medico.query.filter_by(usuario_id=self.id).first()
        if medico:
            data['medico_id'] = medico.id
        return data

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    direccion = db.Column(db.Text)
    historial_clinico = db.Column(db.Text)
    
    usuario = db.relationship('Usuario', backref='paciente')
    citas = db.relationship('Cita', backref='paciente', lazy='dynamic')
    historial = db.relationship('HistorialMedico', backref='paciente', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'fecha_nacimiento': str(self.fecha_nacimiento) if self.fecha_nacimiento else None,
            'direccion': self.direccion,
            'usuario': self.usuario.to_dict() if self.usuario else None
        }

class Medico(db.Model):
    __tablename__ = 'medicos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    cedula_profesional = db.Column(db.String(50), unique=True)
    activo = db.Column(db.Boolean, default=True)
    
    usuario = db.relationship('Usuario', backref='medico')
    disponibilidad = db.relationship('Disponibilidad', backref='medico', lazy='dynamic', cascade='all, delete-orphan')
    citas = db.relationship('Cita', backref='medico', lazy='dynamic')
    historial = db.relationship('HistorialMedico', backref='medico', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'especialidad': self.especialidad,
            'cedula_profesional': self.cedula_profesional,
            'activo': self.activo,
            'usuario': self.usuario.to_dict() if self.usuario else None
        }

class Disponibilidad(db.Model):
    __tablename__ = 'disponibilidad'
    
    id = db.Column(db.Integer, primary_key=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'medico_id': self.medico_id,
            'dia_semana': self.dia_semana,
            'hora_inicio': str(self.hora_inicio),
            'hora_fin': str(self.hora_fin),
            'activo': self.activo
        }

class Cita(db.Model):
    __tablename__ = 'citas'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    tipo_consulta = db.Column(db.String(50), default='Medicina General')
    estado = db.Column(db.String(20), default='pendiente')
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'paciente_id': self.paciente_id,
            'medico_id': self.medico_id,
            'fecha': str(self.fecha),
            'hora': str(self.hora),
            'tipo_consulta': self.tipo_consulta,
            'estado': self.estado,
            'observaciones': self.observaciones,
            'paciente': self.paciente.to_dict() if self.paciente else None,
            'medico': self.medico.to_dict() if self.medico else None
        }

class HistorialMedico(db.Model):
    __tablename__ = 'historial_medico'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    cita_id = db.Column(db.Integer, db.ForeignKey('citas.id'))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    diagnostico = db.Column(db.Text)
    tratamiento = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'paciente_id': self.paciente_id,
            'medico_id': self.medico_id,
            'cita_id': self.cita_id,
            'fecha_registro': str(self.fecha_registro),
            'diagnostico': self.diagnostico,
            'tratamiento': self.tratamiento,
            'observaciones': self.observaciones
        }

class Especialidad(db.Model):
    __tablename__ = 'especialidades'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion, 'activo': self.activo}
