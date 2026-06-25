"""Firma HTML Colbeef — réplica del diseño oficial (contacto + banner)."""
from __future__ import annotations

import base64
from html import escape

from app.core.config import get_settings
from app.services.email_assets import BANNER_CID, banner_public_url, get_banner_path

# Colores oficiales Colbeef (firma corporativa)
GREEN = "#2e933c"
GREEN_DARK = "#1a6b42"
RED = "#d32f2f"
GREY = "#555555"
GREY_MUTED = "#666666"

SIGNATURE_WIDTH = 580


def _banner_img_src() -> str | None:
    s = get_settings()
    if s.email_firma_banner_url:
        return s.email_firma_banner_url
    if get_banner_path():
        return f"cid:{BANNER_CID}"
    return banner_public_url()


def _svg_icon_data_uri(svg_body: str) -> str:
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" '
        f'viewBox="0 0 24 24" fill="none" stroke="{GREEN}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{svg_body}</svg>'
    )
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _icon_img(svg_body: str, alt: str) -> str:
    src = _svg_icon_data_uri(svg_body)
    return (
        f'<img src="{src}" alt="{escape(alt)}" width="18" height="18" '
        f'style="display:block;border:0;outline:none;" />'
    )


def firma_texto() -> str:
    s = get_settings()
    sep = "─" * 44
    return f"""
{sep}
{s.email_firma_nombre}
{s.email_firma_cargo} | {s.email_firma_empresa}
Tel: {s.email_firma_telefono}
Email: {s.email_firma_email}
{s.email_firma_direccion}
Web: {s.email_firma_web}
{sep}"""


def _icono_social(href: str, label: str, font_size: str = "14px") -> str:
    return (
        f'<a href="{href}" target="_blank" rel="noopener noreferrer" '
        f'style="display:inline-block;width:32px;height:32px;background:{GREEN};'
        f"color:#ffffff;text-align:center;line-height:32px;border-radius:8px;"
        f'text-decoration:none;font-weight:bold;font-size:{font_size};'
        f'font-family:Arial,Helvetica,sans-serif;margin-right:6px;">{label}</a>'
    )


def _fila_contacto(icon_svg: str, icon_alt: str, contenido: str) -> str:
    return f"""
    <tr>
      <td style="padding:0 10px 8px 0;vertical-align:top;width:20px;line-height:0;">
        {_icon_img(icon_svg, icon_alt)}
      </td>
      <td style="padding:0 0 8px;font-size:12px;color:{GREY};font-family:Arial,Helvetica,sans-serif;line-height:1.5;">
        {contenido}
      </td>
    </tr>"""


def _banner_html_fallback() -> str:
    """Banner Colbeef en HTML cuando no hay imagen PNG instalada."""
    web = escape(get_settings().email_firma_web)
    direccion = "Vía Corredor / Río Frío Calle 210 # 9-631 Floridablanca / Santander"

    def servicio(emoji: str, etiqueta: str, color: str) -> str:
        return f"""
        <td align="center" style="padding:0 3px;vertical-align:top;">
          <div style="font-size:20px;line-height:1;margin-bottom:3px;">{emoji}</div>
          <div style="font-size:8px;font-weight:bold;color:{color};font-family:Arial,Helvetica,sans-serif;
            text-decoration:underline;letter-spacing:0.2px;white-space:nowrap;">{etiqueta}</div>
        </td>"""

    servicios = "".join(
        [
            servicio("🐄", "GANADO", GREEN),
            servicio("🐮", "BENEFICIO", GREEN),
            servicio("🥩", "DESPOSTE", RED),
            servicio("🍖", "PORCIONADO", RED),
            servicio("🥓", "CARNES", RED),
        ]
    )

    return f"""
    <table role="presentation" width="{SIGNATURE_WIDTH}" cellpadding="0" cellspacing="0" border="0"
      style="margin-top:16px;border:1px solid #e0e0e0;border-radius:12px 12px 0 0;overflow:hidden;
      box-shadow:0 2px 8px rgba(0,0,0,0.08);max-width:100%;">
      <tr>
        <td style="padding:16px 14px 12px;background:#ffffff;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="vertical-align:middle;width:140px;">
                <span style="font-size:28px;font-weight:bold;font-family:Arial,Helvetica,sans-serif;
                  color:{GREEN};letter-spacing:-0.5px;">Col</span><span style="font-size:28px;
                  font-weight:bold;font-family:Arial,Helvetica,sans-serif;color:{RED};">beef</span><sup
                  style="color:{RED};font-size:8px;font-weight:bold;vertical-align:super;">®</sup>
              </td>
              <td style="vertical-align:middle;">
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="right">
                  <tr>{servicios}</tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
      </tr>
      <tr>
        <td style="background:{GREEN};padding:10px 12px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="font-size:8px;color:#ffffff;font-family:Arial,Helvetica,sans-serif;
                font-weight:bold;letter-spacing:0.3px;vertical-align:middle;white-space:nowrap;">
                UNIDOS PARA GENERAR CONFIANZA Y CALIDAD
              </td>
              <td align="center" style="vertical-align:middle;padding:0 6px;white-space:nowrap;">
                <span style="display:inline-block;border:1px solid #ffffff;border-radius:20px;
                  padding:3px 10px;font-size:8px;color:#ffffff;font-family:Arial,Helvetica,sans-serif;">
                  {web}
                </span>
              </td>
              <td align="right" style="font-size:7px;color:#ffffff;font-family:Arial,Helvetica,sans-serif;
                vertical-align:middle;line-height:1.25;">
                📍 {direccion}
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>"""


