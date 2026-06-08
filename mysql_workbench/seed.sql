-- ============================================
-- SEED DATA - EPS Bienestar
-- MySQL Workbench
-- ============================================

USE eps_salud;

-- ============================================
-- PROCEDIMIENTOS ALMACENADOS
-- ============================================

DROP PROCEDURE IF EXISTS sp_citas_proximas_afiliado;
DROP PROCEDURE IF EXISTS sp_diagnosticos_frecuentes;
DROP PROCEDURE IF EXISTS sp_afiliados_facturas_pendientes;
DROP PROCEDURE IF EXISTS sp_facturacion_por_plan;
DROP PROCEDURE IF EXISTS sp_centros_mas_utilizados;

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
-- TRIGGERS
-- ============================================

DROP TRIGGER IF EXISTS tr_before_insert_cita;

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
-- VISTAS
-- ============================================

DROP VIEW IF EXISTS v_afiliados_completo;
DROP VIEW IF EXISTS v_profesionales_centro;
DROP VIEW IF EXISTS v_citas_detalle;
DROP VIEW IF EXISTS v_facturas_pendientes;
DROP VIEW IF EXISTS v_historial_clinico;

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
-- DATOS DE PRUEBA (Opcional - usar API o frontend)
-- ============================================

-- Para crear usuarios de prueba, usar el API:
-- POST /api/auth/register con rol AFILIADO o PROFESIONAL
-- El password será hasheado correctamente por bcrypt

-- O llamar a POST /api/init después de crear la BD
-- para insertar el admin: admin@eps.com / admin123

-- ============================================
-- FIN DEL SEED
-- ============================================