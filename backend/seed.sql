-- Datos de prueba para el sistema de citas médicas
-- Ejecutar después de crear las tablas

-- Verificar que existan los roles
INSERT INTO roles (nombre, descripcion) VALUES 
    ('paciente', 'Usuario que solicita citas médicas'),
    ('medico', 'Profesional de la salud que atiende citas'),
    ('administrador', 'Usuario que gestiona el sistema')
ON CONFLICT (nombre) DO NOTHING;

-- Crear paciente de prueba (password: paciente123)
-- Hash de bcrypt para 'paciente123'
INSERT INTO usuarios (email, password, nombre, apellido, telefono, rol_id)
SELECT 'paciente@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQ3Z5kK7e', 'Juan', 'Pérez', '3001234567', id FROM roles WHERE nombre = 'paciente'
WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE email = 'paciente@test.com');

-- Obtener ID del paciente creado
DO $$
DECLARE
    paciente_user_id INTEGER;
    paciente_id INTEGER;
BEGIN
    SELECT id INTO paciente_user_id FROM usuarios WHERE email = 'paciente@test.com';
    IF paciente_user_id IS NOT NULL THEN
        INSERT INTO pacientes (usuario_id, fecha_nacimiento, direccion)
        SELECT paciente_user_id, '1990-05-15', 'Calle 123, Ciudad'
        WHERE NOT EXISTS (SELECT 1 FROM pacientes WHERE usuario_id = paciente_user_id);
    END IF;
END $$;

-- Crear médico de prueba (password: medico123)
INSERT INTO usuarios (email, password, nombre, apellido, telefono, rol_id)
SELECT 'medico@test.com', '$2b$12$KIXxP8kYz9j.vPqQ.X5YEO.Y5L0qN6zR8W8Y5L3kX5YEO.Y5L0q', 'María', 'García', '3009876543', id FROM roles WHERE nombre = 'medico'
WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE email = 'medico@test.com');

-- Crear médico
DO $$
DECLARE
    medico_user_id INTEGER;
    medico_id INTEGER;
BEGIN
    SELECT id INTO medico_user_id FROM usuarios WHERE email = 'medico@test.com';
    IF medico_user_id IS NOT NULL THEN
        INSERT INTO medicos (usuario_id, especialidad, cedula_profesional)
        SELECT medico_user_id, 'Medicina General', 'MD-12345'
        WHERE NOT EXISTS (SELECT 1 FROM medicos WHERE usuario_id = medico_user_id);
        
        SELECT id INTO medico_id FROM medicos WHERE usuario_id = medico_user_id;
        
        IF medico_id IS NOT NULL THEN
            INSERT INTO disponibilidad (medico_id, dia_semana, hora_inicio, hora_fin)
            SELECT medico_id, dia, inicio, fin FROM (
                VALUES (1, '08:00'::time, '17:00'::time),
                       (2, '08:00'::time, '17:00'::time),
                       (3, '08:00'::time, '17:00'::time),
                       (4, '08:00'::time, '17:00'::time),
                       (5, '08:00'::time, '17:00'::time)
            ) AS t(dia, inicio, fin)
            WHERE NOT EXISTS (
                SELECT 1 FROM disponibilidad 
                WHERE medico_id = medico_id AND dia_semana = t.dia
            );
        END IF;
    END IF;
END $$;

-- Crear segundo médico
INSERT INTO usuarios (email, password, nombre, apellido, telefono, rol_id)
SELECT 'medico2@test.com', '$2b$12$ABCdefGHIJKLMNOPQRSTU.OYQv0r6W1A2B3C4D5E6F7G8H9I0JK', 'Carlos', 'López', '3008765432', id FROM roles WHERE nombre = 'medico'
WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE email = 'medico2@test.com');

DO $$
DECLARE
    medico_user_id INTEGER;
    medico_id INTEGER;
BEGIN
    SELECT id INTO medico_user_id FROM usuarios WHERE email = 'medico2@test.com';
    IF medico_user_id IS NOT NULL THEN
        INSERT INTO medicos (usuario_id, especialidad, cedula_profesional)
        SELECT medico_user_id, 'Cardiología', 'MD-67890'
        WHERE NOT EXISTS (SELECT 1 FROM medicos WHERE usuario_id = medico_user_id);
        
        SELECT id INTO medico_id FROM medicos WHERE usuario_id = medico_user_id;
        
        IF medico_id IS NOT NULL THEN
            INSERT INTO disponibilidad (medico_id, dia_semana, hora_inicio, hora_fin)
            SELECT medico_id, dia, inicio, fin FROM (
                VALUES (1, '09:00'::time, '16:00'::time),
                       (3, '09:00'::time, '16:00'::time),
                       (5, '09:00'::time, '16:00'::time)
            ) AS t(dia, inicio, fin)
            WHERE NOT EXISTS (
                SELECT 1 FROM disponibilidad 
                WHERE medico_id = medico_id AND dia_semana = t.dia
            );
        END IF;
    END IF;
END $$;

-- Admin ya creado en el script principal