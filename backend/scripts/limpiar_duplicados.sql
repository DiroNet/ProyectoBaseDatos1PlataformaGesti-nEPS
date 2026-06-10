-- Limpiar duplicados y agregar constraints únicas
-- Ejecutar en MySQL Workbench

-- Eliminar afiliados duplicados (mantener el más reciente por id)
DELETE a1 FROM afiliados a1
JOIN afiliados a2 
WHERE a1.id_afiliado > a2.id_afiliado 
AND a1.documento = a2.documento;

DELETE a1 FROM afiliados a1
JOIN afiliados a2 
WHERE a1.id_afiliado > a2.id_afiliado 
AND a1.telefono = a2.telefono 
AND a1.telefono IS NOT NULL 
AND a2.telefono IS NOT NULL;

-- Agregar unique constraints si no existen
-- Para documento
ALTER TABLE afiliados ADD CONSTRAINT IF NOT EXISTS unique_documento UNIQUE (documento);

-- Para telefono  
ALTER TABLE afiliados ADD CONSTRAINT IF NOT EXISTS unique_telefono UNIQUE (telefono);

-- Verificar duplicados restantes
SELECT documento, COUNT(*) as count FROM afiliados 
WHERE documento IS NOT NULL AND documento != '' 
GROUP BY documento 
HAVING count > 1;

SELECT telefono, COUNT(*) as count FROM afiliados 
WHERE telefono IS NOT NULL AND telefono != '' 
GROUP BY telefono 
HAVING count > 1;