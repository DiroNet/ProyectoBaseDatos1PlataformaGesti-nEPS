-- ========================================
-- SEED DATA - Sistema EPS Bienestar
-- MySQL Version
-- Password para todos: admin123
-- ========================================

INSERT IGNORE INTO usuarios (email, password, nombre, rol) VALUES
('admin@eps.com', '$2b$12$T9NP9i8aOjgbTFwB5NL4BejLW420nGwo/LIC./2iAEFm9xxKRJ8w.', 'Administrador', 'ADMIN'),
('afiliado@test.com', '$2b$12$T9NP9i8aOjgbTFwB5NL4BejLW420nGwo/LIC./2iAEFm9xxKRJ8w.', 'Juan Pérez', 'AFILIADO'),
('profesional@test.com', '$2b$12$T9NP9i8aOjgbTFwB5NL4BejLW420nGwo/LIC./2iAEFm9xxKRJ8w.', 'Dra. María García', 'PROFESIONAL'),
('drlorenzo@test.com', '$2b$12$T9NP9i8aOjgbTFwB5NL4BejLW420nGwo/LIC./2iAEFm9xxKRJ8w.', 'Dr. Carlos Lorenzo', 'PROFESIONAL');

INSERT IGNORE INTO afiliados (id_usuario, documento, telefono, direccion, id_plan)
SELECT id_usuario, '12345678', '3001234567', 'Calle 123, Ciudad', 1
FROM usuarios WHERE email = 'afiliado@test.com';

INSERT IGNORE INTO profesionales (id_usuario, especialidad, id_centro)
SELECT id_usuario, 'Medicina General', 1
FROM usuarios WHERE email = 'profesional@test.com';

INSERT IGNORE INTO profesionales (id_usuario, especialidad, id_centro)
SELECT id_usuario, 'Cardiología', 1
FROM usuarios WHERE email = 'drlorenzo@test.com';

INSERT IGNORE INTO disponibilidad_profesional (id_profesional, dia_semana, hora_inicio, hora_fin, activo)
SELECT p.id_profesional, dia_semana, hora_inicio, hora_fin, 1
FROM profesionales p
CROSS JOIN (
    SELECT 1 AS dia_semana, '08:00' AS hora_inicio, '17:00' AS hora_fin
    UNION ALL SELECT 2, '08:00', '17:00'
    UNION ALL SELECT 3, '08:00', '17:00'
    UNION ALL SELECT 4, '08:00', '17:00'
    UNION ALL SELECT 5, '08:00', '17:00'
) AS horarios
WHERE p.usuario_id IN (SELECT id_usuario FROM usuarios WHERE email IN ('profesional@test.com', 'drlorenzo@test.com'))
AND NOT EXISTS (
    SELECT 1 FROM disponibilidad_profesional dp
    WHERE dp.id_profesional = p.id_profesional AND dp.dia_semana = horarios.dia_semana
);