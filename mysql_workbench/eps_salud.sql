-- ============================================
-- SISTEMA DE GESTIÓN EPS
-- Base de datos: eps_salud
-- Gestor: MySQL Workbench
-- Universidad de Caldas - Bases de Datos I
-- Marzo 2026
-- ============================================

DROP DATABASE IF EXISTS eps_salud;
CREATE DATABASE eps_salud CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE eps_salud;

-- ============================================
-- TABLA DE USUARIOS
-- ============================================
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    rol ENUM('AFILIADO', 'ADMIN', 'PROFESIONAL') NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_rol (rol)
) ENGINE=InnoDB;

-- ============================================
-- TABLA DE PLANES DE SALUD
-- ============================================
CREATE TABLE planes (
    id_plan INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    costo DECIMAL(10, 2) NOT NULL DEFAULT 0.00
) ENGINE=InnoDB;

-- ============================================
-- TABLA DE AFILIADOS
-- ============================================
CREATE TABLE afiliados (
    id_afiliado INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    documento VARCHAR(20),
    fecha_nacimiento DATE,
    telefono VARCHAR(20),
    direccion VARCHAR(150),
    id_plan INT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_plan) REFERENCES planes(id_plan) ON DELETE SET NULL,
    INDEX idx_documento (documento),
    INDEX idx_id_plan (id_plan)
) ENGINE=InnoDB;

-- ============================================
-- TABLA DE CENTROS DE SALUD
-- ============================================
CREATE TABLE centros_salud (
    id_centro INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(150),
    ciudad VARCHAR(50)
) ENGINE=InnoDB;

-- ============================================
-- TABLA DE PROFESIONALES
-- ============================================
CREATE TABLE profesionales (
    id_profesional INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    especialidad VARCHAR(100) NOT NULL,
    id_centro INT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_centro) REFERENCES centros_salud(id_centro) ON DELETE SET NULL,
    INDEX idx_especialidad (especialidad),
    INDEX idx_id_centro (id_centro)
) ENGINE=InnoDB;

-- ============================================
-- TABLA DE CITAS
-- ============================================
CREATE TABLE citas (
    id_cita INT AUTO_INCREMENT PRIMARY KEY,
    id_afiliado INT NOT NULL,
    id_profesional INT NOT NULL,
    id_centro INT NOT NULL,
    fecha DATETIME NOT NULL,
    estado ENUM('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'FINALIZADA') DEFAULT 'PENDIENTE',
    FOREIGN KEY (id_afiliado) REFERENCES afiliados(id_afiliado) ON DELETE CASCADE,
    FOREIGN KEY (id_profesional) REFERENCES profesionales(id_profesional) ON DELETE CASCADE,
    FOREIGN KEY (id_centro) REFERENCES centros_salud(id_centro) ON DELETE CASCADE,
    INDEX idx_fecha (fecha),
    INDEX idx_estado (estado),
    INDEX idx_id_afiliado (id_afiliado),
    INDEX idx_id_profesional (id_profesional),
    INDEX idx_id_centro (id_centro)
) ENGINE=InnoDB;

-- ============================================
-- TABLA DE FACTURAS
-- ============================================
CREATE TABLE facturas (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    id_afiliado INT NOT NULL,
    fecha DATE NOT NULL,
    total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    estado ENUM('PENDIENTE', 'PAGADA') DEFAULT 'PENDIENTE',
    FOREIGN KEY (id_afiliado) REFERENCES afiliados(id_afiliado) ON DELETE CASCADE,
    INDEX idx_estado (estado),
    INDEX idx_id_afiliado (id_afiliado),
    INDEX idx_fecha (fecha)
) ENGINE=InnoDB;

-- ============================================
-- TABLA DE PAGOS
-- ============================================
CREATE TABLE pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_factura INT NOT NULL,
    fecha DATE NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    metodo_pago VARCHAR(50),
    FOREIGN KEY (id_factura) REFERENCES facturas(id_factura) ON DELETE CASCADE,
    INDEX idx_id_factura (id_factura)
) ENGINE=InnoDB;

-- ============================================
-- TABLA DE HISTORIAL CLÍNICO
-- ============================================
CREATE TABLE historial_clinico (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_afiliado INT NOT NULL,
    id_profesional INT NOT NULL,
    fecha DATE NOT NULL,
    diagnostico TEXT,
    tratamiento TEXT,
    FOREIGN KEY (id_afiliado) REFERENCES afiliados(id_afiliado) ON DELETE CASCADE,
    FOREIGN KEY (id_profesional) REFERENCES profesionales(id_profesional) ON DELETE CASCADE,
    INDEX idx_id_afiliado (id_afiliado),
    INDEX idx_id_profesional (id_profesional),
    INDEX idx_fecha (fecha)
) ENGINE=InnoDB;

-- ============================================
-- DATOS INICIALES
-- ============================================

