"""Crea la base de datos y todas las tablas."""
from urllib.parse import urlparse

import pymysql
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import Base, engine
from app.models import (  # noqa: F401 - registra modelos
    Banco,
    Configuracion,
    CuentaOrdenante,
    EnvioCorreo,
    EventoUsabilidad,
    LotePago,
    OficinaBanco,
    Pago,
    Proveedor,
    TipoCuenta,
    TipoIdentificacion,
    Usuario,
)


def _parse_db_url(url: str) -> dict:
    parsed = urlparse(url.replace("mysql+pymysql://", "mysql://"))
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 3306,
        "user": parsed.username or "root",
        "password": parsed.password or "",
        "database": (parsed.path or "/pago_proveedores").lstrip("/").split("?")[0],
    }


def create_database_if_not_exists() -> None:
    settings = get_settings()
    db_info = _parse_db_url(settings.database_url)
    db_name = db_info.pop("database")

    conn = pymysql.connect(**db_info, charset="utf8mb4")
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        print(f"  Base de datos '{db_name}' lista.")
    finally:
        conn.close()


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    _apply_schema_patches()
    print("  Tablas creadas/verificadas.")


def _apply_schema_patches() -> None:
    """Añade columnas nuevas en instalaciones existentes."""
    with engine.connect() as conn:
        if not conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'proveedores'
                  AND COLUMN_NAME = 'cod_oficina'
                """
            )
        ).scalar():
            conn.execute(
                text("ALTER TABLE proveedores ADD COLUMN cod_oficina VARCHAR(10) NULL")
            )
            conn.commit()
        conn.execute(
            text(
                """
                UPDATE proveedores
                SET digito_verificacion = 0
                WHERE tipo_identificacion != 3
                  AND (digito_verificacion IS NULL OR digito_verificacion != 0)
                """
            )
        )
        conn.commit()

        if not conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'eventos_usabilidad'
                """
            )
        ).scalar():
            EventoUsabilidad.__table__.create(bind=conn)
            conn.commit()
            print("  Tabla eventos_usabilidad creada.")


def create_resumen_view() -> None:
    with engine.connect() as conn:
        conn.execute(text("DROP VIEW IF EXISTS vw_resumen_lotes"))
        conn.execute(
            text(
                """
                CREATE VIEW vw_resumen_lotes AS
                SELECT
                    l.id,
                    l.fecha_operacion,
                    l.estado,
                    l.importe_total,
                    l.cantidad_pagos,
                    u.nombre_completo AS operador
                FROM lotes_pago l
                JOIN usuarios u ON u.id = l.usuario_id
                """
            )
        )
        conn.commit()
    print("  Vista vw_resumen_lotes creada.")
