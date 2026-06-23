-- ============================================================
-- SISTEMA PAGO PROVEEDORES - COLBEEF
-- MySQL 8.x | Charset: utf8mb4
-- ============================================================

CREATE DATABASE IF NOT EXISTS pago_proveedores
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE pago_proveedores;

-- Catálogos base (las tablas se crean vía SQLAlchemy; este script
-- sirve para crear la BD manualmente si se prefiere)

-- Tipos de identificación
CREATE TABLE IF NOT EXISTS tipos_identificacion (
    codigo      TINYINT      NOT NULL PRIMARY KEY,
    descripcion VARCHAR(50)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO tipos_identificacion (codigo, descripcion) VALUES
    (1, 'Cédula de Ciudadanía'),
    (2, 'Cédula de Extranjería'),
    (3, 'NIT'),
    (5, 'Pasaporte'),
    (9, 'Otro');

-- Tipos de cuenta
CREATE TABLE IF NOT EXISTS tipos_cuenta (
    codigo      TINYINT      NOT NULL PRIMARY KEY,
    descripcion VARCHAR(30)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO tipos_cuenta (codigo, descripcion) VALUES
    (1, 'Ahorros'),
    (2, 'Corriente');

-- Vista resumen (se crea después de las tablas principales vía seed)
