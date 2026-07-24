"""Generación de archivo plano BBVA (macro Planocash del Excel modelo)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_DOWN
from pathlib import Path

from app.core.config import get_settings
from app.core.nit import TIPOS_IDENTIFICACION_NIT, normalizar_numero_nit
from app.models import Pago

# Código BBVA en el catálogo del Excel modelo
BANCO_BBVA = 13

IDENTIFICACION_ARCHIVO_LENGTH = 15
REFERENCIA_CORREO_LENGTH = 16
CUENTA_ACH_LENGTH = 17
IMPORTE_LENGTH = 15
NOMBRE_LENGTH = 36
DIRECCION_LENGTH = 36
EMAIL_LENGTH = 48
CONCEPTO_LENGTH = 40
CIUDAD_DEFAULT_PLANO = "BOGOTA"


def _digitos_identificacion(valor: str) -> str:
    digitos = "".join(c for c in valor.strip() if c.isdigit())
    return digitos.lstrip("0") or "0"


def _pad_left_zeros(valor: str, length: int) -> str:
    return valor.zfill(length)[-length:]


def _pad_right_spaces(valor: str, length: int) -> str:
    return (valor or "")[:length].ljust(length)


def _tipo_registro(tipo_identificacion: int) -> str:
    """Tipo Id con formato Excel '00'."""
    return f"{int(tipo_identificacion):02d}"


def _campo_identificacion_archivo(pago: Pago) -> str:
    """15 dígitos de identificación (formato Excel '000000000000000'), sin DV."""
    if pago.tipo_identificacion in TIPOS_IDENTIFICACION_NIT:
        id_num = normalizar_numero_nit(pago.identificacion)
    else:
        id_num = _digitos_identificacion(pago.identificacion)
    return _pad_left_zeros(id_num, IDENTIFICACION_ARCHIVO_LENGTH)


def _digito_verificacion_plano(pago: Pago) -> str:
    """1 carácter, como .Text General del Excel."""
    if pago.digito_verificacion is None:
        return "0"
    return str(int(pago.digito_verificacion))


def _forma_pago_plano(pago: Pago) -> str:
    """1 carácter (formato General del Excel: '1', no '01')."""
    return str(int(pago.forma_pago))


def _tipo_cuenta_plano(pago: Pago) -> str:
    """Tipo cuenta como .Text en hoja Pagos (sin cero a la izquierda)."""
    return str(int(pago.tipo_cuenta))


def _importe_plano(importe: Decimal) -> str:
    """Entero + 2 decimales, sin punto, relleno a 15 con ceros a la izquierda."""
    cuantia = Decimal(importe).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    entero = int(cuantia)
    decimales = f"{int((cuantia - entero) * 100):02d}"
    return _pad_left_zeros(f"{entero}{decimales}", IMPORTE_LENGTH)


def _fechas_y_oficina(pago: Pago) -> tuple[str, str, str, str]:
    """Para abono en cuenta (forma 1): 0000/00/00 y oficina 0000."""
    forma = int(pago.forma_pago)
    if forma == 1:
        return "0000", "00", "00", "0000"
    if forma == 3:
        oficina = "9999"
    else:
        oficina = (
            str(pago.cod_oficina).zfill(4)[-4:]
            if pago.cod_oficina and str(pago.cod_oficina).strip()
            else "0000"
        )
    if pago.fecha_limite:
        return (
            f"{pago.fecha_limite.year:04d}",
            f"{pago.fecha_limite.month:02d}",
            f"{pago.fecha_limite.day:02d}",
            oficina,
        )
    return "0000", "00", "00", oficina


def _bloques_cuenta(pago: Pago) -> tuple[str, str, str, str]:
    """Replica Hallardatoscuenta del Excel (ACH vs BBVA 0013).

    Returns:
        banco (4), cuentabbva (16), tipocuentanacha, cuentanacha (17)
    """
    forma = int(pago.forma_pago)
    banco = int(pago.banco_codigo)
    cuenta = "".join(c for c in str(pago.numero_cuenta).strip() if c.isdigit())

    if forma != 1:
        return "0013", "0000000000000000", "00", "0" * CUENTA_ACH_LENGTH

    banco_txt = f"{banco:04d}"
    if banco == BANCO_BBVA:
        oficinabbva = f"0{(cuenta[:3] if cuenta else '000').zfill(3)[-3:]}"
        tipocuentabbva = f"{int(pago.tipo_cuenta)}00"
        cuentabbva = f"{oficinabbva}00{tipocuentabbva}{cuenta[-6:].zfill(6)}"
        cuentabbva = (cuentabbva + "0" * 16)[:16]
        return banco_txt, cuentabbva, "00", "0" * CUENTA_ACH_LENGTH

    return (
        banco_txt,
        "0" * 16,
        _tipo_cuenta_plano(pago),
        _pad_right_spaces(cuenta, CUENTA_ACH_LENGTH),
    )

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
    return pago.identificacion.strip()


def _campo_identificacion(pago: Pago) -> str:
    return _campo_identificacion_referencia(pago)


def concepto_linea_pago(pago: Pago) -> str:
    return (pago.concepto1 or "").strip()[:CONCEPTO_LENGTH]


def _concepto_campo(valor: str | None) -> str:
    texto = (valor or "").strip()
    if not texto:
        return ""
    return _pad_right_spaces(texto, CONCEPTO_LENGTH)


def build_payment_line(pago: Pago, *, concepto: str | None = None, ciudad: str) -> str:
    """Construye una línea con la estructura exacta de la macro Planocash."""
    ciudad_txt = (ciudad or CIUDAD_DEFAULT_PLANO).upper().strip() or CIUDAD_DEFAULT_PLANO
    direccion1 = _pad_right_spaces(ciudad_txt, DIRECCION_LENGTH)
    direccion2 = " " * DIRECCION_LENGTH

    banco_txt, cuentabbva, tipocuentanacha, cuentanacha = _bloques_cuenta(pago)

    anio, mes, dia, oficina = _fechas_y_oficina(pago)
    nombre = _pad_right_spaces((pago.razon_social or "").upper(), NOMBRE_LENGTH)
    email = _pad_right_spaces((pago.email_destino or "").strip(), EMAIL_LENGTH)

    concepto1 = _concepto_campo(concepto if concepto is not None else pago.concepto1)
    concepto2 = _concepto_campo(pago.concepto2)
    concepto3 = _concepto_campo(pago.concepto3)
    concepto4 = _concepto_campo(pago.concepto4)

    return (
        _tipo_registro(pago.tipo_identificacion)
        + _campo_identificacion_archivo(pago)
        + _digito_verificacion_plano(pago)
        + _forma_pago_plano(pago)
        + banco_txt
        + cuentabbva
        + tipocuentanacha
        + cuentanacha
        + _importe_plano(Decimal(pago.importe))
        + anio
        + mes
        + dia
        + oficina
        + nombre
        + direccion1
        + direccion2
        + email
        + concepto1
        + concepto2
        + concepto3
        + concepto4
    )


def generar_archivo_plano(
    pagos: list[Pago],
    *,
    ciudad: str | None = None,
    nombre_archivo: str | None = None,
) -> tuple[Path, str]:
    settings = get_settings()
    ciudad = ciudad or settings.ciudad_default or CIUDAD_DEFAULT_PLANO
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    if not nombre_archivo:
        nombre_archivo = f"PAGOS_{date.today().strftime('%Y%m%d')}.txt"

    ruta = settings.output_dir / nombre_archivo
    lineas = [build_payment_line(p, ciudad=ciudad) for p in pagos]
    # VBA Print # escribe CRLF al final de cada línea
    contenido = "\r\n".join(lineas) + ("\r\n" if lineas else "")
    ruta.write_text(contenido, encoding="latin-1", errors="replace")
    return ruta, nombre_archivo
