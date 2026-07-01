"""Plantillas de correo — cuerpo y firma Colbeef (HTML + texto plano)."""
from __future__ import annotations

from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

from app.services.email_signature import (
    GREEN_DARK,
    firma_html,
    firma_texto,
    logo_header_html,
)
from app.version import EMAIL_TEMPLATE_VERSION

TZ_COLOMBIA = ZoneInfo("America/Bogota")


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


def construir_correo(
    *,
    saludo: str,
    factura: str,
    monto_entero: str,
    monto_exacto: str,
    razon_social: str,
    identificacion: str,
    numero_cuenta: str,
    banco_nombre: str,
    banco_codigo: str,
    concepto: str,
) -> tuple[str, str]:
    """Devuelve (texto_plano, html)."""
    concepto_txt = concepto.strip() or "Abono/Cargo cuenta"
    concepto_html = escape(concepto_txt)
    banco_corto = banco_codigo.zfill(4)[-4:]
    fila = (
        f"{razon_social}\t{identificacion}\t{numero_cuenta}\t"
        f"{concepto_txt}\t{banco_corto}\t{monto_exacto}"
    )

    texto = f"""{saludo}

envio soporte de pago fv {factura}
valor consignado ${monto_entero}
mil gracias

{fila}
{firma_texto()}"""

    celdas = [
        ("Proveedor", escape(razon_social)),
        ("Identificación", escape(identificacion)),
        ("Cuenta", escape(numero_cuenta)),
        ("Concepto", concepto_html),
        ("Banco", escape(banco_nombre)),
        ("Valor", escape(monto_exacto)),
    ]
    header_cells = "".join(
        f'<td style="padding:8px 10px;background:{GREEN_DARK};color:#fff;font-size:11px;'
        f'font-weight:bold;border:1px solid {GREEN_DARK};font-family:Arial,sans-serif;">{h}</td>'
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
          <td style="background:{GREEN_DARK};padding:14px 20px;">
            {logo_header_html()}
            <span style="color:rgba(255,255,255,0.85);font-size:12px;display:block;margin-top:6px;">
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
          <td style="padding:0 20px 24px;">
            {firma_html()}
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>"""

    return texto, html
