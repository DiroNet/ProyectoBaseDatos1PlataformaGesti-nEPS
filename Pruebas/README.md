# Pruebas - Sistema EPS

Este directorio contiene los scripts de pruebas para el sistema EPS.

## Archivos

- **PruebasUnitarias.py** - Pruebas unitarias del sistema
- **PruebasIntegracion.py** - Pruebas de integracion del sistema

## Ejecucion

### Pruebas Unitarias

```bash
python PruebasUnitarias.py
```

### Pruebas de Integracion

```bash
python PruebasIntegracion.py
```

## Descripcion

### Pruebas Unitarias

Contiene 36 pruebas organizadas en 8 categorias:

| Categoria | Pruebas |
|-----------|---------|
| Validaciones Usuario | UT-01 a UT-07 |
| Validaciones Afiliado | UT-08 a UT-11 |
| Validaciones Profesional | UT-12 a UT-15 |
| Validaciones Cita | UT-16 a UT-20 |
| Validaciones Factura | UT-21 a UT-24 |
| Validaciones Horario | UT-25 a UT-29 |
| Validaciones Plan | UT-30 a UT-32 |
| Logica Negocio | UT-33 a UT-36 |

### Pruebas de Integracion

Contiene 17 pruebas organizadas en:

| Prueba | Descripcion |
|--------|-------------|
| PI-01 | Conexion a base de datos |
| PI-02 a PI-11 | Modelos (Usuario, Afiliado, Profesional, Plan, etc.) |
| PI-12 a PI-15 | Reportes SQL |
| PI-16 | Relaciones entre tablas |
| PI-17 | Estadisticas dashboard |

## Requisitos

- Python 3.x
- Flask y dependencias del backend instaladas

## Nota

Las pruebas de integracion acceden a la base de datos real pero no la modifican. Solo realizan operaciones de lectura (SELECT).