-- Sistema de Citas Médicas - PostgreSQL
-- Base de datos: ClaseLunesPruebasSoftware

-- Tabla de roles
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL UNIQUE,
    descripcion TEXT
);

-- Tabla de usuarios (padre para pacientes, médicos y administradores)
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    rol_id INTEGER NOT NULL REFERENCES roles(id),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de pacientes
CREATE TABLE IF NOT EXISTS pacientes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL UNIQUE REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_nacimiento DATE,
    direccion TEXT,
    historial_clinico TEXT
);

-- Tabla de médicos
CREATE TABLE IF NOT EXISTS medicos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL UNIQUE REFERENCES usuarios(id) ON DELETE CASCADE,
    especialidad VARCHAR(100) NOT NULL,
    cedula_profesional VARCHAR(50) UNIQUE,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de disponibilidad de médicos
CREATE TABLE IF NOT EXISTS disponibilidad (
    id SERIAL PRIMARY KEY,
    medico_id INTEGER NOT NULL REFERENCES medicos(id) ON DELETE CASCADE,
    dia_semana INTEGER NOT NULL CHECK (dia_semana >= 1 AND dia_semana <= 7),
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    UNIQUE(medico_id, dia_semana, hora_inicio)
);

-- Tabla de citas
CREATE TABLE IF NOT EXISTS citas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id),
    medico_id INTEGER NOT NULL REFERENCES medicos(id),
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    tipo_consulta VARCHAR(50) NOT NULL DEFAULT 'Medicina General',
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'confirmada', 'cancelada', 'completada')),
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de historial médico
CREATE TABLE IF NOT EXISTS historial_medico (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id),
    medico_id INTEGER NOT NULL REFERENCES medicos(id),
    cita_id INTEGER REFERENCES citas(id),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    diagnostico TEXT,
    tratamiento TEXT,
    observaciones TEXT
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_citas_paciente ON citas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_citas_medico ON citas(medico_id);
CREATE INDEX IF NOT EXISTS idx_citas_fecha ON citas(fecha);
CREATE INDEX IF NOT EXISTS idx_citas_estado ON citas(estado);
CREATE INDEX IF NOT EXISTS idx_disponibilidad_medico ON disponibilidad(medico_id);
CREATE INDEX IF NOT EXISTS idx_historial_paciente ON historial_medico(paciente_id);

-- Insertar roles base
INSERT INTO roles (nombre, descripcion) VALUES 
    ('paciente', 'Usuario que solicita citas médicas'),
    ('medico', 'Profesional de la salud que atiende citas'),
    ('administrador', 'Usuario que gestiona el sistema')
ON CONFLICT (nombre) DO NOTHING;

-- Insertar usuario administrador por defecto (password: admin123)
-- Password hash de 'admin123' usando bcrypt
INSERT INTO usuarios (email, password, nombre, apellido, telefono, rol_id)
VALUES ('admin@hospital.com', '$2b$12$KIXxP8kYz9j.vPqQ.X5YEO.Y5L0qN6zR8W8Y5L3kX5YEO.Y5L0q', 'Administrador', 'Sistema', '3000000000', 3)
ON CONFLICT (email) DO NOTHING;