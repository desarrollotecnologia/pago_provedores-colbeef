"""Envío de correos de soporte de pago a proveedores."""
from __future__ import annotations

import smtplib
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from email import policy
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_POLICY = policy.SMTP

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.version import APP_VERSION
from app.models import Banco, EnvioCorreo, LotePago, Pago
from app.services.config_service import get_campo_factura, get_smtp_config
from app.services.email_assets import BANNER_CID, get_banner_path
from app.services.email_templates import construir_correo, saludo_por_hora


def _formato_monto_entero(importe: Decimal) -> str:
    entero = int(importe.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return f"{entero:,}".replace(",", ".")


def _formato_monto_exacto(importe: Decimal) -> str:
    texto = f"{importe:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _numero_factura(pago: Pago, campo: str) -> str:
    if pago.numero_factura:
        return pago.numero_factura
    valor = getattr(pago, campo, None) or pago.concepto1 or ""
    return str(valor).replace("fv", "").replace("FV", "").strip()


def _cuerpo_correo(pago: Pago, banco_nombre: str, campo_factura: str) -> tuple[str, str]:
    factura = _numero_factura(pago, campo_factura)
    monto_entero = _formato_monto_entero(Decimal(pago.importe))
    monto_exacto = _formato_monto_exacto(Decimal(pago.importe))
    saludo = saludo_por_hora()

    return construir_correo(
        saludo=saludo,
        factura=factura,
        monto_entero=monto_entero,
        monto_exacto=monto_exacto,
        razon_social=pago.razon_social or "",
        referencia_16=pago.referencia_16 or "",
        referencia_11=pago.referencia_11 or "",
        banco_nombre=banco_nombre,
    )


def _construir_mensaje(smtp_cfg: dict, destinatario: str, asunto: str, texto_plano: str, html: str):
    """Correo HTML (con texto plano de respaldo) y banner inline si existe."""
    banner_path = get_banner_path()
    use_cid = banner_path and not get_settings().email_firma_banner_url

    plain = MIMEText(texto_plano, "plain", "utf-8", policy=SMTP_POLICY)
    html_part = MIMEText(html, "html", "utf-8", policy=SMTP_POLICY)

    if use_cid and banner_path:
        msg = MIMEMultipart("related", policy=SMTP_POLICY)
        alt = MIMEMultipart("alternative", policy=SMTP_POLICY)
        alt.attach(plain)
        alt.attach(html_part)
        msg.attach(alt)
        img = MIMEImage(banner_path.read_bytes(), _subtype="png", policy=SMTP_POLICY)
        img.add_header("Content-ID", f"<{BANNER_CID}>")
        img.add_header("Content-Disposition", "inline", filename="email-banner-colbeef.png")
        msg.attach(img)
    else:
        msg = MIMEMultipart("alternative", policy=SMTP_POLICY)
        msg.attach(plain)
        msg.attach(html_part)

    msg["From"] = f"{smtp_cfg['from_name']} <{smtp_cfg['from_email']}>"
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg["X-Mailer"] = f"PagoProveedores-Colbeef/{APP_VERSION}"

    return msg


def _pago_ya_enviado(pago: Pago) -> bool:
    return pago.estado == "correo_enviado"


def enviar_correo_pago(
    db: Session,
    pago: Pago,
    smtp: dict | None = None,
    *,
    campo_factura: str = "concepto1",
) -> EnvioCorreo | None:
    """Envía correo. Devuelve None si el pago ya tenía correo enviado (no reenvía)."""
    if _pago_ya_enviado(pago):
        return None

    smtp_cfg = smtp or get_smtp_config(db)
    destinatario = (pago.email_destino or "").strip()
    asunto = f"SOPORTE DE PAGO {pago.razon_social}"

    envio = EnvioCorreo(
        pago_id=pago.id,
        destinatario=destinatario or "(sin email)",
        asunto=asunto,
        estado="pendiente",
    )
    db.add(envio)
    db.flush()

    if not destinatario:
        envio.estado = "error"
        envio.mensaje_error = "Proveedor sin correo electrónico"
        return envio

    if not smtp_cfg.get("host"):
        envio.estado = "error"
        envio.mensaje_error = "SMTP no configurado (definir SMTP_HOST en .env)"
        return envio

    banco = db.get(Banco, pago.banco_codigo)
    banco_txt = f"{pago.banco_codigo:04d} - {banco.descripcion}" if banco else str(pago.banco_codigo)

    texto_plano, html = _cuerpo_correo(pago, banco_txt, campo_factura)
    msg = _construir_mensaje(smtp_cfg, destinatario, asunto, texto_plano, html)

    try:
        smtp_class = smtplib.SMTP_SSL if smtp_cfg.get("use_ssl") else smtplib.SMTP
        with smtp_class(smtp_cfg["host"], smtp_cfg["port"], timeout=30) as server:
            if smtp_cfg.get("use_tls") and not smtp_cfg.get("use_ssl"):
                server.starttls()
            if smtp_cfg.get("user"):
                server.login(smtp_cfg["user"], smtp_cfg["password"])
            server.send_message(msg)
        envio.estado = "enviado"
        envio.enviado_en = datetime.now(UTC).replace(tzinfo=None)
        pago.estado = "correo_enviado"
    except Exception as exc:
        envio.estado = "error"
        envio.mensaje_error = str(exc)[:500]
        pago.estado = "correo_error"

    return envio


def lote_correos_ya_enviados(lote: LotePago) -> bool:
    return lote.estado == "correos_enviados"


def pagos_pendientes_correo(lote: LotePago) -> list[Pago]:
    return [
        p
        for p in lote.pagos
        if p.estado not in ("anulado", "correo_enviado")
    ]


def enviar_correos_lote(db: Session, lote: LotePago) -> tuple[int, int, int]:
    """
    Envía correos pendientes del lote.
    Retorna (enviados, errores, omitidos_ya_enviados).
  """
    if lote_correos_ya_enviados(lote):
        raise ValueError("Los correos de este lote ya fueron enviados. No se permiten reenvíos.")

    campo_factura = get_campo_factura(db)
    smtp = get_smtp_config(db)
    enviados = 0
    errores = 0
    omitidos = 0

    pendientes = pagos_pendientes_correo(lote)
    if not pendientes:
        raise ValueError("No hay correos pendientes por enviar en este lote.")

    for pago in lote.pagos:
        if pago.estado == "anulado":
            continue
        if _pago_ya_enviado(pago):
            omitidos += 1
            continue
        if not pago.numero_factura:
            pago.numero_factura = _numero_factura(pago, campo_factura)
        envio = enviar_correo_pago(db, pago, smtp, campo_factura=campo_factura)
        if envio is None:
            omitidos += 1
            continue
        if envio.estado == "enviado":
            enviados += 1
        else:
            errores += 1

    if enviados and errores == 0:
        lote.estado = "correos_enviados"
    elif enviados:
        lote.estado = "completado"
    return enviados, errores, omitidos