-- Insertar planes de salud
INSERT INTO planes (nombre, descripcion, costo) VALUES
('Plan Basico', 'Cobertura basica de salud - Atencion primaria y emergencias', 50000.00),
('Plan Premium', 'Cobertura completa - Incluye especialistas y procedimientos', 150000.00),
('Plan Empresarial', 'Cobertura para empresas - Servicios integrales', 100000.00);

-- Insertar centros de salud
INSERT INTO centros_salud (nombre, direccion, ciudad) VALUES
('Centro Medico EPS Central', 'Calle 50 #45-30', 'Manizales'),
('Hospital EPS Norte', 'Carrera 20 #30-15', 'Manizales'),
('Centro de Salud EPS Sur', 'Calle 15 #10-25', 'Manizales'),
('Clinica EPS Occidente', 'Carrera 30 #5-40', 'Manizales');

-- El admin se crea via API: POST /api/init
-- Credenciales: admin@eps.com / admin123

-- ============================================
-- CONSULTAS SQL REQUERIDAS POR ROL
-- ============================================

-- 1. CITAS PRÓXIMAS DE UN AFILIADO
-- Muestra las próximas citas de un afiliado específico
DELIMITER //
CREATE PROCEDURE sp_citas_proximas_afiliado(IN p_id_usuario INT)
BEGIN
    SELECT 
        c.id_cita,
        c.fecha,
        c.estado,
        pr.especialidad AS tipo_consulta,
        cs.nombre AS centro_salud,
        cs.direccion AS direccion_centro,
        u_prof.nombre AS profesional
    FROM citas c
    INNER JOIN afiliados a ON c.id_afiliado = a.id_afiliado
    INNER JOIN profesionales pr ON c.id_profesional = pr.id_profesional
    INNER JOIN centros_salud cs ON c.id_centro = cs.id_centro
    INNER JOIN usuarios u_prof ON pr.id_usuario = u_prof.id_usuario
    WHERE a.id_usuario = p_id_usuario
      AND c.fecha >= NOW()
      AND c.estado IN ('PENDIENTE', 'CONFIRMADA')
    ORDER BY c.fecha ASC
    LIMIT 10;
END //
DELIMITER ;

-- 2. DIAGNÓSTICOS FRECUENTES POR ESPECIALIDAD
-- Agrupa diagnósticos por especialidad médica
DELIMITER //
CREATE PROCEDURE sp_diagnosticos_frecuentes()
BEGIN
    SELECT 
        pr.especialidad,
        hc.diagnostico,
        COUNT(*) AS cantidad
    FROM historial_clinico hc
    INNER JOIN profesionales pr ON hc.id_profesional = pr.id_profesional
    GROUP BY pr.especialidad, hc.diagnostico
    ORDER BY cantidad DESC
    LIMIT 20;
END //
DELIMITER ;

-- 3. AFILIADOS CON FACTURAS PENDIENTES
-- Lista afiliados que tienen facturas pendientes de pago
DELIMITER //
CREATE PROCEDURE sp_afiliados_facturas_pendientes()
BEGIN
    SELECT 
        a.id_afiliado,
        u.nombre,
        u.email,
        a.documento,
        COUNT(f.id_factura) AS facturas_pendientes,
        COALESCE(SUM(f.total), 0) AS total_pendiente
    FROM afiliados a
    INNER JOIN usuarios u ON a.id_usuario = u.id_usuario
    INNER JOIN facturas f ON a.id_afiliado = f.id_afiliado
    WHERE f.estado = 'PENDIENTE'
    GROUP BY a.id_afiliado, u.nombre, u.email, a.documento
    HAVING COUNT(f.id_factura) > 0
    ORDER BY total_pendiente DESC;
END //
DELIMITER ;

-- 4. FACTURACIÓN TOTAL POR PLAN DE SALUD
-- Muestra la facturación total agrupada por plan
DELIMITER //
CREATE PROCEDURE sp_facturacion_por_plan()
BEGIN
    SELECT 
        p.nombre AS plan,
        p.costo AS valor_plan,
        COUNT(DISTINCT a.id_afiliado) AS total_afiliados,
        COALESCE(SUM(f.total), 0) AS facturacion_total
    FROM planes p
    LEFT JOIN afiliados a ON p.id_plan = a.id_plan
    LEFT JOIN facturas f ON a.id_afiliado = f.id_afiliado AND f.estado = 'PAGADA'
    GROUP BY p.id_plan, p.nombre, p.costo
    ORDER BY facturacion_total DESC;
END //
DELIMITER ;

-- 5. CENTROS MÁS UTILIZADOS PARA CITAS
-- Lista los centros ordenados por cantidad de citas
DELIMITER //
CREATE PROCEDURE sp_centros_mas_utilizados()
BEGIN
    SELECT 
        cs.id_centro,
        cs.nombre AS centro,
        cs.ciudad,
        COUNT(c.id_cita) AS total_citas
    FROM centros_salud cs
    LEFT JOIN citas c ON cs.id_centro = c.id_centro
    GROUP BY cs.id_centro, cs.nombre, cs.ciudad
    ORDER BY total_citas DESC;
END //
DELIMITER ;

