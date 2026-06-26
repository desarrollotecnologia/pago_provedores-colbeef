from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.config import get_settings
from app.version import APP_VERSION, EMAIL_TEMPLATE_VERSION, UI_VERSION
from app.core.database import get_db
from app.models import CuentaOrdenante, Usuario
from app.schemas.dashboard import DashboardResponse, PublicConfig
from app.schemas.historial import HistorialPagoDetalle, HistorialPagosResponse
from app.services import dashboard_service, historial_service

router = APIRouter(tags=["Sistema"])


@router.get("/config", response_model=PublicConfig)
def config_publica():
    """Configuración pública para el frontend — sin autenticación."""
    s = get_settings()
    return PublicConfig(
        app_name=s.app_name,
        app_url=s.app_url,
        api_base="/api",
        version=APP_VERSION,
        env=s.app_env,
        email_template_version=EMAIL_TEMPLATE_VERSION,
        ui_version=UI_VERSION,
    )


@router.get("/email-firma-preview", response_class=HTMLResponse)
def email_firma_preview():
    """Vista previa de la firma HTML (sin enviar correo)."""
    from app.services.email_signature import firma_html

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>Firma correo Colbeef</title></head>
<body style="margin:0;padding:24px;background:#eef4f0;font-family:Arial,sans-serif;">
<div style="max-width:640px;margin:0 auto;background:#fff;padding:24px;border-radius:12px;">
<h2 style="color:#1a6b42;margin:0 0 16px;font-size:1rem;">Vista previa — firma de correo</h2>
{firma_html()}
</div></body></html>"""


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return dashboard_service.obtener_dashboard(
        db, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
    )


@router.get("/config/smtp-status")
def smtp_status(_: Usuario = Depends(require_admin)):
    s = get_settings()
    return {
        "configured": bool(s.smtp_host and s.smtp_password),
        "host": s.smtp_host or None,
        "from_email": s.smtp_from_email,
    }


@router.get("/cuentas-ordenantes")
def cuentas_ordenantes(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    rows = db.scalars(
        select(CuentaOrdenante).where(CuentaOrdenante.activa.is_(True))
    ).all()
    return [{"id": r.id, "alias": r.alias, "numero_cuenta": r.numero_cuenta} for r in rows]


@router.get("/historial/pagos", response_model=HistorialPagosResponse)
def historial_pagos(
    fecha: date = Query(..., description="Fecha de operación del lote (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    q: str | None = Query(None, max_length=80),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return historial_service.buscar_pagos_por_fecha(
        db, fecha=fecha, page=page, page_size=page_size, q=q
    )


@router.get("/historial/pagos/{pago_id}", response_model=HistorialPagoDetalle)
def historial_pago_detalle(
    pago_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    detalle = historial_service.obtener_pago_detalle(db, pago_id)
    if not detalle:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")
    return detalle
