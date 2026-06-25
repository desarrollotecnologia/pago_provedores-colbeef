"""Valida que los datos del Excel MODELO PAGO PROVEEDORES coincidan con la BD."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import xlrd
from sqlalchemy import select, text

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models import Banco, Proveedor
from app.seeds.import_excel import (
    TIPOS_CUENTA_VALIDOS,
    TIPOS_ID_VALIDOS,
    _clean_text,
    _normalize_digito,
    _to_int,
    _to_str_id,
)

TIPOS_CUENTA_LABEL = {1: "Ahorros", 2: "Corriente"}
TIPOS_ID_LABEL = {1: "CC", 2: "CE", 3: "NIT", 5: "Pasaporte", 9: "Otro"}


@dataclass
class ValidationReport:
    excel_path: str
    excel_rows: int = 0
    db_proveedores: int = 0
    matched: int = 0
    missing_in_db: list[dict] = field(default_factory=list)
    mismatch_in_db: list[dict] = field(default_factory=list)
    extra_in_db: int = 0
    excel_omitidos: list[dict] = field(default_factory=list)
    db_issues: list[dict] = field(default_factory=list)
    bancos_faltantes: set[int] = field(default_factory=set)

    @property
    def ok(self) -> bool:
        return (
            not self.missing_in_db
            and not self.mismatch_in_db
            and not self.excel_omitidos
            and not self.db_issues
        )


def _load_excel_rows(path: Path) -> tuple[list[dict], list[dict], set[int]]:
    wb = xlrd.open_workbook(str(path))
    sh = wb.sheet_by_name("Beneficiarios")
    sh_bancos = wb.sheet_by_name("Bancos")
    bancos_cat = {
        int(sh_bancos.cell_value(r, 0))
        for r in range(2, sh_bancos.nrows)
        if sh_bancos.cell_value(r, 0)
    }

    for row_idx in range(2, sh.nrows):
        codigo = _to_int(sh.cell_value(row_idx, 6))
        if codigo is not None:
            bancos_cat.add(codigo)

    valid_rows: list[dict] = []
    omitidos: list[dict] = []

    for row_idx in range(2, sh.nrows):
        identificacion = _to_str_id(sh.cell_value(row_idx, 1))
        tipo_id = _to_int(sh.cell_value(row_idx, 2))
        digito_v = _normalize_digito(tipo_id, sh.cell_value(row_idx, 3))
        razon_social = _clean_text(sh.cell_value(row_idx, 4)).upper()
        forma_pago = _to_int(sh.cell_value(row_idx, 5)) or 1
        banco = _to_int(sh.cell_value(row_idx, 6))
        tipo_cuenta = _to_int(sh.cell_value(row_idx, 7))
        numero_cuenta = _to_str_id(sh.cell_value(row_idx, 8))
        email = _clean_text(sh.cell_value(row_idx, 9)) or None

        row = {
            "identificacion": identificacion,
            "tipo_identificacion": tipo_id,
            "digito_verificacion": digito_v,
            "razon_social": razon_social,
            "forma_pago": forma_pago,
            "banco_codigo": banco,
            "tipo_cuenta": tipo_cuenta,
            "numero_cuenta": numero_cuenta,
            "email": email.lower() if email else None,
            "excel_row": row_idx + 1,
        }

        if not identificacion or not razon_social:
            omitidos.append({**row, "motivo": "Sin identificación o razón social"})
            continue
        if tipo_id not in TIPOS_ID_VALIDOS:
            omitidos.append({**row, "motivo": f"Tipo identificación inválido ({tipo_id})"})
            continue
        if banco is None:
            omitidos.append({**row, "motivo": "Sin banco"})
            continue
        if banco not in bancos_cat:
            omitidos.append({**row, "motivo": f"Banco {banco} no está en hoja Bancos"})
            continue
        if tipo_cuenta not in TIPOS_CUENTA_VALIDOS:
            omitidos.append({**row, "motivo": f"Tipo cuenta inválido ({tipo_cuenta})"})
            continue
        if not numero_cuenta:
            omitidos.append({**row, "motivo": "Sin número de cuenta"})
            continue
        if tipo_id == 3 and digito_v is None:
            omitidos.append({**row, "motivo": "NIT sin dígito de verificación"})
            continue
        if not numero_cuenta.isdigit():
            omitidos.append({**row, "motivo": f"Cuenta con caracteres no numéricos ({numero_cuenta})"})
            continue

        valid_rows.append(row)

    return valid_rows, omitidos, bancos_cat


def _proveedor_key(identificacion: str, tipo_id: int) -> tuple[str, int]:
    return identificacion.strip(), int(tipo_id)


def validate(excel_path: str | None = None) -> ValidationReport:
    settings = get_settings()
    path = Path(excel_path or settings.excel_path)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el Excel: {path}")

    excel_rows, omitidos, _ = _load_excel_rows(path)
    report = ValidationReport(
        excel_path=str(path),
        excel_rows=len(excel_rows),
        excel_omitidos=omitidos,
    )

    db = SessionLocal()
    try:
        db_proveedores = db.scalars(select(Proveedor).where(Proveedor.activo.is_(True))).all()
        report.db_proveedores = len(db_proveedores)

        db_map = {
            _proveedor_key(p.identificacion, p.tipo_identificacion): p for p in db_proveedores
        }
        excel_keys = set()

        compare_fields = [
            "razon_social",
            "digito_verificacion",
            "forma_pago",
            "banco_codigo",
            "tipo_cuenta",
            "numero_cuenta",
            "email",
        ]

        for row in excel_rows:
            key = _proveedor_key(row["identificacion"], row["tipo_identificacion"])
            excel_keys.add(key)
            prov = db_map.get(key)
            if not prov:
                report.missing_in_db.append(row)
                continue

            diffs: dict[str, tuple] = {}
            for fld in compare_fields:
                excel_val = row[fld]
                db_val = getattr(prov, fld)
                if fld == "email":
                    db_val = (db_val or "").lower() or None
                if excel_val != db_val:
                    diffs[fld] = (excel_val, db_val)

            if diffs:
                report.mismatch_in_db.append(
                    {
                        "identificacion": row["identificacion"],
                        "tipo_identificacion": row["tipo_identificacion"],
                        "razon_social": row["razon_social"],
                        "excel_row": row["excel_row"],
                        "diffs": diffs,
                    }
                )
            else:
                report.matched += 1

        report.extra_in_db = sum(1 for k in db_map if k not in excel_keys)

        bancos_db = {b.codigo for b in db.scalars(select(Banco)).all()}
        for row in excel_rows:
            if row["banco_codigo"] not in bancos_db:
                report.bancos_faltantes.add(row["banco_codigo"])

        for prov in db_proveedores:
            issues: list[str] = []
            if prov.tipo_identificacion == 3 and prov.digito_verificacion is None:
                issues.append("NIT sin dígito de verificación")
            if prov.tipo_identificacion != 3 and prov.digito_verificacion != 0:
                issues.append("Dígito de verificación debe ser 0 (solo aplica a NIT)")
            if prov.banco_codigo not in bancos_db:
                issues.append(f"Banco {prov.banco_codigo} no existe en catálogo")
            if not prov.numero_cuenta.isdigit():
                issues.append(f"Cuenta no numérica ({prov.numero_cuenta})")
            if prov.tipo_identificacion not in TIPOS_ID_VALIDOS:
                issues.append("Tipo identificación inválido")
            if prov.tipo_cuenta not in TIPOS_CUENTA_VALIDOS:
                issues.append("Tipo cuenta inválido")
            if issues:
                report.db_issues.append(
                    {
                        "id": prov.id,
                        "identificacion": prov.identificacion,
                        "razon_social": prov.razon_social,
                        "issues": issues,
                    }
                )
    finally:
        db.close()

    return report


def print_report(report: ValidationReport) -> None:
    print("=== Validación Excel vs Base de Datos ===")
    print(f"Excel: {report.excel_path}")
    print(f"Filas válidas en Excel (Beneficiarios): {report.excel_rows}")
    print(f"Proveedores activos en BD:              {report.db_proveedores}")
    print(f"Coinciden exactamente:                  {report.matched}")
    print(f"Solo en BD (no en Excel):               {report.extra_in_db}")
    print(f"Faltan en BD:                           {len(report.missing_in_db)}")
    print(f"Diferencias de datos:                   {len(report.mismatch_in_db)}")
    print(f"Filas omitidas del Excel:               {len(report.excel_omitidos)}")
    print(f"Proveedores con problemas en BD:        {len(report.db_issues)}")
    print()

    if report.excel_omitidos:
        print("--- Filas del Excel que no se pueden importar ---")
        for item in report.excel_omitidos[:20]:
            print(
                f"  Fila {item['excel_row']}: {item.get('razon_social') or '?'} — {item['motivo']}"
            )
        if len(report.excel_omitidos) > 20:
            print(f"  ... y {len(report.excel_omitidos) - 20} más")
        print()

    if report.missing_in_db:
        print("--- En Excel pero no en BD ---")
        for item in report.missing_in_db[:15]:
            print(
                f"  Fila {item['excel_row']}: {item['razon_social']} "
                f"({TIPOS_ID_LABEL.get(item['tipo_identificacion'], '?')} {item['identificacion']})"
            )
        if len(report.missing_in_db) > 15:
            print(f"  ... y {len(report.missing_in_db) - 15} más")
        print()

    if report.mismatch_in_db:
        print("--- Diferencias Excel vs BD ---")
        for item in report.mismatch_in_db[:15]:
            print(
                f"  Fila {item['excel_row']}: {item['razon_social']} "
                f"({item['identificacion']})"
            )
            for fld, (excel_val, db_val) in item["diffs"].items():
                print(f"    {fld}: Excel={excel_val!r}  BD={db_val!r}")
        if len(report.mismatch_in_db) > 15:
            print(f"  ... y {len(report.mismatch_in_db) - 15} más")
        print()

    if report.db_issues:
        print("--- Proveedores en BD con datos inconsistentes ---")
        for item in report.db_issues[:15]:
            print(f"  #{item['id']} {item['razon_social']}: {', '.join(item['issues'])}")
        if len(report.db_issues) > 15:
            print(f"  ... y {len(report.db_issues) - 15} más")
        print()

    if report.bancos_faltantes:
        print(f"--- Bancos usados pero no en catálogo BD: {sorted(report.bancos_faltantes)} ---")
        print()

    if report.ok:
        print("RESULTADO: OK — Excel y BD están alineados.")
    else:
        print("RESULTADO: HAY DIFERENCIAS — ejecute importación o corrija datos.")
        print("  Sugerencia: scripts\\setup.bat  o  python -m app.seeds.import_excel")


def main() -> None:
    excel_arg = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        report = validate(excel_arg)
    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
    print_report(report)
    sys.exit(0 if report.ok else 2)


if __name__ == "__main__":
    main()
