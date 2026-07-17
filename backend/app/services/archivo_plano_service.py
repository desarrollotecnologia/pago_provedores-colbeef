"""Generación de archivo plano bancario (281+ caracteres por línea)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from app.core.config import get_settings
from app.core.nit import TIPOS_IDENTIFICACION_NIT, normalizar_numero_nit
from app.models import Pago

LINE_LENGTH_BASE = 281
CUENTA_START_POS = 22
CONCEPTO_PADDING_BASE = 76


LINE_LENGTH_BASE = 281
CUENTA_START_POS = 22
CONCEPTO_PADDING_BASE = 76
# Plan B / archivo bancario: tipo (2) + identificación (15) = 17 caracteres antes de forma de pago.
IDENTIFICACION_ARCHIVO_LENGTH = 15
REFERENCIA_CORREO_LENGTH = 16


def _digitos_identificacion(valor: str) -> str:
    """Solo dígitos, sin ceros a la izquierda (evita doble relleno desde Excel)."""
    digitos = "".join(c for c in valor.strip() if c.isdigit())
    return digitos.lstrip("0") or "0"


def _tipo_registro(tipo_identificacion: int) -> str:
    """Código de tipo de identificación del banco, en 2 dígitos (01-09)."""
    return f"{int(tipo_identificacion):02d}"


def _campo_identificacion_archivo(pago: Pago) -> str:
    """15 dígitos de identificación — sin dígito de verificación (formato banco Plan B)."""
    if pago.tipo_identificacion in TIPOS_IDENTIFICACION_NIT:
        id_num = normalizar_numero_nit(pago.identificacion)
    else:
        id_num = _digitos_identificacion(pago.identificacion)
    return id_num.zfill(IDENTIFICACION_ARCHIVO_LENGTH)[-IDENTIFICACION_ARCHIVO_LENGTH:]


def _campo_identificacion_referencia(pago: Pago) -> str:
    """16 dígitos para referencia en correos — NIT incluye dígito de verificación."""
    if pago.tipo_identificacion in TIPOS_IDENTIFICACION_NIT:
        id_num = normalizar_numero_nit(pago.identificacion)
    else:
        id_num = _digitos_identificacion(pago.identificacion)
    if (
        pago.tipo_identificacion in TIPOS_IDENTIFICACION_NIT
        and pago.digito_verificacion is not None
    ):
        id_num = id_num + str(pago.digito_verificacion)
    return id_num.zfill(REFERENCIA_CORREO_LENGTH)[-REFERENCIA_CORREO_LENGTH:]


def identificacion_correo(pago: Pago) -> str:
    """NIT/identificación legible en correos (sin ceros a la izquierda)."""
    return pago.identificacion.strip()


def _campo_identificacion(pago: Pago) -> str:
    """Alias usado en referencias de correo."""
    return _campo_identificacion_referencia(pago)


def _ruta_pago(pago: Pago) -> str:
    """Forma de pago + banco/oficina (5 o 9 caracteres)."""
    if pago.cod_oficina and str(pago.cod_oficina).strip():
        return (
            f"{pago.forma_pago}"
            f"{int(pago.banco_codigo):04d}"
            f"{str(pago.cod_oficina).zfill(4)[-4:]}"
        )
    return f"{pago.forma_pago}{int(pago.banco_codigo):04d}"


def _parte_importe(ruta: str, cuenta: str, centavos: int) -> tuple[str, str]:
    cuenta = cuenta.strip()
    if len(ruta) == 9:
        combined = ruta + cuenta
        parte2 = combined[:37]
        overflow = combined[37:]
        if overflow:
            parte3 = (overflow + str(centavos)).ljust(30, "0")[:30]
        else:
            if len(str(centavos)) <= 7:
                body = "0" * 9 + str(centavos // 100).zfill(6)
            else:
                body = "0" * 8 + str(centavos)
            parte3 = body.ljust(30, "0")[:30]
        return parte2, parte3

    combined = ruta + "0" * (CUENTA_START_POS - len(ruta)) + cuenta
    parte2 = combined[:37].ljust(37)[:37]
    overflow = combined[37:]
    if overflow.strip():
        parte3 = (overflow[:2] + " " + str(centavos).zfill(15)).ljust(30, "0")[:30]
    else:
        parte3 = ("   " + str(centavos).zfill(15) + "0" * 12)[:30].ljust(30)
    return parte2, parte3


def _nombre_ciudad(pago: Pago, ciudad: str) -> tuple[str, str]:
    nombre = pago.razon_social.upper()
    ciudad = ciudad.upper()
    if len(nombre) > 36:
        bloque = (nombre + ciudad)[:80].ljust(80)
        return bloque[:40], bloque[40:80]
    n1 = nombre[:36].ljust(36) + ciudad[:4].ljust(4)
    n2 = (ciudad[4:] if len(ciudad) > 4 else "").ljust(40)
    return n1[:40], n2[:40]


def concepto_linea_pago(pago: Pago) -> str:
    """Concepto que va al banco en cada línea del archivo plano (por pago, no del lote)."""
    return (pago.concepto1 or "").strip()[:40]


def build_payment_line(pago: Pago, *, concepto: str | None = None, ciudad: str) -> str:
    nombre_len = len(pago.razon_social.upper())
    extra = max(0, nombre_len - 36)
    line_length = LINE_LENGTH_BASE + extra
    concepto_len = 116 + extra
    concepto_pad = CONCEPTO_PADDING_BASE + extra

    parte1 = _tipo_registro(pago.tipo_identificacion) + _campo_identificacion_archivo(pago)
    centavos = int(round(Decimal(pago.importe) * 100))
    parte2, parte3 = _parte_importe(_ruta_pago(pago), pago.numero_cuenta, centavos)
    n1, n2 = _nombre_ciudad(pago, ciudad)
    concepto_field = (
        " " * concepto_pad + (concepto or concepto_linea_pago(pago)).strip()[:40]
    ).ljust(concepto_len)[:concepto_len]

    line = parte1 + parte2 + parte3 + n1 + n2 + concepto_field
    return line[:line_length].ljust(line_length)


def generar_archivo_plano(
    pagos: list[Pago],
    *,
    ciudad: str | None = None,
    nombre_archivo: str | None = None,
) -> tuple[Path, str]:
    settings = get_settings()
    ciudad = ciudad or settings.ciudad_default
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    if not nombre_archivo:
        nombre_archivo = f"PAGOS_{date.today().strftime('%Y%m%d')}.txt"

    ruta = settings.output_dir / nombre_archivo
    lineas = [build_payment_line(p, ciudad=ciudad) for p in pagos]
    contenido = "\r\n".join(lineas) + ("\r\n" if lineas else "")
    ruta.write_text(contenido, encoding="latin-1")
    return ruta, nombre_archivo