def _bloque_banner() -> str:
    src = _banner_img_src()
    if src:
        return f"""
    <table role="presentation" width="{SIGNATURE_WIDTH}" cellpadding="0" cellspacing="0" border="0"
      style="margin-top:16px;max-width:100%;">
      <tr>
        <td style="line-height:0;font-size:0;">
          <img src="{escape(src)}" alt="Colbeef — Unidos para generar confianza y calidad"
            width="{SIGNATURE_WIDTH}" style="display:block;max-width:100%;height:auto;border:0;
            border-radius:12px 12px 0 0;" />
        </td>
      </tr>
    </table>"""
    return _banner_html_fallback()


def firma_html() -> str:
    s = get_settings()
    nombre = escape(s.email_firma_nombre)
    cargo = escape(s.email_firma_cargo)
    empresa = escape(s.email_firma_empresa)
    telefono = escape(s.email_firma_telefono)
    email = escape(s.email_firma_email)
    direccion = escape(s.email_firma_direccion)
    web = escape(s.email_firma_web)
    web_href = web.replace("https://", "").replace("http://", "")
    tel_href = telefono.replace(" ", "")

    icon_phone = (
        '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 '
        '19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 '
        '12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 '
        '2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>'
    )
    icon_mail = (
        '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>'
        '<polyline points="22,6 12,13 2,6"/>'
    )
    icon_pin = (
        '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>'
        '<circle cx="12" cy="10" r="3"/>'
    )
    icon_globe = (
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="2" y1="12" x2="22" y2="12"/>'
        '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>'
    )

    redes = (
        _icono_social("https://www.facebook.com/colbeef", "f")
        + _icono_social("https://www.linkedin.com/company/colbeef", "in", "11px")
        + _icono_social("https://x.com/colbeef", "𝕏", "13px")
        + _icono_social("https://www.instagram.com/colbeef", "◎", "15px")
    )

    contacto = (
        _fila_contacto(
            icon_phone,
            "Teléfono",
            f'<a href="tel:{tel_href}" style="color:{GREY};text-decoration:underline;">{telefono}</a>',
        )
        + _fila_contacto(
            icon_mail,
            "Email",
            f'<a href="mailto:{email}" style="color:{GREY};text-decoration:underline;">{email}</a>',
        )
        + _fila_contacto(icon_pin, "Dirección", direccion)
        + _fila_contacto(
            icon_globe,
            "Web",
            f'<a href="https://{web_href}" style="color:{GREY};text-decoration:underline;">{web}</a>',
        )
    )

    return f"""
<table role="presentation" width="{SIGNATURE_WIDTH}" cellpadding="0" cellspacing="0" border="0"
  style="max-width:100%;margin-top:8px;font-family:Arial,Helvetica,sans-serif;">
  <tr>
    <td style="padding:0;">
      <p style="margin:0 0 2px;font-size:17px;font-weight:bold;color:{GREEN};line-height:1.3;">{nombre}</p>
      <p style="margin:0 0 12px;font-size:13px;color:{GREY_MUTED};line-height:1.4;">
        {cargo} | <strong style="color:{GREEN};font-weight:bold;">{empresa}</strong>
      </p>
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:10px;">
        {contacto}
      </table>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:10px;">
        <tr>
          <td style="border-top:2px solid {GREEN};font-size:0;line-height:0;height:2px;">&nbsp;</td>
        </tr>
      </table>
      <p style="margin:0 0 0;line-height:1;">{redes}</p>
    </td>
  </tr>
  <tr>
    <td>{_bloque_banner()}</td>
  </tr>
</table>"""
