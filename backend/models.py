from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta

db = SQLAlchemy()

def get_colombia_datetime():
    return datetime.now(timezone(timedelta(hours=-5)))

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('AFILIADO', 'ADMIN', 'PROFESIONAL'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id_usuario': self.id_usuario,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'fecha_creacion': str(self.fecha_creacion) if self.fecha_creacion else None
        }

class Plan(db.Model):
    __tablename__ = 'planes'
    
    id_plan = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    costo = db.Column(db.Numeric(10, 2))
    
    def to_dict(self):
        return {
            'id_plan': self.id_plan,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'costo': float(self.costo) if self.costo else None
        }

class Afiliado(db.Model):
    __tablename__ = 'afiliados'
    
    id_afiliado = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    documento = db.Column(db.String(20))
    fecha_nacimiento = db.Column(db.Date)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(150))
    id_plan = db.Column(db.Integer, db.ForeignKey('planes.id_plan'))
    
    usuario = db.relationship('Usuario', backref='afiliado')
    plan = db.relationship('Plan', backref='afiliados')
    citas = db.relationship('Cita', backref='afiliado', lazy='dynamic')
    facturas = db.relationship('Factura', backref='afiliado', lazy='dynamic')
    historial = db.relationship('HistorialClinico', backref='afiliado', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id_afiliado': self.id_afiliado,
            'id_usuario': self.id_usuario,
            'documento': self.documento,
            'fecha_nacimiento': str(self.fecha_nacimiento) if self.fecha_nacimiento else None,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'id_plan': self.id_plan,
            'plan': self.plan.to_dict() if self.plan else None,
            'usuario': {'nombre': self.usuario.nombre, 'email': self.usuario.email} if self.usuario else None
        }

class CentroSalud(db.Model):
    __tablename__ = 'centros_salud'
    
    id_centro = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(150))
    ciudad = db.Column(db.String(50))
    
    profesionales = db.relationship('Profesional', backref='centro', lazy='dynamic')
    citas = db.relationship('Cita', backref='centro', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id_centro': self.id_centro,
            'nombre': self.nombre,
            'direccion': self.direccion,
            'ciudad': self.ciudad
        }

class Profesional(db.Model):
    __tablename__ = 'profesionales'
    
    id_profesional = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    id_centro = db.Column(db.Integer, db.ForeignKey('centros_salud.id_centro'))
    
    usuario = db.relationship('Usuario', backref='profesional')
    citas = db.relationship('Cita', backref='profesional', lazy='dynamic')
    historiales = db.relationship('HistorialClinico', backref='profesional', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id_profesional': self.id_profesional,
            'id_usuario': self.id_usuario,
            'especialidad': self.especialidad,
            'id_centro': self.id_centro,
            'centro': self.centro.to_dict() if self.centro else None,
            'usuario': {'nombre': self.usuario.nombre, 'email': self.usuario.email} if self.usuario else None
        }

class Factura(db.Model):
    __tablename__ = 'facturas'
    
    id_factura = db.Column(db.Integer, primary_key=True)
    id_afiliado = db.Column(db.Integer, db.ForeignKey('afiliados.id_afiliado'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    total = db.Column(db.Numeric(10, 2))
    estado = db.Column(db.Enum('PENDIENTE', 'PAGADA'), default='PENDIENTE')
    
    pagos = db.relationship('Pago', backref='factura', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id_factura': self.id_factura,
            'id_afiliado': self.id_afiliado,
            'fecha': str(self.fecha) if self.fecha else None,
            'total': float(self.total) if self.total else None,
            'estado': self.estado,
            'afiliado': self.afiliado.to_dict() if self.afiliado else None,
            'pagos': [p.to_dict() for p in self.pagos]
        }

class Pago(db.Model):
    __tablename__ = 'pagos'
    
    id_pago = db.Column(db.Integer, primary_key=True)
    id_factura = db.Column(db.Integer, db.ForeignKey('facturas.id_factura'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Numeric(10, 2))
    metodo_pago = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id_pago': self.id_pago,
            'id_factura': self.id_factura,
            'fecha': str(self.fecha) if self.fecha else None,
            'monto': float(self.monto) if self.monto else None,
            'metodo_pago': self.metodo_pago
        }

class Cita(db.Model):
    __tablename__ = 'citas'
    
    id_cita = db.Column(db.Integer, primary_key=True)
    id_afiliado = db.Column(db.Integer, db.ForeignKey('afiliados.id_afiliado'), nullable=False)
    id_profesional = db.Column(db.Integer, db.ForeignKey('profesionales.id_profesional'), nullable=False)
    id_centro = db.Column(db.Integer, db.ForeignKey('centros_salud.id_centro'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.Enum('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'FINALIZADA'), default='PENDIENTE')
    
    def to_dict(self):
        return {
            'id_cita': self.id_cita,
            'id_afiliado': self.id_afiliado,
            'id_profesional': self.id_profesional,
            'id_centro': self.id_centro,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'estado': self.estado,
            'afiliado': self.afiliado.to_dict() if self.afiliado else None,
            'profesional': self.profesional.to_dict() if self.profesional else None,
            'centro': self.centro.to_dict() if self.centro else None
        }

class HistorialClinico(db.Model):
    __tablename__ = 'historial_clinico'
    
    id_historial = db.Column(db.Integer, primary_key=True)
    id_afiliado = db.Column(db.Integer, db.ForeignKey('afiliados.id_afiliado'), nullable=False)
    id_profesional = db.Column(db.Integer, db.ForeignKey('profesionales.id_profesional'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    diagnostico = db.Column(db.Text)
    tratamiento = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id_historial': self.id_historial,
            'id_afiliado': self.id_afiliado,
            'id_profesional': self.id_profesional,
            'fecha': str(self.fecha) if self.fecha else None,
            'diagnostico': self.diagnostico,
            'tratamiento': self.tratamiento,
            'afiliado': self.afiliado.to_dict() if self.afiliado else None,
            'profesional': self.profesional.to_dict() if self.profesional else None
        }

class DisponibilidadProfesional(db.Model):
    __tablename__ = 'disponibilidad_profesional'

    id_disponibilidad = db.Column(db.Integer, primary_key=True)
    id_profesional = db.Column(db.Integer, db.ForeignKey('profesionales.id_profesional'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    activo = db.Column(db.Boolean, default=True)

    profesional = db.relationship('Profesional', backref='disponibilidades')

    def to_dict(self):
        return {
            'id_disponibilidad': self.id_disponibilidad,
            'id_profesional': self.id_profesional,
            'dia_semana': self.dia_semana,
            'hora_inicio': str(self.hora_inicio) if self.hora_inicio else None,
            'hora_fin': str(self.hora_fin) if self.hora_fin else None,
            'activo': self.activo
        }