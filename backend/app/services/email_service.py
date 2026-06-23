"""Envío de correos de soporte de pago a proveedores."""
from __future__ import annotations

import smtplib
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy.orm import Session

from app.models import Banco, EnvioCorreo, LotePago, Pago
from app.services.config_service import get_campo_factura, get_smtp_config


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


def _cuerpo_correo(pago: Pago, banco_nombre: str) -> str:
    factura = _numero_factura(pago, "concepto1")
    monto_entero = _formato_monto_entero(Decimal(pago.importe))
    monto_exacto = _formato_monto_exacto(Decimal(pago.importe))

    texto = f"""Buenas tardes

envio soporte de pago fv {factura}
valor consignado ${monto_entero}
mil gracias

{pago.razon_social}\t{pago.referencia_16 or ''}\t{pago.referencia_11 or ''}\t{banco_nombre}\tAbono/Cargo cuenta\t{monto_exacto}
"""
    return texto


def enviar_correo_pago(db: Session, pago: Pago, smtp: dict | None = None) -> EnvioCorreo:
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

    msg = MIMEMultipart()
    msg["From"] = f"{smtp_cfg['from_name']} <{smtp_cfg['from_email']}>"
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(_cuerpo_correo(pago, banco_txt), "plain", "utf-8"))

    try:
        with smtplib.SMTP(smtp_cfg["host"], smtp_cfg["port"], timeout=30) as server:
            if smtp_cfg.get("use_tls"):
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


def enviar_correos_lote(db: Session, lote: LotePago) -> tuple[int, int]:
    campo_factura = get_campo_factura(db)
    smtp = get_smtp_config(db)
    enviados = 0
    errores = 0

    for pago in lote.pagos:
        if pago.estado == "anulado":
            continue
        if not pago.numero_factura:
            pago.numero_factura = _numero_factura(pago, campo_factura)
        envio = enviar_correo_pago(db, pago, smtp)
        if envio.estado == "enviado":
            enviados += 1
        else:
            errores += 1

    if enviados and errores == 0:
        lote.estado = "correos_enviados"
    elif enviados:
        lote.estado = "completado"
    return enviados, errores
