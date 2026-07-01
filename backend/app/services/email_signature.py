"""Firma HTML Colbeef — réplica del diseño oficial (contacto + banner)."""
from __future__ import annotations

from html import escape

from app.core.config import get_settings
from app.services.email_assets import (
    BANNER_CID,
    ICON_EMAIL,
    ICON_FACEBOOK,
    ICON_INSTAGRAM,
    ICON_LINKEDIN,
    ICON_LOCATION,
    ICON_PHONE,
    ICON_WEB,
    ICON_X,
    LOGO_CID,
    EmailIcon,
    banner_public_url,
    get_banner_path,
    get_icon_path,
    get_logo_path,
)

# Colores oficiales Colbeef (firma corporativa)
GREEN = "#2e933c"
GREEN_DARK = "#1a6b42"
RED = "#d32f2f"
GREY = "#555555"
GREY_MUTED = "#666666"

SIGNATURE_WIDTH = 580
LOGO_HEADER_WIDTH = 148


def logo_header_html() -> str:
    """Logotipo Colbeef para el encabezado del correo (imagen CID o wordmark HTML)."""
    logo = get_logo_path()
    if logo:
        return f"""<table role="presentation" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td style="background:#ffffff;border-radius:6px;padding:5px 12px;">
      <img src="cid:{LOGO_CID}" width="{LOGO_HEADER_WIDTH}" alt="Colbeef"
        style="display:block;border:0;max-width:{LOGO_HEADER_WIDTH}px;height:auto;" />
    </td>
  </tr>
</table>"""
    return f"""<span style="font-size:24px;font-weight:800;font-family:Arial,Helvetica,sans-serif;
      letter-spacing:-0.3px;line-height:1.2;display:inline-block;background:#ffffff;
      border-radius:6px;padding:5px 12px;">
      <span style="color:{GREEN};">Col</span><span style="color:{RED};">beef</span><sup style="color:{RED};font-size:10px;">®</sup>
    </span>"""

SOCIAL_LINKS: tuple[tuple[EmailIcon, str, str], ...] = (
    (ICON_FACEBOOK, "https://www.facebook.com/colbeefoficial", "Facebook Colbeef"),
    (ICON_LINKEDIN, "https://www.linkedin.com/company/colbeefoficial", "LinkedIn Colbeef"),
    (ICON_X, "https://x.com/colbeefoficial", "X Colbeef"),
    (ICON_INSTAGRAM, "https://www.instagram.com/colbeefoficial", "Instagram Colbeef"),
)


def _banner_img_src() -> str | None:
    s = get_settings()
    if s.email_firma_banner_url:
        return s.email_firma_banner_url
    if get_banner_path():
        return f"cid:{BANNER_CID}"
    return banner_public_url()


def _cid_img(icon: EmailIcon, alt: str, width: int, height: int) -> str:
    if get_icon_path(icon):
        return (
            f'<img src="cid:{icon.cid}" alt="{escape(alt)}" width="{width}" height="{height}" '
            f'style="display:block;border:0;outline:none;" />'
        )
    return (
        f'<span style="display:inline-block;width:{width}px;height:{height}px;'
        f"background:{GREEN};border-radius:6px;color:#fff;font-size:{max(10, width // 3)}px;"
        f'line-height:{height}px;text-align:center;font-family:Arial,sans-serif;">•</span>'
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


def _icono_social(icon: EmailIcon, href: str, alt: str) -> str:
    img = _cid_img(icon, alt, 32, 32)
    return (
        f'<a href="{href}" target="_blank" rel="noopener noreferrer" '
        f'style="display:inline-block;margin-right:6px;text-decoration:none;line-height:0;">'
        f"{img}</a>"
    )


def _fila_contacto(icon: EmailIcon, icon_alt: str, contenido: str) -> str:
    return f"""
    <tr>
      <td style="padding:0 10px 8px 0;vertical-align:middle;width:22px;line-height:0;">
        {_cid_img(icon, icon_alt, 18, 18)}
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

    redes = "".join(_icono_social(icon, href, alt) for icon, href, alt in SOCIAL_LINKS)

    contacto = (
        _fila_contacto(
            ICON_PHONE,
            "Teléfono",
            f'<a href="tel:{tel_href}" style="color:{GREY};text-decoration:underline;">{telefono}</a>',
        )
        + _fila_contacto(
            ICON_EMAIL,
            "Email",
            f'<a href="mailto:{email}" style="color:{GREY};text-decoration:underline;">{email}</a>',
        )
        + _fila_contacto(ICON_LOCATION, "Dirección", direccion)
        + _fila_contacto(
            ICON_WEB,
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
