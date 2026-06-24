from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.config import get_settings
from app.version import APP_VERSION, EMAIL_TEMPLATE_VERSION, UI_VERSION
from app.core.database import get_db
from app.models import CuentaOrdenante, Usuario
from app.schemas.common import MessageResponse
from app.schemas.dashboard import DashboardResponse, PublicConfig
from app.services import dashboard_service

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


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    top_dias: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return dashboard_service.obtener_dashboard(
        db, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, top_dias=top_dias
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