-- ============================================
-- VISTAS PARA CONSULTAS FRECUENTES
-- ============================================

-- Vista de afiliados con información completa
CREATE VIEW v_afiliados_completo AS
SELECT 
    a.id_afiliado,
    a.documento,
    a.fecha_nacimiento,
    a.telefono,
    a.direccion,
    u.nombre,
    u.email,
    u.fecha_creacion,
    p.nombre AS plan,
    p.costo AS valor_plan
FROM afiliados a
INNER JOIN usuarios u ON a.id_usuario = u.id_usuario
LEFT JOIN planes p ON a.id_plan = p.id_plan;

-- Vista de profesionales con centro de salud
CREATE VIEW v_profesionales_centro AS
SELECT 
    pr.id_profesional,
    u.nombre,
    u.email,
    pr.especialidad,
    cs.nombre AS centro,
    cs.ciudad
FROM profesionales pr
INNER JOIN usuarios u ON pr.id_usuario = u.id_usuario
LEFT JOIN centros_salud cs ON pr.id_centro = cs.id_centro;

-- Vista de citas con información relacionada
CREATE VIEW v_citas_detalle AS
SELECT 
    c.id_cita,
    c.fecha,
    c.estado,
    a.documento AS documento_afiliado,
    u_af.nombre AS nombre_afiliado,
    pr.especialidad,
    u_pr.nombre AS nombre_profesional,
    cs.nombre AS centro,
    cs.ciudad
FROM citas c
INNER JOIN afiliados a ON c.id_afiliado = a.id_afiliado
INNER JOIN usuarios u_af ON a.id_usuario = u_af.id_usuario
INNER JOIN profesionales pr ON c.id_profesional = pr.id_profesional
INNER JOIN usuarios u_pr ON pr.id_usuario = u_pr.id_usuario
INNER JOIN centros_salud cs ON c.id_centro = cs.id_centro;

-- Vista de facturas pendientes con datos del afiliado
CREATE VIEW v_facturas_pendientes AS
SELECT 
    f.id_factura,
    f.fecha,
    f.total,
    f.estado,
    a.id_afiliado,
    u.nombre AS nombre_afiliado,
    u.email,
    a.documento
FROM facturas f
INNER JOIN afiliados a ON f.id_afiliado = a.id_afiliado
INNER JOIN usuarios u ON a.id_usuario = u.id_usuario
WHERE f.estado = 'PENDIENTE';

-- Vista de historial clínico detallado
CREATE VIEW v_historial_clinico AS
SELECT 
    hc.id_historial,
    hc.fecha,
    hc.diagnostico,
    hc.tratamiento,
    a.documento AS documento_afiliado,
    u_af.nombre AS nombre_afiliado,
    pr.especialidad,
    u_pr.nombre AS nombre_profesional
FROM historial_clinico hc
INNER JOIN afiliados a ON hc.id_afiliado = a.id_afiliado
INNER JOIN usuarios u_af ON a.id_usuario = u_af.id_usuario
INNER JOIN profesionales pr ON hc.id_profesional = pr.id_profesional
INNER JOIN usuarios u_pr ON pr.id_usuario = u_pr.id_usuario;

-- ============================================
-- TRIGGERS PARA VALIDACIONES
-- ============================================

-- Trigger para validar que la fecha de cita no sea pasado
DELIMITER //
CREATE TRIGGER tr_before_insert_cita
BEFORE INSERT ON citas
FOR EACH ROW
BEGIN
    IF NEW.fecha < NOW() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se pueden agendar citas en fechas pasadas';
    END IF;
END //
DELIMITER ;

-- Nota: La actualizacion de cita a FINALIZADA se maneja en la aplicacion (app.py)

-- ============================================
-- CONSULTAS SQL ADICIONALES
-- ============================================

-- Consulta: Total de citas por estado
-- SELECT estado, COUNT(*) AS total FROM citas GROUP BY estado;

-- Consulta: Ingresos totales por período
-- SELECT MONTH(fecha) AS mes, YEAR(fecha) AS año, SUM(total) AS ingresos 
-- FROM facturas WHERE estado = 'PAGADA' GROUP BY YEAR(fecha), MONTH(fecha);

-- Consulta: Afiliados sin citas en el último año
-- SELECT u.nombre, u.email FROM afiliados a
-- INNER JOIN usuarios u ON a.id_usuario = u.id_usuario
-- WHERE a.id_afiliado NOT IN (
--     SELECT DISTINCT id_afiliado FROM citas WHERE fecha >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
-- );

-- Consulta: Profesionales con más citas atendidas
-- SELECT u.nombre, pr.especialidad, COUNT(c.id_cita) AS total_citas
-- FROM profesionales pr
-- INNER JOIN usuarios u ON pr.id_usuario = u.id_usuario
-- INNER JOIN citas c ON pr.id_profesional = c.id_profesional
-- GROUP BY pr.id_profesional, u.nombre, pr.especialidad
-- ORDER BY total_citas DESC LIMIT 10;

-- ============================================
-- FIN DEL SCRIPT
-- ============================================