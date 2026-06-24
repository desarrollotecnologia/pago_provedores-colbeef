"""Plantillas de correo — cuerpo y firma Colbeef (HTML + texto plano)."""
from __future__ import annotations

from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

from app.core.config import get_settings
from app.services.email_assets import BANNER_CID, banner_public_url, get_banner_path

TZ_COLOMBIA = ZoneInfo("America/Bogota")
GREEN = "#1a6b42"


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
    """cid: para adjunto inline, o URL pública si está configurada."""
    s = get_settings()
    if s.email_firma_banner_url:
        return s.email_firma_banner_url
    if get_banner_path():
        return f"cid:{BANNER_CID}"
    return banner_public_url()


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
    banner_block = ""
    footer_block = ""
    if banner_src:
        banner_block = f"""
  <tr><td style="padding-top:16px;">
    <img src="{escape(banner_src)}" alt="Colbeef" width="560" style="max-width:100%;height:auto;display:block;border-radius:8px;" />
  </td></tr>"""
    else:
        footer_block = f"""
  <tr><td style="padding-top:12px;background:{GREEN};color:#fff;font-size:11px;text-align:center;border-radius:0 0 8px 8px;padding:10px;">
    UNIDOS PARA GENERAR CONFIANZA Y CALIDAD &nbsp;|&nbsp; {web}
  </td></tr>"""

    return f"""
<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333;max-width:580px;margin-top:24px;">
  <tr><td style="padding-top:12px;border-top:2px solid {GREEN};">
    <p style="margin:0 0 4px;font-size:15px;font-weight:bold;color:{GREEN};">{nombre}</p>
    <p style="margin:0 0 12px;font-size:13px;color:#444;">
      {cargo} | <strong style="color:{GREEN};">{empresa}</strong>
    </p>
    <p style="margin:0 0 6px;font-size:12px;color:#555;">
      <span style="color:{GREEN};font-weight:bold;">&#9742;</span>
      <a href="tel:{telefono.replace(' ', '')}" style="color:#333;text-decoration:underline;">{telefono}</a>
    </p>
    <p style="margin:0 0 6px;font-size:12px;color:#555;">
      <span style="color:{GREEN};font-weight:bold;">&#9993;</span>
      <a href="mailto:{email}" style="color:#333;text-decoration:underline;">{email}</a>
    </p>
    <p style="margin:0 0 6px;font-size:12px;color:#555;">
      <span style="color:{GREEN};font-weight:bold;">&#128205;</span> {direccion}
    </p>
    <p style="margin:0 0 12px;font-size:12px;color:#555;">
      <span style="color:{GREEN};font-weight:bold;">&#127760;</span>
      <a href="https://{web_href}" style="color:{GREEN};text-decoration:underline;">{web}</a>
    </p>
    <p style="margin:0 0 8px;">
      <a href="https://www.facebook.com/colbeef" style="display:inline-block;background:{GREEN};color:#fff;width:28px;height:28px;line-height:28px;text-align:center;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;margin-right:6px;">f</a>
      <a href="https://www.linkedin.com/company/colbeef" style="display:inline-block;background:{GREEN};color:#fff;width:28px;height:28px;line-height:28px;text-align:center;border-radius:6px;text-decoration:none;font-weight:bold;font-size:11px;margin-right:6px;">in</a>
      <a href="https://x.com/colbeef" style="display:inline-block;background:{GREEN};color:#fff;width:28px;height:28px;line-height:28px;text-align:center;border-radius:6px;text-decoration:none;font-weight:bold;font-size:12px;margin-right:6px;">X</a>
      <a href="https://www.instagram.com/colbeef" style="display:inline-block;background:{GREEN};color:#fff;width:28px;height:28px;line-height:28px;text-align:center;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;">&#9679;</a>
    </p>
  </td></tr>
  {banner_block}
  {footer_block}
</table>"""


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
    fila = f"{razon_social}\t{referencia_16}\t{referencia_11}\t{banco_nombre}\tAbono/Cargo cuenta\t{monto_exacto}"

    texto = f"""{saludo}

envio soporte de pago fv {factura}
valor consignado ${monto_entero}
mil gracias

{fila}
"""

    fila_html = escape(fila).replace("\t", "&nbsp;&nbsp;")

    html = f"""<!DOCTYPE html>
<html><body style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222;margin:0;padding:16px;">
<p style="margin:0 0 12px;">{escape(saludo)}</p>
<p style="margin:0 0 12px;line-height:1.6;">
envio soporte de pago fv {escape(factura)}<br>
valor consignado ${escape(monto_entero)}<br>
mil gracias
</p>
<p style="margin:0 0 8px;font-size:13px;white-space:pre-wrap;">{fila_html}</p>
{_firma_html()}
</body></html>"""

    return texto, html
