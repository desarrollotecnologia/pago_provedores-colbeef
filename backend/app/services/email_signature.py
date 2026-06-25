"""Firma HTML Colbeef — réplica del diseño oficial (contacto + banner)."""
from __future__ import annotations

from html import escape

from app.core.config import get_settings
from app.services.email_assets import BANNER_CID, banner_public_url, get_banner_path

# Colores oficiales Colbeef (firma)
GREEN = "#2e933c"
GREEN_DARK = "#1a6b42"
RED = "#d32f2f"
GREY = "#555555"
GREY_LIGHT = "#f5f5f5"


def _banner_img_src() -> str | None:
    s = get_settings()
    if s.email_firma_banner_url:
        return s.email_firma_banner_url
    if get_banner_path():
        return f"cid:{BANNER_CID}"
    return banner_public_url()


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


def _icono_social(href: str, letra: str, size: str = "14px") -> str:
    return (
        f'<a href="{href}" style="display:inline-block;width:30px;height:30px;'
        f"background:{GREEN};color:#ffffff;text-align:center;line-height:30px;"
        f'border-radius:7px;text-decoration:none;font-weight:bold;font-size:{size};'
        f'font-family:Arial,Helvetica,sans-serif;margin-right:5px;">{letra}</a>'
    )


def _fila_contacto(icono: str, contenido: str) -> str:
    return f"""
    <tr>
      <td style="padding:0 8px 7px 0;vertical-align:top;width:22px;font-size:14px;color:{GREEN};">{icono}</td>
      <td style="padding:0 0 7px;font-size:12px;color:{GREY};font-family:Arial,Helvetica,sans-serif;line-height:1.45;">{contenido}</td>
    </tr>"""


def _servicio_columna(emoji: str, etiqueta: str, color: str) -> str:
    return f"""
    <td align="center" style="padding:0 4px;vertical-align:top;width:72px;">
      <div style="font-size:22px;line-height:1;margin-bottom:4px;">{emoji}</div>
      <div style="font-size:9px;font-weight:bold;color:{color};font-family:Arial,Helvetica,sans-serif;
        text-decoration:underline;letter-spacing:0.3px;">{etiqueta}</div>
    </td>"""


def _banner_html_fallback() -> str:
    """Banner Colbeef en HTML cuando no hay imagen PNG instalada."""
    web = escape(get_settings().email_firma_web)
    direccion = (
        "Vía Corredor / Río Frío Calle 210 # 9-631 Floridablanca / Santander"
    )
    servicios = "".join(
        [
            _servicio_columna("🐄", "GANADO", GREEN),
            _servicio_columna("🐮", "BENEFICIO", GREEN),
            _servicio_columna("🥩", "DESPOSTE", RED),
            _servicio_columna("🍖", "PORCIONADO", RED),
            _servicio_columna("🥓", "CARNES", RED),
        ]
    )
    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
      style="margin-top:14px;border:1px solid #e2e2e2;border-radius:10px;overflow:hidden;
      box-shadow:0 2px 10px rgba(0,0,0,0.07);max-width:580px;">
      <tr>
        <td style="padding:18px 16px 14px;background:linear-gradient(180deg,#ffffff 0%,{GREY_LIGHT} 100%);">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="vertical-align:middle;width:150px;">
                <span style="font-size:30px;font-weight:bold;font-family:Arial,Helvetica,sans-serif;
                  color:{GREEN};letter-spacing:-0.5px;">Col</span><span style="font-size:30px;
                  font-weight:bold;font-family:Arial,Helvetica,sans-serif;color:{RED};">beef</span><sup
                  style="color:{RED};font-size:9px;font-weight:bold;">®</sup>
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
        <td style="background:{GREEN};padding:11px 14px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="font-size:9px;color:#ffffff;font-family:Arial,Helvetica,sans-serif;
                font-weight:bold;letter-spacing:0.4px;vertical-align:middle;">
                UNIDOS PARA GENERAR CONFIANZA Y CALIDAD
              </td>
              <td align="center" style="vertical-align:middle;padding:0 8px;">
                <span style="display:inline-block;border:1px solid #ffffff;border-radius:20px;
                  padding:3px 12px;font-size:9px;color:#ffffff;font-family:Arial,Helvetica,sans-serif;">
                  {web}
                </span>
              </td>
              <td align="right" style="font-size:8px;color:#ffffff;font-family:Arial,Helvetica,sans-serif;
                vertical-align:middle;line-height:1.3;">
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
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:14px;">
      <tr>
        <td>
          <img src="{escape(src)}" alt="Colbeef — Unidos para generar confianza y calidad"
            width="580" style="display:block;max-width:100%;height:auto;border:0;border-radius:10px;" />
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
    tel_href = telefono.replace(" ", "").replace("+", "")

    redes = (
        _icono_social("https://www.facebook.com/colbeef", "f")
        + _icono_social("https://www.linkedin.com/company/colbeef", "in", "11px")
        + _icono_social("https://x.com/colbeef", "X", "12px")
        + _icono_social("https://www.instagram.com/colbeef", "●", "16px")
    )

    contacto = (
        _fila_contacto(
            "☎",
            f'<a href="tel:+{tel_href}" style="color:{GREY};text-decoration:underline;">{telefono}</a>',
        )
        + _fila_contacto(
            "✉",
            f'<a href="mailto:{email}" style="color:{GREY};text-decoration:underline;">{email}</a>',
        )
        + _fila_contacto("📍", direccion)
        + _fila_contacto(
            "🔗",
            f'<a href="https://{web_href}" style="color:{GREEN};text-decoration:underline;">{web}</a>',
        )
    )

    return f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
  style="max-width:580px;margin-top:20px;font-family:Arial,Helvetica,sans-serif;">
  <tr>
    <td style="border-top:3px solid {GREEN};padding-top:18px;">
      <p style="margin:0 0 3px;font-size:17px;font-weight:bold;color:{GREEN};line-height:1.25;">{nombre}</p>
      <p style="margin:0 0 14px;font-size:13px;color:#666666;line-height:1.4;">
        {cargo} | <strong style="color:{GREEN};font-weight:bold;">{empresa}</strong>
      </p>
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:12px;">
        {contacto}
      </table>
      <p style="margin:0 0 0;line-height:1;">{redes}</p>
    </td>
  </tr>
  <tr>
    <td>{_bloque_banner()}</td>
  </tr>
</table>"""
