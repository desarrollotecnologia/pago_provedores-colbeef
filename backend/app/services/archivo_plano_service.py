"""Generación de archivo plano bancario (281 caracteres por línea)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from app.core.config import get_settings
from app.models import Pago

LINE_LENGTH = 281
CUENTA_START_POS = 22


def _tipo_registro(tipo_identificacion: int) -> str:
    return "03" if tipo_identificacion == 3 else "01"


def _campo_identificacion(pago: Pago) -> str:
    id_num = pago.identificacion.strip()
    if pago.tipo_identificacion == 3 and pago.digito_verificacion is not None:
        id_num = id_num + str(pago.digito_verificacion)
    return id_num.zfill(16)[-16:]


def _codigo_ruta(pago: Pago) -> str:
    if pago.cod_oficina and str(pago.cod_oficina).strip():
        return str(pago.cod_oficina).zfill(4)[-4:]
    return str(pago.banco_codigo).zfill(4)[-4:]


def _cuenta_archivo(pago: Pago) -> str:
    cuenta = pago.numero_cuenta.strip()
    if pago.tipo_identificacion == 3 and not cuenta.startswith("1"):
        cuenta = "1" + cuenta
    return cuenta


def _parte_routing(pago: Pago) -> str:
    route_part = f"{pago.forma_pago}{_codigo_ruta(pago)}"
    zeros = CUENTA_START_POS - len(route_part)
    inner = _cuenta_archivo(pago)
    return (route_part + "0" * zeros + inner).ljust(37)[:37]


def build_payment_line(pago: Pago, *, concepto: str, ciudad: str) -> str:
    settings = get_settings()
    parte1 = _tipo_registro(pago.tipo_identificacion) + _campo_identificacion(pago)
    parte2 = _parte_routing(pago)

    centavos = int(round(Decimal(pago.importe) * 100))
    parte3 = ("   " + str(centavos).zfill(15) + "0" * 12)[:30].ljust(30)

    nombre = pago.razon_social.upper()
    n1 = nombre[:36].ljust(36) + ciudad[:4].ljust(4)
    n2 = (ciudad[4:] if len(ciudad) > 4 else "").ljust(40)

    pad = settings.concepto_padding
    concepto_field = (" " * pad + concepto.strip()[:40]).ljust(116)[:116]

    line = parte1 + parte2 + parte3 + n1[:40] + n2[:40] + concepto_field
    return line[:LINE_LENGTH].ljust(LINE_LENGTH)


def generar_archivo_plano(
    pagos: list[Pago],
    *,
    concepto_general: str,
    ciudad: str | None = None,
    nombre_archivo: str | None = None,
) -> tuple[Path, str]:
    settings = get_settings()
    ciudad = ciudad or settings.ciudad_default
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    if not nombre_archivo:
        nombre_archivo = f"PAGOS_{date.today().strftime('%Y%m%d')}.txt"

    ruta = settings.output_dir / nombre_archivo
    lineas = [build_payment_line(p, concepto=concepto_general, ciudad=ciudad) for p in pagos]
    contenido = "\r\n".join(lineas) + ("\r\n" if lineas else "")
    ruta.write_text(contenido, encoding="latin-1")
    return ruta, nombre_archivo
