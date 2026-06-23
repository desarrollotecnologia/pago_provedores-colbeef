"""Importa catálogos y proveedores desde el Excel operativo."""
from __future__ import annotations

from pathlib import Path

import xlrd
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert as mysql_insert

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models import Banco, CuentaOrdenante, OficinaBanco, Proveedor, TipoCuenta, TipoIdentificacion

BATCH_SIZE = 500
TIPOS_ID_VALIDOS = {1, 2, 3, 5, 9}
TIPOS_CUENTA_VALIDOS = {1, 2}


def _to_int(value) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        return int(float(value))
    return int(value)


def _to_str_id(value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return str(value).rstrip("0").rstrip(".")
    return str(value).strip()


def _clean_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _get_workbook(path: Path) -> xlrd.Book:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo Excel: {path}")
    return xlrd.open_workbook(str(path))


def import_from_excel(excel_path: str | None = None) -> dict:
    settings = get_settings()
    path = Path(excel_path or settings.excel_path)
    wb = _get_workbook(path)

    stats = {"bancos": 0, "oficinas": 0, "cuentas": 0, "proveedores": 0, "omitidos": 0}

    db = SessionLocal()
    try:
        stats["bancos"] = _import_bancos(db, wb)
        stats["oficinas"] = _import_oficinas(db, wb)
        stats["cuentas"] = _import_cuentas(db, wb)
        imported, omitted = _import_proveedores(db, wb)
        stats["proveedores"] = imported
        stats["omitidos"] = omitted
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return stats


def _import_bancos(db, wb: xlrd.Book) -> int:
    sh = wb.sheet_by_name("Bancos")
    count = 0
    for row_idx in range(2, sh.nrows):
        codigo = _to_int(sh.cell_value(row_idx, 0))
        descripcion = _clean_text(sh.cell_value(row_idx, 1))
        if codigo is None or not descripcion:
            continue

        stmt = mysql_insert(Banco).values(
            codigo=codigo, descripcion=descripcion, activo=True
        )
        stmt = stmt.on_duplicate_key_update(
            descripcion=stmt.inserted.descripcion, activo=True
        )
        db.execute(stmt)
        count += 1

    db.flush()
    return count


def _import_oficinas(db, wb: xlrd.Book) -> int:
    sh = wb.sheet_by_name("Oficinas")
    batch: list[dict] = []
    count = 0

    for row_idx in range(2, sh.nrows):
        codigo = _clean_text(sh.cell_value(row_idx, 0))
        nombre = _clean_text(sh.cell_value(row_idx, 1))
        if not codigo or not nombre:
            continue

        if isinstance(sh.cell_value(row_idx, 0), float):
            codigo = str(int(sh.cell_value(row_idx, 0)))

        batch.append({"codigo": codigo, "nombre": nombre})
        if len(batch) >= BATCH_SIZE:
            count += _flush_oficinas(db, batch)
            batch.clear()

    if batch:
        count += _flush_oficinas(db, batch)

    db.flush()
    return count


def _flush_oficinas(db, batch: list[dict]) -> int:
    for item in batch:
        stmt = mysql_insert(OficinaBanco).values(**item)
        stmt = stmt.on_duplicate_key_update(nombre=stmt.inserted.nombre)
        db.execute(stmt)
    return len(batch)


def _import_cuentas(db, wb: xlrd.Book) -> int:
    sh = wb.sheet_by_name("Cuentas Ordenantes")
    count = 0
    for row_idx in range(2, sh.nrows):
        alias = _clean_text(sh.cell_value(row_idx, 0))
        if not alias:
            continue

        exists = db.scalar(
            select(CuentaOrdenante).where(CuentaOrdenante.alias == alias)
        )
        if exists:
            continue

        db.add(
            CuentaOrdenante(
                numero_cuenta=alias,
                alias=alias,
                activa=True,
            )
        )
        count += 1

    db.flush()
    return count


def _import_proveedores(db, wb: xlrd.Book) -> tuple[int, int]:
    sh = wb.sheet_by_name("Beneficiarios")

    tipos_id = {t.codigo for t in db.scalars(select(TipoIdentificacion)).all()}
    tipos_cta = {t.codigo for t in db.scalars(select(TipoCuenta)).all()}
    bancos = {b.codigo for b in db.scalars(select(Banco)).all()}

    imported = 0
    omitted = 0

    for row_idx in range(2, sh.nrows):
        identificacion = _to_str_id(sh.cell_value(row_idx, 1))
        tipo_id = _to_int(sh.cell_value(row_idx, 2))
        digito_v = _to_int(sh.cell_value(row_idx, 3))
        razon_social = _clean_text(sh.cell_value(row_idx, 4))
        forma_pago = _to_int(sh.cell_value(row_idx, 5)) or 1
        banco = _to_int(sh.cell_value(row_idx, 6))
        tipo_cuenta = _to_int(sh.cell_value(row_idx, 7))
        numero_cuenta = _to_str_id(sh.cell_value(row_idx, 8))
        email = _clean_text(sh.cell_value(row_idx, 9)) or None

        if not identificacion or not razon_social:
            omitted += 1
            continue

        if tipo_id not in tipos_id or tipo_id not in TIPOS_ID_VALIDOS:
            omitted += 1
            continue

        if banco not in bancos:
            omitted += 1
            continue

        if tipo_cuenta not in tipos_cta or tipo_cuenta not in TIPOS_CUENTA_VALIDOS:
            omitted += 1
            continue

        if not numero_cuenta:
            omitted += 1
            continue

        digito_v = digito_v if digito_v is not None else None

        stmt = mysql_insert(Proveedor).values(
            identificacion=identificacion,
            tipo_identificacion=tipo_id,
            digito_verificacion=digito_v,
            razon_social=razon_social,
            forma_pago=forma_pago,
            banco_codigo=banco,
            tipo_cuenta=tipo_cuenta,
            numero_cuenta=numero_cuenta,
            email=email,
            activo=True,
        )
        stmt = stmt.on_duplicate_key_update(
            digito_verificacion=stmt.inserted.digito_verificacion,
            razon_social=stmt.inserted.razon_social,
            forma_pago=stmt.inserted.forma_pago,
            banco_codigo=stmt.inserted.banco_codigo,
            tipo_cuenta=stmt.inserted.tipo_cuenta,
            numero_cuenta=stmt.inserted.numero_cuenta,
            email=stmt.inserted.email,
            activo=True,
        )
        db.execute(stmt)
        imported += 1

    db.flush()
    return imported, omitted
