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
    from app.core.facturas import split_facturas

    concepto_txt = concepto.strip() or "Abono/Cargo cuenta"
    concepto_html = escape(concepto_txt)
    banco_corto = banco_codigo.zfill(4)[-4:]
    facturas = split_facturas(factura)
    factura_txt = factura.strip()
    etiqueta_fv = "facturas" if len(facturas) > 1 else "factura"
    fila = (
        f"{razon_social}\t{identificacion}\t{numero_cuenta}\t"
        f"{concepto_txt}\t{banco_corto}\t{monto_exacto}"
    )

    lista_fv_txt = "\n".join(f"  - {f}" for f in facturas) if len(facturas) > 1 else ""
    detalle_fv = f"\n{lista_fv_txt}\n" if lista_fv_txt else "\n"

    texto = f"""{saludo}

envio soporte de pago {etiqueta_fv} fv {factura_txt}{detalle_fv}valor consignado ${monto_entero}
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
    if facturas:
        celdas.insert(3, (etiqueta_fv.capitalize(), escape(factura_txt)))

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

    lista_html = ""
    if len(facturas) > 1:
        items = "".join(
            f'<li style="margin:0 0 4px;">{escape(f)}</li>' for f in facturas
        )
        lista_html = (
            f'<ul style="margin:8px 0 12px 18px;padding:0;color:#222;font-size:13px;">{items}</ul>'
        )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Soporte de pago</title></head>
<body style="margin:0;padding:0;background:#eef4f0;">
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
            <p style="margin:0 0 8px;">
              envio soporte de pago {escape(etiqueta_fv)} fv <strong>{escape(factura_txt)}</strong><br>
              valor consignado <strong>${escape(monto_entero)}</strong><br>
              mil gracias
            </p>
            {lista_html}
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
