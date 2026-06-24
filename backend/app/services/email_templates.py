"""Plantillas de correo — cuerpo y firma Colbeef (HTML + texto plano)."""
from __future__ import annotations

from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

from app.core.config import get_settings
from app.services.email_assets import BANNER_CID, banner_public_url, get_banner_path

TZ_COLOMBIA = ZoneInfo("America/Bogota")
GREEN = "#1a6b42"
RED = "#c62828"
from app.version import EMAIL_TEMPLATE_VERSION


def saludo_por_hora(fecha: datetime | None = None) -> str:
    """Buenos días / Buenas tardes / Buenas noches según hora en Colombia."""
    now = fecha or datetime.now(TZ_COLOMBIA)
    if now.tzinfo is None:
        now = now.replace(tzinfo=TZ_COLOMBIA)
    else:
        now = now.astimezone(TZ_COLOMBIA)
    hora = now.hour
    if 5 <= hora < 12:
        return "Buenos días"
    if 12 <= hora < 19:
        return "Buenas tardes"
    return "Buenas noches"


def _banner_img_src() -> str | None:
    s = get_settings()
    if s.email_firma_banner_url:
        return s.email_firma_banner_url
    if get_banner_path():
        return f"cid:{BANNER_CID}"
    return banner_public_url()


def _firma_texto() -> str:
    s = get_settings()
    linea = "═" * 42
    return f"""
{linea}
{s.email_firma_nombre}
{s.email_firma_cargo} | {s.email_firma_empresa}
Tel: {s.email_firma_telefono}
Email: {s.email_firma_email}
{s.email_firma_direccion}
Web: {s.email_firma_web}
{linea}"""


def _firma_html() -> str:
    s = get_settings()
    nombre = escape(s.email_firma_nombre)
    cargo = escape(s.email_firma_cargo)
    empresa = escape(s.email_firma_empresa)
    telefono = escape(s.email_firma_telefono)
    email = escape(s.email_firma_email)
    direccion = escape(s.email_firma_direccion)
    web = escape(s.email_firma_web)
    web_href = web.replace("https://", "").replace("http://", "")

    banner_src = _banner_img_src()
    banner_row = ""
    if banner_src:
        banner_row = f"""
            <tr>
              <td style="padding:14px 0 0;">
                <img src="{escape(banner_src)}" alt="Colbeef" width="560"
                  style="display:block;max-width:100%;height:auto;border:0;border-radius:6px;" />
              </td>
            </tr>"""

    return f"""
            <tr>
              <td style="padding:20px 0 0;border-top:3px solid {GREEN};">
                <p style="margin:0 0 2px;font-size:16px;font-weight:bold;color:{GREEN};font-family:Arial,sans-serif;">{nombre}</p>
                <p style="margin:0 0 14px;font-size:13px;color:#444;font-family:Arial,sans-serif;">
                  {cargo} | <strong style="color:{GREEN};">{empresa}</strong>
                </p>
                <table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,sans-serif;font-size:12px;color:#555;">
                  <tr>
                    <td style="padding:0 10px 6px 0;color:{GREEN};font-weight:bold;vertical-align:top;">Tel</td>
                    <td style="padding:0 0 6px;"><a href="tel:{telefono.replace(' ', '')}" style="color:#333;">{telefono}</a></td>
                  </tr>
                  <tr>
                    <td style="padding:0 10px 6px 0;color:{GREEN};font-weight:bold;vertical-align:top;">Email</td>
                    <td style="padding:0 0 6px;"><a href="mailto:{email}" style="color:#333;">{email}</a></td>
                  </tr>
                  <tr>
                    <td style="padding:0 10px 6px 0;color:{GREEN};font-weight:bold;vertical-align:top;">Dir</td>
                    <td style="padding:0 0 6px;">{direccion}</td>
                  </tr>
                  <tr>
                    <td style="padding:0 10px 0 0;color:{GREEN};font-weight:bold;vertical-align:top;">Web</td>
                    <td><a href="https://{web_href}" style="color:{GREEN};">{web}</a></td>
                  </tr>
                </table>
              </td>
            </tr>
            {banner_row}
            <tr>
              <td style="padding:14px 0 0;background:{GREEN};color:#fff;font-size:11px;text-align:center;border-radius:6px;font-family:Arial,sans-serif;">
                UNIDOS PARA GENERAR CONFIANZA Y CALIDAD &nbsp;|&nbsp; {web}
              </td>
            </tr>"""


def construir_correo(
    *,
    saludo: str,
    factura: str,
    monto_entero: str,
    monto_exacto: str,
    razon_social: str,
    referencia_16: str,
    referencia_11: str,
    banco_nombre: str,
) -> tuple[str, str]:
    """Devuelve (texto_plano, html)."""
    fila = (
        f"{razon_social}\t{referencia_16}\t{referencia_11}\t"
        f"{banco_nombre}\tAbono/Cargo cuenta\t{monto_exacto}"
    )

    texto = f"""{saludo}

envio soporte de pago fv {factura}
valor consignado ${monto_entero}
mil gracias

{fila}
{_firma_texto()}"""

    celdas = [
        ("Proveedor", escape(razon_social)),
        ("Cuenta", escape(referencia_16)),
        ("Ref.", escape(referencia_11)),
        ("Banco", escape(banco_nombre)),
        ("Concepto", "Abono/Cargo cuenta"),
        ("Valor", escape(monto_exacto)),
    ]
    header_cells = "".join(
        f'<td style="padding:8px 10px;background:{GREEN};color:#fff;font-size:11px;'
        f'font-weight:bold;border:1px solid {GREEN};font-family:Arial,sans-serif;">{h}</td>'
        for h, _ in celdas
    )
    data_cells = "".join(
        f'<td style="padding:8px 10px;border:1px solid #d4e5db;font-size:12px;'
        f'font-family:Arial,sans-serif;">{v}</td>'
        for _, v in celdas
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Soporte de pago</title>
</head>
<body style="margin:0;padding:0;background:#eef4f0;font-family:Arial,Helvetica,sans-serif;">
<!-- pago-proveedores-email v{EMAIL_TEMPLATE_VERSION} -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#eef4f0;">
  <tr>
    <td align="center" style="padding:24px 12px;">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"
        style="max-width:600px;width:100%;background:#ffffff;border-radius:10px;overflow:hidden;
        border:1px solid #d4e5db;">
        <tr>
          <td style="background:{GREEN};padding:14px 20px;">
            <span style="color:#fff;font-size:18px;font-weight:bold;font-family:Arial,sans-serif;">
              Col<span style="color:{RED};">beef</span>
            </span>
            <span style="color:rgba(255,255,255,0.85);font-size:12px;display:block;margin-top:2px;">
              Soporte de pago a proveedores
            </span>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 24px 8px;font-size:14px;color:#222;line-height:1.6;">
            <p style="margin:0 0 12px;">{escape(saludo)}</p>
            <p style="margin:0 0 16px;">
              envio soporte de pago fv <strong>{escape(factura)}</strong><br>
              valor consignado <strong>${escape(monto_entero)}</strong><br>
              mil gracias
            </p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
              style="border-collapse:collapse;margin-bottom:8px;">
              <tr>{header_cells}</tr>
              <tr>{data_cells}</tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:0 24px 24px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
              {_firma_html()}
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>"""

    return texto, html
