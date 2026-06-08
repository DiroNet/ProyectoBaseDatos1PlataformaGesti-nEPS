-- Script para corregir caracteres corruptos en la base de datos
-- Ejecutar en MySQL: mysql -u root -p eps_salud < fix_encoding.sql

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Corregir planes
UPDATE planes SET nombre = 'Plan Basico', descripcion = 'Cobertura basica de salud - Atencion primaria y emergencias' WHERE nombre LIKE '%B%ico%';
UPDATE planes SET nombre = 'Plan Premium', descripcion = 'Cobertura completa - Incluye especialistas y procedimientos' WHERE nombre LIKE '%Premium%';
UPDATE planes SET nombre = 'Plan Empresarial', descripcion = 'Cobertura para empresas - Servicios integrales' WHERE nombre LIKE '%Empresarial%';

-- Corregir centros
UPDATE centros_salud SET nombre = 'Centro Medico EPS Central' WHERE nombre LIKE '%Centro M%ico%';
UPDATE centros_salud SET nombre = 'Clinica EPS Occidente' WHERE nombre LIKE '%Cl%nica%';